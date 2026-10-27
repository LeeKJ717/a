# -*- coding: utf-8 -*-
"""계산 3-2: Taylor Dome(Indermuhle 등 1999 자료표)의 홀로세 이산화탄소에서 같은 꺾는 점 분석을 하고, Dome C 와 견준다.
두 코어는 나이 눈금이 다르다(Taylor Dome 자료표는 'years BP 1950' 표본 나이, Dome C 는 EDC1 연대). 나이를 어긋나게 해 보며 두 곡선이 가장 잘 맞는 어긋남을 찾는다.
"""
import numpy as np
import common3 as C
td, yd, sd, dd = C.taylor()
te, ye, se, de = C.edc()
print('=== 계산 3-2 (1) 표 점검 ===')
print('Taylor Dome: 행 %d개, 나이 %d~%d yr BP, 깊이 오름차순 %s, 나이 오름차순 %s' % (len(td), td.min(), td.max(), bool(np.all(np.diff(dd) > 0)), bool(np.all(np.diff(td) > 0))))
print('Taylor Dome 점별 표준편차(자료표의 +/-, 다섯 값의 표준편차) 평균 %.2f ppm, 범위 %.1f~%.1f' % (sd.mean(), sd.min(), sd.max()))
print()
print('=== (2) Taylor Dome 1000년 칸 평균 ===')
lows = []; mt = []
for lo in range(0, 12000, 1000):
    k = (td >= lo) & (td < lo + 1000)
    if k.sum() == 0: continue
    lows.append(lo); mt.append(yd[k].mean())
    print('%5d~%5d  n=%2d  평균 %.1f ppm  표준편차 %.2f' % (lo, lo + 1000, k.sum(), yd[k].mean(), yd[k].std(ddof=1) if k.sum() > 1 else float('nan')))
lows = np.array(lows); mt = np.array(mt)
print('칸 평균이 가장 낮은 칸: %d~%d yr BP, %.1f ppm' % (lows[np.argmin(mt)], lows[np.argmin(mt)] + 1000, mt.min()))
def win(a, b):
    k = (td >= a) & (td <= b); return k.sum(), yd[k].mean(), yd[k].std(ddof=1)
for a, b, note in ((10000, 11200, '정점 시기(논문 268 ppm)'), (7500, 8500, '8 ka 부근(논문 261 ppm)'), (390, 2000, '0.4~2 ka(논문: 최근 수천 년에 280~285 ppm)')):
    n, mu, s_ = win(a, b); print('%5d~%5d  n=%2d  평균 %.1f  표준편차 %.2f   %s' % (a, b, n, mu, s_, note))
print('논문(Ruddiman 2003)이 적은 값: 정점 268, 8 ka 261, 최근 280~285 -> 이 책 표의 같은 시기 평균으로 다시 구한 값은 위와 같다.')
print()
print('=== (3) 꺾는 점(연속 꺾은선, 나이 390~11,103 yr BP) ===')
k = td <= 11103
x = 11.2 - td[k] / 1000.0; yy = yd[k]
sse, x0, beta = C.hinge_fit(x, yy, 1.0, 9.0, step=0.05)
print('꺾는 점 나이 %.2f ka. 앞 기울기 %.2f ppm/ka, 뒤 기울기 %.2f ppm/ka, 잔차 표준편차 %.2f ppm, 꺾는 점의 값 %.1f ppm' % (11.2 - x0, beta[1], beta[1] + beta[2], np.sqrt(sse / (len(yy) - 4)), beta[0]))
rng = np.random.default_rng(3402)
ba = []
for _ in range(1000):
    i = rng.integers(0, len(x), len(x))
    _, xb, _b = C.hinge_fit(x[i], yy[i], 1.0, 9.0, step=0.1); ba.append(11.2 - xb)
print('부트스트랩 1000회(시드 3402): 꺾는 점 나이 2.5/50/97.5 백분위 = %s ka' % np.round(np.percentile(ba, [2.5, 50, 97.5]), 2))
print()
print('=== (4) 두 코어를 같은 나이에서 견주기 ===')
# Dome C 를 Taylor Dome 나이에서 선형 보간
def diff_at(shift):
    ta = td + shift          # Taylor Dome 나이를 shift 만큼 늦춘다(+이면 더 오래된 나이로)
    ok = (ta >= te.min()) & (ta <= 11000)
    yi = np.interp(ta[ok], te, ye)
    return ta[ok], yd[ok] - yi
ta, d0 = diff_at(0)
print('겹치는 나이 %d~%d yr BP, 점 %d개' % (ta.min(), ta.max(), len(ta)))
print('Taylor Dome - Dome C(보간): 평균 %.2f ppm, 표준편차 %.2f ppm, 제곱평균제곱근 %.2f ppm' % (d0.mean(), d0.std(ddof=1), np.sqrt(np.mean(d0 ** 2))))
for a, b in ((390, 2000), (2000, 5000), (5000, 8000), (8000, 11000)):
    k = (ta >= a) & (ta < b)
    print('   %5d~%5d: n=%2d  평균 차 %.2f ppm' % (a, b, k.sum(), d0[k].mean()))
print()
print('나이 어긋남을 -1000~+1000 yr 에서 100년씩 바꾸며, 평균 차를 뺀 뒤의 표준편차(두 곡선의 모양 차이)를 구한다:')
res = []
for sh in range(-1000, 1001, 100):
    ta2, dd2 = diff_at(sh)
    res.append((sh, len(ta2), dd2.mean(), dd2.std(ddof=1)))
    print('   어긋남 %+5d yr  n=%2d  평균차 %+.2f  표준편차 %.2f' % res[-1])
best = min(res, key=lambda r: r[3])
print('표준편차가 가장 작은 어긋남: %+d yr (표준편차 %.2f ppm; 어긋남 0 에서는 %.2f ppm)' % (best[0], best[3], [r for r in res if r[0] == 0][0][3]))
print('비교용 숫자: Ruddiman(2003)은 Taylor Dome 의 1000 yr BP 이전 연대 오차를 +-500 yr 로 적었고, Monnin 등(2001)은 Dome C 의 얼음 나이-가스 나이 차이가 홀로세에 약 2000 yr 이고 불확실성이 약 10% 라고 적었다(= 약 200 yr).')
print('(어긋남에 따른 표준편차 변화는 작아서 이 점 수에서는 어긋남을 하나로 정하기 어렵다. 가스 나이 모형 자체를 다시 만든 것이 아니다.)')
