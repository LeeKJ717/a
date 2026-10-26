# -*- coding: utf-8 -*-
"""5장 실습 5-8: 자기상관이 있는 두 계열의 상관은 얼마나 쉽게 '유의'해지는가.
제1권 11장 계산 11-9(유효 표본 크기 n_eff)를 시뮬레이션으로 점검한다.
서로 독립인 1차 자기회귀(AR(1)) 계열 쌍을 많이 만들어 상관 r의 분포를 직접 잰다. 모든 계열은 이 책이 만든 시연값이다.
A. 순진한 임계값(n = 414)의 거짓 양성률과 n_eff 임계값의 거짓 양성률.
B. 제1권의 r = -0.18이 두 계열이 모두 AR(1) 0.72인 귀무 아래에서 얼마나 드문가.
C. 이동평균을 한 계열의 경우.
D. 순열 검정 두 가지: 계열을 아무렇게나 섞기(자기상관 파괴) 대 원형 이동(자기상관 보존).
실행: python3 autocorr-null.py | tee autocorr-null.log
"""
import time, platform, json
J = {'A': []}
from math import sqrt
import numpy as np
import scipy
from scipy import stats
from scipy.signal import lfilter

T0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
n = 414


def rcrit(nn, al):
    tc = stats.t.isf(al / 2, nn - 2)
    return tc / sqrt(nn - 2 + tc * tc)


def ar1(rg, rho, reps, n, burn=300):
    e = rg.standard_normal((reps, n + burn))
    if rho == 0:
        return e[:, burn:]
    return lfilter([sqrt(1 - rho * rho)], [1.0, -rho], e, axis=1)[:, burn:]


def corr_rows(x, y):
    x = x - x.mean(axis=1, keepdims=True); y = y - y.mean(axis=1, keepdims=True)
    return (x * y).sum(axis=1) / np.sqrt((x * x).sum(axis=1) * (y * y).sum(axis=1))


def simulate(r1, r2, reps, seed, chunk=4000):
    rg = np.random.default_rng(seed)
    out = []
    left = reps
    while left > 0:
        m = min(chunk, left)
        out.append(corr_rows(ar1(rg, r1, m, n), ar1(rg, r2, m, n)))
        left -= m
    return np.concatenate(out)


print('\n== A. 서로 독립인 두 AR(1) 계열 (길이 414)의 상관 r: 순진한 임계값과 n_eff 임계값에서의 거짓 양성률 ==')
print('순진한 임계 r (n=414): 5%% %.4f, 1%% %.4f' % (rcrit(n, .05), rcrit(n, .01)))
print('%-12s %8s | %10s %10s | %10s %10s | %-34s' % ('(rho1, rho2)', '쌍 수', '|r| 95%', '|r| 99%', '순진 5%', '순진 1%', 'n_eff 공식 n(1-r1r2)/(1+r1r2): n_eff, 거짓 양성 5% / 1%'))
t = time.perf_counter()
cases = [(0.0, 0.0), (0.3, 0.3), (0.5, 0.5), (0.72, 0.72), (0.9, 0.9), (0.72, 0.0), (0.72, 0.3)]
store = {}
for i, (a, b) in enumerate(cases):
    reps = 20000
    r = simulate(a, b, reps, 1000 + i)
    store[(a, b)] = r
    ar = np.abs(r)
    ne = n * (1 - a * b) / (1 + a * b)
    c5, c1 = rcrit(int(round(ne)), .05), rcrit(int(round(ne)), .01)
    J['A'].append(dict(r1=a, r2=b, naive5=float((ar >= rcrit(n, .05)).mean()), naive1=float((ar >= rcrit(n, .01)).mean()), neff=ne, neff5=float((ar >= c5).mean()), neff1=float((ar >= c1).mean())))
    print('(%.2f,%.2f) %10d | %10.4f %10.4f | %9.3f %10.3f | n_eff=%6.1f 임계 %.3f/%.3f -> %.3f / %.3f' % (
        a, b, reps, np.quantile(ar, .95), np.quantile(ar, .99), (ar >= rcrit(n, .05)).mean(), (ar >= rcrit(n, .01)).mean(), ne, c5, c1, (ar >= c5).mean(), (ar >= c1).mean()))
print('(시간 %.1f초)' % (time.perf_counter() - t))
print('\n제1권 계산 11-9의 "한 계열만 자기상관 0.72이면 n_eff = 67.4" 점검: 식 n(1-rho)/(1+rho)로 얻은 값이다.')
ne1 = n * (1 - 0.72) / (1 + 0.72)
ar = np.abs(store[(0.72, 0.0)])
print('  n_eff = %.1f로 임계 r을 잡으면 5%% %.3f, 1%% %.3f. 실제 (0.72, 0) 쌍의 거짓 양성률: %.4f / %.4f (목표 0.05 / 0.01)' % (ne1, rcrit(int(round(ne1)), .05), rcrit(int(round(ne1)), .01), (ar >= rcrit(int(round(ne1)), .05)).mean(), (ar >= rcrit(int(round(ne1)), .01)).mean()))
print('  순진한 임계(n=414)의 거짓 양성률: %.4f / %.4f' % ((ar >= rcrit(n, .05)).mean(), (ar >= rcrit(n, .01)).mean()))

