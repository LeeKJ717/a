# -*- coding: utf-8 -*-
"""13장 계산 13-1 ~ 13-7. 입력은 논문이 적은 숫자이고, 가상 계열과 가상 값은 '시연값'이다.
실행(작업 폴더 /home/claude/book4): python3 ms/code/ch13/calc13.py > ms/code/ch13/calc13.log
난수 시드는 계산마다 고정했다.
"""
import os, json, warnings
warnings.filterwarnings('ignore', message='Mean of empty slice')
import numpy as np
from scipy.signal import lfilter
from scipy.stats import binom, norm, t as tdist

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}


def ar1(n_series, n, rho, rng):
    e = rng.standard_normal((n_series, n + 200))
    x = lfilter([1.0], [1.0, -rho], e, axis=1)[:, 200:]
    return x / np.sqrt(1.0 / (1.0 - rho ** 2))      # 분산 1로 맞춘다


def run_mean(x, w):
    c = np.cumsum(np.pad(x, ((0, 0), (1, 0))), axis=1)
    return (c[:, w:] - c[:, :-w]) / w


print('=== 계산 13-1. 가장 따뜻한 51년 창이 기록 끝에 놓일 우연의 확률(가상 계열, 시연값) ===')
N, W = 2000, 51
rng = np.random.default_rng(1301)
nwin = N - W + 1
print('기록 길이 %d년, 창 %d년, 창의 수 %d개. 교환 가능한 계열이면 마지막 %d개 창 중 하나일 기준 확률 = %d/%d = %.4f' % (N, W, nwin, W, W, nwin, W / nwin))
res = {}
for rho in (0.0, 0.3, 0.6, 0.8, 0.9, 0.95):
    cnt51 = cnt100 = tot = 0
    for _ in range(10):
        x = ar1(2000, N, rho, rng)
        m = run_mean(x, W)
        am = m.argmax(axis=1)
        cnt51 += int((am >= nwin - W).sum()); cnt100 += int((am >= nwin - 100).sum()); tot += am.size
    res[rho] = (cnt51 / tot, cnt100 / tot)
    print('  연 단위 자기상관 rho=%.2f: 가장 따뜻한 창이 마지막 51개 창 안 %.4f, 마지막 100개 창 안 %.4f (표본 %d개)' % (rho, cnt51 / tot, cnt100 / tot, tot))
OUT['edge'] = {str(k): v for k, v in res.items()}
print('  추세 없는 가상 계열에서 마지막 창이 가장 따뜻할 확률은 rho가 커지면 기준 확률의 몇 배가 되는가:', {k: round(v[0] / (W / nwin), 2) for k, v in res.items()})
print('  Neukom 등(2019)의 "지구 면적의 98%에서 가장 따뜻한 51년이 20세기 후반"은 위 확률(2.6~수 %)과 한 자리 이상 다르다.')

