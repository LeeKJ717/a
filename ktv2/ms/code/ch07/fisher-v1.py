# -*- coding: utf-8 -*-
"""실습 7-3. Fisher 정확검정을 직접 구현해 scipy와 맞추고, 제1권 11장의 세 비교와 맞춘 뒤,
같은 입력 표에서 제1권에 없던 비교(네 유적 쌍별 6개 + Holm 보정, 6 x 5 전체 표)를 해 본다.
사용: python fisher-v1.py"""
import sys, time
import numpy as np
import scipy
from scipy import stats
from gentools import fisher_2x2, fisher_rxc_mc, holm, read_cui, HG

t0 = time.time()
print('numpy', np.__version__, '| scipy', scipy.__version__, '| python', sys.version.split()[0])
print('\n[1] 검증: 위키백과 예(청소년 24명) [[1,9],[11,3]]')
p, o, pr = fisher_2x2(1, 9, 11, 3, 'less')
print('  한쪽 p = %.9f (위키백과 0.001379728)' % p)
print('  표 자신의 확률 %.9f (위키 0.001346076), [[0,10],[12,2]]의 확률 %.9f (위키 0.000033652)' % (pr[1], pr[0]))

print('\n[2] 제1권 11장 계산 11-3의 세 비교')
V1 = [('신석기 대 청동기(대전자+대산전)', (16, 2, 4, 10), 0.00079, 20.0),
      ('신석기 대 대전자(하가점하층)', (16, 2, 3, 2), 0.194, 5.3),
      ('신석기 대 대산전(하가점상층)', (16, 2, 1, 8), 0.00017, 64.0)]
for nm, t, pv1, ov1 in V1:
    p, o, _ = fisher_2x2(*t)
    ps = stats.fisher_exact([[t[0], t[1]], [t[2], t[3]]])
    print('  %-28s %s  이 책 p=%.5f 오즈비=%.1f | scipy p=%.5f 오즈비=%.1f | 제1권 p=%s 오즈비=%s' % (nm, list(t), p, o, ps[1], ps[0], pv1, ov1))
chi = stats.chi2_contingency([[16, 2], [4, 10]], correction=False)
print('  같은 [[16,2],[4,10]]의 카이제곱(보정 없음) = %.3f, p = %.5f, 기대도수 최소 = %.2f (제1권 12.224, 0.00047, 5.25)' % (chi[0], chi[1], chi[3].min()))

print('\n[3] [[16,2],[4,10]]의 13개 표(a = 첫 칸)와 확률')
p, o, pr = fisher_2x2(16, 2, 4, 10)
for a in sorted(pr):
    print('  a = %2d  확률 %.3e %s' % (a, pr[a], '<= 관측' if pr[a] <= pr[16] * (1 + 1e-9) else ''))
print('  확률 합 = %.6f, 양쪽 p = %.3e, 한쪽(a 큰 쪽) p = %.3e' % (sum(pr.values()), p, fisher_2x2(16, 2, 4, 10, 'greater')[0]))

print('\n[4] 이 책의 새 계산(제1권에 없음): 서요하 네 유적에서 N1(x)인가 아닌가, 쌍별 Fisher 6개')
rows = read_cui()[:4]
names = [r[0] for r in rows]
pv, lab = [], []
for i in range(4):
    for j in range(i + 1, 4):
        a, b = rows[i][5][0], rows[i][4] - rows[i][5][0]
        c, d = rows[j][5][0], rows[j][4] - rows[j][5][0]
        p, o, _ = fisher_2x2(a, b, c, d)
        pv.append(p); lab.append((names[i], names[j], (a, b, c, d), o))
adj = holm(np.array(pv))
for (x, y, t, o), p, q in zip(lab, pv, adj):
    print('  %-4s 대 %-4s %-18s p = %.4g  Holm 보정 p = %.4g  오즈비 %s' % (x, y, list(t), p, q, '%.2f' % o if o != float('inf') else '무한대(0칸)'))
print('  6개 가운데 p < 0.05: %d개, Holm 보정 후 p < 0.05: %d개' % (sum(1 for p in pv if p < 0.05), sum(1 for q in adj if q < 0.05)))

print('\n[5] 4 x 2 표(네 유적 x [N1(x), 그 밖])의 전체 검정과 6 x 5 표(여섯 유적 x 하플로그룹 5개), Monte Carlo(B=100000, 시드 1)')
T42 = np.array([[r[5][0], r[4] - r[5][0]] for r in rows])
print('  4 x 2 표 =', T42.tolist(), ' Freeman-Halton MC p = %.6f (B=100000이므로 가능한 가장 작은 값은 1/100001 = %.6f)' % (fisher_rxc_mc(T42, 100000, 1), 1 / 100001))
T65 = np.array([r[5] for r in read_cui()])
print('  6 x 5 표 =', T65.tolist())
print('  Freeman-Halton MC p = %.6f (가능한 가장 작은 값 %.6f이므로 "p < 1e-5 수준"이라는 뜻이며 값 자체는 정해지지 않는다)' % (fisher_rxc_mc(T65, 100000, 1), 1 / 100001))
chi = stats.chi2_contingency(T65[:, T65.sum(0) > 0], correction=False)
print('  같은 표의 카이제곱 = %.2f (자유도 %d), 근사 p = %.2e, 기대도수가 5 미만인 칸 %d/%d' % (chi[0], chi[2], chi[1], (chi[3] < 5).sum(), chi[3].size))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
