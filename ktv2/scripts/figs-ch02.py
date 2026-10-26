# -*- coding: utf-8 -*-
"""제2권 2장 그림 6장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch02 의 실행 결과(json)에서 읽는다.
  fig-ch02-flow-v1    : 수집 파이프라인과 이 컨테이너에서 실행한 범위
  fig-ch02-throttle-v1: 간격 없는 요청과 정중한 요청의 시간 선 (가짜 서버, 실습 2-2)
  fig-ch02-schema-v1  : 메타데이터 DB의 표와 관계 (실습 2-3)
  fig-ch02-extract-v1 : 표 추출 방법별 온전한 행 비율 (실습 2-5, 2-6)
  fig-ch02-order-v1   : 글자가 PDF에 쓰인 순서(행 순서와 열 순서) (실습 2-6b)
  fig-ch02-repair-v1  : 흩어진 표를 산술로 되짜맞출 때 남는 경우의 수 (실습 2-7)
시연 PDF, 가짜 서버, 시연 DB의 값은 이 책이 만든 시연값이다.
사용: python figs-ch02.py | tee figs-ch02.log"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figkit import *
ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch02', 'out')
OUT = os.path.join(ROOT, 'fig')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))
L, T, R, B = 220.0, 100.0, 1240.0, 640.0


def box(f, P, x, y, w, h, title, lines=(), solid=True, fill=None, tsize=FS_S):
    f.rect(x, y, w, h, fill or '#FFFFFF', P['frame'], 3.0, '' if solid else 'stroke-dasharray="14 8"')
    f.text(x + w / 2, y + 44, title, tsize, 'middle', P['text'], 700, False)
    for i, s in enumerate(lines):
        f.text(x + w / 2, y + 90 + i * 38, s, FS_I, 'middle', P['soft'], 400, False)


def arrow(f, P, x1, y1, x2, y2, col=None):
    col = col or P['frame']
    f.line(x1, y1, x2, y2, col, 3.0)
    a = math.atan2(y2 - y1, x2 - x1)
    f.poly([(x2, y2), (x2 - 22 * math.cos(a - 0.4), y2 - 22 * math.sin(a - 0.4)), (x2 - 22 * math.cos(a + 0.4), y2 - 22 * math.sin(a + 0.4))], col, 'none', 0)


# ============================================================ 그림 1
def fig_flow(mode):
    f, P = base(mode, 1000.0)
    cols = series_colors(mode)
    bw, bh, gap = 255.0, 190.0, 50.0
    x0 = 55.0
    row1 = [('1 검색', ['API로 DOI와', '서지 목록을 받음'], False),
            ('2 DOI 정규화', ['소문자, 접두어 없음', '같은 DOI는 한 줄'], True),
            ('3 메타데이터', ['제목, 연도, 초록', '상태 abstract'], False),
            ('4 OA 판 찾기', ['PDF 주소를 고름', '랜딩 페이지는 제외'], True)]
    row2 = [('5 PDF 받기', ['요청 간격, 429 처리', '%PDF- 확인, 해시'], False),
            ('6 글과 표 추출', ['PDF에서 글자, 표', '상태 pdf'], True),
            ('7 점검', ['행 합, 열 합,', '값 범위, 비율'], True),
            ('DB에 적재', ['SQLite works,', 'sources, refs'], True)]
    y1, y2 = 120.0, 430.0
    for k, (t, ls, solid) in enumerate(row1):
        box(f, P, x0 + k * (bw + gap), y1, bw, bh, t, ls, solid)
        if k:
            arrow(f, P, x0 + k * (bw + gap) - gap + 4, y1 + bh / 2, x0 + k * (bw + gap) - 4, y1 + bh / 2)
    for k, (t, ls, solid) in enumerate(row2):
        box(f, P, x0 + k * (bw + gap), y2, bw, bh, t, ls, solid)
        if k:
            arrow(f, P, x0 + k * (bw + gap) - gap + 4, y2 + bh / 2, x0 + k * (bw + gap) - 4, y2 + bh / 2)
    xe = x0 + 3 * (bw + gap) + bw / 2
    f.line(xe, y1 + bh, xe, y1 + bh + 40, P['frame'], 3.0)
    f.line(xe, y1 + bh + 40, x0 + bw / 2, y1 + bh + 40, P['frame'], 3.0)
    arrow(f, P, x0 + bw / 2, y1 + bh + 40, x0 + bw / 2, y2 - 4)
    # 범례
    ly = 700.0
    f.rect(55, ly - 26, 70, 36, '#FFFFFF', P['frame'], 3.0)
    f.text(140, ly, '이 컨테이너에서 실행해 확인(실선)', FS_I, 'start', P['text'], 400, False)
    f.rect(55, ly + 36, 70, 36, '#FFFFFF', P['frame'], 3.0, 'stroke-dasharray="14 8"')
    f.text(140, ly + 62, '실제 서버에 접속하지 못함: 가짜 서버로만 실행(z840 확인 필요, 점선)', FS_I, 'start', P['text'], 400, False)
    # 상태 계단
    sy = 900.0
    f.text(55, sy - 30, '상태(status)는 올라가기만 한다', FS_I, 'start', P['soft'], 700, False)
    for k, (nm, col) in enumerate([('cited 서지만 앎', cols[2]), ('abstract 초록까지', cols[1]), ('pdf 전문 확보', cols[0])]):
        xx = 55 + k * 400
        f.rect(xx, sy - 8, 340, 44, col if mode == 'color' else ['#DDDDDD', '#AAAAAA', '#666666'][k], P['frame'], 2.0)
        f.text(xx + 170, sy + 24, nm, FS_I, 'middle', '#FFFFFF' if (k == 2 or mode == 'color') else '#111111', 700, False)
    return f


# ============================================================ 그림 2
def fig_throttle(mode):
    D = J('throttle-result.json')
    f, P = base(mode, 860.0)
    cols = series_colors(mode)
    tmax = max(max(d['t']) for d in D) + 0.1
    L = 420.0
    X = lin(0, tmax, L, R)
    lanes = [(D[0], 210.0), (D[1], 400.0)]
    for d, y in lanes:
        f.text(L - 20, y + 10, d['name'], FS_I, 'end', P['text'], 700, False)
        f.line(L, y, R, y, P['grid'], 1.5)
        for t, c in zip(d['t'], d['codes']):
            if c == 429:                                   # 같은 시각에 겹치지 않도록 줄 아래에 따로 그린다
                yy = y + 34
                f.line(X(t) - 12, yy - 12, X(t) + 12, yy + 12, cols[0], 5.0)
                f.line(X(t) - 12, yy + 12, X(t) + 12, yy - 12, cols[0], 5.0)
            elif c == 404:
                hollow(f, X(t), y, 'sq', cols[2], 1.1)
            else:
                f.marker(X(t), y, 'dot', 1.2, cols[1])
        n = len(d['codes'])
        f.text(60, y + 90, '서버가 받은 요청 %d회, 그중 429가 %d회, 모두 끝나기까지 %.2f초' % (n, d['codes'].count(429), d['elapsed']), FS_I, 'start', P['soft'], 400, False)
    xticks(f, 570.0, X, [0, 0.5, 1.0, 1.5, 2.0, 2.5], ['0', '0.5', '1.0', '1.5', '2.0', '2.5'])
    f.text((L + R) / 2, 570.0 + 92, '첫 요청 이후의 시간 (초)', FS_S, 'middle', P['text'], 400, False)
    ly = 780.0
    f.marker(70, ly - 8, 'dot', 1.0, cols[1]); f.text(100, ly, '200 성공', FS_I, 'start', P['text'], 400, False)
    hollow(f, 330, ly - 8, 'sq', cols[2], 1.0); f.text(360, ly, '404 없음', FS_I, 'start', P['text'], 400, False)
    f.line(580, ly - 20, 604, ly + 4, cols[0], 5.0); f.line(580, ly + 4, 604, ly - 20, cols[0], 5.0); f.text(620, ly, '429 너무 빠름', FS_I, 'start', P['text'], 400, False)
    return f


# ============================================================ 그림 3
def fig_schema(mode):
    f, P = base(mode, 1130.0)
    W = 1300.0
    tb = {
        'works': (430, 60, 440, ['id', 'doi (고유, 소문자)', 'ext_id (DOI 없을 때)', 'title, authors, year', 'journal, abstract', 'status cited|abstract|pdf', 'oa_status, pdf_url', 'pdf_path, sha256', 'fulltext, chapters']),
        'sources': (60, 60, 330, ['id', 'work_id', 'source (openalex..)', 'url, http_status', 'fetched', 'raw (응답 원문)', 'raw_sha256']),
        'refs': (910, 60, 330, ['id', 'chapter_id', 'apa (서지 한 줄)', 'doi_raw', 'work_id']),
        'conflicts': (60, 560, 330, ['id', 'work_id', 'field', 'v_old, v_new', 'src_new']),
        'extracted': (450, 600, 400, ['id', 'work_id, page', 'method', 'n_rows, n_cols', 'cells (JSON)', 'checks, verdict']),
        'fetch_log': (910, 460, 330, ['id', 't', 'url', 'http_status, nbytes', 'note']),
    }
    names = {'works': 'works', 'sources': 'sources', 'refs': 'refs', 'conflicts': 'conflicts', 'extracted': 'extracted_tables', 'fetch_log': 'fetch_log'}
    pos = {}
    for k, (x, y, w, ls) in tb.items():
        h = 64 + len(ls) * 38 + 10
        f.rect(x, y, w, h, '#FFFFFF', P['frame'], 3.0)
        f.rect(x, y, w, 52, P['grid'] if mode == 'color' else '#DDDDDD', P['frame'], 3.0)
        f.text(x + 14, y + 38, names[k], FS_S, 'start', P['text'], 700, False)
        for i, s in enumerate(ls):
            f.text(x + 14, y + 92 + i * 38, s, FS_I, 'start', P['text'], 400, False)
        pos[k] = (x, y, w, h)
    cx = lambda k: pos[k][0] + pos[k][2] / 2
    # 관계선: 외래 키
    wx, wy, ww, wh = pos['works']
    f.line(pos['sources'][0] + pos['sources'][2], 190, wx, 190, P['frame'], 3.0)
    f.line(wx + ww, 302, pos['refs'][0], 302, P['frame'], 3.0)
    f.line(wx + ww / 2 - 100, wy + wh, wx + ww / 2 - 100, 540, P['frame'], 3.0)
    f.line(225, 540, wx + ww / 2 - 100, 540, P['frame'], 3.0); f.line(225, 540, 225, 560, P['frame'], 3.0)
    f.line(cx('extracted'), wy + wh, cx('extracted'), 600, P['frame'], 3.0)
    f.text(910, 980, '외래 키 없는 독립 표', FS_I, 'start', P['soft'], 400, False)
    f.text(60, 1100, '선은 work_id(외래 키)로 works에 이어짐', FS_I, 'start', P['soft'], 400, False)
    return f


# ============================================================ 그림 4
def fig_extract(mode):
    f, P = base(mode, 1560.0)
    cols = series_colors(mode)
    TE = J('table-extract-result.json')['summary']
    SY = J('synth-result.json')
    # 위 칸: 제1권 PDF 36개 표
    f.text(60, 70, '(가) 제1권 조판 PDF의 표 36개(정답 행 394줄)', FS_S, 'start', P['text'], 700, False)
    X = lin(0, 100, L + 250, R)
    names = list(TE.keys())
    short = ['선 기준', '글자 위치 기준', 'pdftotext -layout']
    for i, nm in enumerate(names):
        y = 140 + i * 78
        v = 100.0 * TE[nm]['rows_exact'] / TE[nm]['rows']
        f.text(L + 230, y + 30, short[i], FS_I, 'end', P['text'], 400, False)
        f.rect(L + 250, y, X(v) - (L + 250), 52, cols[1], P['frame'], 1.5)
        f.text(X(v) + 14 if v < 85 else X(v) - 14, y + 38, '%.1f%%' % v, FS_I, 'start' if v < 85 else 'end', P['text'] if v < 85 else '#FFFFFF', 700, False)
    f.line(L + 250, 120, L + 250, 380, P['frame'], 2.0)
    # 아래 칸: 시연 PDF 세 가지 조판 x 다섯 방법
    f.text(60, 470, '(나) 같은 36개 표를 다시 조판한 시연 PDF(정답 행 394줄)', FS_S, 'start', P['text'], 700, False)
    meths = list(SY.keys())
    shortm = ['pdfplumber 선 기준', 'pdfplumber 글자 위치', 'pdftotext -layout', 'pdftotext -raw', 'pdfplumber 글자 흐름']
    lay = [('L', '선 있음, 행 순서', cols[1]), ('R', '선 없음, 행 순서', cols[2]), ('C', '선 없음, 열 순서', cols[0])]
    for i, m in enumerate(meths):
        y0 = 540 + i * 150
        f.text(L + 230, y0 + 70, shortm[i], FS_I, 'end', P['text'], 700, False)
        for k, (md, nm, c) in enumerate(lay):
            e, j, g = SY[m][md]
            v = 100.0 * e / g
            yy = y0 + k * 44
            f.rect(L + 250, yy, max(1.0, X(v) - (L + 250)), 36, c, P['frame'], 1.5)
            f.text(X(max(v, 0)) + 14 if v < 85 else X(v) - 14, yy + 28, '%.0f%%' % v, FS_I, 'start' if v < 85 else 'end', P['text'] if v < 85 else '#FFFFFF', 400, False)
    f.line(L + 250, 520, L + 250, 540 + 5 * 150 - 20, P['frame'], 2.0)
    xticks(f, 540 + 5 * 150 - 20, X, [0, 20, 40, 60, 80, 100], ['0', '20', '40', '60', '80', '100'])
    f.text((L + 250 + R) / 2, 540 + 5 * 150 + 64, '온전한 행의 비율 (%)', FS_S, 'middle', P['text'], 400, False)
    ly = 540 + 5 * 150 + 150
    for k, (md, nm, c) in enumerate(lay):
        f.rect(60 + k * 410, ly - 28, 44, 32, c, P['frame'], 1.5)
        f.text(116 + k * 410, ly, nm, FS_I, 'start', P['text'], 400, False)
    return f


# ============================================================ 그림 5
def fig_order(mode):
    G = J('scatter-geometry.json')
    f, P = base(mode, 800.0)
    cols = series_colors(mode)
    for pi, (md, title) in enumerate([('R', '행 순서로 쓴 PDF'), ('C', '열 순서로 쓴 PDF')]):
        pts = G[md]['pts']
        pw, ph = G[md]['page']
        x0 = 70 + pi * 640
        wbox, hbox = 560.0, 560.0
        y0 = 150.0
        f.text(x0, 100, title, FS_S, 'start', P['text'], 700, False)
        f.rect(x0, y0, wbox, hbox, '#FFFFFF', P['frame'], 2.4)
        sx = lambda x: x0 + 20 + (x - 20) / (pw - 40) * (wbox - 40)
        ymin = min(p[1] for p in pts); ymax = max(p[1] for p in pts)
        sy = lambda y: y0 + 40 + (y - ymin) / (ymax - ymin) * (hbox - 80)
        path = [(sx(x), sy(y)) for x, y, _ in pts[1:]]            # 첫 낱말은 캡션이므로 뺀다
        for a, b in zip(path, path[1:]):
            f.line(a[0], a[1], b[0], b[1], cols[2] if mode == 'color' else '#999999', 2.0)
        for k, (x, y) in enumerate(path):
            f.marker(x, y, 'dot', 0.8, cols[1] if mode == 'color' else '#333333')
        for k in (0, 5, 10, 15, 20, 24):
            if k < len(path):
                f.text(path[k][0] + 14, path[k][1] - 12, '%d' % (k + 1), FS_I, 'start', cols[0], 700, True)
    f.text(70, 760, '번호는 PDF 안에 글자가 쓰인 순서(1 = 표의 첫 칸). 점은 낱말의 왼쪽 위 위치.', FS_I, 'start', P['soft'], 400, False)
    return f


# ============================================================ 그림 6
def fig_repair(mode):
    f, P = base(mode, 760.0)
    cols = series_colors(mode)
    S = J('scatter-result.json')
    items = [('합 점검만으로 남는 방향의 경우의 수', 2 ** 17, '17행이면 2의 17제곱'),
             ('변화 강도의 사슬을 더한 뒤', 2, '전체를 뒤집은 두 가지만 남음'),
             ('본문의 기준값(80.19, 320.06 km)을 더한 뒤', 1, '17행 중 %d행이 제1권 표와 같음' % S['orient_ok'])]
    X = logmap(1, 200000, 130.0, R)
    f.text(60, 80, '(AC, NC) 방향의 남는 경우의 수(로그 눈금)', FS_S, 'start', P['text'], 700, False)
    for k, (lab, n, note_) in enumerate(items):
        yy = 150.0 + k * 150
        f.text(60, yy + 30, lab, FS_I, 'start', P['text'], 400, False)
        w = max(X(n) - 130.0, 12.0)
        f.rect(130, yy + 50, w, 50, cols[1] if k == 0 else (cols[2] if k == 1 else cols[0]), P['frame'], 1.5)
        f.text(130 + w + 14, yy + 88, '%s, %s' % (format(n, ','), note_), FS_I, 'start' if w < 700 else 'end', P['text'], 700, False) if w < 700 else f.text(130 + w - 14, yy + 88, '%s' % format(n, ','), FS_I, 'end', '#FFFFFF', 700, False)
    xticks(f, 620, X, [1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1천', '1만', '10만'])
    f.text((130 + R) / 2, 620 + 92, '경우의 수', FS_S, 'middle', P['text'], 400, False)
    return f


FIGS = [('flow', fig_flow), ('throttle', fig_throttle), ('schema', fig_schema), ('extract', fig_extract), ('order', fig_order), ('repair', fig_repair)]
if __name__ == '__main__':
    for name, fn in FIGS:
        for mode in ('color', 'bw'):
            f = fn(mode)
            path = os.path.join(OUT, 'fig-ch02-%s-v1-%s.svg' % (name, mode))
            w = f.save(path)
            print('%-9s %-5s %s 경고 %d %s' % (name, mode, os.path.basename(path), len(w), w[:6]))
