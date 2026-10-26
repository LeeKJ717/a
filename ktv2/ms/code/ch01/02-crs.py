# -*- coding: utf-8 -*-
"""실습 1-2: 좌표계. 경위도(WGS84)와 투영 좌표계를 pyproj 로 오가며 길이와 면적이 어떻게 달라지는지 잰다."""
import os, sys, math, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K
import numpy as np
from pyproj import CRS, Transformer
from shapely.ops import unary_union

print('== 1. 좌표계 정보 ==')
for code in (4326, 32652, 5179, 3857, 6933):
    c = CRS.from_epsg(code)
    ax = ', '.join('%s(%s)' % (a.abbrev, a.direction) for a in c.axis_info)
    au = c.area_of_use
    print('EPSG:%d  %s  | 종류 %s | 축 %s | 단위 %s | 쓰임 범위 %.1f~%.1fE, %.1f~%.1fN' % (
        code, c.name, 'geographic' if c.is_geographic else 'projected', ax, c.axis_info[0].unit_name, au.west, au.east, au.south, au.north))

print()
print('== 2. 축 순서 함정: 같은 (126.9978, 37.5683)를 두 방식으로 변환 ==')
lon, lat = 126.997785, 37.568295        # 서울(Natural Earth 거주지 자료)
t_default = Transformer.from_crs(4326, 32652)                  # always_xy 없음: EPSG:4326 의 공식 축 순서(위도, 경도)
t_xy = Transformer.from_crs(4326, 32652, always_xy=True)       # 경도, 위도 순서로 고정
print('always_xy=True  (lon, lat) 넣음 ->', tuple(round(v, 1) for v in t_xy.transform(lon, lat)))
print('기본값          (lat, lon) 넣음 ->', tuple(round(v, 1) for v in t_default.transform(lat, lon)))
print('기본값          (lon, lat) 넣음 ->', tuple(round(v, 1) for v in t_default.transform(lon, lat)), ' <- 순서를 바꿔 넣으면 값이 터무니없다(또는 inf)')

print()
print('== 3. 서울을 여러 좌표계로, 왕복 오차 ==')
for code in (32652, 5179, 3857, 6933):
    tr = Transformer.from_crs(4326, code, always_xy=True)
    inv = Transformer.from_crs(code, 4326, always_xy=True)
    x, y = tr.transform(lon, lat)
    lo2, la2 = inv.transform(x, y)
    err = K.geodesic_km(lon, lat, lo2, la2) * 1000
    print('EPSG:%-5d x=%14.2f y=%14.2f  왕복 오차 %.2e m' % (code, x, y, err))

print()
print('== 4. 경도 1도, 위도 1도의 실제 길이(WGS84 타원체, 측지선) ==')
print('%5s %14s %14s %16s' % ('위도', '경도 1° (km)', '위도 1° (km)', '111.32·cos(위도)'))
for la in (0, 35, 44, 60):
    e = K.geodesic_km(127, la, 128, la)
    n = K.geodesic_km(127, la - 0.5, 127, la + 0.5)
    print('%4d° %14.3f %14.3f %16.3f' % (la, e, n, 111.32 * math.cos(math.radians(la))))

print()
print('== 5. 같은 동서 1도(127E→128E)를 투영 좌표계마다 재면 ==')
print('투영 길이 / 측지선 길이  (1이면 길이가 보존됨)')
print('%5s %12s %10s %10s %10s %10s' % ('위도', '측지선 km', 'UTM52N', 'EPSG5179', 'Web Merc.', '111.32km/도'))
for la in (0, 35, 44, 60):
    g = K.geodesic_km(127, la, 128, la)
    r = [K.projected_km(127, la, 128, la, c) / g for c in (32652, 5179, 3857)]
    deg = 111.32 / g
    print('%4d° %12.3f %10.4f %10.4f %10.4f %10.4f' % (la, g, r[0], r[1], r[2], deg))
print('(마지막 열 = 경도 1°를 위도와 상관없이 111.32 km 로 친 길이의 비. 웹 메르카토르의 동서 길이는 이 값과 같다.)')

