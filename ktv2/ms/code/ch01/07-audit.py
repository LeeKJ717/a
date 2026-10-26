# -*- coding: utf-8 -*-
"""실습 1-7: 제1권의 지도 도록과 11장 계산을 되풀이해 값이 맞는지 점검한다. 제1권 파일을 읽기만 하고 고치지 않는다.
(가) 제1권 11.5.6절 거리 82.4 km / 82.43 km / 2.46 km
(나) 지도 도록의 "도시 좌표 26곳이 Natural Earth 거주지 자료와 0.12도 이내로 일치" (제1권 scripts/figs_maps.py 의 좌표표 C)
(다) 지도 도록 「산지와 높이」 표의 봉우리 14곳의 좌표·높이 (ms/ch00-maps-v1.md)
(라) 제1권 노백산 지도(map-laobai)가 범례에 "강"을 넣었는데 그 범위에 강이 있는가"""
import os, sys, ast, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K
import numpy as np
import geopandas as gpd
from shapely.geometry import box

V1 = '/home/claude/book'

print('== (가) 11.5.6절 거리 ==')
lb = (K.dms(128, 3), K.dms(44, 6)); dh = (K.dms(128, 12), K.dms(43, 22))
d = K.haversine(*lb, *dh)
txt = open(V1 + '/ms/ch11-v1.md', encoding='utf-8').read()
print('제1권 본문에서 찾은 문장:', re.search(r'두 점의 거리는 [\d.]+ km', txt).group(0), '/', re.search(r'대원 거리 계산은 [\d.]+ km', txt).group(0), '/', re.search(r'기상대 좌표 사이는 [\d.]+ km', txt).group(0))
print('이번 계산: haversine %.2f km, 도시-기상대 %.2f km' % (d, K.geodesic_km(128.22, 43.35, *dh)))

print()
print('== (나) 도시 좌표 대조 ==')
src = open(V1 + '/scripts/figs_maps.py', encoding='utf-8').read()
tree = ast.parse(src)
C = None
for n in tree.body:
    if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'C':
        C = {k.arg: ast.literal_eval(k.value) for k in n.value.keywords}
print('제1권 좌표표 C 의 도시 수:', len(C))
EXP = {'서울': 'Seoul', '평양': 'Pyongyang', '부산': 'Busan', '북경': 'Beijing', '상해': 'Shanghai', '서안': r"Xi.?an", '낙양': 'Luoyang', '성도': 'Chengdu',
       '심양': 'Shenyeng|Shenyang', '대련': 'Dalian', '합이빈': 'Harbin', '남경': 'Nanjing', '무한': 'Wuhan', '도쿄': 'Tokyo', '오사카': r'.saka', '후쿠오카': 'Fukuoka',
       '삿포로': 'Sapporo', '장춘': 'Changchun', '적봉': 'Chifeng', '조양': 'Chaoyang', '난주': 'Lanzhou', '은천': 'Yinchuan', '태원': 'Taiyuan', '정주': 'Zhengzhou',
       '천진': 'Tianjin', '항주': 'Hangzhou', '울란바토르': 'Ulaanbaatar'}
pp = K.read('ne_10m_populated_places_simple')
pts = np.c_[pp.longitude.values, pp.latitude.values]
print('%-8s %-18s %-9s %-9s %-9s %-9s %7s %7s %8s' % ('도시', 'NE 이름', '제1권경도', '제1권위도', 'NE경도', 'NE위도', 'Δ경도', 'Δ위도', '거리km'))
dev, rows = [], []
for ko, (lo, la) in C.items():
    cand = pp[pp['name'].str.contains(EXP[ko], regex=True) | pp['nameascii'].str.contains(EXP[ko], regex=True)]
    cand = cand[(abs(cand.longitude - lo) < 3) & (abs(cand.latitude - la) < 3)]
    if len(cand) == 0:
        print('%-8s NE 에서 이름이 맞는 도시를 찾지 못함 (%s)' % (ko, EXP[ko])); continue
    dd = np.hypot(cand.longitude - lo, cand.latitude - la)
    r = cand.loc[dd.idxmin()]
    dl, dp = r.longitude - lo, r.latitude - la
    km = K.geodesic_km(lo, la, r.longitude, r.latitude)
    rows.append((ko, r['name'], lo, la, r.longitude, r.latitude, dl, dp, km))
    print('%-8s %-18s %9.3f %9.3f %9.3f %9.3f %+7.3f %+7.3f %8.1f' % rows[-1])
