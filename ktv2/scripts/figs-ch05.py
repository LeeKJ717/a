# -*- coding: utf-8 -*-
"""제2권 5장 그림 7장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch05 의 실행 결과(.json, .jsonl)에서 읽는다.
  fig-ch05-fisher-v1    : [[16,2],[4,10]]에서 합계를 고정했을 때 13개 표의 확률(로그 눈금)
  fig-ch05-permconv-v1  : 이름표 섞기 횟수 B에 따른 한쪽 p의 흔들림(시드 20개 또는 5개)
  fig-ch05-bootstab-v1  : 부트스트랩 구간 끝의 흔들림(표준편차) 대 B
  fig-ch05-reint-v1     : 시연 자료의 RE, CE 95% 구간
  fig-ch05-autocorr-v1  : 독립인 두 AR(1) 계열의 상관을 순진하게 검정했을 때 거짓 양성률
  fig-ch05-scale-v1     : B를 늘릴 때 CPU 시간(실측과 직선 외삽)
  fig-ch05-prop-v1      : 연대 오차가 퇴적속도로 전파된 분포(몬테카를로 천만 번)
사용: python figs-ch05.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geomap import Fig, FS, FS_S, FS_I, tw
ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch05')
OUT = os.path.join(ROOT, 'fig')


def jd(name):
    return json.load(open(os.path.join(CODE, name), encoding='utf-8'))


def jl(name):
    return [json.loads(l) for l in open(os.path.join(CODE, name), encoding='utf-8') if l.strip()]


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


def base(mode, H=1130.0):
    f = Fig(1300.0, H, mode)
    f.rect(0, 0, 1300.0, H, '#FFFFFF')
    return f, f.P


def cols(P, mode):
    return (P['hot'], P['river'], P['site']) if mode == 'color' else ('#111111', '#777777', '#444444')


def frame(f, L, T, R, B):
    f.rect(L, T, R - L, B - T, 'none', f.P['frame'], 2.4)


def ytick(f, L, R, y, label, grid=True):
    P = f.P
    if grid:
        f.line(L, y, R, y, P['grid'], 1.0, '8 8')
    f.line(L - 8, y, L, y, P['frame'], 2.0)
    f.text(L - 14, y + 10, label, FS_I, 'end', P['soft'], 400, False)


def xtick(f, B, x, label):
    f.line(x, B, x, B + 10, f.P['frame'], 2.0)
    f.text(x, B + 44, label, FS_I, 'middle', f.P['soft'], 400, False)


def legend_row(f, x, y, items):
    for kind, color, label in items:
        if kind == 'box':
            f.rect(x, y - 22, 30, 30, color, f.P['frame'], 1.4)
        elif kind == 'line':
            f.line(x, y - 8, x + 40, y - 8, color, 4.0)
        elif kind == 'dash':
            f.line(x, y - 8, x + 40, y - 8, color, 3.0, '12 8')
        else:
            f.circle(x + 15, y - 8, 10, color, '#FFFFFF', 2.0)
        f.text(x + 52, y, label, FS_I, 'start', f.P['text'], 400, False)
        x += 52 + tw(label, FS_I) + 36
    return x


def sci(v):
    e = int(math.floor(math.log10(v)))
    m = v / 10 ** e
    return ('%de%d' % (round(m), e)) if abs(m - round(m)) < 1e-9 else '%.1ge%d' % (m, e)


# ------------------------------------------------------------------ 그림 1: 13개 표의 확률
def fig_fisher(mode):
    d = jd('fisher-scratch.json')
    f, P = base(mode, 1060.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    lo, hi = -7.0, 0.0
    Y = lambda v: B - (math.log10(v) - lo) / (hi - lo) * (B - T)
    frame(f, L, T, R, B)
    for e in range(-7, 1):
        ytick(f, L, R, B - (e - lo) / (hi - lo) * (B - T), '1e%d' % e if e else '1')
    f.text(L - 150, T - 30, '그 표가 나올 확률 (로그 눈금)', FS_S, 'start', P['text'], 400, False)
    xs = d['x']; ps = d['p']; n = len(xs)
    obs = ps[xs.index(d['obs'])]
    c_tail, c_other, _ = cols(P, mode)
    c_other = P['river'] if mode == 'color' else '#BBBBBB'
    c_tail = P['hot'] if mode == 'color' else '#111111'
    bw = (R - L) / n
    for i, (x, p) in enumerate(zip(xs, ps)):
        x0 = L + i * bw + bw * 0.12
        col = c_tail if p <= obs * (1 + 1e-9) else c_other
        f.rect(x0, Y(p), bw * 0.76, B - Y(p), col, P['frame'], 1.4)
        xtick(f, B, L + (i + 0.5) * bw, str(x))
    f.line(L, Y(obs), R, Y(obs), P['text'], 2.4, '14 8')
    f.text((L + R) / 2, B + 92, '왼쪽 위 칸 a (신석기에서 N1(x)인 사람 수)', FS_S, 'middle', P['text'], 400, False)
    legend_row(f, 150, B + 150, [('box', c_tail, '관측 이하 4개(a = 6, 16, 17, 18)'), ('box', c_other, '나머지 9개'), ('dash', P['text'], '관측 표의 확률 6.78e-4')])
    note(f, 150, B + 206, '막대 13개의 확률을 모두 더하면 1이다. 빨간(진한) 막대 네 개의 합이 양쪽 p = 7.90e-4이다(제1권 계산 11-3b의 값과 같다). 값은 fisher-scratch.json.')
    return f


# ------------------------------------------------------------------ 그림 2: 순열 횟수와 p의 흔들림
def fig_permconv(mode):
    rows = jd('permutation-basic.json')['fisher-perm']
    f, P = base(mode, 1130.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    lo, hi = -4.0, -1.5
    Y = lambda v: B - (math.log10(v) - lo) / (hi - lo) * (B - T)
    frame(f, L, T, R, B)
    for e, lab in ((-4, '1e-4'), (-3, '1e-3'), (-2, '1e-2')):
        ytick(f, L, R, Y(10 ** e), lab)
    f.text(L - 150, T - 30, '추정한 한쪽 p (로그 눈금)', FS_S, 'start', P['text'], 400, False)
    X = lambda i: L + (i + 0.5) / len(rows) * (R - L)
    ex = rows[0]['exact']
    c1, c2, _ = cols(P, mode)
    f.line(L, Y(ex), R, Y(ex), c2, 3.0, '14 8')
    f.text(R - 20, Y(ex) - 14, '정확한 값 7.08e-4', FS_I, 'end', c2, 700, False)
    for i, r in enumerate(rows):
        x = X(i)
        f.line(x, Y(r['min']), x, Y(r['max']), P['text'], 3.0)
        f.line(x - 20, Y(r['min']), x + 20, Y(r['min']), P['text'], 3.0)
        f.line(x - 20, Y(r['max']), x + 20, Y(r['max']), P['text'], 3.0)
        f.circle(x, Y(r['mean']), 11, c1, '#FFFFFF', 2.0)
        xtick(f, B, x, '{:,}'.format(r['B']))
    f.text((L + R) / 2, B + 92, '이름표를 섞은 횟수 B', FS_S, 'middle', P['text'], 400, False)
    legend_row(f, 150, B + 150, [('dot', c1, '시드마다 구한 p의 평균'), ('line', P['text'], '시드 사이의 최소~최대'), ('dash', c2, '정확한 p')])
    note(f, 150, B + 206, '표 [[16,2],[4,10]]의 이름표를 섞어 구한 p = (b+1)/(B+1). B가 1000 이하이면 가능한 가장 작은 p(1/(B+1))가 정확한 값보다 크다. 되풀이는 B 10만까지 20번, 100만은 5번. 값은 permutation-basic.json(실습 5-2).')
    return f


# ------------------------------------------------------------------ 그림 3: 부트스트랩 구간 끝의 흔들림 대 B
def fig_bootstab(mode):
    rows = jd('bootstrap-basic.json')['cont']
    f, P = base(mode, 1130.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    lo, hi = -4.0, -0.5
    Y = lambda v: B - (math.log10(v) - lo) / (hi - lo) * (B - T)
    frame(f, L, T, R, B)
    for e in (-4, -3, -2, -1):
        ytick(f, L, R, Y(10 ** e), '1e%d' % e)
    f.text(L - 150, T - 30, '구간 끝의 표준편차 (시드 20개 또는 5개, 로그 눈금)', FS_S, 'start', P['text'], 400, False)
    X = lambda i: L + (i + 0.5) / len(rows) * (R - L)
    c1, c2, _ = cols(P, mode)
    s0 = rows[0]['lo_sd']
    for i, r in enumerate(rows):
        xtick(f, B, X(i), '{:,}'.format(r['B']))
    # 기울기 -1/2 기준선: 첫 점에서 출발
    f.line(X(0), Y(s0), X(len(rows) - 1), Y(s0 * math.sqrt(rows[0]['B'] / rows[-1]['B'])), P['soft'], 3.0, '14 8')
    for key, col, off in (('lo_sd', c1, -14), ('hi_sd', c2, 14)):
        pts = [(X(i) + off, Y(r[key])) for i, r in enumerate(rows)]
        for a, b in zip(pts[:-1], pts[1:]):
            f.line(a[0], a[1], b[0], b[1], col, 3.0)
        for x, y in pts:
            f.circle(x, y, 11, col, '#FFFFFF', 2.0)
    f.text((L + R) / 2, B + 92, '재표집 횟수 B', FS_S, 'middle', P['text'], 400, False)
    legend_row(f, 150, B + 150, [('dot', c1, '2.5% 끝'), ('dot', c2, '97.5% 끝'), ('dash', P['soft'], '기울기 -1/2(B가 100배이면 10분의 1)')])
    note(f, 150, B + 206, '시연값 표본(로그정규에서 뽑은 n=18)의 평균에 대한 퍼센타일 구간. 같은 B에서 시드를 바꾸어 구한 구간 끝의 표준편차. 값은 bootstrap-basic.json(실습 5-4).')
    return f


# ------------------------------------------------------------------ 그림 4: RE, CE 구간
def fig_reint(mode):
    iv = jd('re-ce-demo.json')['intervals']
    names = [('검증 연도 재표집(식 고정)', '추세 없음, 검증 연도 재표집'), ('이동 블록 재표집(블록 5, 식 고정)', '추세 없음, 이동 블록(5)'),
             ('보정 연도 재표집(식 다시 맞춤)', '추세 없음, 보정 연도 재표집'), ('추세 있음: 검증 연도 재표집', '추세 있음, 검증 연도 재표집'),
             ('추세 있음: 보정 연도 재표집', '추세 있음, 보정 연도 재표집')]
    f, P = base(mode, 1240.0)
    L, T, R, B = 520.0, 90.0, 1240.0, 820.0
    vlo, vhi = -3.5, 1.0
    X = lambda v: L + (v - vlo) / (vhi - vlo) * (R - L)
    frame(f, L, T, R, B)
    for v in (-3, -2, -1, 0, 1):
        f.line(X(v), T, X(v), B, P['grid'] if v else P['text'], 1.0 if v else 2.4, None if v == 0 else '8 8')
        xtick(f, B, X(v), '%d' % v)
    f.text((L + R) / 2, B + 92, '검증 통계 값 (0보다 커야 통과)', FS_S, 'middle', P['text'], 400, False)
    c1, c2, _ = cols(P, mode)
    rh = (B - T) / (len(names) * 2)
    for i, (k, lab) in enumerate(names):
        d = iv[k]
        for j, (nm, key, col) in enumerate((('RE', 're', c1), ('CE', 'ce', c2))):
            y = T + (i * 2 + j + 0.5) * rh
            a, b = d[key]
            f.line(X(a), y, X(b), y, col, 6.0)
            f.line(X(a), y - 14, X(a), y + 14, col, 4.0); f.line(X(b), y - 14, X(b), y + 14, col, 4.0)
            f.circle(X(d['obs_' + key]), y, 12, col, '#FFFFFF', 2.5)
            f.text(L - 14, y + 10, nm, FS_I, 'end', col if mode == 'color' else P['text'], 700, False)
        f.text(L - 90, T + (i * 2 + 1) * rh + 10, lab, FS_I, 'end', P['text'], 400, False)
        if i:
            f.line(40, T + i * 2 * rh, R, T + i * 2 * rh, P['grid'], 1.0, '4 8')
    legend_row(f, 150, B + 150, [('dot', c1, 'RE (점은 관측, 선은 95% 구간)'), ('dot', c2, 'CE')])
    note(f, 150, B + 206, '58년 시연 자료(가상 값)에서 앞 29년로 보정하고 뒤 29년로 검증. 추세 있음의 CE는 구간 전체가 0 아래다. 값은 re-ce-demo.json(실습 5-6).')
    return f


# ------------------------------------------------------------------ 그림 5: 거짓 양성률
def fig_autocorr(mode):
    A = [r for r in jd('autocorr-null.json')['A'] if r['r1'] == r['r2']]
    f, P = base(mode, 1130.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    vhi = 0.6
    Y = lambda v: B - v / vhi * (B - T)
    frame(f, L, T, R, B)
    for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        ytick(f, L, R, Y(v), '%.1f' % v)
    f.text(L - 150, T - 30, '거짓 양성률 (5% 수준에서 "유의"가 나온 독립 쌍의 비율)', FS_S, 'start', P['text'], 400, False)
    X = lambda i: L + (i + 0.5) / len(A) * (R - L)
    c1, c2, _ = cols(P, mode)
    f.line(L, Y(0.05), R, Y(0.05), P['text'], 2.4, '14 8')
    bw = 88
    for i, r in enumerate(A):
        x = X(i)
        f.rect(x - bw - 6, Y(r['naive5']), bw, B - Y(r['naive5']), c1, P['frame'], 1.4)
        f.rect(x + 6, Y(r['neff5']), bw, B - Y(r['neff5']), c2, P['frame'], 1.4)
        f.text(x - bw / 2 - 6, Y(r['naive5']) - 12, '%.3f' % r['naive5'], FS_I, 'middle', P['text'], 700, False)
        f.text(x + bw / 2 + 6, Y(r['neff5']) - 12, '%.3f' % r['neff5'], FS_I, 'middle', P['text'], 700, False)
        xtick(f, B, x, '%.2f' % r['r1'])
    f.text((L + R) / 2, B + 92, '두 계열 각각의 1차 자기상관 rho (길이 414)', FS_S, 'middle', P['text'], 400, False)
    legend_row(f, 150, B + 150, [('box', c1, '순진한 임계 r (n = 414)'), ('box', c2, 'n_eff의 임계 r'), ('dash', P['text'], '목표 0.05')])
    note(f, 150, B + 206, '서로 독립인 AR(1) 계열 쌍 20,000개마다 상관을 구해 5% 수준의 임계 r을 넘은 비율. 값은 autocorr-null.json(실습 5-8). rho = 0.72가 제1권 계산 11-9의 가정이다.')
    return f


# ------------------------------------------------------------------ 그림 6: CPU 시간
def fig_scale(mode):
    rows = jl('scale-cpu.jsonl')
    f, P = base(mode, 1130.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    xlo, xhi = 2.5, 10.5
    ylo, yhi = -3.5, 5.0
    X = lambda B_: L + (math.log10(B_) - xlo) / (xhi - xlo) * (R - L)
    Y = lambda s: B - (math.log10(s) - ylo) / (yhi - ylo) * (B - T)
    frame(f, L, T, R, B)
    for s, lab in ((0.001, '0.001초'), (0.1, '0.1초'), (10, '10초'), (600, '10분'), (36000, '10시간')):
        ytick(f, L, R, Y(s), lab)
    for e in range(3, 11):
        xtick(f, B, X(10 ** e), '1e%d' % e)
    f.text(L - 150, T - 30, '걸린 시간 (로그 눈금)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '재표집(또는 순열, 추출) 횟수 B', FS_S, 'middle', P['text'], 400, False)
    c1, c2, c3 = cols(P, mode)
    series = (('boot-idx', c1, 'dot'), ('perm-shuffle', c2, 'dot'), ('perm-hyper', c3, 'dot'))
    for mode_, col, _ in series:
        pts = sorted({(r['B'], r['sec']) for r in rows if r['mode'] == mode_ and r.get('chunk', 100000) == 100000 and r['B'] >= 1000})
        for a, b in zip(pts[:-1], pts[1:]):
            f.line(X(a[0]), Y(a[1]), X(b[0]), Y(b[1]), col, 3.0)
        for B_, s in pts:
            f.circle(X(B_), Y(s), 10, col, '#FFFFFF', 2.0)
        if pts:
            B_, s = pts[-1]
            thr = B_ / s
            f.line(X(B_), Y(s), X(1e10), Y(1e10 / thr), col, 2.4, '12 8')
    legend_row(f, 150, B + 150, [('dot', c1, '부트스트랩 n=18'), ('dot', c2, '이름표 섞기 32명'), ('dot', c3, '초기하 직접 추출')])
    note(f, 150, B + 206, '이 컨테이너의 CPU 코어 2개(GPU 없음)에서 실측한 점. 점선은 마지막 실측의 속도(횟수/초)를 1e10까지 곧게 늘린 외삽이며 측정이 아니다. 값은 scale-cpu.jsonl(실습 5-9). GPU 시간은 z840 실행 필요.')
    return f


# ------------------------------------------------------------------ 그림 7: 연대 오차 전파
def fig_prop(mode):
    d = jd('uncertainty-propagation.json')['rate']
    f, P = base(mode, 1130.0)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    xlo, xhi = d['edges'][0], d['edges'][-1]
    cnt = d['counts']; mx = max(cnt)
    X = lambda v: L + (v - xlo) / (xhi - xlo) * (R - L)
    Y = lambda c: B - c / (mx * 1.12) * (B - T)
    frame(f, L, T, R, B)
    for v in range(5, 14, 2):
        xtick(f, B, X(v), str(v))
    f.text((L + R) / 2, B + 92, '퇴적속도 12,500 mm ÷ 연대 차이 (mm/yr)', FS_S, 'middle', P['text'], 400, False)
    f.text(L - 150, T - 30, '추출 횟수(천만 번 중)', FS_S, 'start', P['text'], 400, False)
    for v in (0, 0.5, 1.0):
        ytick(f, L, R, Y(v * mx), '%.1f 백만' % (v * mx / 1e6) if v else '0')
    c1, c2, c3 = cols(P, mode)
    ed = d['edges']
    for i, c in enumerate(cnt):
        f.rect(X(ed[i]), Y(c), X(ed[i + 1]) - X(ed[i]) - 1, B - Y(c), c2 if mode == 'color' else '#BBBBBB', 'none', 0)
    r0, sd = d['rate'], d['sd']
    f.line(X(r0), T, X(r0), B, c1, 4.0)
    f.text(X(r0) - 10, T + 40, '식의 값 %.2f' % r0, FS_I, 'end', c1 if mode == 'color' else P['text'], 700, False)
    for v in (r0 - sd, r0 + sd):
        f.line(X(v), T + 70, X(v), B, c3, 3.0, '12 8')
    f.text(X(r0 + sd) + 12, T + 110, '식(1차 근사) 7.62 ± 0.97', FS_I, 'start', c3, 700, False)
    q = d['q1']
    f.line(X(q[0]), B - 40, X(q[1]), B - 40, P['text'], 6.0)
    f.line(X(q[0]), B - 56, X(q[0]), B - 24, P['text'], 4.0); f.line(X(q[1]), B - 56, X(q[1]), B - 24, P['text'], 4.0)
    f.text(X(q[1]) + 16, B - 52, '몬테카를로 15.87~84.13%%: %.2f ~ %.2f' % (q[0], q[1]), FS_I, 'start', P['text'], 700, False)
    legend_row(f, 150, B + 150, [('box', c2 if mode == 'color' else '#BBBBBB', '몬테카를로 분포'), ('line', c1, '식의 값'), ('dash', c3, '식의 ±1시그마')])
    note(f, 150, B + 206, '연대 차이 7660-6020 = 1640 ± 209.3년(1시그마, 독립 정규분포 가정)에서 천만 번 뽑아 12,500 mm를 나눈 분포. 오른쪽 꼬리가 길다(평균 %.2f, 중앙값 %.2f). 값은 uncertainty-propagation.json(실습 5-7).' % (d['mean'], d['median']))
    return f


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    figs = (('fig-ch05-fisher-v1', fig_fisher), ('fig-ch05-permconv-v1', fig_permconv), ('fig-ch05-bootstab-v1', fig_bootstab),
            ('fig-ch05-reint-v1', fig_reint), ('fig-ch05-autocorr-v1', fig_autocorr), ('fig-ch05-scale-v1', fig_scale), ('fig-ch05-prop-v1', fig_prop))
    only = sys.argv[1:]
    for mode in ('color', 'bw'):
        for nm, fn in figs:
            if only and nm not in only:
                continue
            f = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, '경고:', w)
