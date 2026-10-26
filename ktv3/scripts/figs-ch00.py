# -*- coding: utf-8 -*-
"""0장 「유라시아 지도 도록」 그림 생성: fig/fig-ch00-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book3 에서):  python3 scripts/figs-ch00.py
자료: Natural Earth 10m (geodata/). 땅, 호수, 강, 지형 구역(geography_regions_polys), 도시(populated_places_simple).
지형 구역은 Natural Earth 가 개략적으로 그린 다각형이며 측정한 고도 자료가 아니다.
지명은 한글만 쓴다. 한글 표기는 NAMES 표에 있는 것(한국어 위키백과 항목 제목 또는 Natural Earth NAME_KO 속성으로 확인한 것)만 쓴다.
글자 위치는 Natural Earth 다각형(또는 점) 안이나 곁에 둔다. 위치 검사 결과는 ms/code/ch00/figs-ch00.log 에 남는다.
"""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import mapkit as K
import numpy as np
import geopandas as gpd
import shapely
import shapely.geometry
from shapely.geometry import box, Point
from shapely.ops import unary_union, nearest_points
from pyproj import Transformer, CRS
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D

FIGDIR = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p')
LOG = []
OUT = []

# ---------------------------------------------------------------- 색
EX = {
    'color': dict(mtn='#C8B08A', plat='#EADBB4', desert='#F3E3A5', lowl='#DDE7C8', rivw=1.0, lakeedge='#7D9BAA', seatxt='#2B5F80', rng='#6E5333', des='#8A6A1E', reg='#4F4A3A', riv='#2F6F9A', lake='#BBD4E0', ocean='#DCEAF1'),
    'bw': dict(mtn='#B0B0B0', plat='#DADADA', desert='#F4F4F4', lowl='#FFFFFF', rivw=1.0, lakeedge='#555555', seatxt='#111111', rng='#111111', des='#111111', reg='#111111', riv='#111111', lake='#BDBDBD', ocean='#F0F0F0'),
}
HATCH = {'mtn': '////', 'plat': '', 'desert': '....', 'lowl': ''}

# ---------------------------------------------------------------- 지명표 (한글 표기 근거)
# 근거 A: 한국어 위키백과 항목 제목(2026-10-26 WebSearch 결과 제목) / 근거 B: Natural Earth NAME_KO 속성
NAMES = {
    # 지형
    '몽골고원': 'A', '알타이산맥': 'A', '항가이산맥': 'A', '헹티산맥': 'A', '사얀산맥': 'A', '톈산산맥': 'A', '파미르고원': 'A',
    '우랄산맥': 'A', '캅카스산맥': 'A', '중앙시베리아고원': 'A', '서시베리아 평원': 'A', '타림 분지': 'A', '중가르 분지': 'A', '페르가나 분지': 'A',
    '고비 사막': 'A', '타클라마칸 사막': 'A', '키질쿰 사막': 'A', '카라쿰 사막': 'A',
    # 물
    '바이칼호': 'A', '발하시호': 'A', '이식쿨호': 'A', '아랄해': 'A', '카스피해': 'A', '흑해': 'A', '후브스굴호': 'A', '우브스호': 'A',
    '예니세이강': 'A', '오비강': 'A', '레나강': 'A', '이르티시강': 'A', '안가라강': 'A', '셀렝가강': 'A', '아무다리야강': 'A', '시르다리야강': 'A',
    '볼가강': 'A', '우랄강': 'A', '드니프로강': 'A', '다뉴브강': 'A',
    # 도시
    '울란바타르': 'A', '노보시비르스크': 'A', '이르쿠츠크': 'A', '크라스노야르스크': 'A', '옴스크': 'A', '바르나울': 'A', '알마티': 'A', '비슈케크': 'A',
    '타슈켄트': 'A', '사마르칸트': 'A', '두샨베': 'A', '우루무치': 'A', '카슈가르': 'A', '투루판': 'A', '아스트라한': 'A', '트빌리시': 'A', '오데사': 'A', '키이우': 'A',
    # 큰 구역
    '시베리아': 'A', '크림반도': 'B',
}
# Natural Earth 쪽 이름(영문, 위치를 얻는 열쇠)
CITYKEY = {'울란바타르': 'Ulaanbaatar', '노보시비르스크': 'Novosibirsk', '이르쿠츠크': 'Irkutsk', '크라스노야르스크': 'Krasnoyarsk', '옴스크': 'Omsk',
           '바르나울': 'Barnaul', '알마티': 'Almaty', '비슈케크': 'Bishkek', '타슈켄트': 'Tashkent', '사마르칸트': 'Samarkand', '두샨베': 'Dushanbe',
           '우루무치': 'Ürümqi', '카슈가르': 'Kashgar', '투루판': 'Turpan', '아스트라한': 'Astrakhan', '트빌리시': 'Tbilisi', '오데사': 'Odessa', '키이우': 'Kyiv'}
