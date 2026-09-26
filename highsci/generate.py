#!/usr/bin/env python3
"""통합과학1·2 문제은행 생성기 — 분산 코디네이터 (Ollama/gemma).

- holymind에서 코디네이터 1개가 실행되고, nodes.json에 적힌 GPU 서버(z840·z440·soul3 …)의
  Ollama API로 생성·검증 요청을 나눠 보낸다. 빠른 서버가 더 많은 배치를 가져간다(작업 풀 방식).
  DB는 코디네이터 한 곳(holymind ~/Downloads/highsci_db)에만 쓰므로 병합이 필요 없다.

- 프롬프트는 soul3 prompt_db.prompts 에서 prompt_key로 조회한다 (하드코딩 금지 표준).
    highsci_item_gen    : 문항 일괄 생성
    highsci_item_verify : 독립 풀이 검증
- 결과는 ~/Downloads/highsci_db/highsci.db (SQLite) 에 누적 저장, 중단 후 재실행하면 이어서 생성.
- 중단원(물리/화학/생물/지구과학)마다 --target 개(기본 1000)를 채운다.

사용 예:
    python3 generate.py                     # nodes.json의 서버들로 전체 생성 (이어하기)
    python3 generate.py --check-nodes       # 서버 상태·모델 확인만
    python3 generate.py --only-nodes z840 soul3
    python3 generate.py --ollama http://localhost:11434 --workers 2   # 단일 서버 모드
    python3 generate.py --subunits 3-3 4-4  # 특정 중단원만
    python3 generate.py --status            # 진행 현황
    python3 generate.py --export            # JSONL/그래프 내보내기만
"""
import argparse
import hashlib
import json
import os
import random
import re
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CURRICULUM = HERE / "curriculum.json"
SCHEMA = HERE / "sql" / "schema.sql"
NODES = HERE / "nodes.json"
SEEDS = HERE / "seeds"

GEN_KEY = "highsci_item_gen"
VERIFY_KEY = "highsci_item_verify"
DEFAULT_SUBJECTS = ["물리", "화학", "생물", "지구과학"]

# 목표 난이도 비율 (1=매우 쉬움 … 5=매우 어려움)
DIFFICULTY_MIX = {1: 0.10, 2: 0.25, 3: 0.30, 4: 0.25, 5: 0.10}
COGNITIVE = {1: "기억", 2: "이해", 3: "적용", 4: "분석", 5: "분석·평가"}
# IRT 3PL 사전값: 난이도 → b, 5지선다 추측도 c=0.2
IRT_B_PRIOR = {1: -2.0, 2: -1.0, 3: 0.0, 4: 1.0, 5: 2.0}
ITEM_STYLES = [
    "개념 확인형",
    "자료(표) 해석형",
    "계산형(물리·화학 단원에 적합한 경우)",
    "<보기> ㄱ·ㄴ·ㄷ 합답형",
    "실생활·첨단 기술 적용형",
    "탐구 실험 설계·결과 해석형",
]
CIRCLED = re.compile(r"^\s*(?:[①②③④⑤]|\(?[1-5][\).]|[1-5]번)\s*")

stop_event = threading.Event()
db_lock = threading.Lock()


def log(msg):
    print(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg, flush=True)


def default_out_dir():
    try:
        d = subprocess.run(["xdg-user-dir", "DOWNLOAD"], capture_output=True, text=True, timeout=5).stdout.strip()
        if d and d != str(Path.home()) and Path(d).is_dir():
            return Path(d) / "highsci_db"
    except (OSError, subprocess.SubprocessError):
        pass
    for name in ("Downloads", "다운로드"):
        if (Path.home() / name).is_dir():
            return Path.home() / name / "highsci_db"
    return Path.home() / "Downloads" / "highsci_db"


# ---------------------------------------------------------------- prompt_db

