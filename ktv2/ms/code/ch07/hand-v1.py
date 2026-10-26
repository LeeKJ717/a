# -*- coding: utf-8 -*-
"""실습 7-3b, 7-4b, 7-5b, 7-6b, 7-11b. 손으로 따라 풀 수 있는 작은 자료로 각 계산의 중간 값을 모두 찍는다.
(가) Fisher 정확검정의 한 표 확률을 이항계수로 풀고, (나) 사람 8명의 AMOVA를 정의대로 풀어 gentools와 맞추고 순열 p를 전수로 구하고,
(다) 점 4개의 Mantel 검정에서 24개 순열의 r을 모두 늘어놓고, (라) 블록 5개의 잭나이프를 한 블록씩 빼며 풀어 gentools.wjack과 맞추고, (마) 7.4절의 거리 세 가지를 우하량과 합라해구 한 쌍에서 손으로 푼다.
모든 자료는 시연값이다.  사용: python hand-v1.py"""
import itertools, math, sys, time
import numpy as np
from math import comb
from gentools import amova, mantel, wjack, read_cui, individuals

t0 = time.time()
print('numpy', np.__version__, '| python', sys.version.split()[0])

print('\n[1] (가) [[16,2],[4,10]]의 표 확률을 이항계수로 푼다 (7.3절의 신석기 대 청동기)')
a, b, c, d = 16, 2, 4, 10
r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
tot = comb(n, c1)
print('  행의 합 r1 = %d, r2 = %d, 열의 합 c1 = %d, 총합 n = %d, C(n, c1) = C(%d, %d) = %d' % (r1, r2, c1, n, n, c1, tot))
ps = {}
for x in (6, 16, 17, 18):
    top = comb(r1, x) * comb(r2, c1 - x)
    ps[x] = top / tot
    print('  a = %2d: C(%d, %d) x C(%d, %d) = %d x %d = %d, 확률 = %d / %d = %.4e' % (x, r1, x, r2, c1 - x, comb(r1, x), comb(r2, c1 - x), top, top, tot, ps[x]))
print('  네 표의 확률 합 = %.4e (양쪽 p)' % sum(ps.values()))

print('\n[2] (나) 사람 8명의 AMOVA를 정의대로 푼다. 집단 1 = A A A B, 집단 2 = A B B B (시연값)')
hap = np.array([0, 0, 0, 1, 0, 1, 1, 1])
pop = np.array([0, 0, 0, 0, 1, 1, 1, 1])
N = len(hap)
D2 = (hap[:, None] != hap[None, :]).astype(float)
pairs_all = int(D2.sum() / 2)
print('  서로 다른 사람 쌍: 전체 %d쌍 (A 4명 x B 4명), 집단 1 안 %d쌍, 집단 2 안 %d쌍' % (pairs_all, int(D2[:4, :4].sum() / 2), int(D2[4:, 4:].sum() / 2)))
ssd_t = D2.sum() / (2 * N)
ssd_wp = sum(D2[np.ix_(pop == p, pop == p)].sum() / (2 * (pop == p).sum()) for p in (0, 1))
print('  SSD(전체) = (모든 순서쌍 거리의 합 %.0f) / (2 x %d) = %.4f' % (D2.sum(), N, ssd_t))
print('  SSD(집단 안) = 집단 1 %.4f + 집단 2 %.4f = %.4f' % tuple([D2[np.ix_(pop == 0, pop == 0)].sum() / 8, D2[np.ix_(pop == 1, pop == 1)].sum() / 8, ssd_wp]))
ssd_ap = ssd_t - ssd_wp
msd_ap, msd_wp = ssd_ap / 1, ssd_wp / (N - 2)
n0 = (N - (4 ** 2 + 4 ** 2) / N) / (2 - 1)
s2b = (msd_ap - msd_wp) / n0
print('  SSD(집단 사이) = %.4f - %.4f = %.4f, 자유도 1과 %d, 평균제곱 MSD(사이) = %.4f, MSD(안) = %.4f' % (ssd_t, ssd_wp, ssd_ap, N - 2, msd_ap, msd_wp))
print('  계수 n = (N - 집단 크기 제곱의 합/N)/(P - 1) = (%d - %.0f/%d)/1 = %.4f' % (N, 4 ** 2 + 4 ** 2, N, n0))
print('  분산 성분: 집단 사이 = (%.4f - %.4f)/%.4f = %.4f, 집단 안 = %.4f, Phi_ST = %.4f/(%.4f + %.4f) = %.4f' % (msd_ap, msd_wp, n0, s2b, msd_wp, s2b, s2b, msd_wp, s2b / (s2b + msd_wp)))
g = amova(D2, pop)
print('  gentools.amova: SSD 사이 %.4f, 안 %.4f, s2b %.4f, s2c %.4f, Phi_ST %.4f' % (g['ssd_ap'], g['ssd_wp'], g['s2b'], g['s2c'], g['phi_st']))
obs = g['phi_st']
cnt = tot_s = 0
for sel in itertools.combinations(range(N), 4):
    pp = np.ones(N, int)
    pp[list(sel)] = 0
    tot_s += 1
    if amova(D2, pp)['phi_st'] >= obs - 1e-12:
        cnt += 1
