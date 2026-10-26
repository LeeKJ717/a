# -*- coding: utf-8 -*-
"""계산 3-1: 벨루하 빙핵(Bl2003, Aizen 등 2016)의 깊이-연대 표를 되풀이한다.
입력은 모두 Aizen 등(2016)이 적은 숫자이다(웹 요약 도구가 건네 준 core-reader 본문). 시추 연도는 2003.
(1) 표지 층마다 깊이/경과 연수 = 평균 층 두께(물당량 m/년)를 구하고 표면 근처 값 0.34 와 견줘 얇아진 정도를 본다.
(2) 가장 단순한 Nye 모형 t(z) = -(H/a) ln(1 - z/H) 에 H=145.87 m w.e., a=0.34 를 넣어 예측 연대를 표지 층과 견준다. 이 모형은 이 책의 시연이며 논문의 흐름 모형(k=1.53)이 아니다.
(3) 방사성탄소 점 사이의 평균 층 두께와 몬테카를로(10만 번) 구간.
"""
import numpy as np
rng = np.random.default_rng(3101)
H = 145.87           # m w.e. 총 두께
A0 = 0.34            # m w.e./년 표면 근처 평균 집적(논문: 약 0.34~0.36, 위쪽 14.1 m w.e. 에서 0.35)
DRILL = 2003
marks = [  # 이름, 깊이(m w.e.), 연도(AD)
    ('삼중수소 1963(772 TU)', 14.11, 1963),
    ('삼중수소 1958(68.5 TU)', 15.49, 1958),
    ('노바룹타 1912', 27.56, 1912),
    ('퉁구스카 1908', 28.5, 1908),
    ('1842 먼지 폭풍', 41.0, 1842),
    ('탐보라 1815', 46.25, 1815),
    ('창바이산 화산 약 1000 AD', 117.3, 1000),
]
print('=== 계산 3-1 (1) 표지 층의 평균 층 두께 ===')
print('H = %.2f m w.e., 표면 근처 a = %.2f m w.e./년, 시추 %d' % (H, A0, DRILL))
print('%-26s %8s %6s %8s %12s %12s' % ('표지', '깊이', '연수', '평균두께', '두께/a', 'Nye 1-z/H'))
for n, z, y in marks:
    yrs = DRILL - y
    thick = z / yrs
    print('%-26s %8.2f %6d %8.3f %12.2f %12.2f' % (n, z, yrs, thick, thick / A0, 1 - z / H))
print()
print('=== 계산 3-1 (2) Nye 모형 예측 연대 vs 표지 연수 (a=%.2f) ===' % A0)
print('%-26s %8s %10s %10s %8s' % ('표지', '깊이', '표지 연수', 'Nye 예측', '차이'))
for n, z, y in marks:
    yrs = DRILL - y
    t = -(H / A0) * np.log(1 - z / H)
    print('%-26s %8.2f %10d %10.1f %8.1f' % (n, z, yrs, t, t - yrs))
# 표지 7개에 가장 맞는 a(최소제곱)
zs = np.array([m[1] for m in marks]); ys = np.array([DRILL - m[2] for m in marks], float)
f = -H * np.log(1 - zs / H)       # t = f / a
a_fit = (f @ f) / (f @ ys)   # t = f/a 를 최소제곱으로 맞출 때의 a
print('\n최소제곱 a (t=f/a) = %.4f m w.e./년 ; 이때 잔차(예측-표지):' % a_fit, np.round(f / a_fit - ys, 1))
print('잔차 제곱합 = %.0f' % (((f / a_fit - ys) ** 2).sum()))
print()
print('=== 계산 3-1 (3) 방사성탄소 점 사이의 평균 층 두께 ===')
# 연도: BC 는 음수(1 BC = 0 으로 두면 1년 이하의 어긋남, 아래 간격은 수천 년이라 무시)
rc = [  # 깊이(m w.e.), 연도(달력연도, AD+), 오차
    (145.2, -9075, 1221),
    (142.8, -6197, 473),
    (134.6, -135, 221),
    (121.1, 790, 93),
]
print('점: ', rc)
print('(본문 발견) 논문은 142.8 m 점을 6197 BC 로, 다른 곳에서 6297 BC 로 적는다. 여기서는 6197 을 쓰고 6297 일 때를 아래에 따로 보인다.')
def rates(rc, n=100000):
    out = []
    for i in range(len(rc) - 1):
        z1, y1, s1 = rc[i]; z2, y2, s2 = rc[i + 1]
        dz = z1 - z2
        dy = (y2 + rng.normal(0, s2, n)) - (y1 + rng.normal(0, s1, n))
        ok = dy > 0
        r = dz / dy[ok] * 1000  # mm w.e./년
        out.append((z1, z2, dz, (y2 - y1), ok.mean(), np.percentile(r, [2.5, 50, 97.5])))
    return out
for z1, z2, dz, dy, okf, pr in rates(rc):
    print('%.1f→%.1f m w.e. (%.1f m) 중앙 간격 %d 년 | 순서가 맞는 추출 %.3f | 두께 mm w.e./년 2.5%%=%.2f 50%%=%.2f 97.5%%=%.2f | 표면 a 대비 %.2f%%' % (
        z1, z2, dz, dy, okf, pr[0], pr[1], pr[2], pr[1] / 1000 / A0 * 100))
rc2 = [rc[0], (142.8, -6297, 473), rc[2], rc[3]]
print('\n142.8 m 점을 6297 BC 로 바꾸면:')
for z1, z2, dz, dy, okf, pr in rates(rc2):
    print('%.1f→%.1f m w.e. 중앙 간격 %d 년 | 50%%=%.2f mm w.e./년 (95%%: %.2f~%.2f)' % (z1, z2, dy, pr[1], pr[0], pr[2]))
print('\n간단 확인: 표면에서 첫 점(121.1 m) 까지 평균 = %.1f m / %d 년 = %.1f mm w.e./년' % (121.1, DRILL - 790, 121.1 / (DRILL - 790) * 1000))

import json
json.dump(dict(H=H, A0=A0, DRILL=DRILL, marks=marks, rc=rc, a_fit=float(a_fit)), open('calc3-1-out.json', 'w'), ensure_ascii=False)
