# -*- coding: utf-8 -*-
"""계산 3-9: 본문에서 쓰는 산술 점검. 논문이 적은 숫자만 입력으로 쓴다."""
print('=== 계산 3-9 (1) 코다르 1950~60년대 목록의 기준에 따라 달라지는 감소율 (2001/02년 42개 11.68 km² 와 비교) ===')
base = [('Novikova & Grinberg(1972) 재인용: 30개', 18.8), ('Preobrazhensky 재인용(1958~59 조사): 31개', 15.0), ('Plastinin(1998) 재인용: 39개', 15.25)]
now = 11.68
for n, a in base:
    print('  %-48s %6.2f km² -> %.2f km² : 감소 %.1f %%' % (n, a, now, (a - now) / a * 100))
lo = min(a for _, a in base); hi = max(a for _, a in base)
print('  1950~60년대 세 목록의 면적 범위 %.2f~%.2f km², 가장 큰 값 대비 가장 작은 값의 차이 %.1f %%' % (lo, hi, (hi - lo) / hi * 100))
print('  논문이 적은 감소율은 23%')
print()
print('=== 계산 3-9 (2) 아크켐 창과 벨루하가 적은 다른 기록의 가뭄 구간 (기원전 연도) ===')
akkem = (1950 - 4900, 1950 - 4200)      # 서기(음수는 기원전)
print('  아크켐 창 4900~4200 cal BP = 기원전 %d~%d년' % (-akkem[0], -akkem[1]))
other = (-2400, -1800)
ov = max(0, min(-akkem[0] * -1, 0) )
a0, a1 = akkem; b0, b1 = other
ov = max(0, min(a1, b1) - max(a0, b0))
print('  Aizen 등이 "다른 기록" 으로 적은 가뭄 기원전 2400~1800년과 겹침 = %d 년 (아크켐 창 길이 %d 년의 %.0f %%)' % (ov, a1 - a0, ov / (a1 - a0) * 100))
sc = (-2000, -600)
ov2 = max(0, min(a1, sc[1]) - max(a0, sc[0]))
print('  벨루하 심한 백년 가뭄 기원전 2000~600년과 겹침 = %d 년' % ov2)
print()
print('=== 계산 3-9 (3) 영거 드라이아스의 길이 ===')
print('  Aizen 등: 기원전 약 10950~7500년 = %d 년' % (10950 - 7500))
print('  Tarasov 등(2009): 12.8~11.6 ka = %d 년' % round((12.8 - 11.6) * 1000))
print()
print('=== 계산 3-9 (4) 나이테 복제 수와 평균 (Büntgen 등, 2016) ===')
print('  최대 240(1279 AD), 최소 10(98 AD): 비 = %.0f 배' % (240 / 10))
print('  평균 계열 길이 355 년 x 660 계열 / 연대 범위 2370 년 = %.1f 계열/년 ; 최소 10 은 평균의 %.0f %%' % (355 * 660 / 2370, 10 / (355 * 660 / 2370) * 100))

print()
print('=== 계산 3-9 (5) 계산 3-5 의 23개 구간: 구간마다 겹치는 다른 구간의 수 ===')
import itertools, math
def bc(y): return 1950 + y
def ad(y): return 1950 - y
S = {
 'A1': (4900, 4200), 'A2': (2300, 1700), 'A3': (ad(1270), ad(1850)),
 'B1': (bc(10950), bc(7500)), 'B2': (bc(6500), bc(3600)), 'B3': (bc(2000), bc(600)), 'B4': (ad(640), ad(1100)), 'B5': (ad(1480), ad(1880)),
 'C1': (3900, 3600), 'C2': (2700, 1600), 'C3': (ad(1450), ad(1800)),
 'D1': (11000, 9000), 'D2': (7000, 5000), 'D3': (3500, 1500), 'D4': (1500, 0),
 'E1': (10800, 7300), 'E2': (11000, 7000), 'E3': (6000, 3500),
 'F1': (8000, 7000), 'F2': (6200, 5800),
 'G1': (ad(536), ad(660)), 'G2': (ad(1120), ad(1180)), 'G3': (ad(1640), ad(1820)),
}
def ov(a, b):
    return max(0, min(max(a), max(b)) - max(min(a), min(b)))
pairs = [(a, b, ov(S[a], S[b])) for a, b in itertools.combinations(S, 2) if ov(S[a], S[b]) > 0]
print('  구간 %d 개, 쌍 %d 개, 겹치는 쌍 %d 개' % (len(S), len(list(itertools.combinations(S, 2))), len(pairs)))
cnt = {k: sum(1 for p in pairs if k in p[:2]) for k in S}
print('  구간별 겹치는 상대 수:', cnt)
print('  같은 논문 안의 쌍은 시간 순서로 이어지므로 겹치지 않는다(구간 정의상).')
for k in ('G1', 'G2', 'G3', 'A3'):
    print('  %s 와 겹침:' % k, [(b if a == k else a, o) for a, b, o in pairs if k in (a, b)])
print('  A1 과 겹침:', [(b if a == 'A1' else a, o) for a, b, o in pairs if 'A1' in (a, b)])
print()
print('=== 계산 3-9 (6) 오차울(Ochaul)과 코토켈(Kotokel) 사이 거리 ===')
def hav(la1, lo1, la2, lo2):
    R = 6371.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dphi = p2 - p1; dl = math.radians(lo2 - lo1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))
d = hav(54 + 14 / 60, 106 + 28 / 60, 52 + 47 / 60, 108 + 7 / 60)
print('  오차울(54°14′N, 106°28′E)과 코토켈(52°47′N, 108°07′E)의 큰 원 거리 = %.0f km' % d)
print('  오차울 숲 확장 약 11,650 cal BP, 논문이 적은 "약 1000년 뒤" 코토켈 = 약 %d cal BP' % (11650 - 1000))
print('  Kitoi 쇠퇴 약 6660 cal BP 와 중기 신석기 공백 6660~6060 cal BP: 길이 %d 년' % (6660 - 6060))

print()
print('=== 계산 3-9 (7) 흡스굴 E3 와 벨루하 B3 의 겹침 ===')
print('  B3 %s, E3 %s : 겹침 %d 년' % (S['B3'], S['E3'], ov(S['B3'], S['E3'])))
print('  C1 %s 와 B3 %s : 겹침 %d 년 ; C1 와 E3 : 겹침 %d 년' % (S['C1'], S['B3'], ov(S['C1'], S['B3']), ov(S['C1'], S['E3'])))
print()
print('=== 계산 3-9 (8) 텔레츠코예 전달 함수 오차와 소빙기 냉각 크기 ===')
print('  RMSEP 1.23 ℃ 는 냉각 2~3 ℃ 의 %.0f%%~%.0f%%' % (1.23 / 3 * 100, 1.23 / 2 * 100))
print()
print('=== 계산 3-9 (9) 벨루하 연대 불일치 10% 의 크기 ===')
for t in (1400, 1450):
    print('  %d 년 전 연대의 10%% = %.0f 년' % (t, t * 0.10))
