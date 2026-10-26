# -*- coding: utf-8 -*-
"""제2권 11장 그림 5장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch11 의 실행 결과(json, jsonl)에서 읽는다.
  fig-ch11-mcerr-v1   : 몬테카를로 오차 대 반복 수 (p05)
  fig-ch11-permnull-v1: 순열 검정의 귀무분포와 정확한 초기하분포 (p02)
  fig-ch11-hdist-v1   : 부트스트랩 H의 값별 빈도와 정확한 확률 (p01)
  fig-ch11-prop-v1    : OSL 나이의 몬테카를로 분포와 정규 근사 (p03)
  fig-ch11-arnull-v1  : 자기상관 계열의 우연한 상관 분포 (p06)
사용: python figs-ch11.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figkit import *
ROOT = os.path.dirname(HERE); CODE = os.path.join(ROOT, 'ms', 'code', 'ch11'); OUT = os.path.join(ROOT, 'fig')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
JL = lambda n: [json.loads(l) for l in open(os.path.join(CODE, n), encoding='utf-8') if l.strip()]
L, T, R, B = 200.0, 90.0, 1240.0, 700.0
NLAB = {100: '100', 1000: '1,000', 10000: '1만', 100000: '10만', 1000000: '100만', 10000000: '1,000만'}

def fig_mcerr(mode):
    f, P = base(mode, 1260.0); d = J('p05-mcerror.json'); cols = series_colors(mode)
    X = logmap(100, 1e7, L, R); Y = logmap(1e-6, 10.0, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10], ['1e-6', '1e-5', '1e-4', '1e-3', '0.01', '0.1', '1', '10'])
    xticks(f, B, X, list(NLAB), [NLAB[k] for k in NLAB], T, True)
    f.text(L - 160, T - 30, '상대 오차 (제곱평균제곱근 / 정확한 값)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '반복 수 N (로그 눈금)', FS_S, 'middle', P['text'], 400, False)
    spec = [('mean', '부트스트랩 H의 평균', 'dot'), ('perm_p', '순열 검정 p (Fisher 0.00079)', 'sq'), ('tail', '정규 꼬리 확률 (1.7e-4)', 'dia')]
    for (tg, nm, kind), c in zip(spec, cols):
        rows = [r for r in d['rows'] if r['target'] == tg]
        ex = rows[0]['exact']
        th = [(X(r['N']), Y(r['theory'] / ex)) for r in rows]
        dash_line(f, th, c, 3.0, '14 8')
        for r in rows:
            x, y = X(r['N']), Y(r['rmse'] / ex)
            if tg != 'mean' and r['N'] * ex < 10: hollow(f, x, y, kind, c, 1.1)
            else: f.marker(x, y, kind, 1.1, c)
    ly = B + 150
    for i, ((tg, nm, kind), c) in enumerate(zip(spec, cols)):
        f.marker(180, ly + i * 44 - 8, kind, 1.0, c); f.text(210, ly + i * 44, nm, FS_I, 'start', P['text'], 400, False)
    f.line(160, ly + 3 * 44 - 8, 220, ly + 3 * 44 - 8, P['soft'], 3.0, '14 8'); f.text(234, ly + 3 * 44, '이론: 표준오차 = (표준편차 또는 sqrt(p(1-p))) / sqrt(N)', FS_I, 'start', P['text'], 400, False)
    ly = ly + 3 * 44 - 44
    note(f, 150, ly + 104 + 44, '속이 빈 표지는 기대 횟수 N x p 가 10 미만인 점이며 이론선에서 벗어날 수 있다(대부분의 반복에서 0이 나오므로, 기울기를 맞출 때 뺐다). 맞춘 기울기: ' +
         ', '.join('%s %.3f' % (k, v['slope']) for k, v in d['fit'].items()) + ' (이론 -0.5). 각 점은 R = 20~400번 되풀이한 값이다. NumPy 경로, CPU.')
    return f

def fig_permnull(mode):
    f, P = base(mode); rows = [r for r in JL('p02-perm-fisher.jsonl') if r.get('N') == 1000000 and r.get('freq') and r['table'] == '신석기 대 청동기'][0]
    cols = series_colors(mode)
    xs = sorted(int(k) for k in rows['pmf']); pm = {int(k): v for k, v in rows['pmf'].items()}; fr = {int(k): v / 1e6 for k, v in rows['freq'].items()}
    p0 = pm[16]
    X = lin(5, 19, L, R); Y = logmap(1e-7, 1.0, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1], ['1e-7', '1e-6', '1e-5', '1e-4', '1e-3', '0.01', '0.1', '1'])
    xticks(f, B, X, list(range(6, 19, 2)), None, T, False)
    f.text(L - 160, T - 30, '확률 (로그 눈금)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '신석기 집단 18명 가운데 N1(x)를 가진 사람 수', FS_S, 'middle', P['text'], 400, False)
    w = (R - L) / 14 * 0.62
    for x in xs:
        reg = pm[x] <= p0 * (1 + 1e-9)
        f.rect(X(x) - w / 2, Y(pm[x]), w, B - Y(pm[x]), cols[0] if reg else ('#C9D6DD' if mode == 'color' else '#CFCFCF'), P['frame'], 1.5)
    for x in xs:
        if fr.get(x, 0) > 0:
            f.marker(X(x), Y(fr[x]), 'dot', 0.9, '#111111' if mode == 'bw' else '#1B2A33')
    xo = X(16)
    f.text(xo + 30, Y(pm[16]) - 96, '관측 16명', FS_I, 'start', P['text'], 700, True)
    f.line(xo, Y(pm[16]) - 82, xo, Y(pm[16]) - 14, P['text'], 2.5)
    ly = B + 150
    f.rect(170, ly - 26, 28, 28, cols[0], P['frame'], 1.5); f.text(210, ly, '양쪽 p에 들어가는 표(확률이 관측 표 이하)', FS_I, 'start', P['text'], 400, False)
    f.rect(170, ly + 18, 28, 28, '#C9D6DD' if mode == 'color' else '#CFCFCF', P['frame'], 1.5); f.text(210, ly + 44, '들어가지 않는 표', FS_I, 'start', P['text'], 400, False)
    f.marker(184, ly + 76, 'dot', 0.9, P['text']); f.text(210, ly + 88, '순열 검정 N = 100만의 상대 빈도 (0이면 점 없음)', FS_I, 'start', P['text'], 400, False)
    ly = ly + 44
    note(f, 150, ly + 100, '막대는 초기하분포의 정확한 확률이다. 색을 칠한 막대(6, 16, 17, 18명)의 합이 Fisher 양쪽 p = %.5f 이고, 순열 100만 번은 %.5f 를 얻었다(실습 11-2). 18명의 정확한 확률은 %.1e 이고 100만 번 가운데 %d번 나왔다.' % (rows['p_exact'], rows['p_hat'], pm[18], rows['freq']['18']))
    return f

def fig_hdist(mode):
    f, P = base(mode); r = [x for x in JL('p01-boot-exact.jsonl') if x['group'] == '대산전' and x['B'] == 1000000][0]; cols = series_colors(mode)
    vals, ex, mc_ = r['pmf']['vals'], r['pmf']['exact'], r['pmf']['mc']
    X = lin(-0.04, 1.02, L, R); Y = lin(0, 0.30, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
    xticks(f, B, X, [0, 0.2, 0.4, 0.6, 0.8, 1.0], None, T, False)
    f.text(L - 160, T - 30, '확률', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '유전자 다양도 H (대산전 [1,3,1,2,2] 다시 뽑은 9명)', FS_S, 'middle', P['text'], 400, False)
    w = 22.0
    for v, e in zip(vals, ex):
        f.rect(X(v) - w / 2, Y(e), w, B - Y(e), '#C9D6DD' if mode == 'color' else '#CFCFCF', P['frame'], 1.5)
    for v, m in zip(vals, mc_):
        f.marker(X(v), Y(m), 'dot', 0.9, cols[0])
    for q, nm in ((r['exact_q'][0], '2.5%'), (r['exact_q'][2], '97.5%')):
        f.line(X(q), T, X(q), B, cols[1], 3.0, '16 8')
        f.text(X(q) + (-12 if q > 0.8 else 12), T + (96 if q > 0.8 else 40), nm + ' = %.3f' % q, FS_I, 'end' if q > 0.8 else 'start', cols[1], 700, True)
    hy = Y(max(ex[i] for i, v in enumerate(vals) if abs(v - 0.8611) < 1e-3))
    f.marker(X(0.8611), hy - 24, 'tri', 1.0, cols[2]); f.text(X(0.8611) + 20, hy - 56, '관측 0.861', FS_I, 'start', P['text'], 700, True)
    ly = B + 150
    f.rect(170, ly - 26, 28, 28, '#C9D6DD' if mode == 'color' else '#CFCFCF', P['frame'], 1.5); f.text(210, ly, '정확한 확률 (다항분포 715가지 전수 계산)', FS_I, 'start', P['text'], 400, False)
    f.marker(750, ly - 12, 'dot', 0.9, cols[0]); f.text(774, ly, '부트스트랩 B = 100만의 상대 빈도', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 70, '막대와 점의 높이 차이는 가장 큰 값에서도 %.5f 이하였다. 세로 점선은 정확한 분포의 2.5%%, 97.5%% 분위수이며 제1권 계산 11-4의 구간 0.556~0.889와 같다. NumPy 경로, 시드 11.' % max(abs(a - b) for a, b in zip(ex, mc_)))
    return f

def fig_prop(mode):
    f, P = base(mode); d = J('p03-propagate.json')['b']['HZ-OSL-180']; cols = series_colors(mode)
    ed = d['edges']; h = d['hist']; N = sum(h); w = ed[1] - ed[0]
    X = lin(0.6, 4.0, L, R); dens = [v / N / w for v in h]; Y = lin(0, 1.1, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [0, 0.2, 0.4, 0.6, 0.8, 1.0])
    xticks(f, B, X, [1, 1.5, 2, 2.5, 3, 3.5, 4], None, T, False)
    f.text(L - 160, T - 30, '확률 밀도 (1/ka)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, 'OSL 나이 = De / DR (ka), HZ-OSL-180', FS_S, 'middle', P['text'], 400, False)
    for i, v in enumerate(dens):
        lo, hi = ed[i], ed[i + 1]
        if hi < 0.6 or lo > 4.0: continue
        f.rect(X(lo), Y(v), X(hi) - X(lo), B - Y(v), '#C9D6DD' if mode == 'color' else '#CFCFCF', 'none', 0)
    mu, sd = d['formula']
    pts = []
    for k in range(0, 341):
        a = 0.6 + k * 0.01
        pts.append((X(a), Y(math.exp(-0.5 * ((a - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi)))))
    dash_line(f, pts, cols[0], 4.0)
    for qv in (d['q'][0], d['q'][2]):
        f.line(X(qv), T, X(qv), B, cols[1], 3.0, '16 8')
    f.text(X(d['q'][0]) - 10, T + 40, '2.5%% %.3f' % d['q'][0], FS_I, 'end', cols[1], 700, True)
    f.text(X(d['q'][2]) + 10, T + 40, '97.5%% %.3f' % d['q'][2], FS_I, 'start', cols[1], 700, True)
    ly = B + 150
    f.rect(170, ly - 26, 28, 28, '#C9D6DD' if mode == 'color' else '#CFCFCF', P['frame'], 1.5); f.text(210, ly, '난수 {:,}개의 막대그래프 (De 5.28 +- 0.96, DR 2.39 +- 0.09)'.format(N), FS_I, 'start', P['text'], 400, False)
    f.line(150, ly + 38, 200, ly + 38, cols[0], 4.0); f.text(214, ly + 46, '식으로 합친 정규 근사 (%.3f +- %.3f, 제1권 계산 9-10)' % (mu, sd), FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 104, '난수의 왜도는 %+.3f 으로 오른쪽 꼬리가 약간 길다. 식으로 합친 정규 근사와 거의 겹친다. 입력의 +-는 서로 독립인 1 표준편차(이 실습의 가정). NumPy 경로.' % d['skew'])
    return f

def fig_arnull(mode):
    f, P = base(mode); d = J('p06-arnull.json'); cols = series_colors(mode)
    c0, c1 = d['cases']['0.0'], d['cases']['0.72']
    X = lin(-0.4, 0.4, L, R); Y = lin(0, 9.0, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [0, 2, 4, 6, 8])
    xticks(f, B, X, [-0.4, -0.2, 0, 0.2, 0.4], None, T, False)
    f.text(L - 160, T - 30, '확률 밀도', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '서로 독립인 두 계열의 표본 상관 r (n = 414)', FS_S, 'middle', P['text'], 400, False)
    for case, c, dash in ((c0, cols[1], '14 8'), (c1, cols[0], None)):
        ed = case['edges']; h = case['hist']; N = sum(h); w = ed[1] - ed[0]
        pts = [(X((ed[i] + ed[i + 1]) / 2), Y(h[i] / (d['M']) / w)) for i in range(len(h)) if -0.4 <= ed[i] <= 0.4]
        dash_line(f, pts, c, 4.0, dash)
    for xv, c, dash, nm, dy in ((0.18, P['text'], None, 'r = 0.18', 0), (-0.18, P['text'], None, '', 0), (c1['rc_iid'], cols[1], '10 8', '', 0), (-c1['rc_iid'], cols[1], '10 8', '', 0), (c1['rc_neff'], cols[0], '10 8', '', 0), (-c1['rc_neff'], cols[0], '10 8', '', 0)):
        f.line(X(xv), T, X(xv), B, c, 2.5, dash)
    f.text(X(0.18) + 10, T + 40, '관측 0.18', FS_I, 'start', P['text'], 700, True)
    f.text(X(-c1['rc_iid']) - 10, T + 96, '독립 임계 %.3f' % c1['rc_iid'], FS_I, 'end', cols[1], 700, True)
    f.text(X(-c1['rc_neff']) - 10, T + 150, '유효 표본 임계 %.3f' % c1['rc_neff'], FS_I, 'end', cols[0], 700, True)
    ly = B + 150
    f.line(150, ly - 8, 210, ly - 8, cols[1], 4.0, '14 8'); f.text(224, ly, '자기상관 0 (표준편차 %.3f)' % c0['sd'], FS_I, 'start', P['text'], 400, False)
    f.line(650, ly - 8, 710, ly - 8, cols[0], 4.0); f.text(724, ly, '자기상관 0.72 (표준편차 %.3f)' % c1['sd'], FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 60, '점선 세로선은 5%% 임계 상관이다. 독립으로 본 값 %.3f, 유효 표본 %.1f로 본 값 %.3f. 자기상관 0.72인 %d만 쌍에서 |r| >= 0.18 이 나온 비율은 %.4f 이고, 독립으로 본 t 검정은 %.1e 를 준다(실습 11-6). NumPy 경로, 시드 11.'
         % (c1['rc_iid'], c1['neff_formula'], c1['rc_neff'], d['M'] // 10000, c1['p_big'], c1['p_iid_t']))
    return f

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in (('mcerr', fig_mcerr), ('permnull', fig_permnull), ('hdist', fig_hdist), ('prop', fig_prop), ('arnull', fig_arnull)):
            f = fn(mode)
            pth = os.path.join(OUT, 'fig-ch11-%s-v1-%s.svg' % (nm, mode))
            w = f.save(pth)
            import xml.etree.ElementTree as ET
            ET.parse(pth)          # 문서가 올바른 XML인지 검사
            print('fig-ch11-%s' % nm, mode, '경고:', w)