POLYKEY = {'몽골고원': 'MONGOLIAN PLATEAU', '알타이산맥': 'ALTAY MOUNTAINS', '항가이산맥': 'Hangayn Mts.', '헹티산맥': 'Hentiyn Mts.', '사얀산맥': ('Western Sayan Mts.', 'EASTERN SAYAN MTS.'),
           '톈산산맥': 'TIAN SHAN', '파미르고원': 'PAMIRS', '우랄산맥': 'URAL MOUNTAINS', '캅카스산맥': 'CAUCASUS MTS.', '중앙시베리아고원': 'CENTRAL SIBERIAN PLATEAU',
           '서시베리아 평원': 'WESTERN SIBERIAN PLAIN', '타림 분지': 'TARIM BASIN', '중가르 분지': 'Junggar Basin', '페르가나 분지': 'Fergana Valley',
           '고비 사막': 'GOBI DESERT', '타클라마칸 사막': 'TAKLIMAKAN DESERT', '키질쿰 사막': 'QIZILQUM DESERT', '카라쿰 사막': 'GARAGUM DESERT', '크림반도': 'CRIMEA'}
LAKEKEY = {'바이칼호': ('Lake Baikal',), '발하시호': ('Lake Balkhash',), '이식쿨호': ('Issyk-Kul',), '아랄해': ('North Aral Sea', 'South Aral Sea'),
           '후브스굴호': ('Khövsgöl Nuur',), '우브스호': ('Uvs Nuur',)}
RIVKEY = {'예니세이강': ('Yenisey', 'Verkhniy Yenisey', 'Malyy Yenisey'), '오비강': ('Ob',), '레나강': ('Lena',), '이르티시강': ('Irtysh', 'Ertis', 'Ertix'),
          '안가라강': ('Angara',), '셀렝가강': ('Selenga',), '아무다리야강': ('Amu  Darya', 'Panj'), '시르다리야강': ('Syr  Darya', 'Naryn'),
          '볼가강': ('Volga',), '우랄강': ('Ural',), '드니프로강': ('Dnipro', 'Dnepre'), '다뉴브강': ('Danube',)}
RIVDRAW = sorted({n for v in RIVKEY.values() for n in v} | {'Tarim', 'Don', 'Amur', 'Heilong Jiang', 'Argun’', 'Tobol', 'Kama', 'Ili', 'Aldan', 'Vilyuy', 'Tom’', 'Biya'})
SEEDS = {'카스피해': (51.0, 42.0), '흑해': (34.0, 43.0)}   # 바다 이름은 땅에서 뺀 물 다각형 안의 이 점으로 찾는다

CLASSES = [('lowl', ['Lowland', 'Plain', 'Basin', 'Valley', 'Tundra']), ('plat', ['Plateau', 'Geoarea']), ('desert', ['Desert']), ('mtn', ['Range/mtn'])]


# ---------------------------------------------------------------- 자료
_cache = {}


def layer(name, bb):
    key = (name, tuple(bb))
    if key not in _cache:
        g = K.read(name, bb)
        g.columns = [c.lower() if c != 'geometry' else c for c in g.columns]
        _cache[key] = g
    return _cache[key]


def lower_name(g):
    g = g.copy()
    g['nm'] = g['name'].astype(str)
    return g


def build_water(bb_read):
    land = K.fix(layer('ne_10m_land', bb_read))[0]
    lakes = K.fix(layer('ne_10m_lakes', bb_read))[0]
    cut = box(*bb_read)
    landu = unary_union(list(gpd.clip(land, cut).geometry))
    return landu, lakes


