# -*- coding: utf-8 -*-
"""계산 7-6. Deng 등(2019) 표 1: 맥락(층)의 시기와 낟알 자체의 연대가 어긋난 '혼입' 밀의 규모.
맥락의 달력 연대는 표에 없다. 그래서 (1) 혼입으로 판정된 밀이 전체 직접 연대 밀에서 차지하는 비율, (2) 혼입 밀의 보정 연대와 이 표에서 가장 이른 진짜 밀(Baligang)의 차이만 센다."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, c14lib as c, c14data as d
W = [r for r in d.DENG if r[3] == '밀']
print('직접 연대 밀 %d개 (표 1)' % len(W))
xz = [r for r in W if r[0] == 'Xiazhai']; intr = [r for r in xz if '혼입' in r[2]]
print('Xiazhai 밀 %d개 중 혼입 %d개 (%.1f%%)' % (len(xz), len(intr), 100 * len(intr) / len(xz)))
allintr = [r for r in W if '혼입' in r[2]]
print('다른 유적(Baligang, Nanjie, Nangao)의 후기 용산 밀 3개 중 2개(Nanjie 100±20, Nangao 1580±20)는 후기 용산 맥락인데 기원후 연대. 이 둘도 층과 어긋남(논문 표에는 혼입 표기가 없음)')
ref = c.calibrate(3670, 25); mref = float(c.to_year(c.median(ref)))
print('가장 이른 진짜 밀 Baligang UGAMS#27671 3670±25: 중앙값 %s' % c.fmt_year(mref))
res = []
for r in intr:
    p = c.calibrate(r[4], r[5]); m = float(c.to_year(c.median(p))); a, b = c.outer(p)
    # 두 연대의 차를 몬테카를로로: 년
    rng = np.random.default_rng(3)
    cd1 = np.cumsum(p); cd2 = np.cumsum(ref)
    s1 = c.GRID[np.minimum(np.searchsorted(cd1, rng.random(100000)), len(c.GRID) - 1)]
    s2 = c.GRID[np.minimum(np.searchsorted(cd2, rng.random(100000)), len(c.GRID) - 1)]
    dif = s2 - s1
    lo, md, hi = np.percentile(dif, [2.5, 50, 97.5])
    print('  %-9s %-14s %4d±%-3d 중앙값 %-10s Baligang보다 젊은 정도 %5.0f년 (95%% %5.0f ~ %5.0f)' % (r[1], r[2], r[4], r[5], c.fmt_year(m), md, lo, hi))
    res.append((r[1], r[2], m, float(md), float(lo), float(hi)))
json.dump(dict(n_wheat=len(W), n_xz=len(xz), n_intrusive_xz=len(intr), baligang_median=mref, rows=res), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-6-intrusive.json'), 'w'), ensure_ascii=False, indent=1)
