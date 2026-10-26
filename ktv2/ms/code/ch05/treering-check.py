# -*- coding: utf-8 -*-
"""5장 실습 5-5: 제1권 11장 노백산 나이테 회귀의 검증 통계를 scipy와 numpy로 처음부터 되풀이한다.
입력은 Lyu 등(2016)의 본문 값(제1권 11.5절이 옮긴 값)이다: Y = 2.987 X + 4.829, N = 58, r = 0.757, R2 = 0.573,
표 3의 R = 0.414, 0.632, 반 기간 29년, 부호 검정 (20, 9)와 (22, 7). 논문의 연별 자료는 없다.
RE와 CE의 6년 예는 제1권이 만든 시연값이다.
실행: python3 treering-check.py | tee treering-check.log
"""
import time, platform
from math import comb, sqrt, atanh, tanh
import numpy as np
import scipy
from scipy import stats

T0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))

print('\n== A. 회귀 통계 (제1권 계산 11-5) ==')
N, r, R2p = 58, 0.757, 0.573
a_, b_ = 4.829, 2.987
print('r^2 = %.5f (논문 R2 0.573)' % (r * r))
R2adj = 1 - (1 - R2p) * (N - 1) / (N - 2)
print('조정 R2 = 1 - (1-0.573)(57)/(56) = %.4f (논문 0.565)' % R2adj)
F1 = R2p * (N - 2) / (1 - R2p)
F2 = r * r * (N - 2) / (1 - r * r)
print('F = R2(N-2)/(1-R2): R2=0.573 -> %.3f ; R2=r^2 -> %.3f (논문 75.161)' % (F1, F2))
t = r * sqrt(N - 2) / sqrt(1 - r * r)
print('t = %.4f, t^2 = %.3f, 양쪽 p = %.2e' % (t, t * t, 2 * stats.t.sf(t, N - 2)))
for al in (0.05, 0.01):
    tc = stats.t.isf(al / 2, N - 2)
    print('임계 r (N=58, 양쪽 %.2f) = %.4f' % (al, tc / sqrt(N - 2 + tc * tc)))
# 처음부터 구현: 상관의 t 분포 p를 사다리꼴 적분 없이 베타 함수로 (scipy.special 사용)
from scipy import special
pbeta = special.betainc((N - 2) / 2, 0.5, (N - 2) / ((N - 2) + t * t))
print('불완전 베타 함수로 구한 양쪽 p = %.2e (scipy.stats.t.sf와 %s)' % (pbeta, '일치' if abs(pbeta - 2 * stats.t.sf(t, N - 2)) < 1e-15 else '다름'))
print('Y(X): X=0.80 -> %.3f, 1.00 -> %.3f, 1.20 -> %.3f' % (b_ * .8 + a_, b_ + a_, b_ * 1.2 + a_))
print('복원 평균 7.66이 되는 X = %.4f / 복원 표준편차 0.53 <-> X의 표준편차 %.4f / 표 1 std 0.20 x 2.987 = %.3f (논문 0.53)' % ((7.66 - a_) / b_, 0.53 / b_, 2.987 * 0.20))

print('\n== A2. 이 책의 추가 계산: 불확실성 (논문에 수치가 없는 것, 가정을 밝힌다) ==')
se_b = b_ / t
print('기울기의 표준오차 = 기울기 / t = %.4f / %.3f = %.4f (가정: b, r, N이 같은 최소제곱 회귀에서 나온 값이다)' % (b_, t, se_b))
tc = stats.t.isf(0.025, N - 2)
print('기울기의 95%% 구간 = %.3f ~ %.3f (t 임계 %.3f)' % (b_ - tc * se_b, b_ + tc * se_b, tc))
z = atanh(r); sez = 1 / sqrt(N - 3)
lo, hi = tanh(z - 1.96 * sez), tanh(z + 1.96 * sez)
print('Fisher z 변환으로 r의 95%% 구간 = %.3f ~ %.3f, R2로는 %.3f ~ %.3f (연별 자료 없이 r과 N만으로 구한 구간)' % (lo, hi, lo * lo, hi * hi))
print('(참고: 이 구간은 연속한 해가 서로 독립이라는 가정에서 나온다. 나이테 자료는 자기상관이 있어 실제로는 더 넓을 수 있다. 이 장의 자기상관 절 참조)')

print('\n== B. 표 3의 일관성 (제1권 계산 11-6) ==')
for rr, lab in ((0.414, '0.414(a)'), (0.632, '0.632(b)'), (0.757, '0.757(b)'), (0.738, '0.738 (제1권 계산 11-6 항목 2에 적힌 값)')):
    print('R=%s  R^2 = %.4f' % (lab, rr * rr))
