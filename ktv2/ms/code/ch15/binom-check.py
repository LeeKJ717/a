# -*- coding: utf-8 -*-
"""사례 1 보조: 순열 100만 번의 b가 정확한 p에서 기대되는 값과 얼마나 떨어졌는가(이항분포). 입력은 case1.log의 값이다."""
import math
from scipy import stats
B = 1000000
for name, p, b in [('신석기 대 청동기(대전자 + 대산전)', 7.077107e-04, 698), ('신석기 대 대전자(하가점하층)', 1.936759e-01, 193474), ('신석기 대 대산전(하가점상층)', 1.653571e-04, 190)]:
    mu = B * p; sd = math.sqrt(B * p * (1 - p))
    print('%-34s 정확한 한쪽 p %.6e  기대 b %.1f  표준편차 %.1f  관측 b %d  z = %.2f  이항 양쪽 p = %.3f' % (name, p, mu, sd, b, (b - mu) / sd, 2 * min(stats.binom.cdf(b, B, p), stats.binom.sf(b - 1, B, p))))
