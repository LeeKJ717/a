# -*- coding: utf-8 -*-
"""실습 2-5: 제1권 조판 PDF(book-color-v20.pdf)의 표를 여러 방법으로 뽑아 정답(제1권 원고의 표)과 견준다.
정답 단위: 표의 한 행. 뽑은 행이 정답의 행과 (공백을 뺀) 글자까지 모두 같으면 '온전히 되살린 행'이다.
실행: python3 05-table-extract.py | tee 05-table-extract.log"""
import json, re, subprocess, sys, time, collections, statistics
import pdfplumber
import vol1gt

PDF = '/home/claude/book/build/book-color-v20.pdf'
t0 = time.time()
txt = subprocess.run(['pdftotext', '-layout', PDF, '-'], capture_output=True, text=True).stdout.split('\f')
print('PDF 쪽 수(pdftotext):', len(txt) - 1, '/ 걸린 시간 %.1f초' % (time.time() - t0))

# 표 캡션이 있는 쪽 찾기: '표 9-2.' 꼴
cap_page = {}
for pg, s in enumerate(txt, 1):
    for m in re.finditer(r'표\s*(\d+)-(\d+)\.', s):
        cap_page.setdefault((int(m.group(1)), int(m.group(2))), pg)

GT = []
for ch, p in sorted(vol1gt.latest().items()):
    for n, cap, rows in vol1gt.tables(ch, p):
        GT.append(dict(ch=ch, n=n, cap=cap, rows=rows, page=cap_page.get((ch, n))))
print('정답 표 %d개, 쪽을 찾은 것 %d개' % (len(GT), sum(1 for g in GT if g['page'])))


def is_num(c):
    return bool(re.fullmatch(r'[-+−]?\d[\d,]*\.?\d*%?', vol1gt.norm(c)))


for g in GT:
    cells = [c for r in g['rows'][1:] for c in r if c.strip()]
    g['numfrac'] = sum(is_num(c) for c in cells) / max(1, len(cells))
    g['ncol'] = max(len(r) for r in g['rows'])
    g['nrow'] = len(g['rows'])
# 대상: 쪽을 찾았고, 열 3개 이상, 행 3개 이상, 칸의 절반 이상이 숫자인 표(숫자 표가 점검 대상이므로)
SEL = [g for g in GT if g['page'] and g['ncol'] >= 3 and g['nrow'] >= 3 and g['numfrac'] >= 0.5]
print('대상(열>=3, 행>=3, 숫자 칸 비율>=0.5): %d개' % len(SEL))
print('대상 표의 크기: 행 중앙값 %d, 열 중앙값 %d, 숫자 칸 비율 중앙값 %.2f' % (
    statistics.median(g['nrow'] for g in SEL), statistics.median(g['ncol'] for g in SEL), statistics.median(g['numfrac'] for g in SEL)))

pdf = pdfplumber.open(PDF)
PAGES_AFTER = 2          # 캡션 쪽과 그 뒤 두 쪽까지 본다(쪽을 넘어가는 표)


def rows_pl(pages, settings):
    out = []
    for pg in pages:
        for t in pdf.pages[pg - 1].extract_tables(settings) if settings else pdf.pages[pg - 1].extract_tables():
            for r in t:
                out.append([c or '' for c in r])
    return out


def rows_layout(pages):
    out = []
    for pg in pages:
        for ln in txt[pg - 1].splitlines():
            parts = [x for x in re.split(r'\s{2,}', ln.strip()) if x]
            if len(parts) >= 2:
                out.append(parts)
    return out


METHODS = {
    'pdfplumber 선 기준(기본)': lambda pages: rows_pl(pages, None),
    'pdfplumber 글자 위치 기준': lambda pages: rows_pl(pages, {'vertical_strategy': 'text', 'horizontal_strategy': 'text'}),
    'pdftotext -layout, 두 칸 이상 공백으로 쪼갬': rows_layout,
}


def score(g, got):
    gt_rows = [tuple(vol1gt.norm(c) for c in r) for r in g['rows']]
    got_rows = set(tuple(vol1gt.norm(c) for c in r) for r in got)
    got_cells = collections.Counter(vol1gt.norm(c) for r in got for c in r if vol1gt.norm(c))
    exact = sum(1 for r in gt_rows if r in got_rows)
    cells = [c for r in gt_rows for c in r if c]
    pool = got_cells.copy()
    hit = 0
    for c in cells:                       # 칸이 '어디엔가' 있기만 해도 센다(열 배치는 무시)
        if pool[c] > 0:
            pool[c] -= 1; hit += 1
    return exact, len(gt_rows), hit, len(cells)


res = {m: [] for m in METHODS}
tm = {m: 0.0 for m in METHODS}
for g in SEL:
    pages = [g['page'] + k for k in range(PAGES_AFTER + 1) if g['page'] + k <= len(txt) - 1]
    for m, f in METHODS.items():
        t = time.time()
        try:
            got = f(pages)
        except Exception as e:
            got = []
            print('오류', m, g['ch'], g['n'], repr(e)[:80])
        tm[m] += time.time() - t
        e, nr, h, nc = score(g, got)
        res[m].append(dict(ch=g['ch'], n=g['n'], exact=e, rows=nr, hit=h, cells=nc, ncol=g['ncol']))

print('\n방법별 결과(정답 행 %d줄, 정답 칸 %d개)' % (sum(r['rows'] for r in res[next(iter(METHODS))]), sum(r['cells'] for r in res[next(iter(METHODS))])))
print('%-46s %-22s %-22s %s' % ('방법', '온전한 행', '칸이 어딘가에 있음', '걸린 시간'))
summary = {}
for m in METHODS:
    R = res[m]
    er, nr = sum(r['exact'] for r in R), sum(r['rows'] for r in R)
    hh, nc = sum(r['hit'] for r in R), sum(r['cells'] for r in R)
    full = sum(1 for r in R if r['exact'] == r['rows'])
    summary[m] = dict(rows_exact=er, rows=nr, cells_hit=hh, cells=nc, tables_full=full, tables=len(R), sec=tm[m])
    print('%-46s %5d/%d (%.1f%%)  %5d/%d (%.1f%%)  표 전체가 맞은 것 %d/%d  %.1f초' % (
        m, er, nr, 100 * er / nr, hh, nc, 100 * hh / nc, full, len(R), tm[m]))
json.dump(dict(summary=summary, tables=res, selected=[(g['ch'], g['n'], g['page'], g['nrow'], g['ncol'], round(g['numfrac'], 2)) for g in SEL]),
          open('out/table-extract-result.json', 'w'), ensure_ascii=False)

# 열 수별로: 선 기준 방법이 어디서 틀리는가
print('\n선 기준(pdfplumber 기본)에서 표 전체가 맞지 않은 표')
bad = [r for r in res['pdfplumber 선 기준(기본)'] if r['exact'] < r['rows']]
for r in bad[:40]:
    print('  표 %d-%d: 행 %d 중 온전한 %d, 칸 %d 중 어딘가에 %d, 열 %d' % (r['ch'], r['n'], r['rows'], r['exact'], r['cells'], r['hit'], r['ncol']))
print('  (모두 %d개)' % len(bad))
