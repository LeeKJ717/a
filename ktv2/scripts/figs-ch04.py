# -*- coding: utf-8 -*-
"""4장 그림: fig/fig-ch04-이름-v1-{color,bw}.svg 두 벌.
그림의 값은 ms/code/ch04/results/*.json(실습 스크립트가 저장한 결과)과, 같은 시드로 다시 계산한 값이다.
글자는 8pt(29단위) 이상. 겹침·넘침은 Fig.save가 검사한다.
실행: python3 scripts/figs-ch04.py   (작업 폴더 /home/claude/book2에서)
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
for d in (HERE, '/home/claude/book/scripts'):
    if os.path.exists(os.path.join(d, 'geomap.py')):
        sys.path.insert(0, d); break
import numpy as np, scipy.signal as ss, scipy.fft as sf
import geomap as G
from geomap import Fig, FS_S, FS_I, f1
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'fig')
RES = os.path.join(ROOT, 'ms', 'code', 'ch04', 'results')
os.makedirs(OUT, exist_ok=True)
J = lambda n: json.load(open(os.path.join(RES, n)))

def base(mode, H=1000.0):
    W = 1300.0
    f = Fig(W, H, mode)
    f.rect(0, 0, W, H, '#FFFFFF')
    return f, f.P
def cols(mode):
    if mode == 'color':
        return dict(a='#3A7CA5', b='#9C4F2E', c='#8A6A2C', d='#6B7A82', e='#9DB7C6', light='#E4E9EC', band='#DCE6EC')
    return dict(a='#111111', b='#666666', c='#999999', d='#444444', e='#BBBBBB', light='#EEEEEE', band='#E4E4E4')
def axes(f, L, T, R, B, xt, yt, X, Y, xlab=None, ylab=None, xfmt=str, yfmt=str, grid=True, ylab_x=None):
    P = f.P
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in yt:
        if grid: f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8')
        f.line(L - 8, Y(v), L, Y(v), P['frame'], 2.0)
        f.text(L - 14, Y(v) + 10, yfmt(v), FS_I, 'end', P['soft'], 400, False)
    for v in xt:
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, xfmt(v), FS_I, 'middle', P['soft'], 400, False)
    if xlab: f.text((L + R) / 2, B + 92, xlab, FS_S, 'middle', P['text'], 400, False)
    if ylab: f.text(L - 120 if ylab_x is None else ylab_x, T - 24, ylab, FS_S, 'start', P['text'], 400, False)
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
def legend_line(f, x, y, color, dash, label, sw=4.0, w=70):
    f.line(x, y - 8, x + w, y - 8, color, sw, dash)
    f.text(x + w + 14, y, label, FS_I, 'start', f.P['text'], 400, False)
    return x + w + 14 + G.tw(label, FS_I) + 40

# ================================================================= 그림 1: 별칭
def fig_alias(mode):
    f, P = base(mode, 1010.0); C = cols(mode)
    L, R = 160.0, 1240.0
    X = lambda v: L + v / 0.5 * (R - L)
    rows = [('간격 1.087 a (XRF)', 1 / 0.92), ('간격 2.0 a', 2.0), ('간격 10.87 a (입도)', 10 / 0.92)]
    f.text(L, 56, '주기 3.9 a(진동수 0.256)의 사인파를 세 가지 간격으로 뽑았을 때의 주기도', FS_S, 'start', P['text'], 700, False)
    top = 110.0; rh = 230.0
    for i, (lab, dt) in enumerate(rows):
        T0 = top + i * (rh + 20); B0 = T0 + rh - 50
        fN = 0.5 / dt
        # 해상 불가 영역
        if fN < 0.5:
            f.rect(X(fN), T0, X(0.5) - X(fN), B0 - T0, C['band'], 'none', 0)
        f.rect(L, T0, R - L, B0 - T0, 'none', P['frame'], 2.0)
        n = int(2000 / dt); t = np.arange(n) * dt
        y = np.sin(2 * np.pi * t / 3.9)
        m = sf.next_fast_len(n * 16)
        Fz = np.abs(sf.rfft(y * np.hanning(n), n=m)) ** 2
        fr = sf.rfftfreq(m, dt); sel = fr <= fN
        pk = Fz[sel].max()
        pts = [(X(a), B0 - (b / pk) * (B0 - T0 - 20)) for a, b in zip(fr[sel][::4], Fz[sel][::4])]
        polyline(f, pts, C['a'], 3.0)
        k = Fz[sel].argmax(); fa = fr[sel][k]
        f.circle(X(fa), B0 - (B0 - T0 - 20), 9, C['b'], '#FFFFFF', 2.0)
        f.line(X(1 / 3.9), T0, X(1 / 3.9), B0, C['d'], 2.0, '10 8')
        f.text(R - 16, T0 + 40, lab, FS_S, 'end', P['text'], 700, False)
        tx = '봉우리 주기 %.2f a' % (1 / fa)
        if fa < 0.12:
            f.text(X(fa) + 24, T0 + 70, tx, FS_I, 'start', P['text'], 400, False)
        else:
            f.text(X(fa) - 24, T0 + 70, tx, FS_I, 'end', P['text'], 400, False)
        f.line(X(fN), B0, X(fN), B0 + 10, P['frame'], 2.0)
        if fN < 0.4:
            f.text(X(fN) + 14, B0 - 14, '나이키스트 %.3f' % fN, FS_I, 'start', P['soft'], 400, False)
    B = top + 3 * (rh + 20) - 70
    for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%.1f' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '진동수 (1/a)', FS_S, 'middle', P['text'], 400, False)
    note(f, 60, B + 150, '점선은 참 진동수 0.256. 회색 띠는 나이키스트 진동수 위쪽으로, 이 간격으로는 풀리지 않는 구간. 둘째와 셋째 줄에서는 참 진동수가 띠 안에 있어 봉우리가 더 낮은 진동수로 접혀 나타난다. 시연값(실습 4-1).')
    return f

# ================================================================= 그림 2: 불규칙 간격 시연 1
def fig_ls1(mode):
    D = J('ch04-02.json')['demo1']
    f, P = base(mode, 1080.0); C = cols(mode)
    age = np.array(D['age']); y = np.array(D['y'])
    L, R = 160.0, 1240.0
    # (a) 처음 40 a의 점과 시각 눈금
    T1, B1 = 110.0, 400.0
    X1 = lambda v: L + v / 40.0 * (R - L)
    ymin, ymax = -3.5, 3.5
    Y1 = lambda v: B1 - (v - ymin) / (ymax - ymin) * (B1 - T1)
    f.text(L, 60, '(a) 시연 계열의 처음 40 a. 점 하나가 시료 하나', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T1, R, B1, [0, 10, 20, 30, 40], [-2, 0, 2], X1, Y1, '시각 (a)', None, lambda v: '%d' % v, lambda v: '%d' % v)
    m = age <= 40
    polyline(f, [(X1(a), Y1(b)) for a, b in zip(age[m], y[m])], C['c'], 2.0)
    for a, b in zip(age[m], y[m]): f.circle(X1(a), Y1(b), 6, C['a'], '#FFFFFF', 1.5)
    # (b) 주기도
    fq = np.array(D['f']); pl = np.array(D['p_ls']); pn = np.array(D['p_naive'])
    T2, B2 = 640.0, 960.0
    X2 = lambda v: L + v / 0.45 * (R - L)
    Y2 = lambda v: B2 - v / 0.30 * (B2 - T2)
    f.text(L, 596, '(b) 정규화 파워. 심은 주기 5.2 a (진동수 0.192)', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T2, R, B2, [0, 0.1, 0.2, 0.3, 0.4], [0, 0.1, 0.2, 0.3], X2, Y2, '진동수 (1/a)', None, lambda v: '%.1f' % v, lambda v: '%.1f' % v)
    f.line(X2(1 / 5.2), T2, X2(1 / 5.2), B2, C['d'], 2.0, '10 8')
    polyline(f, [(X2(a), Y2(b)) for a, b in zip(fq, pn)], C['b'], 3.0, '14 8')
    polyline(f, [(X2(a), Y2(b)) for a, b in zip(fq, pl)], C['a'], 3.4)
    legend_line(f, 60, B2 + 150, C['a'], None, '진짜 시각 사용(Lomb-Scargle)')
    legend_line(f, 60, B2 + 196, C['b'], '14 8', '시료 번호를 시각으로 사용(간격 일정 가정)')
    note(f, 60, B2 + 260, '시연값(실습 4-2). 퇴적률이 깊이에 따라 +-30% 흔들려 시료 간격이 0.84~1.55 a이다. 시간 눈금을 일정하다고 가정하면 봉우리가 낮아지고 6.0 a쪽으로 밀린다.')
    return f

# ================================================================= 그림 3: 불규칙 간격 시연 2 (145점, 4263년)
def fig_ls2(mode):
    D = J('ch04-02.json')['demo2']
    f, P = base(mode, 1000.0); C = cols(mode)
    fq = np.array(D['f']); p = np.array(D['p']); t = np.array(D['t']); thr = D['thr']
    L, R, T, B = 160.0, 1240.0, 110.0, 640.0
    X = lambda v: L + v / 0.0169 * (R - L)
    Y = lambda v: B - v / 0.45 * (B - T)
    f.text(L, 60, '145개 점, 4263년의 시연 계열: 정규화 파워(Lomb-Scargle)', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T, R, B, [0, 0.004, 0.008, 0.012, 0.016], [0, 0.1, 0.2, 0.3, 0.4], X, Y, '진동수 (1/년)', None, lambda v: '%.3f' % v, lambda v: '%.1f' % v)
    m = fq <= 0.0169
    polyline(f, [(X(a), Y(b)) for a, b in zip(fq[m], p[m])], C['a'], 3.4)
    f.line(L, Y(thr), R, Y(thr), C['b'], 3.0, '14 8')
    f.text(R - 14, Y(thr) - 14, '백색 잡음 95%% 문턱 %.3f' % thr, FS_I, 'end', P['text'], 400, False)
    for per in (1000, 500):
        f.line(X(1 / per), T, X(1 / per), B, C['d'], 2.0, '10 8')
    f.text(X(0.0026), T + 40, '점선: 심은 주기 1000년(왼쪽), 500년(오른쪽)', FS_I, 'start', P['text'], 400, False)
    for tt in t:
        xx_ = L + (tt / t[-1]) * (R - L)
        f.line(xx_, B + 6, xx_, B + 22, C['d'], 1.4)
    f.text(L, B + 150, '축 아래의 짧은 눈금: 시료 시각(0~4263년을 가로로 늘려 그림)', FS_I, 'start', P['soft'], 400, False)
    note(f, 60, B + 210, '시연값(실습 4-3). 가장 낮은 진동수 1/L = 0.000235, 평균 간격 29.6년.')
    return f

# ================================================================= 그림 4: 자기상관
def fig_acf(mode):
    from statsmodels.tsa.stattools import acf
    D = J('ch04-03.json')['B']
    x = np.array(D['x']); a = acf(x, nlags=20, fft=True)
    f, P = base(mode, 800.0); C = cols(mode)
    L, R, T, B = 170.0, 1240.0, 110.0, 560.0
    X = lambda v: L + (v + 0.5) / 20.5 * (R - L)
    Y = lambda v: B - (v + 0.2) / 1.2 * (B - T)
    f.text(L, 60, 'AR(1) 시연 계열(n = 414)의 표본 자기상관', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T, R, B, [0, 5, 10, 15, 20], [0, 0.25, 0.5, 0.75, 1.0], X, Y, '시차 (년)', None, lambda v: '%d' % v, lambda v: '%.2f' % v)
    bd = 1.96 / math.sqrt(414)
    f.rect(L, Y(bd), R - L, Y(-bd) - Y(bd), C['band'], 'none', 0)
    f.line(L, Y(0), R, Y(0), P['frame'], 2.0)
    for k in range(21):
        f.line(X(k), Y(0), X(k), Y(a[k]), C['a'], 6.0)
    th = [(X(k), Y(0.72 ** k)) for k in range(21)]
    polyline(f, th, C['b'], 3.0, '12 8')
    for k, v in enumerate(th): f.circle(v[0], v[1], 6, C['b'], '#FFFFFF', 1.5)
    xx = legend_line(f, L + 330, T + 50, C['a'], None, '표본 자기상관', 6.0, 50)
    legend_line(f, L + 330, T + 100, C['b'], '12 8', '이론값 0.72의 거듭제곱', 4.0, 50)
    f.rect(L + 330, T + 128, 50, 22, C['band'], P['frame'], 1.2)
    f.text(L + 330 + 64, T + 148, '백색 잡음의 95%% 한계 +-%.3f' % bd, FS_I, 'start', P['text'], 400, False)
    note(f, 60, B + 140, '시연값(실습 4-4). 시차 1의 값은 0.729. 띠의 폭 0.096은 제1권 n=414의 5% 임계 상관과 같다.')
    return f

# ================================================================= 그림 5: 독립한 두 AR(1)의 상관 분포
def fig_neff(mode):
    D = J('ch04-03.json')
    h = np.array(D['hist'], float); sd = D['r_sd']
    edges = np.linspace(-0.5, 0.5, 81); ctr = (edges[:-1] + edges[1:]) / 2
    dens = h / h.sum() / (edges[1] - edges[0])
    f, P = base(mode, 1000.0); C = cols(mode)
    L, R, T, B = 170.0, 1240.0, 110.0, 640.0
    X = lambda v: L + (v + 0.4) / 0.8 * (R - L)
    ymax = 8.5
    Y = lambda v: B - v / ymax * (B - T)
    f.text(L, 60, '서로 독립인 두 AR(1)(0.72)의 상관계수 r, 100000쌍 (n = 414)', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T, R, B, [-0.4, -0.2, 0, 0.2, 0.4], [0, 2, 4, 6, 8], X, Y, '표본 상관계수 r', None, lambda v: '%.1f' % v, lambda v: '%d' % v)
    for c_, d_ in zip(ctr, dens):
        if abs(c_) <= 0.4:
            f.rect(X(c_ - 0.00625), Y(d_), X(c_ + 0.00625) - X(c_ - 0.00625), B - Y(d_), C['e'], '#FFFFFF', 0.8)
    xs = np.linspace(-0.4, 0.4, 300)
    sd0 = 1 / math.sqrt(413)
    polyline(f, [(X(v), Y(math.exp(-v * v / (2 * sd0 ** 2)) / (sd0 * math.sqrt(2 * math.pi)))) for v in xs], C['b'], 3.4, '14 8')
    polyline(f, [(X(v), Y(math.exp(-v * v / (2 * sd ** 2)) / (sd * math.sqrt(2 * math.pi)))) for v in xs], C['a'], 3.4)
    for v, col, dsh in ((0.0963, C['b'], '5 7'), (0.172, C['a'], '22 8')):
        for sg in (-1, 1): f.line(X(sg * v), T, X(sg * v), B, col, 2.6, dsh)
    f.line(X(-0.18), T, X(-0.18), B, C['d'], 4.0)
    f.text(X(-0.18) - 12, T + 30, '제1권의 r = -0.18', FS_I, 'end', P['text'], 700, False)
    legend_line(f, 60, B + 150, C['b'], '14 8', '독립 가정(표준편차 0.0492)의 정규 분포', 4.0, 50)
    legend_line(f, 60, B + 196, C['a'], None, '모의 r의 표준편차 %.4f로 그린 정규 분포' % sd, 4.0, 50)
    note(f, 60, B + 260, '모의(실습 4-5). 막대는 모의한 r의 밀도. 짧은 점선(+-0.096)은 독립 가정의 5% 임계 상관, 긴 점선(+-0.172)은 n_eff = 131.3일 때의 5% 임계 상관이다. 굵은 실선은 제1권의 r = -0.18.')
    return f

# ================================================================= 그림 6: 기각률
def fig_rej(mode):
    D = J('ch04-03.json')
    f, P = base(mode, 1060.0); C = cols(mode)
    cases = [('두 계열 AR(1) 0.72, n = 414', D['C']['both'], ['독립 가정', 'rho 참값 공식', 'rho 추정 공식', 'ACF 곱 공식(K=20)']),
             ('백색 잡음의 11년 이동평균 두 개, n = 404', D['E']['white'], ['독립 가정', 'rho 참값 공식', 'rho 추정 공식', 'ACF 곱 공식(K=30)']),
             ('AR(1) 0.72의 11년 이동평균 두 개, n = 404', D['E']['ar'], ['독립 가정', 'rho 추정 공식', 'ACF 곱 공식(K=30)'])]
    L, R, T = 560.0, 1240.0, 110.0
    X = lambda v: L + v / 0.6 * (R - L)
    f.text(60, 60, '독립인 두 계열의 상관검정이 5% 수준에서 기각한 비율 (참값은 5%)', FS_S, 'start', P['text'], 700, False)
    y = T
    palette = [C['e'], C['c'], C['b'], C['a']]
    bh = 40.0
    for nm, dct, keys in cases:
        f.text(60, y + 30, nm, FS_S, 'start', P['text'], 700, False)
        y += 52
        for i, k in enumerate(keys):
            v = dct[k][0]
            colr = C['e'] if k == '독립 가정' else (C['c'] if '참값' in k else (C['b'] if 'rho 추정' in k else C['a']))
            f.rect(L, y, X(v) - L, bh, colr, P['frame'], 1.2)
            f.text(L - 12, y + 30, k, FS_I, 'end', P['text'], 400, False)
            f.text(max(X(v), X(0.07)) + 20, y + 30, '%.3f' % v, FS_I, 'start', P['text'], 400, False)
            y += bh + 10
        y += 40
    B = y - 20
    f.line(X(0.05), T + 40, X(0.05), B, C['d'], 3.0, '10 8')
    f.rect(L, T + 40, R - L, B - T - 40, 'none', P['frame'], 2.0)
    for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, '%.1f' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '5% 수준 기각 비율 (점선 = 0.05)', FS_S, 'middle', P['text'], 400, False)
    note(f, 60, B + 150, '모의(실습 4-5, 4-6). 쌍 수는 첫째 100000, 나머지 60000. "독립 가정"은 자유도 n-2를 그대로 쓴 것, 나머지는 유효 표본으로 자유도를 줄인 것이다.')
    f.h = max(f.h, B + 260)
    return f

# ================================================================= 그림 7: 추세 제거
def fig_detrend(mode):
    D = J('ch04-04.json')['B']
    yr = np.array(D['years']); w = np.array(D['width']); fits = {k: np.array(v) for k, v in D['fits'].items()}; clim = np.array(D['clim'])
    f, P = base(mode, 1300.0); C = cols(mode)
    L, R = 170.0, 1240.0
    X = lambda v: L + (v - 1600) / 413.0 * (R - L)
    T1, B1 = 110.0, 470.0
    Y1 = lambda v: B1 - (v - 0.2) / (3.0 - 0.2) * (B1 - T1)
    f.text(L, 60, '(a) 시연 계열의 테 너비(mm)와 추세선', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T1, R, B1, [1600, 1700, 1800, 1900, 2000], [0.5, 1.0, 1.5, 2.0, 2.5], X, Y1, None, None, lambda v: '%d' % v, lambda v: '%.1f' % v)
    polyline(f, [(X(a), Y1(b)) for a, b in zip(yr, w)], C['e'], 2.4)
    polyline(f, [(X(a), Y1(b)) for a, b in zip(yr, fits['음의 지수'])], C['a'], 4.0)
    polyline(f, [(X(a), Y1(b)) for a, b in zip(yr, fits['67% 스플라인'])], C['b'], 4.0, '14 8')
    polyline(f, [(X(a), Y1(b)) for a, b in zip(yr, fits['직선'])], C['d'], 3.0, '4 8')
    x = legend_line(f, L + 360, T1 + 40, C['a'], None, '음의 지수', 4.0, 50)
    x = legend_line(f, x, T1 + 40, C['b'], '14 8', '67% 스플라인', 4.0, 50)
    legend_line(f, L + 360, T1 + 90, C['d'], '4 8', '직선', 3.0, 50)
    T2, B2 = 620.0, 1000.0
    idx = w / fits['67% 스플라인']; idx2 = w / fits['음의 지수']
    Y2 = lambda v: B2 - (v - (-2.2)) / (2.6 - (-2.2)) * (B2 - T2)
    f.text(L, 570, '(b) 1800~1950년: 지수(67% 스플라인)와 참 기후 신호, z 점수', FS_S, 'start', P['text'], 700, False)
    z = lambda a: (a - a.mean()) / a.std()
    X2 = lambda v: L + (v - 1800) / 150.0 * (R - L)
    sel = (yr >= 1800) & (yr <= 1950)
    zc, zi = z(clim), z(idx)
    axes(f, L, T2, R, B2, [1800, 1850, 1900, 1950], [-2, -1, 0, 1, 2], X2, Y2, '연도', None, lambda v: '%d' % v, lambda v: '%d' % v)
    polyline(f, [(X2(a), Y2(b)) for a, b in zip(yr[sel], zc[sel])], C['b'], 3.4, '14 8')
    polyline(f, [(X2(a), Y2(b)) for a, b in zip(yr[sel], zi[sel])], C['a'], 3.0)
    legend_line(f, 60, B2 + 150, C['a'], None, '지수(67% 스플라인)', 4.0, 50)
    legend_line(f, 60, B2 + 196, C['b'], '14 8', '참 기후 신호', 4.0, 50)
    note(f, 60, B2 + 260, '시연값(실습 4-8). 심은 나이 곡선은 음의 지수, 기후 신호는 해마다 성분과 130년 주기 성분의 합이다. 표는 4.5절.')
    return f

# ================================================================= 그림 8: 시간
def fig_time(mode):
    D = J('ch04-05.json')
    f, P = base(mode, 900.0); C = cols(mode)
    L, R, T, B = 200.0, 1240.0, 110.0, 640.0
    X = lambda b: L + (math.log10(b) - 3.0) / 3.0 * (R - L)
    lo, hi = -2.0, 4.0
    Y = lambda s: B - (math.log10(s) - lo) / (hi - lo) * (B - T)
    f.text(L, 60, '대리 자료 B개를 만들고 주기도를 계산하는 시간 (2코어 CPU, 로그 눈금)', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T, R, B, [1e3, 1e4, 1e5, 1e6], [0.01, 0.1, 1, 10, 100, 1000, 10000], X, Y, '대리 자료 수 B', None, lambda v: {1000: '1천', 10000: '1만', 100000: '10만', 1000000: '100만'}[int(v)], lambda v: ('%g' % v))
    bs = [1e3, 1e4, 1e5, 1e6]
    ps, pa = D['per_scipy'], D['per_astro']
    for per, cc_ in ((ps, C['d']), (pa, C['c'])):
        b2 = min(1e6, 10 ** hi / per)          # 축 위쪽(10^4 s)을 넘기 전까지만 그린다
        polyline(f, [(X(1e3), Y(1e3 * per)), (X(b2), Y(b2 * per))], cc_, 3.4, '4 8')
    tl = D['timing_ls']
    pts = [(X(b), Y(g + c)) for b, g, c in tl]
    polyline(f, pts, C['a'], 4.0)
    for p_ in pts: f.circle(p_[0], p_[1], 8, C['a'], '#FFFFFF', 2.0)
    tf = D['timing_fft']
    pts2 = [(X(b), Y(g + c)) for b, g, c in tf]
    polyline(f, pts2, C['b'], 4.0)
    for p_ in pts2: f.rect(p_[0] - 8, p_[1] - 8, 16, 16, C['b'], '#FFFFFF', 2.0)
    legend_line(f, 60, B + 150, C['d'], '4 8', 'scipy 반복문(곱셈 추정)', 3.4, 50)
    legend_line(f, 60, B + 196, C['c'], '4 8', 'astropy fast 반복문(곱셈 추정)', 3.4, 50)
    legend_line(f, 60, B + 242, C['a'], None, '행렬곱 Lomb-Scargle(실측, 불규칙 간격, N=552, 칸 1086)', 4.0, 50)
    legend_line(f, 60, B + 288, C['b'], None, 'rfft(실측, 일정 간격, N=414)', 4.0, 50)
    note(f, 60, B + 352, '실습 4-12. 점선은 한 번의 실측 시간에 B를 곱한 것이고(위쪽 눈금 10^4 s에서 끊었다), 실선은 B개를 모두 계산해 잰 값이다(행렬곱은 B = 10^5까지). GPU 시간은 z840 실행 필요.')
    return f

# ================================================================= 그림 9: 띠 안의 봉우리 수
def fig_band(mode):
    D = J('ch04-05.json')['band']
    h = np.array(D['runs_hist'], float); h = h / h.sum()
    f, P = base(mode, 800.0); C = cols(mode)
    L, R, T, B = 170.0, 1240.0, 110.0, 560.0
    X = lambda v: L + (v + 0.5) / 26.0 * (R - L)
    Y = lambda v: B - v / 0.20 * (B - T)
    f.text(L, 60, '순수 붉은 잡음 500개에서 3~8 a 띠 안의 95% 문턱 위 봉우리 수', FS_S, 'start', P['text'], 700, False)
    axes(f, L, T, R, B, list(range(0, 26, 5)), [0, 0.05, 0.10, 0.15, 0.20], X, Y, '봉우리 수 (25는 25개 이상)', None, lambda v: '%d' % v, lambda v: '%.2f' % v)
    for k, v in enumerate(h):
        f.rect(X(k - 0.4), Y(v), X(k + 0.4) - X(k - 0.4), B - Y(v), C['a'] if k >= 5 else C['e'], '#FFFFFF', 1.0)
    f.text(X(15), T + 40, '5개 이상인 실현의 비율 %.3f' % h[5:].sum(), FS_S, 'start', P['text'], 700, False)
    f.text(X(15), T + 84, '봉우리 수의 평균 %.2f개' % D['runs_mean'], FS_I, 'start', P['text'], 400, False)
    note(f, 60, B + 140, '모의(실습 4-14). 문턱은 진동수마다 구한 점별 95% 선이고, 봉우리는 문턱을 넘는 연속 구간이다. REDFIT의 구간 평균 방식과는 다르다.')
    return f

FIGS = [('fig-ch04-alias-v1', fig_alias), ('fig-ch04-ls1-v1', fig_ls1), ('fig-ch04-ls2-v1', fig_ls2), ('fig-ch04-acf-v1', fig_acf),
        ('fig-ch04-neff-v1', fig_neff), ('fig-ch04-rej-v1', fig_rej), ('fig-ch04-detrend-v1', fig_detrend), ('fig-ch04-time-v1', fig_time),
        ('fig-ch04-band-v1', fig_band)]
if __name__ == '__main__':
    for mode in ('color', 'bw'):
        for nm, fn in FIGS:
            fg = fn(mode)
            print(nm, mode, 'warn', fg.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
