# -*- coding: utf-8 -*-
"""실습 14-5: 시연 레코드에 위상 추정 검사를 돌린다. 같은 이름이 시대마다 같은 땅을 가리키는가를 가려낸다.
검사 여섯 가지: ① 시대 쌍별 겹침/분리/판정 불가와 묶음, ② 사슬 경고, ③ 방향·거리 서술 점검과 교감 의존, ④ 같은 좌표 다른 이름,
⑤ 후보 시기와 시대 창의 어긋남, ⑥ 좌표 없는 (이름, 시대). 결과는 DB 의 check_result 에도 적는다."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P, demorec

t0 = time.time()
con = P.connect(os.path.join(P.HERE, 'out', 'demo.db'), fresh=True)
ids = demorec.load(con)
run = P.log_run(con, 'p05-topo-demo-v1.py', '시연 레코드(가상)')
summary = {}

print('[① 이름별 시대 쌍 판정과 묶음]  판정 기준: 확인 후보(좌표 있고 가설 아님) 사이의 거리 <= 반경 합 이면 겹침')
for (nid, nm) in con.execute("SELECT name_id, name_ko FROM name ORDER BY name_id").fetchall():
    c = P.referent_clusters(con, nid)
    if len(c['eras']) < 2:
        continue
    print('  <%s> 시대 %d개' % (nm, len(c['eras'])))
    for i, j, v, why, d, gap in c['pairs']:
        print('     %s - %s : %-10s %s' % (c['eras'][i][1], c['eras'][j][1], v, why))
        P.log_res(con, run, 'pair', '%s %s~%s' % (nm, c['eras'][i][1], c['eras'][j][1]), v, why)
    print('     묶음:', ' | '.join('{' + ', '.join(x) + '}' for x in c['clusters']))
    if any(p[2] == '판정 불가' for p in c['pairs']):
        print('     주의: 판정 불가 쌍이 있어 위 묶음의 따로따로는 "다른 곳"이 아니라 "묶지 못함"이다')
    for w in c['chain_warnings']:
        print('     사슬 경고:', w)
        P.log_res(con, run, 'chain', nm, '사슬 경고', w)
    if c['no_point']:
        print('     좌표 있는 후보가 없는 시대:', ', '.join(c['no_point']))
    summary[nm] = dict(clusters=c['clusters'], pairs=[(c['eras'][i][1], c['eras'][j][1], v, (None if d is None else round(d, 1))) for i, j, v, _, d, _ in c['pairs']],
                       chain=c['chain_warnings'])

print('\n[③ 글의 방향·거리 서술 점검] 구절: 견본나루는 가상성 동쪽 삼십 리(가상). 환산 1리 = 0.4 km (시연값)')
pb, a, b = ids['pas']['b1'], ids['ne'][('가상성', 2)], ids['ne'][('견본나루', 2)]
for key in ('main', 'alt'):
    rid = ids['rel_b'][key]
    v, out = P.check_relation(con, rid)
    row = con.execute('SELECT dist_km, dist_tol_km, bearing_deg, bearing_tol, note FROM relation WHERE rel_id=?', (rid,)).fetchone()
    print('  읽기 %-4s (%s): 서술 %g±%g km, 방위 %g±%g도 -> %s' % (key, row['note'], row['dist_km'], row['dist_tol_km'], row['bearing_deg'], row['bearing_tol'], v))
    for o in out:
        print('       후보 %d -> %d : 거리 %.2f km, 방위 %.1f도(%s), 거리 부합 %s, 방위 부합 %s' % (o['a'], o['b'], o['dist'], o['az'], P.dir8(o['az']), o['ok_dist'], o['ok_bearing']))
    P.log_res(con, run, 'relation', 'rel %d %s' % (rid, key), v, row['note'])
v, res = P.relation_by_reading(con, pb, a, b)
print('  읽기별 판정을 모으면:', v, res)
P.log_res(con, run, 'relation-collation', '견본나루', v, str(res))

print('\n[④ 같은 좌표, 다른 이름]')
for x in P.same_coordinate_diff_name(con):
    print('  %s(%s) 와 %s(%s): 거리 %.3f km' % x)
    P.log_res(con, run, 'same-coord', '%s/%s' % (x[0], x[2]), '이름과 좌표 불일치 의심', '%.3f km' % x[4])
print('\n[⑤ 후보의 시기가 시대 창과 겹치지 않음]')
for x in P.window_conflicts(con):
    print('  후보 %d: %s %s(%d~%d) 인데 후보 시기 %d~%d' % x)
    P.log_res(con, run, 'window', '후보 %d' % x[0], '시기 어긋남', str(x))
print('\n[⑥ 지도에 찍지 않는 (이름, 시대): 좌표 있는 후보가 없다]')
npt = P.no_point_ne(con)
for nm, era, ne in npt:
    print('  %s %s' % (nm, era))
    P.log_res(con, run, 'no-point', '%s %s' % (nm, era), '좌표 없음')
print('  합계 %d / 전체 (이름, 시대) %d' % (len(npt), con.execute('SELECT COUNT(*) FROM name_era').fetchone()[0]))
con.commit()
print('\ncheck_result 에 %d행 기록' % con.execute('SELECT COUNT(*) FROM check_result WHERE run_id=?', (run,)).fetchone()[0])
json.dump(summary, open(os.path.join(P.HERE, 'p05-topo-demo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('걸린 시간 %.2f초' % (time.time() - t0))
