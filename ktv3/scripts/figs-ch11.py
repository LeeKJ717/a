# -*- coding: utf-8 -*-
"""11장 그림. 자료 그림은 논문에서 옮긴 숫자(또는 계산 11-x 로그)를 다시 그린 것이다.
실행: python3 scripts/figs-ch11.py  → fig/fig-ch11-*-v1-{color,bw}.svg
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
from matplotlib.patches import Rectangle
import mapkit
mapkit.use_font(8.5)
FIG = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR')
LOG = os.path.join(ROOT, 'ms', 'code', 'ch11', 'calc-ch11-v1.log')
MM = 1 / 25.4

PAL = {
 'color': dict(bg='#FFFFFF', ink='#1B2A33', soft='#5B6B75', grid='#D5DCE0', win='#4C7FA3', win2='#7BA6C4', hot='#B2512E', ev='#B2512E', ok='#2F7D5B', land='#F1EBDD', sea='#E3EEF3', coast='#7D7255', box='#2F6F9A'),
 'bw': dict(bg='#FFFFFF', ink='#111111', soft='#444444', grid='#CFCFCF', win='#666666', win2='#999999', hot='#111111', ev='#111111', ok='#333333', land='#F4F4F4', sea='#E6E6E6', coast='#444444', box='#222222'),
}

def save(fig, name, mode):
    p = os.path.join(FIG, 'fig-ch11-%s-v1-%s.svg' % (name, mode))
    fig.savefig(p, format='svg', bbox_inches=None)
    if PREV:
        fig.savefig(os.path.join(PREV, 'ch11-%s-%s.png' % (name, mode)), dpi=110)
    plt.close(fig)

# ---------------------------------------------------------------- 그림 1: 사건과 기후 창
WINS = [
 ("중부유럽 기후 변동 큼 250~550 (Büntgen 2011)", 250, 550),
 ("알타이 나무 새로 자람 적음 약 350~650 (Büntgen 2016)", 350, 650),
 ("알타이 빙하 전진 마셰이 433~595 (Solomina 2016)", 433, 595),
 ("알타이 빙하 전진 멘수 435~767 (Solomina 2016)", 435, 767),
 ("헝가리 건조 여름 420~450 (Hakenbeck·Büntgen 2022)", 420, 450),
 ("후기 고대 소빙기 536~660 (Büntgen 2016)", 536, 660),
 ("몽골 소나무 한랭 536~545 (D'Arrigo 2001)", 536, 545),
 ("텔멘호 고수위 600~700 (Struck 2022)", 600, 700),
]
EVS = [  # (라벨, 시작, 끝, 수준, 정렬)
 ("훈 유럽 출현 약 370~376", 370, 376, 0, 'right'),
 ("습격·침공 422~452", 422, 452, 1, 'center'),
 ("유연 패망 551~555", 551, 555, 2, 'right'),
 ("아바르 정착 567~568", 567, 568, 0, 'left'),
 ("마자르 도하 894~895", 894, 895, 1, 'right'),
]
def fig1(mode):
    C = PAL[mode]
    fig = plt.figure(figsize=(172 * MM, 112 * MM), facecolor=C['bg'])
    axE = fig.add_axes([0.40, 0.80, 0.58, 0.17])
    ax = fig.add_axes([0.40, 0.14, 0.58, 0.64])
    X0, X1 = 250, 910
    for a in (axE, ax):
        a.set_xlim(X0, X1); a.set_facecolor(C['bg'])
        for s in a.spines.values(): s.set_visible(False)
    axE.set_ylim(0, 3.2); axE.set_yticks([]); axE.set_xticks([])
    ax.set_ylim(len(WINS) - 0.4, -0.6); ax.set_yticks(range(len(WINS)))
    ax.set_yticklabels([w[0].replace(' (', '\n(') for w in WINS], fontsize=8.5, color=C['ink']); ax.tick_params(axis='y', length=0)
    ax.set_xticks(range(300, 901, 100)); ax.tick_params(axis='x', colors=C['soft'], labelsize=8.5, length=3)
    ax.set_xlabel('서기(년)', color=C['ink'], fontsize=8.5, labelpad=2)
    ax.spines['bottom'].set_visible(True); ax.spines['bottom'].set_color(C['soft'])
    for x in range(300, 901, 100): ax.axvline(x, color=C['grid'], lw=0.5, zorder=0)
    for i, (lab, a, b) in enumerate(WINS):
        fc = C['win'] if mode == 'color' else '#777777'
        ax.add_patch(Rectangle((a, i - 0.28), b - a, 0.56, facecolor=fc, edgecolor=C['ink'], lw=0.5, hatch=('' if mode == 'color' else ('//' if i % 2 == 0 else '..')), zorder=2))
    for k, (lab, a, b, lv, ha) in enumerate(EVS):
        xm = (a + b) / 2
        axE.add_patch(Rectangle((a - 2, 0), max(b - a, 4) + 4, 0.35, facecolor=C['ev'], edgecolor=C['ev'], lw=0.4))
        y = 0.6 + lv * 0.85
        axE.plot([xm, xm], [0.35, y], color=C['ev'], lw=0.6)
        axE.text(xm + (4 if ha == 'left' else (-4 if ha == 'right' else 0)), y + 0.05, lab, ha=ha, va='bottom', fontsize=8.5, color=C['ink'])
        ax.axvspan(a - 1, b + 1, color=C['ev'], alpha=0.16 if mode == 'color' else 0.20, lw=0, zorder=1)
    fig.text(0.02, 0.015, '논문과 이 장 표 11-4, 11-5의 연대를 다시 그린 것. 막대 경계는 논문이 "약"으로 적은 값이며 오차는 그리지 않았다.', fontsize=8, color=C['soft'])
    save(fig, 'timeline', mode)

# ---------------------------------------------------------------- 그림 2: 창 위치 우연성
def parse_scan():
    txt = open(LOG, encoding='utf-8').read()
    rows = re.findall(r'기준 \[(\d+),(\d+)\]: \(가\).*?비율 ([0-9.]+) \| \(나\).*?확률 ([0-9.]+)', txt)
    return [(int(a), int(b), float(c), float(d)) for a, b, c, d in rows]
def fig2(mode):
    C = PAL[mode]
    rows = parse_scan()
    fig = plt.figure(figsize=(150 * MM, 82 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.10, 0.26, 0.88, 0.66])
    x = np.arange(len(rows)); w = 0.36
    f1 = C['win'] if mode == 'color' else '#888888'
    f2 = C['hot'] if mode == 'color' else '#222222'
    b1 = ax.bar(x - w / 2, [r[2] for r in rows], w, color=f1, edgecolor=C['ink'], lw=0.5, hatch='' if mode == 'color' else '//', label='(가) 31년 창을 무작위로 옮겼을 때 습격 3개 이상을 담는 비율')
    b2 = ax.bar(x + w / 2, [r[3] for r in rows], w, color=f2, edgecolor=C['ink'], lw=0.5, hatch='' if mode == 'color' else '..', label='(나) 습격 연대 5개를 무작위로 뽑았을 때 고정 창 420~450이 3개 이상 담을 확률')
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.012, '%.3f' % r.get_height(), ha='center', va='bottom', fontsize=8.5, color=C['ink'])
    ax.set_xticks(x); ax.set_xticklabels(['[%d, %d]\n(%d년)' % (r[0], r[1], r[1] - r[0] + 1) for r in rows], fontsize=8.5)
    ax.set_ylim(0, 0.62); ax.set_ylabel('비율 또는 확률', fontsize=8.5)
    ax.set_xlabel('우연 기준 구간 (이 책이 정한 값)', fontsize=8.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.yaxis.grid(True, color=C['grid'], lw=0.5); ax.set_axisbelow(True)
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    fig.text(0.02, 0.01, '계산 11-2 로그에서 옮긴 값. 창 420~450은 저자들이 연대를 본 뒤 정한 것이어서 사후 선택은 반영되지 않았다.', fontsize=8, color=C['soft'])
    save(fig, 'scan', mode)

# ---------------------------------------------------------------- 그림 3: Wilson 구간
def parse_wilson():
    txt = open(LOG, encoding='utf-8').read()
    out = []
    for line in txt.splitlines():
        m = re.match(r'(.*) : ([0-9.]+)  95% 구간 ([0-9.]+) ~ ([0-9.]+)', line)
        if m: out.append((m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))))
    return out
def fig3(mode):
    C = PAL[mode]
    rows = parse_wilson()
    fig = plt.figure(figsize=(160 * MM, 78 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.40, 0.22, 0.58, 0.74])
    for i, (nm, p, lo, hi) in enumerate(rows):
        ax.plot([lo, hi], [i, i], color=C['ink'], lw=1.6)
        ax.plot([p], [i], 'o', color=C['hot'] if mode == 'color' else '#FFFFFF', mec=C['ink'], ms=6, zorder=3)
        ax.text(hi + 0.02, i, '%.2f (%.2f~%.2f)' % (p, lo, hi), va='center', fontsize=8, color=C['ink'])
    ax.set_yticks(range(len(rows))); 
    short = ['훈 시대 공개 유전체 R1a-Z93 (10/23)', '훈 시대 공개 유전체 Q (9/23)', '훈 시대 6명 중 R1a1a1b2 (4/6)', '아바르 계열 76명 중 아시아 핵심 (12/76)', 'ARK 남성 10명 중 Q (8/10)']
    ax.set_yticklabels(short[:len(rows)], fontsize=8.5)
    ax.invert_yaxis(); ax.set_xlim(0, 1.45); ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel('비율 (Wilson 95% 구간)', fontsize=8.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.xaxis.grid(True, color=C['grid'], lw=0.5); ax.set_axisbelow(True)
    fig.text(0.02, 0.02, '분자·분모는 Maróti 등(2022) 본문에서 옮겼다. 구간은 계산 11-4에서 이 책이 구했다.', fontsize=8, color=C['soft'])
    save(fig, 'wilson', mode)

# ---------------------------------------------------------------- 그림 4: 지도
def fig4(mode):
    C = PAL[mode]
    import geopandas as gpd
    from shapely.geometry import box
    bb = (10, 34, 115, 62)
    land = gpd.clip(mapkit.read('ne_10m_land', bb), box(*bb))
    lakes = gpd.clip(mapkit.read('ne_10m_lakes', bb), box(*bb))
    fig = plt.figure(figsize=(172 * MM, 92 * MM), facecolor=C['bg'])
    ax = fig.add_axes([0.07, 0.10, 0.91, 0.86])
    ax.set_facecolor(C['sea'])
    land.plot(ax=ax, color=C['land'], edgecolor=C['coast'], lw=0.4)
    lakes.plot(ax=ax, color=C['sea'], edgecolor=C['coast'], lw=0.3)
    ax.set_xlim(bb[0], bb[2]); ax.set_ylim(bb[1], bb[3]); ax.set_aspect(1 / np.cos(np.radians(48)))
    ax.set_xticks(range(20, 111, 20)); ax.set_yticks(range(40, 61, 10))
    ax.tick_params(labelsize=8, colors=C['soft'], length=2)
    ax.set_xticklabels(['%d°E' % v for v in range(20, 111, 20)]); ax.set_yticklabels(['%d°N' % v for v in range(40, 61, 10)])
    ax.grid(color=C['grid'], lw=0.4); ax.set_xlabel(''); ax.set_ylabel('')
    for s in ax.spines.values(): s.set_color(C['soft'])
    def pt(x, y, label, dx, dy, ha='left', m='o', ms=6, fc=None):
        ax.plot([x], [y], m, color=fc or C['hot'], mec=C['ink'], ms=ms, zorder=5)
        ax.text(x + dx, y + dy, label, fontsize=8.5, color=C['ink'], ha=ha, va='center', zorder=6,
                path_effects=[__import__('matplotlib.patheffects', fromlist=['x']).withStroke(linewidth=2, foreground='white')])
    lk = lambda n: [(r.geometry.centroid.x, r.geometry.centroid.y) for _, r in mapkit.read('ne_10m_lakes').iterrows() if str(r['name_en']) == n][0]
    tel = lk('Telmen'); tlt = lk('Teletskoe')
    pt(*tel, '텔멘호', 1.2, -1.4)
    pt(*tlt, '텔레츠코예호', -1.2, 1.7, ha='right')
    pt(86 + 34 / 60, 49 + 48 / 60, '벨루하 빙핵', -1.4, -2.3, ha='right', m='^')
    ax.add_patch(Rectangle((79, 42), 5, 3, fill=False, ec=C['box'], lw=1.3, zorder=5))
    ax.text(84.8, 41.0, '톈산 나이테 지점 범위', fontsize=8.5, color=C['ink'], ha='left', va='center', zorder=6)
    pt(19.08, 47.50, '부다페스트', 1.2, 1.6)
    ax.text(50.5, 40.6, '카스피해', fontsize=8.5, color=C['ink'], ha='center', va='center', path_effects=[__import__('matplotlib.patheffects', fromlist=['x']).withStroke(linewidth=2, foreground=C['sea'])])
    bud = (19.08, 47.50)
    for q in (tel, (86.57, 49.8)):
        ax.plot([bud[0], q[0]], [bud[1], q[1]], color=C['ink'], lw=0.7, ls=(0, (4, 3)), zorder=4)
    ax.text(60, 55.2, '점선은 대원 거리 비교선이며 이동 경로가 아니다', fontsize=8.5, color=C['ink'], ha='center',
            path_effects=[__import__('matplotlib.patheffects', fromlist=['x']).withStroke(linewidth=2, foreground='white')])
    save(fig, 'map', mode)

if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig1(m); fig2(m); fig3(m); fig4(m)
    print('ok')
