# -*- coding: utf-8 -*-
"""4장 실습 4-8~4-11: 추세 제거와 표준화
제1권 11.5절의 쉬운 예(w = 2.0 - 0.01 x 연령)와 표 1(표준 연대기 AR1 0.72, 잔차 연대기 0.03), 계산 11-5의 7번 항목을 되풀이한다.
나무 나이테 자료는 제1권에 표로 없으므로 모든 계열은 시연값(가상 자료)이다.
실행: python3 ch04-04-detrend-standardize.py
"""
import time, json, platform
import numpy as np, scipy, scipy.signal as ss, scipy.fft as sf, statsmodels
from scipy import stats, optimize, interpolate
from statsmodels.tsa.ar_model import AutoReg, ar_select_order

t0 = time.perf_counter()
print('파이썬 %s, numpy %s, scipy %s, statsmodels %s' % (platform.python_version(), np.__version__, scipy.__version__, statsmodels.__version__))
out = {}
TWO_PI = 2 * np.pi

# ---------------------------------------------------------------- A. 제1권 11.5절의 쉬운 예
print('\n== A. 제1권 11.5절 쉬운 예: 직선 w = 2.0 - 0.01 x 연령')
w = lambda age: 2.0 - 0.01 * age
print('  연령 50, 실제 1.4 mm: 직선값 %.2f, 지수 %.4f' % (w(50), 1.4 / w(50)))
print('  연령 51, 실제 1.5 mm: 직선값 %.2f, 지수 %.4f' % (w(51), 1.5 / w(51)))
print('  제1권 값: 0.933, 1.007')
# 직선을 자료에서 되찾기
rng = np.random.default_rng(11)
age = np.arange(30, 130.0)
wid = w(age) * (1 + 0.15 * rng.standard_normal(len(age)))
c = np.polyfit(age, wid, 1)
print('  잡음이 낀 가상 자료에서 np.polyfit으로 되찾은 직선: 기울기 %.4f, 절편 %.3f (심은 값 -0.01, 2.0)' % (c[0], c[1]))

# ---------------------------------------------------------------- B. 가상 나이테 한 줄로 추세 제거 방법 비교
print('\n== B. 시연값 한 줄(414년): 추세 제거 방법을 비교한다 (참값을 아는 가상 자료)')
N = 414
years = np.arange(1600, 1600 + N)
def ar1_series(n, rho, rng, burn=300):
    e = rng.standard_normal(n + burn)
    x = ss.lfilter([1.0], [1.0, -rho], e)[burn:]
    return x / x.std()
rng = np.random.default_rng(1600)
c_hi = ar1_series(N, 0.3, rng)                              # 해마다의 기후 신호
c_lo = np.sin(TWO_PI * np.arange(N) / 130.0 + 0.8)          # 130년 주기의 느린 신호(시연 가정)
clim = 0.7 * c_hi + 0.5 * c_lo
bio = ar1_series(N, 0.6, rng)                               # 나무 자신의 생장 기억
nse = rng.standard_normal(N)
agev = np.arange(15, 15 + N, dtype=float)                   # 나이 15 ~ 428
G = 2.2 * np.exp(-0.015 * agev) + 0.55                      # 나이에 따른 자연 감소(음의 지수, 시연 가정)
width = G * np.exp(0.18 * clim + 0.10 * bio + 0.08 * nse)
print('  나이 %d~%d, 테 너비 %.2f~%.2f mm (처음 10년 평균 %.2f, 끝 10년 평균 %.2f)' % (agev[0], agev[-1], width.min(), width.max(), width[:10].mean(), width[-10:].mean()))

def fit_negexp(y, x):
    f = lambda x, a, b, c: a * np.exp(-b * x) + c
    p0 = (y[:20].mean() - y[-20:].mean(), 0.01, y[-20:].mean())
    p, _ = optimize.curve_fit(f, x, y, p0=p0, maxfev=20000)
    return f(x, *p), p
