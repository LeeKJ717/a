# -*- coding: utf-8 -*-
"""geomap v1 - 책에 넣을 지도 엔진 (geo.md 방식)
- 해안선·강·산은 Natural Earth 실좌표 (퍼블릭 도메인). 손으로 찍지 않는다.
- 1단위 = 0.1mm. 캔버스 폭 = 인쇄 mm x 10. B5 본문 폭 130mm.
- 위도 보정(가운데 위도의 코사인), 자르기·간략화(shapely), 인셋, 축척 막대, 방위표, 격자.
- 글자 겹침·넘침·크기·인셋 가림을 자동 검사한다.
"""
import json, math, os
from shapely.geometry import shape, box, Point
from shapely.ops import nearest_points

GEO = os.environ.get('GEODIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'geodata'))
MAXW_MM, MAXH_MM = 130.0, 185.0          # B5, 좌측 여백 20% 뒤 본문 폭 / 그림 최대 높이
FS, FS_S, FS_I, FS_T = 33, 29, 29, 40    # 큰 지명 9.4pt / 보통 8.2pt / 인셋·주석 8.2pt / 제목
FONT = "'Noto Sans CJK KR','Malgun Gothic',sans-serif"

PAL = {
    'color': dict(ocean='#D9E6EC', land='#F1EBDD', coast='#7D7255', river='#3A7CA5', lake='#BBD4E0',
                  grid='#B3C3CB', text='#1B2A33', soft='#5F7F93', hot='#9C4F2E', site='#8A6A2C',
                  frame='#6B7A82', inset_land='#E2D9C2', inset_sea='#FFFFFF', halo='#FFFFFF', rng='#B89B62', rngo='0.45', rngt='#6E5726'),
    'bw': dict(ocean='#E4E4E4', land='#FFFFFF', coast='#4A4A4A', river='#1F1F1F', lake='#C8C8C8',
               grid='#B5B5B5', text='#111111', soft='#555555', hot='#111111', site='#111111',
               frame='#555555', inset_land='#D6D6D6', inset_sea='#FFFFFF', halo='#FFFFFF', rng='#8C8C8C', rngo='0.5', rngt='#222222'),
}

_cache = {}


def layer(name):
    if name not in _cache:
        d = json.load(open(os.path.join(GEO, name + '.geojson'), encoding='utf-8'))
        _cache[name] = [(shape(f['geometry']), f['properties']) for f in d['features'] if f.get('geometry')]
    return _cache[name]


def tw(s, size, spacing=0.0):
    """글자 폭 추정(한글 1.0, 영문·숫자 0.58, 좁은 기호 0.32)."""
    w = 0.0
    for ch in s:
        if ch in ' ij.,·()[]:;°/-':
            w += 0.32 * size
        elif ord(ch) < 128:
            w += 0.58 * size
        else:
            w += 1.0 * size
        w += spacing
    return w


class Proj:
    def __init__(self, bbox, w):
        self.lo0, self.la0, self.lo1, self.la1 = bbox
        self.bbox = bbox
        self.cos = math.cos(math.radians((self.la0 + self.la1) / 2.0))
        self.k = w / ((self.lo1 - self.lo0) * self.cos)       # 위도 1도당 단위
        self.w = w
        self.h = (self.la1 - self.la0) * self.k

    def __call__(self, lon, lat):
        return ((lon - self.lo0) * self.cos * self.k, (self.la1 - lat) * self.k)

    def km(self, km):
        return km / 111.32 * self.k


def fit(bbox, pad=0.0):
    lo0, la0, lo1, la1 = bbox
    cosm = math.cos(math.radians((la0 + la1) / 2))
    asp = (la1 - la0) / ((lo1 - lo0) * cosm)
    wmm = min(MAXW_MM, (MAXH_MM - pad / 10.0) / asp)
    return wmm * 10.0


def f1(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


class Fig:
    def __init__(self, w, h, mode='color'):
        self.w, self.h, self.mode = w, h, mode
        self.P = PAL[mode]
        self.parts = []
        self.texts = []      # (x0,y0,x1,y1,s,size)
        self.blocks = []     # 인셋 등 글자를 가리는 사각형
        self.warn = []

    # ---- 기본 도형 ----
    def raw(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill='none', stroke='none', sw=1.0, extra=''):
        self.raw('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>'
                 % (f1(x), f1(y), f1(w), f1(h), fill, stroke, sw, extra))

    def line(self, x1, y1, x2, y2, stroke, sw=1.5, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.raw('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>'
                 % (f1(x1), f1(y1), f1(x2), f1(y2), stroke, sw, d))

    def poly(self, pts, fill='none', stroke='none', sw=1.0):
        self.raw('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>'
                 % (' '.join('%s,%s' % (f1(x), f1(y)) for x, y in pts), fill, stroke, sw))

    def circle(self, x, y, r, fill='none', stroke='none', sw=1.0):
        self.raw('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
                 % (f1(x), f1(y), f1(r), fill, stroke, sw))

    def text(self, x, y, s, size=FS_S, anchor='start', fill=None, weight=400, halo=True, spacing=0.0, italic=False):
        fill = fill or self.P['text']
        if size < 28.3:
            self.warn.append('글자 8pt 미만: %s (%s)' % (s, size))
        w = tw(s, size, spacing)
        x0 = x if anchor == 'start' else (x - w if anchor == 'end' else x - w / 2)
        self.texts.append((x0, y - size * 0.88, x0 + w, y + size * 0.22, s, size))
        sp = ' letter-spacing="%s"' % spacing if spacing else ''
        it = ' font-style="italic"' if italic else ''
        base = ('x="%s" y="%s" font-size="%s" font-weight="%s" text-anchor="%s" font-family="%s"%s%s'
                % (f1(x), f1(y), size, weight, anchor, FONT, sp, it))
        if halo:   # 흰 테두리 글자: 흰 복사본을 먼저 깐다(렌더러 무관)
            self.raw('<text %s fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" opacity="0.9">%s</text>'
                     % (base, self.P['halo'], f1(size * 0.28), s))
        self.raw('<text %s fill="%s">%s</text>' % (base, fill, s))

    # ---- 표지 ----
    def marker(self, x, y, kind='dot', size=1.0, fill=None, stroke=None):
        P = self.P
        fill = fill or P['text']
        stroke = stroke or '#FFFFFF'
        if kind == 'dot':
            self.circle(x, y, 7.5 * size, fill, stroke, 2.0)
        elif kind == 'sq':
            r = 7.5 * size
            self.rect(x - r, y - r, 2 * r, 2 * r, fill, stroke, 2.0)
        elif kind == 'tri':      # 화산·산
            r = 12 * size
            self.poly([(x, y - r), (x + r * 0.95, y + r * 0.7), (x - r * 0.95, y + r * 0.7)], fill, stroke, 2.0)
        elif kind == 'star':
            r1, r2 = 14 * size, 6 * size
            pts = []
            for i in range(10):
                a = -math.pi / 2 + i * math.pi / 5
                r = r1 if i % 2 == 0 else r2
                pts.append((x + r * math.cos(a), y + r * math.sin(a)))
            self.poly(pts, fill, stroke, 2.0)
        elif kind == 'dia':
            r = 10 * size
            self.poly([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill, stroke, 2.0)

    def save(self, path, note=None):
        # 검사
        T = self.texts
        for i in range(len(T)):
            a = T[i]
            if a[0] < 0 or a[1] < 0 or a[2] > self.w or a[3] > self.h:
                self.warn.append('글자 넘침: %s' % a[4])
            for b in T[i + 1:]:
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 0 and oy > 0:
                    sm = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                    if ox * oy / sm > 0.06:
                        self.warn.append('글자 겹침: %s / %s' % (a[4], b[4]))
            for blk in self.blocks:
                if blk[4] <= i < blk[5]:
                    continue          # 인셋 자신의 글자는 검사에서 뺀다
                ox = min(a[2], blk[2]) - max(a[0], blk[0])
                oy = min(a[3], blk[3]) - max(a[1], blk[1])
                if ox > 0 and oy > 0:
                    self.warn.append('인셋·상자가 글자를 가림: %s' % a[4])
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">'
                % (f1(self.w), f1(self.h), f1(self.w), f1(self.h)))
        body = '\n'.join(self.parts)
        open(path, 'w', encoding='utf-8').write(head + '\n' + body + '\n</svg>\n')
        return self.warn


# ---------------------------------------------------------------- 지도 그리기
def _ring_d(coords, pr):
    pts = [pr(x, y) for x, y in coords]
    return 'M' + ' L'.join('%s,%s' % (f1(x), f1(y)) for x, y in pts) + ' Z'


def _poly_d(g, pr):
    out = []
    geoms = g.geoms if hasattr(g, 'geoms') else [g]
    for p in geoms:
        if p.geom_type != 'Polygon' or p.is_empty:
            continue
        out.append(_ring_d(p.exterior.coords, pr))
        for r in p.interiors:
            out.append(_ring_d(r.coords, pr))
    return ' '.join(out)


def _line_d(g, pr):
    out = []
    geoms = g.geoms if hasattr(g, 'geoms') else [g]
    for l in geoms:
        if l.geom_type != 'LineString' or l.is_empty:
            continue
        pts = [pr(x, y) for x, y in l.coords]
        out.append('M' + ' L'.join('%s,%s' % (f1(x), f1(y)) for x, y in pts))
    return ' '.join(out)


def _clipped(names, bbox, pr, eps_units=0.7):
    lo0, la0, lo1, la1 = bbox
    cb = box(lo0 - 0.02, la0 - 0.02, lo1 + 0.02, la1 + 0.02)
    eps = eps_units / pr.k
    res = []
    for n in names:
        for g, _ in layer(n):
            if not g.intersects(cb):
                continue
            c = g.intersection(cb)
            if c.is_empty:
                continue
            res.append(c.simplify(eps, preserve_topology=True))
    return res


def basemap(bbox, pad=0.0, mode='color', rivers=(), lakes=False, grid=None, land_src=None, river_sw=3.2, latside='left', ranges=()):
    """지도 한 장의 바탕: 바다·육지·호수·강·격자. 반환 (Fig, Proj)."""
    w = fit(bbox, pad)
    pr = Proj(bbox, w)
    f = Fig(w, pr.h + pad, mode)
    P = f.P
    f.rect(0, 0, f.w, f.h, '#FFFFFF')
    f.rect(0, 0, pr.w, pr.h, P['ocean'])
    f.raw('<clipPath id="mc"><rect x="0" y="0" width="%s" height="%s"/></clipPath><g clip-path="url(#mc)">'
          % (f1(pr.w), f1(pr.h)))
    # 육지
    for c in _clipped(land_src or ('ne_10m_land', 'ne_10m_minor_islands'), bbox, pr):
        d = _poly_d(c, pr)
        if d:
            f.raw('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6" stroke-linejoin="round" fill-rule="evenodd"/>'
                  % (d, P['land'], P['coast']))
    if ranges:
        want = set(r.lower() for r in ranges)
        ld = []
        for c in _clipped(land_src or ('ne_10m_land', 'ne_10m_minor_islands'), bbox, pr):
            d = _poly_d(c, pr)
            if d:
                ld.append(d)
        f.raw('<clipPath id="lc"><path d="%s" clip-rule="evenodd"/></clipPath><g clip-path="url(#lc)">' % ' '.join(ld))
        cb = box(bbox[0], bbox[1], bbox[2], bbox[3])
        for g, pp in layer('ne_10m_geography_regions_polys'):
            if (pp.get('NAME') or '').lower() in want and g.intersects(cb):
                c = g.intersection(cb).simplify(0.7 / pr.k, preserve_topology=True)
                d = _poly_d(c, pr)
                if d:
                    f.raw('<path d="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="1.2" stroke-opacity="0.8" stroke-dasharray="10 6" fill-rule="evenodd"/>'
                          % (d, P['rng'], P['rngo'], P['rngt']))
        f.raw('</g>')
    if lakes:
        for c in _clipped(('ne_10m_lakes',), bbox, pr):
            d = _poly_d(c, pr)
            if d:
                f.raw('<path d="%s" fill="%s" stroke="%s" stroke-width="1.2" fill-rule="evenodd"/>'
                      % (d, P['lake'], P['coast']))
    # 격자
    if grid:
        lo0, la0, lo1, la1 = bbox
        g0 = math.ceil(lo0 / grid) * grid
        while g0 <= lo1 + 1e-9:
            x, _ = pr(g0, la0)
            f.line(x, 0, x, pr.h, P['grid'], 1.0, '8 8')
            g0 += grid
        g0 = math.ceil(la0 / grid) * grid
        while g0 <= la1 + 1e-9:
            _, y = pr(lo0, g0)
            f.line(0, y, pr.w, y, P['grid'], 1.0, '8 8')
            g0 += grid
    # 강
    if rivers:
        lo0, la0, lo1, la1 = bbox
        cb = box(lo0, la0, lo1, la1)
        eps = 0.5 / pr.k
        for g, pp in layer('ne_10m_rivers_lake_centerlines'):
            if pp.get('name') in rivers and g.intersects(cb):
                c = g.intersection(cb).simplify(eps)
                d = _line_d(c, pr)
                if d:
                    f.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>'
                          % (d, P['river'], river_sw))
    f.raw('</g>')
    f.rect(0, 0, pr.w, pr.h, 'none', P['frame'], 2.4)
    # 격자 눈금 글자(테두리 안쪽)
    if grid:
        lo0, la0, lo1, la1 = bbox
        g0 = math.ceil(lo0 / grid) * grid
        while g0 <= lo1 + 1e-9:
            x, _ = pr(g0, la0)
            if 120 < x < pr.w - 120:
                f.text(x, pr.h - 12, '%s°E' % f1(g0), FS_I, 'middle', P['soft'], 400)
            g0 += grid
        g0 = math.ceil(la0 / grid) * grid
        while g0 <= la1 + 1e-9:
            _, y = pr(lo0, g0)
            if 60 < y < pr.h - 60:
                if latside == 'left':
                    f.text(12, y - 8, '%s°N' % f1(g0), FS_I, 'start', P['soft'], 400)
                else:
                    f.text(pr.w - 12, y - 8, '%s°N' % f1(g0), FS_I, 'end', P['soft'], 400)
            g0 += grid
    return f, pr


def on_river(names, hint, bbox=None):
    """강 위에서 hint(경도,위도)에 가장 가까운 점 - 라벨을 강 곁에 정확히 두기 위해."""
    best, bd = None, 1e9
    pt = Point(hint)
    for g, pp in layer('ne_10m_rivers_lake_centerlines'):
        if pp.get('name') in names:
            a, _ = nearest_points(g, pt)
            d = a.distance(pt)
            if d < bd:
                best, bd = (a.x, a.y), d
    return best, bd


def city(f, pr, lon, lat, name, dx=12, dy=8, anchor='start', kind='dot', big=False, size=FS_S, weight=400, fill=None):
    x, y = pr(lon, lat)
    P = f.P
    f.marker(x, y, kind, 1.25 if big else 1.0, fill or (P['hot'] if big else P['text']))
    f.text(x + dx, y + dy, name, size, anchor, fill or P['text'], 700 if big else weight)


def area(f, pr, lon, lat, s, size=FS, fill=None, weight=700, spacing=6.0, anchor='middle', where=None):
    """지역·바다 이름. where='sea'|'land' 이면 그 좌표가 실제로 바다/육지인지 검사한다."""
    if where and not pt_check(lon, lat, where == 'land'):
        f.warn.append('이름 위치가 %s이 아님: %s (%.2f, %.2f)' % ('육지' if where == 'land' else '바다', s, lon, lat))
    x, y = pr(lon, lat)
    f.text(x, y, s, size, anchor, fill or f.P['soft'], weight, True, spacing)


def scalebar(f, pr, x, y, km, nseg=2):
    """(x,y)=막대 왼쪽 아래. 두 칸 흑백 교차 + 눈금 글자."""
    L = pr.km(km)
    P = f.P
    seg = L / nseg
    for i in range(nseg):
        f.rect(x + i * seg, y - 14, seg, 14, '#FFFFFF' if i % 2 else P['text'], P['text'], 1.4)
    f.text(x, y - 22, '0', FS_I, 'middle', P['text'], 400)
    f.text(x + L, y - 22, '%s km' % f1(km), FS_I, 'middle', P['text'], 400)


def north(f, x, y, h=80):
    P = f.P
    f.poly([(x, y), (x + h * 0.22, y + h), (x, y + h * 0.78), (x - h * 0.22, y + h)], P['text'], P['text'], 1.0)
    f.text(x, y - 8, 'N', FS_I, 'middle', P['text'], 700)


def inset(f, obox, dbox, x, y, w, marks=(), title=None):
    """전체 위치도(인셋). ne_50m_land. 본그림 범위는 붉은 네모."""
    P = f.P
    pr = Proj(obox, w)
    h = pr.h
    n0 = len(f.texts)
    if title and tw(title, FS_I) > w:
        f.warn.append('인셋 제목이 인셋보다 넓음: %s' % title)
    f.rect(x - 4, y - 4, w + 8, h + 8, P['inset_sea'], P['frame'], 2.0)
    f.rect(x, y, w, h, P['ocean'])
    ox = Proj(obox, w)
    sub = Fig(w, h, f.mode)
    f.raw('<g transform="translate(%s,%s)"><clipPath id="ic%d"><rect x="0" y="0" width="%s" height="%s"/></clipPath><g clip-path="url(#ic%d)">'
          % (f1(x), f1(y), int(x * 10 + y), f1(w), f1(h), int(x * 10 + y)))
    for c in _clipped(('ne_50m_land',), obox, ox, 0.6):
        d = _poly_d(c, ox)
        if d:
            f.raw('<path d="%s" fill="%s" stroke="%s" stroke-width="1.0" fill-rule="evenodd"/>' % (d, P['inset_land'], P['coast']))
    f.raw('</g>')
    lo0, la0, lo1, la1 = dbox
    x0, y0 = ox(lo0, la1)
    x1, y1 = ox(lo1, la0)
    red = '#C0392B' if f.mode == 'color' else '#000000'
    f.raw('<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
          % (f1(x0), f1(y0), f1(x1 - x0), f1(y1 - y0), red))
    f.raw('</g>')
    for lon, lat, nm, dx, dy, an in marks:
        mx, my = ox(lon, lat)
        f.text(x + mx + dx, y + my + dy, nm, FS_I, an, P['text'], 400)
    if title:
        f.text(x + w / 2, y + h + FS_I + 6, title, FS_I, 'middle', P['soft'], 700, False)
    f.blocks.append((x - 6, y - 6, x + w + 6, y + h + 6 + (FS_I + 12 if title else 0), n0, len(f.texts)))
    return h


def legend(f, x, y, items, gap=34, size=FS_S):
    """(x,y) 부터 가로로 항목을 늘어놓고, 폭을 넘으면 줄을 바꾼다. items=(kind,label)."""
    P = f.P
    cx, cy = x, y
    maxx = f.w - 20
    for kind, label in items:
        iw = 46 + tw(label, size)
        if cx + iw > maxx and cx > x:
            cx = x
            cy += size * 1.7
        if kind in ('dot', 'sq', 'tri', 'star', 'dia'):
            col = P['hot'] if kind in ('tri',) else (P['site'] if kind == 'star' else P['text'])
            f.marker(cx + 14, cy - size * 0.32, kind, 0.95, col)
        elif kind == 'river':
            f.line(cx, cy - size * 0.32, cx + 30, cy - size * 0.32, P['river'], 3.2)
        elif kind == 'range':
            f.raw('<rect x="%s" y="%s" width="30" height="18" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="1.2" stroke-dasharray="6 4"/>' % (f1(cx), f1(cy - size * 0.62), P['rng'], P['rngo'], P['rngt']))
        elif kind == 'coast':
            f.line(cx, cy - size * 0.32, cx + 30, cy - size * 0.32, P['coast'], 2.0)
        f.text(cx + 40, cy, label, size, 'start', P['text'], 400, False)
        cx += iw + gap
    return cy


def pt_check(lon, lat, expect_land=True, names=('ne_10m_land', 'ne_10m_minor_islands')):
    """좌표가 육지(또는 바다)에 있는지 확인 - 지명 좌표 검증용."""
    p = Point(lon, lat)
    inland = any(g.contains(p) for n in names for g, _ in layer(n))
    return inland == expect_land


def range_label(f, pr, bbox, ne_name, ko, pos=None, dx=0, dy=0, size=FS_I, spacing=3.0):
    """산맥 이름: Natural Earth 지역 폴리곤의 대표점(또는 pos=(경도,위도))에 이탤릭 갈색 글자."""
    if pos is None:
        cb = box(*bbox)
        for g, pp in layer('ne_10m_geography_regions_polys'):
            if (pp.get('NAME') or '').lower() == ne_name.lower():
                c = g.intersection(cb)
                if c.is_empty:
                    f.warn.append('산맥이 범위 밖: %s' % ne_name)
                    return
                p = c.representative_point()
                pos = (p.x, p.y)
                break
        if pos is None:
            f.warn.append('산맥 자료 없음: %s' % ne_name)
            return
    x, y = pr(*pos)
    f.text(x + dx, y + dy, ko, size, 'middle', f.P['rngt'], 700, True, spacing, True)


PEAKH = {}
for _g, _p in layer('ne_10m_geography_regions_elevation_points'):
    if _p.get('name') and _p.get('elevation'):
        PEAKH[_p['name']] = (_g.x, _g.y, int(_p['elevation']))


def peak(f, pr, key, ko, dx=14, dy=8, anchor='start', size=FS_S):
    """봉우리: 삼각 표지 + '이름 높이 m' (높이는 Natural Earth 표고점 자료)."""
    lon, lat, h = PEAKH[key]
    x, y = pr(lon, lat)
    f.marker(x, y, 'tri', 1.0, f.P['hot'])
    f.text(x + dx, y + dy, '%s %s m' % (ko, format(h, ',')), size, anchor, f.P['hot'], 700)
