# -*- coding: utf-8 -*-
"""계산 3-6: 이론 상자의 시연값과, 표를 성기게 옮긴 것(Beck 표는 약 3행마다)이 칸 평균에 미치는 영향의 시험.
(1) 가스 나이 = 얼음 나이 - Δage. 시연값. 논문 숫자(Monnin 등 2001): Δage 홀로세 약 2000 yr, 불확실성 약 10%.
(2) 꺾은선 맞춤이 꺾는 점을 되찾는지(시연값, 잡음 없음과 잡음 있음).
(3) Dome C 표(진짜 자료)에서 3행마다 하나씩만 남겨 1000년 칸 평균이 얼마나 달라지는지.
"""
import numpy as np
import common3 as C
print('=== 계산 3-6 (1) 가스 나이 산술(시연값) ===')
for ice in (3000, 8000, 11000):
    d = 2000; e = 0.10 * d
    print('얼음 나이 %5d yr, 얼음-가스 나이 차 %d +- %.0f yr -> 가스 나이 %d +- %.0f yr (오차는 이 한 항만 센 것)' % (ice, d, e, ice - d, e))
print('논문 값: Monnin 등(2001)은 Δage 가 홀로세에 약 2000 yr, 마지막 빙기 최성기에 약 5500 yr 이고 불확실성이 약 10% 라고 적었다 -> 홀로세 약 200 yr, 최성기 약 550 yr.')
print('Ruddiman(2003)의 이산화탄소 8 ka 와 메탄 5 ka 의 차이는 3000 yr. 위 한 항의 오차(약 200 yr)의 %.0f배.' % (3000 / 200))
print()
print('=== (2) 꺾은선 맞춤이 꺾는 점을 되찾는가(시연값) ===')
x = np.arange(0, 10.01, 0.5)           # 시간(ka, 과거->현재)
y0 = np.where(x < 3.0, 266 - 2.0 * x, 260 + 3.0 * (x - 3.0))     # 꺾는 점 3.0 ka, 앞 기울기 -2, 뒤 +3
sse, x0, b = C.hinge_fit(x, y0, 0.5, 9.0, step=0.05)
print('잡음 없는 시연 자료: 꺾는 점 %.2f (참 3.00), 기울기 %.2f, %.2f (참 -2, +3)' % (x0, b[1], b[1] + b[2]))
rng = np.random.default_rng(3406)
est = []
for _ in range(500):
    yn = y0 + rng.normal(0, 2.0, len(x))
    est.append(C.hinge_fit(x, yn, 0.5, 9.0, step=0.05)[1])
print('잡음 표준편차 2 ppm 을 더해 500번 맞춘 꺾는 점: 중앙 %.2f, 2.5~97.5 백분위 %.2f~%.2f' % (np.median(est), *np.percentile(est, [2.5, 97.5])))
print()
print('=== (3) 3행마다 남기기(Dome C 진짜 표, 나이 <= 11,000) ===')
t, yv, s, dep = C.edc()
k = t <= 11000; t, yv = t[k], yv[k]
full = [yv[(t >= a) & (t < a + 1000)].mean() for a in range(0, 11000, 1000)]
mx = 0
for off in range(3):
    sub = np.arange(len(t)) % 3 == off
    ms = [yv[sub & (t >= a) & (t < a + 1000)].mean() if (sub & (t >= a) & (t < a + 1000)).sum() else np.nan for a in range(0, 11000, 1000)]
    dif = np.array(ms) - np.array(full)
    print('시작 %d: 칸 평균 차 최대 %.2f ppm, 평균 %.2f ppm, 점 수 %d' % (off, np.nanmax(np.abs(dif)), np.nanmean(np.abs(dif)), sub.sum()))
    mx = max(mx, np.nanmax(np.abs(dif)))
print('3행마다 남겨도 1000년 칸 평균은 최대 %.2f ppm 달라진다(자료의 점 하나 표준오차 약 1 ppm 과 같은 크기). 메탄 표(Beck)는 같은 방식으로 성기게 옮긴 것이고 행 사이 간격이 고르지 않아, 이 시험은 칸 평균에 대한 참고일 뿐이다.' % mx)
