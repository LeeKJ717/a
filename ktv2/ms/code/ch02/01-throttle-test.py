# -*- coding: utf-8 -*-
"""실습 2-2: 요청 속도 제한기와 429 처리를 가짜 서버로 시험한다. 실행: python3 01-throttle-test.py | tee 01-throttle-test.log
가짜 서버는 직전 요청과 0.20초 안에 오면 429를 돌려준다(시험용으로 정한 값)."""
import json, os, statistics, time
import apiclient, fakeserver

os.environ['NO_PROXY'] = '127.0.0.1'
srv = fakeserver.Fake(min_gap=0.20).start()
base = 'http://127.0.0.1:%d' % srv.port
dois = ['10.9999/demo.001', '10.9999/demo.002', '10.9999/demo.004', '10.9999/demo.005', '10.9999/demo.009'] * 2   # 10건, 마지막 둘은 없는 DOI


def run(name, interval, backoff0):
    time.sleep(1.0); srv.log.clear(); srv.last = None   # 앞 시험의 마지막 요청과 붙지 않게 쉰다
    cl = apiclient.Client(base + '/openalex', min_interval=interval, backoff0=backoff0, max_retries=6)
    cl.s.trust_env = False                      # 프록시를 거치지 않는다(localhost)
    t0 = time.monotonic()
    ok = miss = 0
    for d in dois:
        r = apiclient.openalex_by_doi(cl, d)
        ok += r is not None; miss += r is None
    el = time.monotonic() - t0
    time.sleep(0.1)                              # 서버가 마지막 요청을 기록할 시간
    codes = [c for _, _, c in srv.log]
    ts = [t - srv.log[0][0] for t, _, _ in srv.log]
    gaps = [b - a for a, b in zip(ts, ts[1:])]
    print('%-24s 요청 %d회(서버가 받은 것) 200=%d 404=%d 429=%d | 클라이언트 429 %d회 | 걸린 시간 %.2f초 | 최소 간격 %.3f초'
          % (name, len(codes), codes.count(200), codes.count(404), codes.count(429), cl.n429, el, min(gaps)))
    return dict(name=name, interval=interval, t=ts, codes=codes, elapsed=el, n429=cl.n429, ok=ok, miss=miss)


res = [run('간격 없음(0초)', 0.0, 0.25), run('정중한 간격(0.30초)', 0.30, 0.25)]
json.dump(res, open('out/throttle-result.json', 'w'), ensure_ascii=False)

# 403 시험: 다시 시도하지 않고 멈추는가
time.sleep(1.0); srv.log.clear(); srv.last = None
cl = apiclient.Client(base, min_interval=0.3)
cl.s.trust_env = False
try:
    cl.get('/blocked')
    print('403: 예외 없음(오류)')
except RuntimeError as e:
    time.sleep(0.1)
    print('403: 예외로 멈춤. 서버가 받은 요청 %d회. 메시지 앞부분: %s' % (len(srv.log), str(e)[:40]))

# 키/연락처가 다른 서버로 새지 않는가
time.sleep(1.0); srv.last = None
cl = apiclient.Client(base + '/crossref', min_interval=0.3, params={'mailto': 'me@example.org', 'api_key': 'SECRET'})
cl.s.trust_env = False
seen = []
orig = cl.s.get
def spy(url, params=None, timeout=None):
    seen.append((url, dict(params or {})))
    return orig(url, params=params, timeout=timeout)
cl.s.get = spy
cl.get('/works/10.9999/demo.003')
cl.get('http://127.0.0.1:%d/pdf/demo001.pdf' % srv.port, raw=True)
for u, p in seen:
    print('  요청 %-52s 보낸 매개변수 %s' % (u.split('%d' % srv.port)[1], sorted(p)))
srv.stop()
