# -*- coding: utf-8 -*-
"""계산 3-5: 논문들이 적은 시기 구간을 한 시간축(cal BP, 1950 기준)에 올려 겹침을 센다.
각 구간은 논문이 적은 숫자를 그대로 옮긴 것이다(아래 표). BC/AD 는 BP = 1950 - 연도. 'ka'는 논문이 쓴 그대로 천 년 전으로 읽는다.
겹침은 두 구간의 교집합 길이(년)이다. 이 계산은 '논문 서술이 같은 시기를 가리키는가'만 보며 인과를 말하지 않는다.
"""
import itertools, json
def bc(y): return 1950 + y      # BC y년 -> BP
def ad(y): return 1950 - y
S = {  # 이름: (오래된 쪽 BP, 젊은 쪽 BP, 출처)
 'A1 아크켐 단계(큰 전진)':   (4900, 4200, 'Agatova 등 2012'),
 'A2 역사 단계':             (2300, 1700, 'Agatova 등 2012'),
 'A3 아크투 단계':           (ad(1270), ad(1850), 'Agatova 등 2012 (13세기 말~19세기 중반; 시작을 1270으로 가정)'),
 'B1 벨루하 영거 드라이아스':  (bc(10950), bc(7500), 'Aizen 등 2016'),
 'B2 벨루하 홀로세 기후 최적기': (bc(6500), bc(3600), 'Aizen 등 2016'),
 'B3 벨루하 심한 백년 가뭄':   (bc(2000), bc(600), 'Aizen 등 2016'),
 'B4 벨루하 중세 온난기':      (ad(640), ad(1100), 'Aizen 등 2016'),
 'B5 벨루하 소빙기(시베리아)':  (ad(1480), ad(1880), 'Aizen 등 2016'),
 'C1 텔레츠코예 서늘하고 건조': (3900, 3600, 'Rudaya 등 2016'),
 'C2 텔레츠코예 침엽수 최대':   (2700, 1600, 'Rudaya 등 2016'),
 'C3 텔레츠코예 가장 서늘':     (ad(1450), ad(1800), 'Rudaya 등 2016'),
 'D1 열카르스트 침강 시작':     (11000, 9000, 'Ulrich 등 2019'),
 'D2 열카르스트 집중':         (7000, 5000, 'Ulrich 등 2019'),
 'D3 수위 요동과 분지 확장':    (3500, 1500, 'Ulrich 등 2019'),
 'D4 영구동토 재집적':         (1500, 0, 'Ulrich 등 2019 (1.5 ka 이후)'),
 'E1 코토켈 타이가 최대':      (10800, 7300, 'Tarasov 등 2009'),
 'E2 호브스골 강수·유출 증가':  (11000, 7000, 'Prokopenko 등 2007'),
 'E3 호브스골 여름 따뜻, 숲 감소': (6000, 3500, 'Prokopenko 등 2007'),
 'F1 고비 권곡 빙하':          (8000, 7000, 'Batbaatar 등 2018'),
 'F2 참바가라프 신빙기 시작':   (6200, 5800, 'Khandsuren 등 2026 (약 6 ka 로 보고 ±200년 창을 가정)'),
 'G1 늦은 고대 소빙기':        (ad(536), ad(660), 'Büntgen 등 2016'),
 'G2 알타이 12세기 전진':      (ad(1120), ad(1180), 'Nazarov 등 2022'),
 'G3 알타이 17~19세기 전진':   (ad(1640), ad(1820), 'Nazarov 등 2022(17세기~19세기 초; 끝을 1820으로 가정), Solomina 등 2016: 1640~1740 최대'),
}
def ov(a, b):
    lo = max(min(a), min(b)); hi = min(max(a), max(b))
    return max(0, hi - lo)
print('=== 계산 3-5 (1) 구간 표 (BP) ===')
for k, (a, b, src) in S.items():
    print('%-34s %6d ~ %-6d  길이 %5d년   %s' % (k, a, b, abs(a - b), src))
print()
print('=== 계산 3-5 (2) 아크켐 단계(A1)와 겹치는 구간 ===')
a1 = S['A1 아크켐 단계(큰 전진)'][:2]
for k, (a, b, src) in S.items():
    if k.startswith('A1'): continue
    o = ov(a1, (a, b))
    if o > 0: print('  %-34s 겹침 %5d년 (A1 길이의 %.0f%%)' % (k, o, o / 700 * 100))
print('  (A1 4900~4200 BP 는 BC %d~%d 에 해당)' % (4900 - 1950, 4200 - 1950))
print('  벨루하가 이름 붙인 기후 구간 중 A1 과 겹치는 것: ', [k for k in S if k.startswith('B') and ov(a1, S[k][:2]) > 0] or '없음')
print('  벨루하 최적기 끝(BC 3600 = %d BP)과 가뭄 시작(BC 2000 = %d BP) 사이 이름 없는 구간: %d~%d BP (%d년)' % (bc(3600), bc(2000), bc(3600), bc(2000), bc(3600) - bc(2000)))
print('  A1 은 이 이름 없는 구간(%d~%d)과 겹침 %d년' % (bc(3600), bc(2000), ov(a1, (bc(3600), bc(2000)))))
print()
print('=== 계산 3-5 (3) 역사 단계(A2)와 겹치는 구간 ===')
a2 = S['A2 역사 단계'][:2]
for k, (a, b, src) in S.items():
    if k.startswith('A2'): continue
    o = ov(a2, (a, b))
    if o > 0: print('  %-34s 겹침 %5d년 (A2 길이의 %.0f%%)' % (k, o, o / 600 * 100))
print()
print('=== 계산 3-5 (4) 홀로세 이른~중기: 고비 권곡 빙하(F1)와 겹치는 구간 ===')
f1 = S['F1 고비 권곡 빙하'][:2]
for k, (a, b, src) in S.items():
    if k.startswith('F1'): continue
    o = ov(f1, (a, b))
    if o > 0: print('  %-34s 겹침 %5d년 (F1 길이의 %.0f%%)' % (k, o, o / 1000 * 100))
print('  → 같은 시기를 Agatova 등(2012)은 "골짜기 위쪽 빙하가 7 ka 까지 거의 모두 후퇴"(알타이), Batbaatar 등(2018)은 "고비의 권곡 빙하가 8~7 ka 에 자랐다"로 적는다(두 서술은 구간 표에 넣지 않았다: 앞의 것은 경향이고 뒤의 것은 F1)')
print()
print('=== 계산 3-5 (5) 겹치는 쌍의 수 ===')
names = list(S)
pairs = [(i, j, ov(S[i][:2], S[j][:2])) for i, j in itertools.combinations(names, 2) if ov(S[i][:2], S[j][:2]) > 0]
print('겹치는 쌍 수 = %d / 전체 쌍 %d' % (len(pairs), len(names) * (len(names) - 1) // 2))
json.dump({k: S[k][:2] for k in S}, open('calc3-5-intervals.json', 'w'), ensure_ascii=False)
