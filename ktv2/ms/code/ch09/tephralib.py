# -*- coding: utf-8 -*-
"""제2권 9장 실습 라이브러리 tephralib (numpy, scipy만 사용). 이 장의 모든 스크립트가 불러 쓴다.
구성
  1. 구면 거리, 방위, 목적지 점, 구면 면적        (제1권 4장 계산 4-1의 확장)
  2. 가중 평균, 카이제곱 합치 시험 T', 쌍별 z     (제1권 4장 계산 4-6)
  3. 화산 유리 주성분 산화물: 닫힘(100% 정규화), 유사 계수, 유클리드, 에이치슨(clr/ilr), 마할라노비스,
     선형 판별(LDA), 호텔링 T2                      (제1권에는 입력이 없다. 시연값으로만 쓴다)
  4. 층서 순서 제약을 둔 단순 베이즈 연대 모형(격자 사후분포 + 순서 기각 표집)
"""
import numpy as np
from scipy import stats

R_EARTH = 6371.0   # 제1권 4장과 같은 평균 지구 반지름(km)

# ---------------------------------------------------------------- 1. 구면 기하
def hav(lat1, lon1, lat2, lon2, R=R_EARTH):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

def bearing(lat1, lon1, lat2, lon2):
    """출발점에서 도착점으로 가는 처음 방위(북 0도, 시계 방향, 0~360)."""
    p1, p2, dl = np.radians(lat1), np.radians(lat2), np.radians(lon2 - lon1)
    y = np.sin(dl) * np.cos(p2)
    x = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0

def destination(lat1, lon1, brg, dist_km, R=R_EARTH):
    """출발점에서 방위 brg(도)로 dist_km 가서 닿는 점(위도, 경도). 구면."""
    d = np.asarray(dist_km) / R
    p1, l1, b = np.radians(lat1), np.radians(lon1), np.radians(brg)
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(b))
    l2 = l1 + np.arctan2(np.sin(b) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), (np.degrees(l2) + 540.0) % 360.0 - 180.0

def cap_area(r_km, R=R_EARTH):
    """구면 위에서 중심에서 측지 거리 r_km 이내인 부분(구면 모자)의 넓이(km2)."""
    return 2 * np.pi * R ** 2 * (1 - np.cos(r_km / R))

# ---------------------------------------------------------------- 2. 연대 합치
def wmean(x, s):
    x, s = np.asarray(x, float), np.asarray(s, float)
    w = 1 / s ** 2
    m = np.sum(w * x) / np.sum(w)
    return m, 1 / np.sqrt(np.sum(w))

def tprime(x, s):
    """합치 시험. T' = sum(((x_i - xbar) / s_i)^2), 자유도 n-1.
    이 책이 이 이름으로 부르는 통계량이다(원문 Ward & Wilson 1978의 기호와 식은 읽지 못했다)."""
    x, s = np.asarray(x, float), np.asarray(s, float)
    m, e = wmean(x, s)
    T = float(np.sum(((x - m) / s) ** 2))
    df = len(x) - 1
    p = float(stats.chi2.sf(T, df)) if df > 0 else float('nan')
    crit = float(stats.chi2.ppf(0.95, df)) if df > 0 else float('nan')
    return dict(mean=float(m), err=float(e), T=T, df=df, p=p, crit5=crit, agree=bool(T < crit))

def pair_z(x1, s1, x2, s2):
    d = x1 - x2
    sd = float(np.hypot(s1, s2))
    return d, sd, d / sd

# ---------------------------------------------------------------- 3. 화산 유리 조성
def close100(X, total_min=93.0):
    """EPMA 원자료 X(행=파편, 열=산화물, 질량 %). 합계가 total_min 미만인 행을 빼고 합계를 100으로 맞춘다.
    반환: (닫힌 자료, 남긴 행 마스크, 원 합계)."""
    X = np.asarray(X, float)
    tot = X.sum(axis=1)
    keep = tot >= total_min
    return X[keep] / tot[keep, None] * 100.0, keep, tot

def sim_coef(x, y):
    """유사 계수 SC = 평균_i[ min(x_i,y_i) / max(x_i,y_i) ]. Borchardt 등(1972)이 '다변량 유사성의 간단한 척도'로
    계수를 소개했다는 것만 확인했고 원식은 읽지 못했다. 이 책이 널리 쓰이는 형태로 정의해 쓴다. 1이면 같음."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(np.mean(np.minimum(x, y) / np.maximum(x, y)))

def clr(X):
    L = np.log(np.asarray(X, float))
    return L - L.mean(axis=-1, keepdims=True)

def helmert(D):
    """clr 공간(합이 0인 초평면)의 정규직교 기저 D x (D-1). ilr 좌표를 만든다."""
    H = np.zeros((D, D - 1))
    for j in range(1, D):
        H[:j, j - 1] = 1.0 / j
        H[j, j - 1] = -1.0
        H[:, j - 1] *= np.sqrt(j / (j + 1.0))
    return H

def ilr(X):
    X = np.asarray(X, float)
    return clr(X) @ helmert(X.shape[-1])

def aitchison(x, y):
    return float(np.linalg.norm(clr(x) - clr(y)))

def mahal2(Z, mu, S):
    """각 행 Z_i의 마할라노비스 제곱 거리 (Z_i-mu)' S^-1 (Z_i-mu)."""
    d = np.atleast_2d(Z) - mu
    return np.einsum('ij,jk,ik->i', d, np.linalg.inv(S), d)

