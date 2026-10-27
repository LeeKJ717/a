# -*- coding: utf-8 -*-
"""계산 15-4: 방향 집계(8장 계산 8-3)가 분류와 선택에 얼마나 달려 있는가.
입력(8장 계산 8-3): 24곳 = 건조 15, 습윤 4, 변화 없음 3, 따뜻함·녹은 물 1, 혼합 1. 유라시아 19곳 = 건조 12, 습윤 3, 변화 없음 3, 따뜻함 1.
새 5곳 = Booth(건조), Thompson 킬리만자로(건조), Marchant 아프리카(건조), Marchant 남미(습윤), Bini(혼합).
(a) 분류 규칙 여덟 가지의 이항 검정. (b) 안 보인 습윤·무변화 기록 k 개를 더하면. (c) 기록이 건조로 보고될 확률 p0 가 얼마여야 15/19 가 평범한가.
모든 대안 분류는 이 책의 시험이며 논문의 분류가 아니다."""
import numpy as np, json
from scipy import stats
from scipy.optimize import brentq
def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1); hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi
def p1(k, n, p0=0.5): return stats.binomtest(k, n, p0, alternative='greater').pvalue
print('=== 계산 15-4 (a) 분류 규칙을 바꾸면(건조 쪽 단측 이항 p, 기준 0.5) ===')
S = [
 ('S1 8장의 규칙: 건조 15, 습윤 4 (변화 없음·따뜻함·혼합 제외)', 15, 19),
 ('S2 아프리카를 한 곳으로(Thompson 킬리만자로와 Marchant 아프리카가 같은 대륙): 건조 14, 습윤 4', 14, 18),
 ('S3 변화 없음 3과 따뜻함 1과 혼합 1을 건조 아님으로 센다: 건조 15 / 24', 15, 24),
 ('S4 혼합과 따뜻함을 습윤 쪽에 센다: 건조 15, 습윤 4+1+1=6', 15, 21),
 ('S5 변화 없음 3을 습윤 쪽에 센다: 건조 15, 습윤 4+3=7', 15, 22),
 ('S6 유라시아 19곳만(건조 12, 습윤 3)', 12, 15),
 ('S7 새 5곳 가운데 혼합 제외 4곳만(건조 3, 습윤 1)', 3, 4),
 ('S8 S2와 S3를 함께(아프리카 한 곳, 건조 14 / 23)', 14, 23),
]
rows = []
for nm, k, n in S:
    lo, hi = cp(k, n); p = p1(k, n)
    rows.append(dict(name=nm, k=k, n=n, p=p, lo=lo, hi=hi))
    print('  %-80s 비율 %.3f, 95%% 구간 %.3f~%.3f, p = %.4f' % (nm, k / n, lo, hi, p))
print('  p < 0.05 인 규칙: %d 개 / %d 개. p 의 범위 %.4f ~ %.4f' % (sum(r['p'] < 0.05 for r in rows), len(rows), min(r['p'] for r in rows), max(r['p'] for r in rows)))
print()
print('=== 계산 15-4 (b) 서랍 문제: 보고되지 않은 습윤 기록 k 개를 S1 에 더하면(건조 15, 습윤 4+k) ===')
for kk in (0, 1, 2, 3, 4, 5, 6, 8):
    print('  k = %2d: 건조 15 / %d, p = %.4f' % (kk, 19 + kk, p1(15, 19 + kk)))
kmin = next(kk for kk in range(0, 60) if p1(15, 19 + kk) >= 0.05)
print('  p 가 0.05 이상이 되는 최소 k = %d (습윤 %d, 합 %d)' % (kmin, 4 + kmin, 19 + kmin))
kmin10 = next(kk for kk in range(0, 60) if p1(15, 19 + kk) >= 0.10)
print('  p 가 0.10 이상이 되는 최소 k = %d' % kmin10)
print('  (점검) k = 5 는 건조 15 / 24 로 S3 와 같은 수이다: p = %.4f' % p1(15, 24))
print()
print('=== 계산 15-4 (c) 기록이 건조로 보고될 확률 p0 가 얼마여야 건조 15 / 19 가 평범한가 ===')
f = lambda p0: p1(15, 19, p0) - 0.05
p05 = brentq(f, 0.5, 0.99)
print('  15/19 의 단측 p 가 0.05 가 되는 p0 = %.3f. p0 가 이보다 크면 15/19 는 우연으로 평범하다(p >= 0.05)' % p05)
for p0 in (0.5, 0.6, 0.65, 0.7, 0.75):
    print('  p0 = %.2f: P(건조 >= 15 | 19) = %.4f' % (p0, p1(15, 19, p0)))
json.dump(dict(rows=rows, kmin=kmin, kmin10=kmin10, p0=p05), open('calc15-4-out.json', 'w'), ensure_ascii=False)
