# -*- coding: utf-8 -*-
"""지명표 만들기: 이 장 지도에 쓴 모든 한글 지명, 종류, Natural Earth 영문 이름, Natural Earth 기준 위치, 한글 표기 근거, 쓰인 지도.
위치는 도시는 Natural Earth 점, 지형 구역은 다각형 대표점(representative_point), 호수는 다각형 대표점, 강은 중심선의 시작 좌표 범위,
카스피해와 흑해는 이 책이 정한 라벨 점(땅 밖 물 다각형 안임을 확인한 점)이다. 결과: names-table.csv, names-table.log"""
import os, sys, importlib.util, csv
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
spec = importlib.util.spec_from_file_location('figs', os.path.join(ROOT, 'scripts', 'figs-ch00.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
G = lambda n: gpd.read_file(os.path.join(ROOT, 'geodata', n + '.geojson'))
pp = G('ne_10m_populated_places_simple'); reg = G('ne_10m_geography_regions_polys'); reg.columns = [c.lower() if c != 'geometry' else c for c in reg.columns]
lk = G('ne_10m_lakes'); rv = G('ne_10m_rivers_lake_centerlines')
used = {}
for mp, sp in F.SPECS.items():
    for grp in ('regions', 'waters', 'rivers', 'cities'):
        for ko in sp.get(grp, {}):
            used.setdefault(ko, []).append(sp['title'])
rows = []
for ko, maps in used.items():
    basis = {'A': '한국어 위키백과 항목 제목', 'B': 'Natural Earth NAME_KO 속성'}[F.NAMES[ko]]
    if ko in F.CITYKEY:
        en = F.CITYKEY[ko]; q = pp[pp['name'] == en]
        if en == 'Odessa': q = q[q['adm0name'] == 'Ukraine']
        r = q.iloc[0]; kind = '도시'; pos = '%.2f E, %.2f N (NE 점)' % (r.longitude, r.latitude)
    elif ko in F.POLYKEY:
        key = F.POLYKEY[ko]; keys = key if isinstance(key, tuple) else (key,)
        q = reg[reg['name'].str.upper().isin([k.upper() for k in keys])]
        g = unary_union(list(q.geometry)); p = g.representative_point(); en = ' + '.join(keys)
        kind = {'Range/mtn': '산맥·고원', 'Desert': '사막', 'Plateau': '고원', 'Basin': '분지', 'Lowland': '평원', 'Plain': '평원', 'Valley': '분지', 'Pen/cape': '반도'}.get(q.iloc[0]['featurecla'], q.iloc[0]['featurecla'])
        pos = '%.1f E, %.1f N (NE 다각형 대표점)' % (p.x, p.y)
    elif ko in F.LAKEKEY:
        en = ' + '.join(F.LAKEKEY[ko]); q = lk[lk['name'].isin(F.LAKEKEY[ko])]
        p = unary_union(list(q.geometry)).representative_point(); kind = '호수'; pos = '%.2f E, %.2f N (NE 다각형 대표점)' % (p.x, p.y)
    elif ko in F.RIVKEY:
        en = ' + '.join(F.RIVKEY[ko]); q = rv[rv['name'].isin(F.RIVKEY[ko])]
        b = q.total_bounds; kind = '강'; pos = '중심선 범위 %.0f~%.0f E, %.0f~%.0f N' % (b[0], b[2], b[1], b[3])
    elif ko in F.SEEDS:
        en = 'Caspian Sea' if ko == '카스피해' else 'Black Sea'; kind = '바다(호수)'
        pos = '%.1f E, %.1f N (땅 밖 물 다각형 안의 라벨 점)' % F.SEEDS[ko]
    else:
        continue
    rows.append((ko, kind, en, pos, basis, ', '.join(maps)))
order = {'도시': 0, '산맥·고원': 1, '고원': 1, '사막': 2, '분지': 3, '평원': 3, '반도': 4, '호수': 5, '바다(호수)': 5, '강': 6}
rows.sort(key=lambda r: (order.get(r[1], 9), r[0]))
with open(os.path.join(HERE, 'names-table.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['ko', 'kind', 'ne_name', 'position', 'basis', 'maps']); w.writerows(rows)
for r in rows: print(' | '.join(r))
print(len(rows), '개 지명')
