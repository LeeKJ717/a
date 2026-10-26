# -*- coding: utf-8 -*-
"""5장 그림(색·흑백 SVG 두 벌). 자료 그림은 논문이 적은 숫자를 다시 그린 것이다. 값은 모두 ms/code/ch05 의 입력과 같은 숫자.
  fig-ch05-map-v1       : 중앙아시아의 호수와 강(Natural Earth). 롭노르와 카라쿨은 좌표를 본문에서 확인하지 못해 그리지 않았다.
  fig-ch05-timeline-v1  : 8.7 ka 이후 호수·바다 기록의 단계(논문별)
  fig-ch05-aral2k-v1    : 지난 2천 년 아랄해 수위 단계의 다섯 기록
  fig-ch05-caspian-v1   : 카스피해 1700~1880년 수위 문헌 계열 세 가지
  fig-ch05-kroon-v1     : Kroonenberg 등(2007) 표 1의 석호 시료 보정 연대 범위
사용: GEODIR=/home/claude/book3/geodata python3 figs-ch05.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.environ.setdefault('GEODIR', os.path.join(ROOT, 'geodata'))
sys.path.insert(0, HERE)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geopandas as gpd
from shapely.geometry import box
import mapkit as mk
from mapkit import PAL, use_font, mm_fig, label_audit
FIG = os.path.join(ROOT, 'fig')
CODE = os.path.join(ROOT, 'ms', 'code', 'ch05')
use_font(8.0)

SER = {'color': dict(dry='#9C4F2E', wet='#2F6F9A', mid='#B58B2A', g1='#5B7F3A', g2='#7A5C99', ink='#1B2A33', soft='#4F6E80', grid='#D6DEE2', band='#F1EBDD'),
       'bw': dict(dry='#111111', wet='#BBBBBB', mid='#777777', g1='#444444', g2='#999999', ink='#111111', soft='#444444', grid='#DDDDDD', band='#F2F2F2')}


def save(fig, name, mode):
    w, n = label_audit(fig)
    p = os.path.join(FIG, 'fig-ch05-%s-v1-%s.svg' % (name, mode))
    fig.savefig(p, format='svg', bbox_inches=None)
    plt.close(fig)
    print('%s %-10s 글자 %3d개 경고 %d %s' % (mode, name, n, len(w), w[:4]))
    return w


# ------------------------------------------------------------------ 그림 1: 지도
def fig_map(mode):
    P = PAL[mode]
    proj = '+proj=aea +lat_1=36 +lat_2=50 +lat_0=43 +lon_0=70 +datum=WGS84 +units=m'
    bb = (44.0, 33.0, 98.0, 53.0)
    fig = mm_fig(130, 74)
    ax = fig.add_axes([0.075, 0.10, 0.905, 0.88])
    ax.set_facecolor(P['lake'])
    land = mk.read('ne_10m_land', (bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4))
    land, _ = mk.fix(land)
    land = gpd.clip(land, box(bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4)).to_crs(proj)
    land.plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.4, zorder=2)
    lakes = mk.read('ne_10m_lakes', (bb[0] - 2, bb[1] - 2, bb[2] + 2, bb[3] + 2)).to_crs(proj)
    lakes.plot(ax=ax, color=P['lake'], edgecolor=P['coast'], linewidth=0.3, zorder=3)
    rv = mk.read('ne_10m_rivers_lake_centerlines', bb).to_crs(proj)
    keep = rv[rv['name'].isin(['Amu  Darya', 'Syr  Darya', 'Tarim', 'Volga', 'Ile', 'Ural', 'Konqi', 'Kura', 'Ertix', 'Irtysh'])]
    keep.plot(ax=ax, color=P['river'], linewidth=0.9, zorder=4)
    x0, y0, x1, y1 = mk.proj_bounds(bb, proj)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    mk.graticule(ax, bb, proj, 10, mode)
    mk.edge_ticks(ax, bb, proj, 10, mode)
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, proj, always_xy=True)
    def put(lon, lat, s, dx=0, dy=0, ha='left', bold=False, color=None, size=8):
        x, y = tr.transform(lon, lat)
        mk.label(ax, x, y, s, size=size, ha=ha, dx=dx, dy=dy, mode=mode, bold=bold, color=color)
    def dot(lon, lat, m='o', c=None, s=22):
        x, y = tr.transform(lon, lat)
        ax.scatter([x], [y], s=s, marker=m, color=c or P['hot'], edgecolor=P['text'], linewidth=0.5, zorder=12)
    # 호수 이름(Natural Earth 호수 도형 위)
    names = {'South Aral Sea': ('아랄해', 'right', -6, 4), 'Lake Balkhash': ('발하시호', 'center', 0, 3), 'Issyk-Kul': ('이식쿨', 'left', 6, -2), 'Bosten Hu': ('보스텐호', 'left', 5, -3)}
    ll = mk.read('ne_10m_lakes', (bb[0], bb[1], bb[2], bb[3]))
    for nm, (ko, ha, dx, dy) in names.items():
        g = ll[ll['name'] == nm]
        if len(g):
            c = g.to_crs(proj).geometry.centroid.iloc[0]
            mk.label(ax, c.x, c.y, ko, size=8, ha=ha, dx=dx, dy=dy, mode=mode, bold=True)
            ax.scatter([c.x], [c.y], s=14, marker='o', color=P['hot'], edgecolor=P['text'], linewidth=0.4, zorder=12)
    put(51.0, 42.3, '카스피해', ha='center', bold=True, color=P['soft'], size=8)
    put(60.3, 40.3, '아무다리야', dx=4, dy=-9, ha='left', color=P['soft'])
    put(66.3, 44.6, '시르다리야', dx=5, dy=1, color=P['soft'])
    put(83.8, 40.6, '타림강', dx=0, dy=-9, ha='center', color=P['soft'])
    put(46.7, 48.3, '볼가강 하류', color=P['soft'], dy=7)
    for nm, ko, dx, dy in (('Tashkent', '타슈켄트', 4, -3), ('Almaty', '알마티', 4, 1), ('Ürümqi', '우루무치', 4, 1), ('Kashgar', '카슈가르', -4, -9), ('Tehran', '테헤란', 4, 0), ('Baku', '바쿠', 5, -9)):
        pl = mk.read('ne_10m_populated_places_simple', (40, 28, 100, 56))
        r = pl[pl['name'] == nm]
        if len(r):
            lo, la = r.geometry.iloc[0].x, r.geometry.iloc[0].y
            dot(lo, la, 's', P['text'], 10)
            put(lo, la, ko, dx=dx, dy=dy, ha='right' if dx < 0 else 'left')
    ax.set_aspect('equal'); ax.set_xlabel(''); ax.set_ylabel('')
    for s in ax.spines.values(): s.set_edgecolor(P['frame']); s.set_linewidth(0.6)
    mk.scalebar(ax, 1000, 0.03, 0.04, mode)
    mk.north_arrow(ax, 0.94, 0.80, mode)
    return save(fig, 'map', mode)


# ------------------------------------------------------------------ 그림 2: 단계 연표
def fig_timeline(mode):
    C = SER[mode]
    fig = mm_fig(130, 150)
    ax = fig.add_axes([0.275, 0.075, 0.71, 0.89])
    rows = ['보스텐호 건조기', '이식쿨 (패충류)', '이식쿨 (꽃가루)', '아랄해 얕은 물', '카스피해 남동', '카스피해 중부', '카스피해 터랄리', '롭노르', '카라쿨']
    n = len(rows)
    ypos = {r: n - 1 - i for i, r in enumerate(rows)}
    ax.set_xlim(10.8, -0.2)
    ax.set_ylim(-0.7, n - 0.1)
    ax.set_yticks([ypos[r] for r in rows]); ax.set_yticklabels(rows, fontsize=8, color=C['ink'])
    for xv in range(0, 11):
        ax.axvline(xv, color=C['grid'], lw=0.5, zorder=0)
    ax.set_xticks(range(0, 11)); ax.set_xticklabels([str(i) for i in range(0, 11)], fontsize=8, color=C['soft'])
    ax.set_xlabel('보정 연대(천 년 전, cal ka BP). 왼쪽이 오래된 때', fontsize=8, color=C['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'): ax.spines[s].set_linewidth(0.6)
    def bar(row, a, b, fc, hatch=None, ec=None, h=0.36, alpha=1.0):
        ax.add_patch(Rectangle((b, ypos[row] - h / 2), a - b, h, facecolor=fc, edgecolor=ec or C['ink'], linewidth=0.5, hatch=hatch, alpha=alpha, zorder=3))
    def pt(row, t, m='o', fc=None, s=26):
        ax.scatter([t], [ypos[row]], s=s, marker=m, facecolor=fc or C['dry'], edgecolor=C['ink'], linewidth=0.6, zorder=5)
    def txt(row, x, s, dy=0.30, ha='center'):
        ax.text(x, ypos[row] + dy, s, fontsize=8, ha=ha, va='bottom', color=C['ink'], zorder=6)
    # 보스텐 건조기 (Wunnemann 등 2006)
    for a, b in [(8.5, 8.1), (7.3, 7.1), (5.4, 5.0), (4.6, 4.3), (3.9, 3.6), (3.4, 3.2), (2.6, 2.5), (1.9, 1.1), (0.5, 0.3), (0.18, 0.05)]:
        bar('보스텐호 건조기', a, b, C['dry'])
    pt('보스텐호 건조기', 6.0, 'D')
    # 이식쿨 패충류 (Ricketts 등 2001)
    for a, b, fc, hh in [(8.7, 8.3, C['wet'], None), (8.3, 6.9, C['g1'], None), (6.9, 4.9, C['mid'], '///'), (4.9, 1.0, C['dry'], None)]:
        bar('이식쿨 (패충류)', a, b, fc, hatch=hh)
    ax.text(8.5, ypos['이식쿨 (패충류)'] - 0.55, '', fontsize=8)
    txt('이식쿨 (패충류)', 7.6, '열림·담수', dy=0.22)
    txt('이식쿨 (패충류)', 5.9, '전이', dy=0.22)
    txt('이식쿨 (패충류)', 2.9, '닫힘·안정', dy=0.22)
    # 이식쿨 꽃가루 (Leroy 등 2021)
    bar('이식쿨 (꽃가루)', 10.8, 10.0, C['mid'], hatch='...')
    bar('이식쿨 (꽃가루)', 10.0, 8.0, C['wet'])
    txt('이식쿨 (꽃가루)', 10.4, '낮음', dy=0.22)
    txt('이식쿨 (꽃가루)', 9.0, '수위 상승', dy=0.22)
    # 아랄 (Krivonogov 등 2010)
    for t, e, ha in [(8.0, '26.5 m', 'right'), (7.2, '28 m', 'left'), (5.6, '44 m', 'center'), (4.5, '38 m', 'left')]:
        pt('아랄해 얕은 물', t, 's', C['dry'])
        ax.text(t + (-0.08 if ha == 'left' else (0.08 if ha == 'right' else 0)), ypos['아랄해 얕은 물'] + 0.2, e, fontsize=8, ha=ha, va='bottom', color=C['ink'], zorder=6)
    # 카스피 남동 (Kakroodi 등 2015)
    pt('카스피해 남동', 8.4, 'v'); pt('카스피해 남동', 7.7, 'v')
    ax.text(8.32, ypos['카스피해 남동'] + 0.2, '8.4', fontsize=8, ha='left', va='bottom', color=C['ink'], zorder=6); ax.text(7.62, ypos['카스피해 남동'] + 0.2, '7.7', fontsize=8, ha='left', va='bottom', color=C['ink'], zorder=6)
    bar('카스피해 남동', 3.26, 0.0, C['g2'], hatch='\\\\\\')
    txt('카스피해 남동', 1.6, '5회 이상 순환', dy=0.22)
    # 카스피 중부 (Leroy 등 2014)
    bar('카스피해 중부', 10.55, 4.11, C['wet'])
    txt('카스피해 중부', 7.3, '낮은 염분(고수위)', dy=0.22)
    # 카스피 터랄리 (Kroonenberg 등 2007): 석호 시료 범위 2.0~2.71, 최고수위 2.6
    bar('카스피해 터랄리', 2.71, 2.0, C['wet'])
    pt('카스피해 터랄리', 2.6, '^', C['dry'])
    ax.text(2.35, ypos['카스피해 터랄리'] + 0.26, '2.6 고수위', fontsize=8, ha='center', va='bottom', color=C['ink'], zorder=6)
    # 롭노르 (Wang 등 2026; Mischke 등 2017)
    bar('롭노르', 7.8, 4.0, C['wet'])
    bar('롭노르', 4.0, 1.3, C['dry'], hatch='///')
    pt('롭노르', 8.5, 'o', C['wet'], 24)
    txt('롭노르', 5.9, '습함 7.8~4.0', dy=0.22)
    txt('롭노르', 2.65, '건조화 4.0~1.3', dy=0.22)
    # 카라쿨 (Mischke 등 2010)
    bar('카라쿨', 4.2, 3.5, C['g1'])
    pt('카라쿨', 3.5, 'v', C['dry'])
    ax.text(4.08, ypos['카라쿨'] + 0.22, '따뜻·녹은 물', fontsize=8, ha='left', va='bottom', color=C['ink'], zorder=6)
    # 기준선
    for xv, lab in ((8.2, '8.2'), (4.2, '4.2')):
        ax.axvline(xv, color=C['ink'], lw=0.7, ls=(0, (3, 3)), zorder=1)
    ax.text(8.2, n - 0.14, '8.2', fontsize=8, ha='center', va='bottom', color=C['ink'])
    ax.text(4.2, n - 0.14, '4.2', fontsize=8, ha='center', va='bottom', color=C['ink'])
    import matplotlib.patheffects as pe
    for t in ax.texts:
        t.set_path_effects([pe.withStroke(linewidth=2.2, foreground='#FFFFFF')])
    return save(fig, 'timeline', mode)


# ------------------------------------------------------------------ 그림 3: 지난 2천 년 아랄해
def fig_aral2k(mode):
    C = SER[mode]
    fig = mm_fig(130, 78)
    ax = fig.add_axes([0.225, 0.14, 0.76, 0.84])
    rows = ['K10 (2010)', 'K14 퇴적물', 'K14 고고', 'S06 와편모충', 'S07 꽃가루']
    n = len(rows)
    yp = {r: n - 1 - i for i, r in enumerate(rows)}
    ax.set_xlim(-200, 2050); ax.set_ylim(-0.6, n - 0.35)
    ax.set_yticks(list(yp.values())); ax.set_yticklabels(rows, fontsize=8, color=C['ink'])
    ax.set_xticks([0, 500, 1000, 1500, 2000]); ax.set_xticklabels(['0', '500', '1000', '1500', '2000'], fontsize=8, color=C['soft'])
    ax.set_xlabel('서기(AD). 기원전은 음수', fontsize=8, color=C['soft'])
    for xv in (0, 500, 1000, 1500, 2000): ax.axvline(xv, color=C['grid'], lw=0.5, zorder=0)
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    def bar(r, a, b, kind, label=None):
        fc = C['dry'] if kind == 'L' else C['wet']
        ax.add_patch(Rectangle((a, yp[r] - 0.19), b - a, 0.38, facecolor=fc, edgecolor=C['ink'], linewidth=0.5, hatch='///' if (kind == 'L' and mode == 'bw') else None, zorder=3))
        if label:
            ax.text((a + b) / 2, yp[r] + 0.23, label, fontsize=8, ha='center', va='bottom', color=C['ink'])
    bar('K10 (2010)', 301, 1100, 'H', '52 m'); bar('K10 (2010)', 1101, 1500, 'L', '29 m'); bar('K10 (2010)', 1501, 2000, 'H', '53 m')
    bar('K14 퇴적물', -150, 650, 'L', '약 10 m'); bar('K14 퇴적물', 651, 849, 'H', '52 m'); bar('K14 퇴적물', 850, 1600, 'L', '약 29 m'); bar('K14 퇴적물', 1601, 2000, 'H', '54 m')
    bar('K14 고고', -150, 500, 'L'); bar('K14 고고', 501, 949, 'H'); bar('K14 고고', 950, 1500, 'L'); bar('K14 고고', 1501, 2000, 'H')
    for a, b in [(0, 425), (920, 1230), (1500, 1500), (1600, 1650)]:
        bar('S06 와편모충', a, max(b, a + 12), 'L')
    for a, b in [(0, 400), (900, 1150), (1500, 1650)]:
        bar('S07 꽃가루', a, b, 'L')
    for a, b in [(400, 900), (1150, 1450)]:
        bar('S07 꽃가루', a, b, 'H')
    # 범례
    ax.add_patch(Rectangle((300, -0.5), 60, 0.22, facecolor=C['dry'], edgecolor=C['ink'], linewidth=0.5, hatch='///' if mode == 'bw' else None, clip_on=False))
    ax.text(380, -0.39, '낮음·건조', fontsize=8, va='center', color=C['ink'])
    ax.add_patch(Rectangle((800, -0.5), 60, 0.22, facecolor=C['wet'], edgecolor=C['ink'], linewidth=0.5, clip_on=False))
    ax.text(880, -0.39, '높음·습윤', fontsize=8, va='center', color=C['ink'])
    return save(fig, 'aral2k', mode)


# ------------------------------------------------------------------ 그림 4: 카스피해 문헌 수위
def fig_caspian(mode):
    C = SER[mode]
    d = json.load(open(os.path.join(CODE, 'ch05-caspian-series.json'), encoding='utf-8'))
    fig = mm_fig(130, 82)
    ax = fig.add_axes([0.10, 0.15, 0.86, 0.82])
    ax.set_xlim(1700, 1880); ax.set_ylim(-27.5, -21.3)
    for yv in range(-27, -21): ax.axhline(yv, color=C['grid'], lw=0.5, zorder=0)
    ax.set_xticks(range(1700, 1881, 20)); ax.set_xticklabels([str(v) for v in range(1700, 1881, 20)], fontsize=8, color=C['soft'])
    ax.set_yticks(range(-27, -21)); ax.set_yticklabels([str(v) for v in range(-27, -21)], fontsize=8, color=C['soft'])
    ax.set_ylabel('수위(m, 바다 수준 기준)', fontsize=8, color=C['soft'])
    ax.set_xlabel('연도(AD)', fontsize=8, color=C['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    spec = [('B', 'Bruckner(1890)', 'o', C['dry']), ('K', 'Karpychev(1998, 2001)', 's', C['wet']), ('V', 'Varushchenko 등(1987)', '^', C['mid'] if mode == 'color' else '#FFFFFF')]
    for key, lab, m, fc in spec:
        xs, ys, xe = [], [], []
        for a, b, v in d[key]:
            if b < 1700 or a > 1880: continue
            xs.append((a + b) / 2); ys.append(v); xe.append((b - a) / 2)
        ax.errorbar(xs, ys, xerr=xe, fmt='none', ecolor=C['ink'], elinewidth=0.6, capsize=0, zorder=3)
        ax.scatter(xs, ys, s=24, marker=m, facecolor=fc, edgecolor=C['ink'], linewidth=0.6, zorder=5, label=lab)
    ax.legend(loc='upper right', fontsize=8, frameon=True, framealpha=1.0, edgecolor=C['grid'], borderpad=0.4, handletextpad=0.3)
    return save(fig, 'caspian', mode)


# ------------------------------------------------------------------ 그림 5: Kroonenberg 석호 시료
def fig_kroon(mode):
    C = SER[mode]
    T = [('HV#08b', -24.70, 2603, (2340, 2470)), ('HVDag14a', -27.30, 2747, (2560, 2710)), ('HV#04c', -24.00, 2350, (2020, 2190)),
         ('HV#01a', -26.50, 2373, (2080, 2240)), ('HV#02c', -26.50, 2366, (2050, 2210)), ('HVDag8a', -28.00, 2504, (2210, 2230)),
         ('HVDag9B', -25.15, 2370, (2060, 2240)), ('HVDag1T', -25.25, 2322, (2000, 2140)), ('HVDag10A', -25.55, 2517, (2240, 2390)),
         ('HVDagK', -26.00, 2507, (2210, 2230))]
    T.sort(key=lambda t: t[2])
    fig = mm_fig(130, 78)
    ax = fig.add_axes([0.285, 0.15, 0.665, 0.83])
    n = len(T)
    ax.set_xlim(1900, 2800); ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks(range(n)); ax.set_yticklabels(['%s (%.2f m)' % (t[0], t[1]) for t in T], fontsize=8, color=C['ink'])
    ax.set_xticks(range(1900, 2801, 100)); ax.set_xticklabels([str(v) for v in range(1900, 2801, 100)], fontsize=8, color=C['soft'])
    ax.set_xlabel('보정 연대(cal BP). 논문이 적은 범위', fontsize=8, color=C['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for xv in range(1900, 2801, 100): ax.axvline(xv, color=C['grid'], lw=0.5, zorder=0)
    for i, (nm, el, a14, (a, b)) in enumerate(T):
        grp = 'lo' if a14 < 2400 else ('mid' if a14 < 2700 else 'hi')
        fc = {'lo': C['wet'], 'mid': C['dry'], 'hi': C['mid']}[grp]
        ax.add_patch(Rectangle((a, i - 0.3), b - a, 0.6, facecolor=fc, edgecolor=C['ink'], linewidth=0.5, hatch={'lo': None, 'mid': None, 'hi': '///'}[grp], zorder=3))
    ax.axvline(2600, color=C['ink'], lw=0.9, ls=(0, (4, 3)), zorder=4)
    ax.text(2608, 0.0, '2600', fontsize=8, ha='left', va='center', color=C['ink'])
    for k, (lab, fc, hh) in enumerate((('14C 2300대', C['wet'], None), ('2500대', C['dry'], None), ('2747', C['mid'], '///'))):
        ax.add_patch(Rectangle((2120 + k * 0, 6.2 - 0.0), 0, 0))
    lx = 2290
    for k, (lab, fc, hh) in enumerate((('14C 2300대', C['wet'], None), ('2500대', C['dry'], None), ('2747', C['mid'], '///'))):
        yy = 2.0 - k * 0.8 + 0.4
        ax.add_patch(Rectangle((lx, yy - 0.25), 40, 0.5, facecolor=fc, edgecolor=C['ink'], linewidth=0.5, hatch=hh))
        ax.text(lx + 55, yy, lab, fontsize=8, va='center', ha='left', color=C['ink'])
    return save(fig, 'kroon', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        fig_map(mode); fig_timeline(mode); fig_aral2k(mode); fig_caspian(mode); fig_kroon(mode)
