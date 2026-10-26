# -*- coding: utf-8 -*-
"""실습 9-1~9-4. 화산 유리 주성분 산화물의 대비: 닫힘, 유사 계수, 거리, 판별.
이 스크립트의 모든 조성은 시연값(이 책이 난수로 만든 가상 자료)이다. 실제 어느 화산의 조성이 아니다.
제1권 4장에는 주성분 분석값이 없다(McLean 등과 Lee 등이 분석했다고만 쓰고 표는 읽지 못했다).
실행: python3 ex1-oxides.py > ex1-oxides.log"""
import os, sys, json, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy
from scipy import stats
import tephralib as T

print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
OX = ['SiO2', 'TiO2', 'Al2O3', 'FeO', 'MnO', 'MgO', 'CaO', 'Na2O', 'K2O']
D = len(OX)
# 시연값: 원천별 평균(질량 %)과 파편 사이 표준편차(질량 %). 분석 오차와 원천 안의 변동을 합친 값으로 가정.
MEAN = {
    'A': [74.0, 0.25, 12.9, 2.6, 0.10, 0.05, 0.40, 4.4, 4.6],
    'B': [64.5, 0.50, 15.5, 5.3, 0.20, 0.20, 1.20, 6.3, 6.0],
    'C': [70.0, 0.35, 14.0, 3.4, 0.12, 0.30, 1.60, 4.0, 3.8],
    'D': [72.0, 0.30, 13.6, 2.9, 0.09, 0.12, 0.90, 4.3, 4.4],
}
SD = np.array([0.55, 0.04, 0.25, 0.20, 0.025, 0.03, 0.10, 0.22, 0.20])
rng = np.random.default_rng(20261026)

def gen(name, n):
    comp = np.array(MEAN[name]) + rng.normal(0, 1, (n, D)) * SD
    comp = np.clip(comp, 0.01, None)
    comp = comp / comp.sum(axis=1, keepdims=True) * 100.0          # 참 조성은 합 100
    f = np.clip(rng.normal(0.965, 0.025, n), 0.88, 1.0)             # 분석 합계(수화, 분석 손실)를 흉내 낸 배율
    return comp * f[:, None]

print('\n[입력] 시연값 원천 평균(질량 %%), 산화물 %s' % OX)
for k, v in MEAN.items():
    print('  원천 %s: %s  (합 %.2f)' % (k, ' '.join('%6.2f' % x for x in v), sum(v)))
print('  파편 사이 표준편차(가정):', ' '.join('%.3f' % x for x in SD))

REF_N = 40
raw = {k: gen(k, REF_N) for k in 'ABC'}
UNK = {'X층': gen('A', 24), 'Y층': gen('C', 24),
       'Z층': np.vstack([gen('A', 12), gen('B', 12)]), 'W층': gen('D', 24)}
TRUE = {'X층': '원천 A 24개', 'Y층': '원천 C 24개', 'Z층': '원천 A 12개 + 원천 B 12개', 'W층': '원천 D 24개 (기준 집단에 없음)'}

print('\n[실습 9-1] 닫힘: 합계 93% 미만 제외, 나머지를 100%로')
clo, ref_tot = {}, {}
for k, X in list(raw.items()) + list(UNK.items()):
    c, keep, tot = T.close100(X)
    clo[k] = c
    print('  %-4s 분석 %2d개, 합계 범위 %.1f~%.1f, 93%% 미만 제외 %d개, 남음 %d개' % (k, len(X), tot.min(), tot.max(), (~keep).sum(), keep.sum()))
print('  (닫은 뒤 모든 행의 합계 범위: %.6f~%.6f)' % (min(c.sum(axis=1).min() for c in clo.values()), max(c.sum(axis=1).max() for c in clo.values())))

print('\n[기준 집단의 닫힌 평균(질량 %)]')
print('  %-3s ' % '' + ' '.join('%7s' % o for o in OX))
for k in 'ABC':
    print('  %-3s ' % k + ' '.join('%7.3f' % x for x in clo[k].mean(axis=0)))

print('\n[실습 9-2] 유사 계수 SC(파편 대 집단 평균)의 분포: 같은 원천 안과 다른 원천 사이')
mus = {k: clo[k].mean(axis=0) for k in 'ABC'}
def sc_rows(Z, mu):
    return np.array([T.sim_coef(z, mu) for z in Z])
rows_sc = {}
for g in 'ABC':
    for h in 'ABC':
        s = sc_rows(clo[g], mus[h])
        rows_sc[(g, h)] = s
        print('  파편 %s 대 평균 %s: 중앙값 %.4f, 범위 %.4f~%.4f' % (g, h, np.median(s), s.min(), s.max()))
