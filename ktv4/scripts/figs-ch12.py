# -*- coding: utf-8 -*-
"""12장 「남반구와 오세아니아」 그림. 자료 그림은 논문이 적은 숫자(ms/code/ch12/calc12.log)를 다시 그린 것이며 측정 자료 그 자체가 아니다.
실행(작업 폴더 /home/claude/book4): python3 scripts/figs-ch12.py → fig/fig-ch12-*-v1-{color,bw}.svg
지도(그림 12-1)는 논문이 좌표를 적은 지점만 점으로 찍은 개략도이며 나머지는 지역 이름만 적었다.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as fk
import mapkit as mk
import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = json.load(open(os.path.join(ROOT, 'ms', 'code', 'ch12', 'calc12-out.json'), encoding='utf-8'))


def fig_map(mode):
    P = fk.C[mode]
    f = fk.fig(130, 66)
    ax = f.add_axes([0.07, 0.10, 0.90, 0.86])
    ax.set_facecolor(P['sea'])
    bb = (-180, -85, 180, 2)
    land = gpd.clip(mk.read('ne_50m_land', bb), box(*bb))
    land.plot(ax=ax, color=P['land'], edgecolor=P['soft'], linewidth=0.35)
    ax.set_xlim(bb[0], bb[2]); ax.set_ylim(bb[1], bb[3]); ax.set_aspect('auto')
    pts = [  # 논문이 좌표를 적은 지점
        ('Lamy 등의 피오르드 지점(52~53°S)', -72.9, -52.8, 'o', P['a']),
        ('카메론 빙하(약 43°S, 171°E)', 171.0, -43.0, 's', P['b']),
        ('KNI-51 동굴(15°18′S, 128°37′E)', 128.6, -15.3, '^', P['c']),
    ]
    for name, x, y, m, c in pts:
        ax.scatter([x], [y], s=34, marker=m, color=c, edgecolor=P['ink'], linewidth=0.6, zorder=5)
    txt = [('남극', 0, -79), ('남극반도', -95, -66), ('남아메리카 남부', -66, -38), ('호주', 134, -26), ('뉴질랜드', 171, -49), ]
    for s, x, y in txt:
        ax.text(x, y, s, fontsize=8, color=P['ink'], ha='center', va='center')
    ax.text(-72.9, -60.5, '피오르드 지점', fontsize=8, color=P['ink'], ha='center')
    ax.text(160, -39.5, '카메론 빙하', fontsize=8, color=P['ink'], ha='right')
    ax.text(128.6, -11.5, 'KNI-51', fontsize=8, color=P['ink'], ha='center')
    ax.set_xticks(range(-180, 181, 60)); ax.set_yticks(range(-80, 1, 20))
    ax.set_xticklabels(['%d°%s' % (abs(v), '서' if -180 < v < 0 else ('동' if 0 < v < 180 else '')) for v in range(-180, 181, 60)])
    ax.set_xlabel(''); ax.set_ylabel('')
    ax.set_yticklabels(['%d°남' % abs(v) if v else '적도' for v in range(-80, 1, 20)])
    fk.style_ax(ax, mode, grid=None)
    for s in ax.spines.values():
        s.set_color(P['soft'])
    fk.save(f, 'ch12-map', mode)


def fig_moraine(mode):
    P = fk.C[mode]
    M = OUT['moraine']
    f = fk.fig(130, 78)
    ax1 = f.add_axes([0.13, 0.13, 0.50, 0.76])
    ax2 = f.add_axes([0.70, 0.13, 0.26, 0.76], sharey=ax1)
    ys = np.arange(len(M))[::-1]
    for ax, lo, hi in ((ax1, 6.4, 11.6), (ax2, -0.05, 0.85)):
        for (a, s, n), y in zip(M, ys):
            if lo <= a <= hi:
                ax.errorbar(a, y, xerr=s, fmt='o', color=P['ink'], ecolor=P['ink'], ms=4 + 0.5 * n, mfc=P['a'], mec=P['ink'], capsize=2, lw=0.8, zorder=4)
                ax.text(a - (s + 0.12 if ax is ax1 else s + 0.025), y, 'n=%d' % n, fontsize=8, color=P['soft'], va='center', ha='left')
        ax.set_xlim(lo, hi)
        fk.style_ax(ax, mode, grid='x')
    ax1.invert_xaxis()
    ax1.set_yticks(ys); ax1.set_yticklabels(['모레인 %d' % (i + 1) for i in range(len(M))], fontsize=8)
    ax2.tick_params(labelleft=False); ax2.invert_xaxis()
    ax1.set_xlabel('평균 연대 (ka, 서기 1950 기준)', fontsize=8)
    ax2.set_xlabel('ka', fontsize=8)
    ax1.set_title('이른~중기 홀로세', fontsize=8, color=P['ink'], loc='left')
    ax2.set_title('최근 700년', fontsize=8, color=P['ink'], loc='left')
    fk.save(f, 'ch12-moraine', mode)


def fig_windows(mode):
    P = fk.C[mode]
    W = OUT['windows']
    grp = [0, 0, 0, 1, 2, 2, 2, 3, 3, 3]  # 남극, 뉴질랜드, 파타고니아, 호주
    cols = [P['a'], P['b'], P['c'], P['d']]
    hat = ['', '//', '\\\\', 'xx']
    short = ['남극 이른 최적기(11.5~9)', '남극 Ross 쪽 2차(7~5)', '동남극 늦은 최적기(6~3)', '뉴질랜드 빙하 최대(10.7~9.8)',
             '편서풍 강함 52°S(12~8.5)', '편서풍 약화 52°S(5.5~0)', '편서풍 강함 51°S(7.5~0)',
             '킴벌리 몬순 강화(9~7)', '킴벌리 몬순 최대(5~4)', '퀸즐랜드 습함(7.7~3.2)']
    f = fk.fig(130, 82)
    ax = f.add_axes([0.40, 0.20, 0.57, 0.77])
    for i, (nm, a, b) in enumerate(W):
        y = len(W) - 1 - i
        ax.barh(y, a - b, left=b, height=0.62, color=cols[grp[i]], edgecolor=P['ink'], linewidth=0.5, hatch=hat[grp[i]] if mode == 'bw' else '', zorder=3)
    ax.set_yticks(range(len(W))); ax.set_yticklabels(short[::-1], fontsize=8)
    ax.set_xlim(12.2, -0.2)
    ax.set_xlabel('ka (천 년 전)', fontsize=8)
    fk.style_ax(ax, mode, grid='x')
    handles = [Patch(facecolor=cols[g], edgecolor=P['ink'], hatch=hat[g] if mode == 'bw' else '', label=n) for g, n in enumerate(['남극', '뉴질랜드', '파타고니아', '호주'])]
    ax.legend(handles=handles, loc='upper left', fontsize=8, frameon=False, bbox_to_anchor=(-0.65, -0.12), ncol=4)
    fk.save(f, 'ch12-windows', mode)


def fig_kni(mode):
    P = fk.C[mode]
    K = OUT['kni']
    labs = ['이른 홀로세 강화\n(9→7 ka)', '늦은 홀로세 약화\n(4.2→1.5 ka)', '회복, 본문\n(1.2→0.9 ka)', '회복, 결론\n(1.0→0.7 ka)']
    vals = [K['early'], K['late'], K['rec1'], K['rec2']]
    f = fk.fig(130, 62)
    ax = f.add_axes([0.12, 0.30, 0.85, 0.64])
    cs = [P['a'], P['b'], P['c'], P['c']]
    ax.bar(range(4), vals, color=cs, edgecolor=P['ink'], linewidth=0.5, width=0.6, zorder=3, hatch='' if mode == 'color' else None)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.25 if v >= 0 else -0.25), '%.2f' % v, ha='center', va='bottom' if v >= 0 else 'top', fontsize=8, color=P['ink'])
    ax.axhline(0, color=P['soft'], lw=0.6)
    ax.set_xticks(range(4)); ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylabel('δ18O 변화율 (‰/ka)', fontsize=8)
    ax.set_ylim(-8, 2.2)
    fk.style_ax(ax, mode, grid='y')
    fk.save(f, 'ch12-kni', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        fig_map(mode); fig_moraine(mode); fig_windows(mode); fig_kni(mode)