# ---------------------------------------------------------------- 그림 틀
def inscribed(bbox, crs, n=60):
    """경위도 상자에 완전히 들어 있는 가장 큰 투영 좌표 직사각형(X0, Y0, X1, Y1)."""
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    lo0, la0, lo1, la1 = bbox
    xs = np.linspace(lo0, lo1, n); ys = np.linspace(la0, la1, n)
    xl, _ = tr.transform(np.full(n, lo0), ys); xr, _ = tr.transform(np.full(n, lo1), ys)
    _, yb = tr.transform(xs, np.full(n, la0)); _, yt = tr.transform(xs, np.full(n, la1))
    return float(np.max(xl)), float(np.max(yb)), float(np.min(xr)), float(np.min(yt))


def place(ax, tr, x, y, s, size, dx, dy, ha, va, mode, color, bold=False, zorder=22, spacing=None):
    x0_, x1_ = ax.get_xlim(); y0_, y1_ = ax.get_ylim()
    if not (x0_ < x < x1_ and y0_ < y < y1_):
        OUT.append('지도 틀 밖에 놓인 글자: %s' % s)
    t = K.label(ax, x, y, s, size, color=color, bold=bold, dx=dx, dy=dy, ha=ha, va=va, mode=mode, zorder=zorder)
    return t


