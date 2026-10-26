# -*- coding: utf-8 -*-
"""4장 실습 4-12의 보충: 같은 계산의 시간이 실행마다 얼마나 흔들리는가
같은 계산을 7번 되풀이해 최소, 중앙값, 최대를 적는다. 이 컨테이너는 다른 작업과 CPU를 나누어 쓰는 것으로 보이며(확인하지 못함) 시간이 크게 흔들린다.
실행: python3 ch04-07-timing-variance.py
"""
import os, time, platform
import numpy as np, scipy, scipy.signal as ss
TWO_PI = 2 * np.pi
print('파이썬 %s, numpy %s, scipy %s, 논리 코어 %s' % (platform.python_version(), np.__version__, scipy.__version__, os.cpu_count()))
z = np.arange(0, 552.0)
rate = 0.92 * (1 + 0.30 * np.sin(TWO_PI * z / 220.0 + 0.4))
age = np.concatenate([[0], np.cumsum(1.0 / (0.5 * (rate[1:] + rate[:-1])))])
T = age[-1]
fgrid = np.arange(1 / T, 0.45, 1 / (4 * T)); F = len(fgrid)
rng = np.random.default_rng(7)
y = rng.standard_normal(len(age)); y -= y.mean()
om = TWO_PI * fgrid[None, :]
tau = np.arctan2(np.sin(2 * om * age[:, None]).sum(0), np.cos(2 * om * age[:, None]).sum(0)) / (2 * om[0])
arg = om * (age[:, None] - tau[None, :])
C, S = np.cos(arg), np.sin(arg)
cc, s2 = (C * C).sum(0), (S * S).sum(0)
Y = rng.standard_normal((5000, len(age))); Y -= Y.mean(axis=1, keepdims=True)
t_sc, t_mm = [], []
for rep in range(7):
    load = os.getloadavg()[0]
    a = time.perf_counter()
    for _ in range(10): ss.lombscargle(age, y, TWO_PI * fgrid, normalize=True, floating_mean=True)
    t_sc.append((time.perf_counter() - a) / 10 * 1e3)
    a = time.perf_counter()
    yc = Y @ C; ys = Y @ S
    P = (yc * yc / cc + ys * ys / s2) / (Y * Y).sum(axis=1, keepdims=True)
    t_mm.append((time.perf_counter() - a) / 5000 * 1e3)
    print('  반복 %d: scipy lombscargle %.1f ms/회, 행렬곱 방식 %.3f ms/개 (5000개 묶음), 1분 평균 부하 %.2f' % (rep + 1, t_sc[-1], t_mm[-1], load))
print('scipy lombscargle ms/회: 최소 %.1f, 중앙값 %.1f, 최대 %.1f' % (min(t_sc), np.median(t_sc), max(t_sc)))
print('행렬곱 방식 ms/개: 최소 %.3f, 중앙값 %.3f, 최대 %.3f' % (min(t_mm), np.median(t_mm), max(t_mm)))
