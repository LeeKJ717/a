# -*- coding: utf-8 -*-
"""10장 「태양 활동」 그림 5장(색·흑백 SVG 두 벌): fig/fig-ch10-*-v1-{color,bw}.svg
값은 이 장이 읽은 논문의 숫자이거나 ms/code/ch10/out 의 계산 결과(json)와 IntCal20 곡선 파일이다. 논문의 그림을 옮긴 것이 아니라 숫자를 다시 그린 것이다.
  grand  : 큰 극소기와 극대기(Usoskin 등 2016 표 1, 2)  (계산 10-1)
  miyake : 세 사건의 Δ14C와 초과 14C(Brehm 등 2022 표 1)  (계산 10-2)
  gaps   : 극소기 사이의 간격, 변동계수 기준선, 레일리 R(P)  (계산 10-1)
  periods: 논문들이 적은 주기  (계산 10-4)
  intcal : IntCal20 곡선의 서기 774~775, 993~994 둘레  (계산 10-3)
쓰는 법(작업 폴더 /home/claude/book4): PREVDIR=/경로 python3 scripts/figs-ch10.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p10')
import numpy as np
import figkit12 as F
from matplotlib.patches import Patch
CODE = os.path.join(ROOT, 'ms', 'code', 'ch10')
J = lambda n: json.load(open(os.path.join(CODE, 'out', n), encoding='utf-8'))


def fig_grand(mode):
    P = F.C[mode]; R = J('calc10-1.json')
    f = F.fig(130, 96)
    a1 = f.add_axes([0.10, 0.62, 0.86, 0.28]); a2 = f.add_axes([0.10, 0.13, 0.86, 0.28])
    for ax, lo, hi in ((a1, -7000, 2100), (a2, 400, 2100)):
        for c, d in R['minima']:
            ax.barh(1, d, left=c - d / 2, height=0.7, color=P['a'], edgecolor=P['ink'], lw=0.4, zorder=3)
        for c, d in R['maxima']:
            ax.barh(0, d, left=c - d / 2, height=0.7, color=P['wet'] if mode == 'bw' else P['b'], edgecolor=P['ink'], lw=0.4, zorder=3)
        ax.set_xlim(lo, hi); ax.set_ylim(-0.6, 1.7); ax.set_yticks([0, 1]); ax.set_yticklabels(['큰 극대기', '큰 극소기'], fontsize=8)
        F.style_ax(ax, mode, grid='x')
    a1.set_xticks(range(-7000, 2001, 1000)); a1.set_xticklabels([('기원전\n%d' % -v) if v < 0 else ('0' if v == 0 else '%d' % v) for v in range(-7000, 2001, 1000)], fontsize=8)
    a1.set_xlabel('연도(기원전은 앞에 표시, 막대는 중심 ± 지속/2)', fontsize=8)
    a2.set_xticks(range(400, 2101, 200)); a2.set_xticklabels([str(v) for v in range(400, 2101, 200)], fontsize=8)
    a2.set_xlabel('서기 400~2100 확대(소수 연도는 표의 중심 연대)', fontsize=8)
    for c, n, dy in ((690, '690', 0), (1030, '오르트', 0), (1310, '볼프', 0), (1470, '슈푀러', 0), (1680, '마운더', 0)):
        a2.text(c, 1.45, n, ha='center', va='bottom', fontsize=8, color=P['ink'])
    a2.text(1970, 0.55, '현대', ha='center', va='bottom', fontsize=8, color=P['ink'])
    a2.text(505, 0.55, '505', ha='center', va='bottom', fontsize=8, color=P['ink'])
    a1.set_title('', fontsize=8)
    return F.save(f, 'ch10-grand', mode)


def fig_miyake(mode):
    P = F.C[mode]
    f = F.fig(130, 78)
    a1 = f.add_axes([0.10, 0.20, 0.36, 0.72]); a2 = f.add_axes([0.58, 0.20, 0.38, 0.72])
    names = ['7176 BCE', '5259 BCE', '775 CE']
    d = [19.5, 19.1, 17.6]; sd = [0.6, 0.6, 0.5]
    a1.bar(range(3), d, yerr=sd, color=[P['a'], P['a'], P['b']], edgecolor=P['ink'], lw=0.6, capsize=3, zorder=3)
    for i, v in enumerate(d): a1.text(i, v + 0.9 + sd[i], '%.1f' % v, ha='center', va='bottom', fontsize=8, color=P['ink'])
    a1.set_xticks(range(3)); a1.set_xticklabels(names, fontsize=8); a1.set_ylim(0, 24); a1.set_ylabel('Δ14C 상승(‰)', fontsize=8)
    F.style_ax(a1, mode, grid='y')
    # 초과 14C 와 정규화
    raw = [28.7, 29.2, 26.2]; rsd = [0.9, 0.9, 1.0]
    kn = [(30.1, 3.6), (27.6, 1.4), (31.5, 1.4)]; pa = [(28.0, 1.2), (28.4, 1.2), (29.0, 1.4)]
    x = np.arange(3)
    a2.errorbar(x - 0.22, raw, yerr=rsd, fmt='o', ms=5, color=P['ink'], mfc='white', capsize=2.5, lw=0.9, label='정규화 전')
    a2.errorbar(x, [v for v, _ in kn], yerr=[e for _, e in kn], fmt='s', ms=5, color=P['a'], capsize=2.5, lw=0.9, label='정규화(Knudsen)')
    a2.errorbar(x + 0.22, [v for v, _ in pa], yerr=[e for _, e in pa], fmt='^', ms=5, color=P['b'], capsize=2.5, lw=0.9, label='정규화(Panovska)')
    a2.set_xticks(x); a2.set_xticklabels(names, fontsize=8); a2.set_xlim(-0.6, 2.6); a2.set_ylim(22, 38); a2.set_ylabel('초과 14C(kg)', fontsize=8)
    F.style_ax(a2, mode, grid='y')
    a2.legend(loc='upper left', frameon=False, fontsize=8, handletextpad=0.3, borderaxespad=0.1)
    return F.save(f, 'ch10-miyake', mode)


def fig_gaps(mode):
    P = F.C[mode]; R = J('calc10-1.json')
    f = F.fig(130, 108)
    a1 = f.add_axes([0.10, 0.70, 0.42, 0.25]); a2 = f.add_axes([0.62, 0.70, 0.34, 0.25]); a3 = f.add_axes([0.10, 0.10, 0.86, 0.43])
    g = R['gaps_min']
    a1.bar(range(len(g)), g, color=P['a'], edgecolor=P['ink'], lw=0.4, zorder=3)
    a1.axhline(np.mean(g), color=P['ink'], lw=0.9, ls='--')
    a1.set_xlabel('오래된 쪽부터 번호(점선: 평균 %d년)' % round(np.mean(g)), fontsize=8); a1.set_ylabel('중심 사이 간격(년)', fontsize=8); a1.set_xticks([0, 5, 10, 15]); F.style_ax(a1, mode, grid='y')
    h = R['cv_hist']; e = np.array(h['edges']); c = np.array(h['counts'])
    a2.bar((e[:-1] + e[1:]) / 2, c / c.sum(), width=e[1] - e[0], color=P['mid'], edgecolor=P['ink'], lw=0.3, zorder=3)
    a2.axvline(R['cv_min'], color=P['a'], lw=1.6); a2.text(R['cv_min'] - 0.03, c.max() / c.sum() * 0.92, '관측 %.2f' % R['cv_min'], ha='right', va='top', fontsize=8, color=P['ink'])
    a2.set_xlabel('변동계수 CV', fontsize=8); a2.set_ylabel('비율', fontsize=8); F.style_ax(a2, mode, grid='y')
    rc = R['ray_curve']; Ps = np.array(rc['P'])
    a3.plot(Ps, rc['Rmin'], color=P['a'], lw=1.5, label='극소기 20개'); a3.plot(Ps, rc['nullmin95'], color=P['a'], lw=0.9, ls=':', label='극소기 기준선(점별 95%)')
    a3.plot(Ps, rc['Rmax'], color=P['b'] if mode == 'color' else '#777777', lw=1.5, label='극대기 14개'); a3.plot(Ps, rc['nullmax95'], color=P['b'] if mode == 'color' else '#777777', lw=0.9, ls=':', label='극대기 기준선(점별 95%)')
    a3.axvline(2400, color=P['ink'], lw=0.8, ls='--'); a3.text(2420, 0.02, '2400년', fontsize=8, color=P['ink'], ha='left', va='bottom')
    a3.set_xlabel('가정한 주기 P(년)', fontsize=8); a3.set_ylabel('레일리 R(0~1)', fontsize=8); a3.set_ylim(0, 0.95); a3.set_xlim(1500, 3600)
    a3.legend(loc='upper right', frameon=False, fontsize=8, ncol=2)
    F.style_ax(a3, mode, grid='y')
    return F.save(f, 'ch10-gaps', mode)


def fig_periods(mode):
    P = F.C[mode]
    f = F.fig(130, 94); ax = f.add_axes([0.40, 0.14, 0.56, 0.80])
    rows = [('드 브리스(Steinhilber 등)', 210, 210, 'a'), ('약 350(Steinhilber 등)', 350, 350, 'a'), ('약 500, 약 710(Steinhilber 등)', 500, 710, 'a'),
            ('에디 약 1000(Steinhilber 등)', 1000, 1000, 'a'), ('태양 쪽 1000(Debret 등)', 1000, 1000, 'b'), ('홀로세 평균 1340(Bond 등)', 1340, 1340, 'c'), ('해양 쪽 1500(Debret 등)', 1500, 1500, 'c'),
            ('홀레하임 약 2000(Vecchio 등)', 2000, 2000, 'd'), ('드 브리스 진폭 약 2200(Steinhilber 등)', 2200, 2200, 'a'), ('홀레하임 약 2400(Usoskin 등)', 2400, 2400, 'd'),
            ('태양 쪽 2500(Debret 등)', 2500, 2500, 'b'), ('Usoskin 등 결맞음 구간', 2000, 3000, 'd')]
    ys = np.arange(len(rows))[::-1]
    for y, (n, lo, hi, k) in zip(ys, rows):
        if lo == hi:
            ax.plot([lo], [y], 'o', ms=6, color=P[k], mec=P['ink'], mew=0.6, zorder=4)
        else:
            ax.plot([lo, hi], [y, y], '-', lw=3.5, color=P[k], solid_capstyle='butt', zorder=3)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.set_xscale('log'); ax.set_xlim(150, 4000); ax.set_xticks([200, 500, 1000, 2000, 4000]); ax.set_xticklabels(['200', '500', '1000', '2000', '4000'], fontsize=8)
    import matplotlib.ticker as mt
    ax.xaxis.set_minor_formatter(mt.NullFormatter()); ax.xaxis.set_minor_locator(mt.NullLocator())
    ax.set_xlabel('주기(년, 로그 눈금)', fontsize=8); F.style_ax(ax, mode, grid='x')
    return F.save(f, 'ch10-periods', mode)


def fig_intcal(mode):
    P = F.C[mode]
    c = np.loadtxt(os.path.join(CODE, 'data', 'intcal20.14c'), delimiter=',')
    c = c[np.argsort(c[:, 0])]
    f = F.fig(130, 70)
    a1 = f.add_axes([0.10, 0.20, 0.38, 0.72]); a2 = f.add_axes([0.60, 0.20, 0.36, 0.72])
    for ax, lo, hi, ev in ((a1, 755, 800, 775), (a2, 975, 1020, 993)):
        m = (1950 - c[:, 0] >= lo) & (1950 - c[:, 0] <= hi)
        ax.plot(1950 - c[m, 0], c[m, 3], '-o', ms=3, lw=1.1, color=P['a'], zorder=3)
        ax.axvline(ev, color=P['ink'], lw=0.8, ls='--'); ax.set_xlim(lo, hi)
        ax.set_xlabel('서기 연도', fontsize=8); F.style_ax(ax, mode, grid='y')
    a1.set_ylabel('IntCal20 Δ14C(‰)', fontsize=8)
    a1.text(776.5, a1.get_ylim()[0] + 1.0, '774~775', fontsize=8, ha='left', va='bottom', color=P['ink'])
    a2.text(994.5, a2.get_ylim()[0] + 0.6, '993~994', fontsize=8, ha='left', va='bottom', color=P['ink'])
    return F.save(f, 'ch10-intcal', mode)


if __name__ == '__main__':
    for m in ('color', 'bw'):
        for fn in (fig_grand, fig_miyake, fig_gaps, fig_periods, fig_intcal):
            fn(m)
