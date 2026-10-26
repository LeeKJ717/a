# -*- coding: utf-8 -*-
"""실습 7-6. Mantel 검정. (가) 제1권 11.4.2절의 'P 해상도' 점검, (나) scikit-bio의 mantel과 대조, (다) 시연값 4개 집단,
(라) 같은 입력 표의 여섯 유적: 유전 거리와 시간 차의 Mantel(제1권에 없는 새 계산), (마) 함정: 공간적으로 이어진 두 변수의 거짓 양성률 모의.
사용: python mantel-v1.py"""
import math, sys, time, itertools
import numpy as np
import scipy
from gentools import mantel, read_cui

t0 = time.time()
print('numpy', np.__version__, '| scipy', scipy.__version__, '| python', sys.version.split()[0])

print('\n[1] 제1권 11.4.2절 점검: 집단이 n개이면 이름표를 바꾸는 방법은 n!가지, 가능한 가장 작은 단측 P = 1/n!')
for n in (4, 5, 6, 8, 16):
    print('  n = %2d: n! = %s, 1/n! = %.3g' % (n, '{:,}'.format(math.factorial(n)), 1 / math.factorial(n)))
print('  Duggan 등(2013) 표 3(제1권이 옮김): 에벤 4개 집단 r = 0.71, P = 0.04 -> 1/24 = %.4f' % (1 / 24))
print('  5개 집단 r = 0.46, P = 0.11 -> 가능한 P는 k/120. 13/120 = %.4f (반올림 0.11), 14/120 = %.4f (반올림 0.12), 12/120 = %.4f (반올림 0.10)' % (13 / 120, 14 / 120, 12 / 120))
print('  16개 집단 r = 0.24, P = 0.12: 16! = %s 이라 전수는 불가능하고 무작위 순열로 추정한다' % '{:,}'.format(math.factorial(16)))

print('\n[2] 대조: 무작위 점 12개(시연값, 시드 3), 유전 거리 = 0.6 x 지리 거리 + 잡음. 이 책의 mantel 대 scikit-bio')
rng = np.random.default_rng(3)
xy = rng.uniform(0, 10, (12, 2))
G = np.sqrt(((xy[:, None] - xy[None, :]) ** 2).sum(-1))
Z = rng.normal(0, 1.5, (12, 12)); Z = (Z + Z.T) / 2; np.fill_diagonal(Z, 0)
H = np.abs(0.6 * G + Z)
np.fill_diagonal(H, 0)
mine = mantel(G, H, perms=9999, seed=11)
print('  이 책: r = %.6f, 양쪽 p = %.4f, 한쪽(큰 쪽) p = %.4f (무작위 순열 9999)' % (mine['r'], mine['p_two'], mine['p_greater']))
try:
    import skbio
    from skbio import DistanceMatrix
    from skbio.stats.distance import mantel as skm
    ids = [str(i) for i in range(12)]
    for alt in ('two-sided', 'greater'):
        r, p, n = skm(DistanceMatrix(G, ids), DistanceMatrix(H, ids), method='pearson', permutations=9999, alternative=alt, seed=11)
        print('  scikit-bio %s: r = %.6f, p = %.4f (%s, 순열 9999)' % (skbio.__version__, r, p, alt))
except Exception as e:
    print('  scikit-bio를 불러오지 못함:', repr(e))
a6 = mantel(G[:6, :6], H[:6, :6])
print('  앞 6점만 (정확, 720가지): r = %.6f, 양쪽 p = %.4f, 한쪽 p = %.4f, 순열 %d(%s)' % (a6['r'], a6['p_two'], a6['p_greater'], a6['n_perm'], a6['mode']))
try:
    r, p, n = skm(DistanceMatrix(G[:6, :6], ids[:6]), DistanceMatrix(H[:6, :6], ids[:6]), permutations=99999, alternative='two-sided', seed=5)
    print('  같은 6점을 scikit-bio 무작위 순열 99999로: r = %.6f, 양쪽 p = %.4f' % (r, p))
except Exception as e:
    print('  ', repr(e))

print('\n[3] 시연값 4개 집단: 전수 24가지 순열에서의 P')
xy4 = np.array([[0.0, 0.0], [1.0, 0.2], [2.5, 1.0], [3.0, 3.2]])
g4 = np.sqrt(((xy4[:, None] - xy4[None, :]) ** 2).sum(-1))
res = mantel(g4, g4)
print('  유전 거리 = 지리 거리(r = 1): r = %.3f, 한쪽 p = %.4f = 1/24, 양쪽 p = %.4f' % (res['r'], res['p_greater'], res['p_two']))
best = None
for seed in range(1, 400):
    rr = np.random.default_rng(seed)
    z = rr.normal(0, 0.9, (4, 4)); z = (z + z.T) / 2; np.fill_diagonal(z, 0)
    h = np.abs(g4 + z); np.fill_diagonal(h, 0)
    m = mantel(g4, h)
    if 0.69 < m['r'] < 0.73 and abs(m['p_greater'] - 1 / 24) < 1e-9:
        best = (seed, m, h); break
