# -*- coding: utf-8 -*-
"""제2권 7장 도구 모음 v1. numpy, scipy만 쓴다(표준 라이브러리 포함).
하플로그룹 빈도표, Nei 유전자 다양도, Fisher 정확검정, AMOVA와 순열 검정, Mantel 검정,
최소 신장 네트워크(MSN)와 단순화한 중앙결합 네트워크, rho 통계, f 통계와 블록 잭나이프.
모두 이 책이 직접 구현했다. 공개 도구(Arlequin, Network, PopART, ADMIXTOOLS 등)의 코드를 옮기지 않았다."""
import csv, itertools, math, os
from math import comb
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HG = ['N1(x)', 'N1c', 'C/C3e', 'O3a', 'O3a3c']


# ------------------------------------------------------------------ 입력 표
def read_cui(path=None):
    """cui-table1-v1.csv를 읽어 [(유적, 문화, 시작BP, 끝BP, n, [5개 수])]로."""
    path = path or os.path.join(HERE, 'cui-table1-v1.csv')
    rows = []
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            c = [int(r[k]) for k in ('N1x', 'N1c', 'C', 'O3a', 'O3a3c')]
            rows.append((r['site'], r['culture'], int(r['period_bp_from']), int(r['period_bp_to']), int(r['n']), c))
    return rows


def individuals(counts_by_pop):
    """집단별 하플로그룹 개수 -> (개체의 하플로그룹 번호 배열, 개체의 집단 번호 배열)."""
    hap, pop = [], []
    for p, cnt in enumerate(counts_by_pop):
        for h, k in enumerate(cnt):
            hap += [h] * k
            pop += [p] * k
    return np.array(hap), np.array(pop)


def nei_h(counts):
    """Nei 유전자 다양도 H = n/(n-1) (1 - sum p^2). 0인 칸은 무시."""
    n = sum(counts)
    if n < 2:
        return float('nan')
    return n / (n - 1) * (1 - sum((c / n) ** 2 for c in counts if c > 0))


