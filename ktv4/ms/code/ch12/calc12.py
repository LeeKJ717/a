# -*- coding: utf-8 -*-
"""12장 계산 12-1 ~ 12-6 (본문 절의 차례대로 번호를 매겼다). 입력은 모두 논문이 적은 숫자이며, 가상 값은 '시연값'이라 표시한다.
실행: python3 ms/code/ch12/calc12.py > ms/code/ch12/calc12.log  (작업 폴더 /home/claude/book4)
"""
import json, os
import numpy as np
from scipy.stats import norm, binom

OUT = {}
HERE = os.path.dirname(os.path.abspath(__file__))

print('=== 계산 12-4. 뉴질랜드 남알프스 카메론 빙하 모레인 10개(Putnam 등 2012) ===')
# 논문이 적은 모레인 평균 연대(ka, AD 1950 기준), 1 표준 오차로 적힌 ±, 표본 수
M = [(10.69, 0.41, 6), (9.84, 0.47, 6), (9.14, 0.28, 2), (8.67, 0.29, 1), (8.19, 0.23, 5),
     (7.19, 0.12, 4), (6.89, 0.19, 4), (0.65, 0.03, 4), (0.52, 0.06, 9), (0.18, 0.05, 4)]
n_tot = sum(m[2] for m in M)
print('모레인 수 %d, 표본 수 합 %d (논문: 10Be 연대 45개)' % (len(M), n_tot))
rows = []
for i in range(len(M) - 1):
    a, sa, na = M[i]; b, sb, nb = M[i + 1]
    d = a - b; s = np.hypot(sa, sb); z = d / s; p = norm.cdf(z)
    rows.append((a, b, d, s, z, p))
    print('  %5.2f → %5.2f ka: 간격 %5.2f ka, 합성 오차 %.3f, z = %.2f, 순서가 맞을 확률 %.3f' % (a, b, d, s, z, p))
OUT['moraine'] = M
OUT['moraine_pairs'] = rows
print('  2σ(≈95%)로 서로 구별되지 않는 이웃 쌍(|z|<1.96):', sum(1 for r in rows if r[4] < 1.96), '개 /', len(rows), '쌍')
lapse = 0.0065
print('눈선 온도 환산: 240 m × %.4f °C/m = %.2f °C (논문 약 1.6 °C)' % (lapse, 240 * lapse))
print('  1.0 °C에 해당하는 눈선 높이 = %.0f m' % (1.0 / lapse))
print('  1.6 °C에 해당하는 눈선 높이 = %.0f m' % (1.6 / lapse))
r1, e1, r2, e2 = 0.83, 0.24, 0.93, 0.28
z = (r2 - r1) / np.hypot(e1, e2)
print('빙하 추정 온난화율 %.2f ± %.2f 와 관측 %.2f ± %.2f ℃/세기: 차 %.2f, z = %.2f' % (r1, e1, r2, e2, r2 - r1, z))
print('  1930~2006년(76년) × 0.83/100 = %.2f °C,  1909~2009년(100년) × 0.93/100 = %.2f °C' % (76 * 0.0083, 100 * 0.0093))
OUT['putnam_T'] = dict(snow=240, T=240 * lapse)

print()
print('=== 계산 12-2. 파타고니아 토레 빙하 이른 단계와 해석 쪽 비교(Reynhout 등 2019, Moreno 등 2018) ===')
ab = [(17600, 900), (13500, 500), (9700, 400), (6900, 200), (6100, 300), (4500, 200), (530, 60)]
s4 = [17100, 13520, 9730, 6860, 6080, 4510, 520]
print('초록 값과 본문 4절 값의 차(년), 차/초록 오차:')
for (a, s), b in zip(ab, s4):
    print('  %6d ± %4d vs %6d: 차 %4d (오차의 %.2f배)' % (a, s, b, a - b, abs(a - b) / s))
