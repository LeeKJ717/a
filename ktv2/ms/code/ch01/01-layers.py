# -*- coding: utf-8 -*-
"""실습 1-1: Natural Earth 벡터 층을 geopandas 로 읽고 들여다본다.
입력: book2/geodata 의 GeoJSON 10개(제1권이 쓴 파일)
확인: 층마다 좌표계, 도형 종류, 개수, 범위, 깨진 도형 수. 한반도 상자만 읽기."""
import os, sys, time, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K
import geopandas as gpd

t_all = K.timer()
print('== 1. 층 10개 훑어보기 ==')
print('%-48s %6s %-9s %-26s %5s' % ('파일', '개수', '좌표계', '도형', '깨짐'))
for p in sorted(glob.glob(os.path.join(K.GEO, '*.geojson'))):
    t = K.timer()
    g = gpd.read_file(p)
    dt = t()
    kinds = ','.join('%s %d' % (k, v) for k, v in g.geom_type.value_counts().items())
    bad = int((~g.geometry.is_valid).sum())
    print('%-48s %6d %-9s %-26s %5d  (읽기 %.2f초)' % (os.path.basename(p), len(g), g.crs.to_string(), kinds, bad, dt))

print()
print('== 2. 한반도 상자(122.5~133.5E, 31.5~44N)만 읽기: bbox 인자 ==')
bb = (122.5, 31.5, 133.5, 44.0)
for nm in ('ne_10m_land', 'ne_10m_minor_islands', 'ne_10m_lakes', 'ne_10m_rivers_lake_centerlines', 'ne_10m_populated_places_simple', 'ne_10m_geography_regions_elevation_points'):
    t = K.timer()
    g = K.read(nm, bb)
    print('%-44s 상자 안 %5d 개  (읽기 %.2f초)' % (nm, len(g), t()))

print()
print('== 3. 속성표 들여다보기 ==')
pp = K.read('ne_10m_populated_places_simple', bb)
korea = pp[pp.sov0name.isin(['Korea, South', 'Korea, North'])].sort_values('pop_max', ascending=False)
print(korea[['name', 'sov0name', 'pop_max', 'longitude', 'latitude']].head(8).to_string(index=False))
print('geometry 열의 첫 점:', korea.geometry.iloc[0].wkt, ' (x=경도, y=위도 순서)')

print()
print('== 4. 수심 층(제1권 geodata의 200 m 층) ==')
b = K.read('ne_10m_bathymetry_K_200')
print('열:', list(b.columns), ' depth 값:', [int(v) for v in sorted(b.depth.unique())], ' 도형 %d개, 깨진 도형 %d개' % (len(b), (~b.geometry.is_valid).sum()))
print('깨진 도형의 이유(shapely.validation.explain_validity) 처음 3개:')
from shapely.validation import explain_validity
for i, geom in enumerate(b.geometry[~b.geometry.is_valid].head(3)):
    print('  ', explain_validity(geom)[:90])
print()
print('== 5. GeoJSON 은 글자 파일이다: 거주지 파일의 처음 330자 ==')
print(open(K.path_of('ne_10m_populated_places_simple'), encoding='utf-8').read(330))
print()
print('전체 실행 %.2f초' % t_all())
