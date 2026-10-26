# -*- coding: utf-8 -*-
"""12장 그림. 자료 그림은 논문에서 옮긴 숫자(또는 계산 12-x 로그)를 다시 그린 것이다.
실행: python3 scripts/figs-ch12.py → fig/fig-ch12-*-v1-{color,bw}.svg
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
os.environ['GEODIR'] = os.path.join(ROOT, 'geodata')
sys.path.insert(0, HERE)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Patch
from scipy import stats
import mapkit
mapkit.use_font(8.5)
FIG = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR')
LOG = os.path.join(ROOT, 'ms', 'code', 'ch12', 'calc-ch12-v1.log')
MM = 1 / 25.4
PAL = {
 'color': dict(bg='#FFFFFF', ink='#1B2A33', soft='#5B6B75', grid='#D5DCE0', wet='#4C7FA3', dry='#C27A3A', adv='#4A4F55', ret='#B9C0C6', frc='#8E7DB0', span='#FFFFFF', land='#F1EBDD', sea='#E3EEF3', coast='#7D7255', box='#2F6F9A', hot='#B2512E'),
 'bw': dict(bg='#FFFFFF', ink='#111111', soft='#444444', grid='#CFCFCF', wet='#BDBDBD', dry='#555555', adv='#222222', ret='#E2E2E2', frc='#9A9A9A', span='#FFFFFF', land='#F4F4F4', sea='#E6E6E6', coast='#444444', box='#222222', hot='#111111'),
}
HATCH = {'wet': '', 'dry': '', 'adv': '', 'ret': '', 'frc': '//', 'span': ''}
def save(fig, name, mode):
    p = os.path.join(FIG, 'fig-ch12-%s-v1-%s.svg' % (name, mode))
    fig.savefig(p, format='svg')
    if PREV: fig.savefig(os.path.join(PREV, 'ch12-%s-%s.png' % (name, mode)), dpi=110)
    plt.close(fig)
def halo(): return [pe.withStroke(linewidth=2, foreground='white')]

# ---------------------------------------------------------------- 그림 1
ROWS = [
 ('알타이 빙하·나무 피해\n(Solomina 2016)', [(700, 1199, 'ret'), (1200, 1260, 'adv'), (1320, 1380, 'adv'), (1440, 1510, 'adv'), (1640, 1740, 'adv')]),
 ('텔레츠코예호 꽃가루\n(Andreev 2007)', [(1050, 1100, 'wet'), (1100, 1200, 'dry'), (1200, 1410, 'wet'), (1410, 1560, 'dry'), (1560, 1820, 'dry')]),
 ('텔멘호 수문\n(Struck 2022)', [(700, 1300, 'dry'), (1300, 2000, 'wet')]),
 ('몽골 나이테 가뭄지수\n(Pederson 2014)', [(1115, 1139, 'dry'), (1180, 1190, 'dry'), (1211, 1225, 'wet')]),
 ('톈산 하천 유량\n(Chen 2022)', [(1225, 1239, 'wet'), (1240, 1251, 'dry'), (1252, 1260, 'wet'), (1361, 1400, 'wet'), (1437, 1467, 'wet'), (1494, 1511, 'dry'), (1678, 1692, 'dry'), (1693, 1705, 'wet'), (1731, 1759, 'wet'), (1758, 1790, 'dry'), (1961, 1996, 'dry')]),
 ('화산·태양 저하 구간\n(PAGES 2k 2013)', [(1251, 1310, 'frc'), (1431, 1520, 'frc'), (1581, 1610, 'frc'), (1641, 1700, 'frc'), (1791, 1820, 'frc')]),
 ('벨루하 빙핵 기록 범위\n(Eichler 2009)', [(1250, 2001, 'span')]),
]
def fig1(mode):
    C = PAL[mode]
    fig = plt.figure(figsize=(172 * MM, 108 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.27, 0.27, 0.71, 0.72])
    ax.set_xlim(700, 2020); ax.set_ylim(len(ROWS) - 0.4, -0.6)
    ax.set_yticks(range(len(ROWS))); ax.set_yticklabels([r[0] for r in ROWS], fontsize=8.5); ax.tick_params(axis='y', length=0)
    ax.set_xticks(range(800, 2001, 200)); ax.tick_params(axis='x', labelsize=8.5)
    ax.set_xlabel('서기(년)', fontsize=8.5)
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
    for x in range(800, 2001, 200): ax.axvline(x, color=C['grid'], lw=0.5, zorder=0)
    for i, (_, segs) in enumerate(ROWS):
        for a, b, k in segs:
            ax.add_patch(Rectangle((a, i - 0.3), b - a, 0.6, facecolor=C[k], edgecolor=C['ink'], lw=0.5, hatch=HATCH[k], zorder=2))
    ax.axvspan(950, 1250, color=C['grid'], alpha=0.35, lw=0, zorder=0)
    ax.axvspan(1250, 1850, color=C['grid'], alpha=0.18, lw=0, zorder=0)
    ax.text(1100, -0.45, '중세 온난기 약 950~1250', fontsize=8, ha='center', va='center', color=C['ink'])
    ax.text(1550, -0.45, '소빙기 약 1250~1850', fontsize=8, ha='center', va='center', color=C['ink'])
    h = [Patch(fc=C['wet'], ec=C['ink'], lw=0.5, label='습윤·높은 유량·온난 습윤'), Patch(fc=C['dry'], ec=C['ink'], lw=0.5, label='건조·낮은 유량·냉건'),
         Patch(fc=C['adv'], ec=C['ink'], lw=0.5, label='빙하 나무 피해 군집(전진)'), Patch(fc=C['ret'], ec=C['ink'], lw=0.5, label='빙하 후퇴(추정)'),
         Patch(fc=C['frc'], ec=C['ink'], lw=0.5, hatch='//', label='화산·태양 저하 구간'), Patch(fc='white', ec=C['ink'], lw=0.5, label='기록이 덮는 기간')]
    fig.legend(handles=h, loc='lower left', bbox_to_anchor=(0.02, 0.0), ncol=3, fontsize=8, frameon=False, columnspacing=1.2)
    fig.text(0.02, 0.135, '논문의 연대를 다시 그린 것. 중세 온난기와 소빙기의 경계는 Solomina 등(2016)의 정의.', fontsize=8, color=C['soft'])
    fig.text(0.02, 0.105, '텔멘호 "1300년 이후"는 2000년까지 그렸다. 경계는 논문이 "약"으로 적은 값이다.', fontsize=8, color=C['soft'])
    save(fig, 'timeline', mode)

# ---------------------------------------------------------------- 그림 2
def fig2(mode):
    C = PAL[mode]
    N, K, n = 2370, 64, 20
    x = np.arange(0, 14)
    pm = stats.hypergeom.pmf(x, N, K, n)
    fig = plt.figure(figsize=(150 * MM, 80 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.12, 0.22, 0.85, 0.70])
    cols = [C['wet'] if i < 13 else C['hot'] for i in x]
    ax.bar(x, pm, color=cols, edgecolor=C['ink'], lw=0.5, hatch='')
    ax.set_yscale('log'); ax.set_ylim(1e-18, 3)
    ax.set_xticks(x); ax.tick_params(labelsize=8.5)
    ax.set_xlabel('가장 추운 여름 20개 가운데 536~599년 창 안에 드는 개수', fontsize=8.5)
    ax.set_ylabel('확률(독립 가정, 로그 눈금)', fontsize=8.5)
    ax.annotate('관측 13개\nP(X≥13) = %.1e' % stats.hypergeom.sf(12, N, K, n), xy=(13, pm[13]), xytext=(9.0, 1e-6), fontsize=8.5, color=C['ink'], arrowprops=dict(arrowstyle='->', color=C['ink'], lw=0.7))
    ax.text(3.3, 0.2, '무작위 기대값 %.2f개' % (n * K / N), fontsize=8.5, color=C['ink'])
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.yaxis.grid(True, color=C['grid'], lw=0.5); ax.set_axisbelow(True)
    fig.text(0.02, 0.02, '계산 12-1. N=2370년, 창 64년, 뽑은 해 20개의 초기하 분포. 관측 13개는 Büntgen 등(2016) 서술.', fontsize=8, color=C['soft'])
    save(fig, 'hyper', mode)

# ---------------------------------------------------------------- 그림 3
def parse_ped():
    t = open(LOG, encoding='utf-8').read()
    return [(float(a), float(b), float(c)) for a, b, c in re.findall(r'rho=([0-9.]+) : 정해진 한 시작점에서 15년 평균>=0\.600 비율 ([0-9.]+) \| 1112년 어디선가 최대>=0\.600 비율 ([0-9.]+)', t)]
def fig3(mode):
    C = PAL[mode]
    r = parse_ped()
    fig = plt.figure(figsize=(150 * MM, 80 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.11, 0.24, 0.86, 0.68])
    x = np.arange(len(r)); w = 0.36
    b1 = ax.bar(x - w / 2, [q[1] for q in r], w, color=C['wet'], edgecolor=C['ink'], lw=0.5, hatch='' if mode == 'color' else '//', label='정해 둔 한 시작점의 15년 평균이 0.600 이상')
    b2 = ax.bar(x + w / 2, [q[2] for q in r], w, color=C['hot'] if mode == 'color' else '#222222', edgecolor=C['ink'], lw=0.5, hatch='' if mode == 'color' else '..', label='1112년 기록 어디선가 15년 평균 최대가 0.600 이상')
    for bs in (b1, b2):
        for q in bs: ax.text(q.get_x() + q.get_width() / 2, q.get_height() + 0.012, '%.3f' % q.get_height(), ha='center', fontsize=8, color=C['ink'])
    ax.set_xticks(x); ax.set_xticklabels(['ρ = %.1f' % q[0] for q in r], fontsize=8.5)
    ax.set_ylim(0, 1.32); ax.set_ylabel('비율(가상 계열 20000개)', fontsize=8.5); ax.tick_params(labelsize=8.5)
    ax.set_xlabel('가상 계열의 1년 자기상관(이 책이 바꿔 본 시연값)', fontsize=8.5)
    ax.legend(loc='upper left', fontsize=8, frameon=False)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.yaxis.grid(True, color=C['grid'], lw=0.5); ax.set_axisbelow(True)
    fig.text(0.02, 0.02, '계산 12-3. 평균 -0.546, 표준편차 1.550(Pederson 등 2014)을 쓴 가상 계열. 실제 계열의 자기상관은 확인하지 못했다.', fontsize=8, color=C['soft'])
    save(fig, 'pederson', mode)

# ---------------------------------------------------------------- 그림 4
def parse_sol():
    t = open(LOG, encoding='utf-8').read()
    return [(int(a), int(b), float(c)) for a, b, c in re.findall(r'균등 가정 \[(\d+),(\d+)\] 에 20개: 100년 창 최대 >=8 비율 ([0-9.]+)', t)]
def fig4(mode):
    C = PAL[mode]
    r = parse_sol()
    fig = plt.figure(figsize=(140 * MM, 76 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.12, 0.26, 0.85, 0.66])
    x = np.arange(len(r))
    bs = ax.bar(x, [q[2] for q in r], 0.5, color=C['adv'] if mode == 'color' else '#777777', edgecolor=C['ink'], lw=0.5, hatch='' if mode == 'color' else '//')
    for q in bs: ax.text(q.get_x() + q.get_width() / 2, q.get_height() + 0.012, '%.3f' % q.get_height(), ha='center', fontsize=8.5, color=C['ink'])
    ax.set_xticks(x); ax.set_xticklabels(['%d~%d년\n(%d년 폭)' % (q[0], q[1], q[1] - q[0]) for q in r], fontsize=8.5)
    ax.set_ylim(0, 0.45); ax.set_ylabel('우연히 8개 이상 모일 비율', fontsize=8.5); ax.tick_params(labelsize=8.5)
    ax.set_xlabel('20개 연대를 흩뿌린다고 가정한 구간(이 책이 정한 값)', fontsize=8.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.yaxis.grid(True, color=C['grid'], lw=0.5); ax.set_axisbelow(True)
    fig.text(0.02, 0.02, '계산 12-4. 8개는 Solomina 등(2016)의 1640~1740년 군집. 구간을 어떻게 잡느냐에 따라 비율이 달라진다(시연값).', fontsize=8, color=C['soft'])
    save(fig, 'solomina', mode)

# ---------------------------------------------------------------- 그림 5 지도
def fig5(mode):
    C = PAL[mode]
    import geopandas as gpd
    from shapely.geometry import box
    bb = (38, 36, 112, 72)
    land = gpd.clip(mapkit.read('ne_10m_land', bb), box(*bb))
    lakes = gpd.clip(mapkit.read('ne_10m_lakes', bb), box(*bb))
    pp = mapkit.read('ne_10m_populated_places_simple')
    fig = plt.figure(figsize=(172 * MM, 108 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.07, 0.08, 0.91, 0.90]); ax.set_facecolor(C['sea'])
    land.plot(ax=ax, color=C['land'], edgecolor=C['coast'], lw=0.4)
    lakes.plot(ax=ax, color=C['sea'], edgecolor=C['coast'], lw=0.3)
    ax.set_xlim(bb[0], bb[2]); ax.set_ylim(bb[1], bb[3]); ax.set_aspect(1 / np.cos(np.radians(55)))
    ax.set_xticks(range(40, 111, 10)); ax.set_yticks(range(40, 71, 10)); ax.tick_params(labelsize=8, colors=C['soft'], length=2)
    ax.set_xticklabels(['%d°E' % v for v in range(40, 111, 10)]); ax.set_yticklabels(['%d°N' % v for v in range(40, 71, 10)])
    ax.grid(color=C['grid'], lw=0.4); ax.set_xlabel(''); ax.set_ylabel('')
    for s in ax.spines.values(): s.set_color(C['soft'])
    def pt(x, y, label, dx, dy, ha='left', m='o', fc=None):
        ax.plot([x], [y], m, color=fc or C['hot'], mec=C['ink'], ms=6, zorder=5)
        ax.text(x + dx, y + dy, label, fontsize=8.5, color=C['ink'], ha=ha, va='center', zorder=6, path_effects=halo())
    lk = {str(r['name_en']): (r.geometry.centroid.x, r.geometry.centroid.y) for _, r in mapkit.read('ne_10m_lakes').iterrows()}
    sal = pp[pp['name'].astype(str) == 'Salekhard'].iloc[0]
    pt(*lk['Telmen'], '텔멘호', 1.2, -1.6)
    pt(*lk['Teletskoe'], '텔레츠코예호', -1.2, 1.9, ha='right')
    pt(86 + 34 / 60, 49 + 48 / 60, '벨루하 빙핵', -1.6, -2.6, ha='right', m='^')
    pt(sal.geometry.x, sal.geometry.y, '살레하르드(도시 점, 야말 복원의 교정 기상대)', 1.4, 1.7)
    ax.add_patch(Rectangle((79, 42), 5, 3, fill=False, ec=C['box'], lw=1.3, zorder=5))
    ax.text(85, 40.6, '톈산 나이테 지점 범위', fontsize=8.5, color=C['ink'], ha='left', va='center', zorder=6, path_effects=halo())
    ax.text(51, 41.0, '카스피해', fontsize=8.5, color=C['ink'], ha='center', va='center', path_effects=[pe.withStroke(linewidth=2, foreground=C['sea'])])
    ax.text(40, 37.0, '몽골 나이테(Pederson, D\'Arrigo)와 카스피해 수위 지점은 좌표를 확인하지 못해 그리지 않았다.', fontsize=8, color=C['ink'], ha='left', path_effects=halo())
    save(fig, 'map', mode)

if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig1(m); fig2(m); fig3(m); fig4(m); fig5(m)
    print('ok')