def pooled_cov(groups):
    num = sum((len(g) - 1) * np.cov(g, rowvar=False) for g in groups)
    return num / (sum(len(g) for g in groups) - len(groups))

def lda_fit(groups):
    mus = [g.mean(axis=0) for g in groups]
    S = pooled_cov(groups)
    pri = np.array([len(g) for g in groups], float); pri /= pri.sum()
    return mus, S, np.log(pri)

def lda_post(Z, model):
    """각 파편이 각 집단에서 나왔을 사후확률(같은 공분산, 사전확률 = 표본 비율). 반환 (확률, 마할라노비스 제곱 거리)."""
    mus, S, lp = model
    Z = np.atleast_2d(Z)
    D2 = np.stack([mahal2(Z, m, S) for m in mus], axis=1)
    sc = lp[None, :] - 0.5 * D2
    sc -= sc.max(axis=1, keepdims=True)
    P = np.exp(sc); P /= P.sum(axis=1, keepdims=True)
    return P, D2

def hotelling2(A, B):
    """두 표본 평균이 같은지 호텔링 T2 검정. 반환 (T2, F, p, p, n1, n2)."""
    n1, n2, p = len(A), len(B), A.shape[1]
    d = A.mean(axis=0) - B.mean(axis=0)
    S = ((n1 - 1) * np.cov(A, rowvar=False) + (n2 - 1) * np.cov(B, rowvar=False)) / (n1 + n2 - 2)
    T2 = float(d @ np.linalg.solve(S * (1 / n1 + 1 / n2), d))
    F = T2 * (n1 + n2 - p - 1) / (p * (n1 + n2 - 2))
    pv = float(stats.f.sf(F, p, n1 + n2 - p - 1))
    return T2, float(F), pv, p, n1, n2

# ---------------------------------------------------------------- 4. 순서 제약 베이즈(단순)
def grid_posterior(dates, sigs, grid, q=0.0, tau=1000.0):
    """한 층(사건)의 참 나이 theta의 격자 사후분포. 사전분포 균일.
    각 날짜는 확률 1-q로 N(theta, s^2), 확률 q로 N(theta, s^2+tau^2)(이상치)에서 나온다고 본다.
    반환: (사후밀도(격자 합 1), 날짜별 이상치 사후확률)."""
    dates, sigs = np.asarray(dates, float), np.asarray(sigs, float)
    G = grid[:, None]
    good = stats.norm.pdf(dates[None, :], G, sigs[None, :])
    wide = stats.norm.pdf(dates[None, :], G, np.hypot(sigs, tau)[None, :])
    lik_i = (1 - q) * good + q * wide                 # (격자, 날짜)
    with np.errstate(divide='ignore'):      # 날짜에서 먼 격자점은 가능도가 0으로 넘쳐 로그가 -inf가 된다(사후확률 0)
        logl = np.sum(np.log(lik_i), axis=1)
    post = np.exp(logl - logl.max()); post /= post.sum()
    if q > 0:
        r = (q * wide) / lik_i                         # 격자점마다 날짜 i가 이상치일 확률
        pout = (post[:, None] * r).sum(axis=0)
    else:
        pout = np.zeros(len(dates))
    return post, pout

def sample_grid(post, grid, n, rng):
    cdf = np.cumsum(post); cdf /= cdf[-1]
    u = rng.random(n)
    idx = np.searchsorted(cdf, u)
    step = grid[1] - grid[0]
    return grid[np.minimum(idx, len(grid) - 1)] + (rng.random(n) - 0.5) * step

def ordered_samples(posts, grid, n, rng, older_first=True):
    """층 k=0이 가장 오래된(나이 값이 가장 큼) 순서로 posts를 주면, 독립 표집 후 순서(theta0 > theta1 > ...)를
    만족하는 표본만 남긴다(기각 표집). 반환: (남긴 표본 (m, K), 통과 비율)."""
    S = np.stack([sample_grid(p, grid, n, rng) for p in posts], axis=1)
    ok = np.all(np.diff(S, axis=1) < 0, axis=1) if older_first else np.all(np.diff(S, axis=1) > 0, axis=1)
    return S[ok], float(ok.mean())
