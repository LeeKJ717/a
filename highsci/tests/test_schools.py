"""학교별 기출 수집 모드 검증: 가짜 나이스 API + 가짜 학교 홈페이지 (외부 접속 없음).

    python3 highsci/tests/test_schools.py
"""
import io
import json
import os
import sqlite3
import sys
import tempfile
import threading
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "refs"))
import fetch_refs  # noqa: E402


def hwpx(text):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("mimetype", "application/hwp+zip")
        z.writestr("Contents/section0.xml", "<hs:sec><hp:p><hp:t>%s</hp:t></hp:p><hp:p><hp:t>2번 문항</hp:t></hp:p></hs:sec>" % text)
    return buf.getvalue()


FILES = {  # 경로: (Content-Disposition 파일명, 내용)
    "/board/downFile.do?f=a": ("2025_1학기_중간_1학년_통합과학.hwpx", hwpx("자유 낙하 운동에서 가속도는")),
    "/board/downFile.do?f=b": ("2025_1학기_중간_1학년_국어.hwp", fetch_refs.OLE_MAGIC + b"korean"),
    "/board/downFile.do?f=c": ("과학_정답.hwp", fetch_refs.OLE_MAGIC + b"answers"),
    "/board/downFile.do?f=d": ("1학년.pdf", b"%PDF-1.4 science final"),
    "/gg/down.do?f=g": ("2025_2학기_기말_통합과학.pdf", b"%PDF-1.4 gyeonggi science"),
}
PAGES = {
    "/": "<title>OO고등학교</title><a href='/intro.do'>학교소개</a> <a href='/sub/menu.do?id=77'>정기고사 기출문제</a>"
         "<a href='/sub/menu.do?id=12'>급식</a>",
    "/intro.do": "<a href='/secret.hwp'>과학 비밀</a>",  # 기출 메뉴가 아니므로 따라가지 않아야 함
    "/sub/menu.do?id=77": "<title>정기고사 기출문제</title><a href='/board/view.do?no=1'>2025 1학기 중간고사</a>"
                          "<a href='/sub/menu.do?id=77&page=2'>2</a>",
    "/sub/menu.do?id=77&page=2": "<a href='/board/view.do?no=2'>2024 2학기 기말고사</a>",
    "/board/view.do?no=1": "<title>2025학년도 1학기 중간고사 기출</title>"
                           "<a href='/board/downFile.do?f=a'>1학년 통합과학</a><a href='/board/downFile.do?f=b'>1학년 국어</a>"
                           "<a href='/board/downFile.do?f=c'>과학 정답</a>",
    "/board/view.do?no=2": "<title>2024학년도 2학기 기말고사 과학 기출</title><a href='/board/downFile.do?f=d'>1학년</a>",
    # 경기 학교 (다른 홈페이지 경로)
    "/gg/": "<title>GG고등학교</title><a href='/gg/bbs.do?m=5'>지필평가 문항 공개</a>",
    "/gg/bbs.do?m=5": "<a href='/gg/down.do?f=g'>2학기 기말 통합과학</a>",
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        if path.startswith("/hub/schoolInfo"):
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(path).query))
            assert q["KEY"] == "testkey"
            rows = {("B10", "고등학교"): [{"SD_SCHUL_CODE": "7010001", "SCHUL_NM": "OO고등학교", "SCHUL_KND_SC_NM": "고등학교",
                                          "ATPT_OFCDC_SC_CODE": "B10", "HMPG_ADRES": self.server.home}],
                    ("B10", "중학교"): [{"SD_SCHUL_CODE": "7020002", "SCHUL_NM": "XX중학교", "SCHUL_KND_SC_NM": "중학교",
                                        "ATPT_OFCDC_SC_CODE": "B10", "HMPG_ADRES": ""}],
                    ("J10", "고등학교"): [{"SD_SCHUL_CODE": "7530003", "SCHUL_NM": "GG고등학교", "SCHUL_KND_SC_NM": "고등학교",
                                          "ATPT_OFCDC_SC_CODE": "J10", "HMPG_ADRES": "http://%s/gg/" % self.server.home}],
                    }.get((q["ATPT_OFCDC_SC_CODE"], q["SCHUL_KND_SC_NM"]))
            if rows is None:
                return self.reply("application/json", json.dumps(
                    {"RESULT": {"CODE": "INFO-200", "MESSAGE": "해당하는 데이터가 없습니다."}}, ensure_ascii=False).encode())
            return self.reply("application/json", json.dumps(
                {"schoolInfo": [{"head": [{"list_total_count": len(rows)}]}, {"row": rows}]}, ensure_ascii=False).encode())
        if path in FILES:
            name, body = FILES[path]
            return self.reply("application/octet-stream", body,
                              {"Content-Disposition": "attachment; filename=\"%s\"" % name.encode("utf-8").decode("latin-1")})
        if path in PAGES:
            return self.reply("text/html; charset=utf-8", PAGES[path].encode())
        self.send_response(404)
        self.end_headers()

    def reply(self, ctype, body, headers=None):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    srv.home = "127.0.0.1:%d" % srv.server_port  # 나이스처럼 http:// 없이 주는 경우
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    fetch_refs.DELAY = 0
    fetch_refs.NEIS_URL = "http://%s/hub/schoolInfo" % srv.home
    os.environ["NEIS_API_KEY"] = "testkey"
    real = fetch_refs.extract_pages
    fetch_refs.extract_pages = lambda p: [(1, "PDF 과학 기말")] if p.suffix == ".pdf" else real(p)
    with tempfile.TemporaryDirectory() as d:
        fetch_refs.main(["--out", d, "--schools", "--region", "서울"])   # 서울만
        conn = sqlite3.connect(Path(d) / "highsci.db")
        assert [r[0] for r in conn.execute("SELECT code FROM ref_schools ORDER BY code")] == ["7010001", "7020002"]
        fetch_refs.main(["--out", d, "--schools"])                       # 기본: 서울+경기
        schools = conn.execute("SELECT code,name,homepage,source_id,office FROM ref_schools ORDER BY code").fetchall()
        print(schools)
        assert schools[0][2] == "http://" + srv.home and schools[0][3] == "kr_school_7010001"
        assert schools[1][3] is None  # 홈페이지 없는 학교는 건너뜀
        assert schools[2][1:] == ("GG고등학교", "http://%s/gg/" % srv.home, "kr_school_7530003", "J10"), schools[2]
        gg = conn.execute("SELECT path, year FROM ref_docs WHERE source_id='kr_school_7530003'").fetchall()
        assert gg == [("references/한국/kr_school_7530003/2025_2학기_기말_통합과학.pdf", 2025)], gg
        exam = conn.execute("SELECT exam FROM ref_sources WHERE id='kr_school_7530003'").fetchone()[0]
        assert exam.startswith("경기 고등학교"), exam
        try:
            fetch_refs.main(["--out", d, "--schools", "--region", "부산"])
            raise AssertionError("알 수 없는 지역은 오류여야 함")
        except SystemExit as e:
            assert "부산" in str(e)
        docs = {r[0].split("f=")[-1] if "f=" in r[0] else r[0]: r[1:] for r in conn.execute(
            "SELECT url,status,path,text_status,year FROM ref_docs WHERE source_id='kr_school_7010001'")}
        print(json.dumps(docs, ensure_ascii=False, indent=1))
        assert set(docs) == {"a", "c", "d"}, docs                 # 국어(b) 제외, 학교소개 쪽 파일은 탐색 안 함
        assert docs["a"][1].endswith("통합과학.hwpx") and docs["a"][2] == "ok" and docs["a"][3] == 2025
        assert docs["c"][1].endswith("과학_정답.hwp") and docs["c"][2] in ("no_extractor", "ok")
        assert docs["d"][1].endswith("1학년.pdf") and docs["d"][3] == 2024   # 2쪽 게시물, 글 제목으로 과학 판별
        text = conn.execute("SELECT text FROM ref_pages p JOIN ref_docs d ON d.id=p.doc_id "
                            "WHERE d.path LIKE '%.hwpx'").fetchone()[0]
        assert "자유 낙하 운동에서 가속도는" in text and "2번 문항" in text, text
        snaps = list((Path(d) / "logs" / "snapshots" / "kr_school_7010001").glob("*.html"))
        assert snaps, "기출 페이지 스냅숏이 저장되어야 함"
        fetch_refs.main(["--out", d, "--status"])
        fetch_refs.main(["--out", d, "--status", "--schools-detail"])

        csvp = Path(d) / "schools.csv"
        csvp.write_text("학교명,학교종류명,표준학교코드,홈페이지주소\nAA고,고등학교,1,aa.sen.hs.kr\nBB중,중학교,2,\nCC초,초등학교,3,cc.es.kr\n",
                        encoding="utf-8")
        tpl = {"neis": {"offices": {"서울": "B10", "경기": "J10"}, "kinds": ["중학교", "고등학교"]}, "max_depth": 3}
        rows = fetch_refs.load_schools(tpl, str(csvp))
        assert [r["name"] for r in rows] == ["AA고", "BB중"], rows      # 지역 열 없으면 첫 지역(서울)으로
        csvp = Path(d) / "schools2.csv"
        csvp.write_text("학교명,학교종류명,표준학교코드,홈페이지주소,시도\nDD고,고등학교,4,dd.goe.go.kr,경기\nEE고,고등학교,5,ee.sen.hs.kr,서울\n",
                        encoding="utf-8")
        rows2 = fetch_refs.load_schools(tpl, str(csvp), regions=["경기"])
        assert [(r["name"], r["office"], r["region"]) for r in rows2] == [("DD고", "J10", "경기")], rows2
        srcs = fetch_refs.school_sources(tpl, rows)
        assert len(srcs) == 1 and srcs[0]["seeds"] == ["http://aa.sen.hs.kr"] and "www.aa.sen.hs.kr" in srcs[0]["allow_domains"]
        print("OK")


if __name__ == "__main__":
    main()
