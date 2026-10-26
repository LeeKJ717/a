# -*- coding: utf-8 -*-
"""제2권 15장 그림 6장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch15 의 실행 결과(case1.json, case2.json, case3.json)에서 읽는다.
  fig-ch15-pvals-v1 : 사례 1. 세 비교의 p 값: Fisher 정확값, 순열 100만 번, Holm 보정
  fig-ch15-hdiv-v1  : 사례 1. 유전자 다양도 H와 부트스트랩 2.5~97.5% 구간
  fig-ch15-tephra-v1: 사례 2. 날짜별 보정 확률 밀도와 McLean 등의 구간, 오쿠노 등의 채택·후보 연대
  fig-ch15-agree-v1 : 사례 2. 날짜 묶음의 합치 통계 T'와 5% 한계
  fig-ch15-brune-v1 : 사례 3. Brune 곡선과 표 4의 점, 실측 포획 효율
  fig-ch15-cia-v1   : 사례 3. CIA 재계산(규칙 A, 규칙 E)과 논문 표의 CIA
사용: python figs-ch15.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figkit import *
ROOT = os.path.dirname(HERE); CODE = os.path.join(ROOT, 'ms', 'code', 'ch15'); OUT = os.path.join(ROOT, 'fig')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
L, T, R, B = 200.0, 90.0, 1240.0, 700.0
GRAYBAR = lambda mode: '#C9D6DD' if mode == 'color' else '#CFCFCF'


def legend_row(f, x, y, kind, color, text, P, dash=None, sw=4.0):
    if kind == 'line':
        f.line(x, y - 8, x + 60, y - 8, color, sw, dash); f.text(x + 74, y, text, FS_I, 'start', P['text'], 400, False)
    elif kind == 'rect':
        f.rect(x, y - 26, 28, 28, color, P['frame'], 1.5); f.text(x + 40, y, text, FS_I, 'start', P['text'], 400, False)
    else:
        f.marker(x + 14, y - 10, kind, 1.0, color); f.text(x + 40, y, text, FS_I, 'start', P['text'], 400, False)


# ------------------------------------------------------------------ 그림 1: p 값
def fig_pvals(mode, H=6000.0):
    f, P = base(mode, H); d = J('case1.json'); cols = series_colors(mode)
    nms = list(d['fisher'])
    X = lambda i: L + 170 + i * 340.0
    Y = logmap(1e-5, 1.0, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1], ['1e-5', '1e-4', '1e-3', '0.01', '0.1', '1'])
    f.text(L - 160, T - 30, 'p 값 (로그 눈금)', FS_S, 'start', P['text'], 400, False)
    labs = ['신석기 대 청동기', '신석기 대 대전자', '신석기 대 대산전']
    for i, lb in enumerate(labs):
        f.text(X(i), B + 52, lb, FS_I, 'middle', P['text'], 400, False)
        f.text(X(i), B + 90, str(d['fisher'][nms[i]]['table']), FS_I, 'middle', P['soft'], 400, False)
    f.line(L, Y(0.05), R, Y(0.05), cols[1], 3.0, '16 8'); f.text(R - 12, Y(0.05) - 12, '0.05', FS_I, 'end', cols[1], 700, True)
    f.line(L, Y(1 / 1001), R, Y(1 / 1001), cols[2], 3.0, '6 8')
    for i, nm in enumerate(nms):
        fi, pe, ho = d['fisher'][nm]['p_two'], d['perm'][nm]['p_two'], d['holm'][i]
        f.marker(X(i) - 60, Y(fi), 'dot', 1.3, cols[0]); f.marker(X(i), Y(pe), 'sq', 1.3, cols[1] if mode == 'color' else '#666666'); f.marker(X(i) + 60, Y(ho), 'dia', 1.4, P['text'])
        f.text(X(i) - 60, Y(fi) + 58, '%.2e' % fi, FS_I, 'middle', cols[0], 700, True)
        f.text(X(i), Y(pe) - 34, '%.2e' % pe, FS_I, 'middle', P['text'], 400, True)
        f.text(X(i) + 60, Y(ho) - 34 if i != 1 else Y(ho) + 58, '%.2e' % ho, FS_I, 'middle', P['text'], 400, True)
    ly = B + 150
    legend_row(f, 170, ly, 'dot', cols[0], 'Fisher 정확검정(양쪽)', P)
    legend_row(f, 620, ly, 'sq', cols[1] if mode == 'color' else '#666666', '순열 검정 100만 번(양쪽)', P)
    legend_row(f, 170, ly + 46, 'dia', P['text'], 'Fisher p에 Holm 보정(세 검정을 한 묶음으로)', P)
    legend_row(f, 170, ly + 92, 'line', cols[2], '순열 1,000번으로 얻을 수 있는 가장 작은 p = 1/1001', P, '6 8', 3.0)
    f._end = note(f, 150, ly + 156, '입력은 제1권 11장 표 4에서 만든 2x2 표 세 개이다(사례 1). 순열 100만 번은 가능한 가장 작은 값이 1/1,000,001이라 7.9e-4와 1.65e-4를 해상한다. 순열의 1.91e-4는 190번 대 기대 165번으로 표준편차의 1.9배 떨어졌다(이항 양쪽 p = 0.065). 가운데 비교의 p는 0.05보다 훨씬 크다. NumPy 경로, CPU.')
    return f


# ------------------------------------------------------------------ 그림 2: 유전자 다양도
def fig_hdiv(mode, H=6000.0):
    f, P = base(mode, H); d = J('case1.json')['boot']; cols = series_colors(mode)
    LL = 420.0
    X = lin(0.0, 1.0, LL, R)
    order = [('신석기 합', '신석기 합 (n = 18)'), ('대전자', '대전자 (n = 5)'), ('대산전', '대산전 (n = 9)')]
    Y = lambda i: T + 140 + i * 170.0
    f.rect(LL, T, R - LL, 3 * 170 + 70, 'none', P['frame'], 2.4)
    for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        f.line(X(v), T, X(v), T + 3 * 170 + 70, P['grid'], 1.0, '8 8'); f.line(X(v), T + 3 * 170 + 70, X(v), T + 3 * 170 + 80, P['frame'], 2.0)
        f.text(X(v), T + 3 * 170 + 120, '%g' % v, FS_I, 'middle', P['soft'], 400, False)
    f.text((LL + R) / 2, T + 3 * 170 + 170, '유전자 다양도 H (Nei 보정 포함, 하플로그룹 수준)', FS_S, 'middle', P['text'], 400, False)
    for i, (k, lb) in enumerate(order):
        r = d[k]; y = Y(i)
        f.text(LL - 24, y + 10, lb, FS_S, 'end', P['text'], 400, False)
        lo, md, hi = r['q']; lo2, md2, hi2 = r['q1m']
        f.rect(X(lo), y - 30, max(X(hi) - X(lo), 4), 60, '#C9D6DD' if mode == 'color' else '#CFCFCF', P['frame'], 2.0)
        f.marker(X(md), y, 'dot', 1.1, P['text'])
        f.marker(X(r['H']), y, 'tri', 1.3, cols[0])
        f.line(X(lo2), y + 44, X(hi2), y + 44, cols[1], 4.0)
        f.text(X(hi) + 14, y - 40, '%.3f ~ %.3f' % (lo, hi), FS_I, 'start' if hi < 0.8 else 'end', P['text'], 400, True)
        f.text(X(r['H']) + 18, y - 46, 'H = %.3f' % r['H'], FS_I, 'start', cols[0], 700, True) if False else None
    ly = T + 3 * 170 + 230
    legend_row(f, 170, ly, 'tri', cols[0], '관측 H (제1권 계산 11-4)', P)
    legend_row(f, 170, ly + 46, 'rect', '#C9D6DD' if mode == 'color' else '#CFCFCF', '부트스트랩 2.5~97.5% (2만 번, 시드 11, 점은 중앙값)', P)
    legend_row(f, 170, ly + 92, 'line', cols[1], '같은 구간, 100만 번(시드 12). 끝이 3자리까지 같다', P)
    f._end = note(f, 150, ly + 150, '신석기 합의 구간(0.000~0.464)은 대산전의 구간(0.556~0.889)과 겹치지 않고 대전자의 구간(0.000~0.600)과 겹친다. 신석기 합은 재표집의 %.1f%%가 H = 0이다(모두 같은 형, 이론값 12.0%%). 재표집은 관측에 없는 형을 만들 수 없다.' % (100 * d['신석기 합']['p_h0']))
    return f


# ------------------------------------------------------------------ 그림 3: 화산재층 보정
def fig_tephra(mode, H=6000.0):
    f, P = base(mode, H); d = J('case2.json'); cols = series_colors(mode)
    cur = d['curves']; ml = d['ml']
    panels = [
        ('U-2', (5300, 5900), list(range(5300, 5901, 100)), [('U-2|4910', 'a'), ('U-2|4965', 'a'), ('U-2|4945', 'a'), ('U-2|4940', 'a'), ('U-2|4710', 'o')], ('U-2|wm', '네 날짜 가중 평균 4940 ± 17.5'), [5600], {'U-2|4710': ('4710 BP', 'start'), 'U-2|4910': ('4910~4965 BP', 'middle')}),
        ('U-3', (8100, 9100), list(range(8100, 9101, 200)), [('U-3|7525', 'a'), ('U-3|8030', 'a')], None, [8300, 9000], {'U-3|7525': ('7525 BP', 'middle'), 'U-3|8030': ('8030 BP', 'middle')}),
        ('U-4', (10000, 14400), [10000, 11000, 12000, 13000, 14000], [('U-4|9785', 'o'), ('U-4|11840', 'o'), ('U-4|12165', 'a'), ('U-4|12030', 'a'), ('U-4|12090', 'a'), ('U-4|12095', 'a')], ('U-4|wm', '네 날짜 가중 평균 12095 ± 20'), [14000, 11000], {'U-4|9785': ('9785 BP', 'middle'), 'U-4|11840': ('11840 BP', 'end'), 'U-4|12090': ('12,000 BP대', 'end')}),
    ]
    ph, gap = 400.0, 150.0
    for k, (ly, (x0, x1), ticks, dates, wm, cands, tags) in enumerate(panels):
        top = T + k * (ph + gap); bot = top + ph
        X = lin(x0, x1, L, R); Y = lin(0, 1.32, bot, top)
        frame(f, L, top, R, bot)
        for tv in ticks:
            f.line(X(tv), top, X(tv), bot, P['grid'], 1.0, '8 8'); f.line(X(tv), bot, X(tv), bot + 10, P['frame'], 2.0)
            f.text(X(tv), bot + 44, '{:,}'.format(tv), FS_I, 'middle', P['soft'], 400, False)
        f.text(L, top - 14, ly, FS_S, 'start', P['text'], 700, False)
        lo, hi = ml[ly]
        f.rect(X(lo), top, max(X(hi) - X(lo), 3), ph, '#E4D2B8' if mode == 'color' else '#DADADA', 'none', 0)
        for cv in cands:
            f.line(X(cv), top, X(cv), bot, P['text'], 2.5, '12 8')
        def poly(key, c, sw, dash=None):
            q = cur[key]; pts = []
            m = max(q['p'])
            for i, v in enumerate(q['p']):
                xx = q['x0'] + i
                if x0 <= xx <= x1: pts.append((X(xx), Y(v / m)))
            dash_line(f, pts, c, sw, dash)
            return pts
        for key, kind in dates:
            c = cols[1] if kind == 'a' else cols[2]
            pts = poly(key, c, 2.5, None if kind == 'a' else '10 6')
            if key in tags:
                pk = min(pts, key=lambda t: t[1])
                tx, an = tags[key]
                f.text(pk[0] + (10 if an == 'start' else (-10 if an == 'end' else 0)), pk[1] - (50 if key == 'U-4|11840' else 14), tx, FS_I, an, c if mode == 'color' else P['text'], 700, True)
        if wm:
            poly(wm[0], cols[0], 5.0)
        # 오쿠노 후보 표시
        for cv in cands:
            f.text(X(cv) + 10, bot - 14, '{:,}'.format(cv), FS_I, 'start', P['text'], 700, True)
        f.text(R, top - 14, 'McLean 등 %s~%s' % ('{:,}'.format(lo), '{:,}'.format(hi)), FS_I, 'end', P['soft'], 400, False)
    ly0 = T + 3 * (ph + gap) - gap + 100
    f.text((L + R) / 2, ly0 - 26, '보정 연대 (cal BP, 오른쪽이 더 오래됨)', FS_S, 'middle', P['text'], 400, False)
    ly = ly0 + 40
    legend_row(f, 170, ly, 'line', cols[1], '날짜 하나의 보정 확률(IntCal13, 각 곡선의 최댓값 = 1)', P, None, 3.0)
    legend_row(f, 170, ly + 46, 'line', cols[2], '합치 시험에서 걸린 날짜(4710, 9785, 11840)', P, '10 6', 3.0)
    legend_row(f, 170, ly + 92, 'line', cols[0], '합치한 날짜들의 가중 평균(U-2, U-4)', P, None, 5.0)
    legend_row(f, 170, ly + 138, 'rect', '#E4D2B8' if mode == 'color' else '#DADADA', 'McLean 등의 95.4% 구간', P)
    legend_row(f, 170, ly + 184, 'line', P['text'], '오쿠노 등이 채택하거나 후보로 든 연대(제1권 표 5)', P, '12 8', 2.5)
    f._end = note(f, 150, ly + 248, 'U-2는 네 날짜의 평균이 McLean 등의 구간과 겹치고, U-3은 7525 BP만 겹친다. U-4는 날짜 여섯 개 모두 McLean 등의 구간(10,171~10,230)에서 947년 이상 떨어져 있다. 날짜는 제1권 4장 계산 4-6의 값, 보정은 3장 c14lib. 가로 눈금은 패널마다 다르다.')
    return f


# ------------------------------------------------------------------ 그림 4: 합치 통계
def fig_agree(mode, H=6000.0):
    f, P = base(mode, H); d = J('case2.json')['agree']; cols = series_colors(mode)
    LL = 560.0
    X = logmap(0.5, 6000, LL, R)
    keys = ['U-2 네 날짜', 'U-2 다섯 날짜(4710 포함)', 'U-3 두 날짜', 'U-4 다섯 날짜(12,000 BP대)', 'U-4 네 날짜(11,840 제외)', 'U-4 여섯 날짜(9,785 포함, 이 장의 새 계산)']
    short = ['U-2 네 날짜', 'U-2 다섯 날짜(4710 포함)', 'U-3 두 날짜', 'U-4 다섯 날짜(12,000 BP대)', 'U-4 네 날짜(11,840 뺌)', 'U-4 여섯 날짜(9785 포함)']
    n = len(keys); Y = lambda i: T + 70 + i * 100.0
    f.rect(LL, T, R - LL, n * 100 + 40, 'none', P['frame'], 2.4)
    for v in (1, 10, 100, 1000):
        f.line(X(v), T, X(v), T + n * 100 + 40, P['grid'], 1.0, '8 8'); f.line(X(v), T + n * 100 + 40, X(v), T + n * 100 + 50, P['frame'], 2.0)
        f.text(X(v), T + n * 100 + 90, '{:,}'.format(v), FS_I, 'middle', P['soft'], 400, False)
    f.text((LL + R) / 2, T + n * 100 + 140, "합치 통계 T' (로그 눈금)", FS_S, 'middle', P['text'], 400, False)
    for i, k in enumerate(keys):
        r = d[k]; y = Y(i)
        f.text(LL - 20, y + 10, short[i], FS_I, 'end', P['text'], 400, False)
        ok = r['agree']
        f.rect(LL, y - 28, X(r['T']) - LL, 56, cols[3] if (ok and mode == 'color') else (cols[0] if mode == 'color' else ('#BBBBBB' if ok else '#444444')), P['frame'], 1.5)
        f.text(max(X(r['T']), X(r['crit5'])) + 14, y + 10, "%s (n = %d)" % ('%.2f' % r['T'] if r['T'] < 1000 else '%.0f' % r['T'], len(r['x'])), FS_I, 'start', P['text'], 700, True) if r['T'] < 300 else f.text(X(r['T']) - 14, y + 10, "%.0f (n = %d)" % (r['T'], len(r['x'])), FS_I, 'end', '#FFFFFF' if mode == 'color' or True else P['text'], 700, False)
        f.line(X(r['crit5']), y - 40, X(r['crit5']), y + 40, P['text'], 4.0)
    ly = T + n * 100 + 200
    legend_row(f, 170, ly, 'rect', cols[3] if mode == 'color' else '#BBBBBB', "합치(T'가 한계보다 작음)", P)
    legend_row(f, 170, ly + 46, 'rect', cols[0] if mode == 'color' else '#444444', '불일치', P)
    f.line(184, ly + 56, 184, ly + 94, P['text'], 4.0); f.text(210, ly + 92, '5% 한계(카이제곱, 자유도 n - 1)', FS_I, 'start', P['text'], 400, False)
    f._end = note(f, 150, ly + 150, "날짜는 제1권 4장 계산 4-6의 값이다. 한계는 자유도에 따라 달라 막대마다 다르다(3.84~11.07). 합치한 두 묶음(U-2 네 날짜, U-4 네 날짜)만 평균을 쓸 수 있다. 맨 아래 막대는 이 장에서 새로 계산한 값으로 제1권에 없다.")
    return f


# ------------------------------------------------------------------ 그림 5: Brune
def fig_brune(mode, H=6000.0):
    f, P = base(mode, H); d = J('case3.json'); cols = series_colors(mode)
    X = logmap(0.02, 0.45, L, R); Y = lin(60, 95, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [60, 65, 70, 75, 80, 85, 90, 95])
    xticks(f, B, X, [0.02, 0.03, 0.05, 0.1, 0.2, 0.4], ['0.02', '0.03', '0.05', '0.1', '0.2', '0.4'], T, True)
    f.text(L - 160, T - 30, '포획 효율 TE (%)', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '저수량 대 연 유입량 V/Q (로그 눈금)', FS_S, 'middle', P['text'], 400, False)
    te = d['te']
    bq = te['boot_q']
    f.rect(L, Y(bq[2]), R - L, Y(bq[0]) - Y(bq[2]), '#E4D2B8' if mode == 'color' else '#E2E2E2', 'none', 0)
    pts = []
    for i in range(0, 201):
        vq = 10 ** (math.log10(0.02) + i * (math.log10(0.45) - math.log10(0.02)) / 200)
        pts.append((X(vq), Y(100 * (1 - 0.05 / math.sqrt(vq)))))
    dash_line(f, pts, cols[1], 4.0)
    for v, dash in ((te['te_paper'], None), (te['te_167'], '14 8')):
        f.line(L, Y(v), R, Y(v), cols[0], 3.0, dash)
    f.text(R - 12, Y(te['te_paper']) - 14, '실측 172/228 = %.1f%%' % te['te_paper'], FS_I, 'end', cols[0], 700, True)
    f.text(R - 12, Y(te['te_167']) + 40, '167.4/228.4 = %.1f%%' % te['te_167'], FS_I, 'end', cols[0], 700, True)
    for b in d['brune']:
        nm = b['name']
        kind = 'sq' if nm.startswith('삼협') else ('tri' if nm.startswith('네') else 'dot')
        f.marker(X(b['vq']), Y(b['te']), kind, 1.2, P['text'])
    for b in d['brune'][5:]:
        f.text(X(b['vq']) + 16, Y(b['te']) + 42, b['name'].replace('삼협댐 ', '삼협 '), FS_I, 'start', P['text'], 700, True)
    f.text(X(d['brune'][4]['vq']) - 16, Y(d['brune'][4]['te']) - 20, '네 댐 합계', FS_I, 'end', P['text'], 400, True)
    ly = B + 150
    legend_row(f, 170, ly, 'line', cols[1], 'Brune 곡선 TE = 1 - 0.05/sqrt(V/Q)', P)
    legend_row(f, 170, ly + 46, 'dot', P['text'], '표 4의 점(오동덕, 백학탄, 계락도, 향가패)', P)
    legend_row(f, 170, ly + 92, 'sq', P['text'], '삼협댐 139, 156, 175 m 단계', P)
    legend_row(f, 170, ly + 138, 'tri', P['text'], '네 댐 합계', P)
    legend_row(f, 170, ly + 184, 'rect', '#E4D2B8' if mode == 'color' else '#E2E2E2', '실측 TE의 연 재표집 95%% 구간 %.1f~%.1f' % (bq[0], bq[2]), P)
    f._end = note(f, 150, ly + 250, '점은 V와 Q로 계산한 값이다(제1권 계산 10-1). 가로선은 수지로 잰 포획 효율이다. 띠는 가동 후 6개 연을 복원추출로 10만 번 다시 뽑은 합계 비의 2.5~97.5%이며 이 책의 시연이다. 연도 사이는 독립이 아니고 수위 단계가 연마다 다르므로 구간은 참고용이다.')
    return f


# ------------------------------------------------------------------ 그림 6: CIA
def fig_cia(mode, H=6000.0):
    f, P = base(mode, H); d = J('case3.json'); cols = series_colors(mode)
    X = lin(54, 82, L, R); Y = lin(54, 88, B, T)
    frame(f, L, T, R, B)
    yticks(f, L, R, Y, [55, 60, 65, 70, 75, 80, 85])
    xticks(f, B, X, [55, 60, 65, 70, 75, 80], None, T, True)
    f.text(L - 160, T - 30, '이 책의 재계산 CIA', FS_S, 'start', P['text'], 400, False)
    f.text((L + R) / 2, B + 92, '논문 표 2의 CIA(제1권 10장 표 10의 CIA(표))', FS_S, 'middle', P['text'], 400, False)
    f.line(X(54), Y(54), X(82), Y(82), P['soft'], 3.0, '14 8')
    bad = set(d['cia_bad'])
    ce = d['cia_e']
    for x in d['cia']:
        if x['sample'] in bad:
            continue
        f.marker(X(x['table']), Y(x['calc']), 'dot', 1.0, cols[1] if mode == 'color' else '#666666')
    for k, x in enumerate([x for x in d['cia'] if x['sample'] in bad]):
        f.marker(X(x['table']), Y(x['calc']), 'dia', 1.5, cols[0] if mode == 'color' else '#111111')
        f.marker(X(x['table']), Y(x['table'] + ce['diff_bad'][k]), 'sq', 1.2, '#FFFFFF', P['text'])
        dx = 22 if x['table'] < 70 else -22
        f.text(X(x['table']) + dx, Y(x['calc']) + 10, '%s %+.2f' % (x['sample'], x['calc'] - x['table']), FS_I, 'start' if dx > 0 else 'end', P['text'], 700, True)
    ly = B + 150
    legend_row(f, 170, ly, 'dot', cols[1] if mode == 'color' else '#666666', '규칙 A로 표와 맞는 27개', P)
    legend_row(f, 170, ly + 46, 'dia', cols[0] if mode == 'color' else '#111111', '규칙 A로 맞지 않는 3개(원강, 상강, 감강)', P)
    legend_row(f, 170, ly + 92, 'sq', '#FFFFFF', '같은 3개를 규칙 E(CaO* = Na2O)로 계산한 값', P)
    f.line(900, ly - 8, 960, ly - 8, P['soft'], 3.0, '14 8'); f.text(974, ly, '1:1선', FS_I, 'start', P['text'], 400, False)
    f._end = note(f, 150, ly + 150, '규칙 A는 제1권 10장이 쓴 규칙(CaO* = min(CaO - 10/3 P2O5, Na2O), 몰)이다. 규칙 E는 이 장에서 새로 시험한 규칙으로 30개 모두 표와 0.1 이내이며(최대 0.095), 논문이 이 규칙을 썼다는 근거는 아니다. 규칙 E의 점은 가로 위치가 표 값 그대로이고 세로가 규칙 E의 값이다. 입력은 제1권 표 10.')
    return f


FIGS = (('pvals', fig_pvals), ('hdiv', fig_hdiv), ('tephra', fig_tephra), ('agree', fig_agree), ('brune', fig_brune), ('cia', fig_cia))
if __name__ == '__main__':
    import xml.etree.ElementTree as ET
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in FIGS:
            f = fn(mode)
            f = fn(mode, f._end + 40)
            pth = os.path.join(OUT, 'fig-ch15-%s-v1-%s.svg' % (nm, mode))
            w = f.save(pth)
            ET.parse(pth)
            print('fig-ch15-%s' % nm, mode, '경고:', w)
