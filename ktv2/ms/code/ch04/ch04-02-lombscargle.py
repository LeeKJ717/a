# -*- coding: utf-8 -*-
"""4장 실습 4-2, 4-3: 불규칙 간격 자료의 스펙트럼 (Lomb-Scargle)
시연값(가상 자료)으로 절차를 보인다. 제1권 10장(코어 YD0901형)과 2장(145개 점, 4263년)의 설정을 따른다.
실행: python3 ch04-02-lombscargle.py
"""
import time, json, platform
import numpy as np, scipy, scipy.signal as ss, scipy.fft as sf
import astropy
from astropy.timeseries import LombScargle

t0 = time.perf_counter()
print('파이썬 %s, numpy %s, scipy %s, astropy %s' % (platform.python_version(), np.__version__, scipy.__version__, astropy.__version__))
TWO_PI = 2 * np.pi
out = {}

def ou_at(times, tau, rng):
    """불규칙한 시각에서 정확히 뽑은 AR(1)/OU 붉은 잡음(분산 1). 계수 rho_i = exp(-dt_i / tau)."""
    x = np.empty(len(times)); x[0] = rng.standard_normal()
    for i in range(1, len(times)):
        r = np.exp(-(times[i] - times[i - 1]) / tau)
        x[i] = r * x[i - 1] + np.sqrt(1 - r * r) * rng.standard_normal()
    return x

# ---------------------------------------------------------------- A. 구현 검증: 직접 최소제곱, astropy, 일정 간격과의 관계
print('\n== A. scipy.signal.lombscargle을 세 가지로 검증한다')
rng = np.random.default_rng(20261026)
n = 200
t = np.sort(rng.uniform(0, 100, n))
y = 1.5 * np.sin(TWO_PI * t / 12.0 + 0.7) + 0.5 + rng.standard_normal(n)
yc = y - y.mean()
freq = np.linspace(1 / 100, 0.5, 500)               # 주기 1/주파수 (1/a)
w = TWO_PI * freq
p_sc = ss.lombscargle(t, yc, w, normalize=True, floating_mean=True)
# (1) 진동수마다 y = a cos + b sin + c 를 최소제곱으로 맞추어 1 - SSE/SST
def r2_fit(t, y, om):
    M = np.column_stack([np.cos(om * t), np.sin(om * t), np.ones_like(t)])
    c, *_ = np.linalg.lstsq(M, y, rcond=None)
    return 1 - np.sum((y - M @ c) ** 2) / np.sum((y - y.mean()) ** 2)
p_fit = np.array([r2_fit(t, y, om) for om in w])
print('  (1) 직접 최소제곱 1-SSE/SST 대 scipy(normalize=True, floating_mean=True): 최대 차이 %.2e' % np.abs(p_fit - p_sc).max())
# (2) astropy
p_as = LombScargle(t, y).power(freq, normalization='standard')
print('  (2) astropy LombScargle(standard) 대 scipy: 최대 차이 %.2e' % np.abs(p_as - p_sc).max())
k = p_sc.argmax()
print('      봉우리: scipy 주기 %.3f, 정규화 파워 %.4f / astropy 주기 %.3f, 파워 %.4f (심은 주기 12.0)' % (1 / freq[k], p_sc[k], 1 / freq[p_as.argmax()], p_as.max()))
# (3) 일정 간격: LS 파워 = 고전 주기도 x N/2 (normalize=False, 평균을 뺀 자료)
nn = 256; tt = np.arange(nn) * 1.0
yy = np.random.default_rng(3).standard_normal(nn)
yy -= yy.mean()
ff = sf.rfftfreq(nn, 1.0)[1:-1]
pl = ss.lombscargle(tt, yy, TWO_PI * ff, normalize=False)
f_, pp = ss.periodogram(yy, fs=1.0, window='boxcar', detrend=False, scaling='spectrum')
ratio = pl / pp[1:-1]
print('  (3) 일정 간격 N=%d: LS 파워/고전 주기도 의 범위 %.6f ~ %.6f, 이론값 N/2 = %.1f' % (nn, ratio.min(), ratio.max(), nn / 2))

