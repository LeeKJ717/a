# -*- coding: utf-8 -*-
"""9장과 10장 계산이 함께 쓰는 통계 도우미. 정수 조합으로 Fisher 정확검정을 직접 구현하고 scipy와 맞춘다.
제1권 11장 계산 11-3 과 같은 방식이다."""
import math
from fractions import Fraction

def fisher_two_sided(a, b, c, d):
    """표 [[a,b],[c,d]]의 양쪽 p. 합이 고정된 모든 표 가운데 확률이 관측 이하인 표의 확률을 더한다(Fraction으로 정확히)."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    den = math.comb(n, c1)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    probs = {x: Fraction(math.comb(r1, x) * math.comb(r2, c1 - x), den) for x in range(lo, hi + 1)}
    p_obs = probs[a]
    p2 = sum(p for p in probs.values() if p <= p_obs)
    p_hi = sum(p for x, p in probs.items() if x >= a)
    p_lo = sum(p for x, p in probs.items() if x <= a)
    return float(p2), float(p_hi), float(p_lo), den

def wilson(k, n, z=1.959964):
    """Wilson 점수 구간."""
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)

def clopper_pearson(k, n, alpha=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))

def gene_diversity(counts):
    n = sum(counts)
    return n / (n - 1) * (1 - sum((x / n) ** 2 for x in counts))