def load_prompts(keys, source, ssh_host):
    """soul3 prompt_db에서 프롬프트를 읽는다.

    source=ssh   : holymind → ssh soul3 → mysql socket (기본)
    source=local : soul3에서 직접 실행할 때
    """
    in_list = ",".join("'%s'" % k for k in keys)
    sql = ("SELECT JSON_OBJECT('prompt_key', prompt_key, 'model', model, 'prompt_text', prompt_text, "
           "'options_json', options_json) FROM prompts WHERE is_active=1 AND prompt_key IN (%s)" % in_list)
    user = os.environ.get("PROMPT_DB_USER", "prompt_user")
    pw = os.environ.get("PROMPT_DB_PASS", "prompt2026!")
    sock = os.environ.get("PROMPT_DB_SOCK", "/home/mysql/mysql.sock")
    mysql = ["mysql", "-u", user, "-p" + pw, "--socket=" + sock, "prompt_db", "-N", "-B", "--raw", "-e", sql]
    if source == "ssh":
        import shlex
        cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", ssh_host, " ".join(shlex.quote(a) for a in mysql)]
    else:
        cmd = mysql
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("prompt_db 조회 실패: " + r.stderr.strip())
    prompts = {}
    for line in r.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            opts = row.get("options_json") or {}
            row["options"] = json.loads(opts) if isinstance(opts, str) else opts
            prompts[row["prompt_key"]] = row
    missing = [k for k in keys if k not in prompts]
    if missing:
        raise RuntimeError("prompt_db에 없는 prompt_key: %s (sql/register_prompts.sql 을 soul3에서 실행하세요)" % missing)
    return prompts


# ---------------------------------------------------------------- Ollama

class Gemma:
    def __init__(self, prompts, ollama_url, model_override=None):
        self.prompts = prompts
        self.url = ollama_url.rstrip("/") + "/api/generate"
        self.model_override = model_override

    def model_for(self, key):
        return self.model_override or self.prompts[key]["model"]

    def call_json(self, key, text, timeout=600):
        p = self.prompts[key]
        opts = dict(p["options"])
        body = {
            "model": self.model_for(key),
            "prompt": p["prompt_text"].format(text=text),
            "think": opts.pop("think", False),
            "stream": False,
        }
        opts.pop("stream", None)
        fmt = opts.pop("format", None)
        if fmt:
            body["format"] = fmt
        body["options"] = opts
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode()).get("response", "")
        return parse_json(out)


def parse_json(s):
    s = s.strip()
    s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.M).strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", s, re.S)
        if m:
            return json.loads(m.group(0))
        raise


# ---------------------------------------------------------------- DB

def open_db(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False, timeout=60)
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    for table in ("items", "gen_log"):  # 단일 서버 버전에서 만든 DB 이전
        cols = [r[1] for r in conn.execute("PRAGMA table_info(%s)" % table)]
        if "node" not in cols:
            conn.execute("ALTER TABLE %s ADD COLUMN node TEXT" % table)
    return conn


def seed_curriculum(conn, cur):
    with db_lock:
        for su in cur["subunits"]:
            conn.execute("INSERT OR REPLACE INTO subunits(code,course,unit,name,subject) VALUES (?,?,?,?,?)",
                         (su["code"], su["course"], su["unit"], su["name"], su["subject"]))
            for st in su["standards"]:
                conn.execute("INSERT OR REPLACE INTO standards(id,subunit_code,official_code,text) VALUES (?,?,?,?)",
                             (st["id"], su["code"], st.get("official_code", ""), st["text"]))
            prev = None
            for i, name in enumerate(su["concepts"], 1):
                cid = concept_id(su["code"], i)
                conn.execute("INSERT OR IGNORE INTO concepts(id,subunit_code,name,seq) VALUES (?,?,?,?)",
                             (cid, su["code"], name, i))
                if prev:
                    conn.execute("INSERT OR IGNORE INTO concept_edges(src,dst,kind) VALUES (?,?,'intra')", (prev, cid))
                prev = cid
        by_code = {s["code"]: s for s in cur["subunits"]}
        for src, dst in cur["subunit_prereqs"]:
            conn.execute("INSERT OR IGNORE INTO subunit_edges(src,dst) VALUES (?,?)", (src, dst))
            # 선수 중단원의 마지막 개념 → 후속 중단원의 첫 개념 (웹 단계에서 세분화 가능)
            conn.execute("INSERT OR IGNORE INTO concept_edges(src,dst,kind,weight) VALUES (?,?,'inter',0.5)",
                         (concept_id(src, len(by_code[src]["concepts"])), concept_id(dst, 1)))
        conn.commit()


def concept_id(code, seq):
    return "%s:%02d" % (code, seq)


