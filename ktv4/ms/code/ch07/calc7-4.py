# -*- coding: utf-8 -*-
"""계산 7-4: 크기(그린란드 기온 낙폭)의 논문 간 차이와 강수 방향 집계.
입력: Alley 등 6+-2 C, 0.33 permil/C; Kobashi 3.3 +- 1 C(요약 값); Morrill 그린란드 d18O -0.8~-1.2 permil, 강수 6곳 중 5곳 감소 등."""
import numpy as np
from scipy import stats
print('[A] Alley 6+-2 C x 0.33 permil/C = %.2f +- %.2f permil (그린란드 d18O 낙폭에 해당하는 값)' % (6*0.33, 2*0.33))
lo, hi = 0.8/0.33, 1.2/0.33
print('    Morrill 의 그린란드 d18O -0.8~-1.2 permil 을 같은 0.33 으로 나누면 %.1f ~ %.1f C' % (lo, hi))
print('    (0.33 은 Alley 논문이 쓴 값이다. 시간에 따른 기울기가 다르면 환산값도 달라진다)')
print()
print('[B] 낙폭 6+-2(Alley) 와 3.3+-1(Kobashi): z')
d = 6-3.3; sd = np.hypot(2,1); print('  차 %.1f, 합성 오차 %.2f, z=%.2f (오차를 1시그마로 읽었을 때)' % (d, sd, d/sd))
print('    Barber 의 그린란드 -4~-8 C 범위와 Kobashi 3.3: Barber 하한 -4 와의 차 %.1f' % (4-3.3))
print('    Morrill 환산 2.4~3.6 C 는 Kobashi 3.3 안; Alley 의 6 보다 %.1f~%.1f C 작다' % (6-3.6, 6-2.4))
print()
print('[C] Morrill 강수: 6곳 중 5곳 감소')
k, n = 5, 6
lo, hi = stats.beta.ppf(0.025, k, n-k+1), stats.beta.ppf(0.975, k+1, n-k)
print('  관측 비율 %.2f, Clopper-Pearson 95%% 구간 %.2f ~ %.2f' % (k/n, lo, hi))
p = stats.binomtest(k, n, 0.5, alternative='greater').pvalue
print('  단측 이항 검정(동전 던지기 0.5) p=%.3f; 양측 p=%.3f' % (p, stats.binomtest(k, n, 0.5).pvalue))
print('  6곳은 고른 방법이 논문 안에 있는 선택 표본이므로 전지구 비율로 읽을 수 없다')
print()
print('[D] Morrill d18O 지역별 부호 (논문 요약): 북반구 열대 +0.4~+0.8, 남반구 열대 -0.5~-1.3, 그린란드 -0.8~-1.2, 북대서양/유럽 -0.4~-0.8')
mid = {'그린란드':-1.0,'북대서양/유럽':-0.6,'북반구 열대':0.6,'남반구 열대':-0.9}
for kx,vx in mid.items(): print('  %-12s 중간값 %+.1f permil' % (kx, vx))
print('  구간 폭(최대-최소)의 비: 그린란드 0.4, 북대서양 0.4, 북열대 0.4, 남열대 0.8 permil -> 남반구 열대 구간이 2배 넓다')
print()
print('[E] Hijma: 해수면 도약/배경 속도 비율 = 2.11/1.95 = %.2f (같은 약 200 년 안에서 도약량이 배경 상승량과 비슷)' % (2.11/1.95))
print('    도약 2.11+-0.89 가 0 과 다른가: z=%.2f' % (2.11/0.89))
