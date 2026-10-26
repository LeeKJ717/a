# -*- coding: utf-8 -*-
"""12장 그림: 지도 1장 + 그래프 4장. 값은 각 논문 본문의 숫자이거나 ms/ch12-calc-v1.py 의 계산 결과다.
지도의 점은 Natural Earth 도시 위치이며 유적 위치가 아니다."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomap as G
from geomap import basemap, area, city, scalebar, north, legend, Fig, FS, FS_S, FS_I, f1, PAL
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')

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

def base(mode, H=1000.0):
    f = Fig(1300.0, H, mode)
    f.rect(0, 0, 1300.0, H, '#FFFFFF')
    return f, f.P

def shades(P, mode):
    if mode == 'color':
        return [P['river'], P['hot'], P['site'], '#6B7A82', '#9DB7C6', '#C9A87A']
    return ['#111111', '#555555', '#888888', '#BBBBBB', '#DDDDDD', '#333333']

# ------------------------------------------------------------ 지도: 한반도
def map_korea(mode):
    bbox = (124.2, 33.0, 130.6, 38.8)
    f, pr = basemap(bbox, pad=420, mode=mode, rivers=(), lakes=False, grid=1, latside='left')
    P = f.P
    area(f, pr, 124.9, 35.0, '황해', FS_S, P['soft'], 700, 2.0, where='sea')
    area(f, pr, 130.0, 36.2, '동해', FS_S, P['soft'], 700, 2.0, where='sea')
    # 북위 36~37도 띠(소리리)
    x0, y1 = pr(124.2, 37.0); x1, y2 = pr(130.6, 36.0)
    f.raw('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="2" stroke-dasharray="10 8"/>' % (
        f1(x0), f1(y1), f1(x1 - x0), f1(y2 - y1), P['hot'], P['hot']))
    f.text(x1 - 12, y1 + 38, '소리리 위도 띠 36~37°N', FS_S, 'end', P['hot'], 700)
    for nm, lo, la, dx, dy, an, big in (
            ('서울', 126.998, 37.568, -14, -12, 'end', True), ('인천', 126.640, 37.478, -14, 10, 'end', False),
            ('춘천', 127.734, 37.875, 14, -12, 'start', False), ('강릉', 128.896, 37.756, 14, -12, 'start', False),
            ('청주', 127.501, 36.644, 14, 34, 'start', False), ('울산', 129.315, 35.549, -14, 8, 'end', True),
            ('부산', 129.008, 35.097, 14, 30, 'start', False), ('제주', 126.522, 33.510, 14, 8, 'start', True)):
        city(f, pr, lo, la, nm, dx, dy, an, big=big)
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('dot', '도시(Natural Earth 위치)')])
    scalebar(f, pr, 40, last + 76, 100)
    note(f, 30, last + 150, '※ 점은 도시의 대표 위치이며 유적 위치가 아니다. 고산리, 암사동, 오산리, 대능리, 중도, 송국리, 소리리 등의 좌표는 이 책이 읽은 본문에 없어 그리지 않았다. 좌표 확인 필요.')
    note(f, 30, last + 260, '띠는 소리리 보고서의 "북위 36~37도"를 그대로 옮긴 것이며 유적의 점이 아니다(남북 폭 약 111 km, 계산 12-17).')
    return f

# ------------------------------------------------------------ 그래프 1: 시기 구분 비교(기원전)
def chart_period(mode):
    f, P = base(mode, 1180.0)
    L, T, R, B = 400.0, 60.0, 1250.0, 720.0
    lo, hi = -8200.0, 0.0
    X = lambda v: L + (v - lo) / (hi - lo) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(-8000, 1, 2000):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, ('기원전 %d' % -v) if v < 0 else '0', FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '연대(기원전, cal BP는 1950 - cal BP로 옮김)', FS_S, 'middle', P['text'], 400, False)
    rows = [
        ('Kim 등(2021) 빗살무늬', [(-8050, -6050), (-6050, -4550), (-4550, -3550), (-3550, -3050), (-3050, -2050), (-2050, -1550)]),
        ('Kim 등(2025) 빗살무늬', [(-8000, -6200), (-6200, -4500), (-4500, -3000), (-3000, -1500)]),
        ('Kim 등(2025) 무문', [(-1500, -800), (-800, -400), (-400, -100)]),
        ('Nelson 등(2020) 무문', [(-1300, -800), (-800, -500)]),
        ('Robbeets 등 청동기', [(-1350, -850)]),
    ]
    cols = shades(P, mode)
    rowh = (B - T) / len(rows)
    for i, (nm, segs) in enumerate(rows):
        y = T + (i + 0.5) * rowh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        for k, (a, b) in enumerate(segs):
            f.rect(X(a), y - 28, X(b) - X(a), 56, cols[(k + i) % 6], '#FFFFFF', 2.0)
            if X(b) - X(a) >= 70:
                f.text((X(a) + X(b)) / 2, y + 10, '%d' % (k + 1), FS_I, 'middle', '#FFFFFF' if (mode == 'color' or (k + i) % 6 in (0, 1, 2, 5)) else '#111111', 700, False)
    ly = B + 150
    note(f, 40, ly, '막대 안 숫자는 단계의 순서이다(첫째 줄 1=Incipient, 2=Initial, 3=Early, 4=Middle, 5=Late, 6=Final. 둘째 줄 1=Initial, 2=Early, 3=Middle, 4=Late. 셋째 줄 1=Early, 2=Middle, 3=Late).')
    note(f, 40, ly + 110, '같은 이름 "Early"가 첫째 줄에서는 기원전 4550~3550, 둘째 줄에서는 기원전 6200~4500이다(계산 12-1). 너비 70 이하의 칸은 숫자를 생략했다.')
    return f

# ------------------------------------------------------------ 그래프 2: Kim 등(2021) 자료 흐름
def chart_funnel(mode):
    f, P = base(mode, 900.0)
    L, T, R, B = 470.0, 60.0, 1230.0, 560.0
    rows = [('날짜 처음', 894, 0), ('날짜 분석', 683, 0), ('해안 날짜', 363, 1), ('내륙 날짜', 319, 1),
            ('해안 성기게 한 뒤', 197, 2), ('내륙 성기게 한 뒤', 179, 2), ('유적 처음', 163, 3), ('유적 분석', 136, 3)]
    mx = 900.0
    X = lambda v: L + v / mx * (R - L)
    rowh = (B - T) / len(rows)
    cols = shades(P, mode)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 901, 300):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%d' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '개수(날짜 또는 유적)', FS_S, 'middle', P['text'], 400, False)
    for i, (nm, v, g) in enumerate(rows):
        y = T + (i + 0.5) * rowh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        f.rect(L, y - 24, X(v) - L, 48, cols[g], '#FFFFFF', 2.0)
        f.text(X(v) + 10, y + 10, str(v), FS_I, 'start', P['text'], 700, False)
    ly = B + 150
    note(f, 40, ly, '해안 363 + 내륙 319 = 682이며 본문의 683과 1이 다르다(계산 12-2). 성기게 한 뒤의 197 + 179 = 376.')
    return f

# ------------------------------------------------------------ 그래프 3: 콩 크기 보고값
def chart_soy(mode):
    f, P = base(mode, 1000.0)
    L, T, R, B = 520.0, 60.0, 1090.0, 640.0
    rows = [('Jiahu 평균(탄화 258알)', 3.1, 3.1, 0), ('Yuezhuang 평균(탄화)', 2.6, 2.6, 0), ('Jiaochangpu 평균(탄화)', 3.4, 3.4, 0),
            ('무문토기 시기 한국(탄화, 범위)', 3.8, 9.9, 1), ('Usujiri 후기 조몬(탄화 1알)', 4.5, 4.5, 2), ('Yamanokami 토기 자국', 5.62, 5.62, 3),
            ('Kyushu 후기 조몬 토기 자국', 10.2, 11.8, 3)]
    mx = 12.0
    X = lambda v: L + v / mx * (R - L)
    rowh = (B - T) / len(rows)
    cols = shades(P, mode)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, 13, 2):
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%d' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '콩의 길이(mm)', FS_S, 'middle', P['text'], 400, False)
    for i, (nm, a, b, g) in enumerate(rows):
        y = T + (i + 0.5) * rowh
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        if a == b:
            f.marker(X(a), y, 'dot', 1.3, cols[g])
            f.text(X(a) + 24, y + 10, '%.2f' % a if a * 100 % 10 else '%.1f' % a, FS_I, 'start', P['text'], 400, False)
        else:
            f.rect(X(a), y - 22, X(b) - X(a), 44, cols[g], '#FFFFFF', 2.0)
            f.text(X(b) + 10, y + 10, '%.1f~%.1f' % (a, b), FS_I, 'start', P['text'], 400, False)
    ly = B + 150
    note(f, 40, ly, '탄화한 씨앗은 불에 탈 때 줄어들고 토기 자국은 구멍의 크기이므로 두 값을 같은 줄에 놓고 비교할 수 없다. 이 그림은 보고된 숫자를 늘어놓았을 뿐이다(계산 12-12).')
    return f

# ------------------------------------------------------------ 그래프 4: Nelson 등(2020) 표 1의 한국 10행
def chart_whorl(mode):
    f, P = base(mode, 1080.0)
    L, T = 470.0, 150.0
    cols = ['기장', '농기구', '삼', '원뿔 가락바퀴', '납작 가락바퀴', '뼈바늘·송곳']
    data = [('Osan-li', [0, 1, 0, 1, 0, 'N']), ('Pibong-li', [1, 1, 0, 1, 1, 'N']), ('Amsadong', [1, 1, 0, 1, 1, 'N']),
            ('Sopohang', [0, 1, 0, 1, 0, 0]), ('Nongpodong', [0, 1, 0, 1, 0, 'N']), ('Sinam-li', [0, 1, 0, 1, 1, 0]),
            ('Upper Kungsan-li', ['?', 1, 0, 1, 1, 1]), ('Tongsamdong', [1, 1, 0, 1, 1, 1]), ('Jungsandong', [1, 1, 0, 1, 1, 'N']),
            ('Pangokdong', [1, 1, 0, 1, 0, 'N'])]
    cw, rh = 120.0, 66.0
    cl = shades(P, mode)
    for j, c in enumerate(cols):
        x = L + j * cw + cw / 2
        f.text(x, T - 22 - (30 if j % 2 else 0), c, FS_I, 'middle', P['text'], 700, False)
    for i, (nm, v) in enumerate(data):
        y = T + i * rh + rh / 2
        f.text(L - 14, y + 10, nm, FS_I, 'end', P['text'], 400, False)
        for j, s in enumerate(v):
            x = L + j * cw + cw / 2
            f.rect(x - cw / 2 + 4, y - rh / 2 + 4, cw - 8, rh - 8, 'none', P['grid'], 1.2)
            if s == 1: f.marker(x, y, 'dot', 1.3, cl[1])
            elif s == '?': f.text(x, y + 12, '?', FS, 'middle', P['text'], 700, False)
            elif s == 'N': f.text(x, y + 10, 'ND', FS_I, 'middle', P['soft'], 400, False)
            else: f.text(x, y + 12, '0', FS_I, 'middle', P['soft'], 400, False)
    ly = T + len(data) * rh + 70
    note(f, 40, ly, '채운 점 = 있음(1), 0 = 없음, ? = 불확실, ND = 본문 표에 자료 없음(No data). 기장이 0인 네 곳(Osan-li, Sopohang, Nongpodong, Sinam-li)도 농기구 열은 1이다(계산 12-13).')
    note(f, 40, ly + 110, '표는 가락바퀴가 있는 유적을 골라 만든 것이어서 가락바퀴 없는 유적의 농업 여부는 비교되지 않는다.')
    return f

if __name__ == '__main__':
    items = [('map-v1', map_korea), ('period-v1', chart_period), ('funnel-v1', chart_funnel),
             ('soy-v1', chart_soy), ('whorl-v1', chart_whorl)]
    for mode in ('color', 'bw'):
        for nm, fn in items:
            f = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, 'fig-ch12-%s-%s.svg' % (nm, mode))))
