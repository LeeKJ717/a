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
import csv
import hashlib
import json
import os
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
DOC_EXT = (".pdf", ".zip", ".hwp", ".hwpx")  # 학교 시험지는 한글(HWP/HWPX) 파일이 많다
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # HWP 5.x(복합 문서)
TEXT_EXT = (".pdf", ".hwp", ".hwpx")
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

def expand_templates(src):
    """seed_templates: {"template": ".../{year}/{level}/...", "vars": {"year": [2019, 2020], "level": ["vwo"]}}
    → 모든 조합의 시작 URL. vars 값에 "2015-2026" 같은 범위 문자열도 가능."""
    import itertools
    urls = []
    for t in src.get("seed_templates", []):
        keys = list(t["vars"])
        values = []
        for k in keys:
            v = t["vars"][k]
            if isinstance(v, str) and re.fullmatch(r"\d+-\d+", v):
                a, b = map(int, v.split("-"))
                v = list(range(a, b + 1))
            values.append(v)
        for combo in itertools.product(*values):
            urls.append(t["template"].format(**dict(zip(keys, combo))))
    return urls


def discover(conn, http, src, out=None):
    found_before = db(conn, "SELECT COUNT(*) FROM ref_docs WHERE source_id=?", (src["id"],), fetch=True)[0][0]
    for url in src.get("direct", []):
        add_found(conn, src, url, "direct", "")
    if src.get("openstax_books"):
        discover_openstax(conn, http, src)
    include = re.compile(src.get("include") or ".", re.I)
    exclude = re.compile(src["exclude"], re.I) if src.get("exclude") else None
    # follow=URL 정규식, follow_text=링크 글자 정규식(학교 홈페이지처럼 URL에 규칙이 없을 때). 둘 중 하나라도 맞으면 따라간다.
    follow_text = re.compile(src["follow_text"], re.I) if src.get("follow_text") else None
    follow_re = re.compile(src.get("follow") or ("(?!)" if follow_text else "."), re.I)
    doc_url = re.compile(src["doc_url"], re.I) if src.get("doc_url") else None      # 확장자 없는 다운로드 링크
    snap = re.compile(src["snapshot"], re.I) if src.get("snapshot") and out else None  # 구조 확인용 HTML 저장
    snaps = 0
    paginate = re.compile(src["paginate"], re.I) if src.get("paginate") else None   # 게시판 다음 쪽(깊이 증가 없음)
    domains = set(src.get("allow_domains", []))
    queue = [(u, 0) for u in src.get("seeds", []) + expand_templates(src)]
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
        if snap and snaps < 5 and snap.search(html):
            d = out / "logs" / "snapshots" / src["id"]
            d.mkdir(parents=True, exist_ok=True)
            snaps += 1
            (d / ("%02d.html" % snaps)).write_text("<!-- %s -->\n%s" % (final, html), encoding="utf-8")
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
            else:
                follow = follow_re.search(absu) or (follow_text and follow_text.search(text))
                same_board = urllib.parse.urlsplit(absu).path == urllib.parse.urlsplit(final).path
                if paginate and paginate.search(absu) and (follow or same_board):  # 같은 게시판의 다음 쪽
                    queue.append((absu, depth))
                elif depth < src.get("max_depth", 1) and follow:
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
            # 링크 글자에 연도가 없으면 서버가 준 파일명에서 추정
            db(conn, "UPDATE ref_docs SET year=COALESCE(year, ?) WHERE id=?", (guess_year(path.name), doc_id))
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
    low = name.lower()
    if head.startswith(b"%PDF"):
        kind = ".pdf"
    elif head.startswith(b"PK"):  # ZIP 계열: .zip / .hwpx
        kind = ".hwpx" if low.endswith(".hwpx") else ".zip"
    elif head.startswith(OLE_MAGIC) or head.startswith(b"HWP Doc"):  # HWP 5.x / HWP 3.0
        kind = ".hwp"
    else:  # 확장자만 문서인 로그인·차단·오류 페이지 등
        tmp.unlink()
        raise ValueError("PDF/ZIP/HWP가 아닌 응답 (%s) — 로그인·차단 페이지일 수 있음" % (mime or "형식 불명"))
    if not low.endswith(kind):
        name = (name[:-len(Path(name).suffix)] if Path(name).suffix.lower() in DOC_EXT else name) + kind
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
    """[(page, text)] 또는 None(추출 도구 없음). PDF는 쪽 단위, HWPX는 구역(section) 단위, HWP는 전체 1쪽."""
    suffix = pdf.suffix.lower()
    if suffix == ".hwpx":
        with zipfile.ZipFile(pdf) as z:
            names = sorted((n for n in z.namelist() if re.match(r"Contents/section\d+\.xml$", n)),
                           key=lambda n: int(re.search(r"\d+", n).group()))
            out = []
            for i, n in enumerate(names, 1):
                xml = z.read(n).decode("utf-8", "replace")
                xml = re.sub(r"</hp:p>|<hp:lineBreak/>", "\n", xml)
                out.append((i, re.sub(r"<[^>]+>", "", xml)))
            return out
    if suffix == ".hwp":
        if not shutil.which("hwp5txt"):  # pip install pyhwp
            return None
        r = subprocess.run(["hwp5txt", str(pdf)], capture_output=True, timeout=300)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode("utf-8", "replace")[:200])
        return [(1, r.stdout.decode("utf-8", "replace"))]
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
    rows = db(conn, "SELECT id,path FROM ref_docs WHERE source_id=? AND status='ok' "
                    "AND (text_status IS NULL OR text_status='no_extractor')", (src["id"],), fetch=True)
    rows = [r for r in rows if r[1] and r[1].lower().endswith(TEXT_EXT)]
    done, missing = 0, set()
    for doc_id, rel in rows:
        try:
            pages = extract_pages(out / rel)
        except Exception as e:
            db(conn, "UPDATE ref_docs SET text_status='error', error=? WHERE id=?", (str(e)[:300], doc_id))
            continue
        if pages is None:  # 이 형식의 추출 도구가 없음 → 표시만 하고 계속 (도구 설치 후 --extract로 다시)
            missing.add(Path(rel).suffix.lower())
            db(conn, "UPDATE ref_docs SET text_status='no_extractor' WHERE id=?", (doc_id,))
            continue
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
    hints = {".pdf": "sudo apt install poppler-utils", ".hwp": "pip install pyhwp"}
    for ext in sorted(missing):
        log("[%s] %s 본문 추출 도구 없음 → %s 후 --extract" % (src["id"], ext, hints.get(ext, "")))


