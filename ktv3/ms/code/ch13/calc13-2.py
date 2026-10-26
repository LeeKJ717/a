# -*- coding: utf-8 -*-
"""계산 13-2: "396년, 오차의 7.1배"가 무엇의 몇 배인가. 어긋남의 크기를 오차의 종류별로 다시 잰다.
입력(모두 Rudaya 등 2009 표의 숫자를 이 책이 옮긴 것, 4장 계산 4-2와 같다):
  Hoton-2 KIA32076: 깊이 174.5~175 cm, 논문 보정 10,304 ± 56 cal BP. 꽃가루 구역 경계 H4/H3: 깊이 175 cm, 10.7 ka.
  구역 경계(깊이 cm, ka): 205(11.5), 175(10.7), 97.5(7.9), 40(4.9), 0(0).
  Hoton-1 여섯 연대의 논문 보정값(깊이 구간 중앙 cm): 82.5(3122), 158.5(4331), 207.5(6141), 257.5(6841), 307.5(8780), 362.5(10195).
"""
import numpy as np
from scipy import stats

AGE_B = 10700.0; AGE_D = 10304.0; SD_D = 56.0
gap = AGE_B - AGE_D
print('=== 계산 13-2 (1) 기본 숫자 ===')
print('경계 연대 %d - 14C 보정 연대 %d = %d 년' % (AGE_B, AGE_D, gap))
print('논문의 14C 오차 %d 년만 쓰면 %.2f 배(4장 계산 4-2의 7.1배), 이 책의 보정 분포 표준편차 59.6 년을 쓰면 %.2f 배' % (SD_D, gap / SD_D, gap / 59.6))

print('\n=== 계산 13-2 (2) 깊이 보정: 시료는 경계 바로 위(얕은 쪽)에 있다 ===')
rate_H3 = 77.5 / 2800.0; rate_H4 = 30.0 / 800.0     # cm/년
mid = 174.75
dz = 175.0 - mid
exp_age = AGE_B - dz / rate_H3
print('시료 구간 174.5~175 cm 의 중앙 %.2f cm 는 경계 175 cm 보다 %.2f cm 얕다. H3 속도 %.4f cm/년이면 경계 연대에서 %.0f 년 젊다 → 기대 연대 %.0f' % (mid, dz, rate_H3, dz / rate_H3, exp_age))
print('기대 연대 %.0f 와 보정 연대 %d 의 차 = %.0f 년 (경계와의 차 %d 년보다 %.0f 년 작다)' % (exp_age, AGE_D, exp_age - AGE_D, gap, gap - (exp_age - AGE_D)))
print('시료 구간의 두께 0.5 cm 는 H3 속도로 %.0f 년, H4 속도로 %.0f 년' % (0.5 / rate_H3, 0.5 / rate_H4))
print('396년을 깊이 어긋남으로 설명하려면 H3 속도로 %.1f cm, H4 속도로 %.1f cm 가 어긋나야 한다' % (gap * rate_H3, gap * rate_H4))
print('꽃가루 시료 간격 약 2.5 cm(2장이 옮긴 논문 서술) 대비: %.1f 칸, %.1f 칸' % (gap * rate_H3 / 2.5, gap * rate_H4 / 2.5))

