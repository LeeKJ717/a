# -*- coding: utf-8 -*-
"""10장 그림 3장(색·흑백 SVG 두 벌): fig/fig-ch10-*-v1-{color,bw}.svg
값은 ms/code/ch10/out 의 계산 결과(json)와 이 장이 읽은 논문의 숫자이다. 논문의 그림을 옮긴 것이 아니라 숫자를 다시 그린 것이다.
 verdict : 주장 장부의 판정을 사료·연구 묶음별로 센 것
 clans   : Zhetiru 씨족의 우세 하플로그룹 비율(씨족 안 대 씨족 밖)
 ages    : 계보 주장과 증거의 연대를 달력 연도 위에 놓은 것
쓰는 법(작업 폴더 /home/claude/book3): python3 scripts/figs-ch10.py"""
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
PREV = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p10')
os.makedirs(PREV, exist_ok=True)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch10', 'out')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
W = 130 / 25.4
PAL = {'color': dict(a='#9C4F2E', b='#3A7CA5', c='#8A6A2C', d='#4F7F4A', e='#8E8E8E', txt='#1B2A33', soft='#4F6E80', grid='#C9D3D8', ref='#B03A2E'),
       'bw': dict(a='#111111', b='#555555', c='#8A8A8A', d='#C4C4C4', e='#FFFFFF', txt='#111111', soft='#444444', grid='#C8C8C8', ref='#111111')}

def save(fig, name, mode):
    fig.savefig(os.path.join(OUT, 'fig-ch10-%s-v1-%s.svg' % (name, mode)), format='svg')
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
    rows = J('ledger.json')
    groups = ['집사', '튀르크 계보', '칭기즈 Y', 'Ulitau', '카자흐 씨족', '샤이바니']
    glab = {'집사': '『집사』와 『몽골비사』', '튀르크 계보': '『튀르크 계보』', '칭기즈 Y': '칭기즈 칸의 Y', 'Ulitau': 'Ulitau 영묘', '카자흐 씨족': '카자흐 씨족 계보', '샤이바니': '『샤이바니나마』와 Töre'}
    verd = ['지지', '부분 지지', '반증', '시험 불가', '근거 확인 필요']
    col = [P['d'], P['b'], P['a'], P['e'], P['c']] if mode == 'color' else ['#FFFFFF', '#BBBBBB', '#111111', '#E4E4E4', '#777777']
    hat = ['', '', '', '//', '..'] if mode == 'bw' else ['', '', '', '//', '']
    fig, ax = plt.subplots(figsize=(W, 3.5))
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
    ax.set_xlim(0, 11)
    ax.set_xlabel('주장 수 (10장 주장 장부 %d개)' % len(rows))
    ax.set_xticks(range(0, 11, 2))
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    ax.set_axisbelow(True)
    clean(ax, P)
    ax.legend(handles=[Patch(fc=col[j], ec=P['txt'], hatch=hat[j] if (mode == 'bw' or verd[j] == '시험 불가') else '', label=verd[j]) for j in range(5)],
              ncol=3, loc='upper center', bbox_to_anchor=(0.4, -0.2), frameon=False, fontsize=FS - 0.3, columnspacing=1.0)
    fig.subplots_adjust(left=0.30, right=0.97, top=0.98, bottom=0.30)
    save(fig, 'verdict', mode)

