# -*- coding: utf-8 -*-
"""계산 0-4: Natural Earth 10 m 육지 다각형의 면적을 정적 투영(EPSG:6933, 원통 정적)으로 재고, 메르카토르(EPSG:3395) 위 면적과 비교한다.
다각형이 대륙과 일치하는 것은 아니다(아프리카와 유라시아는 시나이에서 한 다각형으로 이어져 있다). 가장 큰 다각형 몇 개와 그린란드, 오스트레일리아 본섬을 본다.
메르카토르는 위도 85도 안쪽만 투영되므로 남극 대륙은 위도 -85 아래를 잘라 낸 면적을 따로 적는다."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'scripts'))
import geopandas as gpd
from shapely.geometry import box, Point
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
g = gpd.read_file(os.path.join(ROOT, 'geodata', 'ne_10m_land.geojson'))
polys = [p for geom in g.geometry for p in (geom.geoms if hasattr(geom, 'geoms') else [geom])]
print('육지 다각형 수:', len(polys))
gs = gpd.GeoSeries(polys, crs=4326)
ae = gs.to_crs(6933).area / 1e6
order = ae.sort_values(ascending=False).index[:8]
pts = {'유라시아와 아프리카': (80, 50), '아메리카(두 대륙이 파나마에서 한 다각형)': (-100, 50), '남극 대륙': (0, -80), '그린란드': (-40, 72), '오스트레일리아': (134, -25)}
print('이름 | 정적 면적 km2(EPSG:6933) | 메르카토르 위 면적 km2(위도 -85~85 로 자름) | 비(메르카토르/정적, 같은 자른 부분의 정적 면적 기준)')
res = {}
cut = box(-180, -85, 180, 85)
for nm, (lo, la) in pts.items():
    cand = [i for i, p in enumerate(polys) if p.contains(Point(lo, la))]
    if not cand: print(nm, '다각형을 못 찾음'); continue
    p = polys[cand[0]]
    q = p.intersection(cut)
    a_eq = gpd.GeoSeries([p], crs=4326).to_crs(6933).area.iloc[0] / 1e6
    a_eq_cut = gpd.GeoSeries([q], crs=4326).to_crs(6933).area.iloc[0] / 1e6
    a_m = gpd.GeoSeries([q], crs=4326).to_crs(3395).area.iloc[0] / 1e6
    res[nm] = (a_eq, a_eq_cut, a_m)
    print('%s | %.0f | %.0f | %.2f' % (nm, a_eq, a_m, a_m / a_eq_cut))
print('같은 다각형 면적 비교(정적 6933): 그린란드 / 오스트레일리아 = %.3f ; 메르카토르 위 = %.3f' % (res['그린란드'][0] / res['오스트레일리아'][0], res['그린란드'][2] / res['오스트레일리아'][2]))
print('아프리카만 따로 떼지 못해(유라시아와 한 다각형) 그린란드 / 아메리카 정적 %.3f, 메르카토르 %.3f' % (res['그린란드'][0] / res['아메리카(두 대륙이 파나마에서 한 다각형)'][0], res['그린란드'][2] / res['아메리카(두 대륙이 파나마에서 한 다각형)'][2]))
print('참고: 정적 면적은 NE 10 m 윤곽 기준이며 얼음 위 윤곽(남극, 그린란드의 빙붕 포함 여부)은 다각형 정의를 따른다. 외부 통계값과는 대조하지 않았다.')
