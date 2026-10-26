# -*- coding: utf-8 -*-
"""실습 14-3: 제1권 원고가 사료 구절을 재인용한 곳을 '재인용' 상태로 적재한다. 구절을 새로 만들지 않고 제1권 원고의 글자를 옮긴다.
적재한 뒤 (가) 원고의 글자와 DB 의 글자가 같은지 다시 읽어 대조하고, (나) 제1권 4장 전체의 한자 인용이 DB 에 있는지 점검한다.
로그에는 한자 구절을 찍지 않고 행 번호, 글자 수, 해시 앞 8자리만 적는다."""
import os, sys, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P, vol1load as V

t0 = time.time()
con = P.connect(os.path.join(P.HERE, 'out', 'vol1-passages.db'), fresh=True)
p4 = V.load_ch04(con); pd = V.load_ch04_danju(con); p9 = V.load_ch09(con); p11 = V.load_ch11(con)
con.commit()
print('[적재] 제1권 4장 표 %d행, 4장 단주 인용 %d행, 9장 표 %d행, 11장 표 %d행 (모두 상태 재인용)' % (len(p4), len(pd), len(p9), len(p11)))
print('  상태별:', dict(con.execute('SELECT status, COUNT(*) FROM passage GROUP BY status').fetchall()))
print('  원문(text)이 있는 구절 %d건, 서술만 있는 구절 %d건' % (con.execute('SELECT COUNT(*) FROM passage WHERE text IS NOT NULL').fetchone()[0], con.execute('SELECT COUNT(*) FROM passage WHERE text IS NULL').fetchone()[0]))
print('  서명 %d, 판본 %d, 권·편 %d' % tuple(con.execute('SELECT COUNT(*) FROM %s' % t).fetchone()[0] for t in ('work', 'edition', 'section')))

print('\n[한자 구절은 찍지 않고 위치만] 4장 표에서 옮긴 %d건' % len(p4))
print('  id  서명(독음)           권     편   연도  글자수  해시앞8  제1권 위치')
for r in con.execute('''SELECT p.passage_id, w.title_ko, COALESCE(s.juan,'-') j, COALESCE(s.pyeon,'-') py, p.year_from y, length(p.text) n, substr(p.text_sha256,1,8) h, p.locator
                        FROM passage p JOIN section s USING(section_id) JOIN work w ON w.work_id=s.work_id WHERE p.passage_id IN (%s) ORDER BY 1''' % ','.join(map(str, p4))):
    print('  %2d  %-14s %-6s %-4s %5s %5d  %s  %s' % tuple(r))

print('\n[cite 시험] 원문이 없는 재인용(9장 표 첫 행)과 원문이 있는 재인용(꼬리표만 보임)')
print('  ', P.cite(con, p9[0]))
r0 = con.execute('SELECT p.secondary_source, w.title_ko, e.label, p.collation FROM passage p JOIN section s USING(section_id) JOIN work w ON w.work_id=s.work_id JOIN edition e ON e.edition_id=p.edition_id WHERE p.passage_id=?', (p4[0],)).fetchone()
print('   [재인용: %s] (구절은 한자라 생략) (%s, %s; 교감 %s)' % tuple(r0))

print('\n[대조 1] 적재한 글자 = 제1권 원고에 적힌 글자? (원고를 다시 읽어 칸을 잘라 비교)')
lines = V.read_md(4)
rows = V.table_after(lines, 'Yun 등(2023)이 든 사료 기록')
ok = 0
for pid, (ln, cells) in zip(p4, rows):
    t = con.execute('SELECT text FROM passage WHERE passage_id=?', (pid,)).fetchone()[0]
    ok += (t == cells[2] and cells[2] in lines[ln - 1])
print('  %d / %d 건이 같음.  해시 재계산 어긋남: %s' % (ok, len(p4), P.verify_hashes(con)))

print('\n[대조 2] 제1권 4장 원고의 따옴표 안 한자 인용이 DB 원문에 글자 그대로 있는가')
tbl_lines = {ln for ln, _ in rows}
quotes = []
for i, l in enumerate(lines, 1):
    if i in tbl_lines:
        continue
    for m in re.finditer(r'["“]([^"”\n]*[一-鿿][^"”\n]*)["”]', l):
        quotes.append((i, m.group(1)))
found, miss = [], []
for i, q in quotes:
    (found if P.quote_audit(con, q) else miss).append((i, q))
print('  따옴표 안에 한자가 든 인용 %d건 (표 안의 행은 제외): DB 원문에 있음 %d건, 없음 %d건' % (len(quotes), len(found), len(miss)))
print('  없음 목록(행 번호, 글자 수):', [(i, len(q)) for i, q in miss])
print('  있음 목록(행 번호, 글자 수):', [(i, len(q)) for i, q in found])
# 서명으로 쓰인 한자는 구절이 아니므로 따로 센다
titles = {r[0] for r in con.execute('SELECT title_orig FROM work WHERE title_orig IS NOT NULL')}
miss2 = [(i, q) for i, q in miss if q not in titles]
print('  서명만 인용한 것을 빼면 DB 에 없는 인용 %d건: 행 번호 %s' % (len(miss2), [i for i, _ in miss2]))
dan_ln = next(i + 1 for i, l in enumerate(lines) if l.startswith('| 端州 |'))
circ = [(i, q) for i, q in found if i == dan_ln]
print('  이 가운데 단주 행(%d행)의 인용 %d건은 같은 행에서 적재한 것이므로 항상 있다(순환). 순환이 아닌 일치는 %d건이다.' % (dan_ln, len(circ), len(found) - len(circ)))
print('  따옴표 안 글자가 2글자인 인용 %d건은 아무 구절에나 걸릴 수 있어 일치의 힘이 약하다.' % sum(1 for _, q in found if len(q) <= 2))
print('\n걸린 시간 %.2f초' % (time.time() - t0))
