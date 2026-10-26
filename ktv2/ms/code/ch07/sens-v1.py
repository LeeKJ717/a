# -*- coding: utf-8 -*-
"""실습 7-5c. 표본이 작을 때 Phi_ST가 얼마나 흔들리는가(제1권에 없는 이 책의 새 계산).
Cui 등(2013) 표 1(제1권 11장의 재구성)의 여섯 유적에서 (가) 한 유적씩 빼고 Phi_ST를 다시 구하고, (나) 한 사람씩 빼고 구하고,
(다) 각 유적 안에서 사람을 다중항으로 다시 뽑아(부트스트랩) Phi_ST의 분포를 구한다. 사용: python sens-v1.py"""
import sys, time
import numpy as np
from gentools import amova, individuals, read_cui

t0 = time.time()
print('numpy', np.__version__, '| python', sys.version.split()[0])
rows = read_cui()
names = [r[0] for r in rows]
cnt = [r[5] for r in rows]

def phi(counts):
    hap, pop = individuals(counts)
    D2 = (hap[:, None] != hap[None, :]).astype(float)
    return amova(D2, pop)['phi_st']

print('\n[1] 전체: 여섯 유적, 하플로그룹이 같으면 0, 다르면 1')
base = phi(cnt)
print('  Phi_ST = %.4f (실습 7-5와 같다)' % base)
print('\n[2] (가) 한 유적씩 빼고 다시 계산')
for i, nm in enumerate(names):
    sub = [c for j, c in enumerate(cnt) if j != i]
    print('  %s(n=%d)를 뺀 Phi_ST = %.4f (전체와의 차 %+.4f)' % (nm, sum(cnt[i]), phi(sub), phi(sub) - base))
print('\n[3] (나) 한 사람씩 빼고 다시 계산(47명)')
vals = []
for i, c in enumerate(cnt):
    for h, k in enumerate(c):
        if k == 0:
            continue
        c2 = [list(x) for x in cnt]
        c2[i][h] -= 1
        vals += [phi(c2)] * k
vals = np.array(vals)
print('  뺀 사람 %d명의 Phi_ST: 최솟값 %.4f, 최댓값 %.4f, 평균 %.4f' % (len(vals), vals.min(), vals.max(), vals.mean()))
print('\n[4] (다) 유적 안에서 사람을 다중항으로 다시 뽑는 부트스트랩(2000회, 시드 1)')
rng = np.random.default_rng(1)
out = []
for _ in range(2000):
    c2 = [list(rng.multinomial(sum(c), np.array(c) / sum(c))) for c in cnt]
    v = phi(c2)
    if not np.isnan(v):
        out.append(v)
out = np.array(out)
q = np.percentile(out, [2.5, 50, 97.5])
print('  유효한 반복 %d회. Phi_ST의 2.5%%, 중앙, 97.5%% = %.4f, %.4f, %.4f (관측 %.4f)' % (len(out), q[0], q[1], q[2], base))
print('  서요하 네 유적만(같은 절차):')
cnt4 = cnt[:4]
b4 = phi(cnt4)
out4 = []
for _ in range(2000):
    c2 = [list(rng.multinomial(sum(c), np.array(c) / sum(c))) for c in cnt4]
    v = phi(c2)
    if not np.isnan(v):
        out4.append(v)
q4 = np.percentile(out4, [2.5, 50, 97.5])
print('  관측 %.4f, 유효한 반복 %d회, 2.5%%, 중앙, 97.5%% = %.4f, %.4f, %.4f' % (b4, len(out4), q4[0], q4[1], q4[2]))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