# ------------------------------------------------------------------ Fisher 정확검정
def fisher_2x2(a, b, c, d, alt='two-sided'):
    """합계를 고정한 초기하분포. 양쪽은 '관측 이하의 확률'을 가진 표의 확률 합(상대 허용 1e-9)."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    lo, hi = max(0, c1 - r2), min(r1, c1)
    pr = {x: comb(r1, x) * comb(r2, c1 - x) / comb(n, c1) for x in range(lo, hi + 1)}
    p0 = pr[a]
    if alt == 'two-sided':
        p = sum(v for v in pr.values() if v <= p0 * (1 + 1e-9))
    elif alt == 'greater':
        p = sum(v for x, v in pr.items() if x >= a)
    else:
        p = sum(v for x, v in pr.items() if x <= a)
    odds = (a * d) / (b * c) if b * c > 0 else float('inf')
    return min(1.0, p), odds, pr


def multinom_logp(table):
    """r x c 표의 합계 고정 확률의 로그(다변량 초기하분포). Freeman-Halton의 순서 기준."""
    t = np.asarray(table)
    from math import lgamma
    R, C, n = t.sum(1), t.sum(0), t.sum()
    lp = sum(lgamma(x + 1) for x in R) + sum(lgamma(x + 1) for x in C) - lgamma(n + 1) - sum(lgamma(x + 1) for x in t.ravel())
    return lp


def fisher_rxc_mc(table, B=100000, seed=1):
    """r x c 표의 Monte Carlo Fisher-Freeman-Halton: 열 이름표를 섞어 표 확률이 관측 이하인 비율."""
    t = np.asarray(table)
    rng = np.random.default_rng(seed)
    R = t.sum(1)
    lab = np.repeat(np.arange(t.shape[1]), t.sum(0))
    rowid = np.repeat(np.arange(t.shape[0]), R)
    lp0 = multinom_logp(t)
    cnt = 0
    for _ in range(B):
        rng.shuffle(lab)
        tt = np.zeros_like(t)
        np.add.at(tt, (rowid, lab), 1)
        if multinom_logp(tt) <= lp0 + 1e-9:
            cnt += 1
    return (cnt + 1) / (B + 1)


def holm(ps):
    """Holm 보정. 입력 순서대로 보정 p를 돌려준다."""
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * ps[i])
        adj[i] = min(1.0, run)
    return adj


# ------------------------------------------------------------------ AMOVA
def _onehot(lab):
    u, inv = np.unique(lab, return_inverse=True)
    M = np.zeros((len(lab), len(u)))
    M[np.arange(len(lab)), inv] = 1.0
    return M, inv


def _ssd(D2, lab):
    """집단 안 제곱합 sum_g (1/2 n_g) sum_{i,j in g} D2_ij."""
    M, _ = _onehot(lab)
    n = M.sum(0)
    return float(np.sum(np.einsum('ip,ij,jp->p', M, D2, M) / (2 * n)))


def amova(D2, pop, grp=None):
    """Excoffier, Smouse, Quattro(1992)의 AMOVA. D2는 개체 사이 '제곱' 거리 행렬(대각 0).
    pop: 개체의 집단 이름표, grp: 개체의 묶음 이름표(없으면 묶음 하나). 반수체 자료.
    돌려주는 값: 제곱합, 자유도, 평균제곱, 분산 성분, Phi 통계."""
    D2 = np.asarray(D2, float)
    N = len(D2)
    pop = np.asarray(pop)
    grp = np.zeros(N, int) if grp is None else np.asarray(grp)
    pops = np.unique(pop)
    P = len(pops)
    gl = np.unique(grp)
    G = len(gl)
    npop = np.array([(pop == p).sum() for p in pops], float)
    grp_of_pop = [grp[pop == p][0] for p in pops]
    Ng = np.array([(grp == g).sum() for g in gl], float)
    # 계수 n, n', n''
    s_g = sum(sum(npop[i] ** 2 for i in range(P) if grp_of_pop[i] == g) / Ng[k] for k, g in enumerate(gl))
    s_p = (npop ** 2).sum() / N
    n1 = (N - s_g) / (P - G)
    ssd_t = D2.sum() / (2 * N)
    ssd_wp = _ssd(D2, pop)
    ssd_wg = _ssd(D2, grp)
    ssd_ag = ssd_t - ssd_wg
    ssd_ap = ssd_wg - ssd_wp
    df_ag, df_ap, df_wp = G - 1, P - G, N - P
    msd_wp = ssd_wp / df_wp
    msd_ap = ssd_ap / df_ap
    s2c = msd_wp
    s2b = (msd_ap - s2c) / n1
    out = dict(N=N, P=P, G=G, n1=n1, ssd_t=ssd_t, ssd_wp=ssd_wp, ssd_ap=ssd_ap, ssd_ag=ssd_ag,
               df_ag=df_ag, df_ap=df_ap, df_wp=df_wp, msd_wp=msd_wp, msd_ap=msd_ap)
    if G > 1:
        n2 = (s_g - s_p) / (G - 1)
        n3 = (N - (Ng ** 2).sum() / N) / (G - 1)
        msd_ag = ssd_ag / df_ag
        s2a = (msd_ag - s2c - n2 * s2b) / n3
        out.update(n2=n2, n3=n3, msd_ag=msd_ag)
    else:
        s2a = 0.0
    tot = s2a + s2b + s2c
    nan = float('nan')
    if abs(tot) < 1e-12:       # 변이가 전혀 없으면 Phi는 0/0이다(정의되지 않음)
        out.update(s2a=s2a, s2b=s2b, s2c=s2c, total=tot, pct_a=nan, pct_b=nan, pct_c=nan, phi_ct=nan, phi_sc=nan, phi_st=nan)
        return out
    den_sc = s2b + s2c
    out.update(s2a=s2a, s2b=s2b, s2c=s2c, total=tot,
               pct_a=100 * s2a / tot, pct_b=100 * s2b / tot, pct_c=100 * s2c / tot,
               phi_ct=s2a / tot if G > 1 else nan, phi_sc=s2b / den_sc if abs(den_sc) > 1e-12 else nan, phi_st=(s2a + s2b) / tot)
    return out


def amova_perm(D2, pop, grp=None, B=9999, seed=1):
    """순열 검정. Phi_ST: 개체를 모든 집단에 섞는다. Phi_SC: 같은 묶음 안의 집단들 사이에서 개체를 섞는다.
    Phi_CT: 집단을 통째로 묶음 사이에 섞는다(묶음마다 집단 수 유지). p = (1 + 관측 이상인 횟수)/(1 + B).
    (순열 규칙은 이 책의 구현이며 Arlequin의 출력과 같은지는 확인하지 못했다.)"""
    rng = np.random.default_rng(seed)
    D2 = np.asarray(D2, float)
    pop = np.asarray(pop)
    N = len(pop)
    grp = np.zeros(N, int) if grp is None else np.asarray(grp)
    obs = amova(D2, pop, grp)
    res = {}
    # Phi_ST
    cnt = 0
    for _ in range(B):
        pp = rng.permutation(pop)
        # 집단->묶음 대응은 그대로 두려면 묶음도 집단 따라간다
        gmap = {p: grp[pop == p][0] for p in np.unique(pop)}
        gg = np.array([gmap[p] for p in pp])
        if amova(D2, pp, gg)['phi_st'] >= obs['phi_st'] - 1e-12:
            cnt += 1
    res['phi_st'] = (cnt + 1) / (B + 1)
    # Phi_SC (묶음이 둘 이상일 때 의미, 하나면 Phi_ST와 같다)
    if len(np.unique(grp)) > 1:
        cnt = 0
        for _ in range(B):
            pp = pop.copy()
            for g in np.unique(grp):
                ix = np.where(grp == g)[0]
                pp[ix] = rng.permutation(pop[ix])
            if amova(D2, pp, grp)['phi_sc'] >= obs['phi_sc'] - 1e-12:
                cnt += 1
        res['phi_sc'] = (cnt + 1) / (B + 1)
        # Phi_CT: 집단 통째로 묶음 사이에 섞기
        pops = np.unique(pop)
        gofp = np.array([grp[pop == p][0] for p in pops])
        cnt = 0
        for _ in range(B):
            perm_g = rng.permutation(gofp)
            gmap = dict(zip(pops, perm_g))
            gg = np.array([gmap[p] for p in pop])
            if amova(D2, pop, gg)['phi_ct'] >= obs['phi_ct'] - 1e-12:
                cnt += 1
        res['phi_ct'] = (cnt + 1) / (B + 1)
    return obs, res


def phi_from_percent(pa, pb, pc):
    """논문 표처럼 분산 성분의 백분율(묶음 사이, 묶음 안 집단 사이, 집단 안)에서 Phi 통계."""
    t = pa + pb + pc
    return dict(phi_ct=pa / t, phi_sc=pb / (pb + pc), phi_st=(pa + pb) / t, identity=1 - (1 - pa / t) * (1 - pb / (pb + pc)))


# ------------------------------------------------------------------ Mantel
def _tri(M):
    i, j = np.triu_indices(len(M), 1)
    return M[i, j]


def mantel(A, B, perms=9999, seed=1, exact_max=8):
    """두 거리 행렬의 Mantel 검정. 행과 열을 함께 섞는다.
    집단이 exact_max개 이하이면 n! 순열을 전부 센다(정확). 돌려주는 값: r, 한쪽(큰 쪽) p, 양쪽 p, 순열 수, 방식."""
    A, B = np.asarray(A, float), np.asarray(B, float)
    n = len(A)
    a = _tri(A)
    r0 = np.corrcoef(a, _tri(B))[0, 1]
    if n <= exact_max:
        rs = np.array([np.corrcoef(a, _tri(B[np.ix_(p, p)]))[0, 1] for p in itertools.permutations(range(n))])
        return dict(r=r0, p_greater=float((rs >= r0 - 1e-12).mean()), p_two=float((np.abs(rs) >= abs(r0) - 1e-12).mean()),
                    n_perm=len(rs), mode='exact', rs=rs)
    rng = np.random.default_rng(seed)
    rs = np.empty(perms)
    for k in range(perms):
        p = rng.permutation(n)
        rs[k] = np.corrcoef(a, _tri(B[np.ix_(p, p)]))[0, 1]
    return dict(r=r0, p_greater=(1 + (rs >= r0 - 1e-12).sum()) / (perms + 1), p_two=(1 + (np.abs(rs) >= abs(r0) - 1e-12).sum()) / (perms + 1),
                n_perm=perms, mode='random', rs=rs)


# ------------------------------------------------------------------ 네트워크
def l1(u, v):
    return int(sum(abs(a - b) for a, b in zip(u, v)))


def mst_length(V):
    """완전 그래프의 최소 신장 트리 길이(Prim)."""
    n = len(V)
    if n < 2:
        return 0
    inT = [False] * n
    dist = [float('inf')] * n
    dist[0] = 0
    tot = 0
    for _ in range(n):
        u = min((i for i in range(n) if not inT[i]), key=lambda i: dist[i])
        inT[u] = True
        tot += dist[u]
        for v in range(n):
            if not inT[v]:
                dist[v] = min(dist[v], l1(V[u], V[v]))
    return tot


def msn(V):
    """최소 신장 네트워크: 모든 최소 신장 트리의 합집합. 간선 (i,j,w)는 w보다 작은 간선만으로
    i와 j가 이어지지 않을 때에만 들어간다. 돌려주는 값: [(i, j, w)]."""
    n = len(V)
    E = sorted(((l1(V[i], V[j]), i, j) for i in range(n) for j in range(i + 1, n)))
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    out = []
    k = 0
    while k < len(E):
        w = E[k][0]
        grp = []
        while k < len(E) and E[k][0] == w:
            grp.append(E[k])
            k += 1
        for _, i, j in grp:
            if find(i) != find(j):
                out.append((i, j, w))
        for _, i, j in grp:
            par[find(i)] = find(j)
    return out


def median_joining(obs, max_iter=500):
    """단순화한 중앙결합(median-joining) 네트워크, 오차 허용 epsilon = 0.
    1) 현재 꼭짓점의 MSN을 만든다. 2) 차수 2 미만인 중앙 벡터는 지운다.
    3) MSN에서 한 꼭짓점을 공유하는 두 간선(y-x-z)마다 세 점의 좌표별 중앙값 m을 후보로 하고,
       m이 아직 없으면 비용 d(m,x)+d(m,y)+d(m,z)를 구해, 후보 전체의 최소 비용과 같은 것을 모두 더한다.
    4) 더할 것이 없을 때까지 되풀이한다. 마지막에 차수 2 미만인 중앙 벡터를 지운다.
    Bandelt 등(1999)과 PopART의 구현을 단순화한 것이며 두 프로그램의 출력과 같다고 보증하지 않는다.
    돌려주는 값: 꼭짓점 목록(관측 먼저), 관측 수, MSN 간선, 반복 횟수."""
    V = []
    for v in obs:
        v = tuple(int(x) for x in v)
        if v not in V:
            V.append(v)
    nobs = len(V)
    seen = set()
    it = 0
    while it < max_iter:
        it += 1
        # 차수 2 미만의 중앙 벡터 지우기
        while True:
            E = msn(V)
            deg = [0] * len(V)
            for i, j, _ in E:
                deg[i] += 1
                deg[j] += 1
            drop = [i for i in range(nobs, len(V)) if deg[i] < 2]
            if not drop:
                break
            V = [v for i, v in enumerate(V) if i not in drop]
        state = frozenset(V)
        if state in seen:
            break
        seen.add(state)
        nb = {i: [] for i in range(len(V))}
        for i, j, _ in E:
            nb[i].append(j)
            nb[j].append(i)
        have = set(V)
        cand = {}
        for x in range(len(V)):
            for y, z in itertools.combinations(nb[x], 2):
                m = tuple(int(t) for t in np.median(np.array([V[x], V[y], V[z]]), axis=0))
                if m in have:
                    continue
                c = l1(V[x], m) + l1(V[y], m) + l1(V[z], m)
                cand[m] = c
        if not cand:
            break
        cmin = min(cand.values())
        V += sorted(m for m, c in cand.items() if c == cmin)
    # 마무리
    while True:
        E = msn(V)
        deg = [0] * len(V)
        for i, j, _ in E:
            deg[i] += 1
            deg[j] += 1
        drop = [i for i in range(nobs, len(V)) if deg[i] < 2]
        if not drop:
            break
        V = [v for i, v in enumerate(V) if i not in drop]
    return V, nobs, E, it


def network_stats(V, nobs, E):
    L = sum(w for _, _, w in E)
    return dict(n_nodes=len(V), n_median=len(V) - nobs, n_edges=len(E), total_len=L, mst_len=mst_length(V),
                mst_len_obs=mst_length(V[:nobs]), cyclomatic=len(E) - len(V) + 1)


# ------------------------------------------------------------------ rho 통계
def rho(root, haps, counts=None):
    """뿌리 하플로타입에서 각 개체까지의 걸음(L1 거리)의 평균. counts는 하플로타입별 사람 수."""
    counts = counts or [1] * len(haps)
    d = [l1(root, h) for h in haps]
    n = sum(counts)
    r = sum(c * x for c, x in zip(counts, d)) / n
    return r, n, d


def rho_age(r, mu, loci, gen):
    """나이 = rho / (mu x 자리 수) 세대 x 세대 길이(년)."""
    return r / (mu * loci) * gen


# ------------------------------------------------------------------ f 통계
def f4_snp(p1, p2, p3, p4):
    """자리별 f4 항 (p1-p2)(p3-p4). 서로 다른 표본이라 편향 보정이 필요 없다."""
    return (p1 - p2) * (p3 - p4)


def f3_unbiased(pc, pa, pb, nc):
    """외집단 f3(C; A, B)의 자리별 불편 항. nc는 C의 대립유전자 수(자리별 배열 또는 수)."""
    return (pc - pa) * (pc - pb) - pc * (1 - pc) / (nc - 1)


def wjack(num, den, m):
    """블록별 분자·분모 합 num, den과 블록 크기 m에서 비 추정량 sum(num)/sum(den)의
    가중 블록 잭나이프(delete-m_j jackknife). 돌려주는 값: 전체 추정값, 잭나이프 평균, SE."""
    num, den, m = (np.asarray(x, float) for x in (num, den, m))
    g = len(m)
    n = m.sum()
    th = num.sum() / den.sum()
    thm = (num.sum() - num) / (den.sum() - den)
    h = n / m
    thj = g * th - ((1 - m / n) * thm).sum()
    tau = h * th - (h - 1) * thm
    var = ((tau - thj) ** 2 / (h - 1)).sum() / g
    return th, thj, math.sqrt(var)


def blocks(L, nb):
    """L개 자리를 연속한 nb개 블록으로 나눈 경계(블록 크기 차이는 1 이하)."""
    b = np.linspace(0, L, nb + 1).astype(int)
    return b[:-1], b[1:]


def block_sums(x, nb):
    s, e = blocks(len(x), nb)
    cs = np.concatenate([[0.0], np.cumsum(x)])
    return cs[e] - cs[s], (e - s)
