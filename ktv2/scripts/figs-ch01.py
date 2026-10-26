# -*- coding: utf-8 -*-
"""제2권 1장 그림 6장. 실행: python3 scripts/figs-ch01.py  → fig/fig-ch01-<이름>-v1-color.svg, -bw.svg
그림 속 숫자는 ms/code/ch01 의 mapkit 함수로 이 스크립트가 다시 계산한 값이며, 같은 값이 실행 로그(ms/code/ch01/*.log)에 있다.
글자는 8pt 이상, 글꼴은 Noto Sans CJK KR, 지도의 지명은 한글만. 본문 폭 130 mm 로 그린다."""
import os, sys, math, importlib.util, warnings
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch01'))
import mapkit as K
import numpy as np
import geopandas as gpd
import shapely, shapely.ops
from shapely.geometry import box, Polygon, Point
from pyproj import CRS, Transformer
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

OUT = K.FIG
os.makedirs(OUT, exist_ok=True)
WARN = []


def spec(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def save(fig, name, mode):
    with warnings.catch_warnings():
        if name == 'hangul':            # 이 그림은 일부러 한글 없는 글꼴을 쓰므로 "글리프 없음" 경고가 나오는 것이 정상이다
            warnings.filterwarnings('ignore', message='.*missing from font.*')
        warns, n = K.label_audit(fig)
        WARN.extend('[%s %s] %s' % (name, mode, w) for w in warns)
        p = os.path.join(OUT, 'fig-ch01-%s-v1-%s.svg' % (name, mode))
        fig.savefig(p)
    print('저장 %s (%s B), 글자 %d개, 경고 %d개' % (os.path.basename(p), format(os.path.getsize(p), ','), n, len(warns)))
    plt.close(fig)


# ------------------------------------------------------------------ 그림 1: 같은 500 km 원이 좌표계마다 어떻게 보이는가
AEA = CRS.from_proj4('+proj=aea +lat_1=20 +lat_2=50 +lat_0=30 +lon_0=127 +datum=WGS84 +units=m')


def circle_ring(lon, lat, r_km, n=180):
    az = np.linspace(0, 360, n, endpoint=False)
    lo, la, _ = K.GEOD.fwd(np.full(n, lon), np.full(n, lat), az, np.full(n, r_km * 1000.0))
    return np.c_[lo, la]


def fig_crs(mode):
    P = K.PAL[mode]
    K.use_font(8)
    land = gpd.clip(K.read('ne_50m_land', (90, -5, 165, 65)), box(90, -5, 165, 65))
    centers = [(127.0, 12.0), (127.0, 32.0), (127.0, 52.0)]
    R = 500.0
    panels = [('(가) 경위도 그대로', 4326, 111.32e3), ('(나) 웹 메르카토르', 3857, 1.0), ('(다) 알베르스 등적', AEA, 1.0)]
    fig = K.mm_fig(130, 78)
    info = []
    for i, (ttl, crs, unit) in enumerate(panels):
        ax = fig.add_axes([0.012 + i * 0.328, 0.075, 0.318, 0.80])
        ax.set_facecolor(P['ocean'])
        tr = Transformer.from_crs(4326, crs, always_xy=True)
        g = land.to_crs(crs if not isinstance(crs, CRS) else crs)
        g.plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.3)
        # 경위선
        for lon in range(100, 161, 20):
            la = np.linspace(-5, 65, 100); x, y = tr.transform(np.full_like(la, lon), la); ax.plot(x, y, color=P['grid'], lw=0.4, zorder=2)
        for lat in range(0, 61, 20):
            lo = np.linspace(90, 165, 100); x, y = tr.transform(lo, np.full_like(lo, lat)); ax.plot(x, y, color=P['grid'], lw=0.4, zorder=2)
        row = []
        for (lo, la) in centers:
            ring = circle_ring(lo, la, R)
            xs, ys = tr.transform(ring[:, 0], ring[:, 1])
            if crs == 4326:
                a_draw = Polygon(np.c_[xs * unit, ys * unit]).area / 1e6          # 1도 = 111.32 km 로 친 면적
            else:
                a_draw = Polygon(np.c_[xs, ys]).area / 1e6
            a_true = abs(K.GEOD.polygon_area_perimeter(ring[:, 0], ring[:, 1])[0]) / 1e6
            row.append(a_draw / a_true)
            ax.fill(xs, ys, facecolor=P['hot'], alpha=0.55 if mode == 'color' else 0.45, edgecolor=P['hot'], lw=0.6, zorder=6)
            x0, y0 = tr.transform(lo, la)
        info.append(row)
        # 범위: 세 원이 모두 보이게
        xl, yl = tr.transform([100, 155], [2, 62])
        pad_x = 0.0
        ax.set_xlim(min(xl), max(xl)); ax.set_ylim(min(yl), max(yl))
        ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlabel(''); ax.set_ylabel('')
        for sp in ax.spines.values():
            sp.set_color(P['frame']); sp.set_linewidth(0.6)
        fig.text(0.012 + i * 0.328 + 0.159, 0.93, ttl, ha='center', va='center', fontsize=8, color=P['text'], fontweight='bold')
        # 원 옆에 면적 비
        for (lo, la), r in zip(centers, row):
            x, y = tr.transform(lo, la)
            t = ax.text(x, y, '×%.2f' % r, fontsize=8, ha='center', va='center', color=P['text'], zorder=9, fontweight='bold')
            t.set_path_effects(K.halo(2.0, P['halo']))
    fig.text(0.5, 0.012, '원의 중심: 12°N, 32°N, 52°N (127°E). 숫자는 "그려진 원의 면적 ÷ 실제 면적".', ha='center', va='bottom', fontsize=8, color=P['soft'])
    return fig, info