def spline_fit(y, x, wavelength):
    """50% 진동수 응답 파장이 wavelength(년)인 3차 평활 스플라인. lam을 이분법으로 맞춘다."""
    mid = slice(len(x) // 5, -len(x) // 5)
    s = np.sin(TWO_PI * x / wavelength)
    def gain(loglam):
        sp = interpolate.make_smoothing_spline(x, s, lam=10 ** loglam)
        r = sp(x)
        return (r[mid] @ s[mid]) / (s[mid] @ s[mid]) - 0.5
    lg = optimize.brentq(gain, -6, 12)
    return interpolate.make_smoothing_spline(x, y, lam=10 ** lg)(x), 10 ** lg
fits = {}
fits['직선'] = np.polyval(np.polyfit(agev, width, 1), agev)
fits['음의 지수'], pexp = fit_negexp(width, agev)
fits['67% 스플라인'], lam67 = spline_fit(width, agev, 0.67 * N)
fits['100년 스플라인'], lam100 = spline_fit(width, agev, 100.0)
fits['평균(추세 제거 안 함)'] = np.full(N, width.mean())
print('  음의 지수 적합: a=%.3f, b=%.4f, c=%.3f (심은 값 2.2, 0.015, 0.55; 나이 기준 적합)' % tuple(pexp))
print('  평활 스플라인 lam: 67%% 규칙(파장 %.0f년) %.3e, 100년 파장 %.3e' % (0.67 * N, lam67, lam100))
def lowpass(x, k=51):
    return np.convolve(x, np.ones(k) / k, mode='valid')
def rho1(x):
    x = x - x.mean()
    return (x[1:] @ x[:-1]) / (x @ x)
print('  %-18s %7s %7s %9s %9s %9s' % ('방법', '지수 sd', 'AR1', 'r(기후)', 'r(고주파)', 'r(저주파)'))
tab = {}
hi_true = c_hi
for nm, fit in fits.items():
    idx = width / fit
    r_all = np.corrcoef(idx, clim)[0, 1]
    r_hi = np.corrcoef(idx, hi_true)[0, 1]
    r_lo = np.corrcoef(lowpass(idx), lowpass(clim))[0, 1]
    tab[nm] = (float(idx.std()), float(rho1(idx)), float(r_all), float(r_hi), float(r_lo))
    print('  %-18s %7.3f %7.3f %9.3f %9.3f %9.3f' % ((nm,) + tab[nm]))
print('  (r(기후): 지수와 참 기후 신호 전체의 상관, r(고주파): 해마다 성분 c_hi와의 상관, r(저주파): 51년 이동평균끼리의 상관)')
out['B'] = dict(tab=tab, years=years.tolist(), width=width.tolist(), fits={k: v.tolist() for k, v in fits.items()}, clim=clim.tolist())

# ---------------------------------------------------------------- C. 자기상관 제거(잔차 연대기)
print('\n== C. 지수의 자기상관을 AR 모형으로 빼면(잔차 지수): 제1권 표 1의 표준 0.72와 잔차 0.03에 해당하는 절차')
idx = width / fits['67% 스플라인']
sel = ar_select_order(idx, maxlag=6, ic='aic', trend='c')
lags = list(sel.ar_lags) if sel.ar_lags is not None else []
nl = max(lags) if lags else 0
m = AutoReg(idx, lags=lags, trend='c').fit() if lags else None
res = m.resid + idx.mean() if m is not None else idx
idt = idx[nl:]                                   # 잔차와 같은 해들로 맞춘다
print('  AIC로 고른 AR 차수 lags=%s' % (lags,))
print('  표준(67%% 스플라인) 지수: sd %.3f, AR1 %.3f / 잔차 지수: sd %.3f, AR1 %.3f' % (idt.std(), rho1(idt), res.std(), rho1(res)))
print('  제1권 표 1은 논문의 값이다: 표준 sd 0.20, AR1 0.72 / 잔차 sd 0.12, AR1 0.03')
print('  참 기후 신호와의 상관: 표준 %.3f, 잔차 %.3f / 해마다 성분 c_hi와의 상관: 표준 %.3f, 잔차 %.3f' % (
    np.corrcoef(idt, clim[nl:])[0, 1], np.corrcoef(res, clim[nl:])[0, 1], np.corrcoef(idt, c_hi[nl:])[0, 1], np.corrcoef(res, c_hi[nl:])[0, 1]))
f1_, p1 = ss.periodogram(idt - idt.mean(), window='boxcar', detrend=False)
f2_, p2 = ss.periodogram(res - res.mean(), window='boxcar', detrend=False)
lo = (f1_ > 0) & (f1_ <= 1 / 50.0)
print('  주기 50년보다 긴 쪽의 분산 몫: 표준 %.3f, 잔차 %.3f' % (p1[lo].sum() / p1.sum(), p2[lo].sum() / p2.sum()))
out['C'] = dict(sd=[float(idt.std()), float(res.std())], ar1=[float(rho1(idt)), float(rho1(res))])

# ---------------------------------------------------------------- D. 여러 그루 평균
print('\n== D. 20그루를 평균하면 (제1권 11.5절 이론 상자 마지막 문장)')
K = 20
rng = np.random.default_rng(20)
common = clim
idxs = []
for k in range(K):
    a0 = rng.integers(10, 120)
    ag = np.arange(a0, a0 + N, dtype=float)
    Gk = (1.8 + 0.8 * rng.random()) * np.exp(-(0.010 + 0.01 * rng.random()) * ag) + 0.5 + 0.3 * rng.random()
    b = ar1_series(N, 0.6, rng); e = rng.standard_normal(N)
    wk = Gk * np.exp(0.18 * common + 0.10 * b + 0.14 * e)
    fk, _ = fit_negexp(wk, ag)
    idxs.append(wk / fk)
idxs = np.array(idxs)
single_noise = np.mean([np.std(idxs[k] - np.polyval(np.polyfit(common, idxs[k], 1), common)) for k in range(K)])
mean_idx = idxs.mean(axis=0)
mean_noise = np.std(mean_idx - np.polyval(np.polyfit(common, mean_idx, 1), common))
print('  나무 %d그루, 각자 음의 지수로 추세 제거(나이는 나무마다 다르다)' % K)
print('  기후 신호에 직선 회귀한 뒤 남는 표준편차: 한 그루 평균 %.4f, 20그루 평균 %.4f, 비 %.3f (잡음이 독립이면 1/sqrt(20) = %.3f)' % (single_noise, mean_noise, mean_noise / single_noise, 1 / np.sqrt(K)))
rbar = (np.corrcoef(idxs).sum() - K) / (K * (K - 1))
print('  나무 사이 평균 상관 %.3f, 20그루 평균 지수와 기후 신호의 상관 %.3f, 한 그루와 기후 신호의 평균 상관 %.3f' % (rbar, np.corrcoef(mean_idx, common)[0, 1], np.mean([np.corrcoef(idxs[k], common)[0, 1] for k in range(K)])))
out['D'] = dict(single=float(single_noise), mean=float(mean_noise), rbar=float(rbar))

# ---------------------------------------------------------------- E. 추세와 푸리에 스펙트럼
print('\n== E. 추세를 남겨 두면 스펙트럼이 어떻게 보이는가')
rng = np.random.default_rng(5)
n = 256
t = np.arange(n)
y = 0.02 * t + rng.standard_normal(n)
for nm, yy in (('평균만 뺀 원자료(직선 추세 0.02/년 + 백색 잡음)', y - y.mean()), ('직선 추세 제거(scipy.signal.detrend)', ss.detrend(y, type='linear'))):
    Pw = np.abs(sf.rfft(yy)) ** 2
    Pw = Pw[1:]
    print('  %-48s 가장 낮은 3개 칸의 파워 비중 %.3f (칸이 %d개이므로 백색 잡음이면 약 %.3f)' % (nm, Pw[:3].sum() / Pw.sum(), len(Pw), 3 / len(Pw)))
out['E'] = {}

# ---------------------------------------------------------------- F. 차분: 저주파와 고주파의 상관
print('\n== F. 1차 차분 상관 (제1권 11.5.5절: 원 상관 대 차분 상관)')
rng = np.random.default_rng(57)
n = 58
slow = np.sin(TWO_PI * np.arange(n) / 40.0 + 0.5)          # 두 계열이 함께 가진 40년 주기의 느린 성분(시연 가정)
xx = slow + 0.5 * rng.standard_normal(n)
yy = 1.5 * slow + 1.0 * rng.standard_normal(n)
r0 = np.corrcoef(xx, yy)[0, 1]
r1 = np.corrcoef(np.diff(xx), np.diff(yy))[0, 1]
print('  공통의 느린 성분 + 독립 잡음 (n=58, 시연값): 원 계열 r = %.3f, 1차 차분(n=57) r = %.3f' % (r0, r1))
print('  제1권 값은 논문의 r = 0.757(원)과 0.12(차분)이며, 이 시연은 같은 현상(느린 성분만 일치)을 보이려는 것이다.')
out['F'] = dict(r0=float(r0), r1=float(r1))

# ---------------------------------------------------------------- G. 표준화(척도 변환)와 제1권 계산 11-5의 7번
print('\n== G. 표준화(z 점수)와 척도 변환: 제1권 계산 11-5의 7번 항목')
slope, icpt = 2.987, 4.829
print('  복원 평균 7.66 -> X = (7.66 - 4.829)/2.987 = %.4f (제1권 0.948)' % ((7.66 - icpt) / slope))
print('  복원 sd 0.53 -> X의 sd = 0.53/2.987 = %.4f (제1권 0.177)' % (0.53 / slope))
print('  표 1 표준 sd 0.20 x 기울기 = %.4f (제1권 0.597; 논문 0.53과 다르다 -> 제1권에서도 미결)' % (0.20 * slope))
print('  비 0.53/0.597 = %.3f' % (0.53 / (0.20 * slope)))
z = (width / fits['67% 스플라인'] - idx.mean()) / idx.std()
print('  시연 계열을 z 점수로 바꾸면 평균 %.1e, 표준편차 %.3f (z 점수는 평균 0, 표준편차 1로 맞춘다)' % (z.mean(), z.std()))
# 최소제곱 변환의 분산 축소: sd(Yhat) = R sd(Y)
rng = np.random.default_rng(58)
X = rng.standard_normal(58); Y = 0.757 * X + np.sqrt(1 - 0.757 ** 2) * rng.standard_normal(58)
b = np.polyfit(X, Y, 1)
print('  최소제곱 변환의 성질(시연값): sd(추정)/sd(관측) = %.3f = |r| = %.3f' % (np.std(np.polyval(b, X)) / Y.std(), abs(np.corrcoef(X, Y)[0, 1])))
out['G'] = {}
json.dump(out, open('results/ch04-04.json', 'w'))
print('\n총 실행 시간 %.2f s' % (time.perf_counter() - t0))
