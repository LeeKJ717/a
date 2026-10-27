# -*- coding: utf-8 -*-
"""계산 9-3: 연대의 비교. 마자마 분화(Sigl 등 2022의 빙핵 연대, Egan 등 2015의 방사성탄소 연대), 테라(Pearson 등 2018),
아니아착 II(Sigl 등 2022, Pearson 등 2018이 인용한 빙핵 연대), 보정 곡선의 어긋남을 14C 연수와 퍼밀(‰)로 바꾸기, Marshall 등(2018)의 모형 대 빙핵 비.
BP는 1950년 기준(논문들의 관례). 기원전 연도를 BP로 바꿀 때는 논문이 쓴 +1950을 따른다(5677 BCE = 7627 BP).
"""
import json, math
import numpy as np
out = {}
print('=== 계산 9-3 (1) 마자마 분화 ===')
ice, ice_sd = 5677, 150
ice_bp = ice + 1950
print('  Sigl 등(2022): 기원전 %d ± %d → %d ± %d BP. Egan 등(2015)이 인용한 GISP2 연대 7627 ± 150 BP와 같다(%s)' % (ice, ice_sd, ice_bp, ice_sd, '일치' if ice_bp == 7627 else '불일치'))
eg_lo, eg_hi = 7584, 7682
mid = (eg_lo + eg_hi) / 2
print('  Egan 등(2015) 베이즈 95.4%% 구간 %d~%d cal BP: 폭 %d년, 가운데 %.0f, 반폭 %.0f' % (eg_lo, eg_hi, eg_hi - eg_lo, mid, (eg_hi - eg_lo) / 2))
print('  빙핵 ±150(1σ인지 확인하지 못함)의 구간 %d~%d, 폭 %d. Egan 구간이 그 안에 드는가: %s' % (ice_bp - ice_sd, ice_bp + ice_sd, 2 * ice_sd, '예' if (eg_lo >= ice_bp - ice_sd and eg_hi <= ice_bp + ice_sd) else '아니오'))
print('  가운데 값의 차 = %.0f년 = 빙핵 1σ의 %.2f배. Egan 구간 폭은 빙핵 ±150 구간 폭의 %.0f%%' % (abs(mid - ice_bp), abs(mid - ice_bp) / ice_sd, 100 * (eg_hi - eg_lo) / (2 * ice_sd)))
print('  Egan 구간을 기원전으로: %d~%d BCE (BP − 1950)' % (eg_hi - 1950, eg_lo - 1950))
print('  [이차 자료] 백과사전은 7640 ± 20 cal BP를 Egan 등으로 돌린다. 논문 초록의 구간 반폭은 %.0f년이다(차이 %.0f년)' % ((eg_hi - eg_lo) / 2, (eg_hi - eg_lo) / 2 - 20))
out['mazama'] = dict(ice_bp=ice_bp, ice_sd=ice_sd, egan=[eg_lo, eg_hi], mid=mid)
print('\n=== 계산 9-3 (2) 테라(산토리니)의 방사성탄소 연대와 고고 연대(Pearson 등 2018) ===')
ic13 = (1642, 1559, 1614); icp = (1614, 1538, 1570)
print('  IntCal13 후행 분포(올리브 가지, 모형 7): %d~%d BCE (평균 %d), 폭 %d년' % (ic13[0], ic13[1], ic13[2], ic13[0] - ic13[1]))
print('  ICCP17(연간 자료로 고친 곡선): %d~%d BCE (평균 %d), 폭 %d년' % (icp[0], icp[1], icp[2], icp[0] - icp[1]))
print('  평균의 이동 %d년, 이른 끝 %d년, 늦은 끝 %d년' % (ic13[2] - icp[2], ic13[0] - icp[0], ic13[1] - icp[1]))
arch = (1550, 1500)
ov = max(0, min(icp[0], arch[0]) - max(icp[1], arch[1]))
print('  고고학 쪽 신왕국 시작 c.%d~%d BCE와 ICCP17 구간의 겹침: %d년(%d~%d BCE)' % (arch[0], arch[1], ov, min(icp[0], arch[0]), max(icp[1], arch[1])))
print('  Pearson 등의 결론 "c.1510 BCE보다 늦은 연대는 가능성이 낮다": 늦은 끝 1538과의 거리 %d년' % (1538 - 1510))
print('  Sigl 등(2022): 아니아착 II 약 1628 BCE(빙핵). ICCP17 구간의 이른 끝 1614보다 %d년 이르다' % (1628 - 1614))
print('  Pearson 등(2018)이 인용한 아니아착 II 빙핵 연대 c.1641 BCE와 Sigl 등(2022)의 1628 BCE의 차 = %d년' % (1641 - 1628))
print('  Sigl 등(2022)은 테라가 빙핵에서 확인되지 않았다고 쓴다.')
out['thera'] = dict(ic13=ic13, icp=icp, arch=arch, overlap=ov)
print('\n=== 계산 9-3 (3) 보정 곡선의 어긋남 14C 연수를 퍼밀로 ===')
tau = 8033.0   # 리비 평균 수명(년). 14C 연대의 정의에 쓰는 관례 상수
per_yr = 1000.0 / tau
print('  14C 연대 1년 차이 = 비율 변화 %.4f‰ (평균 수명 %.0f년 관례). 30~40 14C년 = %.1f~%.1f‰ (논문 "4 to 5‰")' % (per_yr, tau, 30 * per_yr, 40 * per_yr))
print('  Brehm 등(2022)의 7176 BCE Δ14C 상승 19.5‰ = %.0f 14C년에 해당(같은 환산). Pearson의 어긋남 30~40년의 %.1f~%.1f배' % (19.5 / per_yr, 19.5 / per_yr / 40, 19.5 / per_yr / 30))
out['permil_per_year'] = per_yr
print('\n=== 계산 9-3 (4) 모형 대 빙핵 침적(Marshall 등 2018, 탐보라) ===')
ice_c = 50.0
rng_ant = (19, 264); rng_gr = (31, 194)
for n, (a, b) in (('남극', rng_ant), ('그린란드', rng_gr)):
    print('  %s 모형 침적 %d~%d kg/km² 대 빙핵 약 %.0f: 비 %.2f~%.2f, 최대/최소 %.1f배' % (n, a, b, ice_c, a / ice_c, b / ice_c, b / a))
