# -*- coding: utf-8 -*-
"""제2권 8장 그림 5장(색·흑백 SVG 두 벌). 값은 ms/code/ch08 의 계산 결과(sedkit, 입력 CSV, out-*.npz)에서 읽는다.
  fig-ch08-cia-v1    : 표의 CIA 대 이 책이 다시 계산한 CIA (30개)
  fig-ch08-ack-v1    : A-CN-K 삼각도 (30개)
  fig-ch08-mix-v1    : Sr-Nd 도표의 두 끝 성분 혼합선과 Dou 등의 값 범위
  fig-ch08-tri-v1    : 세 끝 성분 혼합: 끝 성분 배치가 좋은 경우와 나쁜 경우(시연값)
  fig-ch08-grain-v1  : 시연 입도 분포의 누적 곡선과 등급별 무게
  fig-ch08-brune-v1  : Brune 포획 효율 곡선과 표 4의 점
사용: python figs-ch08.py"""
import csv, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'ms', 'code', 'ch08'))
import numpy as np
from geomap import Fig, FS, FS_S, FS_I, tw
import sedkit as K
ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch08')
OUT = os.path.join(ROOT, 'fig')


def rd(fn):
    return list(csv.DictReader(open(os.path.join(CODE, 'data', fn), encoding='utf-8')))


def base(mode, H=1130.0, W=1300.0):
    f = Fig(W, H, mode)
    f.rect(0, 0, W, H, '#FFFFFF')
    return f, f.P


def note(f, x, y, s, maxw=None):
    maxw = maxw or (f.w - x - 40)
    lines, cur = [], ''
    for ch in s:
        if tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    for i, ln in enumerate(lines):
        f.text(x, y + i * 38, ln, FS_I, 'start', f.P['soft'], 400, False)
    return y + len(lines) * 38


class Ax:
    """직사각형 축. 자료 좌표를 그림 좌표로 바꾸고 눈금과 틀을 그린다."""
    def __init__(self, f, L, T, R, B, x0, x1, y0, y1, xlog=False):
        self.f, self.L, self.T, self.R, self.B = f, L, T, R, B
        self.x0, self.x1, self.y0, self.y1, self.xlog = x0, x1, y0, y1, xlog

    def X(self, v):
        if self.xlog:
            return self.L + (math.log10(v) - math.log10(self.x0)) / (math.log10(self.x1) - math.log10(self.x0)) * (self.R - self.L)
        return self.L + (v - self.x0) / (self.x1 - self.x0) * (self.R - self.L)

    def Y(self, v):
        return self.B - (v - self.y0) / (self.y1 - self.y0) * (self.B - self.T)

    def frame(self, xt, yt, xfmt='%g', yfmt='%g', grid=True):
        f, P = self.f, self.f.P
        f.rect(self.L, self.T, self.R - self.L, self.B - self.T, 'none', P['frame'], 2.4)
        for v in yt:
            if grid and self.y0 < v < self.y1:
                f.line(self.L, self.Y(v), self.R, self.Y(v), P['grid'], 1.0, '8 8')
            f.line(self.L - 8, self.Y(v), self.L, self.Y(v), P['frame'], 2.0)
            f.text(self.L - 14, self.Y(v) + 10, yfmt % v, FS_I, 'end', P['soft'], 400, False)
        for v in xt:
            if grid and self.x0 < v < self.x1:
                f.line(self.X(v), self.T, self.X(v), self.B, P['grid'], 1.0, '8 8')
            f.line(self.X(v), self.B, self.X(v), self.B + 10, P['frame'], 2.0)
            f.text(self.X(v), self.B + 44, xfmt % v, FS_I, 'middle', P['soft'], 400, False)


def cols(mode):
    P = Fig(10, 10, mode).P
    if mode == 'color':
        return dict(a=P['hot'], b=P['river'], c=P['site'], k=P['text'], g=P['soft'])
    return dict(a='#111111', b='#666666', c='#333333', k='#111111', g='#555555')


