# -*- coding: utf-8 -*-
"""계산 2-2: 영거 드라이아스 끝(홀로세 시작)의 계단을 GISP2 d18O 에서 다시 찾고, 같은 계단 크기를 세 가지 기울기로 온도로 바꿔 본다.
논문 값: 홀로세 시작은 NGRIP d18O 에서 11,651 ± 13 b2k, 중수소 과잉에서 11,701 ± 1.5 b2k (Steffensen 등 2008), GISP2 의 경계 나이 11,690 b2k (Walker 등 2009),
         GICC05 11,703 b2k 최대 계수 오차 99년 (Rasmussen 등 2007, Walker 등 2009). b2k 는 BP 보다 50년 늦다(Walker 등 2009, 2018).
         온도 변화: Buizert 등(2014) 홀로세 전이 GISP2 12.4 ± 3.4 °C, NGRIP 10.9 ± 3.0, NEEM 8.4 ± 3.0. 현재의 공간 기울기 0.69 퍼밀/K, 레일리 모형 0.88 퍼밀/K.
         Cuffey & Clow(1997): 온도 = 3.05 °C/퍼밀 (8 ka 이전), 3.98 °C/퍼밀 (8~3 ka).
"""
import numpy as np
from scipy.optimize import least_squares
from io2 import gisp2
g = gisp2()
print('=== 계산 2-2 (1) 계단의 위치: 램프 맞춤 ===')
w = g[(g.age >= 10800) & (g.age <= 12800)].reset_index(drop=True)
t = w.age.values; y = w.d18o.values
def ramp(p, t):
    t0, dur, hi, lo = p     # t0: 램프 시작(젊은 쪽), dur: 램프 길이, hi: 홀로세 쪽 값, lo: 영거 드라이아스 쪽 값
    return np.where(t <= t0, hi, np.where(t >= t0 + dur, lo, hi + (lo - hi) * (t - t0) / dur))
def fit(t, y):
    best = None
    for dur0 in (10., 40., 80.):
        r = least_squares(lambda p: ramp(p, t) - y, [11580., dur0, -36.5, -40.4], bounds=([11300, 1, -38, -42], [11800, 200, -34, -39]))
        if best is None or r.cost < best.cost: best = r
    return best.x
p = fit(t, y)
mid = p[0] + p[1] / 2
print('맞춘 값: 램프 시작 %.0f BP, 길이 %.0f 년, 홀로세 쪽 %.2f, 영거 드라이아스 쪽 %.2f 퍼밀' % tuple(p))
print('램프 중점 %.0f BP = %.0f b2k (BP 에 50을 더함)' % (mid, mid + 50))
rng = np.random.default_rng(20261027)
res = np.array(y - ramp(p, t)); sd = res.std(ddof=4)
bs = []
for _ in range(2000):
    yy = ramp(p, t) + rng.choice(res, len(res), replace=True)
    try: q = fit(t, yy); bs.append(q[0] + q[1] / 2 + 50)
    except Exception: pass
bs = np.array(bs)
print('잔차 표준편차 %.2f 퍼밀. 잔차 재표집 2000회: 중점(b2k) 평균 %.0f, 표준편차 %.0f, 2.5~97.5 백분위 %.0f~%.0f' % (sd, bs.mean(), bs.std(), *np.percentile(bs, [2.5, 97.5])))
print('표본 간격(램프 부근 11,500~11,800 BP): %.0f 년' % np.diff(g[(g.age > 11500) & (g.age < 11800)].age.values).mean())
print('논문과 견줌(b2k): NGRIP d18O 11,651 ± 13 (Steffensen 2008); GISP2 경계 11,690 (Walker 2009); 중수소 과잉 11,701 ± 1.5; GICC05 11,703 (MCE 99)')
print('  이 책의 GISP2 램프 중점 - NGRIP d18O 11,651 = %+.0f 년; - GISP2 경계 11,690 = %+.0f 년; - 11,703 = %+.0f 년' % (mid + 50 - 11651, mid + 50 - 11690, mid + 50 - 11703))
print()
print('=== 계산 2-2 (2) 계단의 크기와 온도 환산 ===')
yd = g[(g.age >= 11800) & (g.age <= 12800)].d18o
eh = g[(g.age >= 8000) & (g.age <= 11000)].d18o
eh2 = g[(g.age >= 9000) & (g.age <= 11000)].d18o
for lab, a, b in (('영거 드라이아스 11.8~12.8 ka 평균과 8~11 ka 평균', yd, eh), ('같은 영거 드라이아스와 9~11 ka 평균', yd, eh2)):
    d = b.mean() - a.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    print('%s: %.2f vs %.2f -> 차 %.2f 퍼밀 (표본 %d, %d; 표준오차 %.2f)' % (lab, a.mean(), b.mean(), d, len(a), len(b), se))
d = eh.mean() - yd.mean()
print()
print('계단 %.2f 퍼밀을 온도로 바꾸면:' % d)
for lab, s_perK in (('현재의 공간 기울기 0.69 퍼밀/K (Buizert 2014)', 0.69), ('레일리 모형 0.88 퍼밀/K (Buizert 2014)', 0.88), ('Cuffey & Clow 8 ka 이전 3.05 °C/퍼밀 (= 0.328 퍼밀/K)', 1 / 3.05), ('Cuffey & Clow 8~3 ka 3.98 °C/퍼밀 (= 0.251 퍼밀/K)', 1 / 3.98)):
    print('  %-58s -> %5.1f K' % (lab, d / s_perK))
print('Buizert 등(2014)의 GISP2 홀로세 전이 온도 12.4 ± 3.4 °C 에서 거꾸로 구한 유효 기울기: %.2f 퍼밀/K (범위 %.2f~%.2f)' % (d / 12.4, d / (12.4 + 3.4), d / (12.4 - 3.4)))
print('  같은 방식으로 NGRIP 10.9 ± 3.0, NEEM 8.4 ± 3.0 이면 (같은 d18O 계단을 가정하는 것은 거칠다): %.2f, %.2f 퍼밀/K' % (d / 10.9, d / 8.4))
