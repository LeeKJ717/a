# -*- coding: utf-8 -*-
"""2장 그림 v1. 자료는 논문의 표와 본문 숫자를 다시 그린 것이며 계산 값은 ms/code/ch02/calc-ch02-v1.py 의 결과다.
지도는 1장 그림의 지도 함수를 같은 틀로 쓰되 점만 이 장의 호수로 바꾼다. 좌표를 읽지 못한 호수(우기, 군, 홉스골)와 토양 기록(오르혼)은 그리지 않았다.
실행: python3 figs-ch02.py   (미리보기 PNG: PREVDIR=경로 python3 figs-ch02.py)
"""
import os, sys, io, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as K
import matplotlib.pyplot as plt
from scipy import stats

ROOT = os.path.dirname(HERE)
CODE1 = os.path.join(ROOT, 'ms', 'code', 'ch01'); CODE2 = os.path.join(ROOT, 'ms', 'code', 'ch02')
sys.path.insert(0, CODE1)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m
calc = load('calc2', os.path.join(CODE2, 'calc-ch02-v1.py'))
f1 = load('figs1', os.path.join(HERE, 'figs-ch01.py'))
import rcal
MODES = ('color', 'bw')

# ---------------------------------------------------------------- 그림 1: 위치 지도
f1.SITES = [(1, '호톤 호', 88.346, 48.617), (2, '텔멘 호', 97.32, 48.82), (3, '시레트 나이만 호', 101.82, 46.53), (4, '울란 호', 103.654, 44.514),
            (5, '호륜호', 117.506, 49.127), (6, '차간 누르', 115.027, 43.436), (7, '달리호', 116.60, 43.26)]
def fig_map(mode):
    return f1.fig_map(mode)