def build(spec, mode):
    P = K.PAL[mode]; E = EX[mode]
    K.use_font(8)
    crs = CRS.from_user_input(spec['proj'])
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    bbox = spec['bbox']
    pad = spec.get('pad', 14.0)
    bb = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
    cutbox = box(*bb)
    if spec.get('view'):
        X0, Y0, X1, Y1 = [v * 1000.0 for v in spec['view']]
        gbox = spec.get('gbox', bbox)
    else:
        X0, Y0, X1, Y1 = K.proj_bounds(bbox, crs)
        gbox = (bbox[0] - 12, bbox[1] - 6, bbox[2] + 12, bbox[3] + 6)
    LEG = spec.get('leg_mm', 15.0)
    W = 130.0
    Hm = W * (Y1 - Y0) / (X1 - X0) * 0.905 / 0.905
    axw = 0.895; left = 0.095
    plot_w_mm = W * axw
    plot_h_mm = plot_w_mm * (Y1 - Y0) / (X1 - X0)
    H = plot_h_mm + LEG + 6.0
    fig = K.mm_fig(W, H)
    ax = fig.add_axes([left, (LEG + 4.5) / H, axw, plot_h_mm / H])
    ax.set_facecolor(E['ocean'])
    # 지형 구역 다각형
    reg = layer('ne_10m_geography_regions_polys', bb)
    reg = reg.copy(); reg['nm'] = reg['name'].astype(str)
    for cname, fcs in CLASSES:
        sub = reg[reg['featurecla'].isin(fcs)]
        if cname == 'plat':
            sub = sub[~sub['nm'].str.upper().isin(['SIBERIA', 'ANATOLIA', 'MESOPOTAMIA', 'LAPLAND', 'KARELIA', 'BALUCHISTAN', 'PUNJAB', 'FINNISH LAKE REGION', 'HEXI CORRIDOR'])]
        if cname == 'lowl':
            sub = sub[~sub['nm'].str.upper().isin(['VYCHEGDA LOWLAND', 'BOL’SHEZEMEL’SKAYA TUNDRA', 'BALTIC PLAINS', 'NORTHERN EUROPEAN PLAIN', 'NORTH CHINA PLAIN', 'MANCHURIAN PLAIN', 'GANGES PLAIN', 'HASA PLAIN', 'SICHUAN BASIN', 'QAIDAM BASIN'])] if False else sub
        if len(sub) == 0:
            continue
        g = gpd.clip(K.fix(sub)[0], cutbox)
        g = g[~g.is_empty]
        if len(g):
            g.to_crs(crs).plot(ax=ax, facecolor=E[cname], edgecolor='none', linewidth=0, zorder=2 + CLASSES.index((cname, fcs)),
                               hatch=HATCH[cname] or None, alpha=1.0 if mode == 'bw' else 0.95)
    # 땅, 윤곽선
    land = gpd.clip(K.fix(layer('ne_10m_land', bb))[0], cutbox)
    isl = gpd.clip(layer('ne_10m_minor_islands', bb), cutbox)
    landu = unary_union(list(land.geometry))
    sea = cutbox.difference(landu)
    land.to_crs(crs).plot(ax=ax, facecolor=P['land'], edgecolor='none', zorder=1)
    land.to_crs(crs).plot(ax=ax, facecolor='none', edgecolor=P['coast'], linewidth=0.5, zorder=8)
    isl.to_crs(crs).plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.3, zorder=8)
    lakes = gpd.clip(K.fix(layer('ne_10m_lakes', bb))[0], cutbox)
    lakes = lakes[lakes.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]
    lakes.to_crs(crs).plot(ax=ax, facecolor=E['lake'], edgecolor=P['coast'], linewidth=0.35, zorder=9)
    # 강
    riv = layer('ne_10m_rivers_lake_centerlines', bb)
    riv = riv[riv['name'].isin(RIVDRAW)]
    riv_c = gpd.clip(riv, cutbox)
    riv_c.to_crs(crs).plot(ax=ax, color=E['riv'], linewidth=spec.get('rivw', 0.8), zorder=10)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal')
    ax.set_xlabel(''); ax.set_ylabel('')
    K.graticule(ax, gbox, crs, spec['grid'], mode)
    for ln in ax.lines:
        ln.set_zorder(11)
    K.edge_ticks(ax, gbox, crs, spec['grid'], mode)
    if spec.get('inlat'):
        for la in range(int(math.ceil(gbox[1] / 10.0) * 10), int(gbox[3]) + 1, 10):
            x, y = tr.transform(spec['inlat'], la)
            if X0 < x < X1 and Y0 < y < Y1:
                K.label(ax, x, y, '%d°N' % la, 8, color=P['soft'], ha='center', va='center', mode=mode, zorder=12)
    # 도시
    pp = layer('ne_10m_populated_places_simple', bb)
    chk = []
    for ko, (dx, dy, ha) in spec.get('cities', {}).items():
        assert NAMES.get(ko), ko
        r = pp[pp['name'] == CITYKEY[ko]]
        assert len(r) == 1, (ko, len(r))
        r = r.iloc[0]
        x, y = tr.transform(r.longitude, r.latitude)
        ax.plot(x, y, 'o', ms=3.4, mfc=P['text'], mec='#FFFFFF', mew=0.6, zorder=15)
        place(ax, tr, x, y, ko, 8, dx, dy, ha, 'bottom', mode, P['text'])
        chk.append((ko, 'city', round(float(r.longitude), 2), round(float(r.latitude), 2), 'NE 점'))
    # 지형 이름: 다각형 안의 점
    regs = reg.set_index('nm')
    for ko, v in spec.get('regions', {}).items():
        assert NAMES.get(ko), ko
        key = POLYKEY[ko]
        keys = key if isinstance(key, tuple) else (key,)
        rows = reg[reg['nm'].str.upper().isin([k.upper() for k in keys])]
        assert len(rows), (ko, key)
        geom = unary_union(list(rows.geometry))
        ll = v.get('lonlat')
        if v.get('lat'):
            sl = geom.intersection(shapely.geometry.LineString([(-180, v['lat']), (180, v['lat'])]))
            c = sl.bounds
            ll = ((c[0] + c[2]) / 2, v['lat'])
        pt = Point(ll) if ll else geom.representative_point()
        inside = geom.buffer(v.get('tol', 0.0)).contains(pt)
        chk.append((ko, 'region', round(pt.x, 2), round(pt.y, 2), 'NE 다각형 안' if inside else '다각형 밖(!)'))
        x, y = tr.transform(pt.x, pt.y)
        kind = rows.iloc[0]['featurecla']
        col = E['rng'] if kind == 'Range/mtn' else (E['des'] if kind == 'Desert' else E['reg'])
        t = place(ax, tr, x, y, ko, 8, v.get('dx', 0), v.get('dy', 0), v.get('ha', 'center'), 'center', mode, col, bold=(kind != 'Range/mtn'), zorder=18)
        if v.get('rot'):
            t.set_rotation(v['rot'])
    # 호수, 바다 이름
    for ko, v in spec.get('waters', {}).items():
        assert NAMES.get(ko), ko
        if ko in SEEDS:
            seed = Point(SEEDS[ko])
            parts = list(sea.geoms) if hasattr(sea, 'geoms') else [sea]
            hit = [p for p in parts if p.contains(seed)]
            assert hit, ko
            pt = Point(v['lonlat']) if v.get('lonlat') else seed
            src = 'NE 땅에서 뺀 물 다각형 안'
            inside = hit[0].contains(pt)
        else:
            rows = lakes_all(bb, LAKEKEY[ko])
            geom = unary_union(list(rows.geometry))
            pt = Point(v['lonlat']) if v.get('lonlat') else geom.representative_point()
            src = 'NE 호수 다각형 안'
            inside = geom.buffer(v.get('tol', 0.0)).contains(pt)
        chk.append((ko, 'water', round(pt.x, 2), round(pt.y, 2), src if inside else '다각형 밖(곁에 둠)'))
        x, y = tr.transform(pt.x, pt.y)
        place(ax, tr, x, y, ko, 8, v.get('dx', 0), v.get('dy', 0), v.get('ha', 'center'), 'center', mode, E['seatxt'], bold=True, zorder=19)
    # 강 이름: 힌트 좌표에서 가장 가까운 강 위의 점
    for ko, v in spec.get('rivers', {}).items():
        assert NAMES.get(ko), ko
        rows = riv[riv['name'].isin(RIVKEY[ko])]
        line = unary_union(list(rows.geometry))
        a, _ = nearest_points(line, Point(v['hint']))
        dist = Point(v['hint']).distance(a)
        chk.append((ko, 'river', round(a.x, 2), round(a.y, 2), 'NE 강 중심선 위(힌트와 %.1f도)' % dist))
        x, y = tr.transform(a.x, a.y)
        t = place(ax, tr, x, y, ko, 8, v.get('dx', 0), v.get('dy', 0), v.get('ha', 'center'), 'center', mode, E['riv'] if mode == 'color' else '#111111', zorder=17)
        if v.get('rot'):
            t.set_rotation(v['rot'])
    # 축척 막대, 북쪽 화살표
    K.scalebar(ax, spec['scale_km'], x_frac=spec.get('sb', (0.04, 0.05))[0], y_frac=spec.get('sb', (0.04, 0.05))[1], mode=mode)
    K.north_arrow(ax, x_frac=spec.get('na', (0.94, 0.86))[0], y_frac=spec.get('na', (0.94, 0.86))[1], mode=mode)
    for s in ax.spines.values():
        s.set_color(P['frame']); s.set_linewidth(0.6)
    # 범례
    lax = fig.add_axes([0.0, 0.0, 1.0, (LEG + 2.0) / H]); lax.axis('off')
    hs = [Patch(fc=E['mtn'], ec=P['frame'], lw=0.4, hatch=HATCH['mtn'], label='산맥·고원 구역'),
          Patch(fc=E['plat'], ec=P['frame'], lw=0.4, label='고원·구릉 구역'),
          Patch(fc=E['desert'], ec=P['frame'], lw=0.4, hatch=HATCH['desert'], label='사막 구역'),
          Patch(fc=E['lowl'], ec=P['frame'], lw=0.4, label='저지·분지·평원 구역'),
          Patch(fc=E['lake'], ec=P['coast'], lw=0.4, label='호수·바다'),
          Line2D([0], [0], color=E['riv'], lw=1.0, label='강'),
          Line2D([0], [0], marker='o', color='none', mfc=P['text'], mec='#FFFFFF', ms=5, label='도시')]
    lax.legend(handles=hs, loc='center', ncol=4, frameon=False, fontsize=8, handlelength=1.8, columnspacing=1.0, labelspacing=0.45, handletextpad=0.5)
    ps = proj_note(spec, bbox)
    fig._chk = chk
    fig._info = dict(inscribed_km=((X1 - X0) / 1000, (Y1 - Y0) / 1000), H_mm=H)
    return fig, ax, lax


