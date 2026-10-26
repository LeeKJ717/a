# -*- coding: utf-8 -*-
"""6장 그림(색·흑백 SVG 두 벌). 자료 그림은 논문이 적은 숫자를 다시 그린 것이다. 입력: ms/code/ch06 의 기록 목록과 계산 결과(.json).
  fig-ch06-intervals-v1 : 지역별 4.2 ka 사건 구간(논문이 적은 시작과 끝)
  fig-ch06-overlap-v1   : 건조 구간 10개의 쌍별 겹침 비율
  fig-ch06-onset-v1     : 연대 점추정과 오차(서아시아 넷, 고고 둘, 호륜호 재현)
  fig-ch06-null-v1      : 무작위 배치 대비 관측 겹침(창 너비 세 가지)
사용: GEODIR=/home/claude/book3/geodata python3 figs-ch06.py"""
import os, sys, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault('GEODIR', os.path.join(ROOT, 'geodata'))
sys.path.insert(0, HERE)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
from mapkit import use_font, mm_fig, label_audit
FIG = os.path.join(ROOT, 'fig'); CODE = os.path.join(ROOT, 'ms', 'code', 'ch06')
use_font(8.0)
spec = importlib.util.spec_from_file_location('rec', os.path.join(CODE, 'ch06-records.py'))
rec = importlib.util.module_from_spec(spec); spec.loader.exec_module(rec)
R = {r['id']: r for r in rec.R}
SER = {'color': dict(dry='#9C4F2E', wet='#2F6F9A', melt='#5B7F3A', none='#9AA7AE', ink='#1B2A33', soft='#4F6E80', grid='#D6DEE2', band='#F1EBDD'),
       'bw': dict(dry='#111111', wet='#BBBBBB', melt='#666666', none='#EEEEEE', ink='#111111', soft='#444444', grid='#DDDDDD', band='#EDEDED')}
HATCH = {'dry': None, 'wet': None, 'melt': '///', 'none': '...'}


def save(fig, name, mode):
    w, n = label_audit(fig)
    fig.savefig(os.path.join(FIG, 'fig-ch06-%s-v1-%s.svg' % (name, mode)), format='svg')
    plt.close(fig)
    print('%s %-10s 글자 %3d개 경고 %d %s' % (mode, name, n, len(w), w[:4]))


