# -*- coding: utf-8 -*-
"""mapkit v1 - 제2권 1장 실습 공용 도우미 (자료 읽기, 거리 계산, 글꼴, 지도 요소)
파일 이름에 밑줄을 쓰지 않으려고 이 모듈 이름은 mapkit 이다. 다른 실습 파일은 이 모듈을 불러 쓴다.
"""
import os, math, time
import numpy as np
import geopandas as gpd
from shapely.geometry import box, Point
from shapely import make_valid
from pyproj import Geod, Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))           # 제2권 작업 폴더(book2)
GEO = os.environ.get('GEODIR', os.path.join(ROOT, 'geodata'))           # 제1권이 쓴 Natural Earth 파일
DATA = os.environ.get('BATHYDIR', os.path.join(ROOT, 'data', 'ch01'))   # 이 장이 더 내려받은 수심 층
FIG = os.path.join(ROOT, 'fig')

R_MEAN = 6371.0088          # 지구 평균 반지름(km). 제1권 계산 11-13과 같은 값
GEOD = Geod(ellps='WGS84')  # WGS84 타원체 위의 측지선 계산(Karney 알고리즘)

BATHY = [(200, 'ne_10m_bathymetry_K_200'), (1000, 'ne_10m_bathymetry_J_1000'), (2000, 'ne_10m_bathymetry_I_2000'),
         (3000, 'ne_10m_bathymetry_H_3000'), (4000, 'ne_10m_bathymetry_G_4000'), (5000, 'ne_10m_bathymetry_F_5000')]

PAL = {
    'color': dict(ocean='#E3EEF3', land='#F1EBDD', coast='#7D7255', river='#2F6F9A', lake='#BBD4E0', text='#1B2A33',
                  soft='#4F6E80', hot='#9C4F2E', grid='#B3C3CB', frame='#6B7A82', halo='#FFFFFF',
                  bathy={200: '#C9DEE9', 1000: '#A5C6D9', 2000: '#7FADC7', 3000: '#5B93B3', 4000: '#3D7799', 5000: '#26597A'},
                  iso='#2B5F80'),
    'bw': dict(ocean='#EBEBEB', land='#FFFFFF', coast='#3C3C3C', river='#111111', lake='#D0D0D0', text='#111111',
               soft='#444444', hot='#111111', grid='#B5B5B5', frame='#555555', halo='#FFFFFF',
               bathy={200: '#D6D6D6', 1000: '#BEBEBE', 2000: '#A4A4A4', 3000: '#888888', 4000: '#6C6C6C', 5000: '#505050'},
               iso='#333333'),
}

FONT = 'Noto Sans CJK KR'


# ------------------------------------------------------------------ 글꼴
def use_font(size=8.0):
    """matplotlib 글꼴을 Noto Sans CJK KR 로 바꾼다. 없으면 오류를 낸다(조용히 다른 글꼴로 넘어가지 않게)."""
    names = {f.name for f in fm.fontManager.ttflist}
    if FONT not in names:
        raise RuntimeError('글꼴 %s 를 찾지 못했다. fc-list | grep -i noto 로 확인하라' % FONT)
    plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'svg.fonttype': 'path',
                         'font.size': size, 'axes.titlesize': size, 'axes.labelsize': size,
                         'xtick.labelsize': size, 'ytick.labelsize': size, 'legend.fontsize': size})
    return fm.findfont(FONT)


# ------------------------------------------------------------------ 자료 읽기
def path_of(name):
    for d in (GEO, DATA):
        p = os.path.join(d, name + '.geojson')
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def read(name, bbox=None):
    """GeoJSON 한 층을 GeoDataFrame 으로 읽는다. bbox=(경도 최소, 위도 최소, 경도 최대, 위도 최대)면 그 범위만."""
    return gpd.read_file(path_of(name), bbox=bbox)


def fix(gdf):
    """깨진(자기 교차) 도형을 shapely.make_valid 로 고친다. 고친 개수도 돌려준다."""
    bad = ~gdf.geometry.is_valid
    out = gdf.copy()
    if bad.any():
        out.loc[bad, 'geometry'] = out.loc[bad, 'geometry'].apply(make_valid)
    return out, int(bad.sum())


def clip_to(gdf, bbox):
    """경위도 상자 bbox 로 도형을 자른다(도형이 이미 올바른 것으로 가정)."""
    return gpd.clip(gdf, box(*bbox))


def bathy_layers(bbox, pad=0.5):
    """수심 층 6개를 bbox 범위에서 읽고 고쳐 자른다. 반환: {깊이(m): GeoDataFrame}, 고친 도형 수 합계."""
    bb = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
    out, nfix = {}, 0
    for d, nm in BATHY:
        g = read(nm, bb)
        if len(g) == 0:
            out[d] = g
            continue
        g, k = fix(g)
        nfix += k
        out[d] = gpd.clip(g, box(*bb))
    return out, nfix


