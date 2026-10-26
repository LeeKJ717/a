#!/usr/bin/env python3
# 장 표지 그림 생성(제3권 유라시아): fig/chapart-NN-{color,bw}.svg  (Natural Earth, 도안용 - 자료 그림이 아님)
# 쓰는 법: 작업 폴더(book3)에서 python3 scripts/chapart-v1.py   0~13장의 색, 흑백 도안 28개를 만든다.
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
HI = {'Selenga': ('Selenga',), 'Yenisey': ('Yenisey', 'Verkhniy Yenisey', 'Malyy Yenisey'), 'Irtysh': ('Irtysh', 'Ertis', 'Ertix'),
      'Amu': ('Amu  Darya', 'Panj'), 'Syr': ('Syr  Darya', 'Naryn'), 'Huang': ('Huang',), 'Volga': ('Volga',), 'Lena': ('Lena',), 'Ob': ('Ob',)}
RIV = {'Selenga', 'Yenisey', 'Verkhniy Yenisey', 'Malyy Yenisey', 'Irtysh', 'Ertis', 'Ertix', 'Amu  Darya', 'Panj', 'Syr  Darya', 'Naryn', 'Huang', 'Volga', 'Lena', 'Ob',
       'Angara', 'Ural', 'Tarim', 'Don', 'Dnipro', 'Dnepre', 'Danube', 'Amur', 'Heilong Jiang', 'Argun’', 'Tobol', 'Kama', 'Ili', 'Aldan', 'Vilyuy', 'Tom’', 'Biya',
       'Songhua', 'Liao', 'Xiliao', 'Chang Jiang', 'Euphrates', 'Tigris', 'Firat', 'Dicle', 'Indus'}
CH = {  # 제3권 장 표지 도안: (중심 경도, 중심 위도, 반높이(도), 강조할 강, 덧그림)
 0: (90.0, 50.0, 27.0, None, None),        # 유라시아 전체(지도 도록)
 1: (100.0, 40.0, 14.0, None, 'wind'),     # 내륙 아시아, 몬순과 편서풍의 경계
 2: (104.0, 46.5, 9.0, 'Selenga', None),   # 몽골 고원
 3: (92.0, 56.0, 13.0, 'Yenisey', None),   # 알타이와 시베리아
 4: (75.0, 50.0, 14.0, 'Irtysh', None),    # 초원
 5: (64.0, 42.5, 9.5, 'Amu', 'waves'),     # 중앙아시아의 하천과 호수
 6: (70.0, 42.0, 22.0, None, 'rings'),     # 4.2ka 사건의 유라시아 비교
 7: (75.0, 40.0, 22.0, None, 'route2'),    # 기장과 밀의 이동(방향을 정하지 않음)
 8: (108.0, 42.0, 10.0, 'Huang', None),    # 유목과 농경의 경계
 9: (70.0, 48.0, 18.0, None, 'route2'),    # 사람의 이동(고대 DNA, 방향을 정하지 않음)
 10: (68.0, 44.0, 14.0, 'Syr', 'rings'),   # 부족 계보 서술의 시험
 11: (62.0, 49.0, 20.0, None, 'routew'),   # 기후와 민족 이동의 연쇄
 12: (80.0, 50.0, 24.0, None, 'rings'),    # 최근 천 년과 소빙기
 13: (90.0, 50.0, 27.0, None, 'focus'),    # 하나의 쟁점을 끝까지
}
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
        for (lo, la, rs) in ((128.08, 41.99, (5, 10, 16, 23, 31)), (130.87, 37.5, (3, 6, 10))):
            for r in rs:
                o.append(f'<circle cx="{X(lo):.1f}" cy="{Y(la):.1f}" r="{r}" fill="none" stroke="{P["ring"]}" stroke-opacity=".85" stroke-width=".4" stroke-dasharray="1.2 1"/>')
            o.append(f'<circle cx="{X(lo):.1f}" cy="{Y(la):.1f}" r="1.1" fill="{P["ring"]}"/>')
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