for nn in (29, 58):
    for al in (0.05, 0.01):
        tc = stats.t.isf(al / 2, nn - 2)
        print('임계 r (n=%d, 양쪽 %.2f) = %.4f' % (nn, al, tc / sqrt(nn - 2 + tc * tc)))
print('0.414는 n=29의 5% 임계(0.367)를 넘고 1% 임계(0.470)에는 못 미친다 -> 별표 a와 맞는다. 0.632는 1%를 넘는다 -> b와 맞는다.')
print('0.757은 N=58의 1% 임계(0.336)를 넘는다. n=29의 임계(0.470)와 견줄 필요가 없는 전 기간 값이다.')


def binom_two(k, n):
    """정확한 이항 검정(p=0.5) 양쪽: 꼬리의 두 배(대칭이므로 확률 이하 합과 같다)."""
    tail = sum(comb(n, i) for i in range(max(k, n - k), n + 1)) / 2 ** n
    return min(1.0, 2 * tail), tail


print('\n부호 검정 (n=29, p=0.5): 처음부터 구한 값과 scipy.stats.binomtest')
for k in (20, 22, 21, 19, 23):
    p2, p1 = binom_two(k, 29)
    ref = stats.binomtest(k, 29, 0.5).pvalue
    print('  (%d, %d): 양쪽 %.4f (scipy %.4f), 한쪽 %.4f' % (k, 29 - k, p2, ref, p1))
print('29회에서 양쪽 5%를 넘으려면 한쪽이 최소 몇 번이어야 하는가:', min(k for k in range(15, 30) if binom_two(k, 29)[0] < 0.05), '(이 값 이상)')
print('(20, 9)는 양쪽 p = 0.0614이므로 5%에 못 미친다. 한쪽 0.0307은 5%를 넘는다. 제1권 계산 11-6과 같다.')
print('20+9 = 22+7 = 29 = 58/2')

print('\n"27/30" 사건 일치 (이항, 일치율 p는 가정):')
for p in (0.5, 0.6, 0.7):
    print('  p=%.1f: P(X>=27|n=30) = %.3e (scipy %.3e)' % (p, sum(comb(30, i) * p ** i * (1 - p) ** (30 - i) for i in range(27, 31)), stats.binom.sf(26, 30, p)))

print('\n== C. 1차 차분 상관과 북반구 복원과의 상관 (제1권 계산 11-9 앞부분) ==')
tt = 0.12 * sqrt(55) / sqrt(1 - 0.12 ** 2)
print('1차 차분 r=0.12, n=57: t = %.3f, p = %.3f (논문 p>0.05)' % (tt, 2 * stats.t.sf(tt, 55)))
tt = 0.18 * sqrt(412) / sqrt(1 - 0.18 ** 2)
print('북반구 복원 r=-0.18, n=414 독립 가정: t = %.2f, p = %.2e' % (tt, 2 * stats.t.sf(tt, 412)))

print('\n== D. RE와 CE의 6년 시연값 (제1권 계산 11-7) ==')
obs = [7.0, 7.4, 7.9, 7.2, 8.1, 7.6]
est = [7.2, 7.3, 7.6, 7.5, 7.8, 7.5]
cal_mean = 7.5
# 순수 파이썬
sse = sum((o - e) ** 2 for o, e in zip(obs, est))
ss_cal = sum((o - cal_mean) ** 2 for o in obs)
vm = sum(obs) / len(obs)
ss_ver = sum((o - vm) ** 2 for o in obs)
RE = 1 - sse / ss_cal; CE = 1 - sse / ss_ver
print('순수 파이썬: SSE = %.4f, 보정 평균 기준 %.4f, 검증 평균 기준 %.4f, 검증 평균 %.4f' % (sse, ss_cal, ss_ver, vm))
print('RE = %.4f, CE = %.4f (제1권 0.6250, 0.6221)' % (RE, CE))
o, e = np.array(obs), np.array(est)
re2 = 1 - ((o - e) ** 2).sum() / ((o - cal_mean) ** 2).sum()
ce2 = 1 - ((o - e) ** 2).sum() / ((o - o.mean()) ** 2).sum()
print('numpy: RE = %.4f, CE = %.4f, r = %.4f (제1권 0.8808), r^2 = %.4f' % (re2, ce2, np.corrcoef(o, e)[0, 1], np.corrcoef(o, e)[0, 1] ** 2))
print('CE <= RE: %s (%.4f <= %.4f)' % (ce2 <= re2, ce2, re2))
print('\n걸린 시간 %.2f초' % (time.perf_counter() - T0))
