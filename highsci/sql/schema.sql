-- highsci_db (SQLite) 스키마
-- 문항반응이론(IRT 3PL)과 개념 그래프(선수 관계)를 웹 풀이 단계에서 바로 쓰도록 설계.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS subunits (
  code        TEXT PRIMARY KEY,          -- 예: 3-3
  course      TEXT NOT NULL,             -- 통합과학1 / 통합과학2
  unit        TEXT NOT NULL,             -- 대단원
  name        TEXT NOT NULL,             -- 중단원
  subject     TEXT NOT NULL              -- 물리 / 화학 / 생물 / 지구과학 / 융합
);

CREATE TABLE IF NOT EXISTS standards (
  id            TEXT PRIMARY KEY,
  subunit_code  TEXT NOT NULL REFERENCES subunits(code),
  official_code TEXT,
  text          TEXT NOT NULL
);

-- 그래프 노드: 개념
CREATE TABLE IF NOT EXISTS concepts (
  id            TEXT PRIMARY KEY,        -- 예: 3-3:05
  subunit_code  TEXT NOT NULL REFERENCES subunits(code),
  name          TEXT NOT NULL,
  seq           INTEGER NOT NULL,
  UNIQUE (subunit_code, name)
);

-- 그래프 간선: 선수 개념 → 후속 개념 (kind: intra=중단원 내 순서, inter=중단원 간 선수)
CREATE TABLE IF NOT EXISTS concept_edges (
  src   TEXT NOT NULL REFERENCES concepts(id),
  dst   TEXT NOT NULL REFERENCES concepts(id),
  kind  TEXT NOT NULL,
  weight REAL NOT NULL DEFAULT 1.0,
  PRIMARY KEY (src, dst)
);

CREATE TABLE IF NOT EXISTS subunit_edges (
  src TEXT NOT NULL REFERENCES subunits(code),
  dst TEXT NOT NULL REFERENCES subunits(code),
  PRIMARY KEY (src, dst)
);

CREATE TABLE IF NOT EXISTS items (
  id            TEXT PRIMARY KEY,        -- HS-<subunit>-<6자리>
  subunit_code  TEXT NOT NULL REFERENCES subunits(code),
  subject       TEXT NOT NULL,
  standard_id   TEXT NOT NULL REFERENCES standards(id),
  item_type     TEXT NOT NULL DEFAULT 'MC5',
  stem          TEXT NOT NULL,
  choices_json  TEXT NOT NULL,           -- JSON 배열 5개
  answer        INTEGER NOT NULL,        -- 1~5
  explanation   TEXT,
  difficulty    INTEGER NOT NULL,        -- 생성 시 목표 난이도 1~5
  cognitive     TEXT,                    -- 기억/이해/적용/분석/평가
  -- IRT 3PL 파라미터: 생성 시 사전값(prior), 응답 누적 후 보정
  irt_a         REAL NOT NULL DEFAULT 1.0,
  irt_b         REAL NOT NULL,
  irt_c         REAL NOT NULL DEFAULT 0.2,
  irt_calibrated INTEGER NOT NULL DEFAULT 0,
  irt_n         INTEGER NOT NULL DEFAULT 0, -- 보정에 쓰인 응답 수
  verified      INTEGER NOT NULL DEFAULT 0, -- 1=독립 풀이 검증 통과
  status        TEXT NOT NULL DEFAULT 'draft', -- draft / reviewed / active / retired
  stem_hash     TEXT NOT NULL UNIQUE,    -- 중복 방지
  model         TEXT,
  node          TEXT,                    -- 생성한 GPU 서버 (z840/z440/soul3 …)
  created_at    TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_items_subunit ON items(subunit_code, difficulty);
CREATE INDEX IF NOT EXISTS idx_items_subject ON items(subject);

CREATE TABLE IF NOT EXISTS item_concepts (
  item_id    TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  concept_id TEXT NOT NULL REFERENCES concepts(id),
  PRIMARY KEY (item_id, concept_id)
);
CREATE INDEX IF NOT EXISTS idx_item_concepts_c ON item_concepts(concept_id);

-- 웹 단계용: 학생 응답 로그 (IRT 보정 / 능력치 추정 입력)
CREATE TABLE IF NOT EXISTS responses (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    TEXT NOT NULL,
  item_id    TEXT NOT NULL REFERENCES items(id),
  chosen     INTEGER,
  correct    INTEGER NOT NULL,
  elapsed_ms INTEGER,
  theta_before REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_responses_user ON responses(user_id);
CREATE INDEX IF NOT EXISTS idx_responses_item ON responses(item_id);

-- 웹 단계용: 학생별 개념 숙달도 (그래프 기반 추천)
CREATE TABLE IF NOT EXISTS user_concept_mastery (
  user_id    TEXT NOT NULL,
  concept_id TEXT NOT NULL REFERENCES concepts(id),
  theta      REAL NOT NULL DEFAULT 0.0,
  se         REAL NOT NULL DEFAULT 1.0,
  n          INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  PRIMARY KEY (user_id, concept_id)
);

-- 생성 작업 로그 (재시작/모니터링)
CREATE TABLE IF NOT EXISTS gen_log (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  subunit_code TEXT,
  requested  INTEGER,
  accepted   INTEGER,
  rejected   INTEGER,
  seconds    REAL,
  node       TEXT,
  reasons_json TEXT,                     -- 거부 사유별 수 {"mismatch":2,"invalid":1,...}
  note       TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 거부된 문항 (사유 분석·검증기 오판 점검용)
CREATE TABLE IF NOT EXISTS rejected_items (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  subunit_code    TEXT,
  node            TEXT,
  difficulty      INTEGER,
  reason          TEXT NOT NULL,         -- format / dup / mismatch / invalid / verify_error / db
  stem            TEXT,
  choices_json    TEXT,
  answer          TEXT,                  -- 문항에 표시된 정답
  verifier_answer INTEGER,               -- 검증 풀이 답
  verifier_valid  INTEGER,               -- 1=문제없음 0=오류 판정
  verifier_reason TEXT,
  raw             TEXT,                  -- 깨진 검증 응답 원문 등
  created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_rejected_reason ON rejected_items(reason, subunit_code);
