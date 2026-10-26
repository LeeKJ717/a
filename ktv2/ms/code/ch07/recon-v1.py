# -*- coding: utf-8 -*-
"""실습 7-2b. 논문 표의 반올림된 비율(소수 첫째 자리)에서 사람 수를 되짚을 수 있는가.
Cui 등(2013) 표 1의 비율(제1권 계산 11-1이 옮긴 값)에 대해, 표본 크기 n이 알려진 경우 그 비율을 내는 정수 개수를 모두 찾는다.
비율의 반올림은 소수 첫째 자리에서 반올림(0.05는 올림)으로 가정한다. 사용: python recon-v1.py"""
import sys, time
from decimal import Decimal, ROUND_HALF_UP
t0 = time.time()
print('python', sys.version.split()[0])

def pct(k, n):
    return (Decimal(100) * Decimal(k) / Decimal(n)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

SITE = [('우하량', 6, [66.7, None, 13.7, 13.7, None], [4, 0, 1, 1, 0]), ('합라해구', 12, [100.0, None, None, None, None], [12, 0, 0, 0, 0]),
        ('대전자', 5, [60.0, None, None, 40.0, None], [3, 0, 0, 2, 0]), ('대산전', 9, [11.1, 33.3, 11.1, 22.2, 22.2], [1, 3, 1, 2, 2]),
        ('금구자', 12, [None, None, 100.0, None, None], [0, 0, 12, 0, 0]), ('묘자구', 3, [100.0, None, None, None, None], [3, 0, 0, 0, 0])]
HG = ['N1(x)', 'N1c', 'C/C3e', 'O3a', 'O3a3c']
print('\n[1] n이 알려졌을 때, 표에 적힌 비율을 내는 정수 개수 k(0..n)를 모두 찾는다 (재구성 개수는 제1권 11장이 쓴 값)')
for nm, n, pr, used in SITE:
    for h, p, u in zip(HG, pr, used):
        if p is None:
            continue
        ks = [k for k in range(n + 1) if pct(k, n) == Decimal(str(p))]
        near = min(range(n + 1), key=lambda k: abs(float(pct(k, n)) - p))
        print('  %-5s n=%2d %-6s 표의 %5.1f%% -> 가능한 개수 %s (제1권이 쓴 개수 %d)%s' % (nm, n, h, p, ks if ks else '없음', u, '' if ks else ' | 가장 가까운 개수 %d는 %s%%' % (near, pct(near, n))))
print('\n[2] 13.7%를 내는 (n, k) 쌍: n = 1..60')
hits = [(n, k) for n in range(1, 61) for k in range(n + 1) if pct(k, n) == Decimal('13.7')]
print('  ' + ', '.join('%d/%d' % (k, n) for n, k in hits))
print('  n = 6에서는 없음. 논문 표의 우하량 시료 6명과 13.7%는 정수 개수로는 함께 성립하지 않는다.')
print('\n[3] 같은 비율이 서로 다른 n에서 나오는 정도: 66.7%와 33.3%가 나오는 n = 1..30')
for p in ('66.7', '33.3'):
    h = [(n, k) for n in range(1, 31) for k in range(n + 1) if pct(k, n) == Decimal(p)]
    print('  %s%%: %s' % (p, ', '.join('%d/%d' % (k, n) for n, k in h)))
print('  비율만 있고 n을 모르면 개수가 정해지지 않는다. n이 알려져 있고 비율에 모순이 없을 때에만 되짚을 수 있다.')
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
