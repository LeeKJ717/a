# -*- coding: utf-8 -*-
"""실습 3-1: 14C 연대 <-> 남은 비율, 오차 전파, 가중평균과 카이제곱. 곡선 불필요.
제1권 2장(계산 2-6), 4장(계산 4-6 예 2~5), 9장(계산 9-10), 11장 11.2절 이론 상자와 맞춰 본다."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c14lib import *

def chk(label, mine, vol1, tol):
    ok = abs(mine - vol1) <= tol
    print(f'  {label}: 이 책 {mine:.4f} / 제1권 {vol1} -> {"일치" if ok else "어긋남"} (허용 {tol})')
    return ok

print('[3-1a] 11장 11.2절 이론 상자: t = -8033 ln F')
res = []
for F, v1 in ((0.45, 6414), (0.80, 1793), (0.38, 7773)):
    res.append(chk(f'F={F}', age_from_F(F), v1, 0.5))
print('  8033 = 5568/ln2 =', round(5568 / math.log(2), 3))

print('[3-1b] 9장 이론 상자: 475 BP <-> F')
F = F_from_age(475)
print(f'  F = exp(-475/8033) = {F:.5f}')
chk('F', F, 0.94258, 5e-6)
print(f'  F 를 4자리 0.9425 로 반올림하면 t = {age_from_F(0.9425):.2f}  (제1권 475.7)')
chk('t(0.9425)', age_from_F(0.9425), 475.7, 0.1)
print(f'  1950-475 = {1950-475} (제1권 1475 년); 2050 BP -> {1950-2050} = {year_label(1950-2050)}')

print('[3-1c] 4장 예 5: pMC')
for t, v1 in ((4940, 54.1), (7525, 39.2), (9785, 29.6), (12090, 22.2)):
    chk(f'{t} BP pMC', 100 * F_from_age(t), v1, 0.05)

print('[3-1d] 2장 2.9.6절 예제 3·4, 계산 2-20: 반감기 5730 과 5568(8033) 의 차이')
lam30 = math.log(2) / 5730; lam68 = math.log(2) / 5568
a5730 = -math.log(0.3) / lam30; a5568 = -math.log(0.3) / lam68
chk('f=0.30 (5730) 나이', a5730, 9953, 0.6)
chk('f=0.30 (5568) 나이', a5568, 9671, 0.6)
print(f'  8033 식과 5568 식은 같은 값: {age_from_F(0.3):.1f} / {a5568:.1f}; 5730 과의 차이 {a5730-a5568:.1f} 년 = {100*(a5730/a5568-1):.2f} %  (제1권 282 년, 2.9 %)')
for t, v5730, v5568 in ((12060, 0.2325, 0.2228), (12000, 0.2342, None), (52000, 0.00185, 0.00154), (11460, 0.2500, None), (12660, 0.2162, None)):
    f1_ = math.exp(-lam30 * t); f2_ = math.exp(-lam68 * t)
    chk(f'{t} BP 남은 비율 (5730)', f1_, v5730, 6e-5)
    if v5568: chk(f'{t} BP 남은 비율 (5568)', f2_, v5568, 6e-5)
print(f'  101.38 pMC: 5730 식 {-math.log(1.0138)/lam30:.1f} 년 (제1권 -113), 8033 식 {age_from_F(1.0138):.1f} 년. 음수는 1950 년 이후의 핵실험 14C 라서 "현대" 판정이 맞다.')
print('  제1권 2장은 5730 을 기본으로 쓰고 5568 을 "확인 필요"로 병기한다. 보정 곡선의 14C 나이는 5568(8033) 기준이므로 이 장에서는 8033 식만 쓴다.')

print('[3-1e] 오차 전파: sigma_t = 8033 * sigma_F / F')
for F, sF in ((0.94258, 0.0023), (0.45, 0.003), (0.10, 0.001)):
    print(f'  F={F} +- {sF}: t = {age_from_F(F):.1f} +- {age_err_from_F(F, sF):.1f} BP')
# 몬테카를로로 확인
import numpy as np
rng = np.random.default_rng(20261026)
x = rng.normal(0.45, 0.003, 1_000_000)
t = -TAU * np.log(x)
print(f'  몬테카를로(10^6, F=0.45+-0.003): 평균 {t.mean():.1f}, 표준편차 {t.std():.2f}  (1차식 {age_err_from_F(0.45,0.003):.2f})')
x = rng.normal(0.10, 0.03, 1_000_000)
x = x[x > 0]
t = -TAU * np.log(x)
print(f'  F 의 오차가 크면 1차식이 무너진다 (F=0.10+-0.03): 1차식 {age_err_from_F(0.10,0.03):.0f}, 몬테카를로 표준편차 {t.std():.0f}, 평균 {t.mean():.0f} (점추정 {age_from_F(0.10):.0f})')

print('[3-1f] 4장 예 3, 4: 가중평균과 카이제곱')
d = 8030 - 7525; s = math.hypot(35, 35)
print(f'  U-3 두 날짜: 차이 {d}, sigma {s:.1f}, 비 {d/s:.2f}  (제1권 10.2)')
m, s, c = weighted_mean([12165, 11840, 12030, 12090, 12095], [40, 45, 40, 40, 40])
print(f'  U-4 다섯 날짜: {m:.1f} +- {s:.1f}, chi2 = {c:.1f} (자유도 4)  (제1권 12,052.9 +- 18.3, 32.5)')
m, s, c = weighted_mean([12165, 12030, 12090, 12095], [40, 40, 40, 40])
print(f'  11,840 을 뺀 네 날짜: {m:.1f} +- {s:.1f}, chi2 = {c:.1f} (자유도 3)  (제1권 12,095 +- 20, 5.7)')
from scipy.stats import chi2 as C2
print(f'  임계값 자유도 4: {C2.ppf(0.95,4):.2f}, 자유도 3: {C2.ppf(0.95,3):.2f}  (제1권 9.49, 7.81)')
print('  [시연] 100+-10 과 120+-20:', [round(v, 2) for v in weighted_mean([100, 120], [10, 20])])
print('전부 일치:', all(res))
