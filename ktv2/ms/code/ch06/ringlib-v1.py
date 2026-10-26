# -*- coding: utf-8 -*-
"""제2권 6장 나이테 분석 라이브러리 v1 (파이썬 직접 구현, numpy + scipy만 쓴다).

R의 dplR 꾸러미가 하는 일 가운데 이 장이 쓰는 것을 같은 정의로 다시 구현했다. 정의는 dplR 소스(GitHub
OpenDendro/dplR, 커밋 205caac, DESCRIPTION의 Version 1.8.1)를 읽고 옮겼고, 값이 같은지는 compare-dplr-v1.py가
같은 입력으로 dplR를 실행해 확인한다. 이 파일의 함수가 dplR와 한 글자까지 같다는 보증은 없다. 확인한 범위는
compare-dplr.log에 있다.

자료 구조: 연도 배열 years(오름차순, 연속), 계열 이름 names, 행렬 X(연도 x 계열, 결측 NaN).
스크립트는 이 파일을 importlib로 불러 쓴다(파일 이름에 하이픈이 있어 import 문을 직접 쓸 수 없다).
"""
import numpy as np
from scipy import stats
from scipy.linalg import solve_banded
from scipy.optimize import curve_fit

RINGLIB_VERSION = 'v1'


# ------------------------------------------------------------------ 입출력: Tucson(.rwl) 형식
def write_rwl(path, years, names, X, site='SYN001', unit=0.001):
    """Tucson 형식으로 쓴다. 값은 mm, 단위 unit(0.001 mm)의 정수로 반올림하고 끝 표시는 -9999(0.001 mm 형식).
    결측(NaN)은 계열의 앞뒤에서만 허용하고 줄에 쓰지 않는다. 0은 '없는 테'로 읽히므로 값이 0이 되지 않게 최소 1로 둔다."""
    years = np.asarray(years)
    with open(path, 'w', encoding='ascii') as f:
        for j, nm in enumerate(names):
            col = X[:, j]
            ok = np.where(~np.isnan(col))[0]
            a, b = ok[0], ok[-1]
            if np.isnan(col[a:b + 1]).any():
                raise ValueError('계열 %s의 안쪽에 결측이 있다' % nm)
            vals = [max(1, int(round(v / unit))) for v in col[a:b + 1]]
            y0 = int(years[a])
            seq = vals + [-9999]
            # 첫 줄은 시작 연도에서 그 10년 구간의 끝까지, 이후는 10년 구간 단위
            i = 0
            y = y0
            while i < len(seq):
                n_in_row = 10 - (y % 10)
                row = seq[i:i + n_in_row]
                f.write('%-8s%4d' % (nm[:8], y) + ''.join('%6d' % v for v in row) + '\n')
                i += len(row)
                y += len(row)
    return path


def read_rwl(path):
    """write_rwl이 쓴 형식과 dplR의 write.tucson이 쓴 Tucson 형식(0.001 mm 또는 0.01 mm)을 읽는다.
    머리줄이 있는 파일은 읽지 않는다(이 장의 실습에는 필요 없다).
    끝 표시는 계열의 마지막 값으로 판별한다: -9999이면 단위 0.001 mm, 999이면 단위 0.01 mm. 같은 파일에서 999는
    -9999 형식에서는 0.999 mm라는 보통 값이므로, 줄 안의 999를 끝 표시로 읽으면 안 된다(실습 6-1에서 겪은 함정)."""
    rows = {}
    order = []
    for line in open(path, encoding='ascii'):
        line = line.rstrip('\n')
        if len(line) < 12:
            continue
        nm = line[:8].strip()
        yr = int(line[8:12])
        toks = [line[12 + 6 * k:18 + 6 * k] for k in range(10)]
        vals = [int(t) for t in toks if t.strip()]
        if nm not in rows:
            rows[nm] = []
            order.append(nm)
        rows[nm].append((yr, vals))
    data = {}
    scale = {}
    for nm in order:
        last = rows[nm][-1][1][-1]
        if last == -9999:
            scale[nm] = 0.001
        elif last == 999:
            scale[nm] = 0.01
        else:
            raise ValueError('계열 %s의 끝 표시를 찾지 못했다' % nm)
        d = {}
        for yr, vals in rows[nm]:
            for k, v in enumerate(vals):
                d[yr + k] = v
        d.pop(max(d))                      # 끝 표시가 놓인 자리
        data[nm] = d
    allyears = sorted({y for d in data.values() for y in d})
    years = np.arange(allyears[0], allyears[-1] + 1)
    X = np.full((len(years), len(order)), np.nan)
    for j, nm in enumerate(order):
        for y, v in data[nm].items():
            X[y - years[0], j] = v * scale[nm]
    return years, order, X


