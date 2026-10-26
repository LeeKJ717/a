# -*- coding: utf-8 -*-
"""3장 「알타이와 시베리아의 빙하와 동토」 그림 생성: fig/fig-ch03-*-v1-{color,bw}.svg
쓰는 법(작업 폴더 /home/claude/book3): python3 scripts/figs-ch03.py
자료 그림은 모두 논문이 적은 숫자를 다시 그린 것이며 측정 자료 그 자체가 아니다. 숫자의 출처와 계산은 ms/code/ch03/ 의 계산 3-1~3-7 로그에 있다.
지도(그림 3-1)는 Natural Earth 10m(geodata/)이고 번호 점의 좌표는 논문 본문에 적힌 좌표이다. 지도 위 글자는 한글 지명과 번호만 쓴다.
글자는 8pt 이상. 같은 그림을 색(color)과 흑백(bw) 두 벌로 만든다.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch03'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
import mapkit as K
import c14cal as C
import geopandas as gpd
from shapely.geometry import box
from pyproj import Transformer

K.use_font(8.5)
FIG = os.path.join(ROOT, 'fig')
CODE = os.path.join(ROOT, 'ms', 'code', 'ch03')
PREVIEW = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p3')
os.makedirs(PREVIEW, exist_ok=True)
LOG = []

PC = {'color': dict(ink='#1B2A33', soft='#4F6E80', grid='#D5DDE1', a='#9C4F2E', b='#2F6F9A', c='#3F7F5A', d='#7A5A9A', e='#B8892B', f='#5B7F95', g='#8A8A3A', hl='#F1D9A0', bg='#FFFFFF'),
      'bw': dict(ink='#111111', soft='#444444', grid='#D0D0D0', a='#111111', b='#555555', c='#888888', d='#333333', e='#AAAAAA', f='#666666', g='#BBBBBB', hl='#DDDDDD', bg='#FFFFFF')}
HAT = {'a': '', 'b': '////', 'c': '....', 'd': 'xxxx', 'e': '\\\\\\\\', 'f': '----', 'g': '++'}


def save(fig, name, mode):
    base = 'fig-ch03-%s-v1-%s' % (name, mode)
    fig.savefig(os.path.join(FIG, base + '.svg'), format='svg', bbox_inches='tight')
    fig.savefig(os.path.join(PREVIEW, base + '.png'), format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    LOG.append(base)


def ax_style(ax, P):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(P['soft'])
    ax.tick_params(colors=P['ink'], labelsize=8.5)
    ax.xaxis.label.set_color(P['ink']); ax.yaxis.label.set_color(P['ink'])


# ---------------------------------------------------------------- 그림 3-1 지도
SITES = [  # 번호, 경도, 위도 (논문 본문 좌표)
    (1, 86.55, 49.80), (2, 87.50, 51.50), (3, 88.3458, 48.6217), (4, 93.95, 49.98),
    (5, 108.1167, 52.7833), (6, 106.4667, 54.2333), (7, 103.6544, 44.5139)]
LABELS = [('알타이산맥', 90.8, 50.6, 0), ('사얀산맥', 95.5, 52.3, 0), ('바이칼호', 108.4, 54.6, 0), ('후브스굴호', 100.2, 50.9, 0), ('몽골고원', 100.0, 46.6, 0), ('항가이산맥', 98.0, 47.9, 0)]


def fig_map(mode):
    P = K.PAL[mode]; Q = PC[mode]
    bb = (78, 42, 114, 57)
    crs = '+proj=aea +lat_1=45 +lat_2=55 +lat_0=50 +lon_0=96 +datum=WGS84 +units=m'
    tr = Transformer.from_crs(4326, crs, always_xy=True)
    xs = [tr.transform(*p) for p in [(bb[0], bb[1]), (bb[2], bb[1]), (bb[0], bb[3]), (bb[2], bb[3])]]
    x0, x1 = min(p[0] for p in xs), max(p[0] for p in xs); y0, y1 = min(p[1] for p in xs), max(p[1] for p in xs)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_facecolor(P['ocean'])
    land = gpd.clip(K.read('ne_10m_land', bb), box(*bb)).to_crs(crs)
    land.plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.5)
    lakes = gpd.clip(K.read('ne_10m_lakes', bb), box(*bb)).to_crs(crs)
    lakes.plot(ax=ax, color=P['lake'], edgecolor=P['soft'], linewidth=0.4)
    riv = gpd.clip(K.read('ne_10m_rivers_lake_centerlines', bb), box(*bb)).to_crs(crs)
    riv.plot(ax=ax, color=P['river'], linewidth=0.6)
    for lon in range(80, 115, 5):
        xx, yy = tr.transform([lon] * 20, np.linspace(bb[1], bb[3], 20)); ax.plot(xx, yy, color=P['grid'], lw=0.4, zorder=1)
    for lat in range(44, 58, 4):
        xx, yy = tr.transform(np.linspace(bb[0], bb[2], 40), [lat] * 40); ax.plot(xx, yy, color=P['grid'], lw=0.4, zorder=1)
    for n, lo, la in SITES:
        x, y = tr.transform(lo, la)
        ax.scatter([x], [y], s=150, marker='o', facecolor='#FFFFFF', edgecolor=P['text'], linewidth=1.2, zorder=10)
        ax.text(x, y, str(n), ha='center', va='center', fontsize=8.5, fontweight='bold', color=P['text'], zorder=11)
    for s, lo, la, rot in LABELS:
        x, y = tr.transform(lo, la)
        K.label(ax, x, y, s, size=8.5, color=P['soft'], ha='center', va='center', mode=mode, bold=True)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(P['frame'])
    ax.set_xlabel(''); ax.set_ylabel('')
    K.scalebar(ax, 500, x_frac=0.78, y_frac=0.10, mode=mode)
    K.north_arrow(ax, x_frac=0.95, y_frac=0.80, mode=mode)
    # 경위도 눈금 글자
    for lon in range(80, 115, 10):
        xx, yy = tr.transform(lon, bb[1] + 0.15); K.label(ax, xx, y0 + (y1 - y0) * 0.012, '동경 %d°' % lon, size=8, ha='center', va='bottom', color=P['soft'], mode=mode)
    for lat in (46, 50, 54):
        xx, yy = tr.transform(bb[0] + 0.2, lat); K.label(ax, x0 + (x1 - x0) * 0.01, yy, '북위 %d°' % lat, size=8, ha='left', va='bottom', color=P['soft'], mode=mode)
    save(fig, 'map', mode)


# ---------------------------------------------------------------- 그림 3-2 벨루하 깊이-연대
def fig_belukha(mode):
    P = PC[mode]
    d = json.load(open(os.path.join(CODE, 'calc3-1-out.json')))
    H, A0, DR = d['H'], d['A0'], d['DRILL']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.9), gridspec_kw=dict(width_ratios=[1, 1.15]))
    z = np.linspace(0, 125, 300)
    for ax in (a1, a2):
        ax_style(ax, P)
        ax.invert_yaxis()
    # 왼쪽: 표지 층 (0~1100년)
    zz = np.linspace(0, 120, 300)
    for a, ls, lab in ((A0, '-', 'Nye, a=0.34'), (d['a_fit'], '--', 'Nye, a=%.3f(표지에 맞춤)' % d['a_fit'])):
        t = -(H / a) * np.log(1 - zz / H)
        a1.plot(t, zz, ls, color=P['b'] if a == A0 else P['a'], lw=1.4, label=lab)
    for n, zk, y in d['marks']:
        a1.scatter([DR - y], [zk], s=34, marker='o', facecolor=P['ink'], edgecolor='#FFFFFF', zorder=5)
    a1.set_xlim(0, 1100); a1.set_xlabel('시추(2003)로부터 경과 연수(년)'); a1.set_ylabel('깊이 (m 물당량)')
    a1.set_title('표지 층 7개와 단순 Nye 모형', fontsize=8.5, color=P['ink'], loc='left')
    a1.legend(frameon=False, fontsize=8, loc='upper right')
    a1.text(70, 6, '삼중수소 1958, 1963', fontsize=8, color=P['ink'], ha='left', va='center')
    a1.text(215, 44, '1842 먼지, 탐보라 1815', fontsize=8, color=P['ink'], ha='left', va='center')
    a1.text(1090, 112, '창바이산\n약 1000 AD', fontsize=8, color=P['ink'], ha='right', va='bottom')
    # 오른쪽: 방사성탄소 점
    for n, zk, y in d['marks']:
        a2.scatter([DR - y], [zk], s=24, marker='o', facecolor=P['ink'], edgecolor='#FFFFFF', zorder=5)
    for zk, y, s in d['rc']:
        a2.errorbar([DR - y], [zk], xerr=[[s], [s]], fmt='s', ms=6, color=P['a'], mfc='#FFFFFF', mec=P['a'], capsize=3, lw=1.2, zorder=6)
    tt = -(H / A0) * np.log(1 - np.linspace(0, 143, 400) / H)
    a2.plot(tt, np.linspace(0, 143, 400), '-', color=P['b'], lw=1.2)
    a2.set_xlim(-300, 12000); a2.set_xlabel('시추(2003)로부터 경과 연수(년)')
    a2.set_title('방사성탄소 4점(사각형, 가로 막대는 논문의 오차)', fontsize=8.5, color=P['ink'], loc='left')
    a2.text(11800, 95, 'Nye 모형(a=0.34)은 깊이 142.8 m 에서도\n약 %d년만 예측(계산 3-1)' % round(-(H / A0) * np.log(1 - 142.8 / H)), fontsize=8, ha='right', va='center', color=P['b'])
    fig.suptitle('논문의 숫자를 다시 그림: Aizen 등(2016)의 벨루하 빙핵 깊이-연대', fontsize=8.5, color=P['ink'], x=0.01, ha='left', y=1.0)
    fig.tight_layout()
    save(fig, 'belukha', mode)


# ---------------------------------------------------------------- 그림 3-3 시간 구간
GRP = {'A': ('알타이 빙하 단계(Agatova)', 'a'), 'B': ('벨루하 빙핵 기후 구간(Aizen)', 'b'), 'C': ('텔레츠코예 꽃가루(Rudaya)', 'c'),
       'D': ('야쿠티아 열카르스트(Ulrich)', 'd'), 'E': ('호수 기록(Tarasov, Prokopenko)', 'e'), 'F': ('몽골 빙하(Batbaatar, Khandsuren)', 'f'), 'G': ('최근 2천 년 전진(Büntgen, Nazarov)', 'g')}


def fig_timeline(mode):
    P = PC[mode]
    iv = json.load(open(os.path.join(CODE, 'calc3-5-intervals.json')))
    names = list(iv)
    n = len(names)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 6.6), sharey=True, gridspec_kw=dict(width_ratios=[2.6, 1.5], wspace=0.04))
    for ax, (lo, hi) in ((a1, (2.0, 13.0)), (a2, (0.0, 2.0))):
        ax_style(ax, P)
        for i, k in enumerate(names):
            old, young = iv[k]
            g = k[0]
            col = P[GRP[g][1]]
            xa, xb = max(young / 1000, lo), min(old / 1000, hi)
            if xb > xa:
                ax.barh(i, xb - xa, left=xa, height=0.62, color=col, edgecolor=P['ink'], hatch=HAT[GRP[g][1]] if mode == 'bw' else '', linewidth=0.5)
        ax.set_xlim(hi, lo)
        ax.grid(axis='x', color=P['grid'], lw=0.5)
        ax.set_axisbelow(True)
    a1.set_yticks(range(n)); a1.set_yticklabels(names, fontsize=8.5)
    a1.invert_yaxis()
    a2.spines['left'].set_visible(False); a2.tick_params(axis='y', left=False)
    a1.set_xlabel('13~2 ka (천 년 전, 1950 기준)'); a2.set_xlabel('2~0 ka')
    a1.set_xticks([13, 12, 10, 8, 6, 4]); a2.set_xticks([2, 1.5, 1, 0.5, 0])
    handles = [Patch(facecolor=P[v[1]], edgecolor=P['ink'], hatch=HAT[v[1]] if mode == 'bw' else '', label=v[0]) for v in GRP.values()]
    fig.legend(handles=handles, loc='lower center', ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.095))
    fig.suptitle('논문이 적은 시기 구간을 한 시간축에 놓음(구간 표: 계산 3-5)', fontsize=8.5, color=P['ink'], x=0.01, ha='left', y=0.93)
    save(fig, 'timeline', mode)


# ---------------------------------------------------------------- 그림 3-4 보정
def fig_calib(mode):
    P = PC[mode]
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    ax_style(ax, P)
    for (a, e, ls, lab, col) in ((4550, 350, '-', '4550 ± 350 BP (Nazarov 등이 재인용한 값)', P['a']), (4550, 50, '--', '같은 값, 오차 50년으로 가정한 비교', P['b'])):
        t, p = C.calibrate(a, e)
        m = (t > 3500) & (t < 7000)
        ax.plot(t[m], p[m] * 1000, ls, color=col, lw=1.6, label=lab)
    ax.axvspan(4200, 4900, color=P['hl'], alpha=0.8, lw=0)
    ax.text(4550, ax.get_ylim()[1] * 0.97, '아크켐 단계\n4.9~4.2 ka\n(Agatova 등 2012)', fontsize=8.5, ha='center', va='top', color=P['ink'])
    ax.set_xlim(7000, 3500); ax.set_xlabel('보정 연대 (cal BP)'); ax.set_ylabel('확률 밀도(‰ / 년)')
    ax.legend(frameon=False, fontsize=8.5, loc='upper left')
    ax.set_title('IntCal20 으로 이 책이 보정(계산 3-2): 창에 든 확률은 약 25%', fontsize=8.5, color=P['ink'], loc='left')
    fig.tight_layout(); save(fig, 'calib', mode)


# ---------------------------------------------------------------- 그림 3-5 빙하 면적
def fig_area(mode):
    P = PC[mode]
    rows = [('동사얀 피크 토포그라포프 빙하 7개\n(8.1 → 3.8 km², 소빙기~2010)', (8.1 - 3.8) / 8.1 * 100, 53, 160),
            ('동남 시베리아 세 산맥 평균\n(소빙기~현재 약 160년)', 59, 59, 160),
            ('코다르 무빙하파편 면적\n(소빙기~2006/11)', 62, 62, 160),
            ('코다르 1953/63~2001/02\n(논문 23%, 연 0.55%)', 23, 23, 23 / 0.55)]
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax_style(ax, P)
    y = np.arange(len(rows))
    cols = [P['b'], P['a'], P['a'], P['c']]
    for i, (lab, v, pv, yrs) in enumerate(rows):
        ax.barh(i, v, height=0.55, color=cols[i], edgecolor=P['ink'], hatch=['', '////', '////', '....'][i] if mode == 'bw' else '', lw=0.5)
        ax.text(v + 1.2, i, '%.0f%% (연 %.2f%%)' % (v, v / yrs), va='center', fontsize=8.5, color=P['ink'])
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5); ax.invert_yaxis()
    ax.set_xlim(0, 85); ax.set_xlabel('면적 감소(%)')
    ax.set_title('논문이 적은 감소 비율을 다시 그림(계산 3-3); 연율은 이 책이 나눈 값', fontsize=8.5, color=P['ink'], loc='left')
    fig.tight_layout(); save(fig, 'area', mode)


# ---------------------------------------------------------------- 그림 3-6 퇴적 속도
def fig_rates(mode):
    P = PC[mode]
    d = json.load(open(os.path.join(CODE, 'calc3-7-out.json')))
    lab = {'KB7': 'KB7 (6.6~5.8 ka)\n집중기 퇴적', 'KB1': 'KB1 (3.3~1.8 ka)', 'YU-L7': 'YU-L7 알라스 호수\n(13.8~3.7 ka)', 'YU3': 'YU3 (34.9~4.0 ka)\n중간 틈 포함'}
    order = ['KB7', 'KB1', 'YU-L7', 'YU3']
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    ax_style(ax, P)
    for i, k in enumerate(order):
        lo, md, hi = d[k]
        ax.barh(i, md, height=0.55, color=[P['d'], P['c'], P['b'], P['e']][i], edgecolor=P['ink'], hatch=['xxxx', '....', '////', '\\\\\\\\'][i] if mode == 'bw' else '', lw=0.5)
        ax.plot([lo, hi], [i, i], color=P['ink'], lw=1.4)
        ax.text(hi * 1.15, i, ('%.3f mm/년 (95%%: %.3f~%.3f)' if md < 0.1 else '%.2f mm/년 (95%%: %.2f~%.2f)') % (md, lo, hi), va='center', fontsize=8.5, color=P['ink'])
    ax.set_xscale('log'); ax.set_xlim(0.02, 40)
    ax.set_yticks(range(len(order))); ax.set_yticklabels([lab[k] for k in order], fontsize=8.5); ax.invert_yaxis()
    ax.set_xlabel('평균 퇴적 속도 (mm/년, 로그 눈금)')
    ax.set_title('Ulrich 등(2019, 2021)의 연대로 이 책이 나눈 값(계산 3-7)', fontsize=8.5, color=P['ink'], loc='left')
    fig.tight_layout(); save(fig, 'rates', mode)


# ---------------------------------------------------------------- 그림 3-7 비율의 분포
def fig_ratio(mode):
    P = PC[mode]
    rng = np.random.default_rng(3104)
    N = 400000
    c = rng.normal(159, 24, N); y = rng.normal(100, 34, N)
    r = c[y > 0] / y[y > 0]
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax_style(ax, P)
    ax.hist(r[(r > 0) & (r < 6)], bins=120, color=P['b'], edgecolor='none', density=True)
    for q, ls in ((2.5, ':'), (50, '-'), (97.5, ':')):
        v = np.percentile(r, q)
        ax.axvline(v, color=P['ink'], ls=ls, lw=1.2)
        ax.text(v - 0.05 if q == 2.5 else v + 0.05, ax.get_ylim()[1] * 0.95, '%g%% = %.2f' % (q, v), fontsize=8.5, color=P['ink'], va='top', ha='right' if q == 2.5 else 'left')
    ax.axvline(1.0, color=P['a'], lw=1.4)
    ax.annotate('비율 1', xy=(0.99, ax.get_ylim()[1] * 0.40), xytext=(0.30, ax.get_ylim()[1] * 0.40), fontsize=8.5, color=P['a'], ha='left', va='center', arrowprops=dict(arrowstyle='->', color=P['a'], lw=1.0))
    ax.set_xlabel('홀로세 탄소 ÷ yedoma 방출 탄소 (두 값을 독립 정규분포로 가정)'); ax.set_ylabel('확률 밀도')
    ax.set_title('논문의 159 ± 24, 100 ± 34 Pg 로 본 비율 1.6 의 불확실성(계산 3-4)', fontsize=8.5, color=P['ink'], loc='left')
    fig.tight_layout(); save(fig, 'ratio', mode)


if __name__ == '__main__':
    for mode in ('color', 'bw'):
        for f in (fig_map, fig_belukha, fig_timeline, fig_calib, fig_area, fig_rates, fig_ratio):
            f(mode)
    print('\n'.join(LOG))