# ------------------------------------------------------------------ 그림 2: 거리 계산 방법별 차이
def fig_dist(mode):
    P = K.PAL[mode]
    K.use_font(8)
    pts = {'노백산': (K.dms(128, 3), K.dms(44, 6)), '돈화 기상대': (K.dms(128, 12), K.dms(43, 22)), '서울': (126.997785, 37.568295), '부산': (129.008102, 35.096999),
           '제주': (126.521931, 33.510137), '평양': (125.752745, 39.021385), '도쿄': (139.749462, 35.686963), '북경': (116.386340, 39.930838), '합이빈': (126.648, 45.752)}
    pairs = [('노백산', '돈화 기상대'), ('서울', '평양'), ('서울', '부산'), ('서울', '제주'), ('서울', '북경'), ('서울', '도쿄'), ('부산', '합이빈')]
    rows = []
    for a, b in pairs:
        pa, pb = pts[a], pts[b]
        g = K.geodesic_km(*pa, *pb)
        rows.append((a + '–' + b, g, K.haversine(*pa, *pb) / g - 1, K.projected_km(*pa, *pb, 32652) / g - 1, K.projected_km(*pa, *pb, 5179) / g - 1,
                     K.projected_km(*pa, *pb, 3857) / g - 1, math.hypot(pb[0] - pa[0], pb[1] - pa[1]) * 111.2 / g - 1))
    fig = K.mm_fig(130, 78)
    cols = {'구면(haversine)': ('#2F6F9A', '#222222', 1), 'UTM 52N': ('#C2872F', '#777777', 2), 'EPSG:5179': ('#5E9E6B', '#BBBBBB', 3)}
    cols2 = {'웹 메르카토르': ('#B0413E', '#222222', 1), '도×111.2 km': ('#7A5CA3', '#AAAAAA', 2)}
    y = np.arange(len(rows))[::-1]
    axs = [fig.add_axes([0.255, 0.31, 0.33, 0.63]), fig.add_axes([0.665, 0.31, 0.32, 0.63])]
    for ax, (cset, idxs, ttl, xl) in zip(axs, [(cols, (2, 3, 4), '(가) 구면, 투영 평면', (-1.0, 1.0)), (cols2, (5, 6), '(나) 웹 메르카토르, 도 단위 곱', (0, 40))]):
        w = 0.8 / len(idxs)
        for k, (nm, (cc, cb, hat)) in enumerate(cset.items()):
            vals = [100 * r[idxs[k]] for r in rows]
            ax.barh(y + (k - (len(idxs) - 1) / 2) * w, vals, height=w * 0.92, color=cc if mode == 'color' else cb,
                    edgecolor='#222222', linewidth=0.3, hatch=None if mode == 'color' else ['', '///', '...'][k], label=nm)
        ax.set_xlim(*xl); ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.axvline(0, color=P['frame'], lw=0.6)
        ax.set_title(ttl, fontsize=8, fontweight='bold', loc='left', pad=4)
        ax.tick_params(labelsize=8, length=2.5, width=0.5)
        ax.grid(axis='x', color=P['grid'], lw=0.4, ls=(0, (4, 3)))
        ax.set_axisbelow(True)
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        ax.legend(fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=1 if len(idxs) == 2 else 3, handlelength=1.2, columnspacing=0.9, handletextpad=0.4, labelspacing=0.25)
        ax.set_xlabel('측지선 거리 대비 차이 (%)', fontsize=8)
    axs[0].set_yticks(y); axs[0].set_yticklabels(['%s\n%s km' % (r[0], format(round(r[1]), ',')) if r[1] > 100 else '%s\n%.1f km' % (r[0], r[1]) for r in rows], fontsize=8)
    axs[1].set_yticks([])
    for ax in axs:
        ax.set_facecolor('#FFFFFF')
    return fig, rows


