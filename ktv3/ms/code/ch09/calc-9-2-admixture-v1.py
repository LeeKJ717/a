# -*- coding: utf-8 -*-
"""계산 9-2. 혼합 비율의 표준오차와 혼합 시기(세대 수)의 해석.
입력: Jeong 등(2018) 본문의 qpAdm 비율과 표준오차, Jeong 등(2020)의 혼합 세대 수, Maróti 등(2022)의 혼합 연대 구간.
세대 길이를 25~30년으로 바꾸면 연대가 얼마나 흔들리는가를 제1권 11장 계산 11-11(Duggan 등의 세대 길이 민감도)과 같은 방식으로 본다."""
import json, os, math
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
print('== 계산 9-2 (a) Jeong 등(2018): 서쪽 초원 목축민(Sintashta 계열) 비율의 표준오차 ==')
items = [('주 무리, 3원천 모형 (Shamanka_EN + AG3 + Sintashta)', 3.7, 2.0, 0.180),
         ('주 무리, Shamanka_EBA 기반 모형', 6.4, 1.0, None),
         ('이상치 ARS026', 48.6, 2.0, 0.307)]
rows = []
for name, est, se, p in items:
    z = est / se
    lo, hi = est - 1.96 * se, est + 1.96 * se
    # 정규 근사 양쪽 p (0에서 떨어진 정도). 비율은 0 아래로 갈 수 없으므로 구간 하한이 음수이면 0으로 자른 값도 적는다.
    from scipy.stats import norm
    p0 = 2 * (1 - norm.cdf(abs(z)))
    rows.append(dict(name=name, est=est, se=se, z=z, lo=lo, hi=hi, lo_clip=max(0.0, lo), p_zero=p0, p_model=p))
    print('%-52s 추정 %.1f%%, SE %.1f, z = %.2f, 95%% 구간 %.1f ~ %.1f%% (0으로 자르면 %.1f), 0과의 정규 근사 p = %.4f, 논문 모형 P = %s'
          % (name, est, se, z, lo, hi, max(0.0, lo), p0, p))
res['jeong2018'] = rows
# 두 모형의 차이
d = 6.4 - 3.7
print('두 모형의 추정 차이 %.1f%%p. 같은 시료에 대한 두 모형이므로 독립이 아니어서 차이의 SE는 이 책이 계산하지 못한다.' % d)
print('ARS026 비율이 주 무리 6.4%%의 %.1f배' % (48.6 / 6.4))

print('\n== 계산 9-2 (b) Jeong 등(2020): 혼합 세대 수 -> 연수 환산과 세대 길이 민감도 ==')
groups = [('Chemurchek 남부 알타이', 12, 6, 336, 168), ('Altai_MLBA', 10, 2, 290, None), ('Chandman_IA', 18, 4, None, None),
          ('Türkic (혼합 시기 ca. 500 CE)', 8, 2, None, None), ('Uyghur (혼합 시기 ca. 500 CE)', 12, 2, None, None)]
print('논문이 세대 수와 연수를 함께 적은 곳에서 암시되는 세대 길이:')
imp = []
for n, g, sg, yrs, syrs in groups:
    if yrs:
        print('  %-26s %d 세대 -> %d년 : 세대당 %.2f년' % (n, g, yrs, yrs / g))
        imp.append(yrs / g)
    if syrs:
        print('  %-26s ±%d 세대 -> ±%d년 : 세대당 %.2f년' % (n, sg, syrs, syrs / sg))
print('암시되는 세대 길이 범위: %.1f ~ %.1f년 (논문 발췌에 세대 길이가 명시되어 있지 않다)' % (min(imp), max(imp)))
res['implied_gen'] = imp
sens = []
print('\n세대 길이별 환산(연). 평균 ± 1 SE 세대 수를 그대로 곱한 값이다.')
print('%-30s %-12s %s' % ('무리', '세대 수', '  '.join('%2d년/세대' % L for L in (25, 28, 29, 30))))
for n, g, sg, yrs, syrs in groups:
    cells = []
    row = dict(name=n, g=g, sg=sg)
    for L in (25, 28, 29, 30):
        cells.append('%4d ± %3d' % (g * L, sg * L))
        row['L%d' % L] = (g * L, sg * L)
    print('%-30s %2d ± %d     %s' % (n, g, sg, '  '.join(cells)))
    sens.append(row)
res['sensitivity'] = sens
print('\n세대 길이 25년과 30년 사이의 비 = %.2f 배(어느 무리에서나 같다). 연대는 세대 길이에 정비례한다.' % (30 / 25))

print('\nChandman_IA 점검: 혼합 18 ± 4 세대, 논문의 혼합 시기 ca. 750 BCE, 시료 시기 ca. 400~200 BCE')
for L in (25, 28, 29, 30):
    lo_s, hi_s = 400 + 18 * L, 200 + 18 * L
    print('  세대 %d년: 시료가 400~200 BCE이면 혼합은 %d~%d BCE. 750 BCE가 이 안에 %s' % (L, lo_s, hi_s, '있다' if hi_s <= 750 <= lo_s else '없다'))
res['chandman_check'] = {L: (400 + 18 * L, 200 + 18 * L) for L in (25, 28, 29, 30)}
print('\nTürkic 점검: 8 ± 2 세대, 혼합 시기 ca. 500 CE. 암시되는 시료 연대(혼합 + 세대 수 × 세대 길이):')
for L in (25, 29, 30):
    print('  세대 %d년: Türkic %d CE, Uyghur(12세대) %d CE' % (L, 500 + 8 * L, 500 + 12 * L))
print('  (논문 발췌에 Türkic과 Uyghur 시료의 연대가 없다. 위 값은 역산이며 시료 연대와의 대조는 확인 필요.)')

print('\n== 계산 9-2 (c) Maróti 등(2022): 혼합 연대 구간 ==')
iv = [('Mansi-Sarmatian', -643, -431), ('Mansi-Scythian/Hun', 217, 315)]
for n, a, b in iv:
    print('  %-20s %s ~ %s, 폭 %d년, 중앙 %.0f' % (n, ('%d BCE' % -a) if a < 0 else ('%d CE' % a), ('%d BCE' % -b) if b < 0 else ('%d CE' % b), b - a, (a + b) / 2))
print('  두 구간 사이의 간격: 431 BCE에서 217 CE까지 %d년 (서력에 0년이 없으므로 431 + 217 - 1)' % (431 + 217 - 1))
res['maroti_intervals'] = iv
json.dump(res, open(os.path.join(OUT, 'calc-9-2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
