-- 해외 참고 자료 (highsci.db 안에 함께 저장). 원본 파일은 highsci_db/references/ 아래 디스크에, 메타데이터와 본문 텍스트는 DB에.

CREATE TABLE IF NOT EXISTS ref_sources (
  id        TEXT PRIMARY KEY,           -- sources.json의 id
  country   TEXT NOT NULL,
  org       TEXT NOT NULL,
  exam      TEXT NOT NULL,
  level     TEXT,
  subjects  TEXT,                       -- JSON 배열
  license   TEXT,
  config_json TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS ref_docs (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id  TEXT NOT NULL REFERENCES ref_sources(id),
  url        TEXT NOT NULL UNIQUE,
  found_on   TEXT,                      -- 링크를 발견한 페이지
  link_text  TEXT,
  parent_id  INTEGER REFERENCES ref_docs(id), -- ZIP 안에서 풀린 파일이면 ZIP 문서 id
  path       TEXT,                      -- highsci_db 기준 상대 경로
  sha256     TEXT,
  bytes      INTEGER,
  mime       TEXT,
  year       INTEGER,                   -- URL/링크 글자에서 추정
  status     TEXT NOT NULL DEFAULT 'found', -- found / ok / dup / error / skipped
  error      TEXT,
  pages      INTEGER,
  text_status TEXT,                     -- ok / empty / no_extractor / error
  fetched_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_ref_docs_source ON ref_docs(source_id, status);
CREATE INDEX IF NOT EXISTS idx_ref_docs_sha ON ref_docs(sha256);

-- 페이지별 본문 텍스트
CREATE TABLE IF NOT EXISTS ref_pages (
  doc_id INTEGER NOT NULL REFERENCES ref_docs(id) ON DELETE CASCADE,
  page   INTEGER NOT NULL,
  text   TEXT NOT NULL,
  PRIMARY KEY (doc_id, page)
);

-- 전문 검색 (trigram: 한·일·불 부분 문자열 검색 가능)
CREATE VIRTUAL TABLE IF NOT EXISTS ref_fts USING fts5(
  text, doc_id UNINDEXED, page UNINDEXED, tokenize = 'trigram'
);

-- 참고 문서(또는 특정 쪽) ↔ 우리 중단원 매핑 (수동·자동 태깅용)
CREATE TABLE IF NOT EXISTS ref_doc_subunits (
  doc_id       INTEGER NOT NULL REFERENCES ref_docs(id) ON DELETE CASCADE,
  page_from    INTEGER,
  page_to      INTEGER,
  subunit_code TEXT NOT NULL,
  note         TEXT,
  PRIMARY KEY (doc_id, subunit_code, page_from)
);
