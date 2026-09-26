#!/usr/bin/env python3
"""해외 입시·교과 참고 자료 수집기 (holymind에서 실행).

refs/sources.json의 공식 페이지에서 출발해 PDF/ZIP을 찾아 내려받고,
~/Downloads/highsci_db/references/ 에 원본을, highsci.db 에 목록·본문 텍스트·전문검색 색인을 저장한다.
참고용 개인 보관이며 재배포(저장소 커밋, 웹 공개, 책 전재)는 하지 않는다.

    python3 refs/fetch_refs.py                 # 찾기 → 내려받기 → 본문 추출 (이어하기)
    python3 refs/fetch_refs.py --discover      # 링크만 찾아 목록화 (내려받지 않음)
    python3 refs/fetch_refs.py --sources jp_dnc_kyotsu us_openstax
    python3 refs/fetch_refs.py --status        # 출처별 현황
    python3 refs/fetch_refs.py --search "自由落下"   # 본문 검색
"""
import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import zipfile
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from generate import default_out_dir  # noqa: E402  (저장 폴더 규칙 공유)

SOURCES = HERE / "sources.json"
SCHEMA = ROOT / "sql" / "refs_schema.sql"
DOC_EXT = (".pdf", ".zip")
MAX_PAGES_PER_SOURCE = 400
MAX_BYTES = 400 * 1024 * 1024
DELAY = 1.5  # 같은 도메인 요청 간격(초)

db_lock = threading.Lock()
_domain_lock = threading.Lock()
_domain_last = {}
_robots = {}


def log(msg):
    print(time.strftime("[%H:%M:%S] ") + msg, flush=True)


# ---------------------------------------------------------------- HTTP

class Http:
    def __init__(self, user_agent, ignore_robots=False):
        self.ua = user_agent
        self.ignore_robots = ignore_robots

    def _wait(self, url):
        host = urllib.parse.urlsplit(url).netloc
        with _domain_lock:
            last = _domain_last.get(host, 0)
            wait = last + DELAY - time.time()
            _domain_last[host] = max(time.time(), last + DELAY)
        if wait > 0:
            time.sleep(wait)

    def allowed(self, url, src=None):
        if self.ignore_robots or (src and src.get("ignore_robots")):
            return True
        parts = urllib.parse.urlsplit(url)
        base = "%s://%s" % (parts.scheme, parts.netloc)
        if base not in _robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                self._wait(base)
                req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": self.ua})
                with urllib.request.urlopen(req, timeout=20) as r:
                    rp.parse(r.read().decode("utf-8", "replace").splitlines())
            except Exception:
                rp = None  # robots.txt 없음/오류 → 허용
            _robots[base] = rp
        rp = _robots[base]
        return rp is None or rp.can_fetch(self.ua, url)

    def open(self, url, timeout=60):
        self._wait(url)
        req = urllib.request.Request(url, headers={"User-Agent": self.ua, "Accept-Language": "ko,en;q=0.8,ja;q=0.6,fr;q=0.6"})
        return urllib.request.urlopen(req, timeout=timeout)

    def text(self, url):
        with self.open(url) as r:
            ctype = r.headers.get("Content-Type", "")
            raw = r.read(8 * 1024 * 1024)
            m = re.search(r"charset=([\w-]+)", ctype)
            return r.geturl(), ctype, raw.decode(m.group(1) if m else "utf-8", "replace")


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self._href, self._buf = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._buf = []

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._buf).split())))
            self._href = None


def is_doc(url):
    return urllib.parse.urlsplit(url).path.lower().endswith(DOC_EXT)


def guess_year(s):
    m = re.search(r"令和\s*(\d+)", s) or re.search(r"/r(\d{1,2})[/_]", s)
    if m:
        return 2018 + int(m.group(1))
    m = re.search(r"(?<!\d)(20[0-3]\d|19[89]\d)(?!\d)", s)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- DB

def open_db(out):
    out.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(out / "highsci.db"), check_same_thread=False, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    return conn


def db(conn, sql, args=(), fetch=False):
    with db_lock:
        cur = conn.execute(sql, args)
        rows = cur.fetchall() if fetch else cur.lastrowid
        conn.commit()
        return rows