# ------------------------------------------------------------------ 그림 3: 한글 글꼴
def fig_hangul(mode):
    P = K.PAL[mode]
    K.use_font(8)
    fig = K.mm_fig(130, 36)
    txt = '서울 부산 제주 평양 동해'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        fig.text(0.03, 0.80, '(가) 한글이 없는 글꼴(DejaVu Sans)', fontsize=8, va='center', color=P['soft'])
        fig.text(0.03, 0.57, txt, fontsize=16, va='center', fontfamily='DejaVu Sans', color=P['text'])
        fig.text(0.03, 0.36, '(나) Noto Sans CJK KR', fontsize=8, va='center', color=P['soft'])
        fig.text(0.03, 0.14, txt, fontsize=16, va='center', fontfamily='Noto Sans CJK KR', color=P['text'])
    fig.add_artist(plt.Line2D([0.02, 0.98], [0.46, 0.46], color=P['grid'], lw=0.5, transform=fig.transFigure))
    return fig, None


# ------------------------------------------------------------------ 그림 4: 수심 띠와 등심선
LCC = CRS.from_proj4('+proj=lcc +lat_1=30 +lat_2=45 +lat_0=37 +lon_0=134 +datum=WGS84 +units=m')
BB4 = (118.0, 26.0, 150.0, 46.0)
BOX_AREA = (120.0, 30.0, 134.0, 44.0)


