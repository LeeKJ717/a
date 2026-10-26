# -*- coding: utf-8 -*-
"""c14cal v1: 방사성탄소 연대를 보정하는 작은 함수(3장과 4장 공용 사본).
곡선: data/intcal20.14c (PyPI 패키지 radiocarbon 0.5.0 안의 intcal20.14c, SHA-256 0c553685...fbd6a8).
열: cal BP, 14C BP, 14C 오차, Delta14C, Delta14C 오차. 곡선 논문의 서지는 이 작업에서 확인하지 못했다(서지 확인 필요).
방법: 달력 연대 격자(1년)마다 곡선값 mu(t)를 보간해 정규분포 N(mu, 측정오차^2 + 곡선오차^2)의 밀도를 계산하고 합이 1이 되게 맞춘다.
이것은 OxCal, CALIB과 같은 방식의 가장 단순한 형태이며, 두 프로그램과 같은 숫자가 나온다고 주장하지 않는다.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CURVE = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'data', 'intcal20.14c'))
_c = np.loadtxt(CURVE, delimiter=',')
_c = _c[np.argsort(_c[:, 0])]   # 파일은 오래된 쪽부터 적혀 있어 np.interp 를 위해 오름차순으로 바꾼다
CAL, C14, SIG = _c[:, 0], _c[:, 1], _c[:, 2]


def calibrate(c14, err, step=1.0):
    """반환: (cal BP 격자, 확률 질량). 곡선 범위(0~55000)를 넘으면 오류."""
    t = np.arange(0.0, 55000.0 + step, step)
    mu = np.interp(t, CAL, C14)
    sc = np.interp(t, CAL, SIG)
    s2 = err ** 2 + sc ** 2
    p = np.exp(-0.5 * (c14 - mu) ** 2 / s2) / np.sqrt(s2)
    p /= p.sum()
    return t, p


def hpd(t, p, level=0.954):
    """최고 확률 밀도 구간들. 반환: [(시작, 끝, 질량)] (cal BP, 시작이 더 오래됨)."""
    idx = np.argsort(p)[::-1]
    cum = np.cumsum(p[idx])
    k = np.searchsorted(cum, level) + 1
    keep = np.zeros(len(t), bool)
    keep[idx[:k]] = True
    out, i = [], 0
    while i < len(t):
        if keep[i]:
            j = i
            while j + 1 < len(t) and keep[j + 1]:
                j += 1
            out.append((t[j], t[i], p[i:j + 1].sum()))
            i = j + 1
        else:
            i += 1
    return out


def summary(c14, err, level=0.954):
    t, p = calibrate(c14, err)
    mean = float((t * p).sum())
    med = float(t[np.searchsorted(np.cumsum(p), 0.5)])
    sd = float(np.sqrt(((t - mean) ** 2 * p).sum()))
    return dict(mean=mean, median=med, sd=sd, hpd=hpd(t, p, level))
