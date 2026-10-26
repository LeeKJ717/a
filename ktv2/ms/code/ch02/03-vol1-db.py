# -*- coding: utf-8 -*-
"""실습 2-4: 제1권 DB(ktv1bookdb-v14.sqlite, 읽기 전용)의 papers, refs에 DOI 정규화와 새 상태 규칙을 적용해 본다.
실행: python3 03-vol1-db.py | tee 03-vol1-db.log"""
import sqlite3, collections
import paperlib as pl

SRC = '/home/claude/book/db/ktv1bookdb-v14.sqlite'
v = sqlite3.connect('file:%s?mode=ro' % SRC, uri=True)
print('제1권 DB:', SRC)
for t in ('papers', 'refs', 'chapters'):
    print('  %-9s %d줄' % (t, v.execute('SELECT COUNT(*) FROM %s' % t).fetchone()[0]))
print('papers 열:', [r[1] for r in v.execute('PRAGMA table_info(papers)')])
print('refs 열  :', [r[1] for r in v.execute('PRAGMA table_info(refs)')])

print('\n== papers')
P = v.execute('SELECT id, doi, status, sha256, fulltext IS NOT NULL AND length(fulltext)>0, chapters FROM papers').fetchall()
print('상태:', collections.Counter(r[2] for r in P))
print('상태별 (sha256 있음, 전문 있음):', {s: (sum(1 for r in P if r[2] == s and r[3]), sum(1 for r in P if r[2] == s and r[4])) for s in {r[2] for r in P}})
ch = [r for r in P if r[1]]
print('DOI 있는 줄:', len(ch), '/ 전체', len(P))
changed = [(r[1], pl.doi_norm(r[1])) for r in ch if pl.doi_norm(r[1]) != r[1]]
print('정규화로 바뀐 DOI:', len(changed), changed[:5])
print('이미 소문자·접두어 없음:', sum(1 for r in ch if r[1] == r[1].lower() and r[1].startswith('10.')))
nd = collections.Counter(pl.doi_norm(r[1]) for r in ch)
print('정규화 후 같은 DOI가 겹치는 papers 줄:', [k for k, n in nd.items() if n > 1])
odd = [(r[0], r[1]) for r in P if r[1] and pl.doi_norm(r[1]) is None]
print('DOI 칸에 DOI가 아닌 값이 든 papers 줄:', odd, v.execute('SELECT substr(title,1,50), status FROM papers WHERE id=?', (odd[0][0],)).fetchone() if odd else '')

print('\n== refs')
R = v.execute('SELECT id, chapter_id, doi FROM refs').fetchall()
print('refs 줄', len(R), '/ DOI 칸이 빈 줄', sum(1 for r in R if not r[2]))
rn = [pl.doi_norm(r[2]) for r in R if r[2]]
print('정규화 못 한 DOI:', sum(1 for x in rn if x is None))
print('refs의 서로 다른 DOI(정규화 후):', len(set(rn)), ' (정규화 전:', len({r[2] for r in R if r[2]}), ')')
raw_forms = collections.Counter('https://doi.org/' if r[2].lower().startswith('http') else ('doi:' if r[2].lower().startswith('doi') else '10.') for r in R if r[2])
print('refs DOI 표기 모양:', dict(raw_forms))
papers_doi = {pl.doi_norm(r[1]) for r in ch}
ref_doi = set(rn)
print('refs DOI 중 papers에도 있는 것:', len(ref_doi & papers_doi), ' refs에만 있는 것:', len(ref_doi - papers_doi), ' papers에만 있는 것:', len(papers_doi - ref_doi))

print('\n== 새 상태 규칙으로 옮기면')
status = {}
for r in P:
    d = (pl.doi_norm(r[1]) or r[1]) if r[1] else None      # DOI가 아니면 ext_id로 쓴다(openalex:W...)
    if d and r[2] == 'pdf' and r[3]:
        status[d] = 'pdf'
    elif d:
        status.setdefault(d, 'cited')       # 제1권의 meta, nopdf가 abstract를 뜻하는지는 DB에서 확인하지 못해 cited로 둔다
for d in ref_doi - papers_doi:
    status.setdefault(d, 'cited')
nx = sum(1 for k in status if not k.startswith('10.'))
print('새 works 줄 수(서로 다른 식별자):', len(status), '(그중 DOI 없는 것 %d)' % nx, ' 상태:', dict(collections.Counter(status.values())))