def stem_hash(stem):
    norm = re.sub(r"[\s\W_]+", "", stem).lower()
    return hashlib.sha1(norm.encode()).hexdigest()


# ---------------------------------------------------------------- generation

class Node:
    """Ollama가 돌고 있는 GPU 서버 1대. slots = 동시에 보낼 요청 수 (서버의 OLLAMA_NUM_PARALLEL 이하)."""

    def __init__(self, cfg, prompts, model_override=None):
        self.name = cfg["name"]
        self.url = cfg["url"].rstrip("/")
        self.slots = int(cfg.get("slots", 1))
        self.timeout = int(cfg.get("timeout", 600))  # 요청당 제한 시간(초). CPU 전용 서버는 크게
        self.gemma = Gemma(prompts, self.url, model_override or cfg.get("model"))
        self.fails = 0
        self.down_until = 0.0
        self.dead = False
        self.lock = threading.Lock()

    def health(self):
        """(ok, 메시지). 서버 응답과 필요한 모델 설치 여부를 확인한다."""
        try:
            with urllib.request.urlopen(self.url + "/api/tags", timeout=8) as r:
                names = {m["name"] for m in json.loads(r.read().decode()).get("models", [])}
        except Exception as e:
            return False, "접속 실패 (%s)" % e
        need = {self.gemma.model_for(k) for k in (GEN_KEY, VERIFY_KEY)}
        missing = [m for m in need if m not in names and m + ":latest" not in names]
        if missing:
            return False, "모델 없음 %s → 해당 서버에서 ollama pull %s" % (missing, " ".join(missing))
        return True, "OK (%s, 슬롯 %d)" % (", ".join(sorted(need)), self.slots)

    def ok(self):
        with self.lock:
            self.fails = 0

    def failed(self, err):
        with self.lock:
            self.fails += 1
            if self.fails % 5 == 0:
                self.down_until = time.time() + min(1800, 60 * self.fails)
                log("[%s] 연속 실패 %d회 — %d초 쉬었다 재시도 (%s)" % (
                    self.name, self.fails, self.down_until - time.time(), err))
            if self.fails >= 50:
                self.dead = True
                log("[%s] 연속 실패 50회 — 이 서버는 이번 실행에서 제외합니다." % self.name)


class Task:
    def __init__(self, su, diff, n, std, focus, spec):
        self.su, self.diff, self.n, self.std, self.focus, self.spec = su, diff, n, std, focus, spec


