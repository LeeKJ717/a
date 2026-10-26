# -*- coding: utf-8 -*-
"""실습 1-5: 해저 지형(수심) 자료로 수심 등고선(등심선)을 만든다.
Natural Earth 의 수심 층 6개(200, 1000, 2000, 3000, 4000, 5000 m)는 "그 깊이보다 깊은 바다"를 덮는 다각형이다.
이 층의 경계선이 곧 등심선이다. 여기서는 (1) 층의 뜻을 점으로 확인하고 (2) 깨진 도형을 고치고 (3) 등심선을 뽑고
(4) 한반도 둘레 바다에서 깊이별 면적을 잰다. 모든 값은 이 파일을 실행해 나온 것이다."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, box
from shapely.ops import unary_union

BB = (120.0, 30.0, 134.0, 44.0)          # 황해·동해·남해를 모두 품는 상자
tt = K.timer()

print('== 1. 수심 층 6개: 개수, 깨진 도형, 고친 뒤 ==')
raw = {}
for d, nm in K.BATHY:
    g = K.read(nm)
    gf, nbad = K.fix(g)
    raw[d] = (len(g), nbad, int((~gf.geometry.is_valid).sum()))
    print('%5d m 층  도형 %5d 개, 깨진 것 %3d 개, make_valid 뒤 깨진 것 %d 개' % (d, *raw[d]))

print()
print('== 2. 상자(%.0f~%.0fE, %.0f~%.0fN) 안의 층 읽고 자르기 ==' % (BB[0], BB[2], BB[1], BB[3]))
t = K.timer()
lay, nfix = K.bathy_layers(BB, pad=0.0)
print('걸린 시간 %.2f초, 이 상자에서 고친 도형 %d 개' % (t(), nfix))
for d, g in lay.items():
    print('%5d m 층: 조각 %d 개, 꼭짓점 합 %s' % (d, len(g), format(int(sum(len(x.exterior.coords) + sum(len(r.coords) for r in x.interiors) for geom in g.geometry for x in (geom.geoms if hasattr(geom, 'geoms') else [geom]) if x.geom_type == 'Polygon')), ',') if len(g) else 0))

print()
print('== 3. 점이 어느 깊이 구간에 드는가: 층 안에 있는지(contains) ==')
def depth_class(lo, la):
    p = Point(lo, la)
    deepest = 0
    for d, g in lay.items():
        if len(g) and g.contains(p).any():
            deepest = d
    return deepest
def label(d):
    return '200 m보다 얕음(층 밖)' if d == 0 else '%d m 이상' % d
spots = [('황해 한가운데', 123.5, 35.5), ('황해 서해안 가까이(인천 앞)', 125.5, 37.0), ('제주 남쪽', 126.5, 32.0),
         ('대한해협', 129.5, 34.2), ('동해 울릉도 북쪽', 130.9, 38.2), ('동해 북부', 132.5, 41.0), ('동해 한가운데 아래쪽', 133.0, 39.0)]
for nm, lo, la in spots:
    print('%-24s (%.1fE, %.1fN) → %s' % (nm, lo, la, label(depth_class(lo, la))))
print()
print('층이 포개져 있는가: 깊은 층 가운데 얕은 층 밖에 있는 부분의 면적(km², 등적 투영). 0 이면 완전히 포개진 것')
EA0 = 6933
def A0(geom):
    return gpd.GeoSeries([geom], crs=4326).to_crs(EA0).area.iloc[0] / 1e6
ds = [d for d in lay if len(lay[d])]
for a, b in zip(ds[:-1], ds[1:]):
    ua, ub = unary_union(list(lay[a].geometry)), unary_union(list(lay[b].geometry))
    print('  %4d m 층 중 %4d m 층 밖에 있는 부분 = %.3f km²   (%d m 층 면적 %s km²)' % (b, a, A0(ub.difference(ua)), b, format(round(A0(ub)), ',')))
print('이 방법은 "층 안인가"만 안다. 실제 수심 값은 모르고, 같은 층 안에서는 구간 안의 어디든 같은 답이다.')

print()
print('== 4. 등심선 뽑기: 다각형의 경계(boundary) ==')
import shapely
core = box(*BB).buffer(-1e-6)        # 상자를 아주 조금 줄인 것: 자르면서 생긴 상자 가장자리 선을 걷어내려고
iso = {}
for d, g in lay.items():
    if len(g) == 0:
        continue
    u = unary_union(list(g.geometry))
    allb = u.boundary
    cut = allb.intersection(core)
    parts = [p for p in shapely.get_parts(cut) if p.geom_type == 'LineString' and not p.is_empty]
    iso[d] = shapely.MultiLineString(parts)
    km_all = sum(K.GEOD.geometry_length(p) for p in shapely.get_parts(allb) if p.geom_type == 'LineString') / 1000
    km = sum(K.GEOD.geometry_length(p) for p in parts) / 1000
    print('%5d m 등심선: 선 %2d 개, 총 길이 %s km (상자 가장자리 선까지 넣으면 %s km)' % (d, len(parts), format(round(km), ','), format(round(km_all), ',')))

print()
print('== 5. 깊이별 면적(등적 투영 EPSG:6933 에서 shapely .area) ==')
a_box, a_land, a_sea, bands = K.area_by_depth(BB, lay)
print('상자 전체 %s km², 땅(상자 안) %s km², 바다 %s km²' % (format(round(a_box), ','), format(round(a_land), ','), format(round(a_sea), ',')))
print('%-20s %12s %8s' % ('깊이 구간', '면적(km²)', '바다 비율'))
for nm, ar, fr in bands:
    print('%-20s %12s %7.1f%%' % (nm, format(round(ar), ','), 100 * fr))
print('구간 면적의 합 %s km² (바다 면적 %s km²)' % (format(round(sum(b[1] for b in bands)), ','), format(round(a_sea), ',')))
print('※ 땅-바다 경계는 Natural Earth 해안선이다. 등심선이 해안선과 만나는 곳의 처리와 얕은 바다의 세부는 이 자료로 알 수 없다.')

print()
print('== 6. 등심선이 해안선을 넘는가: 200 m 층과 땅의 겹침 ==')
landu = unary_union(list(gpd.clip(K.read('ne_10m_land', BB), box(*BB)).geometry) + list(gpd.clip(K.read('ne_10m_minor_islands', BB), box(*BB)).geometry))
over = unary_union(list(lay[200].geometry)).intersection(landu)
print('200 m 층과 땅이 겹치는 면적 %.1f km²' % A0(over) if not over.is_empty else '200 m 층과 땅이 겹치지 않음')
print()
print('전체 실행 %.2f초' % tt())
