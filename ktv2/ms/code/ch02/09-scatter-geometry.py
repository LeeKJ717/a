# -*- coding: utf-8 -*-
"""실습 2-6b: 같은 표를 행 순서(R)와 열 순서(C)로 쓴 시연 PDF에서, 글자가 PDF 안에 쓰인 순서와 쪽 위의 위치를 견준다(그림의 자료).
실행: python3 09-scatter-geometry.py | tee 09-scatter-geometry.log"""
import json
import pdfplumber
T = (2, 10)
out = {}
for md in 'RC':
    page = pdfplumber.open('out/synth/t%02d-%02d-%s.pdf' % (T[0], T[1], md)).pages[0]
    # 한 칸의 글이 공백을 품으면 여러 낱말로 쪼개지므로, 글자 흐름(use_text_flow)으로 줄을 읽고 낱말 위치를 쓴다
    words = page.extract_words(use_text_flow=True, keep_blank_chars=True, x_tolerance=3)
    pts = [(round(w['x0'], 1), round(w['top'], 1), w['text']) for w in words]
    steps = list(zip(pts, pts[1:]))
    row_major = sum(1 for a, b in steps if b[1] >= a[1] - 0.5)         # 다음 낱말이 같은 줄이거나 아래
    col_major = sum(1 for a, b in steps if b[0] >= a[0] - 0.5)         # 다음 낱말이 같은 열이거나 오른쪽
    print('%s: 낱말 %d개, 쓰인 순서로 이웃한 쌍 %d개 중 다음이 같은 높이이거나 아래: %d, 같은 x이거나 오른쪽: %d' % (md, len(pts), len(steps), row_major, col_major))
    out[md] = dict(pts=pts, page=(page.width, page.height))
    print('   앞 8개:', [p[2] for p in pts[:8]])
json.dump(out, open('out/scatter-geometry.json', 'w'), ensure_ascii=False)
