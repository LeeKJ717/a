# -*- coding: utf-8 -*-
"""실습 7-5. AMOVA를 직접 구현(gentools.amova)해 (가) 1차원 값에서 분산분석과 같은지, (나) 제1권 시연값 Va=2, Vb=3, Vc=15를
되찾는지(불편성 모의), (다) scikit-bio의 PERMANOVA와 F가 같은지 확인하고, (라) 제1권 11장 표 2의 Phi 산술을 되풀이한 뒤,
(마) 제1권과 같은 입력 표(Cui 등 2013 표 1)에 AMOVA를 적용한다.  사용: python amova-v1.py"""
import sys, time
import numpy as np
import scipy
from scipy import stats
from gentools import amova, amova_perm, individuals, read_cui, phi_from_percent

t0 = time.time()
print('numpy', np.__version__, '| scipy', scipy.__version__, '| python', sys.version.split()[0])

print('\n[1] 검증 (가): 값이 1차원 수이고 거리가 (x_i - x_j)^2이면 AMOVA는 일원 분산분석이다')
rng = np.random.default_rng(7)
sizes = [5, 8, 3, 6]
x = np.concatenate([rng.normal(m, 1.0, s) for m, s in zip([0.0, 0.8, -0.5, 0.3], sizes)])
pop = np.repeat(np.arange(4), sizes)
D2 = (x[:, None] - x[None, :]) ** 2
a = amova(D2, pop)
grp_vals = [x[pop == g] for g in range(4)]
F, pF = stats.f_oneway(*grp_vals)
N, P = len(x), 4
gm = x.mean()
ssb = sum(len(v) * (v.mean() - gm) ** 2 for v in grp_vals)
ssw = sum(((v - v.mean()) ** 2).sum() for v in grp_vals)
msb, msw = ssb / (P - 1), ssw / (N - P)
n0 = (N - sum(len(v) ** 2 for v in grp_vals) / N) / (P - 1)
print('  표본 크기 %s (시연값, 시드 7)' % sizes)
print('  AMOVA: SSD 집단 사이 %.6f, 집단 안 %.6f, 분산 성분 s2a = %.6f, s2c = %.6f' % (a['ssd_ap'], a['ssd_wp'], a['s2b'], a['s2c']))
print('  분산분석: SSB %.6f, SSW %.6f, (MSB-MSW)/n0 = %.6f, MSW = %.6f, n0 = %.6f (AMOVA n = %.6f)' % (ssb, ssw, (msb - msw) / n0, msw, n0, a['n1']))
print('  F = MSB/MSW: scipy %.6f, AMOVA %.6f' % (F, a['msd_ap'] / a['msd_wp']))
print('  최대 절대 차 = %.2e' % max(abs(a['ssd_ap'] - ssb), abs(a['ssd_wp'] - ssw), abs(a['s2b'] - (msb - msw) / n0), abs(a['s2c'] - msw)))

print('\n[2] 검증 (나): 이단 AMOVA의 불편성 모의. 참 분산 성분 Va=2, Vb=3, Vc=15(제1권 11.4.1절 시연값)')
va, vb, vc = 2.0, 3.0, 15.0
design = [[3, 4, 2], [5, 2], [6, 3, 4]]            # 묶음 3개, 집단 7개, 집단별 개체 수(불균형)
pop2, grp2 = [], []
pid = 0
for g, pops in enumerate(design):
    for s in pops:
        pop2 += [pid] * s; grp2 += [g] * s; pid += 1
pop2, grp2 = np.array(pop2), np.array(grp2)
Nn = len(pop2)
R = 4000
est = np.empty((R, 3))
rng = np.random.default_rng(2026)
for r in range(R):
    ag = rng.normal(0, np.sqrt(va), 3)[grp2]
    bp = rng.normal(0, np.sqrt(vb), pid)[pop2]
    xx = ag + bp + rng.normal(0, np.sqrt(vc), Nn)
    out = amova((xx[:, None] - xx[None, :]) ** 2, pop2, grp2)
    est[r] = [out['s2a'], out['s2b'], out['s2c']]
print('  개체 %d, 집단 %d, 묶음 3, 반복 %d회(시드 2026)' % (Nn, pid, R))
for nm, tv, e in zip(['Va', 'Vb', 'Vc'], [va, vb, vc], est.T):
    print('  %s: 참 %.1f, 추정의 평균 %.3f, 평균의 표준오차 %.3f, (평균-참)/SE = %+.2f' % (nm, tv, e.mean(), e.std(ddof=1) / np.sqrt(R), (e.mean() - tv) / (e.std(ddof=1) / np.sqrt(R))))
print('  추정이 음수가 된 비율: Va %.3f, Vb %.3f, Vc %.3f' % tuple((est < 0).mean(0)))
print('  제1권 시연: Va=2, Vb=3, Vc=15 -> Phi_CT = %.3f, Phi_SC = %.4f, Phi_ST = %.3f' % (2 / 20, 3 / 18, 5 / 20))

print('\n[3] 검증 (다): scikit-bio PERMANOVA의 pseudo-F와 순열 p (일원, 0/1 거리가 아닌 1차원 자료 [1]의 x)')
try:
    import skbio
    from skbio import DistanceMatrix
    from skbio.stats.distance import permanova
    D = np.sqrt(D2)
    dm = DistanceMatrix(D, ids=[str(i) for i in range(N)])
    res = permanova(dm, grouping=[str(g) for g in pop], permutations=9999, seed=1)
    print('  scikit-bio', skbio.__version__, ': 검정통계량 %.6f, p = %.4f (순열 9999)' % (res['test statistic'], res['p-value']))
    obs, pp = amova_perm(D2, pop, None, B=9999, seed=1)
    print('  이 책 AMOVA: F = MSD_AP/MSD_WP = %.6f, Phi_ST = %.4f, 순열 p = %.4f (순열 9999)' % (obs['msd_ap'] / obs['msd_wp'], obs['phi_st'], pp['phi_st']))
