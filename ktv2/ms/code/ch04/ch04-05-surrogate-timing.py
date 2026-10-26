# -*- coding: utf-8 -*-
"""4장 실습 4-12~4-15: 대리 자료(surrogate) 검정과 CPU 시간
(가) Lomb-Scargle를 행렬곱으로 한꺼번에 계산하는 방법을 scipy와 맞춰 본다.
(나) 대리 자료 수천~수십만 개의 계산 시간을 잰다.
(다) 순수 붉은 잡음 500개로 대리 자료 검정이 5%를 제대로 지키는지(보정) 본다.
(라) 3~8 a 띠 안에서 순수 붉은 잡음이 95% 문턱을 몇 번 넘는지 센다 (제1권 10장 ENSO 서술의 점검).
자료는 모두 시연값이다. GPU가 있으면 cupy로 같은 코드가 돈다. 이 컨테이너에는 GPU가 없어 CPU 경로만 실행했다.
실행: python3 ch04-05-surrogate-timing.py
"""
import os, time, json, platform, resource
import numpy as np, scipy, scipy.signal as ss, scipy.fft as sf
from scipy import optimize
try:
    import cupy as xp
    GPU = True
except Exception:
    xp = np
    GPU = False
def to_np(a): return xp.asnumpy(a) if GPU else a

t00 = time.perf_counter()
print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
print('논리 코어 수 %s, GPU(cupy) 사용 가능: %s -> %s' % (os.cpu_count(), '예' if GPU else '아니오', 'GPU 경로' if GPU else 'CPU 경로(numpy)'))
try:
    from threadpoolctl import threadpool_info
    print('BLAS:', [(d['internal_api'], d.get('num_threads')) for d in threadpool_info()])
except Exception as e:
    print('threadpoolctl 없음')
TWO_PI = 2 * np.pi
out = {}

# ---------------------------------------------------------------- 시연 자료: 퇴적률이 흔들리는 코어의 시각(4-2와 같은 설정)
z = np.arange(0, 552.0)
rate = 0.92 * (1 + 0.30 * np.sin(TWO_PI * z / 220.0 + 0.4))
age = np.concatenate([[0], np.cumsum(1.0 / (0.5 * (rate[1:] + rate[:-1])))])
N = len(age); T = age[-1]
fgrid = np.arange(1 / T, 0.45, 1 / (4 * T))
F = len(fgrid)
print('시료 %d개, 총 %.1f a, 진동수 칸 %d개 (칸 간격 1/(4T))' % (N, T, F))

def ls_prep(t, freqs):
    """Lomb-Scargle 한꺼번에 계산용 사전 계산: 시각과 진동수에만 달려 있다."""
    om = TWO_PI * freqs[None, :]
    tau = np.arctan2(np.sin(2 * om * t[:, None]).sum(0), np.cos(2 * om * t[:, None]).sum(0)) / (2 * om[0])
    arg = om * (t[:, None] - tau[None, :])
    C, S = np.cos(arg), np.sin(arg)
    return xp.asarray(C), xp.asarray(S), xp.asarray((C * C).sum(0)), xp.asarray((S * S).sum(0))
def ls_batch(Y, prep):
    """Y: (B, N) 평균을 뺀 자료. 반환: (B, F) 정규화 파워(scipy normalize=True, floating_mean=False와 같은 정의)."""
    C, S, cc, ss_ = prep
    Y = xp.asarray(Y)
    yc = Y @ C; ys = Y @ S
    return (yc * yc / cc + ys * ys / ss_) / (Y * Y).sum(axis=1, keepdims=True)

def ou_surrogates(times, tau, B, rng):
    """불규칙한 시각에서 정확한 AR(1)/OU 붉은 잡음 B개(분산 1)."""
    n = len(times)
    rho = np.exp(-np.diff(times) / tau)
    X = np.empty((B, n)); X[:, 0] = rng.standard_normal(B)
    E = rng.standard_normal((B, n - 1))
    for i in range(1, n):
        X[:, i] = rho[i - 1] * X[:, i - 1] + np.sqrt(1 - rho[i - 1] ** 2) * E[:, i - 1]
    return X

# ---------------------------------------------------------------- (가) 정확성
print('\n== (가) 행렬곱 방식을 scipy.signal.lombscargle과 맞춘다')
rng = np.random.default_rng(1)
prep = ls_prep(age, fgrid)
y = ou_surrogates(age, 5.0, 3, rng); y = y - y.mean(axis=1, keepdims=True)
Pb = to_np(ls_batch(y, prep))
Ps = np.array([ss.lombscargle(age, y[i], TWO_PI * fgrid, normalize=True) for i in range(3)])
print('  3개 계열, 진동수 %d개: 최대 절대 차이 %.2e, 최대 상대 차이 %.2e' % (F, np.abs(Pb - Ps).max(), (np.abs(Pb - Ps) / Ps.max()).max()))

