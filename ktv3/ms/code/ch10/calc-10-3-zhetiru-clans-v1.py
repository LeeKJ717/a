# -*- coding: utf-8 -*-
"""계산 10-3. Zhunussova 등(2025) Zhetiru 7개 씨족의 Y 하플로그룹: "일곱 씨족이 한 조상 Karakatysh의 일곱 아들에게서 나왔다"(Blaramberg, 1848)와
"독립된 씨족의 17세기 연합"(Tevkelev, 1748) 가운데 어느 쪽과 맞는가.
입력은 논문이 적은 퍼센트와 시료 수이다. 퍼센트는 반올림되어 있어 개수에는 범위가 있다. 범위의 양 끝에서 Fisher 정확검정을 해서 결론이 반올림에 기대는지 본다."""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stathelp import fisher_two_sided, wilson
from scipy.stats import fisher_exact
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
clans = dict(Kerderi=40, Kereit=32, Ramadan=39, Tabyn=85, Tama=36, Teleu=53, Zhagalbaily=65)
N = sum(clans.values())
print('== 계산 10-3 (a) 시료 수 점검 ==')
print('7개 씨족 합 = %d (논문 350)' % N)
print('고유 하플로타입 260 / 350 = %.3f (논문 "판별력 74%%")' % (260 / 350))
for c, h in [('Kerderi', 26), ('Kereit', 19), ('Ramadan', 28), ('Tabyn', 69), ('Tama', 31), ('Teleu', 33), ('Zhagalbaily', 57)]:
    print('  %-12s 서로 다른 하플로타입 %2d / %2d = %.3f' % (c, h, clans[c], h / clans[c]))
res['N'] = N

print('\n== 계산 10-3 (b) 씨족 우세 하플로그룹의 개수와 부족 전체 개수 ==')
dom = [('Teleu', 'J2a2', 0.83, 0.13), ('Tama', 'C2a1a3', 0.64, 0.10), ('Kereit', 'N1a2', 0.59, 0.10), ('Kerderi', 'R1a1a', 0.55, 0.14)]
rows = []
for clan, hg, pc, pt in dom:
    n = clans[clan]
    k = round(pc * n)
    print('\n%s 씨족 (n = %d): %s 비율 %d%% -> 개수 %.2f 가까운 정수 %d (%d/%d = %.1f%%)' % (clan, n, hg, round(pc * 100), pc * n, k, k, n, 100 * k / n))
    lo_t = math.ceil((pt - 0.005) * N - 1e-9); hi_t = math.floor((pt + 0.005) * N + 1e-9)
    lo_t = max(lo_t, k)
    print('  부족 전체 %s: 퍼센트 %d%% 반올림 범위 -> %d ~ %d명 (씨족 안의 %d명을 포함해야 하므로 하한 %d)' % (hg, round(pt * 100), math.ceil((pt - 0.005) * N), hi_t, k, lo_t))
    best = None
    for T in range(lo_t, hi_t + 1):
        out_k = T - k; out_n = N - n
        p2, ph, pl, den = fisher_two_sided(k, n - k, out_k, out_n - out_k)
        w = wilson(out_k, out_n)
        print('    부족 전체 %d명이면 씨족 밖 %d / %d = %.3f (Wilson %.3f~%.3f), Fisher 양쪽 p = %.3g' % (T, out_k, out_n, out_k / out_n, w[0], w[1], p2))
        rows.append(dict(clan=clan, hg=hg, n=n, k=k, T=T, out_k=out_k, out_n=out_n, p=p2))
res['b'] = rows
print('\n네 씨족 모두 우세 하플로그룹의 씨족 밖 비율이 한 자릿수 퍼센트 안팎이다. 한 씨족에 몰린 하플로그룹이다.')
print('주의: 씨족마다 가장 흔한 하플로그룹을 데이터를 본 뒤에 골랐으므로 위 p는 사후 선택으로 과장되어 있다. p 값의 크기보다 개수(씨족 안 대 밖)를 읽어야 한다.')

print('\n== 계산 10-3 (c) 한 조상의 일곱 아들 가설이 예측하는 것과 관측 ==')
print('부족 수준에서 가장 흔한 하플로그룹은 R1a1a 14%이다(논문의 부족 수준 빈도). 9개 하플로그룹을 합쳐도 86%이고 어느 하나도 15%를 넘지 못한다.')
print('한 남성의 아들 일곱의 부계 후손이라면 Y 하플로그룹은 (그 뒤의 비친자 사건을 빼고) 모두 같아야 한다. 관측은 네 씨족의 우세형이 서로 다른 네 하플로그룹(J2a2, C2a1a3, N1a2, R1a1a)이다.')
print('Tevkelev의 연합설은 서로 독립인 창시 계통을 예측한다. 관측은 이와 같은 방향이다. 다만 Y 염색체만의 결과이고, 비친자 입양·혼인 편입은 계보 기록과 Y 사이의 불일치를 만들 수 있다.')
print('논문의 씨족 사이 분화 FST = 0.29, 남북 묶음 FCT = -0.07 (논문 값).')
json.dump(res, open(os.path.join(OUT, 'calc-10-3.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
