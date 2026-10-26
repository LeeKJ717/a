# -*- coding: utf-8 -*-
"""5장 실습 5-6: 회귀 보정·검증과 RE, CE, 그리고 그 불확실성.
모든 연별 자료는 이 책이 만든 시연값(가상 값)이다. Lyu 등(2016)의 연별 자료가 아니다.
시연의 모양만 논문과 맞춘다: 58년(1956~2013), 반 기간 29년, 기온의 평균 7.66, 변환식 Y = 2.987 X + 4.829를 만드는 쪽의 참 모형으로 쓴다.
(나무 쪽에 잡음을 넣으므로 이 자료에서 다시 맞춘 기울기는 2.987보다 작아진다. 시연 자료의 r은 논문의 0.757과 같지 않다.)
A. 6년 시연값의 모든 짝짓기(6! = 720가지)로 RE, CE가 우연히 이만큼 나올 확률을 정확히 센다.
B. 58년 시연 자료에서 분할 보정·검증(앞 29년 -> 뒤 29년, 뒤 -> 앞)의 RE, CE, 부호 검정.
C. RE는 양수인데 CE는 음수가 되는 경우(시연값).
D. 검증 연도 재표집, 보정 연도 재표집, 블록 재표집으로 RE와 CE의 구간을 구한다. 반복 횟수에 따른 안정.
실행: python3 re-ce-demo.py | tee re-ce-demo.log
"""
import time, platform, itertools, json
J = {'intervals': {}, 'bstab': []}
from math import comb, sqrt
import numpy as np
import scipy
from scipy import stats

T0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))


def re_ce(obs, est, cal_mean):
    sse = ((obs - est) ** 2).sum()
    re = 1 - sse / ((obs - cal_mean) ** 2).sum()
    ce = 1 - sse / ((obs - obs.mean()) ** 2).sum()
    return re, ce


print('\n== A. 6년 시연값(제1권 계산 11-7): 짝짓기를 모두 바꾸어 본다 ==')
obs6 = np.array([7.0, 7.4, 7.9, 7.2, 8.1, 7.6]); est6 = np.array([7.2, 7.3, 7.6, 7.5, 7.8, 7.5])
re0, ce0 = re_ce(obs6, est6, 7.5)
print('관측한 짝짓기: RE = %.4f, CE = %.4f' % (re0, ce0))
res = np.array([re_ce(obs6, est6[list(p)], 7.5) for p in itertools.permutations(range(6))])
print('모든 짝짓기 6! = %d가지 (추정값의 순서만 바꿈; 값의 모임은 그대로)' % len(res))
print('RE >= %.4f 인 짝짓기 %d개 -> 정확한 단측 p = %d/720 = %.4f' % (re0, int((res[:, 0] >= re0 - 1e-12).sum()), int((res[:, 0] >= re0 - 1e-12).sum()), (res[:, 0] >= re0 - 1e-12).mean()))
print('CE >= %.4f 인 짝짓기 %d개 -> 정확한 단측 p = %.4f' % (ce0, int((res[:, 1] >= ce0 - 1e-12).sum()), (res[:, 1] >= ce0 - 1e-12).mean()))
print('우연한 짝짓기에서 RE > 0인 비율 %.3f, CE > 0인 비율 %.3f (0 이상이면 통과라는 기준이 우연에서도 얼마나 통과되는가)' % ((res[:, 0] > 0).mean(), (res[:, 1] > 0).mean()))
print('가능한 가장 작은 p = 1/720 = %.4f (6개 짝으로는 이보다 작은 p를 얻을 수 없다)' % (1 / 720))
print('같은 값의 모임에서 RE 최대 %.4f, 최소 %.4f' % (res[:, 0].max(), res[:, 0].min()))

# ---------------------------------------------------------------- 시연 자료
years = np.arange(1956, 2014)
NY = len(years)
A0, B0 = 4.829, 2.987


def make(seed, trend, sdw, phi, sde):
    rg = np.random.default_rng(seed)
    w = np.zeros(NY + 50)
    e = rg.normal(0, 1, NY + 50)
    for i in range(1, NY + 50):
        w[i] = phi * w[i - 1] + sqrt(1 - phi * phi) * e[i]
    w = w[50:]
    Y = 7.66 + sdw * w + trend * (years - years.mean())
    X = (Y - A0) / B0 + rg.normal(0, sde, NY)
    return X, Y