# ---------------------------------------------------------------- 그림 2: 우기 호
def fig_ugii(mode):
    P = K.C[mode]
    f = K.fig(130, 98)
    ax = f.add_axes([0.14, 0.60, 0.82, 0.31]); ax2 = f.add_axes([0.14, 0.14, 0.82, 0.18])
    K.style_ax(ax, mode, 'x'); K.style_ax(ax2, mode, 'y')
    for i, (d, c, s, pa, ps) in enumerate(calc.UG):
        y = len(calc.UG) - 1 - i
        r13 = rcal.summary(c, s, 'intcal13'); r20 = rcal.summary(c, s, 'intcal20')
        ax.errorbar(pa, y + 0.22, xerr=ps, fmt='s', ms=4, color=P['ink'], ecolor=P['ink'], elinewidth=0.9, capsize=1.8, zorder=4)
        ax.errorbar(r13['mean'], y, xerr=r13['sd'], fmt='o', ms=4, mfc=P['a'], mec=P['ink'], ecolor=P['soft'], elinewidth=0.9, capsize=1.8, zorder=4)
        ax.errorbar(r20['mean'], y - 0.22, xerr=r20['sd'], fmt='^', ms=4, mfc='#FFFFFF', mec=P['ink'], ecolor=P['soft'], elinewidth=0.9, capsize=1.8, zorder=4)
    ax.set_yticks(range(3)); ax.set_yticklabels(['%d cm' % u[0] for u in calc.UG][::-1], fontsize=8)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel('보정 나이 (cal yr BP)', fontsize=8)
    ax.legend(handles=[plt.Line2D([], [], marker='s', color=P['ink'], ls='', ms=4), plt.Line2D([], [], marker='o', mfc=P['a'], mec=P['ink'], color=P['soft'], ls='', ms=4),
                       plt.Line2D([], [], marker='^', mfc='#FFFFFF', mec=P['ink'], color=P['soft'], ls='', ms=4)],
              labels=['논문 값', '이 책 IntCal13', '이 책 IntCal20'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=3, handletextpad=0.2, columnspacing=1.0)
    f.text(0.02, 0.975, '(가) 세 방사성탄소 연대의 보정', fontsize=8, va='top', color=P['ink'])
    rates = [2100 / 3809] + [(calc.UG[i][0] - calc.UG[i - 1][0]) * 10.0 / (calc.UG[i][3] - calc.UG[i - 1][3]) for i in (1, 2)]
    ax2.axhspan(0.43, 0.63, color=P['grid'], zorder=1)
    ax2.bar(range(3), rates, color=P['a'], edgecolor=P['ink'], linewidth=0.4, width=0.6, zorder=3)
    ax2.set_xticks(range(3)); ax2.set_xticklabels(['0→210', '210→510', '510→580'], fontsize=8)
    ax2.set_xlabel('깊이 구간 (cm)', fontsize=8); ax2.set_ylabel('퇴적률 (mm/년)', fontsize=8)
    ax2.set_ylim(0, 0.8)
    ax2.text(2.45, 0.735, '회색 띠: 논문이 쓴 범위 0.43~0.63', fontsize=8, ha='right', va='center', color=P['soft'])
    f.text(0.02, 0.385, '(나) 구간 퇴적률(논문의 보정 나이로 계산)', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 3: 호톤 호
def fig_hoton(mode):
    P = K.C[mode]
    f = K.fig(130, 104)
    ax = f.add_axes([0.14, 0.50, 0.82, 0.43]); ax2 = f.add_axes([0.20, 0.10, 0.76, 0.15])
    K.style_ax(ax, mode, 'both'); K.style_ax(ax2, mode, 'x')
    dep = np.array([(a + b) / 2 for (a, b), *_ in calc.H1]); age = np.array([x[3] for x in calc.H1], float) / 1000; err = np.array([x[4] for x in calc.H1], float) / 1000
    ax.errorbar(age, dep, xerr=err, fmt='o', ms=4, mfc=P['a'], mec=P['ink'], ecolor=P['soft'], elinewidth=0.9, capsize=1.8, zorder=4)
    cf = np.polyfit(dep, age * 1000, 2, w=1 / (err * 1000)); dd = np.linspace(0, 375, 100)
    ax.plot(np.polyval(cf, dd) / 1000, dd, color=P['soft'], lw=1.0, zorder=3)
    ax.plot([10.304], [174.75], '*', ms=11, mfc=P['dry'] if mode == 'color' else '#FFFFFF', mec=P['ink'], zorder=5)
    ax.plot([10.7], [175], 'D', ms=5, mfc='#FFFFFF', mec=P['ink'], zorder=5)
    ax.annotate('같은 깊이에서 14C 10.30과\n꽃가루대 경계 10.7(차 0.40)', (10.5, 175), xytext=(6.9, 62), fontsize=8, color=P['ink'], ha='left', va='center',
                arrowprops=dict(arrowstyle='-', color=P['ink'], lw=0.6))
    ax.set_ylim(385, 0); ax.set_xlim(0, 12)
    ax.set_xlabel('나이 (cal kyr BP)', fontsize=8); ax.set_ylabel('깊이 (cm)', fontsize=8)
    ax.legend(handles=[plt.Line2D([], [], marker='o', mfc=P['a'], mec=P['ink'], color=P['soft'], ls='', ms=4), plt.Line2D([], [], color=P['soft'], lw=1.0),
                       plt.Line2D([], [], marker='*', mfc=P['dry'] if mode == 'color' else '#FFFFFF', mec=P['ink'], ls='', ms=9), plt.Line2D([], [], marker='D', mfc='#FFFFFF', mec=P['ink'], ls='', ms=5)],
              labels=['Hoton-1 연대 6개(논문 보정)', '2차 다항 적합(이 책)', 'Hoton-2의 14C 연대', 'Hoton-2의 꽃가루대 경계'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.19), ncol=2, columnspacing=0.8, handletextpad=0.3)
    f.text(0.02, 0.975, '(가) 호톤 호의 깊이와 나이', fontsize=8, va='top', color=P['ink'])
    zb = calc.zb; rr = []; lab = []
    for i in range(len(zb) - 1):
        dd_ = zb[i][0] - zb[i + 1][0]; dt = zb[i][1] - zb[i + 1][1]; rr.append(dd_ * 10 / (dt * 1000)); lab.append('%g~%g' % (zb[i + 1][1], zb[i][1]))
    ax2.barh(range(4), rr[::-1], color=P['a'], edgecolor=P['ink'], linewidth=0.4, height=0.6, zorder=3)
    ax2.set_yticks(range(4)); ax2.set_yticklabels(lab[::-1], fontsize=8)
    ax2.set_xlabel('퇴적률 (mm/년). 축 글자는 구간 나이(kyr BP)', fontsize=8)
    f.text(0.02, 0.30, '(나) 꽃가루대 경계로 구한 퇴적률', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 4: 울란 호
def fig_ulaan(mode):
    P = K.C[mode]
    f = K.fig(130, 92)
    ax = f.add_axes([0.12, 0.30, 0.46, 0.58]); ax2 = f.add_axes([0.72, 0.30, 0.25, 0.58])
    K.style_ax(ax, mode, 'both'); K.style_ax(ax2, mode, 'x')
    Z = calc.Z
    ax.plot([z[1] for z in Z], [z[0] for z in Z], 'o-', color=P['a'], mfc='#FFFFFF', mec=P['ink'], lw=1.0, ms=4, zorder=4)
    for d, pub in ((534, 15.2), (411, 11.7), (390, 11.1), (355, 10.1), (114, 3.2)):
        ax.plot(pub, d, 'x', color=P['ink'], ms=5, mew=1.0, zorder=5)
    ax.set_ylim(600, 0); ax.set_xlim(0, 18)
    ax.set_xlabel('나이 (ka)', fontsize=8); ax.set_ylabel('깊이 (cm)', fontsize=8)
    ax.legend(handles=[plt.Line2D([], [], marker='o', mfc='#FFFFFF', mec=P['ink'], color=P['a'], ms=4), plt.Line2D([], [], marker='x', color=P['ink'], ls='', ms=5, mew=1.0)],
              labels=['구간 경계(논문)', '본문의 깊이-나이 짝'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.45, -0.17), ncol=1)
    f.text(0.02, 0.975, '(가) 구간 경계의 직선 이음', fontsize=8, va='top', color=P['ink'])
    sp = calc.sp; tot = sum(sp.values())
    nm = {'Limnocythere inopinata': 'L. inopinata', 'Ilyocypris gr. inermis': 'Ilyocypris', 'Cypridopsis vidua': 'C. vidua', 'Heterocypris salina': 'H. salina', 'Pseudocandona': 'Pseudocandona', 'Sarscypridopsis aculeata': 'S. aculeata'}
    ks = list(sp)
    ax2.barh(range(len(ks)), [sp[k] / tot * 100 for k in ks][::-1], color=P['a'], edgecolor=P['ink'], linewidth=0.4, height=0.6, zorder=3)
    ax2.set_yticks(range(len(ks))); ax2.set_yticklabels([nm[k] for k in ks][::-1], fontsize=8, style='italic')
    ax2.set_xlim(0, 100)
    for i, k in enumerate(ks[::-1]):
        v = sp[k] / tot * 100
        ax2.text(v + 2 if v < 70 else v - 2, i, '%.1f' % v, fontsize=8, va='center', ha='left' if v < 70 else 'right', color=P['ink'] if v < 70 else '#FFFFFF')
    ax2.set_xlabel('밸브 비율 (%%, 합 %d)' % tot, fontsize=8)
    f.text(0.62, 0.975, '(나) 패충류 종 구성', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 5: 몽골 기록의 습윤·건조 구간과 중점
MGS = {'텔멘 호(Peck 2002)': '텔멘 호(Peck)', '텔멘 호(Struck 2022)': '텔멘 호(Struck)', '우기 호(Schwanghart 2008)': '우기 호', '호톤 호(Rudaya 2008)': '호톤 호',
       '군 호(Zhang C. 2012)': '군 호', '울란 호(Mischke 2020)': '울란 호', '홉스골 호(Prokopenko 2007)': '홉스골 호', '오르혼 토양(Timireva 2026)': '오르혼 토양'}
def fig_mongolia(mode):
    P = K.C[mode]
    f = K.fig(130, 112)
    ax = f.add_axes([0.25, 0.43, 0.72, 0.50]); ax2 = f.add_axes([0.25, 0.10, 0.72, 0.17])
    K.style_ax(ax, mode, 'x'); K.style_ax(ax2, mode, 'x')
    f1.gantt(ax, calc.MG, mode, MGS)
    ax.set_xlim(12, 0)
    plt.setp(ax.get_xticklabels(), visible=False)
    for k, nm in enumerate(calc.MG):
        y = len(calc.MG) - 1 - k
        ax.plot(calc.M_mid[k], y, 'D', ms=4.5, mfc='#FFFFFF', mec=P['ink'], zorder=6)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=P['wet'], ec=P['ink'], lw=0.5, hatch=K.HATCH[mode]['wet']), plt.Rectangle((0, 0), 1, 1, fc=P['dry'], ec=P['ink'], lw=0.5), plt.Line2D([], [], marker='D', mfc='#FFFFFF', mec=P['ink'], ls='', ms=4.5)],
              labels=['습윤', '건조', '가장 긴 습윤 구간의 중점'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.45, -0.02), ncol=3, handletextpad=0.3, columnspacing=0.8)
    f.text(0.02, 0.975, '(가) 몽골 안쪽 기록 8개의 습윤·건조 구간 (이 책의 판독)', fontsize=8, va='top', color=P['ink'])
    rng = np.random.default_rng(3)
    for yy, arr, mk_, fc in ((1, calc.E_mid, 'o', P['a']), (0, calc.M_mid, 'D', '#FFFFFF')):
        ax2.plot(arr, yy + rng.uniform(-0.12, 0.12, len(arr)), mk_, ms=4.5, mfc=fc, mec=P['ink'], zorder=4)
        ax2.plot([arr.mean() - arr.std(ddof=1), arr.mean() + arr.std(ddof=1)], [yy - 0.33, yy - 0.33], color=P['ink'], lw=1.6, zorder=3)
        ax2.plot(arr.mean(), yy - 0.33, '|', ms=7, color=P['ink'], mew=1.6, zorder=3)
    ax2.set_yticks([0, 1]); ax2.set_yticklabels(['몽골 안쪽 8', '가장자리 13'], fontsize=8); ax2.set_ylim(-0.7, 1.5)
    ax2.set_xlim(12, 0); ax2.set_xlabel('가장 긴 습윤 구간의 중점 (ka). 선은 평균±1 표준편차', fontsize=8)
    f.text(0.02, 0.305, '(나) 중점의 흩어짐: 표준편차 %.2f 대 %.2f ka' % (calc.M_mid.std(ddof=1), calc.E_mid.std(ddof=1)), fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 6: 텔멘 호 두 논문
def fig_telmen(mode):
    P = K.C[mode]
    f = K.fig(130, 70)
    ax = f.add_axes([0.25, 0.30, 0.72, 0.55]); K.style_ax(ax, mode, 'x')
    ce = calc.ce2
    pk = [(7110, 6260, -1), (6260, 4390, -1), (4390, 0, +1)]
    sk = [(4250, ce(-1200), -1), (ce(-1200), ce(700), +1), (ce(700), ce(1300), -1), (ce(1300), 0, +1)]
    for y, rec in ((1, pk), (0, sk)):
        for a, b, s in rec:
            K.wet_dry_bar(ax, y, a, b, s, mode, h=0.5)
    ax.plot([2710, 1260], [1.38, 1.38], '-', color=P['ink'], lw=2.0); ax.text(1985, 1.55, '현재 이상 습윤(Peck)', fontsize=8, ha='center', va='bottom', color=P['ink'])
    ax.axvspan(4390, 3149, color=P['grid'], zorder=1, alpha=0.8)
    ax.text(3770, -0.58, '서로 어긋나는 1101년', fontsize=8, ha='center', va='top', color=P['soft'])
    ax.set_xlim(7400, 0); ax.set_ylim(-0.95, 2.0)
    ax.set_yticks([0, 1]); ax.set_yticklabels(['Struck 등 2022', 'Peck 등 2002'], fontsize=8)
    ax.set_xlabel('cal yr BP (오래된 쪽이 왼쪽)', fontsize=8)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=P['wet'], ec=P['ink'], lw=0.5, hatch=K.HATCH[mode]['wet']), plt.Rectangle((0, 0), 1, 1, fc=P['dry'], ec=P['ink'], lw=0.5)],
              labels=['습윤', '건조'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2)
    f.text(0.02, 0.975, '텔멘 호의 두 논문 판독. 기원 연도는 BP = 1950 − 연도로 옮김', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 7: 유효 표본과 상관
def fig_neff(mode):
    P = K.C[mode]
    f = K.fig(130, 70)
    ax = f.add_axes([0.13, 0.20, 0.80, 0.64]); K.style_ax(ax, mode, 'y')
    rhos = [0.0, 0.5, 0.8, 0.9]; n = calc.n; cnt = []; ne_ = []
    for rho in rhos:
        ne = n * (1 - rho) / (1 + rho); tc = stats.t.ppf(0.975, max(ne - 2, 1)); rc = tc / np.sqrt(max(ne - 2, 1) + tc ** 2)
        cnt.append(sum(1 for _, r in calc.R if abs(r) > rc)); ne_.append(ne)
    ax.bar(range(4), cnt, color=P['a'], edgecolor=P['ink'], linewidth=0.4, width=0.6, zorder=3, hatch='////' if mode == 'bw' else None)
    for i, c in enumerate(cnt):
        ax.text(i, c + 0.25, '%d / 10' % c, fontsize=8, ha='center', va='bottom', color=P['ink'])
    ax.set_xticks(range(4)); ax.set_xticklabels(['%.1f\n(유효 표본 %.0f)' % (r, e) for r, e in zip(rhos, ne_)], fontsize=8)
    ax.set_ylim(0, 12); ax.set_xlabel('가정한 1차 자기상관 (시연값, 논문에는 없음)', fontsize=8); ax.set_ylabel('5% 유의 상관 수', fontsize=8)
    f.text(0.02, 0.975, '시레트 나이만 호 상관 10개가 유효 표본에 따라 남는 수', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 8: 경도와 습윤 시작 나이
def fig_lon(mode):
    P = K.C[mode]
    f = K.fig(130, 78)
    ax = f.add_axes([0.12, 0.17, 0.84, 0.68]); K.style_ax(ax, mode, 'both')
    off = {'호톤 호': (-0.4, 0.45, 'right'), '텔멘 호': (0.7, 0.0, 'left'), '울란 호': (0.7, 0.25, 'left'), '차간 누르': (-0.6, 0.5, 'right'), '달리호': (-0.6, 0.35, 'right'), '호륜호': (0.7, 0.45, 'left')}
    for nm, lo, on, _ in calc.GEO:
        ax.plot(lo, on, 'o', ms=6, mfc=P['a'], mec=P['ink'], zorder=4)
        dx, dy, ha = off[nm]
        ax.text(lo + dx, on + dy, nm, fontsize=8, ha=ha, va='center', color=P['ink'])
    ax.plot([97.32, 97.32], [4.39, 3.15], color=P['soft'], lw=0.8, ls=':'); ax.plot(97.32, 3.15, 'o', ms=6, mfc='#FFFFFF', mec=P['ink'], zorder=4)
    ax.text(98.0, 3.15, '텔멘 Struck 값', fontsize=8, va='center', color=P['soft'])
    ax.set_xlim(85, 122); ax.set_ylim(2, 13)
    ax.set_xlabel('동경 (도)', fontsize=8); ax.set_ylabel('습윤 시작 나이 (ka)', fontsize=8)
    f.text(0.02, 0.975, '경도와 습윤 시작 나이 (스피어만 rho = −0.31, 정확 순열 p = 0.564, n = 6)', fontsize=8, va='top', color=P['ink'])
    return f

if __name__ == '__main__':
    todo = [('ch02-map', fig_map), ('ch02-ugii', fig_ugii), ('ch02-hoton', fig_hoton), ('ch02-ulaan', fig_ulaan), ('ch02-mongolia', fig_mongolia),
            ('ch02-telmen', fig_telmen), ('ch02-neff', fig_neff), ('ch02-lon', fig_lon)]
    only = sys.argv[1:]
    bad = 0
    for nm, fn in todo:
        if only and nm not in only:
            continue
        for m in MODES:
            bad += len(K.save(fn(m), nm, m))
    print('경고 합계', bad)