print('\n=== 계산 13-2 (3) 경계 연대 쪽의 오차를 넣으면 몇 배가 되는가 ===')
dep = np.array([82.5, 158.5, 207.5, 257.5, 307.5, 362.5]); age = np.array([3122, 4331, 6141, 6841, 8780, 10195], float)
co = np.polyfit(dep, age, 2); res = age - np.polyval(co, dep)
ssr = float((res ** 2).sum()); s_model = np.sqrt(ssr / (len(dep) - 3))
print('Hoton-1 여섯 점의 2차 맞춤 계수 a=%.5f b=%.4f c=%.1f, 잔차 제곱합 %.0f, 제곱평균제곱근 %.0f 년, 자유도 3 의 잔차 표준오차 s = %.0f 년' % (*co, ssr, np.sqrt(ssr / 6), s_model))
cases = []
cases.append(('(가) 14C 오차만(경계는 정확하다고 놓음)', 0.0, '4장의 7.1배'))
cases.append(('(나) 경계를 0.1 ka 단위로 적은 반올림(균등 ±50년)', 100 / np.sqrt(12), '논문 표의 자릿수'))
cases.append(('(다) 가장 가까운 Hoton-1 연대 TA-1419의 보정 오차 229년', 229.0, '점 하나의 오차만 인정'))
cases.append(('(라) 6점 2차식의 잔차 표준오차(자유도 3)', s_model, '이 책이 6점으로 맞춘 식'))
# R^2 = 0.95 에서 잔차 표준편차의 자릿수(시연: 점들이 0~11.5 ka 에 고르게 놓였다고 가정)
sd_age_uniform = 11500 / np.sqrt(12)
s_r2 = np.sqrt(1 - 0.95) * sd_age_uniform
cases.append(('(마) 논문이 적은 R²=0.95의 잔차(시연: 연대가 0~11.5 ka에 고르게 놓였다고 가정)', s_r2, '자릿수 어림'))
print('%-82s %7s %8s %6s %8s' % ('경계 연대 쪽 오차의 가정', '그 오차', '합성 sd', '배', '양쪽 p'))
zrows = []
for nm, sb, note in cases:
    comb = np.hypot(SD_D, sb)
    z = gap / comb
    p = 2 * (1 - stats.norm.cdf(z))
    zrows.append(dict(name=nm, sb=float(sb), comb=float(comb), z=float(z), p=float(p)))
    print('%-82s %7.0f %8.0f %6.2f %8.2g' % (nm, sb, comb, z, p))
# (라) 의 t 분포 꼬리
t_stat = gap / np.hypot(SD_D, s_model)
print('(라)를 자유도 3 의 t 분포로 읽으면 양쪽 p = %.3f (정규분포로 읽으면 %.3f)' % (2 * (1 - stats.t.cdf(t_stat, 3)), 2 * (1 - stats.norm.cdf(t_stat))))
print('(마)의 가정: 연대 표준편차 11,500/√12 = %.0f 년, 잔차 표준편차 √(1-0.95) × %.0f = %.0f 년' % (sd_age_uniform, sd_age_uniform, s_r2))

print('\n=== 계산 13-2 (4) 가까운 Hoton-1 연대와의 비교(조건부) ===')
m1, s1 = 10194.0, 228.0      # TA-1419 이 책 IntCal20 평균과 표준편차(계산 13-1)
m2, s2 = 10298.2, 59.6       # KIA32076
print('TA-1419(깊이 350~375 cm) %.0f ± %.0f 와 경계 10,700: 차 %.0f 년, %.2f 배' % (m1, s1, 10700 - m1, (10700 - m1) / s1))
print('TA-1419 와 KIA32076: 차 %.0f 년, %.2f 배(합성 sd %.0f)' % (m2 - m1, abs(m2 - m1) / np.hypot(s1, s2), np.hypot(s1, s2)))
print('주의: Hoton-1 에서 이 꽃가루 경계가 어느 깊이에 있는지 이 책은 읽지 못했다. 위 비교는 경계가 TA-1419 의 깊이 구간 근처라는 조건에서만 뜻이 있다.')

print('\n=== 계산 13-2 (5) 연대 모형에서 396년은 Hoton-1 깊이로 몇 cm 인가 ===')
def depth_for(a):
    r = np.roots([co[0], co[1], co[2] - a]); r = r[np.isreal(r)].real
    return float(r[(r > 0) & (r < 600)][0])
for a in (10700, 10304, 10000):
    z = depth_for(a); slope = 2 * co[0] * z + co[1]
    print('2차식이 연대 %d 에 주는 Hoton-1 깊이 %.1f cm, 그 깊이의 기울기 %.1f 년/cm' % (a, z, slope))
z1, z2 = depth_for(10700), depth_for(10304)
print('10,700 과 10,304 의 깊이 차 = %.1f cm. 점 TA-1419 의 깊이 구간 폭은 25 cm' % (z1 - z2))
import json
json.dump(dict(z=zrows, s_model=float(s_model), co=[float(x) for x in co], exp_age=float(exp_age), depth_diff=float(z1 - z2)), open('calc13-2-out.json', 'w'), ensure_ascii=False)

print('\n=== 계산 13-2 (6) 이론 상자의 시연값: 같은 차 30 이 한쪽 오차에 따라 몇 배가 되는가 ===')
for sb in (0.0, 30.0):
    comb = np.hypot(5.0, sb)
    print('A = 100 ± 5, B = 130, B 의 불확실성 %.0f: 합성 오차 %.2f, 차 30 은 %.2f 배' % (sb, comb, 30.0 / comb))
