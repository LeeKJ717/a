# -*- coding: utf-8 -*-
"""figkit12 v1 - 제3권 1장·2장 그림 공용 도우미.
mapkit(제2권 1장 도우미)의 글꼴, 팔레트, 글자 검사를 쓰고, 이 두 장의 자료 그림에 필요한 몇 가지를 더한다.
그림은 fig/fig-chNN-이름-v1-color.svg 와 -bw.svg 두 벌. 본문 폭 130 mm 기준으로 그린다(글자 8 pt 이상).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.environ.setdefault('GEODIR', os.path.join(ROOT, 'geodata'))
sys.path.insert(0, HERE)
import numpy as np
import mapkit as mk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.text
from matplotlib.patches import Patch

OUT = os.path.join(ROOT, 'fig')
PREV = os.environ.get('PREVDIR', '')          # 미리보기 PNG 를 둘 곳(없으면 만들지 않음)
FS = 8.0
mk.use_font(FS)
plt.rcParams.update({'axes.linewidth': 0.6, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5, 'axes.spines.top': False, 'axes.spines.right': False})

C = {
    'color': dict(wet='#2F6F9A', dry='#B5733A', mid='#9AA5AB', ink='#1B2A33', soft='#4F6E80', grid='#D5DDE1', acc='#9C4F2E',
                  a='#2F6F9A', b='#B5733A', c='#5E8C61', d='#7A5C99', e='#C2A33B', land='#F1EBDD', sea='#E3EEF3', lake='#BBD4E0'),
    'bw': dict(wet='#3A3A3A', dry='#C8C8C8', mid='#9A9A9A', ink='#111111', soft='#444444', grid='#DDDDDD', acc='#111111',
               a='#3A3A3A', b='#9A9A9A', c='#6A6A6A', d='#BDBDBD', e='#8A8A8A', land='#FFFFFF', sea='#EBEBEB', lake='#D0D0D0'),
}
HATCH = {'color': dict(wet=None, dry=None), 'bw': dict(wet='////', dry=None)}


def fig(w=130, h=90):
    f = mk.mm_fig(w, h)
    return f


def audit(f, name, min_size=8.0):
    """글자 크기, 그림 밖으로 넘침, 글자끼리 겹침을 검사한다. 눈금이 축 범위 밖이라 그려지지 않는 눈금 글자는 건너뛴다."""
    f.canvas.draw()
    r = f.canvas.get_renderer()
    phantom = set()
    for ax in f.axes:
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = min(lim), max(lim)
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                loc = tick.get_loc()
                if loc < lo - 1e-9 * abs(hi - lo) or loc > hi + 1e-9 * abs(hi - lo):
                    phantom.add(id(tick.label1)); phantom.add(id(tick.label2))
    texts = []
    for t in f.findobj(matplotlib.text.Text):
        s = t.get_text()
        if not s or not t.get_visible() or id(t) in phantom:
            continue
        try:
            bb = t.get_window_extent(r)
        except Exception:
            continue
        if bb.width < 1 or bb.height < 1:
            continue
        texts.append((s, t.get_fontsize(), bb))
    W, H = f.canvas.get_width_height()
    warn = []
    for i, (s, fs, bb) in enumerate(texts):
        if fs < min_size - 1e-6:
            warn.append('글자 %.1fpt 미만: %s (%.1fpt)' % (min_size, s, fs))
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > W + 1 or bb.y1 > H + 1:
            warn.append('글자 넘침: %s' % s)
        for s2, fs2, bb2 in texts[i + 1:]:
            ox = min(bb.x1, bb2.x1) - max(bb.x0, bb2.x0)
            oy = min(bb.y1, bb2.y1) - max(bb.y0, bb2.y0)
            if ox > 1 and oy > 1 and ox * oy / min(bb.width * bb.height, bb2.width * bb2.height) > 0.06:
                warn.append('글자 겹침: %s / %s' % (s, s2))
    print('%s: 글자 %d개, 경고 %d개' % (name, len(texts), len(warn)))
    for w in warn[:12]:
        print('   ', w)
    return warn


def save(f, name, mode, audit_it=True):
    """name 예: 'ch01-windows' -> fig/fig-ch01-windows-v1-color.svg"""
    os.makedirs(OUT, exist_ok=True)
    w = audit(f, name + '-' + mode) if audit_it else []
    p = os.path.join(OUT, 'fig-%s-v1-%s.svg' % (name, mode))
    f.savefig(p, format='svg', bbox_inches=None)
    if PREV:
        os.makedirs(PREV, exist_ok=True)
        f.savefig(os.path.join(PREV, 'fig-%s-v1-%s.png' % (name, mode)), dpi=170)
    plt.close(f)
    return w


def style_ax(ax, mode, grid='y'):
    P = C[mode]
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(P['soft'])
    ax.tick_params(colors=P['soft'], labelsize=FS, length=2.5, pad=2)
    if grid:
        ax.grid(axis=grid, color=P['grid'], lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def wet_dry_bar(ax, y, a, b, sign, mode, h=0.62, label=None, lw=0.5):
    """+1 습윤은 진한 막대, -1 건조는 연한 막대(흑백은 빗금도 더한다)."""
    P = C[mode]
    lo, hi = min(a, b), max(a, b)
    if sign > 0:
        ax.barh(y, hi - lo, left=lo, height=h, color=P['wet'], edgecolor=P['ink'], linewidth=lw, hatch=HATCH[mode]['wet'], zorder=3)
    else:
        ax.barh(y, hi - lo, left=lo, height=h, color=P['dry'], edgecolor=P['ink'], linewidth=lw, zorder=3)
