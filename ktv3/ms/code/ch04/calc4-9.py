# -*- coding: utf-8 -*-
"""계산 4-9: 본문이 쓴 보조 산수. 모든 입력은 논문 본문(또는 초록)의 숫자이거나 앞선 계산의 출력이다."""
import json, itertools, math
import numpy as np
print('=== 계산 4-9 (1) 호톤 호수 14C 오차가 보정 뒤 몇 배가 되었나 (표 숫자: 논문 오차는 14C 오차, 이 책 sd) ===')
rows = [('TA-1471', 80, 116), ('TA-1440', 140, 207), ('TA-1472', 80, 97), ('TA-1439', 150, 188), ('TA-1473', 120, 162), ('TA-1419', 150, 228), ('KIA32076', 40, 60)]
rs = [b / a for _, a, b in rows]
for (n, a, b), r in zip(rows, rs): print('  %-9s %3d -> %3d  배율 %.2f' % (n, a, b, r))
print('  배율 범위 %.2f~%.2f' % (min(rs), max(rs)))
print('  Hoton-1 속도 최대/최소 = %.4f / %.4f = %.2f' % (0.0714, 0.0258, 0.0714 / 0.0258))
print('  Hoton-1 깊이 구간 폭: 25, 23, 25, 25, 25, 25 cm (논문 표 70~95, 147~170, 195~220, 245~270, 295~320, 350~375)')
print()
print('=== 계산 4-9 (2) 텔레츠코예 2006: 1450~1800년 구간의 시료 수 ===')
span = 1800 - 1450
d_cm = span * 0.45 / 10   # 0.45 mm/년 -> cm
print('  구간 %d년 x 0.45 mm/년 = %.2f cm ; 시료 간격 2.5 cm -> 약 %.1f 개' % (span, d_cm, d_cm / 2.5))
d_cm2 = span * 1.15 / 10
print('  Tel 2001-2004: %d년 x 1.15 mm/년 = %.1f cm ; 시료 간격 2.5 cm -> 약 %.1f 개' % (span, d_cm2, d_cm2 / 2.5))
print('  RMSEP 1.23 ℃ / 2 ℃ = %.3f ; / 3 ℃ = %.3f' % (1.23 / 2, 1.23 / 3))
print()
print('=== 계산 4-9 (3) Ugii Nuur 구간 길이(Wang 2009) ===')
ug = [(8.66, 7.8), (7.8, 6.86), (6.86, 3.17), (3.17, 2.34), (2.34, 1.6)]
tot = 0
for a, b in ug:
    print('  %.2f~%.2f ka: %d 년' % (a, b, round((a - b) * 1000))); tot += round((a - b) * 1000)
print('  합 %d 년 (8.66 -> 1.60 ka = %d 년)' % (tot, round((8.66 - 1.6) * 1000)))
print('  서늘하고 습한 시기 8350~8250: %d 년' % 100)
print()
print('=== 계산 4-9 (4) Qigai Nuur(초록) 구간 길이와 다른 기록과의 겹침 ===')
q_forest = 9200 - 2800
c1 = 7400 - 6000; c2 = 4000 - 2800
print('  숲 스텝 우세기 9200~2800: %d 년 ; 춥고 건조 7400~6000 = %d, 4000~2800 = %d, 합 %d 년 = %.1f%%' % (q_forest, c1, c2, c1 + c2, (c1 + c2) / q_forest * 100))
print('  건조 스텝 우세 2800~850: %d 년' % (2800 - 850))
def ov(a, b):   # (old, young) 쌍의 겹침 길이
    return max(0, min(a[0], b[0]) - max(a[1], b[1]))
