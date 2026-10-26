# -*- coding: utf-8 -*-
"""계산 4-1: 호톤 호수(Hoton-Nur, 몽골 알타이)의 방사성탄소 연대를 IntCal20 으로 다시 보정한다(Rudaya 등 2009, 표 1).
논문이 적은 보정 연대는 (평균 ± 오차)이다. 이 책의 보정기(c14cal.py)로 같은 14C 연대를 보정해 견준다.
Hoton-1 코어 6개는 Tarasov 등(2000)이 낸 연대를 Rudaya 등이 재수록한 것(논문 표 1의 'Hoton-1' 칸).
Hoton-2 코어는 4개 중 너무 오래된 2개와 의심스러운 1개를 논문이 쓰지 않았다(아래에서 보정은 하지 않는다: 55,000 BP 가까운 값은 곡선 끝이다).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, json
import c14cal as C
def fmt(h):
    return ' ; '.join('%d~%d (%.1f%%)' % (a, b, m * 100) for a, b, m in h)
H1 = [  # 깊이 구간(cm), 14C, 오차, 논문 보정 평균, 논문 오차, 실험실 번호
    ((70, 95), 2950, 80, 3122, 119, 'TA-1471'),
    ((147, 170), 3900, 140, 4331, 199, 'TA-1440'),
    ((195, 220), 5360, 80, 6141, 106, 'TA-1472'),
    ((245, 270), 5975, 150, 6841, 188, 'TA-1439'),
    ((295, 320), 7910, 120, 8780, 166, 'TA-1473'),
    ((350, 375), 9070, 150, 10195, 229, 'TA-1419'),
]
H2 = [((174.5, 175), 9130, 40, 10304, 56, 'KIA32076')]
print('=== 계산 4-1 (1) 호톤 호수 7개 연대의 재보정 ===')
print('%-9s %-10s %6s %5s | %8s %5s | %8s %5s | %6s %6s' % ('코어', '깊이 cm', '14C', '오차', '논문 평균', '오차', '이 책', 'sd', '차이', '차이/논문오차'))
OUT = []
for core, rows in (('Hoton-1', H1), ('Hoton-2', H2)):
    for (d, a, e, pm, pe, lab) in rows:
        s = C.summary(a, e)
        diff = s['mean'] - pm
        OUT.append(dict(core=core, lab=lab, c14=a, err=e, paper=pm, paper_err=pe, mine=s['mean'], mine_sd=s['sd']))
        print('%-9s %-10s %6d ±%-4d | %8d ±%-4d | %8.0f ±%-4.0f | %6.0f %6.2f   %s  [%s]' % (core, '%s~%s' % d, a, e, pm, pe, s['mean'], s['sd'], diff, diff / pe, lab, fmt(s['hpd'])))
d = np.array([o['mine'] - o['paper'] for o in OUT])
print('\n차이 평균 %.1f 년, 절대 차이 최대 %.1f 년. (논문이 쓴 보정 프로그램과 곡선 버전은 이 책이 확인하지 못했다. IntCal20 은 2020년 곡선이라 논문보다 새로울 가능성이 크다)' % (d.mean(), np.abs(d).max()))
print()
print('=== 계산 4-1 (2) 오래된 두 시료의 위치 ===')
for a, lab in ((55000, 'KIA32074(논문: 55,000 +5220/-3140)'), (53580, 'KIA32075(논문: 53,580 +2870/-2110)')):
    print('%s: 14C 연대 %d 가 IntCal20 곡선이 덮는 가장 큰 14C 연대 %.0f 보다 커서 이 책의 보정기로 보정할 수 없다. 논문도 "너무 오래됨"으로 판단했다' % (lab, a, C.C14.max()))
print('KIA29869(32,450 ± 380 BP): 퇴적물 하부(236.5~237 cm)가 후기 갱신세 점토일 수 있다는 논문 서술. 보정하면 %s cal BP 평균 %.0f' % (fmt(C.summary(32450, 380)['hpd']), C.summary(32450, 380)['mean']))
json.dump(OUT, open('calc4-1-out.json', 'w'), ensure_ascii=False)
