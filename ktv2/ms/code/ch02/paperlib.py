# -*- coding: utf-8 -*-
"""paperlib v1 (제2권 2장): DOI 정규화, 응답 해석, 메타데이터 DB(SQLite) 적재.
표준 라이브러리만 쓴다. 응답의 필드 이름은 공식 문서에서 확인하지 못한 것이 있어(2.3절),
해석 함수는 .get으로 읽고, 빠진 필드는 probe_fields가 알려 준다."""
import hashlib, html, json, re, sqlite3, time, urllib.parse

# ---------------------------------------------------------------- DOI 정규화
_PREFIX = re.compile(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', re.I)
_DOI_CORE = re.compile(r'10\.\d{4,9}/\S+', re.I)


def doi_norm(s):
    """여러 모양으로 적힌 DOI를 하나의 모양(소문자, 접두어 없음)으로 바꾼다. 못 읽으면 None."""
    if not s:
        return None
    s = urllib.parse.unquote(str(s)).strip()
    s = _PREFIX.sub('', s)
    m = _DOI_CORE.search(s)
    if not m:
        return None
    d = m.group(0)
    while d and d[-1] in '.,;:)]}>"\'':      # 문장 끝 기호가 붙어 온 경우만 벗긴다
        ch = d[-1]
        pair = {')': '(', ']': '[', '}': '{', '>': '<'}.get(ch)
        if pair and d.count(pair) >= d.count(ch):   # 괄호가 짝이 맞으면 DOI의 일부이다
            break
        d = d[:-1]
    return d.lower()


# ---------------------------------------------------------------- 응답 해석
def abstract_from_inverted(inv):
    """단어 -> 위치 목록 꼴로 온 초록을 문장으로 되돌린다."""
    if not inv:
        return None
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return ' '.join(pos[k] for k in sorted(pos))


def parse_openalex(w):
    loc = w.get('best_oa_location') or {}
    prim = w.get('primary_location') or {}
    src = (prim.get('source') or {})
    oa = w.get('open_access') or {}
    return dict(
        doi=doi_norm(w.get('doi')),
        title=w.get('title') or w.get('display_name'),
        authors='; '.join((a.get('author') or {}).get('display_name', '') for a in w.get('authorships', [])) or None,
        year=w.get('publication_year'),
        journal=src.get('display_name'),
        abstract=abstract_from_inverted(w.get('abstract_inverted_index')),
        oa_status=oa.get('oa_status'),
        is_oa=oa.get('is_oa'),
        pdf_url=pick_pdf_url(w),
        cited_by=w.get('cited_by_count'),
        n_refs=len(w.get('referenced_works') or []),
    )


def pick_pdf_url(w):
    """오픈 액세스 PDF 주소를 고르는 순서: best_oa_location -> 그 밖의 위치. 랜딩 페이지는 PDF로 치지 않는다."""
    cands = []
    if w.get('best_oa_location'):
        cands.append(w['best_oa_location'])
    cands += [x for x in (w.get('locations') or []) if x.get('is_oa')]
    for c in cands:
        if c.get('pdf_url'):
            return c['pdf_url']
    return None


_TAG = re.compile(r'<[^>]+>')


def parse_crossref(msg):
    m = msg.get('message', msg)
    dp = ((m.get('issued') or {}).get('date-parts') or [[None]])[0]
    au = '; '.join(((a.get('given', '') + ' ' + a.get('family', '')).strip()) for a in m.get('author', [])) or None
    ab = m.get('abstract')
    return dict(
        doi=doi_norm(m.get('DOI')),
        title=(m.get('title') or [None])[0],
        authors=au,
        year=dp[0] if dp else None,
        journal=(m.get('container-title') or [None])[0],
        abstract=html.unescape(_TAG.sub('', ab)).strip() if ab else None,
        cited_by=m.get('is-referenced-by-count'),
    )


# 필드 점검: 실제 응답이 이 파서가 기대하는 모양인지
OPENALEX_EXPECT = ['doi', 'title', 'publication_year', 'authorships', 'open_access', 'primary_location', 'best_oa_location',
                   'abstract_inverted_index', 'cited_by_count', 'referenced_works']
CROSSREF_EXPECT = ['DOI', 'title', 'author', 'issued', 'container-title', 'is-referenced-by-count']


def probe_fields(obj, expect):
    """기대한 최상위 필드 가운데 응답에 없는 것을 돌려준다. (값이 null인 것은 있는 것으로 센다)"""
    return [k for k in expect if k not in obj]


# ---------------------------------------------------------------- 데이터베이스
RANK = {'cited': 1, 'abstract': 2, 'pdf': 3}

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS works(
  id        INTEGER PRIMARY KEY,
  doi       TEXT UNIQUE,                     -- 정규화한 DOI(소문자, 접두어 없음). DOI가 없는 자료는 NULL
  ext_id    TEXT UNIQUE,                     -- DOI가 없을 때의 다른 식별자(예: openalex:W...)
  title     TEXT, authors TEXT, year INT, journal TEXT, abstract TEXT,
  status    TEXT NOT NULL DEFAULT 'cited' CHECK(status IN ('cited','abstract','pdf')),
  oa_status TEXT, pdf_url TEXT, pdf_path TEXT, sha256 TEXT, fulltext TEXT,
  chapters  TEXT,                            -- 인용한 장(제1권 papers.chapters와 같은 뜻)
  first_seen TEXT, updated TEXT,
  CHECK(doi IS NOT NULL OR ext_id IS NOT NULL));
CREATE TABLE IF NOT EXISTS sources(           -- 응답 원문 보존: 해석을 고쳐도 다시 읽을 수 있다
  id INTEGER PRIMARY KEY, work_id INT REFERENCES works(id), source TEXT NOT NULL,
  url TEXT, http_status INT, fetched TEXT, raw TEXT, raw_sha256 TEXT);
CREATE TABLE IF NOT EXISTS refs(              -- 제1권 refs와 같은 철학: 서지 한 줄 + DOI
  id INTEGER PRIMARY KEY, chapter_id INT, apa TEXT, doi_raw TEXT,
  work_id INT REFERENCES works(id));
CREATE TABLE IF NOT EXISTS conflicts(         -- 출처끼리 값이 다를 때 덮어쓰지 말고 기록
  id INTEGER PRIMARY KEY, work_id INT REFERENCES works(id), field TEXT, v_old TEXT, v_new TEXT, src_new TEXT);
CREATE TABLE IF NOT EXISTS extracted_tables(  -- 2.6절의 표 추출 결과와 점검 결과
  id INTEGER PRIMARY KEY, work_id INT REFERENCES works(id), page INT, method TEXT,
  n_rows INT, n_cols INT, cells TEXT, checks TEXT, verdict TEXT);
CREATE TABLE IF NOT EXISTS fetch_log(
  id INTEGER PRIMARY KEY, t REAL, url TEXT, http_status INT, nbytes INT, note TEXT);
CREATE INDEX IF NOT EXISTS ix_works_status ON works(status);
CREATE INDEX IF NOT EXISTS ix_works_year ON works(year);
"""


def connect(path=':memory:'):
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    return c


def _now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _tn(s):
    return re.sub(r'[^0-9a-z가-힣]', '', (s or '').lower())


def upsert_work(c, rec, status, src, chapters=None):
    """한 건을 넣는다. 규칙: (1) doi가 같으면 한 줄. (2) status는 올라가기만 한다. (3) 빈 칸만 채운다.
    (4) 이미 값이 있고 새 값이 다르면 덮어쓰지 않고 conflicts에 적는다. 돌려주는 값: (work_id, 새로 만들었나)"""
    d, ext = rec.get('doi'), rec.get('ext_id')
    if not d and not ext:
        raise ValueError('doi도 ext_id도 없음')
    key, val = ('doi', d) if d else ('ext_id', ext)
    row = c.execute('SELECT id, status, title, year, journal, abstract, authors, chapters FROM works WHERE %s=?' % key, (val,)).fetchone()
    now = _now()
    if row is None:
        cur = c.execute('INSERT INTO works(doi,ext_id,title,authors,year,journal,abstract,status,oa_status,pdf_url,chapters,first_seen,updated) '
                        'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (d, ext, rec.get('title'), rec.get('authors'), rec.get('year'), rec.get('journal'), rec.get('abstract'),
                         status, rec.get('oa_status'), rec.get('pdf_url'), chapters, now, now))
        return cur.lastrowid, True
    wid, st, title, year, journal, abstract, authors, chs = row
    for f, old in (('title', title), ('year', year), ('journal', journal), ('abstract', abstract), ('authors', authors)):
        new = rec.get(f)
        if new in (None, ''):
            continue
        if old in (None, ''):
            c.execute('UPDATE works SET %s=? WHERE id=?' % f, (new, wid))
        elif (_tn(str(old)) != _tn(str(new))) and f in ('title', 'year'):
            if not c.execute('SELECT 1 FROM conflicts WHERE work_id=? AND field=? AND v_old=? AND v_new=?', (wid, f, str(old), str(new))).fetchone():
                c.execute('INSERT INTO conflicts(work_id,field,v_old,v_new,src_new) VALUES(?,?,?,?,?)', (wid, f, str(old), str(new), src))
    for f in ('oa_status', 'pdf_url'):
        if rec.get(f):
            c.execute('UPDATE works SET %s=COALESCE(%s,?) WHERE id=?' % (f, f), (rec[f], wid))
    if RANK[status] > RANK[st]:
        c.execute('UPDATE works SET status=? WHERE id=?', (status, wid))
    if chapters:
        merged = sorted(set((chs or '').split(',')) | set(chapters.split(',')) - {''})
        c.execute('UPDATE works SET chapters=? WHERE id=?', (','.join(x for x in merged if x), wid))
    c.execute('UPDATE works SET updated=? WHERE id=?', (now, wid))
    return wid, False


def save_raw(c, wid, source, url, http_status, raw):
    c.execute('INSERT INTO sources(work_id,source,url,http_status,fetched,raw,raw_sha256) VALUES(?,?,?,?,?,?,?)',
              (wid, source, url, http_status, _now(), raw, hashlib.sha256(raw.encode('utf-8')).hexdigest()))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()
