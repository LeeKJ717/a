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
