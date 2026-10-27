# -*- coding: utf-8 -*-
"""계산 7-2: 빙하호 물 부피, 해수면 환산, 흐름률(Sv)의 일관성.
입력(논문): Hijma와 Cohen(2010): 지구 평균 해수면 도약 약 3.0 +- 1.2 m(본문 1.25), 부피 10.7 +- 4.5 x 10^14 m3, 서네덜란드가 지구 평균의 약 70%, Leverington 등(2002): 호수 부피 약 163,000 km3 = 약 0.46 m;
 Barber 등(1999): 10^14 m3 이상; Clarke 등(2004): Kinojevis 단계 최대 저장 40,000~151,000 km3, 홍수 약 5 Sv, 약 0.5 년; Alley 등(1997): 모형 대류 중단 문턱 약 0.015 Sv, 해수면으로 환산한 담수 약 0.07 Sv, 라브라도 호수가 1년에 빠지면 0.05 Sv;
 Obrist-Farner 등(2022): 상대 해수면 도약 2.60 +- 0.88 m."""
import numpy as np
YR = 365.25*24*3600
print('[A] Hijma와 Cohen 의 부피와 해수면 높이로 바다 면적을 거꾸로 구함')
A = 10.7e14/3.0
print('  10.7e14 m3 / 3.0 m = %.2e m2 (바다 면적에 해당; 지구 해양 면적 약 3.6e14 m2 라는 일반 값과 같은 크기)' % A)
rel_v = 4.5/10.7; rel_h = 1.2/3.0
print('  상대 오차: 부피 %.1f %%, 높이 %.1f %% (같은 숫자에서 나왔으면 같아야 한다)' % (100*rel_v, 100*rel_h))
print('  높이 오차 1.25 로 보면 %.1f %%' % (100*1.25/3.0))
print()
print('[B] 호수 부피의 해수면 환산(위의 면적 %.2e m2 사용)' % A)
for nm, km3 in (('Clarke Kinojevis 하한', 40000), ('Clarke Kinojevis 상한', 151000), ('Leverington 등', 163000), ('Barber 1e14 m3 이상', 1e14/1e9)):
    h = km3*1e9/A
    print('  %-24s %9.0f km3 = %.2e m3 -> %.2f m (지구 평균 해수면)' % (nm, km3, km3*1e9, h))
print('  Leverington 등이 적은 0.46 m 과 비교: 이 책 환산 %.2f m' % (163000e9/A))
print()
print('[C] 호수 부피가 Hijma와 Cohen 의 3.0 m 에서 차지하는 몫')
for nm, km3 in (('Clarke 하한', 40000), ('Clarke 상한', 151000), ('Leverington', 163000)):
    print('  %-12s %.2f m / 3.0 m = %.0f %%' % (nm, km3*1e9/A, 100*km3*1e9/A/3.0))
print()
print('[D] 같은 부피를 몇 년에 쏟았는가: 흐름률 (Sv = 1e6 m3/s)')
V = 10.7e14
print('  Hijma 총 부피 %.1e m3' % V)
for T in (0.5, 1, 5, 50, 200):
    print('    %6.1f 년 -> %8.2f Sv' % (T, V/(T*YR)/1e6))
print('  Leverington 부피 163,000 km3')
V2 = 163000e9
for T in (0.5, 1, 5, 50, 200):
    print('    %6.1f 년 -> %8.2f Sv' % (T, V2/(T*YR)/1e6))
print()
print('[E] Clarke 등의 5 Sv x 0.5 년 = %.2e m3 = %.0f km3 (논문 저장 범위 40,000~151,000 안인가: %s)' % (5e6*0.5*YR, 5e6*0.5*YR/1e9, 40000 <= 5e6*0.5*YR/1e9 <= 151000))
print('    Alley 등: 0.05 Sv 가 1년 = %.2e m3 = %.0f km3 (Clarke 하한 40,000 km3 의 %.1f %%)' % (0.05e6*YR, 0.05e6*YR/1e9, 100*0.05e6*YR/1e9/40000))
print('    Alley 등: 0.015 Sv 문턱이 200 년 = %.2e m3 (Hijma 총 부피의 %.2f %%)' % (0.015e6*200*YR, 100*0.015e6*200*YR/V))
print('    Alley 등: 0.07 Sv 가 200 년 = %.2e m3 -> %.2f m' % (0.07e6*200*YR, 0.07e6*200*YR/A))
print()
print('[F] 상대 해수면 도약: Hijma 2.11 +- 0.89 m (국지, 서네덜란드), 지구 평균 환산 3.0 +- 1.2; Obrist-Farner 등 2.60 +- 0.88 m (과테말라 이사발호, 국지)')
d = 2.60-2.11; sd = np.hypot(0.88, 0.89)
print('  두 국지 값의 차 %.2f m, 합성 오차 %.2f, z=%.2f' % (d, sd, d/sd))
print('  Obrist-Farner 등의 2.60 은 지구 평균이 아니라 한 지점의 값이다. 서네덜란드와 과테말라는 지각 균형 조정과 중력 지문이 달라 같은 양으로 읽을 수 없다')
print()
print('[G] 국지 값에서 지구 평균으로: Hijma 와 Cohen 은 서네덜란드가 지구 평균의 약 70% 를 기록한다고 가정')
print('  2.11 / 0.70 = %.2f m (논문 지구 평균 약 3.0 m)' % (2.11/0.70))
print('  불확실성: 2.11 +- 0.89 를 0.70 으로 나누면 +- %.2f m (논문 +-1.2~1.25)' % (0.89/0.70))
