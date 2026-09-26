"""외부 접속 없이 참고 자료 수집기 검증: 가짜 사이트 + 가짜 본문 추출기.

    python3 highsci/tests/test_refs.py
"""
import io
import json
import sqlite3
import sys
import tempfile
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "refs"))
import fetch_refs  # noqa: E402

PDF_A = b"%PDF-1.4 fake A"


def make_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("keph1dd/keph101.pdf", b"%PDF-1.4 chapter 1")
        z.writestr("keph1dd/keph102.pdf", b"%PDF-1.4 chapter 2")
        z.writestr("keph1dd/readme.txt", b"x")
    return buf.getvalue()


PAGES = {
    "/robots.txt": ("text/plain", b"User-agent: *\nDisallow: /secret/\n"),
    "/kakomondai/": ("text/html; charset=utf-8", """
        <a href="r7/">令和7年度</a> <a href="/news/">お知らせ</a>
        <a href="/secret/r7_butsuri.pdf">物理 (secret)</a>""".encode()),
    "/kakomondai/r7/": ("text/html; charset=utf-8", """
        <a href="/files/r7_butsuri_kiso.pdf">物理基礎 問題</a>
        <a href="/files/r7_butsuri_kiso_copy.pdf">物理基礎 問題(再掲)</a>
        <a href="/files/r7_kokugo.pdf">国語 問題</a>
        <a href="/files/r7_seibutsu_kaitou.pdf">生物 正解</a>
        <a href="/files/login.pdf">化学 (要ログイン)</a>
        <a href="/files/keph1dd.zip">物理 教科書 zip</a>""".encode()),
    "/news/": ("text/html", b'<a href="/files/r7_chigaku_news.pdf">chigaku</a>'),
    "/files/r7_butsuri_kiso.pdf": ("application/pdf", PDF_A),
    "/files/r7_butsuri_kiso_copy.pdf": ("application/pdf", PDF_A),
    "/files/r7_seibutsu_kaitou.pdf": ("application/pdf", b"%PDF-1.4 bio answers"),
    "/files/login.pdf": ("text/html", b"<html>please log in</html>"),
    "/files/keph1dd.zip": ("application/zip", make_zip()),
    # 한국형 게시판: 목록 여러 쪽 → 글 보기 → fileDown.do (확장자 없음, 파일명은 헤더로)
    "/board/list.do?boardID=1500235&page=1": ("text/html; charset=utf-8", """<title>기출문제</title>
        <a href="/board/view.do?boardID=1500235&seq=1">2025학년도 수능</a>
        <a href="/board/list.do?boardID=1500235&page=2">2</a>""".encode()),
    "/board/list.do?boardID=1500235&page=2": ("text/html; charset=utf-8", """
        <a href="/board/view.do?boardID=1500235&seq=2">2024학년도 수능</a>
        <a href="/board/list.do?boardID=1500235&page=3">3</a>""".encode()),
    "/board/list.do?boardID=1500235&page=3": ("text/html; charset=utf-8", """
        <a href="/board/view.do?boardID=1500235&seq=3">2023학년도 6월 모의평가 과학탐구</a>""".encode()),
    "/board/view.do?boardID=1500235&seq=1": ("text/html; charset=utf-8", """<title>2025학년도 수능 문제 및 정답</title>
        <a href="/board/fileDown.do?f=11">2025 과학탐구영역 문제</a>
        <a href="/board/fileDown.do?f=12">2025 국어영역 문제</a>
        <span onclick="fn_down('13')">정답표</span>""".encode()),
    "/board/view.do?boardID=1500235&seq=2": ("text/html; charset=utf-8", """<title>2024학년도 수능</title>
        <a href="/board/fileDown.do?f=21">물리학Ⅰ 문제</a>""".encode()),
    "/board/view.do?boardID=1500235&seq=3": ("text/html; charset=utf-8", """<title>2023학년도 6월 모의평가 과학탐구영역</title>
        <a href="/board/fileDown.do?f=31">문제지</a>""".encode()),
}
DISPO = {
    "/board/fileDown.do?f=11": "attachment; filename=\"2025_수능_과학탐구.pdf\"".encode("utf-8").decode("latin-1"),
    "/board/fileDown.do?f=13": "attachment; filename*=UTF-8''2025_%EC%A0%95%EB%8B%B5.pdf",
    "/board/fileDown.do?f=21": "attachment; filename=\"2024_물리학I.pdf\"".encode("cp949").decode("latin-1"),
    "/board/fileDown.do?f=31": "attachment; filename=\"mock_2306.pdf\"",
}
for k in DISPO:
    PAGES[k] = ("application/octet-stream", ("%PDF-1.4 " + k).encode())