mx = max(max(abs(r[6]), abs(r[7])) for r in rows)
over = [(r[0], max(abs(r[6]), abs(r[7]))) for r in rows if max(abs(r[6]), abs(r[7])) > 0.12]
print('찾은 도시 %d곳. 경도차·위도차 가운데 가장 큰 값 %.3f도. 0.12도를 넘는 곳: %s' % (len(rows), mx, over if over else '없음'))
print('제1권 도록 서술: "26곳 ... 0.12도 이내". 좌표표 C 의 도시 수는 %d, 이름이 맞아 짝지은 수는 %d' % (len(C), len(rows)))
big = sorted(rows, key=lambda r: -r[8])[:3]
print('거리가 가장 큰 3곳(km):', ', '.join('%s %.1f' % (r[0], r[8]) for r in big))

print()
print('== (다) 봉우리 14곳 ==')
ep = K.read('ne_10m_geography_regions_elevation_points')
tab = []
for ln in open(V1 + '/ms/ch00-maps-v1.md', encoding='utf-8'):
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c) == 6 and re.fullmatch(r'[\d,]+', c[5]):
        tab.append((c[0], float(c[3]), float(c[4]), int(c[5].replace(',', ''))))
print('도록 표에서 읽은 봉우리 수:', len(tab))
print('%-10s %8s %9s %7s | %-14s %8s %9s %7s %7s' % ('한글', '표 위도', '표 경도', '표 높이', 'NE 이름', 'NE 위도', 'NE 경도', 'NE 높이', '차이'))
ok = 0
for ko, la, lo, h in tab:
    dd = np.hypot(ep.long_x - lo, ep.lat_y - la)
    r = ep.loc[dd.idxmin()]
    same = abs(int(r.elevation) - h) == 0
    ok += same
    print('%-10s %8.2f %9.2f %7d | %-14s %8.2f %9.2f %7d %7s  (두 좌표 간격 %.1f km)' % (ko, la, lo, h, r['name'], r.lat_y, r.long_x, int(r.elevation), '%+d' % (int(r.elevation) - h), K.geodesic_km(lo, la, r.long_x, r.lat_y)))
print('높이가 NE 표고점과 정확히 같은 봉우리 %d / %d' % (ok, len(tab)))

print()
print('== (라) 제1권 노백산 지도(map-laobai) 범위(127.2~129.3E, 42.9~44.5N)에 강이 있는가 ==')
bb = (127.2, 42.9, 129.3, 44.5)
rv = K.read('ne_10m_rivers_lake_centerlines', bb)
want = {'Songhua', 'Di’er Songhua', 'Tumen'}
print('범위 안의 하천 선 %d개, 이름: %s' % (len(rv), sorted(set(rv['name'].dropna())) or '없음'))
sel = rv[rv['name'].isin(want)]
print('제1권이 그리려 한 이름(%s)에 해당하는 선 %d개' % (', '.join(sorted(want)), len(sel)))
cl = gpd.clip(sel, box(*bb))
km = sum(K.GEOD.geometry_length(g) for g in cl.geometry) / 1000
print('그 선 가운데 이 범위 안에 든 길이 %.2f km (선 전체 범위: %s)' % (km, [round(float(v), 2) for v in sel.total_bounds]))
lk = K.read('ne_10m_lakes', bb)
print('범위 안의 호수 %d개: %s' % (len(lk), sorted(set(lk['name'].dropna())) or '없음'))
svg = open(V1 + '/fig/map-laobai-v1-color.svg', encoding='utf-8').read()
n_riv = len(re.findall(r'stroke="#3A7CA5"', svg))
print('제1권 SVG 에서 하천 색(#3A7CA5) 선의 수 %d (범례 견본 1개 포함); 범례 글자 "강(Natural Earth)" 있음: %s' % (n_riv, '강(Natural Earth)' in svg))
