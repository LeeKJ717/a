# -*- coding: utf-8 -*-
"""제2권 12장 그림 5장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch12 의 실행 결과(json)와 sim-core-v1.py 의 입력에서 읽는다.
  fig-ch12-sealevel-v1: 시연 모형의 수위 입력(제1권 2장의 점들)
  fig-ch12-shore-v1   : 경사별 해안선 위치의 시간 변화 (p01)
  fig-ch12-diff-v1    : 확산 방정식의 격자 풀이와 해석해 (p02)
  fig-ch12-sens-v1    : 땅 높이 변화율에 따른 해안선 후퇴, 세 경사 (p01 격자)
  fig-ch12-grid-v1    : 매개변수 격자 탐색의 어긋남 지도 (p03)
이 그림들은 이 책이 만든 시연 모형의 결과이며 실제 한반도·황해의 해안선이나 퇴적이 아니다.
사용: python figs-ch12.py"""
import importlib.util, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figkit import *
ROOT = os.path.dirname(HERE); CODE = os.path.join(ROOT, 'ms', 'code', 'ch12'); OUT = os.path.join(ROOT, 'fig')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
_s = importlib.util.spec_from_file_location('sc', os.path.join(CODE, 'sim-core-v1.py')); sc = importlib.util.module_from_spec(_s); _s.loader.exec_module(sc)
L, T, R, B = 200.0, 90.0, 1240.0, 700.0

