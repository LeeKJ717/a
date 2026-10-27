#!/usr/bin/env python3
# 장 표지 그림 생성(제4권 지구): fig/chapart-NN-{color,bw}.svg  (Natural Earth, 도안용 - 자료 그림이 아님)
# 쓰는 법: 작업 폴더(book4)에서 python3 scripts/chapart-v1.py   0~15장의 색, 흑백 도안 32개를 만든다.
# 도안의 굽은 화살표(해류, 바람, 이동)와 고리는 장의 주제를 보이는 장식이며 측정한 자료가 아니다. 점(빙핵 지점)만 2장이 확인한 좌표이다.
import json, math, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from shapely.geometry import shape, box
W, H = 129.6, 64.0
PAL = {
 'color': dict(sea='#3b8ca6', deep='#1b4d66', land='#eadfc6', river='#2a7390', hi='#e07a3f', grid='#ffffff', ring='#e07a3f', ink='#0f2a3f',
               strata=['#d9c9a3', '#b89b6a', '#e6dcc2', '#8f7451', '#c7ae80', '#6f5a40', '#d4c096', '#a98a5c', '#4d3f2e']),
 'bw':    dict(sea='#d6d6d6', deep='#9c9c9c', land='#fafafa', river='#555555', hi='#000000', grid='#ffffff', ring='#222222', ink='#222222',
               strata=['#eeeeee', '#bdbdbd', '#f6f6f6', '#8a8a8a', '#d0d0d0', '#666666', '#e2e2e2', '#a0a0a0', '#444444']),
}
_c = {}
def load(n):
    if n not in _c: _c[n] = [shape(f['geometry']) for f in json.load(open(os.path.join(ROOT, 'geodata', n + '.geojson')))['features']]
    return _c[n]
def props(n): return [f['properties'] for f in json.load(open(os.path.join(ROOT, 'geodata', n + '.geojson')))['features']]
def path(g, X, Y):
    polys = [g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))
    d = ''
    for p in polys:
        if p.geom_type != 'Polygon' or p.is_empty: continue
        for r in [p.exterior] + list(p.interiors):
            d += 'M' + 'L'.join(f'{X(x):.2f},{Y(y):.2f}' for x, y in r.coords) + 'Z'
    return d
def lines(g, X, Y):
    ls = [g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))
    return ''.join('M' + 'L'.join(f'{X(x):.2f},{Y(y):.2f}' for x, y in l.coords) for l in ls if not l.is_empty)
HI = {'Selenga': ('Selenga',), 'Nile': ('Nile', 'El Bahr el Abyad', 'El Bahr el Azraq', 'Albert Nile', 'Victoria Nile', 'Bahr el Jebel', 'Abay'),
      'Euphrates': ('Euphrates', 'Al Furat', 'Firat', 'Shatt al Arab'), 'Amazonas': ('Amazonas', 'Madeira', 'Mamoré', 'Ucayali'),
      'Murray': ('Murray', 'Darling', 'Barwon'), 'Mekong': ('Mekong', 'Lancang'), 'Yangtze': ('Chang Jiang', 'Yangtze', 'Jinsha', 'Tongtian'),
      'StLawrence': ('St. Lawrence',), 'Niger': ('Niger',), 'Ganges': ('Ganges', 'Brahmaputra', 'Yarlung')}
RIV = set(['Selenga', 'Nile', 'El Bahr el Abyad', 'El Bahr el Azraq', 'Albert Nile', 'Victoria Nile', 'Bahr el Jebel', 'Abay', 'Congo', 'Lualaba', 'Ubangi', 'Niger', 'Zambezi',
           'Euphrates', 'Al Furat', 'Firat', 'Tigris', 'Dicle', 'Shatt al Arab', 'Indus', 'Ganges', 'Brahmaputra', 'Yarlung', 'Mekong', 'Lancang', 'Chang Jiang', 'Yangtze', 'Jinsha', 'Tongtian', 'Huang',
           'Amur', 'Heilong Jiang', 'Lena', 'Ob', 'Irtysh', 'Ertis', 'Yenisey', 'Volga', 'Danube', 'Donau', 'Amazonas', 'Madeira', 'Mamoré', 'Ucayali', 'Paraná', 'Orinoco',
           'Mississippi', 'Missouri', 'Ohio', 'Mackenzie', 'Yukon', 'St. Lawrence', 'Murray', 'Darling', 'Barwon', 'Rhine', 'Rhône', 'Colorado', 'Columbia', 'Sao Francisco', 'Magdalena'])