# ---------------------------------------------------------------- B. 계산 시간
print('\n== B. 한 번의 계산에 걸리는 시간 (N=550, 진동수 1100개)')
tt = np.sort(np.random.default_rng(5).uniform(0, 600, 550)); yy = np.random.default_rng(6).standard_normal(550)
ww = TWO_PI * np.linspace(1 / 600, 0.5, 1100)
reps = 50
s = time.perf_counter()
for _ in range(reps): ss.lombscargle(tt, yy - yy.mean(), ww, normalize=True, floating_mean=True)
print('  scipy lombscargle (normalize=True, floating_mean=True): %.3f ms/회' % ((time.perf_counter() - s) / reps * 1e3))
s = time.perf_counter()
for _ in range(reps): ss.lombscargle(tt, yy - yy.mean(), ww, normalize=True)
print('  scipy lombscargle (normalize=True, floating_mean=False): %.3f ms/회' % ((time.perf_counter() - s) / reps * 1e3))
fq = ww / TWO_PI
s = time.perf_counter()
for _ in range(20): LombScargle(tt, yy).power(fq, method='fast')
print('  astropy (fast): %.3f ms/회' % ((time.perf_counter() - s) / 20 * 1e3))
pf = LombScargle(tt, yy).power(fq, method='fast')
pc = LombScargle(tt, yy).power(fq, method='cython')
print('  astropy fast 대 cython 방식의 최대 차이 %.2e (fast는 근사)' % np.abs(pf - pc).max())

# ---------------------------------------------------------------- C. 시연 1: 퇴적률이 흔들리는 코어 (제1권 10장 설정)
print('\n== C. 시연 1 (시연값): 퇴적률이 깊이에 따라 흔들리는 코어, 심은 주기 5.2 a')
rng = np.random.default_rng(1087)
z = np.arange(0, 552.0)               # cm, 시료 간격 1 cm, 길이 5.52 m
rate0 = 0.92
rate = rate0 * (1 + 0.30 * np.sin(TWO_PI * z / 220.0 + 0.4))          # cm/a, 시연 가정
age = np.concatenate([[0], np.cumsum(1.0 / (0.5 * (rate[1:] + rate[:-1])))])
dts = np.diff(age)
print('  시료 %d개, 총 %.1f a, 시료 간격 평균 %.3f a (최소 %.3f, 최대 %.3f)' % (len(z), age[-1], dts.mean(), dts.min(), dts.max()))
P0, amp = 5.2, 0.9
noise = ou_at(age, 5.0, rng)
y = amp * np.sin(TWO_PI * age / P0 + 1.1) + noise
yc = y - y.mean()
T = age[-1]
fgrid = np.arange(1 / T, 0.45, 1 / (8 * T))
p_ls = ss.lombscargle(age, yc, TWO_PI * fgrid, normalize=True, floating_mean=True)
def band_peak(f, p, lo=1 / 12.0, hi=1 / 3.0):
    m = (f >= lo) & (f <= hi)
    i = np.where(m)[0][p[m].argmax()]
    # 반치폭(봉우리 높이의 절반 이상인 연속 구간)
    j0 = i
    while j0 > 0 and p[j0 - 1] >= p[i] / 2: j0 -= 1
    j1 = i
    while j1 < len(p) - 1 and p[j1 + 1] >= p[i] / 2: j1 += 1
    return 1 / f[i], p[i], 1 / f[j1], 1 / f[j0]
