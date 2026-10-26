# -*- coding: utf-8 -*-
"""5장 실습 5-2: 순열 검정의 원리와 반복 횟수에 따른 안정.
A. 2x2 표의 이름표를 섞는 순열 검정이 Fisher의 정확한 값으로 모이는 모습(제1권 11장 표 [[16,2],[4,10]]).
B. 시연값 두 집단의 평균 차이: 모든 나눔을 다 세는 정확한 값과 무작위 순열의 값.
C. 집단이 k개뿐인 Mantel 검정의 최소 p (제1권 11.9절, 계산 11-12).
난수 시드는 모두 코드 안에 고정했다.
실행: python3 permutation-basic.py | tee permutation-basic.log
"""
import time, platform, itertools, math, json
J = {'fisher-perm': []}
from math import comb, factorial
import numpy as np
import scipy
from scipy import stats

T0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))

# ---------------------------------------------------------------- A
print('\n== A. 이름표 섞기로 Fisher 값을 되찾는다 (표 [[16,2],[4,10]], 총 32명, N1(x) 20명) ==')
exact_one = sum(comb(18, x) * comb(14, 20 - x) for x in range(16, 19)) / comb(32, 20)
print('정확한 한쪽 p = %.6e (제1권 계산 11-3의 7.08e-4)' % exact_one)
lab = np.array([1] * 20 + [0] * 12)       # 1 = N1(x)인 사람, 0 = 아닌 사람
obs_a = 16                                # 신석기 18명 가운데 N1(x) 16명


def perm_counts(B, seed, chunk=200000):
    """집단 1(18명)의 자리를 무작위로 뽑아 그 안의 N1(x) 수 a를 센다. B번."""
    rng = np.random.default_rng(seed)
    left = B; ge = 0
    while left > 0:
        m = min(chunk, left)
        keys = rng.random((m, 32))
        idx = np.argpartition(keys, 18, axis=1)[:, :18]      # 무작위 18명
        a = lab[idx].sum(axis=1)
        ge += int((a >= obs_a).sum())
        left -= m
    return ge


print('반복 횟수 B마다 시드 20개로 되풀이한 한쪽 p의 분포 (p = (b+1)/(B+1), b = a>=16인 순열 수)')
print('%10s %12s %12s %12s %12s %10s' % ('B', '평균 p', '최소 p', '최대 p', '표준편차', '시간(초)'))
for B in (100, 1000, 10000, 100000, 1000000):
    t = time.perf_counter()
    ps = []
    reps = 20 if B <= 100000 else 5
    for s in range(reps):
        b = perm_counts(B, 5000 + s)
        ps.append((b + 1) / (B + 1))
    ps = np.array(ps)
    J['fisher-perm'].append(dict(B=B, mean=float(ps.mean()), min=float(ps.min()), max=float(ps.max()), sd=float(ps.std(ddof=1)), exact=exact_one))
    print('%10s %12.3e %12.3e %12.3e %12.3e %10.2f   (되풀이 %d회, 1/(B+1) = %.1e)' % (
        '{:,}'.format(B), ps.mean(), ps.min(), ps.max(), ps.std(ddof=1), time.perf_counter() - t, reps, 1 / (B + 1)))
print('정확한 값 %.3e. B가 작으면 정확한 값(7.08e-4)을 해상할 수 없다: B = 1000이면 가능한 가장 작은 p가 1/1001 = %.2e이다.' % (exact_one, 1 / 1001))

# ---------------------------------------------------------------- A2: 차 8잔 전수
print('\n== A2. 차 8잔(시연값): 70가지 고르기를 모두 세어 본다 ==')
cups = np.array([1] * 4 + [0] * 4)
tab = {}
for comb4 in itertools.combinations(range(8), 4):
    k = int(cups[list(comb4)].sum())
    tab[k] = tab.get(k, 0) + 1
print('맞힌 개수별 가짓수:', dict(sorted(tab.items())), '합', sum(tab.values()))
print('3개 이상 맞힘 한쪽 p = (%d+%d)/70 = %.4f' % (tab[3], tab[4], (tab[3] + tab[4]) / 70))