def fig_bathy(mode):
    P = K.PAL[mode]
    K.use_font(8)
    pad = 9.0                      # 자르는 상자를 보이는 범위보다 넉넉히: LCC 에서 위도선이 휘어 보이는 범위가 상자 밖으로 나가므로
    cut = box(BB4[0] - pad, BB4[1] - pad, BB4[2] + pad, BB4[3] + pad)
    bb_read = cut.bounds
    land = gpd.clip(K.fix(K.read('ne_10m_land', bb_read))[0], cut)
    isl = gpd.clip(K.read('ne_10m_minor_islands', bb_read), cut)
    lay, nfix = K.bathy_layers(BB4, pad=pad)
    tr = Transformer.from_crs(4326, LCC, always_xy=True)
    xl, _ = tr.transform(BB4[0], 36); xr, _ = tr.transform(BB4[2], 36); _, yb = tr.transform(134, BB4[1]); _, yt = tr.transform(134, BB4[3])
    X0, X1, Y0, Y1 = xl + 60000, xr - 60000, yb + 80000, yt - 20000
    W = 130.0
    left, axw_mm = 11.0, 118.0
    Hmap = axw_mm * (Y1 - Y0) / (X1 - X0)
    Hbar, Hgap, Htop = 40.0, 10.0, 2.0
    H = Htop + Hmap + 6.0 + Hgap + Hbar
    fig = K.mm_fig(W, H)
    ax = fig.add_axes([left / W, (H - Htop - Hmap) / H, axw_mm / W, Hmap / H])
    ax.set_facecolor(P['ocean'])
    present = []
    for d, _ in K.BATHY:
        g = lay[d]
        if len(g) == 0:
            continue
        gp = g.explode(index_parts=False); gp = gp[gp.geometry.geom_type == 'Polygon'].to_crs(LCC)
        if not gp.intersects(box(X0, Y0, X1, Y1)).any():
            continue
        gpd.GeoSeries([shapely.make_valid(shapely.unary_union(list(g.geometry)))], crs=4326).to_crs(LCC).plot(ax=ax, facecolor=P['bathy'][d], edgecolor=P['iso'], linewidth=0.3, zorder=3)   # 한 층을 하나로 합쳐 이웃 조각 사이의 머리카락 선을 없앤다
        present.append(d)
    lp = land.explode(index_parts=False); lp = lp[lp.geometry.geom_type == 'Polygon']
    lp.to_crs(LCC).plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.4, zorder=5)
    isl.to_crs(LCC).plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.3, zorder=5)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal'); ax.set_xlabel(''); ax.set_ylabel('')
    K.graticule(ax, BB4, LCC, 10, mode)
    K.edge_ticks(ax, BB4, LCC, 10, mode)
    for ko, lo, la in (('황해', 123.7, 35.9), ('동중국해', 126.0, 29.6), ('동해', 132.2, 40.2), ('태평양', 145.5, 33.0)):
        x, y = tr.transform(lo, la)
        t = ax.text(x, y, ko, fontsize=8, color=P['soft'] if ko != '태평양' else '#FFFFFF', ha='center', va='center', style='italic', zorder=14)
        t.set_path_effects(K.halo(2.2, P['halo'] if ko != '태평양' else P['iso']))
    ring = [(BOX_AREA[0], BOX_AREA[1]), (BOX_AREA[2], BOX_AREA[1]), (BOX_AREA[2], BOX_AREA[3]), (BOX_AREA[0], BOX_AREA[3]), (BOX_AREA[0], BOX_AREA[1])]
    n = 60
    edge = []
    for (a, b), (c, d) in zip(ring[:-1], ring[1:]):
        edge += [(a + (c - a) * t_, b + (d - b) * t_) for t_ in np.linspace(0, 1, n, endpoint=False)]
    edge.append(ring[0])
    ex, ey = tr.transform([e[0] for e in edge], [e[1] for e in edge])
    ax.plot(ex, ey, color=P['hot'], lw=1.1, ls=(0, (5, 2.5)), zorder=12)
    bx, by = tr.transform(BOX_AREA[0] + 1.0, BOX_AREA[3] - 1.0)
    K.label(ax, bx, by, '면적을 잰 상자', 8, color=P['hot'], bold=True, mode=mode, va='top')
    K.scalebar(ax, 500, 0.04, 0.045, mode)
    K.north_arrow(ax, 0.94, 0.86, mode)
    # 아래: 상자 안 바다의 깊이별 면적(막대 색이 곧 범례)
    lay0, _ = K.bathy_layers(BOX_AREA, pad=0.0)
    a_box, a_land, a_sea, bands = K.area_by_depth(BOX_AREA, lay0)
    ia = fig.add_axes([(left + 24.0) / W, 9.0 / H, (axw_mm - 24.0 - 8.0) / W, (Hbar - 9.0) / H])
    ia.set_facecolor('#FFFFFF')
    keep = [(b, c) for b, c in zip(bands, [P['ocean']] + [P['bathy'][d] for d in (200, 1000, 2000, 3000, 4000, 5000)]) if b[1] > 0]
    nm = [b[0] for b, _ in keep]; fr = [100 * b[2] for b, _ in keep]; cl = [c for _, c in keep]
    yy = np.arange(len(nm))[::-1]
    ia.barh(yy, fr, color=cl, edgecolor='#222222', linewidth=0.4, height=0.8)
    ia.set_yticks(yy); ia.set_yticklabels(nm, fontsize=8)
    for yv, v in zip(yy, fr):
        ia.text(v + 1.2, yv, '%.1f%%' % v, fontsize=8, va='center', color=P['text'])
    ia.set_xlim(0, 80); ia.set_xticks([0, 20, 40, 60, 80]); ia.tick_params(labelsize=8, length=2.5, width=0.5)
    ia.set_xlabel('상자 안 바다 면적의 비율 (%)', fontsize=8, labelpad=1)
    for sp in ('top', 'right'):
        ia.spines[sp].set_visible(False)
    return fig, (a_box, a_land, a_sea, bands, present, nfix)


