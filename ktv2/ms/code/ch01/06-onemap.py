# -*- coding: utf-8 -*-
"""실습 1-6: 지도 한 장을 코드로 처음부터 끝까지 만든다. 한반도와 둘레 바다, 수심 띠, 강, 도시, 산, 한글 지명, 축척, 경위선.
쓰는 법:  python3 06-onemap.py            → out/onemap-color.svg, out/onemap-bw.svg (+ png)
다른 파일에서:  build('color') 가 (fig, 경고목록, 통계)를 돌려준다."""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K
import numpy as np
import geopandas as gpd
import shapely, shapely.ops, shapely.geometry
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

BBOX = (123.2, 32.8, 134.4, 43.0)       # 지도에 보일 경위도 상자
EPSG = 5179                              # 한국 통합 좌표계(TM). 중앙 경도 127.5E, 단위 미터
GRID = 2.0
LEG_MM = 17.0                            # 범례 띠 높이(mm)

CITY = [  # 한글, NE 영문 이름, 글자 어긋남(dx, dy: pt), 정렬
    ('서울', 'Seoul', (-4, 4), 'right'), ('인천', 'Incheon', (-5, -3), 'right'), ('대전', 'Daejeon', (5, -9), 'left'),
    ('광주', 'Gwangju', (-5, -9), 'right'), ('대구', 'Daegu', (-5, 1), 'right'), ('부산', 'Busan', (4, -9), 'left'),
    ('울산', 'Ulsan', (5, -2), 'left'), ('제주', 'Jeju', (-5, -3), 'right'), ('평양', 'Pyongyang', (-5, 3), 'right'),
    ('원산', 'Wonsan', (5, -9), 'left'), ('함흥', 'Hamhung', (5, 3), 'left'), ('청진', 'Chongjin', (-5, 3), 'right'),
    ('후쿠오카', 'Fukuoka', (5, 3), 'left')]
PEAK = [('백두산', 'Paektu-san', (6, 3), 'left'), ('한라산', 'Halla-san', (6, -4), 'left'), ('설악산', 'Sorak-san', (6, 0), 'left'), ('지리산', 'Chiri-san', (-6, -7), 'right')]
SEA = [('황해', 124.15, 36.0, 0), ('동해', 131.2, 39.8, 0), ('동중국해', 124.9, 33.6, 0), ('대한해협', 129.75, 34.55, 0)]
RIVER = [('압록강', 'Yalu', (125.9, 40.55), (0, 4), 'center'), ('두만강', 'Tumen', (129.55, 42.35), (4, 2), 'left'),
         ('낙동강', 'Nakdong', (128.75, 36.6), (6, 0), 'left'), ('한강', 'Han', (127.6, 37.35), (0, -11), 'center')]
RIV_NAMES = ['Yalu', 'Tumen', 'Nakdong', 'Han', 'Namhan']


def to_proj(gdf):
    return gdf.to_crs(EPSG)


def polys(gdf):
    """clip 결과에서 면 도형만 남긴다."""
    g = gdf.explode(index_parts=False)
    return g[g.geometry.geom_type == 'Polygon']


