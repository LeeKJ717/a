# -*- coding: utf-8 -*-
"""6장 그림(색·흑백 SVG 두 벌). 자료 그림은 논문이 적은 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다.
  fig-ch06-map   : 이 장이 읽은 기록 중 좌표를 확인한 지점(서아프리카 연안 코어, 카리아코 분지)
  fig-ch06-insol : 일사 문턱 시연(계산 6-1)과 종료 연대 띠
  fig-ch06-term  : 습윤기 종료 연대(계산 6-3)
  fig-ch06-core  : ODP 658C 플럭스와 시료 해상도(계산 6-2)
  fig-ch06-dongge: 둥거 동굴 사건 연대와 간격(계산 6-5)
사용(작업 폴더 /home/claude/book4): PREVDIR=<미리보기 폴더> python3 scripts/figs-ch06.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as F
import mapkit as K
import geopandas as gpd
from shapely.geometry import box
from matplotlib.patches import Rectangle
plt = F.plt
C = F.C
FS = 8.0
MODES = ('color', 'bw')


def sty(ax, mode, grid='y'):
    F.style_ax(ax, mode, grid)


# ---------------------------------------------------------------- 지도
SITES = [(1, '카리아코 분지 ODP 1002', -65.1698, 10.7123), (2, 'ODP 658(모리타니 앞바다)', -18.583, 20.75),
         (3, 'GC68', -17.282, 19.363), (4, 'GC49', -17.854, 23.206), (5, 'GC37', -15.118, 26.816), (6, 'GC27', -10.63, 30.88)]


def fig_map(mode):
    P = K.PAL[mode]
    bb = (-78, 4, -2, 40)
    f = F.fig(130, 88)
    ax = f.add_axes([0.14, 0.25, 0.84, 0.73])
    ax.set_facecolor(P['ocean'])
    land = gpd.clip(K.read('ne_10m_land', bb), box(*bb))
    land.plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.5)
    ax.set_xlim(bb[0], bb[2]); ax.set_ylim(bb[1], bb[3]); ax.set_xlabel(''); ax.set_ylabel('')
    ax.set_aspect(1/np.cos(np.radians(22)))
    for lo in range(-70, 0, 10):
        ax.axvline(lo, color=P['grid'], lw=0.4, zorder=1)
    for la in range(10, 40, 10):
        ax.axhline(la, color=P['grid'], lw=0.4, zorder=1)
    ax.set_xticks(range(-70, 0, 10)); ax.set_xticklabels(['서경 %d°' % -v for v in range(-70, 0, 10)], fontsize=FS, color=P['soft'])
    ax.set_yticks(range(10, 40, 10)); ax.set_yticklabels(['북위 %d°' % v for v in range(10, 40, 10)], fontsize=FS, color=P['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ax.spines.values(): s.set_color(P['frame'])
    for n, nm, lo, la in SITES:
        ax.scatter([lo], [la], s=95, marker='o', facecolor='#FFFFFF', edgecolor=P['text'], linewidth=1.1, zorder=10)
        ax.text(lo, la, str(n), ha='center', va='center', fontsize=FS, fontweight='bold', color=P['text'], zorder=11)
    K.label(ax, -48, 32, '대서양', size=FS, color=P['soft'], ha='center', va='center', mode=mode, bold=True)
    K.label(ax, -8, 17, '사하라', size=FS, color=P['soft'], ha='center', va='center', mode=mode, bold=True)
    K.label(ax, -60, 7, '남아메리카', size=FS, color=P['soft'], ha='center', va='center', mode=mode, bold=True)
    K.label(ax, -75, 20, '카리브해', size=FS, color=P['soft'], ha='left', va='center', mode=mode, bold=True)
    key = ['1 카리아코 분지 ODP 1002 (Haug 등)', '2 ODP 658 (deMenocal 등)', '3~6 GC68, GC49, GC37, GC27 (Tierney 등)']
    for i, t in enumerate(key):
        f.text(0.03, 0.135 - 0.052*i, t, fontsize=FS, color=P['text'], ha='left', va='center')
    F.save(f, 'ch06-map', mode)


# ---------------------------------------------------------------- 일사 시연
def fig_insol(mode):
    P = C[mode]
    f = F.fig(130, 78)
    ax = f.add_axes([0.10, 0.17, 0.87, 0.78])
    t = np.linspace(0, 13, 600)
    pk, thr = 8.0, 100*(470-451)/451
    def sinus(Pd, T):
        c0 = np.cos(2*np.pi*T/Pd); A = pk/(1-c0)
        return A*(np.cos(2*np.pi*(t-T)/Pd)-c0)
    ax.axhline(thr, color=P['ink'], lw=0.8, ls=(0, (4, 3)), zorder=2)
    ax.text(12.7, thr+0.18, '문턱 +4.2 % (470 W/m²)', ha='left', va='bottom', fontsize=FS, color=P['ink'])
    ax.add_patch(Rectangle((5.49-0.19, -1), 0.38, 10, facecolor=P['mid'], alpha=0.45, edgecolor='none', zorder=1))
    ax.text(5.49, 8.55, '코어의 종료 5.49 ± 0.19 ka', ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ls = {19.0: ('-', P['a']), 21.0: ('-', P['b']), 23.0: ('-', P['d'])}
    for Pd, (l, c) in ls.items():
        y = sinus(Pd, 10.5)
        m = t <= 10.5
        ax.plot(t[t >= 0], y, color=c, lw=1.2 if Pd == 21.0 else 0.9, ls=l if mode == 'color' else {19.0: ':', 21.0: '-', 23.0: '--'}[Pd], zorder=4, label='정현파, 세차 %d ka' % Pd)
    ax.plot([0, 10.5], [0, 8], color=P['ink'], lw=0.8, ls='-.', zorder=3, label='직선 감소')
    ax.set_xlim(13, 0); ax.set_ylim(-0.6, 9.6)
    ax.set_xlabel('시간(ka, 왼쪽이 오래된 때)', fontsize=FS, color=P['soft'])
    ax.set_ylabel('현재 대비 일사(%)', fontsize=FS, color=P['soft'])
    sty(ax, mode)
    ax.legend(loc='lower left', fontsize=FS, frameon=False)
    F.save(f, 'ch06-insol', mode)


# ---------------------------------------------------------------- 종료 연대
def fig_term(mode):
    P = C[mode]
    f = F.fig(130, 88)
    ax = f.add_axes([0.34, 0.15, 0.63, 0.80])
    rows = [('Kuper와 Kröpelin(2006)\n이집트 사하라(고고, 달력 환산)', 7249, None, 'c'),
            ('Tierney 등(2017) 31°N', 6500, None, 'a'),
            ('Tierney 등(2017) 19~27°N 셋', None, (5000, 5300, 5300), 'a'),
            ('deMenocal 등(2000) 연안 코어', 5490, 190, 'b'),
            ('Haug 등(2001) 카리아코\n건조 경향 시작', 5400, None, 'd'),
            ('Claussen 등(1999) 모형 앙상블', 5440, 30, 'e')]
    n = len(rows)
    for i, (nm, v, e, key) in enumerate(rows):
        y = n-1-i
        col = P[key]
        if isinstance(e, tuple) or v is None:
            for k, vv in enumerate(e):
                ax.scatter([vv], [y + (0.16 if (k == 2) else 0)], s=26, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=4)
        else:
            ax.scatter([v], [y], s=30, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=4)
            if e: ax.errorbar([v], [y], xerr=[e], color=P['ink'], lw=0.9, capsize=2.5, zorder=3)
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=FS, color=P['ink'])
    ax.set_xlim(7700, 4700); ax.set_ylim(-0.7, n-0.3)
    ax.set_xlabel('종료 연대(cal BP, 왼쪽이 오래된 때)', fontsize=FS, color=P['soft'])
    sty(ax, mode, grid='x')
    ax.axvline(5490, color=P['ink'], lw=0.5, ls=':', zorder=1)
    F.save(f, 'ch06-term', mode)


# ---------------------------------------------------------------- 코어 플럭스
def fig_core(mode):
    P = C[mode]
    f = F.fig(130, 78)
    ax = f.add_axes([0.09, 0.17, 0.52, 0.78])
    grp = ['17.2~26.0 ka', '5.3~14.8 ka\n(습윤기)', '0~5.2 ka']
    terr = [8.30, 7.64, 11.22]; carb = [5.3, 8.45, 6.46]
    x = np.arange(3); w = 0.36
    ax.bar(x-w/2, terr, w, color=P['b'], edgecolor=P['ink'], linewidth=0.5, label='육상기원', hatch=None, zorder=3)
    ax.bar(x+w/2, carb, w, color=P['a'] if mode == 'color' else '#EEEEEE', edgecolor=P['ink'], linewidth=0.5, label='탄산염', hatch='///' if mode == 'bw' else None, zorder=3)
    for xi, v in zip(x-w/2, terr): ax.text(xi, v+0.15, '%.2f' % v, ha='center', va='bottom', fontsize=FS, color=P['ink'])
    for xi, v in zip(x+w/2, carb): ax.text(xi, v+0.15, '%.2f' % v, ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ax.set_xticks(x); ax.set_xticklabels(grp, fontsize=FS, color=P['ink'])
    ax.set_ylim(0, 13.5)
    ax.set_ylabel('플럭스(g/cm²/ka)', fontsize=FS, color=P['soft'])
    sty(ax, mode)
    ax.legend(loc='upper left', fontsize=FS, frameon=False)
    ax2 = f.add_axes([0.70, 0.17, 0.27, 0.78])
    names = ['시료\n간격', '종료\n오차', '종료\n길이']
    vals = [111, 190, 400]
    ax2.bar(range(3), vals, 0.55, color=[P['mid'], P['mid'], P['b']], edgecolor=P['ink'], linewidth=0.5, zorder=3)
    for i, v in enumerate(vals): ax2.text(i, v+10, '%d' % v, ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ax2.set_xticks(range(3)); ax2.set_xticklabels(names, fontsize=FS, color=P['ink'])
    ax2.set_ylim(0, 470); ax2.set_ylabel('년', fontsize=FS, color=P['soft'])
    sty(ax2, mode)
    F.save(f, 'ch06-core', mode)


# ---------------------------------------------------------------- 둥거 사건
def fig_dongge(mode):
    P = C[mode]
    f = F.fig(130, 78)
    ax = f.add_axes([0.30, 0.17, 0.68, 0.78])
    ev = [('11225 ± 97 (1.05‰)', 11225, 97), ('10880 ± 117 (1.15‰)', 10880, 117), ('9165 ± 75 (1.40‰)', 9165, 75),
          ('8260 ± 64 (1.1‰)', 8260, 64), ('8080 ± 74 (1.0‰)', 8080, 74), ('3550 ± 59 (1.1‰/100 년)', 3550, 59)]
    n = len(ev)
    for i, (nm, v, e) in enumerate(ev):
        y = n-1-i
        ax.scatter([v], [y], s=30, color=P['b'] if i < 5 else P['acc'], edgecolor=P['ink'], linewidth=0.5, zorder=4)
        ax.errorbar([v], [y], xerr=[e], color=P['ink'], lw=0.9, capsize=2.5, zorder=3)
    ax.set_yticks(range(n)); ax.set_yticklabels([e[0] for e in ev][::-1], fontsize=FS, color=P['ink'])
    ax.axvspan(4150, 3930, color=P['mid'], alpha=0.4, zorder=1)
    ax.text(5300, n-0.55, '4.2 ka 사건 경계\n4150~3930', ha='center', va='top', fontsize=FS, color=P['ink'])
    ax.set_xlim(11800, 3300); ax.set_ylim(-0.7, n-0.2)
    ax.set_xlabel('연대(yr BP, 왼쪽이 오래된 때)', fontsize=FS, color=P['soft'])
    sty(ax, mode, grid='x')
    F.save(f, 'ch06-dongge', mode)


if __name__ == '__main__':
    for m in MODES:
        fig_map(m); fig_insol(m); fig_term(m); fig_core(m); fig_dongge(m)