# ---------------------------------------------------------------- schools

NEIS_URL = "https://open.neis.go.kr/hub/schoolInfo"


def neis_offices(tpl, regions=None):
    """{지역명: 교육청코드}. 템플릿 neis.offices에서 regions(예: ["서울", "경기"])만 고른다."""
    offices = tpl["neis"].get("offices") or {"서울": tpl["neis"]["office"]}
    if regions:
        unknown = [r for r in regions if r not in offices]
        if unknown:
            raise SystemExit("알 수 없는 지역 %s — sources.json 학교 템플릿의 neis.offices에 추가하세요 (가능: %s)"
                             % (unknown, ", ".join(offices)))
        offices = {r: offices[r] for r in regions}
    return offices


def load_schools(tpl, csv_path=None, kinds=None, regions=None):
    """학교 목록 [{code,name,kind,office,region,homepage}].
    CSV가 있으면 CSV, 없으면 나이스 교육정보 개방 포털 API(NEIS_API_KEY)로 지역(교육청)별로 받는다."""
    kinds = kinds or tpl["neis"]["kinds"]
    offices = neis_offices(tpl, regions)
    region_of = {code: name for name, code in offices.items()}
    if csv_path:
        pick = lambda row, *keys: next((row[k].strip() for k in keys if row.get(k)), "")
        all_offices = neis_offices(tpl)  # 지역명→코드 조회는 필터 전 전체 표로
        default_office = next(iter(all_offices.values()))
        with open(csv_path, encoding="utf-8-sig") as f:
            rows = []
            for r in csv.DictReader(f):
                off = pick(r, "office", "ATPT_OFCDC_SC_CODE", "시도교육청코드")
                reg = pick(r, "region", "시도", "지역")
                off = off or all_offices.get(reg) or (None if reg else default_office)
                rows.append({"code": pick(r, "code", "SD_SCHUL_CODE", "표준학교코드", "학교코드"),
                             "name": pick(r, "name", "SCHUL_NM", "학교명"),
                             "kind": pick(r, "kind", "SCHUL_KND_SC_NM", "학교종류명", "학교급"),
                             "office": off, "region": region_of.get(off, reg),
                             "homepage": pick(r, "homepage", "HMPG_ADRES", "홈페이지주소", "홈페이지")})
        return [r for r in rows if r["code"] and r["kind"] in kinds and r["office"] in region_of]
    key = os.environ.get("NEIS_API_KEY")
    if not key:
        raise SystemExit("NEIS_API_KEY가 없습니다. https://open.neis.go.kr 에서 무료 인증키를 받아 "
                         "export NEIS_API_KEY=... 후 다시 실행하거나 --school-csv로 학교 목록을 주세요.")
    rows = []
    for region, office in offices.items():
        for kind in kinds:
            page = 1
            while True:
                q = urllib.parse.urlencode({"KEY": key, "Type": "json", "pIndex": page, "pSize": 1000,
                                            "ATPT_OFCDC_SC_CODE": office, "SCHUL_KND_SC_NM": kind})
                with urllib.request.urlopen(NEIS_URL + "?" + q, timeout=30) as r:
                    data = json.loads(r.read().decode("utf-8"))
                if "schoolInfo" not in data:  # 결과 없음/오류는 {"RESULT": {...}}
                    msg = data.get("RESULT", {}).get("MESSAGE", "")
                    if page == 1 and msg and "데이터가 없습니다" not in msg:
                        raise SystemExit("나이스 API 오류: %s" % msg)
                    break
                chunk = data["schoolInfo"][1]["row"]
                rows += [{"code": x["SD_SCHUL_CODE"], "name": x["SCHUL_NM"], "kind": x["SCHUL_KND_SC_NM"],
                          "office": x["ATPT_OFCDC_SC_CODE"], "region": region,
                          "homepage": (x.get("HMPG_ADRES") or "").strip()} for x in chunk]
                if len(chunk) < 1000:
                    break
                page += 1
        log("학교 목록: %s(%s) %d곳" % (region, office, sum(1 for r in rows if r["office"] == office)))
    return rows


