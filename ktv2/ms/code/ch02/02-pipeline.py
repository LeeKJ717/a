# -*- coding: utf-8 -*-
"""실습 2-3: 검색 응답 받기 -> 해석 -> DB 적재 -> DOI 정규화로 중복 제거 -> OA PDF 받기 -> 상태 올리기.
서버는 가짜 서버(시연값)이다. 같은 코드를 실제 서버에 쓰려면 Client의 base만 바꾼다(z840 실행 필요).
실행: python3 02-pipeline.py | tee 02-pipeline.log"""
import json, os, subprocess, time
import pdfplumber
import apiclient, fakeserver, paperlib as pl, demodata

os.environ['NO_PROXY'] = '127.0.0.1'
DB = 'out/demo-ktvdb.sqlite'
if os.path.exists(DB):
    os.remove(DB)
open('schema-v1.sql', 'w', encoding='utf-8').write(pl.SCHEMA.strip() + '\n')
c = pl.connect(DB)
srv = fakeserver.Fake(min_gap=0.20).start()
base = 'http://127.0.0.1:%d' % srv.port
log = []
oa = apiclient.Client(base + '/openalex', min_interval=0.30, backoff0=0.25, log=log); oa.s.trust_env = False
cr = apiclient.Client(base + '/crossref', min_interval=0.30, backoff0=0.25, params={'mailto': 'me@example.org'}, log=log); cr.s.trust_env = False
oa.ths = cr.ths = {}  # 호스트별 제한기: 같은 가짜 서버 하나이므로 하나를 같이 쓴다
shared = apiclient.Throttle(0.30)
oa.ths = {'127.0.0.1:%d' % srv.port: shared}; cr.ths = oa.ths

print('== 1. 참고문헌 목록을 읽어 DOI를 정규화하고 적재(status = cited)')
nodoi = 0
for apa, ch in demodata.REFLIST:
    raw = apa
    d = pl.doi_norm(apa)
    if d is None:
        nodoi += 1
        c.execute('INSERT INTO refs(chapter_id, apa, doi_raw, work_id) VALUES(?,?,?,NULL)', (ch, apa, None))
        print('  DOI 없음 -> works에 넣지 않음:', apa[:48])
        continue
    wid, new = pl.upsert_work(c, dict(doi=d), 'cited', 'reflist', chapters=str(ch))
    c.execute('INSERT INTO refs(chapter_id, apa, doi_raw, work_id) VALUES(?,?,?,?)', (ch, apa, d, wid))
    print('  %-22s -> works.id %d %s' % (d, wid, '새 줄' if new else '이미 있음(같은 DOI)'))
c.commit()
n_refs = c.execute('SELECT COUNT(*) FROM refs').fetchone()[0]
n_w = c.execute('SELECT COUNT(*) FROM works').fetchone()[0]
print('  refs %d줄 -> works %d줄 (DOI 없는 %d줄 제외, 중복 %d줄 합침)' % (n_refs, n_w, nodoi, n_refs - nodoi - n_w))

print('\n== 2. 검색으로 찾았다고 가정한 DOI 둘을 더한다(검색 호출 openalex_list는 가짜 서버에 없어 실행하지 않음)')
for d in ('10.9999/DEMO.004', '10.9999/demo.005'):
    wid, new = pl.upsert_work(c, dict(doi=pl.doi_norm(d)), 'cited', 'search')
    print('  ', pl.doi_norm(d), '새 줄' if new else '이미 있음')

print('\n== 3. 각 DOI의 메타데이터 받기(OpenAlex 먼저, 이어서 Crossref)')
for wid, d in c.execute('SELECT id, doi FROM works ORDER BY id').fetchall():
    j = apiclient.openalex_by_doi(oa, d)
    if j:
        miss = pl.probe_fields(j, pl.OPENALEX_EXPECT)
        rec = pl.parse_openalex(j)
        pl.save_raw(c, wid, 'openalex', '/works/doi:' + d, 200, json.dumps(j, ensure_ascii=False))
        st = 'abstract' if rec['abstract'] else 'cited'
        pl.upsert_work(c, rec, st, 'openalex')
    j2 = apiclient.crossref_by_doi(cr, d)
    if j2:
        miss2 = pl.probe_fields(j2['message'], pl.CROSSREF_EXPECT)
        rec2 = pl.parse_crossref(j2)
        pl.save_raw(c, wid, 'crossref', '/works/' + d, 200, json.dumps(j2, ensure_ascii=False))
        pl.upsert_work(c, rec2, 'abstract' if rec2['abstract'] else 'cited', 'crossref')
    print('  %-20s openalex=%s crossref=%s' % (d, 'O' if j else '-', 'O' if j2 else '-'))
