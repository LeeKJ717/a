# -*- coding: utf-8 -*-
"""9장 그림 4장(색·흑백 SVG 두 벌): fig/fig-ch09-*-v1-{color,bw}.svg
모든 값은 이 장이 읽은 논문의 숫자(연대, 비율, 표준오차, 개수)이거나 ms/code/ch09/out 의 계산 결과이다. 논문의 그림을 옮긴 것이 아니라 숫자를 다시 그린 것이다.
쓰는 법(작업 폴더 /home/claude/book3): python3 scripts/figs-ch09.py
글자는 8 pt 이상(그림 폭 130 mm 기준), 겹침은 PNG 미리보기를 눈으로 확인한다."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
FONT = 'Noto Sans CJK KR'
names = {f.name for f in fm.fontManager.ttflist}
assert FONT in names
FS = 8.5
plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'svg.fonttype': 'path', 'font.size': FS, 'axes.titlesize': FS,
                     'axes.labelsize': FS, 'xtick.labelsize': FS, 'ytick.labelsize': FS, 'legend.fontsize': FS})
OUT = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR', '/tmp/claude-0/-home-claude/ed3cac1b-b1c0-5712-817a-3e7a8e2c17a2/scratchpad/p9')
os.makedirs(PREV, exist_ok=True)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch09', 'out')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
W = 130 / 25.4
PAL = {'color': dict(a='#9C4F2E', b='#3A7CA5', c='#8A6A2C', d='#4F7F4A', e='#7B5EA7', txt='#1B2A33', soft='#4F6E80', grid='#C9D3D8', ref='#B03A2E'),
       'bw': dict(a='#111111', b='#666666', c='#999999', d='#CCCCCC', e='#EEEEEE', txt='#111111', soft='#444444', grid='#C8C8C8', ref='#111111')}

def save(fig, name, mode):
    fig.savefig(os.path.join(OUT, 'fig-ch09-%s-v1-%s.svg' % (name, mode)), format='svg')
    fig.savefig(os.path.join(PREV, '%s-%s.png' % (name, mode)), dpi=130)
    plt.close(fig)

def clean(ax, P):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(P['soft'])
    ax.tick_params(colors=P['txt'], length=3)

# ------------------------------------------------------------------ 그림 1 시간표
BARS = [  # (이름, 시작, 끝, 출처, 종류) 연도는 음수가 BCE. 논문 본문의 연대. 점은 시작 = 끝.
    ('Botai (Botai_CA)', -3500, -3300, 'Damgaard 2018 Science', 0),
    ('Afanasievo, 몽골', -3112, -2917, 'Jeong 2020', 0),
    ('Chemurchek 문화', -2750, -1900, 'Jeong 2020', 0),
    ('Okunevo (EMBA)', -2500, -2000, 'Damgaard 2018 Science', 0),
    ('Sintashta 문화', -2100, -1800, 'Jeong 2018', 1),
    ('Andronovo 문화', -1800, -1300, 'Jeong 2018', 1),
    ('타림 분지 개체', -2100, -1700, 'Zhang 2021', 0),
    ('Ulaanzuukh 무덤', -1450, -1150, 'Jeong 2020', 0),
    ('Khövsgöl 후기 청동기 무덤', -1380, -975, 'Jeong 2018', 0),
    ('Slab Grave 문화', -1000, -300, 'Jeong 2020', 0),
    ('Chandman_IA, Sagly/Uyuk', -400, -200, 'Jeong 2020', 0),
    ('흉노 제국', -209, 98, 'Jeong 2020', 2),
    ('유럽 사료의 훈 (약 370 CE)', 370, 380, 'Maróti 2022', 2),
    ('Türkic, Uyghur 혼합 (약 500 CE)', 500, 500, 'Jeong 2020', 2),
    ('훈, 아바르, 정복 헝가리인의 도착', 400, 900, 'Maróti 2022 초록', 2),
    ('몽골 제국', 1206, 1368, 'Jeong 2020', 2)]

def fig_timeline(mode):
    P = PAL[mode]
    fig, ax = plt.subplots(figsize=(W, 6.3))
    cols = [P['a'], P['b'], P['c']]
    hat = ['', '//', '..']
    for i, (n, s, e, src, k) in enumerate(BARS):
        y = len(BARS) - 1 - i
        if e - s < 25:
            ax.plot([s], [y], 'o', color=cols[k], ms=6, mec=P['txt'] if mode == 'bw' else cols[k])
        else:
            ax.barh(y, e - s, left=s, height=0.62, color=cols[k], edgecolor=P['txt'], linewidth=0.6, hatch=hat[k] if mode == 'bw' else '')
        ax.text(-3700, y, n, ha='right', va='center', fontsize=FS, color=P['txt'])
    ax.set_xlim(-3700, 1500)
    ax.set_ylim(-0.8, len(BARS) - 0.2)
    ax.set_yticks([])
    ax.set_xticks([-3500, -3000, -2500, -2000, -1500, -1000, -500, 0, 500, 1000, 1500])
    ax.set_xticklabels(['3500\nBCE', '3000', '2500', '2000', '1500', '1000', '500', '0', '500\nCE', '1000', '1500'])
    ax.set_xlim(-3700, 1500)
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    ax.set_axisbelow(True)
    clean(ax, P)
    ax.spines['left'].set_visible(False)
    from matplotlib.patches import Patch
    leg = [Patch(fc=cols[0], ec=P['txt'], hatch=hat[0] if mode == 'bw' else '', label='고고학 연대(무덤, 문화)'),
           Patch(fc=cols[1], ec=P['txt'], hatch=hat[1] if mode == 'bw' else '', label='문화의 연대(논문이 문맥으로 적음)'),
           Patch(fc=cols[2], ec=P['txt'], hatch=hat[2] if mode == 'bw' else '', label='역사 시기 또는 사료의 연대')]
    ax.legend(handles=leg, loc='lower left', frameon=True, framealpha=1, edgecolor=P['grid'], fontsize=FS - 0.3)
    fig.subplots_adjust(left=0.36, right=0.975, top=0.99, bottom=0.09)
    save(fig, 'timeline', mode)

# ------------------------------------------------------------------ 그림 2 혼합 비율
def fig_admix(mode):
    P = PAL[mode]
    H = 7.4
    fig = plt.figure(figsize=(W, H))
    def axin(x0, y0, w, h):
        return fig.add_axes([x0 / W, y0 / H, w / W, h / H])
    axs = [axin(1.45, 5.35, W - 1.55, 1.55), axin(1.9, 2.95, W - 2.0, 1.25), axin(1.9, 0.62, W - 2.0, 1.35)]
    # (a) Damgaard 2018 Nature
    ax = axs[0]
    groups = [('중앙 사카', [56, 44, 0, 0]), ('시베리아 타가르', [83.5, 7.5, 9, 0]), ('톈산 사카', [70, 25, 0, 5])]
    comp = ['후기 청동기 목축민 계열', '남부 시베리아 수렵채집민 계열', 'Mal\'ta(MA1) 계열', '신석기 이란 계열']
    cc = [P['a'], P['b'], P['c'], P['d']]
    ht = ['', '//', '..', 'xx']
    for i, (n, v) in enumerate(groups):
        y = len(groups) - 1 - i
        left = 0
        for j, x in enumerate(v):
            if x > 0:
                ax.barh(y, x, left=left, color=cc[j], edgecolor=P['txt'], linewidth=0.6, height=0.62, hatch=ht[j] if mode == 'bw' else '')
                if x >= 7:
                    if mode == 'color':
                        ax.text(left + x / 2, y, '%g' % x, ha='center', va='center', fontsize=FS, color='#FFFFFF')
                    else:
                        ax.text(left + x / 2, y, '%g' % x, ha='center', va='center', fontsize=FS, color=P['txt'], bbox=dict(fc='#FFFFFF', ec='none', pad=1.2))
                left += x
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[0] for g in groups][::-1])
    ax.set_xlim(0, 100)
    ax.set_xlabel('비율(퍼센트), Damgaard 등(2018, Nature)의 본문 값')
    ax.set_title('(a) 철기 시대 사카와 타가르의 구성', loc='left', fontsize=FS, color=P['txt'], x=-0.28)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=cc[j], ec=P['txt'], hatch=ht[j] if mode == 'bw' else '', label=comp[j]) for j in range(4)], ncol=2, loc='upper center',
              bbox_to_anchor=(0.30, -0.30), frameon=False, fontsize=FS - 0.4, columnspacing=1.0, handlelength=1.4)
    clean(ax, P)
    # (b) Jeong 2018
    ax = axs[1]
    rows = J('calc-9-2.json')['jeong2018']
    lab = ['주 무리, 3원천 모형', '주 무리, Shamanka_EBA 모형', '이상치 ARS026']
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        ax.errorbar(r['est'], y, xerr=1.96 * r['se'], fmt='o', color=P['a'], ecolor=P['a'], elinewidth=1.4, capsize=3, ms=5)
        ax.text(min(r['est'] + 1.96 * r['se'] + 1.5, 62) if r['est'] < 40 else r['est'] - 1.96 * r['se'] - 1.2, y + 0.28, '%.1f ± %.1f' % (r['est'], r['se']), fontsize=FS - 0.3,
                color=P['txt'], ha='left' if r['est'] < 40 else 'right', va='center')
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(lab[::-1])
    ax.set_ylim(-0.6, len(rows) - 0.3)
    ax.set_xlim(-2, 62)
    ax.axvline(0, color=P['soft'], lw=0.6)
    ax.set_xlabel('Sintashta 계열 비율(퍼센트), 막대는 평균 ± 1.96 SE(계산 9-2)')
    ax.set_title('(b) Jeong 등(2018): 후기 청동기 Khövsgöl 무덤', loc='left', fontsize=FS, color=P['txt'], x=-0.57)
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    clean(ax, P)
    # (c) Jeong 2020 몽골 시대 세 원천 구간
    ax = axs[2]
    src = [('서쪽 초원 계열', 15, 18), ('Ulaanzuukh_SlabGrave', 55, 64), ('한(Han) 계열', 21, 27)]
    for i, (n, lo, hi) in enumerate(src):
        y = len(src) - 1 - i
        ax.barh(y, hi - lo, left=lo, height=0.42, color=[P['a'], P['b'], P['c']][i], edgecolor=P['txt'], linewidth=0.6, hatch=['', '//', '..'][i] if mode == 'bw' else '')
        ax.text(hi + 1.2, y, '%d~%d' % (lo, hi), va='center', fontsize=FS, color=P['txt'])
    ax.set_yticks(range(len(src)))
    ax.set_yticklabels([s[0] for s in src][::-1])
    ax.set_xlim(0, 75)
    ax.set_xlabel('비율 구간(퍼센트), 3원천 모형이 맞은 개체 56/61')
    ax.set_title('(c) 몽골 시대 개체의 세 원천 (Jeong 등, 2020)', loc='left', fontsize=FS, color=P['txt'], x=-0.57)
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    clean(ax, P)
    save(fig, 'admix', mode)

# ------------------------------------------------------------------ 그림 3 구간
def fig_ci(mode):
    P = PAL[mode]
    c3 = J('calc-9-3.json'); c1 = J('calc-9-1.json'); c4 = J('calc-9-4.json')
    items = [('Q: 아바르 시기 세 묘지, 10/15', c3['a']['q_av'][0], c3['a']['q_av'][1], 'a'),
             ('Q: 훈 시기 공개 자료, 9/23', c3['a']['q_hun'][0], c3['a']['q_hun'][1], 'a'),
             ('R1b: Okunevo 남성, 1/10', 1, 10, 'b'),
             ('N1c: 서요하 대산전, 3/9 (제1권)', 3, 9, 'c'),
             ('N1c1a: Khövsgöl, 1/12 (n 상한)', 1, 12, 'c'),
             ('3원천 모형이 맞는 몽골 시대, 56/61', 56, 61, 'd'),
             ('초기형 모형이 맞는 후기 흉노, 26/47', 26, 47, 'd'),
             ('현생 몽골계와 같은 가지, 34/61', 34, 61, 'd')]
    import math
    def wil(k, n, z=1.959964):
        p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    fig, ax = plt.subplots(figsize=(W, 4.4))
    colmap = dict(a=P['a'], b=P['b'], c=P['c'], d=P['d'] if mode == 'color' else P['b'])
    if mode == 'color':
        colmap['d'] = P['d']
    mk = dict(a='o', b='s', c='^', d='D')
    for i, (n, k, tot, g) in enumerate(items):
        y = len(items) - 1 - i
        lo, hi = wil(k, tot)
        ax.plot([lo, hi], [y, y], color=colmap[g], lw=2.0, solid_capstyle='butt')
        ax.plot([k / tot], [y], mk[g], color=colmap[g], ms=6, mec=P['txt'], mew=0.6)
        ax.text(1.02, y, '%.2f (%.2f~%.2f)' % (k / tot, lo, hi), va='center', fontsize=FS - 0.4, color=P['txt'], clip_on=False)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([x[0] for x in items][::-1])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.7, len(items) - 0.3)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel('비율과 Wilson 95퍼센트 구간 (계산 9-1, 9-3, 9-4)')
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    clean(ax, P)
    fig.subplots_adjust(left=0.47, right=0.76, top=0.98, bottom=0.14)
    save(fig, 'ci', mode)

# ------------------------------------------------------------------ 그림 4 세대 길이
def fig_gen(mode):
    P = PAL[mode]
    sens = J('calc-9-2.json')['sensitivity']
    fig, ax = plt.subplots(figsize=(W, 3.5))
    labs = {'Chemurchek 남부 알타이': 'Chemurchek 남부 알타이 12 ± 6', 'Altai_MLBA': 'Altai_MLBA 10 ± 2', 'Chandman_IA': 'Chandman_IA 18 ± 4',
            'Türkic (혼합 시기 ca. 500 CE)': 'Türkic 8 ± 2', 'Uyghur (혼합 시기 ca. 500 CE)': 'Uyghur 12 ± 2'}
    for i, r in enumerate(sens):
        y = len(sens) - 1 - i
        g, sg = r['g'], r['sg']
        ax.plot([(g - sg) * 25, (g + sg) * 30], [y, y], color=P['soft'], lw=1.2, solid_capstyle='butt')
        ax.plot([g * 25, g * 30], [y, y], color=P['a'], lw=5.0, solid_capstyle='butt', alpha=0.9 if mode == 'color' else 1)
        for L, m in ((25, 'v'), (29, 'o'), (30, '^')):
            ax.plot([g * L], [y], m, color='#FFFFFF', mec=P['txt'], ms=4.8, mew=0.8)
    ax.set_yticks(range(len(sens)))
    ax.set_yticklabels([labs[r['name']] for r in sens][::-1])
    ax.set_xlim(0, 800)
    ax.set_xlabel('혼합 이후 지난 연수(세대 수 x 세대 길이)')
    ax.grid(axis='x', color=P['grid'], lw=0.5, ls=(0, (4, 3)))
    clean(ax, P)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker=m, color='#FFFFFF', mec=P['txt'], ms=5, ls='', label=l) for m, l in (('v', '25년'), ('o', '29년'), ('^', '30년'))], loc='upper right', bbox_to_anchor=(1.0, -0.2), frameon=False, ncol=4, title='세대 길이(굵은 선 25~30년, 가는 선 ± 1 SE 포함)', title_fontsize=FS - 0.4, columnspacing=1.2)
    fig.subplots_adjust(left=0.40, right=0.97, top=0.98, bottom=0.30)
    save(fig, 'gen', mode)

if __name__ == '__main__':
    for m in ('color', 'bw'):
        fig_timeline(m); fig_admix(m); fig_ci(m); fig_gen(m)
    print('그림 4장 x 2 저장 ->', OUT)
