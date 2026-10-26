# -*- coding: utf-8 -*-
"""11장 그림: 지도 2장 + 그래프 7장. 좌표는 Lyu 등(2016) 본문의 표기와 Natural Earth 도시 위치.
그래프 값은 각 논문 표·본문의 값이거나 ms/ch11-calc-v1.py 의 계산 결과다."""
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

LAOBAI = (dms(128, 3), dms(44, 6))
DUNHUA_ST = (dms(128, 12), dms(43, 22))
RIV = {'Liao', 'Xar Moron', 'Xiliao', 'Daling', 'Songhua', 'Nen', 'Di’er Songhua', 'Yalu', 'Tumen', 'Tao’er', 'Luan', 'Yongding', 'Amur', 'Ussuri'}

# ----------------------------------------------------------------- 지도 1: 동북 지역
def map_ne(mode):
    bbox = (113.0, 38.5, 133.0, 49.0)
    f, pr = basemap(bbox, pad=470, mode=mode, rivers=RIV, lakes=True, grid=5, latside='right')
    P = f.P
    area(f, pr, 131.3, 40.2, '동해', FS_S, P['soft'], 700, 2.0, where='sea')
    rlabel(f, pr, {'Songhua', 'Di’er Songhua'}, (126.0, 45.2), '송화강', -12, -14, 'end')
    rlabel(f, pr, {'Liao', 'Xiliao'}, (122.5, 43.5), '요하(서요하)', 0, 26, 'start')
    for nm, lo, la, dx, dy, an, big in (
            ('북경', 116.394, 39.902, 14, 8, 'start', True), ('적봉', 118.948, 42.272, -14, -12, 'end', False),
            ('부신', 121.658, 42.012, 14, 28, 'start', False), ('통료', 122.268, 43.622, -14, -12, 'end', False),
            ('장춘', 125.338, 43.867, -14, -12, 'end', False), ('길림', 126.548, 43.852, 12, -14, 'start', False),
            ('합이빈', 126.648, 45.752, 14, 8, 'start', True), ('연길', 129.513, 42.882, 14, 12, 'start', False),
            ('대련', 121.628, 38.925, 14, -10, 'start', False)):
        city(f, pr, lo, la, nm, dx, dy, an, big=big)
    x, y = pr(*LAOBAI)
    f.marker(x, y, 'tri', 1.1, P['hot'])
    f.text(x + 16, y - 16, '노백산', FS_S, 'start', P['hot'], 700)
    x, y = pr(*DUNHUA_ST)
    f.marker(x, y, 'star', 0.9, P['hot'])
    f.text(x - 16, y + 40, '돈화 기상대', FS_S, 'end', P['hot'], 700)
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('river', '강(Natural Earth)'), ('dot', '도시(Natural Earth 위치)'), ('tri', '노백산(Lyu 등, 2016 본문 좌표)'), ('star', '돈화 기상대(같은 논문 좌표)')])
    scalebar(f, pr, 40, last + 76, 300)
    note(f, 30, last + 150, '※ 적봉과 부신은 Shelach-Lavi 등(2019)의 두 지역 조사가 이 도시들 "주변"에서 이루어졌다는 뜻으로만 표시했다. 도시 위치는 유적 위치가 아니다.')
    note(f, 30, last + 224, '우하량, 합라해구, 대전자, 대산전, 금구자, 묘자구, 12D56, 12D16의 좌표는 이 책이 읽은 본문에 없어 그리지 않았다. 좌표 확인 필요.')
    return f, pr

# ----------------------------------------------------------------- 지도 2: 노백산과 돈화
def map_laobai(mode):
    bbox = (127.2, 42.9, 129.3, 44.5)
    f, pr = basemap(bbox, pad=360, mode=mode, rivers={'Songhua', 'Di’er Songhua', 'Tumen'}, lakes=True, grid=0.5, latside='right')
    P = f.P
    x1, y1 = pr(*LAOBAI)
    f.marker(x1, y1, 'tri', 1.2, P['hot'])
    f.text(x1 + 18, y1 - 16, '노백산 1650 m', FS_S, 'start', P['hot'], 700)
    x2, y2 = pr(*DUNHUA_ST)
    f.marker(x2, y2, 'star', 1.0, P['hot'])
    f.text(x2 + 18, y2 + 12, '돈화 기상대 524.9 m', FS_S, 'start', P['hot'], 700)
    city(f, pr, 128.22, 43.35, '돈화시(Natural Earth)', -16, 38, 'end', 'dot')
    f.line(x1, y1, x2, y2, P['hot'], 2.4, '10 8')
    d = hav(LAOBAI[0], LAOBAI[1], DUNHUA_ST[0], DUNHUA_ST[1])
    f.text((x1 + x2) / 2 + 20, (y1 + y2) / 2, '%.1f km' % d, FS_S, 'start', P['hot'], 700)
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('river', '강(Natural Earth)'), ('tri', '표본 산지(Lyu 등, 2016)'), ('star', '기상 자료(돈화 기상대)'), ('dot', '도시(Natural Earth)')])
    scalebar(f, pr, 40, last + 76, 50)
    note(f, 30, last + 150, '※ 점선은 두 지점의 직선거리(계산 11-13). 표본은 남사면 950~1050 m에서 채취했다고 본문이 적었고, 노백산 정상의 고도는 1650 m이다.')
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

