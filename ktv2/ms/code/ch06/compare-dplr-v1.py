# -*- coding: utf-8 -*-
"""6장 실습 6-10b: ringlib-v1.py(파이썬 직접 구현)와 R dplR의 출력을 같은 입력으로 견준다.
먼저 dplr-run-v1.R를 실행해 work/r-*.csv를 만든다. 두 자료(co021, 시연값)에서 표준화 지수, 연대기, 연대기 통계, 평균 민감도,
계열 사이 상관, 구간 상관을 견주고 차이의 최댓값을 적는다.
실행: python3 compare-dplr-v1.py | tee compare-dplr.log"""
import os, csv, platform, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
print('환경: python %s, numpy %s' % (platform.python_version(), np.__version__))
W = lambda f: os.path.join(HERE, 'work', f)

def read_csv_mat(path):
    rd = list(csv.reader(open(path, encoding='utf-8')))
    head = rd[0][1:]
    rows = rd[1:]
    idx = [r[0] for r in rows]
    M = np.array([[np.nan if v in ('NA', '') else float(v) for v in r[1:]] for r in rows])
    return idx, head, M

def diff(a, b):
    both = ~np.isnan(a) & ~np.isnan(b)
    nan_mismatch = int(np.sum(np.isnan(a) != np.isnan(b)))
    d = np.abs(a[both] - b[both])
    return (d.max() if d.size else 0.0), nan_mismatch, int(both.sum())

results = []
def report(tag, what, mx, nm, n, tol=1e-6):
    ok = mx < tol and nm == 0
    results.append(ok)
    print('  [%s] %-12s %-34s 최대 차이 %.2e, 결측 위치가 다른 칸 %d, 비교한 칸 %d' % ('일치' if ok else '차이', tag, what, mx, nm, n))

for tag, path in (('co021', W('co021.rwl')), ('시연값', os.path.join(HERE, 'synth-demo-fixed.rwl'))):
    key = 'co021' if tag == 'co021' else 'synth'
    years, names, X = L.read_rwl(path)
    print('\n=== 자료 %s: 계열 %d개, 연도 %d~%d' % (tag, len(names), years[0], years[-1]))
    # R이 읽은 입력(Spline 지수 파일의 행·열 이름으로 확인)
    ridx, rn, _ = read_csv_mat(W('r-%s-sp67.csv' % key))
    print('  R의 연도 %s~%s, 계열 수 %d, 이름 일치 %s' % (ridx[0], ridx[-1], len(rn), 'yes' if rn == names else 'no'))
    # 지수 비교
    I = {}
    for lab, fname, kw in (('스플라인 67%', 'sp67', dict(method='Spline')), ('스플라인 32년', 'sp32', dict(method='Spline', nyrs=32)),
                           ('음의 지수', 'mne', dict(method='ModNegExp')), ('평균', 'mean', dict(method='Mean'))):
        _, _, R = read_csv_mat(W('r-%s-%s.csv' % (key, fname)))
        P, _ = L.detrend(X, **kw)
        I[fname] = P
        mx, nm, n = diff(P, R)
        report(tag, '지수 ' + lab, mx, nm, n, 1e-6 if fname != 'mne' else 1e-3)   # 음의 지수는 비선형 최소제곱의 수렴 허용 오차가 달라 허용치를 1e-3으로 둔다
        if fname == 'mne':
            # 계열별로 어디서 큰 차이가 났는가
            dd = [np.nanmax(np.abs(P[:, j] - R[:, j])) for j in range(P.shape[1])]
            big = [(names[j], d) for j, d in enumerate(dd) if d > 1e-6]
            print('        음의 지수에서 차이가 1e-6보다 큰 계열 %d개 %s' % (len(big), ', '.join('%s(%.2e)' % b for b in big[:6])))
    # 연대기
    for lab, fname in (('std(스플라인 67%)', 'sp67'), ('std(음의 지수)', 'mne')):
        _, hd, C = read_csv_mat(W('r-%s-chron-%s.csv' % (key, fname)))
        c, dep = L.chron(I[fname], True)
        mx, nm, n = diff(c, C[:, hd.index('std')])
        report(tag, '연대기 ' + lab, mx, nm, n, 1e-6 if fname != 'mne' else 1e-3)
        ok = np.array_equal(dep, C[:, hd.index('samp.depth')].astype(int))
        results.append(ok)
        print('  [%s] %-12s %-34s' % ('일치' if ok else '차이', tag, '표본 깊이(연도별 계열 수) ' + lab))
    # 잔차 연대기(음의 지수)
    _, hd, C = read_csv_mat(W('r-%s-chron-mne.csv' % key))
    Ir = np.full_like(I['mne'], np.nan)
    for j in range(I['mne'].shape[1]):
        Ir[:, j] = L.ar_prewhiten(I['mne'][:, j])
    cres, _ = L.chron(Ir, True)
    mx, nm, n = diff(cres, C[:, hd.index('res')])
    report(tag, '잔차 연대기(음의 지수)', mx, nm, n, 1e-3)
    # 연대기 통계
    if key == 'synth':
        ids = list(csv.DictReader(open(os.path.join(HERE, 'synth-ids.csv'), encoding='utf-8')))
        tree = np.array([int(r['tree']) for r in ids])
    else:
        tree = np.arange(len(names))
    for lab, fname in (('음의 지수', 'mne'), ('스플라인 67%', 'sp67')):
        rd = list(csv.DictReader(open(W('r-%s-stats-%s.csv' % (key, fname)), encoding='utf-8')))[0]
        st = L.rwi_stats(I[fname], tree)
        for k_py, k_r in (('rbar_tot', 'rbar.tot'), ('rbar_bt', 'rbar.bt'), ('rbar_wt', 'rbar.wt'), ('c_eff', 'c.eff'), ('rbar_eff', 'rbar.eff'), ('eps', 'eps'), ('snr', 'snr')):
            rv = np.nan if rd[k_r] in ('NA', '') else float(rd[k_r])
            pv = st[k_py]
            if np.isnan(rv) and np.isnan(pv):
                continue
            tol = 1e-6 if fname != 'mne' else 1e-3
            ok = abs(rv - pv) < tol * max(1, abs(rv))
            results.append(ok)
            print('  [%s] %-12s 연대기 통계 %-9s %-8s 파이썬 %.6f, dplR %.6f, 차이 %.1e' % ('일치' if ok else '차이', tag, lab, k_r, pv, rv, pv - rv))
    # 평균 민감도
    rd = list(csv.DictReader(open(W('r-%s-sens1.csv' % key), encoding='utf-8')))
    rs = np.array([float(r['sens1']) for r in rd])
    ps = np.array([L.mean_sensitivity(I['mne'][:, j]) for j in range(I['mne'].shape[1])])
    mx = float(np.max(np.abs(rs - ps)))
    results.append(mx < 1e-3)
    print('  [%s] %-12s 평균 민감도(sens1, 음의 지수 지수) 최대 차이 %.2e' % ('일치' if mx < 1e-3 else '차이', tag, mx))
    # 계열 사이 상관
    rd = list(csv.DictReader(open(W('r-%s-interseries.csv' % key), encoding='utf-8')))
    rr = np.array([float(r['res.cor']) for r in rd])
    r_py, _ = L.interseries_cor(X, 32)
    mx = float(np.nanmax(np.abs(rr - r_py)))
    results.append(mx < 1e-6)
    print('  [%s] %-12s 계열 사이 상관(interseries.cor) 최대 차이 %.2e' % ('일치' if mx < 1e-6 else '차이', tag, mx))
    if key == 'synth':
        rd = list(csv.reader(open(W('r-synth-sss-mne.csv'), encoding='utf-8')))[1:]
        sr = np.array([float(r[1]) for r in rd]); sr_p = np.array([float(r[2]) for r in rd])
        stm = L.rwi_stats(I['mne'], tree)
        sp = L.sss(I['mne'], tree, stm['rbar_eff'], stm['n'])
        mx = float(np.nanmax(np.abs(sr_p - sp)))
        results.append(mx < 1e-4)
        print('  [%s] %-12s SSS(피어슨 rbar.eff로 같은 식) 최대 차이 %.2e' % ('일치' if mx < 1e-4 else '차이', tag, mx))
        print('        (참고: dplR의 sss() 그대로의 값과 파이썬 값의 최대 차이 %.2e. sss()가 내부에서 rbar.eff를 스피어만 상관으로 구하기 때문이다)' % float(np.nanmax(np.abs(sr - sp))))

