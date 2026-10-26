# -*- coding: utf-8 -*-
"""4장 실습 4-4~4-7: 자기상관과 유효 표본 크기
제1권 11장 계산 11-9(상관의 유의성과 유효 표본)를 되풀이하고, 모의로 그 근사가 맞는지 점검한다.
자료는 모두 시연값(가상 AR(1) 계열)이다. 제1권에는 노백산 414년 원자료가 표로 없다.
실행: python3 ch04-03-autocorr-neff.py
"""
import time, json, platform
import numpy as np, scipy, scipy.signal as ss, statsmodels
from scipy import stats
from statsmodels.tsa.stattools import acf
from statsmodels.regression.linear_model import yule_walker
from statsmodels.tsa.ar_model import AutoReg

t0 = time.perf_counter()
print('파이썬 %s, numpy %s, scipy %s, statsmodels %s' % (platform.python_version(), np.__version__, scipy.__version__, statsmodels.__version__))
out = {}

def rcrit(n, a):
    tc = stats.t.isf(a / 2, n - 2)
    return tc / np.sqrt(n - 2 + tc * tc)
def neff_pair(n, r1, r2): return n * (1 - r1 * r2) / (1 + r1 * r2)

# ---------------------------------------------------------------- A. 제1권 계산 11-9 되풀이
print('\n== A. 제1권 계산 11-9 되풀이')
print('  임계 상관(양쪽 5%, 1%), 제1권 값과 같은 식 t/sqrt(n-2+t^2)')
for n in (57, 100, 130, 414):
    print('    n=%3d: %.3f, %.3f' % (n, rcrit(n, .05), rcrit(n, .01)))
print('  제1권: n=57 0.261 0.339 / n=100 0.197 0.256 / n=130 0.172 0.225 / n=414 0.096 0.126')
r = 0.12; n = 57
tt = r * np.sqrt(n - 2) / np.sqrt(1 - r * r)
print('  1차 차분 r=0.12, n=57: t=%.3f, p=%.3f (제1권 0.896, 0.374)' % (tt, 2 * stats.t.sf(tt, n - 2)))
r = 0.18; n = 414
tt = r * np.sqrt(n - 2) / np.sqrt(1 - r * r)
print('  r=-0.18, n=414 독립 가정: t=%.2f, p=%.2e (제1권 3.71, 2.3e-4)' % (tt, 2 * stats.t.sf(tt, n - 2)))
rho = 0.72
ne = neff_pair(414, rho, rho)
print('  두 계열 모두 rho=0.72: n_eff = 414(1-rho^2)/(1+rho^2) = %.1f (제1권 131.3)' % ne)
print('    임계 상관: 1%% %.3f, 5%% %.3f (n_eff를 정수 %d로 놓고; 제1권 0.224, 0.172)' % (rcrit(int(ne), .01), rcrit(int(ne), .05), int(ne)))
tt = 0.18 * np.sqrt(ne - 2) / np.sqrt(1 - 0.18 ** 2)
print('    r=-0.18의 t=%.2f, p=%.3f (n_eff=%.1f, df=n_eff-2)' % (tt, 2 * stats.t.sf(tt, ne - 2), ne))
print('  제1권 "한 계열만 0.72이면 n_eff = 67.4": n(1-rho)/(1+rho) = 414*0.28/1.72 = %.1f' % (414 * (1 - rho) / (1 + rho)))
print('    제1권의 쌍 공식에 rho1=0.72, rho2=0 을 넣으면 n_eff = %.1f' % neff_pair(414, rho, 0.0))
out['A'] = dict(neff=ne)

# ---------------------------------------------------------------- B. 자기상관 추정
print('\n== B. 시연 계열(AR(1), rho=0.72, n=414)의 자기상관 추정')
rng = np.random.default_rng(414)
def ar1(R, n, rho, rng, burn=300):
    e = rng.standard_normal((R, n + burn))
    x = ss.lfilter([1.0], [1.0, -rho], e, axis=1)[:, burn:]
    return x / np.sqrt(1 / (1 - rho * rho))
