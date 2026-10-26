# -*- coding: utf-8 -*-
"""실습 7-1, 7-2. Cui 등(2013) 표 1(제1권 11장이 옮긴 값, cui-table1-v1.csv)로 하플로그룹 빈도표를 만들고
제1권 11장의 계산 11-1, 11-2, 11-4와 맞춘다. 사용: python hgtab-v1.py"""
import itertools, math, sys, time
import numpy as np
from gentools import read_cui, HG, nei_h

t0 = time.time()
rows = read_cui()
print('numpy', np.__version__, '| python', sys.version.split()[0])
print('\n[1] 표와 행의 합')
print('%-6s %-14s %5s | %s | %s | %s' % ('유적', '문화', 'n', ' '.join('%6s' % h for h in HG), '합', '빈도(%)'))
for s, cu, a, b, n, c in rows:
    print('%-6s %-14s %5d | %s | %2d %s | %s' % (s, cu, n, ' '.join('%6d' % x for x in c), sum(c), '정합' if sum(c) == n else '불일치',
                                                  ' '.join('%5.1f' % (100 * x / n) for x in c)))
W = rows[:4]
nW = sum(r[4] for r in W)
print('서요하 네 곳 시료 합 = %s = %d' % (' + '.join(str(r[4]) for r in W), nW))
print('전체(6곳) 시료 합 = %d (논문 47)' % sum(r[4] for r in rows))
print('\n[2] 서요하 네 곳 열 합과 빈도')
cs = [sum(r[5][i] for r in W) for i in range(5)]
for h, x in zip(HG, cs):
    print('  %-6s %2d/%d = %.1f%%' % (h, x, nW, 100 * x / nW))
print('  N1 전체(N1(x)+N1c) = %d/%d = %.1f%%' % (cs[0] + cs[1], nW, 100 * (cs[0] + cs[1]) / nW))
neo_n = rows[0][4] + rows[1][4]
neo_c = rows[0][5][0] + rows[1][5][0]
print('  신석기(우하량+합라해구) N1(x) = %d/%d = %.1f%%' % (neo_c, neo_n, 100 * neo_c / neo_n))
print('  우하량 C 1/6 = %.1f%% (논문 표 13.7)' % (100 / 6))

print('\n[3] Nei 유전자 다양도 H')
for s, cu, a, b, n, c in rows:
    cc = [x for x in c if x > 0]
    print('  %-6s n=%2d 빈도 %-18s H = %.4f' % (s, n, cc, nei_h(cc)))
neo = [x + y for x, y in zip(rows[0][5], rows[1][5])]
print('  신석기 합 %s: H = %.4f' % ([x for x in neo if x > 0], nei_h(neo)))

print('\n[4] 부트스트랩(제1권과 같은 절차: 같은 빈도에서 n명을 다중항 추출, B=20000, 시드 11, 같은 호출 순서)')
rng = np.random.default_rng(11)
def boot(c, B=20000):
    n = sum(c); pr = np.array(c) / n
    hs = []
    for _ in range(B):
        k = rng.multinomial(n, pr)
        hs.append(nei_h([int(x) for x in k if x > 0]) if n > 1 else 0)
    hs = np.array([h for h in hs if not math.isnan(h)])
    return np.percentile(hs, [2.5, 50, 97.5])
V1 = {'신석기 합': ([16, 1, 1], (0.000, 0.209, 0.464)), '대산전': ([1, 3, 1, 2, 2], (0.556, 0.778, 0.889)), '대전자': ([3, 2], (0.000, None, 0.600))}
for nm, (c, v1) in V1.items():
    lo, md, hi = boot(c)
    print('  %-8s 2.5%% %.3f 중앙 %.3f 97.5%% %.3f | 제1권 %s' % (nm, lo, md, hi, v1))

print('\n[5] 난수 없이 정확하게: 다중항 분포를 모든 구성으로 세어 H의 분포를 구한다')
def exact_h(c):
    n = sum(c); k = len(c); pr = [x / n for x in c]
    dist = {}
    def comps(n, k):
        if k == 1:
            yield (n,); return
        for i in range(n + 1):
            for rest in comps(n - i, k - 1):
                yield (i,) + rest
    lf = [math.lgamma(i + 1) for i in range(n + 1)]
    for comp in comps(n, k):
        lp = lf[n] - sum(lf[x] for x in comp) + sum(x * math.log(p) for x, p in zip(comp, pr) if x > 0)
        h = round(nei_h([x for x in comp if x > 0]), 10)
        dist[h] = dist.get(h, 0.0) + math.exp(lp)
    return sorted(dist.items())
for nm, (c, v1) in V1.items():
    d = exact_h(c)
    tot = sum(p for _, p in d)
    cum = 0; q = {}
    for h, p in d:
        cum += p
        for qq in (0.025, 0.5, 0.975):
            if qq not in q and cum >= qq - 1e-12:
                q[qq] = h
    print('  %-8s H가 가질 수 있는 값 %d개, 확률 합 %.6f; 누적분포가 처음 0.025, 0.5, 0.975 이상이 되는 H = %.3f, %.3f, %.3f' % (nm, len(d), tot, q[0.025], q[0.5], q[0.975]))
    if nm == '대산전':
        print('    대산전의 P(H < 0.556) = %.4f, P(H = 0.556) = %.4f' % (sum(p for h, p in d if h < 0.5555), sum(p for h, p in d if abs(h - 0.5556) < 1e-3)))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
