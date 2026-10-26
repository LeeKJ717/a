# -*- coding: utf-8 -*-
"""계산 3-2: 방사성탄소 보정(IntCal20, 이 책의 단순 보정기 c14cal.py).
(1) 아크켐 단계 기준면 4550 ± 350 BP (Galakhov 등 2005, Nazarov 등 2022 가 재인용)를 보정해 Agatova 등(2012)의 아크켐 단계 4.9~4.2 ka 와 견준다.
(2) Ulrich 등(2021) 표 1 의 보정 연대를 되풀이한다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import c14cal as C

def fmt(h):
    return ' ; '.join('%d~%d (%.1f%%)' % (a, b, m * 100) for a, b, m in h)

print('=== 계산 3-2 (1) 4550 ± 350 BP ===')
t, p = C.calibrate(4550, 350)
s = C.summary(4550, 350)
print('평균 %.0f, 표준편차 %.0f, 중앙값 %.0f cal BP' % (s['mean'], s['sd'], s['median']))
print('95.4%% 최고확률구간: %s' % fmt(s['hpd']))
print('68.3%% 최고확률구간: %s' % fmt(C.hpd(t, p, 0.683)))
m_ak = p[(t >= 4200) & (t <= 4900)].sum()
print('아크켐 창(4900~4200 cal BP)에 든 확률 질량 = %.3f' % m_ak)
m_lg = p[(t >= 5500)].sum(); m_young = p[t < 4200].sum()
print('4900 cal BP 보다 오래된 질량 = %.3f ; 4200 보다 젊은 질량 = %.3f' % (p[t > 4900].sum(), m_young))
print('측정 오차가 350년으로 커서 곡선의 굴곡이 거의 지워진다: 95.4%% 구간 폭 = %d 년' % (max(a for a, b, m in s['hpd']) - min(b for a, b, m in s['hpd'])))
print('비교용: 오차 50년이면')
s50 = C.summary(4550, 50); print('   평균 %.0f, 95.4%% %s' % (s50['mean'], fmt(s50['hpd'])))
print('참고: 이 숫자가 Nazarov 등이 재인용한 값 "4550±350 BP, 지의류 264 mm"의 보정 결과이며, 그들은 이 면을 늦은 빙기 또는 이른 홀로세로 보고 이 연대를 믿지 않는다.')
print()
print('=== 계산 3-2 (2) Ulrich 등(2021) 표 1 되풀이 ===')
tab = [  # 시료, 깊이, 물질, 14C, 오차, 논문 보정 평균, 논문 오차
    ('YUL7_519-521', 520, '식물', 3473, 48, 3740, 70),
    ('YUL7_745-751', 748, '퇴적물', 11789, 263, 13750, 340),
    ('YUL7_1997-2000', 1998.5, '퇴적물', 39714, 311, 43020, 270),
    ('YUL15_598-601', 599.5, '식물', 134, 53, 140, 80),
    ('YUL15_779-787', 783, '퇴적물', 37122, 247, 41870, 180),
    ('YUL15_1915-1920a', 1917.5, '식물', 39120, 1178, 43180, 830),
    ('YUL15_1915-1920b', 1917.5, '퇴적물', 40349, 349, 43540, 360),
]
print('%-18s %6s %7s %5s %8s %8s | %9s %6s | %9s %6s | %7s' % ('시료', '깊이', '물질', '14C', '오차', '', '논문평균', '오차', '이 책평균', 'sd', '차이'))
for n, d, m, a, e, pm, pe in tab:
    sm = C.summary(a, e)
    print('%-18s %6.1f %7s %5d ±%-6d %8s | %9d ±%-5d | %9.0f ±%-5.0f | %7.0f' % (n, d, m, a, e, '', pm, pe, sm['mean'], sm['sd'], sm['mean'] - pm))
print('\n95.4% 구간(이 책): ')
for n, d, m, a, e, pm, pe in tab[:4]:
    print('  %s %s' % (n, fmt(C.summary(a, e)['hpd'])))
print('\n주: 논문 표 1 에서 YUL15_598-601 의 최상단 연대를 본문은 140, 논의는 142 ± 49 로 적는다(논문 안의 불일치).')
print('주: 1950 이후(현대) 연대 134 ± 53 BP 는 곡선의 최근 구간이 평탄해 구간이 넓다.')
