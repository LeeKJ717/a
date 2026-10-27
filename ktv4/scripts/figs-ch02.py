# -*- coding: utf-8 -*-
"""2장 「빙핵의 1만 년」 그림 생성: fig/fig-ch02-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book4): python3 scripts/figs-ch02.py
자료 그림은 파일(GISP2 d18O, EDC 중수소와 온도)과 논문 숫자를 다시 그린 것이다. 숫자의 출처와 계산은 ms/code/ch02/ 의 로그에 있다.
지도의 점 좌표는 이 장이 확인한 값(위키백과 '빙핵 목록'과 NOAA 기록)이며, 지도 위 글자는 번호만 쓰고 이름은 캡션에 쓴다. 글자 8pt 이상, 색과 흑백 두 벌.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch02'))
import figkit12 as F
from figkit12 import plt, np, C, HATCH
import mapkit as K
import geopandas as gpd
from shapely.geometry import box
from pyproj import Transformer
from io2 import gisp2, edc
FS = 8.0
plt.rcParams['mathtext.default'] = 'regular'
g = gisp2(); e = edc()


def P_(mode): return C[mode]


# ---------------------------------------------------------------- 그림 2-1 지도
GL = [(1, 77 + 10 / 60, -(61 + 8 / 60)), (2, 65 + 11 / 60, -(43 + 50 / 60)), (3, 72 + 34 / 60 + 44.4 / 3600, -(37 + 33 / 60 + 55.2 / 3600)),
      (4, 75 + 6 / 60, -(42 + 18 / 60)), (5, 77 + 27 / 60, -(51 + 4 / 60)), (6, 71 + 18 / 60, -(26 + 42 / 60))]
AN = [(1, -(78 + 28 / 60), 106 + 48 / 60), (2, -75.1, 123.4), (3, -79.468, -112.086), (4, -(66 + 46 / 60), 112 + 48 / 60), (5, -(64 + 13 / 60), -(57 + 41 / 60))]


def fig_map(mode):
    P = K.PAL[mode]; Q = C[mode]
    f = F.fig(130, 78)
    land50 = K.read('ne_50m_land')
    for k, (crs, bb, pts, ax_rect, off) in enumerate((
            ('EPSG:3413', (-85, 55, 0, 85), GL, [0.01, 0.02, 0.47, 0.90], {1: (6, 5), 2: (6, -10), 3: (-12, 4), 4: (-12, -4), 5: (-11, 3), 6: (6, 3)}),
            ('EPSG:3031', (-180, -90, 180, -62), AN, [0.51, 0.02, 0.48, 0.90], {1: (6, -3), 2: (6, 3), 3: (-12, -2), 4: (6, 4), 5: (-12, 4)}))):
        ax = f.add_axes(ax_rect); ax.set_facecolor(P['ocean'])
        tr = Transformer.from_crs(4326, crs, always_xy=True)
        gl = gpd.clip(land50, box(*bb)).to_crs(crs)
        if k == 0:
            gl.plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.5)
            from shapely.ops import unary_union
            polys = [p for geom in gl.geometry for p in (geom.geoms if hasattr(geom, 'geoms') else [geom])]
            gx, gy = tr.transform(-40, 72)
            main = [p for p in polys if p.contains(__import__('shapely').geometry.Point(gx, gy))]
            gbounds = main[0].bounds if main else gl.total_bounds
        else:
            gl.plot(ax=ax, color=P['land'], edgecolor='none', linewidth=0)
            for geom in land50.geometry:
                for p in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
                    if p.bounds[3] < -60:
                        xy = np.array(p.exterior.coords)
                        seam = (np.abs(xy[:, 0]) >= 179.999) | (xy[:, 1] <= -89.99)
                        X, Y = tr.transform(xy[:, 0], xy[:, 1])
                        a, b = 0, 0
                        for i in range(len(xy) - 1):
                            if seam[i] and seam[i + 1]: continue
                            ax.plot(X[i:i + 2], Y[i:i + 2], color=P['coast'], lw=0.5, zorder=3)
                    
            gbounds = gl.total_bounds
        if k == 0:
            for lon in range(-70, -9, 10):
                x, y = tr.transform(np.full(30, lon), np.linspace(60, 83.5, 30)); ax.plot(x, y, color=P['grid'], lw=0.4, ls=(0, (4, 3)), zorder=1)
            for lat in (65, 70, 75, 80):
                x, y = tr.transform(np.linspace(-72, -10, 60), np.full(60, lat)); ax.plot(x, y, color=P['grid'], lw=0.4, ls=(0, (4, 3)), zorder=1)
            xb = gbounds
            pad = 60000
            ax.set_xlim(xb[0] - pad, xb[2] + pad); ax.set_ylim(xb[1] - pad, xb[3] + pad)
        else:
            for lat in (-70, -80):
                x, y = tr.transform(np.linspace(-180, 180, 200), np.full(200, lat)); ax.plot(x, y, color=P['grid'], lw=0.4, ls=(0, (4, 3)), zorder=1)
            for lon in range(-180, 180, 30):
                x, y = tr.transform(np.full(20, lon), np.linspace(-90, -62, 20)); ax.plot(x, y, color=P['grid'], lw=0.4, ls=(0, (4, 3)), zorder=1)
            xb = gbounds; pad = 120000
            ax.set_xlim(xb[0] - pad, xb[2] + pad); ax.set_ylim(xb[1] - pad, xb[3] + pad)
        for n, la, lo in pts:
            x, y = tr.transform(lo, la)
            ax.scatter([x], [y], s=95, marker='o', facecolor='#FFFFFF', edgecolor=P['text'], linewidth=1.0, zorder=10)
            ax.text(x, y, str(n), ha='center', va='center', fontsize=FS, fontweight='bold', color=P['text'], zorder=11)
        ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
        for s in ax.spines.values(): s.set_color(P['frame'])
        ax.text(0.02, 0.03 if k == 0 else 0.98, '그린란드' if k == 0 else '남극', transform=ax.transAxes, fontsize=FS + 0.5, fontweight='bold', color=P['text'], ha='left', va='bottom' if k == 0 else 'top')
    return f


# ---------------------------------------------------------------- 그림 2-2 GISP2 d18O 전체
def fig_gisp2(mode):
    Q = C[mode]
    f = F.fig(130, 66); ax = f.add_axes([0.095, 0.17, 0.89, 0.78]); F.style_ax(ax, mode, grid='y')
    m = (g.age >= -50) & (g.age <= 13500)
    ax.plot(g.age[m] / 1000, g.d18o[m], color=Q['soft'], lw=0.7, zorder=3)
    edges = np.arange(0, 13, 1)
    cs = []; vs = []
    for a in edges:
        s = g[(g.age >= a * 1000) & (g.age < (a + 1) * 1000)]
        ax.plot([a, a + 1], [s.d18o.mean()] * 2, color=Q['acc'], lw=1.8, zorder=5, solid_capstyle='butt')
    ax.axvspan(8.119, 8.256 + 0.019, color=Q['grid'], zorder=1)
    ax.axvline(11.608, color=Q['ink'], lw=0.7, ls=(0, (3, 2)), zorder=2)
    ax.text(11.85, -33.3, '영거 드라이아스 끝', fontsize=FS, color=Q['ink'], ha='right', va='bottom')
    ax.text(8.75, -42.0, '8.2 ka 사건', fontsize=FS, color=Q['ink'], ha='left', va='bottom')
    ax.set_xlim(13.5, -0.1); ax.set_ylim(-42.6, -32.8)
    ax.set_xlabel('나이 (천 년 전, 1950 기준, 이 파일의 눈금)', fontsize=FS); ax.set_ylabel('δ$^{18}$O (‰)', fontsize=FS)
    return f


# ---------------------------------------------------------------- 그림 2-3 8.2 ka 사건 확대
def fig_event(mode):
    Q = C[mode]
    f = F.fig(130, 66); ax = f.add_axes([0.11, 0.17, 0.865, 0.78]); F.style_ax(ax, mode, grid='y')
    m = (g.age >= 7600) & (g.age <= 9200)
    ax.plot(g.age[m], g.d18o[m], color=Q['soft'], lw=0.8, zorder=3)
    ax.scatter(g.age[m], g.d18o[m], s=9, color=Q['ink'], zorder=4)
    base = g[(g.age >= 8400) & (g.age <= 9400)].d18o; mu = base.mean(); sd = base.std(ddof=1)
    ax.axhline(mu, color=Q['acc'], lw=1.0, zorder=2)
    ax.axhline(mu - sd, color=Q['acc'], lw=0.8, ls=(0, (4, 2)), zorder=2)
    ax.axhline(mu - 2 * sd, color=Q['acc'], lw=0.8, ls=(0, (1, 2)), zorder=2)
    ax.axvspan(8119, 8256 + 19, color=Q['grid'], zorder=1)
    from matplotlib.lines import Line2D
    hs = [Line2D([0], [0], color=Q['acc'], lw=1.0), Line2D([0], [0], color=Q['acc'], lw=0.8, ls=(0, (4, 2))), Line2D([0], [0], color=Q['acc'], lw=0.8, ls=(0, (1, 2)))]
    ax.legend(hs, ['8.4~9.4 ka 기준선 평균 −34.58', '평균 −1 표준편차', '평균 −2 표준편차'], loc='lower left', frameon=True, framealpha=1.0, edgecolor=Q['grid'], fontsize=FS, handlelength=2.2)
    ax.text(8190, -33.15, '묶음 8119~8256 (8개 표본)', fontsize=FS, color=Q['ink'], ha='center', va='bottom')
    ax.set_xlim(9200, 7600); ax.set_ylim(-36.9, -33.0)
    ax.set_xlabel('나이 (년 전, 1950 기준)', fontsize=FS); ax.set_ylabel('δ$^{18}$O (‰)', fontsize=FS)
    return f


# ---------------------------------------------------------------- 그림 2-4 영거 드라이아스 끝 계단과 연대 표시
def fig_ramp(mode):
    Q = C[mode]
    f = F.fig(130, 88); ax = f.add_axes([0.095, 0.12, 0.89, 0.50]); F.style_ax(ax, mode, grid='y')
    m = (g.age >= 10800) & (g.age <= 12800)
    ax.plot(g.age[m], g.d18o[m], color=Q['soft'], lw=0.8, zorder=3)
    ax.scatter(g.age[m], g.d18o[m], s=9, color=Q['ink'], zorder=4)
    t0, dur, hi, lo = 11586, 44, -36.74, -40.53
    xs = np.array([10800, t0, t0 + dur, 12800]); ys = np.array([hi, hi, lo, lo])
    ax.plot(xs, ys, color=Q['acc'], lw=1.5, zorder=5)
    ax.set_xlim(12800, 10800); ax.set_ylim(-42.0, -35.2)
    ax.set_ylabel('δ$^{18}$O (‰)', fontsize=FS); ax.tick_params(labelbottom=False)
    ax.text(11610, -42.0 + 0.2, '이 책의 램프 맞춤 중점 11,608 BP', fontsize=FS, color=Q['acc'], ha='left', va='bottom')
    # 위쪽 작은 축: 논문이 적은 홀로세 시작 연대(b2k 에서 50을 빼 BP 로)
    ax2 = f.add_axes([0.095, 0.69, 0.89, 0.29]); F.style_ax(ax2, mode, grid=None)
    ax2.set_xlim(12800, 10800); ax2.set_ylim(-0.7, 4)
    rows = [(3.2, 11651 - 50, 13, 'NGRIP δ$^{18}$O 11,651 ± 13 b2k'), (2.2, 11690 - 50, 0, 'GISP2 경계 11,690 b2k'), (1.2, 11701 - 50, 1.5, '중수소 과잉 11,701 ± 1.5 b2k'), (0.2, 11703 - 50, 99, 'GICC05 11,703 ± 99 b2k')]
    for y0, x0, err, lab in rows:
        ax2.errorbar([x0], [y0 + 0.2], xerr=[err] if err else None, fmt='o', ms=3, color=Q['ink'], capsize=1.5, lw=0.8)
        ax2.text(12780, y0 + 0.2, lab, fontsize=FS, color=Q['ink'], ha='left', va='center')
    ax2.set_yticks([]); ax2.spines['left'].set_visible(False)
    ax2.tick_params(labelbottom=False)
    ax3 = f.add_axes([0.095, 0.0, 0.89, 0.0001]); ax3.axis('off')
    ax.set_xlabel('나이 (년 전, 1950 기준; b2k 값은 50을 빼서 옮김)', fontsize=FS); ax.tick_params(labelbottom=True)
    return f


# ---------------------------------------------------------------- 그림 2-5 계단의 온도 환산
def fig_slope(mode):
    Q = C[mode]
    f = F.fig(130, 62); ax = f.add_axes([0.40, 0.17, 0.57, 0.78]); F.style_ax(ax, mode, grid='x')
    d = 5.55
    items = [('현재 공간 기울기 0.69‰/K', d / 0.69, None, False), ('레일리 모형 0.88‰/K', d / 0.88, None, False), ('Cuffey와 Clow, 8 ka 이전\n3.05 °C/‰', d * 3.05, None, False),
             ('Cuffey와 Clow, 8~3 ka\n3.98 °C/‰ (이 나이에는 범위 밖)', d * 3.98, None, True), ('Buizert 등, GISP2\n홀로세 전이 12.4 ± 3.4 °C', 12.4, 3.4, False)]
    for i, (lab, v, err, out) in enumerate(items):
        col = Q['a'] if i < 2 else (Q['b'] if i < 4 else Q['c'])
        ax.barh(i, v, color=col, edgecolor=Q['ink'], lw=0.5, height=0.6, hatch='////' if (mode == 'bw' and out) else None, alpha=0.55 if out else 1.0, zorder=3)
        if err: ax.errorbar([v], [i], xerr=[err], fmt='none', ecolor=Q['ink'], capsize=3, lw=1.0, zorder=5)
        ax.text(v + (err or 0) + 0.4, i, '%.1f K' % v, fontsize=FS, va='center', ha='left', color=Q['ink'])
    ax.set_yticks(range(len(items))); ax.set_yticklabels([x[0] for x in items], fontsize=FS); ax.invert_yaxis()
    ax.set_xlim(0, 29); ax.set_xlabel('같은 δ$^{18}$O 계단 5.55‰ 에 대응하는 온도 변화 (K)', fontsize=FS)
    return f


# ---------------------------------------------------------------- 그림 2-6 최대 계수 오차
def fig_mce(mode):
    Q = C[mode]
    f = F.fig(130, 62)
    ax = f.add_axes([0.085, 0.17, 0.50, 0.78]); F.style_ax(ax, mode, grid='y')
    pts = [(8236, 47, '8.2 ka 경계'), (10347, 89, '사크순바튼'), (11703, 99, '홀로세 시작'), (12171, 114, '베데'), (14692, 186, 'GI-1e')]
    x = np.array([p[0] for p in pts]) / 1000; y = np.array([p[1] for p in pts])
    ax.plot([0, 15], [0, 0.0057 * 15000], color=Q['grid'], lw=1.0, zorder=1)
    ax.scatter(x, y, s=22, color=Q['acc'], zorder=4)
    for (xx, yy, lab), dx, dy, ha in zip(pts, (6, -5, -5, 5, -5), (-2, 6, 8, -2, 7), ('left', 'right', 'right', 'left', 'right')):
        ax.annotate(lab, (xx / 1000, yy), xytext=(dx, dy), textcoords='offset points', fontsize=FS, color=Q['ink'], ha=ha, va='bottom' if dy > 0 else 'top')
    ax.text(14.6, 0.0057 * 14600 - 14, '0.57% 선', fontsize=FS, color=Q['soft'], ha='right', va='top')
    ax.set_xlim(7.5, 15.2); ax.set_ylim(0, 215)
    ax.set_xlabel('나이 (천 년 전, b2k)', fontsize=FS); ax.set_ylabel('논문의 최대 계수 오차 (년)', fontsize=FS)
    ax2 = f.add_axes([0.70, 0.17, 0.28, 0.78]); F.style_ax(ax2, mode, grid='y')
    w = 0.36
    ax2.bar(np.arange(2) - w / 2, [47, 99], width=w, color=Q['acc'], edgecolor=Q['ink'], lw=0.5, label='MCE', zorder=3)
    ax2.bar(np.arange(2) + w / 2, [9.7, 14.1], width=w, color=Q['mid'], edgecolor=Q['ink'], lw=0.5, label='독립 가정 2σ', zorder=3, hatch='////' if mode == 'bw' else None)
    for i, (a, b) in enumerate(((47, 9.7), (99, 14.1))):
        ax2.text(i - w / 2, a + 2, '%d' % a, fontsize=FS, ha='center', va='bottom', color=Q['ink'])
        ax2.text(i + w / 2, b + 2, '%.1f' % b, fontsize=FS, ha='center', va='bottom', color=Q['ink'])
    ax2.set_xticks([0, 1]); ax2.set_xticklabels(['8236', '11,703'], fontsize=FS)
    ax2.set_ylim(0, 150); ax2.set_xlabel('나이 (b2k)', fontsize=FS)
    ax2.legend(frameon=False, fontsize=FS, loc='upper left', handlelength=1.2)
    return f


# ---------------------------------------------------------------- 그림 2-7 EDC 홀로세
def fig_edc(mode):
    Q = C[mode]
    f = F.fig(130, 84)
    ax = f.add_axes([0.095, 0.55, 0.89, 0.41]); F.style_ax(ax, mode, grid='y')
    lm = e[e.age <= 1000]; dD0 = lm.dD.mean()
    m = (e.age <= 16000)
    simple = (e.dD - dD0) / 6.04
    ax.plot(e.age[m] / 1000, simple[m], color=Q['mid'], lw=0.8, zorder=2)
    ax.plot(e.age[m] / 1000, e['T'][m], color=Q['ink'], lw=0.8, zorder=3)
    ax.axvline(11.7, color=Q['grid'], lw=1.0, zorder=1)
    ax.set_xlim(16, 0); ax.set_ylim(-9, 7.0)
    ax.set_ylabel('온도 변화 (°C)', fontsize=FS); ax.tick_params(labelbottom=False)
    ax.text(15.8, 6.6, '검은 선: 파일의 온도  회색 선: 중수소를 6.04‰/°C 로 나눈 값', fontsize=FS, color=Q['ink'], ha='left', va='top')
    ax2 = f.add_axes([0.095, 0.14, 0.89, 0.31]); F.style_ax(ax2, mode, grid='y')
    diff = e['T'] - simple
    ax2.plot(e.age[m] / 1000, diff[m], color=Q['acc'], lw=1.2)
    ax2.axvline(11.7, color=Q['grid'], lw=1.0, zorder=1)
    ax2.set_xlim(16, 0); ax2.set_ylim(-2.3, 0.1)
    ax2.set_xlabel('나이 (천 년 전, EDC3 눈금)', fontsize=FS); ax2.set_ylabel('파일 − 단순 환산 (°C)', fontsize=FS)
    return f


# ---------------------------------------------------------------- 그림 2-8 서술된 최적기 구간
def fig_windows(mode):
    Q = C[mode]
    f = F.fig(130, 78); ax = f.add_axes([0.40, 0.14, 0.57, 0.82]); F.style_ax(ax, mode, grid='x')
    W = [('그린란드 NorthGRIP (Johnsen 2001)', 8.6, 4.3, 0), ('그린란드 네 지점 (Vinther 2009)', 9.0, 6.0, 0), ('남극 11개 코어, 초기 (Masson 2000)', 11.5, 9.0, 1),
         ('로스해 쪽 2차 (Masson 2000)', 7.0, 5.0, 1), ('동남극 후기 (Masson 2000)', 6.0, 3.0, 1), ('제임스 로스섬 (Mulvaney 2012)', 9.2, 2.5, 1)]
    for i, (lab, a, b, k) in enumerate(W):
        ax.barh(i, a - b, left=b, height=0.55, color=Q['wet'] if k == 0 else Q['dry'], edgecolor=Q['ink'], lw=0.5, hatch=HATCH[mode]['wet'] if (k == 0 and mode == 'bw') else None, zorder=3)
    ax.axvline(8.236, color=Q['ink'], lw=0.8, ls=(0, (3, 2)), zorder=4)
    ax.axvline(11.7, color=Q['ink'], lw=0.8, ls=(0, (1, 2)), zorder=4)
    ax.text(8.236, -0.62, '8.2', fontsize=FS, ha='center', va='bottom', color=Q['ink'], zorder=8, bbox=dict(fc='#FFFFFF', ec='none', pad=0.6))
    ax.text(11.7, -0.62, '11.7', fontsize=FS, ha='center', va='bottom', color=Q['ink'], zorder=8, bbox=dict(fc='#FFFFFF', ec='none', pad=0.6))
    ax.set_yticks(range(len(W))); ax.set_yticklabels(['%s\n%.1f~%.1f ka' % (w[0], w[1], w[2]) for w in W], fontsize=FS); ax.invert_yaxis()
    ax.set_xlim(13.6, 2); ax.set_ylim(5.6, -0.95)
    ax.set_xlabel('나이 (천 년 전, 논문마다 기준이 다름)', fontsize=FS)
    return f


FIGS = [('ch02-map', fig_map), ('ch02-gisp2', fig_gisp2), ('ch02-event', fig_event), ('ch02-ramp', fig_ramp), ('ch02-slope', fig_slope), ('ch02-mce', fig_mce), ('ch02-edc', fig_edc), ('ch02-windows', fig_windows)]
if __name__ == '__main__':
    only = sys.argv[1:]
    for name, fn in FIGS:
        if only and name not in only: continue
        for mode in ('color', 'bw'):
            F.save(fn(mode), name, mode)
