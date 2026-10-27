# -*- coding: utf-8 -*-
"""13장 「최근 이천 년」 그림. 자료 그림은 논문이 적은 숫자와 이 책의 계산(ms/code/ch13/calc13.log, calc13-out.json)을 다시 그린 것이며 측정 자료 그 자체가 아니다.
가상 계열에서 나온 값은 모두 시연값이다.
실행(작업 폴더 /home/claude/book4): python3 scripts/figs-ch13.py → fig/fig-ch13-*-v1-{color,bw}.svg
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as fk
from matplotlib.patches import Patch

OUT = json.load(open(os.path.join(ROOT, 'ms', 'code', 'ch13', 'calc13-out.json'), encoding='utf-8'))


def fig_windows(mode):
    P = fk.C[mode]
    cold, warm = OUT['cold'], OUT['warm']
    short = {
        'Neukom 등(2014) 두 반구 모두 추움': 'Neukom 2014 두 반구 모두 추움',
        'Neukom 등(2014) 동시 한랭 이상': 'Neukom 2014 동시 한랭 이상',
        'PAGES 2k(2013) 대체로 추움': 'PAGES 2k 2013 대체로 추움',
        'Stenni 등(2017) 남극 가장 추움': 'Stenni 2017 남극 가장 추움',
        'Solomina 등(2016) 소빙기(제3권 12장)': 'Solomina 2016 소빙기',
        'Esper 등(2002) 소빙기': 'Esper 2002 소빙기',
        'Park 등(2017) 소빙기(제1권 5장)': 'Park 2017 소빙기',
        'Miller 등(2012) 급한 시작~강화': 'Miller 2012 시작~강화',
        'Esper 등(2002) 중세 온난기': 'Esper 2002 중세 온난기',
        'Solomina 등(2016) 중세 온난기': 'Solomina 2016 중세 온난기',
        'Park 등(2017) 중세 이상기': 'Park 2017 중세 이상기',
        'Stenni 등(2017) 남극 가장 따뜻함': 'Stenni 2017 남극 가장 따뜻함',
    }
    rows = [(short[n], a, b, 'cold') for n, a, b in cold] + [(short[n], a, b, 'warm') for n, a, b in warm]
    rows.sort(key=lambda r: (r[3] != 'warm', r[1]))
    f = fk.fig(130, 92)
    ax = f.add_axes([0.35, 0.20, 0.62, 0.77])
    for i, (nm, a, b, k) in enumerate(rows):
        y = len(rows) - 1 - i
        if k == 'cold':
            ax.barh(y, b - a, left=a, height=0.62, color=P['wet'], edgecolor=P['ink'], linewidth=0.5, hatch='////' if mode == 'bw' else '', zorder=3)
        else:
            ax.barh(y, b - a, left=a, height=0.62, color=P['dry'], edgecolor=P['ink'], linewidth=0.5, zorder=3)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
    ax.set_xlim(250, 1950)
    ax.set_xlabel('서기 연도', fontsize=8)
    fk.style_ax(ax, mode, grid='x')
    ax.axvspan(1594, 1677, color=P['grid'], alpha=0.6, zorder=1)
    handles = [Patch(facecolor=P['wet'], edgecolor=P['ink'], hatch='////' if mode == 'bw' else '', label='소빙기류 창'),
               Patch(facecolor=P['dry'], edgecolor=P['ink'], label='중세 온난기류 창'),
               Patch(facecolor=P['grid'], edgecolor=P['soft'], label='1594~1677 두 반구 모두 추움')]
    f.legend(handles=handles, loc='lower left', fontsize=8, frameon=False, bbox_to_anchor=(0.01, 0.0), ncol=3, handlelength=1.2, columnspacing=0.8)
    fk.save(f, 'ch13-windows', mode)


def fig_coherence(mode):
    P = fk.C[mode]
    C = OUT['coh']
    ks = sorted(C, key=float)
    x = np.array([float(k) for k in ks])
    med = np.array([C[k][0] for k in ks]) * 100
    lo = np.array([C[k][1] for k in ks]) * 100
    hi = np.array([C[k][2] for k in ks]) * 100
    f = fk.fig(130, 70)
    ax = f.add_axes([0.11, 0.17, 0.86, 0.78])
    ax.fill_between(x, lo, hi, color=P['grid'], zorder=2)
    ax.plot(x, med, '-o', color=P['a'], lw=1.2, ms=3.5, mec=P['ink'], mew=0.5, zorder=4)
    ax.axhline(24, color=P['b'], lw=0.9, ls='--', zorder=3)
    ax.text(0.01, 24 + 2.0, '논문 한 구성원: 소빙기 최저 창 공유 24%', fontsize=8, color=P['ink'], ha='left', va='bottom')
    ax.set_xlim(-0.02, 0.85); ax.set_ylim(0, 100)
    ax.set_xlabel('모든 격자가 함께 가진 신호의 분산 비중 (가상 격자, 시연값)', fontsize=8)
    ax.set_ylabel('같은 약 102년에 든 격자 (%)', fontsize=8)
    ax.text(0.02, 92, '선: 중앙값, 띠: 5~95%', fontsize=8, color=P['soft'], va='center')
    fk.style_ax(ax, mode, grid='y')
    fk.save(f, 'ch13-coherence', mode)


def fig_fp(mode):
    P = fk.C[mode]
    rows = [r for r in OUT['fp'] if r[0] == 85 and r[0] and r[1] in (0.0, 0.3, 0.5, 0.7, 0.9)]
    # 같은 (n, rho)가 앞부분 (a)에 있다. (b), (c)는 같은 n이어도 구성이 달라 앞 5개만 쓴다
    rows = OUT['fp'][:5]
    rho = [r[1] for r in rows]
    raw = [r[2] * 100 for r in rows]
    cor = [r[3] * 100 for r in rows]
    f = fk.fig(130, 66)
    ax = f.add_axes([0.11, 0.18, 0.86, 0.77])
    xs = np.arange(len(rho))
    w = 0.36
    ax.bar(xs - w / 2, raw, w, color=P['b'], edgecolor=P['ink'], linewidth=0.5, zorder=3, label='보정 없는 검정', hatch='////' if mode == 'bw' else '')
    ax.bar(xs + w / 2, cor, w, color=P['a'], edgecolor=P['ink'], linewidth=0.5, zorder=3, label='유효 표본수 보정')
    for x, v in zip(xs - w / 2, raw):
        ax.text(x, v + 1.2, '%.0f' % v, ha='center', fontsize=8, color=P['ink'])
    ax.axhline(5, color=P['ink'], lw=0.8, ls='--', zorder=4)
    ax.text(len(rho) - 0.5, 7.5, '5% 기준', fontsize=8, color=P['ink'], ha='right')
    ax.set_xticks(xs); ax.set_xticklabels(['%.1f' % r for r in rho], fontsize=8)
    ax.set_xlabel('연 단위 자기상관 rho (두 계열 같게, n=85, 가상 계열, 시연값)', fontsize=8)
    ax.set_ylabel('우연히 유의해 보인 비율 (%)', fontsize=8)
    ax.set_ylim(0, 58)
    ax.legend(loc='upper left', fontsize=8, frameon=False)
    fk.style_ax(ax, mode, grid='y')
    fk.save(f, 'ch13-fp', mode)


def fig_esper(mode):
    P = fk.C[mode]
    rows = OUT['esper']
    Ls = [150, 300, 500]
    f = fk.fig(130, 66)
    ax = f.add_axes([0.11, 0.20, 0.86, 0.75])
    w = 0.36
    xs = np.arange(len(Ls))
    ind = [[r[3] for r in rows if r[0] == L and r[1].startswith('개별')][0] for L in Ls]
    rcs = [[r[3] for r in rows if r[0] == L and r[1].startswith('지역')][0] for L in Ls]
    ax.bar(xs - w / 2, ind, w, color=P['b'], edgecolor=P['ink'], linewidth=0.5, zorder=3, label='나무마다 3차 다항식 제거', hatch='////' if mode == 'bw' else '')
    ax.bar(xs + w / 2, rcs, w, color=P['a'], edgecolor=P['ink'], linewidth=0.5, zorder=3, label='지역 곡선(RCS)')
    for x, v in zip(xs - w / 2, ind):
        ax.text(x, v + 0.025, '%.2f' % v, ha='center', fontsize=8, color=P['ink'])
    for x, v in zip(xs + w / 2, rcs):
        ax.text(x, v + 0.06, '%.2f' % v, ha='center', fontsize=8, color=P['ink'])
    ax.axhline(1, color=P['ink'], lw=0.8, ls='--', zorder=4)
    ax.set_xticks(xs); ax.set_xticklabels(['%d년' % L for L in Ls], fontsize=8)
    ax.set_xlabel('가상 나무 한 그루의 나이테 길이 (시연값)', fontsize=8)
    ax.set_ylabel('복원한 느린 변동 / 넣은 느린 변동', fontsize=8)
    ax.set_ylim(0, 1.6)
    ax.legend(loc='upper left', fontsize=8, frameon=False, bbox_to_anchor=(0.0, 1.0), ncol=1)
    fk.style_ax(ax, mode, grid='y')
    fk.save(f, 'ch13-esper', mode)


def fig_intcal(mode):
    P = fk.C[mode]
    cv = np.array(OUT['miller']['curve'])
    f = fk.fig(130, 66)
    ax = f.add_axes([0.12, 0.18, 0.85, 0.77])
    ax.fill_between(cv[:, 0], cv[:, 1] - cv[:, 2], cv[:, 1] + cv[:, 2], color=P['grid'], zorder=2)
    ax.plot(cv[:, 0], cv[:, 1], color=P['a'], lw=1.2, zorder=4)
    for a, b, lab in ((1275, 1300, '1275~1300'), (1430, 1455, '1430~1455')):
        ax.axvspan(a, b, color=P['b'], alpha=0.35, zorder=1)
        ax.text((a + b) / 2, 880, lab, fontsize=8, ha='center', color=P['ink'])
    ax.set_xlim(1200, 1500); ax.set_ylim(330, 920)
    ax.set_xlabel('서기 연도 (달력)', fontsize=8)
    ax.set_ylabel('IntCal20의 방사성탄소 연대 (BP)', fontsize=8)
    fk.style_ax(ax, mode, grid='y')
    fk.save(f, 'ch13-intcal', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        fig_windows(mode); fig_coherence(mode); fig_fp(mode); fig_esper(mode); fig_intcal(mode)
