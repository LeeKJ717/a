# -*- coding: utf-8 -*-
"""c14lib: IntCal20 곡선으로 방사성탄소 연대를 보정하는 최소 구현 (제3권 7장, 8장 공용).
곡선 파일: data/ch07/intcal20.14c (pip 패키지 radiocarbon 0.5.0 안에 든 사본; 열: cal BP, 14C BP, 오차, Delta14C, 오차).
이 파일이 공식 IntCal20 배포본과 같은지는 이 컨테이너에서 확인하지 못했다. 7.2절의 검증(논문이 낸 보정 구간과의 비교)이 간접 점검이다.
보정 방식: 정규 우도, 오차는 측정 오차와 곡선 오차를 제곱합으로 합친다. 사전분포는 달력 연대에 대해 균등.
달력 연대 표기: cal BP 에서 기원전은 BC = cal BP - 1949, 기원후는 AD = 1950 - cal BP (연도 0이 없는 관례).
"""
import os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CURVE = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'data', 'ch07', 'intcal20.14c'))
_raw = np.loadtxt(CURVE, delimiter=',')
_raw = _raw[np.argsort(_raw[:, 0])]
CAL = _raw[:, 0]; C14 = _raw[:, 1]; CERR = _raw[:, 2]
GRID = np.arange(0, 12001, 1.0)          # cal BP 0..12000, 1년 간격 (곡선은 이 범위에서 5~20년 간격)
MU = np.interp(GRID, CAL, C14)
SIG = np.interp(GRID, CAL, CERR)

def calibrate(age, err):
    """반환: 격자 GRID(cal BP) 위의 확률 질량(합 1)"""
    s2 = err ** 2 + SIG ** 2
    p = np.exp(-0.5 * (age - MU) ** 2 / s2) / np.sqrt(s2)
    return p / p.sum()

def hpd(p, level=0.954):
    """최고사후밀도 구간들(격자 인덱스 마스크). 반환: 구간 목록 [(cal BP 작은 쪽, 큰 쪽)]와 질량"""
    order = np.argsort(p)[::-1]
    cs = np.cumsum(p[order])
    k = np.searchsorted(cs, level) + 1
    mask = np.zeros_like(p, bool); mask[order[:k]] = True
    segs = []; i = 0; n = len(p)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]: j += 1
            segs.append((GRID[i], GRID[j], p[i:j + 1].sum())); i = j + 1
        else:
            i += 1
    return segs

def outer(p, level=0.954):
    s = hpd(p, level)
    return min(a for a, b, m in s), max(b for a, b, m in s)

def to_year(calbp):
    """cal BP -> 부호 있는 연도(기원전 음수). 연도 0 없음: BC = calBP - 1949"""
    calbp = np.asarray(calbp, float)
    return np.where(calbp >= 1950, -(calbp - 1949), 1950 - calbp)

def fmt_year(y):
    y = int(round(float(y)))
    return ('기원전 %d' % -y) if y < 0 else ('기원후 %d' % y)

def median(p):
    c = np.cumsum(p); return GRID[np.searchsorted(c, 0.5)]

def mean_sd(p):
    m = (GRID * p).sum(); sd = np.sqrt(((GRID - m) ** 2 * p).sum()); return m, sd
