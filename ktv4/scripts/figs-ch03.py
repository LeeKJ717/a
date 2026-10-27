# -*- coding: utf-8 -*-
"""3장 「온실기체의 기록」 그림 생성: fig/fig-ch03-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book4):  python3 scripts/figs-ch03.py   (미리보기 PNG: PREVDIR=경로 python3 scripts/figs-ch03.py)
자료 그림은 모두 논문의 자료표(NOAA 고기후 자료 센터와 저자 사이트의 표)나 논문이 적은 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다.
표는 ms/code/ch03/ 의 csv 이고, 계산은 같은 폴더의 calc3-N.py 와 로그에 있다. 글자 8 pt 이상, 색과 흑백 두 벌.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch03'))
import numpy as np
import figkit12 as K
import common3 as C3
import matplotlib.pyplot as plt

MODES = ('color', 'bw')
te, ye, se, de = C3.edc(); tt, yt, st, dt = C3.taylor(); tc, yc, oc = C3.ch4()
WARN = []


def pal(mode):
    P = K.C[mode]
    if mode == 'color':
        return dict(edc='#2F6F9A', tay='#B5733A', fit='#1B2A33', hl='#F1D9A0', mk='#9C4F2E')
    return dict(edc='#222222', tay='#8A8A8A', fit='#111111', hl='#DDDDDD', mk='#111111')


# ---------------------------------------------------------------- 그림 1: 홀로세 이산화탄소 두 코어
def fig_co2(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 108)
    ax = f.add_axes([0.095, 0.40, 0.88, 0.57]); ax2 = f.add_axes([0.095, 0.085, 0.88, 0.20])
    k = te <= 11100
    ax.errorbar(te[k] / 1000, ye[k], yerr=se[k], fmt='o', ms=2.6, color=Q['edc'], ecolor=Q['edc'], elinewidth=0.5, capsize=0, label='Dome C(Monnin 등 2004의 표)', zorder=3)
    ax.plot(tt / 1000, yt, marker='s', ms=2.6, ls='none', mfc='none', mec=Q['tay'], mew=0.8, label='Taylor Dome(Indermühle 등 1999의 표)', zorder=3)
    # 1000년 칸 평균(Dome C)
    xs, ys = [], []
    for a in range(0, 11000, 1000):
        kk = (te >= a) & (te < a + 1000)
        xs.append(a / 1000 + 0.5); ys.append(ye[kk].mean())
    ax.plot(xs, ys, color=Q['fit'], lw=1.2, label='Dome C 1000년 칸 평균', zorder=4)
    # Ruddiman(2003)이 적은 값
    ax.plot([10.5], [268], marker='D', ms=5.5, mfc=Q['hl'], mec=P['ink'], ls='none', zorder=5, label='Ruddiman(2003)이 적은 값')
    ax.plot([8.0], [261], marker='D', ms=5.5, mfc=Q['hl'], mec=P['ink'], ls='none', zorder=5)
    ax.plot([0.0, 0.0], [280, 285], color=P['ink'], lw=1.4, zorder=5)
    ax.axvline(7.65, color=P['soft'], lw=0.8, ls='--', zorder=2)
    ax.text(7.55, 251.6, '꺾는 점(Dome C) 7.65 ka\n(부트스트랩 구간 7.4~8.0)', fontsize=8, color=P['ink'], ha='left', va='bottom')
    ax.set_xlim(11.2, -0.35); ax.set_ylim(250.5, 288)
    ax.set_ylabel('이산화탄소(ppm)'); ax.set_xticklabels([])
    K.style_ax(ax, mode)
    lg = ax.legend(loc='upper left', frameon=True, framealpha=0.92, edgecolor='none', fontsize=8, handletextpad=0.4, borderpad=0.3, labelspacing=0.25); lg.set_zorder(10)
    # 아래: 두 코어의 차
    ta = tt; ok = (ta >= te.min()) & (ta <= 11000)
    d = yt[ok] - np.interp(ta[ok], te, ye)
    ax2.axhline(0, color=P['soft'], lw=0.6)
    ax2.plot(ta[ok] / 1000, d, marker='o', ms=2.4, ls='-', lw=0.5, color=Q['tay'])
    ax2.set_xlim(11.2, -0.35); ax2.set_ylim(-8, 10)
    ax2.set_ylabel('Taylor − Dome C\n(ppm)', fontsize=8); ax2.set_xlabel('나이(ka, 1000년 전; 왼쪽이 오래된 때)')
    K.style_ax(ax2, mode)
    WARN.extend(K.save(f, 'ch03-co2', mode))


# ---------------------------------------------------------------- 그림 2: 홀로세 메탄(북 그린란드 표본)
def fig_ch4(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 100)
    ax = f.add_axes([0.095, 0.15, 0.58, 0.80]); ax2 = f.add_axes([0.765, 0.15, 0.215, 0.80])
    k = (tc >= 200) & (tc <= 11700)
    ax.plot(tc[k] / 1000, yc[k], marker='o', ms=2.2, ls='none', color=Q['edc'], alpha=0.8, label='표본 점(Beck 등 2018 표의 일부)', zorder=3)
    xs, ms_ = [], []
    for a in np.arange(200, 11700, 500):
        kk = (tc >= a) & (tc < a + 500)
        if kk.sum() >= 3:
            xs.append((a + 250) / 1000); ms_.append(np.median(yc[kk]))
    ax.plot(xs, ms_, color=Q['fit'], lw=1.3, label='500년 칸 중앙값', zorder=4)
    imin = int(np.argmin(ms_))
    ax.plot([xs[imin]], [ms_[imin]], marker='v', ms=6, mfc=Q['hl'], mec=P['ink'], ls='none', zorder=5)
    ax.text(xs[imin] + 0.15, ms_[imin] - 12, '최소 칸 %.1f~%.1f ka\n%.0f ppb' % (xs[imin] - 0.25, xs[imin] + 0.25, ms_[imin]), fontsize=8, color=P['ink'], ha='left', va='top')
    ax.axvspan(8.0, 8.4, color=Q['hl'], alpha=0.6, zorder=1, lw=0)
    ax.text(8.2, 790, '8.2 ka', fontsize=8, ha='center', va='bottom', color=P['ink'])
    ax.set_xlim(11.8, 0.0); ax.set_ylim(560, 800)
    ax.set_xlabel('나이(ka; 왼쪽이 오래된 때)'); ax.set_ylabel('메탄(ppb)')
    K.style_ax(ax, mode)
    ax.legend(loc='upper left', frameon=False, fontsize=8, bbox_to_anchor=(0.30, 1.0), handletextpad=0.3, borderpad=0.1)
    kk = (tc >= 7700) & (tc <= 8800)
    ax2.plot(tc[kk] / 1000, yc[kk], marker='o', ms=2.4, ls='-', lw=0.5, color=Q['edc'])
    ax2.set_xlim(8.45, 8.0); ax2.set_ylim(560, 720)
    ax2.set_xticks([8.4, 8.2, 8.0]); ax2.set_title('8.2 ka 확대', fontsize=8, pad=3)
    ax2.set_yticklabels([]) if False else None
    ax2.set_xlabel('나이(ka)')
    K.style_ax(ax2, mode)
    WARN.extend(K.save(f, 'ch03-ch4', mode))


# ---------------------------------------------------------------- 그림 3: 후기 상승 약 20 ppm 에 붙는 숫자
ITEMS = [  # 이름, 하한, 상한, 종류('paper' 논문 값, 'book' 이 책 산술)
    ('관측된 후기 상승(Elsig 등 2009, Joos 등 2004)', 20, 20, 'paper'),
    ('관측된 후기 상승(Dome C, Taylor Dome 칸 평균 차)', 18.7, 19.0, 'book'),
    ('Joos 등: 탄산염 보상이 설명하는 몫', 4, 10, 'paper'),
    ('Joos 등: 초기 토지 이용이 더한 몫', 4, 6, 'paper'),
    ('Ruddiman 등(2016): 이산화탄소 용해도 되먹임', 6, 6, 'paper'),
    ('Ruddiman 등(2016): 남극해 되먹임', 5, 15, 'paper'),
    ('Ruddiman(2003): 이상 전체(이산화탄소)', 40, 40, 'paper'),
    ('KK10 산업화 이전 방출 343 Gt 의 환산', 24.2, 24.2, 'book'),
    ('일정한 1인당 개간 약 70 Gt 의 환산', 4.9, 4.9, 'book'),
]

def fig_budget(mode):
    P = K.C[mode]; Q = pal(mode)
    f = K.fig(130, 88)
    ax = f.add_axes([0.52, 0.13, 0.46, 0.83])
    n = len(ITEMS)
    for i, (nm, lo, hi, kind) in enumerate(ITEMS):
        y = n - 1 - i
        col = Q['edc'] if kind == 'paper' else Q['tay']
        if hi - lo < 1e-9:
            ax.plot([lo], [y], marker='o', ms=6, color=col, mec=P['ink'], mew=0.5, zorder=3)
            ax.text(lo + 1.2, y, '%g' % lo, fontsize=8, va='center', color=P['ink'])
        else:
            ax.barh(y, hi - lo, left=lo, height=0.5, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=3, hatch=('////' if (mode == 'bw' and kind == 'book') else None))
            ax.text(hi + 1.2, y, '%g~%g' % (lo, hi), fontsize=8, va='center', color=P['ink'])
        ax.text(-1.0, y, nm, fontsize=8, va='center', ha='right', color=P['ink'])
    ax.axvline(20, color=P['soft'], lw=0.7, ls='--', zorder=1)
    ax.set_xlim(0, 50); ax.set_ylim(-0.7, n - 0.3); ax.set_yticks([])
    ax.set_xlabel('이산화탄소(ppm)')
    K.style_ax(ax, mode, grid='x')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=Q['edc'], ec=P['ink'], label='논문이 적은 값'), Patch(fc=Q['tay'], ec=P['ink'], label='이 책의 산술(계산 3-3, 3-5)')], loc='lower right', frameon=False, fontsize=8, bbox_to_anchor=(1.0, 0.0))
    WARN.extend(K.save(f, 'ch03-budget', mode))


if __name__ == '__main__':
    for m in MODES:
        fig_co2(m); fig_ch4(m); fig_budget(m)
    print('경고 합계', len(WARN))
