# -*- coding: utf-8 -*-
"""계산 4-10: 쌍마다 일치율이 1.00 또는 0.00 이 되는 쌍이 부호 독립(동전 던지기) 가정에서 몇 개나 나오는가.
입력은 calc4-5-out.json(이 책의 코딩)이다. 시연값(작은 예)과 관측 쌍 50개의 기대값을 함께 낸다."""
import json, itertools
from math import comb
import numpy as np
print('=== 계산 4-10 (1) 시연값: 두 기록이 n칸을 함께 서술하고 부호가 서로 독립이면 ===')
for n in (3, 4, 5, 8):
    p_all = 0.5 ** n
    p_ge75 = sum(comb(n, k) for k in range(n + 1) if k / n >= 0.75) / 2 ** n
    print('  n=%d: 모두 일치 확률 %.4f = 모두 불일치 확률 ; 일치율 0.75 이상 확률 %.4f' % (n, p_all, p_ge75))
print()
J = json.load(open('calc4-5-out.json'))
M = J['M']
names = list(M)
ns = []; fr = []
for a, b in itertools.combinations(names, 2):
    both = [j for j in range(12) if M[a][j] != 0 and M[b][j] != 0]
    if len(both) >= 3:
        ns.append(len(both)); fr.append(sum(1 for j in both if M[a][j] == M[b][j]) / len(both))
ns = np.array(ns); fr = np.array(fr)
print('=== 계산 4-10 (2) 관측 쌍 %d 개에서 기대값(칸마다 독립, 같은 쪽일 확률 0.5) ===' % len(ns))
e_all = (0.5 ** ns).sum()
e_ge75 = sum(sum(comb(n, k) for k in range(n + 1) if k / n >= 0.75) / 2 ** n for n in ns)
e_le25 = sum(sum(comb(n, k) for k in range(n + 1) if k / n <= 0.25) / 2 ** n for n in ns)
print('  일치율 1.00 인 쌍: 관측 %d, 독립 가정의 기대 %.1f' % ((fr == 1).sum(), e_all))
print('  일치율 0.00 인 쌍: 관측 %d, 독립 가정의 기대 %.1f' % ((fr == 0).sum(), e_all))
print('  일치율 0.75 이상: 관측 %d, 기대 %.1f' % ((fr >= 0.75).sum(), e_ge75))
print('  일치율 0.25 이하: 관측 %d, 기대 %.1f' % ((fr <= 0.25).sum(), e_le25))
print('  공통 칸 수 분포: 3칸 %d, 4~5칸 %d, 6~9칸 %d, 10칸 이상 %d' % ((ns == 3).sum(), ((ns >= 4) & (ns <= 5)).sum(), ((ns >= 6) & (ns <= 9)).sum(), (ns >= 10).sum()))
print()
print('=== 계산 4-10 (3) 해석 메모 ===')
print('  쌍마다 칸이 이웃해 이어진 구간(시간적 자기상관)이면 같은 기록이 이웃 칸에서 같은 부호를 가지므로 극단 쌍(1.00, 0.00)이 독립 가정보다 많이 나온다. 이 계산은 그 효과를 빼지 않는다.')
print()
print('=== 계산 4-10 (4) 연대 오차와 1000년 칸 너비 ===')
for e in (56, 116, 229, 396):
    print('  연대 오차(또는 어긋남) %d 년 = 1000년 칸 너비의 %.1f%%' % (e, e / 10))
print('  Hoton-2 H4/H3 경계의 어긋남 396 년은 칸 하나(1000년)의 39.6%. 10.7 ka 와 10.304 ka 는 모두 10~11 ka 칸 안이므로 이 경계가 칸 경계를 넘지는 않는다. 그러나 이 책의 코딩은 논문 본문의 "약 10 ka"를 쓰므로 9~10, 10~11 칸의 경계에 놓인다')
print()
print('=== 계산 4-10 (5) 쿨룬다 PZ I 의 4~5 ka 칸 겹침(칸의 절반 규칙) ===')
for top in (4.4, 4.66):
    print('  PZ I 가 %.2f ka 에서 시작하면 4~5 ka 칸과 겹치는 길이 = %.2f ka (절반 0.50 ka %s)' % (top, top - 4.0, '이상' if top - 4.0 >= 0.5 else '미만'))
