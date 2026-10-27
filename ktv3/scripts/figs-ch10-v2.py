# -*- coding: utf-8 -*-
"""10장 v2 그림(주장 장부 27개의 판정 분포) 1장(색·흑백 SVG 두 벌): fig/fig-ch10-*-v1-{color,bw}.svg
값은 ms/code/ch10/out 의 계산 결과(json)와 이 장이 읽은 논문의 숫자이다. 논문의 그림을 옮긴 것이 아니라 숫자를 다시 그린 것이다.
 verdict : 주장 장부 v2의 판정을 사료·연구 묶음별로 센 것(ms/code/ch10/out/ledger-v2.json)
쓰는 법(작업 폴더 /home/claude/book3): python3 scripts/figs-ch10-v2.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
FONT = 'Noto Sans CJK KR'
assert FONT in {f.name for f in fm.fontManager.ttflist}
FS = 8.5
plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'svg.fonttype': 'path', 'font.size': FS, 'axes.titlesize': FS,
                     'axes.labelsize': FS, 'xtick.labelsize': FS, 'ytick.labelsize': FS, 'legend.fontsize': FS})
OUT = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p10v2')
os.makedirs(PREV, exist_ok=True)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch10', 'out')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
W = 130 / 25.4
PAL = {'color': dict(a='#9C4F2E', b='#3A7CA5', c='#8A6A2C', d='#4F7F4A', e='#8E8E8E', txt='#1B2A33', soft='#4F6E80', grid='#C9D3D8', ref='#B03A2E'),
       'bw': dict(a='#111111', b='#555555', c='#8A8A8A', d='#C4C4C4', e='#FFFFFF', txt='#111111', soft='#444444', grid='#C8C8C8', ref='#111111')}

def save(fig, name, mode):
    fig.savefig(os.path.join(OUT, 'fig-ch10-%s-v2-%s.svg' % (name, mode)), format='svg')
    fig.savefig(os.path.join(PREV, '%s-%s.png' % (name, mode)), dpi=130)
    plt.close(fig)

def clean(ax, P):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(P['soft'])
    ax.tick_params(colors=P['txt'], length=3)

def fig_verdict(mode):
    P = PAL[mode]
    rows = J('ledger-v2.json')
    groups = ['집사', '튀르크 계보', '칭기즈 Y', 'Ulitau', '카자흐 씨족', '샤이바니', '고대 유전체']
    glab = {'집사': '『집사』와 『몽골비사』', '튀르크 계보': '『튀르크 계보』', '칭기즈 Y': '칭기즈 칸의 Y', 'Ulitau': 'Ulitau 영묘', '카자흐 씨족': '카자흐 씨족 계보', '샤이바니': '『샤이바니나마』와 Töre', '고대 유전체': '초원 고대 유전체'}
    verd = ['지지', '부분 지지', '반증', '시험 불가', '근거 확인 필요']
    col = [P['d'], P['b'], P['a'], P['e'], P['c']] if mode == 'color' else ['#FFFFFF', '#BBBBBB', '#111111', '#E4E4E4', '#777777']
    hat = ['', '', '', '//', '..'] if mode == 'bw' else ['', '', '', '//', '']
    fig, ax = plt.subplots(figsize=(W, 3.8))
    for i, g in enumerate(groups):
        y = len(groups) - 1 - i
        left = 0
        for j, v in enumerate(verd):
            n = sum(1 for r in rows if r['group'] == g and r['verdict'] == v)
            if n:
                ax.barh(y, n, left=left, height=0.62, color=col[j], edgecolor=P['txt'], linewidth=0.7, hatch=hat[j] if (mode == 'bw' or v == '시험 불가') else '')
                tc = '#FFFFFF' if (mode == 'color' and v in ('지지', '반증', '부분 지지')) or (mode == 'bw' and v == '반증') or (mode == 'bw' and v == '근거 확인 필요') else P['txt']
                ax.text(left + n / 2, y, str(n), ha='center', va='center', fontsize=FS, color=tc,
                        bbox=dict(fc='#FFFFFF', ec='none', pad=1.0) if (v == '시험 불가' or (mode == 'bw' and v in ('근거 확인 필요', '부분 지지'))) else None)
                left += n
        ax.text(left + 0.15, y, '합 %d' % left, va='center', fontsize=FS - 0.3, color=P['soft'])
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([glab[g] for g in groups][::-1])
    ax.set_xlim(0, 12)
    ax.set_xlabel('주장 수 (10장 주장 장부 %d개)' % len(rows))
    ax.set_xticks(range(0, 12, 2))
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    ax.set_axisbelow(True)
    clean(ax, P)
    ax.legend(handles=[Patch(fc=col[j], ec=P['txt'], hatch=hat[j] if (mode == 'bw' or verd[j] == '시험 불가') else '', label=verd[j]) for j in range(5)],
              ncol=3, loc='upper center', bbox_to_anchor=(0.4, -0.2), frameon=False, fontsize=FS - 0.3, columnspacing=1.0)
    fig.subplots_adjust(left=0.30, right=0.97, top=0.98, bottom=0.30)
    save(fig, 'verdict', mode)


if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_verdict(m)
    print('ok')
