# -*- coding: utf-8 -*-
"""계산 0-2: 이 책이 좌표를 확인한 빙핵 지점 쌍의 거리를 네 가지로 잰다.
(가) WGS84 타원체 측지선(pyproj Geod)  (나) 구면 대원(반지름 6371.0088 km, haversine)  (다) 위도 보정 없이 1도=111 km 를 곱한 평면 거리
(라) 극 입체 투영 위의 직선 거리(그린란드 EPSG:3413, 남극 EPSG:3031).  좌표는 2장 표 2-2(위키백과 빙핵 목록과 NOAA 기록)의 값이다."""
import math
from pyproj import Geod, Transformer
G = Geod(ellps='WGS84'); R = 6371.0088
def dms(d, m=0, s=0): return d + m / 60 + s / 3600
S = {  # 이름: (위도, 경도)
 'GRIP': (dms(72, 34, 44.4), -dms(37, 33, 55.2)), 'NGRIP': (dms(75, 6), -dms(42, 18)), 'NEEM': (dms(77, 27), -dms(51, 4)), '캠프 센추리': (dms(77, 10), -dms(61, 8)),
 'GISP2': (dms(72, 35), -dms(38, 28)), '다이3': (dms(65, 11), -dms(43, 50)), '렌란': (dms(71, 18), -dms(26, 42)),
 '보스토크': (-dms(78, 28), dms(106, 48)), '돔 C': (-75.1, 123.4), 'WAIS 디바이드': (-79.468, -112.086), '로 돔': (-dms(66, 46), dms(112, 48)), '제임스 로스 섬': (-dms(64, 13), -dms(57, 41))}
PAIRS = [('GRIP', 'NGRIP', 3413), ('GRIP', 'GISP2', 3413), ('NGRIP', 'NEEM', 3413), ('NEEM', '캠프 센추리', 3413), ('GRIP', '다이3', 3413), ('GRIP', '렌란', 3413), ('보스토크', '돔 C', 3031), ('보스토크', '로 돔', 3031), ('돔 C', '로 돔', 3031), ('보스토크', 'WAIS 디바이드', 3031), ('WAIS 디바이드', '제임스 로스 섬', 3031), ('GRIP', '보스토크', None)]
print('쌍 | 측지선 km | 구면 km | 구면의 차 % | 111 km 평면 km | 평면의 차 % | 투영 직선 km | 투영의 차 %')
for a, b, epsg in PAIRS:
    la1, lo1 = S[a]; la2, lo2 = S[b]
    d = G.inv(lo1, la1, lo2, la2)[2] / 1000
    p1, p2, dl = map(math.radians, (la1, la2, lo2 - lo1))
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    sph = 2 * R * math.asin(math.sqrt(h))
    flat = 111.0 * math.hypot(la2 - la1, lo2 - lo1)
    if epsg:
        t = Transformer.from_crs(4326, epsg, always_xy=True); x1, y1 = t.transform(lo1, la1); x2, y2 = t.transform(lo2, la2)
        pr = math.hypot(x2 - x1, y2 - y1) / 1000; ps = '%.1f | %+.2f' % (pr, (pr / d - 1) * 100)
    else: ps = '- | -'
    print('%s-%s | %.1f | %.1f | %+.2f | %.1f | %+.1f | %s' % (a, b, d, sph, (sph / d - 1) * 100, flat, (flat / d - 1) * 100, ps))
# GRIP-GISP2 : 2장 지도 캡션의 '약 28 km'
GISP2 = (dms(72, 35), -dms(38, 28)); la1, lo1 = S['GRIP']
print('GRIP-GISP2 (GISP2 = 72°35′N, 38°28′W, 2장 표 2-2): 측지선 %.1f km' % (G.inv(lo1, la1, GISP2[1], GISP2[0])[2] / 1000))
for g2 in ((dms(72, 35), -dms(38, 28)), (dms(72, 35, 30), -dms(38, 28, 30)), (dms(72, 34, 30), -dms(38, 27, 30))):   # 분 단위 반올림 범위 안의 흔들림 확인
    print('  GISP2 =', g2, '->', '%.1f km' % (G.inv(lo1, la1, g2[1], g2[0])[2] / 1000))
# 보스토크-WAIS 디바이드: 경도 차이를 218.9도 그대로 쓴 평면 값과 반대쪽 141.1도로 바꾼 값
la1, lo1 = S['보스토크']; la2, lo2 = S['WAIS 디바이드']
dlon = lo2 - lo1; wrapped = dlon + 360 if dlon < -180 else dlon
print('보스토크-WAIS 디바이드: 경도 차 %.1f도, 반대쪽 %.1f도; 111 km 평면 %.1f km, 반대쪽 경도 차로 %.1f km' % (abs(dlon), abs(wrapped), 111 * math.hypot(la2 - la1, dlon), 111 * math.hypot(la2 - la1, wrapped)))