def normalize_homepage(url):
    url = (url or "").strip()
    if not url or url in ("-", "없음"):
        return None
    if not re.match(r"https?://", url, re.I):
        url = "http://" + url
    return url if urllib.parse.urlsplit(url).netloc else None


def school_sources(tpl, schools):
    """학교마다 출처 설정 하나씩 만든다 (템플릿의 탐색 규칙 + 학교 홈페이지)."""
    srcs = []
    for s in schools:
        home = normalize_homepage(s["homepage"])
        if not home:
            continue
        host = urllib.parse.urlsplit(home).netloc.lower()
        bare = host[4:] if host.startswith("www.") else host
        src = {k: v for k, v in tpl.items() if k not in ("type", "neis", "_comment")}
        src.update({"id": "kr_school_%s" % s["code"], "org": s["name"],
                    "exam": "%s %s 정기고사(중간·기말) 기출" % (s.get("region", ""), s["kind"]), "seeds": [home],
                    "allow_domains": sorted({host, bare, "www." + bare} | set(tpl.get("extra_domains", [])))})
        s["homepage"] = home
        s["source_id"] = src["id"]
        srcs.append(src)
    return srcs


# ---------------------------------------------------------------- report

def status(conn):
    rows = conn.execute(
        "SELECT s.country, s.id, "
        "SUM(d.status='found'), SUM(d.status='ok'), SUM(d.status='dup'), SUM(d.status='error'), SUM(d.status='skipped'), "
        "ROUND(SUM(CASE WHEN d.status='ok' THEN d.bytes ELSE 0 END)/1048576.0,1), SUM(d.text_status='ok') "
        "FROM ref_sources s LEFT JOIN ref_docs d ON d.source_id=s.id GROUP BY s.id ORDER BY s.country, s.id").fetchall()
    print("%-5s %-34s %6s %6s %5s %6s %6s %9s %6s" % ("나라", "출처", "대기", "완료", "중복", "오류", "건너뜀", "MB", "본문"))
    for r in rows:
        if not r[1].startswith("kr_school_"):
            print("%-5s %-34s %6s %6s %5s %6s %6s %9s %6s" % tuple("-" if v is None else v for v in r))
    sch = [r for r in rows if r[1].startswith("kr_school_")]
    if sch:
        tot = [sum(r[i] or 0 for r in sch) for i in range(2, 9)]
        print("%-5s %-34s %6s %6s %5s %6s %6s %9.1f %6s" % (("한국", "학교별 기출 (%d개교, 자료 있는 곳 %d)"
              % (len(sch), sum(1 for r in sch if (r[3] or 0) > 0))) + tuple(tot)))
        print("  학교별 상세: --status --schools-detail")