def fit(X, Y):
    b, a = np.polyfit(X, Y, 1)
    return a, b


def split_report(X, Y, label, first=True):
    h = NY // 2
    parts = (('앞 29년(1956~1984)에서 보정, 뒤 29년(1985~2013)에서 검증', slice(0, h), slice(h, NY)),
             ('뒤 29년에서 보정, 앞 29년에서 검증', slice(h, NY), slice(0, h)))
    out = []
    for nm, c, v in parts:
        a, b = fit(X[c], Y[c])
        est = a + b * X[v]
        re, ce = re_ce(Y[v], est, Y[c].mean())
        r = np.corrcoef(Y[v], est)[0, 1]
        agree = int((np.sign(Y[v] - Y[c].mean()) == np.sign(est - Y[c].mean())).sum())
        p2 = stats.binomtest(agree, h, 0.5).pvalue
        print('  %s: 보정 r=%.3f, 식 Y = %.3f X + %.3f, 검증 r=%.3f, RE=%.3f, CE=%.3f, 부호 일치 %d/%d (양쪽 p=%.4f)' % (nm, np.corrcoef(X[c], Y[c])[0, 1], b, a, r, re, ce, agree, h, p2))
        out.append((a, b, re, ce))
    return out


print('\n== B. 시연 자료 1: 추세 없음 (Y의 모형 표준편차 0.53, 자기상관 0.3, 나무 쪽 잡음 0.153) ==')
X1, Y1 = make(2016, 0.0, 0.53, 0.3, 0.153)
print('전 기간 r(X, Y) = %.3f, Y 평균 %.3f, Y 표준편차 %.3f' % (np.corrcoef(X1, Y1)[0, 1], Y1.mean(), Y1.std(ddof=1)))
a_all, b_all = fit(X1, Y1)
print('전 기간 식: Y = %.3f X + %.3f (모형의 참값 2.987, 4.829)' % (b_all, a_all))
S1 = split_report(X1, Y1, '추세 없음')

print('\n== C. 시연 자료 2: 뒤쪽이 더 따뜻한 추세 (0.02 °C/년), 해마다의 신호는 약함 ==')
X2, Y2 = make(2017, 0.02, 0.40, 0.3, 0.25)
print('전 기간 r(X, Y) = %.3f, 앞 29년 평균 %.3f, 뒤 29년 평균 %.3f' % (np.corrcoef(X2, Y2)[0, 1], Y2[:29].mean(), Y2[29:].mean()))
S2 = split_report(X2, Y2, '추세')
# 추세를 뺀 해마다 값에서의 상관
d2 = np.polyfit(years, Y2, 1); dx2 = np.polyfit(years, X2, 1)
print('추세를 뺀 뒤 r(X, Y) = %.3f (해마다의 일치)' % np.corrcoef(X2 - np.polyval(dx2, years), Y2 - np.polyval(d2, years))[0, 1])
print('이 자료에서 (RE, CE): 앞->뒤 (%.3f, %.3f), 뒤->앞 (%.3f, %.3f)' % (S2[0][2], S2[0][3], S2[1][2], S2[1][3]))


