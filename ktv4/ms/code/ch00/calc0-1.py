# -*- coding: utf-8 -*-
"""계산 0-1: 위도별 경도 1도와 위도 1도의 길이(WGS84 타원체)와 '1도=111 km' 어림의 오차.
경도 1도 = (pi/180) * a * cos(phi) / sqrt(1 - e2 sin^2 phi), 위도 1도 = (pi/180) * a (1-e2) / (1 - e2 sin^2 phi)^1.5.
pyproj 측지선 거리로 같은 값을 다시 구해 식과 맞는지 검사한다."""
import math
from pyproj import Geod
a = 6378137.0; f = 1 / 298.257223563; e2 = f * (2 - f)
G = Geod(ellps='WGS84')
print('위도 | 경도 1도(km, 식) | 경도 1도(km, 측지선) | 위도 1도(km, 식) | 111 km 어림이 경도에 대해 몇 배인가 | 식과 측지선 차(m)')
for lat in (0, 10, 20, 30, 40, 45, 50, 60, 66.5, 70, 75, 80, 85, 89, 90):
    p = math.radians(lat); w = 1 - e2 * math.sin(p) ** 2
    lon_km = math.pi / 180 * a * math.cos(p) / math.sqrt(w) / 1000
    lat_km = math.pi / 180 * a * (1 - e2) / w ** 1.5 / 1000
    la = min(lat, 89.9999)
    _, _, d = G.inv(0, la, 1, la); g_km = d / 1000
    if lat >= 89.9: g_km = float('nan')
    print('%5.1f | %8.3f | %8.3f | %8.3f | %6.2f | %7.2f' % (lat, lon_km, g_km, lat_km, 111.0 / lon_km if lon_km > 0 else float('inf'), (lon_km - g_km) * 1000))
# 111 km 어림이 20% 틀리는 위도, 두 배 틀리는 위도
for tgt in (1.10, 1.25, 2.0):
    lo, hi = 0.0, 89.9
    for _ in range(60):
        m = (lo + hi) / 2; p = math.radians(m); w = 1 - e2 * math.sin(p) ** 2
        r = 111.0 / (math.pi / 180 * a * math.cos(p) / math.sqrt(w) / 1000)
        if r < tgt: lo = m
        else: hi = m
    print('어림이 경도 방향으로 %.2f배가 되는 위도: %.2f 도' % (tgt, lo))
