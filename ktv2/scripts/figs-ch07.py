# -*- coding: utf-8 -*-
"""제2권 7장 그림 5장(색·흑백 SVG 두 벌). 값은 ms/code/ch07 의 입력 표·실행 로그·TSV에서 읽고,
네트워크와 Mantel 분포 그림은 같은 폴더의 gentools.py 로 다시 계산한다(난수 없음, 시드 없음).
  fig-ch07-hgfreq-v1 : 여섯 유적의 하플로그룹 빈도(쌓은 막대)
  fig-ch07-phist-v1  : 쌍별 Phi_ST 행렬
  fig-ch07-fisher-v1 : [[16,2],[4,10]] 표의 13개 표 확률(로그 눈금)
  fig-ch07-mantel-v1 : 여섯 유적 유전 거리 대 시간 차의 Mantel 정확 순열 분포(720가지)
  fig-ch07-net-v1    : msprime 시연 자료(시드 5)의 중앙결합 네트워크
사용: python figs-ch07.py"""
import math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geomap import Fig, FS, FS_S, FS_I, tw
ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch07')
sys.path.insert(0, CODE)
import numpy as np
import gentools as g
OUT = os.path.join(ROOT, 'fig')


def base(mode, H):
    f = Fig(1300.0, H, mode)
    f.rect(0, 0, 1300.0, H, '#FFFFFF')
    return f, f.P


def note(f, x, y, s, maxw=None):
    maxw = maxw or (f.w - x - 40)
    lines, cur = [], ''
    for ch in s:
        if tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur)
            cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    for i, ln in enumerate(lines):
        f.text(x, y + i * 38, ln, FS_I, 'start', f.P['soft'], 400, False)
    return y + len(lines) * 38


def shade(mode, t):
    """0(옅음)~1(짙음). 색은 갈색 계열, 흑백은 회색."""
    t = max(0.0, min(1.0, t))
    if mode == 'color':
        a, b = (0xF6, 0xEE, 0xDD), (0x9C, 0x4F, 0x2E)
    else:
        a, b = (0xF4, 0xF4, 0xF4), (0x22, 0x22, 0x22)
    c = [int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)]
    return '#%02X%02X%02X' % tuple(c)


def rd_tsv(name):
    return np.array([[float(x) for x in l.split('\t')] for l in open(os.path.join(CODE, name), encoding='utf-8') if l.strip()])


SITES = None


def sites():
    global SITES
    if SITES is None:
        SITES = g.read_cui()
    return SITES


def fig_hgfreq(mode):
    f, P = base(mode, 960.0)
    rows = sites()
    names = ['N1(x)', 'N1c', 'C/C3e', 'O3a', 'O3a3c']
    if mode == 'color':
        cols = ['#9C4F2E', '#D9A36A', '#3A7CA5', '#8A6A2C', '#9FB7C4']
        txt = ['#FFFFFF', '#1B2A33', '#FFFFFF', '#FFFFFF', '#1B2A33']
    else:
        cols = ['#222222', '#777777', '#BBBBBB', '#4A4A4A', '#E0E0E0']
        txt = ['#FFFFFF', '#FFFFFF', '#111111', '#FFFFFF', '#111111']
    L, R, T = 330.0, 1130.0, 80.0
    bh, gap = 72.0, 34.0
    f.text(L, T - 26, '0%', FS_I, 'middle', P['soft'], 400, False)
    f.text(R, T - 26, '100%', FS_I, 'middle', P['soft'], 400, False)
    for i, (site, cul, a, b, n, cnt) in enumerate(rows):
        y = T + i * (bh + gap)
        f.text(L - 20, y + bh / 2 + 10, site, FS_S, 'end', P['text'], 700, False)
        x = L
        for k, c in enumerate(cnt):
            w = (R - L) * c / n
            if w > 0:
                f.rect(x, y, w, bh, cols[k], '#FFFFFF', 2.0)
                if w > 70:
                    f.text(x + w / 2, y + bh / 2 + 10, '%d' % c, FS_I, 'middle', txt[k], 700, False)
            x += w
        f.text(R + 18, y + bh / 2 + 10, 'n=%d' % n, FS_I, 'start', P['soft'], 400, False)
    ly = T + len(rows) * (bh + gap) + 20
    x = 150.0
    for k, nm in enumerate(names):
        f.rect(x, ly - 24, 36, 36, cols[k], P['frame'], 1.5)
        f.text(x + 48, ly + 6, nm, FS_I, 'start', P['text'], 400, False)
        x += 48 + tw(nm, FS_I) + 54
    note(f, 150, ly + 70, '입력은 cui-table1-v1.csv(제1권 11장이 옮긴 Cui 등(2013) 표 1의 여섯 유적, 시료 합 47). 막대 안의 수는 사람 수. 폭은 그 유적 안의 비율이다.')
    return f