CH = {  # 제4권 장 표지 도안: (중심 경도, 중심 위도, 반높이(도), 강조할 강, 덧그림)
 0: (0.0, 0.0, 90.0, None, None),             # 지구 전체(지도 도록)
 1: (0.0, 25.0, 55.0, None, 'strata'),        # 기록을 읽는 법(층 도안)
 2: (-42.0, 73.0, 13.0, None, 'gl'),          # 빙핵의 1만 년(그린란드, 2장이 좌표를 확인한 지점)
 3: (60.0, -66.0, 24.0, None, 'an'),         # 온실기체의 기록(남극의 빙핵 지점)
 4: (108.0, 0.0, 22.0, None, 'waves'),        # 해수면과 해안선(대륙붕이 넓은 순다 쪽)
 5: (-40.0, 38.0, 30.0, None, 'current'),     # 해류와 대순환(북대서양, 개략도)
 6: (40.0, 12.0, 33.0, 'Nile', 'wind'),       # 몬순과 열대(아프리카에서 인도양까지)
 7: (-72.0, 55.0, 20.0, 'StLawrence', 'waves'),  # 8.2ka 사건과 홀로세 초기(북미 북동부)
 8: (45.0, 32.0, 17.0, 'Euphrates', 'rings'), # 4.2ka와 중기 홀로세 사건
 9: (-19.0, 64.0, 13.0, None, 'ash'),         # 화산과 기후(북대서양 화산 지대, 도안)
 10: (0.0, 74.0, 16.0, None, 'sun'),          # 태양 활동(북극)
 11: (-80.0, 10.0, 48.0, 'Amazonas', None),   # 아메리카
 12: (125.0, -30.0, 22.0, 'Murray', None),    # 남반구와 오세아니아
 13: (10.0, 50.0, 24.0, None, 'rings'),       # 최근 이천 년(유럽과 북대서양)
 14: (70.0, 30.0, 40.0, 'Yangtze', 'route2'), # 사람과 기후(방향을 정하지 않음)
 15: (0.0, 20.0, 60.0, None, 'focus'),        # 하나의 쟁점을 끝까지
}
GL = [(-61.13, 77.17), (-43.83, 65.18), (-37.565, 72.579), (-38.467, 72.583), (-42.3, 75.1), (-51.07, 77.45), (-26.7, 71.3)]
AN = [(106.8, -78.47), (123.4, -75.1), (-112.086, -79.468), (112.8, -66.77), (-57.68, -64.22)]
CUR = [(-82.0, 24.5), (-78.5, 31.0), (-72.0, 37.5), (-60.0, 42.0), (-45.0, 46.0), (-30.0, 52.0), (-18.0, 58.5), (-8.0, 64.0)]
def art(ci, mode):
    P = PAL[mode]; lon0, lat0, hd, hi, ov = CH[ci]
    if ov == 'strata':
        o = [f'<rect width="{W}" height="{H}" fill="{P["strata"][0]}"/>']
        ws = [0.9, 1.6, 0.7, 2.1, 1.2, 1.8, 0.8, 1.5, 1.4]; tot = sum(ws); y = 0
        for c, q in zip(P['strata'], ws):
            hh = H * q / tot; o.append(f'<rect x="0" y="{y:.2f}" width="{W}" height="{hh + .05:.2f}" fill="{c}"/>'); y += hh
        for r in range(6, 90, 8):
            o.append(f'<circle cx="{W * .78:.1f}" cy="{H * 1.1:.1f}" r="{r}" fill="none" stroke="{P["ink"]}" stroke-opacity=".22" stroke-width=".4"/>')
        o.append(f'<rect x="0" y="{H * .43:.1f}" width="{W}" height="1.3" fill="{P["hi"]}"/>')
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">' + ''.join(o) + '</svg>'
    k = math.cos(math.radians(lat0))
    hw = hd * (W / H) / k
    x0, x1, y0, y1 = lon0 - hw, lon0 + hw, lat0 - hd, lat0 + hd
    s = H / (2 * hd)
    X = lambda lon: (lon - x0) * k * s
    Y = lambda lat: (y1 - lat) * s
    bx = box(x0, y0, x1, y1)
    o = [f'<rect width="{W}" height="{H}" fill="{P["sea"]}"/>']
    step = 5 if hd > 5 else 2
    for lon in range(int(x0 // step) * step, int(x1) + 1, step):
        o.append(f'<path d="M{X(lon):.2f},0L{X(lon):.2f},{H}" stroke="{P["grid"]}" stroke-opacity=".18" stroke-width=".25"/>')
    for lat in range(int(y0 // step) * step, int(y1) + 1, step):
        o.append(f'<path d="M0,{Y(lat):.2f}L{W},{Y(lat):.2f}" stroke="{P["grid"]}" stroke-opacity=".18" stroke-width=".25"/>')
    d = ''
    for g in load('ne_10m_bathymetry_K_200'):
        if g.intersects(bx): d += path(g.intersection(bx), X, Y)
    o.append(f'<path d="{d}" fill="{P["deep"]}" fill-rule="evenodd"/>')
    d = ''
    for n in ('ne_10m_land', 'ne_10m_minor_islands'):
        for g in load(n):
            if g.intersects(bx): d += path(g.intersection(bx), X, Y)
    o.append(f'<path d="{d}" fill="{P["land"]}" fill-rule="evenodd"/>')
    d = ''
    for g, p in zip(load('ne_10m_lakes'), props('ne_10m_lakes')):
        if g.intersects(bx) and g.area > 0.25: d += path(g.intersection(bx), X, Y)
    o.append(f'<path d="{d}" fill="{P["sea"]}" fill-rule="evenodd" stroke="{P["deep"]}" stroke-width=".15"/>')
    gs = load('ne_10m_rivers_lake_centerlines'); pr = props('ne_10m_rivers_lake_centerlines')
    d1 = d2 = ''
    for g, p in zip(gs, pr):
        n = p.get('name')
        if n in RIV and g.intersects(bx):
            gg = g.intersection(bx)
            if hi and n in HI[hi]: d2 += lines(gg, X, Y)
            else: d1 += lines(gg, X, Y)
    o.append(f'<path d="{d1}" fill="none" stroke="{P["river"]}" stroke-width=".45" stroke-linecap="round"/>')
    if d2: o.append(f'<path d="{d2}" fill="none" stroke="{P["hi"]}" stroke-width="1.0" stroke-linecap="round" stroke-linejoin="round"/>')
    if ov == 'ash':
        for r in (5, 10, 16, 23, 31):
            o.append(f'<circle cx="{X(lon0):.1f}" cy="{Y(lat0):.1f}" r="{r}" fill="none" stroke="{P["ring"]}" stroke-opacity=".85" stroke-width=".4" stroke-dasharray="1.2 1"/>')
        o.append(f'<circle cx="{X(lon0):.1f}" cy="{Y(lat0):.1f}" r="1.1" fill="{P["ring"]}"/>')
    if ov in ('gl', 'an'):
        for (lo, la) in (GL if ov == 'gl' else AN):
            o.append(f'<circle cx="{X(lo):.2f}" cy="{Y(la):.2f}" r="1.5" fill="{P["hi"]}" stroke="{P["ink"]}" stroke-width=".3"/>')
    if ov == 'current':
        pts = [(X(lo), Y(la)) for lo, la in CUR]
        d = 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        o.append(f'<path d="{d}" fill="none" stroke="{P["hi"]}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>')
        (x1, y1), (x2, y2) = pts[-2], pts[-1]; ang = math.atan2(y2 - y1, x2 - x1)
        for da in (2.6, -2.6):
            o.append(f'<path d="M{x2:.1f},{y2:.1f}l{-4 * math.cos(ang + da / 5):.1f},{-4 * math.sin(ang + da / 5):.1f}" stroke="{P["hi"]}" stroke-width="1.1" stroke-linecap="round"/>')
    if ov == 'sun':
        cx, cy = W * .82, H * .28
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{P["hi"]}"/>')
        for k2 in range(12):
            a2 = k2 * math.pi / 6
            o.append(f'<path d="M{cx + 7 * math.cos(a2):.1f},{cy + 7 * math.sin(a2):.1f}L{cx + 11 * math.cos(a2):.1f},{cy + 11 * math.sin(a2):.1f}" stroke="{P["hi"]}" stroke-width=".8" stroke-linecap="round"/>')
    if ov == 'wind':
        for i, (ax, ay) in enumerate(((.12, .82), (.2, .62), (.3, .42))):
            x, y = W * ax, H * ay
            o.append(f'<path d="M{x:.1f},{y:.1f}C{x + 28:.1f},{y - 18:.1f} {x + 55:.1f},{y + 2:.1f} {x + 82:.1f},{y - 16:.1f}" fill="none" stroke="{P["hi"]}" stroke-width=".9" stroke-linecap="round"/>')
            xe, ye = x + 82, y - 16
            o.append(f'<path d="M{xe:.1f},{ye:.1f}l-3.6,.2m3.6,-.2l-.9,3.4" stroke="{P["hi"]}" stroke-width=".9" fill="none" stroke-linecap="round"/>')
    if ov in ('route2', 'routew'):
        # 방향 도안: route2 는 양쪽 화살표(서쪽과 동쪽 어느 쪽인지 정하지 않음), routew 는 동쪽에서 서쪽으로 가는 화살표
        xs, xe = W * .14, W * .86
        ys, ye = H * (.62 if ov == 'route2' else .50), H * (.50 if ov == 'route2' else .56)
        if ov == 'routew': xs, xe, ys, ye = xe, xs, ye, ys
        sg = 1 if xe > xs else -1
        dx = xe - xs
        o.append(f'<path d="M{xs:.1f},{ys:.1f}C{xs + dx * .3:.1f},{ys - 14:.1f} {xs + dx * .65:.1f},{ye + 12:.1f} {xe:.1f},{ye:.1f}" fill="none" stroke="{P["hi"]}" stroke-width=".9" stroke-dasharray="2.2 1.4" stroke-linecap="round"/>')
        o.append(f'<path d="M{xe:.1f},{ye:.1f}l{-sg * 3.6:.1f},-1.6m{sg * 3.6:.1f},1.6l{-sg * 3.6:.1f},2.4" stroke="{P["hi"]}" stroke-width=".9" fill="none" stroke-linecap="round"/>')
        if ov == 'route2':
            o.append(f'<path d="M{xs:.1f},{ys:.1f}l{sg * 3.6:.1f},1.6m{-sg * 3.6:.1f},-1.6l{sg * 3.6:.1f},-2.4" stroke="{P["hi"]}" stroke-width=".9" fill="none" stroke-linecap="round"/>')
    if ov == 'focus':
        for r in (6, 12, 19):
            o.append(f'<circle cx="{W * .5:.1f}" cy="{H * .5:.1f}" r="{r}" fill="none" stroke="{P["hi"]}" stroke-width=".7"/>')
        o.append(f'<circle cx="{W * .5:.1f}" cy="{H * .5:.1f}" r="1.4" fill="{P["hi"]}"/>')
    if ov == 'rings':
        for r in range(4, 40, 4):
            o.append(f'<circle cx="{W * .88:.1f}" cy="{H * 1.0:.1f}" r="{r}" fill="none" stroke="{P["ink"]}" stroke-opacity=".5" stroke-width=".4"/>')
    if ov == 'waves':
        for yy in (.14, .22, .30):
            y = H * yy; d = 'M' + 'L'.join(f'{x:.1f},{y + 1.4 * math.sin(x / 4.0):.2f}' for x in [i * 1.5 for i in range(int(W / 1.5) + 1)])
            o.append(f'<path d="{d}" fill="none" stroke="{P["hi"]}" stroke-width=".6" stroke-opacity=".9"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="none" stroke="{P["ink"]}" stroke-width=".6"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}"><defs><clipPath id="c"><rect width="{W}" height="{H}"/></clipPath></defs><g clip-path="url(#c)">' + ''.join(o[:-1]) + '</g>' + o[-1] + '</svg>'
if __name__ == '__main__':
    for ci in CH:
        for m in ('color', 'bw'):
            open(f'fig/chapart-{ci:02d}-{m}.svg', 'w').write(art(ci, m))
    print('ok', len(CH) * 2)
