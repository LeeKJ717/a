# -*- coding: utf-8 -*-
"""12장 실습 12-3: 매개변수 격자 탐색 (시연 모형 C = 해수면 상승 + 퇴적).
모형: 땅의 높이 z(x,t) = z0(x) + D(x,t). z0는 경사 1/1000의 직선 지형(x = 0에서 -40 m), D는 공급점 x = 25 km 근처에서 쌓이는 퇴적 두께로
      확산 방정식 dD/dt = kappa d2D/dx2 + q g(x) 를 따른다(g는 폭 6 km의 가우스). 수위는 제1권 2장의 점들(실습 12-1)을 따라 9 ka -31.7 m에서 5 ka -2.4 m로 오른다.
      해안선 = 바다 쪽에서 처음으로 z >= 수위가 되는 위치. 공급점은 해안선을 따라가지 않고 고정했다(이 모형의 큰 단순화).
탐색: 알려진 정답으로 가짜 관측을 만들어 되찾을 수 있는지 본다. 정답 kappa* = 7.3 km^2/ka, q* = 61.5 m km/ka (격자 위의 점이 아닌 값),
      관측 = 8, 7, 6, 5 ka의 해안선 위치 + 정규 잡음(표준편차 0.5 km, 시드 11). 격자 = kappa 41개(로그, 1~20) x q 51개(0~150).
      어긋남 chi2 = sum(((모형 - 관측)/0.5)^2). 이것은 시연이다. 실제 한반도·황해의 값이 아니다.
사용: python p03-grid-v1.py --xp numpy|cupy|auto"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('sc', os.path.join(HERE, 'sim-core-v1.py'))
sc = importlib.util.module_from_spec(_s); _s.loader.exec_module(sc)
ap = argparse.ArgumentParser(); ap.add_argument('--xp', default='numpy'); ap.add_argument('--dx', type=float, default=0.5)
ap.add_argument('--dt', type=float, default=0.004); a = ap.parse_args()
xp = sc.choose_xp(a.xp); H = lambda v: sc.to_host(xp, v)
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| python', sys.version.split()[0])
LX, XM, SIG, SLOPE, Z0 = 300.0, 25.0, 6.0, 1 / 1000.0, -40.0
T0, TOBS = 9.0, [8.0, 7.0, 6.0, 5.0]
NOISE = 0.5
KT, QT = 7.3, 61.5

def simulate(kap, q, dx, dt):
    """kap, q: 길이 P 배열. 반환 (P, 4) 관측 시각의 해안선 위치(km)."""
    x = np.arange(dx / 2, LX, dx)
    z0 = sc.terrain_uniform(xp, x, Z0, [SLOPE])
    g = sc.gauss_source(xp, x, XM, SIG, dx)
    n = int(round((T0 - min(TOBS)) / dt)); snaps = [int(round((T0 - t) / dt)) for t in TOBS]
    D, out = sc.diffuse_run(xp, xp.zeros((len(kap), len(x))), np.asarray(kap), dx, dt, n, np.asarray(q) * dt, g, snaps)
    return np.stack([H(sc.shoreline(xp, z0 + out[k], x, float(H(sc.sea_level(xp, t))))) for t, k in zip(TOBS, snaps)], axis=1), D

print('\n[1] 정답 모형의 해안선 (kappa* = %.1f, q* = %.1f)과 퇴적이 없을 때(q = 0)' % (KT, QT))
tr, Dt = simulate([KT, KT], [QT, 0.0], a.dx, a.dt)
print('    관측 시각 %s ka' % TOBS)
print('    q = q*: %s km' % np.round(tr[0], 3)); print('    q = 0 : %s km (직선 지형의 식과 같다)' % np.round(tr[1], 3))
print('    질량 점검: 합 x dx / (q t) = %.6f' % (H(Dt)[0].sum() * a.dx / (QT * 4.0)))
fine, _ = simulate([KT], [QT], a.dx / 2, a.dt / 4)
print('    격자 점검: dx = %.2f -> %.3f km, 시간 간격 1/4 로 같이 줄이면 최대 차이 %.4f km' % (a.dx, a.dx / 2, np.abs(fine[0] - tr[0]).max()))
rng = np.random.default_rng(11)
obs = tr[0] + rng.normal(0, NOISE, 4)
print('    가짜 관측 (정답 + 잡음 %.1f km): %s km' % (NOISE, np.round(obs, 3)))

kg = np.logspace(0, math.log10(20), 41); qg = np.linspace(0, 150, 51)
KK, QQ = np.meshgrid(kg, qg, indexing='ij'); K = KK.ravel(); Q = QQ.ravel(); P = len(K)
rmax = K.max() * a.dt / a.dx ** 2
print('\n[2] 격자 탐색: P = %d 조합 (kappa %d x q %d), r_max = %.2f (<= 0.5 이어야 함), 단계 %d, 격자 %d칸' % (P, len(kg), len(qg), rmax, int(round(4 / a.dt)), int(LX / a.dx)))
t = time.perf_counter()
xs, _ = simulate(K, Q, a.dx, a.dt)
dt_ = time.perf_counter() - t
chi = (((xs - obs[None, :]) / NOISE) ** 2).sum(axis=1)
print('    걸린 시간 %.1f s (NumPy, CPU), NaN %d개' % (dt_, int(np.isnan(chi).sum())))
chi = np.where(np.isnan(chi), np.inf, chi)
ib = int(np.argmin(chi)); cmin = float(chi[ib])
print('    최소 chi2 = %.3f (자유도 4 - 2 = 2) 에서 kappa = %.3f, q = %.1f  (정답 %.1f, %.1f)' % (cmin, K[ib], Q[ib], KT, QT))
reg = chi <= cmin + 2.30
print('    chi2 <= 최소 + 2.30 (매개변수 둘의 68%% 영역에 해당): %d칸 / %d칸. kappa %.2f ~ %.2f, q %.1f ~ %.1f' % (reg.sum(), P, K[reg].min(), K[reg].max(), Q[reg].min(), Q[reg].max()))
reg2 = chi <= cmin + 6.18
print('    chi2 <= 최소 + 6.18 (95%% 영역): %d칸. kappa %.2f ~ %.2f, q %.1f ~ %.1f' % (reg2.sum(), K[reg2].min(), K[reg2].max(), Q[reg2].min(), Q[reg2].max()))
inside = bool(chi[np.argmin(np.abs(np.log(K) - math.log(KT)) + np.abs(Q - QT) / 150)] <= cmin + 2.30)
jt = int(np.argmin(np.abs(np.log(K) - math.log(KT)) + np.abs(Q - QT) / 150))
print('    정답에 가장 가까운 격자점(kappa %.2f, q %.1f)의 chi2 = %.2f: 68%% 영역 안 %s, 95%% 영역 안 %s' % (K[jt], Q[jt], chi[jt], inside, bool(chi[jt] <= cmin + 6.18)))
c = np.corrcoef(np.log(K[reg2]), Q[reg2])[0, 1]
print('    95%% 영역 안에서 log kappa 와 q 의 상관 = %+.2f (한쪽을 키우면 다른 쪽도 키워야 맞는 능선이 있는지)' % c)
qz = chi.reshape(len(kg), len(qg))[:, 0]
print('    퇴적이 없는 모형(q = 0 줄)의 최소 chi2 = %.1f  (kappa에 무관)' % qz.min())
rec = {'obs': obs.tolist(), 'truth_path': tr[0].tolist(), 'q0_path': tr[1].tolist(), 'tobs': TOBS, 'kappa': kg.tolist(), 'q': qg.tolist(), 'chi2': chi.reshape(len(kg), len(qg)).tolist(),
       'best': {'kappa': float(K[ib]), 'q': float(Q[ib]), 'chi2': cmin}, 'truth': {'kappa': KT, 'q': QT}, 'seconds': dt_, 'P': P, 'noise': NOISE,
       'n68': int(reg.sum()), 'n95': int(reg2.sum()), 'corr95': float(c), 'q0_chi2_min': float(qz.min()), 'fine_diff': float(np.abs(fine[0] - tr[0]).max()),
       'best_path': xs[ib].tolist()}
with open(os.path.join(HERE, 'p03-grid.json'), 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False)