# ---------------------------------------------------------------- B
print('\n== B. 시연값 두 집단의 평균 차이: 정확한 순열 p와 무작위 순열 p ==')
rs = np.random.default_rng(2026)
g1 = np.round(rs.normal(10.0, 2.0, 12), 2)     # 시연값: 평균 10, 표준편차 2에서 12개
g2 = np.round(rs.normal(12.0, 2.0, 10), 2)     # 시연값: 평균 12, 표준편차 2에서 10개
x = np.concatenate([g1, g2])
n1 = len(g1)
obs = g1.mean() - g2.mean()
print('시연 자료(가상 값, 시드 2026): 집단1 n=%d 평균 %.3f, 집단2 n=%d 평균 %.3f, 차 %.4f' % (len(g1), g1.mean(), len(g2), g2.mean(), obs))
t = time.perf_counter()
tot = x.sum(); N = len(x)
stat_all = []
combs = np.array(list(itertools.combinations(range(N), n1)), dtype=np.int8)
s1 = x[combs].sum(axis=1)
diffs = s1 / n1 - (tot - s1) / (N - n1)
print('모든 나눔 C(22,12) = %s 가지를 다 셈 (%.1f초)' % ('{:,}'.format(len(diffs)), time.perf_counter() - t))
tol = 1e-9
p_exact_two = float((np.abs(diffs) >= abs(obs) - tol).mean())
p_exact_less = float((diffs <= obs + tol).mean())
print('정확한 순열 p: 양쪽 %.6f, 한쪽(집단1이 작다) %.6f' % (p_exact_two, p_exact_less))
tt = stats.ttest_ind(g1, g2, equal_var=False)
mw = stats.mannwhitneyu(g1, g2, alternative='two-sided')
print('참고: Welch t 검정 p = %.6f, Mann-Whitney p = %.6f' % (tt.pvalue, mw.pvalue))
print('무작위 순열(이 실습의 구현): p = (b+1)/(B+1), 양쪽')
print('%10s %12s %12s %12s %12s %12s' % ('B', '평균 p', '최소 p', '최대 p', '표준편차', '|평균-정확|'))
for B in (100, 1000, 10000, 100000, 1000000):
    ps = []
    reps = 20 if B <= 100000 else 5
    for s in range(reps):
        rng = np.random.default_rng(7000 + s)
        ge = 0; left = B
        while left > 0:
            m = min(100000, left)
            keys = rng.random((m, N))
            idx = np.argpartition(keys, n1, axis=1)[:, :n1]
            a = x[idx].sum(axis=1)
            d = a / n1 - (tot - a) / (N - n1)
            ge += int((np.abs(d) >= abs(obs) - tol).sum()); left -= m
        ps.append((ge + 1) / (B + 1))
    ps = np.array(ps)
    print('%10s %12.6f %12.6f %12.6f %12.6f %12.6f' % ('{:,}'.format(B), ps.mean(), ps.min(), ps.max(), ps.std(ddof=1), abs(ps.mean() - p_exact_two)))
print('scipy.stats.permutation_test (n_resamples=9999, 시드 1): ', end='')
r = stats.permutation_test((g1, g2), lambda a, b, axis: a.mean(axis=axis) - b.mean(axis=axis), n_resamples=9999, alternative='two-sided', random_state=np.random.default_rng(1))
print('p = %.6f' % r.pvalue)
r2 = stats.permutation_test((g1, g2), lambda a, b, axis: a.mean(axis=axis) - b.mean(axis=axis), n_resamples=np.inf, alternative='two-sided')
print('scipy 정확 순열(n_resamples=inf): p = %.6f (이 실습의 전수 %.6f)' % (r2.pvalue, p_exact_two))
print('  scipy의 양쪽 p는 한쪽 p 두 개 중 작은 것의 2배다: 2 x min(%.6f, %.6f) = %.6f' % (p_exact_less, float((diffs >= obs - tol).mean()), 2 * min(p_exact_less, float((diffs >= obs - tol).mean()))))
print('  이 실습의 양쪽 p는 |차이|가 관측 이상인 순열의 비율이다. 두 정의가 다르므로 값이 다르다(자료 분포가 0을 중심으로 대칭이 아니기 때문).')

# ---------------------------------------------------------------- C
print('\n== C. 집단이 k개뿐인 Mantel 검정의 최소 단측 p (시연값 거리 행렬) ==')


def pair_idx(k):
    return np.triu_indices(k, 1)


def mantel_all(D1, D2):
    """D2의 행·열 이름표를 k!가지로 바꾸고 상관을 모두 구한다. 처음 값이 관측이다."""
    k = D1.shape[0]
    iu = pair_idx(k)
    v1 = D1[iu]
    rs_ = []
    for perm in itertools.permutations(range(k)):
        P = np.array(perm)
        v2 = D2[np.ix_(P, P)][iu]
        rs_.append(np.corrcoef(v1, v2)[0, 1])
    return np.array(rs_)


def euclid(pts):
    return np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(axis=2))


for k in (4, 5, 6, 7):
    rg = np.random.default_rng(100 + k)
    pts = rg.random((k, 2))                    # 시연값: 평면 위 무작위 점
    Dg = euclid(pts)
    Dgen = Dg ** 1.5                            # 시연값: 지리 거리의 단조 변환을 유전 거리로 놓는다(r이 가장 큰 경우)
    rr = mantel_all(Dg, Dgen)
    robs = rr[0]
    nge = int((rr >= robs - 1e-12).sum())
    print('  k=%d: 순열 %s가지, 관측 r = %.4f, r이 관측 이상인 순열 %d개, 단측 p = %d/%d = %.4f, 1/k! = %.4f' % (
        k, '{:,}'.format(factorial(k)), robs, nge, nge, factorial(k), nge / factorial(k), 1 / factorial(k)))
for k in (4, 5, 6):
    pts = np.arange(k, dtype=float)[:, None]    # 시연값: 일직선 위 같은 간격의 집단
    Dg = euclid(pts); Dgen = Dg ** 1.5
    rr = mantel_all(Dg, Dgen)
    nge = int((rr >= rr[0] - 1e-12).sum())
    print('  일직선 위 같은 간격 k=%d: 관측과 같은 r인 순열 %d개 → 단측 p = %d/%d = %.4f (1/k! = %.4f)' % (k, nge, nge, factorial(k), nge / factorial(k), 1 / factorial(k)))
print('제1권의 서술: 4개 집단의 최소 단측 p = 1/24 = %.4f, 5개는 1/120 = %.4f' % (1 / 24, 1 / 120))
print('\n걸린 시간 %.1f초' % (time.perf_counter() - T0))
json.dump(J, open('permutation-basic.json', 'w'))
