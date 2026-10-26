# -*- coding: utf-8 -*-
"""11장 실습 11-3: 불확실성 전파를 xp 방식으로. 제1권의 네 계산에 같은 입력을 넣고 난수 N개로 합친다.
  (가) 제1권 1장 계산 1-3: 사이토 -120 +- 10 m 와 오시마 -80 +- 5 m 의 차이 (두 +-를 독립인 1 표준편차로 읽은 시연 가정)
  (나) 제1권 9장 계산 9-10: OSL 나이 = De / DR (HZ-OSL-115, HZ-OSL-180). 달력 연도 = 2024 - 나이(ka) x 1000 은 제1권의 가정
  (다) 제1권 1장 계산 1-2: 40 m 상승이 3000~4000년에 걸쳤다고 놓고, 걸린 시간을 균등분포로 흔든다 (시연 가정)
  (라) 제1권 11장 계산 11-13: 노백산-돈화 기상대 거리. 좌표가 분 단위로 반올림되었다고 보고 네 좌표를 +-0.5' 균등분포로 흔든다 (시연 가정)
사용: python p03-propagate-v1.py --xp numpy|cupy|auto [--N 10000000] [--seed 11]"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
from math import erfc, sqrt, log
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'mc-core-v1.py'))
mc = importlib.util.module_from_spec(_s); _s.loader.exec_module(mc)

ap = argparse.ArgumentParser()
ap.add_argument('--xp', default='numpy'); ap.add_argument('--N', type=int, default=10000000); ap.add_argument('--seed', type=int, default=11)
a = ap.parse_args()
xp = mc.choose_xp(a.xp); N = a.N
rng = mc.make_rng(xp, a.seed)
H = lambda v: float(mc.to_host(xp, v))
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| N = %d | 시드 %d' % (N, a.seed))
rec = {'N': N, 'seed': a.seed, 'backend': xp.__name__}
Phi = lambda z: 0.5 * erfc(-z / sqrt(2))

print('\n== (가) 계산 1-3: D = (-80) - (-120) = 40 m, 불확도 sqrt(10^2+5^2) = %.4f m' % sqrt(125))
t = time.perf_counter()
A = rng.standard_normal(N) * 10 - 120; Bv = rng.standard_normal(N) * 5 - 80
D = Bv - A
mean, sd = H(D.mean()), H(D.std())
k = int((D <= 0).sum())
z = 40 / sqrt(125); pex = Phi(-z)
print('  난수 평균 %.4f, 표준편차 %.4f (식: 40, %.4f); 비 = %.4f (제1권 3.58)' % (mean, sd, sqrt(125), mean / sd))
print('  P(D <= 0): 난수 %d/%d = %.3e, 정확(정규분포) Phi(-%.4f) = %.3e, 비 = %.3f, 상대 표준오차 약 %.1f%%' % (k, N, k / N, z, pex, (k / N) / pex, 100 / sqrt(max(k, 1))))
rec['a'] = {'mean': mean, 'sd': sd, 'k': k, 'p_mc': k / N, 'p_exact': pex, 'z': z, 'seconds': time.perf_counter() - t}

print('\n== (나) 계산 9-10: OSL 나이 = De / DR')
rec['b'] = {}
for nm, De, sDe, DR, sDR, a_v, a_s in (('HZ-OSL-115', 4.64, 0.55, 2.57, 0.09, 1.805, 0.223), ('HZ-OSL-180', 5.28, 0.96, 2.39, 0.09, 2.209, 0.410)):
    t = time.perf_counter()
    x = (rng.standard_normal(N) * sDe + De) / (rng.standard_normal(N) * sDR + DR)
    m, s = H(x.mean()), H(x.std())
    q = mc.quantiles(xp, x, (0.025, 0.5, 0.975))
    cal = 2024 - 1000 * x
    lo, hi = -131, -108                                  # 제1권의 한 무제 시기 구간(천문 연도 -131 ~ -108)
    inwin = H(((cal >= lo) & (cal <= hi)).mean())
    skew = H(((x - m) ** 3).mean()) / s ** 3
    mu_c, sd_c = 2024 - 1000 * a_v, 1000 * a_s
    pdf = math.exp(-0.5 * ((-119.5 - mu_c) / sd_c) ** 2) / (sd_c * sqrt(2 * math.pi))
    print('  %s: 식 %.3f +- %.3f ka (제1권 %.3f +- %.3f) | 난수 평균 %.4f, 표준편차 %.4f, 왜도 %+.3f' % (nm, De / DR, De / DR * sqrt((sDe / De) ** 2 + (sDR / DR) ** 2), a_v, a_s, m, s, skew))
    print('     난수 2.5/50/97.5%% = %.3f / %.3f / %.3f ka | 달력 연도 구간(2.5~97.5%%) %.0f ~ %.0f' % (*q, 2024 - 1000 * q[2], 2024 - 1000 * q[0]))
    print('     달력 연도가 [-131, -108](23년 창)에 들어갈 확률: 난수 %.5f, 정규 근사(창 폭 x 밀도) %.5f' % (inwin, 23 * pdf))
    edges = np.linspace(0, 6, 121)
    hh = mc.to_host(xp, xp.histogram(x, bins=xp.asarray(edges))[0]) if xp is not np else np.histogram(x, bins=edges)[0]
    rec['b'][nm] = {'mean': m, 'sd': s, 'skew': skew, 'q': q, 'in_window': inwin, 'normal_window': 23 * pdf, 'hist': [int(v) for v in hh], 'edges': [float(v) for v in edges],
                    'formula': [De / DR, De / DR * sqrt((sDe / De) ** 2 + (sDR / DR) ** 2)], 'seconds': time.perf_counter() - t}

print('\n== (다) 계산 1-2: 40 m 상승, 걸린 시간 U(3000, 4000)년 -> 속도 = 40000 mm / 시간')
t = time.perf_counter()
dur = 3000 + 1000 * rng.random(N)
rate = 40000 / dur
m, s = H(rate.mean()), H(rate.std())
q = mc.quantiles(xp, rate, (0.025, 0.5, 0.975))
mex = 40 * log(4 / 3)
print('  난수 평균 %.4f mm/yr, 표준편차 %.4f | 정확한 평균 40 x ln(4/3) = %.4f | 2.5/50/97.5%% = %.3f / %.3f / %.3f' % (m, s, mex, *q))
print('  제1권의 세 점(3000, 3500, 4000년): 13.33, 11.43, 10.00. 평균이 중간점(11.43)보다 큰 것은 1/x가 아래로 볼록하기 때문(젠센 부등식)')
rec['c'] = {'mean': m, 'sd': s, 'q': q, 'mean_exact': mex, 'seconds': time.perf_counter() - t}

print('\n== (라) 계산 11-13: 노백산(128°03′E, 44°06′N) - 돈화 기상대(128°12′E, 43°22′N) 거리, 좌표를 +-0.5′ 균등으로 흔듦')
t = time.perf_counter()
w = 0.5 / 60.0
c = [128 + 3 / 60, 44 + 6 / 60, 128 + 12 / 60, 43 + 22 / 60]
j = [c[i] + (2 * rng.random(N) - 1) * w for i in range(4)]
d = mc.hav_pair(xp, j[0], j[1], j[2], j[3])
d0 = H(mc.hav_pair(xp, xp.asarray([c[0]]), xp.asarray([c[1]]), xp.asarray([c[2]]), xp.asarray([c[3]]))[0])
m, s = H(d.mean()), H(d.std())
q = mc.quantiles(xp, d, (0.025, 0.5, 0.975))
print('  공칭 거리 %.2f km (제1권 82.43) | 난수 평균 %.3f km, 표준편차 %.3f km, 2.5/50/97.5%% = %.2f / %.2f / %.2f km' % (d0, m, s, *q))
print('  제1권: 반올림 크기 0.0167° = 1.86 km 규모. 난수 결과: 95%% 구간의 반폭 %.2f km' % ((q[2] - q[0]) / 2))
rec['d'] = {'nominal': d0, 'mean': m, 'sd': s, 'q': q, 'seconds': time.perf_counter() - t}
with open(os.path.join(HERE, 'p03-propagate.json'), 'w', encoding='utf-8') as f:
    json.dump(rec, f, ensure_ascii=False)