print('  정확한 순열 검정: 8명을 4명씩 두 집단으로 나누는 방법 C(8,4) = %d가지 중 Phi_ST가 관측 이상인 것 %d가지 -> p = %d/%d = %.4f' % (tot_s, cnt, cnt, tot_s, cnt / tot_s))
print('  (이름표만 서로 바뀐 나눔은 같은 값이라 관측한 나눔이 짝으로 두 번 센다. 가능한 가장 작은 p는 2/%d = %.4f)' % (tot_s, 2 / tot_s))

print('\n[3] (다) 점 4개의 Mantel 검정에서 24개 순열을 모두 늘어놓는다 (시연값)')
A = np.array([[0, 1, 3, 4], [1, 0, 2, 3], [3, 2, 0, 1], [4, 3, 1, 0]], float)
B = np.array([[0, 2, 4, 7], [2, 0, 3, 5], [4, 3, 0, 2], [7, 5, 2, 0]], float)
iu = np.triu_indices(4, 1)
print('  유전 거리 A의 윗삼각 6개(01 02 03 12 13 23 순) = %s' % A[iu])
print('  지리 거리 B의 윗삼각 6개 = %s' % B[iu])
r0 = np.corrcoef(A[iu], B[iu])[0, 1]
print('  관측 r = %.4f' % r0)
rows = []
for p in itertools.permutations(range(4)):
    Bp = B[np.ix_(p, p)]
    rows.append((p, np.corrcoef(A[iu], Bp[iu])[0, 1]))
for k, (p, rr) in enumerate(rows):
    print('    %2d. 순서 %s -> 섞은 B의 윗삼각 %s, r = %+.4f%s' % (k + 1, ''.join(map(str, p)), B[np.ix_(p, p)][iu], rr, ' <= 관측(항등 순열)' if p == (0, 1, 2, 3) else ''))
rs = np.array([rr for _, rr in rows])
print('  관측 r 이상인 순열 %d개 / 24 = %.4f, gentools.mantel: r = %.4f, 한쪽 p = %.4f, 양쪽 p = %.4f' % ((rs >= r0 - 1e-12).sum(), (rs >= r0 - 1e-12).mean(), mantel(A, B)['r'], mantel(A, B)['p_greater'], mantel(A, B)['p_two']))
print('  r의 서로 다른 값 %d개(대칭 때문에 같은 r이 반복된다), 가장 큰 값 %.4f가 나온 순열 %d개' % (len(set(np.round(rs, 10))), rs.max(), int((rs >= rs.max() - 1e-12).sum())))

