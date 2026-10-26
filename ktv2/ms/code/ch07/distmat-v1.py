# -*- coding: utf-8 -*-
"""실습 7-4. 하플로그룹 빈도표(Cui 등 2013 표 1, 제1권 11장)에서 유적 사이의 거리 행렬 세 가지를 만든다.
(1) 빈도 벡터의 유클리드 거리, (2) Nei 표준 유전 거리, (3) 쌍별 Phi_ST(AMOVA, 하플로그룹이 같으면 0, 다르면 1).
사용: python distmat-v1.py"""
import sys, time
import numpy as np
from scipy.spatial.distance import pdist, squareform
from gentools import read_cui, individuals, amova, HG

t0 = time.time()
print('numpy', np.__version__, '| python', sys.version.split()[0])
rows = read_cui()
names = [r[0] for r in rows]
C = np.array([r[5] for r in rows], float)
N = C.sum(1)
F = C / N[:, None]
k = len(rows)

def show(M, title, fmt='%7.3f'):
    print('\n' + title)
    print('        ' + ' '.join('%7s' % n for n in names))
    for i in range(k):
        print('%-6s  ' % names[i] + ' '.join((fmt % M[i, j]) if np.isfinite(M[i, j]) else '    inf' for j in range(k)))

print('\n빈도 행렬(행 = 유적, 열 = %s)' % HG)
for n, f, nn in zip(names, F, N):
    print('  %-6s n=%2d %s' % (n, nn, ' '.join('%.3f' % x for x in f)))

# (1) 유클리드
E = squareform(pdist(F, 'euclidean'))
show(E, '(1) 빈도 벡터의 유클리드 거리')

# (2) Nei(1972) 표준 유전 거리: I = Jxy / sqrt(Jx Jy), D = -ln I
J = F @ F.T
d = np.sqrt(np.diag(J))
I = J / np.outer(d, d)
with np.errstate(divide='ignore'):
    ND = np.clip(-np.log(I), 0.0, None)
np.fill_diagonal(ND, 0.0)
show(ND, '(2) Nei 표준 유전 거리 D = -ln I (겹치는 하플로그룹이 없으면 I = 0이라 D는 무한대)')
print('  무한대인 쌍:', [(names[i], names[j]) for i in range(k) for j in range(i + 1, k) if not np.isfinite(ND[i, j])])

# (3) 쌍별 Phi_ST (AMOVA, 0/1 거리)
hap, pop = individuals([r[5] for r in rows])
Dh = (hap[:, None] != hap[None, :]).astype(float)         # 같은 하플로그룹 0, 다르면 1 (제곱해도 같다)
PS = np.zeros((k, k))
for i in range(k):
    for j in range(i + 1, k):
        sel = (pop == i) | (pop == j)
        a = amova(Dh[np.ix_(sel, sel)], pop[sel])
        PS[i, j] = PS[j, i] = a['phi_st']
und = [(names[i], names[j]) for i in range(k) for j in range(i + 1, k) if np.isnan(PS[i, j])]
print('\nPhi_ST가 0/0이라 정의되지 않는 쌍(두 유적 모두 같은 하나의 하플로그룹뿐):', und, '-> 이 책은 거리 0으로 둔다')
PS = np.nan_to_num(PS, nan=0.0)
show(PS, '(3) 쌍별 Phi_ST (음수는 그대로 둠, 0/0은 0)')
PS0 = np.clip(PS, 0, None)
print('  음수인 쌍:', [(names[i], names[j], round(PS[i, j], 4)) for i in range(k) for j in range(i + 1, k) if PS[i, j] < 0])
print('  음수인 쌍은 0으로 올리면 두 유적이 구별되지 않는(거리 0) 것으로 바뀐다')

# 거리 행렬의 성질
def props(M, nm):
    M2 = np.where(np.isfinite(M), M, np.nan)
    sym = np.allclose(M, M.T, equal_nan=True)
    hol = np.allclose(np.diag(M), 0)
    viol = []
    for i in range(k):
        for j in range(k):
            for l in range(k):
                if np.isfinite(M[i, j]) and np.isfinite(M[i, l]) and np.isfinite(M[l, j]) and M[i, j] > M[i, l] + M[l, j] + 1e-12:
                    viol.append((i, j, l))
    print('  %-10s 대칭 %s, 대각 0 %s, 삼각 부등식 위반 (i,j,l) 순서쌍 %d개(같은 세 점도 순서마다 센다)' % (nm, sym, hol, len(viol)))
print('\n거리 행렬의 성질')
props(E, '유클리드'); props(ND, 'Nei'); props(PS, 'Phi_ST'); props(PS0, 'Phi_ST(>=0)')

# 시간 행렬(표의 시기 구간의 가운데, BP)
mid = np.array([(r[2] + r[3]) / 2 for r in rows])
T = np.abs(mid[:, None] - mid[None, :])
print('\n표의 시기 구간 가운데(BP):', dict(zip(names, mid.astype(int))))
show(T, '시간 차 |가운데 BP 차| (년)', '%7.0f')
np.savetxt('cui-euclid-v1.tsv', E, delimiter='\t', fmt='%.6f')
np.savetxt('cui-phist-v1.tsv', PS, delimiter='\t', fmt='%.6f')
np.savetxt('cui-timediff-v1.tsv', T, delimiter='\t', fmt='%.1f')
print('\n저장: cui-euclid-v1.tsv, cui-phist-v1.tsv, cui-timediff-v1.tsv (행·열 순서 = %s)' % names)
print('총 걸린 시간 %.2f s' % (time.time() - t0))
