# -*- coding: utf-8 -*-
"""계산 13-6: 연습 5의 풀이. 4장 계산 4-3의 쿨룬다 바닥 연대(404 cm)를 외삽 방식을 바꿔 되풀이한다.
입력(Rudaya 등 2012 표 1을 4장이 옮긴 것): 깊이 0.18, 1.76, 2.56, 3.46 m / 연대 0.52, 2.31, 3.05, 4.03 ka. 코어 바닥 4.04 m. 논문 본문 4.4 ka(4장이 옮김)."""
import numpy as np
d = np.array([0.18, 1.76, 2.56, 3.46]); a = np.array([0.52, 2.31, 3.05, 4.03]); bot = 4.04; paper = 4.4
rows = []
r3 = (d[3]-d[2])/(a[3]-a[2]); rows.append(('마지막 구간 속도(2.56→3.46 m)', a[3]+(bot-d[3])/r3))
r2 = (d[3]-d[1])/(a[3]-a[1]); rows.append(('마지막 두 구간 속도(1.76→3.46 m)', a[3]+(bot-d[3])/r2))
r4 = (d[3]-d[0])/(a[3]-a[0]); rows.append(('네 점 전체 평균 속도', a[3]+(bot-d[3])/r4))
k = np.polyfit(d, a, 1); rows.append(('네 점 직선 회귀(깊이→연대)', np.polyval(k, bot)))
k2 = np.polyfit(d, a, 2); rows.append(('네 점 2차 곡선(깊이→연대)', np.polyval(k2, bot)))
rows.append(('가장 빠른 구간 속도(1.76→2.56 m)', a[3]+(bot-d[3])/((d[2]-d[1])/(a[2]-a[1]))))
rows.append(('가장 느린 구간 속도(0.18→1.76 m)', a[3]+(bot-d[3])/((d[1]-d[0])/(a[1]-a[0]))))
print('=== 계산 13-6 외삽 방식별 코어 바닥(404 cm) 연대 ===')
for n, v in rows: print('%-34s %.2f ka  (논문 4.4 ka와의 차 %+.2f ka)' % (n, v, v-paper))
vals = np.array([v for _, v in rows]); print('범위 %.2f~%.2f ka' % (vals.min(), vals.max()))
print('4.4 ka를 낳는 외삽 방식이 위 일곱 가운데 있는가:', any(abs(v-paper) < 0.05 for v in vals))
print('가장 느린 구간 속도에서 바닥 4.4 ka를 내려면 필요한 속도 %.3f m/ka' % ((bot-d[3])/(paper-a[3])))
print('점 사이 시료 간격 환산: 바닥 아래 0.58 m = 마지막 속도로 %.0f년' % ((bot-d[3])/r3*1000))