c.commit()

print('\n== 4. 오픈 액세스 PDF 받기')
for wid, d, url in c.execute("SELECT id, doi, pdf_url FROM works WHERE pdf_url IS NOT NULL").fetchall():
    dest = 'out/dl/%s.pdf' % d.split('/')[1].replace('.', '')
    path, msg = apiclient.download_pdf(oa, url, dest)
    print('  %-20s %-40s -> %s' % (d, url.split(str(srv.port))[1], msg))
    if path:
        h = pl.sha256_file(path)
        txt = '\n'.join((p.extract_text() or '') for p in pdfplumber.open(path).pages)
        c.execute('UPDATE works SET pdf_path=?, sha256=?, fulltext=?, status=? WHERE id=?', (path, h, txt, 'pdf', wid))
        print('      sha256 %s... 글자 %d' % (h[:12], len(txt)))
c.commit()
for r in log:
    c.execute('INSERT INTO fetch_log(t,url,http_status,nbytes,note) VALUES(?,?,?,?,?)', (r[0], r[1], r[2], r[3], r[4]))
c.commit()
srv.stop()

print('\n== 5. 결과')
print('works 상태별:', c.execute('SELECT status, COUNT(*) FROM works GROUP BY status ORDER BY 2 DESC').fetchall())
for r in c.execute('SELECT id, doi, year, status, oa_status, substr(title,1,40), chapters FROM works ORDER BY id'):
    print('  ', r)
print('conflicts:', c.execute('SELECT w.doi, field, v_old, v_new, src_new FROM conflicts x JOIN works w ON w.id=x.work_id').fetchall())
print('sources 줄 수:', c.execute('SELECT source, COUNT(*) FROM sources GROUP BY 1').fetchall())
print('fetch_log: 요청 %d회, 상태 %s' % (len(log), sorted({(s, sum(1 for r in log if r[2] == s)) for s in {r[2] for r in log}})))

print('\n== 6. 되풀이해도 줄이 늘지 않는가(저장한 원문 raw에서 다시 해석해 적재)')
before = c.execute("SELECT COUNT(*), SUM(status='pdf'), SUM(status='abstract'), SUM(status='cited') FROM works").fetchone()
for wid, src, raw in c.execute('SELECT work_id, source, raw FROM sources').fetchall():
    j = json.loads(raw)
    rec = pl.parse_openalex(j) if src == 'openalex' else pl.parse_crossref(j)
    pl.upsert_work(c, rec, 'abstract' if rec['abstract'] else 'cited', src + '-again')
c.commit()
after = c.execute("SELECT COUNT(*), SUM(status='pdf'), SUM(status='abstract'), SUM(status='cited') FROM works").fetchone()
print('  전: (전체, pdf, abstract, cited) =', before, ' 후:', after, ' 같은가:', before == after)

print('\n== 7. 상태는 내려가지 않는가')
d = c.execute("SELECT doi FROM works WHERE status='pdf' LIMIT 1").fetchone()[0]
pl.upsert_work(c, dict(doi=d), 'cited', 'reflist-again')
print('  pdf인 %s에 cited를 다시 넣은 뒤 상태:' % d, c.execute('SELECT status FROM works WHERE doi=?', (d,)).fetchone()[0])

print('\n== 8. 시연 PDF에서 표 뽑아 DB에 넣기(선 있는 표와 선 없는 표)')
for key in ('demo001', 'demo005'):
    wid = c.execute('SELECT id FROM works WHERE doi=?', ('10.9999/' + key.replace('demo', 'demo.'),)).fetchone()[0]
    page = pdfplumber.open('out/dl/%s.pdf' % key).pages[0]
    for method, ts in (('lines', {}), ('text', {'vertical_strategy': 'text', 'horizontal_strategy': 'text'})):
        tb = page.extract_tables(ts) if ts else page.extract_tables()
        n = len(tb)
        print('  %s %-5s 표 %d개' % (key, method, n), ('첫 표 %d행 x %d열, 첫 행 %s' % (len(tb[0]), len(tb[0][0]), tb[0][0])) if n else '')
        for t in tb:
            c.execute('INSERT INTO extracted_tables(work_id,page,method,n_rows,n_cols,cells,checks,verdict) VALUES(?,?,?,?,?,?,?,?)',
                      (wid, 1, 'pdfplumber-' + method, len(t), max(len(r) for r in t), json.dumps(t, ensure_ascii=False), None, 'unchecked'))
c.commit()
print('extracted_tables:', c.execute('SELECT method, COUNT(*) FROM extracted_tables GROUP BY 1').fetchall())
