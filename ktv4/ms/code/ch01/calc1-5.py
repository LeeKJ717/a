# -*- coding: utf-8 -*-
"""계산 1-5: 두 기록이 같은 신호를 갖고 있어도 연대 오차 때문에 상관이 얼마나 줄어드는가 (시연).
논문 값에서 가져온 오차 크기: GICC05 MCE 47년(8236 b2k)과 99년(홀로세 시작, Walker 등 2009, 2018),
  WD2014 와 그린란드 눈금의 차 24년(11.595 ka, Sigl 등 2016), U-Th 이상적 오차 ±10년(2시그마, 1만 년, Cheng 등 2013), 방사성탄소 보정 후 표준편차 수십~100년(계산 1-2).
신호는 시연으로 만든 것이다(1계 자기회귀, 기억 시간 tau 년). 연대 오차는 두 가지 모양으로 넣는다:
 (A) 한쪽 기록 전체를 s 년 밀기(한 기준면에서 생긴 눈금 어긋남과 같은 모양)
 (B) 500년마다 놓인 연대 점에서 정규 오차 sd=s 를 뽑아 그 사이를 직선으로 이은 매끄러운 눈금 오차(연령-깊이 모형의 오차와 비슷한 모양)
"""
import numpy as np
rng = np.random.default_rng(20261027)
N = 12000

def ar1(tau):
    phi = np.exp(-1.0 / tau)
    e = rng.normal(size=N + 2000)
    x = np.zeros(N + 2000)
    for i in range(1, len(x)):
        x[i] = phi * x[i - 1] + e[i]
    return x[2000:]

def corr(a, b): return float(np.corrcoef(a, b)[0, 1])

print('=== 계산 1-5 (1) (A) 전체를 s 년 밀었을 때 두 기록의 상관 (같은 신호, 측정 잡음 없음), 신호 기억 시간 tau ===')
S = (10, 24, 47, 99, 200)
taus = (20, 50, 150, 500)
print('  tau \\ s' + ''.join('%8d' % s for s in S))
for tau in taus:
    cs = []
    for s in S:
        v = np.mean([corr(x[:-300], np.roll(x, s)[:-300]) for x in (ar1(tau) for _ in range(6))])
        cs.append(v)
    print('  %6d  ' % tau + ''.join('%8.2f' % v for v in cs))
print('  (같은 신호에서 s=0 이면 상관은 1.00. 1계 자기회귀의 상관 함수는 exp(-s/tau) 이므로 아래 해석값과 같은 값이 나온다.)')
print('  해석값 exp(-s/tau):')
for tau in taus:
    print('  %6d  ' % tau + ''.join('%8.2f' % np.exp(-s / tau) for s in S))
print()
print('=== 계산 1-5 (2) (B) 500년 간격 연대 점마다 sd=s 의 오차, 사이는 직선으로 이은 매끄러운 눈금 오차 ===')
print('  tau \\ s' + ''.join('%8d' % s for s in S))
tt = np.arange(N)
nodes = np.arange(0, N + 500, 500)
for tau in taus:
    cs = []
    for s in S:
        vv = []
        for _ in range(8):
            x = ar1(tau)
            off = np.interp(tt, nodes, rng.normal(0, s, len(nodes)))
            y = np.interp(tt + off, tt, x)
            vv.append(corr(x[400:-400], y[400:-400]))
        cs.append(np.mean(vv))
    print('  %6d  ' % tau + ''.join('%8.2f' % v for v in cs))
print()
print('=== 계산 1-5 (3) 사건 크기의 신호: 160년 폭 가우스 사건 두 개의 겹침 (한쪽을 s 년 밀면) ===')
x = np.arange(-1000, 1000, 1.0)
w = 160 / 2.355    # 반치폭 160 년
g0 = np.exp(-0.5 * (x / w) ** 2)
for s in (10, 24, 47, 99, 200):
    g1 = np.exp(-0.5 * ((x - s) / w) ** 2)
    print('  s = %3d 년: 겹침(정규화한 상관) %.3f, 봉우리 위치 어긋남은 반치폭의 %.2f 배' % (s, corr(g0, g1), s / 160))