print('\n[4] (라) 블록 5개의 잭나이프를 한 블록씩 빼며 푼다 (시연값). 추정량 = 분자 합 / 분모 합')
num = np.array([3.0, 5.0, 4.0, 6.0, 2.0])
den = np.array([10.0, 12.0, 11.0, 13.0, 9.0])
gb = len(num)
th = num.sum() / den.sum()
print('  블록별 분자 %s, 분모 %s, 전체 추정값 = %.0f/%.0f = %.5f' % (num, den, num.sum(), den.sum(), th))
loo = (num.sum() - num) / (den.sum() - den)
pv = gb * th - (gb - 1) * loo
print('  한 블록씩 뺀 추정값 = %s' % np.round(loo, 5))
print('  의사값(pseudo-value) = %d x 전체 - %d x 뺀 추정값 = %s' % (gb, gb - 1, np.round(pv, 5)))
se = math.sqrt(pv.var(ddof=1) / gb)
print('  의사값의 평균(잭나이프 추정값) = %.5f, 의사값의 표본 표준편차 = %.5f, SE = 표준편차/sqrt(%d) = %.5f' % (pv.mean(), pv.std(ddof=1), gb, se))
w = wjack(num, den, np.ones(gb))
print('  gentools.wjack(블록 크기 모두 같음): 추정값 %.5f, 잭나이프 추정값 %.5f, SE %.5f' % w)
w2 = wjack(num, den, np.array([1.0, 1.0, 2.0, 3.0, 3.0]))
print('  같은 분자와 분모에 블록 크기만 [1, 1, 2, 3, 3]으로 바꾸면(가중 잭나이프): 추정값 %.5f, 잭나이프 추정값 %.5f, SE %.5f' % w2)

print('\n[5] (마) 우하량과 합라해구 한 쌍에서 7.4절의 거리 세 가지를 손으로 푼다 (입력은 실습 7-1의 표)')
rows = read_cui()
x = np.array(rows[0][5], float) / rows[0][4]
y = np.array(rows[1][5], float) / rows[1][4]
print('  우하량 빈도 %s (n=%d), 합라해구 빈도 %s (n=%d)' % (np.round(x, 4), rows[0][4], np.round(y, 4), rows[1][4]))
dd = (x - y) ** 2
print('  유클리드: 칸마다 차의 제곱 %s, 합 %.4f, 제곱근 = %.4f' % (np.round(dd, 4), dd.sum(), math.sqrt(dd.sum())))
sxy, sxx, syy = (x * y).sum(), (x * x).sum(), (y * y).sum()
I = sxy / math.sqrt(sxx * syy)
print('  Nei: 합(xy) = %.4f, 합(xx) = %.4f, 합(yy) = %.4f, I = %.4f/sqrt(%.4f x %.4f) = %.4f, D = -ln I = %.4f' % (sxy, sxx, syy, sxy, sxx, syy, I, -math.log(I)))
hap2, pop2 = individuals([rows[0][5], rows[1][5]])
D2p = (hap2[:, None] != hap2[None, :]).astype(float)
gp = amova(D2p, pop2)
print('  Phi_ST: 사람 %d명(6 + 12). SSD 전체 %.4f, 집단 안 %.4f, 집단 사이 %.4f, 자유도 1과 %d, MSD 사이 %.4f, 안 %.4f, 계수 n = %.4f' % (gp['N'], gp['ssd_t'], gp['ssd_wp'], gp['ssd_ap'], gp['df_wp'], gp['msd_ap'], gp['msd_wp'], gp['n1']))
print('  s2b = (%.4f - %.4f)/%.4f = %.4f, s2c = %.4f, Phi_ST = %.4f/(%.4f + %.4f) = %.4f' % (gp['msd_ap'], gp['msd_wp'], gp['n1'], gp['s2b'], gp['s2c'], gp['s2b'], gp['s2b'], gp['s2c'], gp['phi_st']))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
