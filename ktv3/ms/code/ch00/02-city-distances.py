# -*- coding: utf-8 -*-
"""계산 0-2: 도시 쌍의 거리를 네 가지 방법으로 잰다.
 (가) WGS84 측지선 (나) 구면 대원 거리(반지름 6371.0088 km) (다) 경위도를 그냥 평면 좌표처럼 놓고 '1도=111 km' 로 잰 값
 (라) 이 장 지도의 투영(원뿔 정적 투영) 위에서 잰 직선 거리. 도시 좌표는 Natural Earth populated_places_simple."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
import geopandas as gpd
from pyproj import Geod, Transformer
G = Geod(ellps='WGS84'); R = 6371.0088
pp = gpd.read_file(os.path.join(ROOT, 'geodata', 'ne_10m_populated_places_simple.geojson'))
CTRY = {'Odessa': 'Ukraine'}   # 같은 이름의 도시가 여럿이면 나라로 고른다(Odessa 는 미국 텍사스에도 있다)
def ll(n):
    q = pp[pp['name'] == n]
    if n in CTRY:
        q = q[q['adm0name'] == CTRY[n]]
    assert len(q) == 1, (n, len(q))
    r = q.iloc[0]; return float(r.longitude), float(r.latitude)
AEA = '+proj=aea +lat_1=%g +lat_2=%g +lat_0=%g +lon_0=%g +datum=WGS84 +units=m +no_defs'
MAPS = {'유라시아 개관': AEA % (38, 68, 52, 82), '몽골 고원': AEA % (42, 55, 48, 105), '알타이와 시베리아': AEA % (50, 66, 58, 94), '중앙아시아': AEA % (37, 49, 43, 68), '카스피해와 흑해': AEA % (40, 54, 47, 44)}
PAIRS = [('울란바타르', 'Ulaanbaatar', '이르쿠츠크', 'Irkutsk', '몽골 고원'),
         ('노보시비르스크', 'Novosibirsk', '이르쿠츠크', 'Irkutsk', '알타이와 시베리아'),
         ('타슈켄트', 'Tashkent', '카슈가르', 'Kashgar', '중앙아시아'),
         ('아스트라한', 'Astrakhan', '사마르칸트', 'Samarkand', '중앙아시아'),
         ('울란바타르', 'Ulaanbaatar', '알마티', 'Almaty', '유라시아 개관'),
         ('키이우', 'Kyiv', '울란바타르', 'Ulaanbaatar', '유라시아 개관'),
         ('트빌리시', 'Tbilisi', '오데사', 'Odessa', '카스피해와 흑해')]
def hav(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0] - a[0])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))
def naive(a, b):
    # 위도 1도 111 km, 경도 1도는 두 점의 평균 위도에서 111 km x cos(평균 위도)
    la = (a[1] + b[1]) / 2
    return math.hypot((b[0] - a[0]) * 111.0 * math.cos(math.radians(la)), (b[1] - a[1]) * 111.0)
def plane_deg(a, b):
    # 경위도를 평면 좌표로 보고 1도=111 km 로 곱한 값(경도에 cos 를 곱하지 않은 값)
    return math.hypot((b[0] - a[0]) * 111.0, (b[1] - a[1]) * 111.0)
print('도시 쌍 | 측지선 km | 구면 km | 평균위도 cos 근사 km | cos 없이 1도=111 km km | 지도 투영 위 직선 km | 지도')
rows = []
for k1, e1, k2, e2, mp in PAIRS:
    a, b = ll(e1), ll(e2)
    _, _, d = G.inv(a[0], a[1], b[0], b[1]); d /= 1000
    t = Transformer.from_crs(4326, MAPS[mp], always_xy=True)
    x1, y1 = t.transform(*a); x2, y2 = t.transform(*b)
    pr = math.hypot(x2 - x1, y2 - y1) / 1000
    h, n, p = hav(a, b), naive(a, b), plane_deg(a, b)
    print('%s-%s (%.2f E %.2f N; %.2f E %.2f N) | %.1f | %.1f (%+.2f%%) | %.1f (%+.1f%%) | %.1f (%+.1f%%) | %.1f (%+.2f%%) | %s' % (k1, k2, a[0], a[1], b[0], b[1], d, h, (h / d - 1) * 100, n, (n / d - 1) * 100, p, (p / d - 1) * 100, pr, (pr / d - 1) * 100, mp))