print()
print('== 6. UTM 52N 에서 중앙 자오선(129E)을 벗어날수록 늘어나는 길이 (위도 37N, 동서 0.1도 구간) ==')
for lo in (126.0, 127.5, 129.0, 131.0, 132.0):
    g = K.geodesic_km(lo, 37, lo + 0.1, 37)
    p = K.projected_km(lo, 37, lo + 0.1, 37, 32652)
    print('경도 %5.1fE  측지선 %.4f km  UTM52N %.4f km  비 %.5f' % (lo, g, p, p / g))

print()
print('== 7. 1°×1° 칸(127~128E)의 면적 ==')
for la in (0, 35, 60):
    ring = [(127, la), (128, la), (128, la + 1), (127, la + 1)]
    lons, lats = zip(*ring)
    area_geod = abs(K.GEOD.polygon_area_perimeter(lons, lats)[0]) / 1e6
    out = []
    for code in (5179, 3857, 6933):
        tr = Transformer.from_crs(4326, code, always_xy=True)
        xs, ys = tr.transform(lons, lats)
        a = 0.5 * abs(sum(xs[i] * ys[(i + 1) % 4] - xs[(i + 1) % 4] * ys[i] for i in range(4))) / 1e6
        out.append(a)
    print('위도 %2d~%2dN  측지선 면적 %9.1f km²  EPSG5179 %9.1f  Web Merc. %9.1f (x%.2f)  EPSG6933 %9.1f' % (la, la + 1, area_geod, out[0], out[1], out[1] / area_geod, out[2]))

print()
print('== 8. 제주도 면적을 네 가지로: 측지선 / 5179 / 3857 / 6933 ==')
land = K.read('ne_10m_land', (126.0, 33.0, 127.0, 34.0))
parts = []
for g in land.geometry:
    parts.extend(list(g.geoms) if g.geom_type == 'MultiPolygon' else [g])
from shapely.geometry import Point
pt = Point(126.55, 33.40)
jeju = [p for p in parts if p.contains(pt)]
print('제주 한가운데(126.55E, 33.40N)를 품은 땅 도형 수:', len(jeju))
jj = jeju[0]
print('꼭짓점 수', len(jj.exterior.coords), ' 범위', [round(v, 3) for v in jj.bounds])
a_geod = abs(K.GEOD.geometry_area_perimeter(jj)[0]) / 1e6
print('측지선(Geod.geometry_area_perimeter) %.1f km²' % a_geod)
import geopandas as gpd
gj = gpd.GeoDataFrame(geometry=[jj], crs=4326)
for code in (5179, 3857, 6933):
    a = gj.to_crs(code).area.iloc[0] / 1e6
    print('EPSG:%d 에서 shapely .area %.1f km²  (측지선 대비 %+.3f%%)' % (code, a, 100 * (a / a_geod - 1)))
print('※ 공식 통계 면적과의 대조는 하지 않았다(근거 확인 필요). 위 값은 Natural Earth 1:10m 해안선 도형의 면적이다.')

print()
print('== 9. 함정: 경위도 좌표계의 .area 는 "제곱도"이다 ==')
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    v = gj.area.iloc[0]
    print('gdf.area (EPSG:4326) = %.6f   ← 단위는 도²이고 km²가 아니다' % v)
    for x in w:
        print('경고:', str(x.message)[:140])

print()
print('== 10. 해안선 해상도: 같은 제주도를 1:10m 과 1:50m 자료로 재면 ==')
res = {}
for nm in ('ne_10m_land', 'ne_50m_land'):
    g = K.read(nm, (126.0, 33.0, 127.0, 34.0))
    prt = []
    for geom in g.geometry:
        prt.extend(list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom])
    j = [p for p in prt if p.contains(Point(126.55, 33.40))][0]
    a, per = K.GEOD.geometry_area_perimeter(j)
    res[nm] = (abs(a) / 1e6, per / 1000)
    print('%-12s 꼭짓점 %4d 개  면적 %.1f km²  둘레 %.1f km' % (nm, len(j.exterior.coords), abs(a) / 1e6, per / 1000))
print('1:50m 은 1:10m 보다 면적이 %.1f%%, 둘레가 %.1f%% 작다(꼭짓점이 적어 굴곡이 깎임).' % (100 * (1 - res['ne_50m_land'][0] / res['ne_10m_land'][0]), 100 * (1 - res['ne_50m_land'][1] / res['ne_10m_land'][1])))
