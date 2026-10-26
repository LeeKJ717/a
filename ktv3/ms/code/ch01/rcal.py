# -*- coding: utf-8 -*-
"""rcal v1 - 방사성탄소 보정 도우미 (제3권 1장·2장 공용)
곡선 파일: curves/intcal13.14c, curves/intcal20.14c
  이 파일들은 intcal.org 에서 받은 것이 아니라 PyPI 패키지 radiocarbon 0.5.0(GPL-3.0, github.com/jgregoriods/radiocarbon)에
  들어 있던 것을 복사한 것이다. 열: cal BP, 14C 나이, 14C 오차, Delta14C, 오차. 공식 파일과의 대조는 하지 못했다.
방법: 14C 나이 공간에서 가우스 가능도  L(t) = exp(-0.5 (c - mu(t))^2 / (s^2 + sc(t)^2)) / sqrt(s^2 + sc(t)^2)
      mu, sc 는 곡선의 14C 나이와 오차를 1년 간격으로 선형 보간한 값. 1년 격자에서 규격화해 사후 분포로 쓴다.
      구간은 확률 밀도가 높은 격자부터 모아 68.2%, 95.4%가 될 때까지의 연속 구간(HPD)으로 낸다.
"""
import os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_cache = {}

def curve(name):
    if name not in _cache:
        a = np.loadtxt(os.path.join(HERE, 'curves', name + '.14c'), delimiter=',')
        a = a[np.argsort(a[:, 0])]
        _cache[name] = a
    return _cache[name]

def calibrate(c14, sd, name='intcal20', tmin=0, tmax=20000):
    a = curve(name)
    t = np.arange(tmin, tmax + 1, 1.0)
    mu = np.interp(t, a[:, 0], a[:, 1])
    sc = np.interp(t, a[:, 0], a[:, 2])
    v = sd ** 2 + sc ** 2
    p = np.exp(-0.5 * (c14 - mu) ** 2 / v) / np.sqrt(v)
    p /= p.sum()
    return t, p

def hpd(t, p, mass=0.682):
    order = np.argsort(p)[::-1]
    cum = np.cumsum(p[order])
    k = np.searchsorted(cum, mass) + 1
    sel = np.zeros_like(p, dtype=bool)
    sel[order[:k]] = True
    # 연속 구간으로 묶기
    idx = np.where(sel)[0]
    out = []
    if len(idx) == 0:
        return out
    s = idx[0]; prev = idx[0]
    for i in idx[1:]:
        if i != prev + 1:
            out.append((t[s], t[prev], float(p[s:prev + 1].sum())))
            s = i
        prev = i
    out.append((t[s], t[prev], float(p[s:prev + 1].sum())))
    return out

def summary(c14, sd, name='intcal20', tmin=0, tmax=20000):
    t, p = calibrate(c14, sd, name, tmin, tmax)
    mean = float((t * p).sum())
    c = np.cumsum(p)
    med = float(t[np.searchsorted(c, 0.5)])
    sdv = float(np.sqrt((p * (t - mean) ** 2).sum()))
    return dict(mean=mean, median=med, sd=sdv, h68=hpd(t, p, 0.682), h95=hpd(t, p, 0.954), t=t, p=p)

def fmt(h):
    return ' ; '.join('%d~%d' % (a, b) for a, b, m in h)