_lk = {}


def lakes_all(bb, names):
    g = layer('ne_10m_lakes', bb)
    return g[g['name'].isin(names)]


def proj_note(spec, bbox):
    return spec['proj']


# ---------------------------------------------------------------- 지도 사양
AEA = '+proj=aea +lat_1=%g +lat_2=%g +lat_0=%g +lon_0=%g +datum=WGS84 +units=m +no_defs'
LAEA = '+proj=laea +lat_0=%g +lon_0=%g +datum=WGS84 +units=m +no_defs'

SPECS = {
    'eurasia': dict(
        title='유라시아 개관', bbox=(10, 20, 170, 82), proj=AEA % (38, 68, 52, 82), grid=10, scale_km=2000, pad=10, view=(-4300, -2000, 3800, 3000), gbox=(5, 15, 175, 85), inlat=132,
        sb=(0.04, 0.05), na=(0.96, 0.14), rivw=0.7, leg_mm=13.0,
        regions={
            '몽골고원': dict(lonlat=(110, 47.0), dx=6, dy=-6), '중앙시베리아고원': dict(lonlat=(104, 65.0)), '서시베리아 평원': dict(lonlat=(77, 58.5)),
            '타림 분지': dict(lonlat=(83, 38.5)), '고비 사막': dict(lonlat=(105, 41.6), dy=-3), '키질쿰 사막': dict(lonlat=(63.5, 42.0), dy=2),
            '알타이산맥': dict(lonlat=(90, 49.0), rot=-20), '톈산산맥': dict(lonlat=(87, 42.6), rot=10, dy=-3),
            '우랄산맥': dict(lat=57.0, rot=70),
        },
        waters={'바이칼호': dict(lonlat=(108, 53.5), dx=8, ha='left'), '발하시호': dict(dy=3), '아랄해': dict(dy=-8), '카스피해': dict(), '흑해': dict(lonlat=(33, 43.3))},
        rivers={'예니세이강': dict(hint=(87, 66), dx=-3, ha='right'), '오비강': dict(hint=(70, 61), dx=3, ha='left'), '레나강': dict(hint=(122, 66), dx=4, ha='left'),
                '볼가강': dict(hint=(47, 54), dx=-3, ha='right')},
        cities={'울란바타르': (4, 1, 'left'), '노보시비르스크': (4, 2, 'left'), '알마티': (-4, -9, 'right')},
    ),
    'mongolia': dict(
        title='몽골 고원', bbox=(90, 41, 121, 54), proj=AEA % (42, 55, 48, 105), grid=4, scale_km=500, pad=8, sb=(0.04, 0.05), na=(0.95, 0.86), leg_mm=13.0,
        regions={'몽골고원': dict(lonlat=(113.5, 47.6)), '항가이산맥': dict(rot=0), '헹티산맥': dict(), '알타이산맥': dict(lonlat=(93.5, 46.5), rot=-30),
                 '사얀산맥': dict(lonlat=(97.1, 53.5)), '고비 사막': dict(lonlat=(105, 43.3))},
        waters={'바이칼호': dict(dx=6, ha='left'), '후브스굴호': dict(dx=-6, ha='right'), '우브스호': dict(dy=-9)},
        rivers={'셀렝가강': dict(hint=(106, 49.5), dx=4, ha='left')},
        cities={'울란바타르': (4, -9, 'left'), '이르쿠츠크': (4, 1, 'left')},
    ),
    'siberia': dict(
        title='알타이와 시베리아', bbox=(66, 48, 118, 68), proj=AEA % (50, 66, 58, 94), grid=8, scale_km=1000, pad=10, sb=(0.04, 0.05), na=(0.95, 0.86), leg_mm=13.0,
        regions={'서시베리아 평원': dict(lonlat=(76, 60)), '중앙시베리아고원': dict(lonlat=(104, 64)), '알타이산맥': dict(lonlat=(88, 49.6), rot=-20),
                 '사얀산맥': dict(lonlat=(97.1, 53.5)), '우랄산맥': dict(lat=62.0, rot=75)},
        waters={'바이칼호': dict(dx=7, ha='left')},
        rivers={'오비강': dict(hint=(68, 62.8), dx=3, ha='left'), '이르티시강': dict(hint=(72, 57.3), dy=-9), '예니세이강': dict(hint=(88, 67), dx=-3, ha='right'),
                '안가라강': dict(hint=(102, 58), dx=3, ha='left'), '레나강': dict(hint=(112, 62), dx=3, ha='left')},
        cities={'노보시비르스크': (-4, 2, 'right'), '바르나울': (-4, -9, 'right'), '크라스노야르스크': (-4, 2, 'right'), '이르쿠츠크': (4, -9, 'left'), '옴스크': (-4, 2, 'right')},
    ),
    'central': dict(
        title='중앙아시아', bbox=(54, 36, 90, 49), proj=AEA % (37, 49, 43, 68), grid=4, scale_km=500, pad=8, sb=(0.04, 0.05), na=(0.05, 0.82), leg_mm=13.0,
        regions={'톈산산맥': dict(lonlat=(80, 42.2), rot=15), '파미르고원': dict(), '키질쿰 사막': dict(lonlat=(63.5, 42.0)), '카라쿰 사막': dict(lonlat=(58.5, 39.5)),
                 '타클라마칸 사막': dict(lonlat=(83, 38.8)), '중가르 분지': dict()},
        waters={'아랄해': dict(dy=-9), '발하시호': dict(dy=3), '이식쿨호': dict(dy=-9)},
        rivers={'아무다리야강': dict(hint=(62, 40.5), dx=3, dy=-4, ha='left'), '시르다리야강': dict(hint=(66, 44.5), dx=3, ha='left'), '이르티시강': dict(hint=(85, 47.5), dx=3, ha='left')},
        cities={'타슈켄트': (4, -9, 'left'), '사마르칸트': (-4, -9, 'right'), '알마티': (4, 2, 'left'), '비슈케크': (-4, 2, 'right'), '두샨베': (-4, -9, 'right'),
                '카슈가르': (4, 1, 'left'), '우루무치': (4, 2, 'left'), '투루판': (4, -9, 'left')},
    ),
    'caspian': dict(
        title='카스피해와 흑해', bbox=(28, 39, 58, 53), proj=AEA % (40, 54, 47, 44), grid=4, scale_km=500, pad=8, sb=(0.04, 0.05), na=(0.95, 0.86), leg_mm=13.0,
        regions={'캅카스산맥': dict(rot=-25, dy=7), '크림반도': dict(dx=9, dy=0, ha='left')},
        waters={'카스피해': dict(), '흑해': dict()},
        rivers={'볼가강': dict(hint=(46.5, 50.5), dx=4, ha='left'), '우랄강': dict(hint=(53, 50.5), dy=-9), '드니프로강': dict(hint=(32.5, 49.8), dx=-3, ha='right'),
                '다뉴브강': dict(hint=(27.5, 45.0), dy=3)},
        cities={'아스트라한': (4, 2, 'left'), '트빌리시': (4, -9, 'left'), '오데사': (4, -9, 'left'), '키이우': (4, 2, 'left')},
    ),
}



