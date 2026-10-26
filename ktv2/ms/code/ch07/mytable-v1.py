# -*- coding: utf-8 -*-
"""실습 7-1b. 독자의 표(집단 x 하플로그룹의 사람 수)를 넣어 이 장의 계산을 한 번에 돌린다.
입력 CSV: 첫 열 pop(집단 이름), 나머지 열은 하플로그룹별 사람 수(0 이상의 정수). 사용: python mytable-v1.py 표.csv [--B 9999]
출력: 행의 합과 열의 합, 유전자 다양도 H, 쌍별 Freeman-Halton Monte Carlo(Holm 보정), 전체 표 검정, AMOVA Phi_ST와 순열 p.
입력에 문제가 있으면 이유를 적고 종료 코드 2로 끝난다."""
import argparse, csv, itertools, sys, time
import numpy as np
from gentools import nei_h, fisher_rxc_mc, holm, individuals, amova_perm

ap = argparse.ArgumentParser()
ap.add_argument('csv')
ap.add_argument('--B', type=int, default=9999)
args = ap.parse_args()
t0 = time.time()
print('numpy', np.__version__, '| python', sys.version.split()[0])

def fail(msg):
    print('입력 오류:', msg)
    sys.exit(2)

try:
    rows = list(csv.reader(open(args.csv, encoding='utf-8')))
except OSError as e:
    fail('파일을 열지 못함 %r' % e)
if len(rows) < 3 or len(rows[0]) < 3 or rows[0][0] != 'pop':
    fail('첫 줄은 pop,열이름,열이름,...이고 집단이 2개 이상, 하플로그룹이 2개 이상이어야 한다')
names, hgs, cnt = [], rows[0][1:], []
for ln, r in enumerate(rows[1:], start=2):
    if len(r) != len(rows[0]):
        fail('%d째 줄의 칸 수가 머리글과 다르다' % ln)
    vals = []
    for x in r[1:]:
        try:
            v = float(x)
        except ValueError:
            fail('%d째 줄에 숫자가 아닌 값 %r' % (ln, x))
        if v < 0 or v != int(v):
            fail('%d째 줄의 값 %r이 0 이상의 정수가 아니다(사람 수여야 한다)' % (ln, x))
        vals.append(int(v))
    if sum(vals) < 2:
        fail('%d째 줄(%s)의 사람이 2명 미만이다' % (ln, r[0]))
    names.append(r[0]); cnt.append(vals)
C = np.array(cnt)
print('\n[1] 표와 합 (집단 %d, 하플로그룹 %d, 사람 %d)' % (C.shape[0], C.shape[1], C.sum()))
print('  %-8s %s | n' % ('집단', ' '.join('%6s' % h for h in hgs)))
for nm, r in zip(names, C):
    print('  %-8s %s | %d' % (nm, ' '.join('%6d' % v for v in r), r.sum()))
print('  %-8s %s | %d' % ('열 합', ' '.join('%6d' % v for v in C.sum(0)), C.sum()))
empty = [h for h, v in zip(hgs, C.sum(0)) if v == 0]
if empty:
    print('  주의: 사람이 한 명도 없는 하플로그룹 열 %s는 계산에서 영향이 없다' % empty)

print('\n[2] 집단별 Nei 유전자 다양도 H')
for nm, r in zip(names, C):
    print('  %-8s n=%2d H = %.4f' % (nm, r.sum(), nei_h([int(v) for v in r if v > 0])))

print('\n[3] 쌍별 Freeman-Halton Monte Carlo(B=20000, 시드 1)와 Holm 보정')
pairs = list(itertools.combinations(range(len(names)), 2))
ps = []
for i, j in pairs:
    t = C[[i, j]][:, C[[i, j]].sum(0) > 0]
    ps.append(fisher_rxc_mc(t, B=20000, seed=1))
adj = holm(np.array(ps))
for (i, j), p, q in zip(pairs, ps, adj):
    print('  %-8s 대 %-8s p = %.5f, Holm 보정 p = %.5f' % (names[i], names[j], p, q))
print('  p의 가능한 가장 작은 값 = 1/20001 = %.5f' % (1 / 20001))
tab = C[:, C.sum(0) > 0]
print('  전체 표(%d x %d) Monte Carlo(B=20000, 시드 1) p = %.5f' % (tab.shape[0], tab.shape[1], fisher_rxc_mc(tab, B=20000, seed=1)))

print('\n[4] AMOVA(하플로그룹이 같으면 0, 다르면 1) 묶음 없음, 순열 %d회(시드 1)' % args.B)
hap, popi = individuals([list(r) for r in C])
D2 = (hap[:, None] != hap[None, :]).astype(float)
obs, pv = amova_perm(D2, popi, None, B=args.B, seed=1)
print('  개체 %d, 집단 %d | 분산 몫(%%): 집단 사이 %.2f, 집단 안 %.2f | Phi_ST = %.4f (p = %.4f, 가능한 가장 작은 p = %.4f)' % (obs['N'], obs['P'], obs['pct_b'], obs['pct_c'], obs['phi_st'], pv['phi_st'], 1 / (args.B + 1)))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
