# -*- coding: utf-8 -*-
"""11장 「아메리카의 기후와 땅」 그림 2장(색·흑백 SVG 두 벌): fig/fig-ch11-*-v1-{color,bw}.svg
이 장은 호수, 빙하, 해안 기록의 근거를 확보하지 못했다. 그림은 이 세션이 읽은 북미 쪽 자료(마자마, 오카모크)의 숫자를 다시 그린 것이다.
  mazama : 마자마 분화 연대의 세 서술(계산 11-1)
  okmok  : 오카모크 II(기원전 43년)의 빙핵 침적과 냉각 서술(계산 11-2)
쓰는 법(작업 폴더 /home/claude/book4): PREVDIR=/경로 python3 scripts/figs-ch11.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p11')
import numpy as np
import figkit12 as F


def fig_mazama(mode):
    P = F.C[mode]
    f = F.fig(130, 66); ax = f.add_axes([0.40, 0.22, 0.56, 0.72])
    rows = [('Egan 등(2015) 방사성탄소 81개\n베이즈 95.4%: 7584~7682', 7584, 7682, 'a'), ('Sigl 등(2022) 빙핵\n7627 ± 150', 7477, 7777, 'mid'), ('백과사전(이차 자료)\n7640 ± 20', 7620, 7660, 'b')]
    for i, (n, lo, hi, k) in enumerate(rows):
        y = 2 - i
        ax.barh(y, hi - lo, left=lo, height=0.5, color=P[k], edgecolor=P['ink'], lw=0.6, zorder=3)
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.set_xlim(7400, 7850); ax.set_ylim(-0.6, 2.6); ax.set_xlabel('마자마 분화, cal BP(1950년 기준)', fontsize=8)
    F.style_ax(ax, mode, grid='x')
    return F.save(f, 'ch11-mazama', mode)


def fig_okmok(mode):
    P = F.C[mode]
    f = F.fig(130, 90)
    a1 = f.add_axes([0.10, 0.58, 0.40, 0.34]); a2 = f.add_axes([0.62, 0.58, 0.34, 0.34]); a3 = f.add_axes([0.40, 0.10, 0.56, 0.34])
    dep = [('NGRIP2', 123), ('NEEM', 110), ('GISP2', 131), ('GRIP', 135), ('Dye3', 128)]
    a1.bar(range(5), [v for _, v in dep], color=P['a'], edgecolor=P['ink'], lw=0.6, zorder=3)
    a1.set_xticks(range(5)); a1.set_xticklabels([n for n, _ in dep], fontsize=8, rotation=35, ha='right')
    a1.set_ylim(0, 160); a1.set_ylabel('2년 합 침적(kg/km²)', fontsize=8)
    for i, (_, v) in enumerate(dep): a1.text(i, v + 3, str(v), ha='center', va='bottom', fontsize=8, color=P['ink'])
    F.style_ax(a1, mode, grid='y')
    rk = [1, 2, 2, 3, 4]   # NGRIP2, NEEM, GISP2, GRIP, Dye3 순서(논문: GRIP 3위, Dye3 4위)
    a2.plot(range(5), rk, 'o', ms=8, color=P['b'] if mode == 'color' else '#666666', mec=P['ink'], zorder=3)
    a2.set_xticks(range(5)); a2.set_xticklabels([n for n, _ in dep], fontsize=8, rotation=35, ha='right'); a2.set_ylim(4.6, 0.4); a2.set_xlim(-0.6, 4.6)
    a2.set_ylabel('지난 2500년 안의 순위', fontsize=8); a2.set_yticks([1, 2, 3, 4])
    F.style_ax(a2, mode, grid='y')
    rows = [('나이테 유럽 43 BCE 여름(>3)', 3.0, 3.0), ('나이테 유럽 42 BCE 여름(>2.5)', 2.5, 2.5), ('중국 석순 3년(>2.0)', 2.0, 2.0), ('CESM 모의 북반구 여름', 2.0, 3.0), ('지중해 모의 계절 냉각', 0.7, 7.4)]
    ys = np.arange(len(rows))[::-1]
    for y, (n, lo, hi) in zip(ys, rows):
        if lo == hi:
            a3.annotate('', xy=(lo + 1.2, y), xytext=(lo, y), arrowprops=dict(arrowstyle='->', color=P['a'] if mode == 'color' else '#111111', lw=2.0)); a3.plot([lo], [y], '|', ms=9, color=P['ink'])
        else:
            a3.plot([lo, hi], [y, y], '-', lw=3.5, color=P['b'], solid_capstyle='butt')
    a3.set_yticks(ys); a3.set_yticklabels([r[0] for r in rows], fontsize=8); a3.set_xlim(0, 8.5); a3.set_xlabel('냉각(℃; 화살표는 "이상")', fontsize=8)
    F.style_ax(a3, mode, grid='x')
    return F.save(f, 'ch11-okmok', mode)


if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_mazama(m); fig_okmok(m)
