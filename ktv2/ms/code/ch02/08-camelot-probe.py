# -*- coding: utf-8 -*-
"""실습 2-5b: Camelot 1.0.9를 제1권 PDF의 표 셋에 써 본다(대량 시험에서 빠진 까닭: 674쪽 PDF에서 호출 한 번이 약 20초).
정답 표의 크기와 견주고, 칸 내용이 정답 행과 일치하는 행 수를 센다. 실행: python3 08-camelot-probe.py | tee 08-camelot-probe.log"""
import json, time
import camelot
import vol1gt
PDF = '/home/claude/book/build/book-color-v20.pdf'
r = json.load(open('out/table-extract-result.json'))
sel = r['selected'][:3]
lat = vol1gt.latest()
for ch, n, pg, nr, nc, nf in sel:
    gt = [t for k, c, t in vol1gt.tables(ch, lat[ch]) if k == n][0]
    G = [tuple(vol1gt.norm(c) for c in row) for row in gt]
    print('표 %d-%d (쪽 %d): 정답 %d행 x %d열' % (ch, n, pg, len(gt), max(len(x) for x in gt)))
    for flavor in ('lattice', 'stream'):
        t0 = time.time()
        ts = camelot.read_pdf(PDF, pages=str(pg), flavor=flavor)
        rows = set()
        for tb in ts:
            for row in tb.df.values.tolist():
                rows.add(tuple(vol1gt.norm(c) for c in row))
        ok = sum(1 for g in G if g in rows)
        print('   %-8s 표 %d개 %s, 정답 행 %d/%d 온전, %.1f초' % (flavor, len(ts), [tuple(x.shape) for x in ts], ok, len(G), time.time() - t0))