def add_found(conn, src, url, found_on, text):
    db(conn, "INSERT OR IGNORE INTO ref_docs(source_id,url,found_on,link_text,year) VALUES (?,?,?,?,?)",
       (src["id"], url, found_on, text[:300], guess_year(url + " " + text)))


# ---------------------------------------------------------------- discover

def discover(conn, http, src):
    found_before = db(conn, "SELECT COUNT(*) FROM ref_docs WHERE source_id=?", (src["id"],), fetch=True)[0][0]
    for url in src.get("direct", []):
        add_found(conn, src, url, "direct", "")
    if src.get("openstax_books"):
        discover_openstax(conn, http, src)
    include = re.compile(src.get("include") or ".", re.I)
    exclude = re.compile(src["exclude"], re.I) if src.get("exclude") else None
    follow = re.compile(src.get("follow") or ".", re.I)
    doc_url = re.compile(src["doc_url"], re.I) if src.get("doc_url") else None      # 확장자 없는 다운로드 링크
    paginate = re.compile(src["paginate"], re.I) if src.get("paginate") else None   # 게시판 다음 쪽(깊이 증가 없음)
    domains = set(src.get("allow_domains", []))
    queue = [(u, 0) for u in src.get("seeds", [])]
    seen, pages = set(), 0
    while queue and pages < src.get("max_pages", MAX_PAGES_PER_SOURCE):
        url, depth = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not http.allowed(url, src):
            log("[%s] robots.txt 불허: %s" % (src["id"], url))
            continue
        try:
            final, ctype, html = http.text(url)
        except Exception as e:
            log("[%s] 페이지 오류 %s: %s" % (src["id"], url, e))
            continue
        pages += 1
        if "html" not in ctype and "<a" not in html[:5000]:
            continue
        p = LinkParser()
        try:
            p.feed(html)
        except Exception:
            pass
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        page_title = " ".join(m.group(1).split())[:200] if m else ""  # 게시글 제목(과목명이 여기만 있을 때)
        links = list(p.links)
        # 자바스크립트 다운로드(onclick="fileDown('123')" 등)를 실제 URL로 바꾸는 규칙
        for rule in src.get("js_links", []):
            for m in re.finditer(rule["match"], html):
                links.append((rule["url"].format(*m.groups()), m.group(0)[:200]))
        for href, text in links:
            if not href or href.startswith(("mailto:", "javascript:", "#")):
                continue
            absu = urllib.parse.urljoin(final, href).split("#")[0]
            host = urllib.parse.urlsplit(absu).netloc
            if host not in domains:
                continue
            link_probe = urllib.parse.unquote(absu) + " " + text
            probe = link_probe + " " + page_title  # 포함 판단은 글 제목까지, 제외 판단은 링크 자체만
            if is_doc(absu) or (doc_url and doc_url.search(absu)):
                if include.search(probe) and not (exclude and exclude.search(link_probe)):
                    add_found(conn, src, absu, final, (text + " | " + page_title).strip(" |"))
            elif absu in seen:
                continue
            elif paginate and paginate.search(absu) and follow.search(absu):
                queue.append((absu, depth))
            elif depth < src.get("max_depth", 1) and follow.search(absu):
                queue.append((absu, depth + 1))
    n = db(conn, "SELECT COUNT(*) FROM ref_docs WHERE source_id=?", (src["id"],), fetch=True)[0][0]
    log("[%s] 페이지 %d개 탐색 → 문서 %d개 (신규 %d)" % (src["id"], pages, n, n - found_before))


def discover_openstax(conn, http, src):
    """OpenStax 책 상세 페이지/CMS API에서 PDF 주소를 찾는다 (둘 다 최선 노력)."""
    for slug in src["openstax_books"]:
        urls = set()
        api = ("https://openstax.org/apps/cms/api/v2/pages/?type=books.Book&fields=title,high_resolution_pdf_url,"
               "low_resolution_pdf_url&slug=%s" % slug)
        for url in (api, "https://openstax.org/details/books/%s" % slug):
            try:
                _, _, body = http.text(url)
                urls.update(re.findall(r"https://assets\.openstax\.org/[^\"'\s<>\\]+?\.pdf", body))
            except Exception as e:
                log("[%s] %s 조회 실패: %s" % (src["id"], slug, e))
            if urls:
                break
        for u in sorted(urls):
            add_found(conn, src, u, "openstax:" + slug, slug)
        if not urls:
            log("[%s] %s: PDF 주소를 찾지 못함 (sources.json direct에 직접 추가 가능)" % (src["id"], slug))


