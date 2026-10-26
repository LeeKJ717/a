# -*- coding: utf-8 -*-
"""계산 7-5. 기장 기록의 지역별 시작 연대를 달력 연대로 모으고 지역 사이 시간 간격(lag)을 구한다. 거리 좌표는 읽은 논문에 없어 속도는 '1000 km당' 환산표만 둔다.
입력 숫자의 출처: 7장 표 7-6."""
import json, os
# (이름, 오래된 쪽 BC, 젊은 쪽 BC, 출처, 수준). BC=cal BP-1949
def bc(calbp): return calbp - 1949
P = [
 ('Cishan(하북) 저장 구덩이 기장', bc(10300), bc(8700), 'Lu 등 2009의 초록으로 소개된 10,300~8,700 cal BP(ScienceOpen 쪽의 인용 초록)', '초록(2차)'),
 ('서요하 12D56 야생형 기장 2알(제1권 11장)', bc(7900), bc(7750), 'Shelach-Lavi 등 2019(제1권 11장 표)', '제1권'),
 ('한반도 조·기장 도착(제1권 12장)', 3550, 3500, '제1권 12장 계산 12-18, 다섯 서술이 모임', '제1권'),
 ('Dali 염소·양에게 기장 먹임(Hermes 등 2019)', 2700, 2700, 'Hermes 등 2019 초록 "약 기원전 2700"', '초록'),
 ('Aigyrzhal-3 사람 뼈 C4 신호(Motuzaite-Matuzeviciute 등 2022)', 2460, 2204, '보정 2460~2204 cal BC', '초록+본문(요약기)'),
 ('Begash 기장 직접 연대(Frachetti 등 2010, Stevens 2016 재인용)', 2200, 2200, '약 기원전 2200', '재인용'),
 ('유럽 기장 재배 시작(Filipović 등 2020)', 1600, 1501, '기원전 16세기 이후(가장 이르게)', '초록'),
 ('Troy 기장(Stevens 2016 재인용)', 1550, 1550, '약 기원전 1550', '재인용'),
]
print('이름 / 오래된 쪽 BC / 젊은 쪽 BC')
for n, a, b, s, l in P: print('%-62s %6.0f %6.0f' % (n, a, b))
def lag(i, j):
    """i에서 j까지 걸린 시간의 최소, 최대(년): i의 젊은 쪽-j의 오래된 쪽 ~ i의 오래된 쪽-j의 젊은 쪽"""
    a1, b1 = P[i][1], P[i][2]; a2, b2 = P[j][1], P[j][2]
    return a1 - a2 if False else (b1 - a2, a1 - b2)
pairs = [(0, 1), (1, 2), (1, 5), (3, 5), (4, 5), (5, 6), (4, 6), (5, 7), (1, 6)]
out = {}
print('\n시간 간격 lag (년): 앞 기록에서 뒤 기록까지. 최소 = 앞의 젊은 끝에서 뒤의 오래된 끝, 최대 = 앞의 오래된 끝에서 뒤의 젊은 끝')
for i, j in pairs:
    lo, hi = lag(i, j); out['%s -> %s' % (P[i][0], P[j][0])] = (lo, hi)
    print('  %-34s -> %-34s %6.0f ~ %6.0f' % (P[i][0][:34], P[j][0][:34], lo, hi))
print('\n환산표: 경로 1000 km를 위 lag 동안 지났다면 평균 속도(km/년). 거리는 이 책이 논문에서 얻지 못했다. 독자가 거리 L을 넣으면 L/1000을 곱한다.')
for (i, j) in [(5, 6), (3, 5), (4, 6), (1, 5)]:
    lo, hi = lag(i, j)
    if lo > 0: print('  %-34s -> %-34s 1000 km당 %.2f ~ %.2f km/년' % (P[i][0][:34], P[j][0][:34], 1000 / hi, 1000 / lo))
json.dump(dict(points=[(n, a, b, s, l) for n, a, b, s, l in P], lags=out), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-5-millet-lag.json'), 'w'), ensure_ascii=False, indent=1)
