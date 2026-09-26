"""GPU 없이 파이프라인 검증: 가짜 Ollama 서버 + SQL 파일의 실제 프롬프트 사용.

    python3 highsci/tests/test_pipeline.py
"""
import json
import re
import sqlite3
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
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

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = body["prompt"]
        assert "{text}" not in prompt and "{{" not in prompt
        if "SPEC:" in prompt:
            spec = json.loads(prompt.split("SPEC:\n", 1)[1])
            items = []
            for _ in range(spec["count"]):
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
        data = json.dumps({"response": json.dumps(out, ensure_ascii=False)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def main():
    srv = HTTPServer(("127.0.0.1", 0), FakeOllama)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    generate.load_prompts = lambda keys, *a: prompts_from_sql()
    with tempfile.TemporaryDirectory() as d:
        args = ["--out", d, "--target", "30", "--workers", "3", "--subunits", "3-3", "4-4", "5-1",
                "--ollama", "http://127.0.0.1:%d" % srv.server_port]
        generate.main(args)
        generate.main(args)  # 재실행 시 이미 채워졌으므로 추가 생성 없어야 함
        conn = sqlite3.connect(Path(d) / "highsci.db")
        per = dict(conn.execute("SELECT subunit_code, COUNT(*) FROM items GROUP BY subunit_code").fetchall())
        assert per == {"3-3": 30, "4-4": 30, "5-1": 30}, per
        assert conn.execute("SELECT COUNT(*) FROM items WHERE choices_json LIKE '%①%'").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM item_concepts").fetchone()[0] >= 90
        diffs = dict(conn.execute("SELECT difficulty, COUNT(*) FROM items WHERE subunit_code='3-3' GROUP BY difficulty"))
        assert diffs == {1: 3, 2: 8, 3: 9, 4: 7, 5: 3}, diffs
        assert conn.execute("SELECT COUNT(*) FROM concept_edges WHERE kind='inter'").fetchone()[0] > 0
        files = sorted(p.name for p in (Path(d) / "exports").iterdir())
        assert "concept_graph.json" in files and "manifest.json" in files and len(files) == 5, files
        print("OK", per, diffs, files)


if __name__ == "__main__":
    main()