class Scheduler:
    """모든 서버의 워커가 공유하는 작업 풀. 진행 중(inflight) 예약분까지 계산해 목표·난이도 비율을 넘기지 않는다."""

    def __init__(self, conn, subunits, target, batch, verify):
        self.conn, self.target, self.batch, self.verify = conn, target, batch, verify
        self.subunits = subunits
        self.concepts = {su["code"]: {n: concept_id(su["code"], i) for i, n in enumerate(su["concepts"], 1)}
                         for su in subunits}
        self.quota = quotas(target)
        self.inflight = {su["code"]: {d: 0 for d in DIFFICULTY_MIX} for su in subunits}
        self.active = {su["code"]: 0 for su in subunits}
        self.zero_streak = {su["code"]: 0 for su in subunits}
        self.skipped = set()
        self.seeds = load_seeds()
        self.lock = threading.Lock()

    def q(self, sql, args=()):
        with db_lock:
            return self.conn.execute(sql, args).fetchall()

    def counts(self, code):
        c = {d: 0 for d in DIFFICULTY_MIX}
        c.update(dict(self.q("SELECT difficulty, COUNT(*) FROM items WHERE subunit_code=? GROUP BY difficulty", (code,))))
        return c

    def busy(self):
        with self.lock:
            return any(self.active.values())

    def unassigned(self):
        """아직 어느 서버에도 배정되지 않은 문항 수."""
        with self.lock:
            return sum(max(0, self.target - sum(self.counts(c).values()) - sum(self.inflight[c].values()))
                       for c in self.inflight if c not in self.skipped)

    def next_task(self):
        with self.lock:
            cands = []
            for su in self.subunits:
                code = su["code"]
                if code in self.skipped:
                    continue
                counts = self.counts(code)
                inf = self.inflight[code]
                rem = self.target - sum(counts.values()) - sum(inf.values())
                if rem > 0:
                    cands.append((self.active[code], -rem, random.random(), su, counts))
            if not cands:
                return None
            # 동시에 같은 중단원을 여러 서버가 붙잡지 않도록 작업 중인 워커가 적은 중단원 우선
            _, neg_rem, _, su, counts = min(cands, key=lambda x: x[:3])
            code, inf = su["code"], self.inflight[su["code"]]
            deficit = {d: self.quota[d] - counts[d] - inf[d] for d in DIFFICULTY_MIX}
            diff = max(deficit, key=lambda d: (deficit[d], random.random()))
            n = max(1, min(self.batch, -neg_rem, deficit[diff]))
            std = self.pick_standard(su)
            focus = self.pick_focus(su)
            spec = {
                "course": su["course"], "unit": su["unit"], "subunit": su["name"],
                "subject": su["subject"], "achievement_standard": std["text"],
                "concept_list": su["concepts"], "focus_concepts": focus,
                "count": n, "difficulty": diff, "cognitive_level": COGNITIVE[diff],
                "item_style": random.choice(ITEM_STYLES),
                "avoid_stems": self.recent_stems(code, focus),
            }
            examples = self.pick_examples(code, diff)
            if examples:
                spec["examples"] = examples
            inf[diff] += n
            self.active[code] += 1
            return Task(su, diff, n, std, focus, spec)

    def done(self, task, accepted):
        with self.lock:
            code = task.su["code"]
            self.inflight[code][task.diff] -= task.n
            self.active[code] -= 1
            self.zero_streak[code] = 0 if accepted else self.zero_streak[code] + 1
            if self.zero_streak[code] >= 40 and code not in self.skipped:
                self.skipped.add(code)
                log("[%s] 40배치 연속 채택 0 — 이 중단원은 건너뜁니다 (프롬프트/모델 점검 필요)." % code)

    def pick_standard(self, su):
        rows = dict(self.q("SELECT standard_id, COUNT(*) FROM items WHERE subunit_code=? GROUP BY standard_id", (su["code"],)))
        return min(su["standards"], key=lambda s: (rows.get(s["id"], 0), random.random()))

    def pick_focus(self, su):
        rows = dict(self.q("SELECT concept_id, COUNT(*) FROM item_concepts WHERE concept_id LIKE ? GROUP BY concept_id",
                           (su["code"] + ":%",)))
        ids = self.concepts[su["code"]]
        return sorted(su["concepts"], key=lambda n: (rows.get(ids[n], 0), random.random()))[:2]

    def recent_stems(self, code, focus):
        rows = self.q("SELECT i.stem FROM items i JOIN item_concepts ic ON ic.item_id=i.id "
                      "WHERE ic.concept_id=? ORDER BY i.created_at DESC LIMIT 12", (self.concepts[code][focus[0]],))
        return [r[0][:90] for r in rows]

    def pick_examples(self, code, diff):
        pool = self.seeds.get(code, [])
        same = [s for s in pool if s.get("difficulty") == diff] or pool
        return [{k: s[k] for k in ("stem", "choices", "answer", "explanation") if k in s}
                for s in random.sample(same, min(2, len(same)))]

    # ------------------------------------------------------------ 저장

    def store(self, task, raw, node):
        accepted = rejected = 0
        for it in raw if isinstance(raw, list) else []:
            item = self.clean(task, it)
            if not item:
                rejected += 1
                continue
            h = stem_hash(item["stem"])
            if self.q("SELECT 1 FROM items WHERE stem_hash=?", (h,)):
                rejected += 1
                continue
            if self.verify and not self.verified(item, node, task.su["code"]):
                rejected += 1
                continue
            if self.insert(task, item, h, node):
                accepted += 1
            else:
                rejected += 1
        return accepted, rejected

    def insert(self, task, item, h, node):
        code = task.su["code"]
        with db_lock:
            try:
                seq = self.conn.execute("SELECT COUNT(*) FROM items WHERE subunit_code=?", (code,)).fetchone()[0] + 1
                iid = "HS-%s-%06d" % (code, seq)
                while self.conn.execute("SELECT 1 FROM items WHERE id=?", (iid,)).fetchone():
                    seq += 1
                    iid = "HS-%s-%06d" % (code, seq)
                self.conn.execute(
                    "INSERT INTO items(id,subunit_code,subject,standard_id,stem,choices_json,answer,explanation,"
                    "difficulty,cognitive,irt_a,irt_b,irt_c,verified,stem_hash,model,node) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (iid, code, task.su["subject"], task.std["id"], item["stem"],
                     json.dumps(item["choices"], ensure_ascii=False), item["answer"], item["explanation"],
                     task.diff, COGNITIVE[task.diff], 1.0, IRT_B_PRIOR[task.diff], 0.2, 1 if self.verify else 0, h,
                     node.gemma.model_for(GEN_KEY), node.name))
                for name in item["concepts"]:
                    self.conn.execute("INSERT OR IGNORE INTO item_concepts(item_id,concept_id) VALUES (?,?)",
                                      (iid, self.concepts[code][name]))
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                self.conn.rollback()
                return False

    def clean(self, task, it):
        if not isinstance(it, dict):
            return None
        stem = str(it.get("stem", "")).strip()
        choices = it.get("choices")
        if len(stem) < 10 or not isinstance(choices, list) or len(choices) != 5:
            return None
        choices = [CIRCLED.sub("", str(c)).strip() for c in choices]
        if any(not c for c in choices) or len(set(choices)) != 5:
            return None
        try:
            answer = int(it.get("answer"))
        except (TypeError, ValueError):
            return None
        if not 1 <= answer <= 5:
            return None
        ids = self.concepts[task.su["code"]]
        concepts = [c for c in (it.get("concepts") or []) if c in ids] or task.focus[:1]
        return {"stem": stem, "choices": choices, "answer": answer,
                "explanation": str(it.get("explanation", "")).strip(), "concepts": list(dict.fromkeys(concepts))}

    def verified(self, item, node, code):
        text = item["stem"] + "\n" + "\n".join("%d) %s" % (i, c) for i, c in enumerate(item["choices"], 1))
        try:
            v = node.gemma.call_json(VERIFY_KEY, text, timeout=node.timeout)
            return bool(v.get("valid")) and int(v.get("answer", 0)) == item["answer"]
        except Exception as e:
            log("[%s@%s] 검증 오류: %s" % (code, node.name, e))
            return False


