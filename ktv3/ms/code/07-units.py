# -*- coding: utf-8 -*-
"""계산 0-7: 연대 단위 환산(cal BP, 서기/기원전 AD/BCE). 기준 1950년. 연 0은 없다(기원전 1년 다음이 서기 1년).
계산 0-6: 경도 1도 x 위도 1도 격자의 면적을 위도별로(WGS84 측지선 다각형, pyproj Geod)."""
from pyproj import Geod
g = Geod(ellps='WGS84')
print('=== 계산 0-7 cal BP -> 서기/기원전 (천문학 연수 1950-BP; 역사 연수는 음수일 때 1을 더해 기원전으로) ===')
for bp in [0, 100, 500, 1000, 1950, 2000, 2500, 3000, 4000, 4200, 5000, 6000, 8000, 10000, 11700]:
    y = 1950 - bp
    lab = ('서기 %d년' % y) if y >= 1 else ('기원전 %d년' % (1 - y))
    print('%6d cal BP | 1950-BP=%6d | %s | 간단식 BCE=BP-1949 -> %s' % (bp, y, lab, ('기원전 %d년' % (bp-1949)) if bp > 1949 else '해당 없음'))
print('\n=== 계산 0-6 위도 lat 에서 경도 1도 x 위도 1도 격자의 면적(km2) ===')
for lat in [0, 30, 40, 45, 50, 55, 60, 65, 70]:
    la0, la1 = lat, lat+1
    area, _ = g.polygon_area_perimeter([100, 101, 101, 100], [la0, la0, la1, la1])
    print('%2d~%2d° | %.1f km2 | 위도 비교 111.2x111.2xcos(%.1f°)=%.1f km2' % (la0, la1, abs(area)/1e6, lat+.5, 111.2*111.2*__import__('math').cos(__import__('math').radians(lat+.5))))
