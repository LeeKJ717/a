# -*- coding: utf-8 -*-
"""6장 실습 6-5(표준화)와 6-6(연대기 만들기): 시연값 자료(날짜를 고친 synth-demo-fixed.rwl)로 표준화 방법을 견주고
연대기를 만든 뒤 참 기후와 견준다.
입력: synth-demo-fixed.rwl, synth-ids.csv, synth-truth.csv
출력: synth-chron.csv (연대기), detrend-fig.json, chron-fig.json (그림용), detrend-chron.log
실행: python3 detrend-chron-v1.py | tee detrend-chron.log
"""
import os, json, csv, platform, importlib.util
import numpy as np
import scipy

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)

print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
years, names, X = L.read_rwl(os.path.join(HERE, 'synth-demo-fixed.rwl'))
ids = list(csv.DictReader(open(os.path.join(HERE, 'synth-ids.csv'), encoding='utf-8')))
tree = np.array([int(r['tree']) for r in ids])
assert [r['series'] for r in ids] == names
T = np.array([float(r['temp_true']) for r in csv.DictReader(open(os.path.join(HERE, 'synth-truth.csv'), encoding='utf-8'))])
zT = (T - T.mean()) / T.std(ddof=1)
print('자료: 계열 %d개, 나무 %d그루, 연도 %d~%d' % (X.shape[1], len(set(tree)), years[0], years[-1]))

# ---------------------------------------------------------------- 한 계열의 표준화
print('\n== 한 계열(T01A, 가장 긴 계열)의 표준화 방법별 곡선과 지수')
j = names.index('T01A')
y = X[:, j]
fig = dict(years=years.tolist(), raw=[None if np.isnan(v) else round(float(v), 4) for v in y], curves={}, index={})
for lab, kw in (('Mean', dict(method='Mean')), ('ModNegExp', dict(method='ModNegExp')), ('Spline67', dict(method='Spline')), ('Spline32', dict(method='Spline', nyrs=32))):
    idx, cur = L.detrend_series(y, **kw)
    ok = ~np.isnan(idx)
    a1 = L.acf1(idx)
    print('  %-9s 곡선: 첫 해 %.3f mm, 마지막 해 %.3f mm | 지수: 평균 %.3f, 표준편차 %.3f, 최소 %.3f, 최대 %.3f, 1차 자기상관 %.3f' % (
        lab, cur[ok][0], cur[ok][-1], np.nanmean(idx), np.nanstd(idx, ddof=1), np.nanmin(idx), np.nanmax(idx), a1))
    fig['curves'][lab] = [None if np.isnan(v) else round(float(v), 4) for v in cur]
    fig['index'][lab] = [None if np.isnan(v) else round(float(v), 4) for v in idx]
a, b, k = None, None, None
n = int(np.sum(~np.isnan(y)))
tt = np.arange(1, n + 1.0)
from scipy.optimize import curve_fit
yy = y[~np.isnan(y)]
popt, _ = curve_fit(lambda t, a, b, k: a * np.exp(b * t) + k, tt, yy, p0=[yy[:41].mean(), -0.01, yy[int(n * 0.9) - 1:].mean()], maxfev=20000)
print('  ModNegExp의 계수: a = %.4f mm, b = %.5f /년, k = %.4f mm (너비 = a exp(b 나이) + k)' % tuple(popt))
json.dump(fig, open(os.path.join(HERE, 'detrend-fig.json'), 'w'))

# ---------------------------------------------------------------- 표준화 방법별 연대기
print('\n== 표준화 방법별 연대기와 참 기후의 일치 (71계열, 이중 가중 평균)')
methods = (('ModNegExp', dict(method='ModNegExp')), ('Spline67', dict(method='Spline')), ('Spline32', dict(method='Spline', nyrs=32)), ('Mean', dict(method='Mean')))
CH = {}
for lab, kw in methods:
    I, _ = L.detrend(X, **kw)
    c, dep = L.chron(I, True)
    CH[lab] = (I, c, dep)


def z(v):
    ok = ~np.isnan(v)
    return (v - np.nanmean(v)) / np.nanstd(v[ok], ddof=1)


def smooth(v, w=31):
    out = np.full(len(v), np.nan)
    h = w // 2
    for i in range(h, len(v) - h):
        seg = v[i - h:i + h + 1]
        if not np.isnan(seg).any():
            out[i] = seg.mean()
    return out


def corr(a, b, sel):
    ok = sel & ~np.isnan(a) & ~np.isnan(b)
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


full = np.ones(len(years), bool)
cal = years >= 1956
print('  방법        전체 r   1956~2013 r   31년 이동평균 r   표준편차(지수)   1차 자기상관')
rows_out = {}
for lab, kw in methods:
    I, c, dep = CH[lab]
    r_full = corr(c, T, full)
    r_cal = corr(c, T, cal)
    r_low = corr(smooth(c), smooth(T), full)
    print('  %-9s  %6.3f   %9.3f   %14.3f   %12.3f   %12.3f' % (lab, r_full, r_cal, r_low, np.nanstd(c, ddof=1), L.acf1(c)))
    rows_out[lab] = dict(r_full=r_full, r_cal=r_cal, r_low=r_low)