def node_worker(node, sched):
    while not stop_event.is_set() and not node.dead:
        wait = node.down_until - time.time()
        if wait > 0:
            if not sched.unassigned():  # 쉬는 동안 다른 서버가 남은 일을 다 가져갔으면 종료
                return
            stop_event.wait(min(wait, 10))
            continue
        task = sched.next_task()
        if task is None:
            if not sched.busy():
                return
            stop_event.wait(5)  # 다른 서버의 진행 중 배치가 실패하면 다시 받아간다
            continue
        code, t0, accepted, rejected = task.su["code"], time.time(), 0, task.n
        try:
            data = node.gemma.call_json(GEN_KEY, json.dumps(task.spec, ensure_ascii=False, indent=1), timeout=node.timeout)
            raw = data.get("items", []) if isinstance(data, dict) else data
            accepted, rejected = sched.store(task, raw, node)
            node.ok()
        except Exception as e:
            log("[%s@%s] 오류: %s" % (code, node.name, e))
            node.failed(e)
        finally:
            sched.done(task, accepted)
        dt = time.time() - t0
        with db_lock:
            sched.conn.execute("INSERT INTO gen_log(subunit_code,requested,accepted,rejected,seconds,node) "
                               "VALUES (?,?,?,?,?,?)", (code, task.n, accepted, rejected, dt, node.name))
            sched.conn.commit()
        have = sum(sched.counts(code).values())
        log("[%s %s@%s] 난이도%d +%d (거부 %d) %.0fs → %d/%d" % (
            code, task.su["subject"], node.name, task.diff, accepted, rejected, dt, have, sched.target))


def quotas(target):
    """난이도별 목표 문항 수 (최대 잉여 방식으로 합계가 정확히 target)."""
    raw = {d: DIFFICULTY_MIX[d] * target for d in DIFFICULTY_MIX}
    q = {d: int(v) for d, v in raw.items()}
    for d in sorted(raw, key=lambda d: (-(raw[d] - q[d]), d))[:target - sum(q.values())]:
        q[d] += 1
    return q


def load_seeds():
    """seeds/<중단원코드>.jsonl — 예시 문항(few-shot). 있으면 SPEC.examples로 2개씩 제공."""
    seeds = {}
    if SEEDS.is_dir():
        for p in SEEDS.glob("*.jsonl"):
            seeds[p.stem] = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return seeds


