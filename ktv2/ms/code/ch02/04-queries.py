# -*- coding: utf-8 -*-
"""실습 2-4b: 시연 DB(out/demo-ktvdb.sqlite)에서 쓸모 있는 질의 넷. 실행: python3 04-queries.py | tee 04-queries.log"""
import sqlite3
c = sqlite3.connect('file:out/demo-ktvdb.sqlite?mode=ro', uri=True)
def q(title, sql, args=()):
    print('--', title); print('   ', ' '.join(sql.split()))
    for r in c.execute(sql, args): print('   ->', r)
q('상태별 줄 수', "SELECT status, COUNT(*) FROM works GROUP BY status ORDER BY status")
q('오픈 액세스라고 하는데 PDF가 아직 없는 것(다시 시도할 목록)', "SELECT doi, oa_status FROM works WHERE status<>'pdf' AND oa_status IN ('gold','green','hybrid','bronze')")
q('인용되었지만 초록도 없는 것(서지부터 채울 목록)', "SELECT w.doi, GROUP_CONCAT(DISTINCT r.chapter_id) FROM works w JOIN refs r ON r.work_id=w.id WHERE w.status='cited' GROUP BY w.id")
q('출처끼리 값이 다른 것', "SELECT w.doi, x.field, x.v_old, x.v_new, x.src_new FROM conflicts x JOIN works w ON w.id=x.work_id")
print('-- DOI로 찾을 때 색인을 쓰는가')
for r in c.execute("EXPLAIN QUERY PLAN SELECT id FROM works WHERE doi='10.9999/demo.001'"): print('   ->', r[3])
print('-- 큰따옴표의 함정: status="abstract"는 abstract 열과 견주어 진다')
print('   ->', c.execute('SELECT COUNT(*) FROM works WHERE status="abstract"').fetchone(), '(올바른 값은 아래)')
print('   ->', c.execute("SELECT COUNT(*) FROM works WHERE status='abstract'").fetchone())