def fig_intervals(mode):
    C = SER[mode]
    rows = [('지중해', 'Roberts', '동지중해 종합'), ('서아시아', 'GOman', '오만만 코어'), ('서아시아', 'Gol', '골에자르드(둘째)'), ('서아시아', 'GolP1', '골에자르드(첫째)'),
            ('남아시아', 'Kotla', '코틀라다하르'),
            ('중앙아시아', 'Bosten1', '보스텐호 (건조)'), ('중앙아시아', 'Bosten2', '보스텐호 (건조)'), ('중앙아시아', 'Karakul', '카라쿨'), ('중앙아시아', 'LopNur', '롭노르'), ('중앙아시아', 'Altai', '하르 노르'),
            ('동아시아', 'Dali', '달리호'), ('동아시아', 'Hulun', '호륜호'), ('동아시아', 'Hunsh', '훈산다크'), ('동아시아', 'Daihai', '다이하이호'), ('동아시아', 'Dongge', '동거동굴'),
            ('동아시아', 'KoreaAP', '한국 남해안'), ('동아시아', 'Shennong', '신농동굴'), ('동아시아', 'Xianglong', '상룡동굴')]
    n = len(rows)
    fig = mm_fig(130, 160)
    ax = fig.add_axes([0.335, 0.125, 0.625, 0.86])
    ax.set_xlim(4700, 3300); ax.set_ylim(-0.7, n + 0.1)
    ys = {i: n - 1 - k for k, i in enumerate(rows)}
    ax.set_yticks([n - 1 - k for k in range(n)]); ax.set_yticklabels([r[2] for r in rows], fontsize=8, color=C['ink'])
    ax.set_xticks(range(4700, 3299, -200)); ax.set_xticklabels([str(v) for v in range(4700, 3299, -200)], fontsize=8, color=C['soft'])
    ax.set_xlabel('보정 연대(cal yr BP). 왼쪽이 오래된 때', fontsize=8, color=C['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    rb = rec.RAILSBACK
    ax.add_patch(Rectangle((rb['lo'], -0.7), rb['hi'] - rb['lo'], n + 0.8, facecolor=C['band'], edgecolor='none', zorder=0))
    for xv in range(4700, 3299, -200): ax.axvline(xv, color=C['grid'], lw=0.5, zorder=1)
    ax.axvline(4200, color=C['ink'], lw=0.7, ls=(0, (3, 3)), zorder=2)
    # 지역 구분선
    prev = None
    for k, (reg, i, lab) in enumerate(rows):
        y = n - 1 - k
        if reg != prev and prev is not None:
            ax.axhline(y + 0.5, color=C['soft'], lw=0.5, zorder=1)
        prev = reg
        r = R[i]
        ax.add_patch(Rectangle((r['end'], y - 0.28), r['start'] - r['end'], 0.56, facecolor=C[r['dir']], edgecolor=C['ink'], linewidth=0.5, hatch=HATCH[r['dir']], zorder=3))
        if r['s_sd']:
            ax.errorbar([r['start']], [y], xerr=[[r['s_sd']], [r['s_sd']]], fmt='none', ecolor=C['ink'], elinewidth=0.8, capsize=2, zorder=5)
    # 지역 이름(왼쪽 가장자리 열)
    regs = {}
    for k, (reg, i, lab) in enumerate(rows): regs.setdefault(reg, []).append(n - 1 - k)
    for reg, yy in regs.items():
        yc = np.mean(yy)
        fy = 0.125 + 0.86 * (yc + 0.7) / (n + 0.1 + 0.7)
        fig.text(0.012, fy, reg, fontsize=8, ha='left', va='center', color=C['ink'], fontweight='bold')
    t = ax.text(4200, n - 0.42, '4200', fontsize=8, ha='center', va='bottom', color=C['ink'], bbox=dict(facecolor='#FFFFFF', edgecolor='none', pad=0.5), zorder=8)
    from matplotlib.patches import Patch
    hs = [Patch(facecolor=C[d], edgecolor=C['ink'], linewidth=0.5, hatch=HATCH[d], label=lab) for d, lab in (('dry', '건조'), ('wet', '습윤'), ('melt', '따뜻·녹은 물'))]
    ax.legend(handles=hs, loc='upper center', bbox_to_anchor=(0.30, -0.105), ncol=3, fontsize=8, frameon=False, handletextpad=0.5, columnspacing=1.5)
    save(fig, 'intervals', mode)


def fig_overlap(mode):
    C = SER[mode]
    d = json.load(open(os.path.join(CODE, 'ch06-calc-overlap.json'), encoding='utf-8'))['6-4-matrix']
    ids = d['ids']; M = np.array(d['m'], float)
    labs = {'Hulun': '호륜호', 'Dali': '달리호', 'Daihai': '다이하이', 'Hunsh': '훈산다크', 'Dongge': '동거', 'Gol': '골에자르드', 'GOman': '오만만', 'Roberts': '동지중해', 'Kotla': '코틀라', 'Altai': '하르 노르'}
    fig = mm_fig(130, 112)
    ax = fig.add_axes([0.20, 0.03, 0.78, 0.74])
    cmap = plt.get_cmap('YlOrBr') if mode == 'color' else plt.get_cmap('Greys')
    A = np.where(np.eye(len(ids)) == 1, np.nan, M)
    im = ax.imshow(A, cmap=cmap, vmin=0, vmax=1.15, aspect='equal')
    ax.set_xticks(range(len(ids))); ax.set_yticks(range(len(ids)))
    ax.set_xticklabels([labs[i] for i in ids], fontsize=8, rotation=90, color=C['ink']); ax.xaxis.tick_top()
    ax.set_yticklabels([labs[i] for i in ids], fontsize=8, color=C['ink'])
    ax.tick_params(length=0)
    for a in range(len(ids)):
        for b in range(len(ids)):
            if a == b: continue
            v = M[a, b]
            ax.text(b, a, '%.2f' % v, fontsize=8, ha='center', va='center', color=('#FFFFFF' if (v > 0.6 and mode == 'bw') or (v > 0.78 and mode == 'color') else C['ink']))
    for s in ax.spines.values(): s.set_visible(False)
    save(fig, 'overlap', mode)


def fig_onset(mode):
    C = SER[mode]
    P = [('골에자르드 먼지 시작', 4260, 66, 'dry'), ('홍해 건조(인용)', 4200, 100, 'dry'), ('오만만 먼지(인용)', 4100, 100, 'dry'), ('오만만 먼지(초록)', 4025, 125, 'dry'),
         ('호륜호 시작(재현)', 4217, 43, 'dry'),
         ('정착지 포기', 4190, 20, 'wet'), ('아카드 붕괴', 4170, 150, 'wet')]
    n = len(P)
    fig = mm_fig(130, 70)
    ax = fig.add_axes([0.285, 0.17, 0.69, 0.80])
    ax.set_xlim(3800, 4500); ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([n - 1 - k for k in range(n)]); ax.set_yticklabels([p[0] for p in P], fontsize=8, color=C['ink'])
    ax.set_xticks(range(3800, 4501, 100)); ax.set_xticklabels([str(v) for v in range(3800, 4501, 100)], fontsize=8, color=C['soft'])
    ax.set_xlabel('보정 연대(cal yr BP). 가로선은 ± 1 표준편차(가정)', fontsize=8, color=C['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for xv in range(3800, 4501, 100): ax.axvline(xv, color=C['grid'], lw=0.5, zorder=0)
    m = 4185.0; e = 45.0
    ax.add_patch(Rectangle((m - e, -0.7), 2 * e, n + 0.4, facecolor=C['band'], edgecolor='none', zorder=0))
    ax.axvline(m, color=C['ink'], lw=0.7, ls=(0, (3, 3)), zorder=1)
    for k, (nm, v, s, kind) in enumerate(P):
        y = n - 1 - k
        ax.errorbar([v], [y], xerr=[[s], [s]], fmt='none', ecolor=C['ink'], elinewidth=1.0, capsize=3, zorder=3)
        ax.scatter([v], [y], s=34, marker='o' if kind == 'dry' else 's', facecolor=C['dry'] if kind == 'dry' else C['wet'], edgecolor=C['ink'], linewidth=0.6, zorder=5)
    save(fig, 'onset', mode)


def fig_null(mode):
    C = SER[mode]
    d = json.load(open(os.path.join(CODE, 'ch06-calc-null.json')))
    fig = mm_fig(130, 62)
    ax = fig.add_axes([0.12, 0.20, 0.86, 0.74])
    Ws = ['800', '1500', '3000']
    means = [d[w]['mean'] for w in Ws]
    ps = [d[w]['p'] for w in Ws]
    ax.bar(range(3), means, width=0.5, facecolor=C['wet'], edgecolor=C['ink'], linewidth=0.6, zorder=3)
    ax.axhline(d['obs'], color=C['dry'], lw=1.4, zorder=4)
    ax.text(2.45, d['obs'] + 0.02, '관측 %.2f' % d['obs'], fontsize=8, ha='right', va='bottom', color=C['ink'])
    for i, (m_, p_) in enumerate(zip(means, ps)):
        ax.text(i, m_ + 0.02, '무작위 %.2f\nP %s' % (m_, ('= %.4f' % p_) if p_ > 0.0001 else '< 0.0001'), fontsize=8, ha='center', va='bottom', color=C['ink'])
    ax.set_xticks(range(3)); ax.set_xticklabels(['창 800년', '창 1500년', '창 3000년'], fontsize=8, color=C['ink'])
    ax.set_ylim(0, 1.15); ax.set_xlim(-0.5, 2.5)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(['0', '0.25', '0.5', '0.75', '1'], fontsize=8, color=C['soft'])
    ax.set_ylabel('쌍별 겹침 비율의 평균', fontsize=8, color=C['soft'])
    ax.tick_params(length=2.5, width=0.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    save(fig, 'null', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        fig_intervals(mode); fig_overlap(mode); fig_onset(mode); fig_null(mode)