def load_nodes(args, prompts):
    if args.ollama:
        cfgs = [{"name": "local", "url": args.ollama, "slots": args.workers}]
    else:
        cfgs = [n for n in json.loads(args.nodes.read_text(encoding="utf-8"))["nodes"] if n.get("enabled", True)]
        if args.only_nodes:
            cfgs = [n for n in json.loads(args.nodes.read_text(encoding="utf-8"))["nodes"] if n["name"] in args.only_nodes]
    nodes, unready = [], []
    for cfg in cfgs:
        node = Node(cfg, prompts, args.model)
        ok, msg = node.health()
        log("서버 %-9s %-28s %s" % (node.name, node.url, msg))
        (nodes if ok else unready).append(node)
    if args.unready_file:  # run_holymind.sh가 이 목록의 서버를 자동 준비(deploy_nodes.sh)한다
        Path(args.unready_file).write_text("".join(n.name + "\n" for n in unready), encoding="utf-8")
    return nodes


def node_report(conn):
    rows = conn.execute("SELECT node, COUNT(*), SUM(accepted), SUM(rejected), ROUND(AVG(seconds),1) "
                        "FROM gen_log WHERE node IS NOT NULL GROUP BY node ORDER BY node").fetchall()
    if rows:
        print("\n%-10s %8s %8s %8s %8s" % ("서버", "배치", "채택", "거부", "초/배치"))
        for r in rows:
            print("%-10s %8d %8d %8d %8s" % r)


# ---------------------------------------------------------------- status / export

def status(conn, subunits, target):
    print("%-5s %-6s %-26s %6s  %s" % ("code", "과목", "중단원", "문항", "난이도1~5"))
    total = 0
    for su in subunits:
        rows = dict(conn.execute("SELECT difficulty, COUNT(*) FROM items WHERE subunit_code=? GROUP BY difficulty",
                                 (su["code"],)).fetchall())
        n = sum(rows.values())
        total += n
        print("%-5s %-6s %-26s %4d/%d  %s" % (su["code"], su["subject"], su["name"][:26], n, target,
                                             " ".join(str(rows.get(d, 0)) for d in range(1, 6))))
    print("합계 %d / %d" % (total, target * len(subunits)))


