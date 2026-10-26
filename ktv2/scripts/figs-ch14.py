# -*- coding: utf-8 -*-
"""제2권 14장 그림 4장. 실행: python3 scripts/figs-ch14.py  → fig/fig-ch14-<이름>-v1-color.svg, -bw.svg
  schema : 스키마 도해 (표와 참조 관계)
  grade  : 시연 후보의 증거와 계산 등급 (DB out/demo.db 에서 읽음)
  topo   : 시연 후보의 불확실 반경과 시대 쌍 판정 (좌표는 가상, 지도 배경 없음)
  yibin  : 제1권 10장 시료 좌표(의빈 1·2, 민강 1, 대도하)와 현대 도시, 하천 (mapkit 으로 그린 실제 지도)
그림 속 숫자는 ms/code/ch14 의 DB 와 placekit 으로 이 스크립트가 다시 계산한 값이다. 글자 8pt 이상, 지도의 지명은 한글만."""
import os, sys, math, warnings
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch14'))
import placekit as P
import demorec
K = P.K
import numpy as np
import geopandas as gpd, shapely, shapely.ops
from shapely.geometry import box, Point
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Patch
from matplotlib.lines import Line2D

OUT = K.FIG
WARN = []


def save(fig, name, mode):
    warns, n = K.label_audit(fig)
    WARN.extend('[%s %s] %s' % (name, mode, w) for w in warns)
    p = os.path.join(OUT, 'fig-ch14-%s-v1-%s.svg' % (name, mode))
    fig.savefig(p)
    print('저장 %s (%s B), 글자 %d개, 경고 %d개' % (os.path.basename(p), format(os.path.getsize(p), ','), n, len(warns)))
    plt.close(fig)


def demo_con():
    con = P.connect(':memory:')
    ids = demorec.load(con)
    return con, ids