# ---------------------------------------------------------------- (나) 시간
print('\n== (나) 대리 자료 B개를 만들고 Lomb-Scargle를 계산하는 시간 (CPU)')
# scipy 반복문: 일부만 재서 곱한다(곱셈 추정으로 표시)
reps = 20
yy = y[0]
t1 = time.perf_counter()
for _ in range(reps): ss.lombscargle(age, yy, TWO_PI * fgrid, normalize=True)
per_scipy = (time.perf_counter() - t1) / reps
print('  scipy lombscargle 반복문: 실측 %d회 평균 %.1f ms/회 -> B=1000: %.0f s, B=10000: %.0f s (곱셈 추정)' % (reps, per_scipy * 1e3, per_scipy * 1e3, per_scipy * 1e4))
from astropy.timeseries import LombScargle
t1 = time.perf_counter()
for _ in range(50): LombScargle(age, yy, fit_mean=False, center_data=False).power(fgrid, method='fast', normalization='psd')
per_astro = (time.perf_counter() - t1) / 50
print('  astropy LombScargle(fast, 근사) 반복문: 실측 50회 평균 %.1f ms/회 -> B=1000: %.1f s, B=10000: %.0f s (곱셈 추정)' % (per_astro * 1e3, per_astro * 1e3, per_astro * 1e4))
rows = []
print('  행렬곱 방식(이 장의 ls_batch), 대리 자료 생성(OU 점화식)과 계산을 나누어 잰다:')
rng = np.random.default_rng(2)
for B in (1000, 5000, 20000, 100000):
    chunk = min(5000, B)
    tg = tc = 0.0
    for _ in range(B // chunk):
        a = time.perf_counter()
        Y = ou_surrogates(age, 5.0, chunk, rng); Y -= Y.mean(axis=1, keepdims=True)
        b = time.perf_counter()
        P = ls_batch(Y, prep)
        if GPU: xp.cuda.Stream.null.synchronize()
        c = time.perf_counter()
        tg += b - a; tc += c - b
    rows.append((B, tg, tc))
    print('    B=%6d: 생성 %.2f s, LS 계산 %.2f s, 합 %.2f s (LS만 %.3f ms/개)' % (B, tg, tc, tg + tc, tc / B * 1e3))
out['timing_ls'] = rows
out['per_scipy'] = per_scipy
out['per_astro'] = per_astro
print('  scipy 반복문 대비 LS 계산 속도비(B=20000 기준): %.0f 배' % (per_scipy / (rows[2][2] / rows[2][0])))
print('  참고: 이 컨테이너의 GPU 실행 시간은 "z840 실행 필요"이다.')

# 일정 간격 FFT 방식
print('\n  일정 간격 N=414 기록의 FFT 대리 자료 검정(AR(1) 0.72, rfft):')
rowsf = []
rng = np.random.default_rng(3)
for B in (1000, 10000, 100000, 1000000):
    chunk = 50000 if B > 50000 else B
    tg = tc = 0.0
    mx = 0.0
    for _ in range(max(1, B // chunk)):
        a = time.perf_counter()
        E = rng.standard_normal((chunk, 414 + 100))
        X = ss.lfilter([1.0], [1.0, -0.72], E, axis=1)[:, 100:]
        b = time.perf_counter()
        Pw = np.abs(sf.rfft(X - X.mean(axis=1, keepdims=True), axis=1)) ** 2
        mx = max(mx, Pw[:, 1:].max())
        c = time.perf_counter()
        tg += b - a; tc += c - b
    rowsf.append((B, tg, tc))
    print('    B=%7d: 생성 %.2f s, rfft %.2f s, 합 %.2f s' % (B, tg, tc, tg + tc))
out['timing_fft'] = rowsf
print('  지금까지 프로세스의 최대 상주 메모리 %.0f MB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))

# ---------------------------------------------------------------- (다) 보정: 순수 붉은 잡음 R개로 5% 점검
print('\n== (다) 대리 자료 검정은 5%%를 지키는가: 순수 붉은 잡음(OU, tau=5 a) %d개에 적용' % 500)
R, B = 500, 400
tau_true = 5.0
lo_f, hi_f = 1 / 8.0, 1 / 3.0
band = (fgrid >= lo_f) & (fgrid <= hi_f)
nb_ind = (hi_f - lo_f) * T
print('  띠 3~8 a(진동수 %.3f~%.3f)의 독립 칸 수 약 (1/3-1/8) x T = %.0f개' % (lo_f, hi_f, nb_ind))
def fit_tau(x, times):
    x = x - x.mean(); s2 = x.var(); dt = np.diff(times)
    def nll(logtau):
        rho = np.exp(-dt / np.exp(logtau))
        v = s2 * (1 - rho ** 2)
        return np.sum((x[1:] - rho * x[:-1]) ** 2 / v + np.log(v))
    r = optimize.minimize_scalar(nll, bounds=(np.log(0.2), np.log(200.0)), method='bounded')
    return float(np.exp(r.x))
# 백색(섞기) 대리 자료의 띠 최대 파워 95% 문턱: 자료와 상관없이 한 번만
rng = np.random.default_rng(10)
Yw = rng.standard_normal((4000, N)); Yw -= Yw.mean(axis=1, keepdims=True)
Pw_ = to_np(ls_batch(Yw, prep))
thr_white = np.quantile(Pw_[:, band].max(axis=1), 0.95)
thr_white_all = np.quantile(Pw_.max(axis=1), 0.95)
print('  백색 잡음 대리 4000개: 최대 정규화 파워의 95%% 문턱 — 띠(3~8 a) 안 %.4f, 전 진동수 %.4f' % (thr_white, thr_white_all))
t1 = time.perf_counter()
rng = np.random.default_rng(11)
rej_white = rej_ar = rej_white_all = rej_ar_all = 0
tau_hats = []
cnt_pt = []; runs_pt = []; fam_any = 0
for rr in range(R):
    x = ou_surrogates(age, tau_true, 1, rng)[0]
    xc = x - x.mean()
    p_obs = to_np(ls_batch(xc[None, :], prep))[0]
    th = fit_tau(x, age); tau_hats.append(th)
    Ys = ou_surrogates(age, th, B, rng); Ys -= Ys.mean(axis=1, keepdims=True)
    Ps = to_np(ls_batch(Ys, prep))
    mx = Ps[:, band].max(axis=1)
    pval = (1 + (mx >= p_obs[band].max()).sum()) / (B + 1)
    rej_ar += pval < 0.05
    rej_white += p_obs[band].max() > thr_white
    rej_white_all += p_obs.max() > thr_white_all
    rej_ar_all += ((1 + (Ps.max(axis=1) >= p_obs.max()).sum()) / (B + 1)) < 0.05
    q95 = np.quantile(Ps, 0.95, axis=0)          # 진동수마다 95% 문턱(점별)
    ex = (p_obs > q95) & band
    cnt_pt.append(int(ex.sum() / 4.0))             # 칸 간격이 1/(4T)이므로 독립 칸 수로 환산(근사)
    d = np.diff(np.concatenate([[0], ex.astype(int), [0]]))
    runs_pt.append(int((d == 1).sum()))
    fam_any += ex.any()
dt_c = time.perf_counter() - t1
print('  소요 시간 %.1f s (대리 자료 %d개 x %d = %d개)' % (dt_c, R, B, R * B))
tau_hats = np.array(tau_hats)
print('  tau 추정: 중앙값 %.2f a (참값 %.1f), 5~95%% 범위 %.2f~%.2f' % (np.median(tau_hats), tau_true, *np.quantile(tau_hats, [.05, .95])))
print('  5% 수준 기각 비율(참값은 모두 붉은 잡음이므로 5%여야 한다; 500개이므로 표준오차 약 0.010)')
print('    띠(3~8 a) 안의 최대 파워: 백색 문턱 %.3f / 붉은 잡음 대리 자료(tau 추정) %.3f' % (rej_white / R, rej_ar / R))
print('    전 진동수의 최대 파워:   백색 문턱 %.3f / 붉은 잡음 대리 자료(tau 추정) %.3f' % (rej_white_all / R, rej_ar_all / R))
out['calib'] = dict(white=rej_white / R, ar=rej_ar / R, white_all=rej_white_all / R, ar_all=rej_ar_all / R, R=R, B=B, thr_white=float(thr_white))

# ---------------------------------------------------------------- (라) 점별 95% 문턱과 띠 안의 봉우리 수
cnt_pt = np.array(cnt_pt); runs_pt = np.array(runs_pt)
print('\n== (라) 순수 붉은 잡음에서 3~8 a 띠 안에 점별 95% 문턱을 넘는 봉우리 수')
print('  넘는 칸 수(독립 칸으로 환산): 평균 %.2f, 중앙값 %.1f (독립 칸 약 %.0f개의 5%% = %.1f)' % (cnt_pt.mean(), np.median(cnt_pt), nb_ind, 0.05 * nb_ind))
print('  넘는 봉우리(연속 구간) 수: 평균 %.2f, 분포 0개 %.3f, 1~4개 %.3f, 5개 이상 %.3f' % (runs_pt.mean(), (runs_pt == 0).mean(), ((runs_pt >= 1) & (runs_pt <= 4)).mean(), (runs_pt >= 5).mean()))
print('  독립 칸 환산 수가 3개 이상인 실현의 비율 %.3f, 5개 이상 %.3f' % ((cnt_pt >= 3).mean(), (cnt_pt >= 5).mean()))
print('  하나라도 넘는 실현의 비율 %.3f' % (fam_any / R))
print('  (제1권 10장: Wang 등(2011)은 95% 수준에서 5개 주기를 보고. 위 수치는 이 책의 가상 붉은 잡음에서 점별 문턱 위의 봉우리가 평균 몇 개 나오는지를 센 것이며 논문의 방법(REDFIT, 구간 평균)과는 다르다.)')
out['band'] = dict(cnt_mean=float(cnt_pt.mean()), runs_mean=float(runs_pt.mean()), runs_hist=np.bincount(np.minimum(runs_pt, 25), minlength=26).tolist(), cnt_ge5=float((cnt_pt >= 5).mean()), cnt_ge3=float((cnt_pt >= 3).mean()), fam=fam_any / R)
json.dump(out, open('results/ch04-05.json', 'w'))
print('\n총 실행 시간 %.1f s, 최대 상주 메모리 %.0f MB' % (time.perf_counter() - t00, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