def shades(P, mode):
    if mode == 'color':
        return [P['river'], P['hot'], P['site'], '#6B7A82', '#9DB7C6', '#C9A87A']
    return ['#111111', '#555555', '#888888', '#BBBBBB', '#DDDDDD', '#333333']

# ----------------------------------------------------------------- 그래프 1: Cui 하플로그룹 쌓은 막대
SITES = [('우하량(홍산, n=6)', [4, 0, 1, 1, 0]), ('합라해구(소하연, n=12)', [12, 0, 0, 0, 0]), ('대전자(하가점하층, n=5)', [3, 0, 0, 2, 0]),
         ('대산전(하가점상층, n=9)', [1, 3, 1, 2, 2]), ('금구자(북방 유목, n=12)', [0, 0, 12, 0, 0]), ('묘자구(앙소 참조, n=3)', [3, 0, 0, 0, 0])]
HGL = ['N1(xN1a,N1c)', 'N1c', 'C 또는 C3e', 'O3a', 'O3a3c']
def chart_cui(mode):
    f, P = base(mode)
    L, T, R, B = 520.0, 90.0, 1240.0, 700.0
    rowh = (B - T) / len(SITES)
    X = lambda v: L + v / 100.0 * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 101, 25):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%d' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '하플로그룹 빈도 (%)', FS_S, 'middle', P['text'], 400, False)
    cols = shades(P, mode)
    for i, (nm, c) in enumerate(SITES):
        y = T + (i + 0.5) * rowh
        f.text(L - 16, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        n = sum(c); x0 = 0.0
        for k, v in enumerate(c):
            if v == 0: continue
            w = 100.0 * v / n
            f.rect(X(x0), y - 30, X(x0 + w) - X(x0), 60, cols[k], '#FFFFFF', 2.0)
            if w >= 12:
                f.text((X(x0) + X(x0 + w)) / 2, y + 10, str(v), FS_I, 'middle', '#FFFFFF' if (mode == 'color' or k in (0, 1, 2, 5)) else '#111111', 700, False)
            x0 += w
    ly = B + 150
    xx = 40
    for k, nm in enumerate(HGL):
        f.rect(xx, ly - 22, 30, 30, cols[k], P['frame'], 1.4)
        f.text(xx + 42, ly, nm, FS_I, 'start', P['text'], 400, False)
        xx += 42 + G.tw(nm, FS_I) + 40
    note(f, 40, ly + 56, '막대 안 숫자는 사람 수(Cui 등, 2013 표 1을 이 책이 재구성, 계산 11-1). 위 네 줄이 서요하, 아래 두 줄은 참조 집단.')
    note(f, 40, ly + 92, '우하량의 C 한 명과 O3a 한 명은 표에 13.7%로 적혔으나 1/6은 16.7%이다.')
    return f

# ----------------------------------------------------------------- 그래프 2: 유전자 다양도
def chart_hdiv(mode):
    f, P = base(mode)
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    Y = lambda v: B - v / 1.0 * (B - T)
    cats = [('신석기 합\n(n=18)', 0.2157, 0.000, 0.464), ('하가점하층\n(n=5)', 0.6000, 0.000, 0.600), ('하가점상층\n(n=9)', 0.8611, 0.556, 0.889)]
    xs = [L + (R - L) * (i + 0.5) / 3 for i in range(3)]
    axes(f, L, T, R, B, [], [0, 0.2, 0.4, 0.6, 0.8, 1.0], lambda v: v, Y, '', 'Nei 유전자 다양도 H (하플로그룹 수준)', str, lambda v: '%.1f' % v)
    col = [P['river'], P['hot'], P['site']] if mode == 'color' else ['#555555', '#888888', '#222222']
    for (nm, h, lo, hi), x, c in zip(cats, xs, col):
        f.rect(x - 90, Y(h), 180, B - Y(h), c, P['frame'], 1.6)
        f.line(x, Y(lo), x, Y(hi), P['text'], 3.0)
        f.line(x - 22, Y(lo), x + 22, Y(lo), P['text'], 3.0)
        f.line(x - 22, Y(hi), x + 22, Y(hi), P['text'], 3.0)
        f.text(x, Y(hi) - 18, '%.3f' % h, FS_I, 'middle', P['text'], 700, False)
        a, b = nm.split('\n')
        f.text(x, B + 44, a, FS_I, 'middle', P['text'], 400, False)
        f.text(x, B + 80, b, FS_I, 'middle', P['soft'], 400, False)
    ly = B + 150
    note(f, 150, ly, '막대는 계산 11-4의 H. 세로선은 같은 빈도에서 다시 뽑은 부트스트랩 2.5~97.5% 구간(2만 회). 시료가 5~18명이어서 구간이 넓다.')
    note(f, 150, ly + 72, '하가점하층의 구간 0.000~0.600은 [3, 2]에서 한 종류만 뽑히는 경우가 있기 때문이다. 이 값들은 논문이 아니라 이 책의 계산이다.')
    return f

# ----------------------------------------------------------------- 그래프 3: 노백산 복원 냉기와 온기
COLD = [(1605, 1616, 7.41), (1645, 1677, 7.19), (1684, 1691, 7.19), (1911, 1924, 7.09), (1930, 1942, 7.27), (1951, 1969, 7.08)]
WARM = [(1767, 1785, 8.35), (1787, 1793, 8.01), (1795, 1807, 8.00), (1819, 1826, 8.07), (1838, 1848, 8.13), (1856, 1873, 8.13), (1991, 2008, 8.38)]
def chart_lyu(mode):
    f, P = base(mode)
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    X = lambda a: L + (a - 1600) / (2013.0 - 1600) * (R - L)
    Y = lambda v: B - (v - 6.8) / (8.6 - 6.8) * (B - T)
    axes(f, L, T, R, B, [1600, 1700, 1800, 1900, 2000], [7.0, 7.4, 7.8, 8.2, 8.6], X, Y, '연도 (AD)', '4~7월 평균 최저기온 (°C)', str, lambda v: '%.1f' % v)
    mean, sd = 7.66, 0.53
    for v, lab, dash in ((mean, '평균 7.66', None), (mean - 0.5 * sd, '냉기 기준 7.395', '14 8'), (mean + 0.5 * sd, '온기 기준 7.925', '14 8')):
        f.line(L, Y(v), R, Y(v), P['text'] if dash is None else P['soft'], 2.4, dash)
    f.text(X(1702), Y(mean) - 12, '평균 7.66', FS_I, 'start', P['text'], 700, False)
    f.text(X(1702), Y(mean - 0.5 * sd) + 34, '냉기 기준 7.395', FS_I, 'start', P['soft'], 400, False)
    f.text(X(1618), Y(mean + 0.5 * sd) - 12, '온기 기준 7.925', FS_I, 'start', P['soft'], 400, False)
    cc = P['river'] if mode == 'color' else '#555555'
    cw = P['hot'] if mode == 'color' else '#111111'
    for a, b, m in COLD:
        f.rect(X(a), Y(mean), max(X(b + 1) - X(a), 4), Y(m) - Y(mean), cc, P['frame'], 1.2)
    for a, b, m in WARM:
        f.rect(X(a), Y(m), max(X(b + 1) - X(a), 4), Y(mean) - Y(m), cw, P['frame'], 1.2)
    # 마운더 극소기 구간
    f.line(X(1645), B - 18, X(1715), B - 18, P['text'], 4.0)
    f.text(X(1645), B - 32, '마운더 극소기 1645~1715(논문 인용)', FS_I, 'start', P['text'], 400, False)
    ly = B + 150
    f.rect(150, ly - 22, 30, 30, cc, P['frame'], 1.4); f.text(192, ly, '냉기(6개)', FS_I, 'start', P['text'], 400, False)
    f.rect(420, ly - 22, 30, 30, cw, P['frame'], 1.4); f.text(462, ly, '온기(7개)', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, '막대의 높이는 Lyu 등(2016) 표 4의 기간 평균, 폭은 기간의 연수(계산 11-8). 연별 복원값은 이 책이 읽은 본문에 수치로 없어 그리지 않았다.')
    note(f, 150, ly + 130, '1605~1616의 기간 평균 7.41은 냉기 기준 7.395보다 높다(미결).')
    return f

# ----------------------------------------------------------------- 그래프 4: 변환식과 기준값을 연륜지수로 되돌리기
def chart_reg(mode):
    f, P = base(mode)
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    X = lambda v: L + (v - 0.6) / (1.3 - 0.6) * (R - L)
    Y = lambda v: B - (v - 6.5) / (8.8 - 6.5) * (B - T)
    axes(f, L, T, R, B, [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3], [6.5, 7.0, 7.5, 8.0, 8.5], X, Y, '표준 연륜지수 X', '복원 기온 Y (°C)', lambda v: '%.1f' % v, lambda v: '%.1f' % v)
    col = P['river'] if mode == 'color' else '#333333'
    f.line(X(0.6), Y(2.987 * 0.6 + 4.829), X(1.3), Y(2.987 * 1.3 + 4.829), col, 4.0)
    hot = P['hot']
    for y, lab, an in ((7.395, '냉기 기준 7.395', 'start'), (7.66, '평균 7.66', 'start'), (7.925, '온기 기준 7.925', 'start')):
        x = (y - 4.829) / 2.987
        f.line(L, Y(y), X(x), Y(y), P['soft'], 2.0, '12 8')
        f.line(X(x), Y(y), X(x), B, P['soft'], 2.0, '12 8')
        f.marker(X(x), Y(y), 'dot', 0.9, hot)
        f.text(L + 14, Y(y) - 10, '%s ↔ X = %.3f' % (lab, x), FS_I, 'start', P['text'], 700, False)
    f.text(X(1.04), Y(2.987 * 1.04 + 4.829) + 70, 'Y = 2.987 X + 4.829', FS_S, 'start', col, 700, False)
    ly = B + 150
    note(f, 150, ly, '변환식은 Lyu 등(2016). 세 기준값은 이 책이 식을 거꾸로 풀어 얻은 X(계산 11-5, 11-8). 표준 연륜지수는 대개 1을 중심으로 하며 논문 표 1의 표준편차는 0.20이다.')
    return f

# ----------------------------------------------------------------- 그래프 5: 시간표
def chart_time(mode):
    f, P = base(mode, 1120.0)
    L, R = 560.0, 1240.0
    T, B = 100.0, 780.0
    a0, a1 = 9000.0, 2000.0
    X = lambda a: L + (a0 - a) / (a0 - a1) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(9000, 1999, -1000):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연대 (오래된 쪽이 왼쪽). 막대는 논문이 적은 값', FS_S, 'middle', P['text'], 400, False)
    rows = [('건조기 9000~8100 (SL)', 9000, 8100, 'a'), ('습윤 시작 창 8100~7900 (SL)', 8100, 7900, 'b'), ('습윤 끝 창 7550~7400 (SL)', 7550, 7400, 'b'),
            ('12D56 소하서 단계 7900~7750 (SL)', 7900, 7750, 'c'), ('12D16 흥륭와 7500~7400 (SL)', 7500, 7400, 'c'),
            ('홍산 6500~5000 (Cui)', 6500, 5000, 'd'), ('소하연 5000~4200 (Cui)', 5000, 4200, 'd'), ('하가점하층 4200~3600 (Cui)', 4200, 3600, 'd'),
            ('하가점상층 3000~2700 (Cui)', 3000, 2700, 'd'), ('북방 유목 금구자 3000~2500 (Cui)', 3000, 2500, 'e')]
    cmap = {'a': '#B4B4B4', 'b': P['river'] if mode == 'color' else '#555555', 'c': P['hot'] if mode == 'color' else '#111111', 'd': P['site'] if mode == 'color' else '#888888', 'e': '#6B7A82' if mode == 'color' else '#333333'}
    rh = (B - T) / len(rows)
    for i, (lab, s, e, k) in enumerate(rows):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, lab, FS_I, 'end', P['text'], 400, False)
        f.rect(X(s), y - 17, max(X(e) - X(s), 5), 34, cmap[k], P['frame'], 1.4)
    ly = B + 150
    note(f, 40, ly, 'SL = Shelach-Lavi 등(2019)의 cal BP. Cui = Cui 등(2013)의 BP(보정 여부를 본문이 밝히지 않음). 두 눈금을 한 축에 놓은 것은 대략의 순서를 보이기 위함이며 같은 척도라는 뜻이 아니다.')
    return f

