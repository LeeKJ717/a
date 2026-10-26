# -*- coding: utf-8 -*-
"""실습 7-7, 7-8, 7-9. 하플로타입 네트워크: (가) MSN과 단순화한 중앙결합 네트워크를 직접 구현해 작은 예로 확인하고,
(나) msprime으로 만든 이진 자료와 임의 자료 200벌에서 성질을 검사하고 PyPopART(GitHub 소스 설치)의 MJN과 대조하며,
(다) rho 통계를 제1권 11.4.3절(계산 11-11)의 시연값과 맞춘다.
사용: python network-v1.py [--pp PyPopART가 설치된 가상환경의 python 경로]"""
import argparse, json, os, subprocess, sys, tempfile, time, math
import numpy as np
from gentools import msn, median_joining, network_stats, mst_length, l1, rho, rho_age

ap = argparse.ArgumentParser()
ap.add_argument('--pp', default='', help='pypopart가 설치된 가상환경의 python 경로(없으면 대조를 건너뜀)')
args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
print('numpy', np.__version__, '| python', sys.version.split()[0])

def fmt(v): return ''.join(str(x) for x in v)
def degree_list(V, E):
    d = [0] * len(V)
    for i, j, _ in E:
        d[i] += 1; d[j] += 1
    return d
def show(name, obs):
    V, nobs, E, it = median_joining(obs)
    st = network_stats(V, nobs, E)
    print('  <%s> 관측 %d개 %s' % (name, len(set(map(tuple, obs))), ' '.join(fmt(v) for v in obs)))
    print('    MSN(관측만): 간선 %d, 길이 %d | MST 길이 %d' % (len(msn(list(map(tuple, obs)))), sum(w for _, _, w in msn(list(map(tuple, obs)))), mst_length(list(map(tuple, obs)))))
    print('    중앙결합: 꼭짓점 %d(중앙 벡터 %d: %s), 간선 %d, 간선 길이 합 %d, 순환 수(간선-꼭짓점+1) %d, 반복 %d회' % (
        st['n_nodes'], st['n_median'], ' '.join(fmt(v) for v in V[nobs:]) or '없음', st['n_edges'], st['total_len'], st['cyclomatic'], it))
    return V, nobs, E, st

print('\n[1] 작은 예(시연값)')
show('세 점 110 101 011', [(1, 1, 0), (1, 0, 1), (0, 1, 1)])
show('네 점 000 110 101 011', [(0, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1)])
show('일렬 000 100 110 111', [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)])

print('\n[2] msprime(이진 돌연변이 모형)으로 만든 자료: 반수체 12개, 유한 자리 40개, 재조합 없음')
sim_ok = True
try:
    import msprime, tskit
    print('  msprime', msprime.__version__, '| tskit', tskit.__version__)
except Exception as e:
    sim_ok = False
    print('  msprime를 불러오지 못함:', repr(e))
def simulate(seed, n=12, L=40, mu=2.5e-4, Ne=1000):
    ts = msprime.sim_ancestry(samples=n, ploidy=1, population_size=Ne, sequence_length=L, recombination_rate=0, random_seed=seed, discrete_genome=True)
    ts = msprime.sim_mutations(ts, rate=mu, model=msprime.BinaryMutationModel(), random_seed=seed, discrete_genome=True)
    G = ts.genotype_matrix()          # 자리 x 개체
    return G.T.astype(int)
def pp_run(H, tag):
    if not args.pp:
        return None
    with tempfile.TemporaryDirectory() as d:
        fa = os.path.join(d, 'in.fasta')
        with open(fa, 'w') as f:
            for i, h in enumerate(H):
                f.write('>h%d\n%s\n' % (i, ''.join('AC'[x] for x in h)))
        r = subprocess.run([args.pp, '-I', os.path.join(HERE, 'pypopart-run-v1.py'), fa], capture_output=True, text=True, cwd=d)
        if r.returncode != 0:
            return {'error': r.stderr[-300:]}
        return json.loads(r.stdout.strip().splitlines()[-1])