# ---------------------------------------------------------------- 장별 안내 지도 (작은 지도 13장)
GUIDE = [  # (장, 짧은 이름, [상자(경도 최소, 위도 최소, 경도 최대, 위도 최대)], 전체 표시 여부)
    (1, '몬순·편서풍 경계', [(80, 32, 125, 50)], False),
    (2, '몽골 고원', [(87, 41, 120, 52)], False),
    (3, '알타이·시베리아', [(82, 44, 101, 53), (60, 53, 130, 70)], False),
    (4, '초원의 식생', [(30, 43, 125, 56)], False),
    (5, '중앙아시아의 물', [(50, 36, 90, 50)], False),
    (6, '4.2ka 비교', [(5, 30, 35, 46), (35, 28, 60, 42), (55, 36, 85, 50), (100, 20, 125, 45)], False),
    (7, '기장과 밀', [(30, 28, 125, 50)], False),
    (8, '유목·농경 경계', [(80, 36, 125, 48)], False),
    (9, '고대 DNA와 이동', [(30, 36, 125, 58)], False),
    (10, '계보 서술 시험', [(48, 36, 125, 56)], False),
    (11, '기후와 이동의 연쇄', [(15, 42, 125, 56)], False),
    (12, '소빙기', [], True),
    (13, '한 쟁점', [], True),
]