def build(mode='color'):
    P = K.PAL[mode]
    K.use_font(8)
    stats = {}
    pad = 3.0
    bb_read = (BBOX[0] - pad, BBOX[1] - pad, BBOX[2] + pad, BBOX[3] + pad)
    cutbox = box(*bb_read)

    land = gpd.clip(K.fix(K.read('ne_10m_land', bb_read))[0], cutbox)
    isl = gpd.clip(K.read('ne_10m_minor_islands', bb_read), cutbox)
    lakes = gpd.clip(K.fix(K.read('ne_10m_lakes', bb_read))[0], cutbox)
    riv = K.read('ne_10m_rivers_lake_centerlines', bb_read)
    riv = riv[riv['name'].isin(RIV_NAMES)]
    pp = K.read('ne_10m_populated_places_simple', bb_read)
    ep = K.read('ne_10m_geography_regions_elevation_points', bb_read)
    bathy, nfix = K.bathy_layers(BBOX, pad=pad)
    stats.update(land=len(land), islands=len(isl), lakes=len(lakes), rivers=len(riv), places=len(pp), peaks=len(ep), made_valid=nfix)

    x0, y0, x1, y1 = K.proj_bounds(BBOX, EPSG)
    # 눈금이 가장자리에서 읽히도록 투영 상자를 경위도 상자의 안쪽 사각형으로 줄인다(모서리의 빈 곳 방지)
    tr = K.Transformer.from_crs(4326, EPSG, always_xy=True)
    xl, _ = tr.transform(BBOX[0], (BBOX[1] + BBOX[3]) / 2)
    xr, _ = tr.transform(BBOX[2], (BBOX[1] + BBOX[3]) / 2)
    _, yb = tr.transform((BBOX[0] + BBOX[2]) / 2, BBOX[1])
    _, yt = tr.transform((BBOX[0] + BBOX[2]) / 2, BBOX[3])
    X0, X1, Y0, Y1 = xl + 20000, xr - 20000, yb + 25000, yt - 10000
    W_mm = 130.0
    H_mm = W_mm * (Y1 - Y0) / (X1 - X0) + LEG_MM           # 아래쪽 범례 띠
    fig = K.mm_fig(W_mm, H_mm)
    axh = (H_mm - LEG_MM) / H_mm
    ax = fig.add_axes([0.085, 1 - axh + 0.0, 0.905, axh - 0.012])
    ax.set_facecolor(P['ocean'])

    # 1) 수심 띠: 깊은 층을 위에 겹쳐 칠한다(층이 "그 깊이보다 깊은 바다"이므로)
    present = []
    for d, _ in K.BATHY:
        g = bathy[d]
        if len(g) == 0:
            continue
        gp = to_proj(polys(g))
        if len(gp) == 0:
            continue
        if not gp.intersects(box(X0, Y0, X1, Y1)).any():
            continue                         # 보이는 범위 밖에만 있는 층은 범례에 넣지 않는다
        gpd.GeoSeries([shapely.make_valid(shapely.unary_union(list(g.geometry)))], crs=4326).to_crs(EPSG).plot(ax=ax, facecolor=P['bathy'][d], edgecolor=P['iso'], linewidth=0.35, zorder=3)   # 한 층을 하나로 합쳐 조각 사이의 머리카락 선을 없앤다
        present.append(d)
    stats['depth_levels_in_view'] = present
    # 2) 땅, 섬, 호수
    to_proj(polys(land)).plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.45, zorder=5)
    to_proj(isl).plot(ax=ax, facecolor=P['land'], edgecolor=P['coast'], linewidth=0.35, zorder=5)
    to_proj(polys(lakes)).plot(ax=ax, facecolor=P['lake'], edgecolor=P['coast'], linewidth=0.3, zorder=6)
    # 3) 강
    to_proj(riv).plot(ax=ax, color=P['river'], linewidth=1.0, zorder=7)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
    ax.set_aspect('equal')
    ax.set_xlabel(''); ax.set_ylabel('')            # geopandas 가 붙이는 Easting/Northing 글자를 지운다
    K.graticule(ax, BBOX, EPSG, GRID, mode)
    K.edge_ticks(ax, BBOX, EPSG, GRID, mode)

    # 4) 도시
    for ko, ne, (dx, dy), ha in CITY:
        r = pp[pp['name'].str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('ascii') == ne].iloc[0]
        x, y = tr.transform(r.longitude, r.latitude)
        ax.plot(x, y, 'o', ms=3.2, mfc=P['text'], mec='#FFFFFF', mew=0.6, zorder=15)
        K.label(ax, x, y, ko, 8, dx=dx, dy=dy, ha=ha, va='bottom', mode=mode)
    # 5) 산: 삼각 표지 + 이름 + 높이(자료의 표고점)
    for ko, ne, (dx, dy), ha in PEAK:
        r = ep[ep['name'] == ne].iloc[0]
        x, y = tr.transform(r.long_x, r.lat_y)
        ax.plot(x, y, '^', ms=4.2, mfc=P['hot'], mec='#FFFFFF', mew=0.5, zorder=15)
        K.label(ax, x, y, '%s %s m' % (ko, format(int(r.elevation), ',')), 8, color=P['hot'], bold=True, dx=dx, dy=dy, ha=ha, va='bottom', mode=mode)
    # 6) 강 이름
    for ko, ne, (lo, la), (dx, dy), ha in RIVER:
        # 이름을 강 위의 점(힌트 좌표에서 가장 가까운 점)에 붙인다
        line = shapely.unary_union(list(riv[riv['name'] == ne].geometry) + (list(riv[riv['name'] == 'Namhan'].geometry) if ne == 'Han' else []))
        a, _ = shapely.ops.nearest_points(line, shapely.geometry.Point(lo, la))
        x, y = tr.transform(a.x, a.y)
        K.label(ax, x, y, ko, 8, color=P['river'], dx=dx, dy=dy, ha=ha, mode=mode, style='italic')
    # 7) 바다 이름(글자 사이를 띄운다)
    for ko, lo, la, rot in SEA:
        x, y = tr.transform(lo, la)
        t = ax.text(x, y, ' '.join(ko) if len(ko) <= 3 else ko, fontsize=8, color=P['soft'], ha='center', va='center', style='italic', rotation=rot, zorder=14)
        t.set_path_effects(K.halo(2.2, P['halo']))
    K.scalebar(ax, 200, 0.04, 0.93, mode)
    K.north_arrow(ax, 0.93, 0.88, mode)

    # 8) 아래 범례
    labels = {200: '200~1000 m', 1000: '1000~2000 m', 2000: '2000~3000 m', 3000: '3000~4000 m', 4000: '4000~5000 m', 5000: '5000 m 이상'}
    hands = [Patch(fc=P['ocean'], ec=P['iso'], lw=0.35, label='0~200 m')]
    for d in present:
        lab = '%d m 이상' % d if d == present[-1] else labels[d]       # 보이는 가장 깊은 층은 "이상"으로 쓴다
        hands.append(Patch(fc=P['bathy'][d], ec=P['iso'], lw=0.35, label=lab))
    hands += [Line2D([0], [0], color=P['river'], lw=1.0, label='강'), Line2D([0], [0], marker='o', ls='', ms=3.2, mfc=P['text'], mec='#FFFFFF', label='도시'),
              Line2D([0], [0], marker='^', ls='', ms=4.2, mfc=P['hot'], mec='#FFFFFF', label='산(표고점)')]
    fig.legend(handles=hands, loc='lower left', bbox_to_anchor=(0.01, 0.0), ncol=4, frameon=False, fontsize=8, handlelength=1.6, columnspacing=1.2, handletextpad=0.5, labelspacing=0.3)
    from pyproj import Proj
    pj = Proj(EPSG)
    conv = {}
    for nm, (lo, la) in {'왼쪽 아래': (BBOX[0], BBOX[1]), '오른쪽 아래': (BBOX[2], BBOX[1]), '왼쪽 위': (BBOX[0], BBOX[3]), '오른쪽 위': (BBOX[2], BBOX[3])}.items():
        f = pj.get_factors(lo, la)
        conv[nm] = round(float(f.meridian_convergence), 2)
    stats['grid_convergence_deg'] = conv
    warns, ntext = K.label_audit(fig)
    stats['texts'] = ntext
    stats['axes_mm'] = (round(W_mm, 1), round(H_mm, 1))
    return fig, warns, stats


if __name__ == '__main__':
    t = K.timer()
    os.makedirs(os.path.join(K.HERE, 'out'), exist_ok=True)
    for mode in ('color', 'bw'):
        fig, warns, stats = build(mode)
        base = os.path.join(K.HERE, 'out', 'onemap-' + mode)
        fig.savefig(base + '.svg')
        fig.savefig(base + '.png', dpi=150)
        print('[%s] 통계 %s' % (mode, json.dumps(stats, ensure_ascii=False)))
        print('[%s] 글자 검사 경고 %d개' % (mode, len(warns)))
        for w in warns:
            print('   ', w)
        print('[%s] 저장: %s.svg (%s B), %s.png (%s B)' % (mode, base, format(os.path.getsize(base + '.svg'), ','), base, format(os.path.getsize(base + '.png'), ',')))
        plt.close(fig)
    print('전체 %.1f초' % t())
