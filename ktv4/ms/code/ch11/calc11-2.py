# -*- coding: utf-8 -*-
"""계산 11-2: 알래스카 오카모크 II 분화(기원전 43년)의 증거 숫자 되풀이(McConnell 등 2020, PNAS 117, 15443). 숫자는 논문 본문(요약 도구 경유).
"""
import json, math
import numpy as np
out = {}
print('=== 계산 11-2 (1) 빙핵 순위 ===')
rank = {'NGRIP2': 1, 'NEEM': 2, 'GISP2': 2, 'Dye3': 4, 'GRIP': 3}
print('  지난 2500년 안의 순위(황, 코어별): ' + ', '.join('%s %d위' % kv for kv in rank.items()))
rv = np.array(list(rank.values()), float)
print('  평균 순위 %.1f, 최악 %d위. 다섯 코어 모두 상위 4위 안' % (rv.mean(), rv.max()))
print('\n=== 계산 11-2 (2) 방사성탄소 범위 안의 43 BCE 위치 ===')
lo, hi = 190, -50   # 기원전 190년 ~ 기원후 50년(기원후는 음수로 쓴 기원전 연도 방식)
width = 190 + 50    # 190 BCE ~ 50 CE (0년 없음: 239년이지만 어림 240)
print('  분화 직전 유기물 보정 2σ: 기원전 190~기원후 50 → 폭 약 %d년. 기원전 43년은 이른 끝에서 %d년(%.0f%%) 지점' % (width, 190 - 43, 100 * (190 - 43) / width))
print('  빙핵 연대 오차 ±2년(고대)과 이 구간 폭의 비 = %.1f%%' % (100 * 4 / width))
print('\n=== 계산 11-2 (3) 사건의 길이 ===')
print('  황 신호: 43 BCE 초에 시작, 늦가을 43 BCE에 최대, 41 BCE 봄에 배경으로 돌아옴 → 43 BCE 초에서 41 BCE 봄까지 2년 남짓')
print('  이른 사건: 45 BCE 초에 시작한 짧은 침적(주로 그린란드 북부). 두 사건의 시작 차 = 2년')
print('\n=== 계산 11-2 (4) 냉각 서술 ===')
vals = [('나이테 유럽 43 BCE 여름', 3.0, '>'), ('나이테 유럽 42 BCE 여름', 2.5, '>'), ('중국 석순 3년 합', 2.0, '>'), ('CESM 모의 여름', 2.0, '~3.0'), ('지중해 모의 계절(최대)', 7.4, '')]
for n, v, k in vals:
    print('  %-28s %s%.1f ℃' % (n, k if k in '>' else '', v) + (' ~ 3.0' if k == '~3.0' else ''))
print('  나이테의 43년 −3 ℃ 초과와 42년 −2.5 ℃ 초과를 더한 두 해 평균은 최소 %.2f ℃ 낮다(하한)' % ((3.0 + 2.5) / 2))
print('  "43 BCE와 42 BCE는 북반구에서 둘째, 여덟째로 추운 해" → 두 해의 순위 차 6, "43~34 BCE는 넷째로 추운 10년"')
print('\n=== 계산 11-2 (5) 황 침적의 코어 사이 흩어짐 ===')
dep = {'NGRIP2': 123, 'NEEM': 110, 'GISP2': 131, 'GRIP': 135, 'Dye3': 128}
v = np.array(list(dep.values()), float)
print('  2년 합 침적(kg/km²): ' + ', '.join('%s %d' % kv for kv in dep.items()) + ' → 평균 %.1f, 표준편차 %.1f(%.1f%%)' % (v.mean(), v.std(ddof=1), 100 * v.std(ddof=1) / v.mean()))
print('  원문의 단위 표기(황산 또는 황 질량)는 요약 도구가 "sulfuric acid"로 돌려주었다. 단위 확인 필요.')
json.dump(out, open('out/calc11-2.json', 'w'), ensure_ascii=False, indent=1)
