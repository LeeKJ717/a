# -*- coding: utf-8 -*-
"""실습 3-6: R 패키지 clam 2.6.3 이 같은 곡선 파일(IntCal20)로 보정한 95% 범위(r/out/GY1_calibrated.txt)와
이 책의 파이썬 보정(c14lib.calibrate, hpd)을 견준다. 먼저 r/ex5-gy1-models.R 을 실행해 파일을 만들어야 한다(없으면 알림 후 끝)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from c14lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(HERE, 'r', 'out', 'GY1_calibrated.txt')
if not os.path.exists(f):
    print('clam 출력 없음: r/ex5-gy1-models.R 을 먼저 실행해야 한다 (R 과 clam 필요)'); sys.exit(0)
try:
    cur = load_curve('intcal20')
except CurveMissing as e:
    print(e); sys.exit(0)
txt = open(f, encoding='utf-8').read()
blocks = re.split(r'Depth:\s+', txt)[1:]
clam = {}
for b in blocks:
    lines = b.strip().splitlines()
    d = int(lines[0].strip())
    segs = []
    for ln in lines[2:]:
        p = ln.split()
        if len(p) >= 3:
            a, bb, pr = float(p[0]), float(p[1]), float(p[2]); segs.append((min(a, bb), max(a, bb), pr))
    clam[d] = segs
dates = {363: (1800, 30), 739: (2810, 30), 889: (4150, 30), 917: (6100, 40), 1416: (7210, 40), 1839: (7900, 40), 2060: (7960, 40), 2351: (8030, 40), 2892: (8870, 40)}
print('깊이(cm)  14C 나이 | clam 95% 외곽 (구간 수) | 이 책 IntCal20 95.4% 외곽 (구간 수) | 끝점 차이(이 책 - clam)')
mx = 0
for d, (c14, sd) in dates.items():
    g, p = calibrate(c14, sd, cur)
    s = hpd(g, p, 0.954)
    h = (s[0][0], s[-1][1])
    cs = clam[d]
    ch = (min(x[0] for x in cs), max(x[1] for x in cs))
    dl, dh = h[0] - ch[0], h[1] - ch[1]
    mx = max(mx, abs(dl), abs(dh))
    print(f'  {d:5d}  {c14}+-{sd} | {ch[0]:.0f}~{ch[1]:.0f} ({len(cs)}) | {h[0]:.0f}~{h[1]:.0f} ({len(s)}) | {dl:+.0f}, {dh:+.0f}')
print(f'끝점 차이의 최대 절댓값: {mx:.0f} 년')
