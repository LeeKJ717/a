# -*- coding: utf-8 -*-
"""9장 「화산과 기후」 그림 5장(색·흑백 SVG 두 벌): fig/fig-ch09-*-v1-{color,bw}.svg
모든 값은 이 장이 읽은 논문의 숫자이거나 ms/code/ch09/out 의 계산 결과(json)이다. 논문의 그림을 옮긴 것이 아니라 숫자를 다시 그린 것이다.
  rates : 세기당 성층권 황 주입량(논문값과 이 책 계산값)  (계산 9-1)
  top10 : eVolv2k 가장 큰 열 개와 오차(오차가 논문에 없는 것은 20% 시연값)  (계산 9-2)
  dating: 마자마와 테라의 연대 구간  (계산 9-3)
  unc   : 서술된 1시그마 불확도의 사다리  (Sigl 등 2022, Toohey & Sigl 2017)
  gap   : 푸아송 기준선과 분화 간격  (계산 9-1)
쓰는 법(작업 폴더 /home/claude/book4): PREVDIR=/경로 python3 scripts/figs-ch09.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p9')
import numpy as np
import figkit12 as F
import matplotlib.pyplot as plt
CODE = os.path.join(ROOT, 'ms', 'code', 'ch09', 'out')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))


def fig_rates(mode):
    P = F.C[mode]
    f = F.fig(130, 88); ax = f.add_axes([0.47, 0.25, 0.50, 0.72])
    c1 = J('calc9-1.json')
    rows = [('홀로세 평균', 63.0, 'p'), ('기원전 10~5천년기 평균', 76.0, 'p'), ('초기 활동기(기원전 9500~7000)', 90.0, 'p'), ('중기 활동기(63 × 1.22)', 63 * 1.22, 'c'),
            ('기원전 4천년기 이후', 45.0, 'p'), ('조용한 시기(기원전 4000~1000)\n63 × 0.64', 63 * 0.64, 'c'), ('최근 2500년\n2250 ÷ 1.86 ÷ 25', c1['late2500_per_century'], 'c')]
    ys = np.arange(len(rows))[::-1]
    for y, (n, v, k) in zip(ys, rows):
        col = P['a'] if k == 'p' else P['b']
        hatch = None if k == 'p' else ('////' if mode == 'bw' else None)
        ax.barh(y, v, height=0.62, color=col if k == 'p' else (P['b'] if mode == 'color' else '#FFFFFF'), edgecolor=P['ink'], linewidth=0.6, hatch=hatch, zorder=3)
        ax.text(v + 1.5, y, '%.1f' % v, va='center', ha='left', fontsize=8, color=P['ink'])
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.set_xlim(0, 110); ax.set_xlabel('세기당 성층권 황 주입량(Tg S/세기)', fontsize=8)
    F.style_ax(ax, mode, grid='x')
    from matplotlib.patches import Patch
    h = [Patch(facecolor=P['a'], edgecolor=P['ink'], label='논문이 적은 값'), Patch(facecolor=P['b'] if mode == 'color' else '#FFFFFF', edgecolor=P['ink'], hatch='////' if mode == 'bw' else None, label='이 책이 논문 값에서 계산한 값')]
    f.legend(handles=h, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, fontsize=8)
    return F.save(f, 'ch09-rates', mode)


def fig_top10(mode):
    P = F.C[mode]; R = J('calc9-2.json')['rank']
    f = F.fig(130, 90); ax = f.add_axes([0.24, 0.24, 0.50, 0.68])
    ys = np.arange(len(R))[::-1]
    known = {'1257 사말라스', '1458', '540', '1815 탐보라'}
    for y, r in zip(ys, R):
        k = r['name'] in known
        ax.barh(y, r['vssi'], height=0.62, color=P['a'] if k else (P['mid'] if mode == 'color' else '#FFFFFF'), edgecolor=P['ink'], linewidth=0.6, zorder=3)
        ax.errorbar(r['vssi'], y, xerr=r['sd'], fmt='none', ecolor=P['ink'], elinewidth=0.9, capsize=2.5, ls='-' if k else ':', zorder=4)
        ax.text(r['vssi'] + r['sd'] + 1.5, y, '%.1f' % r['vssi'], va='center', fontsize=8, color=P['ink'])
        ax.text(1.02, y, '1위 %.0f%%' % (100 * r['p1']) if r['p1'] >= 0.005 else '1위 <1%', va='center', ha='left', fontsize=8, color=P['soft'], transform=ax.get_yaxis_transform())
    ax.set_yticks(ys); ax.set_yticklabels([r['name'] for r in R], fontsize=8)
    ax.set_xlim(0, 85); ax.set_xlabel('VSSI(Tg S) ± 1σ', fontsize=8)
    ax.text(1.03, 1.01, '1위 확률(시연)', transform=ax.transAxes, fontsize=8, color=P['soft'], ha='left', va='bottom')
    F.style_ax(ax, mode, grid='x')
    from matplotlib.patches import Patch
    h = [Patch(facecolor=P['a'], edgecolor=P['ink'], label='1σ가 논문에 있는 사건'), Patch(facecolor=P['mid'] if mode == 'color' else '#FFFFFF', edgecolor=P['ink'], label='1σ를 20%로 둔 시연값')]
    f.legend(handles=h, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=1, frameon=False, fontsize=8)
    return F.save(f, 'ch09-top10', mode)


def fig_dating(mode):
    P = F.C[mode]
    f = F.fig(130, 92)
    ax1 = f.add_axes([0.36, 0.66, 0.60, 0.28]); ax2 = f.add_axes([0.36, 0.11, 0.60, 0.42])
    # (a) 마자마
    ax1.barh(1, 300, left=7477, height=0.45, color=P['mid'], edgecolor=P['ink'], lw=0.6, zorder=3)
    ax1.barh(0, 98, left=7584, height=0.45, color=P['a'], edgecolor=P['ink'], lw=0.6, zorder=3)
    ax1.set_yticks([0, 1]); ax1.set_yticklabels(['Egan 등 방사성탄소\n95.4%: 7584~7682', 'Sigl 등 빙핵\n7627 ± 150'], fontsize=8)
    ax1.set_xlim(7400, 7850); ax1.set_ylim(-0.6, 1.6); ax1.set_xlabel('마자마 분화, cal BP (1950년 기준)', fontsize=8)
    F.style_ax(ax1, mode, grid='x')
    # (b) 테라
    items = [('IntCal13 올리브 가지\n1642~1559', 1642, 1559, 'mid'), ('ICCP17(연간 자료)\n1614~1538', 1614, 1538, 'a'), ('고고학 신왕국 시작\nc.1550~1500', 1550, 1500, 'b')]
    for i, (n, lo, hi, k) in enumerate(items):
        y = 3 - i
        ax2.barh(y, lo - hi, left=hi, height=0.45, color=P[k], edgecolor=P['ink'], lw=0.6, zorder=3)
    ax2.axvline(1628, color=P['ink'], lw=1.0, ls='--', zorder=2); ax2.axvline(1641, color=P['soft'], lw=1.0, ls=':', zorder=2)
    ax2.text(1628.5, 3.55, '1628', ha='left', va='bottom', fontsize=8, color=P['ink']); ax2.text(1641.5, 3.55, '1641', ha='right', va='bottom', fontsize=8, color=P['soft'])
    ax2.text(1624, 0.05, '세로선: 아니아착 II 빙핵\n1628(Sigl 등)\n1641(Pearson 등이 인용)', fontsize=8, color=P['ink'], ha='left', va='bottom')
    ax2.set_yticks([3, 2, 1]); ax2.set_yticklabels([i[0] for i in items], fontsize=8)
    ax2.set_xlim(1660, 1490); ax2.set_ylim(-0.1, 4.1); ax2.set_xlabel('테라 분화, 달력 연도(기원전, 왼쪽이 오래됨)', fontsize=8)
    F.style_ax(ax2, mode, grid='x')
    return F.save(f, 'ch09-dating', mode)


def fig_unc(mode):
    P = F.C[mode]
    f = F.fig(130, 82); ax = f.add_axes([0.40, 0.15, 0.56, 0.80])
    rows = [('탐보라 VSSI(1815)', 16, 'v'), ('1458 VSSI', 15, 'v'), ('사말라스 VSSI(1257)', 18, 'v'), ('540 VSSI', 24, 'v'), ('라키 VSSI(1783)', 34, 'v'),
            ('남극 빙상 플럭스', 20, 'f'), ('그린란드 빙상 플럭스', 33, 'f'), ('열대 기원을 잘못 배정하면 과대(+)', 43, 'b'), ('오래 이어진 분화', 100, 'o')]
    ys = np.arange(len(rows))[::-1]
    col = {'v': P['a'], 'f': P['b'], 'b': P['c'], 'o': P['d']}
    for y, (n, v, k) in zip(ys, rows):
        ax.barh(y, v, height=0.62, color=col[k], edgecolor=P['ink'], lw=0.6, zorder=3, hatch=('////' if (mode == 'bw' and k == 'o') else None))
        ax.text(v + 2, y, ('>%d' if k == 'o' else '%d') % v + ('%' if True else ''), va='center', fontsize=8, color=P['ink'])
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.set_xlim(0, 125); ax.set_xlabel('논문이 적은 불확도(%)', fontsize=8)
    F.style_ax(ax, mode, grid='x')
    return F.save(f, 'ch09-unc', mode)


def fig_gap(mode):
    P = F.C[mode]; J1 = J('calc9-1.json')
    lam = 850 / 11400
    f = F.fig(130, 72); ax = f.add_axes([0.13, 0.17, 0.82, 0.76])
    g = np.linspace(0, 200, 400)
    ax.plot(g, 850 * np.exp(-lam * g), color=P['a'], lw=1.6, zorder=3)
    ax.set_yscale('log'); ax.set_ylim(0.01, 1000); ax.set_xlim(0, 200)
    ax.axhline(1, color=P['soft'], lw=0.8, ls=':'); ax.text(198, 1.15, '기대 1개', ha='right', va='bottom', fontsize=8, color=P['soft'])
    ax.plot([77], [J1['gap77_expected']], 'o', ms=6, color='white', mec=P['ink'], mew=1.2, zorder=5)
    ax.annotate('논문의 최대 간격 77년\n(푸아송 기대 %.1f개)' % J1['gap77_expected'], xy=(77, J1['gap77_expected']), xytext=(100, 25), fontsize=8, color=P['ink'], arrowprops=dict(arrowstyle='-', color=P['ink'], lw=0.7))
    ax.axvline(J1['expected_max_gap'], color=P['ink'], lw=0.9, ls='--'); ax.text(J1['expected_max_gap'] - 2, 0.02, '푸아송 최대 간격의\n기대 약 %d년' % round(J1['expected_max_gap']), fontsize=8, color=P['ink'], ha='right')
    ax.set_xlabel('분화 사이 간격 g(년)', fontsize=8); ax.set_ylabel('g년 이상인 간격의 기대 개수(850개 중)', fontsize=8)
    F.style_ax(ax, mode, grid='y')
    return F.save(f, 'ch09-gap', mode)


if __name__ == '__main__':
    for m in ('color', 'bw'):
        for fn in (fig_rates, fig_top10, fig_dating, fig_unc, fig_gap):
            w = fn(m)