# ------------------------------------------------------------------ 그림 1: 스키마
def fig_schema(mode):
    Pl = K.PAL[mode]
    K.use_font(8)
    fig = K.mm_fig(130, 96)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 130); ax.set_ylim(0, 96); ax.axis('off')
    cA, cB, cC = (Pl['land'], Pl['lake'], '#FFFFFF') if mode == 'color' else ('#FFFFFF', '#E4E4E4', '#FFFFFF')
    W, H = 36.0, 9.0
    cols = {'A': 4.0, 'B': 47.0, 'C': 90.0}
    box_ = {}

    def B(key, col, yc, en, ko, fc):
        x = cols[col]
        ax.add_patch(Rectangle((x, yc - H / 2), W, H, fc=fc, ec=Pl['frame'], lw=0.8, zorder=3))
        ax.text(x + W / 2, yc + 1.6, en, ha='center', va='center', fontsize=8, fontweight='bold', color=Pl['text'], zorder=4)
        ax.text(x + W / 2, yc - 2.3, ko, ha='center', va='center', fontsize=8, color=Pl['soft'], zorder=4)
        box_[key] = (x, yc)
    for k, c, y, en, ko, fc in [('work', 'A', 80, 'work', '서명', cA), ('section', 'A', 68, 'section', '권·편명', cA), ('edition', 'A', 56, 'edition', '판본', cA),
                                ('passage', 'A', 44, 'passage', '원문 구절', cA), ('variant', 'A', 32, 'variant', '이문(교감)', cA),
                                ('era', 'B', 80, 'era', '시대 창', cB), ('name', 'B', 68, 'name', '이름(글자)', cB), ('name_era', 'B', 56, 'name_era', '이름 x 시대', cB),
                                ('att', 'B', 44, 'attestation', '구절에 나옴', cB), ('chk', 'B', 32, 'check_run', '검사 결과 기록', cB),
                                ('evid', 'C', 68, 'evidence', '증거', cC), ('cand', 'C', 56, 'candidate', '후보 위치', cC), ('rel', 'C', 44, 'relation', '방향·거리 서술', cC)]:
        B(k, c, y, en, ko, fc)

    def arrow(p, q, dashed=False, rad=0.0):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=7, lw=0.8, color=Pl['text'], ls=(0, (3, 2)) if dashed else '-',
                                     connectionstyle='arc3,rad=%g' % rad, zorder=2, shrinkA=0, shrinkB=0))
    def top(k): x, y = box_[k]; return (x + W / 2, y + H / 2)
    def bot(k): x, y = box_[k]; return (x + W / 2, y - H / 2)
    def left(k): x, y = box_[k]; return (x, y)
    def right(k): x, y = box_[k]; return (x + W, y)
    def elbow(pts):
        for a, b in zip(pts[:-2], pts[1:-1]):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=Pl['text'], lw=0.8, zorder=2)
        arrow(pts[-2], pts[-1])
    arrow(top('section'), bot('work')); arrow(top('passage'), bot('edition')); arrow(top('variant'), bot('passage'))
    elbow([(cols['A'], 56), (1.6, 56), (1.6, 80), (cols['A'], 80)])                      # 판본이 서명을 가리킨다
    elbow([(cols['A'] + W, 46.5), (cols['A'] + W + 3.0, 46.5), (cols['A'] + W + 3.0, 68), (cols['A'] + W, 68)])   # 구절이 권·편명을 가리킨다
    arrow(top('name_era'), bot('name')); arrow(top('att'), bot('name_era'))
    elbow([(cols['B'] + W, 58.5), (cols['B'] + W + 3.0, 58.5), (cols['B'] + W + 3.0, 80), (cols['B'] + W, 80)])   # (이름, 시대) 쌍이 시대 창을 가리킨다
    arrow(left('att'), right('passage')); arrow(left('cand'), right('name_era'))
    arrow(bot('evid'), top('cand')); arrow(left('rel'), (cols['B'] + W, 52.0))
    for t, x, y in [('사료 원문 쪽', cols['A'], 90), ('지명 쪽', cols['B'], 90), ('후보와 증거', cols['C'], 90)]:
        ax.text(x + W / 2, y, t, ha='center', va='center', fontsize=8, fontweight='bold', color=Pl['hot'])
    ax.text(cols['C'] + W / 2, 34, '화살표는 "가리킨다"\n(자식 표에서 부모 표로)\n일부 외래 키는 생략', ha='center', va='center', fontsize=8, color=Pl['soft'])
    ax.add_patch(Rectangle((4, 7), 122, 13.5, fc='#FFFFFF', ec=Pl['frame'], lw=0.8, zorder=3, ls=(0, (4, 2))))
    ax.text(65, 16.7, '뷰(질의를 이름 붙여 저장한 것)', ha='center', va='center', fontsize=8, fontweight='bold', color=Pl['text'], zorder=4)
    ax.text(65, 11.3, 'v_cand_grade: 증거에서 등급 계산,  v_grade_inflated: 신고가 높은 후보\nv_mappable: 지도에 찍을 후보,  v_geonames: 다른 책과 주고받는 창구', ha='center', va='center', fontsize=8, color=Pl['soft'], zorder=4, linespacing=1.35)
    return fig


