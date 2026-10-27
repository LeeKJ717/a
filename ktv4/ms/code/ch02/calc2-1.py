# -*- coding: utf-8 -*-
"""계산 2-1: 두 자료 파일의 구성 - 시료 수, 간격, 홀로세 1000년 칸 평균 (GISP2 d18O, EDC 중수소와 온도)."""
import numpy as np
from io2 import gisp2, edc
g = gisp2(); e = edc()
print('=== 계산 2-1 (1) 파일 구성 ===')
print('GISP2 d18O 파일: 행 %d (d18O 가 비어 있던 행은 뺌), 깊이 %.2f~%.2f m, 나이 %.1f~%.1f yr BP' % (len(g), g.depth.min(), g.depth.max(), g.age.min(), g.age.max()))
print('  깊이 간격 중앙값 %.2f m (표본 간격은 2 m 로 보임)' % np.median(np.diff(g.depth)))
h = g[(g.age >= 0) & (g.age <= 11700)]
print('  홀로세(0~11,700 BP) 표본 %d개, 평균 시간 간격 %.1f 년' % (len(h), np.diff(h.age.values).mean()))
print('EDC 파일: 행 %d (중수소가 비어 있던 3행은 뺌), 나이 %.1f~%.1f yr' % (len(e), e.age.min(), e.age.max()))
he = e[(e.age >= 0) & (e.age <= 11700)]
print('  홀로세(0~11,700) 표본 %d개, 평균 시간 간격 %.1f 년' % (len(he), np.diff(he.age.values).mean()))
print()
print('=== 계산 2-1 (2) 1000년 칸별 표본 수와 평균 간격, 평균값 ===')
print('칸(ka)  GISP2 n  간격(년)  d18O 평균  d18O 최소  |  EDC n  간격(년)  dD 평균  T 평균(파일)')
rows = []
for a in range(0, 13):
    sg = g[(g.age >= a * 1000) & (g.age < (a + 1) * 1000)]
    se = e[(e.age >= a * 1000) & (e.age < (a + 1) * 1000)]
    dg = 1000.0 / len(sg); de = 1000.0 / len(se)
    rows.append((a, len(sg), dg, sg.d18o.mean(), sg.d18o.min(), len(se), de, se.dD.mean(), se['T'].mean()))
    print('%2d~%2d  %6d  %7.1f  %9.2f  %9.2f  |  %5d  %7.1f  %7.1f  %8.2f' % (a, a + 1, len(sg), dg, sg.d18o.mean(), sg.d18o.min(), len(se), de, se.dD.mean(), se['T'].mean()))
print()
print('=== 계산 2-1 (3) 홀로세 안쪽(1~9 ka)의 GISP2 d18O 평균 흔들림 ===')
inner = np.array([r[3] for r in rows[1:9]])
print('1~9 ka 여덟 칸 평균들: 평균 %.2f, 최소 %.2f, 최대 %.2f, 범위 %.2f 퍼밀' % (inner.mean(), inner.min(), inner.max(), inner.max() - inner.min()))
allh = g[(g.age >= 1000) & (g.age < 9000)].d18o
print('1~9 ka 전체 표본 %d개의 표준편차 %.2f 퍼밀, 표준오차(독립 가정) %.3f' % (len(allh), allh.std(ddof=1), allh.std(ddof=1) / np.sqrt(len(allh))))
a0 = g[(g.age < 1000)].d18o
print('0~1 ka 평균 %.2f (n=%d). 1~9 ka 평균과의 차 %.2f 퍼밀' % (a0.mean(), len(a0), a0.mean() - allh.mean()))
