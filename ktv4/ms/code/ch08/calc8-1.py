# -*- coding: utf-8 -*-
"""계산 8-1: Wanner 등(2011)의 여섯 냉각 사건 연대와 Mayewski 등(2004)의 여섯 급변 구간이 겹치는가.
입력(논문): Wanner 등: 8200, 6300, 4700, 2700, 1550, 550 BP. Mayewski 등: 9000-8000, 6000-5000, 4200-3800, 3500-2500, 1200-1000, 600-150 cal BP.
두 논문의 BP 와 cal BP 는 같은 눈금(1950 기준 보정 연대)이라고 가정한다(원문 확인 필요).
무작위 시험: 사건 6개를 창 안에 균일하게 놓았을 때 구간 안에 들어가는 개수의 분포(이항, 순열)."""
import numpy as np
from scipy import stats
W = [8200, 6300, 4700, 2700, 1550, 550]
M = [(8000, 9000), (5000, 6000), (3800, 4200), (2500, 3500), (1000, 1200), (150, 600)]
tot = sum(b-a for a, b in M)
print('Mayewski 구간 길이:', [b-a for a, b in M], '합', tot, '년')
def hit(t, tol=0): return any(a-tol <= t <= b+tol for a, b in M)
for tol in (0, 50, 100):
    h = [hit(t, tol) for t in W]
    print('허용 +-%d 년: 들어간 사건 %s -> %d / 6' % (tol, [t for t, x in zip(W, h) if x], sum(h)))
print()
print('창 길이별 기대 개수와 이항 확률(구간이 창에서 차지하는 비율 p = 합/창)')
rng = np.random.default_rng(20261027)
for win in (9000, 10000, 11700):
    for tol in (0, 100):
        cover = 0.0
        # 허용을 넣은 덮는 길이(겹침은 합집합으로)
        xs = np.arange(0, win+1)
        m = np.zeros(win+1, bool)
        for a, b in M:
            m[max(0, a-tol):min(win, b+tol)+1] = True
        p = m.mean()
        k = sum(hit(t, tol) for t in W)
        pv = stats.binom.sf(k-1, 6, p)
        # 몬테카를로: 6개 균일 -> 개수
        draws = rng.integers(0, win+1, size=(200000, 6))
        cnt = m[draws].sum(1)
        pmc = (cnt >= k).mean()
        print('  창 0~%5d, 허용 %3d: 덮는 비율 %.3f, 기대 %.2f, 관측 %d, 이항 P(>=관측) %.3f, 몬테카를로 %.3f' % (win, tol, p, 6*p, k, pv, pmc))
print()
print('일치한 세 쌍: 8200 은 9000~8000, 2700 은 3500~2500, 550 은 600~150 안. 어긋난 셋: 6300, 4700, 1550(아래 줄에서 가장 가까운 구간 끝까지의 거리를 계산)')
for t in (6300, 4700, 1550):
    d = min(min(abs(t-a), abs(t-b)) for a, b in M)
    print('   %d 에서 가장 가까운 구간 끝까지 %d 년' % (t, d))
