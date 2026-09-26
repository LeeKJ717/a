"""GPU 없이 분산 파이프라인 검증: 가짜 Ollama 서버 4대 + SQL 파일의 실제 프롬프트 사용.
  - good1, good2 : 정상 서버
  - broken       : 생성 요청마다 500 오류 (다른 서버로 작업이 넘어가는지)
  - nomodel      : 모델 미설치 (시작 시 제외되는지)

    python3 highsci/tests/test_pipeline.py
"""
import json
import re
import sqlite3
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import generate  # noqa: E402


def prompts_from_sql():
    sql = (HERE / "sql" / "register_prompts.sql").read_text(encoding="utf-8")
    rows = re.findall(r"\('(highsci_\w+)', '[^']*', '[^']*', '([^']*)', '[^']*',\n'(.*?)',\n'(\{.*?\})',", sql, re.S)
    assert len(rows) == 2, rows
    return {k: {"prompt_key": k, "model": m, "prompt_text": t, "options": json.loads(o)} for k, m, t, o in rows}


class FakeOllama(BaseHTTPRequestHandler):
    counter = 0
    lock = threading.Lock()
    models = ["gemma4:e4b"]
    broken = False
    examples_seen = 0

    def do_GET(self):
        self.reply({"models": [{"name": m} for m in self.models]}, raw=True)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.broken:
            self.send_response(500)
            self.end_headers()
            return
        prompt = body["prompt"]
        assert "{text}" not in prompt and "{{" not in prompt
        if "SPEC:" in prompt:
            spec = json.loads(prompt.split("SPEC:\n", 1)[1])
            if spec.get("examples"):
                FakeOllama.examples_seen += 1
            items = []
            for _ in range(spec["count"]):
                with FakeOllama.lock:
                    FakeOllama.counter += 1
                    n = FakeOllama.counter
                items.append({"stem": "가상 문항 %d번: %s에 대한 설명으로 옳은 것은?" % (n, spec["focus_concepts"][0]),
                              "choices": ["① 보기A%d" % n, "보기B", "보기C", "보기D", "보기E"],
                              "answer": 1 + n % 5, "explanation": "해설", "concepts": spec["focus_concepts"][:1]})
            if FakeOllama.counter % 7 == 0:  # 불량 문항 섞기
                items.append({"stem": "짧음", "choices": [], "answer": 9})
            out = {"items": items}
        else:
            n = int(re.search(r"가상 문항 (\d+)번", prompt).group(1))
            out = {"answer": 1 + n % 5, "valid": n % 10 != 0, "reason": "ok"}
        self.reply(out)

    def reply(self, out, raw=False):
        data = json.dumps(out if raw else {"response": json.dumps(out, ensure_ascii=False)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def fake_server(**attrs):
    handler = type("H", (FakeOllama,), attrs)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d" % srv.server_port


def main():
    generate.load_prompts = lambda keys, *a: prompts_from_sql()
    nodes = {"nodes": [
        {"name": "good1", "url": fake_server(), "slots": 2},
        {"name": "good2", "url": fake_server(), "slots": 1},
        {"name": "broken", "url": fake_server(broken=True), "slots": 1},
        {"name": "nomodel", "url": fake_server(models=["llama3:8b"]), "slots": 1},
        {"name": "off", "url": "http://127.0.0.1:9", "slots": 1, "enabled": False},
    ]}
    with tempfile.TemporaryDirectory() as d:
        nodes_file = Path(d) / "nodes.json"
        nodes_file.write_text(json.dumps(nodes))
        generate.SEEDS = Path(d) / "seeds"
        generate.SEEDS.mkdir()
        (generate.SEEDS / "4-4.jsonl").write_text(json.dumps(
            {"stem": "예시 문항", "choices": list("ABCDE"), "answer": 2, "explanation": "e", "difficulty": 3},
            ensure_ascii=False) + "\n", encoding="utf-8")
        args = ["--out", d, "--target", "30", "--subunits", "3-3", "4-4", "5-1", "--nodes", str(nodes_file)]
        generate.main(args)
        generate.main(args)  # 재실행 시 이미 채워졌으므로 추가 생성 없어야 함
        conn = sqlite3.connect(Path(d) / "highsci.db")
        per = dict(conn.execute("SELECT subunit_code, COUNT(*) FROM items GROUP BY subunit_code").fetchall())
        assert per == {"3-3": 30, "4-4": 30, "5-1": 30}, per
        assert conn.execute("SELECT COUNT(*) FROM items WHERE choices_json LIKE '%①%'").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM item_concepts").fetchone()[0] >= 90
        for code in ("3-3", "4-4", "5-1"):
            diffs = dict(conn.execute("SELECT difficulty, COUNT(*) FROM items WHERE subunit_code=? GROUP BY difficulty",
                                      (code,)))
            assert diffs == {1: 3, 2: 8, 3: 9, 4: 7, 5: 3}, (code, diffs)
        by_node = dict(conn.execute("SELECT node, COUNT(*) FROM items GROUP BY node"))
        assert set(by_node) == {"good1", "good2"}, by_node
        tried = dict(conn.execute("SELECT node, COUNT(*) FROM gen_log GROUP BY node"))
        assert tried.get("broken", 0) > 0 and "nomodel" not in tried and "off" not in tried, tried
        assert FakeOllama.examples_seen > 0
        assert conn.execute("SELECT COUNT(*) FROM concept_edges WHERE kind='inter'").fetchone()[0] > 0
        files = sorted(p.name for p in (Path(d) / "exports").iterdir())
        assert "concept_graph.json" in files and "manifest.json" in files and len(files) == 5, files
        print("OK", per, "items by node:", by_node, "batches by node:", tried)


if __name__ == "__main__":
    main()
