# -*- coding: utf-8 -*-
"""14장 그림: 지도 1장 + 그래프 8장. 좌표는 Yin 등(2014), Fohlmeister 등(2017), Kim(2023), Hwang과 Park(2026) 본문의 표기.
그래프 값은 각 논문 표·본문의 값이거나 ms/ch14-calc-v1.py 의 계산 결과다. 출력: fig/fig-ch14-이름-v1-{color,bw}.svg"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geomap as G
from geomap import basemap, area, city, scalebar, north, legend, Fig, FS, FS_S, FS_I, f1, PAL, on_river, layer
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
def dms(d, m=0, s=0): return d + m / 60 + s / 3600

def hav(lo1, la1, lo2, la2):
    R = 6371.0088
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def note(f, x, y, s):
    sh = getattr(f, '_sh', 0)
    maxw = f.w - x - 2
    lines, cur = [], ''
    for ch in s:
        if G.tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    if len(lines) > 1 and len(lines[-1]) <= 2:
        last = lines.pop(); lines[-1] += last
    for i, ln in enumerate(lines):
        f.text(x, y + sh + i * 36, ln, FS_I, 'start', f.P['soft'], 400, False)
    f._sh = sh + 36 * (len(lines) - 1)

def rlabel(f, pr, names, hint, ko, dx=10, dy=-12, an='start', size=FS_S):
    pt, d = on_river(names, hint)
    x, y = pr(*pt)
    f.text(x + dx, y + dy, ko, size, an, f.P['river'], 700)

KEK = (dms(72, 35), dms(40, 29))      # Keklik-Too, Yin 아닌 Fohlmeister 등(2017): 40°29'N, 72°35'E
LIAN = (dms(109, 33), dms(29, 9))     # Lianhua 동굴, Yin 등(2014): 29°09'N, 109°33'E
SEOUL = (126.97, 37.57)               # KMA 108, Hwang과 Park(2026)
TAEGU = (129.0, dms(35, 52))          # Kim(2023) "128°60'E" = 129°00'E (계산 14-14)

# ----------------------------------------------------------------- 지도: 세 지점
def map_sites(mode):
    bbox = (68.0, 24.0, 132.0, 47.0)
    f, pr = basemap(bbox, pad=440, mode=mode, rivers={'Chang Jiang', 'Yangtze', 'Huang', 'Naryn', 'Syr  Darya', 'Han'}, lakes=True, grid=10, latside='right')
    P = f.P
    for nm, pt, dx, dy, an in (('케클릭투 동굴', KEK, 16, -18, 'start'), ('연화동굴', LIAN, -18, 40, 'end')):
        x, y = pr(*pt)
        f.marker(x, y, 'tri', 1.1, P['hot'])
        f.text(x + dx, y + dy, nm, FS_S, an, P['hot'], 700)
    x, y = pr(*SEOUL)
    f.marker(x, y, 'star', 1.0, P['hot'])
    f.text(x - 18, y - 22, '서울 기상대', FS_S, 'end', P['hot'], 700)
    x, y = pr(*TAEGU)
    f.marker(x, y, 'dot', 1.0, P['text'])
    f.text(x - 18, y + 36, '대구', FS_S, 'end', P['text'], 700)
    # 두 구간의 거리선
    for a, b, lab, dx, dy in ((KEK, LIAN, None, 0, 0), (LIAN, SEOUL, None, 0, 0)):
        xa, ya = pr(*a); xb, yb = pr(*b)
        f.line(xa, ya, xb, yb, P['hot'], 2.4, '10 8')
    xa, ya = pr(*KEK); xb, yb = pr(*LIAN)
    d1 = hav(KEK[0], KEK[1], LIAN[0], LIAN[1])
    f.text((xa + xb) / 2 - 20, (ya + yb) / 2 + 46, '%d km' % round(d1), FS_S, 'middle', P['hot'], 700)
    xa, ya = pr(*LIAN); xb, yb = pr(*SEOUL)
    d2 = hav(LIAN[0], LIAN[1], SEOUL[0], SEOUL[1])
    f.text((xa + xb) / 2 - 20, (ya + yb) / 2 - 30, '%d km' % round(d2), FS_S, 'middle', P['hot'], 700)
    rlabel(f, pr, {'Chang Jiang', 'Yangtze'}, (112.0, 30.6), '양쯔강', 0, 36, 'middle')
    rlabel(f, pr, {'Huang'}, (111.0, 35.0), '황하', 0, -16, 'middle')
    area(f, pr, 124.2, 32.0, '황해', FS_S, P['soft'], 700, 2.0, where='sea')
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('river', '강(Natural Earth)'), ('tri', '동굴(논문 본문의 좌표)'), ('star', '서울 기상대(KMA 108)'), ('dot', '대구(Kim, 2023의 좌표)')])
    scalebar(f, pr, 40, last + 76, 1000)
    note(f, 30, last + 150, '※ 점선은 두 지점의 직선(대원) 거리이며 물이나 바람이 지나는 길이 아니다(계산 14-14). 대구의 "128°60′E"는 129°00′E로 읽었다.')
    note(f, 30, last + 224, '강진, 나주, 의창 관측소, 오시 기상대, 용간호의 좌표는 이 책이 읽은 본문에 없어 그리지 않았다. 좌표 확인 필요.')
    return f, pr

# ----------------------------------------------------------------- 그래프 공통
def axes(f, L, T, R, B, xt, yt, X, Y, xlab, ylab, xfmt=str, yfmt=str, grid=True):
    P = f.P
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in yt:
        if grid: f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.line(L - 8, Y(v), L, Y(v), P['frame'], 2.0)
        f.text(L - 14, Y(v) + 10, yfmt(v), FS_I, 'end', P['soft'], 400, False)
    for v in xt:
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, xfmt(v), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, xlab, FS_S, 'middle', P['text'], 400, False)
    f.text(L - 120, T - 30, ylab, FS_S, 'start', P['text'], 400, False)

def base(mode, H=1060.0):
    W = 1300.0
    f = Fig(W, H, mode)
    f.rect(0, 0, W, H, '#FFFFFF')
    return f, f.P

def c1c2(P, mode):
    return (P['hot'], P['river']) if mode == 'color' else ('#111111', '#888888')

# ----------------------------------------------------------------- 그래프 1: Keklik1 ln(fm)과 깊이
KK = [(1.0, 1.0979), (8.0, 0.8677), (22.0, 0.8742), (43.0, 0.8618), (64.0, 0.8586), (109.0, 0.8169), (130.5, 0.7889)]
def chart_keklik(mode):
    f, P = base(mode)
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    X = lambda d: L + d / 140.0 * (R - L)
    Y = lambda v: B - (v + 0.26) / (0.14 + 0.26) * (B - T)
    axes(f, L, T, R, B, [0, 20, 40, 60, 80, 100, 120, 140], [-0.2, -0.1, 0.0, 0.1], X, Y, '꼭대기에서 잰 깊이 (mm)', 'ln(방사성탄소 잔량 fm)', str, lambda v: '%.1f' % v)
    a, b = -0.11928, -7.999933e-04
    col, col2 = c1c2(P, mode)
    f.line(X(0), Y(a), X(140), Y(a + b * 140), col2, 4.0)
    for i, (d, fm) in enumerate(KK):
        y = math.log(fm)
        if i == 0:
            f.marker(X(d), Y(y), 'dia', 1.1, '#FFFFFF', col)
        else:
            f.marker(X(d), Y(y), 'dot', 1.1, col)
    f.text(X(1) + 24, Y(math.log(1.0979)) + 8, '12c: 1 mm, fm 1.098 (핵실험 14C, 직선에서 제외)', FS_I, 'start', P['text'], 400, False)
    f.text(X(22) + 6, Y(math.log(0.8742)) - 24, '3c(22 mm)가 11c(8 mm)보다 높다', FS_I, 'start', P['text'], 400, False)
    f.text(X(70), Y(a + b * 70) + 60, '기울기 -8.0 × 10⁻⁴ /mm, r² = 0.902', FS_S, 'start', col2, 700, False)
    ly = B + 150
    note(f, 40, ly, '점은 Fohlmeister 등(2017) 표 1의 fm. 직선은 이 책이 7점 가운데 6점으로 다시 맞춘 1차 추정(계산 14-1). 논문은 IntCal13으로 대기 14C를 네 번 반복해 보정한 뒤 r² = 0.96, 성장률 155 ± 14 µm/a를 얻었고, 이 책은 그 보정을 재현하지 못했다.')
    return f

# ----------------------------------------------------------------- 그래프 2: 사건 시간창
EVT = [(1520, 1471, 1561), (1600, 1559, 1634), (1735, 1708, 1758), (1815, 1796, 1831), (1940, 1933, 1946)]
def chart_win(mode):
    f, P = base(mode, 1000.0)
    L, T, R, B = 380.0, 90.0, 1240.0, 600.0
    a0, a1 = 1400.0, 2000.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(1400, 2001, 100):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연도 (AD). 성장률 155 ± 14 µm/a 일정이라는 가정의 시간창', FS_S, 'middle', P['text'], 400, False)
    col, col2 = c1c2(P, mode)
    rh = (B - T) / len(EVT)
    for i, (c, lo, hi) in enumerate(EVT):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, '사건 중심 ~%d년' % c, FS_I, 'end', P['text'], 400, False)
        f.rect(X(lo), y - 22, X(hi) - X(lo), 44, col2, P['frame'], 1.4)
        f.marker(X(c), y, 'dot', 1.0, col)
        if X(hi) + 14 + 150 > R:
            f.text(X(lo) - 14, y + 10, '%d~%d' % (lo, hi), FS_I, 'end', P['text'], 700, False)
        else:
            f.text(X(hi) + 14, y + 10, '%d~%d' % (lo, hi), FS_I, 'start', P['text'], 700, False)
    ly = B + 150
    note(f, 40, ly, '점은 Fohlmeister 등(2017)이 적은 사건 중심, 막대는 성장률 ±14 µm/a를 깊이에 곱해 되돌린 시간창(계산 14-2). 논문의 선형 근사가 맞다는 조건이며, 방사성탄소 ±값과 표본 위치의 오차는 넣지 않았다.')
    return f

# ----------------------------------------------------------------- 그래프 3: LHD1 깊이-연대
LH = [(6, 33), (10, 80), (16, 240), (26, 361), (30, 402), (40, 494), (55, 652), (70, 766), (90, 959), (109, 1135), (118.5, 1280), (125, 1383)]
def chart_lhd1(mode):
    f, P = base(mode)
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    X = lambda d: L + d / 130.0 * (R - L)
    Y = lambda bp: T + bp / 1450.0 * (B - T)
    axes(f, L, T, R, B, [0, 20, 40, 60, 80, 100, 120], [0, 250, 500, 750, 1000, 1250], X, Y, '꼭대기에서 잰 깊이 (mm)', '230Th 나이 (BP, 1950년 = 0)', str, str)
    col, col2 = c1c2(P, mode)
    pts = [(X(d), Y(a)) for d, a in LH]
    for p, q in zip(pts[:-1], pts[1:]):
        f.line(p[0], p[1], q[0], q[1], col2, 3.6)
    for x, y in pts:
        f.marker(x, y, 'dot', 0.9, col)
    # 1300년 = BP 650의 깊이 54.8 mm, 62 mm의 나이 705
    xa, ya = X(54.8), Y(650)
    xb, yb = X(62.0), Y(705)
    f.line(L, Y(650), xa, ya, P['soft'], 2.0, '12 8')
    f.line(xa, ya, xa, T, P['soft'], 2.0, '12 8')
    f.line(xb, yb, xb, T, P['text'], 2.0, '12 8')
    f.text(xa - 14, T + 36, 'AD 1300 = 54.8 mm', FS_I, 'end', P['soft'], 700, False)
    f.text(xb + 14, T + 100, '논문: 위 62 mm = 1300~2011', FS_I, 'start', P['text'], 700, False)
    f.text(xb + 14, T + 136, '표로 보면 62 mm = BP 705 (AD 1245)', FS_I, 'start', P['text'], 700, False)
    f.text(L + 24, Y(650) - 12, 'BP 650', FS_I, 'start', P['soft'], 400, False)
    ly = B + 150
    note(f, 40, ly, '점은 Yin 등(2014) 표 1의 깊이와 보정 나이(BP). 논문의 연대 모형은 이웃한 두 연대 사이의 직선 보간이다. 맨 위 6 mm 구간을 1950년 이후까지 늘리는 외삽은 그리지 않았다(계산 14-5). 아래쪽 13개 연대는 이 그림의 범위 밖이다.')
    return f

# ----------------------------------------------------------------- 그래프 4: 건습 지수의 13사건과 LHD1의 15연대
EV = [('m', 1491, 1493), ('l', 1502, 1502), ('k', 1585, 1590), ('j', 1616, 1618), ('i', 1637, 1643), ('h', 1689, 1692), ('g', 1729, 1737), ('f', 1756, 1768), ('e', 1784, 1786), ('d', 1856, 1858), ('c', 1876, 1878), ('b', 1886, 1891), ('a', 1896, 1903)]
LHY = [1350, 1420, 1450, 1500, 1550, 1590, 1620, 1640, 1690, 1735, 1760, 1785, 1855, 1877, 1890]
def chart_drought(mode):
    f, P = base(mode, 1060.0)
    L, T, R, B = 400.0, 90.0, 1240.0, 600.0
    a0, a1 = 1340.0, 1920.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(1400, 1901, 100):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연도 (AD)', FS_S, 'middle', P['text'], 400, False)
    col, col2 = c1c2(P, mode)
    yr1, yr2 = T + 130, T + 360
    f.text(L - 14, yr1 + 10, '의창 건습 지수', FS_I, 'end', P['text'], 700, False)
    f.text(L - 14, yr1 + 46, '가뭄 13사건(1470년 이후)', FS_I, 'end', P['soft'], 400, False)
    f.text(L - 14, yr2 + 10, 'LHD1 결론의 가뭄 연대', FS_I, 'end', P['text'], 700, False)
    f.text(L - 14, yr2 + 46, '15개', FS_I, 'end', P['soft'], 400, False)
    for nm, s, e in EV:
        f.rect(X(s - 0.5), yr1 - 22, max(X(e + 0.5) - X(s - 0.5), 6), 44, col2, P['frame'], 1.2)
        f.text((X(s) + X(e)) / 2, yr1 - 36 - (40 if nm == 'l' else 0), nm, FS_I, 'middle', P['text'], 700, False)
    ev_ok = {1500, 1590, 1620, 1640, 1690, 1735, 1760, 1785, 1855, 1877, 1890}
    for i, y in enumerate(LHY):
        x = X(y)
        if y < 1470:
            kind, fill = 'dia', '#BBBBBB'
        elif y in ev_ok:
            kind, fill = 'dia', col
        else:
            kind, fill = 'dia', '#FFFFFF'
        f.marker(x, yr2, kind, 1.0, fill, col if y >= 1470 else '#888888')
        lvl = i % 3
        f.text(x, yr2 + 56 + lvl * 38, str(y), FS_I, 'middle', P['text'], 400, False)
    # 이어 주는 가는 선(±5년 안의 짝)
    pair = {1500: 1502, 1590: 1587.5, 1620: 1617, 1640: 1640, 1690: 1690.5, 1735: 1733, 1760: 1762, 1785: 1785, 1855: 1857, 1877: 1877, 1890: 1888.5}
    for y, e in pair.items():
        f.line(X(y), yr2 - 14, X(e), yr1 + 24, P['soft'], 1.4, '6 6')
    ly = B + 150
    f.marker(60, ly - 8, 'dia', 0.9, col, col); f.text(84, ly, '짝이 있는 연대(±5년, 11개)', FS_I, 'start', P['text'], 400, False)
    f.marker(560, ly - 8, 'dia', 0.9, '#FFFFFF', col); f.text(584, ly, '짝 없음(1550)', FS_I, 'start', P['text'], 400, False)
    f.marker(860, ly - 8, 'dia', 0.9, '#BBBBBB', '#888888'); f.text(884, ly, '시험 못 함(1350, 1420, 1450)', FS_I, 'start', P['text'], 400, False)
    note(f, 40, ly + 56, '막대의 글자 a~m은 Yin 등(2014)의 사건 이름. 점선은 허용 오차 ±5년에서 이 책이 맺은 짝(계산 14-6). 허용 오차는 이 책의 선택이다. 사건 (e) 1784~1786은 논문이 LHD1에 "보인다"고 쓰고 뒤에서 다른 기록에 없다고 쓴 사건이다.')
    return f

# ----------------------------------------------------------------- 그래프 5: 소빙기와 중세 온난기의 구간
DEF = [('Yin 등: 소빙기', 1550, 1850, 'a'), ('Kim(2025): 소빙기', 1350, 1850, 'a'), ('Kamae 등: 소빙기(서론)', 1400, 1700, 'a'), ('Kamae 등: 소빙기(그림 1)', 1400, 1800, 'a'),
       ('Zhou 등: 약한 몬순 지속', 1420, 1625, 'b'), ('Zhou 등: 가장 약함', 1450, 1570, 'b'), ('Fohlmeister 등: 겨울 강수 이탈', 1550, 1850, 'b'),
       ('Kamae 등: 중세 온난기', 950, 1250, 'c'), ('Zhou 등: APO 양(+)', 1000, 1300, 'c'), ('Zhou 등: APO 최고', 1000, 1230, 'c'), ('Zhou 등: 홍수 비교 구간', 1000, 1200, 'c')]
def chart_def(mode):
    f, P = base(mode, 1180.0)
    L, T, R, B = 560.0, 90.0, 1240.0, 800.0
    a0, a1 = 900.0, 1900.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(900, 1901, 100):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연도 (AD)', FS_S, 'middle', P['text'], 400, False)
    cm = {'a': P['river'] if mode == 'color' else '#555555', 'b': P['site'] if mode == 'color' else '#999999', 'c': P['hot'] if mode == 'color' else '#111111'}
    rh = (B - T) / len(DEF)
    # 소빙기 정의 네 개의 공통 구간 1550~1700
    f.rect(X(1550), T, X(1700) - X(1550), B - T, '#000000', 'none', 0, 'fill-opacity="0.08"')
    for i, (nm, s, e, k) in enumerate(DEF):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        f.rect(X(s), y - 17, X(e) - X(s), 34, cm[k], P['frame'], 1.4)
    ly = B + 150
    note(f, 40, ly, '막대는 각 논문 본문이 적은 구간. 위 네 줄은 소빙기라 부른 구간, 다음 셋은 약한 몬순·겨울 강수 이탈을 가리킨 구간, 아래 넷은 중세 쪽 구간. 회색 띠는 Yin, Kim, Kamae(두 개)의 소빙기 구간이 모두 겹치는 1550~1700년(계산 14-7).')
    return f

# ----------------------------------------------------------------- 그래프 6: Kim 사망자
KIM = [('경상도', 235566, 1074166, 45.9), ('전라도', 530535, 909801, 57.2), ('충청도', 180259, 263912, 25.3), ('경기도', 78863, 46300, 9.7), ('강원도', 0, 23150, 3.6)]
def chart_kim(mode):
    f, P = base(mode, 1000.0)
    L, T, R, B = 240.0, 90.0, 1060.0, 600.0
    vmax = 1500.0
    X = lambda v: L + v / vmax * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 1501, 500):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%d' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '추정 사망자 (천 명)', FS_S, 'middle', P['text'], 400, False)
    col, col2 = c1c2(P, mode)
    rh = (B - T) / len(KIM)
    for i, (nm, d1, d2, rate) in enumerate(KIM):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        x0 = 0.0
        if d1 > 0:
            f.rect(X(0), y - 28, X(d1 / 1000.0) - X(0), 56, col2, '#FFFFFF', 2.0)
        f.rect(X(d1 / 1000.0), y - 28, X((d1 + d2) / 1000.0) - X(d1 / 1000.0), 56, col, '#FFFFFF', 2.0)
        f.text(X((d1 + d2) / 1000.0) + 14, y + 10, '%.0f천 (%.1f%%*)' % ((d1 + d2) / 1000.0, rate), FS_I, 'start', P['text'], 700, False)
    ly = B + 150
    f.rect(150, ly - 22, 30, 30, col2, P['frame'], 1.4); f.text(192, ly, '1809~1810년 기근', FS_I, 'start', P['text'], 400, False)
    f.rect(520, ly - 22, 30, 30, col, P['frame'], 1.4); f.text(562, ly, '1814~1815년 기근', FS_I, 'start', P['text'], 400, False)
    note(f, 40, ly + 56, 'Kim(2025) 표 5의 값. 사망자는 "굶주린 사람 몫과 구호 곡물 몫의 평균"으로 나눈 모형값이며 센 사람 수가 아니다(계산 14-10). *괄호의 비율은 1798년 "인구"(가구 × 7.95)를 분모로 한 값이다. 황해도, 평안도, 함경도는 표에서 비었다.')
    return f

# ----------------------------------------------------------------- 그래프 7: Hwang 9개 사건
HW = [('라키 1783 (북반구 고위도)', -152), ('탐보라 1815 (열대)', 298), ('코시구이나 1835 (열대)', -245), ('크라카타우 1883 (열대)', 132), ('산타마리아 1902 (열대)', -109),
      ('카트마이 1912 (북반구 고위도)', 58), ('아궁 1963 (열대)', 267), ('엘치촌 1982 (열대)', -153), ('피나투보 1991 (열대)', -184)]
def chart_hwang(mode):
    f, P = base(mode, 1060.0)
    L, T, R, B = 620.0, 90.0, 1240.0, 700.0
    X = lambda v: L + (v + 300.0) / 680.0 * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(-300, 301, 100):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%d' % v, FS_I, 'middle', P['soft'], 400, False)
    f.line(X(0), T, X(0), B, P['frame'], 2.4)
    f.text((L + R) / 2, B + 92, '분출 후 1~3년 서울 여름(6~8월) 강수 이상의 평균 (mm)', FS_S, 'middle', P['text'], 400, False)
    col, col2 = c1c2(P, mode)
    rh = (B - T) / len(HW)
    for i, (nm, v) in enumerate(HW):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        c = col2 if v > 0 else col
        x0, x1 = (X(0), X(v)) if v > 0 else (X(v), X(0))
        f.rect(x0, y - 22, x1 - x0, 44, c, '#FFFFFF', 2.0)
        if v > 0:
            f.text(X(v) + 12, y + 10, '+%d' % v, FS_I, 'start', P['text'], 700, False)
        else:
            f.text(X(0) + 12, y + 10, '%d' % v, FS_I, 'start', P['text'], 700, False)
    ly = B + 150
    f.rect(150, ly - 22, 30, 30, col2, P['frame'], 1.4); f.text(192, ly, '평소보다 습함', FS_I, 'start', P['text'], 400, False)
    f.rect(470, ly - 22, 30, 30, col, P['frame'], 1.4); f.text(512, ly, '평소보다 건조', FS_I, 'start', P['text'], 400, False)
    note(f, 40, ly + 56, 'Hwang과 Park(2026, 사전 출판) 표 1의 값. 기준은 31년 이동평균. 합성 평균은 유의하지 않았고(+3년 열대 -65.0 mm, p = 0.55) 열대 7개는 습함 3, 건조 4로 갈렸다(계산 14-13). 같은 논문의 검정력 서술은 계산 14-13에서 점검했다.')
    return f

# ----------------------------------------------------------------- 그래프 8: Kamae 표 3의 값 ÷ 신뢰구간 반폭
KM = [('강수: 가을 − 봄 증가(15~35°N)', 0.09, 0.03, 0.06, 0.04), ('상층 두께 25~60°N', 6.39, 1.82, 6.52, 1.60), ('상층 두께 적도~25°N', 3.18, 1.02, 3.81, 1.66),
      ('두 지역의 차', 3.22, 1.14, 2.70, 2.16), ('동아시아-서태평양 몬순 지수', 0.05, 0.28, 0.24, 0.69)]
def chart_kamae(mode):
    f, P = base(mode, 1060.0)
    L, T, R, B = 560.0, 90.0, 1240.0, 700.0
    X = lambda v: L + v / 4.5 * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 5):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%d' % v, FS_I, 'middle', P['soft'], 400, False)
    f.line(X(1), T, X(1), B, P['text'], 2.6, '14 8')
    f.text(X(1) + 10, T + 30, '1보다 크면 구간이 0을 뺀다', FS_I, 'start', P['text'], 700, False)
    f.text((L + R) / 2, B + 92, '값 ÷ (± 구간의 반폭)', FS_S, 'middle', P['text'], 400, False)
    col, col2 = c1c2(P, mode)
    rh = (B - T) / len(KM)
    for i, (nm, v1, e1, v2, e2) in enumerate(KM):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        f.marker(X(v1 / e1), y - 18, 'dot', 1.1, col2)
        f.marker(X(v2 / e2), y + 22, 'dia', 1.0, col)
    ly = B + 150
    f.marker(70, ly - 8, 'dot', 1.0, col2); f.text(94, ly, '다중 모형(PMIP3, 10개)', FS_I, 'start', P['text'], 400, False)
    f.marker(560, ly - 8, 'dia', 0.9, col); f.text(584, ly, '궤도만 바꾼 실험(5회 × 50년)', FS_I, 'start', P['text'], 400, False)
    note(f, 40, ly + 56, 'Kamae 등(2017) 표 3의 값(MWP − LIA, 가을 − 봄)을 이 책이 ±로 나눈 것(계산 14-8). 서로 다른 단위의 다섯 줄을 한 축에 놓기 위한 환산이며 논문에는 없는 양이다. "±"를 95% 신뢰구간의 반폭으로 읽었다(표 머리글의 서술).')
    return f

if __name__ == '__main__':
    maps = [('fig-ch14-map-v1', map_sites)]
    charts = [('fig-ch14-keklik-v1', chart_keklik), ('fig-ch14-win-v1', chart_win), ('fig-ch14-lhd1-v1', chart_lhd1), ('fig-ch14-drought-v1', chart_drought),
              ('fig-ch14-def-v1', chart_def), ('fig-ch14-kim-v1', chart_kim), ('fig-ch14-hwang-v1', chart_hwang), ('fig-ch14-kamae-v1', chart_kamae)]
    for mode in ('color', 'bw'):
        for nm, fn in maps:
            f, pr = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
        for nm, fn in charts:
            f = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