# 잘못된 가정: 간격이 일정하다고 보고 시료 번호에 평균 간격을 곱해 시각으로 쓴다
tn2 = np.arange(len(z)) * dts.mean()
p_naive = ss.lombscargle(tn2, yc, TWO_PI * fgrid, normalize=True, floating_mean=True)
a = band_peak(fgrid, p_ls); b = band_peak(fgrid, p_naive)
print('  진짜 시각 사용(LS): 3~12 a 안의 최고 봉우리 주기 %.2f a, 정규화 파워 %.4f, 반치폭 주기 %.2f~%.2f a' % a)
print('  번호를 시각으로 사용(퇴적률 일정 가정): 주기 %.2f a, 정규화 파워 %.4f, 반치폭 주기 %.2f~%.2f a' % b)
out['demo1'] = dict(f=fgrid.tolist()[::4], p_ls=p_ls[::4].tolist(), p_naive=p_naive[::4].tolist(), age=age.tolist(), y=y.tolist(), P0=P0)

# ---------------------------------------------------------------- D. 시연 2: 145개 점, 4263년 (제1권 2장 설정)
print('\n== D. 시연 2 (시연값): 145개 점, 폭 4263년, 심은 주기 1000년과 500년')
rng = np.random.default_rng(145)
n2, L = 145, 4263.0
base = np.linspace(0, L, n2)
dmean = L / (n2 - 1)
t2 = np.sort(base + rng.uniform(-0.45, 0.45, n2) * dmean); t2[0] = 0.0; t2[-1] = L
d2 = np.diff(t2)
print('  평균 간격 %.2f년 (제1권 29년과 비교), 최소 %.1f, 최대 %.1f 년' % (d2.mean(), d2.min(), d2.max()))
y2 = 1.0 * np.sin(TWO_PI * t2 / 1000 + 0.3) + 0.6 * np.sin(TWO_PI * t2 / 500 + 2.0) + rng.standard_normal(n2)
y2c = y2 - y2.mean()
fg2 = np.arange(1 / L, 1 / (2 * dmean), 1 / (10 * L))
p2 = ss.lombscargle(t2, y2c, TWO_PI * fg2, normalize=True, floating_mean=True)
pk = [(1 / fg2[i], p2[i]) for i in range(1, len(p2) - 1) if p2[i] > p2[i - 1] and p2[i] > p2[i + 1]]
pk.sort(key=lambda x: -x[1])
print('  가장 낮은 진동수 1/L = %.2e 1/년 (주기 %.0f년), 칸 간격 1/(10L)로 10배 촘촘히 계산' % (1 / L, L))
print('  평균 간격 기준 나이키스트 주기 2*%.2f = %.1f년' % (dmean, 2 * dmean))
print('  상위 봉우리(주기 년, 정규화 파워):', ', '.join('%.0f / %.3f' % pk_ for pk_ in pk[:4]))
# 분산 설명 몫과 비교: 사인 두 개를 한꺼번에 맞춘 R^2
M = np.column_stack([np.sin(TWO_PI * t2 / 1000), np.cos(TWO_PI * t2 / 1000), np.sin(TWO_PI * t2 / 500), np.cos(TWO_PI * t2 / 500), np.ones(n2)])
c, *_ = np.linalg.lstsq(M, y2, rcond=None)
print('  두 사인을 동시에 맞춘 R^2 = %.3f' % (1 - np.sum((y2 - M @ c) ** 2) / np.sum((y2 - y2.mean()) ** 2)))
# 유의 수준: 섞기(백색) 대리 자료 2000개의 최대 파워 95% 분위수
B = 2000
mx = np.empty(B)
for i in range(B):
    mx[i] = ss.lombscargle(t2, rng.permutation(y2c), TWO_PI * fg2, normalize=True, floating_mean=True).max()
