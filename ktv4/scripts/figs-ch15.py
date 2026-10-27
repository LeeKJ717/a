# -*- coding: utf-8 -*-
"""15장 「하나의 쟁점을 끝까지」 그림(색·흑백 SVG 두 벌). 자료 그림은 8장 계산 8-4 입력(논문이 적은 창)과 이 장 계산 15-2~15-5 로그의 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다.
  fig-ch15-cover  : 일곱 창과 한 해를 덮는 창의 수(계산 15-2 (b))
  fig-ch15-subset : 창 부분집합 크기별 공통 구간이 있는 비율(계산 15-2 (a))
  fig-ch15-null   : 무작위 배치의 창 너비별 확률(계산 15-3)
  fig-ch15-class  : 분류 규칙별 p 와 서랍 문제(계산 15-4)
  fig-ch15-err    : 간격 대 연대 오차(계산 15-2, 15-5)
사용(작업 폴더 /home/claude/book4): PREVDIR=<미리보기 폴더> python3 scripts/figs-ch15.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as F
plt = F.plt; C = F.C; FS = 8.0
CODE = os.path.join(ROOT, 'ms', 'code', 'ch15')
def load(n): return json.load(open(os.path.join(CODE, n), encoding='utf-8'))
def sty(ax, mode, grid='y'): F.style_ax(ax, mode, grid)

WIN = [('Booth 등 북미 중부', 4100, 4300, 'a'), ('deMenocal 등 먼지 감소', 4100, 4300, 'c'), ('Mayewski 등 급변 구간', 3800, 4200, 'b'),
       ('Bini 등 지중해', 3800, 4300, 'd'), ('Railsback 등 종합', 3930, 4150, 'e'), ('Weiss 개관', 3900, 4200, 'b'), ('유라시아 공통(제3권)', 3970, 4025, 'a')]


def fig_cover(mode):
    P = C[mode]; d = load('calc15-2-out.json')
    f = F.fig(130, 112)
    ax = f.add_axes([0.36, 0.40, 0.61, 0.57]); ax2 = f.add_axes([0.36, 0.09, 0.61, 0.22])
    n = len(WIN)
    for i, (nm, lo, hi, key) in enumerate(WIN):
        y = n - 1 - i
        ax.plot([lo, hi], [y, y], color=P[key], lw=6, solid_capstyle='butt', zorder=3)
    ax.set_yticks(range(n)); ax.set_yticklabels([w[0] for w in WIN][::-1], fontsize=FS, color=P['ink'])
    ax.set_ylim(-0.7, n - 0.3)
    for t, ls in ((4200, '-'), (4070, '--')):
        ax.axvline(t, color=P['ink'], lw=0.8, ls=ls, zorder=2); ax2.axvline(t, color=P['ink'], lw=0.8, ls=ls, zorder=2)
    ax.text(4207, n - 0.35, '4200', ha='right', va='top', fontsize=FS, color=P['ink'])
    ax.text(4063, n - 0.35, '4070', ha='left', va='top', fontsize=FS, color=P['ink'])
    ax.set_xlim(4400, 3500); ax.set_xticklabels([])
    sty(ax, mode, grid='x')
    ts = np.array(d['cov']['ts']); cv = np.array(d['cov']['cov'])
    ax2.step(ts, cv, where='mid', color=P['ink'], lw=1.2)
    ax2.fill_between(ts, 0, cv, step='mid', color=P['mid'], alpha=0.5)
    ax2.scatter([3550], [0], s=30, color=P['d'], edgecolor=P['ink'], linewidth=0.6, zorder=4)
    ax2.text(3555, 1.6, '둥거 3550', ha='right', va='bottom', fontsize=FS, color=P['ink'])
    ax2.set_xlim(4400, 3500); ax2.set_ylim(0, 7.5); ax2.set_yticks([0, 3, 6])
    ax2.set_ylabel('덮는 창 수', fontsize=FS, color=P['soft'])
    ax2.set_xlabel('연대(cal BP, 왼쪽이 오래된 때). 실선 4200, 점선 4070', fontsize=FS, color=P['soft'])
    sty(ax2, mode, grid='x')
    F.save(f, 'ch15-cover', mode)


def fig_subset(mode):
    P = C[mode]; d = load('calc15-2-out.json')['subsets']
    f = F.fig(130, 66)
    ax = f.add_axes([0.13, 0.22, 0.84, 0.70])
    ks = [r[0] for r in d]; tot = [r[1] for r in d]; pos = [r[2] for r in d]
    x = np.arange(len(ks))
    ax.bar(x, tot, width=0.62, color=P['mid'], edgecolor=P['ink'], linewidth=0.5, label='부분집합 수')
    ax.bar(x, pos, width=0.62, color=P['a'], edgecolor=P['ink'], linewidth=0.5, label='공통 구간이 있는 수')
    for xi, t, p in zip(x, tot, pos):
        ax.text(xi, t + 0.8, '%d / %d' % (p, t), ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ax.set_xticks(x); ax.set_xticklabels([str(k) for k in ks], fontsize=FS, color=P['ink'])
    ax.set_xlabel('부분집합에 넣은 창의 수(일곱 창 가운데)', fontsize=FS, color=P['soft'])
    ax.set_ylabel('부분집합 수', fontsize=FS, color=P['soft']); ax.set_ylim(0, 42)
    ax.legend(loc='upper right', fontsize=FS, frameon=False)
    sty(ax, mode, grid='y')
    F.save(f, 'ch15-subset', mode)


def fig_null(mode):
    P = C[mode]; d = load('calc15-3-out.json')
    f = F.fig(130, 76)
    ax = f.add_axes([0.13, 0.22, 0.84, 0.70])
    Ws = ['600', '800', '1000', '1500', '3000']
    pc = [d['null1'][w]['p_common'] for w in Ws]; pp = [d['null1'][w]['p_pair'] for w in Ws]
    x = np.arange(len(Ws))
    ax.plot(x, pc, 'o-', color=P['a'], lw=1.4, ms=5, label='공통 구간이 50년 이상')
    ax.plot(x, pp, 's--', color=P['b'], lw=1.4, ms=5, mfc='#FFFFFF', label='쌍별 겹침 평균이 관측 이상(%.3f)' % d['obs_pair'])
    ax.axhline(0.05, color=P['ink'], lw=0.7, ls=':')
    ax.text(-0.35, 0.058, '0.05', ha='left', va='bottom', fontsize=FS, color=P['ink'])
    for xi, v in zip(x, pc): ax.text(xi, v + 0.05, '%.3f' % v, ha='center', va='bottom', fontsize=FS, color=P['a'] if mode == 'color' else P['ink'])
    ax.scatter([5.1], [d['null2']['p_common']], s=40, marker='D', color=P['a'], edgecolor=P['ink'], linewidth=0.6, zorder=4)
    ax.scatter([5.1], [d['null2']['p_pair']], s=40, marker='D', color=P['b'], edgecolor=P['ink'], linewidth=0.6, zorder=4)
    ax.text(5.1, d['null2']['p_common'] + 0.035, '%.2f' % d['null2']['p_common'], ha='center', va='bottom', fontsize=FS, color=P['ink'])
    ax.text(5.1, d['null2']['p_pair'] - 0.035, '%.2f' % d['null2']['p_pair'], ha='center', va='top', fontsize=FS, color=P['ink'])
    ax.set_xticks(list(x) + [5.1]); ax.set_xticklabels(Ws + ['4200을\n덮는다'], fontsize=FS, color=P['ink'])
    ax.set_xlim(-0.4, 5.6); ax.set_ylim(0, 0.95)
    ax.set_xlabel('영 모형 1의 틀 너비 W(년). 오른쪽 마름모는 영 모형 2(각 창이 4200을 덮는다)', fontsize=FS, color=P['soft'])
    ax.set_ylabel('무작위 배치에서 관측 이상일 확률', fontsize=FS, color=P['soft'])
    ax.legend(loc='upper center', fontsize=FS, frameon=False, bbox_to_anchor=(0.50, 1.0))
    sty(ax, mode, grid='y')
    F.save(f, 'ch15-null', mode)


def fig_class(mode):
    P = C[mode]; d = load('calc15-4-out.json')
    f = F.fig(130, 78)
    ax = f.add_axes([0.10, 0.20, 0.40, 0.74]); ax2 = f.add_axes([0.62, 0.20, 0.35, 0.74])
    rows = d['rows']; n = len(rows)
    for i, r in enumerate(rows):
        y = n - 1 - i
        ax.barh(y, r['p'], height=0.6, color=P['a'] if r['p'] < 0.05 else P['b'], edgecolor=P['ink'], linewidth=0.5, zorder=3)
        ax.text(r['p'] * 1.15, y, '%.3f' % r['p'], ha='left', va='center', fontsize=FS, color=P['ink'])
    ax.set_xscale('log'); ax.set_xlim(0.005, 1.5)
    ax.axvline(0.05, color=P['ink'], lw=0.7, ls=':')
    ax.set_yticks(range(n)); ax.set_yticklabels(['S%d' % (k + 1) for k in range(n)][::-1], fontsize=FS, color=P['ink'])
    ax.set_xlabel('건조 쪽 단측 이항 p(점선 0.05)', fontsize=FS, color=P['soft'])
    ax.set_title('분류 규칙 S1~S8', fontsize=FS, color=P['ink'], loc='left')
    sty(ax, mode, grid='x')
    from scipy import stats
    ks = np.arange(0, 9); ps = [stats.binomtest(15, 19 + k, 0.5, alternative='greater').pvalue for k in ks]
    ax2.plot(ks, ps, 'o-', color=P['a'], lw=1.4, ms=5)
    ax2.axhline(0.05, color=P['ink'], lw=0.7, ls=':')
    ax2.set_xlabel('보고되지 않은 습윤 기록 k', fontsize=FS, color=P['soft']); ax2.set_ylabel('p', fontsize=FS, color=P['soft'])
    ax2.set_title('서랍 문제(건조 15, 습윤 4 + k)', fontsize=FS, color=P['ink'], loc='left')
    ax2.set_ylim(0, 0.42); ax2.set_xticks(range(0, 9, 2))
    sty(ax2, mode, grid='y')
    F.save(f, 'ch15-class', mode)


def fig_err(mode):
    P = C[mode]
    f = F.fig(130, 70)
    ax = f.add_axes([0.40, 0.20, 0.55, 0.74])
    rows = [('둥거 3550과 메갈라야 4200의 간격', 650, 'gap'), ('둥거 3550과 Railsback 중심 4070의 간격', 520, 'gap'), ('유라시아 공통과 Booth 창의 간격', 75, 'gap'),
            ('ODP 658C 종료 오차 ± 190의 2시그마', 380, 'err'), ('둥거 오차 ± 59의 2시그마', 118, 'err'), ('나미비아 DP1 U-Th 오차 ≤ 28의 2시그마', 56, 'err')]
    n = len(rows)
    for i, (nm, v, kind) in enumerate(rows):
        y = n - 1 - i
        ax.barh(y, v, height=0.6, color=P['a'] if kind == 'gap' else P['b'], edgecolor=P['ink'], linewidth=0.5, zorder=3, hatch=('////' if (mode == 'bw' and kind == 'err') else None))
        ax.text(v + 10, y, '%d' % v, ha='left', va='center', fontsize=FS, color=P['ink'])
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=FS, color=P['ink'])
    ax.set_xlim(0, 760); ax.set_xlabel('년(위 셋은 간격, 아래 셋은 8장이 적은 오차의 2시그마)', fontsize=FS, color=P['soft'])
    sty(ax, mode, grid='x')
    F.save(f, 'ch15-err', mode)


if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_cover(m); fig_subset(m); fig_null(m); fig_class(m); fig_err(m)
