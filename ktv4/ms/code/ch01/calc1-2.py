# -*- coding: utf-8 -*-
"""계산 1-2: 방사성탄소 연대가 달력 연대로 바뀔 때 오차가 얼마나 퍼지는가 (IntCal20, 이 책의 c14cal.py).
입력의 14C 연대는 모두 시연값이다(어느 시료의 값도 아니다). 곡선은 Reimer 등(2020)의 IntCal20 파일(PyPI 패키지 사본)이다.
Marine20(Heaton 등 2020) 곡선 파일은 구하지 못했으므로 해양 시료의 보정은 하지 않는다. 마지막 (3)은 저장 효과를 무시한 오류의 크기를 보이는 시연이다.
"""
import numpy as np
import c14cal as C
print('=== 계산 1-2 (1) 14C 연대 오차 ±50 인 시연값을 보정한 95.4% 최고확률구간의 폭 ===')
print('14C BP   평균 cal BP   표준편차   95.4% 구간 폭의 합   구간 수   전체 범위/196 (14C 오차 ±50 의 95.4% 폭 196 년)')
base = 2 * 1.96 * 50
rows = []
for a in range(1000, 12001, 1000):
    s = C.summary(float(a), 50.0)
    w = sum(h[0] - h[1] for h in s['hpd'])
    span = max(h[0] for h in s['hpd']) - min(h[1] for h in s['hpd'])
    rows.append((a, s['mean'], s['sd'], w, len(s['hpd']), span))
    print('%6d   %10.0f   %8.0f   %12.0f (전체 범위 %5.0f)   %3d   %5.2f' % (a, s['mean'], s['sd'], w, span, len(s['hpd']), span / base))
print()
print('=== 계산 1-2 (2) 곡선이 평평한 곳(달력 100년 동안 14C 연대가 60년 미만 변하는 구간) ===')
t = C.CAL; c = C.C14
for lo, hi in ((9000, 8000), (10200, 9800), (11000, 10000)):
    pass
# 곡선에서 14C 연대가 거의 변하지 않는 구간을 찾는다: 달력 100년 동안 14C 변화가 100년 미만
cal = np.arange(5000, 13000, 1.0)
c14 = np.interp(cal, t, c)
d100 = np.interp(cal + 100, t, c) - c14
flat = cal[np.abs(d100) < 60]
print('달력 5000~13,000 cal BP 중 달력 100년 동안 14C 연대가 60년도 안 변하는 해(평평한 곳): %d 개 해' % len(flat))
# 가장 긴 연속 구간
runs = []
if len(flat):
    st = flat[0]; pv = flat[0]
    for x in flat[1:]:
        if x != pv + 1:
            runs.append((st, pv)); st = x
        pv = x
    runs.append((st, pv))
runs.sort(key=lambda r: r[1] - r[0], reverse=True)
for r in runs[:5]:
    print('   cal BP %5.0f ~ %5.0f (길이 %4.0f 년), 이 구간의 14C 연대 %.0f ~ %.0f' % (r[0], r[1], r[1] - r[0], np.interp(r[0], t, c), np.interp(r[1], t, c)))
print()
print('=== 계산 1-2 (3) 시연: 해양 시료의 14C 연대에 저장 효과를 빼지 않고 IntCal20 으로 보정하면 ===')
print('Heaton 등(2020): 홀로세(0~11.6 cal kBP)의 전지구 평균 해양 저장 연령은 약 500 14C년. 아래는 그 500년을 빼지 않은 경우와 뺀 경우의 달력 연대 평균 차(시연, Marine20 아님)')
for a in (3000, 6000, 9000):
    m0 = C.summary(float(a), 50.0)['mean']; m1 = C.summary(float(a - 500), 50.0)['mean']
    print('  14C %5d ± 50: 저장 효과를 빼지 않으면 평균 %.0f cal BP, 500년 빼면 %.0f cal BP, 차 %.0f 년' % (a, m0, m1, m0 - m1))
print()
print('=== 계산 1-2 (4) 영거 드라이아스 끝(GICC05 11,703 b2k = 11,653 BP)의 14C 연대는 IntCal20 곡선에서 ===')
v = np.interp(11653.0, t, c)
sc = np.interp(11653.0, t, C.SIG)
print('  cal 11,653 BP 의 곡선 14C 연대 %.0f, 곡선 오차 %.0f. (참고: 곡선 위 같은 14C 연대가 나오는 달력 연대의 범위를 아래에서 센다)' % (v, sc))
cal2 = np.arange(11000, 12500, 1.0)
c142 = np.interp(cal2, t, c)
ok = cal2[np.abs(c142 - v) <= 50]
print('  14C 연대가 %.0f ± 50 안에 드는 달력 연대: %.0f ~ %.0f cal BP (폭 %.0f 년)' % (v, ok.min(), ok.max(), ok.max() - ok.min()))
