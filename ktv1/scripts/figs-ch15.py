# -*- coding: utf-8 -*-
"""15장 그림: 지도 1장 + 그래프 4장. 값은 Lee 등(2022) 본문의 표기이거나 ms/ch15-calc-v1.py 의 계산 결과다.
시연값 그림(fig-ch15-alias)은 절차를 보이기 위한 가정이며 논문 자료가 아니다.
출력: fig/fig-ch15-*-color.svg, fig/fig-ch15-*-bw.svg"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geomap as G
from geomap import basemap, city, scalebar, north, legend, Fig, FS, FS_S, FS_I, f1, PAL, area
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')

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

# ---------------------------------------------------------------- 자료
# 표 1: (번호, 한글 이름, 약어, 경도, 위도, 해안)
TG = [(1, '인천', 'IC', 126.59, 37.45, 'w'), (2, '보령', 'BR', 126.49, 36.41, 'w'), (3, '군산', 'GS', 126.56, 35.98, 'w'), (4, '목포', 'MP', 126.38, 34.78, 'w'),
      (5, '완도', 'WD', 126.76, 34.32, 's'), (6, '여수', 'YS', 127.77, 34.75, 's'), (7, '통영', 'TY', 128.43, 34.83, 's'), (8, '가덕도', 'GDD', 128.81, 35.02, 's'),
      (9, '울산', 'US', 129.39, 35.50, 'e'), (10, '포항', 'PH', 129.38, 36.05, 'e'), (11, '묵호', 'MH', 129.12, 37.55, 'e'), (12, '속초', 'SC', 128.59, 38.21, 'e'),
      (13, '울릉도', 'ULD', 130.91, 37.49, 'o')]
# 라벨 위치: (dx, dy, anchor)
LAB = {1: (-16, -10, 'end'), 2: (-16, 8, 'end'), 3: (-16, 8, 'end'), 4: (-16, 8, 'end'), 5: (-14, 36, 'end'), 6: (0, 42, 'middle'), 7: (-2, -20, 'middle'),
       8: (16, 40, 'start'), 9: (16, 12, 'start'), 10: (16, 10, 'start'), 11: (16, -4, 'start'), 12: (16, 10, 'start'), 13: (0, -26, 'middle')}

def map_tg(mode):
    bbox = (124.9, 33.7, 131.9, 38.9)
    f, pr = basemap(bbox, pad=520, mode=mode, rivers=(), lakes=False, grid=1.0, latside='right')
    P = f.P
    area(f, pr, 124.45 + 1.0, 36.6, '황해', FS_S, P['soft'], 700, 2.0, where='sea')
    area(f, pr, 130.95, 36.0, '동해', FS_S, P['soft'], 700, 2.0, where='sea')
    # 1도 x 1도 상자 (125.5~126.5E, 36.9~37.9N)
    x0, y0 = pr(125.5, 37.9)
    x1, y1 = pr(126.5, 36.9)
    f.rect(x0, y0, x1 - x0, y1 - y0, 'none', P['hot'], 3.0, 'stroke-dasharray="14 8"')
    xt, yt = pr(126.125, 37.375)
    f.marker(xt, yt, 'tri', 1.0, P['hot'])
    f.text(x0, y1 + 36, '경기만 1°×1° 상자', FS_I, 'start', P['hot'], 700)
    f.text(xt - 16, yt + 40, '선택 지점', FS_I, 'end', P['hot'], 700)
    xu, yu = pr(130.914, 37.491)
    f.marker(xu, yu, 'tri', 1.0, P['hot'])
    for n, ko, ab, lo, la, c in TG:
        x, y = pr(lo, la)
        f.marker(x, y, 'sq', 0.95, P['text'])
        dx, dy, an = LAB[n]
        f.text(x + dx, y + dy, '%d %s' % (n, ko), FS_S, an, P['text'], 700)
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('sq', '검조소 13곳(Lee 등, 2022 표 1 좌표)'), ('tri', '논문이 고른 추세 비교 지점')])
    scalebar(f, pr, 40, last + 76, 100)
    note(f, 30, last + 150, '※ 점선 상자는 논문이 적은 경위도 범위(125.5~126.5°E, 36.9~37.9°N). 인천 검조소(126.59°E)는 상자의 동쪽 바깥 약 7.9 km, 선택 지점과는 약 %.1f km 떨어져 있다(계산 15-5). 울릉도 선택 지점은 검조소와 약 0.4 km이다.' % hav(126.125, 37.375, 126.59, 37.45))
    note(f, 30, last + 260, '검조소 이름은 논문의 로마자를 한국어 지명으로 옮긴 것이다. 위성 궤도는 그리지 않았다(궤도 좌표가 본문에 없음).')
    return f

# ---------------------------------------------------------------- 그래프 공통
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

# ---------------------------------------------------------------- 그래프 1: 위성 임무 시간표
REF = [('T/P', 1993, 2002), ('J1', 2002, 2008), ('J2', 2008, 2016), ('J3', 2016, 2021)]
COMP = [('E1', 1992, 1996), ('E2', 1995, 2003), ('EN', 2002, 2010), ('ENN', 2010, 2012), ('AL', 2013, 2016), ('S3A', 2016, 2019)]
OCOMP = [('C2', 2011, 2019), ('H2', 2014, 2016), ('G2', 2000, 2008)]
OPP = [('TPN', 2002, 2005), ('J1N', 2009, 2012), ('J2N', 2016, 2017), ('J1G', 2012, 2013), ('E1G', 1994, 1995), ('H2G', 2016, 2019), ('J2G', 2017, 2017), ('ALG', 2015, 2019)]
def chart_missions(mode):
    f, P = base(mode, 1180.0)
    L, R, T, B = 230.0, 1240.0, 90.0, 840.0
    a0, a1 = 1992.0, 2022.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    f.rect(X(1993), T, X(2020) - X(1993), B - T, '#F3E7D8' if mode == 'color' else '#EDEDED', 'none', 0)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(1992, 2023, 5):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연도 (논문이 적은 연 단위 표기). 옅은 바탕은 추세를 구한 1993~2019', FS_S, 'middle', P['text'], 400, False)
    groups = [('기준(10일 주기)', REF), ('보충(35일 주기)', COMP), ('기타 보충', OCOMP), ('기회(주기 다양)', OPP)]
    cols = [P['hot'] if mode == 'color' else '#111111', P['river'] if mode == 'color' else '#555555', P['site'] if mode == 'color' else '#888888', '#6B7A82' if mode == 'color' else '#BBBBBB']
    rows = []
    for gi, (gn, lst) in enumerate(groups):
        for nm, s, e in lst:
            rows.append((gi, nm, s, e))
    rh = (B - T) / len(rows)
    for i, (gi, nm, s, e) in enumerate(rows):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 9, nm, FS_I, 'end', P['text'], 400, False)
        f.rect(X(s), y - rh * 0.34, max(X(e) - X(s), 6), rh * 0.68, cols[gi], P['frame'], 1.0)
    ly = B + 150
    xx = 40
    for gi, (gn, lst) in enumerate(groups):
        f.rect(xx, ly - 22, 30, 30, cols[gi], P['frame'], 1.4)
        f.text(xx + 42, ly, '%s %d개' % (gn, len(lst)), FS_I, 'start', P['text'], 400, False)
        xx += 42 + G.tw('%s %d개' % (gn, len(lst)), FS_I) + 30
    note(f, 40, ly + 56, 'Lee 등(2022)의 임무 목록과 연도. 4 + 6 + 3 + 8 = 21개로 논문의 "21 satellite missions"와 같다(계산 15-2). 두 위성 자료는 기준 임무와 보충 임무, 전 위성 자료는 21개 모두를 합친다. 막대 길이는 연 단위 표기를 그대로 그린 것이며 월 단위 가동 기간은 본문에 없다.')
    return f

# ---------------------------------------------------------------- 그래프 2: 장기 추세 비교
def chart_ltslr(mode):
    f, P = base(mode, 1180.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 760.0
    Y = lambda v: B - v / 8.0 * (B - T)
    axes(f, L, T, R, B, [], [0, 2, 4, 6, 8], lambda v: v, Y, '', '장기 선형 추세 (mm/yr)', str, lambda v: '%d' % v)
    items = [('TG\n인천', 3.95, 0.02, 'tg'), ('두 위성\nFES2014', 4.00, 0.04, 'f'), ('두 위성\nTPXO9', 3.28, 0.04, 't'), ('전 위성\nFES2014', 5.83, 0.06, 'f'), ('전 위성\nTPXO9', 1.52, 0.05, 't'),
             ('TG\n울릉도', 6.83, 0.08, 'tg'), ('두 위성\nFES2014', 6.65, 0.07, 'f'), ('두 위성\nTPXO9', 6.63, 0.07, 't')]
    cmap = {'tg': P['text'] if mode == 'color' else '#111111', 'f': P['hot'] if mode == 'color' else '#777777', 't': P['river'] if mode == 'color' else '#BBBBBB'}
    gap = 70
    n = len(items)
    bw = (R - L - 2 * 40 - gap) / n
    xs = []
    for i in range(n):
        x = L + 40 + i * bw + (gap if i >= 5 else 0)
        xs.append(x)
    # 전 지구 평균
    f.line(L, Y(3.7), R, Y(3.7), P['soft'], 2.4, '14 8')
    f.text(L + 14, Y(6.9), '점선: 전 지구 평균 3.7 ± 0.4', FS_I, 'start', P['soft'], 400, False)
    f.text(L + 14, Y(6.9) + 34, '(GIA 제외, 논문이 인용한 값)', FS_I, 'start', P['soft'], 400, False)
    for (lab, v, e, k), x in zip(items, xs):
        f.rect(x + 8, Y(v), bw - 16, B - Y(v), cmap[k], P['frame'], 1.4)
        f.line(x + bw / 2, Y(v - e), x + bw / 2, Y(v + e), '#FFFFFF' if mode == 'color' and k == 'tg' else P['text'], 3.0)
        f.text(x + bw / 2, Y(v) - 16, '%.2f' % v, FS_I, 'middle', P['text'], 700, False)
        a, b = lab.split('\n')
        f.text(x + bw / 2, B + 40, a, FS_I, 'middle', P['text'], 400, False)
        f.text(x + bw / 2, B + 76, b, FS_I, 'middle', P['soft'], 400, False)
    f.text((xs[0] + xs[4] + bw) / 2, T + 36, '서해: 경기만 선택 지점(126.125°E, 37.375°N)', FS_S, 'middle', P['text'], 700, False)
    f.text((xs[5] + xs[7] + bw) / 2, T + 36, '동해: 울릉도 부근', FS_S, 'middle', P['text'], 700, False)
    ly = B + 150
    note(f, 150, ly, '값은 Lee 등(2022) 본문의 R_TG, R_twosat, R_allsat이고 오차 막대는 논문이 적은 ± 값(그 정의는 본문에 없다, 계산 15-8). 서해에서는 같은 자리인데 임무와 조석 모형에 따라 1.52에서 5.83까지 흔들리고, 울릉도 부근에서는 6.63~6.83에 모인다. 보정 전 값(26.6, 34.3)은 눈금 밖이라 그리지 않았다.')
    return f

# ---------------------------------------------------------------- 그래프 3: 조석 표집 편향 시연
def chart_alias(mode):
    f, P = base(mode, 1120.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    yrs = np.arange(1993, 2020)
    X = lambda a: L + (a - 1992) / (2020 - 1992) * (R - L)
    Y = lambda v: B - (v + 400) / 800.0 * (B - T)
    axes(f, L, T, R, B, [1993, 2000, 2005, 2010, 2015, 2019], [-400, -200, 0, 200, 400], X, Y, '연도', '연평균에 남는 조석 잔차 (mm, 시연값)', str, lambda v: '%d' % v)
    f.line(L, Y(0), R, Y(0), P['frame'], 2.0)
    for frac, col, lab in ((0.10, P['hot'] if mode == 'color' else '#111111', '진폭 오차 10%'), (0.05, P['river'] if mode == 'color' else '#777777', '진폭 오차 5%')):
        res = frac * 3.0 * 1000
        b = np.linspace(-res, res, len(yrs))
        pts = [(X(a), Y(v)) for a, v in zip(yrs, b)]
        for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
            f.line(x1, y1, x2, y2, col, 4.0)
        for x, y in pts:
            f.marker(x, y, 'dot', 0.7, col)
        sl = np.polyfit(yrs, b, 1)[0]
        f.text(X(1996), Y(res * 0.55 if frac == 0.10 else res * 0.55) - (0 if frac == 0.10 else 0), '%s: 추세 %.1f mm/yr' % (lab, sl), FS_S, 'start', col, 700, False)
    f.text(X(1993) + 10, Y(-300) + 40, '초기: 저조 쪽을 더 많이 표집', FS_I, 'start', P['soft'], 400, False)
    f.text(X(2019) - 10, Y(300) - 20, '후기: 고조 쪽을 더 많이 표집', FS_I, 'end', P['soft'], 400, False)
    ly = B + 150
    note(f, 150, ly, '시연값이다. 진폭 3.0 m의 조석을 모형이 5%와 10% 작게 잡고, 연평균에 섞이는 표집 위상이 27년 동안 저조에서 고조로 선형으로 옮겨 간다는 극단 가정(계산 15-4). 논문의 실제 잔차가 아니며, 작은 진폭 오차도 표집 위상이 한쪽으로 쏠리면 mm/yr 단위의 추세를 만들 수 있음을 보이는 그림이다.')
    return f

# ---------------------------------------------------------------- 그래프 4: 속도와 창 길이
RATES = [('블룸·박 8.6~4.8 ka', 1.6, 3800, 'a'), ('블룸·박 4.8 ka 이후', 0.4, 4800, 'a'), ('조 10~6 ka', 6.0, 4000, 'a'), ('조 8~6 ka', 10.0, 2000, 'a'),
         ('IC 1960~2014', 0.9, 54, 'b'), ('IC 1985~2014', 3.7, 29, 'b'), ('서해 TG 평균 1993~2019', 3.23, 26, 'c'), ('울릉도 TG 1993~2019', 6.83, 26, 'c')]
def chart_window(mode):
    f, P = base(mode, 1180.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 760.0
    X = lambda w: L + (math.log10(w) - math.log10(10)) / (math.log10(10000) - math.log10(10)) * (R - L)
    Y = lambda v: B - v / 12.0 * (B - T)
    axes(f, L, T, R, B, [10, 100, 1000, 10000], [0, 2, 4, 6, 8, 10, 12], X, Y, '추세를 구한 창의 길이 (년, 로그 눈금)', '속도 (mm/yr = m/ka)', lambda v: '%d' % v, lambda v: '%d' % v)
    cmap = {'a': P['site'] if mode == 'color' else '#888888', 'b': P['hot'] if mode == 'color' else '#111111', 'c': P['river'] if mode == 'color' else '#444444'}
    pos = {'블룸·박 8.6~4.8 ka': (-16, 36, 'end'), '블룸·박 4.8 ka 이후': (-16, 10, 'end'), '조 10~6 ka': (-16, 10, 'end'), '조 8~6 ka': (-16, 10, 'end'),
           'IC 1960~2014': (18, 34, 'start'), 'IC 1985~2014': (18, -12, 'start'), '서해 TG 평균 1993~2019': (18, 40, 'start'), '울릉도 TG 1993~2019': (18, -12, 'start')}
    for nm, v, w, k in RATES:
        x, y = X(w), Y(v)
        f.marker(x, y, 'dot', 1.1, cmap[k])
        dx, dy, an = pos[nm]
        f.text(x + dx, y + dy, '%s  %.2g' % (nm, v), FS_I, an, P['text'], 400, False)
    ly = B + 150
    xx = 40
    for k, nm in (('a', '2장의 해안 곡선'), ('b', '인천 검조소(논문 인용)'), ('c', '이 논문 1993~2019')):
        f.rect(xx, ly - 22, 30, 30, cmap[k], P['frame'], 1.4)
        f.text(xx + 42, ly, nm, FS_I, 'start', P['text'], 400, False)
        xx += 42 + G.tw(nm, FS_I) + 30
    note(f, 40, ly + 56, '같은 mm/yr 눈금에 놓았으나 창이 4,800년에서 26년까지 달라 같은 양이 아니다(계산 15-11). 같은 인천에서 창만 54년에서 29년으로 바꾸면 0.9가 3.7이 된다. 2장의 값은 해안 침강 속도와 해수면 곡선에서 읽은 구간 속도이며 2장의 한계(14C 연대의 불확도 등)를 그대로 지닌다.')
    return f

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    figs = [('fig-ch15-map', map_tg), ('fig-ch15-missions', chart_missions), ('fig-ch15-ltslr', chart_ltslr), ('fig-ch15-alias', chart_alias), ('fig-ch15-window', chart_window)]
    for mode in ('color', 'bw'):
        for nm, fn in figs:
            r = fn(mode)
            f = r[0] if isinstance(r, tuple) else r
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
