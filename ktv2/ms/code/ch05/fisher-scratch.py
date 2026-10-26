# -*- coding: utf-8 -*-
"""5장 실습 5-1: Fisher 정확검정을 처음부터 구현하고 scipy와 맞춘다.
제1권 11장 계산 11-3, 11-3b의 표 [[16, 2], [4, 10]]를 되풀이한다.
실행: python3 fisher-scratch.py | tee fisher-scratch.log
"""
import sys, time, platform, json
from math import comb
from fractions import Fraction
import numpy as np
import scipy
from scipy import stats

t0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))


def counts(a, b, c, d):
    """합계를 고정했을 때 왼쪽 위 칸 x가 가질 수 있는 값마다 경우의 수(정수)를 돌려준다."""
    r1, r2, c1 = a + b, c + d, a + c
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return {x: comb(r1, x) * comb(r2, c1 - x) for x in range(lo, hi + 1)}, comb(a + b + c + d, c1)


def fisher_exact_scratch(a, b, c, d, alt='two-sided'):
    """정수 비교로 양쪽 p를 구한다. 관측 표의 경우의 수 이하인 표를 모두 더한다."""
    ways, total = counts(a, b, c, d)
    w0 = ways[a]
    if alt == 'two-sided':
        s = sum(w for w in ways.values() if w <= w0)
    elif alt == 'greater':
        s = sum(w for x, w in ways.items() if x >= a)
    else:
        s = sum(w for x, w in ways.items() if x <= a)
    return float(Fraction(s, total))


print('\n== A. 단계별 표: [[16, 2], [4, 10]] (제1권 계산 11-3b) ==')
ways, total = counts(16, 2, 4, 10)
print('행 합 18, 14 / 열 합 20, 12 / 총 32 / C(32,20) = {:,}'.format(total))
for x, w in ways.items():
    print('  a = %2d : 경우의 수 %12s  확률 %.3e %s' % (x, '{:,}'.format(w), w / total, '<= 관측' if w <= ways[16] else ''))
print('확률의 합 = %.6f' % (sum(ways.values()) / total))
p_two = fisher_exact_scratch(16, 2, 4, 10)
p_gr = fisher_exact_scratch(16, 2, 4, 10, 'greater')
print('양쪽 p = %.6e / 한쪽(greater) p = %.6e / 한쪽의 2배 = %.6e' % (p_two, p_gr, 2 * p_gr))

print('\n== B. scipy와 대조 ==')
cases = [('신석기 대 청동기(대전자+대산전)', 16, 2, 4, 10), ('신석기 대 대전자', 16, 2, 3, 2),
         ('신석기 대 대산전', 16, 2, 1, 8), ('위키백과 예(한쪽 less)', 1, 9, 11, 3)]
for nm, a, b, c, d in cases:
    alt = 'less' if '한쪽' in nm else 'two-sided'
    mine = fisher_exact_scratch(a, b, c, d, alt)
    ref = stats.fisher_exact([[a, b], [c, d]], alternative=alt)
    orr = (a * d) / (b * c)
    print('%-28s [[%d,%d],[%d,%d]] 직접 %.6g / scipy %.6g / 차 %.1e / 표본 오즈비 %.1f (scipy %.1f)' % (
        nm, a, b, c, d, mine, ref.pvalue, abs(mine - ref.pvalue), orr, ref.statistic))

print('\n== C. 제1권 값과 맞는가 ==')
vol1 = {'p[[16,2],[4,10]]': (0.00079, round(p_two, 5)), 'p[[16,2],[3,2]]': (0.194, round(fisher_exact_scratch(16, 2, 3, 2), 3)),
        'p[[16,2],[1,8]]': (0.00017, round(fisher_exact_scratch(16, 2, 1, 8), 5)), '한쪽 p 7.08e-4': (7.08e-4, float('%.3g' % p_gr)),
        '한쪽의 2배 1.42e-3': (1.42e-3, float('%.3g' % (2 * p_gr)))}
for k, (v1, mine) in vol1.items():
    print('  %-20s 제1권 %-10g 이 실습 %-10g %s' % (k, v1, mine, '일치' if abs(v1 - mine) < 1e-12 else '불일치'))
print('  오즈비 20.0: (16*10)/(2*4) = %.1f' % (160 / 8))