print('  논문 초록: 반구 대기 황산염 부담 대 빙상 침적 비는 모형 사이 최대 15배')
out['marshall'] = dict(ant=[19 / 50, 264 / 50], gr=[31 / 50, 194 / 50])
print('  이 비의 정반대(침적에서 부담을 거꾸로 구하기)에서 같은 15배가 그대로 VSSI의 불확도로 번진다고 말할 수는 없다. 논문은 "생각보다 큰 불확도"라고만 쓴다.')
print('\n=== 계산 9-3 (5) 홀로세 초기의 분화와 급속한 해빙(Huybers & Langmuir 2009) ===')
dap_bp = (9500 + 1950, 7000 + 1950)
hl = (12000, 7000)
print('  HolVol 초기 홀로세 활동기 기원전 9500~7000 = %d~%d BP (2500년)' % dap_bp)
print('  Huybers & Langmuir 창 12 ka~7 ka (5000년). 활동기는 창 안에 든다: %s, 창의 %.0f%%' % (dap_bp[0] <= hl[0] and dap_bp[1] >= hl[1], 100 * 2500 / 5000))
print('  분화율 증가: Huybers & Langmuir 2~6배(지상 분화, 기준 대비) 대 HolVol 개수 1.16배(최근 2500년 대비), 황 1.86배 → 서로 정의가 다르다')
print('  CO2: 40 ppm (90%% 신뢰구간 15~70), 상대 폭 %.0f%%~%.0f%%' % (100 * 25 / 40, 100 * 30 / 40))
out['hl'] = dict(window=hl, dap=dap_bp)
json.dump(out, open('out/calc9-3.json', 'w'), ensure_ascii=False, indent=1)