print('  집단 평균끼리의 SC: ' + ', '.join('%s-%s %.4f' % (a, b, T.sim_coef(mus[a], mus[b])) for a, b in (('A', 'B'), ('A', 'C'), ('B', 'C'))))

print('\n[실습 9-2b] 유사 계수와 유클리드 거리에서 산화물마다 얼마씩 기여하는가')
rat = np.mean(np.minimum(clo['A'], mus['A']) / np.maximum(clo['A'], mus['A']), axis=0)
print('  원천 A 파편 대 원천 A 평균: 산화물별 min/max 평균 (SC는 이 아홉 값의 평균)')
print('  ' + ' '.join('%7s' % o for o in OX)); print('  ' + ' '.join('%7.4f' % v for v in rat) + '   → SC = %.4f' % rat.mean())
dd = (clo['X층'].mean(axis=0) - mus['C']) ** 2
print('  X층 평균 대 원천 C 평균: 산화물별 제곱 차이가 유클리드 제곱 거리에서 차지하는 몫')
print('  ' + ' '.join('%7s' % o for o in OX)); print('  ' + ' '.join('%7.4f' % v for v in dd / dd.sum()) + '   (합 %.4f)' % (dd / dd.sum()).sum())
print('\n[실습 9-3] 층 평균 대 기준 집단 평균: 유사 계수, 유클리드 거리, 에이치슨 거리')
print('  유클리드 = 산화물 질량 %의 직선 거리. 에이치슨 = clr 좌표의 직선 거리(비율 기준).')
ZR = {k: T.ilr(clo[k]) for k in clo}
tab = []
print('  %-4s %-3s %8s %10s %10s' % ('층', '집단', 'SC', '유클리드', '에이치슨'))
for u in UNK:
    mu_u = clo[u].mean(axis=0)
    gm_u = np.exp(np.log(clo[u]).mean(axis=0))      # 기하 평균(에이치슨 거리용)
    for g in 'ABC':
        gm_g = np.exp(np.log(clo[g]).mean(axis=0))
        sc = T.sim_coef(mu_u, mus[g]); eu = float(np.linalg.norm(mu_u - mus[g])); ai = T.aitchison(gm_u, gm_g)
        tab.append((u, g, sc, eu, ai))
        print('  %-4s %-3s %8.4f %10.3f %10.4f' % (u, g, sc, eu, ai))
# 닫힘이 유클리드와 에이치슨 순서를 바꾸는가
print('  각 층에서 가장 가까운 집단: ' + '; '.join('%s: SC=%s, 유클리드=%s, 에이치슨=%s' % (u,
      max([t for t in tab if t[0] == u], key=lambda t: t[2])[1],
      min([t for t in tab if t[0] == u], key=lambda t: t[3])[1],
      min([t for t in tab if t[0] == u], key=lambda t: t[4])[1]) for u in UNK))

print('\n[실습 9-4a] 두 표본 평균이 같은가: 호텔링 T2 (ilr 좌표, p=%d)' % (D - 1))
HT = {}
print('  %-4s %-3s %8s %8s %12s %4s %4s' % ('층', '집단', 'T2', 'F', 'p값', 'n1', 'n2'))
for u in UNK:
    for g in 'ABC':
        T2, F, pv, p, n1, n2 = T.hotelling2(ZR[u], ZR[g])
        HT[(u, g)] = pv
        print('  %-4s %-3s %8.2f %8.3f %12.3e %4d %4d' % (u, g, T2, F, pv, n1, n2))

print('\n[실습 9-4b] 선형 판별(LDA): 기준 집단 A, B, C로 학습, 층의 파편을 하나씩 배정')
refZ = [ZR[g] for g in 'ABC']
model = T.lda_fit(refZ)
# 기준 집단 안의 한 개 빼기 교차 검증
conf = np.zeros((3, 3), int)
for gi, g in enumerate('ABC'):
    for i in range(len(refZ[gi])):
        trn = [np.delete(refZ[j], i, axis=0) if j == gi else refZ[j] for j in range(3)]
        m = T.lda_fit(trn)
        P, _ = T.lda_post(refZ[gi][i], m)
        conf[gi, int(np.argmax(P))] += 1
print('  한 개 빼기 교차 검증(행=참, 열=배정 A B C):')
for gi, g in enumerate('ABC'):
    print('    참 %s: %s' % (g, ' '.join('%3d' % c for c in conf[gi])))
print('  정확도 %d / %d = %.3f' % (np.trace(conf), conf.sum(), np.trace(conf) / conf.sum()))
chi_crit = stats.chi2.ppf(0.99, D - 1)
NU = sum(len(g) for g in refZ) - len(refZ)            # 합친 공분산의 자유도
pD = D - 1
def hot_thr(ng):
    """새 관측 하나가 같은 정규분포에서 나왔다면 D2 는 (1+1/n_g) p nu/(nu-p+1) F(p, nu-p+1) 를 따른다(호텔링 꼴)."""
    return (1 + 1.0 / ng) * pD * NU / (NU - pD + 1) * stats.f.ppf(0.99, pD, NU - pD + 1)
