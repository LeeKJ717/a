# -*- coding: utf-8 -*-
"""실습 14-1: 스키마를 만들고, 제약이 잘못된 입력을 막는지 시험한다. 이 DB 는 파일(out/demo.db)로도 남긴다."""
import os, sys, sqlite3, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P

t0 = time.time()
os.makedirs(os.path.join(P.HERE, 'out'), exist_ok=True)
con = P.connect(os.path.join(P.HERE, 'out', 'schema-only.db'), fresh=True)
print('sqlite 라이브러리 버전', sqlite3.sqlite_version)
print('외래 키 검사 PRAGMA foreign_keys =', con.execute('PRAGMA foreign_keys').fetchone()[0])
print()
print('[표와 뷰]')
for r in con.execute("SELECT type, name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type DESC, name"):
    n = len(con.execute('PRAGMA table_info(%s)' % r['name']).fetchall())
    print('  %-5s %-16s 열 %d개' % (r['type'], r['name'], n))
print('  트리거', [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'")])
print('  인덱스', [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")])

# 제약 시험: 모두 거부되어야 한다
w = P.add_work(con, '시험서', None, '기타', None, 1)
ed = P.add_edition(con, w, '시험본', '미확인', None, None, 1)
sec = P.add_section(con, w, None, None)
tests = []

def attempt(name, fn):
    try:
        fn(); tests.append((name, '들어감(제약이 막지 못함)'))
    except sqlite3.IntegrityError as e:
        tests.append((name, '거부: %s' % e))
    except sqlite3.DatabaseError as e:
        tests.append((name, '거부: %s' % e))

attempt('재인용인데 어느 문헌을 통해 보았는지 없음', lambda: con.execute(
    "INSERT INTO passage (section_id,edition_id,text,text_sha256,status,is_demo) VALUES (?,?,'x','h','재인용',0)", (sec, ed)))
attempt('시연 상태인데 시연 표시(is_demo)가 0', lambda: con.execute(
    "INSERT INTO passage (section_id,edition_id,text,text_sha256,status,is_demo) VALUES (?,?,'x','h','시연',0)", (sec, ed)))
attempt('시연 표시인데 상태가 원문대조(가짜 구절이 진짜처럼)', lambda: con.execute(
    "INSERT INTO passage (section_id,edition_id,text,text_sha256,status,is_demo) VALUES (?,?,'x','h','원문대조',1)", (sec, ed)))
attempt('원문도 서술도 없음', lambda: con.execute(
    "INSERT INTO passage (section_id,edition_id,status,secondary_source,is_demo) VALUES (?,?,'재인용','x',0)", (sec, ed)))
attempt('원문은 있는데 해시가 없음', lambda: con.execute(
    "INSERT INTO passage (section_id,edition_id,text,status,secondary_source,is_demo) VALUES (?,?,'x','재인용','y',0)", (sec, ed)))
attempt('없는 판본을 가리킴(외래 키)', lambda: con.execute(
    "INSERT INTO passage (section_id,edition_id,paraphrase,status,secondary_source,is_demo) VALUES (?,999,'p','재인용','y',0)", (sec,)))
# 정상 입력 한 건 뒤에 원문 수정 시도
pid = P.add_passage(con, sec, ed, '시연', text='[가상] 시험 구절', is_demo=1)
attempt('이미 적재한 원문 고치기(트리거)', lambda: con.execute("UPDATE passage SET text='[가상] 고친 구절' WHERE passage_id=?", (pid,)))
era = P.add_era(con, '시험기', 1, 10, '시험')
attempt('시대 창의 시작이 끝보다 뒤', lambda: con.execute("INSERT INTO era (label,t0,t1,defined_by) VALUES ('거꾸로',10,1,'시험')"))
nm = P.add_name(con, '시험이름', '옛지명', None, 1)
ne = P.add_ne(con, nm, era)
attempt('위도만 있고 경도가 없음', lambda: con.execute("INSERT INTO candidate (ne_id,lat,radius_km,level,coord_origin) VALUES (?,5.0,1,'점','시연값')", (ne,)))
attempt('좌표가 있는데 출처가 "없음"', lambda: con.execute("INSERT INTO candidate (ne_id,lon,lat,radius_km,level,coord_origin) VALUES (?,5.0,5.0,1,'점','없음')", (ne,)))
attempt('좌표가 있는데 반경이 없음', lambda: con.execute("INSERT INTO candidate (ne_id,lon,lat,level,coord_origin) VALUES (?,5.0,5.0,'점','시연값')", (ne,)))
attempt('위도 범위를 벗어남(95도)', lambda: con.execute("INSERT INTO candidate (ne_id,lon,lat,radius_km,level,coord_origin) VALUES (?,5.0,95.0,1,'점','시연값')", (ne,)))
attempt('등급 이름이 목록에 없음("D")', lambda: con.execute("INSERT INTO candidate (ne_id,level,coord_origin,grade_claimed) VALUES (?,'미상','없음','D')", (ne,)))
attempt('같은 (이름, 시대)를 두 번 등록', lambda: con.execute("INSERT INTO name_era (name_id,era_id) VALUES (?,?)", (nm, era)))
print()
print('[제약 시험] %d건' % len(tests))
n_ok = 0
for i, (n, r) in enumerate(tests, 1):
    n_ok += r.startswith('거부')
    print('  %2d. %s -> %s' % (i, n, r))
print('  거부된 것 %d건 / 시험 %d건' % (n_ok, len(tests)))
con.rollback()
con.close()

print('\n[외래 키를 끈 연결에서 같은 6번 입력] PRAGMA foreign_keys 를 켜지 않은 새 연결(SQLite 기본값)')
raw = sqlite3.connect(':memory:')
raw.executescript(open(P.SCHEMA, encoding='utf-8').read().replace('PRAGMA foreign_keys = ON;', ''))
print('  이 연결의 PRAGMA foreign_keys =', raw.execute('PRAGMA foreign_keys').fetchone()[0])
raw.execute("INSERT INTO work (title_ko,kind,is_demo) VALUES ('시험서','기타',1)")
raw.execute("INSERT INTO section (work_id) VALUES (1)")
try:
    raw.execute("INSERT INTO passage (section_id,edition_id,text,text_sha256,status,is_demo) VALUES (1,999,'[가상] x','h','시연',1)")
    print('  없는 판본 999 를 가리키는 구절이 들어감 (제약이 막지 못함)')
    print('  고아 구절 수:', raw.execute('SELECT COUNT(*) FROM passage WHERE edition_id NOT IN (SELECT edition_id FROM edition)').fetchone()[0])
except sqlite3.DatabaseError as e:
    print('  거부:', e)
raw.close()
print('\n걸린 시간 %.2f초' % (time.time() - t0))