def fig_sealevel(mode):
    f, P = base(mode); cols = series_colors(mode)
    X = lin(16, 0, L, R); Y = lin(-90, 10, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [-80, -60, -40, -20, 0])
    xticks(f, B, X, [16, 14, 12, 10, 8, 6, 4, 2, 0], None, T, False)
    f.text(L - 160, T - 30, '수위 (m, 현재 = 0)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '시간 (ka, 천 년 전)', FS_S, 'middle', P['text'], 400, False)
    pts = [(X(t), Y(h)) for t, h in zip(sc.SL_T[::-1], sc.SL_H[::-1])]
    dash_line(f, pts, cols[0], 4.0)
    for (t, h) in zip(sc.SL_T, sc.SL_H): f.marker(X(t), Y(h), 'dot', 1.1, cols[0])
    lab = {16.0: (-18, -26, 'start'), 9.0: (-16, -26, 'end'), 7.0: (-16, -26, 'end'), 5.0: (-4, -26, 'end'), 0.0: (-12, -28, 'end')}
    for t, h in zip(sc.SL_T, sc.SL_H):
        dx_, dy_, an = lab[t]
        f.text(X(t) + dx_, Y(h) + dy_, '%g ka, %.1f m' % (t, h), FS_I, an, P['text'], 400, True)
    segs = list(zip(sc.SL_T[::-1], sc.SL_H[::-1]))
    for (t0, h0), (t1, h1) in zip(segs, segs[1:]):
        rate = (h1 - h0) / (t0 - t1)
        f.text((X(t0) + X(t1)) / 2 + 30, (Y(h0) + Y(h1)) / 2 + 64, '%.2f mm/yr' % rate, FS_I, 'start', cols[1], 700, True)
    note(f, 150, B + 150, '제1권 2장 2.4절이 소개한 Clark 등의 모형 결과(한국 남단, Bloom과 Park, 1985 경유)의 점 네 개(16, 9, 7, 5 ka)와, 5 ka 이후 0.48 mm/yr 일정 상승으로 0 m에 이른다는 서술이다. 점 사이는 직선으로 이었다(제1권 2.9.3절). 이 책이 만든 시연 모형의 입력이며 실측 곡선이 아니다.')
    return f

def fig_shore(mode):
    f, P = base(mode); cols = series_colors(mode); d = J('p01-shoreline.json')['paths']; ts = d['t']
    X = lin(9, 0, L, R); Y = logmap(0.5, 300.0, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [1, 10, 100], ['1', '10', '100'])
    xticks(f, B, X, [9, 8, 7, 6, 5, 4, 3, 2, 1, 0], None, T, False)
    f.text(L - 160, T - 30, '해안선 위치 x (km, 로그 눈금)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '시간 (ka)', FS_S, 'middle', P['text'], 400, False)
    spec = [('1/115', '경사 1/115', cols[2], None), ('1/344', '경사 1/344', cols[0], None), ('1/3500', '경사 1/3500', cols[1], None)]
    for k, nm, c, dash in spec:
        dash_line(f, [(X(t), Y(v)) for t, v in zip(ts, d[k])], c, 4.0, dash)
        f.text(X(0) - 12, Y(d[k][-1]) - 16, nm, FS_I, 'end', c, 700, True)
    tw_ = J('p01-shoreline.json')['two_slope']
    dash_line(f, [(X(t), Y(v)) for t, v in zip(tw_['t'], tw_['xs'])], P['text'], 3.0, '16 8')
    f.text(X(4.9), Y(26.0), '두 경사 (10 km 안쪽 1/344, 바깥쪽 1/3500)', FS_I, 'start', P['text'], 400, True)
    ly = B + 150
    note(f, 150, ly, '수위는 그림 12-1, 땅은 x = 0 에서 -40 m인 직선(경사는 제1권 3장의 1/344, 1/115와 계산 A-2의 1/3500). 해안선 = 땅 높이가 수위와 같아지는 위치(실습 12-1). 같은 수위 상승에서 경사가 30배 완만하면 후퇴 거리가 30배 길다. 시연 모형의 결과이며 실제 해안선이 아니다.')
    return f

def fig_diff(mode):
    f, P = base(mode); cols = series_colors(mode); d = J('p02-diffusion.json')['profiles']
    X = lin(40, 160, L, R); Y = lin(-0.05, 1.05, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [0, 0.25, 0.5, 0.75, 1.0])
    xticks(f, B, X, [40, 60, 80, 100, 120, 140, 160], None, T, False)
    f.text(L - 160, T - 30, '퇴적 두께 D (m)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '거리 x (km)', FS_S, 'middle', P['text'], 400, False)
    xs = d['x']
    for i, (t_, num, ana) in enumerate(zip(d['times'], d['num'], d['ana'])):
        c = cols[i % 4]
        pts = [(X(x), Y(a)) for x, a in zip(xs, ana) if 40 <= x <= 160]
        dash_line(f, pts, c, 3.0)
        for j in range(0, len(xs), 8):
            if 40 <= xs[j] <= 160: f.marker(X(xs[j]), Y(num[j]), ['dot', 'sq', 'dia', 'tri'][i], 0.75, c)
        f.text(X(100 + 2.2 * math.sqrt(10 * t_)) + 10, Y(0.5 * math.erfc(2.2 / 2)) - 10, 't = %g ka' % t_, FS_I, 'start', c, 700, True) if False else None
    ly = B + 150
    for i, t_ in enumerate(d['times']):
        x0 = 170 + i * 270
        f.marker(x0, ly - 8, ['dot', 'sq', 'dia', 'tri'][i], 0.9, cols[i % 4]); f.text(x0 + 24, ly, 't = %g ka' % t_, FS_I, 'start', P['text'], 400, False)
    f.line(170, ly + 38, 230, ly + 38, P['soft'], 3.0); f.text(244, ly + 46, '선: 해석해 0.5 erfc((x - 100) / (2 sqrt(kappa t)))   표지: 격자 계산(8칸마다)', FS_I, 'start', P['text'], 400, False)
    cv = J('p02-diffusion.json')['conv']
    note(f, 150, ly + 100, 'kappa = 10 km^2/ka, 처음 D = 1 m 계단. 격자 간격 %.2f km의 풀이이며, 간격을 절반씩 줄이면 최대 오차가 %.1e, %.1e, %.1e, %.1e m 으로 줄어 차수 %.2f 이다(실습 12-2). 시연 모형이다.' % (0.5, *cv['err'], cv['orders'][-1]))
    return f

def fig_sens(mode):
    f, P = base(mode); cols = series_colors(mode); g = J('p01-shoreline.json')['grid']; us = g['u']; ln = g['lines']
    X = lin(-2, 10, L, R); Y = lin(-50, 130, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [-40, 0, 40, 80, 120])
    xticks(f, B, X, [-2, 0, 2, 4, 6, 8, 10], ['-2', '0', '+2', '+4', '+6', '+8', '+10'], T, False)
    f.text(L - 160, T - 30, '9 ka에서 5 ka까지 해안선 후퇴 (km, 음수 = 전진)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '땅 높이 변화율 u (mm/yr, 융기 +)', FS_S, 'middle', P['text'], 400, False)
    f.line(L, Y(0), R, Y(0), P['text'], 2.5)
    uz = g['u_zero']
    f.line(X(uz), T, X(uz), B, P['soft'], 2.5, '10 8')
    f.text(X(uz) - 12, T + 40, 'u = %.3f 이면 후퇴 0' % uz, FS_I, 'end', P['soft'], 700, True)
    spec = [('1/115', cols[2], 'tri'), ('1/344', cols[0], 'dot'), ('1/3500', cols[1], 'sq')]
    for (k, c, kind) in spec:
        pts = [(X(u), Y(v)) for u, v in zip(us, ln[k])]
        dash_line(f, pts, c, 4.0)
        for i in range(0, len(us), 8): f.marker(X(us[i]), Y(ln[k][i]), kind, 0.9, c)
    pos = {'1/3500': (X(0.0) + 14, None, -22), '1/344': (X(0.0) + 14, None, -40), '1/115': (X(-1.0), Y(0) + 76, 0)}
    for (k, c, kind) in spec:
        v0 = ln[k][us.index(0.0)]
        px, py, dy = pos[k]
        f.text(px, (Y(v0) + dy) if py is None else py, '경사 %s: u = 0 에서 %.1f km' % (k, v0), FS_I, 'start', c, 700, True)
    ly = B + 150
    note(f, 150, ly, '수위는 그림 12-1(9 ka -31.7 m, 5 ka -2.4 m), 시작 높이 x = 0 에서 -100 m인 직선 지형. 땅이 u로 오르내리면 상대 수위가 u x 4 m 달라져 후퇴 = (29.3 - 4u) / (1000 s) km 가 된다(실습 12-1, 격자 60 x 49). 같은 u라도 경사가 완만할수록 km로 환산한 영향이 크다. 시연 모형이다.')
    return f

def fig_grid(mode):
    f, P = base(mode); d = J('p03-grid.json'); cols = series_colors(mode)
    kap, qq, chi = d['kappa'], d['q'], d['chi2']
    Lh, Rh = 200.0, 1090.0
    X = logmap(1, 20, Lh, Rh); Y = lin(-1.5, 151.5, B, T)
    cmin = d['best']['chi2']
    def cls(c):
        dc = c - cmin
        return 0 if dc <= 2.30 else 1 if dc <= 6.18 else 2 if dc <= 11.83 else 3
    shade = {0: 0.95, 1: 0.65, 2: 0.35, 3: 0.08}
    for i in range(len(kap)):
        a = math.sqrt(kap[i - 1] * kap[i]) if i > 0 else kap[0] / (kap[1] / kap[0]) ** 0.5
        b = math.sqrt(kap[i] * kap[i + 1]) if i < len(kap) - 1 else kap[-1] * (kap[-1] / kap[-2]) ** 0.5
        for j in range(len(qq)):
            ya = (qq[j - 1] + qq[j]) / 2 if j > 0 else qq[0] - 1.5
            yb = (qq[j] + qq[j + 1]) / 2 if j < len(qq) - 1 else qq[-1] + 1.5
            f.rect(X(a), Y(yb), X(b) - X(a) + 0.8, Y(ya) - Y(yb) + 0.8, ramp(mode, shade[cls(chi[i][j])]))
    frame(f, Lh, T, Rh, B)
    yticks(f, Lh, Rh, Y, [0, 50, 100, 150], grid=False)
    xticks(f, B, X, [1, 2, 5, 10, 20], None, T, False)
    f.text(Lh - 160, T - 30, '공급 q (m km/ka)', FS_S, 'start', P['text'], 400, False)
    f.text((Lh + Rh) / 2, B + 92, '확산계수 kappa (km^2/ka, 로그 눈금)', FS_S, 'middle', P['text'], 400, False)
    tr, bs = d['truth'], d['best']
    f.marker(X(tr['kappa']), Y(tr['q']), 'star', 1.3, '#FFFFFF' if mode == 'color' else '#FFFFFF', P['text'])
    f.marker(X(bs['kappa']), Y(bs['q']), 'dia', 1.0, P['text'], '#FFFFFF')
    ly = B + 150
    labs = ['chi2가 최소 + 2.30 이하 (68% 영역)', '최소 + 6.18 이하 (95%)', '최소 + 11.83 이하 (99.7%)', '그 밖']
    for k in range(4):
        x0 = 170 + (k % 2) * 520; y0 = ly + (k // 2) * 44
        f.rect(x0, y0 - 26, 28, 28, ramp(mode, shade[k]), P['frame'], 1.5); f.text(x0 + 42, y0, labs[k], FS_I, 'start', P['text'], 400, False)
    y1 = ly + 88
    f.marker(184, y1 - 10, 'star', 1.0, '#FFFFFF', P['text']); f.text(210, y1, '정답 (kappa %.1f, q %.1f)' % (tr['kappa'], tr['q']), FS_I, 'start', P['text'], 400, False)
    f.marker(704, y1 - 10, 'dia', 0.9, P['text'], '#FFFFFF'); f.text(730, y1, '최소 chi2 = %.2f (kappa %.2f, q %.1f)' % (bs['chi2'], bs['kappa'], bs['q']), FS_I, 'start', P['text'], 400, False)
    note(f, 150, y1 + 56, '가짜 관측 4개(정답 + 잡음 %.1f km)에 모형 %d개를 맞춘 어긋남 지도이다. 68%% 영역 %d칸, 95%% 영역 %d칸, 95%% 영역 안의 log kappa와 q의 상관 %+.2f. 퇴적이 없는 모형(q = 0)의 최소 chi2는 %.0f 이다(실습 12-3). 시연이다.' % (d['noise'], d['P'], d['n68'], d['n95'], d['corr95'], d['q0_chi2_min']))
    return f

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in (('sealevel', fig_sealevel), ('shore', fig_shore), ('diff', fig_diff), ('sens', fig_sens), ('grid', fig_grid)):
            f = fn(mode)
            pth = os.path.join(OUT, 'fig-ch12-%s-v1-%s.svg' % (nm, mode))
            w = f.save(pth)
            import xml.etree.ElementTree as ET
            ET.parse(pth)          # 문서가 올바른 XML인지 검사(& 나 < 가 글자에 섞이면 여기서 실패한다)
            print('fig-ch12-%s' % nm, mode, '경고:', w)