def build_guide(mode):
    P = K.PAL[mode]; E = EX[mode]
    K.use_font(8)
    crs = CRS.from_user_input(AEA % (38, 68, 52, 82))
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    bb = (-20, 10, 200, 88)
    cut = box(*bb)
    land = gpd.clip(K.fix(K.read('ne_50m_land', bb))[0], cut).to_crs(crs)
    lakes = layer('ne_10m_lakes', bb)
    lakes['a'] = lakes.geometry.to_crs(6933).area / 1e6
    lakes = gpd.clip(K.fix(lakes[lakes['a'] > 4000])[0], cut)
    lakes = lakes[lakes.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])].to_crs(crs)
    VX0, VY0, VX1, VY1 = -5600e3, -3000e3, 3800e3, 2900e3
    W = 130.0
    cols, rows = 3, 5
    gx, gy = 2.0, 1.5
    cw = (W - 2 * 1.0 - gx * (cols - 1)) / cols
    mh = cw * (VY1 - VY0) / (VX1 - VX0)
    th = 4.2
    ch = mh + th
    H = rows * ch + (rows - 1) * gy + 2 * 1.0
    fig = K.mm_fig(W, H)
    hot = P['hot'] if mode == 'color' else '#111111'
    for i in range(15):
        r, c = divmod(i, cols)
        x0 = 1.0 + c * (cw + gx)
        y0 = H - 1.0 - (r + 1) * ch - r * gy
        if i < 13:
            n, name, boxes, allr = GUIDE[i]
            ax = fig.add_axes([x0 / W, y0 / H, cw / W, mh / H])
            ax.set_facecolor(E['ocean'] if mode == 'color' else '#D9D9D9')
            land.plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.25, zorder=2)
            lakes.plot(ax=ax, facecolor=E['lake'], edgecolor=P['coast'], linewidth=0.2, zorder=3)
            if allr:
                ax.add_patch(Rectangle((VX0, VY0), VX1 - VX0, VY1 - VY0, fc=hot, ec='none', alpha=0.18 if mode == 'color' else 0.12, zorder=4,
                                       hatch=None))
            for (a, b, c2, d) in boxes:
                lon = np.concatenate([np.linspace(a, c2, 40), np.full(40, c2), np.linspace(c2, a, 40), np.full(40, a)])
                lat = np.concatenate([np.full(40, b), np.linspace(b, d, 40), np.full(40, d), np.linspace(d, b, 40)])
                x, y = tr.transform(lon, lat)
                ax.fill(x, y, fc=hot, ec=hot, alpha=0.30 if mode == 'color' else 0.22, lw=0, zorder=5)
                ax.plot(x, y, color=hot, lw=0.9, zorder=6, ls='-' if mode == 'color' else '-')
            ax.set_xlim(VX0, VX1); ax.set_ylim(VY0, VY1); ax.set_aspect('equal')
            ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
            for sp in ax.spines.values():
                sp.set_linewidth(0.5); sp.set_color(P['frame'])
            fig.text((x0 + 0.5) / W, (y0 + mh + 0.8) / H, '%d장 %s' % (n, name), fontsize=8, ha='left', va='bottom', color=P['text'], fontweight='bold')
        elif i == 13:
            ax = fig.add_axes([x0 / W, y0 / H, cw / W, ch / H]); ax.axis('off')
            ax.add_patch(Rectangle((0.02, 0.62), 0.16, 0.24, transform=ax.transAxes, fc=hot, ec=hot, alpha=0.30, lw=0.9))
            ax.text(0.24, 0.74, '이 장이 다루는 곳', transform=ax.transAxes, fontsize=8, va='center', color=P['text'])
            ax.add_patch(Rectangle((0.02, 0.22), 0.16, 0.24, transform=ax.transAxes, fc=hot, ec='none', alpha=0.18))
            ax.text(0.24, 0.34, '유라시아 전체', transform=ax.transAxes, fontsize=8, va='center', color=P['text'])
        else:
            ax = fig.add_axes([x0 / W, y0 / H, cw / W, ch / H]); ax.axis('off')
            ax.text(0.0, 0.5, '상자는 목차안 v1의\n개략 범위이다.\n집필 뒤 달라질 수 있다.', transform=ax.transAxes, fontsize=8, va='center', color=P['text'], linespacing=1.4)
    fig._chk = []
    fig._info = dict(H_mm=H)
    return fig, None, None


