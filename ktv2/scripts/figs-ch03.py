# -*- coding: utf-8 -*-
"""제2권 3장 그림 4장: 보정(그림 3-1), 제1권 보정 범위와의 차이(3-2), 연령-깊이(3-3), OSL 오차(3-4).
값은 ms/code/ch03 의 함수와 곡선 파일(ms/code/ch03/data)에서 직접 계산한다. 곡선이 없으면 그림 3-1~3-3 을 만들지 못한다.
python3 scripts/figs-ch03.py  -> fig/fig-ch03-*-v1-{color,bw}.svg (+ 확인용 png 는 scratch)"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'ms', 'code', 'ch03'))
import numpy as np
from geomap import Fig, FS, FS_S, FS_I, f1
from c14lib import *
OUT = os.path.join(ROOT, 'fig')
os.makedirs(OUT, exist_ok=True)

def cols(mode):
    if mode == 'color':
        return dict(a='#9C4F2E', b='#3A7CA5', c='#8A6A2C', ink='#1B2A33', soft='#5F7F93', grid='#C9D3D8', fa='#E7C9B8', fb='#BBD4E0')
    return dict(a='#111111', b='#666666', c='#333333', ink='#111111', soft='#555555', grid='#CCCCCC', fa='#CFCFCF', fb='#E2E2E2')

def path(f, pts, stroke, sw=3.0, dash=None, fill='none', close=False, op=None):
    d = 'M' + ' L'.join('%s,%s' % (f1(x), f1(y)) for x, y in pts) + (' Z' if close else '')
    ex = (' stroke-dasharray="%s"' % dash) if dash else ''
    o = (' fill-opacity="%s"' % op) if op else ''
    f.raw('<path d="%s" fill="%s" stroke="%s" stroke-width="%s"%s%s stroke-linejoin="round"/>' % (d, fill, stroke, sw, ex, o))

import geomap as G
def note(f, x, y, s, C, maxw=None):
    """주석 한 줄을 폭에 맞춰 나누어 쓰고 다음 y 를 돌려준다."""
    maxw = maxw or (f.w - x - 20)
    lines, cur = [], ''
    for ch in s:
        if G.tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    for i, ln in enumerate(lines):
        f.text(x, y + i * 38, ln, FS_I, 'start', C['soft'], 400, False)
    return y + len(lines) * 38 + 8

def frame(f, x0, y0, x1, y1, C):
    f.rect(x0, y0, x1 - x0, y1 - y0, '#FFFFFF', C['soft'], 2.0)

# --------------------------------------------------------------------------- 그림 3-1
def fig_curve(mode):
    C = cols(mode)
    W, H = 1300.0, 1200.0
    f = Fig(W, H, mode); f.rect(0, 0, W, H, '#FFFFFF')
    cur = load_curve('intcal20'); c, m, s = cur
    c14, sd = 2450, 30
    x0, x1 = 190.0, 1230.0
    A0, A1 = 2300.0, 2750.0
    X = lambda a: x0 + (a - A0) / (A1 - A0) * (x1 - x0)
    # 위 패널: 곡선
    t0, t1 = 80.0, 560.0
    B0, B1 = 2650.0, 2250.0
    Y = lambda b: t0 + (B0 - b) / (B0 - B1) * (t1 - t0)
    frame(f, x0, t0, x1, t1, C)
    for b in (2300, 2400, 2500, 2600):
        f.line(x0, Y(b), x1, Y(b), C['grid'], 1.2, '6 8')
        f.text(x0 - 14, Y(b) + 10, f'{b:,}', FS_I, 'end', C['soft'], 400, False)
    f.text(x0 - 14, t0 - 26, '14C 나이(BP)', FS_I, 'end', C['ink'], 400, False)
    mk = (c >= A0) & (c <= A1)
    cc, mm, ss = c[mk], m[mk], s[mk]
    upper = [(X(a), Y(b + e)) for a, b, e in zip(cc, mm, ss)]
    lower = [(X(a), Y(b - e)) for a, b, e in zip(cc, mm, ss)]
    path(f, upper + lower[::-1], 'none', 0, None, C['fb'], True)
    path(f, [(X(a), Y(b)) for a, b in zip(cc, mm)], C['b'], 4.0)
    # 측정값 띠
    f.rect(x0, Y(c14 + sd), x1 - x0, Y(c14 - sd) - Y(c14 + sd), C['fa'], 'none', 0, 'fill-opacity="0.75"')
    f.line(x0, Y(c14), x1, Y(c14), C['a'], 3.0)
    f.text(x0 + 24, Y(2560) + 5, '측정값 2,450 ± 30 BP (시연값)', FS_I, 'start', C['a'], 700, False)
    f.text(x0 + 24, Y(2610) + 5, 'IntCal20 곡선 ± 1σ', FS_I, 'start', C['b'], 700, False)
    # 아래 패널: 확률
    g, p = calibrate(c14, sd, cur)
    p0, p1 = 650.0, 880.0
    pm = p[(g >= A0) & (g <= A1)].max() * 1.12
    Yp = lambda v: p1 - v / pm * (p1 - p0)
    frame(f, x0, p0, x1, p1 + 70, C)
    pts = [(X(a), Yp(v)) for a, v in zip(g, p) if A0 <= a <= A1]
    path(f, [(pts[0][0], p1)] + pts + [(pts[-1][0], p1)], C['a'], 2.0, None, C['fa'], True)
    segs = hpd(g, p, 0.954)
    for a, b, pr in segs:
        f.line(X(max(a, A0)), p1 + 30, X(min(b, A1)), p1 + 30, C['ink'], 7.0)
    f.text(x0 + 24, p0 + 40, '보정 후 확률(합 = 1)', FS_I, 'start', C['a'], 700, False)
    f.text(x0 + 24, p1 + 62, '굵은 선 = 95.4% 구간', FS_I, 'start', C['ink'], 400, False)
    for a in (2300, 2400, 2500, 2600, 2700):
        f.line(X(a), p1 + 70, X(a), p1 + 82, C['soft'], 2.0)
        f.text(X(a), p1 + 122, f'{a:,}', FS_I, 'middle', C['soft'], 400, False)
    f.text((x0 + x1) / 2, p1 + 170, '달력 나이(cal BP)', FS_S, 'middle', C['ink'], 400, False)
    # 안내선: 측정값과 곡선이 만나는 곳
    cross = [a for a, b in zip(cc, mm) if abs(b - c14) <= 3]
    note(f, 130, p1 + 250, '※ 곡선이 14C 나이 2,450 근처에서 거의 평평해 한 값이 여러 구간으로 갈라진다. 95.4% 구간(cal BP): ' + '; '.join(f'{a:.0f}~{b:.0f}' for a, b, _ in segs), C)
    return f

# --------------------------------------------------------------------------- 그림 3-2
def fig_diff(mode):
    C = cols(mode)
    cur13 = load_curve('intcal13'); cur04 = load_curve('intcal04'); cur20 = load_curve('intcal20')
    rows = []
    gy = [(363, 1800, 30, 1625, 1819), (739, 2810, 30, 2846, 2997), (889, 4150, 30, 4578, 4825), (917, 6100, 40, 6863, 7157),
          (1416, 7210, 40, 7956, 8158), (1839, 7900, 40, 8595, 8976), (2060, 7960, 40, 8649, 8990), (2351, 8030, 40, 8764, 9024), (2892, 8870, 40, 9785, 10173)]
    for d, c14, sd, lo, hi in gy:
        g, p = calibrate(c14, sd, cur13); sg = hpd(g, p, .954); rows.append((f'GY-1 {d} cm', sg[0][0] - lo, sg[-1][1] - hi))
    g, p = calibrate(4940, 35, cur04); sg = hpd(g, p, .954); rows.append(('4,940 BP', sg[0][0] - 5600, sg[-1][1] - 5734))
    g, p = calibrate(9785, 35, cur04); sg = hpd(g, p, .954); rows.append(('9,785 BP', sg[0][0] - 11126, sg[-1][1] - 11177))
    xi = [(59, 2537, 36, 2480, 2650), (69, 2945, 34, 2970, 3220), (79, 3349, 37, 3470, 3690), (89, 3890, 37, 4230, 4430), (101, 4619, 34, 5290, 5470)]
    for d, c14, sd, lo, hi in xi:
        g, p = calibrate(c14, sd, cur04); sg = hpd(g, p, .954); rows.append((f'호륜호 {d} cm', sg[0][0] - lo, sg[-1][1] - hi))
    g, p = calibrate(10500, 40, cur13); sg = hpd(g, p, .954); rows.append(('비금도 1,340 cm', sg[0][0] - 12240, sg[-1][1] - 12590))
    g, p = calibrate(13590, 40, cur13); sg = hpd(g, p, .954); rows.append(('비금도 1,490 cm', sg[0][0] - 16190, sg[-1][1] - 16580))
    n = len(rows)
    W = 1300.0; top = 150.0; rh = 52.0
    H = top + n * rh + 400
    f = Fig(W, H, mode); f.rect(0, 0, W, H, '#FFFFFF')
    x0, x1 = 380.0, 1240.0
    D0, D1 = -150.0, 150.0
    X = lambda v: x0 + (v - D0) / (D1 - D0) * (x1 - x0)
    frame(f, x0, top - 20, x1, top + n * rh, C)
    for v in (-100, -50, 0, 50, 100):
        f.line(X(v), top - 20, X(v), top + n * rh, C['soft'] if v == 0 else C['grid'], 2.0 if v == 0 else 1.2, None if v == 0 else '6 8')
        f.text(X(v), top - 40, f'{v:+d}' if v else '0', FS_I, 'middle', C['soft'], 400, False)
    for i, (nm, dlo, dhi) in enumerate(rows):
        y = top + i * rh + rh / 2 - 10
        f.text(x0 - 16, y + 10, nm, FS_I, 'end', C['ink'], 400, False)
        f.line(X(min(dlo, dhi)), y, X(max(dlo, dhi)), y, C['grid'], 2.0)
        f.marker(X(dlo), y, 'dot', 0.9, C['b'])
        f.marker(X(dhi), y, 'sq', 0.9, C['a'], '#FFFFFF')
    yl = top + n * rh + 60
    f.text(x0, yl, '차이 = 이 책 − 제1권 (단위: 년)', FS_S, 'start', C['ink'], 400, False)
    f.marker(x0 + 8, yl + 60, 'dot', 0.9, C['b']); f.text(x0 + 30, yl + 70, '구간의 젊은 쪽 끝', FS_I, 'start', C['ink'], 400, False)
    f.marker(x0 + 410, yl + 60, 'sq', 0.9, C['a'], '#FFFFFF'); f.text(x0 + 432, yl + 70, '구간의 늙은 쪽 끝', FS_I, 'start', C['ink'], 400, False)
    yy = note(f, 130, yl + 130, '※ 95.4% 최고 밀도 구간들의 바깥 끝을 견줌. 곡선: IntCal13(GY-1, 비금도), IntCal04(그 밖).', C)
    note(f, 130, yy, '※ 9,785 BP: 이 책 구간(11,177~11,246)이 제1권 구간(11,126~11,177)보다 51~69년 늙다. 두 구간은 끝에서 맞닿는다.', C)
    return f

# --------------------------------------------------------------------------- 그림 3-3
def fig_agedepth(mode):
    C = cols(mode)
    cur = load_curve('intcal13')
    z = np.load(os.path.join(ROOT, 'ms', 'code', 'ch03', 'out-ex3.npz'))
    dd, A, gm = z['dd'][3:], z['A'][:, 3:], z['gm'][3:]
    W, H = 1300.0, 1260.0
    f = Fig(W, H, mode); f.rect(0, 0, W, H, '#FFFFFF')
    x0, x1, t0, t1 = 190.0, 1230.0, 90.0, 800.0
    a0, a1 = 6600.0, 10400.0
    d0, d1 = 850.0, 2950.0
    X = lambda a: x0 + (a - a0) / (a1 - a0) * (x1 - x0)
    Y = lambda d: t0 + (d - d0) / (d1 - d0) * (t1 - t0)
    frame(f, x0, t0, x1, t1, C)
    for a in (7000, 8000, 9000, 10000):
        f.line(X(a), t0, X(a), t1, C['grid'], 1.2, '6 8')
        f.text(X(a), t1 + 46, f'{a:,}', FS_I, 'middle', C['soft'], 400, False)
    for d in (1000, 1500, 2000, 2500):
        f.line(x0, Y(d), x1, Y(d), C['grid'], 1.2, '6 8')
        f.text(x0 - 14, Y(d) + 10, f'{d:,}', FS_I, 'end', C['soft'], 400, False)
    f.text(x0 - 14, t0 - 30, '깊이(cm)', FS_I, 'end', C['ink'], 400, False)
    f.text((x0 + x1) / 2, t1 + 100, '달력 나이(cal BP)', FS_S, 'middle', C['ink'], 400, False)
    # 몬테카를로 띠: 깊이 격자에서 각 조합의 나이
    grid = np.linspace(dd[0], dd[-1], 120)
    ages = np.array([np.interp(grid, dd, row) for row in A])
    q = np.percentile(ages, [2.5, 50, 97.5], axis=0)
    band = [(X(a), Y(d)) for a, d in zip(q[0], grid)] + [(X(a), Y(d)) for a, d in zip(q[2][::-1], grid[::-1])]
    path(f, band, 'none', 0, None, C['fb'], True)
    path(f, [(X(a), Y(d)) for a, d in zip(q[1], grid)], C['b'], 4.0)
    # 제1권 방식: 보정 범위 중간값 사이 직선
    path(f, [(X(a), Y(d)) for a, d in zip(gm, dd)], C['a'], 3.0, '14 8')
    # 연대 구간(95.4%) 가로 막대
    gy = [(363, 1800, 30), (739, 2810, 30), (889, 4150, 30), (917, 6100, 40), (1416, 7210, 40), (1839, 7900, 40), (2060, 7960, 40), (2351, 8030, 40), (2892, 8870, 40)]
    for d, c14, sd in gy:
        g, p = calibrate(c14, sd, cur); sg = hpd(g, p, .954)
        for a, b, pr in sg:
            if pr > 0.02 and a >= a0 and b <= a1:
                f.line(X(a), Y(d), X(b), Y(d), C['ink'], 7.0)
    yl = t1 + 160
    f.line(x0, yl - 9, x0 + 70, yl - 9, C['b'], 4.0); f.text(x0 + 90, yl, '몬테카를로 중앙값, 띠는 95%', FS_I, 'start', C['ink'], 400, False)
    f.line(x0 + 620, yl - 9, x0 + 690, yl - 9, C['a'], 3.0, '14 8'); f.text(x0 + 710, yl, '제1권: 범위 중간값 직선', FS_I, 'start', C['ink'], 400, False)
    f.line(x0, yl + 48, x0 + 70, yl + 48, C['ink'], 7.0); f.text(x0 + 90, yl + 57, '각 14C 날짜의 95.4% 구간(IntCal13)', FS_I, 'start', C['ink'], 400, False)
    yy = note(f, 130, yl + 130, '※ 순서(깊을수록 늙음)를 지킨 조합만 남김. 베이즈 연대-깊이 모형이 아니다.', C)
    note(f, 130, yy, '※ 깊이 363~2,892 cm 의 연대 9개(그림은 917 cm 부터). 자료: 제1권 표 6-5 의 14C 나이.', C)
    return f

# --------------------------------------------------------------------------- 그림 3-4
def fig_osl(mode):
    C = cols(mode)
    W, H = 1300.0, 1330.0
    f = Fig(W, H, mode); f.rect(0, 0, W, H, '#FFFFFF')
    osl = [(142, 3.30, 0.19, 21.40, 0.10), (255, 3.36, 0.19, 22.24, 0.33), (355, 3.23, 0.18, 22.82, 0.12), (453, 3.25, 0.18, 24.38, 0.35),
           (553, 3.34, 0.19, 24.03, 0.36), (654, 3.31, 0.19, 24.32, 0.34), (734, 3.28, 0.19, 25.34, 0.45), (834, 3.35, 0.20, 24.42, 0.41),
           (955, 3.18, 0.19, 25.18, 0.29), (1054, 3.19, 0.19, 26.45, 0.62), (1135, 3.11, 0.18, 26.01, 0.31), (1215, 3.19, 0.19, 25.84, 0.46), (1323, 3.35, 0.20, 33.54, 0.75)]
    # 위: 분산 몫
    x0, x1, t0 = 330.0, 1240.0, 120.0
    rh = 34.0
    f.text(130, 56, '(가) 비금도 13개 OSL 나이의 오차 분산 가운데 선량률의 몫', FS_S, 'start', C['ink'], 700, False)
    t1 = t0 + len(osl) * rh
    f.rect(x0, t0, x1 - x0, t1 - t0, '#FFFFFF', C['soft'], 2.0)
    X = lambda v: x0 + v * (x1 - x0)
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        f.line(X(v), t0, X(v), t1, C['grid'], 1.2, '6 8')
        f.text(X(v), t1 + 42, f'{int(v*100)}%', FS_I, 'middle', C['soft'], 400, False)
    for i, (d, dr, sdr, De, sDe) in enumerate(osl):
        a, s, rel = osl_age(De, sDe, dr, sdr)
        share = (sdr / dr) ** 2 / rel ** 2
        y = t0 + i * rh
        f.rect(x0, y + 6, share * (x1 - x0), rh - 12, C['a'], 'none', 0)
        f.rect(x0 + share * (x1 - x0), y + 6, (1 - share) * (x1 - x0), rh - 12, C['fb'], 'none', 0)
        f.text(x0 - 14, y + rh - 8, f'{d:,} cm', FS_I, 'end', C['ink'], 400, False)
    f.rect(x0, t1 + 76, 40, 22, C['a'], 'none', 0); f.text(x0 + 54, t1 + 96, '선량률 오차의 몫', FS_I, 'start', C['ink'], 400, False)
    f.rect(x0 + 420, t1 + 76, 40, 22, C['fb'], 'none', 0); f.text(x0 + 474, t1 + 96, '등가선량 오차의 몫', FS_I, 'start', C['ink'], 400, False)
    # 아래: 분포
    y0 = t1 + 200
    f.text(130, y0 - 30, '(나) 나이 = De ÷ DR 의 분포: 상대 오차 6%일 때와 40%일 때 (시연값, 100만 번 뽑기)', FS_S, 'start', C['ink'], 700, False)
    rng = np.random.default_rng(20261026)
    M = 1_000_000
    panels = [('5.8% (De 5 ± 0.1, DR 2 ± 0.116)', 5.0, 0.1, 2.0, 0.116, (1.8, 3.4)), ('40% (De 5 ± 2, DR 2 ± 0.8)', 5.0, 2.0, 2.0, 0.8, (-1, 9))]
    pw = 520.0
    for k, (lab, De, sDe, DR, sDR, (lo, hi)) in enumerate(panels):
        px0 = 130 + k * (pw + 70); px1 = px0 + pw
        py0, py1 = y0 + 10, y0 + 330
        x = rng.normal(De, sDe, M); y = rng.normal(DR, sDR, M)
        t = x / y
        bins = np.linspace(lo, hi, 61)
        h, _ = np.histogram(t, bins=bins, density=True)
        a, s, rel = osl_age(De, sDe, DR, sDR)
        xs = np.linspace(lo, hi, 200)
        gpdf = np.exp(-0.5 * ((xs - a) / s) ** 2) / (s * math.sqrt(2 * math.pi))
        ymax = max(h.max(), gpdf.max()) * 1.1
        Xp = lambda v: px0 + (v - lo) / (hi - lo) * (px1 - px0)
        Yp = lambda v: py1 - v / ymax * (py1 - py0)
        f.rect(px0, py0, pw, py1 - py0, '#FFFFFF', C['soft'], 2.0)
        for i in range(len(h)):
            f.rect(Xp(bins[i]), Yp(h[i]), Xp(bins[i + 1]) - Xp(bins[i]), py1 - Yp(h[i]), C['fb'], 'none', 0)
        path(f, [(Xp(a_), Yp(v)) for a_, v in zip(xs, gpdf)], C['a'], 3.5)
        tick = [2, 2.5, 3] if k == 0 else [0, 3, 6, 9]
        for tv in tick:
            f.line(Xp(tv), py1, Xp(tv), py1 + 10, C['soft'], 2.0)
            f.text(Xp(tv), py1 + 46, f'{tv:g}', FS_I, 'middle', C['soft'], 400, False)
        f.text(px0 + 10, py1 + 100, lab, FS_I, 'start', C['ink'], 400, False)
    note(f, 130, y0 + 480, '※ 막대: 뽑은 나이의 분포, 곡선: 해석식(오차 전파)이 말하는 정규분포. 막대가 곡선과 겹쳐야 해석식이 맞다.', C)
    return f

if __name__ == '__main__':
    jobs = [('fig-ch03-curve-v1', fig_curve), ('fig-ch03-diff-v1', fig_diff), ('fig-ch03-agedepth-v1', fig_agedepth), ('fig-ch03-osl-v1', fig_osl)]
    for mode in ('color', 'bw'):
        for nm, fn in jobs:
            try:
                f = fn(mode)
            except CurveMissing as e:
                print(nm, mode, '곡선 입수 확인 필요:', e); continue
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, 'warn', w)
