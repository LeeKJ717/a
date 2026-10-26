# -*- coding: utf-8 -*-
"""실습 14-7: 다른 책과 주고받는 CSV(지명, 시대, 후보, 근거등급)로 내보내고 가져온다. 세 가지를 시험한다.
(가) 내보냈다가 다시 가져오면 같은 판정이 나오는가. (나) 네 열만 있는 CSV 를 가져오면 무엇이 사라지는가. (다) 시대 창이 없으면 어떻게 되는가."""
import os, sys, time, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P, demorec, exchange as X

t0 = time.time()
OUT = os.path.join(P.HERE, 'out')
src = P.connect(os.path.join(OUT, 'demo.db'), fresh=True)
demorec.load(src)
g, e, a = X.export(src, OUT, 'demo')
print('[내보내기] 파일 3개')
for p in (g, e, a):
    n = sum(1 for _ in open(p, encoding='utf-8')) - 1
    print('  %-20s 데이터 %d행, 머리글 %s' % (os.path.basename(p), n, open(p, encoding='utf-8').readline().strip()))

def snapshot(con):
    d = {}
    for r in con.execute('SELECT "지명","시대","후보","근거등급","신고등급" FROM v_geonames'):
        d[(r[0], r[1], r[2])] = (r[3], r[4])
    return d

def verdicts(con, nm):
    nid = con.execute('SELECT name_id FROM name WHERE name_ko=?', (nm,)).fetchone()[0]
    c = P.referent_clusters(con, nid)
    return [(p[2]) for p in c['pairs']], c['clusters']

print('\n[가] 세 파일을 모두 가져온 DB 가 원래 DB 와 같은가')
dst = P.connect(os.path.join(OUT, 'roundtrip.db'), fresh=True)
st = X.import_csv(dst, g, a, e, is_demo=1)
print('  가져온 행 %d, 후보 %d' % (st['rows'], st['cands']))
s1, s2 = snapshot(src), snapshot(dst)
print('  (지명, 시대, 후보) 키 수: 원래 %d, 가져온 %d, 같은 키 %d' % (len(s1), len(s2), len(set(s1) & set(s2))))
same = sum(1 for k in s1 if k in s2 and s1[k][0] == s2[k][0])
print('  계산 등급이 같은 행 %d / %d' % (same, len(s1)))
for nm in ('가상성', '가상포', '예시고을'):
    print('  %-6s 판정 원래 %s | 가져온 %s' % (nm, verdicts(src, nm)[0], verdicts(dst, nm)[0]))
print('  증거 행: 원래 %d, 가져온 %d' % (src.execute('SELECT COUNT(*) FROM evidence').fetchone()[0], dst.execute('SELECT COUNT(*) FROM evidence').fetchone()[0]))
print('  못 옮긴 것: 사료 구절(passage), 관계(relation), 후보 시기(valid_from/to), 후보 상태, 좌표 메모. 이 CSV 는 지명 쪽만 나른다')

print('\n[나] 네 열(지명, 시대, 후보, 근거등급)과 시대 창 파일만 가져오면 (증거 파일 없음)')
four = os.path.join(OUT, 'demo-four.csv')
with open(four, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['지명', '시대', '후보', '근거등급'])
    for r in csv.DictReader(open(g, encoding='utf-8')):
        w.writerow([r['지명'], r['시대'], r['후보'], r['근거등급']])
d4 = P.connect(os.path.join(OUT, 'four.db'), fresh=True)
st = X.import_csv(d4, four, a, None, is_demo=1)
print('  가져온 행 %d, 후보 %d  (좌표 열이 없으므로 모든 후보가 좌표 없음)' % (st['rows'], st['cands']))
from collections import Counter
print('  신고등급 분포:', dict(Counter(r[0] for r in d4.execute('SELECT grade_claimed FROM candidate'))))
print('  계산등급 분포:', dict(Counter(r[0] for r in d4.execute('SELECT grade_computed FROM v_cand_grade'))))
print('  등급 부풀림으로 걸리는 후보: %d / 후보 %d' % (d4.execute('SELECT COUNT(*) FROM v_grade_inflated').fetchone()[0], d4.execute('SELECT COUNT(*) FROM candidate').fetchone()[0]))
v, cl = verdicts(d4, '가상성')
print('  가상성 시대 쌍 판정:', v)
print('  v_mappable 행: %d (좌표가 없어 지도에 찍을 후보가 없다)' % d4.execute('SELECT COUNT(*) FROM v_mappable').fetchone()[0])

print('\n[다] 시대 창 파일 없이 가져오기')
d5 = P.connect(os.path.join(OUT, 'noera.db'), fresh=True)
try:
    X.import_csv(d5, four, None, None)
except X.ImportError_ as ex:
    print('  거부:', ex)
print('\n[라] 필요한 열이 없는 파일')
bad = os.path.join(OUT, 'demo-bad.csv')
with open(bad, 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerows([['지명', '시대', '후보'], ['가상성', '가상 1기', '가상 갑 지점']])
try:
    X.import_csv(P.connect(), bad, a)
except X.ImportError_ as ex:
    print('  거부:', ex)
print('\n걸린 시간 %.2f초' % (time.time() - t0))
