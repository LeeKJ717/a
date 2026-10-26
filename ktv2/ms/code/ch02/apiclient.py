# -*- coding: utf-8 -*-
"""apiclient v1 (제2권 2장): 논문 검색 API를 정중하게 부르는 클라이언트.
상태: 실행 확인 필요(z840에서 실행). 이 컨테이너에서는 실제 서버에 접속하지 못했고,
같은 코드를 로컬의 가짜 서버(fakeserver.py) 상대로만 실행해 보았다(실습 2-2, 2-3).

원칙: (1) 요청 사이에 최소 간격을 둔다. (2) 한 번에 한 요청(동시 요청 없음). (3) 연락처를 알린다.
(4) 429는 기다렸다 다시 한다. (5) 403은 다시 하지 않고 멈춘다(차단일 수 있다). (6) 이미 받은 것은 다시 받지 않는다."""
import json, os, random, time
from urllib.parse import urlparse
import requests

CONTACT = os.environ.get('KTV_CONTACT', 'contact@example.org')   # 실제 이메일로 바꾼다(환경 변수)
UA = 'ktvdb-harvester/1.0 (mailto:%s)' % CONTACT


class Throttle:
    """직전 요청과 최소 간격(초)을 지킨다. 단일 스레드용."""
    def __init__(self, min_interval):
        self.min_interval = min_interval
        self._last = None

    def wait(self):
        now = time.monotonic()
        if self._last is not None:
            gap = self.min_interval - (now - self._last)
            if gap > 0:
                time.sleep(gap)
        self._last = time.monotonic()


class Client:
    def __init__(self, base, min_interval=1.5, max_retries=4, backoff0=1.0, timeout=30, params=None, session=None, log=None):
        self.base, self.min_interval = base.rstrip('/'), min_interval
        self.ths = {}                                   # 서버(호스트)마다 따로 간격을 잰다
        self.max_retries, self.backoff0, self.timeout = max_retries, backoff0, timeout
        self.params = dict(params or {})
        self.s = session or requests.Session()
        self.s.headers['User-Agent'] = UA
        self.log = log if log is not None else []     # (시각, 주소, 상태, 바이트, 메모)
        self.n429 = 0

    def get(self, path, params=None, raw=False):
        url = path if path.startswith('http') else self.base + path
        th = self.ths.setdefault(urlparse(url).netloc, Throttle(self.min_interval))
        q = dict(self.params) if url.startswith(self.base) else {}   # api_key와 mailto는 다른 서버(출판사)로 새지 않게 한다
        q.update(params or {})
        for attempt in range(self.max_retries + 1):
            th.wait()
            t = time.monotonic()
            r = self.s.get(url, params=q, timeout=self.timeout)
            self.log.append((t, path, r.status_code, len(r.content), 'try%d' % attempt))
            if r.status_code == 200:
                return r if raw else r.json()
            if r.status_code == 403:
                raise RuntimeError('403: 차단일 수 있다. 다시 시도하지 말고 연락처와 요청 속도를 점검한다: ' + url)
            if r.status_code == 404:
                return None
            if r.status_code == 429 or r.status_code >= 500:
                self.n429 += (r.status_code == 429)
                ra = r.headers.get('Retry-After')              # 일반적인 HTTP 머리말. 두 API 문서에서는 확인하지 못했다
                wait = float(ra) if ra and ra.replace('.', '', 1).isdigit() else self.backoff0 * 2 ** attempt
                time.sleep(wait * (0.8 + 0.4 * random.random()))
                continue
            r.raise_for_status()
        raise RuntimeError('재시도 한도 초과: ' + url)


# ---- 두 서비스용 얇은 껍질. 주소 모양은 공식 문서에서 읽은 것(2.2절)
def openalex_by_doi(cl, doi):
    """GET /works/doi:{doi}  (문서: 'GET /works/doi:10.7717/peerj.4375')"""
    return cl.get('/works/doi:' + doi)


def openalex_list(cl, filt, per_page=100, max_pages=3, select=None):
    """GET /works?filter=...&per_page=...&page=n. 기본 쪽 넘김은 10,000건까지(문서). 깊은 쪽 넘김(cursor)은 쓰지 않는다."""
    out = []
    for page in range(1, max_pages + 1):
        p = {'filter': filt, 'per_page': per_page, 'page': page}
        if select:
            p['select'] = select
        j = cl.get('/works', p)
        res = (j or {}).get('results', [])
        out += res
        if len(res) < per_page:
            break
    return out


def crossref_by_doi(cl, doi):
    """GET /works/{doi}. 연락처는 mailto 매개변수로(문서: polite pool)."""
    return cl.get('/works/' + doi)


def download_pdf(cl, url, dest):
    """오픈 액세스 PDF를 받는다. 받은 바이트가 '%PDF-'로 시작하지 않으면(랜딩 페이지 HTML 등) 버린다."""
    r = cl.get(url, raw=True)
    if r is None:
        return None, '404'
    if not r.content.startswith(b'%PDF-'):
        return None, 'PDF가 아님(첫 바이트 %r, 형식 %s)' % (r.content[:8], r.headers.get('Content-Type'))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        f.write(r.content)
    return dest, 'ok'
