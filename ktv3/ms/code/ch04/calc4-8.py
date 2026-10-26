# -*- coding: utf-8 -*-
"""계산 4-8: 4장 이론 상자에 쓰는 시연값. 논문 숫자가 아니라 이 책이 정한 가상 값이다."""
import math
print('=== 계산 4-8 (1) 꽃가루 비율의 불확실성 (시연값: 계수 300 알) ===')
for p in (0.05, 0.20, 0.50):
    n = 300
    se = math.sqrt(p * (1 - p) / n)
    z = 1.96
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    print('  p = %.2f : 표준오차 %.3f, 95%% 구간(윌슨) %.3f ~ %.3f  (%.1f ~ %.1f %%)' % (p, se, c - h, c + h, 100 * (c - h), 100 * (c + h)))
print()
print('=== 계산 4-8 (2) 연대-깊이: 일정 속도 가정의 보간 (시연값: 20 cm = 1000 년, 80 cm = 4000 년) ===')
d0, t0, d1, t1 = 20.0, 1000.0, 80.0, 4000.0
rate = (d1 - d0) / (t1 - t0)
print('  속도 %.3f cm/년 = %.1f 년/cm' % (rate, 1 / rate))
for d in (30, 50, 70):
    print('  깊이 %d cm -> 연대 %.0f 년' % (d, t0 + (d - d0) / rate))
print('  보간점의 연대가 두 점의 연대 오차(시연: 각 ±200 년)보다 더 믿을 만하다고 말할 근거는 없다')
print()
print('=== 계산 4-8 (3) 경사 길이 대비 RMSEP (시연값: 예측 오차 40, 40, 40, 40 mm 인 네 시료) ===')
errs = [40, 40, 40, 40]
rmsep = math.sqrt(sum(e * e for e in errs) / len(errs))
print('  RMSEP = %.1f mm ; 경사 길이(관측 범위) 260 mm 이면 %.1f %%' % (rmsep, rmsep / 260 * 100))
print()
print('=== 계산 4-8 (4) 구간 합과 빈틈 점검 (시연값: 세 구간 10~7, 7~4, 4~0 ka) ===')
iv = [(10, 7), (7, 4), (4, 0)]
print('  길이 합 %d 천 년 ; 이어진다: %s' % (sum(a - b for a, b in iv), all(iv[i][1] == iv[i + 1][0] for i in range(len(iv) - 1))))