# ------------------------------------------------------------------ 그림 2: 증거와 등급
def fig_grade(mode):
    Pl = K.PAL[mode]
    K.use_font(8)
    con, ids = demo_con()
    rows = con.execute('''SELECT c.cand_id, n.name_ko, e.label, g.grade_computed, c.grade_claimed, g.rank_computed FROM candidate c JOIN name_era ne USING(ne_id) JOIN name n USING(name_id)
                          JOIN era e USING(era_id) JOIN v_cand_grade g USING(cand_id) ORDER BY g.rank_computed DESC, n.name_ko, e.t0, c.cand_id''').fetchall()
    types = ['원문방향거리', '현대지명대응', '좌표', '지형고고', '퇴적증거', '이름일치']
    short = ['원문', '현대', '좌표', '지형', '퇴적', '이름']
    rh, top0 = 4.3, 14.0
    Hmm = top0 + rh * len(rows) + 4
    fig = K.mm_fig(130, Hmm)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 130); ax.set_ylim(Hmm, 0); ax.axis('off')
    x0, cw = 40.0, 10.0
    for j, s in enumerate(short):
        ax.text(x0 + cw * j + cw / 2, top0 - 3.0, s, ha='center', va='bottom', fontsize=8, fontweight='bold', color=Pl['text'])
    ax.text(x0 + cw * 6 + 5.5, top0 - 3.0, '계산', ha='center', va='bottom', fontsize=8, fontweight='bold', color=Pl['text'])
    ax.text(x0 + cw * 6 + 16.5, top0 - 3.0, '신고', ha='center', va='bottom', fontsize=8, fontweight='bold', color=Pl['text'])
    ax.text(2, top0 - 3.0, '이름, 시대', ha='left', va='bottom', fontsize=8, fontweight='bold', color=Pl['text'])
    gcol = {'A': '#2F6F4A', 'B': '#3A7CA5', 'C': '#8A6A2C', '가설': '#9C4F2E'} if mode == 'color' else {'A': '#111111', 'B': '#444444', 'C': '#888888', '가설': '#CCCCCC'}
    inflated = {r[0] for r in con.execute('SELECT cand_id FROM v_grade_inflated')}
    for i, r in enumerate(rows):
        y = top0 + rh * i
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, y), 130, rh, fc=Pl['ocean'] if mode == 'color' else '#F2F2F2', ec='none', zorder=0))
        ax.text(2, y + rh / 2, '%s %s' % (r['name_ko'], r['label']), ha='left', va='center', fontsize=8, color=Pl['text'])
        evs = con.execute('SELECT ev_type, indep_group, support FROM evidence WHERE cand_id=? ORDER BY ev_id', (r['cand_id'],)).fetchall()
        grp = {}
        for e in evs:
            grp.setdefault(e['indep_group'], len(grp) + 1)
        for e in evs:
            j = types.index(e['ev_type'])
            xx = x0 + cw * j + cw / 2
            fc = gcol['C'] if e['ev_type'] != '이름일치' else Pl['grid']
            ax.add_patch(Rectangle((xx - 3.6, y + 0.45), 7.2, rh - 0.9, fc=fc if e['support'] == '지지' else '#FFFFFF', ec=Pl['frame'], lw=0.5, zorder=2))
            ax.text(xx, y + rh / 2, str(grp[e['indep_group']]), ha='center', va='center', fontsize=8, color='#FFFFFF' if (mode == 'color' and e['ev_type'] != '이름일치') or (mode == 'bw' and e['ev_type'] != '이름일치') else Pl['text'], zorder=3)
        gx = x0 + cw * 6 + 5.5
        ax.add_patch(Rectangle((gx - 4.2, y + 0.45), 8.4, rh - 0.9, fc=gcol[r['grade_computed']], ec=Pl['frame'], lw=0.5, zorder=2))
        ax.text(gx, y + rh / 2, r['grade_computed'], ha='center', va='center', fontsize=8, color='#FFFFFF' if r['grade_computed'] in ('A', 'B', 'C') and mode == 'color' or (mode == 'bw' and r['grade_computed'] in ('A', 'B')) else Pl['text'], zorder=3)
        cx = x0 + cw * 6 + 16.5
        infl = r['cand_id'] in inflated
        ax.add_patch(Rectangle((cx - 4.2, y + 0.45), 8.4, rh - 0.9, fc='#FFFFFF', ec=Pl['hot'] if infl else Pl['frame'], lw=1.4 if infl else 0.5, zorder=2))
        ax.text(cx, y + rh / 2, str(r['grade_claimed']), ha='center', va='center', fontsize=8, color=Pl['hot'] if infl else Pl['text'], fontweight='bold' if infl else 'normal', zorder=3)
    return fig


