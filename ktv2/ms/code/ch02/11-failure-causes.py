# -*- coding: utf-8 -*-
"""실습 2-6c: 시연 PDF(L 조판)에서 pdftotext -layout과 pdfplumber 글자 위치 기준이 놓친 행의 원인을 센다.
정답 행에 빈 칸이 있는가, 칸 안에 공백이 있는가를 본다. 실행: python3 11-failure-causes.py | tee 11-failure-causes.log"""
import json, re, subprocess
import pdfplumber
import vol1gt

sel = json.load(open('out/table-extract-result.json'))['selected']
lat = vol1gt.latest()
n_ = vol1gt.norm
tot = dict(rows=0, lay_fail=0, lay_fail_empty=0, lay_fail_space=0, txt_fail=0, txt_fail_empty=0, txt_fail_space=0, empty_rows=0, space_rows=0)
for ch, n, *_ in sel:
    rows = [r for k, c, r in vol1gt.tables(ch, lat[ch]) if k == n][0]
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    p = 'out/synth/t%02d-%02d-L.pdf' % (ch, n)
    lay = subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, text=True).stdout
    got_lay = set(tuple(n_(c) for c in [x for x in re.split(r'\s{2,}', l.strip()) if x]) for l in lay.splitlines() if l.strip())
    pg = pdfplumber.open(p).pages[0]
    got_txt = set()
    for t in pg.extract_tables({'vertical_strategy': 'text', 'horizontal_strategy': 'text'}):
        for r in t:
            got_txt.add(tuple(n_(c or '') for c in r))
    lay_nonempty_ok = 0
    for r in rows:
        key = tuple(n_(c) for c in r)
        has_empty = any(not c.strip() for c in r)
        has_space = any(re.search(r'\s', c.strip()) for c in r)
        tot['rows'] += 1; tot['empty_rows'] += has_empty; tot['space_rows'] += has_space
        if key not in got_lay:
            tot['lay_fail'] += 1; tot['lay_fail_empty'] += has_empty; tot['lay_fail_space'] += has_space
        if has_empty and tuple(x for x in key if x) in got_lay:
            tot['lay_empty_dropped_ok'] = tot.get('lay_empty_dropped_ok', 0) + 1     # 빈 칸을 건너뛴 채로는 글자가 맞음
        if key not in got_txt:
            tot['txt_fail'] += 1; tot['txt_fail_empty'] += has_empty; tot['txt_fail_space'] += has_space
print(json.dumps(tot, ensure_ascii=False))
print('정답 행 %d줄: 빈 칸이 있는 행 %d, 칸 안에 공백이 있는 행 %d' % (tot['rows'], tot['empty_rows'], tot['space_rows']))
print('pdftotext -layout이 놓친 행 %d줄 중 빈 칸이 있는 행 %d, 칸 안에 공백이 있는 행 %d' % (tot['lay_fail'], tot['lay_fail_empty'], tot['lay_fail_space']))
print('빈 칸이 있는 행 가운데, 빈 칸을 건너뛴 글자 순서로는 맞은 행: %d' % tot.get('lay_empty_dropped_ok', 0))
print('pdfplumber 글자 위치 기준이 놓친 행 %d줄 중 빈 칸이 있는 행 %d, 칸 안에 공백이 있는 행 %d' % (tot['txt_fail'], tot['txt_fail_empty'], tot['txt_fail_space']))