# ------------------------------------------------------------------ 그림 5: 한 장의 지도
def fig_map(mode):
    m = spec(os.path.join(ROOT, 'ms', 'code', 'ch01', '06-onemap.py'), 'onemap')
    fig, warns, stats = m.build(mode)
    return fig, (warns, stats)


# ------------------------------------------------------------------ 그림 6: 노백산-돈화 되풀이
def fig_laobai(mode):
    P = K.PAL[mode]
    K.use_font(8)
    EP = 32652
    bb = (127.2, 42.9, 129.3, 44.5)
    tr = Transformer.from_crs(4326, EP, always_xy=True)
    lb = (K.dms(128, 3), K.dms(44, 6)); dh = (K.dms(128, 12), K.dms(43, 22)); ne = (128.220018, 43.350492)
    x0, y0, x1, y1 = K.proj_bounds(bb, EP)
    xl, _ = tr.transform(bb[0], 43.7); xr, _ = tr.transform(bb[2], 43.7); _, yb = tr.transform(128.25, bb[1]); _, yt = tr.transform(128.25, bb[3])
    X0, X1, Y0, Y1 = xl + 4000, xr - 4000, yb + 5000, yt - 5000
    W = 130.0
    H = W * (Y1 - Y0) / (X1 - X0) + 15.0
    fig = K.mm_fig(W, H)
    axh = (H - 15.0) / H
    ax = fig.add_axes([0.085, 1 - axh, 0.905, axh - 0.012])
    cut = box(bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1)
    land = gpd.clip(K.fix(K.read('ne_10m_land', cut.bounds))[0], cut)
    land.to_crs(EP).plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.4, zorder=3)
    rv = K.read('ne_10m_rivers_lake_centerlines', cut.bounds)
    rv = rv[rv['name'].isin(['Di’er Songhua', 'Songhua', 'Tumen'])]
    gpd.clip(rv, cut).to_crs(EP).plot(ax=ax, color=P['river'], linewidth=1.0, zorder=4)
    ax.set_facecolor(P['land'])
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal'); ax.set_xlabel(''); ax.set_ylabel('')
    K.graticule(ax, bb, EP, 0.5, mode)
    K.edge_ticks(ax, bb, EP, 0.5, mode)
    a, b, c = tr.transform(*lb), tr.transform(*dh), tr.transform(*ne)
    # 측지선(경로를 경위도로 촘촘히 뽑아 투영) 과 투영 평면 직선
    gl = K.GEOD.npts(*lb, *dh, 60)
    gx, gy = tr.transform([lb[0]] + [p[0] for p in gl] + [dh[0]], [lb[1]] + [p[1] for p in gl] + [dh[1]])
    ax.plot(gx, gy, color=P['hot'], lw=1.2, zorder=8, label='측지선')
    ax.plot([a[0], b[0]], [a[1], b[1]], color=P['text'], lw=0.9, ls=(0, (4, 2.5)), zorder=9, label='투영 평면 직선')
    ax.plot(*a, '^', ms=7, mfc=P['hot'], mec='#FFFFFF', mew=0.6, zorder=12)
    ax.plot(*b, '*', ms=10, mfc=P['hot'], mec='#FFFFFF', mew=0.6, zorder=12)
    ax.plot(*c, 'o', ms=4.2, mfc=P['text'], mec='#FFFFFF', mew=0.6, zorder=12)
    K.label(ax, *a, '노백산', 8, color=P['hot'], bold=True, dx=7, dy=2, mode=mode)
    K.label(ax, *b, '돈화 기상대', 8, color=P['hot'], bold=True, dx=8, dy=-1, mode=mode, va='bottom')
    K.label(ax, *c, '돈화시', 8, dx=-7, dy=-12, ha='right', mode=mode)
    g, h, u = K.geodesic_km(*lb, *dh), K.haversine(*lb, *dh), K.projected_km(*lb, *dh, EP)
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    K.label(ax, mid[0], mid[1], '측지선 %.2f km\n구면 %.2f km\n투영 직선 %.2f km' % (g, h, u), 8, dx=12, dy=-6, mode=mode, va='center')
    K.scalebar(ax, 20, 0.04, 0.045, mode)
    K.north_arrow(ax, 0.94, 0.84, mode, length=0.09)
    hands = [Line2D([0], [0], color=P['hot'], lw=1.2, label='측지선'), Line2D([0], [0], color=P['text'], lw=0.9, ls=(0, (4, 2.5)), label='투영 평면 직선'),
             Line2D([0], [0], marker='^', ls='', ms=6, mfc=P['hot'], mec='#FFFFFF', label='노백산(논문 좌표)'), Line2D([0], [0], marker='*', ls='', ms=9, mfc=P['hot'], mec='#FFFFFF', label='돈화 기상대(논문 좌표)'),
             Line2D([0], [0], marker='o', ls='', ms=4, mfc=P['text'], mec='#FFFFFF', label='돈화시(Natural Earth)')]
    fig.legend(handles=hands, loc='lower left', bbox_to_anchor=(0.01, 0.0), ncol=2, frameon=False, fontsize=8, handlelength=1.6, columnspacing=1.2, handletextpad=0.5, labelspacing=0.3)
    return fig, (g, h, u)


