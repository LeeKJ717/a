# -*- coding: utf-8 -*-
"""9장 그림: 지도 2장 + 그래프 2장. 좌표는 각 논문 본문의 표기. 시연 아닌 그림은 논문 표의 값."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geomap as G
from geomap import basemap, area, city, scalebar, north, legend, Fig, FS, FS_S, FS_I, f1, PAL
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
def dms(d, m=0, s=0): return d + m / 60 + s / 3600

# ----------------------------------------------------------------- 지도 1: 하류와 코어 두 곳
def map_region(mode):
    bbox = (111.0, 33.0, 125.0, 40.0)
    f, pr = basemap(bbox, pad=300, mode=mode, rivers={'Huang'}, grid=5)
    P = f.P
    area(f, pr, 120.4, 38.9, '발해만', FS_S, P['soft'], where='sea')
    area(f, pr, 122.2, 34.2, '황해', FS, P['soft'], where='sea')
    # 삼각주 상자(Liu 2020 범위, Yang 2025가 인용)
    x0, y0 = pr(dms(117, 31), dms(38, 16)); x1, y1 = pr(dms(119, 18), dms(36, 55))
    f.rect(x0, y0, x1 - x0, y1 - y0, 'none', P['hot'], 3.0, 'stroke-dasharray="14 8"')
    f.text(x0 - 14, y1 + 6, '1', FS_S, 'end', P['hot'], 700)
    # 코어
    for n, lo, la in ((2, 119.99, 38.28), (3, 123.22, 35.22)):
        x, y = pr(lo, la)
        f.marker(x, y, 'sq', 1.0, P['text'])
        f.text(x + 14, y - 10, str(n), FS_S, 'start', P['text'], 700)
    for nm, lo, la, dx, dy, an in (('정주', 113.66, 34.76, -14, 28, 'end'), ('개봉', 114.35, 34.79, 14, 30, 'start'),
                                    ('제남', 116.99, 36.68, -14, 28, 'end'), ('천진', 117.20, 39.08, 14, 8, 'start'),
                                    ('서주', 117.18, 34.28, 14, 28, 'start')):
        city(f, pr, lo, la, nm, dx, dy, an, 'dot')
    area(f, pr, 114.2, 36.2, '화북평원', FS_S, P['soft'], where='land')
    north(f, 80, 130, 100)
    y0b = pr.h + 56
    last = legend(f, 30, y0b, [('river', '현재의 황하 하도(Natural Earth)'), ('sq', '바다 코어(2, 3)'), ('dot', '도시')])
    f.rect(36, last + 30, 40, 22, 'none', P['hot'], 3.0, 'stroke-dasharray="10 6"')
    f.text(88, last + 50, '현대 삼각주 범위(1)', FS_S, 'start', P['text'], 400, False)
    scalebar(f, pr, 40, last + 130, 300)
    f.text(30, last + 200, '※ 번호는 9.1절 표의 지점 번호.', FS_I, 'start', P['soft'], 400, False)
    f.text(30, last + 236, '역사 시기의 옛 하도는 좌표 근거가 없어 그리지 않았다.', FS_I, 'start', P['soft'], 400, False)
    return f, pr

# ----------------------------------------------------------------- 지도 2: 현대 삼각주 확대
def map_delta(mode):
    bbox = (116.4, 36.3, 120.7, 39.2)
    f, pr = basemap(bbox, pad=360, mode=mode, rivers={'Huang'}, grid=1)
    P = f.P
    area(f, pr, 119.55, 38.75, '발해만', FS_S, P['soft'], where='sea')
    area(f, pr, 119.45, 37.35, '래주만', FS_S, P['soft'], where='sea')
    # 상자 둘
    x0, y0 = pr(dms(117, 31), dms(38, 16)); x1, y1 = pr(dms(119, 18), dms(36, 55))
    f.rect(x0, y0, x1 - x0, y1 - y0, 'none', P['hot'], 3.0, 'stroke-dasharray="14 8"')
    a0, b0 = pr(dms(117, 45), dms(38, 31, 32.10)); a1, b1 = pr(dms(119, 22, 8.45), dms(37, 20))
    f.rect(a0, b0, a1 - a0, b1 - b0, 'none', P['text'], 3.0)
    x, y = pr(119.99, 38.28)
    f.marker(x, y, 'sq', 1.0, P['text']); f.text(x - 14, y - 12, '2', FS_S, 'end', P['text'], 700)
    for nm, lo, la, dx, dy, an in (('제남', 116.99, 36.68, 14, 10, 'start'), ('창주', 116.87, 38.32, 14, 10, 'start'), ('유방', 119.16, 36.70, 14, 28, 'start')):
        city(f, pr, lo, la, nm, dx, dy, an, 'dot')
    north(f, 100, 140, 100)
    y0b = pr.h + 56
    last = legend(f, 30, y0b, [('river', '현재의 황하 하도'), ('sq', '바다 코어(2)'), ('dot', '도시')])
    f.rect(36, last + 30, 40, 22, 'none', P['hot'], 3.0, 'stroke-dasharray="10 6"')
    f.text(88, last + 50, '현대 삼각주 범위(Liu 등, 2020)', FS_S, 'start', P['text'], 400, False)
    f.rect(36, last + 76, 40, 22, 'none', P['text'], 3.0)
    f.text(88, last + 96, '이 연구의 해안선 범위(Yang 등, 2025)', FS_S, 'start', P['text'], 400, False)
    scalebar(f, pr, 40, last + 176, 100)
    f.text(30, last + 236, '※ 상자는 각 논문 본문의 위도·경도 표기를 십진도로 바꾸어 그렸다.', FS_I, 'start', P['soft'], 400, False)
    return f, pr

# ----------------------------------------------------------------- 그래프 1: 해안선 길이 1984~2024
Y = [1984, 1986, 1988, 1990, 1994, 1995, 1997, 2000, 2003, 2005, 2008, 2010, 2013, 2015, 2020, 2022, 2024]
AC = [80.19, 125.88, 195.84, 200.56, 233.37, 239.84, 253.06, 320.06, 328.37, 334.51, 324.95, 322.47, 332.49, 361.95, 356.52, 358.08, 364.23]
NC = [318.77, 284.8, 161.39, 170.88, 155.23, 154.81, 166.43, 120.60, 76.13, 60.96, 54.95, 67.93, 32.80, 33.58, 55.38, 60.44, 55.49]
TOT = [398.96, 410.70, 357.22, 371.44, 388.60, 394.65, 419.49, 440.65, 404.50, 395.47, 379.90, 390.40, 365.29, 395.53, 411.89, 418.51, 419.72]

def chart_coast(mode):
    W, H = 1300.0, 960.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    L, T, R, B = 150.0, 90.0, 1240.0, 660.0
    ymax = 500.0
    X = lambda yr: L + (yr - 1984) / 40.0 * (R - L)
    Yp = lambda v: B - v / ymax * (B - T)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 501, 100):
        f.line(L, Yp(v), R, Yp(v), P['grid'], 1.0, '8 8')
        f.text(L - 12, Yp(v) + 10, str(v), FS_I, 'end', P['soft'], 400, False)
    for yr in range(1984, 2025, 8):
        f.line(X(yr), B, X(yr), B + 10, P['frame'], 2.0)
        f.text(X(yr), B + 44, str(yr), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연도', FS_S, 'middle', P['text'], 400, False)
    f.text(12, T - 34, '해안선 길이(km)', FS_S, 'start', P['text'], 400, False)
    # 시기 구분
    for yr in (2000, 2015):
        f.line(X(yr), T, X(yr), B, P['frame'], 2.0, '14 8')
    for a, b, s in ((1984, 2000, '급속 전환기'), (2000, 2015, '완만 전환기'), (2015, 2024, '안정기')):
        f.text((X(a) + X(b)) / 2, T + 36, s, FS_S, 'middle', P['soft'], 700, False)
    # 다항 적합(순번 x) 값
    xi = np.arange(17.0)
    def fit(v):
        c = np.polyfit(xi, np.array(v), 2); return np.polyval(c, xi)
    sty = {
        'AC': dict(col=P['hot'] if mode == 'color' else '#111111', dash=None, sw=4.2, kind='sq'),
        'NC': dict(col=P['river'] if mode == 'color' else '#111111', dash='20 10' if mode == 'bw' else None, sw=4.2, kind='dot'),
        'TOT': dict(col='#6B7A82' if mode == 'color' else '#777777', dash='6 8', sw=3.0, kind='tri'),
    }
    for key, v in (('TOT', TOT), ('AC', AC), ('NC', NC)):
        s = sty[key]
        fv = fit(v) if key != 'TOT' else None
        if fv is not None:
            pts = ' L'.join('%s,%s' % (f1(X(yr)), f1(Yp(val))) for yr, val in zip(Y, fv))
            f.raw('<path d="M%s" fill="none" stroke="%s" stroke-width="2" stroke-opacity="0.55" stroke-dasharray="3 7"/>' % (pts, s['col']))
        pts = ' L'.join('%s,%s' % (f1(X(yr)), f1(Yp(val))) for yr, val in zip(Y, v))
        d = ' stroke-dasharray="%s"' % s['dash'] if s['dash'] else ''
        f.raw('<path d="M%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"%s/>' % (pts, s['col'], s['sw'], d))
        for yr, val in zip(Y, v):
            f.marker(X(yr), Yp(val), s['kind'], 0.55, s['col'] if key != 'NC' or mode == 'color' else '#FFFFFF', '#FFFFFF' if mode == 'color' else '#111111')
    # 1988 교차
    f.line(X(1988), Yp(0), X(1988), Yp(195.84), P['text'], 1.6, '4 6')
    f.text(X(1988) + 12, Yp(34), '1988년: 인공 > 자연', FS_I, 'start', P['text'], 400, False)
    # 범례
    ly = B + 150
    items = [('TOT', '전체 길이'), ('AC', '인공해안선'), ('NC', '자연해안선')]
    cx = 150.0
    for key, lab in items:
        s = sty[key]
        d = ' stroke-dasharray="%s"' % s['dash'] if s['dash'] else ''
        f.raw('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>' % (f1(cx), f1(ly - 9), f1(cx + 60), f1(ly - 9), s['col'], s['sw'], d))
        f.marker(cx + 30, ly - 9, s['kind'], 0.55, s['col'] if key != 'NC' or mode == 'color' else '#FFFFFF', '#FFFFFF' if mode == 'color' else '#111111')
        f.text(cx + 76, ly, lab, FS_S, 'start', P['text'], 400, False)
        cx += 76 + G.tw(lab, FS_S) + 50
    f.raw('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2" stroke-opacity="0.55" stroke-dasharray="3 7"/>' % (f1(cx), f1(ly - 9), f1(cx + 60), f1(ly - 9), '#444444'))
    f.text(cx + 76, ly, '다항 적합', FS_S, 'start', P['text'], 400, False)
    f.text(150, ly + 56, '※ 점선 곡선은 2차 다항 적합(순번 x, 9.2절).', FS_I, 'start', P['soft'], 400, False)
    f.text(150, ly + 92, '자료: Yang 등(2025) 표 2(2023년 없음).', FS_I, 'start', P['soft'], 400, False)
    return f

# ----------------------------------------------------------------- 그래프 2: Houzhuang 단면의 층서와 나이-깊이
def chart_hz(mode):
    W, H = 1300.0, 960.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    top, sc = 190.0, 2.8           # 깊이 0 cm의 y, cm당 단위
    Yd = lambda d: top + d * sc
    cx0, cx1 = 170.0, 300.0
    bounds = [(0, 30, '6', '경작토'), (30, 70, '5', ''), (70, 95, '4', '홍수'), (95, 140, '3', '호수'), (140, 165, '2', '홍수'), (165, 220, '1', '호수')]
    if mode == 'color':
        fills = {'6': '#CFCBB8', '5': '#E8D9A8', '4': '#E3C27A', '3': '#8C7B64', '2': '#E3C27A', '1': '#7A6A55'}
    else:
        fills = {'6': '#F0F0F0', '5': '#DADADA', '4': '#BEBEBE', '3': '#7C7C7C', '2': '#BEBEBE', '1': '#5E5E5E'}
    for a, b, n, lab in bounds:
        f.rect(cx0, Yd(a), cx1 - cx0, (b - a) * sc, fills[n], P['frame'], 1.6)
        col = '#FFFFFF' if n in ('3', '1') else P['text']
        txt = n + (' (' + lab + ')' if lab else '')
        f.text((cx0 + cx1) / 2, Yd((a + b) / 2) + 10, txt, FS_I, 'middle', col, 700, False)
    f.text(cx0 - 12, Yd(0) + 10, '0', FS_I, 'end', P['soft'], 400, False)
    for d in (30, 70, 95, 140, 165, 220):
        f.text(cx0 - 12, Yd(d) + 10, str(d), FS_I, 'end', P['soft'], 400, False)
    f.text(cx0 - 12, top - 40, '깊이(cm)', FS_I, 'end', P['text'], 400, False)
    f.text((cx0 + cx1) / 2, top - 40, '층(단위)', FS_I, 'middle', P['text'], 400, False)
    # 시료 표시
    samples = [(55, '14C 55 cm'), (115, 'OSL 115 cm'), (180, 'OSL 180 cm')]
    for d, lab in samples:
        f.marker(cx1 + 22, Yd(d), 'dia', 0.9, P['hot'] if mode == 'color' else '#111111')
        f.text(cx1 + 40, Yd(d) + 10, lab, FS_I, 'start', P['text'], 400, False)
    # 오른쪽: 나이-깊이
    rx0, rx1 = 560.0, 1270.0
    y0, y1 = -700.0, 1600.0
    Xa = lambda yr: rx0 + (yr - y0) / (y1 - y0) * (rx1 - rx0)
    f.rect(rx0, Yd(0), rx1 - rx0, 220 * sc, 'none', P['frame'], 2.4)
    for d in (30, 70, 95, 140, 165):
        f.line(rx0, Yd(d), rx1, Yd(d), P['grid'], 1.2, '6 8')
    for yr in (-500, 0, 500, 1000, 1500):
        f.line(Xa(yr), Yd(220), Xa(yr), Yd(220) + 10, P['frame'], 2.0)
        f.text(Xa(yr), Yd(220) + 44, str(yr), FS_I, 'middle', P['soft'], 400, False)
        f.line(Xa(yr), Yd(0), Xa(yr), Yd(220), P['grid'], 1.0, '8 8')
    f.text((rx0 + rx1) / 2, Yd(220) + 92, '연도(음수는 기원전, 천문 연도)', FS_S, 'middle', P['text'], 400, False)
    pts = [(1475.0, 55, 1455.0, 1495.0), (224.0, 115, 4.0, 444.0), (-186.0, 180, -596.0, 224.0)]
    line = ' L'.join('%s,%s' % (f1(Xa(a)), f1(Yd(d))) for a, d, lo, hi in pts)
    f.raw('<path d="M%s" fill="none" stroke="%s" stroke-width="3.0" stroke-dasharray="14 8"/>' % (line, '#555555'))
    for a, d, lo, hi in pts:
        f.line(Xa(lo), Yd(d), Xa(hi), Yd(d), P['hot'] if mode == 'color' else '#111111', 5.0)
        f.marker(Xa(a), Yd(d), 'dia', 0.9, P['hot'] if mode == 'color' else '#111111')
    # 사건: 보간으로 깊이를 구한 값
    def depth_at(yr):
        if yr >= 224.0:
            return 55 + (1475.0 - yr) / (1475.0 - 224.0) * 60
        return 115 + (224.0 - yr) / (224.0 + 186.0) * 65
    ev = [(-131, '132 BCE', 0), (69, '69', 1), (944, '944', 0), (1128, '1128', 1), (1448, '1448', 0)]
    f.rect(Xa(-131), Yd(0), Xa(-108) - Xa(-131), 220 * sc, P['hot'] if mode == 'color' else '#999999', 'none', 0, 'fill-opacity="0.25"')
    for yr, lab, row in ev:
        x = Xa(yr); dd = depth_at(yr)
        f.line(x, Yd(0), x, Yd(dd), P['text'], 1.6, '4 6')
        f.circle(x, Yd(dd), 7, '#FFFFFF', P['text'], 2.4)
        f.text(x, Yd(0) - 14 - row * 40, lab, FS_I, 'middle', P['text'], 700, False)
    f.text(130, 40, '선: 세 시료의 선형 보간. 가로선: 시료 나이의 1σ(OSL), 2σ(14C).', FS_I, 'start', P['soft'], 400, False)
    f.text(130, 78, '세로 점선: 논문이 층에 대응시킨 사건 연도(역사 기록).', FS_I, 'start', P['soft'], 400, False)
    return f

if __name__ == '__main__':
    jobs = [('map-yrd-region-v1', map_region), ('map-yrd-delta-v1', map_delta)]
    for mode in ('color', 'bw'):
        for nm, fn in jobs:
            f, pr = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, 'warn', w)
        f = chart_coast(mode)
        print('chart-yrd-coast', mode, 'warn', f.save(os.path.join(OUT, 'chart-yrd-coast-v1-%s.svg' % mode)))
        f = chart_hz(mode)
        print('chart-hz-section', mode, 'warn', f.save(os.path.join(OUT, 'chart-hz-section-v1-%s.svg' % mode)))