thr_mc = np.quantile(mx, 0.95)
ls = LombScargle(t2, y2)
thr_baluev = ls.false_alarm_level(0.05, method='baluev', minimum_frequency=fg2[0], maximum_frequency=fg2[-1])
print('  백색 잡음 귀무가설, 최대 파워의 95%% 문턱: 섞기 %d회 %.4f / astropy Baluev 근사 %.4f' % (B, thr_mc, thr_baluev))
print('  관측 최대 파워 %.3f (문턱 위: %s)' % (p2.max(), '예' if p2.max() > thr_mc else '아니오'))
out['demo2'] = dict(f=fg2.tolist()[::2], p=p2.tolist()[::2], t=t2.tolist(), y=y2.tolist(), thr=float(thr_mc))

# ---------------------------------------------------------------- E. 나이키스트 한계 위의 주기: 일정 간격 대 불규칙 간격 (제1권 계산 2-16과 비교)
print('\n== E. 평균 간격(약 29.6년)의 나이키스트 주기(약 59.2년)보다 짧은 40년 주기 (시연값)')
rng = np.random.default_rng(40)
P40 = 40.0
res = {}
noise40 = 0.3 * rng.standard_normal(n2)
fs_ = 1 / dmean                                   # 평균 표본 진동수
f_true = 1 / P40
f_low = abs(f_true - fs_)                          # 낮은 쪽 별칭
f_high = fs_ + f_low                               # 높은 쪽 별칭
cands = [('진짜', f_true), ('낮은 별칭', f_low), ('높은 별칭', f_high)]
print('  평균 표본 진동수 fs = %.5f 1/년. 진짜 주기 %.1f년, 낮은 별칭 주기 %.1f년, 높은 별칭 주기 %.1f년' % (fs_, P40, 1 / f_low, 1 / f_high))
for name, jit in (('일정 간격', 0.0), ('불규칙(간격의 +-45%)', 0.45)):
    tt = np.sort(base + rng.uniform(-jit, jit, n2) * dmean)
    yy = np.sin(TWO_PI * tt / P40 + 0.5) + noise40
    yy -= yy.mean()
    fgE = np.arange(1 / L, 0.06, 1 / (10 * L))
    pe = ss.lombscargle(tt, yy, TWO_PI * fgE, normalize=True, floating_mean=True)
    vals = {nm: float(pe[np.argmin(np.abs(fgE - fq_))]) for nm, fq_ in cands}
    print('  %s: 정규화 파워 진짜 %.3f, 낮은 별칭 %.3f, 높은 별칭 %.3f' % (name, vals['진짜'], vals['낮은 별칭'], vals['높은 별칭']))
    res[name] = vals
out['E'] = res


# ---------------------------------------------------------------- F. 일정 간격으로 보간하면 높은 진동수의 진폭이 줄어든다 (시연 1의 시간 눈금)
print('\n== F. 불규칙 시각의 사인파(진폭 1)를 평균 간격의 일정한 격자에 선형 보간했을 때 남는 진폭 (시연값)')
dtm = np.diff(age).mean()
tg = np.arange(0, age[-1], dtm)
for Pp in (2.5, 3.9, 5.2, 8.0):
    yy = np.sin(TWO_PI * age / Pp)
    lsp = float(np.atleast_1d(ss.lombscargle(age, yy - yy.mean(), np.array([TWO_PI / Pp]), normalize=True, floating_mean=True))[0])
    yi = np.interp(tg, age, yy)
    M = np.column_stack([np.sin(TWO_PI * tg / Pp), np.cos(TWO_PI * tg / Pp), np.ones_like(tg)])
    cc = np.linalg.lstsq(M, yi, rcond=None)[0]
    print('  주기 %.1f a: 원래 시각에서 LS 정규화 파워 %.3f, 보간한 일정 격자에서 맞춘 진폭 %.3f (참 진폭 1)' % (Pp, lsp, np.hypot(cc[0], cc[1])))
print('  격자 간격 %.3f a, 나이키스트 주기 %.3f a' % (dtm, 2 * dtm))

json.dump(out, open('results/ch04-02.json', 'w'))
print('\n총 실행 시간 %.2f s' % (time.perf_counter() - t0))