# ----------------------------------------------------------------- 그래프 6: rho 연대
def chart_rho(mode):
    f, P = base(mode)
    L, R = 600.0, 1240.0
    T, B = 100.0, 640.0
    a0, a1 = 0.0, 3000.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(0, 3001, 500):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '현재로부터의 연수 (년 전)', FS_S, 'middle', P['text'], 400, False)
    rows = [('공유 STR 다양도 1916 ± 985', 1916, 985, 'a'), ('에벤 고유 615 ± 418', 615, 418, 'a'), ('에벤키 고유 303 ± 177', 303, 177, 'a'),
            ('분기 진화 속도 1400 ± 1060 (재인용)', 1400, 1060, 'b'), ('분기 가계 속도 390 ± 290 (재인용)', 390, 290, 'b')]
    rh = (B - T) / (len(rows) + 1)
    c1 = P['hot'] if mode == 'color' else '#111111'
    c2 = P['river'] if mode == 'color' else '#666666'
    for i, (lab, m, s, k) in enumerate(rows):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, lab, FS_I, 'end', P['text'], 400, False)
        col = c1 if k == 'a' else c2
        f.line(X(m - s), y, X(m + s), y, col, 6.0)
        f.line(X(m - s), y - 14, X(m - s), y + 14, col, 4.0)
        f.line(X(m + s), y - 14, X(m + s), y + 14, col, 4.0)
        f.marker(X(m), y, 'dot', 1.0, col)
    y = T + (len(rows) + 0.5) * rh
    f.text(L - 14, y + 10, '역사가의 분기 연대(인용)', FS_I, 'end', P['text'], 400, False)
    for a, lab in ((1500, '1500'), (800, '800'), (400, '400')):
        f.marker(X(a), y, 'dia', 0.9, P['text'])
        f.text(X(a), y - 22, lab, FS_I, 'middle', P['text'], 700, False)
    ly = B + 150
    note(f, 40, ly, '점은 추정값, 가로선은 ±(논문 표기). Duggan 등은 μ = 0.0025/자리/세대, 9자리, 세대 30년이면 변이 하나가 1333년이라 썼다(계산 11-11). 분기 연대 1500은 Vasilevich, 800과 400은 Tugolukov·Janhunen의 값을 Duggan 등이 인용한 것이다.')
    return f

