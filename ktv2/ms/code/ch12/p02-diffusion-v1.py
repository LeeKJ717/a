# -*- coding: utf-8 -*-
"""12장 실습 12-2: 퇴적 모형(시연 모형 B), 1차원 확산 방정식 dD/dt = kappa d2D/dx2 (+ 공급)의 앞으로 가는 차분(FTCS).
검증 네 가지: (1) 풀이가 알려진 경우(계단의 확산, erfc)와 맞대기, 격자를 촘촘히 할 때 오차가 줄어드는 차수
              (2) 질량 보존(양 끝 반사, 공급이 있을 때 합 = q t)
              (3) 안정 조건 r = kappa dt / dx^2 <= 0.5 를 넘기면 어떻게 되는가
              (4) 매개변수 여러 개를 한 배열로 한꺼번에 돌린 결과가 하나씩 돌린 결과와 같은가(xp 방식의 핵심)
이 모형은 이 책이 절차를 보이려고 만든 시연 모형이며 확산계수 값은 시연값이다(실제 한반도·황해의 값이 아님).
사용: python p02-diffusion-v1.py --xp numpy|cupy|auto"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
from scipy.special import erfc
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('sc', os.path.join(HERE, 'sim-core-v1.py'))
sc = importlib.util.module_from_spec(_s); _s.loader.exec_module(sc)
ap = argparse.ArgumentParser(); ap.add_argument('--xp', default='numpy'); a = ap.parse_args()
xp = sc.choose_xp(a.xp); H = lambda v: sc.to_host(xp, v)
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| python', sys.version.split()[0])
rec = {}
KAP, TEND, L, X0 = 10.0, 2.0, 200.0, 100.0      # km^2/ka, ka, km, km
print('\n[1] 계단의 확산: 처음 D = 1 m (x < %.0f km), 0 m (그 너머), kappa = %.0f km^2/ka, t = %.1f ka. 해석해 D = 0.5 erfc((x - x0) / (2 sqrt(kappa t)))' % (X0, KAP, TEND))
print('    r = kappa dt / dx^2 = 0.25 로 고정하고 dx를 절반씩 줄인다')
errs = []
for dx in (2.0, 1.0, 0.5, 0.25):
    x = np.arange(dx / 2, L, dx)
    D0 = (x < X0).astype(float)[None, :]
    dt = 0.25 * dx * dx / KAP; n = int(round(TEND / dt))
    t = time.perf_counter()
    D, _ = sc.diffuse_run(xp, xp.asarray(D0), [KAP], dx, dt, n)
    el = time.perf_counter() - t
    ex = 0.5 * erfc((x - X0) / (2 * math.sqrt(KAP * TEND)))
    e = float(np.abs(H(D)[0] - ex).max()); errs.append(e)
    print('    dx = %5.2f km, 단계 %6d, 최대 오차 %.3e m, %.2f s' % (dx, n, e, el))
orders = [math.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
print('    오차 비로 구한 차수 = %s (2에 가까우면 격자 간격의 제곱에 비례해 줄어든다)' % ', '.join('%.2f' % o for o in orders))
rec['conv'] = {'dx': [2.0, 1.0, 0.5, 0.25], 'err': errs, 'orders': orders}
# 그림용 프로필
dx = 0.5; x = np.arange(dx / 2, L, dx); dt = 0.25 * dx * dx / KAP
D0 = (x < X0).astype(float)[None, :]
snap_t = [0.25, 0.5, 1.0, 2.0]
snaps = [int(round(t_ / dt)) for t_ in snap_t]
_, out = sc.diffuse_run(xp, xp.asarray(D0), [KAP], dx, dt, max(snaps), snaps=snaps)
rec['profiles'] = {'x': x.tolist(), 'times': snap_t, 'num': [H(out[k])[0].tolist() for k in snaps],
                   'ana': [(0.5 * erfc((x - X0) / (2 * math.sqrt(KAP * t_)))).tolist() for t_ in snap_t]}

print('\n[2] 질량 보존')
dx = 0.5; x = np.arange(dx / 2, L, dx); nx = len(x)
rng = np.random.default_rng(11)
D0 = rng.random((3, nx)) * 5
kap = np.array([2.0, 8.0, 15.0]); dt = 0.004
D, _ = sc.diffuse_run(xp, xp.asarray(D0), kap, dx, dt, 2000)
m0 = D0.sum(axis=1) * dx; m1 = H(D).sum(axis=1) * dx
print('    공급 없음, 2000단계: 처음 질량 %s, 나중 %s, 상대 차이 %s' % (np.round(m0, 4), np.round(m1, 4), ['%.1e' % v for v in (m1 - m0) / m0]))
g = sc.gauss_source(xp, x, 100.0, 6.0, dx)
q = np.array([20.0, 60.0, 150.0])
D, _ = sc.diffuse_run(xp, xp.zeros((3, nx)), kap, dx, dt, 1000, q * dt, g)
exp = q * 1000 * dt
print('    공급 q = %s m*km/ka, 1000단계(%.1f ka): 합 x dx = %s, q t = %s, 상대 차이 %s' % (q, 1000 * dt, np.round(H(D).sum(axis=1) * dx, 4), exp, ['%.1e' % v for v in (H(D).sum(axis=1) * dx - exp) / exp]))
rec['mass'] = {'rel_noflux': [float(v) for v in (m1 - m0) / m0], 'rel_source': [float(v) for v in (H(D).sum(axis=1) * dx - exp) / exp]}

print('\n[3] 안정 조건: r = kappa dt / dx^2, dx = 0.5 km, 처음 D = 1 m 계단, 2000단계')
unst = {}
for r in (0.25, 0.45, 0.50, 0.55, 0.60):
    dtr = r * dx * dx / KAP
    D0s = (x < X0).astype(float)[None, :]
    D, _ = sc.diffuse_run(xp, xp.asarray(D0s), [KAP], dx, dtr, 2000)
    d = H(D)[0]
    print('    r = %.2f: 최댓값 %.4g, 최솟값 %.4g (정답은 0~1 사이)' % (r, d.max(), d.min()))
    unst[str(r)] = [float(d.max()), float(d.min())]
rec['stability'] = unst

print('\n[4] 매개변수 여러 개를 한 배열로 (P = 5 대 하나씩 5번)')
kap5 = np.array([1.0, 3.0, 7.0, 12.0, 20.0]); q5 = np.array([0.0, 30.0, 60.0, 100.0, 150.0])
Db, _ = sc.diffuse_run(xp, xp.zeros((5, nx)), kap5, dx, dt, 1000, q5 * dt, g)
Db = H(Db)
mx = 0.0
for i in range(5):
    Di, _ = sc.diffuse_run(xp, xp.zeros((1, nx)), kap5[i:i + 1], dx, dt, 1000, q5[i:i + 1] * dt, g)
    mx = max(mx, float(np.abs(H(Di)[0] - Db[i]).max()))
print('    최대 차이 = %.2e m (0이면 비트 단위로 같다)' % mx)
rec['batch_diff'] = mx
with open(os.path.join(HERE, 'p02-diffusion.json'), 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False)
