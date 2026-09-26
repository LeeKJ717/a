#!/usr/bin/env python3
"""통합과학1·2 문제은행 생성기 (holymind GPU / Ollama).

- 프롬프트는 soul3 prompt_db.prompts 에서 prompt_key로 조회한다 (하드코딩 금지 표준).
    highsci_item_gen    : 문항 일괄 생성
    highsci_item_verify : 독립 풀이 검증
- 결과는 ~/Downloads/highsci_db/highsci.db (SQLite) 에 누적 저장, 중단 후 재실행하면 이어서 생성.
- 중단원(물리/화학/생물/지구과학)마다 --target 개(기본 1000)를 채운다.

사용 예:
    python3 generate.py                     # 전체 생성 (이어하기)
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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CURRICULUM = HERE / "curriculum.json"
SCHEMA = HERE / "sql" / "schema.sql"

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

class SubunitWorker:
    def __init__(self, conn, gemma, su, target, batch, verify):
        self.conn, self.gemma, self.su = conn, gemma, su
        self.target, self.batch, self.verify = target, batch, verify
        self.concepts = {name: concept_id(su["code"], i) for i, name in enumerate(su["concepts"], 1)}

    def q(self, sql, args=()):
        with db_lock:
            return self.conn.execute(sql, args).fetchall()

    def counts(self):
        rows = self.q("SELECT difficulty, COUNT(*) FROM items WHERE subunit_code=? GROUP BY difficulty", (self.su["code"],))
        c = {d: 0 for d in DIFFICULTY_MIX}
        c.update(dict(rows))
        return c

    def pick_difficulty(self, counts):
        # 목표 대비 부족 비율이 가장 큰 난이도
        return max(DIFFICULTY_MIX, key=lambda d: DIFFICULTY_MIX[d] * self.target - counts[d])

    def pick_standard(self):
        rows = dict(self.q("SELECT standard_id, COUNT(*) FROM items WHERE subunit_code=? GROUP BY standard_id",
                           (self.su["code"],)))
        return min(self.su["standards"], key=lambda s: (rows.get(s["id"], 0), random.random()))

    def pick_focus(self):
        rows = dict(self.q("SELECT concept_id, COUNT(*) FROM item_concepts WHERE concept_id LIKE ? GROUP BY concept_id",
                           (self.su["code"] + ":%",)))
        ranked = sorted(self.su["concepts"], key=lambda n: (rows.get(self.concepts[n], 0), random.random()))
        return ranked[:2]

    def recent_stems(self, focus):
        cid = self.concepts[focus[0]]
        rows = self.q("SELECT i.stem FROM items i JOIN item_concepts ic ON ic.item_id=i.id "
                      "WHERE ic.concept_id=? ORDER BY i.created_at DESC LIMIT 12", (cid,))
        return [r[0][:90] for r in rows]

    def run(self):
        code = self.su["code"]
        fails = 0
        while not stop_event.is_set():
            counts = self.counts()
            have = sum(counts.values())
            if have >= self.target:
                log("[%s %s] 완료 %d/%d" % (code, self.su["subject"], have, self.target))
                return
            diff = self.pick_difficulty(counts)
            std = self.pick_standard()
            focus = self.pick_focus()
            deficit = round(DIFFICULTY_MIX[diff] * self.target) - counts[diff]
            n = max(1, min(self.batch, self.target - have, deficit))
            spec = {
                "course": self.su["course"], "unit": self.su["unit"], "subunit": self.su["name"],
                "subject": self.su["subject"], "achievement_standard": std["text"],
                "concept_list": self.su["concepts"], "focus_concepts": focus,
                "count": n, "difficulty": diff, "cognitive_level": COGNITIVE[diff],
                "item_style": random.choice(ITEM_STYLES),
                "avoid_stems": self.recent_stems(focus),
            }
            t0 = time.time()
            try:
                data = self.gemma.call_json(GEN_KEY, json.dumps(spec, ensure_ascii=False, indent=1))
                raw = data.get("items", []) if isinstance(data, dict) else data
                accepted, rejected = self.store(raw, std, diff, focus)
                fails = 0 if accepted else fails + 1
            except Exception as e:  # 네트워크/파싱 오류는 재시도
                accepted, rejected = 0, n
                fails += 1
                log("[%s] 오류: %s" % (code, e))
                time.sleep(min(60, 2 ** min(fails, 6)))
            dt = time.time() - t0
            with db_lock:
                self.conn.execute("INSERT INTO gen_log(subunit_code,requested,accepted,rejected,seconds) VALUES (?,?,?,?,?)",
                                  (code, n, accepted, rejected, dt))
                self.conn.commit()
            log("[%s %s] 난이도%d +%d (거부 %d) %.0fs → %d/%d" % (code, self.su["subject"], diff, accepted, rejected,
                                                          dt, have + accepted, self.target))
            if fails >= 25:
                log("[%s] 연속 실패 25회 — 이 중단원은 건너뜁니다." % code)
                return

    def store(self, raw, std, diff, focus):
        accepted = rejected = 0
        for it in raw if isinstance(raw, list) else []:
            item = self.clean(it, focus)
            if not item:
                rejected += 1
                continue
            h = stem_hash(item["stem"])
            if self.q("SELECT 1 FROM items WHERE stem_hash=?", (h,)):
                rejected += 1
                continue
            if self.verify and not self.verified(item):
                rejected += 1
                continue
            with db_lock:
                try:
                    seq = self.conn.execute("SELECT COUNT(*) FROM items WHERE subunit_code=?",
                                            (self.su["code"],)).fetchone()[0] + 1
                    iid = "HS-%s-%06d" % (self.su["code"], seq)
                    while self.conn.execute("SELECT 1 FROM items WHERE id=?", (iid,)).fetchone():
                        seq += 1
                        iid = "HS-%s-%06d" % (self.su["code"], seq)
                    self.conn.execute(
                        "INSERT INTO items(id,subunit_code,subject,standard_id,stem,choices_json,answer,explanation,"
                        "difficulty,cognitive,irt_a,irt_b,irt_c,verified,stem_hash,model) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (iid, self.su["code"], self.su["subject"], std["id"], item["stem"],
                         json.dumps(item["choices"], ensure_ascii=False), item["answer"], item["explanation"],
                         diff, COGNITIVE[diff], 1.0, IRT_B_PRIOR[diff], 0.2, 1 if self.verify else 0, h,
                         self.gemma.model_for(GEN_KEY)))
                    for name in item["concepts"]:
                        self.conn.execute("INSERT OR IGNORE INTO item_concepts(item_id,concept_id) VALUES (?,?)",
                                          (iid, self.concepts[name]))
                    self.conn.commit()
                    accepted += 1
                except sqlite3.IntegrityError:
                    self.conn.rollback()
                    rejected += 1
        return accepted, rejected

    def clean(self, it, focus):
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
        concepts = [c for c in (it.get("concepts") or []) if c in self.concepts] or focus[:1]
        return {"stem": stem, "choices": choices, "answer": answer,
                "explanation": str(it.get("explanation", "")).strip(), "concepts": list(dict.fromkeys(concepts))}

    def verified(self, item):
        text = item["stem"] + "\n" + "\n".join("%d) %s" % (i, c) for i, c in enumerate(item["choices"], 1))
        try:
            v = self.gemma.call_json(VERIFY_KEY, text, timeout=300)
            return bool(v.get("valid")) and int(v.get("answer", 0)) == item["answer"]
        except Exception as e:
            log("[%s] 검증 오류: %s" % (self.su["code"], e))
            return False


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
    ap = argparse.ArgumentParser(description="통합과학1·2 문제은행 생성기 (Ollama/gemma)")
    ap.add_argument("--out", type=Path, default=default_out_dir(), help="저장 폴더 (기본 ~/Downloads/highsci_db)")
    ap.add_argument("--target", type=int, default=1000, help="중단원당 목표 문항 수")
    ap.add_argument("--batch", type=int, default=5, help="1회 호출당 생성 문항 수")
    ap.add_argument("--workers", type=int, default=2, help="동시 처리 중단원 수 (OLLAMA_NUM_PARALLEL과 맞출 것)")
    ap.add_argument("--subjects", nargs="+", default=DEFAULT_SUBJECTS)
    ap.add_argument("--subunits", nargs="+", help="특정 중단원 코드만 (예: 3-3 4-4)")
    ap.add_argument("--no-verify", action="store_true", help="독립 풀이 검증 생략 (빠르지만 품질 저하)")
    ap.add_argument("--model", help="prompt_db의 model 대신 사용할 Ollama 모델")
    ap.add_argument("--ollama", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    ap.add_argument("--prompt-source", choices=["ssh", "local"], default=os.environ.get("PROMPT_SOURCE", "ssh"))
    ap.add_argument("--soul3", default=os.environ.get("SOUL3_SSH", "192.168.0.20"), help="soul3 ssh 대상")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--export", action="store_true", help="생성 없이 내보내기만")
    args = ap.parse_args(argv)

    cur = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    subunits = [s for s in cur["subunits"] if s["subject"] in args.subjects]
    if args.subunits:
        subunits = [s for s in cur["subunits"] if s["code"] in args.subunits]
    conn = open_db(args.out / "highsci.db")
    seed_curriculum(conn, cur)

    if args.status:
        return status(conn, subunits, args.target)
    if args.export:
        return export(conn, args.out)

    prompts = load_prompts([GEN_KEY, VERIFY_KEY], args.prompt_source, args.soul3)
    gemma = Gemma(prompts, args.ollama, args.model)
    log("저장 위치: %s | 모델: %s | 중단원 %d개 × %d문항 | 검증 %s" % (
        args.out, gemma.model_for(GEN_KEY), len(subunits), args.target, "끔" if args.no_verify else "켬"))

    def on_signal(*_):
        log("중지 요청 — 현재 호출이 끝나면 멈춥니다 (다시 실행하면 이어서 생성).")
        stop_event.set()
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    workers = [SubunitWorker(conn, gemma, su, args.target, args.batch, not args.no_verify) for su in subunits]
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for f in [pool.submit(w.run) for w in workers]:
            f.result()
    export(conn, args.out)
    status(conn, subunits, args.target)


if __name__ == "__main__":
    sys.exit(main())