# ---------------------------------------------------------------- 그림 1: CIA 표 대 계산
def fig_cia(mode):
    f, P = base(mode, 1150.0)
    C = cols(mode)
    rows = rd('he2015-table2.csv')
    pts = []
    for r in rows:
        v = {k: float(r[k]) for k in r if k != 'sample'}
        pts.append((r['sample'], v['CIA_table'], K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'])))
    ax = Ax(f, 190.0, 90.0, 1200.0, 790.0, 50, 90, 50, 90)
    ax.frame([50, 60, 70, 80, 90], [50, 60, 70, 80, 90], '%d', '%d')
    f.line(ax.X(50), ax.Y(50), ax.X(90), ax.Y(90), C['g'], 2.5, '14 8')
    f.text(ax.X(53), ax.Y(53) - 70, '1:1 선', FS_I, 'start', C['g'], 400, False)
    bad = [p for p in pts if abs(p[2] - p[1]) > 0.1]
    for n, t, c in pts:
        if abs(c - t) <= 0.1:
            f.marker(ax.X(t), ax.Y(c), 'dot', 0.9, C['b'])
    for n, t, c in bad:
        f.marker(ax.X(t), ax.Y(c), 'dia', 1.3, C['a'])
    lab = {'원강': (-20, -4, 'end'), '상강': (-20, 6, 'end'), '감강': (-20, 6, 'end')}
    for n, t, c in bad:
        dx, dy, an = lab[n]
        f.text(ax.X(t) + dx, ax.Y(c) + dy, '%s 표 %.2f / 계산 %.2f' % (n, t, c), FS_I, an, C['k'], 700)
    f.text(ax.L - 150, ax.T - 30, '이 책이 다시 계산한 CIA', FS_S, 'start', P['text'], 400, False)
    f.text((ax.L + ax.R) / 2, ax.B + 92, '논문 표 2의 CIA', FS_S, 'middle', P['text'], 400, False)
    ly = ax.B + 150
    f.marker(170, ly - 8, 'dot', 0.9, C['b']); f.text(196, ly, '표와 0.1 이내로 맞는 27개', FS_I, 'start', P['text'], 400, False)
    f.marker(700, ly - 8, 'dia', 1.3, C['a']); f.text(726, ly, '맞지 않는 3개', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 60, '계산은 sedkit의 CIA 규칙 A(몰, CaO* = min(CaO - 10/3 P2O5, Na2O)). 입력은 제1권 10장이 He 등(2015) 표 2에서 옮긴 값이다.')
    return f


# ---------------------------------------------------------------- 그림 2: A-CN-K
def fig_ack(mode):
    f, P = base(mode, 1180.0)
    C = cols(mode)
    rows = rd('he2015-table2.csv')
    pts = []
    for r in rows:
        v = {k: float(r[k]) for k in r if k != 'sample'}
        A, CN, KK = K.ack(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'])
        pts.append((r['sample'], A, CN, KK, abs(K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5']) - v['CIA_table']) > 0.1))
    side = 900.0
    h = side * math.sqrt(3) / 2
    x0, yb = 250.0, 880.0         # CN 꼭짓점(왼쪽 아래)
    # 좌표: A 위, CN 왼쪽 아래, K 오른쪽 아래
    def XY(A, CN, KK):
        s = A + CN + KK
        a, c, k = A / s, CN / s, KK / s
        return x0 + side * (k + 0.5 * a), yb - h * a
    tri = [XY(100, 0, 0), XY(0, 100, 0), XY(0, 0, 100)]
    f.poly(tri, 'none', P['frame'], 2.4)
    for a in (50, 60, 70, 80, 90):
        p1, p2 = XY(a, 100 - a, 0), XY(a, 0, 100 - a)
        f.line(p1[0], p1[1], p2[0], p2[1], P['grid'], 1.0, '8 8')
        f.text(p1[0] - 14, p1[1] + 10, '%d' % a, FS_I, 'end', P['soft'], 400, False)
    f.text(XY(100, 0, 0)[0], XY(100, 0, 0)[1] - 20, 'A (Al2O3)', FS_S, 'middle', P['text'], 700, False)
    f.text(XY(0, 100, 0)[0], XY(0, 100, 0)[1] + 48, 'CN (CaO* + Na2O)', FS_S, 'middle', P['text'], 700, False)
    f.text(XY(0, 0, 100)[0], XY(0, 0, 100)[1] + 48, 'K (K2O)', FS_S, 'middle', P['text'], 700, False)
    for n, A, CN, KK, b in pts:
        x, y = XY(A, CN, KK)
        if b:
            f.marker(x, y, 'dia', 1.3, C['a'])
        else:
            f.marker(x, y, 'dot', 0.8, C['b'])
    for n, A, CN, KK, b in pts:
        if b:
            x, y = XY(A, CN, KK)
            f.text(x + 22, y + 10, n, FS_I, 'start', C['k'], 700)
    # CIA 눈금 설명
    f.text(x0 + side / 2, yb + 52, '가로선 = CIA (A의 몫, %)', FS_I, 'middle', C['g'], 400, False)
    ly = 1005
    f.marker(170, ly - 8, 'dot', 0.8, C['b']); f.text(196, ly, '표와 0.1 이내로 맞는 27개', FS_I, 'start', P['text'], 400, False)
    f.marker(700, ly - 8, 'dia', 1.3, C['a']); f.text(726, ly, '맞지 않는 3개(원강, 상강, 감강)', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, '세 좌표는 몰 비를 합 100으로 맞춘 값(규칙 A). A 좌표가 곧 CIA이다. 같은 시료 30개.')
    return f


# ---------------------------------------------------------------- 그림 3: Sr-Nd 혼합선
def fig_mix(mode):
    f, P = base(mode, 1180.0)
    C = cols(mode)
    ax = Ax(f, 190.0, 90.0, 1220.0, 800.0, 0.7035, 0.7155, -7.0, 5.0)
    ax.frame([0.704, 0.706, 0.708, 0.710, 0.712, 0.714], [-6, -4, -2, 0, 2, 4], '%.3f', '%d')
    JA, GB = (3.59, 0.704142), (-5.4, 0.7145)
    # 직선(농도 같음)
    f.line(ax.X(JA[1]), ax.Y(JA[0]), ax.X(GB[1]), ax.Y(GB[0]), C['g'], 3.0, '14 8')
    # 곡선(시연 농도): Nd 30/20 ppm, Sr 300/180 ppm
    fs = np.linspace(0, 1, 201)
    # 질량 몫 f (JA)에서 Sr비와 εNd
    sr = K.mix_x(fs, JA[1], GB[1], 300.0, 180.0)
    nd = K.mix_x(fs, JA[0], GB[0], 30.0, 20.0)
    for i in range(len(fs) - 1):
        f.line(ax.X(sr[i]), ax.Y(nd[i]), ax.X(sr[i + 1]), ax.Y(nd[i + 1]), C['b'], 4.0)
    for fm in (0.25, 0.5, 0.75):
        x = float(K.mix_x(fm, JA[1], GB[1], 300.0, 180.0)); y = float(K.mix_x(fm, JA[0], GB[0], 30.0, 20.0))
        f.marker(ax.X(x), ax.Y(y), 'dot', 0.8, C['b'])
        f.text(ax.X(x) + 18, ax.Y(y) - 12, 'f = %.2f' % fm, FS_I, 'start', C['k'], 400)
    # 코어의 값 범위(상자): 짝이 아님
    boxes = [('빙하기 범위', 0.708164, 0.711713, -4.9, -3.6, 'a', '10 6'), ('홀로세 범위', 0.706346, 0.708265, -4.5, -2.5, 'c', None)]
    for nm, xa, xb, ya, yb, ck, dash in boxes:
        col = C[ck]
        f.rect(ax.X(xa), ax.Y(yb), ax.X(xb) - ax.X(xa), ax.Y(ya) - ax.Y(yb), 'none', col, 4.0, ('stroke-dasharray="%s"' % dash) if dash else '')
    f.text(ax.X(0.711713) + 14, ax.Y(-4.9) + 28, '빙하기 범위', FS_I, 'start', C['a'], 700)
    f.text(ax.X(0.706346) - 10, ax.Y(-2.5) - 16, '홀로세 범위', FS_I, 'end', C['c'], 700)
    # 끝 성분
    f.marker(ax.X(JA[1]), ax.Y(JA[0]), 'sq', 1.3, C['k'])
    f.text(ax.X(JA[1]) + 20, ax.Y(JA[0]) - 12, 'JA 끝 성분', FS_I, 'start', C['k'], 700)
    f.marker(ax.X(GB[1]), ax.Y(GB[0]), 'sq', 1.3, C['k'])
    f.text(ax.X(GB[1]) - 20, ax.Y(GB[0]) + 40, 'GB 끝 성분', FS_I, 'end', C['k'], 700)
    f.text(ax.L - 150, ax.T - 30, 'εNd', FS_S, 'start', P['text'], 400, False)
    f.text((ax.L + ax.R) / 2, ax.B + 92, '87Sr/86Sr', FS_S, 'middle', P['text'], 400, False)
    ly = ax.B + 150
    f.line(150, ly - 8, 215, ly - 8, C['g'], 3.0, '14 8'); f.text(228, ly, '두 성분 직선(농도 같음)', FS_I, 'start', P['text'], 400, False)
    f.line(640, ly - 8, 705, ly - 8, C['b'], 4.0); f.text(718, ly, '농도 가중 곡선(농도는 시연값)', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 60, '끝 성분의 값은 제1권 8장이 Dou 등(2021)에서 옮긴 값이고, 곡선의 농도(Nd 30과 20 ppm, Sr 300과 180 ppm)는 시연값이다. 상자는 논문이 적은 값의 범위이며 시료 하나의 Sr과 εNd 짝이 아니다.')
    return f


# ---------------------------------------------------------------- 그림 4: 세 성분 혼합
def fig_tri(mode):
    f, P = base(mode, 1740.0)
    C = cols(mode)
    d = np.load(os.path.join(CODE, 'out-mix.npz'))
    sets = [('끝 성분 배치 1: 세 끝 성분이 넓게 퍼진 경우', d['R'], d['C'], d['obs'], d['d1'], 100.0, 640.0),
            ('끝 성분 배치 2: 끝 성분 3이 1-2 혼합 곡선 바로 옆인 경우', d['R2'], d['C2'], d['obs2'], d['d2'], 840.0, 1380.0)]
    for title, R, Cc, obs, dr, T, B in sets:
        ax = Ax(f, 190.0, T, 1220.0, B, 0.7035, 0.7215, -13.5, 5.0)
        f.text(190, T - 36, title, FS_S, 'start', P['text'], 700, False)
        ax.frame([0.704, 0.708, 0.712, 0.716, 0.720], [-12, -8, -4, 0, 4], '%.3f', '%d')
        fs = np.linspace(0, 1, 121)
        for i, j in ((0, 1), (0, 2), (1, 2)):
            sr = K.mix_x(fs, R[1, i], R[1, j], Cc[1, i], Cc[1, j])
            nd = K.mix_x(fs, R[0, i], R[0, j], Cc[0, i], Cc[0, j])
            for k in range(len(fs) - 1):
                f.line(ax.X(sr[k]), ax.Y(nd[k]), ax.X(sr[k + 1]), ax.Y(nd[k + 1]), C['g'], 2.5)
        for k in range(len(dr)):
            f.circle(ax.X(dr[k, 1]), ax.Y(dr[k, 0]), 3.0, C['a'] if mode == 'color' else '#999999', 'none', 0)
        f.marker(ax.X(obs[1]), ax.Y(obs[0]), 'star', 1.0, C['k'])
        for j in range(3):
            f.marker(ax.X(R[1, j]), ax.Y(R[0, j]), 'sq', 1.2, C['k'])
            f.text(ax.X(R[1, j]) + 20, ax.Y(R[0, j]) - 14, '끝 성분 %d' % (j + 1), FS_I, 'start', C['k'], 700)
        f.text(ax.L - 150, ax.T - 4 - 0, '', FS_I)
    f.text(40, 76, 'εNd', FS_S, 'start', P['text'], 400, False)
    f.text(40, 876, 'εNd', FS_S, 'start', P['text'], 400, False)
    f.text(700, 640 + 92, '87Sr/86Sr', FS_S, 'middle', P['text'], 400, False)
    f.text(700, 1380 + 92, '87Sr/86Sr', FS_S, 'middle', P['text'], 400, False)
    ly = 1540
    f.marker(170, ly - 8, 'sq', 1.2, C['k']); f.text(196, ly, '끝 성분', FS_I, 'start', P['text'], 400, False)
    f.marker(430, ly - 8, 'star', 1.0, C['k']); f.text(462, ly, '혼합물(참값 f = 0.5, 0.3, 0.2)', FS_I, 'start', P['text'], 400, False)
    f.circle(940, ly - 8, 4.0, C['a'] if mode == 'color' else '#999999', 'none', 0); f.text(956, ly, '관측 오차를 준 400번', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 60, '모든 값이 시연값이다. 회색 선은 끝 성분 쌍의 농도 가중 혼합 곡선, 점은 관측(εNd 오차 0.3, Sr비 오차 0.0005)을 흔든 것이다. 세 끝 성분이 이룬 삼각형이 점의 흩어짐보다 훨씬 클 때만 몫이 안정하게 풀린다.')
    return f


# ---------------------------------------------------------------- 그림 5: 입도
def fig_grain(mode):
    f, P = base(mode, 1560.0)
    C = cols(mode)
    d = np.load(os.path.join(CODE, 'out-grain.npz'))
    edges, w, ps, qv = d['edges'], d['w'], d['ps'], d['q']
    ed, cum = K.cumulative(edges, w)
    # 위 패널: 누적 곡선
    ax = Ax(f, 190.0, 150.0, 1220.0, 720.0, 2.0, 10.0, 0, 100)
    ax.frame([2, 3, 4, 5, 6, 7, 8, 9, 10], [0, 20, 40, 60, 80, 100], '%d', '%d')
    for i in range(len(ed) - 1):
        f.line(ax.X(ed[i]), ax.Y(cum[i]), ax.X(ed[i + 1]), ax.Y(cum[i + 1]), C['b'], 5.0)
    for i in range(len(ed)):
        f.marker(ax.X(ed[i]), ax.Y(cum[i]), 'dot', 0.55, C['b'])
    for p, q in zip(ps, qv):
        if p in (16, 50, 84):
            f.line(ax.L, ax.Y(p), ax.X(q), ax.Y(p), C['a'], 1.8, '8 6')
            f.line(ax.X(q), ax.Y(p), ax.X(q), ax.B, C['a'], 1.8, '8 6')
            f.marker(ax.X(q), ax.Y(p), 'dia', 1.0, C['a'])
    for p, q, dx, dy in ((16, qv[1], -16, -18), (50, qv[3], -16, -18), (84, qv[5], 18, 40)):
        f.text(ax.X(q) + dx, ax.Y(p) + dy, 'φ%d = %.2f' % (p, q), FS_I, 'end' if dx < 0 else 'start', C['k'], 700)
    d40 = float(K.mm_to_phi(0.040))
    c40 = float(np.interp(d40, ed, cum))
    f.line(ax.X(d40), ax.Y(c40), ax.X(d40), ax.B, C['c'], 3.0)
    f.marker(ax.X(d40), ax.Y(c40), 'sq', 0.9, C['c'])
    f.line(ax.X(3.6), ax.Y(60), ax.X(d40), ax.Y(c40), C['c'], 2.0)
    f.text(ax.X(2.25), ax.Y(76), '40 μm보다 거친 몫', FS_I, 'start', C['c'], 700)
    f.text(ax.X(2.25), ax.Y(69), '%.1f %% (선형 보간)' % c40, FS_I, 'start', C['c'], 700)
    f.text(ax.L - 150, 60, '거친 쪽부터 누적한 무게 (%)  /  위쪽 눈금: 입경', FS_S, 'start', P['text'], 400, False)
    f.text((ax.L + ax.R) / 2, ax.B + 92, 'φ (클수록 고움)', FS_S, 'middle', P['text'], 400, False)
    # 위쪽 눈금: 입경 μm
    for phi in (4, 6, 8, 10):
        um = float(K.phi_to_um(phi))
        f.text(ax.X(phi), ax.T - 18, ('%g μm' % round(um, 1)), FS_I, 'middle', P['soft'], 400, False)
    # 아래 패널: 등급별 무게
    ax2 = Ax(f, 190.0, 940.0, 1220.0, 1300.0, 2.0, 10.0, 0, 25)
    ax2.frame([2, 3, 4, 5, 6, 7, 8, 9, 10], [0, 5, 10, 15, 20, 25], '%d', '%d')
    for i in range(len(w)):
        x1, x2 = ax2.X(edges[i]), ax2.X(edges[i + 1])
        f.rect(x1 + 3, ax2.Y(w[i]), x2 - x1 - 6, ax2.B - ax2.Y(w[i]), C['b'] if mode == 'color' else '#9A9A9A', C['k'], 1.6)
    f.text(ax2.L - 150, ax2.T - 40, '등급별 무게 (%)', FS_S, 'start', P['text'], 400, False)
    f.text((ax2.L + ax2.R) / 2, ax2.B + 92, 'φ (등급 너비 0.5)', FS_S, 'middle', P['text'], 400, False)
    note(f, 150, 1440, '시연값(두 정규 성분의 혼합, 8.5절). 곡선은 표의 누적 %를 선으로 이은 것이고 점은 등급 경계이다. 마름모는 φ16, φ50, φ84를 선형 보간으로 읽은 값이다.')
    return f


# ---------------------------------------------------------------- 그림 6: Brune 곡선
def fig_brune(mode):
    f, P = base(mode, 1150.0)
    C = cols(mode)
    ax = Ax(f, 190.0, 90.0, 1220.0, 790.0, 0.01, 1.0, 50, 100, xlog=True)
    ax.frame([0.01, 0.1, 1.0], [50, 60, 70, 80, 90, 100], '%g', '%d')
    for v in (0.02, 0.03, 0.05, 0.2, 0.3, 0.5):
        f.line(ax.X(v), ax.B, ax.X(v), ax.B + 6, P['frame'], 1.5)
    vq = np.logspace(-2, 0, 200)
    te = 100 * K.brune_te(vq, np.ones_like(vq))
    for i in range(len(vq) - 1):
        f.line(ax.X(vq[i]), ax.Y(te[i]), ax.X(vq[i + 1]), ax.Y(te[i + 1]), C['b'], 4.0)
    t4 = rd('hu2009-table4.csv')
    for r in t4:
        V, Q = float(r['V_km3']), float(r['Q_km3yr'])
        x, y = V / Q, 100 * float(K.brune_te(V, Q))
        kind = 'sq' if r['name'].startswith('TGD') else ('tri' if r['name'] == 'Cascade' else 'dot')
        f.marker(ax.X(x), ax.Y(y), kind, 1.0, C['k'] if kind != 'tri' else C['a'])
    # 본문 73 %
    vq73 = 436.0 and (0.05 / (1 - 0.73)) ** 2
    f.line(ax.L, ax.Y(73), ax.X(vq73), ax.Y(73), C['a'], 2.5, '12 8')
    f.line(ax.X(vq73), ax.Y(73), ax.X(vq73), ax.B, C['a'], 2.5, '12 8')
    f.text(ax.X(0.0105), ax.Y(73) + 40, '본문의 73 %', FS_I, 'start', C['a'], 700)
    f.text(ax.X(vq73) + 16, ax.B - 16, 'V/Q = %.4f' % vq73, FS_I, 'start', C['a'], 400)
    f.line(ax.L, ax.Y(75.44), ax.X(0.2), ax.Y(75.44), C['c'], 2.5, '4 6')
    f.text(ax.X(0.2) + 14, ax.Y(75.44) + 10, '수지로 얻은 포획 효율 75.4 %', FS_I, 'start', C['c'], 700)
    xx, yy = 0.0312, 71.69
    f.text(ax.X(xx) + 24, ax.Y(yy) + 46, '삼협댐 139 m: 71.69 %', FS_I, 'start', C['k'], 700)
    f.text(ax.L - 150, ax.T - 30, '포획 효율 TE (%)', FS_S, 'start', P['text'], 400, False)
    f.text((ax.L + ax.R) / 2, ax.B + 92, 'V/Q (저수량 / 연 유입량, 로그 눈금)', FS_S, 'middle', P['text'], 400, False)
    ly = ax.B + 150
    f.marker(170, ly - 8, 'dot', 1.0, C['k']); f.text(196, ly, '금사강 댐 4개', FS_I, 'start', P['text'], 400, False)
    f.marker(470, ly - 8, 'tri', 1.0, C['a']); f.text(500, ly, '네 댐 합계', FS_I, 'start', P['text'], 400, False)
    f.marker(740, ly - 8, 'sq', 1.0, C['k']); f.text(766, ly, '삼협댐 세 수위', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 60, '곡선은 TE = 1 - 0.05/sqrt(V/Q). 점은 Hu 등(2009) 표 4의 V와 Q로 이 책이 계산한 값이다.')
    return f


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in (('fig-ch08-cia-v1', fig_cia), ('fig-ch08-ack-v1', fig_ack), ('fig-ch08-mix-v1', fig_mix),
                       ('fig-ch08-tri-v1', fig_tri), ('fig-ch08-grain-v1', fig_grain), ('fig-ch08-brune-v1', fig_brune)):
            f = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, '경고:', w)