def schools_detail(conn):
    rows = conn.execute(
        "SELECT sc.office, sc.kind, sc.name, COUNT(d.id), SUM(d.status='ok'), SUM(d.status='error'), sc.homepage "
        "FROM ref_schools sc LEFT JOIN ref_docs d ON d.source_id=sc.source_id GROUP BY sc.code "
        "ORDER BY SUM(d.status='ok') DESC, sc.office, sc.kind, sc.name").fetchall()
    for office, kind, name, found, ok, err, home in rows:
        print("%-4s %-5s %-20s 발견 %4d  완료 %4s  오류 %4s  %s" % (office, kind, name, found, ok or 0, err or 0, home))


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
    ap.add_argument("--schools", action="store_true", help="중·고등학교 홈페이지별 정기고사 기출 수집 모드 (서울·경기)")
    ap.add_argument("--school-csv", help="학교 목록 CSV (code,name,kind,homepage 또는 나이스 컬럼명). 없으면 나이스 API")
    ap.add_argument("--region", nargs="+", help="학교 지역 (서울 경기 …, 기본: 학교 템플릿의 전체 지역)")
    ap.add_argument("--school-kind", nargs="+", help="중학교 / 고등학교 중 일부만")
    ap.add_argument("--school-name", nargs="+", help="학교 이름에 이 글자가 들어간 곳만 (시험 삼아 몇 곳만 돌릴 때)")
    ap.add_argument("--limit-schools", type=int, help="앞에서부터 N개 학교만")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--schools-detail", action="store_true", help="--status와 함께: 학교별 현황")
    ap.add_argument("--search")
    args = ap.parse_args(argv)

    cfg = json.loads(SOURCES.read_text(encoding="utf-8"))
    conn = open_db(args.out)
    if args.status:
        return schools_detail(conn) if args.schools_detail else status(conn)
    if args.search:
        return search(conn, args.search)

    if args.schools:
        tpl = next(s for s in cfg["sources"] if s.get("type") == "school_template")
        schools = load_schools(tpl, args.school_csv, args.school_kind, args.region)
        if args.school_name:
            schools = [s for s in schools if any(n in s["name"] for n in args.school_name)]
        schools = schools[:args.limit_schools] if args.limit_schools else schools
        srcs = school_sources(tpl, schools)
        for s in schools:
            db(conn, "INSERT OR REPLACE INTO ref_schools(code,name,kind,office,homepage,source_id) VALUES (?,?,?,?,?,?)",
               (s["code"], s["name"], s["kind"], s["office"], s["homepage"], s.get("source_id")))
        log("학교 %d곳 (홈페이지 있는 곳 %d) — 지역 %s" % (len(schools), len(srcs),
            ", ".join(sorted({s.get("region") or s["office"] for s in schools}))))
    else:
        srcs = [s for s in cfg["sources"] if s.get("type") != "school_template" and
                (args.all or s.get("enabled", True) or (args.sources and s["id"] in args.sources))]
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
                discover(conn, http, src, args.out)
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