# ------------------------------------------------------------------ 그림 3: 후보 반경과 판정(가상 좌표)
def fig_topo(mode):
    Pl = K.PAL[mode]
    K.use_font(8)
    con, ids = demo_con()
    tr = Transformer.from_crs(4326, '+proj=aeqd +lat_0=6.0 +lon_0=22.5 +datum=WGS84 +units=m', always_xy=True)
    fig = K.mm_fig(130, 92)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_aspect('equal'); ax.axis('off')
    cols = {'가상성': '#9C4F2E', '시연포': '#3A7CA5', '가상포': '#8A6A2C', '예시고을': '#4F7F4A'} if mode == 'color' else {'가상성': '#111111', '시연포': '#555555', '가상포': '#888888', '예시고을': '#333333'}
    ls = {'가상성': '-', '시연포': '--', '가상포': '-.', '예시고을': ':'}
    xs, ys = [], []
    pos = {}
    for nm in ('가상성', '시연포', '가상포', '예시고을'):
        nid = con.execute('SELECT name_id FROM name WHERE name_ko=?', (nm,)).fetchone()[0]
        c = P.referent_clusters(con, nid)
        for ne, lab, t0 in c['eras']:
            for cd in P.cands_of(con, ne):
                if cd['lon'] is None:
                    continue
                x, y = tr.transform(cd['lon'], cd['lat']); x /= 1000; y /= 1000
                pos[(nm, lab)] = (x, y, cd['radius_km'])
                ax.add_patch(Circle((x, y), cd['radius_km'], fc='none', ec=cols[nm], lw=0.9, ls=ls[nm], zorder=3))
                ax.plot(x, y, 'o', ms=3.2, mfc=cols[nm], mec='#FFFFFF', mew=0.5, zorder=5)
                xs += [x - cd['radius_km'], x + cd['radius_km']]; ys += [y - cd['radius_km'], y + cd['radius_km']]
        # 쌍 판정선
        for i, j, v, why, d, gap in c['pairs']:
            a, b = pos.get((nm, c['eras'][i][1])), pos.get((nm, c['eras'][j][1]))
            if a and b and nm in ('가상성', '가상포') and d > 5:
                ax.plot([a[0], b[0]], [a[1], b[1]], color=cols[nm], lw=0.8, ls='-' if v == '겹침' else (0, (2, 2)), zorder=2)
    ax.set_xlim(min(xs) - 25, max(xs) + 25); ax.set_ylim(min(ys) - 35, max(ys) + 25)
    def L(nm, era, s, dx, dy, ha='left'):
        x, y, r = pos[(nm, era)]
        K.label(ax, x, y, s, 8, color=cols[nm], dx=dx, dy=dy, ha=ha, va='bottom', mode=mode, bold=True)
    L('가상성', '가상 1기', '가상성 1기', 0, 4, 'center'); L('가상성', '가상 2기', '가상성 2기·3기', 0, 5, 'center')
    L('시연포', '가상 1기', '시연포 1~3기', 0, 4, 'center'); L('가상포', '가상 1기', '가상포 1기', 0, -22, 'center')
    L('가상포', '가상 2기', '가상포 2기', 0, -22, 'center'); L('가상포', '가상 3기', '가상포 3기', 0, -22, 'center')
    L('예시고을', '가상 1기', '예시고을 1기', 0, -22, 'center')
    def mid(a, b): return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    g1, g2 = pos[('가상성', '가상 1기')], pos[('가상성', '가상 2기')]
    m = mid(g1, g2); K.label(ax, m[0], m[1], '분리 166 km', 8, dx=0, dy=-12, ha='center', va='bottom', mode=mode)
    p1, p2, p3 = pos[('가상포', '가상 1기')], pos[('가상포', '가상 2기')], pos[('가상포', '가상 3기')]
    m = mid(p1, p2); K.label(ax, m[0], m[1], '겹침', 8, dx=0, dy=3, ha='center', va='bottom', mode=mode)
    m = mid(p2, p3); K.label(ax, m[0], m[1], '겹침', 8, dx=0, dy=3, ha='center', va='bottom', mode=mode)
    ax.add_patch(FancyArrowPatch((p1[0], p1[1] + 62), (p3[0], p3[1] + 62), arrowstyle='-', lw=0.8, ls=(0, (2, 2)), color=cols['가상포'], connectionstyle='arc3,rad=-0.25', zorder=2))
    K.label(ax, p2[0], p2[1] + 105, '분리 200 km (사슬)', 8, dx=0, dy=3, ha='center', va='bottom', mode=mode)
    x0_, x1_ = ax.get_xlim(); y0_, y1_ = ax.get_ylim()
    sx, sy = x0_ + 15, y0_ + 18
    ax.plot([sx, sx + 100], [sy, sy], color=Pl['text'], lw=2.0, solid_capstyle='butt', zorder=9)
    K.label(ax, sx, sy, '0', 8, dx=0, dy=3, ha='center', va='bottom', mode=mode); K.label(ax, sx + 100, sy, '100 km', 8, dx=0, dy=3, ha='center', va='bottom', mode=mode)
    # 범례
    ax.text(0.99, 0.985, '원 = 후보와 불확실 반경\n실선 = 겹침, 점선 = 분리\n좌표는 가상(시연값)', transform=ax.transAxes, ha='right', va='top', fontsize=8, color=Pl['soft'], linespacing=1.35)
    return fig