print('  (가) 단순 기준: D2 > chi2(df=%d)의 99%% 한계 %.2f 이면 "어느 집단에도 안 맞음"' % (pD, chi_crit))
print('  (나) 보정 기준: 평균과 공분산을 표본에서 추정한 효과를 넣은 한계(집단 A %.2f, B %.2f, C %.2f; 합친 자유도 %d)' % (hot_thr(len(refZ[0])), hot_thr(len(refZ[1])), hot_thr(len(refZ[2])), NU))
own = [(g.mean(axis=0), np.cov(g, rowvar=False), len(g)) for g in refZ]
def own_thr(ng):
    nu = ng - 1
    return (1 + 1.0 / ng) * pD * nu / (nu - pD + 1) * stats.f.ppf(0.99, pD, nu - pD + 1)
print('  (다) 집단별 공분산 기준: 각 집단 자기 평균과 자기 공분산으로 D2를 다시 구하고 호텔링 꼴 한계(집단 A %.2f, B %.2f, C %.2f)와 견줌' % tuple(own_thr(o[2]) for o in own))
assign = {}
print('  %-4s %-28s %5s %5s %5s | %9s %9s | %12s' % ('층', '참(시연 설계)', 'A로', 'B로', 'C로', '안맞음(가)', '안맞음(나)', '사후확률>=0.95'))
for u in UNK:
    P, D2 = T.lda_post(ZR[u], model)
    best = P.argmax(axis=1)
    dmin = D2[np.arange(len(best)), best]
    thr_b = np.array([hot_thr(len(refZ[j])) for j in best])
    outl = dmin > chi_crit
    outb = dmin > thr_b
    d_own = np.array([T.mahal2(ZR[u][i], own[best[i]][0], own[best[i]][1])[0] for i in range(len(best))])
    outc = d_own > np.array([own_thr(own[j][2]) for j in best])
    n = len(best)
    cnt = [int(((best == j) & ~outc).sum()) for j in range(3)]
    hi = int(((P.max(axis=1) >= 0.95) & ~outc).sum())
    assign[u] = dict(A=cnt[0], B=cnt[1], C=cnt[2], none=int(outc.sum()), none_naive=int(outl.sum()), none_b=int(outb.sum()), n=n, hi=hi)
    print('  %-4s %-28s %5d %5d %5d | %9d %9d %9d | %12d (n=%d)' % (u, TRUE[u], cnt[0], cnt[1], cnt[2], int(outl.sum()), int(outb.sum()), int(outc.sum()), hi, n))
# 같은 원천에서 만든 새 파편으로 거짓 경보율을 직접 센다(시연값 설계에서)
big = {g: T.ilr(T.close100(gen(g, 4000))[0]) for g in 'ABC'}
fa_n = np.mean([ (T.lda_post(big[g], model)[1][:, 'ABC'.index(g)] > chi_crit).mean() for g in 'ABC'])
fa_b = np.mean([ (T.lda_post(big[g], model)[1][:, 'ABC'.index(g)] > hot_thr(len(refZ['ABC'.index(g)]))).mean() for g in 'ABC'])
fa_c = np.mean([(np.array([T.mahal2(z, own['ABC'.index(g)][0], own['ABC'.index(g)][1])[0] for z in big[g]]) > own_thr(own['ABC'.index(g)][2])).mean() for g in 'ABC'])
print('  같은 원천에서 새로 만든 파편 4000개씩(원천 A, B, C)에서 "안 맞음" 비율: (가) %.4f, (나) %.4f, (다) %.4f (이상적 값 0.01)' % (fa_n, fa_b, fa_c))
assign['false_alarm'] = dict(naive=float(fa_n), corrected=float(fa_b), own=float(fa_c))
# 집단별 ilr 표준편차(합친 공분산이 틀린 이유)
for gi, g in enumerate('ABC'):
    print('  집단 %s의 ilr 좌표 표준편차 (좌표 1~%d): %s' % (g, pD, ' '.join('%.4f' % x for x in np.sqrt(np.diag(own[gi][1])))))
print('  집단 A, B, C의 로그 공분산 크기(대각합) = %s' % ', '.join('%.4f' % np.trace(o[1]) for o in own))

json.dump(dict(OX=OX, closed={k: v.tolist() for k, v in clo.items()}, truth=TRUE, tab=tab,
               ht={'%s|%s' % k: v for k, v in HT.items()}, assign=assign, conf=conf.tolist(), chi_crit=float(chi_crit)),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex1.json'), 'w'))
print('\n결과 저장: results/ex1.json')