if sim_ok:
    H = simulate(5)
    keep = [j for j in range(H.shape[1]) if 0 < H[:, j].sum() < len(H)]
    H = H[:, keep]
    uniq = sorted(set(map(tuple, H)))
    print('  변이 자리 %d개, 서로 다른 하플로타입 %d개 (개체 %d)' % (H.shape[1], len(uniq), len(H)))
    V, nobs, E, st = show('msprime 시드 5', uniq)
    pp = pp_run(uniq, 'sim5')
    if pp and 'error' not in pp:
        print('    PyPopART %s: MJN 꼭짓점 %d(중앙 %d), 간선 %d, 길이 합 %d | MSN(관측) 간선 %d | MST 길이 %d' % (pp['version'], pp['mjn']['nodes'], pp['mjn']['medians'], pp['mjn']['edges'], pp['mjn']['total_len'], pp['msn']['edges'], pp['mst']['total_len']))
        degs = sorted(degree_list(V, E)); ws = sorted(float(w) for _, _, w in E)
        print('    꼭짓점 수, 간선 수, 차수의 정렬 목록, 간선 길이의 정렬 목록이 모두 같은가: %s' % ('예' if (st['n_nodes'], st['n_edges'], degs, ws) == (pp['mjn']['nodes'], pp['mjn']['edges'], pp['mjn']['degrees'], pp['mjn']['weights']) else '아니오'))
        print('    (PyPopART는 같은 패턴의 자리를 하나로 줄여(condense) 계산해 중앙 벡터 글자열의 길이가 달라 서열을 직접 견주지 않고 위 네 가지 불변량으로 견준다)')
    elif pp:
        print('    PyPopART 실행 실패:', pp['error'])

print('\n[3] 성질 검사와 PyPopART와의 대조: 무작위 이진 자료 200벌(하플로타입 6개, 자리 6개, 시드 2026)')
rng = np.random.default_rng(2026)
bad_conn = bad_deg = bad_obs = 0
same_m = same_e = same_len = tested = 0
diff_examples = []
nmed, ncyc = [], []
for k in range(200):
    obs = sorted(set(tuple(int(x) for x in rng.integers(0, 2, 6)) for _ in range(6)))
    if len(obs) < 3:
        continue
    V, nobs, E, it = median_joining(obs)
    st = network_stats(V, nobs, E)
    # 연결성
    par = list(range(len(V)))
    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for i, j, _ in E:
        par[f(i)] = f(j)
    if len({f(i) for i in range(len(V))}) != 1:
        bad_conn += 1
    if set(V[:nobs]) != set(obs):
        bad_obs += 1
    dg = degree_list(V, E)
    if any(dg[i] < 2 for i in range(nobs, len(V))):
        bad_deg += 1            # 차수 2 미만의 중앙 벡터가 남으면 안 된다
    nmed.append(st['n_median']); ncyc.append(st['cyclomatic'])
    pp = pp_run(obs, 'r%d' % k)
    if pp and 'error' not in pp:
        tested += 1
        degs = sorted(dg); ws = sorted(float(w) for _, _, w in E)
        if st['n_median'] == pp['mjn']['medians']:
            same_m += 1
        if st['n_edges'] == pp['mjn']['edges']:
            same_e += 1
        if (st['n_nodes'], st['n_edges'], degs, ws) == (pp['mjn']['nodes'], pp['mjn']['edges'], pp['mjn']['degrees'], pp['mjn']['weights']):
            same_len += 1
        elif len(diff_examples) < 6:
            diff_examples.append((obs, st['n_median'], st['n_edges'], st['total_len'], pp['mjn']['medians'], pp['mjn']['edges'], pp['mjn']['total_len']))
n = len(nmed)
print('  유효한 자료 %d벌. 연결되지 않은 네트워크 %d, 관측 하플로타입이 빠진 것 %d, 차수 2 미만의 중앙 벡터가 남은 것 %d' % (n, bad_conn, bad_obs, bad_deg))
print('  중앙 벡터 수의 분포: 평균 %.2f, 최대 %d | 순환 수 평균 %.2f, 최대 %d' % (np.mean(nmed), max(nmed), np.mean(ncyc), max(ncyc)))
if tested:
    print('  PyPopART와 대조(%d벌): 중앙 벡터 개수가 같은 것 %d벌, 간선 수가 같은 것 %d벌, 꼭짓점 수·간선 수·차수 목록·간선 길이 목록이 모두 같은 것 %d벌' % (tested, same_m, same_e, same_len))
    for obs, a, b, bl, c, d, dl in diff_examples:
        print('    어긋난 예: 관측 %s -> 이 책 중앙 %d·간선 %d·길이 합 %d, PyPopART 중앙 %d·간선 %d·길이 합 %g' % (' '.join(fmt(v) for v in obs), a, b, bl, c, d, dl))
