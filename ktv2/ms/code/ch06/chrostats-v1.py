# -*- coding: utf-8 -*-
"""6장 실습 6-7: 연대기 통계(평균 민감도, 평균 상관, EPS, SNR, SSS)와 EPS의 뜻을 둘로 갈라 맞춰 보기.
자료: 시연값(synth-demo-fixed.rwl)과 실제 공개 자료 co021(work/co021.rwl, 나무 번호 정보가 불확실해 코어마다 한 그루로 둔다).
실행: python3 chrostats-v1.py | tee chrostats.log
"""
import os, csv, json, platform, importlib.util
import numpy as np
import scipy

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))


def stats_block(I, tree, label):
    st = L.rwi_stats(I, tree)
    ms = np.array([L.mean_sensitivity(I[:, j]) for j in range(I.shape[1])])
    a1 = np.array([L.acf1(I[:, j]) for j in range(I.shape[1])])
    sd = np.array([np.nanstd(I[:, j], ddof=1) for j in range(I.shape[1])])
    print('  [%s] 계열 %d, 나무 %d (상관을 낼 수 있는 나무 %d)' % (label, I.shape[1], len(set(tree.tolist())), st['n']))
    print('    개별 계열: 평균 민감도 %.3f, 표준편차 %.3f, 1차 자기상관 %.3f (계열 평균)' % (ms.mean(), sd.mean(), a1.mean()))
    print('    코어 쌍 수: 나무 사이 %d, 나무 안 %d' % (st['n_bt'], st['n_wt']))
    print('    평균 상관: 전체 %.3f, 나무 사이 rbar.bt %.3f, 나무 안 rbar.wt %s' % (st['rbar_tot'], st['rbar_bt'], '%.3f' % st['rbar_wt'] if not np.isnan(st['rbar_wt']) else '없음(코어마다 한 그루로 둠)'))
    print('    유효 코어 수 c.eff %.3f, 유효 평균 상관 rbar.eff %.3f' % (st['c_eff'], st['rbar_eff']))
    print('    EPS %.3f, SNR %.2f (n = %d)' % (st['eps'], st['snr'], st['n']))
    return st


def split_half(R, tree, y0, y1, years, nsplit=2000, seed=7):
    """기간 [y0, y1] 내내 자료가 있는 나무들을 골라 코어를 나무마다 평균하고, 나무를 무작위로 반씩 나눠 두 연대기(산술 평균)의 상관을
    구한다. EPS(n) = n rbar / (1 + (n-1) rbar)는 '나무 n그루씩의 독립된 두 연대기 사이 상관의 기댓값'이라는 뜻이다."""
    sel = (years >= y0) & (years <= y1)
    ut = list(dict.fromkeys(tree.tolist()))
    means = []
    for t in ut:
        sub = R[sel][:, tree == t]
        if np.all(np.sum(~np.isnan(sub), axis=0) == 0):
            continue
        full_cols = [k for k in range(sub.shape[1]) if not np.isnan(sub[:, k]).any()]
        if not full_cols:
            continue
        means.append(np.mean(sub[:, full_cols], axis=1))
    M = np.array(means).T                       # 연도 x 나무
    nt = M.shape[1]
    rng = np.random.default_rng(seed)
    rs = []
    h = nt // 2
    for _ in range(nsplit):
        p = rng.permutation(nt)
        a = M[:, p[:h]].mean(axis=1)
        b = M[:, p[h:2 * h]].mean(axis=1)
        rs.append(np.corrcoef(a, b)[0, 1])
    C = np.corrcoef(M.T)
    rbar = (C.sum() - nt) / (nt * (nt - 1))
    return nt, h, float(np.mean(rs)), float(np.std(rs)), float(rbar), float(L.eps_from_rbar(h, rbar))


