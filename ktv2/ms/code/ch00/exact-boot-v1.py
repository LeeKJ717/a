# -*- coding: utf-8 -*-
"""0장 보충: 대산전 [1,3,1,2,2]의 부트스트랩 H 분포를 모의(난수)가 아니라 정확히 센다.
n=9명을 같은 빈도에서 복원추출하면 형별 수의 벡터는 다항분포를 따른다. 가능한 벡터를 모두 세어 H의 값과 확률을 구한다."""
import itertools, math
from collections import defaultdict
counts = [1, 3, 1, 2, 2]; n = sum(counts); k = len(counts)
p = [c / n for c in counts]
dist = defaultdict(float); nvec = 0
def comps(total, parts):
    if parts == 1:
        yield (total,); return
    for i in range(total + 1):
        for rest in comps(total - i, parts - 1):
            yield (i,) + rest
for v in comps(n, k):
    nvec += 1
    pr = math.factorial(n)
    for c, q in zip(v, p): pr = pr / math.factorial(c) * (q ** c)
    h = n / (n - 1) * (1 - sum((c / n) ** 2 for c in v))
    dist[round(h, 10)] += pr
vals = sorted(dist)
print('가능한 형별 수 벡터의 수 =', nvec, ' 서로 다른 H 값의 수 =', len(vals), ' 확률의 합 = %.12f' % sum(dist.values()))
cum = 0.0; out = {}
for v in vals:
    cum += dist[v]
    for q in (0.025, 0.5, 0.975):
        if q not in out and cum >= q: out[q] = v
print('정확한 분포의 분위수(누적확률이 처음 그 값 이상이 되는 H):', {k_: round(v, 3) for k_, v in out.items()})
print('가장 작은 H %.4f(확률 %.4f), 가장 큰 H %.4f(확률 %.4f)' % (vals[0], dist[vals[0]], vals[-1], dist[vals[-1]]))
