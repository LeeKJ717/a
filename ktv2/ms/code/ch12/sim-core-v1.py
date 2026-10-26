# -*- coding: utf-8 -*-
"""12장 공용 함수. 모든 계산은 xp(numpy 또는 cupy)로 짠다. 10장의 xp-demo-v1.py에서 choose_xp, to_host를 가져다 쓴다.
이 컨테이너에는 GPU가 없어 numpy 경로만 실행했다. cupy 경로는 실행하지 못했다.
이 파일의 모형은 이 책이 절차를 보이려고 만든 시연 모형이다. 실제 한반도·황해의 해안선이나 퇴적을 재현하는 모형이 아니다.
단위: 거리 x는 km, 높이 z와 두께 D는 m, 시간 t는 ka(천 년 전, 시간이 흐르면 t가 줄어든다), 확산계수 kappa는 km^2/ka,
      경사 s는 무차원(m/m, 1/344 = 0.0029), 땅 높이 변화율 u는 m/ka(= mm/yr, 융기가 +)."""
import importlib.util, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('xpd', os.path.join(HERE, '..', 'ch10', 'xp-demo-v1.py'))
xpd = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(xpd)
choose_xp, to_host = xpd.choose_xp, xpd.to_host

# 제1권 2장 2.4절(Bloom & Park, 1985가 소개한 Clark 등의 모형 결과, 한국 남단): 16 ka -82 m, 9 ka -31.7 m, 7 ka -12.2 m, 5 ka -2.4 m
# 5 ka 이후는 제1권이 적은 대로 0.48 mm/yr 일정 상승(2.4 m / 5000 yr)으로 0 m에 이른다.
SL_T = [0.0, 5.0, 7.0, 9.0, 16.0]
SL_H = [0.0, -2.4, -12.2, -31.7, -82.0]

def sea_level(xp, t_ka):
    """해수면 높이(m). 위 다섯 점을 직선으로 잇는다(제1권 2.9.3절 선형 보간)."""
    return xp.interp(xp.asarray(t_ka, dtype=float), xp.asarray(SL_T), xp.asarray(SL_H))

def terrain_uniform(xp, x_km, z0, s):
    """한 가지 경사의 땅. s는 길이 P 배열(경사). 반환 (P, nx) 높이(m). x = 0 에서 z0."""
    s = xp.asarray(s, dtype=float)
    return z0 + 1000.0 * s[:, None] * xp.asarray(x_km)[None, :]

def terrain_two_slope(xp, x_km, z0, s1, s2, xb):
    """x < xb 에서 경사 s1, 그 너머에서 s2. 반환 (1, nx)."""
    x = xp.asarray(x_km)
    return (z0 + 1000.0 * (s1 * xp.minimum(x, xb) + s2 * xp.maximum(x - xb, 0.0)))[None, :]

def shoreline(xp, z, x_km, h):
    """바다 쪽(x가 작은 쪽)에서 처음으로 땅 높이 z가 수위 h 이상이 되는 위치(km), 두 격자점 사이는 직선 보간.
    z: (P, nx), h: 길이 P 또는 스칼라. 영역 밖이면 NaN. 반환 길이 P."""
    P, nx = z.shape
    h = xp.broadcast_to(xp.asarray(h, dtype=float), (P,))
    mask = z >= h[:, None]
    idx = xp.argmax(mask, axis=1)
    ok = mask.any(axis=1) & (idx > 0)
    i1 = xp.clip(idx, 1, nx - 1); i0 = i1 - 1
    z0v = xp.take_along_axis(z, i0[:, None], axis=1)[:, 0]
    z1v = xp.take_along_axis(z, i1[:, None], axis=1)[:, 0]
    xv = xp.asarray(x_km)
    frac = (h - z0v) / (z1v - z0v)
    xs = xv[i0] + frac * (xv[i1] - xv[i0])
    return xp.where(ok, xs, xp.nan)

def diffuse_run(xp, D, kappa, dx, dt, nsteps, qdt=None, g=None, snaps=()):
    """1차원 확산 방정식  dD/dt = kappa d2D/dx2 + q g(x)  의 앞으로 가는 차분(FTCS). 칸 중심 격자, 양 끝은 반사(흐름 0).
    D: (P, nx) 두께, kappa: (P,), qdt: (P,) = q*dt (km*m 단위 공급량 x 시간), g: (nx,) 합이 1/dx가 되도록 정규화된 공급 모양.
    r = kappa dt / dx^2 가 0.5를 넘으면 불안정하다. snaps: 스냅샷을 저장할 단계 번호들. 반환 (D, {단계: D 복사본})."""
    r = (xp.asarray(kappa, dtype=float) * dt / (dx * dx))[:, None]
    src = None
    if qdt is not None:
        src = xp.asarray(qdt, dtype=float)[:, None] * xp.asarray(g)[None, :]
    out = {}
    lap = xp.empty_like(D)
    for k in range(1, nsteps + 1):
        lap[:, 1:-1] = D[:, 2:] - 2.0 * D[:, 1:-1] + D[:, :-2]
        lap[:, 0] = D[:, 1] - D[:, 0]
        lap[:, -1] = D[:, -2] - D[:, -1]
        D = D + r * lap
        if src is not None:
            D = D + src
        if k in snaps:
            out[k] = D.copy()
    return D, out

def gauss_source(xp, x_km, xm, sig, dx):
    """공급 모양: 가우스, 합 x dx = 1 (그러면 q의 단위가 m*km/ka, 곧 단위 폭당 퇴적 면적 속도가 된다)."""
    x = xp.asarray(x_km)
    g = xp.exp(-0.5 * ((x - xm) / sig) ** 2)
    return g / (g.sum() * dx)