ages = [a for a, _ in ab]
print('이웃 단계 간격(년):', [ages[i] - ages[i + 1] for i in range(len(ages) - 1)])
hol = [a for a in ages if a < 11700]
print('홀로세 안의 단계 4개(9,700, 6,900, 6,100, 4,500) 사이 간격:', [hol[i] - hol[i + 1] for i in range(3)], '년, 530년 단계까지 간격', 4500 - 530)
print('Moreno 등(2018): 5.8 ka 이후 양(+)의 남극진동형 사건 9회 → 평균 %.0f년에 한 번(5,800/9)' % (5800 / 9))
print('  같은 5.8 ka 이후에 토레 빙하는 4.5 ka와 0.53 ka의 두 단계(6.1 ka는 5.8 ka보다 오래됨)를 적는다. 빙하는 음의 남극진동형 위상에서 전진하고 Moreno의 9회는 양의 위상의 사건이므로 두 숫자는 같은 것을 세지 않는다(9회 대 2단계).')
print('Lamy 등(2010) 창과 Moreno 등(2018) 창이 갈리는 햇수: Lamy "5.5 ka 이후 약화" 대 Moreno "7.5 ka 이후 강함" → 겹쳐 서로 반대인 구간 = %.1f ka' % (5.5 - 0))

print()
print('=== 계산 12-6. 호주 북서 킴벌리 석순 KNI-51의 변화율(Denniston 등 2013) ===')
def rate(d, t0, t1):
    return d / (t0 - t1)
r_a = rate(-8.5 - (-7.5), 9.0, 7.0)
r_b = rate(2.0, 4.2, 1.5)
r_c1 = rate(-1.5, 1.2, 0.9)
r_c2 = rate(-2.0, 1.0, 0.7)
print('이른 홀로세 강화: δ18O -7.5 → -8.5 ‰ (9 → 7 ka): %.2f ‰/ka' % r_a)
print('늦은 홀로세 약화: δ18O +2 ‰ (4.2 → 1.5 ka): %.2f ‰/ka' % r_b)
print('회복 (본문): -1.5 ‰ (1.2 → 0.9 ka): %.2f ‰/ka' % r_c1)
print('회복 (결론): -2 ‰ (1.0 → 0.7 ka): %.2f ‰/ka' % r_c2)
print('회복 속도 / 약화 속도 = %.1f ~ %.1f 배' % (abs(r_c1 / r_b), abs(r_c2 / r_b)))
print('논문 내부 불일치: 같은 회복을 본문은 1.5 ‰(0.3 ka), 결론은 2 ‰(0.3 ka) → 크기 차 %.0f%%' % ((2 - 1.5) / 1.5 * 100))
print('U-Th 연대 92개 / 석순 19개 = %.1f개/석순, 동위원소 분석 1,497 / 연대 92 = %.1f개/연대' % (92 / 19, 1497 / 92))
OUT['kni'] = dict(early=r_a, late=r_b, rec1=r_c1, rec2=r_c2)

print()
print('=== 계산 12-1. 남극 빙핵 숫자의 안팎 점검(Masson 등 2000, Stenni 등 2017, Mulvaney 등 2012, Kingslake 등 2018, Jones 등 2023) ===')
opt = 11.5 - 9.0
print('Masson: 최적기 길이 %.1f ka 동안 약 800년마다 따뜻한 사건 → %.1f개; 나머지 %.1f ka을 1,200년 이상 간격으로 보면 ≤ %.1f개 → 합 ≤ %.1f개 (논문: 9개)' % (opt, opt / 0.8, 11.5 - opt, (11.5 - opt) / 1.2, opt / 0.8 + (11.5 - opt) / 1.2))
print('  9개 / 11.5 ka = 평균 %.0f년에 한 번' % (11.5 / 9 * 1000))
print('Masson 창: 동쪽 후기 최적기 6~3 ka, Ross 해 쪽 7~5 ka. 겹침 = %.0f년' % ((6 - 5) * 1000))
print('  WAIS 분수령 여름 정점 4.1 ka(Jones 등)는 동쪽 창(6~3 ka) 안: %s, Ross 창(7~5 ka) 안: %s' % (3 <= 4.1 <= 6, 5 <= 4.1 <= 7))
print('Stenni: 기록 112개 / 지역 7개 = 지역당 평균 %.1f개. 가장 따뜻한 300~1000 CE(%d년), 가장 추운 1200~1900 CE(%d년), 둘 사이 %d년' % (112 / 7, 1000 - 300, 1900 - 1200, 1200 - 1000))
print('Mulvaney(해설 쪽): 100년 1.56 ± 0.42 °C 는 연 평균 %.3f °C/년의 100년 평균(=1.56 °C/세기). 지난 50년 2.6 ± 1.2 °C/세기. 비 = %.2f' % (1.56 / 100, 2.6 / 1.56))
print('  2.6 ± 1.2 와 1.56 ± 0.42 의 차 %.2f, z = %.2f' % (2.6 - 1.56, (2.6 - 1.56) / np.hypot(1.2, 0.42)))
print('  이른 홀로세 최적기 +1.3 °C(현재 대비)와 LGM -6 °C: 차 %.1f °C' % (1.3 - (-6)))
print('Kingslake: 퇴각 거리 200 ~ 300 km(방사성탄소 ≥200, 모형 최대 ≈300), 풀린 면적 352,000 km². 해수면 상당 재진출 33 cm = Weddell 2 + Ross 31 = %d cm' % (2 + 31))
print('  최소 연대: Weddell 10.2 ka, Ross 9.7 ka → 차 %.1f ka. 전체 부피 최소 1.5 ka와의 차 %.1f ka(Ross), %.1f ka(Weddell)' % (10.2 - 9.7, 9.7 - 1.5, 10.2 - 1.5))
print('  자료: 얼음 밑 퇴적물 36개 시료, 헨리 빙상 융기 면적 약 7,000 km² 대비 풀린 면적 352,000 km² = %.0f배' % (352000 / 7000))
print('Jones 등: 지난 11,000년 기록, 여름 정점 4.1 ka → 정점 이후 %.1f ka, 전체 길이의 %.0f%%' % (4.1, 4.1 / 11.0 * 100))

