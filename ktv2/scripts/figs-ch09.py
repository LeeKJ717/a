# -*- coding: utf-8 -*-
"""제2권 9장 그림 6장(색·흑백 SVG 두 벌): fig/fig-ch09-이름-v1-{color,bw}.svg
그림의 값은 모두 ms/code/ch09/results/*.json(실습 스크립트가 저장한 결과)에서 읽거나, 같은 입력으로 이 스크립트가 다시 계산한 값이다.
  oxide   : 시연값 화산 유리의 산화물 두 개 산점도(기준 집단과 미지 층)         실습 9-1~9-4
  assign  : 미지 층의 파편을 기준 집단에 배정한 결과                            실습 9-4b
  agree   : 날짜 묶음의 가중 평균과 T' (제1권 4장의 입력)                       실습 9-5
  order   : 층서 순서 제약이 사후분포를 바꾸는 시연값                           실습 9-10
  gap     : 두 분출 단계 간격의 분포(제1권 4장 입력)                            실습 9-11
  radius  : 분출구에서 반경과 부채꼴, 지점(제1권 4장 좌표)                      실습 9-12~9-14
글자는 8pt(29단위) 이상, 지명은 한글만. 겹침·넘침은 Fig.save가 검사한다.
실행: python3 scripts/figs-ch09.py   (작업 폴더 /home/claude/book2에서)"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'ms', 'code', 'ch09'))
import numpy as np
from scipy import stats
import geomap as G
from geomap import Fig, FS, FS_S, FS_I, f1
import tephralib as T
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'fig')
RES = os.path.join(ROOT, 'ms', 'code', 'ch09', 'results')
os.makedirs(OUT, exist_ok=True)
J = lambda n: json.load(open(os.path.join(RES, n)))

def base(mode, H=1000.0):
    W = 1300.0
    f = Fig(W, H, mode)
    f.rect(0, 0, W, H, '#FFFFFF')
    return f, f.P

def cols(mode):
    if mode == 'color':
        return dict(a='#3A7CA5', b='#9C4F2E', c='#8A6A2C', d='#6B7A82', e='#9DB7C6', g='#5B8C5A', v='#7A5C99', light='#E4E9EC', band='#DCE6EC', faint='#C9D1D6')
    return dict(a='#111111', b='#666666', c='#888888', d='#444444', e='#BBBBBB', g='#333333', v='#777777', light='#EEEEEE', band='#E4E4E4', faint='#D2D2D2')

def axes(f, L, T_, R, B, xt, yt, X, Y, xlab=None, ylab=None, xfmt=str, yfmt=str, grid=True, ylab_x=None):
    P = f.P
    f.rect(L, T_, R - L, B - T_, 'none', P['frame'], 2.4)
    for v in yt:
        if grid: f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.line(L - 8, Y(v), L, Y(v), P['frame'], 2.0)
        f.text(L - 14, Y(v) + 10, yfmt(v), FS_I, 'end', P['soft'], 400, False)
    for v in xt:
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, xfmt(v), FS_I, 'middle', P['soft'], 400, False)
    if xlab: f.text((L + R) / 2, B + 92, xlab, FS_S, 'middle', P['text'], 400, False)
    if ylab: f.text(L - 120 if ylab_x is None else ylab_x, T_ - 24, ylab, FS_S, 'start', P['text'], 400, False)

def polyline(f, pts, color, sw=3.0, dash=None, opacity=1.0):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    f.raw('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-opacity="%s"%s/>'
          % (' '.join('%s,%s' % (f1(x), f1(y)) for x, y in pts), color, sw, opacity, d))

def note(f, x, y, s):
    maxw = f.w - x - 30
    lines, cur = [], ''
    for ch in s:
        if G.tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    for i, ln in enumerate(lines):
        f.text(x, y + i * 38, ln, FS_I, 'start', f.P['soft'], 400, False)
    f.h = max(f.h, y + (len(lines) - 1) * 38 + 40)
    return len(lines)

def legend_item(f, x, y, kind, color, label, size=0.9):
    if kind in ('dot', 'sq', 'tri', 'dia', 'star'):
        f.marker(x + 14, y - 8, kind, size, color)
    else:
        f.line(x, y - 8, x + 56, y - 8, color, 4.0, kind if kind != 'solid' else None)
    off = 40 if kind in ('dot', 'sq', 'tri', 'dia', 'star') else 70
    f.text(x + off, y, label, FS_I, 'start', f.P['text'], 400, False)
    return x + off + G.tw(label, FS_I) + 36

# ================================================================= 그림 1: 산화물 산점도
def fig_oxide(mode):
    D = J('ex1.json'); ox = D['OX']
    iS, iN, iK = ox.index('SiO2'), ox.index('Na2O'), ox.index('K2O')
    f, P = base(mode, 900.0); C = cols(mode)
    cl = {k: np.array(v) for k, v in D['closed'].items()}
    xs = lambda a: a[:, iS]; ys = lambda a: a[:, iN] + a[:, iK]
    allx = np.concatenate([xs(a) for a in cl.values()]); ally = np.concatenate([ys(a) for a in cl.values()])
    x0, x1 = math.floor(allx.min()) - 1, math.ceil(allx.max()) + 1
    y0, y1 = math.floor(ally.min()) - 1, math.ceil(ally.max()) + 1
    panels = [(80.0, 640.0, '(가) 기준 집단 A, B, C'), (730.0, 1270.0, '(나) 미지 층 (회색: 기준 집단)')]
    T_, B_ = 150.0, 640.0
    mk = {'A': ('dot', C['a']), 'B': ('sq', C['b']), 'C': ('tri', C['c']), 'X층': ('dot', C['a']), 'Y층': ('tri', C['c']), 'Z층': ('dia', C['v']), 'W층': ('sq', C['g'])}
    for pi, (L, R, ttl) in enumerate(panels):
        X = lambda v, L=L, R=R: L + (v - x0) / (x1 - x0) * (R - L)
        Y = lambda v: B_ - (v - y0) / (y1 - y0) * (B_ - T_)
        f.text(L, T_ - 44, ttl, FS_S, 'start', P['text'], 700, False)
        axes(f, L, T_, R, B_, list(range(x0 + 1, x1, 4)), list(range(y0 + 1, y1, 2)), X, Y, 'SiO2 (질량 %)', None,
             lambda v: '%d' % v, lambda v: '%d' % v)
        if pi == 0:
            for k in 'ABC':
                kind, col = mk[k]
                for a, b in zip(xs(cl[k]), ys(cl[k])): f.marker(X(a), Y(b), kind, 0.55, col)
        else:
            for k in 'ABC':
                for a, b in zip(xs(cl[k]), ys(cl[k])): f.circle(X(a), Y(b), 4.5, C['faint'], 'none', 0)
            for k in ('X층', 'Y층', 'Z층', 'W층'):
                kind, col = mk[k]
                for a, b in zip(xs(cl[k]), ys(cl[k])): f.marker(X(a), Y(b), kind, 0.62, col)
    x = 80.0; yl = B_ + 150
    for k, lab in (('A', '원천 A'), ('B', '원천 B'), ('C', '원천 C')):
        x = legend_item(f, x, yl, mk[k][0], mk[k][1], lab)
    x = 80.0; yl2 = yl + 50
    for k, lab in (('X층', 'X층'), ('Y층', 'Y층'), ('Z층', 'Z층'), ('W층', 'W층')):
        x = legend_item(f, x, yl2, mk[k][0], mk[k][1], lab)
    note(f, 80, yl2 + 70, '가로축은 SiO2, 세로축은 Na2O+K2O(질량 %, 합계 100으로 닫은 값). 시연값(실습 9-1): 난수로 만든 가상의 조성이며 실제 어느 화산의 값도 아니다. 두 산화물만 그리면 W층은 기준 집단 A와 C 사이에 놓인다. 판별은 아홉 개 산화물을 모두 써서 한다(그림 9-2).')
    return f

# ================================================================= 그림 2: 배정 결과
def fig_assign(mode):
    D = J('ex1.json'); A = D['assign']; tr = D['truth']
    f, P = base(mode, 760.0); C = cols(mode)
    f.text(60, 60, '미지 층의 파편을 기준 집단 A, B, C에 배정한 결과 (파편 수)', FS_S, 'start', P['text'], 700, False)
    L, R = 560.0, 1130.0
    top = 120.0; rh = 100.0
    fills = [('A', C['a'], 'A로'), ('B', C['b'], 'B로'), ('C', C['c'], 'C로'), ('none', C['e'], '어느 집단에도 안 맞음')]
    for i, u in enumerate(('X층', 'Y층', 'Z층', 'W층')):
        a = A[u]; y = top + i * rh
        f.text(60, y + 44, u, FS_S, 'start', P['text'], 700, False)
        f.text(60, y + 84, tr[u].replace(' (기준 집단에 없음)', '').replace(' + ', '+'), FS_I, 'start', P['soft'], 400, False)
        sc = (R - L) / 24.0
        xx = L
        for key, col, lab in fills:
            n = a[key]
            if n == 0: continue
            f.rect(xx, y + 10, n * sc, 64, col, '#FFFFFF', 2.0)
            tc = '#FFFFFF' if (mode == 'color' and key in ('A', 'B', 'C')) or (mode == 'bw' and key in ('A', 'B')) else P['text']
            f.text(xx + n * sc / 2, y + 54, str(n), FS_S, 'middle', tc, 700, False)
            xx += n * sc
        f.text(R + 10, y + 54, 'n=%d' % a['n'], FS_I, 'start', P['soft'], 400, False)
    ly = top + 4 * rh + 30
    x = 60.0
    for key, col, lab in fills:
        f.rect(x, ly - 24, 34, 28, col, P['frame'], 1.5)
        f.text(x + 46, ly, lab, FS_I, 'start', P['text'], 400, False)
        x += 46 + G.tw(lab, FS_I) + 40
    note(f, 60, ly + 70, '시연값(실습 9-4b). 선형 판별로 가장 가까운 집단을 고르고, 그 집단 자신의 평균과 공분산으로 잰 거리가 99% 한계를 넘으면 "안 맞음"으로 뺐다. Z층은 두 원천이 섞인 층이고, W층은 기준 집단에 없는 원천이다. n은 분석 합계 93% 이상으로 남은 파편 수이다(24개씩 분석).')
    return f

# ================================================================= 그림 3: 날짜 묶음의 합치
def fig_agree(mode):
    D = J('ex2.json')
    f, P = base(mode, 1500.0); C = cols(mode)
    blocks = [
        ('U-4 층: 날짜 다섯 개(14C 나이, BP, 오차는 1σ)', [12165, 11840, 12030, 12090, 12095], [40, 45, 40, 40, 40], (11750, 12300), [11800, 11950, 12100, 12250],
         [('다섯 개 평균', D['u4five'], C['b']), ('11,840 뺀 평균', D['u4four'], C['a'])]),
        ('U-3 층: 날짜 둘', [7525, 8030], [35, 35], (7400, 8150), [7500, 7700, 7900, 8100],
         [('두 개 평균', D['u3'], C['b'])]),
        ('U-2 층: 날짜 다섯 개 (4,710 포함)', [4910, 4965, 4945, 4940, 4710], [35, 35, 35, 35, 30], (4650, 5050), [4700, 4800, 4900, 5000],
         [('다섯 개 평균', D['u2five'], C['b']), ('네 개 평균(4,710 뺌)', D['u2four'], C['a'])]),
    ]
    L, R = 420.0, 1240.0
    y = 50.0
    for ttl, xs, ss, (lo, hi), ticks, means in blocks:
        n = len(xs); rows = n + len(means)
        h = rows * 54 + 70
        f.text(60, y + 24, ttl, FS_S, 'start', P['text'], 700, False)
        T_ = y + 50; B_ = T_ + rows * 54 + 8
        X = lambda v: L + (v - lo) / (hi - lo) * (R - L)
        f.rect(L, T_, R - L, B_ - T_, 'none', P['frame'], 2.4)
        for t in ticks:
            f.line(X(t), T_, X(t), B_, P['grid'], 1.0, '8 8'); f.line(X(t), B_, X(t), B_ + 10, P['frame'], 2.0)
            f.text(X(t), B_ + 44, format(t, ','), FS_I, 'middle', P['soft'], 400, False)
        for i, (a, s) in enumerate(zip(xs, ss)):
            yy = T_ + 34 + i * 54
            f.text(L - 24, yy + 10, '날짜 %d' % (i + 1), FS_I, 'end', P['soft'], 400, False)
            f.line(X(a - s), yy, X(a + s), yy, C['d'], 4.0)
            f.marker(X(a), yy, 'dot', 0.9, C['d'])
        for j, (lab, r, col) in enumerate(means):
            yy = T_ + 34 + (n + j) * 54
            f.text(L - 24, yy + 10, lab, FS_I, 'end', P['text'], 700, False)
            f.line(X(r['mean'] - r['err']), yy, X(r['mean'] + r['err']), yy, col, 6.0)
            f.marker(X(r['mean']), yy, 'dia', 1.0, col)
            p = r['p']
            ptxt = ('p=%.1e' % p).replace('e-0', 'e-').replace('e-', 'E-') if p < 1e-3 else 'p=%.3f' % p
            f.text(R - 12, yy + 10, "T'=%.1f, df=%d, %s" % (r['T'], r['df'], ptxt), FS_I, 'end', P['text'], 700, False) if r['mean'] - r['err'] < (lo + hi) / 2 else f.text(L + 12, yy + 10, "T'=%.1f, df=%d, %s" % (r['T'], r['df'], ptxt), FS_I, 'start', P['text'], 700, False)
        y = B_ + 110
    note(f, 60, y - 10, "제1권 4장 계산 4-6의 입력(오쿠노 등 2010). 점과 가는 선은 날짜와 1σ, 마름모와 굵은 선은 가중 평균과 그 오차이다. 14C 나이는 보정하지 않은 값이며 층마다 가로 눈금이 다르다. T'가 5% 한계(자유도 3에서 7.81, 4에서 9.49, 1에서 3.84)보다 작으면 합치이다. 실습 9-5.")
    return f

# ================================================================= 그림 4: 순서 제약
def fig_order(mode):
    D = J('ex3.json'); DD = D['demo_dens']; dm = D['demo']
    f, P = base(mode, 900.0); C = cols(mode)
    L, R, T_, B_ = 150.0, 1240.0, 120.0, 620.0
    x0, x1 = 2850.0, 3200.0
    ymax = max(max(DD[str(k)]['ordered']) for k in range(3)) * 1.12
    X = lambda v: L + (v - x0) / (x1 - x0) * (R - L)
    Y = lambda v: B_ - v / ymax * (B_ - T_)
    f.text(L, 66, '시연값: 세 층의 참 나이 사후분포. 순서가 없을 때와 있을 때', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T_, R, B_, [2900, 3000, 3100, 3200], [], X, Y, '14C 나이 (BP, 보정하지 않음)', None, lambda v: format(int(v), ','), lambda v: '')
    f.text(L - 120, T_ - 24, '사후 밀도', FS_S, 'start', P['text'], 400, False)
    colr = [C['b'], C['a'], C['c']]
    for k in range(3):
        d = DD[str(k)]
        pts_f = [(X(a), Y(b)) for a, b in zip(d['x'], d['free']) if x0 <= a <= x1]
        pts_o = [(X(a), Y(b)) for a, b in zip(d['x'], d['ordered']) if x0 <= a <= x1]
        polyline(f, pts_f, colr[k], 3.0, '12 8')
        polyline(f, pts_o, colr[k], 5.0)
    names = ['L1(가장 오래됨)', 'L2', 'L3(가장 젊음)']
    for k in range(3):
        d = DD[str(k)]
        i = int(np.argmax(d['ordered']))
        px, py = X(d['x'][i]), Y(d['ordered'][i])
        f.text(px, py - 20, names[k], FS_I, 'middle', C['d'] if mode == 'bw' else colr[k], 700, True)
    x = L; yl = B_ + 150
    x = legend_item(f, x, yl, '12 8', C['d'], '순서 없이(날짜만으로)')
    x = legend_item(f, x, yl, 'solid', C['d'], '순서 L1 > L2 > L3 를 두었을 때')
    s = '순서 없이: L1 %.0f, L2 %.0f, L3 %.0f (평균, BP). 순서를 두면: %.0f, %.0f, %.0f. 순서를 두면 세 층의 사후 표준편차가 %.0f, %.0f, %.0f에서 %.0f, %.0f, %.0f로 줄지만, 이것은 순서가 옳다는 가정에서 얻은 값이다. 실습 9-10.' % (
        *dm['free_mean'], *dm['mean'], *dm['free_sd'], *dm['sd'])
    note(f, L - 90, yl + 56, s)
    return f

# ================================================================= 그림 5: 두 분출 단계의 간격
def fig_gap(mode):
    g = np.load(os.path.join(RES, 'ex4-gap-sample.npy')).astype(float)
    J4 = J('ex4.json'); r0 = J4['rho0.357']
    f, P = base(mode, 900.0); C = cols(mode)
    L, R, T_, B_ = 150.0, 1240.0, 120.0, 620.0
    x0, x1 = -20.0, 85.0
    X = lambda v: L + (v - x0) / (x1 - x0) * (R - L)
    edges = np.arange(x0, x1 + 1, 1.0)
    h, _ = np.histogram(g, bins=edges, density=True)
    ymax = 0.040
    Y = lambda v: B_ - v / ymax * (B_ - T_)
    f.text(L, 66, '두 분출 단계 사이 간격(일)의 분포: 시점 오차의 상관 ρ=0.357', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T_, R, B_, [-20, 0, 20, 40, 60, 80], [], X, Y, '간격 (일)', None, lambda v: '%d' % v, lambda v: '')
    f.text(L - 120, T_ - 24, '확률 밀도', FS_S, 'start', P['text'], 400, False)
    for a, b in zip(edges[:-1], h):
        f.rect(X(a), Y(b), X(a + 1) - X(a) - 1, B_ - Y(b), C['e'], 'none', 0)
    xx = np.linspace(x0, x1, 300)
    polyline(f, [(X(a), Y(stats.norm.pdf(a, 31, 12.5))) for a in xx], C['a'], 4.0)
    polyline(f, [(X(a), Y(stats.norm.pdf(a, 31, math.hypot(10.5, 11.5)))) for a in xx], C['b'], 4.0, '14 9')
    for d, key in ((7, 'p7'), (28, 'p28'), (56, 'p56')):
        f.line(X(d), T_, X(d), B_, C['d'], 2.0, '8 8')
    f.text(X(7) - 14, T_ + 40, '7일', FS_I, 'end', P['text'], 700, False)
    f.text(X(28) - 14, T_ + 40, '28일', FS_I, 'end', P['text'], 700, False)
    f.text(X(56) + 14, T_ + 40, '56일', FS_I, 'start', P['text'], 700, False)
    x = L; yl = B_ + 150
    x = legend_item(f, x, yl, 'solid', C['a'], '정규 N(31, 12.5²)')
    x = legend_item(f, x, yl, '14 9', C['b'], '독립(ρ=0)이면 σ=15.57')
    s = '막대는 몬테카를로 표본(ρ=0.357, 200만 번 가운데 20만 개). 점선 세로선 왼쪽의 넓이가 간격이 그 날수보다 짧을 확률이다: 7일 %.3f, 28일 %.3f, 56일 %.3f (원문 2.5%%, 42.7%%, 97.9%%). 독립으로 두면 같은 확률이 %.3f, %.3f, %.3f이다. 제1권 계산 4-4, 실습 9-11.' % (
        r0['p7'], r0['p28'], r0['p56'], J4['rho0.000']['p7'], J4['rho0.000']['p28'], J4['rho0.000']['p56'])
    note(f, 60, yl + 56, s)
    return f

# ================================================================= 그림 6: 분출구에서의 반경과 부채꼴
def seg_polyline(f, pts, pr, color, sw, dash=None):
    """화면 안의 점들만 이어 그린다(범위 밖에서는 선을 끊는다)."""
    seg = []
    for (x, y) in pts:
        if 0 <= x <= pr.w and 0 <= y <= pr.h:
            seg.append((x, y))
        else:
            if len(seg) > 1: polyline(f, seg, color, sw, dash)
            seg = []
    if len(seg) > 1: polyline(f, seg, color, sw, dash)

def fig_radius(mode):
    D = J('ex5.json')
    bbox = (122.5, 32.0, 140.5, 44.5)
    f, pr = G.basemap(bbox, pad=300.0, mode=mode, grid=2.0)
    P = f.P; C = cols(mode)
    vent = (41.99, 128.08)
    ring_sty = {465.6: ('개성까지 465.6 km', '4 7', 4.0), 553.1: ('울릉도까지 553.1 km', '14 8', 4.0), 981.5: ('스이게쓰호까지 981.5 km', None, 5.0)}
    for r, (lab, dash, sw) in ring_sty.items():
        az = np.linspace(0, 360, 721)
        la, lo = T.destination(vent[0], vent[1], az, r)
        seg_polyline(f, [pr(a, b) for a, b in zip(lo, la)], pr, P['hot'] if mode == 'color' else '#111111', sw, dash)
    axis = D['sites']['스이게쓰호']['b']
    for sgn in (-1, 1):
        d = np.linspace(0, 981.5, 80)
        la, lo = T.destination(vent[0], vent[1], axis + sgn * 30.0, d)
        seg_polyline(f, [pr(a, b) for a, b in zip(lo, la)], pr, C['a'] if mode == 'color' else '#555555', 3.2, '16 10')
    # 부채꼴 호
    az = np.linspace(axis - 30, axis + 30, 60)
    la, lo = T.destination(vent[0], vent[1], az, 981.5)
    seg_polyline(f, [pr(a, b) for a, b in zip(lo, la)], pr, C['a'] if mode == 'color' else '#555555', 3.2, '16 10')
    # 지점
    vx, vy = pr(vent[1], vent[0]); f.marker(vx, vy, 'tri', 1.3, P['hot']); f.text(vx + 22, vy - 14, '백두산', FS, 'start', P['hot'], 700)
    sites = D['sites']
    spec = [('스이게쓰호', 'star', -18, -22, 'end'), ('울릉도', 'dot', -18, 40, 'end'), ('개성(시연값 좌표)', 'dot', 20, 10, 'start')]
    for nm, kind, dx, dy, an in spec:
        s = sites[nm]; x, y = pr(s['lon'], s['lat'])
        f.marker(x, y, kind, 1.1, P['site'] if kind == 'star' else P['text'])
        f.text(x + dx, y + dy, nm, FS_S, an, P['text'], 700)
    # 눈금 설명(범례)
    ly = pr.h + 70
    items = []
    x = 20.0
    for r, (lab, dash, sw) in ring_sty.items():
        col = P['hot'] if mode == 'color' else '#111111'
        f.line(x, ly - 8, x + 70, ly - 8, col, sw, dash)
        f.text(x + 84, ly, lab, FS_I, 'start', P['text'], 400, False)
        x += 84 + G.tw(lab, FS_I) + 40
        if x > f.w - 400 and r != 981.5:
            x = 20.0; ly += 46
    ly += 52
    x = 20.0
    col = C['a'] if mode == 'color' else '#555555'
    f.line(x, ly - 8, x + 70, ly - 8, col, 3.2, '16 10')
    f.text(x + 84, ly, '부채꼴: 축 방위 %.1f도, 반각 30도(시연값), 반경 981.5 km' % axis, FS_I, 'start', P['text'], 400, False)
    scx, scy = 40.0, pr.h - 40.0
    G.scalebar(f, pr, scx, scy, 500)
    G.north(f, pr.w - 70, pr.h - 150)
    note(f, 20, ly + 70, '제1권 4장의 좌표(분출구는 Lee 등 2024의 41.99N, 128.08E). 원은 구면 위의 측지 거리로 그린 것을 이 지도(위도 보정 직교 투영)에 옮긴 것이어서 약간 찌그러져 보인다. 개성 좌표는 제1권이 시연값으로 둔 값이다. 거리 평면 원 대비 구면 모자 면적비는 반경 981.5 km에서 0.998이다. 실습 9-12~9-13.')
    return f

FIGS = [('fig-ch09-oxide-v1', fig_oxide), ('fig-ch09-assign-v1', fig_assign), ('fig-ch09-agree-v1', fig_agree),
        ('fig-ch09-order-v1', fig_order), ('fig-ch09-gap-v1', fig_gap), ('fig-ch09-radius-v1', fig_radius)]
if __name__ == '__main__':
    for mode in ('color', 'bw'):
        for nm, fn in FIGS:
            fg = fn(mode)
            print(nm, mode, '경고:', fg.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
