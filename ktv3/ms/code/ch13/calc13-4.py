# -*- coding: utf-8 -*-
"""계산 13-4: 호톤 호의 습윤(숲) 시작 연대를 10.7, 10.304, 10.0 ka 로 바꾸면 앞 장의 두 결과가 얼마나 흔들리는가.
(1) 4장 계산 4-5 의 1000년 칸 코딩과 쌍별 일치율(원 코딩은 시작 10.0 ka 를 썼다).
(2) 2장 계산 2-8 의 가장 긴 습윤 구간 중점, 표준편차 비, 순열 검정, 경도 경사(원 판독은 시작 10.7 ka 를 썼다).
다른 기록의 코딩과 판독, 난수 시드는 원 스크립트(ms/code/ch04/calc4-5.py, ms/code/ch02/calc-ch02-v1.py)와 같다.
원 로그와 같은 값이 나오는지 먼저 점검한 뒤 값을 바꾼다.
"""
import itertools, math
import numpy as np
from scipy import stats

# ---------------- (1) 4장 계산 4-5 ----------------
R4 = {
 'Hoton': None,
 'Ugii Nuur': [(8.66, 7.8, +1), (7.8, 6.86, -1), (6.86, 3.17, -1), (3.17, 2.34, +1), (2.34, 1.6, +1)],
 'Hulun': [(11.0, 8.0, -1), (8.0, 6.4, +1), (6.4, 4.4, -1), (4.4, 3.35, -1), (3.35, 2.05, +1), (2.05, 1.0, -1)],
 'Bayan Nuur': [(12.9, 8.5, -1), (8.5, 3.0, +1), (3.0, 0.0, -1)],
 'Minusinsk': [(11.7, 7.6, -1), (7.6, 5.1, +1), (3.6, 3.3, -1), (1.5, 0.0, -1)],
 'Kotokel': [(12.8, 11.6, -1), (10.8, 7.3, +1)],
 'Teletskoye': [(3.9, 3.6, -1), (3.5, 1.6, +1)],
 'Ulaan': [(12.3, 9.4, +1), (6.8, 3.2, -1), (3.2, 0.0, -1)],
 'Ulagan': [(12.0, 9.5, +1)],
 'Altai 상부숲': [(10.0, 7.0, +1)],
 'Hovsgol': [(11.0, 7.0, +1), (6.0, 3.5, -1)],
 'Kulunda 꽃가루': [(4.4, 3.75, -1), (3.75, 0.09, +1), (0.09, 0.0, -1)],
 'Kulunda 규조': [(3.96, 1.92, -1)],
 'Chen 종합': [(11.7, 8.0, -1), (8.0, 0.0, +1)],
}
BINS = [(k, k + 1) for k in range(0, 12)]


def state(iv, lo, hi):
    pos = neg = 0.0
    for a, b, s in iv:
        ov = max(0.0, min(a, hi) - max(b, lo))
        if s > 0: pos += ov
        else: neg += ov
    full = hi - lo
    if pos >= full / 2 and neg < full / 2: return +1
    if neg >= full / 2 and pos < full / 2: return -1
    return 0


def mean_agree(MM):
    rr = []
    for a, b in itertools.combinations(MM, 2):
        both = [j for j in range(12) if MM[a][j] != 0 and MM[b][j] != 0]
        if len(both) >= 3: rr.append(sum(1 for j in both if MM[a][j] == MM[b][j]) / len(both))
    return float(np.mean(rr)), len(rr)


