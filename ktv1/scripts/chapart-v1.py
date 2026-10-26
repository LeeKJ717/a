#!/usr/bin/env python3
# 장 표지 그림 생성: fig/chapart-NN-{color,bw}.svg  (Natural Earth, 도안용 — 자료 그림이 아님)
import json, math, os
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
    if n not in _c: _c[n] = [shape(f['geometry']) for f in json.load(open(f'geodata/{n}.geojson'))['features']]
    return _c[n]
def props(n): return [f['properties'] for f in json.load(open(f'geodata/{n}.geojson'))['features']]
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
HI = {'Han': ('Han',), 'Huang': ('Huang',), 'Chang': ('Chang Jiang', 'Yangtze'), 'Liao': ('Liao', 'Xiliao')}
RIV = {'Huang', 'Chang Jiang', 'Yangtze', 'Liao', 'Xiliao', 'Han', 'Nakdong', 'Yalu', 'Tumen', 'Songhua', 'Amur', 'Huai', 'Xi', 'Xiang'}
CH = {  # 장: (중심 경도, 위도, 반높이(도), 강조 강, 덧그림)
 1: (122.0, 34.0, 9.5, None, None),
 2: (127.6, 36.3, 4.6, None, None),
 3: (134.0, 40.0, 9.0, None, None),
 4: (128.6, 40.8, 5.2, None, 'ash'),
 5: (127.0, 30.0, 11.0, None, 'wind'),
 6: (None, None, None, None, 'strata'),
 8: (108.0, 37.0, 6.5, 'Huang', None),
 9: (114.0, 36.5, 6.5, 'Huang', None),
 10: (112.0, 30.5, 8.5, 'Chang', None),
 11: (122.5, 43.0, 6.5, 'Liao', 'rings'),
 12: (127.8, 36.6, 4.4, 'Han', 'rings'),
 13: (135.5, 35.5, 7.5, None, 'rings'),
 14: (127.8, 37.5, 5.5, None, 'wind'),
 15: (127.8, 36.0, 6.0, None, 'waves'),
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