def export(conn, out_dir):
    ex = out_dir / "exports"
    ex.mkdir(parents=True, exist_ok=True)
    conn.row_factory = sqlite3.Row
    manifest = []
    for su in conn.execute("SELECT * FROM subunits ORDER BY code").fetchall():
        rows = conn.execute("SELECT * FROM items WHERE subunit_code=? ORDER BY id", (su["code"],)).fetchall()
        if not rows:
            continue
        fname = "%s_%s_%s.jsonl" % (su["course"], su["code"], su["subject"])
        with open(ex / fname, "w", encoding="utf-8") as f:
            for r in rows:
                cs = [c[0] for c in conn.execute("SELECT concept_id FROM item_concepts WHERE item_id=?", (r["id"],))]
                f.write(json.dumps({
                    "id": r["id"], "course": su["course"], "unit": su["unit"], "subunit_code": su["code"],
                    "subunit": su["name"], "subject": su["subject"], "standard_id": r["standard_id"],
                    "stem": r["stem"], "choices": json.loads(r["choices_json"]), "answer": r["answer"],
                    "explanation": r["explanation"], "difficulty": r["difficulty"], "cognitive": r["cognitive"],
                    "concepts": cs, "irt": {"a": r["irt_a"], "b": r["irt_b"], "c": r["irt_c"],
                                            "calibrated": bool(r["irt_calibrated"])},
                    "verified": bool(r["verified"]),
                }, ensure_ascii=False) + "\n")
        manifest.append({"file": fname, "subunit_code": su["code"], "subject": su["subject"], "count": len(rows)})
    graph = {
        "nodes": [dict(r) for r in conn.execute(
            "SELECT c.id, c.name, c.subunit_code, s.subject, s.course, c.seq, "
            "(SELECT COUNT(*) FROM item_concepts ic WHERE ic.concept_id=c.id) AS item_count "
            "FROM concepts c JOIN subunits s ON s.code=c.subunit_code ORDER BY c.id")],
        "edges": [dict(r) for r in conn.execute("SELECT src, dst, kind, weight FROM concept_edges")],
        "subunit_edges": [dict(r) for r in conn.execute("SELECT src, dst FROM subunit_edges")],
    }
    (ex / "concept_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
    (ex / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    conn.row_factory = None
    log("내보내기 완료: %s (%d개 파일, 문항 %d)" % (ex, len(manifest), sum(m["count"] for m in manifest)))


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="통합과학1·2 문제은행 분산 생성기 (Ollama/gemma)")
    ap.add_argument("--out", type=Path, default=default_out_dir(), help="저장 폴더 (기본 ~/Downloads/highsci_db)")
    ap.add_argument("--target", type=int, default=1000, help="중단원당 목표 문항 수")
    ap.add_argument("--batch", type=int, default=5, help="1회 호출당 생성 문항 수")
    ap.add_argument("--nodes", type=Path, default=NODES, help="GPU 서버 목록 (기본 nodes.json)")
    ap.add_argument("--only-nodes", nargs="+", help="nodes.json 중 이 서버들만 사용 (enabled 무시)")
    ap.add_argument("--ollama", help="단일 서버 모드: 이 Ollama URL 하나만 사용")
    ap.add_argument("--workers", type=int, default=2, help="단일 서버 모드의 동시 요청 수")
    ap.add_argument("--subjects", nargs="+", default=DEFAULT_SUBJECTS)
    ap.add_argument("--subunits", nargs="+", help="특정 중단원 코드만 (예: 3-3 4-4)")
    ap.add_argument("--no-verify", action="store_true", help="독립 풀이 검증 생략 (빠르지만 품질 저하)")
    ap.add_argument("--model", help="prompt_db·nodes.json의 모델 대신 모든 서버에 쓸 Ollama 모델")
    ap.add_argument("--prompt-source", choices=["ssh", "local"], default=os.environ.get("PROMPT_SOURCE", "ssh"))
    ap.add_argument("--soul3", default=os.environ.get("SOUL3_SSH", "192.168.0.20"), help="soul3 ssh 대상")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--export", action="store_true", help="생성 없이 내보내기만")
    ap.add_argument("--check-nodes", action="store_true", help="서버 접속·모델 확인만")
    ap.add_argument("--unready-file", help="준비 안 된 서버 이름을 이 파일에 기록 (자동 준비용)")
    args = ap.parse_args(argv)

    cur = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    subunits = [s for s in cur["subunits"] if s["subject"] in args.subjects]
    if args.subunits:
        subunits = [s for s in cur["subunits"] if s["code"] in args.subunits]
    conn = open_db(args.out / "highsci.db")
    seed_curriculum(conn, cur)

    if args.status:
        status(conn, subunits, args.target)
        return node_report(conn)
    if args.export:
        return export(conn, args.out)

    prompts = load_prompts([GEN_KEY, VERIFY_KEY], args.prompt_source, args.soul3)
    nodes = load_nodes(args, prompts)
    if args.check_nodes:
        return 0 if nodes else 1
    if not nodes:
        log("사용 가능한 서버가 없습니다. nodes.json과 각 서버의 Ollama(setup_node.sh)를 확인하세요.")
        return 1
    sched = Scheduler(conn, subunits, args.target, args.batch, not args.no_verify)
    log("저장 위치: %s | 서버 %s | 중단원 %d개 × %d문항 | 검증 %s | 예시문항 %d개 중단원" % (
        args.out, ", ".join("%s×%d" % (n.name, n.slots) for n in nodes), len(subunits), args.target,
        "끔" if args.no_verify else "켬", len(sched.seeds)))

    def on_signal(*_):
        log("중지 요청 — 진행 중인 호출이 끝나면 멈춥니다 (다시 실행하면 이어서 생성).")
        stop_event.set()
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    threads = [threading.Thread(target=node_worker, args=(n, sched), name="%s-%d" % (n.name, i), daemon=True)
               for n in nodes for i in range(n.slots)]
    for t in threads:
        t.start()
    while any(t.is_alive() for t in threads):
        for t in threads:
            t.join(timeout=1)
    export(conn, args.out)
    status(conn, subunits, args.target)
    node_report(conn)


if __name__ == "__main__":
    sys.exit(main())
