# -*- coding: utf-8 -*-
"""계산 6-3: 아프리카 습윤기 종료 연대는 위도에 따라 어긋나는가 (Shanahan 등, 2015의 주장을 논문 숫자로 시험).
입력(모두 논문이 적은 값, 연대는 cal BP):
  Tierney 등(2017): 31°N 약 6.5 ka (생물교란 모형 중앙값); 남쪽 세 코어(19.363, 23.206, 26.816 °N) 약 5.0, 5.3, 5.3 ka (코어별 대응은 요약에서 확인 못 함)
  deMenocal 등(2000): 서아프리카 연안 코어, 종료 중심 5490 +- 190 (위도 20°N대, 일사 계산 기준 20°N)
  Claussen 등(1999): CLIMBER-2 사하라 평균 5440 +- 30 (모형, 위도 구분 없음, 격자가 한 덩어리)
  Kuper와 Kröpelin(2006): 이집트 사하라에서 정기 몬순 비가 늦어도 기원전 5300년에 그침
위 값의 위도 대응과 정의가 서로 다르므로 이 계산은 '맞는지 보는 시연'이다."""
import numpy as np
from scipy import stats
def bce_to_bp(x):          # 기원전 x년 -> cal BP (서기 1950 기준, 천문학적 연도 0 = 기원전 1년)
    return x + 1949
print('[A] Kuper와 Kröpelin(2006)의 달력 연대 환산: 기원전 5300 = %d cal BP, 기원전 8500 = %d cal BP' % (bce_to_bp(5300), bce_to_bp(8500)))
print('    습윤기 길이 8500 -> 5300 BCE = %d 년 (논문: 약 3200 달력년)' % (8500-5300))
print()
lat_s = np.array([19.363, 23.206, 26.816]); age_s = np.array([5000., 5300., 5300.])
lat_n, age_n = 30.88, 6500.
print('[B] Tierney 등(2017) 두 묶음: 남쪽 세 코어 평균 위도 %.2f, 평균 연대 %.0f ; 북쪽 31°N(실제 %.2f°N) %.0f' % (lat_s.mean(), age_s.mean(), lat_n, age_n))
dl = lat_n-lat_s.mean(); da = age_n-age_s.mean()
print('    위도 차 %.2f 도, 연대 차 %.0f 년, 기울기 %.0f 년/도 = %.2f 년/km (1도 = 111 km)' % (dl, da, da/dl, da/dl/111.0))
print('    -> 종료 선이 북에서 남으로 %.2f km/년 (%.0f km/ka) 속도로 후퇴한 셈' % (dl*111/da, dl*111/da*1000))
print('    남쪽 코어끼리: 연대 순서(5000, 5300, 5300)를 위도 순(19.4, 23.2, 26.8)에 대응시키면 기울기 %.0f 년/도, 반대로 대응시키면 %.0f 년/도' % (np.polyfit(lat_s, age_s, 1)[0], np.polyfit(lat_s, age_s[::-1], 1)[0]))
print('    (논문 요약에서 코어별 대응을 확인하지 못했으므로 위 두 값은 가능한 대응의 양 끝이다)')
print()
print('[C] 모든 점을 한 표에 (위도는 논문이 준 것만)')
rows = [('Tierney 31°N', 30.88, 6500.), ('Tierney 남쪽 평균', lat_s.mean(), age_s.mean()), ('deMenocal 연안 코어', 20.0, 5490.)]
for r in rows: print('   %-22s 위도 %5.2f  종료 %5.0f' % r)
print('   (deMenocal 위도는 일사 계산의 20°N 로 대신함. 코어 좌표 표기는 추출 중 기호가 깨져 20°45′N, 18°35′W 로 읽었으나 확인 필요)')
print()
print('[D] 세 점 직선 적합과 부트스트랩(점 3개이므로 구간이 매우 넓다)')
X = np.array([r[1] for r in rows]); Y = np.array([r[2] for r in rows])
b, a = np.polyfit(X, Y, 1)
print('    기울기 %.0f 년/도, 절편 %.0f' % (b, a))
rng = np.random.default_rng(20261027)
bs = []
for _ in range(20000):
    i = rng.integers(0, 3, 3)
    if len(set(X[i])) < 2: continue
    bs.append(np.polyfit(X[i], Y[i], 1)[0])
bs = np.array(bs)
print('    부트스트랩 기울기 중앙 %.0f, 2.5~97.5%% = %.0f ~ %.0f (유효 %d회)' % (np.median(bs), np.percentile(bs, 2.5), np.percentile(bs, 97.5), len(bs)))
print('    -> 점 3개이므로 이 구간을 정량 증거로 읽을 수 없다. 방향(북쪽이 먼저 끝남)만 본다')
print()
print('[E] 방향 점검: Kuper(7249 BP, 이집트 사하라)와 Tierney 31°N(6500) 의 차 = %d 년' % (7249-6500))
print('    Kuper의 값은 고고 유적 점유의 끝 + 정기 비의 그침이고, Tierney의 값은 잎 왁스 수소 동위원소 종료다. 정의가 다르다.')
print('    CLIMBER-2 5440 은 단일 값(격자 10도, 서·동 사하라 구분 못 함)이라 위도 의존을 시험할 수 없다')
print()
print('[F] 가정한 선형 후퇴에 견준 습윤기 시작(약 8500 BCE, 북상 800 km, 위도 16~24°N)')
print('    Kuper와 Kröpelin: 열대 강수대가 수 세대 안에 최대 800 km 북상. 종료 후퇴 속도 %.2f km/년 와 시작 속도(800 km / 100 년이라고 가정하면 %.0f km/년)의 비 = %.1f' % (dl*111/da, 8.0, 8.0/(dl*111/da)))
print('    (시작 100년은 \"수 세대\"를 이 책이 100년 안팎으로 옮긴 가정이다)')