print()
print('=== 계산 12-7. 남반구 기록의 창을 한 눈금에 놓고 겹침을 센다(창 경계는 논문이 적은 값, 연대 오차 미반영) ===')
# (이름, 시작 ka, 끝 ka, 부호) : 부호는 이 책의 거친 표기. +따뜻함/강함/습함, -차가움/약함/건조
W = [
 ('남극 이른 홀로세 최적기(Masson)', 11.5, 9.0),
 ('남극 Ross 해 쪽 2차 최적기(Masson)', 7.0, 5.0),
 ('동남극 늦은 최적기(Masson)', 6.0, 3.0),
 ('뉴질랜드 빙하 최대 확장(Putnam)', 10.7, 9.8),
 ('파타고니아 편서풍 강함, 52°S(Lamy)', 12.0, 8.5),
 ('파타고니아 편서풍 약화, 52°S(Lamy)', 5.5, 0.0),
 ('파타고니아 편서풍 강함, 51°S(Moreno)', 7.5, 0.0),
 ('호주 킴벌리 몬순 강화(Denniston)', 9.0, 7.0),
 ('호주 킴벌리 몬순 최대 강수(Denniston)', 5.0, 4.0),
 ('호주 퀸즐랜드 습함, 라니냐형(Barr)', 7.7, 3.2),
]
def ov(a, b):
    lo = max(min(a[1], a[2]), min(b[1], b[2]))
    hi = min(max(a[1], a[2]), max(b[1], b[2]))
    return round(max(0.0, hi - lo), 6)
n = len(W)
mat = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        mat[i, j] = ov(W[i], W[j]) * 1000
print('창 목록:')
for i, w in enumerate(W):
    print('  %2d. %s: %.1f ~ %.1f ka (길이 %.0f년)' % (i + 1, w[0], w[1], w[2], abs(w[1] - w[2]) * 1000))
print('겹침(년), 행·열 번호는 위 목록:')
for i in range(n):
    print('  ' + ' '.join('%5d' % mat[i, j] for j in range(n)))
pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
nz = [(i, j) for i, j in pairs if mat[i, j] > 0]
print('쌍 %d개 중 겹치는 쌍 %d개, 겹치지 않는 쌍 %d개' % (len(pairs), len(nz), len(pairs) - len(nz)))
print('주목할 쌍:')
for (i, j) in [(0, 3), (0, 4), (4, 5), (5, 6), (4, 6), (3, 7), (2, 8), (7, 2)]:
    print('  %s ↔ %s: %d년' % (W[i][0], W[j][0], mat[i, j]))
print('0~12 ka(12,000년)을 1,000년 칸 12개로 나눈 칸마다 몇 개의 창이 덮는가:')
cover = []
for k in range(12):
    lo, hi = k, k + 1
    c = sum(1 for w in W if min(w[1], w[2]) < hi and max(w[1], w[2]) > lo)
    cover.append(c)
print('  ', cover)

print('4.2 ka(4,200년 전)를 덮는 창: ', [w[0] for w in W if min(w[1], w[2]) <= 4.2 <= max(w[1], w[2])], '→ %d개 / %d개' % (sum(1 for w in W if min(w[1], w[2]) <= 4.2 <= max(w[1], w[2])), len(W)))
OUT['windows'] = [(w[0], w[1], w[2]) for w in W]
OUT['mat'] = mat.tolist()
OUT['cover'] = cover

