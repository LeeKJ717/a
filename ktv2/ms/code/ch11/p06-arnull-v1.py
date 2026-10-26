# -*- coding: utf-8 -*-
"""11장 실습 11-6: 자기상관이 있는 두 계열의 '우연한 상관'을 난수로 만들어, 제1권 11장 계산 11-9의 유효 표본 크기를 시험한다.
제1권 계산 11-9: 노백산 복원과 북반구 복원의 상관 r = -0.18 (n = 414로 가정). 독립으로 보면 t = 3.71, p = 2.3e-4.
두 계열의 1차 자기상관을 모두 0.72(논문 표 1의 값을 제1권이 읽은 것)로 놓으면 n_eff = 414 (1 - 0.72^2)/(1 + 0.72^2) = 131.3, 임계 r(0.05) = 0.172, 임계 r(0.01) = 0.224.
이 실습은 '서로 독립인 AR(1) 두 계열' M쌍을 만들어 표본 상관의 분포를 직접 잰다. 계열의 모형이 AR(1)이라는 것은 이 실습의 가정이다.
사용: python p06-arnull-v1.py --xp numpy|cupy|auto [--M 200000] [--seed 11]"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'mc-core-v1.py'))
mc = importlib.util.module_from_spec(_s); _s.loader.exec_module(mc)
ap = argparse.ArgumentParser(); ap.add_argument('--xp', default='numpy'); ap.add_argument('--M', type=int, default=200000)
ap.add_argument('--seed', type=int, default=11); ap.add_argument('--n', type=int, default=414)
a = ap.parse_args(); xp = mc.choose_xp(a.xp); n = a.n; M = a.M
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| n = %d, M = %d 쌍, 시드 %d' % (n, M, a.seed))
def rcrit(nn, al):
    tc = stats.t.isf(al / 2, nn - 2); return tc / math.sqrt(nn - 2 + tc * tc)
r_obs = 0.18
rec = {'n': n, 'M': M, 'seed': a.seed, 'backend': xp.__name__, 'cases': {}}
edges = np.round(np.arange(-0.5, 0.5001, 0.01), 4)
for rho in (0.0, 0.72):
    t = time.perf_counter()
    rng = mc.make_rng(xp, a.seed)
    r = mc.to_host(xp, mc.ar1_pair_corr(xp, n, rho, M, rng))
    dt = time.perf_counter() - t
    sd = float(r.std()); neff_emp = 1 / sd ** 2
    neff_th = n * (1 - rho * rho) / (1 + rho * rho)
    p_big = float((np.abs(r) >= r_obs).mean()); k_big = int((np.abs(r) >= r_obs).sum())
    tt = r_obs * math.sqrt(n - 2) / math.sqrt(1 - r_obs ** 2); p_iid = 2 * stats.t.sf(tt, n - 2)
    tt2 = r_obs * math.sqrt(neff_th - 2) / math.sqrt(1 - r_obs ** 2); p_neff = 2 * stats.t.sf(tt2, neff_th - 2)
    rc_iid = rcrit(n, 0.05); rc_neff = rcrit(int(neff_th), 0.05)
    rej_iid = float((np.abs(r) > rc_iid).mean()); rej_neff = float((np.abs(r) > rc_neff).mean())
    emp975 = float(np.quantile(np.abs(r), 0.95)); emp99 = float(np.quantile(np.abs(r), 0.99))
    print('\n== 자기상관 rho = %.2f (두 계열 모두), %.1f s' % (rho, dt))
    print('  표본 상관 r: 평균 %+.5f, 표준편차 %.5f -> 경험적 n_eff = 1/sd^2 = %.1f (식 n_eff = %.1f)' % (r.mean(), sd, neff_emp, neff_th))
    print('  P(|r| >= %.2f): 난수 %d/%d = %.3e | 독립(n=%d)으로 본 t 검정 p = %.3e | n_eff = %.1f 로 본 t 검정 p = %.3e' % (r_obs, k_big, M, p_big, n, p_iid, neff_th, p_neff))
    print('  5%% 수준 검정의 실제 기각률(귀무가설이 참일 때): 독립 임계 r %.3f -> %.4f | n_eff 임계 r %.3f -> %.4f (명목 0.05)' % (rc_iid, rej_iid, rc_neff, rej_neff))
    print('  난수에서 |r|의 95%% 분위수 = %.4f, 99%% 분위수 = %.4f (식: n_eff 임계 r 0.05 -> %.3f, 0.01 -> %.3f)' % (emp975, emp99, rc_neff, rcrit(int(neff_th), 0.01)))
    h = np.histogram(r, bins=edges)[0]
    rec['cases'][str(rho)] = {'sd': sd, 'mean': float(r.mean()), 'neff_emp': neff_emp, 'neff_formula': neff_th, 'p_big': p_big, 'k_big': k_big, 'p_iid_t': p_iid, 'p_neff_t': p_neff,
                              'rej_iid': rej_iid, 'rej_neff': rej_neff, 'rc_iid': rc_iid, 'rc_neff': rc_neff, 'q95': emp975, 'q99': emp99, 'hist': [int(v) for v in h],
                              'edges': [float(v) for v in edges], 'seconds': dt}
with open(os.path.join(HERE, 'p06-arnull.json'), 'w', encoding='utf-8') as f:
    json.dump(rec, f, ensure_ascii=False)
