# -*- coding: utf-8 -*-
"""계산 0-4: (가) Natural Earth 호수 다각형의 면적(등적 투영 EPSG:6933), 땅 다각형의 구멍으로 그려진 카스피해와 흑해의 면적.
(나) 이 장 지도 틀의 가로 세로 길이(km, 투영 좌표). 틀의 크기는 scripts/figs-ch00.py 의 SPECS 와 같은 식으로 구한다."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
import mapkit as K
import geopandas as gpd
from shapely.geometry import box, Point
from shapely.ops import unary_union
from pyproj import CRS
spec = importlib.util.spec_from_file_location('figs', os.path.join(ROOT, 'scripts', 'figs-ch00.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)

lk = gpd.read_file(os.path.join(ROOT, 'geodata', 'ne_10m_lakes.geojson'))
lk['a'] = lk.geometry.to_crs(6933).area / 1e6
print('(가) Natural Earth 호수 다각형 면적(km², EPSG:6933)')
for en, ko in (('Lake Baikal', '바이칼호'), ('Lake Balkhash', '발하시호'), ('Issyk-Kul', '이식쿨호'), ('Uvs Nuur', '우브스호'), ('Khövsgöl Nuur', '후브스굴호'), ('North Aral Sea', '아랄해(북)'), ('South Aral Sea', '아랄해(남)')):
    r = lk[lk['name'] == en]
    print('%s | %s | %d개 다각형 | %.0f' % (ko, en, len(r), r['a'].sum()))
# 땅 다각형의 구멍
land = K.read('ne_10m_land', (20, 30, 70, 60))
land, _ = K.fix(land)
holes = []
for g in land.geometry:
    for p in (g.geoms if hasattr(g, 'geoms') else [g]):
        for ring in p.interiors:
            holes.append(shapely.geometry.Polygon(ring)) if False else holes.append(__import__('shapely').geometry.Polygon(ring))
for ko, seed in (('카스피해', (51.0, 42.0)), ('흑해', (34.0, 43.0))):
    h = [p for p in holes if p.contains(Point(seed))]
    if h:
        a = gpd.GeoSeries([h[0]], crs=4326).to_crs(6933).area.iloc[0] / 1e6
        print('%s | 땅 다각형의 구멍 | %.0f km²' % (ko, a))
    else:
        print('%s | 땅 다각형의 구멍이 아니다. 지중해와 이어진 물로 그려져 있어 이 책은 흑해만의 면적을 재지 않았다' % ko)
print()
print('(나) 지도 틀의 크기(km)')
for nm, sp in F.SPECS.items():
    crs = CRS.from_user_input(sp['proj'])
    if sp.get('view'):
        X0, Y0, X1, Y1 = [v * 1000.0 for v in sp['view']]
    else:
        X0, Y0, X1, Y1 = K.proj_bounds(sp['bbox'], crs)
    print('%s | %.0f x %.0f km | 격자 %d도 | 축척 막대 %d km' % (sp['title'], (X1 - X0) / 1000, (Y1 - Y0) / 1000, sp['grid'], sp['scale_km']))