# ---------------------------------------------------------------- download

def header_filename(resp):
    """Content-Disposition의 파일명 (RFC 5987, 퍼센트 인코딩, UTF-8/CP949 원문 바이트 모두 처리)."""
    raw = resp.headers.get("Content-Disposition", "")
    m = re.search(r"filename\*\s*=\s*([\w-]*)''([^;]+)", raw, re.I)
    if m:
        name = urllib.parse.unquote(m.group(2).strip().strip('"'), encoding=m.group(1) or "utf-8", errors="replace")
    else:
        m = re.search(r'filename\s*=\s*"?([^";]+)"?', raw, re.I)
        if not m:
            return None
        name = m.group(1).strip()
        try:  # http.client는 헤더를 latin-1로 읽으므로 원래 바이트로 되돌려 다시 디코딩
            b = name.encode("latin-1")
            for enc in ("utf-8", "cp949"):
                try:
                    name = b.decode(enc)
                    break
                except UnicodeDecodeError:
                    pass
        except UnicodeEncodeError:
            pass
        if "%" in name:
            name = urllib.parse.unquote(name)
    name = re.sub(r"[^\w.\-()]+", "_", Path(name.replace("\\", "/")).name)[:150]
    return name or None


def safe_name(url):
    name = urllib.parse.unquote(Path(urllib.parse.urlsplit(url).path).name) or "index"
    name = re.sub(r"[^\w.\-가-힣ぁ-んァ-ン一-龥]+", "_", name)[:120]
    return name


def download(conn, http, src, out, retry_errors):
    states = ("found", "error") if retry_errors else ("found",)
    rows = db(conn, "SELECT id,url FROM ref_docs WHERE source_id=? AND parent_id IS NULL AND status IN (%s)"
              % ",".join("?" * len(states)), (src["id"],) + states, fetch=True)
    folder = out / "references" / src["country"] / src["id"]
    folder.mkdir(parents=True, exist_ok=True)
    ok = 0
    for doc_id, url in rows:
        try:
            if not http.allowed(url, src):
                db(conn, "UPDATE ref_docs SET status='skipped', error='robots.txt' WHERE id=?", (doc_id,))
                continue
            path, sha, size, mime = fetch_file(http, url, folder)
            finish_file(conn, out, doc_id, path, sha, size, mime)
            ok += 1
            if path.suffix.lower() == ".zip":
                unpack_zip(conn, out, src, doc_id, url, path)
        except Exception as e:
            db(conn, "UPDATE ref_docs SET status='error', error=?, fetched_at=datetime('now','localtime') WHERE id=?",
               (str(e)[:300], doc_id))
            log("[%s] 받기 실패 %s: %s" % (src["id"], url, e))
    log("[%s] 내려받음 %d/%d" % (src["id"], ok, len(rows)))


def fetch_file(http, url, folder):
    with http.open(url, timeout=300) as r:
        size = int(r.headers.get("Content-Length") or 0)
        if size > MAX_BYTES:
            raise ValueError("파일이 너무 큼 (%d MB)" % (size >> 20))
        mime = r.headers.get("Content-Type", "")
        name = header_filename(r) or safe_name(r.geturl() or url)
        tmp = folder / (".part-" + hashlib.sha1(url.encode()).hexdigest()[:12])
        h, total, head = hashlib.sha256(), 0, b""
        with open(tmp, "wb") as f:
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BYTES:
                    f.close()
                    tmp.unlink()
                    raise ValueError("파일이 너무 큼")
                if not head:
                    head = chunk[:8]
                h.update(chunk)
                f.write(chunk)
    kind = ".pdf" if head.startswith(b"%PDF") else ".zip" if head.startswith(b"PK") else None
    if kind is None:  # 확장자만 .pdf인 로그인·차단·오류 페이지 등
        tmp.unlink()
        raise ValueError("PDF/ZIP이 아닌 응답 (%s) — 로그인·차단 페이지일 수 있음" % (mime or "형식 불명"))
    if not name.lower().endswith(DOC_EXT):
        name += kind
    dest = folder / name
    if dest.exists() and file_sha(dest) != h.hexdigest():
        dest = folder / ("%s_%s%s" % (dest.stem, h.hexdigest()[:8], dest.suffix))
    tmp.replace(dest)
    return dest, h.hexdigest(), total, mime


