# -*- coding: utf-8 -*-
"""계산 13-7: IntCal20(북반구)과 SHCal20(남반구) 곡선의 비교, 그리고 같은 14C 연대를 두 곡선으로 보정했을 때의 차이.
곡선: data/intcal20.14c (13-1과 같은 사본), data/shcal20.14c (R 패키지 rintcal 1.4.2의 inst/extdata/shcal20.14c. 머리말: Hogg 등 2020, Radiocarbon 62, doi 10.1017/RDC.2020.59).
SHCal20은 남반구 시료용이므로 유라시아 시료에는 쓰지 않는다. 이 계산은 두 곡선이 얼마나 다른지를 크기로 재 두려는 것이다."""
import os, numpy as np
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import c14cal as C
HERE = os.path.dirname(os.path.abspath(__file__))
sh = np.loadtxt(os.path.join(HERE, '..', '..', '..', 'data', 'shcal20.14c'), delimiter=',', comments='#')
sh = sh[np.argsort(sh[:, 0])]
S_CAL, S_C14, S_SIG = sh[:, 0], sh[:, 1], sh[:, 2]
print('=== 계산 13-7 (1) 같은 달력 연대에서 두 곡선의 14C 연대 ===')
print('cal BP | IntCal20 | SHCal20 | 차(SH-IN)')
ds = []
for t in [500, 1000, 2000, 3000, 4000, 4200, 5000, 6000, 7000, 8000, 9000, 10000, 10304, 10700, 11000, 11700]:
    a = np.interp(t, C.CAL, C.C14); b = np.interp(t, S_CAL, S_C14)
    print('%6d | %8.0f | %7.0f | %+5.0f' % (t, a, b, b - a)); ds.append(b - a)
g = np.arange(500, 11701, 50.0)
dd = np.interp(g, S_CAL, S_C14) - np.interp(g, C.CAL, C.C14)
print('500~11,700 cal BP(50년 간격 %d점)에서 SH-IN: 평균 %+.1f, 최소 %+.1f, 최대 %+.1f 14C년' % (len(g), dd.mean(), dd.min(), dd.max()))
print('\n=== 계산 13-7 (2) 같은 측정값을 두 곡선으로 보정 ===')
def cal2(c14, err):
    t = np.arange(0, 55001.0)
    out = []
    for CALx, C14x, SIGx in [(C.CAL, C.C14, C.SIG), (S_CAL, S_C14, S_SIG)]:
        mu = np.interp(t, CALx, C14x); sc = np.interp(t, CALx, SIGx); s2 = err**2 + sc**2
        p = np.exp(-0.5 * (c14 - mu)**2 / s2) / np.sqrt(s2); p /= p.sum()
        out.append((float((t*p).sum()), float(t[np.searchsorted(np.cumsum(p), .5)])))
    return out
for c14, err, nm in [(9130, 40, 'KIA32076(호톤 호)'), (4000, 40, '가상 4000±40'), (3500, 40, '가상 3500±40'), (2000, 40, '가상 2000±40')]:
    (m1, d1), (m2, d2) = cal2(c14, err)
    print('%-18s %5d±%d | IntCal20 평균 %.0f 중앙 %.0f | SHCal20 평균 %.0f 중앙 %.0f | 평균 차 %+.0f년' % (nm, c14, err, m1, d1, m2, d2, m2 - m1))
