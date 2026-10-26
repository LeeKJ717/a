# -*- coding: utf-8 -*-
"""제2권 6장 그림 6장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch06 의 실행 결과 파일(json, csv)과 로그에서 읽는다.
  fig-ch06-lag-v1    : 구간별 상관의 lag 지도(실제 자료 co021의 날짜 오류 계열, 시연값 자료의 같은 종류 오류 계열)
  fig-ch06-detrend-v1: 한 계열(T01A)의 너비와 표준화 곡선 네 가지(시연값)
  fig-ch06-chron-v1  : 연대기(음의 지수, 시연값)와 참 기후, 아래에 코어 수
  fig-ch06-eps-v1    : EPS 대 나무 수(식), 제1권 표 1의 두 점
  fig-ch06-recon-v1  : 복원과 참 기후(시연값), 얕은 세기의 오차
  fig-ch06-mc-v1     : 분할 검증의 CE 대 앞 세기의 참값 대비 RE(몬테카를로 1000회, 시연값)
사용: python figs-ch06.py | tee figs-ch06.log"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geomap import Fig, FS, FS_S, FS_I, tw
ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch06')
OUT = os.path.join(ROOT, 'fig')


def J(name):
    return json.load(open(os.path.join(CODE, name), encoding='utf-8'))


def base(mode, H):
    f = Fig(1300.0, H, mode)
    f.rect(0, 0, 1300.0, H, '#FFFFFF')
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


def cols(mode, P):
    if mode == 'color':
        return dict(a=P['hot'], b=P['river'], c=P['text'], d=P['site'])
    return dict(a='#111111', b='#777777', c='#333333', d='#999999')


def path(f, pts, stroke, sw, dash=None):
    """pts: [(x, y) 또는 None]. None에서 선을 끊는다."""
    seg = []
    out = []
    for p in pts + [None]:
        if p is None:
            if len(seg) > 1:
                out.append('M' + ' L'.join('%.1f,%.1f' % q for q in seg))
            seg = []
        else:
            seg.append(p)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    for s in out:
        f.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"%s/>' % (s, stroke, sw, d))


def axes(f, P, L, T, R, B, xr, yr, xt, yt, xl, yl, xfmt='%g', yfmt='%g', grid=True, ylab_dx=0):
    X = lambda v: L + (v - xr[0]) / (xr[1] - xr[0]) * (R - L)
    Y = lambda v: B - (v - yr[0]) / (yr[1] - yr[0]) * (B - T)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in yt:
        if grid:
            f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.line(L - 8, Y(v), L, Y(v), P['frame'], 2.0)
        f.text(L - 14, Y(v) + 10, yfmt % v, FS_I, 'end', P['soft'], 400, False)
    for v in xt:
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, xfmt % v, FS_I, 'middle', P['soft'], 400, False)
    if xl:
        f.text((L + R) / 2, B + 92, xl, FS_S, 'middle', P['text'], 400, False)
    if yl:
        f.text(L - 150 + ylab_dx, T - 30, yl, FS_S, 'start', P['text'], 400, False)
    return X, Y


def lerp(c0, c1, t):
    t = max(0.0, min(1.0, t))
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(int(round(a[k] + (b[k] - a[k]) * t)) for k in range(3))


def legend(f, P, items, x, y, gap=0):
    """items: (표지 종류, 색, 대시, 글). 한 줄씩 아래로."""
    for k, (kind, col, dash, txt) in enumerate(items):
        yy = y + k * 44
        if kind == 'line':
            f.line(x, yy - 8, x + 70, yy - 8, col, 5.0, dash)
        elif kind == 'dot':
            f.marker(x + 35, yy - 8, 'dot', 0.8, col, '#222222' if col == '#FFFFFF' else None)
        elif kind == 'sq':
            f.marker(x + 35, yy - 8, 'sq', 0.8, col)
        f.text(x + 90, yy, txt, FS_I, 'start', P['text'], 400, False)


# ====================================================================== 그림 1
def fig_lag(mode):
    S = J('crossdate-segs.json')
    lagN = 21
    blocks = [('A_shift', '실제 자료 co021, 계열 %s: 날짜를 3년 어긋나게 한 경우' % S['A_shift']['name'], 16.0),
              ('B_shift', '시연값 자료, 계열 %s: 같은 방식으로 3년 어긋나게 한 경우' % S['B_shift']['name'], 28.0)]
    H = 90 + sum(len(S[k]['segs']) * ch + 250 for k, _, ch in blocks) + 330
    f, P = base(mode, H)
    c0 = '#FFFFFF'
    c1 = P['hot'] if mode == 'color' else '#111111'
    L, R = 190.0, 1240.0
    cw = (R - L) / lagN
    y = 130.0
    for key, title, ch in blocks:
        d = S[key]
        segs = d['segs']
        lags = d['lags']
        f.text(L - 150, y - 54, title, FS_S, 'start', P['text'], 700, False)
        T = y
        B = T + len(segs) * ch
        for i, sg in enumerate(segs):
            rr = sg['r']
            best = max(range(lagN), key=lambda j: rr[j])
            for j in range(lagN):
                f.rect(L + j * cw, T + i * ch, cw, ch, lerp(c0, c1, max(0.0, rr[j]) / 0.95), 'none', 0)
            f.rect(L + best * cw, T + i * ch, cw, ch, 'none', '#111111', 2.6)
        f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
        zero = lags.index(0)
        f.line(L + (zero + 0.5) * cw, T - 14, L + (zero + 0.5) * cw, T, P['text'], 3.0)
        f.text(L - 150, T - 14, '구간 첫 해', FS_I, 'start', P['soft'], 400, False)
        step = max(1, len(segs) // 6)
        for i in range(0, len(segs), step):
            yy = T + (i + 0.5) * ch
            f.line(L - 8, yy, L, yy, P['frame'], 2.0)
            f.text(L - 14, yy + 10, '%d' % segs[i]['a'], FS_I, 'end', P['soft'], 400, False)
        for lg in (-10, -5, 0, 5, 10):
            xx = L + (lags.index(lg) + 0.5) * cw
            f.line(xx, B, xx, B + 10, P['frame'], 2.0)
            f.text(xx, B + 44, '%d' % lg, FS_I, 'middle', P['soft'], 400, False)
        f.text((L + R) / 2, B + 92, '맞춰 보는 이동 lag (년). 위의 짧은 표시가 lag 0', FS_S, 'middle', P['text'], 400, False)
        y = B + 190
    # 색 눈금
    for k in range(6):
        v = k * 0.19
        f.rect(L + k * 90, y - 28, 90, 36, lerp(c0, c1, v / 0.95), P['frame'], 1.5)
        f.text(L + k * 90 + 45, y + 44, '%.2f' % v, FS_I, 'middle', P['text'], 400, False)
    ny = note(f, L - 40, y + 130, '각 줄은 50년 구간 하나이다(25년씩 옮김). 칸은 그 구간에서 이 계열을 나머지 계열의 하나 뺀 마스터와 lag만큼 밀어 견준 상관이다. 테두리 칸이 그 줄의 최고 상관이다. 위쪽(실제 자료)은 오류를 넣은 해 전체에서 같은 lag(-3)가 가장 크지만, 아래쪽(시연값)은 최고 lag가 구간마다 흔들리고 몇 구간에서만 -3이 보인다.', 1100)
    f.h = ny + 30
    return f


# ====================================================================== 그림 2
def fig_detrend(mode):
    D = J('detrend-fig.json')
    yrs = D['years']
    raw = D['raw']
    cur = D['curves']
    f, P = base(mode, 1500.0)
    C = cols(mode, P)
    ymax = 2.2
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    X, Y = axes(f, P, L, T, R, B, (1600, 2013), (0, ymax), (1600, 1700, 1800, 1900, 2000), (0, 0.5, 1.0, 1.5, 2.0), '연도', '너비 또는 곡선 (mm)', '%d', '%.1f')
    ok = [i for i, v in enumerate(raw) if v is not None]
    i0, i1 = ok[0], ok[-1]
    path(f, [(X(yrs[i]), Y(min(raw[i], ymax))) if raw[i] is not None else None for i in range(len(yrs))], '#9AA5AB' if mode == 'color' else '#BBBBBB', 2.0)
    spec = [('ModNegExp', C['a'], None, 5.0), ('Spline67', C['b'], '16 8', 5.0), ('Spline32', C['d'], '4 7', 5.0), ('Mean', C['c'], '26 8 4 8', 4.0)]
    for nm, col, dash, sw in spec:
        path(f, [(X(yrs[i]), Y(min(cur[nm][i], ymax))) if cur[nm][i] is not None else None for i in range(len(yrs))], col, sw, dash)
    legend(f, P, [('line', '#9AA5AB' if mode == 'color' else '#BBBBBB', None, '측정한 너비 (시연값, T01A)'),
                  ('line', C['a'], None, '음의 지수 곡선'), ('line', C['b'], '16 8', '스플라인 67%'),
                  ('line', C['d'], '4 7', '스플라인 32년'), ('line', C['c'], '26 8 4 8', '평균(수평선)')], 170, B + 150)
    ny = note(f, 170, B + 390, '가장 긴 계열 T01A(414년)의 너비와 네 가지 표준화 곡선. 계열은 가상의 값(시연값)이다. 32년 스플라인은 너비의 10년 단위 변동까지 곡선이 따라가므로 지수에서 그만큼의 신호를 지운다. 67% 스플라인은 첫머리에서 측정값보다 낮게 시작한다(곡선의 끝 효과). 너비가 2.2 mm를 넘는 해는 그림에서 잘렸다.', 1000)
    f.h = ny + 30
    return f


# ====================================================================== 그림 3
def fig_chron(mode):
    D = J('chron-fig.json')
    yrs = D['years']
    std = [v for v in D['std']]
    ok = [v for v in std if v is not None]
    m = sum(ok) / len(ok)
    sd = math.sqrt(sum((v - m) ** 2 for v in ok) / (len(ok) - 1))
    z = [None if v is None else (v - m) / sd for v in std]
    tz = D['truth_z']
    dep = D['depth']
    f, P = base(mode, 1330.0)
    C = cols(mode, P)
    L, T, R, B = 190.0, 90.0, 1240.0, 640.0
    X, Y = axes(f, P, L, T, R, B, (1600, 2013), (-4, 4), (1600, 1700, 1800, 1900, 2000), (-3, -2, -1, 0, 1, 2, 3), '', '표준화한 값 (표준편차 단위)', '%d', '%d')
    path(f, [(X(yrs[i]), Y(tz[i])) for i in range(len(yrs))], C['c'], 3.0, '16 8' if mode == 'bw' else None)
    path(f, [(X(yrs[i]), Y(z[i])) if z[i] is not None else None for i in range(len(yrs))], C['a'], 3.0)
    f.line(X(1956), T, X(1956), B, P['frame'], 2.0, '8 8')
    f.text(X(1956) - 10, T + 40, '관측 1956~', FS_I, 'end', P['soft'], 400, False)
    T2, B2 = 800.0, 1000.0
    X2, Y2 = axes(f, P, L, T2, R, B2, (1600, 2013), (0, 80), (1600, 1700, 1800, 1900, 2000), (0, 20, 40, 60, 80), '연도', '연도별 코어 수', '%d', '%d')
    path(f, [(X2(yrs[i]), Y2(dep[i])) for i in range(len(yrs))], C['b'], 3.5)
    legend(f, P, [('line', C['a'], None, '연대기(음의 지수, 이중 가중 평균) - 표준화'), ('line', C['c'], '16 8' if mode == 'bw' else None, '참 기후(시연값을 만든 쪽의 값) - 표준화')], 170, B2 + 150)
    note(f, 170, B2 + 270, '시연값 자료(71코어)로 만든 연대기와 그 자료를 만든 가상 기후의 비교. 연대기와 참 기후의 전 기간 상관은 0.769이다(detrend-chron.log). 1600년대에는 코어가 1~7개뿐이어서 연대기가 참값에서 자주 벗어난다.', 1000)
    f.h = B2 + 270 + 38 * 3 + 20
    return f


# ====================================================================== 그림 4
def fig_eps(mode):
    f, P = base(mode, 1230.0)
    C = cols(mode, P)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    X, Y = axes(f, P, L, T, R, B, (1, 45), (0.3, 1.0), (5, 10, 15, 20, 25, 30, 35, 40, 45), (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0), '나무 수 n (한 해에 쓰인 나무)', 'EPS = n r / ((n-1) r + 1)', '%d', '%.1f')
    eps = lambda n, r: n * r / ((n - 1) * r + 1)
    f.line(L, Y(0.85), R, Y(0.85), '#000000' if mode == 'bw' else P['text'], 2.5, '18 8')
    f.text(R - 10, Y(0.85) - 14, 'EPS 0.85', FS_I, 'end', P['text'], 700, False)
    ser = [(0.22, C['a'], None, '평균 상관 r = 0.22 (제1권 표 1의 std, rbar.bt)'), (0.28, C['b'], '16 8', 'r = 0.28 (표 1의 RES, rbar.bt)'), (0.257, C['d'], '4 7', 'r = 0.257 (시연값 자료의 rbar.eff)')]
    for r, col, dash, _ in ser:
        path(f, [(X(n / 4.0), Y(eps(n / 4.0, r))) for n in range(4, 181)], col, 4.5, dash)
    f.marker(X(11), Y(eps(11, 0.22)), 'dot', 1.3, C['a'])
    f.marker(X(15), Y(eps(15, 0.28)), 'sq', 1.3, C['b'])
    f.text(X(11) + 18, Y(eps(11, 0.22)) + 44, 'n=11, r=0.22: %.3f' % eps(11, 0.22), FS_I, 'start', P['text'], 700, False)
    f.text(X(15) - 18, Y(eps(15, 0.28)) - 24, 'n=15, r=0.28: %.3f' % eps(15, 0.28), FS_I, 'end', P['text'], 700, False)
    legend(f, P, [('line', c, d, t) for _, c, d, t in ser], 170, B + 150)
    note(f, 170, B + 320, '식은 제1권 계산 11-14와 같다. 점 두 개는 표 1이 EPS 0.85를 처음 넘는다고 적은 해의 나무 수(std 11그루, RES 15그루)에 전 기간 평균 상관을 넣은 값이다. 11그루에서 EPS 0.85가 되려면 r = 0.340이 필요하다(lyu-recheck.log).', 1000)
    f.h = B + 320 + 38 * 3 + 20
    return f


# ====================================================================== 그림 5
def fig_recon(mode):
    R5 = J('recon-fig.json')
    yrs = R5['years']
    est, tr, obs = R5['est'], R5['truth'], R5['obs']
    f, P = base(mode, 1330.0)
    C = cols(mode, P)
    L, T, R, B = 190.0, 90.0, 1240.0, 640.0
    X, Y = axes(f, P, L, T, R, B, (1600, 2013), (6.0, 9.5), (1600, 1700, 1800, 1900, 2000), (6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5), '', '4~7월 기온 (섭씨, 시연값)', '%d', '%.1f')
    path(f, [(X(yrs[i]), Y(tr[i])) for i in range(len(yrs))], C['c'], 3.0, '16 8' if mode == 'bw' else None)
    path(f, [(X(yrs[i]), Y(est[i])) if est[i] is not None else None for i in range(len(yrs))], C['a'], 3.0)
    ob = [(X(yrs[i]), Y(obs[i])) for i in range(len(yrs)) if obs[i] is not None]
    for x, y in ob:
        f.marker(x, y, 'dot', 0.45, C['b'])
    f.rect(X(1600), T, X(1699) - X(1600), B - T, '#7D7255' if mode == 'color' else '#555555', 'none', 0, 'opacity="0.12"')
    f.text(X(1650), T + 40, '1600~1699', FS_I, 'middle', P['text'], 700, False)
    f.text(X(1650), T + 80, '코어 평균 7개', FS_I, 'middle', P['text'], 400, False)
    # 아래: 오차
    err = [None if est[i] is None else est[i] - tr[i] for i in range(len(yrs))]
    T2, B2 = 800.0, 1010.0
    X2, Y2 = axes(f, P, L, T2, R, B2, (1600, 2013), (-1.5, 1.5), (1600, 1700, 1800, 1900, 2000), (-1.0, 0.0, 1.0), '연도', '복원 - 참값 (섭씨)', '%d', '%.1f')
    path(f, [(X2(yrs[i]), Y2(err[i])) if err[i] is not None else None for i in range(len(yrs))], C['a'], 2.5)
    legend(f, P, [('line', C['a'], None, '복원(보정 1956~2013, 음의 지수 연대기)'), ('line', C['c'], '16 8' if mode == 'bw' else None, '참 기후(시연값을 만든 쪽의 값)'), ('dot', C['b'], None, '기상 관측(1956~2013, 시연값)')], 170, B2 + 150)
    note(f, 170, B2 + 320, '위: 복원과 참 기후. 아래: 두 값의 차이. 참값을 아는 시연값 자료에서만 이 그림을 그릴 수 있다. 1600~1699의 RE(참값)는 -0.625이고 1800~1899는 0.802이다(reconstruct.log).', 1000)
    f.h = B2 + 320 + 38 * 3 + 20
    return f


# ====================================================================== 그림 6
def fig_mc(mode):
    M = J('reconstruct-mc.json')
    log = open(os.path.join(CODE, 'reconstruct-mc.log'), encoding='utf-8').read()
    npass = [int(x) for x in re.findall(r'RE와 CE가 모두 0보다 큰 되풀이: (\d+)회', log)]
    nneg = [int(x) for x in re.findall(r'검증 통과 여부와 상관없이 1600~1699의 RE\(참값\) < 0: (\d+)회', log)]
    f, P = base(mode, 1900.0)
    C = cols(mode, P)
    L, R = 190.0, 1240.0
    xlo, xhi, ylo, yhi = -0.6, 1.0, -3.0, 1.0
    y = 130.0
    for k, (b, lab) in enumerate((('0.085', '공통 신호 b = 0.085'), ('0.06', '공통 신호 b = 0.060'))):
        T, B = y, y + 560.0
        X, Y = axes(f, P, L, T, R, B, (xlo, xhi), (ylo, yhi), (-0.5, 0.0, 0.5, 1.0), (-3, -2, -1, 0, 1), '검증 CE (두 방향 중 작은 값)', '1600~1699의 RE(참값)', '%.1f', '%d')
        f.text(L + 14, T + 44, lab, FS_S, 'start', P['text'], 700, False)
        f.line(X(0), T, X(0), B, P['text'], 2.2, '10 8')
        f.line(L, Y(0), R, Y(0), P['text'], 2.2, '10 8')
        n_ok = 0
        n_pass = 0
        n_pass_neg = 0
        n_neg = 0
        for r in M[b]:
            ce, re_ = r['ce'], r['ret_e']
            passed = r['re'] > 0 and ce > 0
            n_pass += passed
            n_neg += re_ < 0
            n_pass_neg += passed and re_ < 0
            x = max(xlo + 0.01, min(xhi - 0.01, ce))
            yv = max(ylo + 0.03, min(yhi - 0.03, re_))
            f.circle(X(x), Y(yv), 5.5, (C['a'] if re_ < 0 else C['b']) if mode == 'color' else ('#222222' if re_ < 0 else '#FFFFFF'), '#222222' if mode == 'bw' else 'none', 1.2)
        want_p = npass[k]
        want_n = nneg[k]
        assert n_pass == want_p and n_neg == want_n, (b, n_pass, want_p, n_neg, want_n)
        f.text(R - 14, T + 44, '검증 통과 %d회 중 앞 세기 RE(참값)가 음수: %d회' % (n_pass, n_pass_neg), FS_I, 'end', P['text'], 700, False)
        print('  b=%s: 통과 %d, 앞 세기 음수 %d, 통과이면서 음수 %d (로그와 일치)' % (b, n_pass, n_neg, n_pass_neg))
        y = B + 150
    legend(f, P, [('dot', C['a'], None, '앞 세기(1600~1699)의 RE(참값)가 0보다 작은 되풀이'), ('dot', C['b'] if mode == 'color' else '#FFFFFF', None, '0 이상인 되풀이')], 170, y)
    ny = note(f, 170, y + 130, '시연값 자료를 만드는 과정을 1000번 되풀이해(시드를 바꿔) 매번 같은 보정·검증을 한 결과이다. 가로는 58년 안에서의 분할 검증 CE, 세로는 같은 복원을 참 기후와 견준 1600~1699의 RE이다. 두 값 사이에 관계가 없다는 것이 이 그림의 요점이다(순위 상관은 -0.02~-0.03, reconstruct-mc.log). 그림의 범위 밖 값은 가장자리에 찍었다.', 1000)
    f.h = ny + 30
    return f


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in (('fig-ch06-lag-v1', fig_lag), ('fig-ch06-detrend-v1', fig_detrend), ('fig-ch06-chron-v1', fig_chron),
                       ('fig-ch06-eps-v1', fig_eps), ('fig-ch06-recon-v1', fig_recon), ('fig-ch06-mc-v1', fig_mc)):
            f = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, '높이', round(f.h), '경고:', w)