def file_sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def finish_file(conn, out, doc_id, path, sha, size, mime):
    rel = str(path.relative_to(out))
    dup = db(conn, "SELECT id,path FROM ref_docs WHERE sha256=? AND status='ok' AND id<>?", (sha, doc_id), fetch=True)
    if dup and dup[0][1] != rel:
        path.unlink()  # 같은 파일이 이미 있음 → 하나만 보관
        rel, status = dup[0][1], "dup"
    else:
        status = "ok"
    db(conn, "UPDATE ref_docs SET path=?, sha256=?, bytes=?, mime=?, status=?, error=NULL, "
             "fetched_at=datetime('now','localtime') WHERE id=?", (rel, sha, size, mime, status, doc_id))


def unpack_zip(conn, out, src, doc_id, url, path):
    target = path.with_suffix("")
    target.mkdir(exist_ok=True)
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir() or not info.filename.lower().endswith(".pdf"):
                continue
            name = re.sub(r"[^\w.\-]+", "_", Path(info.filename).name)
            dest = target / name
            with z.open(info) as fsrc, open(dest, "wb") as fdst:
                shutil.copyfileobj(fsrc, fdst)
            child_url = url + "#" + info.filename
            db(conn, "INSERT OR IGNORE INTO ref_docs(source_id,url,found_on,link_text,parent_id,year) VALUES (?,?,?,?,?,?)",
               (src["id"], child_url, url, info.filename, doc_id, guess_year(url)))
            cid = db(conn, "SELECT id FROM ref_docs WHERE url=?", (child_url,), fetch=True)[0][0]
            finish_file(conn, out, cid, dest, file_sha(dest), dest.stat().st_size, "application/pdf")


# ---------------------------------------------------------------- text

def extract_pages(pdf):
    """[(page, text)] 또는 None(추출 도구 없음)."""
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, timeout=600)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode("utf-8", "replace")[:200])
        pages = r.stdout.decode("utf-8", "replace").split("\f")
        return [(i, t) for i, t in enumerate(pages, 1) if t.strip()]
    try:
        import pypdf
    except BaseException:  # 설치 안 됨 또는 의존성 충돌
        return None
    reader = pypdf.PdfReader(str(pdf))
    return [(i, p.extract_text() or "") for i, p in enumerate(reader.pages, 1)]


def extract(conn, out, src):
    rows = db(conn, "SELECT id,path FROM ref_docs WHERE source_id=? AND status='ok' AND text_status IS NULL "
                    "AND lower(path) LIKE '%.pdf'", (src["id"],), fetch=True)
    done = 0
    for doc_id, rel in rows:
        try:
            pages = extract_pages(out / rel)
        except Exception as e:
            db(conn, "UPDATE ref_docs SET text_status='error', error=? WHERE id=?", (str(e)[:300], doc_id))
            continue
        if pages is None:
            log("본문 추출 도구가 없습니다: sudo apt install poppler-utils  (추출은 나중에 --extract로 다시)")
            return
        with db_lock:
            conn.execute("DELETE FROM ref_pages WHERE doc_id=?", (doc_id,))
            conn.execute("DELETE FROM ref_fts WHERE doc_id=?", (doc_id,))
            for page, text in pages:
                text = re.sub(r"[ \t]+", " ", text).strip()
                if text:
                    conn.execute("INSERT INTO ref_pages(doc_id,page,text) VALUES (?,?,?)", (doc_id, page, text))
                    conn.execute("INSERT INTO ref_fts(text,doc_id,page) VALUES (?,?,?)", (text, doc_id, page))
            conn.execute("UPDATE ref_docs SET pages=?, text_status=? WHERE id=?",
                         (len(pages), "ok" if any(t.strip() for _, t in pages) else "empty", doc_id))
            conn.commit()
        done += 1
    log("[%s] 본문 추출 %d/%d" % (src["id"], done, len(rows)))


# ---------------------------------------------------------------- report

