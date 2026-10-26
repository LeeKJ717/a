# -*- coding: utf-8 -*-
"""계산 0-1: 위도에 따라 경도 1도와 위도 1도의 길이(WGS84 측지선, 구 근사와 비교)."""
import math
from pyproj import Geod
G = Geod(ellps='WGS84')
R = 6371.0088
print('위도  경도1도(WGS84,km)  경도1도(구,km)  위도1도(WGS84,km)  위도1도(구,km)  "111 km x cos(위도)" 근사')
for lat in (0, 30, 40, 45, 50, 55, 60, 65, 70, 75):
    _, _, d1 = G.inv(100, lat, 101, lat)
    _, _, d2 = G.inv(100, lat - 0.5, 100, lat + 0.5)
    sph_lon = R * math.cos(math.radians(lat)) * math.radians(1)
    sph_lat = R * math.radians(1)
    print('%3d  %18.2f  %14.2f  %17.2f  %14.2f  %10.2f' % (lat, d1 / 1000, sph_lon, d2 / 1000, sph_lat, 111.0 * math.cos(math.radians(lat))))
