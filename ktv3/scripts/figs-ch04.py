# -*- coding: utf-8 -*-
"""4장 「초원의 식생 변화」 그림 생성: fig/fig-ch04-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book3): python3 scripts/figs-ch04.py
자료 그림은 논문이 적은 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다. 숫자의 출처와 계산은 ms/code/ch04/ 의 계산 4-1~4-7 로그에 있다.
그림 4-1 의 번호 점 좌표는 논문 본문에 적힌 좌표이며 지도 위 글자는 한글 지명과 번호만 쓴다. 글자 8pt 이상, 색과 흑백 두 벌.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch04'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import mapkit as K
import c14cal as C
import geopandas as gpd
from shapely.geometry import box
from pyproj import Transformer

K.use_font(8.5)
FIG = os.path.join(ROOT, 'fig')
CODE = os.path.join(ROOT, 'ms', 'code', 'ch04')
PREVIEW = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p4')
os.makedirs(PREVIEW, exist_ok=True)
LOG = []
PC = {'color': dict(ink='#1B2A33', soft='#4F6E80', grid='#D5DDE1', pos='#2F6F9A', neg='#B8622E', zero='#EFEFEF', a='#9C4F2E', b='#2F6F9A', c='#3F7F5A', d='#7A5A9A', hl='#F1D9A0'),
      'bw': dict(ink='#111111', soft='#444444', grid='#D0D0D0', pos='#444444', neg='#EEEEEE', zero='#FFFFFF', a='#111111', b='#666666', c='#999999', d='#333333', hl='#DDDDDD')}


def save(fig, name, mode):
    base = 'fig-ch04-%s-v1-%s' % (name, mode)
    fig.savefig(os.path.join(FIG, base + '.svg'), format='svg', bbox_inches='tight')
    fig.savefig(os.path.join(PREVIEW, base + '.png'), format='png', dpi=110, bbox_inches='tight')
    plt.close(fig); LOG.append(base)


def ax_style(ax, P):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'): ax.spines[s].set_color(P['soft'])
    ax.tick_params(colors=P['ink'], labelsize=8.5)


SITES = [(1, 88.3458, 48.6217), (2, 93.95, 49.98), (3, 103.6544, 44.5139), (4, 87.50, 51.50), (5, 108.1167, 52.7833), (6, 106.4667, 54.2333), (7, 80.4667, 50.40)]
LABELS = [('알타이산맥', 91.0, 50.7), ('사얀산맥', 96.5, 52.6), ('바이칼호', 108.6, 55.0), ('후브스굴호', 100.2, 50.9), ('몽골고원', 100.0, 46.6), ('항가이산맥', 98.0, 47.9), ('서시베리아 평원', 81.5, 55.4)]


def fig_map(mode):
    P = K.PAL[mode]
    bb = (76, 42, 114, 57)
    crs = '+proj=aea +lat_1=45 +lat_2=55 +lat_0=50 +lon_0=95 +datum=WGS84 +units=m'
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    xs = [tr.transform(*p) for p in [(bb[0], bb[1]), (bb[2], bb[1]), (bb[0], bb[3]), (bb[2], bb[3])]]
    x0, x1 = min(p[0] for p in xs), max(p[0] for p in xs); y0, y1 = min(p[1] for p in xs), max(p[1] for p in xs)
    fig, ax = plt.subplots(figsize=(7.2, 4.6)); ax.set_facecolor(P['ocean'])
    gpd.clip(K.read('ne_10m_land', bb), box(*bb)).to_crs(crs).plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.5)
    gpd.clip(K.read('ne_10m_lakes', bb), box(*bb)).to_crs(crs).plot(ax=ax, color=P['lake'], edgecolor=P['soft'], linewidth=0.4)
    gpd.clip(K.read('ne_10m_rivers_lake_centerlines', bb), box(*bb)).to_crs(crs).plot(ax=ax, color=P['river'], linewidth=0.6)
    for lon in range(80, 115, 5):
        xx, yy = tr.transform([lon] * 20, np.linspace(bb[1], bb[3], 20)); ax.plot(xx, yy, color=P['grid'], lw=0.4, zorder=1)
    for lat in range(44, 58, 4):
        xx, yy = tr.transform(np.linspace(bb[0], bb[2], 40), [lat] * 40); ax.plot(xx, yy, color=P['grid'], lw=0.4, zorder=1)
    for n, lo, la in SITES:
        x, y = tr.transform(lo, la)
        ax.scatter([x], [y], s=150, marker='o', facecolor='#FFFFFF', edgecolor=P['text'], linewidth=1.2, zorder=10)
        ax.text(x, y, str(n), ha='center', va='center', fontsize=8.5, fontweight='bold', color=P['text'], zorder=11)
    for s, lo, la in LABELS:
        x, y = tr.transform(lo, la); K.label(ax, x, y, s, size=8.5, color=P['soft'], ha='center', va='center', mode=mode, bold=True)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
    for s in ax.spines.values(): s.set_color(P['frame'])
    K.scalebar(ax, 500, x_frac=0.78, y_frac=0.10, mode=mode); K.north_arrow(ax, x_frac=0.95, y_frac=0.80, mode=mode)
    for lon in range(80, 115, 10):
        xx, yy = tr.transform(lon, bb[1] + 0.15); K.label(ax, xx, y0 + (y1 - y0) * 0.012, '동경 %d°' % lon, size=8, ha='center', va='bottom', color=P['soft'], mode=mode)
    for lat in (46, 50, 54):
        xx, yy = tr.transform(bb[0] + 0.2, lat); K.label(ax, x0 + (x1 - x0) * 0.01, yy, '북위 %d°' % lat, size=8, ha='left', va='bottom', color=P['soft'], mode=mode)
    save(fig, 'map', mode)


def fig_matrix(mode):
    P = PC[mode]
    d = json.load(open(os.path.join(CODE, 'calc4-5-out.json')))
    names = list(d['M']); M = np.array([d['M'][n] for n in names])
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    for i, n in enumerate(names):
        for j in range(12):
            v = M[i, j]
            col = P['pos'] if v > 0 else (P['neg'] if v < 0 else P['zero'])
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=col, edgecolor='#FFFFFF', lw=1.0, hatch=('////' if (mode == 'bw' and v < 0) else '')))
            sym = '+' if v > 0 else ('−' if v < 0 else '')
            ax.text(j + 0.5, i + 0.5, sym, ha='center', va='center', fontsize=9, fontweight='bold', color=('#FFFFFF' if (v > 0) else P['ink']))
    ax.set_xlim(0, 12); ax.set_ylim(len(names), 0)
    ax.set_xticks(np.arange(12) + 0.5); ax.set_xticklabels(['%d~%d' % (k, k + 1) for k in range(12)], fontsize=8, rotation=0)
    ax.set_yticks(np.arange(len(names)) + 0.5); ax.set_yticklabels(names, fontsize=8.5)
    ax.set_xlabel('1000년 칸 (ka, 1950 기준 천 년 전)'); ax.xaxis.tick_top(); ax.xaxis.set_label_position('top')
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    hs = [Patch(facecolor=P['pos'], label='+ 습윤·숲 확대·수위 상승으로 서술'), Patch(facecolor=P['neg'], hatch='////' if mode == 'bw' else '', edgecolor='#999999', label='− 건조·개방·수위 하강으로 서술'), Patch(facecolor=P['zero'], edgecolor='#999999', label='서술 없음 또는 상반된 부호가 섞임')]
    fig.legend(handles=hs, loc='lower center', ncol=1, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.07))
    save(fig, 'matrix', mode)


def fig_recal(mode):
    P = PC[mode]
    d = json.load(open(os.path.join(CODE, 'calc4-1-out.json')))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw=dict(width_ratios=[1.15, 1]))
    for ax in (a1, a2): ax_style(ax, P)
    x = np.array([o['paper'] for o in d]); y = np.array([o['mine'] for o in d]); ex = np.array([o['paper_err'] for o in d]); ey = np.array([o['mine_sd'] for o in d])
    a1.plot([2500, 10800], [2500, 10800], '-', color=P['soft'], lw=1.0)
    a1.errorbar(x, y, xerr=ex, yerr=ey, fmt='o', ms=5, color=P['a'], capsize=2, lw=1.0)
    a1.set_xlabel('논문의 보정 연대 (cal BP)'); a1.set_ylabel('이 책이 IntCal20 으로 보정 (cal BP)')
    a1.set_title('7개 연대: 1:1 선 위에 놓임', fontsize=8.5, loc='left', color=P['ink'])
    labs = [o['lab'] for o in d]
    a2.barh(range(len(d)), y - x, color=P['b'], edgecolor=P['ink'], lw=0.5, height=0.55)
    a2.axvline(0, color=P['ink'], lw=0.8)
    a2.set_yticks(range(len(d))); a2.set_yticklabels(labs, fontsize=8.5); a2.invert_yaxis()
    a2.set_xlabel('이 책 - 논문 (년)'); a2.set_xlim(-60, 60)
    a2.set_title('차이는 최대 15년', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'recal', mode)


def fig_hoton(mode):
    P = PC[mode]
    zones = [('H4', 205, 175, 11.5, 10.7), ('H3', 175, 97.5, 10.7, 7.9), ('H2', 97.5, 40, 7.9, 4.9), ('H1', 40, 0, 4.9, 0.0)]
    fig, ax = plt.subplots(figsize=(7.0, 3.6)); ax_style(ax, P)
    pts = [(0, 0.0)] + [(z[2], z[4]) for z in zones[::-1]]
    ages = [11.5, 10.7, 7.9, 4.9, 0.0]; deps = [205, 175, 97.5, 40, 0]
    ax.plot(ages, deps, '-o', color=P['a'], lw=1.6, ms=5, label='꽃가루 구역 경계(Hoton-2, 논문 표)')
    place = {'H4': (9.3, 200), 'H3': (10.4, 118), 'H2': (8.9, 66), 'H1': (2.5, 38)}
    for z in zones:
        ax.text(place[z[0]][0], place[z[0]][1], '%s\n%.4f cm/년' % (z[0], (z[1] - z[2]) / ((z[3] - z[4]) * 1000)), ha='center', va='center', fontsize=8.5, color=P['ink'])
    ax.errorbar([10.304], [174.75], xerr=[[0.056], [0.056]], fmt='s', ms=7, mfc='#FFFFFF', mec=P['b'], ecolor=P['b'], capsize=3, label='Hoton-2 방사성탄소 10,304 ± 56 cal BP')
    ax.annotate('경계(175 cm)는 이 점보다\n약 400년 오래 놓임', xy=(10.25, 176), xytext=(6.4, 150), fontsize=8.5, color=P['ink'], arrowprops=dict(arrowstyle='->', color=P['soft'], lw=1.0))
    ax.set_xlim(12, 0); ax.set_ylim(215, -8)
    ax.set_xlabel('연대 (ka, 1950 기준)'); ax.set_ylabel('깊이 (cm)')
    ax.legend(frameon=False, fontsize=8.5, loc='lower right')
    ax.set_title('Rudaya 등(2009) 표의 숫자를 다시 그림(계산 4-2)', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'hoton', mode)


def fig_kotokel(mode):
    P = PC[mode]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.0))
    spec = [('7월 평균기온 (°C)', (12, 12), (17, 18)), ('1월 평균기온 (°C)', (-38, -38), (-19, -19)), ('연강수량 (mm)', (270, 300), (500, 550))]
    for ax, (t, cold, mx) in zip(axs, spec):
        ax_style(ax, P)
        for i, (v, col, h) in enumerate(((cold, P['b'], '////'), (mx, P['a'], ''))):
            lo, hi = v
            ax.bar(i, (lo + hi) / 2, yerr=(hi - lo) / 2 if hi > lo else None, color=col, edgecolor=P['ink'], width=0.6, hatch=h if mode == 'bw' else '', capsize=3, lw=0.6)
            top = hi + (hi - lo) / 2 * 0 if (lo + hi) / 2 >= 0 else lo
            ax.annotate(('%g~%g' % (lo, hi)) if hi > lo else '%g' % lo, (i, top), xytext=(0, 4 if (lo + hi) / 2 >= 0 else -4), textcoords='offset points', ha='center', va='bottom' if (lo + hi) / 2 >= 0 else 'top', fontsize=8.5, color=P['ink'])
        ax.set_xticks([0, 1]); ax.set_xticklabels(['차가운\n시기', '타이가\n최대기'], fontsize=8.5)
        ax.set_title(t, fontsize=8.5, color=P['ink'])
        ax.axhline(0, color=P['soft'], lw=0.6)
        ax.margins(y=0.2)
    fig.suptitle('Tarasov 등(2009) 코토켈 호수 꽃가루 복원값(초록의 숫자, 계산 4-4)', fontsize=8.5, x=0.01, ha='left', color=P['ink'])
    fig.tight_layout(rect=(0, 0, 1, 0.94)); save(fig, 'kotokel', mode)


def fig_hulun(mode):
    P = PC[mode]
    W = [('11~8 ka\n건조 스텝', 11000, 8000, -1), ('8~6.4\n초본·자작 확대', 8000, 6400, 1), ('6.4~4.4\n서늘, 건조', 6400, 4400, -1), ('4.4~3.35\n명아주과(극도 건조)', 4400, 3350, -1), ('3.35~2.05\n쑥 회복', 3350, 2050, 1), ('2.05~1.0\n쑥 감소, 소나무', 2050, 1000, -1), ('최근 1천 년\n사람 활동', 1000, 0, 0)]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); ax_style(ax, P)
    for n, a, b, s in W:
        col = P['pos'] if s > 0 else (P['neg'] if s < 0 else P['zero'])
        ax.barh(0, (a - b) / 1000, left=b / 1000, height=0.5, color=col, edgecolor=P['ink'], lw=0.6, hatch='////' if (mode == 'bw' and s < 0) else '')
        ax.text((a + b) / 2000, 0.45, n, ha='center', va='bottom', fontsize=8, color=P['ink'])
    ax.set_xlim(11.2, -0.2); ax.set_ylim(-0.4, 1.5); ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('cal ka BP')
    ax.set_title('Wen 등(2010) 훌룬 호수 꽃가루 구간(초록의 숫자; 7칸의 합 = 11,000년, 계산 4-4)', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'hulun', mode)


def fig_signal(mode):
    P = PC[mode]
    fig, ax = plt.subplots(figsize=(7.0, 3.0)); ax_style(ax, P)
    rows = [('논문의 복원 범위(85~223 mm)', 85, 223, P['b']), ('두 시료를 95%로 가르는 최소 차이\n(시료별 오차 41.7~51.7 mm)', 0, 0, None), ('오차만으로 생기는 시료 75개의\n최대-최소 차(95% 구간, 이 책의 시연)', 160, 283, P['a'])]
    ax.barh(0, 223 - 85, left=85, height=0.5, color=P['b'], edgecolor=P['ink'], lw=0.6)
    ax.barh(2, 283 - 160, left=160, height=0.5, color=P['a'], edgecolor=P['ink'], lw=0.6, hatch='////' if mode == 'bw' else '')
    ax.barh(1, 143 - 116, left=116, height=0.5, color=P['hl'], edgecolor=P['ink'], lw=0.6)
    ax.text(223 + 4, 0, '폭 138 mm', va='center', fontsize=8.5, color=P['ink'])
    ax.text(143 + 4, 1, '116~143 mm', va='center', fontsize=8.5, color=P['ink'])
    ax.text(283 + 4, 2, '160~283 mm', va='center', fontsize=8.5, color=P['ink'])
    ax.set_yticks([0, 1, 2]); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5); ax.invert_yaxis()
    ax.set_xlim(0, 340); ax.set_xlabel('mm')
    ax.set_title('Tian 등(2014) 바얀 누르 강수 복원: 범위와 오차의 크기를 견줌(계산 4-6)', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'signal', mode)


def fig_tel(mode):
    P = PC[mode]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.4)); [ax_style(a, P) for a in (a1, a2)]
    # Tel 2001-2004
    yrs = [500, 1000, 1820, 2004]; dep = [173, 115, 20, 0]
    a1.plot(yrs, dep, '-o', color=P['a'], lw=1.6, ms=5, label='꽃가루 구역 경계(논문)')
    sm = C.summary(895, 45); sw = C.summary(1540, 25)
    a1.errorbar([1950 - sm['mean'], 1950 - sw['mean']], [96.5, 173], xerr=[sm['sd'], sw['sd']], fmt='s', ms=6, mfc='#FFFFFF', mec=P['b'], ecolor=P['b'], capsize=3, label='14C 두 점(이 책 보정, ±1 sd)')
    a1.set_ylim(185, -5); a1.set_xlim(400, 2100); a1.set_xlabel('연대 (AD)'); a1.set_ylabel('깊이 (cm)')
    a1.set_title('Tel 2001-2004: 평균 1.15 mm/년', fontsize=8.5, loc='left', color=P['ink']); a1.legend(frameon=False, fontsize=8, loc='lower right')
    # Tel 2006
    a2.plot([1120, 2006], [40, 0], '-o', color=P['a'], lw=1.6, ms=5, label='PZ06-V 경계(논문)')
    a2.errorbar([1950 - 800], [38.5], xerr=[[10], [10]], fmt='s', ms=6, mfc='#FFFFFF', mec=P['b'], ecolor=P['b'], capsize=3, label='표지층 0.79~0.81 ka(38~39 cm)')
    a2.set_ylim(48, -3); a2.set_xlim(1000, 2050); a2.set_xlabel('연대 (AD)'); a2.set_title('Tel 2006: 평균 0.45 mm/년', fontsize=8.5, loc='left', color=P['ink']); a2.legend(frameon=False, fontsize=8, loc='lower right')
    fig.suptitle('Rudaya 등(2016) 텔레츠코예 호수 두 코어의 연대-깊이(계산 4-7)', fontsize=8.5, x=0.01, ha='left', color=P['ink'])
    fig.tight_layout(rect=(0, 0, 1, 0.94)); save(fig, 'tel', mode)


def fig_kulunda(mode):
    P = PC[mode]
    d = np.array([0.18, 1.76, 2.56, 3.46]); a = np.array([0.52, 2.31, 3.05, 4.03])
    fig, ax = plt.subplots(figsize=(7.0, 3.3)); ax_style(ax, P)
    ax.plot(a, d, '-o', color=P['a'], lw=1.6, ms=6, label='표 1 의 4점')
    rl = (d[3] - d[2]) / (a[3] - a[2]); ab = a[3] + (4.04 - d[3]) / rl
    ax.plot([a[3], ab], [d[3], 4.04], '--', color=P['a'], lw=1.4, label='외삽: 코어 바닥 %.2f ka' % ab)
    ax.axvline(4.4, color=P['b'], lw=1.2, ls=':'); ax.text(4.4 + 0.04, 2.6, '논문 본문의\n약 4.4 ka', fontsize=8.5, color=P['b'], va='top')
    for n, a0, a1 in [('PZ I', 4.4, 3.75), ('PZ II', 3.75, 2.66), ('PZ III', 2.66, 1.37), ('PZ IV', 1.37, 0.09)]:
        ax.axvspan(a1, a0, ymin=0.0, ymax=0.04, color=P['soft'], alpha=0.6 if n in ('PZ I', 'PZ III') else 0.3)
        ax.text((a0 + a1) / 2, 4.2, n, ha='center', va='bottom', fontsize=8, color=P['ink'])
    ax.set_xlim(0, 5.0); ax.set_ylim(4.35, -0.05)
    ax.set_xlabel('연대 (ka)'); ax.set_ylabel('깊이 (m)'); ax.legend(frameon=False, fontsize=8.5, loc='upper center', bbox_to_anchor=(0.62, 0.98))
    ax.set_title('Rudaya 등(2012) 쿨룬다 빅 야로보예 호수: 표 1 의 4점과 구역 연대(계산 4-3)', fontsize=8.5, loc='left', color=P['ink'])
    fig.tight_layout(); save(fig, 'kulunda', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        for f in (fig_map, fig_matrix, fig_recal, fig_hoton, fig_kotokel, fig_hulun, fig_signal, fig_tel, fig_kulunda):
            f(mode)
    print('\n'.join(LOG))
