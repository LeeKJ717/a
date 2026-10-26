# -*- coding: utf-8 -*-
"""계산 8-3. Begash 숯 연대의 빈 틈이 약 1100 cal BP(Li 등 2022의 건조 정점)를 포함하는 것은 우연 이상인가.
입력: 7장 계산 7-4가 구한 빈 틈 기원후 552~1230년(679년)과 Begash 숯 34행. 틈의 cal BP: 1950-1230=720 ~ 1950-552=1398.
방법: 틈의 폭(679년)을 같은 숯 연대 34개를 가진 유적의 기록 범위 안에서 위치만 무작위로 옮겨, 고정된 한 해(1100 cal BP)를 포함할 비율을 센다(순열). 기록 범위 = 가장 오래된 보정 구간 끝~가장 젊은 끝(7장 로그의 값).
이것은 '위치가 무작위일 때 어떤 해가 틈에 들 기본 확률'이며 인과를 시험하지 않는다. 기록 지점(카자흐스탄)과 Li 등의 지점(중국 서부)은 다르다.
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'ch07'))
import numpy as np, c14lib as c, c14data as d
G = c.GRID
union = np.zeros(len(G), bool)
for r in d.BEGASH:
    p = c.calibrate(r[2], r[3]); a, b = c.outer(p); union |= (G >= a) & (G <= b)
# 95.4% 바깥 구간 합집합이 아닌 HPD 합집합으로 빈 틈을 다시 구해 7장과 비교
union2 = np.zeros(len(G), bool)
for r in d.BEGASH:
    p = c.calibrate(r[2], r[3]); segs = c.hpd(p)
    for lo, hi, _m in segs: union2 |= (G >= lo) & (G <= hi)
def gaps(u):
    out = []; i = 0
    lo_rec = np.where(u)[0].min(); hi_rec = np.where(u)[0].max(); i = lo_rec
    while i <= hi_rec:
        if not u[i]:
            j = i
            while j <= hi_rec and not u[j]: j += 1
            out.append((int(G[i]), int(G[j - 1]), int(G[j - 1] - G[i] + 1))); i = j
        else: i += 1
    return out, int(G[lo_rec]), int(G[hi_rec])
g1, lo1, hi1 = gaps(union); g2, lo2, hi2 = gaps(union2)
print('기록 범위(바깥 구간 합집합) cal BP %d ~ %d (폭 %d년)' % (lo1, hi1, hi1 - lo1 + 1))
print('바깥 구간 합집합의 가장 긴 틈:', sorted(g1, key=lambda x: -x[2])[:3])
print('HPD 합집합의 가장 긴 틈  :', sorted(g2, key=lambda x: -x[2])[:3])
gap = max(g1, key=lambda x: x[2]); W = gap[2]
T = 1100; contains = gap[0] <= T <= gap[1]
print('가장 긴 틈 cal BP %d ~ %d (%d년); 1100 cal BP 포함: %s' % (gap[0], gap[1], W, contains))
rng = np.random.default_rng(20261028); N = 200000
span = hi1 - lo1 + 1
start = rng.integers(lo1, hi1 - W + 2, N)
inc = (start <= T) & (T <= start + W - 1)
p = float(inc.mean())
print('틈 위치를 기록 범위 안에서 무작위로 옮길 때 고정된 한 해를 포함할 비율 = %.3f (해석식 %d/%d = %.3f, 가장자리 보정 전)' % (p, W, span - W + 1, W / (span - W + 1)))
# 1100 이 기록 범위의 어디에 있는가
print('1100 cal BP 근방(1100 +- 50)에서 어느 날짜의 95.4%% 구간에도 안 드는 해의 몫: %.2f' % float((~union[(G >= 1050) & (G <= 1150)]).mean()))
json.dump(dict(span=[lo1, hi1], gap=list(gap), contains_1100=bool(contains), chance=p, gaps_outer=g1, gaps_hpd=g2), open(os.path.join(HERE, 'calc-8-3-gap.json'), 'w'), ensure_ascii=False, indent=1)
