# -*- coding: utf-8 -*-
"""계산 10-4. (a) Askapuli 등(2026)의 친족 판정을 공유 염색체 구간의 기대 길이와 대조한다.
(b) Khussainova 등(2022)과 Zhunussova 등(2025)의 개수 산술.
상염색체 유전 지도 길이를 약 3,500 cM로 두는 것은 이 책의 가정이며 논문의 값이 아니다. 조상-후손 사이 공유 길이의 기대치는 3500 / 2^(g-1)(g는 감수분열 수)로 둔다."""
import json, os, math
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
GL = 3500.0
print('== 계산 10-4 (a) 공유 구간 길이의 기대치 (가정: 상염색체 약 %d cM) ==' % GL)
print('직계 조상과 후손이 g번의 감수분열로 이어질 때 기대 공유 길이 = %d / 2^(g-1)' % GL)
rows = []
for g in range(1, 8):
    e = GL / 2 ** (g - 1)
    print('  g = %d: %.0f cM' % (g, e))
    rows.append((g, e))
res['expect'] = rows
obs = 121.6
print('\nCKZ001-CKZ003: 6구간 합 %.1f cM, 구간 평균 %.1f cM. 논문 요약은 CKZ003이 CKZ001의 조상이며 약 4~5세대(100~150년) 사이라고 한다.' % (obs, obs / 6))
for g in (4, 5, 6):
    e = GL / 2 ** (g - 1)
    print('  직계로 g = %d이면 기대 %.0f cM, 관측은 기대의 %.2f배' % (g, e, obs / e))
print('  관측 %.1f cM에 가장 가까운 g = %.2f (log2 환산)' % (obs, 1 + math.log2(GL / obs)))
print('  가능한 이유(이 책이 정하지 못함): 직계가 아닌 방계 관계, 8 cM 미만 구간을 세지 않는 검출 한계, 낮은 커버리지, 가정한 유전 지도 길이.')
print('\nCKZ004(여성)와 남성 세 명: 논문 요약은 1·2촌 관계가 없고 CKZ004는 남성들과 공유 구간이 없다고 쓴다.')
print('  부녀 관계라면 상염색체 공유 길이의 기대치는 g = 1 -> %.0f cM 안팎(전 염색체)이다. 관측은 0이다.' % GL)
res['father_daughter_expect'] = GL
print('  따라서 "Bolghan Ana 영묘의 여성이 Joshi 영묘의 남성의 딸이다"라는 구전이 그 두 사람의 부녀 관계를 뜻한다면 이 자료와 맞지 않는다.')
print('  단, 이 판단은 두 영묘의 유골이 각각 CKZ002와 CKZ004라는 점과 DNA 판정이 정확하다는 점에 기댄다.')
print('\nCKZ001 ROH: 9구간 합 83.2 Mb, 구간 평균 %.2f Mb' % (83.2 / 9))

print('\n== 계산 10-4 (b) Khussainova 등(2022) 개수 산술 ==')
print('1171 = 433 + 475 + 241 + 22 ? %d' % (433 + 475 + 241 + 22))
print('C2-M217 608 / 1171 = %.2f%% (논문 51.9%%)' % (608 / 1171 * 100))
print('R 12.8%% 대 R1a1a 6.5 + R1b 5.6 + R2 0.8 = %.1f (0.1%%p 차이는 반올림 범위 안)' % (6.5 + 5.6 + 0.8))
print('O2-M122 8.03%% x 1171 = %.0f명' % (0.0803 * 1171))
print('분산 분할: 집단(zhuz) 사이 약 9%%, zhuz 안 부족 사이 약 20%% -> 부족 안 약 %d%% (100 - 9 - 20, 이 책의 산술)' % (100 - 9 - 20))
res['khussainova'] = dict(sum=433 + 475 + 241 + 22, c2=608 / 1171, within=100 - 9 - 20)
print('\n== 계산 10-4 (c) Abilev 등(2012)과 Zhunussova 등(2025)의 이름 층위 ==')
print('Abilev의 Kerey는 Middle zhuz의 부족이고 별무리 C3* 76.5%이다. Zhunussova의 Kereit는 Zhetiru(Junior zhuz) 안의 한 씨족이고 N1a2가 59%이다.')
print('이름이 닮았다는 이유로 둘을 합치지 않는다(제1권 11.8절의 원칙).')
json.dump(res, open(os.path.join(OUT, 'calc-10-4.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