FIGS = [('crs', fig_crs), ('dist', fig_dist), ('hangul', fig_hangul), ('bathy', fig_bathy), ('map', fig_map), ('laobai', fig_laobai)]

if __name__ == '__main__':
    which = sys.argv[1:] or [n for n, _ in FIGS]
    t = K.timer()
    for name, fn in FIGS:
        if name not in which:
            continue
        for mode in ('color', 'bw'):
            fig, extra = fn(mode)
            if mode == 'color':
                if name == 'crs':
                    print('그림 crs 면적 비(그려진 면적 / 실제 면적): ' + ' | '.join('%s: %s' % (n, ', '.join('%.2f' % v for v in r)) for n, r in zip(['경위도', '웹 메르카토르', '알베르스 등적'], extra)))
                elif name == 'dist':
                    for r in extra:
                        print('그림 dist %-14s 측지선 %8.2f km  구면 %+.3f%%  UTM52N %+.3f%%  5179 %+.3f%%  3857 %+.2f%%  도x111.2 %+.2f%%' % (r[0], r[1], *(100 * v for v in r[2:])))
                elif name == 'bathy':
                    a_box, a_land, a_sea, bands, present, nfix = extra
                    print('그림 bathy 면적 상자 %s km², 땅 %s km², 바다 %s km²; 보이는 층 %s; make_valid %d개' % (format(round(a_box), ','), format(round(a_land), ','), format(round(a_sea), ','), present, nfix))
                    for nm, ar, fr in bands:
                        print('   %-14s %10s km² %5.1f%%' % (nm, format(round(ar), ','), 100 * fr))
                elif name == 'map':
                    print('그림 map 통계', extra[1])
                elif name == 'laobai':
                    print('그림 laobai 측지선 %.4f km, 구면 %.4f km, UTM52N 직선 %.4f km' % extra)
            save(fig, name, mode)
    print('\n경고 %d개' % len(WARN))
    for w in WARN:
        print('  ', w)
    print('전체 %.1f초' % t())