class Site(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in PAGES:
            self.send_response(404)
            self.end_headers()
            return
        ctype, body = PAGES[self.path]
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if self.path in DISPO:
            self.send_header("Content-Disposition", DISPO[self.path])
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Site)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    host = "127.0.0.1:%d" % srv.server_port
    base = "http://" + host
    fetch_refs.DELAY = 0
    fetch_refs.extract_pages = lambda pdf: [(1, "自由落下の実験 " + pdf.name), (2, "運動量と力積")]
    cfg = {"user_agent": "test", "sources": [{
        "id": "jp_test", "country": "일본", "org": "t", "exam": "t", "subjects": ["물리"], "license": "t",
        "seeds": [base + "/kakomondai/"], "allow_domains": [host], "max_depth": 2,
        "follow": "/kakomondai/", "include": "物理|生物|化学|butsuri|seibutsu", "exclude": "正解(再)",
        "direct": [base + "/files/missing.pdf"]}, {
        "id": "kr_test", "country": "한국", "org": "t", "exam": "t", "subjects": ["물리"], "license": "t",
        "seeds": [base + "/board/list.do?boardID=1500235&page=1"], "allow_domains": [host], "max_depth": 1,
        "follow": "board/(list|view)\\.do.*boardID=15002", "paginate": "board/list\\.do.*page=\\d+",
        "doc_url": "fileDown", "js_links": [{"match": "fn_down\\('(\\d+)'\\)", "url": "/board/fileDown.do?f={0}"}],
        "include": "과학|물리|정답", "exclude": "국어|수학|영어"}]}
    with tempfile.TemporaryDirectory() as d:
        fetch_refs.SOURCES = Path(d) / "sources.json"
        fetch_refs.SOURCES.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        fetch_refs.main(["--out", d])
        fetch_refs.main(["--out", d])  # 이어하기: 새로 받는 것 없어야 함
        conn = sqlite3.connect(Path(d) / "highsci.db")
        docs = {u.rsplit("/", 1)[-1] if "#" not in u else u.split("/files/")[-1]: (s, p)
                for u, s, p in conn.execute("SELECT url,status,path FROM ref_docs")}
        print(json.dumps(docs, ensure_ascii=False, indent=1))
        assert "r7_kokugo.pdf" not in docs                       # include 불일치
        assert "r7_chigaku_news.pdf" not in docs                 # follow 불일치 페이지
        assert docs["r7_butsuri.pdf"] == ("skipped", None)       # robots.txt Disallow → 기록만
        assert docs["r7_butsuri_kiso.pdf"][0] == "ok"
        assert docs["r7_butsuri_kiso_copy.pdf"][0] == "dup"      # 같은 내용 → 한 파일만 보관
        assert docs["r7_butsuri_kiso_copy.pdf"][1] == docs["r7_butsuri_kiso.pdf"][1]
        assert docs["login.pdf"][0] == "error"                   # HTML 로그인 페이지
        assert docs["missing.pdf"][0] == "error"                 # 404
        assert docs["keph1dd.zip"][0] == "ok"
        assert docs["keph1dd.zip#keph1dd/keph101.pdf"][0] == "ok" and docs["keph1dd.zip#keph1dd/keph102.pdf"][0] == "ok"
        assert not any("readme" in k for k in docs)
        files = sorted(str(p.relative_to(d)) for p in (Path(d) / "references").rglob("*") if p.is_file())
        files = [f for f in files if "/jp_test/" in f]
        assert len(files) == 5, files                            # kiso, seibutsu, zip, zip 안 pdf 2개
        assert conn.execute("SELECT year FROM ref_docs WHERE url LIKE '%r7_seibutsu%'").fetchone()[0] == 2025
        n_text = conn.execute("SELECT COUNT(*) FROM ref_docs WHERE text_status='ok'").fetchone()[0]
        assert n_text == 8, n_text                               # 일본 4 (중복·zip 원본 제외) + 한국 4
        hits = conn.execute("SELECT COUNT(*) FROM ref_fts WHERE ref_fts MATCH '\"自由落下\"'").fetchone()[0]
        assert hits == 8, hits
        kr = {r[0].split("f=")[1]: r[1:] for r in conn.execute(
            "SELECT url,status,path,year FROM ref_docs WHERE source_id='kr_test'")}
        print(kr)
        assert set(kr) == {"11", "13", "21", "31"}, kr             # 국어(12) 제외, 3쪽까지 따라감, JS 링크 포함
        assert kr["11"][1].endswith("2025_수능_과학탐구.pdf")        # UTF-8 원문 바이트 파일명
        assert kr["13"][1].endswith("2025_정답.pdf")                 # RFC 5987
        assert kr["21"][1].endswith("2024_물리학I.pdf")              # CP949 파일명
        assert kr["31"][2] == 2023 and kr["31"][0] == "ok"          # 글 제목으로 과학 판별 + 연도
        fetch_refs.main(["--out", d, "--search", "運動量"])
        print("OK files:", files)


if __name__ == "__main__":
    main()
