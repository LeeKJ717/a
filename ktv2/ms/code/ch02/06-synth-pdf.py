# -*- coding: utf-8 -*-
"""실습 2-6: 같은 36개 표를 '선 없는 표'로 다시 조판해 추출 방법을 견준다(시연 PDF: 이 책이 WeasyPrint로 만든 것).
세 가지 조판: L = 선이 있는 표(글자를 행 순서로 씀), R = 선 없음(행 순서), C = 선 없음(글자를 열 순서로 씀; 일부 논문 PDF가 이렇게 만들어진다고 짐작하는 모양).
실행: python3 06-synth-pdf.py | tee 06-synth-pdf.log"""
import json, re, subprocess, os, time, collections
import pdfplumber
import html
from weasyprint import HTML
import vol1gt

FS, RH, PAD = 8, 13, 14        # 글자 크기(pt), 행 높이(pt), 열 사이 여백(pt)
os.makedirs('out/synth', exist_ok=True)
sel = json.load(open('out/table-extract-result.json'))['selected']
lat = vol1gt.latest()
GT = {}
for ch, n, pg, nr, nc, nf in sel:
    for k, cap, rows in vol1gt.tables(ch, lat[ch]):
        if k == n:
            GT[(ch, n)] = rows


def wpt(s):
    """글자 너비 어림(pt): 한글·한자 1em, 그 밖에 0.6em. 열 너비를 정하는 데만 쓴다."""
    return sum(FS if ord(ch) > 0x2E80 else 0.6 * FS for ch in s)


def make(path, rows, mode, cap):
    """WeasyPrint로 만든다(글꼴 Noto Sans CJK KR을 PDF에 심는다). 칸마다 절대 위치의 상자 하나를 두고 DOM 순서가 곧 PDF 글자 순서가 된다."""
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    w = [max(wpt(r[j]) for r in rows) + PAD for j in range(ncol)]
    W, H = sum(w) + 60, len(rows) * RH + 70
    x = [30]
    for a in w:
        x.append(x[-1] + a)
    border = 'border:0.5pt solid #000;' if mode == 'L' else ''
    order = [(i, j) for i in range(len(rows)) for j in range(ncol)] if mode in ('L', 'R') else [(i, j) for j in range(ncol) for i in range(len(rows))]
    boxes = ['<div style="position:absolute;left:30pt;top:10pt;white-space:nowrap">Table %s</div>' % cap]
    for i, j in order:
        boxes.append('<div style="position:absolute;left:%.1fpt;top:%.1fpt;width:%.1fpt;height:%dpt;%swhite-space:nowrap;padding-left:4pt;box-sizing:border-box;line-height:%dpt">%s</div>'
                     % (x[j], 40 + i * RH, w[j], RH, border, RH, html.escape(rows[i][j])))
    doc = ('<html><head><meta charset="utf-8"><style>@page{size:%.0fpt %.0fpt;margin:0}body{margin:0;font:%dpt "Noto Sans CJK KR"}</style></head><body>%s</body></html>'
           % (W, H, FS, ''.join(boxes)))
    HTML(string=doc).write_pdf(path)


def n_(s):
    return vol1gt.norm(s)


def score_rows(gt, got):
    G = [tuple(n_(c) for c in r) for r in gt]
    S = set(tuple(n_(c) for c in r) for r in got)
    J = set(''.join(n_(c) for c in r) for r in got)
    e = sum(1 for r in G if r in S)
    j = sum(1 for r in G if ''.join(r) in J)
    return e, j, len(G)


def pl_rows(page, st):
    out = []
    for t in (page.extract_tables(st) if st else page.extract_tables()):
        out += [[c or '' for c in r] for r in t]
    return out


def lines_to_rows(s, split):
    return [split(l) for l in s.splitlines() if l.strip()]


SAMPLE = max(GT, key=lambda k: len(GT[k]))      # 행이 가장 많은 표를 견본으로 쓴다
METH = ['pdfplumber 선 기준', 'pdfplumber 글자 위치 기준', 'pdftotext -layout(두 칸 공백)', 'pdftotext -raw(줄 그대로)', 'pdfplumber 글자 흐름(use_text_flow)']
RES = {m: {md: [0, 0, 0] for md in 'LRC'} for m in METH}
sample = {}
t0 = time.time()
for (ch, n), rows in sorted(GT.items()):
    for md in 'LRC':
        p = 'out/synth/t%02d-%02d-%s.pdf' % (ch, n, md)
        if not os.path.exists(p):                 # WeasyPrint는 느리다(108장에 6분). 있으면 다시 만들지 않는다
            make(p, rows, md, '%d-%d' % (ch, n))
        pdf = pdfplumber.open(p)
        page = pdf.pages[0]
        outs = {
            METH[0]: pl_rows(page, None),
            METH[1]: pl_rows(page, {'vertical_strategy': 'text', 'horizontal_strategy': 'text'}),
            METH[2]: lines_to_rows(subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, text=True).stdout, lambda l: [x for x in re.split(r'\s{2,}', l.strip()) if x]),
            METH[3]: lines_to_rows(subprocess.run(['pdftotext', '-raw', p, '-'], capture_output=True, text=True).stdout, lambda l: l.split()),
            METH[4]: lines_to_rows(page.extract_text(use_text_flow=True) or '', lambda l: l.split()),
        }
        for m, got in outs.items():
            e, j, g = score_rows(rows, got)
            RES[m][md][0] += e; RES[m][md][1] += j; RES[m][md][2] += g
        if (ch, n) == SAMPLE and md == 'C':
            sample['raw'] = subprocess.run(['pdftotext', '-raw', p, '-'], capture_output=True, text=True).stdout.splitlines()
            sample['layout'] = subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, text=True).stdout.splitlines()
print('표 %d개 x 조판 3가지 x 방법 %d가지, 걸린 시간 %.1f초' % (len(GT), len(METH), time.time() - t0))
print('\n각 칸: 온전한 행 수(칸 배열까지 같음) / 행 글자가 순서대로 이어서 같은 행 수 / 정답 행 수')
print('%-40s %-26s %-26s %-26s' % ('방법', 'L 선 있음(행 순서)', 'R 선 없음(행 순서)', 'C 선 없음(열 순서)'))
for m in METH:
    print('%-40s' % m, *['%4d / %4d / %d' % tuple(RES[m][md]) + '    ' for md in 'LRC'])
json.dump(RES, open('out/synth-result.json', 'w'), ensure_ascii=False)
print('\n표 %d-%d(%d행 x %d열)를 C로 조판한 PDF에서 pdftotext -raw의 앞 12줄:' % (SAMPLE + (len(GT[SAMPLE]), max(len(r) for r in GT[SAMPLE]))))
for l in sample['raw'][:12]:
    print('   |', l)
print('같은 PDF에서 pdftotext -layout의 앞 6줄:')
for l in sample['layout'][:6]:
    print('   |', l)
