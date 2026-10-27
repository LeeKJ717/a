# -*- coding: utf-8 -*-
"""계산 15-2: "같은 때"의 정의를 바꾸면 답이 어떻게 바뀌는가. 입력은 windows15.py 의 창(8장 계산 8-4의 입력)이다.
(a) 창 부분집합마다 공통 구간. (b) 한 해 t 를 덮는 창의 수. (c) 점으로 정의할 때(메갈라야절 4200, Railsback 중심 4070, 서아시아 점추정 평균 4185)
(d) 창 양쪽을 연대 오차 d 만큼 넓힐 때 일곱 창이 모두 겹치는 최소 d. (e) Weiss 의 "200~300년" 두 판."""
import itertools, json
import numpy as np
from windows15 import *
res = {}
print('=== 계산 15-2 (a) 일곱 창의 모든 부분집합(크기 2 이상 120개)의 공통 구간 ===')
print('크기 | 부분집합 수 | 공통 구간이 있는 수 | 공통 구간 길이(있는 것) 최소 / 중앙 / 최대 (년)')
rows = []
for k in range(2, 8):
    L = []; n = 0
    for c in itertools.combinations(ALL7, k):
        n += 1; L.append(max(0.0, inter(list(c))[2]))
    pos = [x for x in L if x > 0]
    rows.append((k, n, len(pos), (min(pos), float(np.median(pos)), max(pos)) if pos else None))
    print('%3d  | %4d | %4d | %s' % (k, n, len(pos), ('%.0f / %.0f / %.0f' % (min(pos), np.median(pos), max(pos))) if pos else '없음'))
tot = sum(r[1] for r in rows); totpos = sum(r[2] for r in rows)
print('전체 %d 개 부분집합 가운데 공통 구간이 있는 것은 %d 개(%.1f%%)' % (tot, totpos, 100 * totpos / tot))
res['subsets'] = rows
# 유라시아 공통을 포함하는 부분집합
EU = '제3권 6장 유라시아 열 기록 공통'
withEU = [c for k in range(2, 8) for c in itertools.combinations(ALL7, k) if EU in c]
posEU = [c for c in withEU if inter(list(c))[2] > 0]
print('유라시아 공통(55년)을 포함한 부분집합 %d 개 가운데 공통 구간이 있는 것은 %d 개. 없는 쪽은 Booth 또는 deMenocal(젊은 끝 4100)을 함께 넣은 경우뿐이다: %s' % (
    len(withEU), len(posEU), 'True' if all(('Booth 등 북미 중부' in c or 'deMenocal 등 ODP 658C 먼지 감소' in c) for c in withEU if inter(list(c))[2] <= 0) else 'False'))
print()
print('=== 계산 15-2 (b) 한 해 t 를 덮는 창의 수(일곱 창 중) ===')
ts = np.arange(3400, 4401, 10)
cov = np.array([sum(1 for n in ALL7 if W[n][0] <= t <= W[n][1]) for t in ts])
best = ts[cov == cov.max()]
print('가장 많이 덮는 해: %d 개(일곱 중) 덮는 해는 %d~%d (10년 간격 표본)' % (cov.max(), best.min(), best.max()))
for t in (4300, 4250, 4200, 4185, 4150, 4100, 4070, 4025, 4000, 3970, 3930, 3900, 3800, 3550):
    names = [SHORT[n] for n in ALL7 if W[n][0] <= t <= W[n][1]]
    print('  t=%d: %d 개 (%s)' % (t, len(names), ', '.join(names) if names else '없음'))
res['cov'] = dict(ts=ts.tolist(), cov=cov.tolist())
print()
print('=== 계산 15-2 (c) 점으로 정의할 때: 어느 점이 창을 몇 개 덮는가 ===')
pts = [('메갈라야절 시작 4250 b2k = 4200 BP(Walker 등 2018, 8장)', 4200), ('서아시아 점추정 평균 4185 ± 45(제3권 6장, 8장 서문)', 4185), ('Railsback 등 창 중심 4070(8장)', 4070)]
for nm, t in pts:
    inn = [SHORT[n] for n in GLOBAL5 if W[n][0] <= t <= W[n][1]]
    out = [SHORT[n] for n in GLOBAL5 if not (W[n][0] <= t <= W[n][1])]
    gaps = {SHORT[n]: (t - W[n][1] if t > W[n][1] else (W[n][0] - t if t < W[n][0] else 0)) for n in GLOBAL5}
    print('  %s: 전지구 다섯 창 중 %d 개가 덮음. 덮지 못하는 창의 거리: %s' % (nm, len(inn), ', '.join('%s %d년' % (k, v) for k, v in gaps.items() if v > 0) or '없음'))
print('  4185 ± 45 의 구간 4140~4230 은 Railsback 창(4150~3930)과 %d 년 겹치고 Booth 창(4300~4100)과 %d 년 겹친다' % (4150 - 4140, min(4230, 4300) - max(4140, 4100)))
print()
print('=== 계산 15-2 (d) 창의 양쪽을 연대 오차 d 만큼 넓힐 때 공통 구간 ===')
need = None
for d in (0, 10, 25, 37.5, 40, 50, 75, 100):
    a5 = inter(GLOBAL5, d)[2]; a7 = inter(ALL7, d)[2]
    print('  d = %5.1f 년: 다섯 창 공통 %5.0f 년, 일곱 창 공통 %5.0f 년' % (d, a5, a7))
d0 = 0.0
while inter(ALL7, d0)[2] < 0: d0 += 0.5
print('  일곱 창이 처음 겹치는 최소 d = %.1f 년(공통 길이 %.0f). 식으로는 (4100 - 4025) / 2 = %.1f' % (d0, inter(ALL7, d0)[2], (4100 - 4025) / 2))
res['dneed'] = d0
print()
print('=== 계산 15-2 (e) Weiss 의 "200~300년" 두 판(시작 4200 고정, 이 책이 서술에서 읽은 것) ===')
for nm, end in (('4200~4000(200년)', 4000), ('4200~3900(300년, 8장 표)', 3900)):
    W2 = dict(W); W2['Weiss 개관'] = (end, 4200)
    lo = max(W2[n][0] for n in GLOBAL5); hi = min(W2[n][1] for n in GLOBAL5)
    print('  %-26s 다섯 창 공통 %d~%d, %d 년' % (nm, hi, lo, hi - lo))
print('  Weiss 의 창 길이를 200 에서 300 으로 바꾸어도 다섯 창 공통은 같다. 공통 구간을 정하는 것은 Booth 의 젊은 끝(4100)과 Railsback 의 오래된 끝(4150)이다.')
print('  그 두 끝을 이 책이 가정으로 옮겨 보면(Railsback 의 오래된 끝을 4150 에서 4200 으로, 또는 Booth 의 젊은 끝을 4100 에서 4000 으로):')
for nm, key, val in (('Railsback 오래된 끝 4200 으로', 'Railsback 등 종합', (3930, 4200)), ('Booth 젊은 끝 4000 으로', 'Booth 등 북미 중부', (4000, 4300))):
    W2 = dict(W); W2[key] = val
    lo = max(W2[n][0] for n in GLOBAL5); hi = min(W2[n][1] for n in GLOBAL5)
    print('    %-28s 다섯 창 공통 %d~%d, %d 년  (이것은 이 책의 가정 시험이며 논문의 값이 아니다)' % (nm, hi, lo, hi - lo))
json.dump(res, open('calc15-2-out.json', 'w'), ensure_ascii=False)