# ------------------------------------------------------------------ 거리
def haversine(lon1, lat1, lon2, lat2, R=R_MEAN):
    """구면 위의 대원 거리(km). 지구를 반지름 R 의 공으로 본다."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def geodesic_km(lon1, lat1, lon2, lat2):
    """WGS84 타원체 위의 측지선 거리(km)."""
    _, _, d = GEOD.inv(lon1, lat1, lon2, lat2)
    return d / 1000.0


def projected_km(lon1, lat1, lon2, lat2, epsg):
    """경위도를 EPSG 투영 좌표로 바꾼 뒤 평면 직선 거리(km). 투영 거리는 투영 방법에 따라 늘거나 준다."""
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    x1, y1 = tr.transform(lon1, lat1)
    x2, y2 = tr.transform(lon2, lat2)
    return math.hypot(x2 - x1, y2 - y1) / 1000.0


def area_by_depth(bb, lay, epsg=6933):
    """상자 bb 안 바다를 깊이 구간으로 나눈 면적(km², 등적 투영 epsg 에서 shapely .area).
    lay 는 bathy_layers(bb, pad=0) 의 결과. 반환: (상자 면적, 땅 면적, 바다 면적, [(구간 이름, 면적, 바다 비율), ...])"""
    from shapely.ops import unary_union
    land = gpd.clip(read('ne_10m_land', bb), box(*bb))
    mi = gpd.clip(read('ne_10m_minor_islands', bb), box(*bb))
    landu = unary_union(list(land.geometry) + list(mi.geometry))
    sea = box(*bb).difference(landu)
    A = lambda g: gpd.GeoSeries([g], crs=4326).to_crs(epsg).area.iloc[0] / 1e6
    a_box, a_sea = A(box(*bb)), A(sea)
    deep = {d: (A(unary_union(list(g.geometry)).intersection(sea)) if len(g) else 0.0) for d, g in lay.items()}
    bounds = [0] + [d for d, _ in BATHY] + [None]
    out = []
    for i in range(len(bounds) - 1):
        lo, hi = bounds[i], bounds[i + 1]
        top = a_sea if lo == 0 else deep[lo]
        bot = deep[hi] if hi else 0.0
        name = ('0~%d m' % hi) if lo == 0 else (('%d~%d m' % (lo, hi)) if hi else '%d m 이상' % lo)
        out.append((name, top - bot, (top - bot) / a_sea))
    return a_box, a_box - a_sea, a_sea, out


def dms(d, m=0, s=0):
    return d + m / 60 + s / 3600


# ------------------------------------------------------------------ 그림 요소
def halo(w=2.0, color='#FFFFFF'):
    return [pe.withStroke(linewidth=w, foreground=color)]


def label(ax, x, y, s, size=8, color=None, weight='normal', ha='left', va='bottom', dx=0, dy=0, mode='color', bold=False, **kw):
    """글자 한 줄. (x, y)는 자료 좌표, (dx, dy)는 포인트 단위 어긋남. 흰 테두리를 둘러 읽기 쉽게 한다."""
    P = PAL[mode]
    t = ax.annotate(s, (x, y), xytext=(dx, dy), textcoords='offset points', fontsize=size, color=color or P['text'],
                    fontweight='bold' if bold else weight, ha=ha, va=va, zorder=kw.pop('zorder', 20), **kw)
    t.set_path_effects(halo(2.2, P['halo']))
    return t


def scalebar(ax, km, x_frac=0.04, y_frac=0.05, mode='color', size=8):
    """투영 좌표(미터) 축 위에 두 칸짜리 축척 막대. km 는 막대 전체 길이."""
    P = PAL[mode]
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    X = x0 + (x1 - x0) * x_frac
    Y = y0 + (y1 - y0) * y_frac
    L = km * 1000.0
    h = (y1 - y0) * 0.011
    for i in range(2):
        ax.add_patch(plt.Rectangle((X + i * L / 2, Y), L / 2, h, fc=P['text'] if i == 0 else '#FFFFFF', ec=P['text'], lw=0.6, zorder=30))
    for v, s in ((0, '0'), (L, '%g km' % km)):
        t = ax.text(X + v, Y + h * 1.6, s, fontsize=size, ha='center', va='bottom', color=P['text'], zorder=31)
        t.set_path_effects(halo(2.2, P['halo']))


def north_arrow(ax, x_frac=0.93, y_frac=0.85, mode='color', size=8, length=0.07):
    P = PAL[mode]
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    X = x0 + (x1 - x0) * x_frac
    Y = y0 + (y1 - y0) * y_frac
    Ln = (y1 - y0) * length
    ax.annotate('', xy=(X, Y + Ln), xytext=(X, Y), arrowprops=dict(arrowstyle='-|>', color=P['text'], lw=1.0, mutation_scale=9), zorder=30)
    t = ax.text(X, Y + Ln * 1.08, 'N', fontsize=size, ha='center', va='bottom', fontweight='bold', color=P['text'], zorder=31)
    t.set_path_effects(halo(2.2, P['halo']))


def proj_bounds(bbox, epsg, n=40):
    """경위도 상자의 가장자리를 투영해 투영 좌표 상자(xmin, ymin, xmax, ymax)를 구한다."""
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    lo0, la0, lo1, la1 = bbox
    xs = np.concatenate([np.linspace(lo0, lo1, n), np.full(n, lo1), np.linspace(lo1, lo0, n), np.full(n, lo0)])
    ys = np.concatenate([np.full(n, la0), np.linspace(la0, la1, n), np.full(n, la1), np.linspace(la1, la0, n)])
    X, Y = tr.transform(xs, ys)
    return float(np.min(X)), float(np.min(Y)), float(np.max(X)), float(np.max(Y))


def graticule(ax, bbox, epsg, step, mode='color', size=8, lw=0.4, label_edges=True):
    """경위선망을 EPSG 좌표계에 그린다. 눈금 글자는 그림 가장자리(왼쪽, 아래쪽)에 둔다."""
    P = PAL[mode]
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    lo0, la0, lo1, la1 = bbox
    n = 200
    for lon in np.arange(math.ceil(lo0 / step) * step, lo1 + 1e-9, step):
        la = np.linspace(la0, la1, n)
        x, y = tr.transform(np.full(n, lon), la)
        ax.plot(x, y, color=P['grid'], lw=lw, ls=(0, (4, 3)), zorder=2)
    for lat in np.arange(math.ceil(la0 / step) * step, la1 + 1e-9, step):
        lo = np.linspace(lo0, lo1, n)
        x, y = tr.transform(lo, np.full(n, lat))
        ax.plot(x, y, color=P['grid'], lw=lw, ls=(0, (4, 3)), zorder=2)


def edge_ticks(ax, bbox, epsg, step, mode='color', size=8):
    """투영 좌표 축의 눈금을 경위도 값으로 바꿔 쓴다(왼쪽은 위도, 아래쪽은 경도). 격자선이 왼쪽·아래 가장자리와 만나는 곳에 둔다."""
    P = PAL[mode]
    inv = Transformer.from_crs(epsg, 4326, always_xy=True)
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    # 아래 가장자리: 경도선이 y0 에서 만나는 x 를 찾는다
    xt, xl = [], []
    for lon in np.arange(math.ceil(bbox[0] / step) * step, bbox[2] + 1e-9, step):
        las = np.linspace(bbox[1] - 3, bbox[3] + 3, 4000)
        x, y = tr.transform(np.full_like(las, lon), las)
        i = np.argmin(np.abs(y - y0))
        if x0 < x[i] < x1:
            xt.append(x[i]); xl.append('%g°E' % lon)
    yt, yl = [], []
    for lat in np.arange(math.ceil(bbox[1] / step) * step, bbox[3] + 1e-9, step):
        los = np.linspace(bbox[0] - 3, bbox[2] + 3, 4000)
        x, y = tr.transform(los, np.full_like(los, lat))
        i = np.argmin(np.abs(x - x0))
        if y0 < y[i] < y1:
            yt.append(y[i]); yl.append('%g°N' % lat)
    ax.set_xticks(xt); ax.set_xticklabels(xl, fontsize=size, color=P['soft'])
    ax.set_yticks(yt); ax.set_yticklabels(yl, fontsize=size, color=P['soft'])
    ax.tick_params(length=2.5, width=0.5, color=P['frame'], pad=1.5)


def label_audit(fig, ax=None, min_size=8.0):
    """글자 겹침·넘침·크기를 검사한다. 반환: 경고 문자열 목록. fig.canvas 를 한 번 그린 뒤에 부른다."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    texts = []
    for t in fig.findobj(matplotlib.text.Text):
        s = t.get_text()
        if not s or not t.get_visible():
            continue
        try:
            bb = t.get_window_extent(r)
        except Exception:
            continue
        if bb.width < 1 or bb.height < 1:
            continue
        texts.append((s, t.get_fontsize(), bb))
    warn = []
    W, H = fig.canvas.get_width_height()
    for i, (s, fs, bb) in enumerate(texts):
        if fs < min_size - 1e-6:
            warn.append('글자 %.1fpt 미만 기준 위반: %s (%.1fpt)' % (min_size, s, fs))
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > W + 1 or bb.y1 > H + 1:
            warn.append('글자 넘침: %s' % s)
        for s2, fs2, bb2 in texts[i + 1:]:
            ox = min(bb.x1, bb2.x1) - max(bb.x0, bb2.x0)
            oy = min(bb.y1, bb2.y1) - max(bb.y0, bb2.y0)
            if ox > 1 and oy > 1:
                small = min(bb.width * bb.height, bb2.width * bb2.height)
                if ox * oy / small > 0.06:
                    warn.append('글자 겹침: %s / %s' % (s, s2))
    return warn, len(texts)


def mm_fig(w_mm=130.0, h_mm=100.0):
    """B5 본문 폭 130 mm 에 맞춘 그림 틀. 제2권 build 가 그림을 130 mm 폭으로 넣으므로 글자 8pt 는 인쇄에서도 8pt 이다."""
    return plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4), dpi=100)


def timer():
    t0 = time.perf_counter()
    return lambda: time.perf_counter() - t0