# ------------------------------------------------------------------ 평활 스플라인(Cook & Peters 1981)
def caps(y, nyrs=32, f=0.5):
    """dplR::caps와 같은 정의의 평활 스플라인. 주파수 반응이 f(=0.5)가 되는 파장이 nyrs년이다.
    간격이 1인 격자에서 2차 도함수 벌점 스플라인: (Q'Q + 2p R) u = Q'y, 평활값 g = y - Q u.
    p = 6 f (cos(2pi/nyrs) - 1)^2 / ((1 - f)(cos(2pi/nyrs) + 2)). nyrs는 정수로 버린다(dplR의 동작)."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n < 4:
        raise ValueError('자료가 4개보다 적다')
    v = float(int(nyrs))
    c = np.cos(2 * np.pi / v)
    p = ((1.0 / (1.0 - f) - 1.0) * 6.0 * (c - 1.0) ** 2) / (c + 2.0)
    m = n - 2
    diag = np.full(m, 6.0 + p * 4.0 / 3.0)
    off1 = np.full(m - 1, -4.0 + p / 3.0)
    off2 = np.full(m - 2, 1.0)
    ab = np.zeros((5, m))
    ab[0, 2:] = off2
    ab[1, 1:] = off1
    ab[2, :] = diag
    ab[3, :-1] = off1
    ab[4, :-2] = off2
    rhs = y[:-2] - 2.0 * y[1:-1] + y[2:]
    u = solve_banded((2, 2), ab, rhs)
    g = y.copy()
    g[:-2] -= u
    g[1:-1] += 2.0 * u
    g[2:] -= u
    return g


# ------------------------------------------------------------------ 표준화(detrend)
def detrend_series(y, method='Spline', nyrs=None, f=0.5):
    """한 계열(결측은 앞뒤에만)을 표준화해 (지수, 곡선)을 돌려준다. 지수 = 너비 / 곡선(dplR의 기본, 비율).
    method: 'Spline'(nyrs 기본 floor(0.67 n)), 'ModNegExp', 'Mean'."""
    y = np.asarray(y, dtype=float)
    ok = np.where(~np.isnan(y))[0]
    a, b = ok[0], ok[-1]
    y2 = y[a:b + 1].copy()
    if np.isnan(y2).any():
        raise ValueError('계열 안쪽에 결측이 있다')
    y2[y2 == 0] = 0.001
    n = len(y2)
    if method == 'Mean':
        curve = np.full(n, y2.mean())
    elif method == 'Spline':
        curve = caps(y2, nyrs=int(n * 0.67) if nyrs is None else nyrs, f=f)
    elif method == 'ModNegExp':
        curve = _modnegexp(y2)
    else:
        raise ValueError(method)
    idx = np.full(len(y), np.nan)
    cur = np.full(len(y), np.nan)
    idx[a:b + 1] = y2 / curve
    cur[a:b + 1] = curve
    return idx, cur


def _modnegexp(y):
    """dplR의 ModNegExp와 같은 순서: 변형 음의 지수 a exp(b t) + k를 비선형 최소제곱으로 맞추고, 실패하거나
    a <= 0 또는 b >= 0이면 직선, 직선의 기울기가 양수이면 평균을 쓴다."""
    n = len(y)
    t = np.arange(1, n + 1, dtype=float)
    a0 = y[:max(1, int(np.floor(n * 0.1)))].mean()
    k0 = y[int(np.floor(n * 0.9)) - 1:].mean()
    try:
        popt, _ = curve_fit(lambda tt, a, b, k: a * np.exp(b * tt) + k, t, y, p0=[a0, -0.01, k0], maxfev=20000)
        a, b, k = popt
        fit = a * np.exp(b * t) + k
        if a > 0 and b < 0 and fit[-1] > 0:
            return fit
    except Exception:
        pass
    sl, ic = np.polyfit(t, y, 1)[0], np.polyfit(t, y, 1)[1]
    if sl <= 0:
        fit = ic + sl * t
        if fit[0] > 0 and fit[-1] > 0:
            return fit
    return np.full(n, y.mean())


def detrend(X, method='Spline', nyrs=None, f=0.5):
    out = np.full_like(X, np.nan)
    cur = np.full_like(X, np.nan)
    for j in range(X.shape[1]):
        out[:, j], cur[:, j] = detrend_series(X[:, j], method, nyrs, f)
    return out, cur


# ------------------------------------------------------------------ 이중 가중(biweight) 로버스트 평균
def tbrm(x, C=9.0):
    """Tukey의 이중 가중 로버스트 평균(dplR::tbrm과 같은 정의). 중앙값 m, 절대편차의 중앙값 MAD,
    u = (x - m)/(C MAD + 1e-6), |u| <= 1인 값만 가중치 (1 - u^2)^2로 평균한다. 한 번 계산한다(반복 없음)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return np.nan
    m = np.median(x)
    mad = np.median(np.abs(x - m))
    d = mad * C + 1e-6
    u = (x - m) / d
    sel = np.abs(u) <= 1.0
    if not sel.any():
        return np.nan
    w = (1.0 - u[sel] ** 2) ** 2
    return float(np.sum(w * x[sel]) / np.sum(w))