def fig_phist(mode):
    f, P = base(mode, 1180.0)
    D = rd_tsv('cui-phist-v1.tsv')
    nm = [s[0] for s in sites()]
    n = len(nm)
    cw, ch = 150.0, 110.0
    L, T = 250.0, 150.0
    for j in range(n):
        f.text(L + j * cw + cw / 2, T - 24, nm[j], FS_I, 'middle', P['text'], 700, False)
    for i in range(n):
        f.text(L - 18, T + i * ch + ch / 2 + 10, nm[i], FS_I, 'end', P['text'], 700, False)
        for j in range(n):
            v = D[i, j]
            x, y = L + j * cw, T + i * ch
            neg = v < 0
            fill = '#FFFFFF' if neg else shade(mode, v)
            f.rect(x, y, cw, ch, fill, P['frame'], 1.5, 'stroke-dasharray="10 6"' if neg else '')
            dark = (not neg) and v > 0.5
            tc = '#FFFFFF' if dark else P['text']
            if i == j:
                f.text(x + cw / 2, y + ch / 2 + 10, '-', FS_I, 'middle', tc, 400, False)
            else:
                f.text(x + cw / 2, y + ch / 2 + 10, ('%.3f' % v).replace('-0.', '-0.'), FS_I, 'middle', tc, 700 if neg else 400, False)
    by = T + n * ch + 50
    for k, t in enumerate((0.0, 0.25, 0.5, 0.75, 1.0)):
        f.rect(L + k * 90, by, 90, 36, shade(mode, t), P['frame'], 1.0)
        f.text(L + k * 90 + 45, by + 76, '%.2f' % t, FS_I, 'middle', P['soft'], 400, False)
    f.rect(L + 5 * 90 + 40, by, 90, 36, '#FFFFFF', P['frame'], 1.5, 'stroke-dasharray="10 6"')
    f.text(L + 5 * 90 + 145, by + 28, '음수(그대로 둠)', FS_I, 'start', P['text'], 400, False)
    note(f, 150, by + 130, '쌍별 Phi_ST. 하플로그룹이 같으면 0, 다르면 1인 거리로 두 유적만 AMOVA(분자 분산 분석)에 넣은 값이다. 합라해구와 묘자구는 0/0이어서 0으로 두었다. 입력과 값은 distmat.log와 cui-phist-v1.tsv.')
    return f


def fig_fisher(mode):
    f, P = base(mode, 1130.0)
    pr = {}
    for ln in open(os.path.join(CODE, 'fisher.log'), encoding='utf-8'):
        m = re.match(r'\s*a =\s*(\d+)\s+확률 ([\d.e+-]+)\s*(<= 관측)?', ln)
        if m:
            pr[int(m.group(1))] = (float(m.group(2)), bool(m.group(3)))
    ks = sorted(pr)
    L, T, R, B = 210.0, 100.0, 1240.0, 700.0
    lo, hi = -7.0, 0.0
    Y = lambda v: B - (math.log10(v) - lo) / (hi - lo) * (B - T)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for e in range(-7, 1):
        v = 10.0 ** e
        f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.text(L - 14, Y(v) + 10, '1e%d' % e if e else '1', FS_I, 'end', P['soft'], 400, False)
    f.text(L - 160, T - 36, '표의 확률 (로그 눈금)', FS_S, 'start', P['text'], 400, False)
    slot = (R - L) / len(ks)
    c_obs = P['hot'] if mode == 'color' else '#111111'
    c_oth = '#C9D5DB' if mode == 'color' else '#C8C8C8'
    for i, a in enumerate(ks):
        p, ob = pr[a]
        x = L + i * slot + slot * 0.14
        top = Y(p)
        f.rect(x, top, slot * 0.72, B - top, c_obs if ob else c_oth, P['frame'], 1.5)
        f.text(x + slot * 0.36, B + 42, '%d' % a, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '표의 첫 칸 a (신석기 중 N1(x)인 사람 수). 행과 열의 합은 고정', FS_S, 'middle', P['text'], 400, False)
    ly = B + 150
    f.rect(190, ly - 26, 36, 36, c_obs, P['frame'], 1.5)
    f.text(238, ly + 4, '관측한 표(a=16)와 확률이 같거나 더 작은 표 - 양쪽 p에 더함', FS_I, 'start', P['text'], 400, False)
    f.rect(190, ly + 22, 36, 36, c_oth, P['frame'], 1.5)
    f.text(238, ly + 52, '그 밖의 표', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 108, '입력 표 [[16,2],[4,10]](신석기 대 청동기, 제1권 계산 11-3). 13개 표의 확률 합은 1. 짙은 막대 4개(a=6, 16, 17, 18)의 합이 양쪽 p = 7.899e-04. fisher.log 3번 항목.')
    return f


