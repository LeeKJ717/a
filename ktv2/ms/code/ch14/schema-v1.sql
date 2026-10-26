-- schema-v1.sql  제2권 14장: 사료 원문과 지명 DB (SQLite)
-- 한 파일을 sqlite3 로 읽으면 DB 가 만들어진다. 표 이름과 열 이름은 영어, 설명은 한글 주석.
-- 다른 책(동아시아 고전 지명 추정서)과 주고받는 창구는 맨 아래 뷰 v_geonames (지명, 시대, 후보, 근거등급).
PRAGMA foreign_keys = ON;

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO meta VALUES ('schema_version', 'v1'), ('grade_rule', 'ch14-v1: 독립 출처 수와 증거 종류 수로 계산');

-- ① 사료 원문 쪽 -------------------------------------------------------------
CREATE TABLE work (                      -- 서명
  work_id    INTEGER PRIMARY KEY,
  title_ko   TEXT NOT NULL,              -- 서명(한글 독음)
  title_orig TEXT,                       -- 원표기(한자 등). 원고 본문에는 쓰지 않고 DB 에만 둔다
  kind       TEXT NOT NULL CHECK (kind IN ('사서','실록','지리지','문집','금석문','논문','기타')),
  note       TEXT,
  is_demo    INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0,1)),
  UNIQUE (title_ko, title_orig)
);
CREATE TABLE edition (                   -- 판본
  edition_id INTEGER PRIMARY KEY,
  work_id    INTEGER NOT NULL REFERENCES work(work_id),
  label      TEXT NOT NULL,              -- 판본 이름 (예: 어느 도서관의 어느 본)
  holder     TEXT,                       -- 소장처
  how_seen   TEXT NOT NULL CHECK (how_seen IN ('직접열람','영인본·디지털본','인쇄본OCR','2차문헌인용','미확인')),
  note       TEXT,
  is_demo    INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0,1)),
  UNIQUE (work_id, label)
);
CREATE TABLE section (                   -- 권·편명
  section_id INTEGER PRIMARY KEY,
  work_id    INTEGER NOT NULL REFERENCES work(work_id),
  juan       TEXT,                       -- 권 (모르면 NULL. 빈 문자열로 채우지 않는다)
  pyeon      TEXT,                       -- 편명 (모르면 NULL)
  UNIQUE (work_id, juan, pyeon)
);
CREATE TABLE passage (                   -- 원문 구절 한 건
  passage_id       INTEGER PRIMARY KEY,
  section_id       INTEGER NOT NULL REFERENCES section(section_id),
  edition_id       INTEGER NOT NULL REFERENCES edition(edition_id),
  date_text        TEXT,                 -- 구절의 날짜를 적힌 그대로
  year_from        INTEGER,              -- 환산한 연도 범위(기원전은 음수). 모르면 NULL
  year_to          INTEGER,
  text             TEXT,                 -- 원문 구절. 없으면 NULL (지어내지 않는다)
  text_sha256      TEXT,                 -- text 의 SHA-256 (적재할 때 계산)
  paraphrase       TEXT,                 -- 논문이나 제1권이 옮긴 서술(원문이 아님)
  status           TEXT NOT NULL CHECK (status IN ('원문대조','입력미대조','재인용','시연')),
  secondary_source TEXT,                 -- 재인용이면 어느 문헌을 통해 보았는가
  locator          TEXT,                 -- 이 DB 밖의 위치(예: 제1권 4.6절 표)
  collation        TEXT NOT NULL DEFAULT '교감전' CHECK (collation IN ('교감전','교감중','교감완료','해당없음')),
  collation_note   TEXT,
  is_demo          INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0,1)),
  CHECK (status <> '재인용' OR secondary_source IS NOT NULL),
  CHECK (status <> '시연' OR is_demo = 1),
  CHECK (is_demo = 0 OR status = '시연'),
  CHECK (text IS NOT NULL OR paraphrase IS NOT NULL),
  CHECK (text IS NULL OR text_sha256 IS NOT NULL)
);
CREATE TABLE variant (                   -- 교감: 같은 구절의 다른 판본 읽기(이문)
  variant_id INTEGER PRIMARY KEY,
  passage_id INTEGER NOT NULL REFERENCES passage(passage_id),
  edition_id INTEGER NOT NULL REFERENCES edition(edition_id),
  reading    TEXT NOT NULL,
  diff_note  TEXT,
  UNIQUE (passage_id, edition_id)
);
-- 원문은 고치지 않는다. 다른 읽기는 variant 에 넣는다.
CREATE TRIGGER passage_text_frozen BEFORE UPDATE OF text, text_sha256 ON passage
WHEN OLD.text IS NOT NULL
BEGIN SELECT RAISE(ABORT, '원문은 수정하지 않는다: variant 에 다른 읽기를 넣어라'); END;