def chron(rwi, biweight=True):
    """지수 행렬의 연도별 평균. (연대기, 연도별 계열 수)."""
    n = np.sum(~np.isnan(rwi), axis=1)
    if biweight:
        c = np.array([tbrm(r) for r in rwi])
    else:
        with np.errstate(all='ignore'):
            c = np.nanmean(rwi, axis=1)
    return c, n


# ------------------------------------------------------------------ 자기회귀 사전 백색화(R의 ar() 기본값과 같은 정의)
def ar_yw(x):
    """R의 ar(x)(Yule-Walker, AIC로 차수 선택, order.max = min(n-1, floor(10 log10 n)))의 잔차와 평균.
    잔차의 앞 order개는 결측. 반환: (잔차 배열, 평균, 차수, 계수)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    xm = x.mean()
    z = x - xm
    omax = min(n - 1, int(np.floor(10 * np.log10(n))))
    r = np.array([np.sum(z[:n - k] * z[k:]) / n for k in range(omax + 1)])
    # Levinson-Durbin
    vars_ = [r[0]]
    coefs = {}
    phi = np.zeros(0)
    v = r[0]
    for k in range(1, omax + 1):
        acc = r[k] - np.sum(phi * r[k - 1:0:-1][:k - 1]) if k > 1 else r[1]
        kk = acc / v
        phi = np.concatenate([phi - kk * phi[::-1], [kk]]) if k > 1 else np.array([kk])
        v = v * (1.0 - kk * kk)
        vars_.append(v)
        coefs[k] = phi.copy()
    vars_ = np.array(vars_)
    xaic = n * np.log(vars_) + 2 * np.arange(omax + 1) + 2
    order = int(np.argmin(xaic))
    if order == 0:
        return z.copy(), xm, 0, np.zeros(0)
    ar = coefs[order]
    res = np.full(n, np.nan)
    for t in range(order, n):
        res[t] = z[t] - np.sum(ar * z[t - 1::-1][:order])
    return res, xm, order, ar


def ar_prewhiten(x):
    """dplR의 ar.func와 같다: 결측이 아닌 값에 AR 모형을 맞추고 잔차 + 평균을 돌려준다(앞 order개는 결측)."""
    y = np.asarray(x, dtype=float).copy()
    ok = ~np.isnan(y)
    if ok.sum() < 2:
        return y
    res, xm, order, ar = ar_yw(y[ok])
    y[ok] = res + xm
    return y


# ------------------------------------------------------------------ 교차 연대 결정
def xdate_prep(X, nyrs=32, prewhiten=True):
    """원자료(너비)에서 스플라인(nyrs년)으로 지수를 만들고 AR 백색화를 한 행렬. dplR의 nyrs 방식과 같은 순서."""
    out = np.full_like(X, np.nan)
    for j in range(X.shape[1]):
        col = X[:, j]
        ok = np.where(~np.isnan(col))[0]
        a, b = ok[0], ok[-1]
        y = col[a:b + 1].copy()
        y[y == 0] = 0.001
        out[a:b + 1, j] = y / caps(y, nyrs=nyrs)
    if prewhiten:
        for j in range(X.shape[1]):
            out[:, j] = ar_prewhiten(out[:, j])
    return out


def loo_master(P, biweight=True):
    """각 계열을 뺀 나머지의 연도별 이중 가중 평균(자기 자신이 마스터에 섞이지 않게 한다)."""
    nyr, ns = P.shape
    M = np.full_like(P, np.nan)
    for j in range(ns):
        rows = np.where(~np.isnan(P[:, j]))[0]
        others = np.delete(P, j, axis=1)[rows]
        if biweight:
            M[rows, j] = [tbrm(r) for r in others]
        else:
            with np.errstate(all='ignore'):
                M[rows, j] = np.nanmean(others, axis=1)
    return M


def interseries_cor(X, nyrs=32, prewhiten=True, biweight=True):
    """계열마다 '나머지 계열의 마스터'와의 피어슨 상관과 양쪽 p값. dplR의 interseries.cor(method='pearson',
    nyrs=nyrs)와 같은 순서(스플라인 지수 -> AR 백색화 -> 하나 뺀 마스터)."""
    P = xdate_prep(X, nyrs, prewhiten)
    M = loo_master(P, biweight)
    r = np.full(X.shape[1], np.nan)
    p = np.full(X.shape[1], np.nan)
    for j in range(X.shape[1]):
        ok = ~np.isnan(P[:, j]) & ~np.isnan(M[:, j])
        if ok.sum() >= 3:
            r[j], p[j] = stats.pearsonr(P[ok, j], M[ok, j])
    return r, p


def lag_scan(series_col, master_col, years, y0, y1, maxlag=10):
    """한 계열의 구간 [y0, y1]을 마스터의 같은 구간에서 lag년 어긋나게 놓았을 때의 상관(피어슨).
    lag > 0은 '계열의 연도 y가 마스터의 y + lag에 해당한다'는 뜻이다. 반환: {lag: (r, 겹친 연수)}."""
    yi = {int(y): i for i, y in enumerate(years)}
    out = {}
    for lag in range(-maxlag, maxlag + 1):
        xs, ms = [], []
        for y in range(y0, y1 + 1):
            if y in yi and (y + lag) in yi:
                a, b = series_col[yi[y]], master_col[yi[y + lag]]
                if not (np.isnan(a) or np.isnan(b)):
                    xs.append(a)
                    ms.append(b)
        out[lag] = (float(np.corrcoef(xs, ms)[0, 1]) if len(xs) >= 10 else np.nan, len(xs))
    return out


def seg_scan(P, M, years, j, seg=50, step=25, maxlag=10):
    """계열 j를 seg년 구간(step년씩 밀며)으로 나눠 구간마다 lag -maxlag..maxlag의 상관을 구하고, 가장 높은
    상관의 lag와 lag 0의 상관을 돌려준다. COFECHA와 비슷한 구간 방식이지만 이 책은 COFECHA를 실행하지 않았고
    같은 결과를 내는지 확인하지 않았다."""
    col = P[:, j]
    ok = np.where(~np.isnan(col))[0]
    a, b = int(years[ok[0]]), int(years[ok[-1]])
    rows = []
    s = a
    while s + seg - 1 <= b:
        sc = lag_scan(col, M[:, j], years, s, s + seg - 1, maxlag)
        best = max(sc, key=lambda k: -1 if np.isnan(sc[k][0]) else sc[k][0])
        rows.append((s, s + seg - 1, sc[0][0], best, sc[best][0], {k: v[0] for k, v in sc.items()}))
        s += step
    return rows


def flag_series(rows, crit):
    """의심 계열 판정 규칙(이 책의 규칙이며 COFECHA의 규칙이 아니다): 서로 이웃한 두 구간에서 모두 '최고 상관이 나오는 lag가
    0이 아니고, 그 상관은 임계값(crit)을 넘고, lag 0의 상관은 임계값 아래'이며 두 구간의 lag가 같으면 의심한다.
    반환 (의심 여부, 그 lag 또는 None, 해당 구간 번호 목록)."""
    ok = [(lag != 0 and rb > crit and (np.isnan(r0) or r0 < crit)) for _, _, r0, lag, rb, _ in rows]
    for i in range(len(rows) - 1):
        if ok[i] and ok[i + 1] and rows[i][3] == rows[i + 1][3]:
            idx = [k for k in range(len(rows)) if ok[k] and rows[k][3] == rows[i][3]]
            return True, rows[i][3], idx
    return False, None, []


# ------------------------------------------------------------------ 날짜 오류를 일부러 만들기와 고치기(실습용)
def _span(col):
    ok = np.where(~np.isnan(col))[0]
    return ok[0], ok[-1]


def corrupt_shift(col, d):
    """날짜가 통째로 d년 늦게(d > 0) 붙은 계열. 배열 끝을 넘는 테는 잘린다."""
    a, b = _span(col)
    new = np.full_like(col, np.nan)
    hi = min(b + d, len(col) - 1)
    new[a + d:hi + 1] = col[a:a + (hi - a - d) + 1]
    return new


def repair_shift(col, d):
    a, b = _span(col)
    new = np.full_like(col, np.nan)
    new[a - d:b - d + 1] = col[a:b + 1]
    return new


def corrupt_missing(col, years, yg):
    """연도 yg의 테가 측정에서 빠졌고, 바깥(마지막 해)에서 세어 날짜를 붙였다: yg보다 오래된 값은 한 해 늦게 붙는다."""
    a, b = _span(col)
    g = int(yg - years[0])
    seq = np.delete(col[a:b + 1], g - a)
    new = np.full_like(col, np.nan)
    new[a + 1:b + 1] = seq
    return new


def repair_missing(col, years, yg):
    """yg 이전(라벨)의 값을 한 해 앞으로 옮기고 yg에 양 옆 평균의 테를 끼운다(추정값)."""
    a, b = _span(col)
    g = int(yg - years[0])
    new = col.copy()
    seg = col[a:g + 1].copy()
    new[a:g + 1] = np.nan
    new[a - 1:g] = seg
    new[g] = 0.5 * (new[g - 1] + new[g + 1])
    return new


def corrupt_false(col, years, yg):
    """연도 yg의 테가 둘로 쪼개져 두 개로 측정됐다(0.55와 0.45). yg보다 오래된 값은 한 해 일찍 붙는다."""
    a, b = _span(col)
    g = int(yg - years[0])
    seq = list(col[a:b + 1])
    w = seq[g - a]
    seq[g - a:g - a + 1] = [w * 0.55, w * 0.45]
    seq = np.array(seq)
    new = np.full_like(col, np.nan)
    new[a - 1:b + 1] = seq
    return new


def repair_false(col, years, yg):
    """라벨 yg-1과 yg의 두 값을 합쳐 yg에 두고, 그보다 오래된 부분을 한 해 뒤로 옮긴다."""
    a, b = _span(col)
    g = int(yg - years[0])
    new = col.copy()
    merged = col[g - 1] + col[g]
    pre = col[a:g - 1].copy()
    new[:g - 1] = np.nan
    new[a + 1:g] = pre
    new[g] = merged
    return new


# ------------------------------------------------------------------ 연대기 통계
def mean_sensitivity(x):
    """평균 민감도 = 이웃한 해의 값 차이를 두 값의 평균으로 나눈 것의 절댓값의 평균 (dplR의 sens1)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    with np.errstate(all='ignore'):
        t = 2.0 * np.abs(np.diff(x)) / (x[1:] + x[:-1])
    return float(np.mean(t[~np.isnan(t)]))     # 0 + 0처럼 계산할 수 없는 항은 건너뛴다(dplR의 sens1과 같다)


