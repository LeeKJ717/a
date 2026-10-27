# -*- coding: utf-8 -*-
"""0장 「지구 지도 도록」 그림 생성: fig/fig-ch00-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book4): python3 scripts/figs-ch00.py   (한 장만: python3 scripts/figs-ch00.py ch00-world)
지도는 Natural Earth 50 m 육지와 10 m 얕은 바다(200 m 등수심선 안쪽) 자료이다. 지도 위 글자는 한글이며 8 pt 이상, 색과 흑백 두 벌.
그림 0-3 은 ms/code/ch00/calc0-1.py 의 식을 다시 그린 것이고, 그림 0-2 의 원은 반지름 500 km 측지선 원을 투영한 것이다."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import figkit12 as F
from figkit12 import plt, np, C
import mapkit as K
import geopandas as gpd
from shapely.geometry import box, Polygon
from pyproj import Transformer, Geod
FS = 8.0
G = Geod(ellps='WGS84')
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('chapart', os.path.join(HERE, 'chapart-v1.py'))
_land = {}


def land():
    if 'l' not in _land:
        _land['l'] = K.read('ne_50m_land')
    return _land['l']


def shelf():
    if 's' not in _land:
        _land['s'] = K.read('ne_10m_bathymetry_K_200')
    return _land['s']


def draw_world(ax, crs, P, bb=(-180, -90, 180, 90), shelf_on=True):
    ax.set_facecolor(P['ocean'])
    lg = gpd.clip(land(), box(*bb)).to_crs(crs)
    if shelf_on:
        sg = gpd.clip(shelf(), box(*bb)).to_crs(crs)
        sg.plot(ax=ax, color=P['shelf'], edgecolor='none', zorder=1)
    lg.plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.35, zorder=2)
    ax.set_xlabel(''); ax.set_ylabel('')


def graticule(ax, crs, P, step=30, lat_lim=80):
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    for lon in range(-180, 181, step):
        x, y = tr.transform(np.full(80, float(lon)), np.linspace(-lat_lim, lat_lim, 80)); ax.plot(x, y, color=P['grid'], lw=0.35, ls=(0, (4, 3)), zorder=3)
    for lat in range(-60, 61, step):
        x, y = tr.transform(np.linspace(-180, 180, 200), np.full(200, float(lat))); ax.plot(x, y, color=P['grid'], lw=0.35, ls=(0, (4, 3)), zorder=3)


PALW = {'color': dict(ocean='#E3EEF3', shelf='#C8DEE9', land='#F1EBDD', coast='#6E7F88', grid='#8FA5B0', text='#1B2A33', frame='#6E7F88', seatxt='#2B5F80'),
        'bw': dict(ocean='#F2F2F2', shelf='#E0E0E0', land='#FFFFFF', coast='#444444', grid='#888888', text='#111111', frame='#444444', seatxt='#111111')}


def lab(ax, tr, lon, lat, s, P, color=None, bold=False, ha='center'):
    x, y = tr.transform(lon, lat)
    ax.text(x, y, s, fontsize=FS, ha=ha, va='center', color=color or P['text'], fontweight='bold' if bold else 'normal', zorder=12,
            path_effects=[__import__('matplotlib.patheffects', fromlist=['x']).withStroke(linewidth=2.0, foreground='#FFFFFF', alpha=0.8)])


# ---------------------------------------------------------------- 그림 0-1 세계 개관
def fig_world(mode):
    P = PALW[mode]; crs = 'EPSG:8857'
    f = F.fig(130, 78); ax = f.add_axes([0.01, 0.02, 0.98, 0.96])
    draw_world(ax, crs, P); graticule(ax, crs, P)
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    for lon, lat, s in ((85, 48, '아시아'), (15, 52, '유럽'), (20, 5, '아프리카'), (-100, 45, '북아메리카'), (-60, -12, '남아메리카'), (134, -25, '오세아니아'), (60, -78, '남극 대륙'), (-42, 73, '그린란드')):
        lab(ax, tr, lon, lat, s, P, bold=True)
    for lon, lat, s in ((-150, 10, '태평양'), (-35, 15, '대서양'), (78, -20, '인도양'), (0, 82, '북극해'), (160, -58, '남극해')):
        lab(ax, tr, lon, lat, s, P, color=P['seatxt'])
    x0, y0 = tr.transform(-180, 0); x1, y1 = tr.transform(180, 0); xb, yb = tr.transform(0, -90); xt, yt = tr.transform(0, 90)
    ax.set_xlim(x0 * 1.01, x1 * 1.01); ax.set_ylim(yb * 1.02, yt * 1.02)
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color(P['frame'])
    return f


# ---------------------------------------------------------------- 그림 0-2 투영과 모양, 면적
def fig_proj(mode):
    P = PALW[mode]
    f = F.fig(130, 90)
    specs = (('EPSG:3395', '메르카토르 투영', [0.02, 0.02, 0.47, 0.88], 80), ('EPSG:8857', '이퀄 어스 투영', [0.51, 0.02, 0.47, 0.88], 90))
    for crs, title, rect, lim in specs:
        ax = f.add_axes(rect); draw_world(ax, crs, P, bb=(-180, -80, 180, 83), shelf_on=False)
        tr = Transformer.from_crs(4326, crs, always_xy=True)
        for lat in (-60, -30, 0, 30, 60):
            for lon in (-150, -90, -30, 30, 90, 150):
                pts = [G.fwd(lon, lat, 360 * i / 60, 500000)[:2] for i in range(60)]
                xy = np.array([tr.transform(*p) for p in pts])
                ax.fill(xy[:, 0], xy[:, 1], facecolor=C[mode]['wet'] if mode == 'color' else '#555555', alpha=0.55, edgecolor=C[mode]['ink'], linewidth=0.4, zorder=6)
        x0, _ = tr.transform(-180, 0); x1, _ = tr.transform(180, 0)
        _, ya = tr.transform(0, -80 if crs == 'EPSG:3395' else -90); _, yb = tr.transform(0, 83 if crs == 'EPSG:3395' else 90)
        ax.set_xlim(x0 * 1.01, x1 * 1.01); ax.set_ylim(ya * 1.01, yb * 1.01); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color(P['frame'])
        ax.set_title(title, fontsize=FS + 0.5, color=P['text'], pad=3)
    return f


# ---------------------------------------------------------------- 그림 0-3 위도별 경도 1도의 길이
def fig_deg(mode):
    Q = C[mode]
    f = F.fig(130, 68); ax = f.add_axes([0.11, 0.14, 0.62, 0.80]); F.style_ax(ax, mode, grid='both')
    a = 6378137.0; e2 = (1 / 298.257223563) * (2 - 1 / 298.257223563)
    lat = np.linspace(0, 89.5, 300); p = np.radians(lat); w = 1 - e2 * np.sin(p) ** 2
    lon_km = math.pi / 180 * a * np.cos(p) / np.sqrt(w) / 1000
    ax.plot(lat, lon_km, color=Q['wet'], lw=1.6, zorder=4)
    ax.axhline(111.0, color=Q['dry'], lw=1.2, ls=(0, (4, 2)), zorder=3)
    ax.text(2, 113.5, '1도 = 111 km 로 놓은 어림', fontsize=FS, color=Q['ink'], va='bottom')
    ax.text(6, 50, '실제 경도 1도의 길이', fontsize=FS, color=Q['ink'], ha='left')
    for L in (30, 45, 60, 75):
        pp = math.radians(L); v = math.pi / 180 * a * math.cos(pp) / math.sqrt(1 - e2 * math.sin(pp) ** 2) / 1000
        ax.scatter([L], [v], s=18, color=Q['ink'], zorder=6)
    ax.set_xlim(0, 90); ax.set_ylim(0, 125); ax.set_xticks(range(0, 91, 15)); ax.set_yticks(range(0, 121, 20))
    ax.set_xlabel('위도 (도)', fontsize=FS); ax.set_ylabel('경도 1도의 길이 (km)', fontsize=FS)
    ax2 = f.add_axes([0.76, 0.14, 0.22, 0.80]); ax2.axis('off')
    txt = '\n'.join('위도 %d도\n%.1f km (%.2f배)' % (L, math.pi / 180 * a * math.cos(math.radians(L)) / math.sqrt(1 - e2 * math.sin(math.radians(L)) ** 2) / 1000,
                                                  111.0 / (math.pi / 180 * a * math.cos(math.radians(L)) / math.sqrt(1 - e2 * math.sin(math.radians(L)) ** 2) / 1000)) for L in (30, 45, 60, 75))
    ax2.text(0.0, 0.98, txt, fontsize=FS, color=Q['ink'], va='top', linespacing=1.35)
    return f


# ---------------------------------------------------------------- 그림 0-4 장별 지도 창
def windows():
    spec_ = importlib.util.spec_from_file_location('chapart', os.path.join(HERE, 'chapart-v1.py'))
    src = open(os.path.join(HERE, 'chapart-v1.py'), encoding='utf-8').read()
    a = src.index('CH = {'); b = src.index('\n}\n', a) + 3
    ns = {}; exec(src[a:b], ns); return ns['CH']


def fig_windows(mode):
    P = PALW[mode]; CH = windows(); W, H = 129.6, 64.0
    f = F.fig(130, 100)
    groups = (range(2, 9), range(9, 16))
    for gi, grp in enumerate(groups):
        ax = f.add_axes([0.02, 0.51 - 0.49 * gi + 0.0, 0.96, 0.46])
        draw_world(ax, 'EPSG:4326', P, bb=(-180, -90, 180, 90), shelf_on=False)
        for ci in grp:
            lon0, lat0, hd, _, ov = CH[ci]; k = math.cos(math.radians(lat0)); hw = hd * (W / H) / k
            x0, x1, y0, y1 = lon0 - hw, lon0 + hw, max(lat0 - hd, -90), min(lat0 + hd, 90)
            for sh in (0, -360, 360):
                ax.add_patch(plt.Rectangle((x0 + sh, y0), x1 - x0, y1 - y0, fill=False, edgecolor=C[mode]['acc'] if mode == 'color' else '#000000', lw=0.9, zorder=8,
                                           ls='-' if ci % 2 == 0 else (0, (4, 2))))
            ax.text(max(x0, -178) + 2, min(y1, 88) - 2, str(ci), fontsize=FS, fontweight='bold', color=P['text'], ha='left', va='top', zorder=12,
                    bbox=dict(fc='#FFFFFF', ec='none', pad=0.5, alpha=0.9))
        ax.set_xlim(-180, 180); ax.set_ylim(-90, 90); ax.set_aspect('auto'); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color(P['frame'])
    return f


FIGS = [('ch00-world', fig_world), ('ch00-proj', fig_proj), ('ch00-deg', fig_deg), ('ch00-windows', fig_windows)]
if __name__ == '__main__':
    only = sys.argv[1:]
    for name, fn in FIGS:
        if only and name not in only: continue
        for mode in ('color', 'bw'):
            F.save(fn(mode), name, mode)
