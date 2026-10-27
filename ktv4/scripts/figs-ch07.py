# -*- coding: utf-8 -*-
"""7장 그림(색·흑백 SVG 두 벌). 자료 그림은 논문이 적은 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다.
  fig-ch07-dur   : 8.2 ka 사건 지속 기간 값 모음(계산 7-1)
  fig-ch07-time  : 방출, 해수면, 냉각 연대 값 모음(계산 7-3)
  fig-ch07-vol   : 물 부피의 해수면 환산과 흐름률(계산 7-2)
  fig-ch07-amp   : 그린란드 낙폭 환산과 강수 방향 구간(계산 7-4)
  fig-ch07-alarm : 사건 탐지 규칙의 거짓 경보율(계산 7-5, 시연값)
사용(작업 폴더 /home/claude/book4): PREVDIR=<미리보기 폴더> python3 scripts/figs-ch07.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as F
plt = F.plt
C = F.C
FS = 8.0
MODES = ('color', 'bw')


def sty(ax, mode, grid='y'):
    F.style_ax(ax, mode, grid)


def rowplot(ax, P, rows, xlabel):
    """rows: (이름, 하한, 상한, 점 또는 None, 색 키)"""
    n = len(rows)
    for i, (nm, lo, hi, pt, key) in enumerate(rows):
        y = n-1-i
        if hi > lo:
            ax.plot([lo, hi], [y, y], color=P[key], lw=5, solid_capstyle='butt', zorder=3)
        if pt is not None:
            ax.scatter([pt], [y], s=30, color=P['ink'], zorder=5)
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=FS, color=P['ink'])
    ax.set_ylim(-0.7, n-0.3)
    ax.set_xlabel(xlabel, fontsize=FS, color=P['soft'])


def fig_dur(mode):
    P = C[mode]
    f = F.fig(130, 84)
    ax = f.add_axes([0.40, 0.15, 0.57, 0.80])
    rows = [('Kleiven 등(2008) 북대서양', 100, 110, None, 'c'),
            ('Morrill 등(2013) 표 1', 120, 120, 120, 'b'),
            ('Kobashi 등(2007) 전체', 150, 150, 150, 'a'),
            ('Thomas 등(2007) 전체', 160.5, 160.5, 160.5, 'a'),
            ('Morrill 등 z 검정 그린란드', 160, 180, None, 'b'),
            ('Morrill 등 아시아 몬순', 230, 280, None, 'd'),
            ('Ellison 등(2006) 심층', 400, 400, 400, 'e'),
            ('Rohling과 Pälike(2005) 전지구', 400, 600, None, 'e')]
    rowplot(ax, P, rows, '지속 기간(년)')
    ax.set_xlim(0, 650)
    ax.axvline(150.1, color=P['ink'], lw=0.6, ls=':', zorder=1)
    ax.text(155, 7.45, '그린란드 값 평균 150', fontsize=FS, color=P['ink'], ha='left', va='center')
    sty(ax, mode, grid='x')
    F.save(f, 'ch07-dur', mode)


def fig_time(mode):
    P = C[mode]
    f = F.fig(130, 100)
    ax = f.add_axes([0.40, 0.13, 0.57, 0.84])
    rows = [('Ellison 등 첫 냉각', 8490, 8490, 8490, 'a'),
            ('Barber 등 호수 배수', 8470-300, 8470+300, 8470, 'a'),
            ('Hijma와 Cohen 해수면 도약', 8450-44, 8450+44, 8450, 'a'),
            ('Obrist-Farner 등 이사발호', 8370, 8370, 8370, 'a'),
            ('Kleiven 등 심층수 이상', 8270, 8380, None, 'b'),
            ('Ellison 등 둘째 냉각', 8290, 8290, 8290, 'b'),
            ('Dykoski 등 둥거 사건 1', 8260-64, 8260+64, 8260, 'd'),
            ('Thomas 등 냉각 시작', 8247, 8247, 8247, 'b'),
            ('Alley 등 GRIP 최소', 8210-30, 8210+30, 8210, 'b'),
            ('Kobashi 등 시작', 8175, 8175, 8175, 'b'),
            ('Dykoski 등 둥거 사건 2', 8080-74, 8080+74, 8080, 'd')]
    rowplot(ax, P, rows, '연대(BP로 적힌 값, 왼쪽이 오래된 때)')
    ax.set_xlim(8850, 7850)
    sty(ax, mode, grid='x')
    F.save(f, 'ch07-time', mode)


def fig_vol(mode):
    P = C[mode]
    f = F.fig(130, 78)
    ax = f.add_axes([0.12, 0.18, 0.85, 0.77])
    A = 10.7e14/3.0
    YR = 365.25*24*3600
    T = np.logspace(np.log10(0.3), np.log10(300), 100)
    for nm, V, key, ls in (('Hijma와 Cohen 부피 10.7×10¹⁴ m³', 10.7e14, 'a', '-'),
                           ('Leverington 등 163,000 km³', 163000e9, 'b', '--'),
                           ('Clarke 등 하한 40,000 km³', 40000e9, 'd', ':')):
        ax.plot(T, V/(T*YR)/1e6, color=P[key], lw=1.6, ls=ls, label=nm)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.axhline(0.015, color=P['ink'], lw=0.8, ls=(0, (4, 3)))
    ax.text(0.33, 0.0165, 'Alley 등: 모형 대류 중단 문턱 0.015 Sv', fontsize=FS, color=P['ink'], va='bottom')
    ax.scatter([0.5], [5.0], s=40, marker='D', color=P['acc'], edgecolor=P['ink'], zorder=6)
    ax.text(0.62, 5.0, 'Clarke 등 약 5 Sv, 0.5 년', fontsize=FS, color=P['ink'], va='center')
    ax.set_xlabel('같은 부피를 쏟는 데 걸린 시간(년)', fontsize=FS, color=P['soft'])
    ax.set_ylabel('흐름률(Sv)', fontsize=FS, color=P['soft'])
    ax.set_xlim(0.3, 300); ax.set_ylim(0.01, 200)
    leg = ax.legend(loc='upper right', fontsize=FS, frameon=False)
    sty(ax, mode, grid='y')
    F.save(f, 'ch07-vol', mode)


def fig_amp(mode):
    P = C[mode]
    f = F.fig(130, 72)
    ax = f.add_axes([0.40, 0.17, 0.57, 0.78])
    rows = [('Alley 등(1997) 6 ± 2', 4, 8, 6, 'a'),
            ('Barber 등(1999) 그린란드', 4, 8, None, 'b'),
            ('Kobashi 등(2007) 3.3 ± 1', 2.3, 4.3, 3.3, 'c'),
            ('Morrill 등(2013) δ18O 환산', 2.4, 3.6, None, 'd')]
    rowplot(ax, P, rows, '그린란드 낙폭(°C)')
    ax.set_xlim(0, 9)
    sty(ax, mode, grid='x')
    F.save(f, 'ch07-amp', mode)


def fig_alarm(mode):
    P = C[mode]
    f = F.fig(130, 78)
    ax = f.add_axes([0.11, 0.17, 0.86, 0.78])
    lab = ['50 년', '20 년', '10 년', '5 년']
    vals = {0.0: [3.5, 4.6, 7.5, 0.3], 0.3: [9.8, 14.7, 23.6, 5.1], 0.6: [20.1, 30.7, 44.9, 26.7]}
    w = 0.26
    for j, (phi, key) in enumerate(((0.0, 'c'), (0.3, 'b'), (0.6, 'a'))):
        xs = np.arange(4) + (j-1)*w
        ax.bar(xs, vals[phi], width=w*0.92, color=P[key], edgecolor=P['ink'], linewidth=0.5, label='자기상관 φ = %.1f' % phi)
        for x, v in zip(xs, vals[phi]):
            ax.text(x, v+0.8, '%.1f' % v, ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ax.set_xticks(range(4)); ax.set_xticklabels(lab, fontsize=FS, color=P['ink'])
    ax.set_xlabel('시계열 해상도(연속 2점, 5 년은 3점)', fontsize=FS, color=P['soft'])
    ax.set_ylabel('잡음만으로 사건이 잡힌 비율(%)', fontsize=FS, color=P['soft'])
    ax.set_ylim(0, 56)
    ax.legend(loc='upper left', fontsize=FS, frameon=False)
    sty(ax, mode, grid='y')
    F.save(f, 'ch07-alarm', mode)


if __name__ == '__main__':
    for m in MODES:
        fig_dur(m); fig_time(m); fig_vol(m); fig_amp(m); fig_alarm(m)
