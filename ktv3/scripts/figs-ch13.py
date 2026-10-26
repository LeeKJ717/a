# -*- coding: utf-8 -*-
"""13장 「하나의 쟁점을 끝까지」 그림 생성: fig/fig-ch13-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book3): python3 scripts/figs-ch13.py
자료 그림은 논문이 적은 숫자(Rudaya 등 2009 표)와 이 책의 계산 13-1~13-4 로그의 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다.
글자 8pt 이상, 색과 흑백 두 벌.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mapkit as K

K.use_font(8.5)
FIG = os.path.join(ROOT, 'fig')
CODE = os.path.join(ROOT, 'ms', 'code', 'ch13')
PREVIEW = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p13')
os.makedirs(PREVIEW, exist_ok=True)
LOG = []
PC = {'color': dict(ink='#1B2A33', soft='#4F6E80', grid='#D5DDE1', a='#9C4F2E', b='#2F6F9A', c='#3F7F5A', d='#7A5A9A', hl='#F1D9A0', band='#E3EDF3'),
      'bw': dict(ink='#111111', soft='#444444', grid='#D0D0D0', a='#111111', b='#666666', c='#999999', d='#333333', hl='#DDDDDD', band='#E6E6E6')}


def save(fig, name, mode):
    base = 'fig-ch13-%s-v1-%s' % (name, mode)
    fig.savefig(os.path.join(FIG, base + '.svg'), format='svg', bbox_inches='tight')
    fig.savefig(os.path.join(PREVIEW, base + '.png'), format='png', dpi=110, bbox_inches='tight')
    plt.close(fig); LOG.append(base)


def ax_style(ax, P):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'): ax.spines[s].set_color(P['soft'])
    ax.tick_params(colors=P['ink'], labelsize=8.5)


def load(n): return json.load(open(os.path.join(CODE, n)))


def fig_ages(mode):
    """경계 연대와 점의 연대를 한 축에: 논문 표 10.7, 논문 본문 약 10, 14C 점, 이웃 점, 모형 오차 띠."""
    P = PC[mode]
    c1 = load('calc13-1-out.json'); c2 = load('calc13-2-out.json')
    kia = c1['kia']; s_model = c2['s_model']
    fig, ax = plt.subplots(figsize=(7.2, 3.5)); ax_style(ax, P)
    ax.axvspan(10.7 - s_model / 1000, 10.7 + s_model / 1000, color=P['band'], zorder=0)
    ax.text(10.7 + s_model / 1000 - 0.03, 2.5, '회색 띠: 6점 2차식의\n잔차 표준오차 ±%.0f년\n(계산 13-2)' % s_model, ha='left', va='center', fontsize=8.5, color=P['soft'])
    rows = [
        ('논문 표의 H4/H3 경계', 10.7, 0.05, 'o', P['a'], '0.1 ka 단위로 적음(±50년으로 표시)'),
        ('논문 본문의 "약 10 ka"', 10.0, 0.0, 'D', P['d'], ''),
        ('KIA32076 논문 보정(1시그마)', 10.304, 0.056, 's', P['b'], ''),
        ('KIA32076 이 책 재보정(95.4%)', None, None, 's', P['b'], ''),
        ('TA-1419 Hoton-1(1시그마, 조건부)', 10.194, 0.228, '^', P['c'], ''),
    ]
    ys = list(range(len(rows)))[::-1]
    for y, (nm, x, e, mk, col, note) in zip(ys, rows):
        if nm.startswith('KIA32076 이 책'):
            ax.plot([10.218, 10.481], [y, y], '-', color=col, lw=3.2, solid_capstyle='butt')
            ax.plot([10.298], [y], mk, ms=7, mfc='#FFFFFF', mec=col)
        elif e and e > 0:
            ax.errorbar([x], [y], xerr=[[e], [e]], fmt=mk, ms=7, mfc='#FFFFFF', mec=col, ecolor=col, capsize=3, lw=1.4)
        else:
            ax.plot([x], [y], mk, ms=7, mfc='#FFFFFF', mec=col)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.set_xlim(11.15, 9.6); ax.set_ylim(-0.7, 4.7)
    ax.set_xlabel('연대 (ka, 1950년 기준)')
    ax.grid(axis='x', color=P['grid'], lw=0.5)
    ax.axvline(10.7, color=P['a'], lw=0.8, ls=':'); ax.axvline(10.304, color=P['b'], lw=0.8, ls=':')
    ax.annotate('', xy=(10.304, -0.5), xytext=(10.7, -0.5), arrowprops=dict(arrowstyle='<->', color=P['ink'], lw=1.0))
    ax.text(10.5, -0.38, '396년', ha='center', va='bottom', fontsize=8.5, color=P['ink'])
    ax.set_title('호톤 호 H4/H3 경계의 연대를 말하는 숫자 다섯 개(Rudaya 등 2009 표의 숫자와 계산 13-1, 13-2)', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'ages', mode)


def fig_sigma(mode):
    P = PC[mode]
    z = load('calc13-2-out.json')['z']
    labs = ['(가) 14C 오차만', '(나) 반올림 ±50년', '(다) 점 하나의 오차 229년', '(라) 6점 2차식 잔차', '(마) R²=0.95 잔차(시연)']
    vals = [r['z'] for r in z]
    fig, ax = plt.subplots(figsize=(7.0, 3.3)); ax_style(ax, P)
    ys = np.arange(len(vals))[::-1]
    cols = [P['a'], P['a'], P['b'], P['b'], P['c']]
    ax.barh(ys, vals, color=cols, edgecolor=P['ink'], lw=0.5, height=0.58)
    ax.axvline(1.96, color=P['ink'], lw=0.9, ls='--')
    ax.text(1.96 + 0.1, -0.62, '1.96배(양쪽 5% 기준)', fontsize=8.5, color=P['ink'], va='center')
    for y, v, r in zip(ys, vals, z):
        ax.text(max(v, 1.96) + 0.15, y, '%.2f배  (합성 오차 %d년)' % (v, round(r['comb'])), va='center', fontsize=8.5, color=P['ink'])
    ax.set_yticks(ys); ax.set_yticklabels(labs, fontsize=8.5)
    ax.set_xlim(0, 10.8); ax.set_ylim(-0.95, 4.5); ax.set_xlabel('396년이 오차의 몇 배인가')
    ax.set_title('경계 연대 쪽의 오차를 어떻게 잡는가에 따라 7.07배에서 0.53배까지(계산 13-2)', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'sigma', mode)


def fig_reservoir(mode):
    P = PC[mode]
    r = load('calc13-3-out.json')
    res = r['reservoir']; con = r['contam']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw=dict(width_ratios=[1.0, 1.0]))
    for ax in (a1, a2): ax_style(ax, P)
    xs = [x['R'] for x in res]; ys = [x['gap'] for x in res]
    a1.bar(range(len(xs)), ys, color=P['a'], edgecolor=P['ink'], lw=0.5, width=0.6)
    a1.axhline(396, color=P['ink'], lw=0.9, ls='--', label='논문 표의 396년'); a1.legend(frameon=False, fontsize=8.5, loc='upper left')
    for i, v in enumerate(ys): a1.text(i, v + 60, '%d' % round(v), ha='center', fontsize=8.5, color=P['ink'])
    a1.set_xticks(range(len(xs))); a1.set_xticklabels(['0', '400', '685', '1060', '1920'], fontsize=8.5)
    a1.set_xlabel('빼 준 저장 효과 (년, 시연값)'); a1.set_ylabel('경계 10,700과의 차 (년)'); a1.set_ylim(0, 3100)
    a1.set_title('오래된 탄소를 빼면 어긋남이 커진다', fontsize=8.5, loc='left', color=P['ink'])
    ts = [c['target'] for c in con]; fs = [c['f'] * 100 for c in con]
    a2.bar(range(len(ts)), fs, color=P['b'], edgecolor=P['ink'], lw=0.5, width=0.6)
    for i, v in enumerate(fs): a2.text(i, v + 0.06, '%.2f%%' % v, ha='center', fontsize=8.5, color=P['ink'])
    a2.set_xticks(range(len(ts))); a2.set_xticklabels(['%d' % t for t in ts], fontsize=8.5)
    a2.set_xlabel('시료의 참 연대 (cal BP)'); a2.set_ylabel('필요한 현대 탄소 혼입 (%)'); a2.set_ylim(0, 3.5)
    a2.set_title('젊은 탄소는 1~3%면 충분하다', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'reservoir', mode)


def fig_rates(mode):
    P = PC[mode]
    r = load('calc13-3-out.json')['rates']
    keys = ['10.7', '10.304', '10.0']; labs = ['10.7 ka(논문 표)', '10.304 ka(14C 점)', '10.0 ka(논문 본문)']
    cols = [P['a'], P['b'], P['c']]
    zs = ['H4', 'H3', 'H2', 'H1']
    fig, ax = plt.subplots(figsize=(7.0, 3.4)); ax_style(ax, P)
    w = 0.26
    for i, (k, lb, c) in enumerate(zip(keys, labs, cols)):
        vals = [r[k][z] for z in zs]
        ax.bar(np.arange(4) + (i - 1) * w, vals, width=w, color=c, edgecolor=P['ink'], lw=0.5, label='H4/H3 경계 ' + lb)
        for j, v in enumerate(vals[:2]):
            ax.text(j + (i - 1) * w, v + 0.0007, '%.3f' % v, ha='center', fontsize=8, color=P['ink'])
    ax.set_xticks(range(4)); ax.set_xticklabels(['H4(205~175 cm)', 'H3(175~97.5 cm)', 'H2(97.5~40 cm)', 'H1(40~0 cm)'], fontsize=8.5)
    ax.set_ylabel('퇴적 속도 (cm/년)'); ax.set_ylim(0, 0.047)
    ax.legend(frameon=False, fontsize=8.5, loc='upper right')
    ax.set_title('경계 연대에 따른 구역 퇴적 속도(계산 13-3)\n10.7이면 위로 갈수록 느리고, 10.304나 10.0이면 H4와 H3의 순서가 뒤집힌다', fontsize=8.5, loc='left', color=P['ink'], wrap=True)
    fig.tight_layout(); save(fig, 'rates', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        for f in (fig_ages, fig_sigma, fig_reservoir, fig_rates):
            f(mode)
    print('\n'.join(LOG))
