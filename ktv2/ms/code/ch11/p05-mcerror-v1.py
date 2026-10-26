# -*- coding: utf-8 -*-
"""11장 실습 11-5: 몬테카를로 오차가 반복 수 N의 제곱근에 반비례해 줄어드는가를, 정답을 아는 네 목표로 잰다.
각 N마다 서로 독립인 난수 흐름(SeedSequence.spawn)으로 R번 되풀이해 오차의 제곱평균제곱근(RMSE)을 구하고 이론값과 견준다.
목표 1  대산전 [1,3,1,2,2] 부트스트랩 H의 평균            정확한 값: 다항분포 전수 계산 (p01)
목표 2  신석기 대 청동기 [[16,2],[4,10]]의 순열 검정 p       정확한 값: Fisher 정확검정 0.000790 (제1권 계산 11-3). 순열 개수는 초기하분포에서 직접 뽑는다(p02의 섞기와 같은 분포).
목표 3  제1권 계산 1-3의 P(D <= 0)                        정확한 값: 정규분포 꼬리 Phi(-3.5777)
목표 4  대산전 부트스트랩 H의 2.5% 분위수                   정확한 값: 0.556 (이산분포이므로 오차가 계단식)
사용: python p05-mcerror-v1.py --xp numpy|cupy|auto"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
from math import erfc, sqrt
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'mc-core-v1.py'))
mc = importlib.util.module_from_spec(_s); _s.loader.exec_module(mc)
ap = argparse.ArgumentParser(); ap.add_argument('--xp', default='numpy'); ap.add_argument('--seed', type=int, default=11)
a = ap.parse_args()
xp = mc.choose_xp(a.xp)
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| python', sys.version.split()[0])
NS = [100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000, 3000000, 10000000]
def reps(N, cap=None):
    r = 400 if N <= 10000 else 200 if N <= 100000 else 100 if N <= 1000000 else 40 if N <= 3000000 else 20
    return r if cap is None or N <= cap[0] else cap[1]
CNT = [1, 3, 1, 2, 2]
vals, pr, mean_ex = mc.exact_h_distribution(CNT)
sd_ex = math.sqrt(float(((vals - mean_ex) ** 2 * pr).sum()))
q_ex = mc.exact_quantile(vals, pr, 0.025)
p_ex = mc.fisher_two_sided_exact(16, 2, 4, 10)
xs, ps = mc.hyp_pmf(16, 2, 4, 10); pmf = dict(zip(xs, ps)); p0 = pmf[16]
region = np.array([x for x in xs if pmf[x] <= p0 * (1 + 1e-9)])
z = 40 / sqrt(125); t_ex = 0.5 * erfc(z / sqrt(2))
print('정확한 값: E[H] = %.6f (표준편차 %.6f), H의 2.5%% 분위수 = %.4f, Fisher p = %.6e, 정규 꼬리 = %.6e' % (mean_ex, sd_ex, q_ex, p_ex, t_ex))
ss = np.random.SeedSequence(a.seed)
rows = []
def run(target, N, R, fn, exact, theory):
    kids = ss.spawn(R)
    t = time.perf_counter()
    est = np.array([fn(xp.random.default_rng(k) if xp is not np else np.random.default_rng(k), N) for k in kids])
    dt = time.perf_counter() - t
    err = est - exact
    rmse = math.sqrt(float((err ** 2).mean()))
    rows.append({'target': target, 'N': N, 'R': R, 'rmse': rmse, 'theory': theory(N), 'bias': float(err.mean()), 'seconds': dt, 'exact': exact})
    print('  %-8s N=%9d R=%4d  RMSE %.3e  이론 %.3e  비 %.2f  (편향 %+.1e, %.1f s)' % (target, N, R, rmse, theory(N), rmse / theory(N) if theory(N) > 0 else float('nan'), err.mean(), dt))
    return est
def f_boot(rng, N):
    h = mc.boot_h_values(xp, CNT, N, rng, 200000)
    return float(h.mean())
hq = {}
def f_boot_q(rng, N):
    h = mc.boot_h_values(xp, CNT, N, rng, 200000)
    return mc.quantiles(xp, h, (0.025,))[0]
def f_perm(rng, N):
    k = mc.to_host(xp, rng.hypergeometric(20, 12, 18, size=N))
    return float(np.isin(k, region).mean())
def f_tail(rng, N):
    d = rng.standard_normal(N) * 10 - 120
    d = (rng.standard_normal(N) * 5 - 80) - d
    return float((d <= 0).mean())
print('\n목표 1: 대산전 H 평균 (부트스트랩), N <= 1,000,000')
for N in [n for n in NS if n <= 1000000]:
    run("mean", N, (reps(N) if N <= 100000 else 30 if N <= 300000 else 20), f_boot, mean_ex, lambda n: sd_ex / sqrt(n))
print('\n목표 4: 대산전 H의 2.5%% 분위수 (같은 부트스트랩), 정확 %.4f에 일치하는 비율' % q_ex)
qrows = []
for N in [n for n in NS if n <= 300000]:
    R = reps(N)
    kids = ss.spawn(R)
    est = np.array([f_boot_q(np.random.default_rng(k), N) if xp is np else f_boot_q(xp.random.default_rng(k), N) for k in kids])
    frac = float((np.abs(est - q_ex) < 1e-6).mean())
    print('  N=%9d R=%4d  정확한 분위수와 같은 비율 %.3f, 추정 평균 %.4f, 최솟값 %.3f 최댓값 %.3f' % (N, R, frac, est.mean(), est.min(), est.max()))
    qrows.append({'N': N, 'R': R, 'frac_equal': frac, 'mean': float(est.mean()), 'min': float(est.min()), 'max': float(est.max())})
print('\n목표 2: Fisher p (순열 개수를 초기하분포에서 직접 뽑음)')
for N in NS:
    run('perm_p', N, reps(N), f_perm, p_ex, lambda n: sqrt(p_ex * (1 - p_ex) / n))
print('\n목표 3: P(D <= 0), 정규 꼬리')
for N in NS:
    run('tail', N, reps(N), f_tail, t_ex, lambda n: sqrt(t_ex * (1 - t_ex) / n))
print('\n기울기: log10 RMSE 를 log10 N 에 직선으로 맞춤 (이론은 -0.5)')
fit = {}
for tg, cond in (('mean', lambda r: True), ('perm_p', lambda r: r['N'] * r['exact'] >= 10), ('tail', lambda r: r['N'] * r['exact'] >= 10)):
    sel = [r for r in rows if r['target'] == tg and cond(r)]
    xx = np.log10([r['N'] for r in sel]); yy = np.log10([r['rmse'] for r in sel])
    sl, ic = np.polyfit(xx, yy, 1)
    fit[tg] = {'slope': float(sl), 'n_points': len(sel), 'N_min': sel[0]['N'], 'N_max': sel[-1]['N']}
    print('  %-7s 기울기 %.3f (점 %d개, N = %d ~ %d%s)' % (tg, sl, len(sel), sel[0]['N'], sel[-1]['N'], ', 기대 횟수 N x p >= 10 인 점만' if tg != 'mean' else ''))
with open(os.path.join(HERE, 'p05-mcerror.json'), 'w', encoding='utf-8') as f:
    json.dump({'rows': rows, 'qrows': qrows, 'fit': fit, 'exact': {'mean': mean_ex, 'sd': sd_ex, 'q': q_ex, 'p': p_ex, 'tail': t_ex}}, f, ensure_ascii=False)