print('  (참 기후 T 자체의 1차 자기상관 %.3f)' % L.acf1(T))
print('  세기별 r (ModNegExp / Spline67 / Spline32): 이 값은 표본 깊이가 얕은 앞 세기에서 낮아진다')
print('    세기        코어 수(시작)   ModNegExp   Spline67   Spline32')
for a0 in (1600, 1700, 1800, 1900):
    sel = (years >= a0) & (years < a0 + 100)
    sel[-1] = sel[-1] or (a0 == 1900)
    if a0 == 1900:
        sel = years >= 1900
    print('    %d~%d  %9d      %8.3f   %8.3f   %8.3f' % (a0, a0 + 99 if a0 < 1900 else 2013, CH['ModNegExp'][2][sel][0],
          corr(CH['ModNegExp'][1], T, sel), corr(CH['Spline67'][1], T, sel), corr(CH['Spline32'][1], T, sel)))

# 이중 가중 평균과 산술 평균
I = CH['ModNegExp'][0]
c_bi, dep = L.chron(I, True)
c_mean, _ = L.chron(I, False)
print('\n== 이중 가중 평균과 산술 평균 (ModNegExp 지수): 두 연대기의 상관 %.4f, 참 기후와의 r %.3f(이중 가중), %.3f(산술)' % (
    corr(c_bi, c_mean, full), corr(c_bi, T, full), corr(c_mean, T, full)))
print('  연도별 두 값의 차이: 평균 절댓값 %.4f, 최대 %.4f' % (np.nanmean(np.abs(c_bi - c_mean)), np.nanmax(np.abs(c_bi - c_mean))))

# 잔차(RES) 연대기: 지수 계열마다 AR 모형을 맞춰 자기상관을 뺀 뒤 평균
Ires = np.full_like(I, np.nan)
orders = []
for jj in range(I.shape[1]):
    col = I[:, jj]
    ok = ~np.isnan(col)
    res, xm, order, ar = L.ar_yw(col[ok])
    orders.append(order)
    out = np.full(len(col), np.nan)
    out[np.where(ok)[0]] = res + xm
    Ires[:, jj] = out
c_res, _ = L.chron(Ires, True)
print('\n== 표준(std)과 잔차(RES) 연대기 (ModNegExp 지수, 제1권 11.5.1절 표 1의 두 열과 같은 구분)')
print('  AR 차수: 0차 %d개, 1차 %d개, 2차 이상 %d개 (71계열)' % (sum(o == 0 for o in orders), sum(o == 1 for o in orders), sum(o >= 2 for o in orders)))
print('  1차 자기상관: std %.3f, RES %.3f  (제1권이 옮긴 논문 표 1은 0.72와 0.03)' % (L.acf1(c_bi), L.acf1(c_res)))
print('  평균 민감도: std %.3f, RES %.3f  (논문 표 1은 0.12와 0.14)' % (L.mean_sensitivity(c_bi), L.mean_sensitivity(c_res)))
print('  표준편차: std %.3f, RES %.3f  (논문 표 1은 0.20과 0.12)' % (np.nanstd(c_bi, ddof=1), np.nanstd(c_res, ddof=1)))
print('  참 기후와의 r: std %.3f, RES %.3f' % (corr(c_bi, T, full), corr(c_res, T, full)))
print('  (이 비교는 시연값 자료의 값이며 노백산 자료의 값이 아니다)')

# 저장
with open(os.path.join(HERE, 'synth-chron.csv'), 'w', encoding='utf-8') as f:
    f.write('year,std,res,spline67,spline32,depth\n')
    for i, yv in enumerate(years):
        def fmt(v): return '' if np.isnan(v) else '%.6f' % v
        f.write('%d,%s,%s,%s,%s,%d\n' % (yv, fmt(c_bi[i]), fmt(c_res[i]), fmt(CH['Spline67'][1][i]), fmt(CH['Spline32'][1][i]), dep[i]))
cj = dict(years=years.tolist(), std=[None if np.isnan(v) else round(float(v), 4) for v in c_bi],
          spline67=[None if np.isnan(v) else round(float(v), 4) for v in CH['Spline67'][1]],
          spline32=[None if np.isnan(v) else round(float(v), 4) for v in CH['Spline32'][1]],
          truth_z=[round(float(v), 4) for v in zT], depth=dep.tolist())
json.dump(cj, open(os.path.join(HERE, 'chron-fig.json'), 'w'))
print('\n저장: synth-chron.csv, detrend-fig.json, chron-fig.json')
