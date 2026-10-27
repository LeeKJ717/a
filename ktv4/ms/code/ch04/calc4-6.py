# -*- coding: utf-8 -*-
"""계산 4-6: 제1권의 한반도 해수면 숫자와 전지구 숫자의 견줌. 한반도 숫자는 제1권 ch01-v2, ch02-v2에서 옮김(14C 나이로 적힌 것).
방사성탄소 나이를 IntCal20 으로 보정(c14cal.py). 오차 100 년은 시연값(제1권이 오차를 적지 않은 값에 한함).
"""
import numpy as np
import c14cal as C
print('=== (1) 제1권 14C 나이의 보정(IntCal20) ===')
for lab, a, e in (('10,000 BP (Jo 1980 -25 m)', 10000, 100), ('7,000 BP (Jo -10 m)', 7000, 100), ('6,000 BP (Jo 0 m)', 6000, 100),
                  ('8,610+-100 BP (쓰시마 해협 동물상)', 8610, 100)):
    r = C.summary(a, e)
    print('%-34s 중앙 %5.0f cal BP, 평균 %5.0f, sd %3.0f, 95%% HPD %s' % (lab, r['median'], r['mean'], r['sd'], ', '.join('%d~%d' % (s, t) for s, t, m in r['hpd'])))
print('  위 중앙값과 14C 나이의 차: 6,000 BP 는 %.0f 년, 7,000 BP 는 %.0f 년, 10,000 BP 는 %.0f 년 (보정 연대가 더 오래됨)' % (C.summary(6000,100)['median']-6000, C.summary(7000,100)['median']-7000, C.summary(10000,100)['median']-10000))
print()
print('=== (2) 14C 나이 vs 보정 연대: 속도 재계산(Jo 1980 동해안) ===')
t10 = C.summary(10000, 100)['median']; t7 = C.summary(7000, 100)['median']; t6 = C.summary(6000, 100)['median']
print('  14C 기준: -25 -> -10 m (10->7 ka) %.1f mm/yr; -10 -> 0 (7->6 ka) %.1f mm/yr' % (15 / 3.0, 10 / 1.0))
print('  보정 기준: 10 ka -> %.0f, 7 ka -> %.0f, 6 ka -> %.0f cal BP' % (t10, t7, t6))
print('            -25 -> -10 m: %.1f mm/yr; -10 -> 0: %.1f mm/yr' % (15 / ((t10 - t7) / 1000), 10 / ((t7 - t6) / 1000)))
print()
print('=== (3) 한반도 값 vs 전지구 값(같은 단위) ===')
rows = [
 ('Saito: 최저 -120+-10 m(LGM)', 'Lambeck -134 m(29~21 ka)', 134 - 120),
]
print('  LGM: Saito -120 vs Lambeck -134 -> 차 14 m (계산 4-1)')
print('  Saito -40 m 약 10 ka(14C?) 시기, 6~7 ka 에 현재 수준: 평균 10~13 mm/yr (계산 4-2) vs Lambeck 16.5~8.2 ka 평균 12 mm/yr, Hijma 2025 11~3 ka 평균 4.7 mm/yr')
# 시연: Hijma 2025 의 11->3 ka 상승량 37.7 m 를 3 ka 에 0~-3 m 이라 놓고 11 ka 값으로 환산
for lo in (0.0, -3.0):
    print('  시연: 3 ka 에 %+.0f m 라 놓으면 11 ka 에 %.1f m (37.7 m 상승, 2시그마 29.3~42.2 -> %.1f~%.1f m)' % (lo, lo - 37.7, lo - 42.2, lo - 29.3))
print('  제1권 Saito 는 10 ka 에 -40 m 를 적었다(14C 나이). 11 ka 값과 10 ka 값은 다른 나이이므로 직접 같다고 읽지 않고, 규모가 비슷한 범위(-30~-45 m)인 것만 적는다.')
print('  Ohshima: -45 m 12 ka, Clark 모형(남해): -31.7 m 9 ka, -12.2 m 7 ka; Wang 2022: 초기 홀로세 약 -50 m, 약 7 ka 현재 수준')
print('  제1권 Bloom과 Park(서해): 8.6~4.8 ka 에 6.1 m, 이후 0.4 mm/yr; 지난 6 ka 상승 5 m 미만. 전지구 후기 홀로세 속도(Vacchi) <2 mm/yr 보다 작다: 0.4 vs <2 mm/yr')
print('  Kim(1973) 융기 1.1~1.4 mm/yr vs Bloom과 Park 7.1 mm/yr: 두 값 모두 제1권이 서로 어긋난 채 적은 것이며 이 장은 가르지 않는다.')
