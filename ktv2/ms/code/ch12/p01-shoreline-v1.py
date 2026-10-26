# -*- coding: utf-8 -*-
"""12장 실습 12-1: 경사 지형 위의 수위 상승 -> 해안선 이동 (시연 모형 A).
모형: 땅의 높이 z(x)를 바다에서 안쪽으로 가는 거리 x(km)의 함수로 두고, 수위 h(t)가 오르면 해안선은 z(x) = h(t)인 곳이다.
수위 입력은 제1권 2장 2.4절(Bloom & Park, 1985가 소개한 Clark 등의 모형 결과, 한국 남단)의 점들이다.
경사 입력은 제1권 3장 3.9.1절 방법 상자 A의 대륙붕 경사 1/344(퇴적면의 상한)와 1/115(침식면의 하한), 계산 A-2의 옛 도쿄 강 하상 경사 1/3500이다.
땅 높이 변화(융기 +, 침강 -)는 제1권 2장 2.9.2절의 약속(상대 상승 = 해수면 상승 - 융기)을 따른다.
이 모형은 실제 한반도·황해의 해안선이 아니다. 경사와 수위 값의 출처는 위와 같고, 두 값을 한 곳에 놓은 것은 이 책의 시연이다.
사용: python p01-shoreline-v1.py --xp numpy|cupy|auto"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('sc', os.path.join(HERE, 'sim-core-v1.py'))
sc = importlib.util.module_from_spec(_s); _s.loader.exec_module(sc)
ap = argparse.ArgumentParser(); ap.add_argument('--xp', default='numpy'); a = ap.parse_args()
xp = sc.choose_xp(a.xp); H = lambda v: sc.to_host(xp, v)
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| python', sys.version.split()[0])
rec = {}
x = np.arange(0.0, 500.0001, 0.5); nx = len(x)
Z0 = -40.0
SL = {'1/115': 1 / 115, '1/344': 1 / 344, '1/3500': 1 / 3500}

print('\n[1] 수위 입력(제1권 2장): t(ka), 수위(m)')
for t, h in zip(sc.SL_T, sc.SL_H): print('   %5.1f ka  %7.1f m' % (t, h))
print('   구간 상승 속도: 9~7 ka %.2f, 7~5 ka %.2f, 5~0 ka %.2f mm/yr (제1권 2.4절: 최근 5000년 0.48)' % (19.5 / 2.0, 9.8 / 2.0, 2.4 / 5.0))

print('\n[2] 검증: 한 가지 경사에서 격자 계산과 식 x = (h - z0) / (1000 s) km 의 차이')
s_arr = np.array(list(SL.values()))
z = sc.terrain_uniform(xp, x, Z0, s_arr)
worst = 0.0
for h in (-31.7, -21.95, -12.2, -2.4, 0.0):
    xs = H(sc.shoreline(xp, z, x, h))
    an = (h - Z0) / (1000 * s_arr)
    err = np.nanmax(np.abs(xs - an)); worst = max(worst, err)
    print('   h = %7.2f m: 격자 %s km | 식 %s km | 최대 차이 %.2e km' % (h, np.round(xs, 3), np.round(an, 3), err))
print('   모든 경우의 최대 차이 = %.2e km (격자 간격 0.5 km). 직선 지형에서는 직선 보간이 정확하다' % worst)
rec['uniform_check_max_err_km'] = float(worst)

print('\n[3] 제1권 수위(Bloom & Park)를 세 경사에 넣은 해안선 후퇴 거리 (km). 괄호는 후퇴 속도 (m/yr)')
Tb = {'9~7 ka': (9.0, 7.0), '7~5 ka': (7.0, 5.0), '5~0 ka': (5.0, 0.0), '9~0 ka': (9.0, 0.0)}
tab = {}
print('   %-8s %7s | %s' % ('구간', '상승 m', ' | '.join('%-18s' % ('경사 ' + k) for k in SL)))
for nm, (t0, t1) in Tb.items():
    h0, h1 = float(H(sc.sea_level(xp, t0))), float(H(sc.sea_level(xp, t1)))
    x0 = H(sc.shoreline(xp, z, x, h0)); x1 = H(sc.shoreline(xp, z, x, h1))
    ret = x1 - x0; yr = (t0 - t1) * 1000
    tab[nm] = {'rise_m': h1 - h0, 'retreat_km': ret.tolist(), 'rate_m_per_yr': (ret * 1000 / yr).tolist()}
    print('   %-8s %7.2f | %s' % (nm, h1 - h0, ' | '.join('%7.2f (%6.2f)    ' % (r_, r_ * 1000 / yr) for r_ in ret)))
rec['table_retreat'] = tab

print('\n[4] 제1권 1장 계산 1-2의 시연(40 m 상승이 3000~4000년): 해안선 후퇴 = 40 m / 경사')
sc4 = {}
for k, s_ in SL.items():
    d = 40 / (1000 * s_)
    sc4[k] = d
    print('   경사 %-7s: 후퇴 %.2f km; 평균 속도 %.2f m/yr (3500년 기준, 상승 11.43 mm/yr / 경사 = %.2f m/yr)' % (k, d, d * 1000 / 3500, 11.43e-3 / s_))
rec['sc4_km'] = sc4

print('\n[5] 두 경사 지형: x < 10 km 에서 1/344, 그 너머에서 1/3500. 해안선 위치의 시간 변화를 식과 맞댐')
zt = sc.terrain_two_slope(xp, x, Z0, 1 / 344, 1 / 3500, 10.0)
zb = Z0 + 1000 * (1 / 344) * 10.0
ts = np.linspace(9.0, 0.0, 91)
hs = H(sc.sea_level(xp, ts))
xs2 = np.array([float(H(sc.shoreline(xp, zt, x, float(h)))[0]) for h in hs])
def an2(h):
    return (h - Z0) * 344 / 1000 if h <= zb else 10.0 + (h - zb) * 3500 / 1000
xa2 = np.array([an2(h) for h in hs])
print('   꺾임 높이 = %.3f m. 최대 차이 = %.2e km' % (zb, np.abs(xs2 - xa2).max()))
print('   9 ka 위치 %.2f km -> 0 ka 위치 %.2f km, 총 후퇴 %.2f km' % (xs2[0], xs2[-1], xs2[-1] - xs2[0]))
rec['two_slope'] = {'t': ts.tolist(), 'xs': xs2.tolist(), 'xa': xa2.tolist(), 'break_z': zb}
# 세 경사의 시간 변화(그림용)
xs3 = {}
for k, s_ in SL.items():
    zk = sc.terrain_uniform(xp, x, Z0, [s_])
    xs3[k] = [float(H(sc.shoreline(xp, zk, x, float(h)))[0]) for h in hs]
rec['paths'] = {'t': ts.tolist(), **xs3}

print('\n[6] 매개변수 격자: 경사 s (1/100 ~ 1/5000, 로그 60개) x 땅 높이 변화율 u (-2 ~ +10 mm/yr, 0.25 간격 49개) 의 9 ka -> 5 ka 후퇴 (km)')
print('    이 격자는 땅의 시작 높이를 x = 0 에서 -100 m로 두었다(해안선이 영역 밖으로 나가지 않게). 후퇴가 음수이면 해안선이 바다 쪽으로 나아간 것')
Z1 = -100.0
inv = np.logspace(math.log10(100), math.log10(5000), 60); ss = 1.0 / inv
us = np.linspace(-2.0, 10.0, 49)
S, U = np.meshgrid(ss, us, indexing='ij'); S = S.ravel(); U = U.ravel()
P = len(S)
h9 = float(H(sc.sea_level(xp, 9.0))); h5 = float(H(sc.sea_level(xp, 5.0)))
def retreat(Sv, Uv):
    zg = sc.terrain_uniform(xp, x, Z1, Sv)
    x9 = H(sc.shoreline(xp, zg, x, h9)); x5 = H(sc.shoreline(xp, zg, x, h5 - xp.asarray(Uv) * 4.0))   # 땅이 u(m/ka)로 오르내리면 상대 수위는 h(t) - u (t0 - t), 9 ka -> 5 ka 는 4 ka
    return x5 - x9
t0w = time.perf_counter()
ret = retreat(S, U)
dt_ = time.perf_counter() - t0w
an = ((h5 - h9) - U * 4.0) / (1000 * S)
print('   P = %d 조합, 격자 %d칸, 계산 시간 %.3f s (NumPy, CPU)' % (P, nx, dt_))
print('   식 ((h5-h9) - 4u)/(1000 s) 와의 최대 차이 = %.2e km, NaN(영역 밖) %d개' % (np.nanmax(np.abs(ret - an)), int(np.isnan(ret).sum())))
nanidx = np.where(np.isnan(ret))[0]
if len(nanidx):
    print('   NaN인 칸: 경사 1/%s, u = %s mm/yr (해안선이 영역의 끝 x = %.0f km 밖으로 나감)' % (sorted({'%.0f' % (1 / S[i]) for i in nanidx}), sorted({float(U[i]) for i in nanidx}), x[-1]))
lines = {}
print('   세 경사의 u별 후퇴 (km): u = -1, 0, +1, +7.325(후퇴 0), +10 mm/yr')
for nm, s_ in SL.items():
    r_ = retreat(np.full(len(us), s_), us)
    lines[nm] = r_.tolist()
    pick = [int(np.argmin(np.abs(us - v))) for v in (-1.0, 0.0, 1.0, 7.25, 10.0)]
    print('   경사 %-7s: %s' % (nm, ' '.join('%8.2f' % r_[i] for i in pick)), '| u=0 대비 u=+1: %+.1f%%, u=-1: %+.1f%%' % (100 * (r_[pick[2]] / r_[pick[1]] - 1), 100 * (r_[pick[0]] / r_[pick[1]] - 1)))
    print('               u = +/-1 mm/yr 의 후퇴 변화 = %.2f km' % (abs(r_[pick[2]] - r_[pick[1]])))
print('   u가 후퇴를 0으로 만드는 값 = (h5 - h9)/4 = %.3f mm/yr (= 그 땅 융기가 같은 기간 해수면 상승 29.3 m를 상쇄)' % ((h5 - h9) / 4))
rec['grid'] = {'inv_s': inv.tolist(), 'u': us.tolist(), 'retreat_km': ret.reshape(60, 49).tolist(), 'seconds': dt_, 'P': P, 'nx': nx,
               'max_err': float(np.nanmax(np.abs(ret - an))), 'lines': lines, 'u_zero': (h5 - h9) / 4}
with open(os.path.join(HERE, 'p01-shoreline.json'), 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False)
