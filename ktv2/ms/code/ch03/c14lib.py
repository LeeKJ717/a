# -*- coding: utf-8 -*-
"""3장 공용 함수: 14C 환산, 보정(곡선 필요), 연령-깊이, OSL 나이.
곡선 파일은 getcurves.sh 가 data/ 에 받는다. 곡선이 없으면 보정 함수는 CurveMissing 을 일으킨다.
형식: 3열(cal BP, 14C 나이, 1 시그마), cal BP 오름차순."""
import os
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
TAU = 8033.0            # Libby 반감기 5568 년 / ln2 (관례)


class CurveMissing(Exception):
    pass


# ------------------------------------------------------------------ 14C 환산 (곡선 불필요)
def age_from_F(F, tau=TAU):
    return -tau * math.log(F)


def F_from_age(t, tau=TAU):
    return math.exp(-t / tau)


def age_err_from_F(F, sF, tau=TAU):
    """1차 오차 전파: sigma_t = tau * sigma_F / F"""
    return tau * sF / F


def bp_to_year(calbp):
    """cal BP -> 천문학적 연도(0 이 있음). 음수/0 이하는 기원전 (1-year) 년."""
    return 1950 - calbp


def year_label(y):
    y = int(round(y))
    return f'기원전 {1 - y}년' if y <= 0 else f'기원후 {y}년'


def weighted_mean(vals, sigs):
    w = [1 / s ** 2 for s in sigs]
    m = sum(v * wi for v, wi in zip(vals, w)) / sum(w)
    s = 1 / math.sqrt(sum(w))
    chi2 = sum(((v - m) / sg) ** 2 for v, sg in zip(vals, sigs))
    return m, s, chi2


# ------------------------------------------------------------------ 곡선 읽기와 보정
def load_curve(name):
    """name: 'intcal20' 등. data/3Col_<name>.14C"""
    p = os.path.join(DATA, f'3Col_{name}.14C')
    if not os.path.exists(p):
        raise CurveMissing(f'곡선 입수 확인 필요: {p} 없음 (getcurves.sh 실행)')
    a = np.loadtxt(p)
    return a[:, 0], a[:, 1], a[:, 2]


def calibrate(c14, sd, curve, r=0.0, sr=0.0, step=1.0):
    """곡선 위 모든 cal BP(step 년 격자)에서 가우스 가능도를 계산해 정규화한 확률을 돌려준다.
    각 격자에서 분산 = 측정 sd^2 + 곡선 sigma^2 (OxCal, Bchron 과 같은 기본 방식, 가우스 근사).
    r, sr: 저장 효과(측정값에서 뺄 값과 그 오차). 해양 시료는 해양 곡선 + DeltaR 로 같은 방식을 쓴다."""
    cal, mu, sg = curve
    g = np.arange(cal.min(), cal.max() + step, step)
    m = np.interp(g, cal, mu)
    s = np.interp(g, cal, sg)
    x = c14 - r
    v = sd ** 2 + sr ** 2 + s ** 2
    p = np.exp(-(x - m) ** 2 / (2 * v)) / np.sqrt(v)
    p = p / p.sum()
    return g, p


def hpd(g, p, level=0.954, step=1.0):
    """최고 밀도 구간들. [(시작, 끝, 확률)] cal BP 오름차순(젊은 쪽부터)."""
    o = np.argsort(p)[::-1]
    c = np.cumsum(p[o])
    k = int(np.searchsorted(c, level)) + 1
    sel = np.sort(g[o[:k]])
    segs = []
    s0 = prev = sel[0]
    for x in sel[1:]:
        if x - prev > step * 1.5:
            segs.append((s0, prev)); s0 = x
        prev = x
    segs.append((s0, prev))
    out = []
    for a, b in segs:
        mask = (g >= a) & (g <= b)
        out.append((float(a), float(b), float(p[mask].sum())))
    return out


def median_age(g, p):
    return float(np.interp(0.5, np.cumsum(p), g))


def sample_cal(g, p, n, rng):
    """보정 분포에서 n 개를 뽑는다(격자 안은 균등)."""
    idx = rng.choice(len(g), size=n, p=p)
    return g[idx] + rng.uniform(-0.5, 0.5, size=n)


def fmt_segs(segs, as_year=False):
    parts = []
    for a, b, pr in segs:
        if as_year:
            parts.append(f'{year_label(bp_to_year(b))} ~ {year_label(bp_to_year(a))} ({pr * 100:.1f}%)')
        else:
            parts.append(f'{a:.0f}~{b:.0f} ({pr * 100:.1f}%)')
    return '; '.join(parts)


# ------------------------------------------------------------------ OSL
def osl_age(De, sDe, DR, sDR):
    a = De / DR
    rel = math.sqrt((sDe / De) ** 2 + (sDR / DR) ** 2)
    return a, a * rel, rel


def interp_age_depth(depths, ages, d):
    """깊이 d 에서 나이(선형 보간, 구간 밖은 마지막 두 점으로 외삽하지 않고 NaN)."""
    return float(np.interp(d, depths, ages, left=np.nan, right=np.nan))
