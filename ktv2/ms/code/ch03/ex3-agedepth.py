# -*- coding: utf-8 -*-
"""실습 3-3: 연령-깊이 모형. (가) 선형 보간(곡선 불필요), (나) 오차를 실은 몬테카를로 보간(곡선 불필요 / 필요),
제1권 6장 계산 6-4, 6-5 와 9장 계산 9-11 의 값과 견준다."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from c14lib import *

def chk(label, mine, vol1, tol):
    ok = abs(mine - vol1) <= tol
    print(f'  {label}: 이 책 {mine:.3f} / 제1권 {vol1} -> {"일치" if ok else "어긋남"}')
    return ok

print('=' * 70)
print('[3-3a] 9장 계산 9-11: 세 점 (55 cm, 1475 CE), (115 cm, 224 CE), (180 cm, -186 CE) 의 선형 보간')
dep = np.array([55.0, 115.0, 180.0]); yr = np.array([1475.0, 224.0, -186.0])
print('  구간 속도(mm/yr):', [round(float(10 * (dep[i + 1] - dep[i]) / (yr[i] - yr[i + 1])), 3) for i in range(2)], ' (제1권 0.480, 1.585)')
def depth_at(y):
    # 깊이는 아래로 늘고 연도는 줄어든다. np.interp 는 x 가 오름차순이어야 하므로 뒤집는다.
    return float(np.interp(y, yr[::-1], dep[::-1], left=np.nan, right=np.nan))
ev = [('132 BCE', -131, 171.3), ('109 BCE', -108, 167.6), ('69 CE', 69, 139.6), ('944 CE', 944, 80.5), ('1128 CE', 1128, 71.6), ('1448 CE', 1448, 56.3)]
ok = True
for n, y, v1 in ev:
    ok &= chk(f'{n} 깊이(cm)', depth_at(y), v1, 0.06)
print('  전부 일치:', ok)

print('=' * 70)
print('[3-3b] 6장 계산 6-4, 6-5: GY-1 (제1권 표 6-5 의 보정 범위 중간값 사이 선형 보간)')
gy = [(363, 1625, 1819), (739, 2846, 2997), (889, 4578, 4825), (917, 6863, 7157), (1416, 7956, 8158), (1839, 8595, 8976), (2060, 8649, 8990), (2351, 8764, 9024), (2892, 9785, 10173)]
gd = np.array([g[0] for g in gy], float); gm = np.array([(g[1] + g[2]) / 2 for g in gy])
v1rate = [0.313, 0.084, 0.012, 0.477, 0.581, 6.50, 3.91, 0.499]
rates = np.diff(gd) / np.diff(gm)
print('  구간 퇴적률(cm/yr):', [round(float(r), 3) for r in rates])
print('  제1권 표 6-5:', v1rate, ' 최대 차이', round(float(np.max(np.abs(rates - np.array(v1rate)))), 3))
for a, v1 in ((8200, 1499), (8400, 1615), (8000, 1389)):
    d = float(np.interp(a, gm, gd))
    print(f'  {a} cal BP 깊이 = {d:.1f} cm (제1권 약 {v1})')
print('  8.2 ka 근처에서 위아래 연대 사이 공백:', f'{gd[5]-gd[4]:.0f} cm, {gm[5]-gm[4]:.1f} 년')

print('=' * 70)
print('[3-3c] 몬테카를로 연령-깊이 (HZ 세 점, 정규 오차). 제1권 9장의 점 추정이 얼마나 불확실한지')
rng = np.random.default_rng(20261026)
N = 400_000
# 점 1: 475 +- 20 (제1권의 읽기를 따라 1475 CE +- 20 으로 둔다). 점 2, 3: OSL 1.80+-0.22 ka, 2.21+-0.41 ka (채취 2024 가정, 시연)
mu = np.array([1475.0, 2024 - 1805.0, 2024 - 2209.0]); sg = np.array([20.0, 223.0, 410.0])
# 제1권 표의 반올림 값(1.80, 2.21)과 제1권 계산 9-11 의 224, -186 을 쓰려면 다음 줄을 쓴다
mu = np.array([1475.0, 224.0, -186.0])
draws = rng.normal(mu, sg, size=(N, 3))
mono = (draws[:, 0] > draws[:, 1]) & (draws[:, 1] > draws[:, 2])
acc = draws[mono]
print(f'  뽑은 {N} 중 깊이가 늘 때 나이도 늙는 순서를 지킨 것: {mono.sum()} ({100*mono.mean():.1f}%)')
print('  순서를 지킨 뽑기만 남기면 점 2와 3의 분포가 달라진다(조건부):', f'점 2 평균 {acc[:,1].mean():.0f} (원래 224), 점 3 평균 {acc[:,2].mean():.0f} (원래 -186)')
def depth_draws(ys, y):
    """각 뽑기의 세 점에서 연도 y 의 깊이. 맨 위 점보다 젊거나 맨 아래 점보다 늙으면 가까운 구간의 직선을 연장(외삽)한다."""
    d = np.empty(len(ys))
    up = y > ys[:, 1]                      # 두 번째 점보다 젊다: 첫 구간의 직선
    d[up] = 55 + (ys[up, 0] - y) / (ys[up, 0] - ys[up, 1]) * 60
    lo = ~up                               # 두 번째 점보다 늙다: 둘째 구간의 직선
    d[lo] = 115 + (ys[lo, 1] - y) / (ys[lo, 1] - ys[lo, 2]) * 65
    return d
print('  사건 연도의 깊이(cm): 점 추정(제1권) | 몬테카를로 중앙값, 95% 구간 | 외삽이 된 뽑기 비율(55 cm 위쪽 / 180 cm 아래쪽)')
for n, y, v1 in ev:
    d = depth_draws(acc, y)
    q = np.percentile(d, [2.5, 50, 97.5])
    hi = f'{q[2]:6.1f}' if q[2] <= 180 else '>180 (외삽)'
    md = f'{q[1]:6.1f}' if q[1] <= 180 else '>180 (외삽)'
    print(f'    {n:8s} {v1:6.1f} | {md}  [{q[0]:6.1f}, {hi}] | {100*np.mean(d<55):.1f}% / {100*np.mean(d>180):.1f}%')
print('  층 경계: U1 220-165, U2 165-140, U3 140-95, U4 95-70, U5 70-30, U6 30-0 cm')
d = depth_draws(acc, -131)
print(f'  132 BCE 가 U2(140~165 cm) 안에 놓일 비율: {100*np.mean((d>=140)&(d<=165)):.1f}%, U1(165 cm 아래)에 놓일 비율: {100*np.mean(d>165):.1f}%')
d = depth_draws(acc, 944)
print(f'  944 CE 가 U4(70~95 cm) 안에 놓일 비율: {100*np.mean((d>=70)&(d<=95)):.1f}%')

print('=' * 70)
print('[3-3d] 보정 분포에서 뽑아 만든 몬테카를로 연령-깊이 (GY-1, IntCal13, 곡선 필요)')
try:
    cur = load_curve('intcal13')
except CurveMissing as e:
    print('  곡선 입수 확인 필요:', e)
    sys.exit(0)
gyc = [(363, 1800, 30), (739, 2810, 30), (889, 4150, 30), (917, 6100, 40), (1416, 7210, 40), (1839, 7900, 40), (2060, 7960, 40), (2351, 8030, 40), (2892, 8870, 40)]
M = 200_000
S = np.empty((M, len(gyc)))
pdfs = []
for j, (d, c14, sd) in enumerate(gyc):
    g, p = calibrate(c14, sd, cur)
    pdfs.append((g, p))
    S[:, j] = sample_cal(g, p, M, rng)
mono = np.all(np.diff(S, axis=1) > 0, axis=1)
print(f'  각 연대를 따로 뽑으면 위에서 아래로 나이가 늘어나는 순서를 지키는 조합: {mono.sum()}/{M} ({100*mono.mean():.1f}%)')
for j in range(len(gyc) - 1):
    bad = np.mean(S[:, j] >= S[:, j + 1])
    if bad > 0.001: print(f'    {gyc[j][0]} cm 와 {gyc[j+1][0]} cm 의 순서가 뒤집히는 비율 {100*bad:.1f}%')
A = S[mono]
print(f'  순서를 지킨 {len(A)} 조합으로 깊이 -> 나이 보간:')
dd = np.array([g[0] for g in gyc], float)
# 8.2 ka 의 깊이: 각 조합에서 나이가 8200 인 깊이
def depth_for_age(A, age):
    out = np.full(len(A), np.nan)
    for j in range(A.shape[1] - 1):
        m = (A[:, j] <= age) & (A[:, j + 1] > age)
        out[m] = dd[j] + (age - A[m, j]) / (A[m, j + 1] - A[m, j]) * (dd[j + 1] - dd[j])
    return out
for age in (8000, 8200, 8400):
    d = depth_for_age(A, age); d = d[~np.isnan(d)]
    q = np.percentile(d, [2.5, 50, 97.5])
    print(f'    {age} cal BP 의 깊이: 중앙값 {q[1]:.0f} cm, 95% [{q[0]:.0f}, {q[2]:.0f}] cm (폭 {q[2]-q[0]:.0f} cm)')
print('  (제1권 계산 6-5 의 점 추정: 8.4 ka 1,615 cm / 8.2 ka 1,499 cm / 8.0 ka 1,389 cm)')
# 깊이 1,500 cm 의 나이
def age_at_depth(A, depth):
    j = int(np.searchsorted(dd, depth) - 1)
    return A[:, j] + (depth - dd[j]) / (dd[j + 1] - dd[j]) * (A[:, j + 1] - A[:, j])
for dep_ in (1500, 1600):
    a = age_at_depth(A, dep_)
    q = np.percentile(a, [2.5, 50, 97.5])
    print(f'    깊이 {dep_} cm 의 나이: 중앙값 {q[1]:.0f}, 95% [{q[0]:.0f}, {q[2]:.0f}] cal BP (폭 {q[2]-q[0]:.0f} 년)')
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-ex3.npz'), dd=dd, A=A[:20000], gm=gm)
