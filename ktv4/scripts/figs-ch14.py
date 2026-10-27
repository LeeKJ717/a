# -*- coding: utf-8 -*-
"""14장 「사람과 기후」 그림. 자료 그림은 논문이 적은 숫자와 이 책의 계산(ms/code/ch14/calc14.log, calc14-out.json)을 다시 그린 것이며 측정 자료 그 자체가 아니다.
가상 값은 모두 시연값이다.
실행(작업 폴더 /home/claude/book4): python3 scripts/figs-ch14.py → fig/fig-ch14-*-v1-{color,bw}.svg
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as fk
from matplotlib.patches import Patch

OUT = json.load(open(os.path.join(ROOT, 'ms', 'code', 'ch14', 'calc14-out.json'), encoding='utf-8'))


def fig_ruddiman(mode):
    P = fk.C[mode]
    R = OUT['ruddiman']
    f = fk.fig(130, 70)
    ax1 = f.add_axes([0.10, 0.20, 0.50, 0.74])
    ax2 = f.add_axes([0.72, 0.20, 0.25, 0.74])
    # 이산화탄소: 점과 범위
    items = [('정점\n(11~10 ka)', R['co2_peak'], R['co2_peak'], P['a']),
             ('8 ka', R['co2_8ka'], R['co2_8ka'], P['a']),
             ('산업화 이전\n관측', R['pre'][0], R['pre'][1], P['b']),
             ('이전 간빙기\n기준 기대', R['exp'][0], R['exp'][1], P['c'])]
    for i, (lab, lo, hi, c) in enumerate(items):
        if hi > lo:
            ax1.bar(i, hi - lo, bottom=lo, width=0.5, color=c, edgecolor=P['ink'], linewidth=0.6, zorder=3, hatch='////' if (mode == 'bw' and i == 2) else '')
            ax1.text(i, hi + 1.5, '%.0f~%.0f' % (lo, hi), ha='center', fontsize=8, color=P['ink'])
        else:
            ax1.plot([i], [lo], 'o', color=c, mec=P['ink'], ms=6, zorder=4)
            ax1.text(i, lo + 3, '%.0f' % lo, ha='center', fontsize=8, color=P['ink'])
    ax1.set_xticks(range(4)); ax1.set_xticklabels([x[0] for x in items], fontsize=8)
    ax1.set_ylim(225, 295); ax1.set_xlim(-0.6, 3.6)
    ax1.set_ylabel('CO2 (ppm)', fontsize=8)
    fk.style_ax(ax1, mode, grid='y')
    # 메탄
    ax2.bar([0, 1], [R['ch4'][0], R['ch4'][1]], width=0.55, color=[P['b'], P['c']], edgecolor=P['ink'], linewidth=0.6, zorder=3, hatch=None)
    for x, v in zip((0, 1), R['ch4']):
        ax2.text(x, v + 12, '%.0f' % v, ha='center', fontsize=8, color=P['ink'])
    ax2.set_xticks([0, 1]); ax2.set_xticklabels(['관측', '기대'], fontsize=8)
    ax2.set_ylim(0, 820); ax2.set_ylabel('CH4 (ppb)', fontsize=8)
    fk.style_ax(ax2, mode, grid='y')
    fk.save(f, 'ch14-ruddiman', mode)


def fig_archaeo(mode):
    P = fk.C[mode]
    A = OUT['archaeoglobe']
    f = fk.fig(130, 80)
    ax1 = f.add_axes([0.14, 0.60, 0.82, 0.34])
    ax2 = f.add_axes([0.14, 0.30, 0.82, 0.16])
    R = A['regions']
    for y, v, lab in ((1, A['i6'], '6 ka'), (0, A['i2'], '2 ka')):
        ax1.barh(y, v, color=P['a'], edgecolor=P['ink'], linewidth=0.6, zorder=3, height=0.55)
        ax1.barh(y, R - v, left=v, color=P['grid'], edgecolor=P['soft'], linewidth=0.6, zorder=3, height=0.55)
        ax1.text(v + 2, y, '%d개' % v, va='center', fontsize=8, color=P['ink'])
    ax1.set_yticks([0, 1]); ax1.set_yticklabels(['2 ka', '6 ka'], fontsize=8)
    ax1.set_xlim(0, R); ax1.set_xlabel('집약 농업이 흔한 지역 수(전체 %d개 지역 중)' % R, fontsize=8)
    fk.style_ax(ax1, mode, grid='x')
    parts = [('1,000년 넘게 이름', A['e1000'], P['a'], ''), ('이르되 1,000년 이내', A['earlier'] - A['e1000'], P['c'], '//'),
             ('나머지', A['hyde_n'] - A['earlier'] - A['l1000'], P['grid'], ''), ('1,000년 넘게 늦음', A['l1000'], P['b'], '\\\\')]
    left = 0
    for lab, v, c, h in parts:
        ax2.barh(0, v, left=left, color=c, edgecolor=P['ink'], linewidth=0.6, zorder=3, height=0.6, hatch=h if mode == 'bw' else '')
        ax2.text(left + v / 2, 0, '%d' % v, ha='center', va='center', fontsize=8, color=P['ink'])
        left += v
    ax2.set_yticks([]); ax2.set_xlim(0, A['hyde_n'])
    ax2.set_xlabel('HYDE와 견준 농업 시작, 130개 지역', fontsize=8)
    handles = [Patch(facecolor=c, edgecolor=P['ink'], hatch=h if mode == 'bw' else '', label=l) for l, v, c, h in parts]
    f.legend(handles=handles, loc='lower left', bbox_to_anchor=(0.10, 0.0), ncol=2, fontsize=8, frameon=False, handlelength=1.2, columnspacing=1.0)
    fk.style_ax(ax2, mode, grid=None)
    fk.save(f, 'ch14-archaeo', mode)


def fig_polynesia(mode):
    P = fk.C[mode]
    Q = OUT['poly']
    f = fk.fig(130, 86)
    ax1 = f.add_axes([0.30, 0.50, 0.66, 0.46])
    rows = [('소사이어티 제도\n(Wilmshurst 2011)', Q['w1'], P['a'], ''), ('나머지 섬\n(Wilmshurst 2011)', Q['w2'], P['a'], ''),
            ('남반구가 북반구보다\n따뜻했던 때(Neukom 2014)', Q['shwarm'], P['b'], '//'), ('소빙기 급한 시작\n(Miller 2012)', Q['miller'], P['d'], 'xx')]
    for i, (lab, (a, b), c, h) in enumerate(rows):
        y = len(rows) - 1 - i
        ax1.barh(y, b - a, left=a, height=0.55, color=c, edgecolor=P['ink'], linewidth=0.6, zorder=3, hatch=h if mode == 'bw' else '')
    ax1.axvline(Q['rat'], color=P['ink'], lw=1.0, ls='--', zorder=4)
    ax1.text(Q['rat'] - 6, 3.45, '쥐 도착 약 1280', fontsize=8, color=P['ink'], va='center', ha='right')
    ax1.set_yticks(range(len(rows))); ax1.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
    ax1.set_xlim(1000, 1400); ax1.set_ylim(-0.6, 3.9)
    ax1.set_xlabel('서기 연도(논문이 적은 창, 연대 오차 없음)', fontsize=8)
    fk.style_ax(ax1, mode, grid='x')
    ax2 = f.add_axes([0.30, 0.14, 0.66, 0.22])
    ow = OUT['oldwood']
    ages = [a for a, s in ow]; sh = [-s for a, s in ow]
    ax2.bar(range(len(ages)), sh, width=0.55, color=P['c'], edgecolor=P['ink'], linewidth=0.6, zorder=3)
    for i, v in enumerate(sh):
        ax2.text(i, v + 6, '%.0f' % v, ha='center', fontsize=8, color=P['ink'])
    ax2.set_xticks(range(len(ages))); ax2.set_xticklabels(['%d년' % a for a in ages], fontsize=8)
    ax2.set_xlabel('죽을 때 이미 가진 속 나이(시연값)', fontsize=8)
    ax2.set_ylabel('이른 쪽으로(년)', fontsize=8)
    ax2.set_ylim(0, 330)
    fk.style_ax(ax2, mode, grid='y')
    fk.save(f, 'ch14-polynesia', mode)


def fig_coincidence(mode):
    P = fk.C[mode]
    f = fk.fig(130, 64)
    ax1 = f.add_axes([0.10, 0.20, 0.38, 0.74])
    ax2 = f.add_axes([0.62, 0.20, 0.35, 0.74])
    K = np.array([k for k, p in OUT['inflate']]); pr = np.array([p for k, p in OUT['inflate']]) * 100
    ax1.plot(K, pr, '-o', color=P['a'], mec=P['ink'], ms=4, lw=1.2, zorder=4)
    for k, p in zip(K, pr):
        if k in (1, 3, 10):
            ax1.text(k + 0.5, p - 7, '%.0f%%' % p, fontsize=8, color=P['ink'])
    ax1.set_xlabel('독립 사건의 수 K', fontsize=8); ax1.set_ylabel('하나라도 우연히 드는 확률(%)', fontsize=8)
    ax1.set_ylim(0, 105); ax1.set_xlim(0, 21)
    fk.style_ax(ax1, mode, grid='y')
    U = np.array([u for u, p in OUT['dilate']]); pd_ = np.array([p for u, p in OUT['dilate']]) * 100
    ax2.plot(U, pd_, '-o', color=P['b'], mec=P['ink'], ms=4, lw=1.2, zorder=4)
    for u, p in zip(U, pd_):
        if u in (0, 100, 200):
            ax2.text(u + 5, p - 3.5, '%.0f%%' % p, fontsize=8, color=P['ink'])
    ax2.set_xlabel('사건 날짜의 오차 ±U (년)', fontsize=8); ax2.set_ylabel('건조 창과 겹칠 확률(%)', fontsize=8)
    ax2.set_ylim(15, 50); ax2.set_xlim(-5, 215)
    fk.style_ax(ax2, mode, grid='y')
    fk.save(f, 'ch14-coincidence', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        fig_ruddiman(mode); fig_archaeo(mode); fig_polynesia(mode); fig_coincidence(mode)
