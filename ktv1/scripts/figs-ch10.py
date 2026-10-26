# -*- coding: utf-8 -*-
"""10장 그림: 지도 4장 + 그래프 6장. 좌표는 He 등(2015) 표 1과 Wang 등(2011) 본문의 표기.
그래프 값은 각 논문 표·본문의 값이거나 ms/ch10-calc-v1.py 의 계산 결과다."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geomap as G
from geomap import basemap, area, city, scalebar, north, legend, Fig, FS, FS_S, FS_I, f1, PAL, on_river, layer, _line_d
from shapely.geometry import box
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
def dms(d, m=0, s=0): return d + m / 60 + s / 3600


def note(f, x, y, s):
    """주석 한 줄. 폭을 넘으면 줄을 나누고, 뒤따르는 주석을 그만큼 아래로 민다."""
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

# ----------------------------------------------------------------- He 2015 표 1 (이름은 한국 한자음)
S = [(1, '타타하', dms(91, 5, 9.2), dms(34, 17, 43.3)), (2, '금사강', dms(99, 22, 14), dms(28, 11, 9)), (3, '석고', dms(99, 58, 52), dms(26, 52, 14)),
     (4, '반지화 1', dms(101, 29, 25.8), dms(26, 35, 16.2)), (5, '아롱강', dms(101, 49, 16.2), dms(26, 46, 2.4)), (6, '반지화 2', dms(101, 49, 13.8), dms(26, 35, 28.8)),
     (7, '의빈 1', dms(103, 45, 18), dms(29, 37, 28)), (8, '대도하', dms(103, 45, 42), dms(29, 33, 16)), (9, '민강 1', dms(103, 45, 18), dms(29, 37, 28)),
     (10, '의빈 2', dms(104, 41, 26.4), dms(28, 47, 0)), (11, '중경 1', dms(106, 29, 22), dms(29, 23, 35)), (12, '가릉강', dms(106, 29, 1.8), dms(29, 33, 22.8)),
     (13, '중경 2', dms(106, 37, 0.6), dms(29, 37, 11.4)), (14, '부릉 1', dms(107, 21, 9), dms(29, 44, 1)), (15, '오강', dms(107, 23, 33.8), dms(29, 36, 20.8)),
     (16, '부릉 2', dms(107, 24, 37.2), dms(29, 44, 8.4)), (17, '파동', dms(110, 20, 46), dms(30, 3, 3)), (18, '의창', dms(111, 18, 43.7), dms(30, 39, 49.5)),
     (19, '악양 1', dms(112, 55, 7.6), dms(29, 32, 49.5)), (20, '원강', dms(111, 41, 11.2), dms(29, 1, 25.9)), (21, '상강', dms(112, 56, 55.2), dms(28, 8, 51.6)),
     (22, '악양 2', dms(113, 11, 27.3), dms(29, 29, 28.5)), (23, '무한 1', dms(114, 14, 32), dms(30, 28, 31)), (24, '한수', dms(113, 25, 57.8), dms(30, 23, 33.5)),
     (25, '무한 2', dms(114, 25, 32.9), dms(30, 40, 19.1)), (26, '구강', dms(115, 54, 30), dms(29, 43, 8)), (27, '감강', dms(115, 51, 21.5), dms(28, 38, 57.9)),
     (28, '호구', dms(116, 18, 26.8), dms(29, 46, 3.1)), (29, '남경', dms(118, 44, 40.1), dms(32, 6, 47.4)), (30, '장흥도', dms(121, 58, 45), dms(31, 11, 16))]
TRIB = {5, 8, 9, 12, 15, 20, 21, 24, 27}
SD = {n: (nm, lo, la) for n, nm, lo, la in S}
RIV = {'Yangtze', 'Chang Jiang', 'Jinsha', 'Tuotuo', 'Yalong', 'Dadu', 'Jialing', 'Wu', 'Han', 'Yuan', 'Xiang', 'Gan'}

def min_river(f, pr):
    """사천의 민강만 그린다(복건의 같은 이름 강은 제외)."""
    P = f.P
    cb = box(102.0, 28.5, 105.6, 33.6)
    for g, pp in layer('ne_10m_rivers_lake_centerlines'):
        if pp.get('name') == 'Min' and g.intersects(cb):
            c = g.intersection(cb).simplify(0.5 / pr.k)
            d = _line_d(c, pr)
            if d:
                f.raw('<path d="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>' % (d, P['river']))

def rlabel(f, pr, names, hint, ko, dx=10, dy=-12, an='start', size=FS_S):
    pt, d = on_river(names, hint)
    x, y = pr(*pt)
    f.text(x + dx, y + dy, ko, size, an, f.P['river'], 700)

def site(f, pr, n, dx, dy, an='start', num=None, tag=None):
    nm, lo, la = SD[n]
    x, y = pr(lo, la)
    P = f.P
    kind = 'sq' if n in TRIB else 'dot'
    f.marker(x, y, kind, 1.0, P['hot'] if n in TRIB else P['text'])
    f.text(x + dx, y + dy, num or str(n), FS_S, an, P['hot'] if n in TRIB else P['text'], 700)

def sites_legend(f, pr, extra=()):
    y0 = pr.h + 56
    items = [('river', '강(Natural Earth)'), ('dot', '본류 시료'), ('sq', '지류 시료')] + list(extra)
    return legend(f, 30, y0, items)

# ----------------------------------------------------------------- 지도 1: 유역 전체
def map_basin(mode):
    bbox = (90.0, 24.5, 123.5, 36.0)
    f, pr = basemap(bbox, pad=360, mode=mode, rivers=RIV, lakes=True, grid=5, latside='right')
    min_river(f, pr)
    P = f.P
    area(f, pr, 97.0, 31.0, '티베트고원', FS_S, P['soft'], 700, 2.0, where='land')
    area(f, pr, 106.3, 31.9, '사천분지', FS_S, P['soft'], 700, 2.0, where='land')
    rlabel(f, pr, {'Yangtze', 'Chang Jiang'}, (110.0, 30.8), '장강', 0, -16, 'middle')
    rlabel(f, pr, {'Jinsha'}, (100.0, 29.5), '금사강', -14, 0, 'end')
    rlabel(f, pr, {'Han'}, (110.8, 32.6), '한수', 12, -12)
    rlabel(f, pr, {'Gan'}, (115.4, 26.9), '감강', 14, 8)
    rlabel(f, pr, {'Xiang'}, (112.2, 26.2), '상강', -14, 8, 'end')
    for n, dx, dy, an in ((1, 14, -10, 'start'), (2, -14, -10, 'end'), (3, -14, 10, 'end')):
        site(f, pr, n, dx, dy, an)
    # 묶음 표시
    for n, nm, dx, dy, an in ((4, '4-6', -16, 36, 'end'), (7, '7-10', -16, 10, 'end'), (11, '11-16', -2, -34, 'middle'), (17, '17', -4, 36, 'end'), (18, '18', -4, 36, 'middle')):
        site(f, pr, n, dx, dy, an, num=nm)
    for n in (5, 6, 8, 9, 10, 12, 13, 14, 15, 16):
        nm_, lo, la = SD[n]; x, y = pr(lo, la)
        f.marker(x, y, 'sq' if n in TRIB else 'dot', 0.8, P['hot'] if n in TRIB else P['text'])
    for n, dx, dy, an in ((19, 12, 40, 'start'), (23, -14, -16, 'end'), (26, 14, -10, 'start'), (29, 14, -10, 'start'), (30, 14, 6, 'start')):
        site(f, pr, n, dx, dy, an, num={19: '19-27', 23: '23-25', 26: '26-28'}.get(n))
    for n in (20, 21, 22, 24, 25, 27, 28):
        nm_, lo, la = SD[n]; x, y = pr(lo, la)
        f.marker(x, y, 'sq' if n in TRIB else 'dot', 0.8, P['hot'] if n in TRIB else P['text'])
    city(f, pr, 104.07, 30.67, '성도', 14, -10, 'start', 'dot')
    north(f, 60, pr.h - 140, 100)
    last = sites_legend(f, pr)
    scalebar(f, pr, 40, last + 76, 500)
    note(f, 30, last + 150, '※ 번호는 10.4절 표 1의 시료 번호(He 등, 2015). 4-6, 7-10, 11-16, 19-27은 이 축척에서 겹쳐 묶었다.')
    note(f, 30, last + 188, '시료의 본류·지류 구분은 이름과 좌표로 이 책이 정했다.')
    return f, pr

# ----------------------------------------------------------------- 지도 2: 상류 확대 (4-16)
def map_upper(mode):
    bbox = (100.8, 25.9, 108.2, 30.4)
    f, pr = basemap(bbox, pad=360, mode=mode, rivers=RIV, lakes=False, grid=1, latside='right')
    min_river(f, pr)
    P = f.P
    rlabel(f, pr, {'Jinsha'}, (101.9, 28.0), '금사강', 16, 0, 'start')
    rlabel(f, pr, {'Yangtze', 'Chang Jiang'}, (105.3, 28.9), '장강', 0, 40, 'middle')
    rlabel(f, pr, {'Jialing'}, (106.2, 30.1), '가릉강', 14, 0)
    rlabel(f, pr, {'Wu'}, (107.5, 28.4), '오강', -14, 8, 'end')
    rlabel(f, pr, {'Dadu'}, (102.8, 29.5), '대도하', -12, -6, 'end')
    rlabel(f, pr, {'Yalong'}, (101.3, 27.6), '아롱강', -12, 0, 'end')
    offs = {4: (-14, 10, 'end'), 5: (14, -8, 'start'), 6: (14, 28, 'start'), 7: (-14, -8, 'end'), 8: (14, 26, 'start'), 9: (14, -12, 'start'), 10: (14, 8, 'start'),
            11: (-14, 26, 'end'), 12: (-14, -8, 'end'), 13: (14, -10, 'start'), 14: (-14, -12, 'end'), 15: (14, 28, 'start'), 16: (14, -12, 'start')}
    for n, (dx, dy, an) in offs.items():
        site(f, pr, n, dx, dy, an, num='7·9' if n == 7 else ('' if n == 9 else None))
    for nm, lo, la, dx, dy, an in (('의빈', 104.64, 28.77, 14, 36, 'start'), ('중경', 106.55, 29.56, -40, -20, 'end')):
        pass
    north(f, 70, pr.h - 130, 100)
    last = sites_legend(f, pr)
    scalebar(f, pr, 40, last + 76, 100)
    note(f, 30, last + 150, '※ 번호는 표 1의 시료 번호. 7(의빈 1)과 9(민강 1)은 표 1에서 좌표가 같다(미결).')
    return f, pr

# ----------------------------------------------------------------- 지도 3: 중·하류 (17-30)
def map_midlow(mode):
    bbox = (109.6, 27.6, 123.0, 33.2)
    f, pr = basemap(bbox, pad=360, mode=mode, rivers=RIV, lakes=True, grid=2, latside='right')
    P = f.P
    area(f, pr, 122.2, 28.2, '동중국해', FS_S, P['soft'], 700, 2.0, where='sea')
    rlabel(f, pr, {'Yangtze', 'Chang Jiang'}, (112.0, 30.35), '장강', 0, -16, 'middle')
    rlabel(f, pr, {'Han'}, (112.0, 31.9), '한수', 12, -12)
    rlabel(f, pr, {'Gan'}, (116.0, 28.2), '감강', 14, 8)
    rlabel(f, pr, {'Yuan'}, (110.5, 28.6), '원강', 12, -12)
    offs = {17: (-14, -12, 'end'), 18: (-14, -12, 'end'), 19: (14, 28, 'start'), 20: (-14, 8, 'end'), 21: (14, 8, 'start'), 22: (14, -10, 'start'),
            23: (-14, -12, 'end'), 24: (-14, 26, 'end'), 25: (14, -12, 'start'), 26: (-14, 26, 'end'), 27: (14, 8, 'start'), 28: (14, -10, 'start'),
            29: (14, -10, 'start'), 30: (-14, -12, 'end')}
    for n, (dx, dy, an) in offs.items():
        site(f, pr, n, dx, dy, an, num='29 남경' if n == 29 else None)
    for nm, dx, dy, an, big in (('무한', 14, 30, 'start', True), ('상해', 14, 28, 'start', True)):
        lon, lat = {'무한': (114.31, 30.59), '상해': (121.47, 31.23)}[nm]
        city(f, pr, lon, lat, nm, dx, dy, an, big=big)
    for nm, lon, lat, dx, dy, an in (('동정호', 112.9, 29.0, 0, 70, 'middle'), ('파양호', 116.3, 29.0, 20, 50, 'start'), ('태호', 120.2, 31.2, 0, 56, 'middle')):
        x, y = pr(lon, lat)
        f.text(x + dx, y + dy, nm, FS_I, an, P['river'], 400)
    north(f, 70, 90, 100)
    last = sites_legend(f, pr, [('dot', '도시')][:0])
    scalebar(f, pr, 40, last + 76, 200)
    note(f, 30, last + 150, '※ 번호는 표 1의 시료 번호. 도시 표지(큰 점)는 일반 지명 위치.')
    return f, pr

# ----------------------------------------------------------------- 지도 4: 하구와 YD0901
def map_delta(mode):
    bbox = (117.8, 29.6, 123.4, 33.0)
    f, pr = basemap(bbox, pad=360, mode=mode, rivers={'Yangtze', 'Chang Jiang'}, lakes=True, grid=1, latside='right')
    P = f.P
    area(f, pr, 122.7, 30.2, '동중국해', FS_S, P['soft'], 700, 2.0, where='sea')
    rlabel(f, pr, {'Yangtze', 'Chang Jiang'}, (118.4, 32.0), '장강', 12, -14)
    site(f, pr, 29, 14, -10, 'start', num='29 남경'); site(f, pr, 30, -14, 28, 'end')
    x, y = pr(dms(122, 30, 0.655), dms(31, 11, 1.768))
    f.marker(x, y, 'star', 1.0, P['hot'])
    f.text(x + 18, y - 14, 'YD0901', FS_S, 'start', P['hot'], 700)
    for nm, lo, la, dx, dy, an in (('상해', 121.47, 31.23, -14, -14, 'end'), ('항주', 120.16, 30.27, -14, 28, 'end')):
        city(f, pr, lo, la, nm, dx, dy, an, big=nm == '상해')
    x, y = pr(120.2, 31.2)
    f.text(x, y + 56, '태호', FS_I, 'middle', P['river'], 400)
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('river', '장강'), ('star', '코어 YD0901(Wang 등, 2011)'), ('dot', '본류 시료(He 등, 2015)')])
    scalebar(f, pr, 40, last + 76, 100)
    note(f, 30, last + 150, '※ 코어 좌표 31°11′01.768″N, 122°30′00.655″E, 수심 21 m. 30번 시료와 약 49.6 km(계산 10-6).')
    note(f, 30, last + 188, '양저·모산 유적은 두 논문 본문에 좌표가 없어 그리지 않았다.')
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

# ----------------------------------------------------------------- 그래프 1: Brune 곡선
BR = [('우동더', 5.9 / 120, 77.45, 'dot'), ('바이허탄', 19.0 / 130, 86.92, 'dot'), ('시뤄두', 11.6 / 139, 82.69, 'dot'), ('샹자바', 5.0 / 141, 73.45, 'dot'),
      ('네 댐 합계', 41.4 / 145, 90.64, 'tri'), ('삼협댐 139 m', 13.6 / 436, 71.69, 'sq'), ('삼협댐 156 m', 23.1 / 436, 78.28, 'sq'), ('삼협댐 175 m', 39.3 / 436, 83.35, 'sq')]
BRK = {'우동더': '오동덕', '바이허탄': '백학탄', '시뤄두': '계락도', '샹자바': '향가패', '네 댐 합계': '네 댐 합계', '삼협댐 139 m': '삼협댐 139 m', '삼협댐 156 m': '삼협댐 156 m', '삼협댐 175 m': '삼협댐 175 m'}
def chart_brune(mode):
    W, H = 1300.0, 1060.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    lx0, lx1 = math.log10(0.02), math.log10(0.5)
    X = lambda v: L + (math.log10(v) - lx0) / (lx1 - lx0) * (R - L)
    Y = lambda v: B - (v - 60) / 40.0 * (B - T)
    axes(f, L, T, R, B, [0.02, 0.05, 0.1, 0.2, 0.5], range(60, 101, 10), X, Y, '체류 시간 변화 Δτ = ΣV/Q (연)', '포획 효율 TE (%)', lambda v: ('%g' % v))
    xs = np.logspace(lx0, lx1, 80)
    pts = ' L'.join('%s,%s' % (f1(X(x)), f1(Y(100 * (1 - 0.05 / math.sqrt(x))))) for x in xs)
    f.raw('<path d="M%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (pts, P['river'] if mode == 'color' else '#333333'))
    offs = {'오동덕': (-16, 36, 'end'), '백학탄': (16, 40, 'start'), '계락도': (-16, 40, 'end'), '향가패': (-16, -18, 'end'),
            '네 댐 합계': (-16, 40, 'end'), '삼협댐 139 m': (18, 40, 'start'), '삼협댐 156 m': (-18, -18, 'end'), '삼협댐 175 m': (18, 40, 'start')}
    for nm, d, te, kind in BR:
        k = BRK[nm]
        col = P['hot'] if kind == 'sq' else P['text']
        f.marker(X(d), Y(te), kind, 1.1, col)
        dx, dy, an = offs[k]
        f.text(X(d) + dx, Y(te) + dy, k, FS_I, an, col, 700)
    ly = B + 150
    f.line(150, ly - 9, 210, ly - 9, P['river'] if mode == 'color' else '#333333', 3.4)
    f.text(226, ly, 'TE = 1 − 0.05/√Δτ (Brune, 1953)', FS_S, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, '점은 Hu 등(2009) 표 4의 V와 Q로 이 책이 계산한 값(계산 10-1). 사각형이 삼협댐, 삼각형이 네 댐 합계.')
    note(f, 150, ly + 92, '가로축은 로그 눈금. 0.02 미만은 TE가 급히 낮아져 그리지 않았다.')
    return f

# ----------------------------------------------------------------- 그래프 2: 삼협댐 이전 가정과 실측
EST = [260.1, 217.4, 309.6, 111.6, 225.2, 246.6]
MEA = [98, 64, 110, 9, 53, 32]
def chart_tgd(mode):
    W, H = 1300.0, 1060.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    ymax = 350.0
    Y = lambda v: B - v / ymax * (B - T)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 351, 50):
        f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.line(L - 8, Y(v), L, Y(v), P['frame'], 2.0)
        f.text(L - 14, Y(v) + 10, str(v), FS_I, 'end', P['soft'], 400, False)
    gw = (R - L) / 6.0
    c1 = '#C9B27A' if mode == 'color' else '#BBBBBB'
    c2 = P['river'] if mode == 'color' else '#222222'
    for i in range(6):
        x0 = L + i * gw + 10
        bw = (gw - 20) / 2.0
        f.rect(x0, Y(EST[i]), bw, B - Y(EST[i]), c1, P['frame'], 1.6)
        f.rect(x0 + bw, Y(MEA[i]), bw, B - Y(MEA[i]), c2, P['frame'], 1.6)
        f.text(x0 + bw / 2, Y(EST[i]) - 10, '%.1f' % EST[i], FS_I, 'middle', P['text'], 400, False)
        f.text(x0 + bw * 1.5, Y(MEA[i]) - 10, str(MEA[i]), FS_I, 'middle', P['text'], 400, False)
        f.text(x0 + bw, B + 44, str(2003 + i), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연도', FS_S, 'middle', P['text'], 400, False)
    f.text(L - 120, T - 30, '의창 연 유사량(Mt/yr)', FS_S, 'start', P['text'], 400, False)
    ly = B + 150
    f.rect(150, ly - 26, 44, 26, c1, P['frame'], 1.6)
    f.text(206, ly, '회귀식 (3)으로 구한 댐 없는 경우', FS_S, 'start', P['text'], 400, False)
    f.rect(150, ly + 26, 44, 26, c2, P['frame'], 1.6)
    f.text(206, ly + 52, '실측(표 3)', FS_S, 'start', P['text'], 400, False)
    note(f, 150, ly + 108, '차이가 댐이 가둔 양: 2006년 102.6, 2008년 214.6, 6년 평균 167.4 Mt/yr(계산 10-3).')
    note(f, 150, ly + 144, '자료: Hu 등(2009) 표 3, 식 (3). 추정값은 이 책의 계산.')
    return f

# ----------------------------------------------------------------- 그래프 3: CIA
CIA = [60.66, 63.69, 56.69, 61.92, 63.95, 65.15, 63.59, 56.45, 61.37, 64.21, 62.96, 63.77, 60.38, 64.97, 77.50, 62.63, 76.46, 65.81, 60.70, 69.14,
       80.14, 64.48, 69.60, 62.97, 68.24, 65.01, 71.50, 62.31, 60.35, 58.60]
CIA_C = {20: 70.65, 21: 84.01, 27: 74.32}
def chart_cia(mode):
    W, H = 1300.0, 1060.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    X = lambda n: L + (n - 0.5) / 30.0 * (R - L)
    Y = lambda v: B - (v - 50) / 40.0 * (B - T)
    axes(f, L, T, R, B, [1, 5, 10, 15, 20, 25, 30], range(50, 91, 10), X, Y, '시료 번호(표 1·표 2 순서, 대체로 상류에서 하류)', 'CIA')
    m = sum(CIA) / 30.0
    f.line(L, Y(m), R, Y(m), P['text'], 2.0, '14 8')
    f.text(R - 10, Y(m) - 12, '평균 %.2f' % m, FS_I, 'end', P['text'], 400, False)
    for n, v in enumerate(CIA, 1):
        kind = 'sq' if n in TRIB else 'dot'
        col = P['hot'] if n in TRIB else P['text']
        f.marker(X(n), Y(v), kind, 0.9, col)
    for n, v in CIA_C.items():
        f.line(X(n), Y(CIA[n - 1]), X(n), Y(v), P['frame'], 2.0, '6 6')
        f.marker(X(n), Y(v), 'dia', 0.8, '#FFFFFF', P['text'])
    for n, ko, dx, dy, an in ((17, '파동', -18, 8, 'end'), (15, '오강', -18, -4, 'end'), (21, '상강', 18, 8, 'start'), (20, '원강', 18, 28, 'start'), (27, '감강', 18, -4, 'start'),
                              (8, '대도하', 0, 44, 'middle'), (3, '석고', 0, 44, 'middle'), (30, '장흥도', 0, 44, 'end')):
        f.text(X(n) + dx, Y(CIA[n - 1]) + dy, ko, FS_I, an, P['text'], 700)
    ly = B + 150
    f.marker(170, ly - 9, 'dot', 0.9, P['text']); f.text(194, ly, '본류 시료', FS_S, 'start', P['text'], 400, False)
    f.marker(430, ly - 9, 'sq', 0.9, P['hot']); f.text(454, ly, '지류 시료', FS_S, 'start', P['text'], 400, False)
    f.marker(700, ly - 9, 'dia', 0.8, '#FFFFFF', P['text']); f.text(724, ly, '산화물에서 다시 계산한 값(3개만)', FS_S, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, '채운 표지는 논문 표 2의 CIA. 빈 마름모는 CaO가 1% 미만인 세 시료에서 표와 맞지 않는 재계산 값(계산 10-8).')
    note(f, 150, ly + 92, '나머지 27개는 재계산이 표와 0.1 이내로 맞는다. 본류·지류 구분은 이 책이 정했다.')
    return f

# ----------------------------------------------------------------- 그래프 4: εNd
ND = [-10.65, -10.85, -10.69, -8.9, -8.23, -8.84, -11.28, -11.63, -8.54, -10.71, -11.7, -15.18, -13.3, -11.96, -12.39, -11.18, -11.7, -12.19, -14.08, -11.72,
      -10.73, -11.1, -11.22, -13.87, -10.75, -11.9, -11.51]
NDT = {5, 8, 9, 12, 14, 19, 21, 24}
def chart_nd(mode):
    W, H = 1300.0, 1060.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    L, T, R, B = 170.0, 90.0, 1240.0, 700.0
    X = lambda n: L + (n - 0.5) / 27.0 * (R - L)
    Y = lambda v: B - (v + 16.5) / 9.0 * (B - T)
    axes(f, L, T, R, B, [1, 5, 10, 15, 20, 25, 27], [-16, -14, -12, -10, -8], X, Y, '시료 번호(표 6 순서)', 'εNd')
    m = sum(ND) / 27.0
    f.line(L, Y(m), R, Y(m), P['text'], 2.0, '14 8')
    f.text(R - 10, Y(m) - 12, '평균 %.2f' % m, FS_I, 'end', P['text'], 400, False)
    for n, v in enumerate(ND, 1):
        kind = 'sq' if n in NDT else 'dot'
        f.marker(X(n), Y(v), kind, 0.9, P['hot'] if n in NDT else P['text'])
    for n, ko, dx, dy, an in ((5, '아롱강', 18, 8, 'start'), (9, '대도하', 18, 8, 'start'), (12, '가릉강', 18, 8, 'start'), (13, '중경 2', 18, 8, 'start'),
                              (19, '원강', 18, 8, 'start'), (24, '감강', 18, 8, 'start'), (1, '타타하', 18, -14, 'start')):
        f.text(X(n) + dx, Y(ND[n - 1]) + dy, ko, FS_I, an, P['text'], 700)
    ly = B + 150
    f.marker(170, ly - 9, 'dot', 0.9, P['text']); f.text(194, ly, '본류 시료', FS_S, 'start', P['text'], 400, False)
    f.marker(430, ly - 9, 'sq', 0.9, P['hot']); f.text(454, ly, '지류 시료', FS_S, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, '자료: He 등(2015) 표 6의 εNd. 부릉 1, 상강, 악양 1은 Sr-Nd를 분석하지 않아 27개다.')
    note(f, 150, ly + 92, '표 6의 번호는 표 1과 다르다(부릉 한 개로 합쳐짐).')
    return f

# ----------------------------------------------------------------- 그래프 5: 코어 YD0901과 REDFIT 주기
def chart_core(mode):
    W, H = 1300.0, 1060.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    top, sc = 130.0, 9.0
    Yd = lambda d: top + d * sc
    cx0, cx1 = 150.0, 290.0
    secs = [(0, 34.22, '삼각주 앞면', '#E8D9A8', '#DADADA'), (34.22, 51.88, '해성', '#9DB7C4', '#A8A8A8'), (51.88, 65.23, '하성(하상)', '#8C7B64', '#6A6A6A')]
    for a, b, lab, c1, c2 in secs:
        f.rect(cx0, Yd(a), cx1 - cx0, (b - a) * sc, c1 if mode == 'color' else c2, P['frame'], 1.6)
    f.text(cx1 + 18, Yd(17) + 10, '삼각주 앞면 0-34.22 m', FS_I, 'start', P['text'], 700, False)
    f.text(cx1 + 18, Yd(43) + 10, '해성 34.22-51.88 m', FS_I, 'start', P['text'], 700, False)
    f.text(cx1 + 18, Yd(58.5) + 10, '하성 51.88-65.23 m', FS_I, 'start', P['text'], 700, False)
    for d in (0, 34.22, 51.88, 65.23):
        f.text(cx0 - 12, Yd(d) + 10, '%g' % d, FS_I, 'end', P['soft'], 400, False)
    f.text(cx0 - 12, top - 40, '깊이(m)', FS_I, 'end', P['text'], 400, False)
    # 표시
    f.marker(cx0 + 70, Yd(4.01), 'dia', 0.9, P['hot'] if mode == 'color' else '#111111')
    f.text(cx1 + 18, Yd(4.01) - 6, '4.01 m  14C 790±30 a BP', FS_I, 'start', P['hot'] if mode == 'color' else '#111111', 700, False)
    f.text(cx1 + 18, Yd(7.4) + 12, '0-5 m: 명·청 시기, 0.92 cm/a', FS_I, 'start', P['text'], 400, False)
    # 오른쪽: 주기 축
    rx0, rx1 = 740.0, 1240.0
    p0, p1 = 2.0, 9.0
    Xp = lambda p: rx0 + (p - p0) / (p1 - p0) * (rx1 - rx0)
    yb0, yb1 = 200.0, 620.0
    f.rect(rx0, yb0, rx1 - rx0, yb1 - yb0, 'none', P['frame'], 2.4)
    f.rect(Xp(3), yb0, Xp(8) - Xp(3), yb1 - yb0, P['hot'] if mode == 'color' else '#999999', 'none', 0, 'fill-opacity="0.18"')
    for p in range(2, 10):
        f.line(Xp(p), yb1, Xp(p), yb1 + 10, P['frame'], 2.0)
        f.text(Xp(p), yb1 + 44, str(p), FS_I, 'middle', P['soft'], 400, False)
    f.text((rx0 + rx1) / 2, yb1 + 92, '주기(a)', FS_S, 'middle', P['text'], 400, False)
    f.text((Xp(3) + Xp(8)) / 2, yb0 + 40, '현대 ENSO 3-8 a', FS_S, 'middle', P['text'], 700, False)
    peaks = [(3.9, 0), (4.5, 1), (4.7, 0), (5.2, 2), (6.9, 0)]
    for p, row in peaks:
        f.line(Xp(p), yb1, Xp(p), yb0 + 130 + row * 70, P['text'], 4.0)
        f.marker(Xp(p), yb0 + 130 + row * 70, 'dot', 0.9, P['hot'] if mode == 'color' else '#111111')
        f.text(Xp(p), yb0 + 110 + row * 70, '%.1f' % p, FS_I, 'middle', P['text'], 700, False)
    f.text(rx0, yb0 - 34, 'Zr/Rb 시계열 REDFIT, 95% 신뢰', FS_S, 'start', P['text'], 400, False)
    note(f, 150, 790, '왼쪽: 코어 YD0901의 층(Wang 등, 2011 본문의 깊이 경계).')
    note(f, 150, 826, '오른쪽: 본문이 적은 다섯 주기의 위치. 세로선의 높이는 의미가 없다(값이 본문에 없음).')
    note(f, 150, 862, '1 cm 간격 XRF = 1.09 a/시료(계산 10-6).')
    return f

# ----------------------------------------------------------------- 그래프 6: 시간표 (Zhuang 2014)
def chart_timeline(mode):
    W, H = 1300.0, 1060.0
    f = Fig(W, H, mode); P = f.P
    f.rect(0, 0, W, H, '#FFFFFF')
    L, R = 640.0, 1240.0
    T, B = 100.0, 640.0
    a0, a1 = 7500.0, 3500.0
    X = lambda a: L + (a0 - a) / (a0 - a1) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for a in range(7000, 3499, -500):
        f.line(X(a), T, X(a), B, P['grid'], 1.0, '8 8')
        f.line(X(a), B, X(a), B + 10, P['frame'], 2.0)
        if a % 1000 == 0:
            f.text(X(a), B + 44, str(a), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, 'cal BP (왼쪽이 오래됨)', FS_S, 'middle', P['text'], 400, False)
    rows = [('Majiabang (c. 7000-6000)', 7000, 6000, 0), ('벼 길들이기 (6900-6600)', 6900, 6600, 1), ('양저 문화 (5300-4200)', 5300, 4200, 2),
            ('논 층 (4700-4200)', 4700, 4200, 3), ('후기 양저 (c. 4500-4000)', 4500, 4000, 4), ('냉각 사건 (4300-4000)', 4300, 4000, 5), ('Guangfulin (c. 4100-3800)', 4100, 3800, 6)]
    rh = (B - T) / 8.0
    cols = [P['soft'], P['river'], P['hot'], P['hot'], P['text'], '#6B7A82', P['site']] if mode == 'color' else ['#777777', '#999999', '#333333', '#555555', '#111111', '#888888', '#222222']
    for lab, s, e, r in rows:
        y = T + (r + 0.5) * rh
        f.text(L - 16, y + 10, lab, FS_I, 'end', P['text'], 400, False)
        f.rect(X(s), y - 18, X(e) - X(s), 36, cols[r], P['frame'], 1.6)
    # 점 사건
    y = T + 7.5 * rh
    f.text(L - 16, y + 10, '냉각 5500 / 해수면 -2.5 m 7000', FS_I, 'end', P['text'], 400, False)
    for a in (5500, 7000):
        f.marker(X(a), y, 'dia', 0.9, P['hot'] if mode == 'color' else '#111111')
    note(f, 150, 710 + 80, '자료: Zhuang 등(2014) 본문의 연대. 막대의 시작·끝은 본문이 적은 값.')
    note(f, 150, 746 + 80, '논 층 4700-4200 cal BP는 29개 AMS 14C 날짜의 대부분이 들어가는 구간이라고 본문이 적었다.')
    note(f, 150, 782 + 80, '냉각 막대는 연구마다 다른 구간이며 같은 사건이라는 근거는 아니다.')
    return f

if __name__ == '__main__':
    maps = [('map-yz-basin-v1', map_basin), ('map-yz-upper-v1', map_upper), ('map-yz-midlow-v1', map_midlow), ('map-yz-delta-v1', map_delta)]
    charts = [('chart-brune-v1', chart_brune), ('chart-tgd-v1', chart_tgd), ('chart-cia-v1', chart_cia), ('chart-nd-v1', chart_nd),
              ('chart-core-v1', chart_core), ('chart-timeline-v1', chart_timeline)]
    for mode in ('color', 'bw'):
        for nm, fn in maps:
            f, pr = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
        for nm, fn in charts:
            f = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