-- ② 지명 쪽 ------------------------------------------------------------------
CREATE TABLE era (                       -- 시대(시간 창). 같은 이름의 시대도 글마다 창이 다르므로 정의한 곳을 적는다
  era_id     INTEGER PRIMARY KEY,
  label      TEXT NOT NULL,
  t0         INTEGER NOT NULL,           -- 시작 연도(기원전은 음수)
  t1         INTEGER NOT NULL,
  defined_by TEXT NOT NULL,              -- 이 창을 정한 문헌이나 이 책
  CHECK (t0 <= t1),
  UNIQUE (label, defined_by)
);
CREATE TABLE name (                      -- 이름(글자 모양). 땅이 아니다
  name_id   INTEGER PRIMARY KEY,
  name_ko   TEXT NOT NULL,
  orig_form TEXT,
  layer     TEXT NOT NULL CHECK (layer IN ('옛지명','현대지명','유적','시료지점','문화·시대','기관·지점')),
  is_demo   INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0,1)),
  UNIQUE (name_ko, orig_form, layer)
);
CREATE TABLE name_era (                  -- (이름, 시대) 한 쌍. 위상 추정의 기본 단위
  ne_id   INTEGER PRIMARY KEY,
  name_id INTEGER NOT NULL REFERENCES name(name_id),
  era_id  INTEGER NOT NULL REFERENCES era(era_id),
  UNIQUE (name_id, era_id)
);
CREATE TABLE attestation (               -- 이 구절에 이 (이름, 시대)가 나온다
  att_id     INTEGER PRIMARY KEY,
  ne_id      INTEGER NOT NULL REFERENCES name_era(ne_id),
  passage_id INTEGER NOT NULL REFERENCES passage(passage_id),
  note       TEXT,
  UNIQUE (ne_id, passage_id)
);
CREATE TABLE candidate (                 -- 후보 위치. 한 (이름, 시대)에 여러 개를 둘 수 있다
  cand_id       INTEGER PRIMARY KEY,
  ne_id         INTEGER NOT NULL REFERENCES name_era(ne_id),
  modern_name   TEXT,                    -- 현대의 어느 곳이라 하는가(서술)
  lon           REAL,                    -- 좌표가 없으면 둘 다 NULL (찍지 않는다)
  lat           REAL,
  radius_km     REAL,                    -- 후보의 불확실 반경
  level         TEXT NOT NULL CHECK (level IN ('점','현','지역','미상')),
  coord_origin  TEXT NOT NULL CHECK (coord_origin IN ('논문본문','지도','측정','계산','시연값','없음')),
  coord_ref     TEXT,
  coord_note    TEXT,
  valid_from    INTEGER,                 -- 이 후보가 가리키는 시기(없으면 시대 창 전체)
  valid_to      INTEGER,
  grade_claimed TEXT CHECK (grade_claimed IN ('A','B','C','가설')),   -- 사람이 매긴(또는 남이 매긴) 등급
  status        TEXT NOT NULL DEFAULT '후보' CHECK (status IN ('후보','채택','기각')),
  is_demo       INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0,1)),
  CHECK ((lon IS NULL) = (lat IS NULL)),
  CHECK (lon IS NULL OR (lon BETWEEN -180 AND 180 AND lat BETWEEN -90 AND 90)),
  CHECK ((coord_origin = '없음') = (lon IS NULL)),
  CHECK (lon IS NULL OR radius_km IS NOT NULL)
);
CREATE TABLE evidence (                  -- 후보를 받치는(또는 반대하는) 증거
  ev_id       INTEGER PRIMARY KEY,
  cand_id     INTEGER NOT NULL REFERENCES candidate(cand_id),
  ev_type     TEXT NOT NULL CHECK (ev_type IN ('원문방향거리','현대지명대응','좌표','지형고고','퇴적증거','이름일치')),
  indep_group TEXT NOT NULL,             -- 같은 출처에서 나온 증거는 같은 값. 독립 출처 수는 이 값의 종류 수
  support     TEXT NOT NULL CHECK (support IN ('지지','반대','중립')),
  passage_id  INTEGER REFERENCES passage(passage_id),
  source_ref  TEXT NOT NULL,
  note        TEXT
);
CREATE TABLE relation (                  -- 글이 말하는 관계: 방향·거리, 같은 곳이라는 주장
  rel_id        INTEGER PRIMARY KEY,
  passage_id    INTEGER REFERENCES passage(passage_id),   -- 사료 구절에서 나온 관계면 구절 번호, 논문의 서술이면 NULL
  source_ref    TEXT NOT NULL,                            -- 관계를 말한 곳(구절이면 서명·권, 논문이면 논문 이름)
  variant_id    INTEGER REFERENCES variant(variant_id),   -- NULL 이면 본 읽기, 아니면 그 이문을 따른 읽기
  ne_a          INTEGER NOT NULL REFERENCES name_era(ne_id),
  ne_b          INTEGER NOT NULL REFERENCES name_era(ne_id),
  kind          TEXT NOT NULL CHECK (kind IN ('방향거리','동일시주장')),
  bearing_deg   REAL,                    -- a 에서 b 를 본 방위(북 0, 시계 방향)
  bearing_tol   REAL,                    -- 허용 오차(8방위 서술이면 22.5)
  dist_km       REAL,
  dist_tol_km   REAL,
  note          TEXT,
  CHECK (kind <> '방향거리' OR (bearing_deg IS NOT NULL AND bearing_tol IS NOT NULL) OR dist_km IS NOT NULL)
);
-- ③ 검사 결과 기록 -----------------------------------------------------------
CREATE TABLE check_run (run_id INTEGER PRIMARY KEY, tool TEXT NOT NULL, ran_at TEXT NOT NULL, note TEXT);
CREATE TABLE check_result (
  res_id  INTEGER PRIMARY KEY,
  run_id  INTEGER NOT NULL REFERENCES check_run(run_id),
  rule    TEXT NOT NULL,
  subject TEXT NOT NULL,
  verdict TEXT NOT NULL,
  detail  TEXT
);
CREATE INDEX ix_cand_ne ON candidate(ne_id);
CREATE INDEX ix_ev_cand ON evidence(cand_id);
CREATE INDEX ix_att_ne  ON attestation(ne_id);
CREATE INDEX ix_ne_name ON name_era(name_id);