def fig_clans(mode):
    P = PAL[mode]
    c3 = J('calc-10-3.json')
    rows = c3['b']
    order = ['Teleu', 'Tama', 'Kereit', 'Kerderi']
    info = {}
    for r in rows:
        info.setdefault(r['clan'], dict(hg=r['hg'], n=r['n'], k=r['k'], out=[]))['out'].append(r['out_k'] / r['out_n'])
    fig, ax = plt.subplots(figsize=(W, 3.0))
    for i, c in enumerate(order):
        y = len(order) - 1 - i
        d = info[c]
        ins = d['k'] / d['n']
        lo, hi = min(d['out']), max(d['out'])
        ax.plot([lo, ins], [y, y], color=P['soft'], lw=1.2)
        ax.plot([ins], [y], 'o', color=P['a'], ms=7, mec=P['txt'], mew=0.7)
        ax.plot([lo, hi], [y, y], 's', color=P['b'] if mode == 'color' else '#FFFFFF', ms=6, mec=P['txt'], mew=0.7)
        ax.text(ins - 0.02 if ins > 0.7 else ins + 0.025, y + 0.25, '씨족 안 %d/%d = %.2f' % (d['k'], d['n'], ins), fontsize=FS - 0.3, va='center', ha='right' if ins > 0.7 else 'left', color=P['txt'])
        ax.text(max(hi, 0.0) + 0.025, y - 0.28, '씨족 밖 %.2f~%.2f' % (lo, hi), fontsize=FS - 0.3, va='center', color=P['txt'])
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(['%s 씨족, %s' % (c, info[c]['hg']) for c in order][::-1])
    ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlim(0, 1.1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel('그 하플로그룹을 가진 남성의 비율 (계산 10-3)')
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    ax.set_axisbelow(True)
    clean(ax, P)
    ax.legend(handles=[Line2D([], [], marker='o', color='none', mfc=P['a'], mec=P['txt'], ms=7, label='씨족 안'),
                       Line2D([], [], marker='s', color='none', mfc=P['b'] if mode == 'color' else '#FFFFFF', mec=P['txt'], ms=6, label='씨족 밖(부족 전체 퍼센트의 반올림 범위)')],
              loc='upper center', bbox_to_anchor=(0.4, -0.22), ncol=2, frameon=False, fontsize=FS - 0.3)
    fig.subplots_adjust(left=0.30, right=0.97, top=0.98, bottom=0.30)
    save(fig, 'clans', mode)

def fig_ages(mode):
    P = PAL[mode]
    # (이름, 시작 연도, 끝 연도, 점 연도 또는 None, 종류) 종류 0 = 연구 추정, 1 = 사료·구전, 2 = 사건
    items = [
        ('『집사』를 쓴 시기(Rashid al-Din 사망 1318)', 1300, 1318, 1318, 1),
        ('칭기즈 칸의 생애(1162~1227, Zerjal 등 표기)', 1162, 1227, None, 2),
        ('Zerjal 등(2003) 별무리 TMRCA, 발표 2003년 기준', 2003 - 1300, 2003 - 700, 2003 - 1000, 0),
        ('Balaresque 등(2015) DC1 평균 TMRCA', 1090, 1090, 1090, 0),
        ('Askapuli 등(2026) C3* 합착 약 2500년 전', 2026 - 2500, 2026 - 2500, 2026 - 2500, 0),
        ('Kerey 하위 씨족 분기, 20~22세대(2012년 기준)', 2012 - 660, 2012 - 500, None, 0),
        ('Emir Alau 전통 약 650년 전(2021년 기준)', 2021 - 650, 2021 - 650, 2021 - 650, 1),
        ('Alau TMRCA, STR 700 ± 200 (2021년 기준)', 2021 - 900, 2021 - 500, 2021 - 700, 0),
        ('Alau TMRCA, 염기서열 500 ± 200 (2021년 기준)', 2021 - 700, 2021 - 300, 2021 - 500, 0),
        ('Ulitau 영묘 CKZ002~004의 탄소 연대 14세기', 1300, 1399, None, 0),
        ('Zhetiru 연합설 17세기 / 일곱 아들 설(Blaramberg 1848)', 1600, 1699, None, 1)]
    fig, ax = plt.subplots(figsize=(W, 4.9))
    cols = [P['a'], P['b'], P['c']]
    mk = ['o', 's', '^']
    for i, (n, s, e, pt, k) in enumerate(items):
        y = len(items) - 1 - i
        if e - s >= 5:
            ax.plot([s, e], [y, y], color=cols[k], lw=3.2 if mode == 'color' else 3.0, solid_capstyle='butt')
        if pt is not None:
            ax.plot([pt], [y], mk[k], color=cols[k] if mode == 'color' else '#FFFFFF', mec=P['txt'], ms=6.5, mew=0.8)
        if e - s < 5 and pt is None:
            ax.plot([s], [y], mk[k], color=cols[k], ms=6, mec=P['txt'])
        ax.text(-1050, y, n, ha='right', va='center', fontsize=FS - 0.4, color=P['txt'])
    ax.axvline(1162, color=P['soft'], lw=0.8, ls=(0, (3, 3)))
    ax.set_xlim(-1000, 1800)
    ax.set_ylim(-0.7, len(items) - 0.3)
    ax.set_yticks([])
    ax.set_xticks([-500, 0, 500, 1000, 1500])
    ax.set_xticklabels(['500 BCE', '0', '500 CE', '1000', '1500'])
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    ax.set_axisbelow(True)
    clean(ax, P); ax.spines['left'].set_visible(False)
    ax.legend(handles=[Line2D([], [], marker=mk[0], color=cols[0], mfc=cols[0] if mode == 'color' else '#FFFFFF', mec=P['txt'], ms=6, label='연구의 추정(점은 평균, 선은 구간)'),
                       Line2D([], [], marker=mk[1], color=cols[1], mfc=cols[1] if mode == 'color' else '#FFFFFF', mec=P['txt'], ms=6, label='사료·구전의 서술'),
                       Line2D([], [], marker=mk[2], color=cols[2], mfc=cols[2] if mode == 'color' else '#FFFFFF', mec=P['txt'], ms=6, label='인물의 생애'),
                       Line2D([], [], color=P['soft'], lw=0.8, ls=(0, (3, 3)), label='점선 = 칭기즈 칸 생년 1162')],
              loc='upper center', bbox_to_anchor=(0.18, -0.09), ncol=1, frameon=False, fontsize=FS - 0.3)
    fig.subplots_adjust(left=0.58, right=0.98, top=0.99, bottom=0.30)
    save(fig, 'ages', mode)

if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_verdict(m); fig_clans(m); fig_ages(m)
    print('그림 3장 x 2 저장 ->', OUT)