else:
    print('  PyPopART 대조는 --pp를 주지 않아 건너뜀')

print('\n[4] rho 통계: 제1권 11.4.3절 시연값(STR 자리 3개, 걸음 [0,1,1,2,0])')
root = (10, 12, 15)
people = [root, (11, 12, 15), (10, 11, 15), (11, 13, 15), root]            # 뿌리에서 0, 1, 1, 2, 0걸음
dist = [l1(root, h) for h in people]
r, n_, d = rho(root, people)
print('  뿌리에서의 걸음 %s -> rho = %d/%d = %.2f (제1권 0.8)' % (d, sum(d), n_, r))
mu, L = 0.0025, 3
per = 1 / (mu * L)
print('  변이 하나가 쌓이는 세대 = 1/(mu x 자리 수) = %.2f세대' % per)
for gen in (30, 25):
    print('  세대 %d년: 나이 = rho/(mu L) x 세대 = %.1f세대 x %d = %.0f년 (제1권 %s)' % (gen, r / (mu * L), gen, rho_age(r, mu, L, gen), {30: 3200, 25: 2667}[gen]))
print('  같은 rho를 자리 9개로 계산하면 나이는 %.1f년(세대 30년): 자리 3개일 때의 1/3' % rho_age(r, mu, 9, 30))
uniq = sorted(set(people))
V, nobs, E, it = median_joining(uniq)
print('  이 다섯 사람의 서로 다른 하플로타입 %d개로 만든 중앙결합 네트워크: 꼭짓점 %d, 중앙 벡터 %d, 간선 %d' % (len(uniq), len(V), len(V) - nobs, len(E)))
print('  뿌리를 바꾸면 rho가 달라진다(사람 5명의 평균 걸음):')
for h in uniq:
    rr, _, _ = rho(h, people)
    print('    뿌리 %s: rho = %.2f, 나이(자리 3, 세대 30) = %.0f년' % (h, rr, rho_age(rr, mu, L, 30)))
print('  표준오차의 단순 근사(각 가계의 돌연변이 수가 평균 rho인 푸아송이고 별 모양 계통이라고 가정): SE(rho) = sqrt(rho/n) = %.3f -> 나이의 SE = %.0f년' % (math.sqrt(r / n_), rho_age(math.sqrt(r / n_), mu, L, 30)))
rng = np.random.default_rng(1)
bs = np.array([np.mean(rng.choice(d, size=len(d), replace=True)) for _ in range(20000)])
print('  사람 5명의 걸음을 다시 뽑는 부트스트랩(20000회, 시드 1): rho의 2.5%%, 중앙, 97.5%% = %.2f, %.2f, %.2f' % tuple(np.percentile(bs, [2.5, 50, 97.5])))

print('\n[5] 제1권 11.4.3절(계산 11-11)의 환산을 되풀이: 돌연변이율 0.0025, STR 9자리, 세대 30년')
per9 = 1 / (0.0025 * 9)
yr = per9 * 30
print('  변이 하나 = %.2f세대 x 30 = %.1f년 (논문 1333)' % (per9, yr))
for nm, age, sd in (('에벤키와 에벤 공유', 1916, 985), ('에벤 고유', 615, 418), ('에벤키 고유', 303, 177)):
    rr = age / yr
    srel = sd / age
    print('  %-10s %d +- %d년 -> rho = %.3f +- %.3f걸음, 구간 %d~%d년; 상대 표준오차 %.3f' % (nm, age, sd, rr, sd / yr, age - sd, age + sd, srel))
print('  위의 푸아송 근사 SE(rho)/rho = 1/sqrt(n rho)를 논문의 상대 오차에 맞추려면 n x rho = %.2f (공유), %.2f (에벤), %.2f (에벤키)' % tuple(1 / (sd / age) ** 2 for age, sd in ((1916, 985), (615, 418), (303, 177))))
print('  곧 n = %.2f, %.2f, %.2f명에 해당한다. 논문이 실제로 쓴 n과 방식은 본문에 없어 판정하지 못한다(제1권 11.4.3절 판정과 같다).' % tuple(1 / ((sd / age) ** 2 * (age / yr)) for age, sd in ((1916, 985), (615, 418), (303, 177))))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
