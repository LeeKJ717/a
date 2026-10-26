# -*- coding: utf-8 -*-
"""제3권 7장 그림 6장(색·흑백 SVG 두 벌). 모든 그림은 논문의 숫자를 다시 그린 것이고, 값은 ms/code/ch07 의 계산 결과에서 읽거나 같은 코드를 불러 다시 계산한다.
  fig-ch07-earliest-v1 : 지역별 가장 이른 보리 직접 연대(계산 7-2)
  fig-ch07-recalib-v1  : 논문 보정 구간과 이 책 재보정의 차(계산 7-1)
  fig-ch07-begash-v1   : Begash 숯 연대 34개의 보정 구간(계산 7-4)
  fig-ch07-claims-v1   : 중국 쪽 '가장 이른 밀' 서술들(계산 7-3)
  fig-ch07-millet-v1   : 기장 기록의 지역별 시작 연대(계산 7-5)
  fig-ch07-pmatrix-v1  : 지역별 가장 이른 보리 사이의 순서 확률(계산 7-2)
사용: python figs-ch07.py   (글꼴 Noto Sans CJK KR, 가로 5.1인치 = 본문 폭 129.6 mm 와 같아 글자가 줄지 않는다. 8.5pt 이상)"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager as fm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch07'); OUT = os.path.join(ROOT, 'fig')
sys.path.insert(0, CODE)
import c14lib as c, c14data as d
FONT = 'Noto Sans CJK KR'; FS = 8.5
assert FONT in {f.name for f in fm.fontManager.ttflist}
plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'svg.fonttype': 'path', 'font.size': FS, 'axes.titlesize': FS,
                     'axes.labelsize': FS, 'xtick.labelsize': FS, 'ytick.labelsize': FS, 'legend.fontsize': FS, 'figure.dpi': 100})
PAL = {'color': dict(a='#9C4F2E', b='#2F6F9A', c='#6B8E4E', d='#8A6BAA', g='#7D7255', soft='#4F6E80', grid='#B3C3CB', band='#F1EBDD', txt='#1B2A33'),
       'bw':    dict(a='#111111', b='#555555', c='#888888', d='#333333', g='#777777', soft='#444444', grid='#BBBBBB', band='#E6E6E6', txt='#111111')}
W = 5.1
def jd(n): return json.load(open(os.path.join(CODE, n), encoding='utf-8'))
def fmtbc(v, pos=None):
    v = int(round(v)); return ('기원전 %d' % -v) if v < 0 else ('기원후 %d' % v)
def save(fig, name, mode): fig.savefig(os.path.join(OUT, 'fig-ch07-%s-v1-%s.svg' % (name, mode)), format='svg', bbox_inches='tight', pad_inches=0.05); plt.close(fig)
def clean(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.tick_params(length=3)

def fig_earliest(mode):
    P = PAL[mode]; R = jd('calc-7-2-earliest.json')
    order = ['북서인도', '갠지스', '남인도', '청해', '티베트', '감숙', '중앙아시아', '신강', '중·동부 중국']
    fig, ax = plt.subplots(figsize=(W, 3.6)); clean(ax)
    # 각 날짜의 중앙값 점(옅게)
    byreg = {}
    for r in d.LIU:
        g = r[0]; g = '중앙아시아' if g.startswith('중앙아시아') else ('중·동부 중국' if g.startswith('중·동부') else g)
        byreg.setdefault(g, []).append(float(c.to_year(c.median(c.calibrate(r[3], r[4])))))
    for i, g in enumerate(order):
        y = len(order) - 1 - i; e = R[g]
        ax.plot(byreg[g], [y] * len(byreg[g]), 'o', ms=3.2, mfc='none', mec=P['g'], mew=0.7, alpha=0.9, zorder=2)
        ax.plot([e['earliest_lo_BC'], e['earliest_hi_BC']], [y, y], '-', lw=4.5, color=P['a'] if mode == 'color' else '#111111', solid_capstyle='butt', zorder=3)
        ax.plot([e['earliest_median_BC']], [y], 'D', ms=5.5, color='white', mec=P['txt'], mew=1.0, zorder=4)
        ax.text(1.01, y, 'n=%d' % e['n'], va='center', ha='left', fontsize=FS, color=P['soft'], transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order[::-1]); ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlim(-3000, 0); ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: '%d' % -v))
    ax.set_xticks([-2800, -2400, -2000, -1600, -1200, -800, -400]); ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':')
    ax.set_xlabel('기원전(년). 이 책의 IntCal20 보정')
    ax.plot([], [], 'o', ms=3.2, mfc='none', mec=P['g'], label='개별 날짜의 중앙값'); ax.plot([], [], '-', lw=4.5, color=P['a'] if mode == 'color' else '#111111', label='지역의 가장 이른 값 95% 구간'); ax.plot([], [], 'D', ms=5.5, color='white', mec=P['txt'], label='그 중앙값')
    ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.2), ncol=1, frameon=False, handletextpad=0.5)
    save(fig, 'earliest', mode)

def fig_recalib(mode):
    P = PAL[mode]; ds = []; de = []
    for tab, kind in ((d.LIU, 'l'), (d.DENG, 'd'), (d.BEGASH, 'b')):
        for r in tab:
            if kind == 'l': age, err, ps, pe = r[3], r[4], -r[5], -r[6]
            elif kind == 'd': age, err, ps, pe = r[4], r[5], r[6], r[7]
            else: age, err, ps, pe = r[2], r[3], r[4], r[5]
            p = c.calibrate(age, err); a, b = c.outer(p)
            ds.append(float(c.to_year(b)) - ps); de.append(float(c.to_year(a)) - pe)
    ds = np.array(ds); de = np.array(de)
    fig, axs = plt.subplots(2, 1, figsize=(W, 3.5), sharex=True)
    bins = np.arange(-140, 145, 10)
    for ax, v, lab, col in ((axs[0], ds, '구간의 오래된 끝', P['a']), (axs[1], de, '구간의 젊은 끝', P['b'])):
        clean(ax)
        ax.hist(np.clip(v, -139, 139), bins=bins, color=col, edgecolor='white', lw=0.5, hatch=None if mode == 'color' else ('//' if lab.startswith('구간의 오') else '..'))
        ax.axvline(0, color=P['txt'], lw=0.8)
        w30 = int((abs(v) <= 30).sum())
        ax.text(0.02, 0.92, '%s\n139행 중 %d행이 ±30년 안\n중앙값 %+.0f년' % (lab, w30, np.median(v)), transform=ax.transAxes, ha='left', va='top', fontsize=FS, color=P['txt'])
        ax.set_ylabel('행 수')
    axs[1].set_xlabel('이 책의 재보정 - 논문의 구간 (년, 양수 = 이 책이 더 젊다. ±140년 밖은 가장자리 칸에 모음)')
    save(fig, 'recalib', mode)

def fig_begash(mode):
    P = PAL[mode]; rows = []
    for lab, ph, age, err, ps, pe in d.BEGASH:
        p = c.calibrate(age, err); a, b = c.outer(p); rows.append((lab, ph, float(c.to_year(b)), float(c.to_year(a)), float(c.to_year(c.median(p)))))
    rows.sort(key=lambda r: r[4])
    colmap = {'1a': P['a'], '1b': P['a'], '2': P['b'], '3a': P['c'], '3b': P['c'], '4': P['d'], '5': P['g'], '6': P['g']}
    fig, ax = plt.subplots(figsize=(W, 5.0)); clean(ax)
    ax.axvspan(552, 1230, color=P['band'], zorder=0)
    ax.text(891, len(rows) - 1.6, '95.4% 구간 어디에도\n들지 않는 679년\n(기원후 552~1230)', ha='center', va='top', fontsize=FS, color=P['txt'])
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([r[2], r[3]], [y, y], '-', lw=3.2, color=colmap[r[1]], solid_capstyle='butt', zorder=3)
        ax.plot([r[4]], [y], 'o', ms=3.0, color='white', mec=P['txt'], mew=0.6, zorder=4)
    ax.set_xlim(-3700, 2000); ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] + ' (' + r[1] + ')' for r in rows[::-1]], fontsize=FS)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(fmtbc)); ax.set_xticks([-2500, -1500, -500, 500, 1500])
    ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':'); ax.set_xlabel('보정 연대(IntCal20, 이 책의 보정). 괄호는 단계')
    save(fig, 'begash', mode)

def fig_claims(mode):
    P = PAL[mode]; C = jd('calc-7-3-claims.json')['claims']
    names = sorted(C, key=lambda k: -(C[k][0] + C[k][1]) / 2)
    fig, ax = plt.subplots(figsize=(W, 4.2)); clean(ax)
    ax.axvspan(-2200, -1800, color=P['band'], zorder=0)
    ax.text(-2000, len(names) - 0.2, '보수적 추정 띠\n(Stevens 등 2016)', ha='center', va='bottom', fontsize=FS, color=P['txt']); ax.set_ylim(-0.7, len(names) + 0.9)
    for i, k in enumerate(names):
        y = len(names) - 1 - i; a, b, _ = C[k]
        col = P['a'] if k.startswith('Long') else (P['b'] if k.startswith(('Zhou', 'Tasbas')) else P['c'])
        if a == b: ax.plot([-a], [y], 'D', ms=6, color=col, mec=P['txt'], mew=0.8, zorder=4)
        else: ax.plot([-a, -b], [y, y], '-', lw=5, color=col, solid_capstyle='butt', zorder=3)
    ax.set_yticks(range(len(names))); ax.set_yticklabels([k.replace('(', '\n(', 1) if len(k) > 26 else k for k in names[::-1]], fontsize=FS)
    ax.set_xlim(-3750, -1300); ax.xaxis.set_major_formatter(plt.FuncFormatter(fmtbc)); ax.set_xticks([-3500, -3000, -2500, -2000, -1500])
    ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':'); ax.set_xlabel('논문이 낸 달력 연대(점은 마름모, 구간은 막대)')
    save(fig, 'claims', mode)

def fig_millet(mode):
    P = PAL[mode]; M = jd('calc-7-5-millet-lag.json')['points']
    fig, ax = plt.subplots(figsize=(W, 3.7)); clean(ax)
    for i, (n, a, b, s, l) in enumerate(M):
        y = len(M) - 1 - i
        col = P['b'] if 'Begash' in n or 'Dali' in n or 'Aigyrzhal' in n else (P['a'] if ('Cishan' in n or '서요하' in n or '한반도' in n) else P['c'])
        if a == b: ax.plot([-a], [y], 'D', ms=6, color=col, mec=P['txt'], mew=0.8, zorder=4)
        else: ax.plot([-a, -b], [y, y], '-', lw=5, color=col, solid_capstyle='butt', zorder=3)
    short = {'Cishan': 'Cishan(하북) 기장 저장 구덩이', '서요하': '서요하 12D56 야생형 기장 2알', '한반도': '한반도 조·기장 도착', 'Dali': 'Dali 가축에 기장 먹임', 'Aigyrzhal': 'Aigyrzhal-3 사람 뼈 C4 신호', 'Begash': 'Begash 기장 직접 연대', '유럽': '유럽 기장 재배 시작', 'Troy': 'Troy 기장'}
    labs = []
    for n, *_ in M:
        for k, v in short.items():
            if k in n: labs.append(v); break
    ax.set_yticks(range(len(M))); ax.set_yticklabels(labs[::-1])
    ax.set_xlim(-8700, -1000); ax.xaxis.set_major_formatter(plt.FuncFormatter(fmtbc)); ax.set_xticks([-8000, -6000, -4000, -2000])
    ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':'); ax.set_xlabel('논문이 낸 달력 연대(점은 마름모, 구간은 막대). Cishan은 인용된 초록의 값')
    save(fig, 'millet', mode)

def fig_pmatrix(mode):
    P = PAL[mode]; R = jd('calc-7-2-earliest.json')['matrix']; order = R['order']; M = np.array([[np.nan if x is None else x for x in row] for row in R['P']])
    fig, ax = plt.subplots(figsize=(W, 4.4))
    cm = 'YlOrBr' if mode == 'color' else 'Greys'
    im = ax.imshow(M, cmap=cm, vmin=0, vmax=1)
    ax.set_xticks(range(len(order))); ax.set_yticks(range(len(order)))
    ax.set_xticklabels([o.replace('·', '·\n').replace('중앙아시아', '중앙\n아시아').replace('북서인도', '북서\n인도') for o in order], fontsize=FS)
    ax.set_yticklabels(order, fontsize=FS)
    for i in range(len(order)):
        for j in range(len(order)):
            if i == j: ax.text(j, i, '-', ha='center', va='center', fontsize=FS); continue
            v = M[i, j]; ax.text(j, i, '%.2f' % v, ha='center', va='center', fontsize=FS, color='white' if v > 0.62 else P['txt'])
    ax.set_xlabel('열 지역'); ax.set_ylabel('행 지역')
    save(fig, 'pmatrix', mode)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for f in (fig_earliest, fig_recalib, fig_begash, fig_claims, fig_millet, fig_pmatrix):
            f(mode); print(mode, f.__name__)
