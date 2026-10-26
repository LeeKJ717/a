# -*- coding: utf-8 -*-
"""제3권 8장 그림 3장(색·흑백 SVG 두 벌). 모든 그림은 논문의 숫자를 다시 그린 것이고, 계산 값은 ms/code/ch08 의 json 에서 읽는다.
  fig-ch08-first-v1   : 지역별 가장 이른 보리(95% 구간, cal BP)와 4200 cal BP, 습윤 창(계산 8-1, 8-2)
  fig-ch08-windows-v1 : 논문이 적은 시기 구간들과 Begash 숯 빈 틈(계산 8-2, 8-3)
  fig-ch08-rain-v1    : 5~10월 강수 125 mm 문턱을 넘기 위해 필요한 비율(계산 8-4)
사용: python figs-ch08.py   (글꼴 Noto Sans CJK KR, 가로 5.1인치, 8.5pt 이상)"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch08'); OUT = os.path.join(ROOT, 'fig')
FONT = 'Noto Sans CJK KR'; FS = 8.5
assert FONT in {f.name for f in fm.fontManager.ttflist}
plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'svg.fonttype': 'path', 'font.size': FS, 'axes.titlesize': FS,
                     'axes.labelsize': FS, 'xtick.labelsize': FS, 'ytick.labelsize': FS, 'legend.fontsize': FS, 'figure.dpi': 100})
PAL = {'color': dict(a='#9C4F2E', b='#2F6F9A', c='#6B8E4E', g='#7D7255', soft='#4F6E80', grid='#B3C3CB', band='#DDE9EE', txt='#1B2A33', gap='#E8D3C8'),
       'bw':    dict(a='#111111', b='#555555', c='#888888', g='#777777', soft='#444444', grid='#BBBBBB', band='#E6E6E6', txt='#111111', gap='#CFCFCF')}
W = 5.1
def jd(n): return json.load(open(os.path.join(CODE, n), encoding='utf-8'))
def save(fig, name, mode): fig.savefig(os.path.join(OUT, 'fig-ch08-%s-v1-%s.svg' % (name, mode)), format='svg', bbox_inches='tight', pad_inches=0.05); plt.close(fig)
def clean(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.tick_params(length=3)

def fig_first(mode):
    P = PAL[mode]; R = jd('calc-8-1-after42.json')
    order = sorted(R, key=lambda g: -R[g]['first_calBP'][1])
    fig, ax = plt.subplots(figsize=(W, 3.5)); clean(ax)
    ax.axvspan(2900, 6200, color=P['band'], zorder=0)
    ax.axvline(4200, color=P['txt'], lw=1.0, ls='--', zorder=1)
    for i, g in enumerate(order):
        y = len(order) - 1 - i; lo, md, hi = R[g]['first_calBP']
        ax.plot([lo, hi], [y, y], '-', lw=5, color=P['a'] if mode == 'color' else '#111111', solid_capstyle='butt', zorder=3)
        ax.plot([md], [y], 'D', ms=5, color='white', mec=P['txt'], mew=1.0, zorder=4)
        ax.text(1.01, y, 'n=%d' % R[g]['n'], va='center', ha='left', transform=ax.get_yaxis_transform(), color=P['soft'])
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order[::-1]); ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlim(5000, 2400); ax.set_xticks([4800, 4400, 4000, 3600, 3200, 2800]); ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':')
    ax.set_xlabel('cal BP (왼쪽이 오래됨)')
    ax.text(4200, len(order) - 0.45, '4200', ha='center', va='bottom', color=P['txt'], bbox=dict(fc='white', ec='none', pad=1.5), zorder=6)
    ax.plot([], [], '-', lw=5, color=P['a'] if mode == 'color' else '#111111', label='지역의 가장 이른 보리 95% 구간'); ax.plot([], [], 'D', ms=5, color='white', mec=P['txt'], label='중앙값')
    ax.plot([], [], '--', color=P['txt'], label='4200 cal BP'); ax.fill_between([], [], color=P['band'], label='습윤 창 2900~6200 cal BP (Li 등 2022)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.4, -0.2), ncol=1, frameon=False, handletextpad=0.5)
    ax.set_ylim(-0.7, len(order) + 0.2)
    save(fig, 'first', mode)

def fig_windows(mode):
    P = PAL[mode]; R = jd('calc-8-2-windows.json'); G = jd('calc-8-3-gap.json')
    items = [('Zhou 등(2020) Tongtian 동굴 점유', 3200, 5200, 'b'),
             ('Ren 등(2021) 기장만', 4000, 5900, 'c'),
             ('Ren 등(2021) 보리·밀 보조', 3600, 4000, 'a'),
             ('Ren 등(2021) 보리 증가기', 2100, 3600, 'g'),
             ('Spengler 등(2014b) Tasbas 2a', 3209, 3439, 'b'),
             ('Cui 등(2013) 북방 유목 단계(제1권 11장)', 2500, 3000, 'g'),
             ('Begash 숯 연대의 빈 틈(계산 8-3)', G['gap'][0], G['gap'][1], 'a')]
    fig, ax = plt.subplots(figsize=(W, 3.4)); clean(ax)
    ax.axvspan(2900, 6200, color=P['band'], zorder=0)
    ax.axvline(4200, color=P['txt'], lw=1.0, ls='--', zorder=1); ax.axvline(1100, color=P['txt'], lw=1.0, ls=':', zorder=1)
    for i, (nm, lo, hi, k) in enumerate(items):
        y = len(items) - 1 - i
        col = P[k] if mode == 'color' else ('#111111' if i in (0, 2, 6) else '#888888')
        ax.plot([lo, hi], [y, y], '-', lw=6, color=col, solid_capstyle='butt', zorder=3)
    ax.set_yticks(range(len(items))); ax.set_yticklabels([x[0] for x in items][::-1])
    ax.set_ylim(-0.7, len(items) + 0.4); ax.set_xlim(6400, 0); ax.set_xticks([6000, 5000, 4000, 3000, 2000, 1000, 0]); ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':')
    ax.set_xlabel('cal BP (왼쪽이 오래됨). Ren 등(2021)의 BP는 보정 여부가 초록에 없어 cal BP로 두었다')
    ax.text(4200, len(items) - 0.2, '4200', ha='center', va='bottom', color=P['txt'], bbox=dict(fc='white', ec='none', pad=1.5), zorder=6); ax.text(1100, len(items) - 0.2, '1100', ha='center', va='bottom', color=P['txt'], bbox=dict(fc='white', ec='none', pad=1.5), zorder=6)
    ax.fill_between([], [], color=P['band'], label='습윤 창 2900~6200 (Li 등 2022)'); ax.plot([], [], '--', color=P['txt'], label='4200 (4.2 ka 사건의 점 값)'); ax.plot([], [], ':', color=P['txt'], label='1100 (같은 논문의 건조 정점)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.35, -0.25), ncol=1, frameon=False, handletextpad=0.5)
    save(fig, 'windows', mode)

def fig_rain(mode):
    P = PAL[mode]
    fig, ax = plt.subplots(figsize=(W, 3.2)); clean(ax)
    Pg = np.linspace(125, 1100, 300); ax.plot(Pg, 125 / Pg, '-', color=P['b'] if mode == 'color' else '#111111', lw=1.8)
    ax.axvspan(0, 125, color=P['gap'], zorder=0)
    pts = [(200, '200 mm\nSemirech\'ye 저지'), (500, '500 mm\n초원 평균 상한'), (550, '550 mm\nZhuanglang'), (1000, '1000 mm\n산기슭')]
    offs = {200: (6, 8), 500: (6, 20), 550: (8, 6), 1000: (-4, 22)}
    for x, lab in pts:
        ax.plot([x], [125 / x], 'o', ms=5, color=P['a'] if mode == 'color' else '#111111', zorder=4)
    ax.annotate('200 mm\n(Semirech\'ye 저지)\nf = 0.625', (200, 0.625), xytext=(250, 0.78), arrowprops=dict(arrowstyle='-', color=P['soft'], lw=0.7), va='bottom', color=P['txt'])
    ax.annotate('500~550 mm\nf = 0.25, 0.23', (525, 0.24), xytext=(600, 0.42), arrowprops=dict(arrowstyle='-', color=P['soft'], lw=0.7), va='bottom', color=P['txt'])
    ax.annotate('1000 mm\nf = 0.125', (1000, 0.125), xytext=(850, 0.30), arrowprops=dict(arrowstyle='-', color=P['soft'], lw=0.7), va='bottom', color=P['txt'])
    ax.text(62, 0.5, '연강수 125 mm 미만: 문턱 불가', ha='center', va='center', rotation=90, color=P['txt'])
    ax.set_xlim(0, 1100); ax.set_ylim(0, 1.05); ax.set_xticks([0, 200, 400, 600, 800, 1000]); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.grid(color=P['grid'], lw=0.6, ls=':')
    ax.set_xlabel('연강수량 P (mm)'); ax.set_ylabel('필요한 5~10월 비율 f = 125 / P')
    save(fig, 'rain', mode)

if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_first(m); fig_windows(m); fig_rain(m)
    print('ok')
