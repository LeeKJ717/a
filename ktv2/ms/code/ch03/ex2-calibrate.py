# -*- coding: utf-8 -*-
"""실습 3-2: 보정 곡선으로 제1권의 14C 날짜를 다시 보정해 제1권의 보정 범위와 견준다.
곡선(data/3Col_*.14C)이 없으면 "곡선 입수 확인 필요"를 출력하고 끝낸다."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from c14lib import *

try:
    CUR = {n: load_curve(n) for n in ('intcal20', 'intcal13', 'intcal04', 'marine20', 'marine13')}
except CurveMissing as e:
    print(e)
    sys.exit(0)

def cal_hull(c14, sd, name, level, r=0.0, sr=0.0):
    g, p = calibrate(c14, sd, CUR[name], r, sr)
    segs = hpd(g, p, level)
    return g, p, segs, (segs[0][0], segs[-1][1])

def show(label, c14, sd, name, pub=None, pub_is_year=False, r=0.0, sr=0.0):
    g, p, s95, h95 = cal_hull(c14, sd, name, 0.954, r, sr)
    s68 = hpd(g, p, 0.683)
    h68 = (s68[0][0], s68[-1][1])
    print(f'{label}: {c14}+-{sd} BP, {name}' + (f', 저장효과 {r}+-{sr}' if r else ''))
    print(f'    68.3%: {fmt_segs(s68, pub_is_year)}')
    print(f'    95.4%: {fmt_segs(s95, pub_is_year)}')
    print(f'    중앙값 {median_age(g, p):.0f} cal BP; 곡선 위 14C 나이 대 cal BP 의 구간 개수(95.4%): {len(s95)}')
    if pub:
        lo, hi = pub     # cal BP
        print(f'    제1권 범위 {lo}~{hi} cal BP: 이 책 68.3% 외곽 {h68[0]:.0f}~{h68[1]:.0f} (차 {h68[0]-lo:+.0f}, {h68[1]-hi:+.0f}); 95.4% 외곽 {h95[0]:.0f}~{h95[1]:.0f} (차 {h95[0]-lo:+.0f}, {h95[1]-hi:+.0f})')
    return g, p, s68, s95

print('=' * 70)
print('[3-2a] 곡선 자체 점검')
for n, (c, m, s) in CUR.items():
    print(f'  {n}: {len(c)} 행, cal BP {c.min():.0f}~{c.max():.0f}, 14C {m.min():.0f}~{m.max():.0f}, 첫 행 ({c[0]:.0f},{m[0]:.0f},{s[0]:.0f}), 끝 행 ({c[-1]:.0f},{m[-1]:.0f},{s[-1]:.0f})')
c, m, s = CUR['intcal20']
print('  IntCal20 에서 14C 나이가 줄어들거나 평평한 구간(고원)의 예: 2,400 BP 근처의 cal BP 범위')
mask = (m > 2380) & (m < 2420)
print(f'    14C 나이 2380~2420 에 해당하는 cal BP: {c[mask].min():.0f}~{c[mask].max():.0f} ({mask.sum()} 행)')
print('  곡선이 단조가 아닌 곳(14C 나이가 cal 이 늘 때 줄어드는 곳)의 행 수:', int((np.diff(m) < 0).sum()), '/', len(m) - 1)

print('=' * 70)
print('[3-2b] 제1권 9장 (Ma 등, 2025): IntCal20. 제1권은 475+-20 과 2050+-20 을 14C 나이(BP)로 읽었다')
show('HZ-14C-55 를 14C 나이 475+-20 으로 읽으면', 475, 20, 'intcal20', pub=(455, 495))
show('WZ 이탄 를 14C 나이 2050+-20 으로 읽으면', 2050, 20, 'intcal20', pub=(2029, 2069))
print('  논문의 보정 범위(1455~1495 CE = 495~455 cal BP, 기원전 120~80년 = 2069~2029 cal BP)는 이 14C 나이의 IntCal20 보정과 맞지 않는다(제1권은 이 점검을 하지 못했다).')
print('  범위의 가운데: (1455+1495)/2 = 1475 = 1950-475, (-119+-79)/2 = -99 = 1950-2049. 475 와 2050 은 보정 범위의 가운데(cal BP)와 같다.')
c, m, s = CUR['intcal20']
for cb in (455, 475, 495, 2029, 2050, 2069):
    print(f'    곡선이 가리키는 cal {cb} 의 14C 나이: {np.interp(cb, c, m):.0f}')
print('  제1권이 "이 열의 이름을 확인하지 못했다"고 적은 385 를 14C 나이로 읽어 본다(시연: 오차 +-20 을 475 와 같게 가정):')
show('HZ-14C-55 를 14C 나이 385+-20 으로 읽으면', 385, 20, 'intcal20', pub=(455, 495))
print('  -> 385+-20 의 68.3% 가운데 큰 덩어리가 455~494 cal BP 로 논문의 1455~1495 CE 와 같다. 475+-20 은 14C 나이가 아니라 보정 연대(cal BP)로 읽는 쪽이 이 계산과 맞는다. 원문 표의 열 이름은 이 책이 확인하지 못했으므로 "원문 쪽 확인 필요".')
print('  WZ 이탄은 14C 나이를 알지 못해 같은 시험을 하지 못한다(2050+-20 을 14C 나이로 읽은 결과는 위와 같고 논문 범위와 맞지 않는다).')

print('=' * 70)
print('[3-2c] 제1권 4장 (Okuno 등, 2010: IntCal04, CALIB 5.0)')
show('오쿠노 4940 BP', 4940, 35, 'intcal04', pub=(5600, 5734))
show('4940 BP, IntCal20 로 다시', 4940, 35, 'intcal20')
show('오쿠노 9785 BP', 9785, 35, 'intcal04', pub=(11126, 11177))
show('9785 BP, IntCal20 로 다시', 9785, 35, 'intcal20')
for t in (7525, 8030):
    show(f'U-3 {t} BP', t, 35, 'intcal20')

print('=' * 70)
print('[3-2d] 제1권 6장 표 6-5 (Park 등, 2019, GY-1, IntCal13). 범위 폭으로 보아 2 시그마로 읽는다')
gy = [(363, 1800, 30, 1625, 1819), (739, 2810, 30, 2846, 2997), (889, 4150, 30, 4578, 4825), (917, 6100, 40, 6863, 7157),
      (1416, 7210, 40, 7956, 8158), (1839, 7900, 40, 8595, 8976), (2060, 7960, 40, 8649, 8990), (2351, 8030, 40, 8764, 9024), (2892, 8870, 40, 9785, 10173)]
rows = []
for d, c14, sd, lo, hi in gy:
    g, p, s95, h95 = cal_hull(c14, sd, 'intcal13', 0.954)
    g20, p20, s95_20, h20 = cal_hull(c14, sd, 'intcal20', 0.954)
    mid_pub = (lo + hi) / 2
    print(f'  {d:5d} cm {c14}+-{sd}: 제1권 {lo}~{hi} (중간 {mid_pub:.1f}) | IntCal13 95.4% 외곽 {h95[0]:.0f}~{h95[1]:.0f} (차 {h95[0]-lo:+.0f},{h95[1]-hi:+.0f}; 중앙값 {median_age(g,p):.0f}; 구간 {len(s95)}개) | IntCal20 외곽 {h20[0]:.0f}~{h20[1]:.0f} (중앙값 {median_age(g20,p20):.0f})')
    rows.append((d, c14, sd, lo, hi, h95, median_age(g, p), h20, median_age(g20, p20)))
mx = max(max(abs(r[5][0] - r[3]), abs(r[5][1] - r[4])) for r in rows)
for d, c14, sd in ((739, 2810, 30), (2351, 8030, 40)):
    g, p, s95, h95 = cal_hull(c14, sd, 'intcal13', 0.954)
    print(f'  {d} cm 의 95.4% 구간들: {fmt_segs(s95)}')
print(f'  IntCal13 95.4% 외곽과 제1권 범위 끝의 최대 차이: {mx:.0f} 년')
inside = sum(1 for r in rows if r[5][0] <= r[3] + 15 and r[5][1] >= r[4] - 15)
print(f'  제1권 범위가 이 책 외곽 안에(15 년 여유) 들어가는 날짜: {inside}/9')

print('=' * 70)
print('[3-2e] 제1권 6장 호륜호 HL06 (Xiao 등, 2018, IntCal04, 저장효과 685+-21 을 뺀 나이)')
xi = [(59, 2537, 36, 2480, 2650), (69, 2945, 34, 2970, 3220), (79, 3349, 37, 3470, 3690), (89, 3890, 37, 4230, 4430), (101, 4619, 34, 5290, 5470)]
for d, c14, sd, lo, hi in xi:
    g, p, s95, h95 = cal_hull(c14, sd, 'intcal04', 0.954)
    s68 = hpd(g, p, .683)
    print(f'  {d} cm {c14}+-{sd}: 제1권 {lo}~{hi} | 95.4% 외곽 {h95[0]:.0f}~{h95[1]:.0f} (차 {h95[0]-lo:+.0f},{h95[1]-hi:+.0f}) | 68.3% 외곽 {s68[0][0]:.0f}~{s68[-1][1]:.0f}')
for d, c14, sd in ((59, 2537, 36), (89, 3890, 37)):
    g, p, s95, h95 = cal_hull(c14, sd, 'intcal04', 0.954)
    print(f'  {d} cm 의 95.4% 구간들: {fmt_segs(s95)}')
print('  59 cm: 제1권 범위 2480~2650 은 첫 구간(2489~2643, 60.1%)과 맞고, 확률 35.4% 의 둘째 구간(2668~2748)은 제1권 표에 없다. 89 cm: 4231~4421(92.6%)이 제1권 4230~4430 과 맞고 아래쪽의 작은 곁가지(합 2.9%)가 외곽을 넓힌다. 원문(OxCal 3.1)이 어떤 구간만 적었는지는 이 책이 확인하지 못했다.')

print('=' * 70)
print('[3-2f] 제1권 6장 6.2절 (Park 등, 2018, 비금도): 해양 시료. 원문은 저장 효과 보정을 믿기 어렵다고 쓴다')
mar = [(10500, 40, 12240, 12590), (13590, 40, 16190, 16580)]
for n in ('intcal13', 'intcal20', 'marine13', 'marine20'):
    out = []
    for c14, sd, lo, hi in mar:
        g, p, s95, h = cal_hull(c14, sd, n, 0.954)
        out.append(f'{c14}: {h[0]:.0f}~{h[1]:.0f}')
    print(f'  {n:9s} (DeltaR 0): ' + ' | '.join(out) + f'  [제1권 {mar[0][2]}~{mar[0][3]}, {mar[1][2]}~{mar[1][3]}]')
print('  -> 제1권(Park 등, 2018)의 보정 범위는 해양 곡선 없이 대기 곡선 IntCal13 으로 보정해야 재현된다(차이 4 년 이내). 해양 곡선과 DeltaR 0 으로는 약 600~900 년 젊게 나온다.')
print('  논문이 쓴 소프트웨어, 곡선, DeltaR 은 이 책이 확인하지 못했다. 이 책이 아는 것은 "이 숫자들이 대기 곡선 보정과 맞는다"는 계산 결과뿐이다.')

print('=' * 70)
print('[3-2g] 제1권 11장 11.2절 이론 상자의 시연 나이를 보정 (시연: 오차 +-30 BP 를 가정)')
for F in (0.45, 0.80, 0.38):
    t = age_from_F(F)
    g, p, s95, h = cal_hull(t, 30, 'intcal20', 0.954)
    print(f'  F={F}: {t:.0f} BP -> 95.4% {fmt_segs(s95)}; 중앙값 {median_age(g,p):.0f} cal BP')
print('  제1권 11.2.1절의 12D56 은 7.9~7.75 ka cal BP (논문 값). 보정 전 7,773 BP 는 논문의 값이 아니므로 직접 견주지 않는다.')
print('  7.9~7.75 ka cal BP 에 해당하는 IntCal20 의 14C 나이:', f'{np.interp(7750, *CUR["intcal20"][:2]):.0f} ~ {np.interp(7900, *CUR["intcal20"][:2]):.0f} BP')
print('  (거꾸로 읽기: 논문의 cal BP 에서 곡선의 14C 나이를 읽으면, 보정 전 나이의 대략을 가늠할 수 있다.)')

print('=' * 70)
print('[3-2h] 제1권 2장: 김(1973)의 숯 12,060+-600 BP 와 이탄 1,730+-100 BP')
for c14, sd in ((12060, 600), (1730, 100)):
    g, p, s95, h = cal_hull(c14, sd, 'intcal20', 0.954)
    print(f'  {c14}+-{sd}: 95.4% {fmt_segs(s95)}; 외곽 {h[0]:.0f}~{h[1]:.0f}; 중앙값 {median_age(g,p):.0f} cal BP')
print('  제1권 2장은 보정하지 않고 14C 나이 그대로 속도를 계산했다. 보정 후 12,060 BP 는 약 1,000 년 이상 늙어진다: 단구 융기 속도(13 m / T)가 그만큼 작아진다.')
for T in (12060, median_age(*calibrate(12060, 600, CUR['intcal20']))):
    print(f'    13 m / {T:.0f} 년 = {13000/T:.3f} mm/yr')