def fig_mantel(mode):
    f, P = base(mode, 1130.0)
    A = rd_tsv('cui-euclid-v1.tsv')
    Bm = rd_tsv('cui-timediff-v1.tsv')
    res = g.mantel(A, Bm, perms=0, seed=1, exact_max=8)
    rs = np.array(res['rs'])
    r0 = res['r']
    edges = np.linspace(-1.0, 1.0, 21)
    cnt, _ = np.histogram(rs, bins=edges)
    L, T, R, B = 210.0, 100.0, 1240.0, 700.0
    ymax = int(math.ceil(cnt.max() / 20.0) * 20)
    Y = lambda v: B - v / ymax * (B - T)
    X = lambda r: L + (r + 1.0) / 2.0 * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in range(0, ymax + 1, 20):
        f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.text(L - 14, Y(v) + 10, '%d' % v, FS_I, 'end', P['soft'], 400, False)
    f.text(L - 160, T - 36, '순열의 수 (전체 %d)' % len(rs), FS_S, 'start', P['text'], 400, False)
    c_hi = P['hot'] if mode == 'color' else '#111111'
    c_lo = '#C9D5DB' if mode == 'color' else '#C8C8C8'
    for k in range(20):
        x0, x1 = X(edges[k]), X(edges[k + 1])
        f.rect(x0 + 2, Y(cnt[k]), x1 - x0 - 4, B - Y(cnt[k]), c_hi if edges[k] >= 0.5 - 1e-12 else c_lo, P['frame'], 1.2)
    for r in (-1.0, -0.5, 0.0, 0.5, 1.0):
        f.line(X(r), B, X(r), B + 10, P['frame'], 2.0)
        f.text(X(r), B + 44, '%g' % r, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '순열한 뒤의 Mantel r (구간 폭 0.1)', FS_S, 'middle', P['text'], 400, False)
    f.line(X(r0), T, X(r0), B, c_hi, 3.0, '18 8')
    f.text(X(r0) + 14, T + 40, '관측 r = %.4f' % r0, FS_I, 'start', c_hi, 700, False)
    ge = int((rs >= r0 - 1e-12).sum())
    f.text(X(r0) + 14, T + 80, '%d/%d = %.4f 이상' % (ge, len(rs), ge / len(rs)), FS_I, 'start', c_hi, 400, False)
    note(f, 150, B + 150, '여섯 유적의 빈도 벡터 유클리드 거리 대 표의 시기 구간 가운데 BP의 차(mantel.log 4번). 집단 이름표를 바꾸는 6! = 720가지를 모두 계산했다. 점선은 관측 r이다. 짙은 막대는 0.5 이상 구간이며, 0.4~0.5 구간에는 관측 r보다 큰 순열과 작은 순열이 섞여 있다(합 34가지가 관측 r 이상).')
    return f