print('\n== B. 제1권의 r = -0.18: 두 계열이 모두 AR(1) rho = 0.72인 독립 계열일 때 |r| >= 0.18은 얼마나 드문가 ==')
t = time.perf_counter()
big = simulate(0.72, 0.72, 400000, 777)
ab = np.abs(big)
k = int((ab >= 0.18).sum())
print('독립 쌍 400,000개 중 |r| >= 0.18: %d개 -> 양쪽 p = (%d+1)/(400000+1) = %.5f (시간 %.1f초)' % (k, k, (k + 1) / 400001, time.perf_counter() - t))
print('이 분포의 |r| 95%% %.4f, 99%% %.4f (n_eff = 131.3 임계: 0.172, 0.224)' % (np.quantile(ab, .95), np.quantile(ab, .99)))
print('독립을 가정한 p = 2.3e-04와 비교: 같은 r이 자기상관을 반영하면 %.5f이다 (몬테카를로 표준오차 약 %.5f).' % ((k + 1) / 400001, sqrt(((k + 1) / 400001) * (1 - (k + 1) / 400001) / 400001)))
print('(이 결과는 "두 계열의 자기상관이 모두 0.72"라는 가정 위에 있다. 북반구 복원 쪽의 자기상관을 이 책은 알지 못한다.)')

print('\n== C. 이동평균을 한 백색잡음 두 개 (창 11, 원 계열 424개에서 이동평균 414개를 얻음) ==')
rg = np.random.default_rng(555)
reps = 20000
w = 11
res = []; ne_list = []; rho_list = []
for s in range(reps // 4000):
    x = rg.standard_normal((4000, n + w - 1)); y = rg.standard_normal((4000, n + w - 1))
    cs = np.cumsum(np.concatenate([np.zeros((4000, 1)), x], axis=1), axis=1); xm = (cs[:, w:] - cs[:, :-w]) / w
    cs = np.cumsum(np.concatenate([np.zeros((4000, 1)), y], axis=1), axis=1); ym = (cs[:, w:] - cs[:, :-w]) / w
    res.append(corr_rows(xm, ym))
    xc = xm - xm.mean(axis=1, keepdims=True); yc = ym - ym.mean(axis=1, keepdims=True)
    rx = (xc[:, 1:] * xc[:, :-1]).sum(axis=1) / (xc * xc).sum(axis=1); ry = (yc[:, 1:] * yc[:, :-1]).sum(axis=1) / (yc * yc).sum(axis=1)
    ne_list.append(xm.shape[1] * (1 - rx * ry) / (1 + rx * ry)); rho_list.append(rx)
r = np.concatenate(res); ne_all = np.concatenate(ne_list); nn = xm.shape[1]
print('길이 %d, 표본 1차 자기상관의 평균 %.3f (참고: 이론값 1-1/11 = %.3f), 공식 n_eff의 평균 %.1f' % (nn, np.concatenate(rho_list).mean(), 1 - 1 / 11, ne_all.mean()))
ar = np.abs(r)
print('순진한 임계(n=%d) 5%% %.3f, 1%% %.3f -> 거짓 양성률 %.3f / %.3f' % (nn, rcrit(nn, .05), rcrit(nn, .01), (ar >= rcrit(nn, .05)).mean(), (ar >= rcrit(nn, .01)).mean()))
c5 = np.array([rcrit(max(int(round(v)), 4), .05) for v in ne_all]); c1 = np.array([rcrit(max(int(round(v)), 4), .01) for v in ne_all])
print('표본의 1차 자기상관으로 n_eff를 구해 임계를 잡으면 거짓 양성률 %.3f / %.3f (목표 0.05 / 0.01)' % ((ar >= c5).mean(), (ar >= c1).mean()))
print('|r| 95%% %.3f, 99%% %.3f' % (np.quantile(ar, .95), np.quantile(ar, .99)))

print('\n== D. 순열 검정 두 가지의 거짓 양성률 (두 계열 AR(1) 0.72, 길이 414, 독립) ==')
rg = np.random.default_rng(31415)
PAIRS = 3000
fp_shuffle = {0.05: 0, 0.01: 0}; fp_shift = {0.05: 0, 0.01: 0}
NP = 499
t = time.perf_counter()
for i in range(PAIRS):
    x = ar1(rg, 0.72, 1, n)[0]; y = ar1(rg, 0.72, 1, n)[0]
    r0 = np.corrcoef(x, y)[0, 1]
    # 원형 이동: 모든 이동량의 상관을 FFT로 한 번에 (이동 0이 관측)
    xc = x - x.mean(); yc = y - y.mean()
    cc = np.fft.irfft(np.fft.rfft(xc) * np.conj(np.fft.rfft(yc)), n=n) / np.sqrt((xc * xc).sum() * (yc * yc).sum())
    p_shift = (np.abs(cc) >= abs(r0) - 1e-12).sum() / n
    # 아무렇게나 섞기: 499번
    perms = np.argsort(rg.random((NP, n)), axis=1)
    rs = corr_rows(np.broadcast_to(x, (NP, n)), y[perms])
    p_shuf = (1 + (np.abs(rs) >= abs(r0)).sum()) / (NP + 1)
    for al in (0.05, 0.01):
        fp_shuffle[al] += p_shuf <= al; fp_shift[al] += p_shift <= al
print('독립 쌍 %d개: 거짓 양성률' % PAIRS)
print('  아무렇게나 섞기(499회):  5%% 수준 %.3f, 1%% 수준 %.3f' % (fp_shuffle[0.05] / PAIRS, fp_shuffle[0.01] / PAIRS))
print('  원형 이동(414가지 이동): 5%% 수준 %.3f, 1%% 수준 %.3f   (시간 %.1f초)' % (fp_shift[0.05] / PAIRS, fp_shift[0.01] / PAIRS, time.perf_counter() - t))
print('몬테카를로 오차: 3000쌍에서 비율 0.05의 표준오차 %.4f, 0.01의 표준오차 %.4f' % (sqrt(.05 * .95 / PAIRS), sqrt(.01 * .99 / PAIRS)))
print('\n걸린 시간 %.1f초' % (time.perf_counter() - T0))
json.dump(J, open('autocorr-null.json', 'w'))
