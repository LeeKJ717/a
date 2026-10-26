# -*- coding: utf-8 -*-
"""계산 0-5: Natural Earth 도형 사이의 가장 가까운 거리. 지도에서 "닿아 있다", "끊겨 있다" 를 눈이 아니라 숫자로 말하려는 계산.
방법: 두 도형을 등적 투영(EPSG:6933)에서 가장 가까운 점 쌍으로 잇고, 그 두 점을 경위도로 되돌려 WGS84 측지선 거리를 잰다.
이 숫자는 Natural Earth 10m 도형의 거리이며 실제 하천과 호수의 연결을 확인한 것이 아니다(강 중심선은 단순화한 선이다)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union, nearest_points
from pyproj import Geod, Transformer
G = Geod(ellps='WGS84')
to = Transformer.from_crs(4326, 6933, always_xy=True); back = Transformer.from_crs(6933, 4326, always_xy=True)
def L(n, bb=None):
    return gpd.read_file(os.path.join(ROOT, 'geodata', n + '.geojson'), bbox=bb)
def proj(g):
    return gpd.GeoSeries([g], crs=4326).to_crs(6933).iloc[0]
def gap(a, b):
    pa, pb = nearest_points(proj(a), proj(b))
    la = back.transform(pa.x, pa.y); lb = back.transform(pb.x, pb.y)
    _, _, d = G.inv(la[0], la[1], lb[0], lb[1])
    return d / 1000, la, lb
lk = L('ne_10m_lakes'); rv = L('ne_10m_rivers_lake_centerlines'); pp = L('ne_10m_populated_places_simple')
def lake(*n): return unary_union(list(lk[lk['name'].isin(n)].geometry))
def river(*n): return unary_union(list(rv[rv['name'].isin(n)].geometry))
def city(n, c=None):
    q = pp[pp['name'] == n]
    if c: q = q[q['adm0name'] == c]
    return q.iloc[0].geometry
land = L('ne_10m_land', (20, 30, 70, 60))
holes = [Polygon(r) for g in land.geometry for p in (g.geoms if hasattr(g, 'geoms') else [g]) for r in p.interiors]
casp = [h for h in holes if h.contains(Point(51, 42))][0]
print('도형 쌍 | 가장 가까운 거리(km) | 가까운 점 A (경도, 위도) | 가까운 점 B')
for nm, a, b in (('셀렝가강 중심선 - 바이칼호', river('Selenga'), lake('Lake Baikal')),
                 ('이르쿠츠크(점) - 바이칼호', city('Irkutsk'), lake('Lake Baikal')),
                 ('울란바타르(점) - 셀렝가강 중심선', city('Ulaanbaatar'), river('Selenga')),
                 ('울란바타르(점) - 바이칼호', city('Ulaanbaatar'), lake('Lake Baikal')),
                 ('아무다리야강 중심선 - 아랄해(남)', river('Amu  Darya', 'Panj'), lake('South Aral Sea')),
                 ('시르다리야강 중심선 - 아랄해(북)', river('Syr  Darya', 'Naryn'), lake('North Aral Sea')),
                 ('아랄해(북) - 아랄해(남)', lake('North Aral Sea'), lake('South Aral Sea')),
                 ('볼가강 중심선 - 카스피해(땅 다각형의 구멍)', river('Volga'), casp),
                 ('우랄강 중심선 - 카스피해(땅 다각형의 구멍)', river('Ural'), casp),
                 ('아스트라한(점) - 카스피해(땅 다각형의 구멍)', city('Astrakhan'), casp),
                 ('이르티시강 중심선 - 발하시호', river('Irtysh', 'Ertis', 'Ertix'), lake('Lake Balkhash')),
                 ('알마티(점) - 발하시호', city('Almaty'), lake('Lake Balkhash')),
                 ('비슈케크(점) - 이식쿨호', city('Bishkek'), lake('Issyk-Kul'))):
    d, la, lb = gap(a, b)
    print('%s | %.1f | (%.2f, %.2f) | (%.2f, %.2f)' % (nm, d, la[0], la[1], lb[0], lb[1]))
