# -*- coding: utf-8 -*-
"""계산 0-3: 투영이 면적과 모양을 어떻게 바꾸는가. 위도별로 반지름 500 km 의 측지선 원을 만들어 투영한 뒤 (가) 투영 위 면적 / 구 위 면적, (나) 투영된 도형의 동서 폭 / 남북 높이를 구한다.
투영: 메르카토르(EPSG:3395), 이퀄 어스(EPSG:8857, 면적을 보존), 로빈슨(ESRI:54030, 면적을 보존하지 않는 절충 투영), 등장방형(+proj=eqc, 적도 기준).
"""
import math
from pyproj import Geod, Transformer
from shapely.geometry import Polygon
G = Geod(ellps='WGS84')
PR = {'메르카토르 3395': 'EPSG:3395', '이퀄 어스 8857': 'EPSG:8857', '로빈슨 54030': 'ESRI:54030', '등장방형(적도 기준) eqc': '+proj=eqc +lat_ts=0 +datum=WGS84 +units=m +no_defs'}
def circle(lon, lat, r=500000, n=180):
    pts = [G.fwd(lon, lat, 360 * i / n, r)[:2] for i in range(n)]
    return pts
print('원 중심 위도 | 구 위 면적(km2) | ' + ' | '.join('%s: 면적비, 폭/높이' % k for k in PR))
for lat in (0, 20, 40, 60, 70, 80):
    pts = circle(0, lat)
    ga, _ = G.polygon_area_perimeter([p[0] for p in pts], [p[1] for p in pts]); ga = abs(ga) / 1e6
    row = []
    for k, crs in PR.items():
        t = Transformer.from_crs(4326, crs, always_xy=True)
        xy = [t.transform(*p) for p in pts]; P = Polygon(xy)
        xs = [q[0] for q in xy]; ys = [q[1] for q in xy]
        row.append('%.3f, %.3f' % (P.area / 1e6 / ga, (max(xs) - min(xs)) / (max(ys) - min(ys))))
    print('%d | %.0f | %s' % (lat, ga, ' | '.join(row)))
# 메르카토르의 면적 척도 1/cos^2 와 비교(구 어림)
print('메르카토르 면적 배율 구 어림 1/cos(lat)^2: ' + ', '.join('%d도 %.2f' % (l, 1 / math.cos(math.radians(l)) ** 2) for l in (0, 20, 40, 60, 70, 80)))
# 이퀄 어스 정적성 확인: 면적비가 1 에서 벗어난 최대값(위 표에서)
