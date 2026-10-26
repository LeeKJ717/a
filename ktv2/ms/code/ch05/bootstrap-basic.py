# -*- coding: utf-8 -*-
"""5장 실습 5-4: 부트스트랩.
A. 제1권 11장 계산 11-4(유전자 다양도 H의 부트스트랩, 2만 회, 시드 11)를 되풀이한다.
B. 재표집 횟수 B를 바꾸면 구간 끝이 얼마나 흔들리는가.
C. 구간이 말한 만큼 맞는가: 덮개율(coverage) 시뮬레이션.
D. 시연값 연속 자료(가상 값)에서 퍼센타일, BCa, t 구간 비교.
실행: python3 bootstrap-basic.py | tee bootstrap-basic.log
"""
import time, platform, math, json
J = {'cont': [], 'hdiv': []}
import numpy as np
import scipy
from scipy import stats

T0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))


def nei(c):
    n = sum(c)
    if n < 2:
        return float('nan')
    return n / (n - 1) * (1 - sum((x / n) ** 2 for x in c))


def nei_vec(cnt):
    n = cnt.sum(axis=1, keepdims=True)
    return (n[:, 0] / (n[:, 0] - 1)) * (1 - ((cnt / n) ** 2).sum(axis=1))


GROUPS = [('신석기 합', [16, 1, 1]), ('대산전', [1, 3, 1, 2, 2]), ('대전자', [3, 2])]
print('\n== A. 제1권 계산 11-4 되풀이 (제1권과 같은 코드·같은 시드 11·2만 회, 세 집단을 같은 난수열로 차례로) ==')
for nm, c in GROUPS:
    print('  %-8s 관측 H = %.4f' % (nm, nei(c)))
rng = np.random.default_rng(11)


def boot_v1(c, B=20000):          # 제1권의 구현
    n = sum(c); pr = np.array(c) / n
    hs = []
    for _ in range(B):
        k = rng.multinomial(n, pr)
        hs.append(nei([int(x) for x in k if x > 0]) if n > 1 else 0)
    hs = np.array([h for h in hs if not math.isnan(h)])
    return np.percentile(hs, [2.5, 50, 97.5])


t = time.perf_counter()
res_v1 = {}
for nm, c in GROUPS:
    res_v1[nm] = boot_v1(c)
    lo, md, hi = res_v1[nm]
    print('  %-8s 부트스트랩 H: 2.5%% %.3f 중앙 %.3f 97.5%% %.3f' % (nm, lo, md, hi))
print('  (제1권: 신석기 합 0.000 / 0.209 / 0.464, 대산전 0.556 / 0.778 / 0.889, 대전자 0.000 / 0.600 / 0.600) %.1f초' % (time.perf_counter() - t))
# 한 줄 구현이 같은 난수열에서 같은 값을 내는가
rng = np.random.default_rng(11)
same = True
for nm, c in GROUPS:
    n = sum(c)
    cnt = rng.multinomial(n, np.array(c) / n, size=20000)
    lo, md, hi = np.percentile(nei_vec(cnt), [2.5, 50, 97.5])
    ok = np.allclose([lo, md, hi], res_v1[nm])
    same &= ok
    print('  벡터 구현 %-8s %.3f / %.3f / %.3f  제1권 구현과 %s' % (nm, lo, md, hi, '일치' if ok else '불일치'))
print('  한 번에 size=B로 뽑는 방식이 반복문과 같은 값을 냈는가:', same)

print('\n== A2. 구간의 모양: 이산 분포라 끝이 정확히 어디에 걸리는가 ==')
for nm, c in GROUPS:
    n = sum(c); rg = np.random.default_rng(12)
    cnt = rg.multinomial(n, np.array(c) / n, size=200000)
    h = nei_vec(cnt)
    print('  %-8s H=0인 재표집 비율 %.4f, 서로 다른 H 값의 개수 %d, 관측 H 이상인 비율 %.3f' % (nm, (h < 1e-12).mean(), len(np.unique(np.round(h, 10))), (h >= nei(c) - 1e-12).mean()))
print('  [16,1,1]의 재표집에서 H=0이 될 확률(모두 같은 형) = (16/18)^18 = %.4f' % ((16 / 18) ** 18))
print('  재표집은 관측에 없는 하플로그룹을 만들 수 없다: [16,1,1]에서 새 형이 나올 수 없고 H의 위쪽 끝도 표본이 이미 가진 형에 갇힌다.')

print('\n== B. 재표집 횟수 B에 따른 구간 끝의 흔들림 (시드 20개, 각 B마다) ==')
print('%-8s %10s | %-25s | %-25s | %-25s | %8s' % ('집단', 'B', '2.5% 끝: 평균 / 표준편차', '97.5% 끝: 평균 / 표준편차', '중앙: 평균 / 표준편차', '시간(초)'))
for nm, c in GROUPS:
    n = sum(c); pr = np.array(c) / n
    for B in (100, 1000, 10000, 100000, 1000000):
        reps = 20 if B <= 100000 else 5
        t = time.perf_counter()
        L, M_, U = [], [], []
        for s in range(reps):
            rg = np.random.default_rng(900 + s)
            cnt = rg.multinomial(n, pr, size=B)
            lo, md, hi = np.percentile(nei_vec(cnt), [2.5, 50, 97.5])
            L.append(lo); M_.append(md); U.append(hi)
        J['hdiv'].append(dict(g=nm, B=B, lo=float(np.mean(L)), lo_sd=float(np.std(L, ddof=1)), hi=float(np.mean(U)), hi_sd=float(np.std(U, ddof=1))))
        print('%-8s %10s | %8.3f / %-14.4f | %8.3f / %-14.4f | %8.3f / %-12.4f | %8.2f' % (
            nm, '{:,}'.format(B), np.mean(L), np.std(L, ddof=1), np.mean(U), np.std(U, ddof=1), np.mean(M_), np.std(M_, ddof=1), time.perf_counter() - t))