def fig_net(mode):
    f, P = base(mode, 1260.0)
    txt = open(os.path.join(CODE, 'network.log'), encoding='utf-8').read()
    m = re.search(r'<msprime 시드 5> 관측 10개 ([01 ]+)', txt)
    obs = [tuple(int(c) for c in s) for s in m.group(1).split()]
    V, nobs, E, it = g.median_joining(obs)
    n = len(V)
    # 간선 길이에 비례하는 용수철 배치(결정적)
    rng = np.random.RandomState(4)
    pos = rng.uniform(-1, 1, size=(n, 2))
    K = {}
    for i, j, w in E:
        K[(i, j)] = w
    for _ in range(3000):
        d = pos[:, None, :] - pos[None, :, :]
        r = np.sqrt((d ** 2).sum(-1)) + 1e-9
        force = (0.04 / r ** 2)[:, :, None] * d
        fr = force.sum(1)
        for (i, j), w in K.items():
            v = pos[j] - pos[i]
            L0 = 0.35 + 0.22 * w
            rr = np.sqrt((v ** 2).sum()) + 1e-9
            s = (rr - L0) * 0.12 / rr * v
            fr[i] += s
            fr[j] -= s
        pos += 0.5 * fr * 0.5
    pos -= pos.mean(0)
    sx = (pos[:, 0].max() - pos[:, 0].min()) or 1.0
    sy = (pos[:, 1].max() - pos[:, 1].min()) or 1.0
    x0, x1, y0, y1 = 160.0, 1140.0, 120.0, 900.0
    sc = min((x1 - x0) / sx, (y1 - y0) / sy)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    P2 = [(cx + p[0] * sc, cy + p[1] * sc) for p in pos]
    c_obs = P['hot'] if mode == 'color' else '#111111'
    c_med = '#FFFFFF'
    for i, j, w in E:
        xa, ya = P2[i]
        xb, yb = P2[j]
        f.line(xa, ya, xb, yb, P['frame'], 3.0)
        # 돌연변이 수를 가로 눈금으로
        for t in range(w):
            u = (t + 1) / (w + 1.0)
            xm, ym = xa + (xb - xa) * u, ya + (yb - ya) * u
            dx, dy = (xb - xa), (yb - ya)
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / ln * 11, dx / ln * 11
            f.line(xm - nx, ym - ny, xm + nx, ym + ny, P['text'], 3.0)
    for i in range(n):
        x, y = P2[i]
        if i < nobs:
            f.marker(x, y, 'dot', 2.0, c_obs)
            f.text(x, y + 10, chr(65 + i), FS_I, 'middle', '#FFFFFF', 700, False)
        else:
            f.marker(x, y, 'sq', 1.5, c_med, P['text'])
    ly = 1000.0
    f.marker(190, ly - 8, 'dot', 1.3, c_obs)
    f.text(220, ly + 2, '관측한 하플로타입(A~%s, network.log 순서)' % chr(64 + nobs), FS_I, 'start', P['text'], 400, False)
    f.marker(190, ly + 44, 'sq', 1.3, c_med, P['text'])
    f.text(220, ly + 54, '중앙 벡터(추정한 가상의 조상형)', FS_I, 'start', P['text'], 400, False)
    f.line(170, ly + 100, 210, ly + 100, P['frame'], 3.0)
    f.line(190, ly + 88, 190, ly + 112, P['text'], 3.0)
    f.text(220, ly + 110, '선 위의 짧은 금 하나 = 돌연변이 한 자리', FS_I, 'start', P['text'], 400, False)
    st = g.network_stats(V, nobs, E)
    note(f, 150, ly + 160, '시연 자료: msprime 1.4.4 이진 돌연변이 모형(시드 5), 반수체 12개 중 서로 다른 하플로타입 %d개. 꼭짓점 %d(중앙 %d), 간선 %d, 간선 길이 합 %d. 배치는 용수철 모형으로 그린 것이며 그림 위의 거리는 계통의 깊이를 뜻하지 않는다.' % (nobs, st['n_nodes'], st['n_median'], st['n_edges'], st['total_len']))
    return f


FIGS = (('fig-ch07-hgfreq-v1', fig_hgfreq), ('fig-ch07-phist-v1', fig_phist), ('fig-ch07-fisher-v1', fig_fisher),
        ('fig-ch07-mantel-v1', fig_mantel), ('fig-ch07-net-v1', fig_net))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in FIGS:
            f = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, '경고:', w)