x = ar1(1, 414, 0.72, rng)[0]
a = acf(x, nlags=10, fft=True)
print('  표본 자기상관 lag 1..5:', ' '.join('%.3f' % v for v in a[1:6]), '(이론 0.72^k:', ' '.join('%.3f' % (0.72 ** k) for k in range(1, 6)), ')')
print('  yule_walker 추정 rho = %.3f' % yule_walker(x, order=1, method='mle', result_object=False)[0][0])
m = AutoReg(x, lags=1, trend='c').fit()
print('  AutoReg(OLS) 추정 rho = %.3f, 표준오차 %.4f (이론 sqrt((1-rho^2)/n) = %.4f)' % (m.params[1], m.bse[1], np.sqrt((1 - 0.72 ** 2) / 414)))
print('  백색 잡음일 때 자기상관의 95%% 한계 +-1.96/sqrt(n) = +-%.4f (제1권 n=414 임계 상관 0.096과 같은 값)' % (1.96 / np.sqrt(414)))
# 짧은 계열의 편향
R = 20000
xs = ar1(R, 414, 0.72, rng)
xc = xs - xs.mean(axis=1, keepdims=True)
rho_hat = (xc[:, 1:] * xc[:, :-1]).sum(axis=1) / (xc ** 2).sum(axis=1)
print('  n=414 계열 %d개의 rho 추정: 평균 %.4f, 표준편차 %.4f (이론 0.72 -> 평균은 약간 낮게 나온다)' % (R, rho_hat.mean(), rho_hat.std()))
for n_ in (50, 100):
    xs_ = ar1(R, n_, 0.72, rng); xc_ = xs_ - xs_.mean(axis=1, keepdims=True)
    rh = (xc_[:, 1:] * xc_[:, :-1]).sum(axis=1) / (xc_ ** 2).sum(axis=1)
    print('  n=%3d: 평균 %.4f, 표준편차 %.4f' % (n_, rh.mean(), rh.std()))
out['B'] = dict(acf=a.tolist(), x=x.tolist())

# ---------------------------------------------------------------- C. 모의: 독립한 두 계열의 상관이 5%에서 기각되는 비율
print('\n== C. 서로 독립인 두 계열의 상관검정: 이름뿐인 5%는 실제로 몇 %인가 (모의)')
def corr_rows(a, b):
    a = a - a.mean(axis=1, keepdims=True); b = b - b.mean(axis=1, keepdims=True)
    return (a * b).sum(axis=1) / np.sqrt((a * a).sum(axis=1) * (b * b).sum(axis=1))
def rho1_rows(a):
    a = a - a.mean(axis=1, keepdims=True)
    return (a[:, 1:] * a[:, :-1]).sum(axis=1) / (a * a).sum(axis=1)
def acf_rows(a, K):
    a = a - a.mean(axis=1, keepdims=True)
    den = (a * a).sum(axis=1)
    return np.stack([(a[:, k:] * a[:, :a.shape[1] - k]).sum(axis=1) / den for k in range(1, K + 1)], axis=1)
def pvals(r, df):
    t = r * np.sqrt(df) / np.sqrt(1 - r * r)
    return 2 * stats.t.sf(np.abs(t), df)
def bartlett_neff(a, b, K, n):
    ra, rb = acf_rows(a, K), acf_rows(b, K)
    k = np.arange(1, K + 1)
    s = 1 + 2 * ((1 - k / n) * ra * rb).sum(axis=1)
    return np.clip(n / s, 3, n)