def boot_verif(X, Y, cal, ver, B, seed, block=1):
    """검증 연도를 재표집(block>1이면 이동 블록)해 RE, CE의 분포. 보정 식은 고정."""
    a, b = fit(X[cal], Y[cal]); cm = Y[cal].mean()
    yv, ev = Y[ver], a + b * X[ver]
    n = len(yv)
    rg = np.random.default_rng(seed)
    if block == 1:
        idx = rg.integers(0, n, size=(B, n))
    else:
        nb = -(-n // block)
        st = rg.integers(0, n - block + 1, size=(B, nb))
        idx = (st[:, :, None] + np.arange(block)[None, None, :]).reshape(B, -1)[:, :n]
    o = yv[idx]; e = ev[idx]
    sse = ((o - e) ** 2).sum(axis=1)
    re = 1 - sse / ((o - cm) ** 2).sum(axis=1)
    ce = 1 - sse / ((o - o.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
    return re, ce


def boot_calib(X, Y, cal, ver, B, seed):
    """보정 연도를 재표집해 식을 다시 맞추고 검증 기간에서 RE, CE를 구한다(식의 불확실성 포함)."""
    xc, yc = X[cal], Y[cal]
    n = len(xc)
    rg = np.random.default_rng(seed)
    idx = rg.integers(0, n, size=(B, n))
    xb, yb = xc[idx], yc[idx]
    mx, my = xb.mean(axis=1, keepdims=True), yb.mean(axis=1, keepdims=True)
    sxx = ((xb - mx) ** 2).sum(axis=1)
    ok = sxx > 0
    b = ((xb - mx) * (yb - my)).sum(axis=1) / np.where(ok, sxx, 1)
    a = my[:, 0] - b * mx[:, 0]
    yv = Y[ver]
    est = a[:, None] + b[:, None] * X[ver][None, :]
    sse = ((yv[None, :] - est) ** 2).sum(axis=1)
    re = 1 - sse / ((yv[None, :] - yb.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
    ce = 1 - sse / ((yv - yv.mean()) ** 2).sum()
    return re[ok], ce[ok], a[ok], b[ok]


h = NY // 2
cal, ver = slice(0, h), slice(h, NY)
print('\n== D. RE와 CE의 구간 (시연 자료 1, 앞 29년 보정 -> 뒤 29년 검증) ==')
a, b = fit(X1[cal], Y1[cal]); re_o, ce_o = re_ce(Y1[ver], a + b * X1[ver], Y1[cal].mean())
print('관측: RE = %.3f, CE = %.3f' % (re_o, ce_o))
for nm, fn in (('검증 연도 재표집(식 고정)', lambda B, s: boot_verif(X1, Y1, cal, ver, B, s)),
               ('이동 블록 재표집(블록 5, 식 고정)', lambda B, s: boot_verif(X1, Y1, cal, ver, B, s, 5)),
               ('보정 연도 재표집(식 다시 맞춤)', lambda B, s: boot_calib(X1, Y1, cal, ver, B, s)[:2])):
    re, ce = fn(20000, 1)
    J['intervals'][nm] = dict(obs_re=float(re_o), obs_ce=float(ce_o), re=[float(v) for v in np.percentile(re, [2.5, 97.5])], ce=[float(v) for v in np.percentile(ce, [2.5, 97.5])])
    print('  %-30s RE 2.5/50/97.5%% = %.3f / %.3f / %.3f, RE<0 비율 %.4f | CE = %.3f / %.3f / %.3f, CE<0 비율 %.4f' % (
        nm, *np.percentile(re, [2.5, 50, 97.5]), (re < 0).mean(), *np.percentile(ce, [2.5, 50, 97.5]), (ce < 0).mean()))

print('\n  재표집 횟수 B에 따른 구간 끝의 흔들림 (검증 연도 재표집, 시드 20개)')
print('  %10s %24s %24s %10s' % ('B', 'RE 2.5% 끝 평균 / 표준편차', 'RE 97.5% 끝 평균 / 표준편차', '시간(초)'))
for B in (100, 1000, 10000, 100000, 1000000):
    reps = 20 if B <= 100000 else 5
    t = time.perf_counter(); L = []; U = []
    for s in range(reps):
        tot_re = []
        left = B; k = 0
        while left > 0:
            m = min(100000, left)
            re, _ = boot_verif(X1, Y1, cal, ver, m, 40000 + s * 100 + k); tot_re.append(re); left -= m; k += 1
        re = np.concatenate(tot_re)
        lo, hi = np.percentile(re, [2.5, 97.5]); L.append(lo); U.append(hi)
    J['bstab'].append(dict(B=B, lo=float(np.mean(L)), lo_sd=float(np.std(L, ddof=1)), hi=float(np.mean(U)), hi_sd=float(np.std(U, ddof=1))))
    print('  %10s %13.4f / %-9.4f %13.4f / %-9.4f %10.2f' % ('{:,}'.format(B), np.mean(L), np.std(L, ddof=1), np.mean(U), np.std(U, ddof=1), time.perf_counter() - t))

print('\n== D2. 시연 자료 2(추세 있음)의 구간: 앞 -> 뒤 보정·검증 ==')
a, b = fit(X2[cal], Y2[cal]); re_o, ce_o = re_ce(Y2[ver], a + b * X2[ver], Y2[cal].mean())
print('관측: RE = %.3f, CE = %.3f' % (re_o, ce_o))
re, ce = boot_verif(X2, Y2, cal, ver, 20000, 2)
J['intervals']['추세 있음: 검증 연도 재표집'] = dict(obs_re=float(re_o), obs_ce=float(ce_o), re=[float(v) for v in np.percentile(re, [2.5, 97.5])], ce=[float(v) for v in np.percentile(ce, [2.5, 97.5])])
print('  검증 연도 재표집: RE %.3f ~ %.3f, CE %.3f ~ %.3f, CE<0 비율 %.3f' % (*np.percentile(re, [2.5, 97.5]), *np.percentile(ce, [2.5, 97.5]), (ce < 0).mean()))
re, ce, aa, bb = boot_calib(X2, Y2, cal, ver, 20000, 3)
J['intervals']['추세 있음: 보정 연도 재표집'] = dict(obs_re=float(re_o), obs_ce=float(ce_o), re=[float(v) for v in np.percentile(re, [2.5, 97.5])], ce=[float(v) for v in np.percentile(ce, [2.5, 97.5])])
print('  보정 연도 재표집: RE %.3f ~ %.3f, CE %.3f ~ %.3f, CE<0 비율 %.3f' % (*np.percentile(re, [2.5, 97.5]), *np.percentile(ce, [2.5, 97.5]), (ce < 0).mean()))

print('\n== E. 식의 불확실성이 복원값에 전파되는 모습 (시연 자료 1 전 기간 회귀, 예측 X0에서) ==')
n = NY
xm = X1.mean(); sxx = ((X1 - xm) ** 2).sum()
a, b = fit(X1, Y1)
resid = Y1 - (a + b * X1); s = sqrt((resid ** 2).sum() / (n - 2))
print('전 기간 회귀: a = %.3f, b = %.3f, 잔차 표준편차 s = %.3f, x 평균 %.3f, Sxx = %.4f' % (a, b, s, xm, sxx))
tc = stats.t.ppf(0.975, n - 2)
rg = np.random.default_rng(77)
B = 200000
idx = rg.integers(0, n, size=(B, n))
xb, yb = X1[idx], Y1[idx]
mx, my = xb.mean(axis=1), yb.mean(axis=1)
bb = ((xb - mx[:, None]) * (yb - my[:, None])).sum(axis=1) / ((xb - mx[:, None]) ** 2).sum(axis=1)
ab = my - bb * mx
res_b = yb - (ab[:, None] + bb[:, None] * xb)
sb = np.sqrt((res_b ** 2).sum(axis=1) / (n - 2))
print('%8s %10s %24s %24s %24s' % ('X0', '예측 Y', '평균의 95% 구간(공식)', '평균의 95% 구간(쌍 부트스트랩)', '새 해의 95% 예측구간(공식)'))
for x0 in (xm - 0.3, xm, xm + 0.3):
    yh = a + b * x0
    se_mean = s * sqrt(1 / n + (x0 - xm) ** 2 / sxx)
    se_new = s * sqrt(1 + 1 / n + (x0 - xm) ** 2 / sxx)
    lo_b, hi_b = np.percentile(ab + bb * x0, [2.5, 97.5])
    print('%8.3f %10.3f %10.3f ~ %-10.3f %10.3f ~ %-10.3f %10.3f ~ %-10.3f' % (x0, yh, yh - tc * se_mean, yh + tc * se_mean, lo_b, hi_b, yh - tc * se_new, yh + tc * se_new))
print('(평균의 구간은 식의 불확실성만, 예측구간은 거기에 한 해의 흩어짐 s를 더한 것이다.)')
print('쌍 부트스트랩 B = %s, 기울기의 표준오차: 공식 %.4f, 부트스트랩 %.4f' % ('{:,}'.format(B), s / sqrt(sxx), bb.std(ddof=1)))
print('\n걸린 시간 %.1f초' % (time.perf_counter() - T0))
json.dump(J, open('re-ce-demo.json', 'w'))
