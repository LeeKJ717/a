# -*- coding: utf-8 -*-
"""계산 8-1. 지역별 가장 이른 보리가 4.2 ka(4200 cal BP)보다 앞서는가. Liu 등(2017) 표 1의 옮긴 88행(7장 c14data)을 쓴다.
방법: 7장 계산 7-2와 같다. 날짜마다 IntCal20 보정 분포에서 한 값씩 뽑고(독립) 지역 안의 가장 오래된 값을 '가장 이른 값'으로 삼아 20만 번 되풀이한다.
문턱 4200 cal BP는 제1권 12장이 쓴 4.2 ka 사건(기원전 2250)의 점 값이다. 4400, 4000은 이 책이 정한 민감도 점검의 시연값이다(논문에 없다).
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'ch07'))
import numpy as np, c14lib as c, c14data as d
rng = np.random.default_rng(20261027); N = 200000
def reg(r):
    g = r[0]; return '중앙아시아' if g.startswith('중앙아시아') else ('중·동부 중국' if g.startswith('중·동부') else g)
regs = {}
for r in d.LIU: regs.setdefault(reg(r), []).append(r)
order = ['북서인도', '갠지스', '남인도', '티베트', '청해', '감숙', '중앙아시아', '신강', '중·동부 중국']
TH = [4400, 4200, 4000]
out = {}
print('문턱(cal BP)별: 지역, n, 가장 이른 값이 문턱보다 오래될 확률, 날짜 하나하나의 질량 평균 중 문턱보다 젊은 몫')
print('%-10s %3s' % ('지역', 'n') + ''.join('%14s' % ('P(최초>%d)' % t) for t in TH) + ''.join('%14s' % ('젊은몫<%d' % t) for t in TH) + '   가장 이른 값 95%(cal BP)')
for g in order:
    rows = regs[g]; n = len(rows)
    cds = [np.cumsum(c.calibrate(r[3], r[4])) for r in rows]
    S = np.stack([c.GRID[np.minimum(np.searchsorted(cd, rng.random(N)), len(c.GRID) - 1)] for cd in cds])
    e = S.max(axis=0)
    pf = [float((e > t).mean()) for t in TH]
    yg = []
    for t in TH:
        yg.append(float(np.mean([cd[int(t) - 1] if False else (1 - c.calibrate(r[3], r[4])[c.GRID > t].sum()) for r, cd in zip(rows, cds)])))
    lo, md, hi = np.percentile(e, [2.5, 50, 97.5])
    out[g] = dict(n=n, P_first_older=dict(zip(map(str, TH), pf)), young_share=dict(zip(map(str, TH), yg)), first_calBP=[float(lo), float(md), float(hi)])
    print('%-10s %3d' % (g, n) + ''.join('%14.3f' % x for x in pf) + ''.join('%14.3f' % x for x in yg) + '   %d ~ %d (중앙 %d)' % (lo, hi, md))
json.dump(out, open(os.path.join(HERE, 'calc-8-1-after42.json'), 'w'), ensure_ascii=False, indent=1)