if best:
    seed, m, h = best
    print('  잡음을 섞은 시연(시드 %d, r = 0.69~0.73이고 P = 1/24가 되는 첫 시드를 찾음): r = %.3f, 한쪽 p = %.4f, 양쪽 p = %.4f' % (seed, m['r'], m['p_greater'], m['p_two']))
    print('  24가지 순열의 r(내림차순 위 8개): %s' % np.round(np.sort(m['rs'])[::-1][:8], 3))
    print('  (이 시연은 P = 1/24가 되는 값이 존재함을 보이려고 시드를 골랐다. 논문의 행렬이 아니다.)')
line = np.array([0.0, 1.0, 2.0, 3.0])
gl = np.abs(line[:, None] - line[None, :])
rl = mantel(gl, gl)
print('  지리가 일직선(0, 1, 2, 3)이면 순서를 뒤집어도 같은 행렬이라 r = 1인 순열이 2개다: 한쪽 p = %.4f = 2/24' % rl['p_greater'])

print('\n[4] 제1권과 같은 입력 표: 유적 사이 유전 거리 대 시간 차(표의 시기 구간 가운데 BP의 차). 제1권에 없는 이 책의 새 계산')
names = [r[0] for r in read_cui()]
E = np.loadtxt('cui-euclid-v1.tsv'); PS = np.loadtxt('cui-phist-v1.tsv'); T = np.loadtxt('cui-timediff-v1.tsv')
PS0 = np.clip(PS, 0, None)
for lab, M in (('빈도 벡터의 유클리드 거리', E), ('쌍별 Phi_ST(음수는 0)', PS0)):
    m6 = mantel(M, T)
    print('  여섯 유적, %s 대 시간 차: r = %.4f, 한쪽 p = %.4f, 양쪽 p = %.4f (순열 %d, %s; 관측 r 이상인 순열 %d개, |r| 이상 %d개)' % (lab, m6['r'], m6['p_greater'], m6['p_two'], m6['n_perm'], m6['mode'], int((m6['rs'] >= m6['r'] - 1e-12).sum()), int((np.abs(m6['rs']) >= abs(m6['r']) - 1e-12).sum())))
    sel = [0, 1, 2, 3]
    m4 = mantel(M[np.ix_(sel, sel)], T[np.ix_(sel, sel)])
    print('  서요하 네 유적,  %s 대 시간 차: r = %.4f, 한쪽 p = %.4f, 양쪽 p = %.4f (순열 %d, %s)' % (lab, m4['r'], m4['p_greater'], m4['p_two'], m4['n_perm'], m4['mode']))
print('  주의: 유적마다 시료가 3~12명이고, 금구자는 북방 유목 집단이라 시간만으로 설명되는 계통이 아니다.')

print('\n[5] 함정: 공간적으로 이어진 두 변수는 서로 무관해도 Mantel이 자주 유의하게 나오는가? (이 책의 모의)')
def fast_mantel_p(A, B, perms, rng):
    n = len(A)
    i, j = np.triu_indices(n, 1)
    a = A[i, j]; a = (a - a.mean()) / a.std()
    b = B[i, j]; b = (b - b.mean()) / b.std()
    r0 = (a * b).mean()
    cnt = 0
    for _ in range(perms):
        p = rng.permutation(n)
        bb = B[np.ix_(p, p)][i, j]
        rr = ((bb - bb.mean()) / bb.std() * a).mean()
        if abs(rr) >= abs(r0) - 1e-12:
            cnt += 1
    return (cnt + 1) / (perms + 1)
def sim(n, ell, both, S, perms, seed):
    rng = np.random.default_rng(seed)
    hit = 0
    for _ in range(S):
        xy = rng.uniform(0, 10, (n, 2))
        D = np.sqrt(((xy[:, None] - xy[None, :]) ** 2).sum(-1))
        K = np.exp(-D / ell)
        L = np.linalg.cholesky(K + 1e-9 * np.eye(n))
        x = L @ rng.standard_normal(n)
        y = (L @ rng.standard_normal(n)) if both else rng.standard_normal(n)
        A = np.abs(x[:, None] - x[None, :]); B = np.abs(y[:, None] - y[None, :])
        if fast_mantel_p(A, B, perms, rng) < 0.05:
            hit += 1
    return hit / S
S, perms, n = 1500, 199, 15
for lab, both in (('두 변수 모두 공간 자기상관(상관 길이 5)', True), ('한 변수만 공간 자기상관, 다른 변수는 독립 잡음', False)):
    rate = sim(n, 5.0, both, S, perms, 99)
    se = math.sqrt(0.05 * 0.95 / S)
    print('  %s: 점 %d개, 모의 %d회, 순열 %d회, 양쪽 p < 0.05인 비율 = %.3f (두 변수가 서로 무관하게 만들었으므로 0.05여야 한다. 참 비율이 0.05일 때 모의의 표준오차는 약 %.3f)' % (lab, n, S, perms, rate, se))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