-- ④ 뷰 ----------------------------------------------------------------------
-- 후보마다 계산한 등급. 규칙(이 책의 규칙이며 다른 책의 규칙과 같은지는 확인 필요):
--   지지 증거의 종류 수(이름일치 제외) t, 독립 출처 수 g 로
--   A: t>=3 이고 g>=3 이고 '좌표'나 '원문방향거리'를 포함 / B: t>=2 이고 g>=2 / C: t>=1 / 가설: 그 밖
--   독립 출처가 반대하는 증거가 하나라도 있으면 한 단계 낮춘다.
CREATE VIEW v_cand_grade AS
WITH s AS (
  SELECT c.cand_id,
    (SELECT COUNT(DISTINCT e.ev_type)    FROM evidence e WHERE e.cand_id=c.cand_id AND e.support='지지' AND e.ev_type<>'이름일치') AS t,
    (SELECT COUNT(DISTINCT e.indep_group) FROM evidence e WHERE e.cand_id=c.cand_id AND e.support='지지' AND e.ev_type<>'이름일치') AS g,
    (SELECT COUNT(*) FROM evidence e WHERE e.cand_id=c.cand_id AND e.support='지지' AND e.ev_type IN ('좌표','원문방향거리')) AS has_core,
    (SELECT COUNT(DISTINCT e.indep_group) FROM evidence e WHERE e.cand_id=c.cand_id AND e.support='반대') AS opp
  FROM candidate c
), r AS (
  SELECT cand_id, t, g, opp,
    CASE WHEN t>=3 AND g>=3 AND has_core>0 THEN 3 WHEN t>=2 AND g>=2 THEN 2 WHEN t>=1 THEN 1 ELSE 0 END AS base
  FROM s
)
SELECT cand_id, t AS ev_types, g AS indep_groups, opp AS opposing_groups,
  CASE MAX(base - (opp>0), 0) WHEN 3 THEN 'A' WHEN 2 THEN 'B' WHEN 1 THEN 'C' ELSE '가설' END AS grade_computed,
  MAX(base - (opp>0), 0) AS rank_computed
FROM r;

-- 신고한 등급이 계산한 등급보다 높은 후보(등급 부풀림)
CREATE VIEW v_grade_inflated AS
SELECT c.cand_id, c.grade_claimed, g.grade_computed
FROM candidate c JOIN v_cand_grade g USING (cand_id)
WHERE c.grade_claimed IS NOT NULL
  AND (CASE c.grade_claimed WHEN 'A' THEN 3 WHEN 'B' THEN 2 WHEN 'C' THEN 1 ELSE 0 END) > g.rank_computed;

-- 다른 책과 주고받는 창구: 열 이름이 지명, 시대, 후보, 근거등급
CREATE VIEW v_geonames AS
SELECT n.name_ko                                   AS "지명",
       e.label                                     AS "시대",
       COALESCE(c.modern_name, '(후보 없음)')       AS "후보",
       COALESCE(g.grade_computed, '가설')           AS "근거등급",
       c.lon AS "경도", c.lat AS "위도", c.radius_km AS "반경km",
       c.status AS "상태", c.grade_claimed AS "신고등급", c.coord_origin AS "좌표출처",
       n.is_demo AS "시연"
FROM name_era ne
JOIN name n ON n.name_id = ne.name_id
JOIN era  e ON e.era_id = ne.era_id
LEFT JOIN candidate c ON c.ne_id = ne.ne_id
LEFT JOIN v_cand_grade g ON g.cand_id = c.cand_id;

-- 지도에 찍어도 되는 후보: 좌표가 있고 기각이 아니고, 등급이 가설이 아닌 것
CREATE VIEW v_mappable AS
SELECT c.cand_id, n.name_ko, e.label AS era, c.modern_name, c.lon, c.lat, c.radius_km, g.grade_computed
FROM candidate c
JOIN name_era ne ON ne.ne_id=c.ne_id JOIN name n ON n.name_id=ne.name_id JOIN era e ON e.era_id=ne.era_id
JOIN v_cand_grade g ON g.cand_id=c.cand_id
WHERE c.lon IS NOT NULL AND c.status<>'기각' AND g.grade_computed<>'가설';
