# -*- coding: utf-8 -*-
"""계산 13-1: 호톤 호수(Hoton-Nur) 연대 일곱 개의 재보정을 되풀이하고, 곡선 판(IntCal20 대 IntCal13)과 확률 질량을 본다.
4장 계산 4-1(ms/code/ch04/calc4-1.py)의 입력을 그대로 가져왔다. 입력은 Rudaya 등(2009) 표의 숫자이며 이 책이 옮겼다.
추가한 것: (1) 4장 로그와 같은 숫자가 나오는지 자체 점검, (2) IntCal13 곡선(1장 폴더의 사본)으로 같은 일곱 점을 보정,
(3) KIA32076 보정 분포에서 10,700 cal BP 이상이 차지하는 확률 질량.
곡선 사본은 PyPI 패키지 radiocarbon 0.5.0 안의 파일이며 공식 배포본과 대조하지 못했다(서지 확인 필요).
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c14cal as C
CURVE13 = os.path.abspath(os.path.join(HERE, '..', 'ch01', 'curves', 'intcal13.14c'))
a13 = np.loadtxt(CURVE13, delimiter=',')
a13 = a13[np.argsort(a13[:, 0])]
T = np.arange(0.0, 20000.0 + 1, 1.0)


def cal13(c14, err):
    mu = np.interp(T, a13[:, 0], a13[:, 1]); sc = np.interp(T, a13[:, 0], a13[:, 2])
    v = err ** 2 + sc ** 2
    p = np.exp(-0.5 * (c14 - mu) ** 2 / v) / np.sqrt(v)
    p /= p.sum()
    mean = float((T * p).sum()); sd = float(np.sqrt(((T - mean) ** 2 * p).sum()))
    return mean, sd, p


# 깊이 구간(cm), 14C, 오차, 논문 보정 평균, 논문 오차, 실험실 번호
ROWS = [
    ('Hoton-1', (70, 95), 2950, 80, 3122, 119, 'TA-1471'),
    ('Hoton-1', (147, 170), 3900, 140, 4331, 199, 'TA-1440'),
    ('Hoton-1', (195, 220), 5360, 80, 6141, 106, 'TA-1472'),
    ('Hoton-1', (245, 270), 5975, 150, 6841, 188, 'TA-1439'),
    ('Hoton-1', (295, 320), 7910, 120, 8780, 166, 'TA-1473'),
    ('Hoton-1', (350, 375), 9070, 150, 10195, 229, 'TA-1419'),
    ('Hoton-2', (174.5, 175), 9130, 40, 10304, 56, 'KIA32076'),
]
print('=== 계산 13-1 (1) 일곱 점의 재보정: IntCal20(4장 되풀이)과 IntCal13 ===')
print('%-8s %-10s %5s %4s | %6s %4s | %6s %4s %5s | %6s %4s %5s | %s' % ('코어', '깊이cm', '14C', '오차', '논문', '오차', 'IC20', 'sd', '차', 'IC13', 'sd', '차', '실험실'))
out = []
d20 = []; d13 = []; d2013 = []
for core, dep, a, e, pm, pe, lab in ROWS:
    s = C.summary(a, e)
    m13, s13, _ = cal13(a, e)
    d20.append(s['mean'] - pm); d13.append(m13 - pm); d2013.append(s['mean'] - m13)
    out.append(dict(core=core, lab=lab, c14=a, err=e, paper=pm, paper_err=pe, ic20=s['mean'], ic20_sd=s['sd'], ic13=m13, ic13_sd=s13))
    print('%-8s %-10s %5d %4d | %6d %4d | %6.0f %4.0f %5.0f | %6.0f %4.0f %5.0f | %s' % (core, '%s~%s' % dep, a, e, pm, pe, s['mean'], s['sd'], s['mean'] - pm, m13, s13, m13 - pm, lab))
d20 = np.array(d20); d13 = np.array(d13); d2013 = np.array(d2013)
print('\nIntCal20 - 논문: 평균 %.1f 년, 절대값 최대 %.1f 년' % (d20.mean(), np.abs(d20).max()))
print('IntCal13 - 논문: 평균 %.1f 년, 절대값 최대 %.1f 년' % (d13.mean(), np.abs(d13).max()))
print('IntCal20 - IntCal13: 평균 %.1f 년, 절대값 최대 %.1f 년' % (d2013.mean(), np.abs(d2013).max()))
# 4장 로그와 같은 숫자인지 점검(4장 로그: 평균 -7.8, 최대 15.0)
assert abs(d20.mean() - (-7.8)) < 0.1 and abs(np.abs(d20).max() - 15.0) < 0.1, '4장 로그와 다르다'
print('(점검) 4장 로그의 평균 -7.8 년, 최대 15.0 년과 같다.')

print('\n=== 계산 13-1 (2) KIA32076(9130 ± 40 BP, 174.5~175 cm)의 보정 분포 ===')
t, p = C.calibrate(9130, 40)
mean = float((t * p).sum()); sd = float(np.sqrt(((t - mean) ** 2 * p).sum()))
cum = np.cumsum(p)
q = lambda x: float(t[np.searchsorted(cum, x)])
print('평균 %.1f, 표준편차 %.1f cal BP. 2.5%% 분위 %.0f, 중앙값 %.0f, 97.5%% 분위 %.0f' % (mean, sd, q(0.025), q(0.5), q(0.975)))
hp = C.hpd(t, p)
print('95.4%% 최고확률구간: %s' % ' ; '.join('%d~%d (%.1f%%)' % (a, b, m * 100) for a, b, m in hp))
top = max(h[0] for h in hp)
print('구간의 오래된 끝 %d cal BP 는 논문 구역 경계 10,700 보다 %d 년 젊다' % (top, 10700 - top))
for lim in (10500, 10600, 10700):
    print('P(연대 >= %d cal BP) = %.4g' % (lim, p[t >= lim].sum()))
# 곡선이 10,700 cal BP 에서 가리키는 14C 연대
mu10700 = float(np.interp(10700.0, C.CAL, C.C14)); mu10304 = float(np.interp(10304.0, C.CAL, C.C14))
print('IntCal20 곡선: 10,700 cal BP 의 14C 연대 %.0f BP, 10,304 cal BP 의 14C 연대 %.0f BP (측정 9130 BP)' % (mu10700, mu10304))
print('→ 경계 연대 10,700 이 맞으려면 이 시료의 14C 연대가 약 %.0f BP 이어야 하고 측정값 9130 은 %.0f 14C년 젊다' % (mu10700, mu10700 - 9130))
json.dump(dict(rows=out, kia=dict(mean=mean, sd=sd, top=int(top), mu10700=mu10700, mu10304=mu10304)), open(os.path.join(HERE, 'calc13-1-out.json'), 'w'), ensure_ascii=False)
