# -*- coding: utf-8 -*-
"""11장 실습 11-2: 순열 검정을 xp 방식으로 짜서 제1권 11장 계산 11-3(Fisher 정확검정)의 p와 맞대어 본다.
입력: 제1권 11장 계산 11-3의 세 표 (행 = 신석기 합 / 비교 집단, 열 = N1(x) 있음 / 없음).
  [[16,2],[4,10]] 신석기 대 청동기(대전자+대산전), p = 0.00079 (제1권)
  [[16,2],[3,2]]  신석기 대 대전자, p = 0.19368
  [[16,2],[1,8]]  신석기 대 대산전, p = 0.00017
순열 검정: 전체 n명의 표지(N1(x) 있음 1, 없음 0)를 섞어 첫 집단 크기만큼 뽑고, 그 안의 1의 개수가 만드는 분포를 본다.
양쪽 p는 Fisher와 같은 규칙(관측 표보다 확률이 같거나 낮은 표를 모두 더함)으로 센다.
추가: 4개 집단의 이름표 바꾸기(4! = 24가지)에서 나올 수 있는 가장 작은 p (제1권 11장 계산 11-12).
사용: python p02-perm-fisher-v1.py --xp numpy|cupy|auto [--seed 11]"""
import argparse, importlib.util, itertools, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'mc-core-v1.py'))
mc = importlib.util.module_from_spec(_s); _s.loader.exec_module(mc)
from scipy import stats

ap = argparse.ArgumentParser()
ap.add_argument('--xp', default='numpy'); ap.add_argument('--seed', type=int, default=11)
ap.add_argument('--chunk', type=int, default=100000); ap.add_argument('--nmax', type=int, default=4000000)
a = ap.parse_args()
xp = mc.choose_xp(a.xp)
print('백엔드:', xp.__name__, '| numpy', np.__version__, '| 시드', a.seed)
TABLES = [('신석기 대 청동기', 16, 2, 4, 10, 0.00079), ('신석기 대 대전자', 16, 2, 3, 2, 0.19368), ('신석기 대 대산전', 16, 2, 1, 8, 0.00017)]
Ns = [n for n in (10000, 100000, 1000000, 4000000) if n <= a.nmax]
rec = []
for name, A, Bc, C, D, vol1 in TABLES:
    n = A + Bc + C + D; n1 = A + Bc
    labels = [1] * (A + C) + [0] * (Bc + D)
    xs, ps = mc.hyp_pmf(A, Bc, C, D)
    pmf = dict(zip(xs, ps)); p0 = pmf[A]
    pex = mc.fisher_two_sided_exact(A, Bc, C, D)
    psc = stats.fisher_exact([[A, Bc], [C, D]])[1]
    print('\n== %s [[%d,%d],[%d,%d]] n=%d  정확 p = %.6f (scipy %.6f, 제1권 %.5f)' % (name, A, Bc, C, D, n, pex, psc, vol1))
    print('%10s %12s %10s %14s %12s %8s' % ('N', 'p̂ (k/N)', '표준오차', '(k+1)/(N+1)', '정확과의 차', '초'))
    for N in Ns:
        rng = mc.make_rng(xp, a.seed)
        t = time.perf_counter()
        cnt = mc.perm_group1_counts(xp, labels, n1, N, rng, a.chunk)
        cnt = mc.to_host(xp, cnt)
        dt = time.perf_counter() - t
        # 개수별 빈도 -> 양쪽 p
        freq = np.bincount(cnt, minlength=max(xs) + 1)
        k = sum(freq[x] for x in xs if pmf[x] <= p0 * (1 + 1e-9))
        ph = k / N; se = math.sqrt(max(pex * (1 - pex), 1e-12) / N)
        print('%10d %12.6f %10.6f %14.6f %+12.6f %8.2f   (k=%d, 차이/표준오차 %+.2f)' % (N, ph, se, (k + 1) / (N + 1), ph - pex, dt, k, (ph - pex) / se))
        r = {'table': name, 'A': A, 'B': Bc, 'C': C, 'D': D, 'N': N, 'k': int(k), 'p_hat': ph, 'p_exact': pex, 'se': se, 'seconds': dt,
             'seed': a.seed, 'backend': xp.__name__}
        if N == 1000000:
            r['freq'] = {int(x): int(freq[x]) for x in xs}; r['pmf'] = {int(x): pmf[x] for x in xs}
        rec.append(r)
# 4! = 24
print('\n== 이름표 4개: 가능한 순열 4! = 24, 관측 배열이 가장 극단적일 때')
x = np.array([1., 2., 3., 4.]); y = np.array([1., 2., 3., 4.])
allr = [np.corrcoef(x, y[list(p)])[0, 1] for p in itertools.permutations(range(4))]
r0 = np.corrcoef(x, y)[0, 1]
k_ex = sum(1 for r in allr if r >= r0 - 1e-12)
print('정확 계산(24가지 전부): r_obs = %.3f, r >= r_obs 인 순열 %d개, 한쪽 p = %d/24 = %.4f' % (r0, k_ex, k_ex, k_ex / 24))
yx = xp.asarray(y)
for N in (10000, 1000000):
    rng = mc.make_rng(xp, a.seed)
    keys = rng.random((N, 4)); perm = xp.argsort(keys, axis=1)
    yy = yx[perm]; xc = xp.asarray(x - x.mean())
    yc = yy - yy.mean(axis=1, keepdims=True)
    r = (yc * xc[None, :]).sum(axis=1) / xp.sqrt((yc * yc).sum(axis=1) * float((xc * xc).sum()))
    k = int(mc.to_host(xp, (r >= r0 - 1e-9).sum()))
    print('순열 검정 N=%8d: k = %d, p̂ = %.4f (정확 0.0417), 표준오차 %.4f' % (N, k, k / N, math.sqrt(1 / 24 * 23 / 24 / N)))
    rec.append({'table': 'perm24', 'N': N, 'k': k, 'p_hat': k / N, 'p_exact': 1 / 24, 'seed': a.seed, 'backend': xp.__name__})
with open(os.path.join(HERE, 'p02-perm-fisher.jsonl'), 'w', encoding='utf-8') as f:
    for r in rec: f.write(json.dumps(r, ensure_ascii=False) + '\n')