def status(conn):
    rows = conn.execute(
        "SELECT s.country, s.id, "
        "SUM(d.status='found'), SUM(d.status='ok'), SUM(d.status='dup'), SUM(d.status='error'), SUM(d.status='skipped'), "
        "ROUND(SUM(CASE WHEN d.status='ok' THEN d.bytes ELSE 0 END)/1048576.0,1), SUM(d.text_status='ok') "
        "FROM ref_sources s LEFT JOIN ref_docs d ON d.source_id=s.id GROUP BY s.id ORDER BY s.country, s.id").fetchall()
    print("%-5s %-34s %6s %6s %5s %6s %6s %9s %6s" % ("나라", "출처", "대기", "완료", "중복", "오류", "건너뜀", "MB", "본문"))
    for r in rows:
        print("%-5s %-34s %6s %6s %5s %6s %6s %9s %6s" % tuple("-" if v is None else v for v in r))


def search(conn, q, limit=20):
    rows = conn.execute(
        "SELECT d.source_id, f.page, d.path, snippet(ref_fts, 0, '[', ']', ' … ', 12) FROM ref_fts f "
        "JOIN ref_docs d ON d.id=f.doc_id WHERE ref_fts MATCH ? LIMIT ?", ('"%s"' % q.replace('"', ""), limit)).fetchall()
    for src, page, path, snip in rows:
        print("%s  p.%s  %s\n    %s" % (src, page, path, snip.replace("\n", " ")))
    print("(%d건)" % len(rows))


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="해외 참고 자료 수집기")
    ap.add_argument("--out", type=Path, default=default_out_dir())
    ap.add_argument("--sources", nargs="+", help="특정 출처 id만")
    ap.add_argument("--country", nargs="+", help="특정 나라만 (일본 미국 인도 프랑스 영국)")
    ap.add_argument("--all", action="store_true", help="enabled=false(비공식 사이트)도 포함")
    ap.add_argument("--discover", action="store_true", help="링크 찾기만")
    ap.add_argument("--download", action="store_true", help="내려받기만")
    ap.add_argument("--extract", action="store_true", help="본문 추출만")
    ap.add_argument("--retry-errors", action="store_true", help="실패했던 파일도 다시 받기")
    ap.add_argument("--workers", type=int, default=4, help="동시에 처리할 출처 수 (같은 사이트는 항상 순차)")
    ap.add_argument("--ignore-robots", action="store_true",
                    help="robots.txt 무시 (공개 파일을 사람 속도로 개인 참고용으로 받을 때만)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--search")
    args = ap.parse_args(argv)

    cfg = json.loads(SOURCES.read_text(encoding="utf-8"))
    conn = open_db(args.out)
    if args.status:
        return status(conn)
    if args.search:
        return search(conn, args.search)

    srcs = [s for s in cfg["sources"] if args.all or s.get("enabled", True) or (args.sources and s["id"] in args.sources)]
    if args.sources:
        srcs = [s for s in srcs if s["id"] in args.sources]
    if args.country:
        srcs = [s for s in srcs if s["country"] in args.country]
    for s in srcs:
        db(conn, "INSERT OR REPLACE INTO ref_sources(id,country,org,exam,level,subjects,license,config_json) "
                 "VALUES (?,?,?,?,?,?,?,?)",
           (s["id"], s["country"], s["org"], s["exam"], s.get("level"), json.dumps(s.get("subjects", []), ensure_ascii=False),
            s.get("license"), json.dumps(s, ensure_ascii=False)))
    steps = [n for n in ("discover", "download", "extract") if getattr(args, n)] or ["discover", "download", "extract"]
    http = Http(cfg["user_agent"], args.ignore_robots)
    log("출처 %d개 | 단계 %s | 저장 %s" % (len(srcs), "→".join(steps), args.out / "references"))

    def run(src):
        try:
            if "discover" in steps:
                discover(conn, http, src)
            if "download" in steps:
                download(conn, http, src, args.out, args.retry_errors)
            if "extract" in steps:
                extract(conn, args.out, src)
        except Exception as e:
            log("[%s] 중단: %s" % (src["id"], e))

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        list(pool.map(run, srcs))
    status(conn)


if __name__ == "__main__":
    sys.exit(main())
