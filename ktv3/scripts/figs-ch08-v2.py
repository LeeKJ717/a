# -*- coding: utf-8 -*-
"""제3권 8장 v2 그림 2장(색·흑백 SVG 두 벌): fig/fig-ch08-*-v1-{color,bw}.svg  (이름의 v1은 그림 파일의 첫 판이라는 뜻이며 원고 v2에서 처음 쓴다)
  wetwin   : 저자들이 호수·꽃가루 기록에서 '습윤'이라고 적은 기간 일곱 곳과 4.2 ka 창(계산 8-7)
  eventwin : 지역별 가장 이른 보리의 95% 구간과 4200~3900 cal BP 창(계산 8-6)
모든 그림은 논문의 숫자를 다시 그린 것이다. 값은 ms/code/ch08 의 json 에서 읽는다. 사용: python3 scripts/figs-ch08-v2.py"""
import os, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch08'); OUT = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p8')
os.makedirs(PREV, exist_ok=True)
FONT = 'Noto Sans CJK KR'; FS = 8.5
assert FONT in {f.name for f in fm.fontManager.ttflist}
plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'svg.fonttype': 'path', 'font.size': FS, 'axes.titlesize': FS,
                     'axes.labelsize': FS, 'xtick.labelsize': FS, 'ytick.labelsize': FS, 'legend.fontsize': FS, 'figure.dpi': 100})
PAL = {'color': dict(a='#9C4F2E', b='#2F6F9A', c='#6B8E4E', soft='#4F6E80', grid='#B3C3CB', band='#F0DDD3', txt='#1B2A33', bar='#2F6F9A'),
       'bw':    dict(a='#111111', b='#555555', c='#888888', soft='#444444', grid='#BBBBBB', band='#DDDDDD', txt='#111111', bar='#444444')}
W = 5.1
def jd(n): return json.load(open(os.path.join(CODE, n), encoding='utf-8'))
def save(fig, name, mode):
    fig.savefig(os.path.join(OUT, 'fig-ch08-%s-v1-%s.svg' % (name, mode)), format='svg', bbox_inches='tight', pad_inches=0.05)
    fig.savefig(os.path.join(PREV, '%s-%s.png' % (name, mode)), dpi=130, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)
def clean(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.tick_params(length=3)

def fig_wetwin(mode):
    P = PAL[mode]; R = jd('calc-8-7-wetwindows.json')['records']
    short = {'Bayanchagan': 'Bayanchagan (Guiot 등 2008)', 'Daihai': 'Daihai (Li 등 2004)', 'Hulun': 'Hulun (Wen 등 2010)', 'Gonghai': 'Gonghai (Chen 등 2015)',
             'Tianchi': 'Tianchi (Li 등 2022)', 'Bayan Nuur': 'Bayan Nuur (Tian 등 2014)', 'Hovsgol': 'Hovsgol (Katsuta 등 2017)'}
    def lab(n):
        for k, v in short.items():
            if n.startswith(k): return v
    fig, ax = plt.subplots(figsize=(W, 3.5)); clean(ax)
    ax.axvspan(3900, 4200, color=P['band'], zorder=0)
    ax.axvline(4200, color=P['txt'], lw=1.0, ls='--', zorder=1)
    n = len(R)
    for i, r in enumerate(R):
        y = n - 1 - i
        ax.plot([r['end'], r['start']], [y, y], '-', lw=6, color=P['bar'], solid_capstyle='butt', zorder=3)
        ax.text(r['end'] - 150, y, '%d' % r['end'], va='center', ha='left', fontsize=FS - 0.5, color=P['soft'])
    ax.set_yticks(range(n)); ax.set_yticklabels([lab(r['name']) for r in R][::-1])
    ax.set_xlim(11500, 1700); ax.set_ylim(-0.7, n + 0.2)
    ax.set_xticks([11000, 9000, 7000, 5000, 3000]); ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':')
    ax.set_xlabel('cal BP (왼쪽이 오래됨). 막대 끝의 숫자는 저자가 적은 습윤 구간의 끝')
    ax.fill_between([], [], color=P['band'], label='4.2 ka 사건 창 4200~3900'); ax.plot([], [], '-', lw=6, color=P['bar'], label='저자가 습윤이라고 적은 기간')
    ax.legend(loc='upper center', bbox_to_anchor=(0.4, -0.2), ncol=1, frameon=False, handletextpad=1.0, handlelength=2.5)
    save(fig, 'wetwin', mode)

def fig_eventwin(mode):
    P = PAL[mode]; R = jd('calc-8-6-event-window.json')
    order = ['북서인도', '갠지스', '청해', '남인도', '감숙', '중앙아시아', '티베트', '신강', '중·동부 중국']
    fig, ax = plt.subplots(figsize=(W, 3.5)); clean(ax)
    ax.axvspan(3900, 4200, color=P['band'], zorder=0)
    for i, g in enumerate(order):
        y = len(order) - 1 - i; lo, md, hi = R[g]['first_calBP']
        ax.plot([lo, hi], [y, y], '-', lw=5, color=P['bar'], solid_capstyle='butt', zorder=3)
        ax.text(1.01, y, '창 안 %.3f' % R[g]['first_in_window'], va='center', ha='left', transform=ax.get_yaxis_transform(), color=P['soft'], fontsize=FS - 0.5)
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order[::-1]); ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlim(5000, 2600); ax.set_xticks([4800, 4400, 4000, 3600, 3200, 2800]); ax.grid(axis='x', color=P['grid'], lw=0.6, ls=':')
    ax.set_xlabel('cal BP (왼쪽이 오래됨)')
    ax.fill_between([], [], color=P['band'], label='4.2 ka 사건 창 4200~3900 (Zhang & Zhang 2023)'); ax.plot([], [], '-', lw=5, color=P['bar'], label='가장 이른 보리 95% 구간(오른쪽 숫자: 창 안에 있을 확률)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.3, -0.2), ncol=1, frameon=False, handletextpad=1.0, handlelength=2.5)
    save(fig, 'eventwin', mode)

if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_wetwin(m); fig_eventwin(m)
    print('ok')
