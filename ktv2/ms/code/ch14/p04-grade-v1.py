# -*- coding: utf-8 -*-
"""실습 14-4: 근거 등급(A/B/C/가설)을 증거에서 계산하고, 신고한 등급과 견준다. 증거를 바꾸면 등급이 어떻게 움직이는지 시험한다."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P, demorec

t0 = time.time()
con = P.connect(os.path.join(P.HERE, 'out', 'demo.db'), fresh=True)
ids = demorec.load(con)
cand = ids['cand']
inv = {v: k for k, v in cand.items()}

print('[후보별 증거와 계산 등급] 증거 종류 수, 독립 출처 수, 반대 출처 수, 계산 등급, 신고 등급')
print('  %-10s %-8s %3s %3s %3s  %-4s %-4s' % ('이름', '시대', '종류', '출처', '반대', '계산', '신고'))
rows = con.execute('''SELECT c.cand_id, n.name_ko, e.label, g.ev_types, g.indep_groups, g.opposing_groups, g.grade_computed, c.grade_claimed
                      FROM candidate c JOIN name_era ne USING(ne_id) JOIN name n USING(name_id) JOIN era e USING(era_id) JOIN v_cand_grade g USING(cand_id)
                      ORDER BY n.name_ko, e.t0, c.cand_id''').fetchall()
for r in rows:
    print('  %-10s %-8s %3d %3d %3d  %-4s %-4s %s' % (r['name_ko'], r['label'], r['ev_types'], r['indep_groups'], r['opposing_groups'], r['grade_computed'], r['grade_claimed'],
          '<- 신고가 계산보다 높음' if r['cand_id'] in [x['cand_id'] for x in con.execute('SELECT cand_id FROM v_grade_inflated')] else ''))

print('\n[v_grade_inflated] 등급 부풀림 후보')
for r in con.execute('''SELECT n.name_ko, e.label, i.grade_claimed, i.grade_computed FROM v_grade_inflated i JOIN candidate c USING(cand_id)
                        JOIN name_era ne USING(ne_id) JOIN name n USING(name_id) JOIN era e USING(era_id) ORDER BY 1,2'''):
    print('  %s %s: 신고 %s, 계산 %s' % (r['name_ko'], r['label'], r['grade_claimed'], r['grade_computed']))

def g(c):
    return con.execute('SELECT grade_computed, ev_types, indep_groups FROM v_cand_grade WHERE cand_id=?', (c,)).fetchone()

print('\n[증거를 바꾸어 보기] 모두 시험이며 마지막에 되돌린다')
c = cand['gs1']
print('  가상성 1기 처음:', tuple(g(c)))
P.add_ev(con, c, '퇴적증거', '가상논문11', '반대', '반대 증거(가상)')
print('  독립 출처가 반대하는 증거 하나를 더하면:', tuple(g(c)))
con.rollback()
c = cand['gs3']
print('  가상성 3기 처음:', tuple(g(c)))
P.add_ev(con, c, '좌표', '가상논문3', '지지', '같은 논문의 좌표(가상)')
print('  같은 논문(독립 출처 그대로)에서 종류 하나를 더하면:', tuple(g(c)))
P.add_ev(con, c, '지형고고', '가상조사12', '지지', '다른 출처(가상)')
print('  다른 출처에서 종류 하나를 더 더하면:', tuple(g(c)))
con.rollback()
c = cand['nm']
print('  이름뿐성 1기 처음(이름일치 증거뿐):', tuple(g(c)))
for i in range(5):
    P.add_ev(con, c, '이름일치', '이름%d' % i, '지지', '이름이 같은 다른 곳 %d' % i)
print('  이름 일치 증거를 다섯 개 더해도:', tuple(g(c)))
con.rollback()

print('\n[지도 후보] v_mappable: 좌표가 있고 가설이 아닌 후보만 (가설은 지도에 속이 빈 표지로만)')
for r in con.execute('SELECT name_ko, era, grade_computed, lon, lat FROM v_mappable ORDER BY name_ko, era'):
    pass
print('  v_mappable %d행, 좌표 있는 후보 전체 %d행, 그 가운데 가설 %d행' % (
    con.execute('SELECT COUNT(*) FROM v_mappable').fetchone()[0],
    con.execute("SELECT COUNT(*) FROM candidate WHERE lon IS NOT NULL").fetchone()[0],
    con.execute("SELECT COUNT(*) FROM candidate c JOIN v_cand_grade g USING(cand_id) WHERE c.lon IS NOT NULL AND g.grade_computed='가설'").fetchone()[0]))
print('\n걸린 시간 %.2f초' % (time.time() - t0))
