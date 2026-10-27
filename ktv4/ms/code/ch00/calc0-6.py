# -*- coding: utf-8 -*-
"""계산 0-6: 장 표지 도안(scripts/chapart-v1.py 의 CH)이 덮는 경위도 범위와 면적. 도안은 중심 (경도, 위도), 반높이(도)로 정해지고
가로 반폭 = 반높이 x (129.6/64) / cos(중심 위도) 이다(도안의 가로 세로 비 129.6 mm : 64 mm). 면적은 위도선과 경도선으로 둘러싼 구면 사각형의 면적 R^2 x 경도 폭(라디안) x (sin 위도 상단 - sin 위도 하단), R = 6371.0088 km 이다. 경도 폭이 360도를 넘으면 360도로 자른다."""
import os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
src = open(os.path.join(ROOT, 'scripts', 'chapart-v1.py'), encoding='utf-8').read()
a = src.index('CH = {'); b = src.index('\n}\n', a) + 3
ns = {}; exec(src[a:b], ns); CH = ns['CH']
import math
print('장 | 중심(경도, 위도) | 경도 범위 | 위도 범위 | 면적(백만 km2) | 지구 표면(510.07백만 km2)에서 차지하는 %')
for ci, (lon0, lat0, hd, _, ov) in sorted(CH.items()):
    if ci in (0, 1): continue
    k = math.cos(math.radians(lat0)); hw = hd * (129.6 / 64) / k
    lo0, lo1 = lon0 - hw, lon0 + hw; la0, la1 = max(lat0 - hd, -90), min(lat0 + hd, 90)
    dl = math.radians(min(hw, 180.0) * 2); ar = 6371.0088 ** 2 * dl * (math.sin(math.radians(la1)) - math.sin(math.radians(la0))) / 1e6
    print('%d | (%g, %g) | %.1f ~ %.1f | %.1f ~ %.1f | %.1f | %.1f' % (ci, lon0, lat0, lo0, lo1, la0, la1, ar, ar / 510.07 * 100))
print('주의: 도안은 가로를 cos(중심 위도)로 줄여 그린 평면 도안이므로 높은 위도의 창은 경도로 매우 넓다. 장 10 은 위도 90도에서 잘린다.')
