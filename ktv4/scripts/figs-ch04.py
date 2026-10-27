# -*- coding: utf-8 -*-
"""4장 「해수면과 해안선」 그림 생성: fig/fig-ch04-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book4):  python3 scripts/figs-ch04.py   (미리보기: PREVDIR=경로 python3 scripts/figs-ch04.py)
모든 그림은 논문이 본문에 적은 숫자(그리고 제1권이 옮겨 적은 숫자)를 다시 그린 것이며 측정 자료 그 자체나 해수면 곡선이 아니다.
값의 출처와 계산은 ms/code/ch04/ 의 calc4-N.py 와 로그. 글자 8 pt 이상, 색과 흑백 두 벌.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch04'))
import numpy as np
import figkit12 as K
import c14cal as CC
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

MODES = ('color', 'bw')
WARN = []


def pal(mode):
    if mode == 'color':
        return dict(p='#2F6F9A', b='#B5733A', v='#5E8C61', hl='#F1D9A0')
    return dict(p='#333333', b='#9A9A9A', v='#CFCFCF', hl='#DDDDDD')


# ---------------------------------------------------------------- 그림 1: 마지막 빙기 최성기 해수면 추정 범위
LGM = [
    ('Lambeck 등(2014), 29~21 ka', 134, 134, 'p'),
    ('Clark와 Tarasov(2014)가\n정리한 발표 범위', 105, 163, 'p'),
    ('Lewis 등(2013), 21~19 ka', 125, 125, 'p'),
    ('Saito(1998), 제1권 인용', 110, 130, 'v'),
    ('Ohshima(1990), 제1권 인용\n(3.5만 년 전 이전의 값)', 75, 85, 'v'),
    ('얼음 부피 5200만 km³의\n한 줄 환산(계산 4-1)', 128.6, 128.6, 'b'),
]


def fig_lgm(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 78)
    ax = f.add_axes([0.40, 0.17, 0.57, 0.80])
    n = len(LGM)
    for i, (nm, lo, hi, kind) in enumerate(LGM):
        y = n - 1 - i
        col = Q[kind]
        if hi - lo < 1e-9:
            ax.plot([lo], [y], marker='o', ms=6, color=col, mec=P['ink'], mew=0.5, zorder=3)
            ax.text(lo + 3, y, '%g' % lo, fontsize=8, va='center', color=P['ink'])
        else:
            ax.barh(y, hi - lo, left=lo, height=0.5, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=3, hatch=('////' if (mode == 'bw' and kind == 'v') else None))
            ax.text(hi + 3, y, '%g~%g' % (lo, hi), fontsize=8, va='center', color=P['ink'])
        ax.text(58, y, nm, fontsize=8, va='center', ha='right', color=P['ink'], transform=ax.transData)
    ax.set_xlim(60, 250); ax.set_ylim(-0.7, n - 0.3); ax.set_yticks([])
    ax.set_xlabel('현재보다 낮았던 해수면(m)')
    K.style_ax(ax, mode, grid='x')
    ax.legend(handles=[Patch(fc=Q['p'], ec=P['ink'], label='이번 장에서 읽은 논문'), Patch(fc=Q['v'], ec=P['ink'], hatch=('////' if mode == 'bw' else None), label='제1권이 옮긴 값'), Patch(fc=Q['b'], ec=P['ink'], label='이 책의 산술')],
              loc='lower right', frameon=True, framealpha=0.9, edgecolor='none', fontsize=8, bbox_to_anchor=(1.0, 0.0))
    WARN.extend(K.save(f, 'ch04-lgm', mode))


# ---------------------------------------------------------------- 그림 2: 지역별 상대 해수면
HUD = ([8.5, 7.5, 7.1, 6.4, 5.7, 3.5, 1.9], [289, 205, 177, 130, 105, 56, 30])
NS = ([8.3, 6.7, 4.2, 3.8, 1.7], [-34, -21, -9.9, -8.1, -3.3])
SB = ([9.0, 5.2, 4.4], [-35, -13.3, -10.9])
NF = ([5.3, 1.7], [4.9, 2.4])
CLARK = ([9.0, 7.0, 5.0], [-31.7, -12.2, -2.4])


def fig_rsl(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 130)
    ax1 = f.add_axes([0.10, 0.68, 0.87, 0.29]); ax2 = f.add_axes([0.10, 0.30, 0.87, 0.30])
    # 위: 허드슨만 남동쪽 융기 해안
    ax1.plot(HUD[0], HUD[1], marker='o', ms=3.4, color=Q['p'], lw=0.9, label='허드슨만 남동쪽(Vacchi 등 2018이 적은 높이)')
    ax1.set_xlim(11.8, 0); ax1.set_ylim(0, 320)
    ax1.set_ylabel('옛 바닷가 높이(m)'); ax1.set_xticklabels([])
    K.style_ax(ax1, mode)
    ax1.legend(loc='upper right', frameon=False, fontsize=8)
    ax1.text(0.2, 210, '곧바로 위 선의 기울기가\n구간마다 다르다(계산 4-4)', fontsize=8, color=P['ink'], ha='left', va='center') if False else None
    # 아래: 가장자리, 먼 곳, 한반도
    ax2.axhline(0, color=P['soft'], lw=0.6)
    ax2.axhspan(1, 3, xmin=(11.8 - 5.0) / 11.8, xmax=(11.8 - 1.5) / 11.8, color=Q['hl'], zorder=1)
    ax2.text(11.6, 9.0, '띠: 태평양 모형 고해수면 +1~+3 m(5.0~1.5 ka)', fontsize=8, color=P['ink'], ha='left', va='center')
    ax2.plot(NS[0], NS[1], marker='s', ms=3.2, color=Q['p'], lw=0.9, label='노바스코샤 동부(침강 쪽)')
    ax2.plot(SB[0], SB[1], marker='^', ms=3.4, color=P['soft'], lw=0.9, ls='--', label='세이블섬')
    ax2.plot(NF[0], NF[1], marker='D', ms=3.2, color=P['ink'], lw=0.9, ls=':', label='뉴펀들랜드 북서쪽')
    jo = [CC.summary(a, 100)['median'] / 1000 for a in (10000, 7000, 6000)]
    ax2.plot(jo, [-25, -10, 0], marker='o', ms=3.4, mfc='none', mec=Q['b'] if mode == 'color' else '#111111', color=Q['b'] if mode == 'color' else '#111111', lw=0.9, label='한반도 동해안 Jo(1980)(보정 연대)')
    ax2.plot(CLARK[0], CLARK[1], marker='v', ms=3.4, color=Q['b'] if mode == 'color' else '#777777', lw=0.9, ls='-.', label='한반도 남해 Clark 모형(제1권 인용)')
    ax2.set_xlim(11.8, 0); ax2.set_ylim(-42, 12)
    ax2.set_ylabel('상대 해수면(m)'); ax2.set_xlabel('나이(ka, 1000년 전; 왼쪽이 오래된 때)')
    K.style_ax(ax2, mode)
    ax2.legend(loc='upper center', frameon=False, fontsize=8, handletextpad=0.4, labelspacing=0.25, bbox_to_anchor=(0.45, -0.20), ncol=1)
    WARN.extend(K.save(f, 'ch04-rsl', mode))


# ---------------------------------------------------------------- 그림 3: 해수면 상승 속도 모음
RATE = [
    ('MWP-1A 전지구 속도(Deschamps 등)', 40, 40, 'p', '40 이상'),
    ('Hijma와 Cohen(2010) 배경 속도', 8.5, 11.5, 'p', '10±1.5'),
    ('Lambeck 등 16.5~8.2 ka 평균', 12, 12, 'p', '12'),
    ('Vacchi 등 초기 최대(지역 확인 필요)', 17, 17, 'p', '17'),
    ('Vacchi 등 중기(지역 확인 필요)', 9, 9, 'p', '9'),
    ('Vacchi 등 후기(지역 확인 필요)', 0, 2, 'p', '2 미만'),
    ('Hijma 등(2025) 두 가속 정점', 8, 9, 'p', '8~9'),
    ('Hijma 등(2025) 11~3 ka 평균', 3.7, 5.3, 'b', '4.7'),
    ('Saito 평균(제1권 값 환산)', 10, 13.3, 'b', '10~13'),
    ('Jo 동해안 구간(제1권 값 환산)', 5, 10, 'b', '5와 10'),
    ('Clark 모형 남해(제1권 값 환산)', 4.9, 9.75, 'b', '4.9~9.8'),
    ('Bloom과 Park 서해 8.6~4.8 ka', 1.6, 1.6, 'v', '1.6'),
    ('Bloom과 Park 서해 이후', 0.4, 0.4, 'v', '0.4'),
]


def fig_rate(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 108)
    ax = f.add_axes([0.53, 0.10, 0.44, 0.88])
    n = len(RATE)
    for i, (nm, lo, hi, kind, lab) in enumerate(RATE):
        y = n - 1 - i
        col = Q[kind]
        if hi - lo < 1e-9:
            ax.plot([lo], [y], marker='o', ms=6, color=col, mec=P['ink'], mew=0.5, zorder=3)
            if lab.startswith('40'):
                ax.annotate('', xy=(48, y), xytext=(lo + 1, y), arrowprops=dict(arrowstyle='->', color=P['ink'], lw=0.8))
                ax.text(lo - 1.5, y + 0.0, lab, fontsize=8, va='center', ha='right', color=P['ink'])
            else:
                ax.text(lo + 1.2, y, lab, fontsize=8, va='center', color=P['ink'])
        else:
            ax.barh(y, hi - lo, left=lo, height=0.5, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=3)
            ax.text(hi + 1.2, y, lab, fontsize=8, va='center', color=P['ink'])
        ax.text(-1.0, y, nm, fontsize=8, va='center', ha='right', color=P['ink'])
    ax.set_xlim(0, 50); ax.set_ylim(-0.7, n - 0.3); ax.set_yticks([])
    ax.set_xlabel('상승 속도(mm/년 = m/ka)')
    K.style_ax(ax, mode, grid='x')
    ax.legend(handles=[Patch(fc=Q['p'], ec=P['ink'], label='논문이 적은 값'), Patch(fc=Q['b'], ec=P['ink'], label='이 책의 산술(계산 4-2, 4-6)'), Patch(fc=Q['v'], ec=P['ink'], label='제1권이 옮긴 값')],
              loc='lower right', frameon=True, framealpha=0.92, edgecolor='none', fontsize=8, bbox_to_anchor=(1.0, 0.0))
    WARN.extend(K.save(f, 'ch04-rate', mode))


if __name__ == '__main__':
    for m in MODES:
        fig_lgm(m); fig_rsl(m); fig_rate(m)
    print('경고 합계', len(WARN))
