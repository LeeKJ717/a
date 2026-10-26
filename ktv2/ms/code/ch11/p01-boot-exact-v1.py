# -*- coding: utf-8 -*-
"""11장 실습 11-1: 제1권 11장 계산 11-4의 부트스트랩을 xp 방식으로 크게 되풀이하고, 정확히 센 분포와 맞대어 본다.
입력은 제1권 11장 계산 11-4와 같다: 신석기 합 [16,1,1], 대전자 [3,2], 대산전 [1,3,1,2,2] (하플로그룹 수준 빈도).
제1권의 값은 2만 번 되풀이한 numpy.percentile(선형 보간)이다. 여기서는 (가) 같은 방식의 선형 보간 분위수와
(나) 누적확률이 처음 q 이상이 되는 분위수를 둘 다 적고, (다) 정확한 분포와 맞댄다.
사용: python p01-boot-exact-v1.py --xp numpy|cupy|auto [--B 1000000] [--seed 11]"""
import argparse, importlib.util, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'mc-core-v1.py'))
mc = importlib.util.module_from_spec(_s); _s.loader.exec_module(mc)

ap = argparse.ArgumentParser()
ap.add_argument('--xp', default='numpy'); ap.add_argument('--B', type=int, default=1000000)
ap.add_argument('--chunk', type=int, default=200000); ap.add_argument('--seed', type=int, default=11)
a = ap.parse_args()
xp = mc.choose_xp(a.xp)
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| python', sys.version.split()[0], '| 시드', a.seed)
VOL1 = {'신석기 합': (0.000, 0.209, 0.464), '대전자': (0.000, None, 0.600), '대산전': (0.556, 0.778, 0.889)}
GROUPS = [('신석기 합', [16, 1, 1]), ('대전자', [3, 2]), ('대산전', [1, 3, 1, 2, 2])]
rec = []
for name, cnt in GROUPS:
    vals, pr, mean_ex = mc.exact_h_distribution(cnt)
    hobs = mc.nei_h(cnt)
    ex = [mc.exact_quantile(vals, pr, q) for q in (0.025, 0.5, 0.975)]
    print('\n== %s %s  n=%d  관측 H = %.4f' % (name, cnt, sum(cnt), hobs))
    print('  정확한 분포: 서로 다른 H 값 %d개, 평균 %.5f, 분위수(2.5/50/97.5%%) = %.3f / %.3f / %.3f' % (len(vals), mean_ex, *ex))
    v = VOL1[name]
    print('  제1권(2만 번, 선형 보간): %s' % ' / '.join('-' if x is None else '%.3f' % x for x in v))
    for B in (20000, a.B):
        rng = mc.make_rng(xp, a.seed)
        t = time.perf_counter()
        h = mc.boot_h_values(xp, cnt, B, rng, a.chunk)
        lin = [float(x) for x in mc.to_host(xp, xp.percentile(h, xp.asarray([2.5, 50, 97.5])))]
        inv = mc.quantiles(xp, h, (0.025, 0.5, 0.975))
        mean_mc = float(h.mean())
        dt = time.perf_counter() - t
        print('  B=%8d  선형 보간 %.3f / %.3f / %.3f | 누적 기준 %.3f / %.3f / %.3f | 평균 %.5f (정확 %.5f, 차 %+.5f) | %.2f s' % (
            B, *lin, *inv, mean_mc, mean_ex, mean_mc - mean_ex, dt))
        rec.append({'group': name, 'counts': cnt, 'B': B, 'seed': a.seed, 'lin': lin, 'inv': inv, 'mean_mc': mean_mc,
                    'mean_exact': mean_ex, 'exact_q': ex, 'seconds': dt, 'backend': xp.__name__})
    # 큰 B에서 값별 빈도와 정확한 확률을 맞댄다
    hh = mc.to_host(xp, h)
    freq = {}
    for v_, p_ in zip(vals, pr):
        freq[round(float(v_), 10)] = float(np.mean(np.abs(hh - v_) < 1e-9))
    mx = max(abs(freq[round(float(v_), 10)] - p_) for v_, p_ in zip(vals, pr))
    print('  값별 빈도와 정확한 확률의 최대 차이 = %.5f (B=%d, 이론적 표준오차 최대 약 %.5f)' % (mx, a.B, 0.5 / a.B ** 0.5))
    rec[-1]['pmf'] = {'vals': [float(x) for x in vals], 'exact': [float(x) for x in pr], 'mc': [freq[round(float(v_), 10)] for v_ in vals]}
with open(os.path.join(HERE, 'p01-boot-exact.jsonl'), 'w', encoding='utf-8') as f:
    for r in rec: f.write(json.dumps(r, ensure_ascii=False) + '\n')