except Exception as e:
    print('  scikit-bio를 불러오지 못함:', repr(e))

print('\n[4] 제1권 11.4.1절(계산 11-12): Duggan 등(2013) 표 2의 분산 몫(%)에서 Phi 통계')
T2 = [('4 지리집단', 4.01, 6.29, 89.71, (0.0401, 0.0655, 0.1030)), ('6 언어집단', 6.66, 4.54, 88.80, (0.0666, 0.0486, 0.1120)),
      ('북·남 퉁구스', 5.67, 6.77, 87.55, (0.0567, 0.0718, 0.1244)), ('에벤키 대 에벤', -0.21, 7.16, 93.05, None)]
for nm, pa, pb, pc, v1 in T2:
    f = phi_from_percent(pa, pb, pc)
    print('  %-12s 합 %.2f | Phi_CT %.4f Phi_SC %.4f Phi_ST %.4f | 1-(1-CT)(1-SC) = %.4f | 제1권 %s' % (nm, pa + pb + pc, f['phi_ct'], f['phi_sc'], f['phi_st'], f['identity'], v1))
print('  주의: 합이 100이 아닌 반올림 오차(100.01, 99.99)를 분모에 그대로 쓰면 제1권의 값(분모 100)과 끝자리가 달라질 수 있다 -> 분모를 100으로 두고 다시 계산:')
for nm, pa, pb, pc, v1 in T2[:3]:
    print('  %-12s Phi_CT %.4f Phi_SC %.4f Phi_ST %.4f' % (nm, pa / 100, pb / (pb + pc), (pa + pb) / 100))

print('\n[5] 제1권과 같은 입력 표(Cui 등 2013 표 1)에 AMOVA를 적용(제1권에 없는 이 책의 새 계산). 하플로그룹이 같으면 0, 다르면 1')
rows = read_cui()
def run(label, idx, grp_of_site=None, B=9999):
    sub = [rows[i] for i in idx]
    hap, popi = individuals([r[5] for r in sub])
    D2h = (hap[:, None] != hap[None, :]).astype(float)
    grp = None if grp_of_site is None else np.array([grp_of_site[popi[i]] for i in range(len(popi))])
    obs, pv = amova_perm(D2h, popi, grp, B=B, seed=1)
    print('\n  <%s> 개체 %d, 집단 %d, 묶음 %d' % (label, obs['N'], obs['P'], obs['G']))
    print('    SSD: 묶음 사이 %.4f, 묶음 안 집단 사이 %.4f, 집단 안 %.4f, 합 %.4f | 자유도 %d, %d, %d' % (obs['ssd_ag'], obs['ssd_ap'], obs['ssd_wp'], obs['ssd_t'], obs['df_ag'], obs['df_ap'], obs['df_wp']))
    print('    분산 성분: 묶음 사이 %.4f, 집단 사이 %.4f, 집단 안 %.4f | 몫(%%) %.2f, %.2f, %.2f' % (obs['s2a'], obs['s2b'], obs['s2c'], obs['pct_a'], obs['pct_b'], obs['pct_c']))
    print('    Phi_ST = %.4f (p = %.4f)' % (obs['phi_st'], pv['phi_st']) + ('' if obs['G'] == 1 else ', Phi_SC = %.4f (p = %.4f), Phi_CT = %.4f (p = %.4f)' % (obs['phi_sc'], pv['phi_sc'], obs['phi_ct'], pv['phi_ct'])))
    return obs, pv
run('서요하 네 유적, 묶음 없음', [0, 1, 2, 3])
run('서요하 네 유적, 신석기(우하량, 합라해구) 대 청동기(대전자, 대산전)', [0, 1, 2, 3], {0: 0, 1: 0, 2: 1, 3: 1})
run('여섯 유적 전체, 묶음 없음', [0, 1, 2, 3, 4, 5])
sub = rows[:4]
hap, popi = individuals([r[5] for r in sub])
D2h = (hap[:, None] != hap[None, :]).astype(float)
parts = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
phis = []
for A, Bp in parts:
    gmap = {p: 0 for p in A}; gmap.update({p: 1 for p in Bp})
    phis.append(amova(D2h, popi, np.array([gmap[p] for p in popi]))['phi_ct'])
obs_ct = phis[0]
print('\n  Phi_CT의 정확한 순열 검정(집단 4개를 2+2로 나누는 3가지를 모두 계산): ' + ', '.join('{%s | %s} -> %.4f' % (', '.join(sub[i][0] for i in A), ', '.join(sub[i][0] for i in Bp), v) for (A, Bp), v in zip(parts, phis)))
print('  관측 나눔 {우하량, 합라해구} 대 {대전자, 대산전}의 Phi_CT = %.4f는 3가지 중 가장 큰가: %s -> 정확 p = %d/3 = %.4f' % (obs_ct, obs_ct >= max(phis) - 1e-12, sum(1 for v in phis if v >= obs_ct - 1e-12), sum(1 for v in phis if v >= obs_ct - 1e-12) / 3))
from math import comb
print('  묶음 두 개로 집단 4개를 2+2로 나누는 서로 다른 방법 = %d, 관측과 같은 나눔이 가장 극단적이어도 p >= 1/%d = %.3f(이름표 바꿈 3가지 중 하나)' % (comb(4, 2) // 2, comb(4, 2) // 2, 1 / (comb(4, 2) // 2)))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