# ====================================================================== 시연값
print('\n=== 시연값 자료 (날짜를 고친 71계열, 41그루)')
years, names, X = L.read_rwl(os.path.join(HERE, 'synth-demo-fixed.rwl'))
ids = list(csv.DictReader(open(os.path.join(HERE, 'synth-ids.csv'), encoding='utf-8')))
tree = np.array([int(r['tree']) for r in ids])
res = {}
for lab, kw in (('ModNegExp', dict(method='ModNegExp')), ('Spline67', dict(method='Spline'))):
    I, _ = L.detrend(X, **kw)
    res[lab] = (I, stats_block(I, tree, lab))
print('\n  원자료(너비)에 곧바로 통계를 내면(표준화 없이) 어떻게 되는가: 나이 추세가 공통 신호처럼 보인다')
st_raw = stats_block(X, tree, '너비 그대로')

I, st = res['ModNegExp']
rbar = st['rbar_eff']
print('\n== EPS를 연도별로 보기 (rbar.eff = %.3f를 모든 해에 같다고 둔 근사, ModNegExp)' % rbar)
nt = np.zeros(len(years))
for t in dict.fromkeys(tree.tolist()):
    nt += np.any(~np.isnan(I[:, tree == t]), axis=1)
eps_t = np.array([L.eps_from_rbar(n, rbar) if n > 0 else np.nan for n in nt])
sss_t = L.sss(I, tree, rbar, st['n'])
need = L.n_for_eps(0.85, rbar)
print('  EPS 0.85에 필요한 나무 수 = 0.85 (1 - r)/(0.15 r) = %.2f그루' % need)
for yv in (1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000):
    i = int(yv - years[0])
    print('  %d년: 나무 %2d그루, EPS %.3f, SSS %.3f' % (yv, nt[i], eps_t[i], sss_t[i]))
first_e = int(years[np.where(eps_t >= 0.85)[0][0]])
first_s = int(years[np.where(sss_t >= 0.85)[0][0]])
print('  EPS >= 0.85가 처음 되는 해 %d(나무 %d그루), SSS >= 0.85가 처음 되는 해 %d(나무 %d그루)' % (first_e, nt[first_e - years[0]], first_s, nt[first_s - years[0]]))
print('  (이 방식은 연도마다 rbar를 새로 구하는 dplR의 이동 창 방식이 아니다. 근사이다)')

print('\n== EPS의 뜻을 둘로 갈라 맞춰 보기: n그루씩 두 연대기 사이의 상관 (2000번 무작위 분할)')
for lab in ('ModNegExp', 'Spline67'):
    I2 = res[lab][0]
    for (y0, y1) in ((1900, 2010), (1850, 2010)):
        ntree, h, rs, sd_, rb, ep = split_half(I2, tree, y0, y1, years)
        print('  %-9s %d~%d: 기간 내내 자료가 있는 나무 %d그루 -> %d그루씩 두 몫, 분할 상관 평균 %.3f(표준편차 %.3f), 나무 평균 계열의 평균 상관 %.3f, EPS(%d, %.3f) = %.3f' % (
            lab, y0, y1, ntree, h, rs, sd_, rb, h, rb, ep))

# ====================================================================== co021
pathA = os.path.join(HERE, 'work', 'co021.rwl')
if os.path.exists(pathA):
    print('\n=== 실제 공개 자료 co021 (35계열, 연도 1176~1963; 나무 번호는 불확실해 코어마다 한 그루로 둠)')
    yA, nA, XA = L.read_rwl(pathA)
    treeA = np.arange(XA.shape[1])
    for lab, kw in (('Mean', dict(method='Mean')), ('ModNegExp', dict(method='ModNegExp')), ('Spline67', dict(method='Spline')), ('Spline32', dict(method='Spline', nyrs=32))):
        IA, _ = L.detrend(XA, **kw)
        stA = stats_block(IA, treeA, lab)
        if lab in ('ModNegExp', 'Spline67'):
            ntree, h, rs, sd_, rb, ep = split_half(IA, treeA, 1700, 1950, yA)
            print('    분할 점검 1700~1950: 계열 %d개 -> %d개씩 두 몫, 분할 상관 평균 %.3f(표준편차 %.3f), 평균 상관 %.3f, EPS(%d, %.3f) = %.3f' % (ntree, h, rs, sd_, rb, h, rb, ep))
