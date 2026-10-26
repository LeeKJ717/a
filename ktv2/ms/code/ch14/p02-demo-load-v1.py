# -*- coding: utf-8 -*-
"""실습 14-2: 시연 레코드(가상)를 적재하고, 질의하고, 인용 규칙(DB 에 넣은 것만 인용)을 시험한다."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P, demorec

t0 = time.time()
con = P.connect(os.path.join(P.HERE, 'out', 'demo.db'), fresh=True)
ids = demorec.load(con)
print('[적재 결과] 이름·구절·좌표는 모두 가상(시연값)이다')
for t in ['work', 'edition', 'section', 'passage', 'variant', 'era', 'name', 'name_era', 'attestation', 'candidate', 'evidence', 'relation']:
    print('  %-12s %3d행' % (t, con.execute('SELECT COUNT(*) FROM %s' % t).fetchone()[0]))
print('  구절 SHA-256 재계산이 어긋난 행:', P.verify_hashes(con))

print('\n[질의 1] 구절을 서명·권·편명·판본과 함께 (질의는 조인 네 개)')
for r in con.execute('''SELECT p.passage_id id, w.title_ko, COALESCE(s.juan,'-') juan, COALESCE(s.pyeon,'-') pyeon, e.label, p.status, p.collation, substr(p.text,1,22) t
                        FROM passage p JOIN section s USING(section_id) JOIN work w ON w.work_id=s.work_id JOIN edition e ON e.edition_id=p.edition_id ORDER BY p.passage_id'''):
    print('  %2d | %s %s %s | %s | %s | 교감 %s | %s…' % tuple(r))

print('\n[질의 2] 교감중인 구절과 그 이문')
for r in con.execute('''SELECT p.passage_id, p.text, v.reading, v.diff_note FROM passage p JOIN variant v USING(passage_id) WHERE p.collation='교감중' '''):
    print('  본문  :', r['text']); print('  이문  :', r['reading']); print('  차이  :', r['diff_note'])

print('\n[질의 3] v_geonames: 다른 책과 주고받는 창구(열: 지명, 시대, 후보, 근거등급 + 좌표)')
print('  %-8s %-8s %-14s %-4s %8s %8s %6s' % ('지명', '시대', '후보', '근거등급', '경도', '위도', '반경km'))
for r in con.execute('SELECT * FROM v_geonames ORDER BY "지명", "시대", "근거등급"'):
    print('  %-8s %-8s %-14s %-4s %8s %8s %6s' % (r['지명'], r['시대'], r['후보'], r['근거등급'],
          '-' if r['경도'] is None else '%.2f' % r['경도'], '-' if r['위도'] is None else '%.2f' % r['위도'], '-' if r['반경km'] is None else '%g' % r['반경km']))

print('\n[인용 시험] cite(): DB 에 있는 구절만 인용되고, 꼬리표가 붙는다')
for k in ('a1', 'b1'):
    print('  ', P.cite(con, ids['pas'][k]))
try:
    P.cite(con, 9999)
except KeyError as e:
    print('   없는 번호 9999 ->', e)

print('\n[인용 점검] quote_audit(): 원고에 따옴표로 넣으려는 구절이 DB 원문에 글자 그대로 있는가')
for q in ['가상성은 시연산 남쪽에 있다', '가상성은  시연산\n남쪽에 있다', '가상성은 시연산 북쪽에 있다', '견본나루는 가상성 동쪽']:
    hit = P.quote_audit(con, q)
    print('  %-26r -> %s' % (q, ('passage_id %s 에 있음' % hit) if hit else 'DB 에 없음: 인용하지 않는다'))
con.commit()
print('\n걸린 시간 %.2f초' % (time.time() - t0))
