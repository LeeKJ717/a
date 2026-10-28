# -*- coding: utf-8 -*-
"""계산 5-4: 논문이 적은 방류 부피를 유량(Sv)으로 바꾸고, Gerber 등(2025)이 적은 AMOC 세기 약 18 Sv와 나눈다.
입력은 모두 논문 초록 수준에서 옮긴 숫자: Barber 등(1999) 호수 방류 '10^14 m3 이상', Hijma와 Cohen(2010) 도약 10.7±4.5 x10^14 m3, Gerber 등(2025) 1 Sv 단위 AMOC 약 18 Sv.
방류 지속 시간은 논문이 초록에서 주지 않으므로 여러 값을 흔들어 본다(시연). 나누기는 산술이며 둘이 같은 종류의 양은 아니다(아래 한계).
"""
YR = 3.156e7
AMOC = 18.0
def sv(vol_m3, years):
    return vol_m3 / (years * YR) / 1e6
print('=== Barber 등(1999): 10^14 m3 이상 (하한), 지속 시간을 흔듦 ===')
for yrs in (1, 5, 10, 50, 100, 200, 500):
    s = sv(1e14, yrs)
    print('지속 %4d 년: %.3f Sv 이상  = AMOC 18 Sv 의 %.1f %%' % (yrs, s, 100 * s / AMOC))
print()
print('=== Hijma와 Cohen(2010): 10.7 (6.2~15.2) x10^14 m3, 지속 200 년은 해수면 도약의 지속(계산 5-1) ===')
for lab, v in (('하한', 6.2e14), ('중앙', 10.7e14), ('상한', 15.2e14)):
    for yrs in (50, 200, 500):
        s = sv(v, yrs)
        print('%s %.1e m3, %3d 년: %.3f Sv = AMOC 18 Sv 의 %.1f %%' % (lab, v, yrs, s, 100 * s / AMOC))
print()
print('=== 두 부피의 비: Hijma와 Cohen 중앙 / Barber 하한 = %.1f 배 (둘은 같은 양이 아님: 앞은 해수면 도약, 뒤는 호수 방류) ===' % (10.7e14 / 1e14))
print()
print('=== 4장 환산(계산 5-2)의 바다 평균 유량을 18 Sv 로 나눔 ===')
A = 3.61e14
for lab, r in (('MWP-1A 하한 40 mm/yr', 40), ('Lambeck 평균 12 mm/yr', 12), ('Hijma 평균 4.71 mm/yr', 4.71)):
    s = r * 1e-3 * A / YR / 1e6
    print('%-26s %.3f Sv = 18 Sv 의 %.1f %%' % (lab, s, 100 * s / AMOC))
print()
print('주의: 18 Sv 는 Gerber 등이 추정한 AMOC 의 세기(전 수심 합의 한 값)이고 방류 유량은 바다 전체나 특정 시점의 평균 산술이다. 퍼센트는 규모 비교일 뿐 순환이 줄어든 비율이 아니다.')