print('\n== D. 오즈비는 두 가지다: 표본 오즈비와 조건부 최대가능도 추정 ==')
res = stats.contingency.odds_ratio([[16, 2], [4, 10]], kind='conditional')
ci = res.confidence_interval(0.95)
print('조건부 MLE = %.3f, 95%% 신뢰구간 %.3f ~ %.3f (scipy.stats.contingency.odds_ratio)' % (res.statistic, ci.low, ci.high))
print('표본 오즈비 = 20.000 (이 값이 제1권의 20.0이다. 두 값은 같지 않다)')
res2 = stats.contingency.odds_ratio([[16, 2], [4, 10]], kind='sample')
print('같은 함수의 kind=sample = %.3f' % res2.statistic)

print('\n== E. 카이제곱과 비교 ==')
for corr in (False, True):
    chi = stats.chi2_contingency([[16, 2], [4, 10]], correction=corr)
    print('카이제곱 correction=%s: 통계량 %.3f, p = %.5f, 기대도수 최소 %.2f' % (corr, chi[0], chi[1], chi[3].min()))

print('\n== F. 쉬운 예(시연값): 차 8잔, 우유 먼저 4잔 ==')
for k in range(5):
    w = comb(4, k) * comb(4, 4 - k)
    print('  %d개 맞힘: %2d/70 = %.4f' % (k, w, w / 70))
print('3개 이상 맞힘 한쪽 p = 17/70 = %.4f (scipy %.4f)' % (17 / 70, stats.fisher_exact([[3, 1], [1, 3]], alternative='greater').pvalue))

print('\n== G. 다른 검정과의 비교(시연: 같은 표에 Barnard, Boschloo) ==')
for nm, a, b, c, d in cases[:3]:
    t1 = time.perf_counter()
    bn = stats.barnard_exact([[a, b], [c, d]]).pvalue
    bo = stats.boschloo_exact([[a, b], [c, d]]).pvalue
    fi = fisher_exact_scratch(a, b, c, d)
    print('%-28s Fisher %.5f / Boschloo %.5f / Barnard %.5f  (%.2f초)' % (nm, fi, bo, bn, time.perf_counter() - t1))

print('\n== H. 한 사람이 바뀌면 p가 얼마나 움직이는가 ==')
for t in ([[16, 2], [4, 10]], [[15, 3], [4, 10]], [[16, 2], [5, 9]], [[15, 3], [5, 9]], [[14, 4], [6, 8]]):
    print('  %-18s p = %.5f' % (t, fisher_exact_scratch(*t[0], *t[1])))

print('\n== I. 양쪽 p의 정의 세 가지(표 [[16,2],[4,10]]) ==')
tp = [w / total for w in ways.values()]
p_min2 = min(1.0, 2 * min(sum(w for x, w in ways.items() if x >= 16), sum(w for x, w in ways.items() if x <= 16)) / total)
print('확률 이하 합(scipy와 이 실습) %.6e / 작은 쪽 꼬리의 2배 %.6e' % (p_two, p_min2))
mid = (sum(w for x, w in ways.items() if x > 16) + 0.5 * ways[16]) / total
print('mid-p(한쪽) = %.6e (관측 표 확률의 절반만 센다)' % mid)

print('\n== J. 부동소수점 확률을 허용오차 없이 비교하면 정수 비교와 갈리는 표가 있는가 (총 30명 이하 모든 표) ==')
bad = 0; checked = 0; worst = 0.0; example = None
for n in range(4, 31):
    for a in range(0, n + 1):
        for b in range(0, n - a + 1):
            for c in range(0, n - a - b + 1):
                d = n - a - b - c
                checked += 1
                w, tot = counts(a, b, c, d)
                exact = sum(v for v in w.values() if v <= w[a]) / tot
                xs = np.array(list(w.keys()))
                pm = stats.hypergeom.pmf(xs, n, a + c, a + b)      # 부동소수점 확률(로그 감마 경유)
                p0 = stats.hypergeom.pmf(a, n, a + c, a + b)
                naive = pm[pm <= p0].sum()                          # 허용오차 없음
                if abs(naive - exact) > 1e-9:
                    bad += 1
                    if abs(naive - exact) > worst:
                        worst = abs(naive - exact); example = (a, b, c, d, naive, exact)
print('검사한 표 %s개 중 허용오차 없는 부동소수점 비교가 정수 비교와 1e-9 넘게 다른 표 %d개 (최대 차 %.3e)' % ('{:,}'.format(checked), bad, worst))
if example:
    print('가장 크게 다른 표 [[%d,%d],[%d,%d]]: 허용오차 없음 %.6f / 정수 비교 %.6f' % example)
print('\n걸린 시간 %.1f초' % (time.perf_counter() - t0))
json.dump({'x': list(ways.keys()), 'p': [w / total for w in ways.values()], 'obs': 16}, open('fisher-scratch.json', 'w'))