def run_case(label, make_a, make_b, n, R, chunk=10000, K=20, rho_true=None):
    rs = []; ps = {'독립 가정': [], 'rho 참값 공식': [], 'rho 추정 공식': [], 'ACF 곱 공식(K=%d)' % K: []}
    ne_hat = []
    for _ in range(R // chunk):
        A, B = make_a(chunk, n), make_b(chunk, n)
        r = corr_rows(A, B); rs.append(r)
        ps['독립 가정'].append(pvals(r, n - 2))
        if rho_true is not None:
            ne = neff_pair(n, *rho_true)
            ps['rho 참값 공식'].append(pvals(r, np.full(chunk, ne - 2)))
        else:
            ps['rho 참값 공식'].append(np.full(chunk, np.nan))
        ne_e = np.clip(neff_pair(n, rho1_rows(A), rho1_rows(B)), 3, n)
        ne_hat.append(ne_e)
        ps['rho 추정 공식'].append(pvals(r, ne_e - 2))
        ne_b = bartlett_neff(A, B, K, n)
        ps['ACF 곱 공식(K=%d)' % K].append(pvals(r, ne_b - 2))
    rs = np.concatenate(rs)
    print('  [%s] n=%d, 쌍 %d개: r의 표준편차 %.4f (독립 가정이면 1/sqrt(n-1) = %.4f), 쓰인 n_eff(rho 추정 공식)의 중앙값 %.1f' % (label, n, R, rs.std(), 1 / np.sqrt(n - 1), np.median(np.concatenate(ne_hat))))
    res = {}
    for k, v in ps.items():
        v = np.concatenate(v)
        if np.isnan(v).all(): continue
        res[k] = (float((v < 0.05).mean()), float((v < 0.01).mean()))
        print('     %-18s 5%% 수준 기각 %.4f, 1%% 수준 기각 %.4f' % (k, *res[k]))
    return rs, res

rho = 0.72
R = 100000
mk = lambda rh: (lambda c, n: ar1(c, n, rh, rng))
mkw = lambda c, n: rng.standard_normal((c, n))
t1 = time.perf_counter()
r_ar, res_ar = run_case('두 계열 모두 AR(1) 0.72', mk(0.72), mk(0.72), 414, R, rho_true=(0.72, 0.72))
print('     이 사례의 모의 시간 %.1f s' % (time.perf_counter() - t1))
r_one, res_one = run_case('한 계열만 AR(1) 0.72, 다른 계열은 백색', mk(0.72), mkw, 414, R, rho_true=(0.72, 0.0))
# 한 계열만일 때 제1권의 67.4를 쓰면
ps67 = pvals(r_one, np.full(len(r_one), 67.4 - 2))
print('     (제1권 67.4를 df로 쓰면) 5%% 수준 기각 %.4f, 1%% 수준 기각 %.4f' % ((ps67 < .05).mean(), (ps67 < .01).mean()))
out['C'] = dict(both=res_ar, one=res_one, ps67=[float((ps67 < .05).mean()), float((ps67 < .01).mean())])
out['hist'] = np.histogram(r_ar, bins=np.linspace(-0.5, 0.5, 81))[0].tolist()
out['r_sd'] = float(r_ar.std())

# ---------------------------------------------------------------- D. r=-0.18의 모의 p값
print('\n== D. r=-0.18이 두 독립 AR(1)(0.72)의 사이에서 나올 확률 (모의 p값)')
p_emp = float((np.abs(r_ar) >= 0.18).mean())
ne = neff_pair(414, .72, .72)
print('  모의 %d쌍 가운데 |r|>=0.18: %d쌍, 모의 p = %.4f' % (R, int((np.abs(r_ar) >= 0.18).sum()), p_emp))
print('  비교: 독립 가정 p = %.1e, n_eff=%.1f 공식 p = %.4f' % (2 * stats.t.sf(0.18 * np.sqrt(412) / np.sqrt(1 - .18 ** 2), 412), ne, 2 * stats.t.sf(0.18 * np.sqrt(ne - 2) / np.sqrt(1 - .18 ** 2), ne - 2)))
sd_r = r_ar.std()
print('  모의 r의 표준편차 %.4f -> 모의에서 얻은 유효 표본 n_eff = 1/sd^2 + 1 = %.1f (제1권 공식 %.1f)' % (sd_r, 1 / sd_r ** 2 + 1, ne))
out['D'] = dict(p_emp=p_emp, sd=float(sd_r))

# ---------------------------------------------------------------- E. 이동평균
print('\n== E. 11년 이동평균을 하면 (제1권 계산 11-9의 5번 항목 "n_eff는 더 작다"의 크기)')
def ma_rows(x, w=11):
    c = np.cumsum(np.pad(x, ((0, 0), (1, 0))), axis=1)
    return (c[:, w:] - c[:, :-w]) / w
n_raw = 414
nv = n_raw - 10
print('  백색 잡음 %d점에 11년 이동평균(valid) -> %d점. 이론: rho1 = 10/11 = %.3f, 쌍 공식 n_eff = %.1f' % (n_raw, nv, 10 / 11, neff_pair(nv, 10 / 11, 10 / 11)))
mk_maw = lambda c, n: ma_rows(rng.standard_normal((c, n + 10)))
R2 = 60000
rs_ma, res_ma = run_case('백색 잡음의 11년 이동평균 두 개', mk_maw, mk_maw, nv, R2, K=30, rho_true=(10 / 11, 10 / 11))
sd_ma = rs_ma.std()
print('     모의 r의 표준편차 %.4f -> 모의에서 얻은 유효 표본 %.1f' % (sd_ma, 1 / sd_ma ** 2 + 1))
mk_maar = lambda c, n: ma_rows(ar1(c, n + 10, 0.72, rng))
rs_ma2, res_ma2 = run_case('AR(1) 0.72의 11년 이동평균 두 개', mk_maar, mk_maar, nv, R2, K=30)
print('     모의 r의 표준편차 %.4f -> 모의에서 얻은 유효 표본 %.1f' % (rs_ma2.std(), 1 / rs_ma2.std() ** 2 + 1))
out['E'] = dict(white=res_ma, ar=res_ma2, sd_white=float(sd_ma), sd_ar=float(rs_ma2.std()))

# ---------------------------------------------------------------- F. 평균의 유효 표본(67.4의 정체)
print('\n== F. n(1-rho)/(1+rho)는 무엇의 유효 표본인가: 평균의 유효 표본')
xs = ar1(40000, 414, 0.72, rng) * 1.0
var_mean = xs.mean(axis=1).var()
print('  AR(1) 0.72, 분산 1, n=414: 평균의 분산(모의) %.5f, 1/n = %.5f, 모의 n_eff(평균) = 1/분산 = %.1f (공식 %.1f)' % (var_mean, 1 / 414, 1 / var_mean, 414 * 0.28 / 1.72))
out['F'] = dict(neff_mean=float(1 / var_mean))
json.dump(out, open('results/ch04-03.json', 'w'))
print('\n총 실행 시간 %.1f s' % (time.perf_counter() - t0))