u_dry = (6860, 3170)
o1 = ov((7400, 6000), u_dry); o2 = ov((4000, 2800), u_dry)
print('  Ugii 건조(6860~3170)와의 겹침: %d + %d = %d 년 (%.0f%% of %d)' % (o1, o2, o1 + o2, (o1 + o2) / (c1 + c2) * 100, c1 + c2))
b_wet = (8500, 3000)
p1 = ov((7400, 6000), b_wet); p2 = ov((4000, 2800), b_wet)
print('  바얀 누르 습윤 최적기(8500~3000)와의 겹침: %d + %d = %d 년' % (p1, p2, p1 + p2))
print()
print('=== 계산 4-9 (5) Gun Nuur(초록) 구간 길이, RMSEP 비교 ===')
print('  10300~7900 = %d 년 ; 7900~2300 = %d 년 ; 합 %d 년 (10300 - 2300 = %d)' % (2400, 5600, 8000, 8000))
print('  RMSEP 46.22 - 41 = %.2f mm ; 바얀 누르 시료별 오차 범위 41.7~51.7 안에 든다: %s' % (46.22 - 41, 41.7 <= 46.22 <= 51.7))
print()
print('=== 계산 4-9 (6) 훌룬, 흡스굴 구간 길이 ===')
print('  훌룬 습윤 8000~6400 = %d 년 ; 서늘하고 건조~극도 건조 6400~3350 = %d 년' % (1600, 6400 - 3350))
print('  흡스굴 11~7 ka = %d 년 ; 6~3.5 ka = %d 년' % (4000, 2500))
print('  Kitoi 공백 6660~6060 = %d 년 (Kobe 2020)' % (6660 - 6060))
print()
print('=== 계산 4-9 (7) 오차울-코토켈 직선거리(대원, 논문 좌표) ===')
def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1; dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
kot = (52 + 47 / 60, 108 + 7 / 60); och = (54 + 14 / 60, 106 + 28 / 60)
print('  코토켈 %.3f N %.3f E ; 오차울 %.3f N %.3f E ; 거리 %.0f km (지구 반지름 6371 km)' % (*kot, *och, hav(*kot, *och)))
print('  오차울이 코토켈보다 숲이 서는 때가 빠른 차: 약 1000 년 (논문 초록)')
print()
print('=== 계산 4-9 (8) 코딩표(calc4-5-out.json)의 보조 집계 ===')
J = json.load(open('calc4-5-out.json'))
M = J['M']
names = list(M)
for n in names:
    k = sum(1 for x in M[n] if x != 0)
    print('  %-34s 부호가 있는 칸 %2d 개 (+ %d, - %d)' % (n, k, sum(1 for x in M[n] if x > 0), sum(1 for x in M[n] if x < 0)))
pairs = []
for a, b in itertools.combinations(names, 2):
    both = [j for j in range(12) if M[a][j] != 0 and M[b][j] != 0]
    if len(both) >= 3:
        pairs.append((sum(1 for j in both if M[a][j] == M[b][j]) / len(both), len(both), a, b))
fr = np.array([p[0] for p in pairs])
print('  쌍 %d 개: 일치율 0.75 이상 %d 개, 0.25 이하 %d 개, 0.00 %d 개, 1.00 %d 개' % (len(pairs), (fr >= 0.75).sum(), (fr <= 0.25).sum(), (fr == 0).sum(), (fr == 1).sum()))
tot_cells = sum(sum(1 for x in v if x != 0) for v in M.values())
print('  전체 부호가 있는 칸 %d (기록 %d x 12 = %d 칸 가운데 %.1f%%)' % (tot_cells, len(names), len(names) * 12, tot_cells / (len(names) * 12) * 100))
# 같은 기록(꽃가루 기록 11개: Ulaan, Kulunda 규조, Chen 종합, Hovsgol 은 꽃가루 외 증거 포함)을 뺀 점검
excl = {'Ulaan(Mischke 2020)', 'Kulunda 규조(Rudaya 2012)', '건조 중앙아시아 종합(Chen 2008)', 'Hovsgol(Prokopenko 2007)'}
sub = {n: v for n, v in M.items() if n not in excl}
def mean_agree(MM):
    rr = []
    for a, b in itertools.combinations(MM, 2):
        both = [j for j in range(12) if MM[a][j] != 0 and MM[b][j] != 0]
        if len(both) >= 3: rr.append(sum(1 for j in both if MM[a][j] == MM[b][j]) / len(both))
    return float(np.mean(rr)), len(rr)
m_all, n_all = mean_agree(M)
m_sub, n_sub = mean_agree(sub)
print('  꽃가루 중심 기록만(%d개: 호수 수위 Ulaan, 규조 Kulunda, 종합 Chen, 규조와 식생 Hovsgol 제외): 쌍 %d 개, 쌍마다 평균 일치율 %.3f (전체 %.3f, 쌍 %d)' % (len(sub), n_sub, m_sub, m_all, n_all))
rng = np.random.default_rng(4109)
sims = []
for _ in range(5000):
    MM = {n: [int(rng.choice([1, -1])) if x != 0 else 0 for x in v] for n, v in sub.items()}
    sims.append(mean_agree(MM)[0])
sims = np.array(sims)
print('  같은 순열 점검(5000회): 중앙 %.2f, 95%% %.2f~%.2f, 관측의 위치 %.1f%%' % (np.median(sims), *np.percentile(sims, [2.5, 97.5]), (sims < m_sub).mean() * 100))
print()
print('=== 계산 4-9 (9) 칸 수 점검 ===')
print('  Chen(2008) 200년 칸: 12000 / 200 = %d 칸' % (12000 // 200))
print('  1000년 칸 12개 x 기록 14개 = %d' % (12 * 14))
