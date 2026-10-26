# -*- coding: utf-8 -*-
"""12장 실습 12-6: 실습 12-3의 격자 탐색을 잡음 시드 R개로 되풀이해, 정답이 68%, 95% 영역 안에 드는 빈도와 최적점의 흩어짐을 잰다.
모형 계산은 잡음과 무관하므로 격자 2,091개의 해안선은 한 번만 계산하고 시드마다 chi2만 다시 구한다. 정답에서의 chi2는 정답 해안선 4개 위치에서 직접 구한다(격자점이 아니다).
사용: python p04-seeds-v1.py --xp numpy|cupy|auto [--R 2000]"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('sc', os.path.join(HERE, 'sim-core-v1.py'))
sc = importlib.util.module_from_spec(_s); _s.loader.exec_module(sc)
ap = argparse.ArgumentParser(); ap.add_argument('--xp', default='numpy'); ap.add_argument('--dx', type=float, default=0.5)
ap.add_argument('--dt', type=float, default=0.004); ap.add_argument('--R', type=int, default=2000); a = ap.parse_args()
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

tr, _ = simulate([KT], [QT], a.dx, a.dt); tr = tr[0]
kg = np.logspace(0, math.log10(20), 41); qg = np.linspace(0, 150, 51)
KK, QQ = np.meshgrid(kg, qg, indexing='ij'); K = KK.ravel(); Q = QQ.ravel(); P = len(K)
t = time.perf_counter(); xs, _ = simulate(K, Q, a.dx, a.dt); dt_ = time.perf_counter() - t
print('격자 P = %d, 모형 계산 %.1f s, NaN %d개' % (P, dt_, int(np.isnan(xs).sum())))
jt = int(np.argmin(np.abs(np.log(K) - math.log(KT)) + np.abs(Q - QT) / 150))
R = a.R; rng = np.random.default_rng(11)
n68 = n95 = 0; n68t = n95t = 0; edge = 0; bk = []; bq = []; chit = []; cmins = []
for r in range(R):
    obs = tr + rng.normal(0, NOISE, 4)
    chi = (((xs - obs[None, :]) / NOISE) ** 2).sum(axis=1)
    ib = int(np.argmin(chi)); cmin = float(chi[ib])
    ct = float((((tr - obs) / NOISE) ** 2).sum())
    n68 += chi[jt] <= cmin + 2.30; n95 += chi[jt] <= cmin + 6.18
    n68t += ct <= cmin + 2.30; n95t += ct <= cmin + 6.18
    edge += K[ib] <= kg[0] * 1.0000001
    bk.append(K[ib]); bq.append(Q[ib]); chit.append(ct); cmins.append(cmin)
bk = np.array(bk); bq = np.array(bq); chit = np.array(chit); cmins = np.array(cmins)
print('시드 R = %d (잡음 %.1f km, 시드 11의 한 흐름에서 차례로 뽑음)' % (R, NOISE))
print('정답에 가장 가까운 격자점(kappa %.2f, q %.1f)이 68%% 영역 안: %.4f, 95%% 영역 안: %.4f' % (K[jt], Q[jt], n68 / R, n95 / R))
print('정답 자체(chi2를 직접 계산)가 최소 + 2.30 이내: %.4f, 최소 + 6.18 이내: %.4f  (최소는 격자의 최솟값)' % (n68t / R, n95t / R))
print('정답에서의 chi2의 평균 %.3f (자유도 4이면 4), 격자 최소 chi2의 평균 %.3f' % (chit.mean(), cmins.mean()))
print('최적 kappa: 16/50/84%% 분위수 %.2f / %.2f / %.2f (정답 %.1f), 격자 아래 끝(1.00)에 닿은 비율 %.4f' % (*np.percentile(bk, [16, 50, 84]), KT, edge / R))
print('최적 q: 16/50/84%% 분위수 %.1f / %.1f / %.1f (정답 %.1f)' % (*np.percentile(bq, [16, 50, 84]), QT))
print('최적 kappa가 정답 7.3의 0.5~2배(3.65~14.6) 안인 비율: %.4f' % np.mean((bk >= KT / 2) & (bk <= KT * 2)))
print('최적 q가 정답 61.5 +- 10 안인 비율: %.4f' % np.mean(np.abs(bq - QT) <= 10))
rec = {'R': R, 'p68_grid_point': n68 / R, 'p95_grid_point': n95 / R, 'p68_truth': n68t / R, 'p95_truth': n95t / R, 'chi2_truth_mean': float(chit.mean()),
       'cmin_mean': float(cmins.mean()), 'kappa_q': np.percentile(bk, [16, 50, 84]).tolist(), 'q_q': np.percentile(bq, [16, 50, 84]).tolist(), 'edge': edge / R, 'seconds_model': dt_}
with open(os.path.join(HERE, 'p04-seeds.json'), 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False)