print('\n== C. 덮개율: "95% 구간"이 참값을 95%만큼 덮는가 (모집단 빈도 = 관측 빈도라고 놓고 시뮬레이션) ==')
print('모집단의 참값 H0 = 1 - sum p^2 (표본 H는 n/(n-1) 보정이 있어 불편추정이다)')
REP, BB = 2000, 1000
for nm, c in GROUPS:
    n = sum(c); pr = np.array(c) / n
    H0 = 1 - (pr ** 2).sum()
    rg = np.random.default_rng(555)
    t = time.perf_counter()
    cover = 0; mean_h = 0.0; wid = 0.0; undef = 0
    for r in range(REP):
        samp = rg.multinomial(n, pr)
        cnt = rg.multinomial(n, samp / n, size=BB)
        h = nei_vec(cnt)
        lo, hi = np.percentile(h, [2.5, 97.5])
        cover += (lo <= H0 <= hi); wid += hi - lo
        mean_h += nei(list(samp[samp > 0]))
    print('  %-8s n=%2d 참값 H0 = %.4f, 표본 H의 평균 %.4f, 구간이 H0를 덮은 비율 %.3f (목표 0.95), 평균 폭 %.3f  (%.1f초)' % (nm, n, H0, mean_h / REP, cover / REP, wid / REP, time.perf_counter() - t))

print('\n== D. 시연값 연속 자료(가상 값)에서 구간 비교: 로그정규 표본 n=18 ==')
rs = np.random.default_rng(42)
mu, sg = 1.0, 0.8
x = np.round(rs.lognormal(mu, sg, 18), 3)         # 시연값
true_mean = math.exp(mu + sg * sg / 2)
print('시연 표본(시드 42): n=%d, 평균 %.3f, 중앙값 %.3f, 표준편차 %.3f / 모집단 참 평균 %.3f' % (len(x), x.mean(), np.median(x), x.std(ddof=1), true_mean))
tci = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
print('t 구간 %.3f ~ %.3f' % tci)
for meth in ('percentile', 'basic', 'BCa'):
    r = stats.bootstrap((x,), np.mean, n_resamples=9999, confidence_level=0.95, method=meth, random_state=np.random.default_rng(1))
    print('scipy.bootstrap %-10s 평균의 구간 %.3f ~ %.3f (표준오차 %.3f)' % (meth, r.confidence_interval.low, r.confidence_interval.high, r.standard_error))
print('이 실습: 같은 표본에서 B에 따른 퍼센타일 구간(시드 20개)')
print('%10s %22s %22s %10s' % ('B', '2.5% 끝 평균 / 표준편차', '97.5% 끝 평균 / 표준편차', '시간(초)'))
for B in (100, 1000, 10000, 100000, 1000000):
    reps = 20 if B <= 100000 else 5
    t = time.perf_counter(); L = []; U = []
    for s in range(reps):
        rg = np.random.default_rng(1200 + s)
        m = np.empty(B)
        done = 0
        while done < B:
            k = min(100000, B - done)
            m[done:done + k] = x[rg.integers(0, len(x), size=(k, len(x)))].mean(axis=1)
            done += k
        lo, hi = np.percentile(m, [2.5, 97.5]); L.append(lo); U.append(hi)
    J['cont'].append(dict(B=B, lo=float(np.mean(L)), lo_sd=float(np.std(L, ddof=1)), hi=float(np.mean(U)), hi_sd=float(np.std(U, ddof=1))))
    print('%10s %12.4f / %-8.4f %12.4f / %-8.4f %10.2f' % ('{:,}'.format(B), np.mean(L), np.std(L, ddof=1), np.mean(U), np.std(U, ddof=1), time.perf_counter() - t))

print('\n== D2. 덮개율: 로그정규 모집단에서 표본 크기별 평균의 95% 구간 ==')
print('%6s %14s %14s %12s' % ('n', 't 구간 덮개율', '퍼센타일 덮개율', '평균 폭(퍼센타일)'))
for n in (5, 10, 18, 40, 100):
    rg = np.random.default_rng(300 + n)
    R, B = 3000, 1000
    ct = cp = 0; w = 0.0
    for r in range(R):
        s = rg.lognormal(mu, sg, n)
        se = s.std(ddof=1) / math.sqrt(n); tc = stats.t.ppf(0.975, n - 1)
        ct += (s.mean() - tc * se <= true_mean <= s.mean() + tc * se)
        m = s[rg.integers(0, n, size=(B, n))].mean(axis=1)
        lo, hi = np.percentile(m, [2.5, 97.5]); cp += (lo <= true_mean <= hi); w += hi - lo
    print('%6d %14.3f %14.3f %12.3f' % (n, ct / R, cp / R, w / R))
print('\n걸린 시간 %.1f초' % (time.perf_counter() - T0))
json.dump(J, open('bootstrap-basic.json', 'w'))