def run4(b):
    R = dict(R4); R['Hoton'] = [(11.5, b, -1), (b, 5.0, +1), (5.0, 0.0, -1)]
    M = {n: [state(iv, lo, hi) for lo, hi in BINS] for n, iv in R.items()}
    cnt = [(sum(1 for v in M.values() if v[j] > 0), sum(1 for v in M.values() if v[j] < 0)) for j in range(12)]
    obs, npair = mean_agree(M)
    rng = np.random.default_rng(4105)
    sims = []
    for _ in range(5000):
        MM = {n: [int(rng.choice([1, -1])) if x != 0 else 0 for x in v] for n, v in M.items()}
        sims.append(mean_agree(MM)[0])
    sims = np.array(sims)
    both = tot_n = tot_a = 0
    for a, c in itertools.combinations(M, 2):
        bb = [j for j in range(12) if M[a][j] != 0 and M[c][j] != 0]
        if len(bb) >= 3:
            tot_n += len(bb); tot_a += sum(1 for j in bb if M[a][j] == M[c][j])
    return M['Hoton'], cnt, obs, npair, tot_a, tot_n, float(np.median(sims)), np.percentile(sims, [2.5, 97.5]), float((sims < obs).mean() * 100)


print('=== 계산 13-4 (1) 4장 계산 4-5 (원 코딩은 시작 10.0 ka) ===')
res4 = {}
for b in (10.0, 10.304, 10.7):
    h, cnt, obs, npair, ta, tn, med, ci, pct = run4(b)
    res4[b] = dict(hoton=h, cnt=cnt, obs=obs, npair=npair, ta=ta, tn=tn, med=med, ci=[float(x) for x in ci], pct=pct)
    print('시작 %.3f ka: Hoton 행 ' % b + ' '.join({1: '+', -1: '-', 0: '.'}[x] for x in h))
    print('    10~11 ka 칸: + %d, - %d ; 9~10 ka 칸: + %d, - %d ; 11~12 ka 칸: + %d, - %d' % (*cnt[10], *cnt[9], *cnt[11]))
    print('    쌍 %d 개, 일치 %d / 공통 %d = %.3f, 쌍 평균 %.3f ; 기준선 중앙 %.2f (95%%: %.2f~%.2f), 관측 위치 %.1f%%' % (npair, ta, tn, ta / tn, obs, med, *ci, pct))
b0 = res4[10.0]
assert abs(b0['obs'] - 0.480) < 0.0006 and b0['ta'] == 147 and b0['tn'] == 294 and b0['cnt'][10] == (4, 5), '4장 로그와 다르다'
print('(점검) 시작 10.0 ka 의 결과는 4장 로그와 같다: 쌍 평균 0.480, 일치 147/294, 10~11 ka 칸 + 4 - 5.')

# ---------------- (2) 2장 계산 2-8 ----------------
print('\n=== 계산 13-4 (2) 2장 계산 2-8 (원 판독은 시작 10.7 ka) ===')


def ce2(y): return 1950 - y if y > 0 else 1949 - y


def overlap(a, b):
    return max(0.0, min(max(a), max(b)) - max(min(a), min(b)))