# ----------------------------------------------------------------- 그래프 7: AMOVA
AM = [('1집단(16)', None, 9.47, 90.53), ('4 지리집단', 4.01, 6.29, 89.71), ('6 언어집단', 6.66, 4.54, 88.80), ('퉁구스 전체', None, 8.39, 91.61), ('북·남 퉁구스', 5.67, 6.77, 87.55), ('북퉁구스', None, 7.04, 92.96)]
def chart_amova(mode):
    f, P = base(mode)
    L, T, R, B = 400.0, 90.0, 1240.0, 700.0
    vmax = 16.0
    X = lambda v: L + v / vmax * (R - L)
    rowh = (B - T) / len(AM)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 17, 4):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, str(v), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '분산의 몫 (%): 집단 사이 + 집단 안의 집단 사이', FS_S, 'middle', P['text'], 400, False)
    c1 = P['hot'] if mode == 'color' else '#111111'
    c2 = P['river'] if mode == 'color' else '#999999'
    for i, (nm, a, b, c) in enumerate(AM):
        y = T + (i + 0.5) * rowh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        x0 = 0.0
        if a is not None:
            f.rect(X(0), y - 28, X(a) - X(0), 56, c1, '#FFFFFF', 2.0)
            f.text(X(a / 2), y + 10, '%.2f' % a, FS_I, 'middle', '#FFFFFF', 700, False)
            x0 = a
        f.rect(X(x0), y - 28, X(x0 + b) - X(x0), 56, c2, '#FFFFFF', 2.0)
        f.text(X(x0 + b / 2), y + 10, '%.2f' % b, FS_I, 'middle', '#FFFFFF' if mode == 'color' else '#111111', 700, False)
    ly = B + 150
    f.rect(150, ly - 22, 30, 30, c1, P['frame'], 1.4); f.text(192, ly, '집단 사이', FS_I, 'start', P['text'], 400, False)
    f.rect(420, ly - 22, 30, 30, c2, P['frame'], 1.4); f.text(462, ly, '집단 안의 집단(또는 집단 하나일 때 집단) 사이', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, 'Duggan 등(2013) 표 2(mtDNA ΦST 기반 AMOVA)의 값. 나머지는 집단 안 변이로 합이 100이 되도록 이 책이 확인(계산 11-12).')
    return f

if __name__ == '__main__':
    maps = [('map-ne-v1', map_ne), ('map-laobai-v1', map_laobai)]
    charts = [('chart-cui-v1', chart_cui), ('chart-hdiv-v1', chart_hdiv), ('chart-lyu-v1', chart_lyu), ('chart-reg-v1', chart_reg),
              ('chart-time-v1', chart_time), ('chart-rho-v1', chart_rho), ('chart-amova-v1', chart_amova)]
    for mode in ('color', 'bw'):
        for nm, fn in maps:
            f, pr = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
        for nm, fn in charts:
            f = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
