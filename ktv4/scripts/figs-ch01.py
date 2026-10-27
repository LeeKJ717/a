# -*- coding: utf-8 -*-
"""1장 「기록을 읽는 법」 그림 생성: fig/fig-ch01-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book4): python3 scripts/figs-ch01.py [이름...]
그림의 숫자는 ms/code/ch01/ 의 계산 로그에서 옮겼거나 논문 숫자를 다시 그린 것이다. 곡선 그림은 IntCal20 파일(data/intcal20.14c)을 읽는다.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch01'))
import figkit12 as F
from figkit12 import plt, np, C, HATCH
import c14cal as CC
FS = 8.0
plt.rcParams['mathtext.default'] = 'regular'


# ------------------------------------------------ 그림 1-1 같은 사건, 여섯 종류의 기록이 적은 나이
def fig_yd(mode):
    Q = C[mode]
    f = F.fig(130, 74); ax = f.add_axes([0.46, 0.15, 0.52, 0.81]); F.style_ax(ax, mode, grid='x')
    rows = [('얼음 GICC05, 중수소 과잉', 11703, 99), ('얼음 GISP2 경계', 11690, None), ('호수 바브 호이츠마르', 11650, None), ('호수 바브 메이어펠더', 11640, None),
            ('나이테 호엔하임', 11640, None), ('호수 14C 스플랜 연못', 11733, 298), ('호수 연층+14C 스이게쓰', 11602, 88), ('해양 카리아코', 11628, 32), ('호수 화산재 마라토토', 11770, 220)]
    ax.axvspan(11703 - 99, 11703 + 99, color=Q['grid'], zorder=1)
    ax.axvline(11703, color=Q['ink'], lw=0.8, ls=(0, (3, 2)), zorder=2)
    for i, (lab, v, e) in enumerate(rows):
        if e: ax.errorbar([v], [i], xerr=[e], fmt='none', ecolor=Q['soft'], capsize=2.5, lw=1.0, zorder=3)
        ax.scatter([v], [i], s=26, marker='o' if i else 's', color=Q['acc'] if i == 0 else Q['ink'], zorder=5)
        ax.text(v, i - 0.38, '%d' % v, fontsize=FS, ha='center', va='bottom', color=Q['ink'])
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=FS); ax.invert_yaxis()
    ax.set_ylim(len(rows) - 0.4, -0.95)
    ax.set_xlim(11380, 12080)
    ax.set_xlabel('같은 사건의 나이 (b2k, BP 값에는 50을 더함)', fontsize=FS)
    return f


# ------------------------------------------------ 그림 1-2 보정 곡선의 평평한 곳과 오차의 퍼짐
def fig_cal(mode):
    Q = C[mode]
    f = F.fig(130, 66)
    ax = f.add_axes([0.125, 0.17, 0.44, 0.78]); F.style_ax(ax, mode, grid='y')
    m = (CC.CAL >= 10800) & (CC.CAL <= 12600)
    ax.plot(CC.CAL[m], CC.C14[m], color=Q['ink'], lw=1.0, zorder=3)
    ax.axhspan(10092 - 50, 10092 + 50, color=Q['grid'], zorder=1)
    ax.axvspan(11410, 11812, color=Q['grid'], alpha=0.0, zorder=1)
    ax.plot([11410, 11812], [10092 - 50, 10092 - 50], color=Q['acc'], lw=0)
    ax.annotate('', xy=(11410, 10150), xytext=(11812, 10150), arrowprops=dict(arrowstyle='<->', color=Q['acc'], lw=1.0), zorder=6)
    ax.text(11611, 10190, '402년', fontsize=FS, ha='center', va='bottom', color=Q['acc'])
    ax.text(10880, 10930, '회색 띠: 14C 10,092 ± 50', fontsize=FS, ha='left', va='top', color=Q['ink'])
    ax.set_xlim(10800, 12600); ax.set_ylim(9400, 11000)
    ax.set_xlabel('달력 연대 (cal BP)', fontsize=FS); ax.set_ylabel('14C 연대 (BP)', fontsize=FS)
    ax2 = f.add_axes([0.70, 0.17, 0.28, 0.78]); F.style_ax(ax2, mode, grid='y')
    a = np.arange(1000, 12001, 1000)
    sp = []
    for v in a:
        s = CC.summary(float(v), 50.0)
        sp.append(max(h[0] for h in s['hpd']) - min(h[1] for h in s['hpd']))
    ax2.bar(a / 1000, sp, width=0.7, color=Q['a'], edgecolor=Q['ink'], lw=0.5, zorder=3, hatch='////' if mode == 'bw' else None)
    ax2.axhline(196, color=Q['acc'], lw=1.0, ls=(0, (3, 2)), zorder=4)
    ax2.text(12.5, 635, '점선: 14C 오차만의\n폭 196년', fontsize=FS, ha='right', va='top', color=Q['acc'])
    ax2.set_xlim(0.4, 12.6); ax2.set_ylim(0, 640)
    ax2.set_xlabel('14C 연대 (천 년 BP)', fontsize=FS); ax2.set_ylabel('보정 뒤 95.4% 전체 범위 (년)', fontsize=FS)
    return f


# ------------------------------------------------ 그림 1-3 퇴적물 속 뒤섞임이 사건을 깎는 정도
def fig_bio(mode):
    Q = C[mode]
    f = F.fig(130, 62); ax = f.add_axes([0.095, 0.17, 0.865, 0.78]); F.style_ax(ax, mode, grid='y')
    W = np.arange(1, 3500)
    ax.plot(W, np.minimum(1, 160.0 / W), color=Q['acc'], lw=1.4, zorder=4)
    for P, ls, col in ((1000, (0, (4, 2)), Q['a']), (2000, (0, (1, 2)), Q['b'])):
        ax.plot(W, np.abs(np.sinc(W / P)), color=col, lw=1.0, ls=ls, zorder=3)
    for w, lab in ((2206, '7.5 cm\n3.4 cm/kyr'), (2941, '10 cm\n3.4 cm/kyr')):
        ax.axvline(w, color=Q['soft'], lw=0.7, zorder=2)
    ax.text(2160, 0.93, '7.5 cm', fontsize=FS, ha='right', va='top', color=Q['ink'])
    ax.text(2990, 0.93, '10 cm', fontsize=FS, ha='left', va='top', color=Q['ink'])
    ax.text(2580, 0.80, '3.4 cm/kyr', fontsize=FS, ha='center', va='top', color=Q['ink'])
    ax.text(420, 0.42, '160년 사건', fontsize=FS, ha='left', va='bottom', color=Q['acc'])
    ax.text(640, 0.64, '1000년 주기', fontsize=FS, ha='left', va='bottom', color=Q['a'])
    ax.text(1330, 0.79, '2000년 주기', fontsize=FS, ha='left', va='bottom', color=Q['b'])
    ax.set_xlim(0, 3500); ax.set_ylim(0, 1.04)
    ax.set_xlabel('이동평균의 폭 W (년)', fontsize=FS); ax.set_ylabel('남는 진폭의 비율', fontsize=FS)
    return f


# ------------------------------------------------ 그림 1-4 조각 길이의 저주
def fig_seg(mode):
    Q = C[mode]
    f = F.fig(130, 62); ax = f.add_axes([0.095, 0.17, 0.885, 0.78]); F.style_ax(ax, mode, grid='y')
    Ps = np.array([100, 200, 400, 800, 1600, 3200])
    lin = {200: [0.92, 0.71, 0.11, 0.00, 0.00, 0.00], 500: [0.99, 0.98, 0.92, 0.22, 0.02, 0.00], 1000: [1.00, 0.99, 0.98, 0.91, 0.21, 0.02]}
    cols = {200: Q['a'], 500: Q['b'], 1000: Q['c']}
    mk = {200: 'o', 500: 's', 1000: '^'}
    for L in (200, 500, 1000):
        ax.plot(Ps, lin[L], color=cols[L], lw=1.1, marker=mk[L], ms=4, zorder=3)
    ax.set_xscale('log'); ax.set_xticks(Ps); ax.set_xticklabels([str(p) for p in Ps], fontsize=FS); ax.minorticks_off()
    ax.text(110, 0.22, '조각 200년', fontsize=FS, ha='left', va='center', color=Q['a'])
    ax.text(280, 0.33, '조각 500년', fontsize=FS, ha='left', va='center', color=Q['b'])
    ax.text(560, 0.52, '조각 1000년', fontsize=FS, ha='left', va='center', color=Q['c'])
    ax.axhline(0.5, color=Q['grid'], lw=1.0, zorder=1)
    ax.set_xlim(85, 3900); ax.set_ylim(-0.04, 1.06)
    ax.set_xlabel('사인파의 주기 (년)', fontsize=FS); ax.set_ylabel('조각 연대기에 남는 진폭의 비율', fontsize=FS)
    return f


# ------------------------------------------------ 그림 1-5 연대 오차가 상관을 깎는 정도
def fig_jit(mode):
    Q = C[mode]
    f = F.fig(130, 62); ax = f.add_axes([0.095, 0.17, 0.885, 0.78]); F.style_ax(ax, mode, grid='y')
    S = np.array([10, 24, 47, 99, 200])
    B = {20: [0.79, 0.50, 0.39, 0.17, 0.11], 50: [0.88, 0.75, 0.63, 0.40, 0.23], 150: [0.96, 0.90, 0.83, 0.71, 0.48], 500: [0.99, 0.96, 0.93, 0.88, 0.76]}
    cols = {20: Q['a'], 50: Q['b'], 150: Q['c'], 500: Q['d']}
    mk = {20: 'o', 50: 's', 150: '^', 500: 'D'}
    for tau in (20, 50, 150, 500):
        ax.plot(S, B[tau], color=cols[tau], lw=1.1, marker=mk[tau], ms=4, zorder=3)
        ax.text(S[-1] + 6, B[tau][-1], '기억 %d년' % tau, fontsize=FS, ha='left', va='center', color=cols[tau])
    for s, lab in ((24, '24'), (47, '47'), (99, '99')):
        ax.axvline(s, color=Q['grid'], lw=1.0, zorder=1)
    ax.text(24, 1.045, '24', fontsize=FS, ha='center', va='bottom', color=Q['ink'])
    ax.text(47, 1.045, '47', fontsize=FS, ha='center', va='bottom', color=Q['ink'])
    ax.text(99, 1.045, '99', fontsize=FS, ha='center', va='bottom', color=Q['ink'])
    ax.set_xlim(0, 262); ax.set_ylim(0, 1.08)
    ax.set_xlabel('연대 점마다의 표준편차 s (년)', fontsize=FS); ax.set_ylabel('두 기록의 상관', fontsize=FS)
    return f


FIGS = [('ch01-yd', fig_yd), ('ch01-cal', fig_cal), ('ch01-bio', fig_bio), ('ch01-seg', fig_seg), ('ch01-jit', fig_jit)]
if __name__ == '__main__':
    only = sys.argv[1:]
    for name, fn in FIGS:
        if only and name not in only: continue
        for mode in ('color', 'bw'):
            F.save(fn(mode), name, mode)