def acf1(x):
    """1차 자기상관(R의 acf, 분모 n)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    z = x - x.mean()
    return float(np.sum(z[1:] * z[:-1]) / np.sum(z * z))


def rwi_stats(R, tree, min_overlap=30):
    """dplR::rwi.stats(method='pearson', period='max')와 같은 정의의 연대기 통계(윈도 없이 전체 기간).
    R: 지수 행렬(연도 x 코어), tree: 코어마다의 나무 번호 배열.
    반환 dict: n.tot, n.wt, n.bt, rbar.tot, rbar.wt, rbar.bt, c.eff, rbar.eff, n(나무 수), eps, snr."""
    tree = np.asarray(tree)
    ut = list(dict.fromkeys(tree.tolist()))
    cores = {t: np.where(tree == t)[0] for t in ut}

    def pair_r(i, j):
        ok = ~np.isnan(R[:, i]) & ~np.isnan(R[:, j])
        if ok.sum() >= min_overlap:
            return float(np.corrcoef(R[ok, i], R[ok, j])[0, 1])
        return None
    rsum_bt, n_bt = 0.0, 0
    good = set()
    for a in range(len(ut) - 1):
        for b in range(a + 1, len(ut)):
            for i in cores[ut[a]]:
                for j in cores[ut[b]]:
                    r = pair_r(i, j)
                    if r is not None:
                        rsum_bt += r
                        n_bt += 1
                        good.update([ut[a], ut[b]])
    rsum_wt, n_wt = 0.0, 0
    nct = {}
    for t in ut:
        if t not in good:
            continue
        cs = cores[t]
        if len(cs) == 1:
            nct[t] = 1.0
            continue
        cnt = 0
        for a in range(len(cs) - 1):
            for b in range(a + 1, len(cs)):
                r = pair_r(cs[a], cs[b])
                if r is not None:
                    rsum_wt += r
                    cnt += 1
        n_wt += cnt
        nct[t] = 0.5 + np.sqrt(0.25 + 2 * cnt) if cnt > 0 else 1.0
    n_tot = n_wt + n_bt
    rbar_tot = (rsum_wt + rsum_bt) / n_tot
    rbar_wt = rsum_wt / n_wt if n_wt > 0 else np.nan
    rbar_bt = rsum_bt / n_bt
    n = len(good)
    if n_wt == 0:
        c_eff, rbar_eff = 1.0, rbar_bt
    else:
        vals = np.array(list(nct.values()))
        if len(np.unique(vals)) == 1:
            c_eff = float(vals[0])
            rbar_eff = rbar_bt / (rbar_wt + (1 - rbar_wt) / c_eff)
        else:
            c_eff = 1.0 / np.mean(1.0 / vals)
            rbar_eff = rbar_bt / (rbar_wt + (1 - rbar_wt) * np.mean(1.0 / vals))
    eps = n * rbar_eff / ((n - 1) * rbar_eff + 1)
    snr = n * rbar_eff / (1 - rbar_eff)
    return dict(n_tot=n_tot, n_wt=n_wt, n_bt=n_bt, rbar_tot=rbar_tot, rbar_wt=rbar_wt, rbar_bt=rbar_bt,
                c_eff=c_eff, rbar_eff=rbar_eff, n=n, eps=eps, snr=snr)


def eps_from_rbar(n, rbar):
    """표본 신호 EPS = n rbar / ((n-1) rbar + 1)  (Wigley 등 1984의 식을 dplR가 쓰는 형태로)."""
    return n * rbar / ((n - 1) * rbar + 1.0)


def snr_from_rbar(n, rbar):
    return n * rbar / (1.0 - rbar)


def n_for_eps(target, rbar):
    """EPS가 target이 되는 데 필요한 나무 수(실수). EPS = n r/((n-1) r + 1)을 n에 대해 푼 것."""
    return target * (1.0 - rbar) / ((1.0 - target) * rbar)


def sss(R, tree, rbar_eff, n_total):
    """연도별 하위 표본 신호 강도 SSS = n (1 + (N-1) rbar) / (N (1 + (n-1) rbar)). n은 그 해의 나무 수."""
    tree = np.asarray(tree)
    ut = list(dict.fromkeys(tree.tolist()))
    nyr = R.shape[0]
    n = np.zeros(nyr)
    for t in ut:
        n += np.any(~np.isnan(R[:, tree == t]), axis=1)
    return (n * (1 + (n_total - 1) * rbar_eff)) / (n_total * (1 + (n - 1) * rbar_eff))


# ------------------------------------------------------------------ 기후 복원: 보정, 검증
def linfit(x, y):
    """단순 회귀 y = a + b x. 반환 (a, b, r, 기울기의 표준오차)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    b, a = np.polyfit(x, y, 1)
    r = float(np.corrcoef(x, y)[0, 1])
    res = y - (a + b * x)
    se = float(np.sqrt(np.sum(res ** 2) / (n - 2) / np.sum((x - x.mean()) ** 2)))
    return float(a), float(b), r, se