# 구간 상관(lag 0)과 최고 lag
print('\n=== 구간 상관: dplR의 corr.rwl.seg(25년 간격으로 맞춘 구간)와 이 책의 구간 계산을 같은 구간에서 견줌 (오류를 넣은 시연값 자료)')
years, names, Xb = L.read_rwl(os.path.join(HERE, 'synth-demo-bad.rwl'))
P = L.xdate_prep(Xb, 32, True); M = L.loo_master(P, True)
idx, hd, R = read_csv_mat(W('r-synth-segrho.csv'))
idx2, hd2, BL = read_csv_mat(W('r-synth-bestlag.csv'))
mxs, cnt, lagmis, lagcnt = 0.0, 0, 0, 0
for j, nm in enumerate(names):
    for k, h in enumerate(hd):
        a, b = [int(x) for x in h.replace('X', '').split('.')]
        rv = R[idx.index(nm), k] if nm in idx else np.nan
        if np.isnan(rv):
            continue
        sc = L.lag_scan(P[:, j], M[:, j], years, a, b, 10)
        # dplR의 구간 상관은 lag 0, 겹친 해가 구간 길이(50)인 경우만
        if sc[0][1] == 50:
            mxs = max(mxs, abs(sc[0][0] - rv)); cnt += 1
        bl = BL[idx2.index(nm), k]
        if not np.isnan(bl):
            best = max(sc, key=lambda kk: -1 if np.isnan(sc[kk][0]) else sc[kk][0])
            lagcnt += 1
            lagmis += int(best != int(bl))
print('  lag 0 구간 상관: 비교한 구간 %d개, 최대 차이 %.2e' % (cnt, mxs))
results.append(mxs < 1e-6)
print('  구간별 최고 상관의 lag: 비교한 구간 %d개 중 dplR와 다른 구간 %d개' % (lagcnt, lagmis))
print('\n전체: %d개 항목 중 일치 %d개, 차이 %d개' % (len(results), sum(results), len(results) - sum(results)))