def save(fig, name, mode):
    p = os.path.join(FIGDIR, 'fig-ch00-%s-v1-%s.svg' % (name, mode))
    fig.savefig(p, format='svg')
    fig.savefig(os.path.join(PREV, 'fig-ch00-%s-v1-%s.png' % (name, mode)), dpi=170)
    return p


def run(names=None):
    os.makedirs(FIGDIR, exist_ok=True); os.makedirs(PREV, exist_ok=True)
    allnames = list(SPECS) + ['guide']
    for name in allnames:
        if names and name not in names:
            continue
        for mode in ('color', 'bw'):
            OUT.clear()
            fig, ax, lax = build_guide(mode) if name == 'guide' else build(SPECS[name], mode)
            warn, nt = K.label_audit(fig)
            warn = warn + list(OUT)
            p = save(fig, name, mode)
            LOG.append('%s %s 글자 %d개, 경고 %d건, 높이 %.1f mm' % (name, mode, nt, len(warn), fig._info['H_mm']))
            for w in warn:
                LOG.append('  경고: ' + w)
            if mode == 'color':
                for c in fig._chk:
                    LOG.append('  위치 %s' % ' | '.join(str(x) for x in c))
            plt.close(fig)
    print('\n'.join(LOG))


if __name__ == '__main__':
    run(sys.argv[1:] or None)
