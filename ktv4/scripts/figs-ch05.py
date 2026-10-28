# -*- coding: utf-8 -*-
"""5장 「해류와 대순환」 그림 생성: fig/fig-ch05-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book4):  python3 scripts/figs-ch05.py   (미리보기: PREVDIR=경로 python3 scripts/figs-ch05.py)
두 그림 모두 논문(4장이 옮긴 숫자)과 제1권이 적은 숫자를 이 책이 환산해 다시 그린 것이며 측정 자료가 아니다.
계산은 ms/code/ch05/ 의 calc5-N.py 와 로그. 글자 8 pt 이상, 색과 흑백 두 벌.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch05'))
import numpy as np
import figkit12 as K
import c14cal as CC
from matplotlib.patches import Patch

MODES = ('color', 'bw')
WARN = []
YR = 3.156e7; A = 3.61e14


def sv(mm):
    return mm * 1e-3 * A / YR / 1e6


def pal(mode):
    if mode == 'color':
        return dict(p='#2F6F9A', b='#B5733A', v='#5E8C61', hl='#F1D9A0')
    return dict(p='#333333', b='#9A9A9A', v='#CFCFCF', hl='#DDDDDD')


# ---------------------------------------------------------------- 그림 1: 담수 유량(Sv)
ROWS = [
    ('MWP-1A 전지구 속도 하한\n(40 mm/yr 이상, 계산 5-2)', sv(40), sv(40), 'p'),
    ('타히티 14~18 m / 340년\n(4장 계산, 계산 5-2)', sv(41.2), sv(52.9), 'b'),
    ('8.3 ka 로테르담 도약의 부피\n10.7±4.5×10¹⁴ m³ / 200년(계산 5-1)', 6.2e14 / 200 / YR / 1e6 * 1e0, 15.2e14 / 200 / YR / 1e6, 'b'),
    ('Lambeck 등 16.5~8.2 ka 평균\n12 mm/yr(계산 5-2)', sv(12), sv(12), 'p'),
    ('Hijma 등 두 가속 정점\n8~9 mm/yr(계산 5-2)', sv(8), sv(9), 'p'),
    ('Hijma 등 11~3 ka 평균\n4.7 mm/yr(계산 5-2)', sv(3.66), sv(5.28), 'b'),
    ('남극 기여 평균(Ullman 등 함의)\n0.51~1.03 mm/yr(계산 5-2)', sv(0.51), sv(1.03), 'b'),
]


def fig_flux(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 100)
    ax = f.add_axes([0.46, 0.13, 0.51, 0.84])
    n = len(ROWS)
    for i, (nm, lo, hi, kind) in enumerate(ROWS):
        y = n - 1 - i
        if hi - lo < 1e-9:
            ax.plot([lo], [y], marker='o', ms=6, color=Q[kind], mec=P['ink'], mew=0.5, zorder=3)
            ax.text(lo * 1.18, y, '%.2f' % lo, fontsize=8, va='center', color=P['ink'])
        else:
            ax.barh(y, hi - lo, left=lo, height=0.5, color=Q[kind], edgecolor=P['ink'], linewidth=0.5, zorder=3)
            ax.text(hi * 1.12, y, '%.3f~%.3f' % (lo, hi) if hi < 0.1 else '%.2f~%.2f' % (lo, hi), fontsize=8, va='center', color=P['ink'])
        ax.text(0.0035, y, nm, fontsize=8, va='center', ha='right', color=P['ink'])
    ax.set_xscale('log'); ax.set_xlim(0.004, 4); ax.set_ylim(-0.7, n - 0.3); ax.set_yticks([])
    ax.set_xlabel('담수 유량(Sv, 1 Sv = 100만 m³/s), 로그 눈금')
    K.style_ax(ax, mode, grid='x')
    ax.legend(handles=[Patch(fc=Q['p'], ec=P['ink'], label='논문 속도를 이 책이 환산'), Patch(fc=Q['b'], ec=P['ink'], label='이 책의 산술에서 나온 값')], loc='upper left', frameon=True, framealpha=0.92, edgecolor='none', fontsize=8, bbox_to_anchor=(0.0, 1.0))
    WARN.extend(K.save(f, 'ch05-flux', mode))


# ---------------------------------------------------------------- 그림 2: 쓰시마 해협 안부 위의 물 깊이
def fig_sill(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 100)
    ax = f.add_axes([0.11, 0.38, 0.86, 0.58])
    ax.axhline(10, color=P['soft'], lw=0.5, ls=':'); ax.axhline(50, color=P['soft'], lw=0.5, ls=':')
    ax.text(11.8, 12, '해수면 −120 m(Saito)이면 안부 위 10 m', fontsize=8, color=P['ink'], ha='left', va='bottom')
    ax.text(11.8, 52, '해수면 −80 m(Ohshima)이면 50 m', fontsize=8, color=P['ink'], ha='left', va='bottom')
    cl = Q['b'] if mode == 'color' else '#777777'
    ax.plot([9.0, 7.0, 5.0], [130 - 31.7, 130 - 12.2, 130 - 2.4], marker='v', ms=4, color=cl, lw=1.0, ls='-.', label='Clark 모형(제1권 인용, 역년)')
    jo = [CC.summary(a, 100)['median'] / 1000 for a in (10000, 7000)]
    ax.plot(jo, [130 - 25, 130 - 10], marker='o', ms=4, mfc='none', mec=P['ink'], color=P['ink'], lw=1.0, label='Jo(1980)(14C 나이를 보정)')
    ax.plot([10.0], [130 - 40], marker='s', ms=4.5, color=Q['p'], ls='none', label='Saito(1998), 약 10 ka(나이 눈금 불명)')
    for x, ls, lab in ((9.617, '-', '쓰시마 매몰 하곡의 난류 계열 조개 8,610 BP(보정 중앙 9.62 ka)'), (9.3, '--', '동해 코어: 한랭 군집이 끝나는 9.3 cal BP'), (7.3, ':', '동해 남부의 현재와 같은 표층 조건 7.3 cal BP')):
        ax.axvline(x, color=P['ink'] if ls != '--' else P['soft'], lw=0.9, ls=ls, zorder=2, label=lab)
    ax.set_xlim(12.0, 0); ax.set_ylim(0, 135)
    ax.set_ylabel('안부(130 m) 위의 물 깊이(m)'); ax.set_xlabel('나이(ka; 왼쪽이 오래된 때)')
    K.style_ax(ax, mode)
    ax.legend(loc='upper center', frameon=False, fontsize=8, handletextpad=0.4, labelspacing=0.25, bbox_to_anchor=(0.45, -0.20), ncol=1)
    WARN.extend(K.save(f, 'ch05-sill', mode))

# ---------------------------------------------------------------- 그림 3: 논문이 적은 시간창(계산 5-5)
WIN = [
    ('AMOC', 'AMOC 약화 9.2~8 ka (Gerber 등 2025)', 9.2, 8.0, 'p'),
    ('AMOC', '방류 8.47 ka, 한랭 사건 8.4~8.0 ka (Barber 등 1999)', 8.4, 8.0, 'b'),
    ('AMOC', 'AMOC 안정 6.5 ka 이후 (Gerber 등 2025)', 6.5, 0.0, 'p'),
    ('AMOC', '깊은 물 유속 감소 6.5 ka 이후 (Hoogakker 등 2011)', 6.5, 0.0, 'b'),
    ('ENSO', '페루 서늘 편향 7.5~6.7 ka (Carré 등 2014)', 7.5, 6.7, 'p'),
    ('ENSO', 'ENSO 분산 감소 5~3 ka (Emile-Geay 등)', 5.0, 3.0, 'b'),
    ('ENSO', 'ENSO 억제 5~4 ka (Carré 등 2014)', 5.0, 4.0, 'p'),
    ('ENSO', '강수 강도 증가 4.2 ka 이후 (Conroy 등 2008)', 4.2, 0.0, 'b'),
    ('ENSO', '강수 정점 2.0~1.5 ka (Conroy 등 2008)', 2.0, 1.5, 'p'),
]


def fig_windows(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 100)
    ax = f.add_axes([0.05, 0.13, 0.92, 0.84])
    n = len(WIN)
    for i, (grp, nm, a, b, kind) in enumerate(WIN):
        y = n - 1 - i
        ax.barh(y, a - b, left=b, height=0.5, color=Q[kind], edgecolor=P['ink'], linewidth=0.5, zorder=3)
        ax.text(9.95, y + 0.3, nm, fontsize=8, va='bottom', ha='left', color=P['ink'])
    ax.axvspan(8.4, 8.0, color=Q['hl'], zorder=1)
    ax.set_xlim(10, 0); ax.set_ylim(-0.7, n + 0.2); ax.set_yticks([])
    ax.set_xlabel('나이(ka; 왼쪽이 오래된 때). 논문 초록이 적은 시간창이며 불확실성 막대는 그리지 않음')
    K.style_ax(ax, mode, grid='x')
    WARN.extend(K.save(f, 'ch05-windows', mode))


if __name__ == '__main__':
    for m in MODES:
        fig_flux(m); fig_sill(m); fig_windows(m)
    print('경고 합계', len(WARN))
