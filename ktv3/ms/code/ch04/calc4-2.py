# -*- coding: utf-8 -*-
"""계산 4-2: 호톤 호수 코어의 퇴적 속도와 꽃가루 구역의 길이(Rudaya 등 2009 표 1과 표 2의 숫자).
(1) Hoton-1 의 6개 보정 연대 사이의 평균 퇴적 속도, 2차 다항식 맞춤(논문이 Hoton-2 연대 모형에 쓴 형식), 잔차.
(2) Hoton-2 꽃가루 구역 H4~H1 의 깊이와 연대에서 구역별 퇴적 속도.
(3) Hoton-2 의 14C 4개 중 '너무 오래됨' 표시가 없는 하나(174.5~175 cm, 10,304 ± 56 cal BP)와 구역 경계(175 cm = 10.7 ka)의 차이.
"""
import numpy as np
print('=== 계산 4-2 (1) Hoton-1: 연대 사이의 퇴적 속도 ===')
dep = np.array([82.5, 158.5, 207.5, 257.5, 307.5, 362.5])      # 깊이 구간의 중앙(cm)
age = np.array([3122, 4331, 6141, 6841, 8780, 10195], float)   # 논문의 보정 연대(cal BP)
err = np.array([119, 199, 106, 188, 166, 229], float)
for i in range(5):
    dz, dt = dep[i + 1] - dep[i], age[i + 1] - age[i]
    print('  %.1f→%.1f cm: Δ깊이 %.0f cm, Δ연대 %.0f 년 → %.4f cm/년 (%.1f 년/cm)' % (dep[i], dep[i + 1], dz, dt, dz / dt, dt / dz))
print('  표면(0 cm, 연대 0 가정)에서 첫 점까지 %.4f cm/년' % (dep[0] / age[0]))
co = np.polyfit(dep, age, 2)
fit = np.polyval(co, dep)
res = age - fit
print('\n2차 다항식(연대 = a·z² + b·z + c, z = 깊이 cm): a=%.5f, b=%.4f, c=%.1f' % tuple(co))
print('  잔차(연대 - 맞춤, 년): ', np.round(res, 0), ' 잔차 제곱합 평균의 제곱근 = %.0f 년 (논문 연대 오차 106~229 년)' % np.sqrt((res ** 2).mean()))
co1 = np.polyfit(dep, age, 1); r1 = age - np.polyval(co1, dep)
print('1차 직선: 기울기 %.2f 년/cm, 잔차 RMS %.0f 년' % (co1[0], np.sqrt((r1 ** 2).mean())))
print('가중(1/오차) 2차 맞춤은 하지 않았다(점이 6개뿐).')
print()
print('=== 계산 4-2 (2) Hoton-2 꽃가루 구역별 퇴적 속도 (표 2: 깊이 cm, 연대 ka) ===')
zones = [('H4', 205, 175, 11.5, 10.7), ('H3', 175, 97.5, 10.7, 7.9), ('H2', 97.5, 40, 7.9, 4.9), ('H1', 40, 0, 4.9, 0.0)]
for n, d0, d1, a0, a1 in zones:
    dz, dt = d0 - d1, (a0 - a1) * 1000
    print('  %s %5.1f→%5.1f cm (%.1f cm) %4.1f→%3.1f ka (%4.0f 년): %.4f cm/년 (%.0f 년/cm)' % (n, d0, d1, dz, a0, a1, dt, dz / dt, dt / dz))
print('  구역 길이 합 = %.1f ka (11.5 ka → 0)' % sum(z[3] - z[4] for z in zones))
print('  → 위쪽 구역일수록 속도가 느리다(H4 → H1: %.4f → %.4f cm/년). 실제 퇴적이 줄어든 것인지 꽃가루 대비로 만든 연대 모형이 만든 것인지 이 책은 정하지 못한다.' % (30 / 800, 40 / 4900))
print()
print('=== 계산 4-2 (3) Hoton-2 의 방사성탄소 점과 구역 경계 ===')
print('KIA32076: 174.5~175 cm, 10,304 ± 56 cal BP. 구역 H4/H3 경계 175 cm = 10.7 ka (논문 표). 차이 = %d 년 = 연대 오차의 %.1f 배' % (10700 - 10304, (10700 - 10304) / 56))
print('논문은 Hoton-1 과의 꽃가루 대비로 연대 모형을 만들었다. 표에서 Hoton-2 의 네 점 중 "너무 오래됨"이나 "아마 너무 오래됨"이 붙지 않은 것은 이 점뿐이다. 경계가 점보다 약 400년 오래 놓인 이유는 이 책이 알 수 없다.')