def re_ce(obs, est, cal_mean):
    """RE = 1 - SSE / sum (obs - 보정 평균)^2, CE = 1 - SSE / sum (obs - 검증 평균)^2."""
    obs = np.asarray(obs, float)
    est = np.asarray(est, float)
    sse = np.sum((obs - est) ** 2)
    return float(1 - sse / np.sum((obs - cal_mean) ** 2)), float(1 - sse / np.sum((obs - obs.mean()) ** 2))


def sign_test(obs, est, cal_mean):
    """부호 검정: 관측과 추정이 (보정 평균에서) 같은 방향으로 벗어난 해의 수와 다른 방향인 해의 수."""
    o = np.sign(np.asarray(obs, float) - cal_mean)
    e = np.sign(np.asarray(est, float) - cal_mean)
    same = int(np.sum(o == e))
    return same, len(o) - same


def durbin_watson(res):
    res = np.asarray(res, float)
    return float(np.sum(np.diff(res) ** 2) / np.sum(res ** 2))


def n_eff(n, r1a, r1b):
    """두 계열의 1차 자기상관이 r1a, r1b일 때 유효 표본 수의 근사 n (1 - r1a r1b)/(1 + r1a r1b) (제1권 11.5.5절)."""
    return n * (1 - r1a * r1b) / (1 + r1a * r1b)


def crit_r(n, alpha=0.05):
    """피어슨 상관의 양쪽 임계값."""
    tc = stats.t.isf(alpha / 2, n - 2)
    return float(tc / np.sqrt(n - 2 + tc * tc))
