# -*- coding: utf-8 -*-
"""8장 그림(색·흑백 SVG 두 벌). 자료 그림은 논문이 적은 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다.
  fig-ch08-win42   : 4.2 ka 즈음 전지구 창들의 겹침(계산 8-4)
  fig-ch08-events  : Wanner 등의 사건과 Mayewski 등의 구간(계산 8-1)
  fig-ch08-gaps    : 사건 사이 간격(계산 8-2)
  fig-ch08-dir     : 방향 집계(계산 8-3)
  fig-ch08-cluster : 5.5~5.0 ka 열대 값의 모임(계산 8-5)
사용(작업 폴더 /home/claude/book4): PREVDIR=<미리보기 폴더> python3 scripts/figs-ch08.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as F
from matplotlib.patches import Rectangle
plt = F.plt
C = F.C
FS = 8.0
MODES = ('color', 'bw')


def sty(ax, mode, grid='y'):
    F.style_ax(ax, mode, grid)


def fig_win42(mode):
    P = C[mode]
    f = F.fig(130, 90)
    ax = f.add_axes([0.40, 0.15, 0.57, 0.80])
    rows = [('Booth 등(2005) 북미 중부', 4100, 4300, 'a'),
            ('deMenocal 등(2000) 먼지 감소', 4100, 4300, 'c'),
            ('Mayewski 등(2004) 급변 구간', 3800, 4200, 'b'),
            ('Bini 등(2019) 지중해', 3800, 4300, 'd'),
            ('Railsback 등(2018) 종합', 3930, 4150, 'e'),
            ('Weiss(2016) 개관', 3900, 4200, 'b'),
            ('제3권 6장 유라시아 공통', 3970, 4025, 'a')]
    n = len(rows)
    ax.axvspan(4100, 4150, color=P['mid'], alpha=0.55, zorder=1)
    for i, (nm, lo, hi, key) in enumerate(rows):
        y = n-1-i
        ax.plot([lo, hi], [y, y], color=P[key], lw=6, solid_capstyle='butt', zorder=3)
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=FS, color=P['ink'])
    ax.set_ylim(-0.7, n-0.3); ax.set_xlim(4400, 3700)
    ax.text(4125, n-0.55, '공통 4150~4100', ha='center', va='top', fontsize=FS, color=P['ink'])
    ax.set_xlabel('연대(cal BP, 왼쪽이 오래된 때)', fontsize=FS, color=P['soft'])
    sty(ax, mode, grid='x')
    F.save(f, 'ch08-win42', mode)


def fig_events(mode):
    P = C[mode]
    f = F.fig(130, 66)
    ax = f.add_axes([0.16, 0.20, 0.81, 0.74])
    M = [(8000, 9000), (5000, 6000), (3800, 4200), (2500, 3500), (1000, 1200), (150, 600)]
    for a, b in M:
        ax.add_patch(Rectangle((a, 1.15), b-a, 0.7, facecolor=P['mid'], edgecolor=P['ink'], linewidth=0.6, zorder=2))
    W = [8200, 6300, 4700, 2700, 1550, 550]
    hit = [True, False, False, True, False, True]
    for t, h in zip(W, hit):
        ax.scatter([t], [0.5], s=46, marker='o' if h else 's', color=P['a'] if h else P['d'], edgecolor=P['ink'], linewidth=0.7, zorder=4)
        ax.text(t, 0.17, str(t), ha='center', va='top', fontsize=FS, color=P['ink'])
    ax.set_yticks([0.5, 1.5]); ax.set_yticklabels(['Wanner 등\n사건 연대', 'Mayewski 등\n급변 구간'], fontsize=FS, color=P['ink'])
    ax.set_xlim(9300, -100); ax.set_ylim(-0.25, 2.05)
    ax.set_xlabel('연대(cal BP, 왼쪽이 오래된 때). 원은 구간 안에 든 사건, 네모는 밖', fontsize=FS, color=P['soft'])
    sty(ax, mode, grid='x')
    F.save(f, 'ch08-events', mode)


def fig_gaps(mode):
    P = C[mode]
    f = F.fig(130, 72)
    ax = f.add_axes([0.14, 0.17, 0.83, 0.78])
    g1 = [1900, 1600, 2000, 1150, 1000]
    g2 = [3000, 1500, 1000, 1900, 725]
    x = np.arange(5)
    w = 0.38
    ax.bar(x-w/2, g1, width=w*0.92, color=P['a'], edgecolor=P['ink'], linewidth=0.5, label='Wanner 등 사건 사이(평균 1530)')
    ax.bar(x+w/2, g2, width=w*0.92, color=P['b'], edgecolor=P['ink'], linewidth=0.5, label='Mayewski 등 구간 중심 사이(평균 1625)')
    for xx, v in zip(x-w/2, g1): ax.text(xx, v+40, str(v), ha='center', va='bottom', fontsize=FS, color=P['ink'])
    for xx, v in zip(x+w/2, g2): ax.text(xx, v+40, str(v), ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ax.axhline(1340, color=P['ink'], lw=0.8, ls=(0, (4, 3)))
    ax.text(4.55, 1340+40, 'Bond 등 1340', ha='right', va='bottom', fontsize=FS, color=P['ink'])
    ax.set_xticks(x); ax.set_xticklabels(['첫째', '둘째', '셋째', '넷째', '다섯째'], fontsize=FS, color=P['ink'])
    ax.set_xlabel('이웃한 두 사건(오래된 쪽부터) 사이의 간격 순서', fontsize=FS, color=P['soft'])
    ax.set_ylabel('간격(년)', fontsize=FS, color=P['soft'])
    ax.set_ylim(0, 3900)
    ax.legend(loc='upper right', fontsize=FS, frameon=False)
    sty(ax, mode, grid='y')
    F.save(f, 'ch08-gaps', mode)


def fig_dir(mode):
    P = C[mode]
    f = F.fig(130, 66)
    ax = f.add_axes([0.30, 0.20, 0.67, 0.72])
    rows = [('유라시아 19곳\n(제3권 6장)', [12, 3, 3, 1]),
            ('이 장이 새로\n읽은 5곳', [3, 1, 0, 1])]
    cols = [('건조', 'a'), ('습윤', 'b'), ('변화 없음', 'c'), ('따뜻함 또는 혼합', 'd')]
    for i, (nm, vals) in enumerate(rows):
        y = len(rows)-1-i
        left = 0
        for (cn, key), v in zip(cols, vals):
            if v == 0: continue
            ax.barh(y, v, left=left, height=0.55, color=P[key], edgecolor=P['ink'], linewidth=0.5, label=cn if i == 0 else None)
            ax.text(left+v/2, y, str(v), ha='center', va='center', fontsize=FS, color='#FFFFFF' if key in ('a', 'c') else P['ink'])
            left += v
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=FS, color=P['ink'])
    ax.set_xlim(0, 20); ax.set_ylim(-0.6, 1.9); ax.set_xticks(range(0, 21, 5))
    ax.set_xlabel('기록 수(논문 서술을 한 단어로 줄인 이 책의 분류)', fontsize=FS, color=P['soft'])
    ax.legend(loc='upper right', fontsize=FS, frameon=False, ncol=2)
    sty(ax, mode, grid='x')
    F.save(f, 'ch08-dir', mode)


def fig_cluster(mode):
    P = C[mode]
    f = F.fig(130, 90)
    ax = f.add_axes([0.40, 0.15, 0.57, 0.80])
    rows = [('Tierney 등(2017) 31°N', 6500, None, 'd'),
            ('Mayewski 등(2004) 구간 6000~5000', None, (5000, 6000), 'b'),
            ('deMenocal 등(2000) 5490 ± 190', 5490, 190, 'a'),
            ('Claussen 등(1999) 모형 5440 ± 30', 5440, 30, 'e'),
            ('Haug 등(2001) 건조 경향 시작', 5400, None, 'c'),
            ('Tierney 등 남쪽 셋 5000, 5300, 5300', None, 'tri', 'd'),
            ('Thompson 등(2002, 2006) 약 5200', 5200, None, 'b')]
    n = len(rows)
    for i, (nm, v, e, key) in enumerate(rows):
        y = n-1-i
        col = P[key]
        if e == 'tri':
            for k, vv in enumerate((5000, 5300, 5300)):
                ax.scatter([vv], [y + (0.18 if k == 2 else 0)], s=28, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=4)
        elif isinstance(e, tuple):
            ax.plot(list(e), [y, y], color=col, lw=6, solid_capstyle='butt', zorder=3)
        else:
            ax.scatter([v], [y], s=30, color=col, edgecolor=P['ink'], linewidth=0.5, zorder=4)
            if e: ax.errorbar([v], [y], xerr=[e], color=P['ink'], lw=0.9, capsize=2.5, zorder=3)
    ax.axvline(5299, color=P['ink'], lw=0.6, ls=':', zorder=1)
    ax.text(5290, n-0.45, '여덟 값 평균 5299', ha='right', va='top', fontsize=FS, color=P['ink'])
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=FS, color=P['ink'])
    ax.set_xlim(6700, 4700); ax.set_ylim(-0.7, n-0.3)
    ax.set_xlabel('연대(cal BP, 왼쪽이 오래된 때)', fontsize=FS, color=P['soft'])
    sty(ax, mode, grid='x')
    F.save(f, 'ch08-cluster', mode)


if __name__ == '__main__':
    for m in MODES:
        fig_win42(m); fig_events(m); fig_gaps(m); fig_dir(m); fig_cluster(m)