print()
print('=== 계산 13-2. 칸마다 가장 추운 창이 같은 때일 확률: 공통 신호의 비중에 따른 변화(가상 격자, 시연값) ===')
rng = np.random.default_rng(1302)
G, N2 = 400, 1850
W2 = 51
res2 = {}
for wshare in (0.0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.80):
    shares = []
    for rep in range(30):
        g = ar1(1, N2, 0.5, rng)
        e = ar1(G, N2, 0.5, rng)
        x = np.sqrt(wshare) * g + np.sqrt(1 - wshare) * e
        m = run_mean(x, W2)
        am = m.argmin(axis=1)
        hist = np.bincount(am // W2)
        # 가장 많이 모인 51년 칸 + 이웃 칸을 합친 비율 (경계에 걸치는 것을 줄이려 인접 두 칸)
        best = max(hist[i] + (hist[i + 1] if i + 1 < len(hist) else 0) for i in range(len(hist)))
        shares.append(best / G)
    res2[wshare] = (float(np.median(shares)), float(np.percentile(shares, 5)), float(np.percentile(shares, 95)))
    print('  공통 신호 분산 비중 %.2f: 같은 인접 두 칸(약 102년)에 가장 추운 창이 든 격자 비율 중앙 %.3f (5~95%%: %.3f~%.3f)' % (wshare, *res2[wshare]))
OUT['coh'] = {str(k): v for k, v in res2.items()}
print('  참고: 논문의 PCR 한 구성원에서 같은 소빙기 최저 창을 공유한 격자 24%, 잡음 대조 중앙 37~67%(20세기 따뜻한 창), 실제 20세기 98%.')
print('  공통 추세를 마지막 100년에 더하면(상승 3 표준편차) 가장 따뜻한 창 일치율:')
for wshare in (0.0, 0.2):
    g = ar1(1, N2, 0.5, rng)
    e = ar1(G, N2, 0.5, rng)
    x = np.sqrt(wshare) * g + np.sqrt(1 - wshare) * e
    ramp = np.zeros(N2); ramp[-100:] = np.linspace(0, 3.0, 100)
    x = x + ramp
    m = run_mean(x, W2); am = m.argmax(axis=1)
    hist = np.bincount(am // W2)
    best = max(hist[i] + (hist[i + 1] if i + 1 < len(hist) else 0) for i in range(len(hist)))
    print('    공통 비중 %.2f + 마지막 100년 추세 3: 같은 인접 두 칸 비율 %.3f' % (wshare, best / G))

print()
print('=== 계산 13-3. 대리지표 거르기: 우연의 상관이 "유의"하게 나오는 비율(가상 계열, 시연값)과 개수의 산술 ===')
print('논문의 개수: Emile-Geay 등(2017) 기록 692개, 지점 648개 → 지점당 %.3f개; 거의 절반이 HadCRUT4.2와 유의. Neukom 등(2019): 688 → 257 → 210' % (692 / 648))
print('  688 → 257: %.1f%% 남음, 257 → 210: %.1f%% 남음, 688 → 210: %.1f%% 남음, 제외 %d개' % (257 / 688 * 100, 210 / 257 * 100, 210 / 688 * 100, 688 - 210))
print('  692의 절반 = %d개. 독립 잡음이 5%%에서 우연히 유의해 보일 개수 = %.1f개' % (692 // 2, 692 * 0.05))
rng = np.random.default_rng(1303)
def fp(n, rho_p, rho_t, trend_t=0.0, trend_p=0.0, reps=20000):
    x = ar1(reps, n, rho_p, rng); y = ar1(reps, n, rho_t, rng)
    tt = np.linspace(-1, 1, n)
    x = x + trend_p * tt; y = y + trend_t * tt
    xm = x - x.mean(1, keepdims=True); ym = y - y.mean(1, keepdims=True)
    r = (xm * ym).sum(1) / np.sqrt((xm ** 2).sum(1) * (ym ** 2).sum(1))
    tv = r * np.sqrt((n - 2) / (1 - r ** 2))
    p_naive = 2 * tdist.sf(np.abs(tv), n - 2)
    # 유효 표본수 보정(자기상관의 참값 rho로 계산)
    neff = max(3.0, n * (1 - rho_p * rho_t) / (1 + rho_p * rho_t))
    tv2 = r * np.sqrt((neff - 2) / (1 - r ** 2))
    p_adj = 2 * tdist.sf(np.abs(tv2), neff - 2)
    return float((p_naive < 0.05).mean()), float((p_adj < 0.05).mean()), neff
OUT['fp'] = []
print('  (a) 두 계열 모두 추세 없음. 표본 길이 n, 자기상관 rho(두 계열 같게):')
for n in (85, 165):
    for rho in (0.0, 0.3, 0.5, 0.7, 0.9):
        a, b, neff = fp(n, rho, rho)
        OUT['fp'].append((n, rho, a, b, neff))
        print('    n=%3d rho=%.1f: 보정 없는 검정 %.3f, 유효 표본수 보정(neff=%.1f) %.3f' % (n, rho, a, neff, b))
print('  (b) 기온 쪽에 추세(+2 표준편차 폭), 대리지표는 추세 없는 독립 잡음, n=85:')
for rho in (0.0, 0.5, 0.7):
    a, b, neff = fp(85, rho, rho, trend_t=2.0)
    print('    rho=%.1f: 보정 없는 검정 %.3f, 보정 %.3f' % (rho, a, b))
print('  (c) 두 계열 모두 같은 방향의 추세(+1.5 표준편차 폭씩), 서로 독립 잡음, n=85, rho=0.5:')
a, b, neff = fp(85, 0.5, 0.5, trend_t=1.5, trend_p=1.5)
print('    보정 없는 검정 %.3f, 보정 %.3f (추세를 같이 가진 두 계열은 인과 없이도 유의해진다)' % (a, b))

print()
print('=== 계산 13-4. 나이테 긴 변동이 살아남는가: 계열 길이와 표준화 방법(가상 나무, 시연값) ===')
print('Esper 등(2002): 계열 1,205개 = 443 + 762 = %d, 지점 14개, 800~1990년(%d년), 계열당 평균 %.1f개/지점' % (443 + 762, 1990 - 800 + 1, 1205 / 14))
rng = np.random.default_rng(1304)
T = 1100
yrs = np.arange(T)
# 가상 기후: 주기 600, 250, 90년의 사인. 나이테 지수는 1 + AMP*기후 + 잡음으로 만든다.
clim = 1.0 * np.sin(2 * np.pi * yrs / 600 + 0.7) + 0.7 * np.sin(2 * np.pi * yrs / 250 + 2.0) + 0.5 * np.sin(2 * np.pi * yrs / 90 + 4.0)
clim = clim / clim.std()
AMP, NOISE, NTREE, MINCOV, SW = 0.25, 0.15, 600, 30, 201
def smooth(x, w):
    k = np.ones(w) / w
    return np.convolve(x, k, mode='same')
def sim(L):
    rec = np.full((NTREE, T), np.nan)
    ages = np.full((NTREE, T), np.nan)
    for i in range(NTREE):
        start = rng.integers(0, T - L + 1)
        a = np.arange(L)
        growth = 0.4 + np.exp(-a / (L / 4.0))            # 나이에 따라 줄어드는 성장 곡선(음의 지수)
        rec[i, start:start + L] = growth * (1 + AMP * clim[start:start + L] + NOISE * rng.standard_normal(L))
        ages[i, start:start + L] = a
    return rec, ages
def standardize_ind(rec):
    idx = np.full_like(rec, np.nan)
    for i in range(rec.shape[0]):
        m = ~np.isnan(rec[i])
        yv = rec[i, m]; tv = np.arange(m.sum())
        fit = np.polyval(np.polyfit(tv / tv.size, yv, 3), tv / tv.size)      # 나무마다 3차 다항식을 맞춰 나눈다(개별 표준화의 단순한 꼴)
        idx[i, m] = yv / fit
    return np.nanmean(idx, axis=0)
def standardize_rcs(rec, ages):
    ma = int(np.nanmax(ages)) + 1
    rc = np.array([np.nanmean(rec[ages == a]) for a in range(ma)])
    idx = rec / rc[np.nan_to_num(ages, nan=0).astype(int)]
    idx[np.isnan(rec)] = np.nan
    return np.nanmean(idx, axis=0)
rows4 = []
print('  가상 나무 %d그루, 기록 %d년, 기후 신호 진폭 %.2f(지수 단위), 표본 %d그루 이상인 해만 비교, 느린 변동 = %d년 이동평균' % (NTREE, T, AMP, MINCOV, SW))
for L in (150, 300, 500):
    rec, ages = sim(L)
    n_cov = (~np.isnan(rec)).sum(0)
    ok = n_cov >= MINCOV
    lo, hi = np.where(ok)[0][[0, -1]]
    core = np.arange(lo + SW // 2, hi - SW // 2 + 1)   # 이동평균이 가장자리에 걸리지 않는 해
    print('  계열 길이 %d년: 표본 충분한 구간 %d~%d(%d년), 비교 구간 %d년' % (L, lo, hi, hi - lo + 1, core.size))
    for name, f in (('개별 3차 다항식 제거', lambda: standardize_ind(rec)), ('지역 곡선(RCS)', lambda: standardize_rcs(rec, ages))):
        c = f()
        cs = smooth(np.nan_to_num(c - np.nanmean(c[ok])), SW)[core]
        ts = smooth(AMP * (clim - clim.mean()), SW)[core]
        r_slow = np.corrcoef(cs, ts)[0, 1]
        ratio = np.std(cs) / np.std(ts)
        slope = np.polyfit(ts, cs, 1)[0]
        rows4.append((L, name, float(r_slow), float(ratio), float(slope)))
        print('    %s: 느린 변동의 상관 %.2f, 진폭 비 %.2f, 회귀 기울기 %.2f' % (name, r_slow, ratio, slope))
OUT['esper'] = rows4

print()
print('=== 계산 13-5. Kaufman 등(2020): 최대 따뜻함과 냉각 속도의 안팎 점검 ===')
peak, plo, phi = 0.7, 0.3, 1.8
rate, rlo, rhi = 0.08, 0.05, 0.24
tpk = 6.5
print('정점 %.1f ℃(5~95%%: %.1f~%.1f)가 %.1f천 년 전, 냉각 속도 %.2f ℃/천 년(%.2f~%.2f)' % (peak, plo, phi, tpk, rate, rlo, rhi))
print('  중앙값끼리 곱: %.2f × %.2f천 년 = %.2f ℃ (정점 %.1f ℃보다 %.2f ℃ 모자란다)' % (rate, tpk, rate * tpk, peak, peak - rate * tpk))
print('  정점 / 시간 = %.3f ℃/천 년 (논문 범위 %.2f~%.2f 안: %s)' % (peak / tpk, rlo, rhi, rlo <= peak / tpk <= rhi))
print('  속도 범위 × 6.5천 년 = %.2f ~ %.2f ℃' % (rlo * tpk, rhi * tpk))
print('  정점 중앙 0.7 ℃를 식히는 데 걸리는 시간: 속도 0.05 → %.1f, 0.08 → %.2f, 0.24 → %.2f 천 년' % (0.7 / 0.05, 0.7 / 0.08, 0.7 / 0.24))
print('  정점 범위 0.3~1.8 ℃ / 6.5천 년 = %.3f ~ %.3f ℃/천 년' % (0.3 / tpk, 1.8 / tpk))
yrs2k = 1850
print('  냉각 속도 중앙값 0.08 ℃/천 년을 1~1850년(%d년)에 곱하면 %.2f ℃(범위 %.2f~%.2f ℃)' % (yrs2k, 0.08 * yrs2k / 1000, 0.05 * yrs2k / 1000, 0.24 * yrs2k / 1000))
print('  Neukom 등(2014)의 지난 천 년 변동 크기(2σ) 남반구 0.37 ℃, 북반구 0.67 ℃와 견주면 %.2f배, %.2f배(중앙값 0.15 ℃ 기준)' % (0.37 / (0.08 * 1.85), 0.67 / (0.08 * 1.85)))
print('  Kaufman 등 보도 쪽: 기록 1,319개, 지점 679개 → 지점당 %.2f개' % (1319 / 679))

print()
print('=== 계산 13-6. 소빙기와 중세 온난기의 창을 한 눈금에: 정의의 흩어짐 ===')
cold = [
 ('Neukom 등(2014) 두 반구 모두 추움', 1594, 1677),
 ('Neukom 등(2014) 동시 한랭 이상', 1571, 1722),
 ('PAGES 2k(2013) 대체로 추움', 1580, 1880),
 ('Stenni 등(2017) 남극 가장 추움', 1200, 1900),
 ('Solomina 등(2016) 소빙기(제3권 12장)', 1250, 1850),
 ('Esper 등(2002) 소빙기', 1200, 1850),
 ('Park 등(2017) 소빙기(제1권 5장)', 1350, 1850),
 ('Miller 등(2012) 급한 시작~강화', 1275, 1455),
]
warm = [
 ('Esper 등(2002) 중세 온난기', 900, 1300),
 ('Solomina 등(2016) 중세 온난기', 950, 1250),
 ('Park 등(2017) 중세 이상기', 900, 1350),
 ('Stenni 등(2017) 남극 가장 따뜻함', 300, 1000),
]
def inter(ws):
    lo = max(w[1] for w in ws); hi = min(w[2] for w in ws)
    return (lo, hi, max(0, hi - lo))
print('소빙기류 창 %d개. 시작 연대 범위 %d~%d(흩어짐 %d년), 끝 연대 범위 %d~%d(흩어짐 %d년)' % (len(cold), min(w[1] for w in cold), max(w[1] for w in cold), max(w[1] for w in cold) - min(w[1] for w in cold), min(w[2] for w in cold), max(w[2] for w in cold), max(w[2] for w in cold) - min(w[2] for w in cold)))
print('  모든 창의 교집합: %d~%d (%d년)' % inter(cold))
core = [w for w in cold if 'Miller' not in w[0] and 'Stenni' not in w[0]]
print('  북반구 중심 창 %d개(Miller와 Stenni 제외)의 교집합: %d~%d (%d년)' % ((len(core),) + inter(core)))
print('중세 온난기류 창 %d개. 시작 범위 %d~%d(흩어짐 %d년), 끝 범위 %d~%d(흩어짐 %d년); 남극 창(300~1000)을 뺀 세 개의 교집합 %d~%d (%d년)' % (len(warm), min(w[1] for w in warm), max(w[1] for w in warm), max(w[1] for w in warm) - min(w[1] for w in warm), min(w[2] for w in warm), max(w[2] for w in warm), max(w[2] for w in warm) - min(w[2] for w in warm), *inter(warm[:3])))
decs = np.arange(1000, 1900, 10)
cov = [sum(1 for w in cold if w[1] <= d + 5 <= w[2]) for d in decs]
print('10년 칸(1000~1890년)마다 소빙기류 창이 덮는 수의 최대 %d개: 칸 %s' % (max(cov), [int(d) for d, c in zip(decs, cov) if c == max(cov)][:3] + ['...']))
print('  1590~1670년 칸의 덮는 수: %s' % [c for d, c in zip(decs, cov) if 1590 <= d <= 1670])
print('  1000~1200년 칸의 덮는 수: %s' % set(c for d, c in zip(decs, cov) if 1000 <= d < 1200))
OUT['cold'] = cold; OUT['warm'] = warm; OUT['cov'] = [(int(d), int(c)) for d, c in zip(decs, cov)]
print('Neukom 등(2019)의 지역별 가장 추운 때: 15세기(1401~1500, 중앙·동태평양), 17세기(1601~1700, 북서유럽·북미 남동부), 19세기 중엽(나머지 대부분). 세기 가운데(1450, 1650, 1850년경)로 놓으면 간격은 %d년과 %d년이다.' % (1650 - 1450, 1850 - 1650))
print('Neukom 등(2014) 남반구 기록망: %d + %d = %d(해양 %d, 육상 %d), 육상 %d = 나이테 206 + 얼음 42 + 문헌 19 + 호수 8 + 석순 2 = %d' % (48, 277, 325, 46 + 2, 277, 277, 206 + 42 + 19 + 8 + 2))
print('  선별 후 예측변수 111개 / 325 = %.1f%%. 전 천 년 변동 크기(2σ): 북반구 0.67 ± 0.46, 남반구 0.37 ± 0.11 ℃ → 비 %.2f' % (111 / 325 * 100, 0.67 / 0.37))
print('  남반구가 북반구보다 추웠던 때: 1100년 이전과 1400년경, 따뜻했던 때 1280~1350년(%d년)' % (1350 - 1280))
print('Gergis 등(2016): 재구성 4방법 × 망 3개 = %d 앙상블, 방법당 1,000명 × 4 = %d명/망, 전체 %d명' % (4 * 3, 4 * 1000, 12 * 1000))

print()
print('=== 계산 13-7. Miller 등(2012): 날짜가 한 25년 창에 모이는 일은 우연인가, 보정 곡선 모양은 어떤가 ===')
n_d, y0, y1 = 94, 800, 2000
span = y1 - y0 + 1
for (a, b, k) in ((1275, 1300, 41), (1430, 1455, 13)):
    L = b - a + 1
    p = L / span
    print('  창 %d~%d(%d년): 한 날짜가 창에 들 균일 기준 확률 %.4f, 94개 중 기대 %.2f개, 관측 %d개, P(X≥%d) = %.3e' % (a, b, L, p, n_d * p, k, k, binom.sf(k - 1, n_d, p)))
print('  관측 비율: 41/94 = %.1f%%, 13/94 = %.1f%%. 두 창은 시간의 %.1f%%씩.' % (41 / 94 * 100, 13 / 94 * 100, 26 / span * 100))
print('  (날짜가 한 번의 사건으로 한꺼번에 죽은 식물의 것이므로 균일 기준은 거친 비교일 뿐이다. 날짜 연대 곡선이 평평하면 서로 다른 해도 같은 날짜로 모이는 효과가 더해진다)')
cur = np.loadtxt(os.path.join(HERE, 'data', 'intcal20.14c'), delimiter=',')
cur = cur[np.argsort(cur[:, 0])]
cal, c14, sg = cur[:, 0], cur[:, 1], cur[:, 2]
def at(ad):
    bp = 1950 - ad
    return np.interp(bp, cal, c14), np.interp(bp, cal, sg)
print('  IntCal20(북반구) 곡선 14C 연대(BP)와 곡선 오차:')
for ad in (1200, 1225, 1250, 1275, 1288, 1300, 1325, 1350, 1400, 1430, 1455, 1500):
    a, s = at(ad)
    print('    서기 %d: 14C %.0f BP, 곡선 오차 %.0f' % (ad, a, s))
# 기울기: 14C 연대가 1년에 몇 년 변하는가
for a0, a1 in ((1200, 1250), (1250, 1275), (1275, 1300), (1300, 1350), (1350, 1430), (1430, 1455), (1455, 1500)):
    d = (at(a1)[0] - at(a0)[0]) / (a1 - a0)
    print('    서기 %d~%d: 달력 1년당 14C 연대 변화 %.2f년 (1이면 곡선 기울기가 이상적, 0에 가까우면 평평한 구간)' % (a0, a1, -d))
# 14C 연대 750 ± 30 BP 가 어느 달력 범위로 대응하는지
tgrid = np.arange(0, 1500)
mu = np.interp(tgrid, cal, c14)
def span_of(c, e):
    s2 = e ** 2 + np.interp(tgrid, cal, sg) ** 2
    p = np.exp(-0.5 * (c - mu) ** 2 / s2) / np.sqrt(s2); p /= p.sum()
    o = np.argsort(-p); cum = np.cumsum(p[o]); sel = np.sort(tgrid[o[cum <= 0.954]])
    return 1950 - sel.max(), 1950 - sel.min(), p
for ad in (1288, 1442):
    c, s = at(ad)
    lo, hi, _ = span_of(c, 30)
    print('  서기 %d의 곡선 값 14C %.0f BP에 오차 ±30년을 주면 95.4%% 달력 범위 서기 %d~%d(%d년폭)' % (ad, c, lo, hi, hi - lo))

# 그림 스크립트가 읽는 값
OUT['miller'] = {'curve': [(ad, float(at(ad)[0]), float(at(ad)[1])) for ad in range(1200, 1501, 5)]}
json.dump(OUT, open(os.path.join(HERE, 'calc13-out.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