# ------------------------------------------------------------------ 그림 4: 의빈 지도(제1권 10장 좌표)
def fig_yibin(mode):
    Pl = K.PAL[mode]
    K.use_font(8)
    EPSG = 32648
    BBOX = (102.9, 28.2, 105.3, 30.2)
    tr = Transformer.from_crs(4326, EPSG, always_xy=True)
    con = P.connect(':memory:')
    import vol1load as V
    he = dict(V.load_he2015(con))
    def C(lab):
        r = con.execute('SELECT lon, lat FROM candidate WHERE cand_id=?', (he[lab],)).fetchone(); return (r['lon'], r['lat'])
    pad = 0.5
    bb = (BBOX[0] - pad, BBOX[1] - pad, BBOX[2] + pad, BBOX[3] + pad)
    land = gpd.clip(K.read('ne_10m_land', bb), box(*bb))
    lakes = gpd.clip(K.fix(K.read('ne_10m_lakes', bb))[0], box(*bb))
    riv = K.read('ne_10m_rivers_lake_centerlines', bb)
    riv = riv[riv['name'].isin(['Min', 'Dadu', 'Jinsha', 'Chang Jiang', 'Tuo', 'Yalong'])]
    pp = K.read('ne_10m_populated_places_simple', bb)
    x0, y0 = tr.transform(BBOX[0], BBOX[1]); x1, y1 = tr.transform(BBOX[2], BBOX[3])
    W_mm = 130.0
    H_mm = W_mm * (y1 - y0) / (x1 - x0) + 6
    fig = K.mm_fig(W_mm, H_mm)
    ax = fig.add_axes([0.085, 0.01, 0.905, 0.975]); ax.set_facecolor(Pl['land'])
    gpd.GeoSeries(land.geometry, crs=4326).to_crs(EPSG).plot(ax=ax, facecolor=Pl['land'], edgecolor=Pl['coast'], linewidth=0.4, zorder=2)
    gpd.GeoSeries(lakes.geometry, crs=4326).to_crs(EPSG).plot(ax=ax, facecolor=Pl['lake'], edgecolor=Pl['coast'], linewidth=0.3, zorder=3)
    riv.to_crs(EPSG).plot(ax=ax, color=Pl['river'], linewidth=1.0, zorder=4)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.set_xlabel(''); ax.set_ylabel('')
    K.graticule(ax, BBOX, EPSG, 1.0, mode); K.edge_ticks(ax, BBOX, EPSG, 1.0, mode)
    RN = {'Min': ('민강', (104.08, 29.09)), 'Dadu': ('대도하', (103.2, 29.3)), 'Jinsha': ('금사강', (103.8, 28.5)), 'Chang Jiang': ('장강', (105.1, 28.77)), 'Tuo': ('타강', (105.02, 29.45))}
    for en, (ko, (lo, la)) in RN.items():
        g = riv[riv['name'] == en]
        if len(g) == 0:
            continue
        line = shapely.unary_union(list(g.geometry)); a, _ = shapely.ops.nearest_points(line, Point(lo, la)); x, y = tr.transform(a.x, a.y)
        K.label(ax, x, y, ko, 8, color=Pl['river'], dx=4, dy=2, ha='left', mode=mode, style='italic')
    for ko, en, (dx, dy), ha in (('의빈시', 'Yibin', (6, -12), 'left'), ('낙산시', 'Leshan', (14, -52), 'left'), ('자공시', 'Zigong', (5, -2), 'left'), ('성도시', 'Chengdu', (5, -2), 'left')):
        r = pp[pp['name'] == en]
        if len(r) == 0:
            continue
        x, y = tr.transform(r.iloc[0].longitude, r.iloc[0].latitude)
        if x0 < x < x1 and y0 < y < y1:
            ax.plot(x, y, 's', ms=3.6, mfc='#FFFFFF', mec=Pl['text'], mew=0.9, zorder=12)
            K.label(ax, x, y, ko, 8, dx=dx, dy=dy, ha=ha, mode=mode, **({'arrowprops': dict(arrowstyle='-', lw=0.6, color=Pl['text'], shrinkA=0, shrinkB=2)} if en == 'Leshan' else {}))
    pts = {'의빈 1': C('의빈 1'), '의빈 2': C('의빈 2'), '대도하': C('대도하'), '민강 1': C('민강 1')}
    X = {k: tr.transform(*v) for k, v in pts.items()}
    d12 = P.hav(pts['의빈 1'], pts['의빈 2']); d1d = P.hav(pts['의빈 1'], pts['대도하'])
    ax.plot([X['의빈 1'][0], X['의빈 2'][0]], [X['의빈 1'][1], X['의빈 2'][1]], color=Pl['hot'], lw=1.0, ls=(0, (4, 2)), zorder=8)
    m = ((X['의빈 1'][0] + X['의빈 2'][0]) / 2, (X['의빈 1'][1] + X['의빈 2'][1]) / 2)
    K.label(ax, m[0], m[1], '%.1f km' % d12, 8, color=Pl['hot'], bold=True, dx=6, dy=2, ha='left', mode=mode)
    arr = dict(arrowstyle='-', lw=0.6, color=Pl['text'], shrinkA=0, shrinkB=2)
    for k, mk in (('의빈 1', 'o'), ('의빈 2', 'o'), ('대도하', 'D')):
        ax.plot(*X[k], mk, ms=4.6, mfc=Pl['hot'] if k != '대도하' else Pl['text'], mec='#FFFFFF', mew=0.6, zorder=14)
    ax.plot(*X['민강 1'], 'o', ms=8.5, mfc='none', mec=Pl['text'], mew=0.9, zorder=13)
    K.label(ax, X['의빈 1'][0], X['의빈 1'][1], '시료 의빈 1과 민강 1(좌표 같음)', 8, dx=-30, dy=22, ha='right', mode=mode, bold=True, arrowprops=arr)
    K.label(ax, X['대도하'][0], X['대도하'][1], '시료 대도하', 8, dx=-40, dy=-6, ha='right', mode=mode, bold=True, arrowprops=arr)
    K.label(ax, X['의빈 2'][0], X['의빈 2'][1], '시료 의빈 2', 8, dx=10, dy=22, ha='left', mode=mode, bold=True, arrowprops=arr)
    K.scalebar(ax, 50, 0.04, 0.05, mode); K.north_arrow(ax, 0.93, 0.80, mode)
    return fig, dict(d12=d12, d1d=d1d)


def main():
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        save(fig_schema(mode), 'schema', mode)
        save(fig_grade(mode), 'grade', mode)
        save(fig_topo(mode), 'topo', mode)
        f, info = fig_yibin(mode)
        save(f, 'yibin', mode)
    print('거리(DB 후보 좌표에서 다시 계산): 의빈 1-의빈 2 %.1f km, 의빈 1-대도하 %.1f km' % (info['d12'], info['d1d']))
    print('글자 검사 경고 합계 %d개' % len(WARN))
    for w in WARN:
        print('  ', w)


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        main()