print()
print('=== 계산 12-3. 남미 남부 편서풍 두 기록의 같은 구간 불일치와 유한 오차 ===')
print('Lamy: 12 ~ 8.5 ka 강함(%.1f ka), 8.5 ~ 5.5 ka 중간(%.1f ka), 5.5 ka 이후 약함(%.1f ka)' % (12 - 8.5, 8.5 - 5.5, 5.5))
print('Moreno: 7.5 ka 이후 강함(%.1f ka). 두 기록이 같은 부호(강함)인 구간: 7.5 ~ 5.5 ka = %.1f ka 중 Lamy는 "중간"이므로 정의에 따라 다름' % (7.5, 7.5 - 5.5))
print('  두 기록이 명확히 반대(Lamy 약함, Moreno 강함)인 구간: 5.5 ~ 0 ka = %.1f ka, 최근 7.5 ka의 %.0f%%' % (5.5, 5.5 / 7.5 * 100))
print('  Lamy의 기록 지점 위도 52°37′S ~ 52°54′S, Moreno 약 51°S: 위도 차 약 %.1f°(≈%.0f km)' % (52.62 - 51.0, (52.62 - 51.0) * 111.2))

print()
print('=== 계산 12-5. 모레인 평균의 ±가 표준오차라면 암석 하나의 흩어짐은 얼마인가(가정: Putnam 등 2012의 ±가 평균의 표준오차) ===')
for a, sa, n in M:
    if n >= 2:
        print('  모레인 평균 %.2f ka, ± %.2f, 암석 %d개 → 암석 사이 표준편차 약 %.2f ka (= ± × √n)' % (a, sa, n, sa * np.sqrt(n)))
    else:
        print('  모레인 평균 %.2f ka, 암석 1개 → 표준편차를 구할 수 없다' % a)
sd_e = [sa * np.sqrt(n) for a, sa, n in M if a > 6 and n >= 2]
sd_l = [sa * np.sqrt(n) for a, sa, n in M if a < 1 and n >= 2]
print('  이른~중기 홀로세 모레인(암석 ≥2개)의 표준편차 범위 %.2f ~ %.2f ka, 최근 700년 모레인 %.2f ~ %.2f ka' % (min(sd_e), max(sd_e), min(sd_l), max(sd_l)))
print('  상대 흩어짐(표준편차/평균): 이른 홀로세 %s, 최근 %s' % ([round(sa * np.sqrt(n) / a, 3) for a, sa, n in M if a > 6 and n >= 2], [round(sa * np.sqrt(n) / a, 3) for a, sa, n in M if a < 1 and n >= 2]))
print('--- 이론 상자의 시연값(어느 논문의 값도 아님) ---')
print('  δ18O 정의 시연: 시료의 18O/16O 비가 표준의 0.990배이면 δ = (0.990 - 1) × 1000 = %.1f ‰' % ((0.990 - 1) * 1000))
print('  10Be 시연: 농도 N = 20,000 atoms/g, 생성률 P = 4 atoms/g/yr 라면 노출 연대 = N/P = %.0f 년(침식, 붕괴, 눈 덮임을 무시한 가장 단순한 식)' % (20000 / 4))
print('  같은 암석에서 농도 측정 오차 5%% → 연대 오차 %.0f 년; 이전 노출분 1,000 atoms/g 이 섞이면 연대가 %.0f 년 더 오래 나온다' % (0.05 * 5000, 1000 / 4))
print('  같은 모레인에서 암석 4개가 4.8, 5.0, 5.2, 7.0 ka 이면 평균 %.2f ka, 표준편차 %.2f ka, 표준오차 %.2f ka; 7.0 ka 를 빼면 평균 %.2f ka, 표준오차 %.2f ka' % (np.mean([4.8, 5.0, 5.2, 7.0]), np.std([4.8, 5.0, 5.2, 7.0], ddof=1), np.std([4.8, 5.0, 5.2, 7.0], ddof=1) / 2, np.mean([4.8, 5.0, 5.2]), np.std([4.8, 5.0, 5.2], ddof=1) / np.sqrt(3)))

json.dump(OUT, open(os.path.join(HERE, 'calc12-out.json'), 'w'), ensure_ascii=False, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