def run2(b):
    MG = {
     '텔멘 호(Peck 2002)': [(7.11, 6.26, -1), (6.26, 4.39, -1), (4.39, 1.26, +1)],
     '텔멘 호(Struck 2022)': [(4.25, ce2(-1200) / 1000, -1), (ce2(-1200) / 1000, ce2(700) / 1000, +1), (ce2(700) / 1000, ce2(1300) / 1000, -1), (ce2(1300) / 1000, 0.0, +1)],
     '우기 호(Schwanghart 2008)': [(10.6, 7.9, -1), (7.9, 4.2, +1), (4.2, 2.8, -1), (2.8, 0.0, +1)],
     '호톤 호(Rudaya)': [(11.5, b, -1), (b, 4.9, +1), (4.9, 0.0, -1)],
     '군 호(Zhang C. 2012)': [(10.8, 10.3, -1), (10.3, 7.0, +1), (7.0, 5.7, -1), (4.1, 3.6, -1), (3.0, 2.5, -1), (2.5, 0.0, +1)],
     '울란 호(Mischke 2020)': [(11.7, 9.4, +1), (9.4, 0.0, -1)],
     '홉스골 호(Prokopenko 2007)': [(11.0, 7.0, +1), (6.0, 3.5, -1)],
     '오르혼 토양(Timireva 2026)': [(11.7, 8.5, +1), (8.5, 3.5, -1), (3.5, 0.0, +1)],
    }
    def longest_wet(iv):
        best = None
        for a, bb, s in iv:
            if s > 0 and (best is None or abs(a - bb) > abs(best[0] - best[1])): best = (a, bb)
        return best
    mids = []
    for nm, iv in MG.items():
        w = longest_wet(iv); a0 = min(w[0], 11.7); mids.append((a0 + w[1]) / 2)
    M_mid = np.array(mids)
    E_mid = np.array([6.65, 7.55, 8.75, 7.20, 7.10, 7.85, 5.60, 7.30, 7.50, 6.00, 6.00, 6.20, 7.40])
    rng = np.random.default_rng(20261026)
    allv = np.concatenate([E_mid, M_mid]); nE = len(E_mid)
    obs = M_mid.std(ddof=1) / E_mid.std(ddof=1)
    cnt = 0; N = 20000
    for _ in range(N):
        rng.shuffle(allv)
        e = allv[:nE]; m = allv[nE:]
        if m.std(ddof=1) / e.std(ddof=1) >= obs: cnt += 1
    p_perm = (cnt + 1) / (N + 1)
    welch = stats.ttest_ind(M_mid, E_mid, equal_var=False)[1]
    lon = np.array([88.346, 97.32, 103.654, 115.027, 116.60, 117.506]); on = np.array([b, 4.39, 12.3, 10.5, 8.8, 8.0])
    rho = stats.spearmanr(lon, on)[0]
    perm = sum(1 for q in itertools.permutations(range(6)) if abs(stats.spearmanr(lon, on[list(q)])[0]) >= abs(rho) - 1e-12)
    return mids[3], M_mid.mean(), M_mid.std(ddof=1), obs, p_perm, welch, rho, perm / 720.0


res2 = {}
for b in (10.7, 10.304, 10.0):
    mid, mu, sd, ratio, pp, welch, rho, pex = run2(b)
    res2[b] = dict(mid=mid, mean=mu, sd=sd, ratio=ratio, p=pp, welch=welch, rho=rho, pex=pex)
    print('시작 %.3f ka: 호톤 중점 %.2f ; 8개 평균 %.2f, 표준편차 %.2f ; 표준편차 비 %.2f, 순열 p %.4f ; Welch p %.3f ; 경도 경사 rho %.2f, 정확 순열 p %.3f' % (b, mid, mu, sd, ratio, pp, welch, rho, pex))
a0 = res2[10.7]
assert abs(a0['mid'] - 7.80) < 0.005 and abs(a0['mean'] - 6.10) < 0.005 and abs(a0['sd'] - 3.43) < 0.005 and abs(a0['ratio'] - 3.89) < 0.005 and abs(a0['p'] - 0.0007) < 0.00006 and abs(a0['rho'] + 0.31) < 0.005 and abs(a0['pex'] - 0.564) < 0.0005, '2장 로그와 다르다'
print('(점검) 시작 10.7 ka 의 결과는 2장 로그와 같다: 중점 7.80, 평균 6.10, 표준편차 3.43, 비 3.89, 순열 p 0.0007, rho -0.31, p 0.564.')
import json
json.dump(dict(ch04={str(k): v for k, v in res4.items()}, ch02={str(k): v for k, v in res2.items()}), open('calc13-4-out.json', 'w'), ensure_ascii=False, default=lambda o: o if not isinstance(o, np.generic) else o.item())

print('\n=== 계산 13-4 (3) 습윤 구간의 길이에서 396년이 차지하는 몫(2장 판독: 시작 10.7 → 4.9 ka) ===')
L1 = (10.7 - 4.9) * 1000; L2 = (10.304 - 4.9) * 1000
print('구간 길이 %.0f 년(시작 10.7), %.0f 년(시작 10.304). 차 %.0f 년은 구간의 %.1f %%, 1000년 칸 하나의 %.1f %%' % (L1, L2, L1 - L2, (L1 - L2) / L1 * 100, (L1 - L2) / 10))
