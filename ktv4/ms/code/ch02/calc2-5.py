# -*- coding: utf-8 -*-
"""계산 2-5: EPICA Dome C(EDC) 중수소와 온도 파일의 홀로세 - 단순 환산과 파일 값의 차, 1000년 칸 평균, 낮은 온도의 위치.
논문 값(Jouzel 등 2007, 보충자료): 온도 변화는 현재의 공간 기울기 6.04 퍼밀/°C 로 구하며(dT = d(dD)/6.04), 해수 동위원소 조성 변화를 보정하고,
         원본 근거에서 고도 보정이 있다고 했다. 변화는 마지막 천 년(last millennium)의 평균에 대해 잰다. 중수소 측정 정확도 ± 0.5 퍼밀(1시그마). 시간 눈금은 EDC3.
"""
import numpy as np
from io2 import edc
e = edc()
lm = e[e.age <= 1000]
dD0 = lm.dD.mean()
print('=== 계산 2-5 (1) 마지막 천 년 평균 ===')
print('나이 1000 년 이하 표본 %d개: 중수소 평균 %.2f 퍼밀, 파일의 온도 평균 %.3f °C (논문은 이 평균을 기준으로 삼는다고 했으나 이 파일에서는 0 이 아니다)' % (len(lm), dD0, lm['T'].mean()))
print('파일에서 나이가 가장 어린 표본: %.1f 년' % e.age.min())
print()
print('=== 계산 2-5 (2) 단순 환산 dT = (dD - 기준)/6.04 와 파일의 온도 ===')
e['simple'] = (e.dD - dD0) / 6.04
e['diff'] = e['T'] - e['simple']
print('칸(ka)   파일 T   단순 T   차(파일-단순)')
for a in range(0, 16):
    s = e[(e.age >= a * 1000) & (e.age < (a + 1) * 1000)]
    print('%2d~%2d   %6.2f   %6.2f   %6.2f   (표본 %d)' % (a, a + 1, s['T'].mean(), s.simple.mean(), s['diff'].mean(), len(s)))
h = e[e.age <= 12000]
print('0~12 ka 에서 차의 평균 %.2f, 최소 %.2f, 최대 %.2f. 차와 나이의 상관 %.3f' % (h['diff'].mean(), h['diff'].min(), h['diff'].max(), np.corrcoef(h['diff'], h.age)[0, 1]))
within = np.mean([e[(e.age >= a * 1000) & (e.age < (a + 1) * 1000)]['diff'].std() for a in range(0, 12)])
print('같은 1000년 칸 안에서 차의 표준편차는 평균 %.3f °C 로 칸 사이의 변화(%.2f °C)보다 훨씬 작다 -> 파일의 온도는 중수소에 매끈한 보정 곡선을 더한 값으로 보인다.' % (within, h['diff'].max() - h['diff'].min()))
print('보정 곡선의 성분(해수 동위원소, 고도)은 이 책이 논문 보충자료에서 숫자를 읽지 못했다. 위 차는 그 성분의 합일 뿐이다.')
print()
print('=== 계산 2-5 (3) 홀로세 안에서 1000년 칸 평균의 가장 높은 곳과 낮은 곳 ===')
rows = []
for a in range(0, 12):
    s = e[(e.age >= a * 1000) & (e.age < (a + 1) * 1000)]
    rows.append((a, s['T'].mean(), s.dD.mean(), s.simple.mean()))
rows = np.array(rows)
for nm, col in (('파일 T', 1), ('중수소(보정 없음)', 2)):
    i1, i0 = rows[:, col].argmax(), rows[:, col].argmin()
    print('%s: 가장 높은 칸 %d~%d ka (%.2f), 가장 낮은 칸 %d~%d ka (%.2f), 차 %.2f' % (nm, rows[i1, 0], rows[i1, 0] + 1, rows[i1, col], rows[i0, 0], rows[i0, 0] + 1, rows[i0, col], rows[i1, col] - rows[i0, col]))
print('단순 환산 T 로 보면 8~11 ka 칸의 평균은 %.2f °C, 파일 T 는 %.2f °C' % (rows[8:11, 3].mean(), rows[8:11, 1].mean()))
print()
print('=== 계산 2-5 (4) 표본 간격과 측정 오차의 의미 ===')
he = e[e.age <= 11700]
print('홀로세 EDC 표본 %d개, 평균 간격 %.1f 년. 중수소 측정 오차 0.5 퍼밀(1시그마)은 6.04 퍼밀/°C 로 %.2f °C. 표본 사이 중수소 차이의 표준편차(1계 차분)/sqrt(2) = %.2f 퍼밀' % (len(he), np.diff(he.age.values).mean(), 0.5 / 6.04, np.diff(he.dD.values).std() / np.sqrt(2)))
print('  측정 오차 0.5 퍼밀이 표본 사이 변동 %.2f 퍼밀에 차지하는 분산의 비율: %.1f%% (나머지는 눈 쌓임 잡음과 실제 신호가 섞인 것)' % (np.diff(he.dD.values).std() / np.sqrt(2), 100 * 0.25 / (np.diff(he.dD.values).std() ** 2 / 2)))
print()
print('=== 계산 2-5 (5) 1000년 칸 평균의 표준오차(표본 독립 가정과 1계 자기상관 보정) ===')
def se_ac(x):
    n = len(x); x = np.asarray(x) - np.mean(x)
    r1 = (x[:-1] * x[1:]).sum() / (x * x).sum()
    neff = n * (1 - r1) / (1 + r1) if r1 > 0 else n
    return x.std(ddof=1) / np.sqrt(n), x.std(ddof=1) / np.sqrt(max(neff, 2)), r1, neff
print('칸(ka)   파일 T 평균  표준편차  표준오차(독립)  표준오차(보정)  r1   유효 n')
for a in range(0, 12):
    s = e[(e.age >= a * 1000) & (e.age < (a + 1) * 1000)]
    se1, se2, r1, ne = se_ac(s['T'].values)
    print('%2d~%2d   %8.2f   %6.2f   %8.3f   %8.3f   %5.2f  %5.1f' % (a, a + 1, s['T'].mean(), s['T'].std(ddof=1), se1, se2, r1, ne))
