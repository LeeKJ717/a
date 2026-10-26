# -*- coding: utf-8 -*-
"""로컬 언어 모델(Ollama 서버)로 논문 원문에서 주장을 추출하고, 그 결과를 환각 점검기로 점검한다.
표준 라이브러리만 쓴다.

*** z840 실행 필요. 이 컨테이너에는 모델 가중치가 없어 이 파일의 모델 호출은 실행하지 못했다. ***
이 컨테이너에서 한 것: 문법 검사(py_compile), --dry-run(요청 본문만 만들어 보임, 서버에 접속하지 않음),
서버가 없을 때의 실패 경로(연결 거부). 모델의 응답을 받는 경로(응답 해석)는 한 번도 실행하지 못했다.

엔드포인트와 필드의 근거: POST /api/chat, 기본 포트 11434, 요청 필드 model, messages(각 role, content), stream 은
제3자 글(Geshan, 2025)에서 읽었다. options(temperature, seed, num_ctx) 필드의 이름과 응답의 message.content 위치는
이 책이 공식 문서에서 확인하지 못했다. z840 에서 서버의 응답으로 확인해야 한다(확인 필요).

사용 예(z840):
  python llm-client-v1.py --model <모델이름> --source 원문.md --out run1 --runs 2
  python halluccheck-v1.py diffruns run1/output-1.md run1/output-2.md
"""
import argparse, hashlib, importlib.util, json, os, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM = (
    '너는 논문 원문에서 주장과 숫자를 옮겨 적는 도구이다. 원문에 없는 내용을 더하지 않는다. '
    '규칙: (1) 한 줄에 주장 하나만 쓴다. (2) 원문 문장을 그대로 옮길 때는 큰따옴표 안에 한 글자도 바꾸지 말고 쓴다. '
    '(3) 숫자는 원문에 적힌 그대로 쓰고 단위를 붙인다. (4) 원문에 없는 값을 계산해 쓸 때는 줄 끝에 [계산] 을 붙이고 식을 함께 쓴다. '
    '(5) 표는 마크다운 표로 쓰고 합계 줄은 첫 칸을 합계로 쓴다. (6) 원문에 없으면 "원문에 없음"이라고 쓴다.'
)


def build_payload(model, source_text, task, temperature, seed, num_ctx):
    user = '다음 원문에서 %s\n\n--- 원문 시작 ---\n%s\n--- 원문 끝 ---' % (task, source_text)
    return {
        'model': model,
        'stream': False,
        'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}],
        'options': {'temperature': temperature, 'seed': seed, 'num_ctx': num_ctx},
    }


def call_ollama(host, payload, timeout):
    req = urllib.request.Request(host.rstrip('/') + '/api/chat', data=json.dumps(payload).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def load_checker():
    spec = importlib.util.spec_from_file_location('hc', os.path.join(HERE, 'halluccheck-v1.py'))
    hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)
    return hc


def main(argv=None):
    ap = argparse.ArgumentParser(description='로컬 언어 모델로 원문에서 주장을 추출하고 점검한다')
    ap.add_argument('--model', required=True, help='Ollama 에 내려받아 둔 모델 이름(이 책은 특정 모델을 권하지 않는다)')
    ap.add_argument('--source', required=True, help='원문(마크다운 또는 텍스트) 경로')
    ap.add_argument('--task', default='시료 수의 흐름, 표, 그리고 본문이 직접 쓴 주장을 규칙에 맞게 옮겨 써라.')
    ap.add_argument('--host', default='http://127.0.0.1:11434')
    ap.add_argument('--temperature', type=float, default=0.0)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--num-ctx', type=int, default=8192)
    ap.add_argument('--timeout', type=float, default=600.0)
    ap.add_argument('--runs', type=int, default=1, help='같은 입력으로 되풀이할 횟수(2 이상이면 diffruns 로 견준다)')
    ap.add_argument('--out', default='run')
    ap.add_argument('--dry-run', action='store_true', help='요청 본문만 출력하고 서버에 접속하지 않는다')
    a = ap.parse_args(argv)

    src = open(a.source, encoding='utf-8').read()
    payload = build_payload(a.model, src, a.task, a.temperature, a.seed, a.num_ctx)
    meta = {
        'model': a.model, 'host': a.host, 'temperature': a.temperature, 'seed': a.seed, 'num_ctx': a.num_ctx,
        'source_sha256': hashlib.sha256(src.encode('utf-8')).hexdigest(),
        'payload_sha256': hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest(),
    }
    if a.dry_run:
        shown = dict(payload); shown['messages'] = [dict(m, content=m['content'][:200] + ('…(%d자 중 앞 200자)' % len(m['content']) if len(m['content']) > 200 else '')) for m in payload['messages']]
        print(json.dumps({'meta': meta, 'payload(축약)': shown}, ensure_ascii=False, indent=1))
        return 0

    os.makedirs(a.out, exist_ok=True)
    hc = load_checker()
    srclines = hc.read_lines(a.source)
    worst = 0
    for k in range(1, a.runs + 1):
        t0 = time.time()
        try:
            resp = call_ollama(a.host, payload, a.timeout)
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            print('서버에 연결하지 못했다: %s (%s)' % (a.host, type(e).__name__), file=sys.stderr)
            print('Ollama 서버가 떠 있고 모델 "%s" 이 내려받아져 있는지 확인한다.' % a.model, file=sys.stderr)
            return 2
        dt = time.time() - t0
        try:
            text = resp['message']['content']
        except (KeyError, TypeError):
            print('응답에서 message.content 를 찾지 못했다. 응답의 키: %s (확인 필요)' % (list(resp)[:10] if isinstance(resp, dict) else type(resp)), file=sys.stderr)
            return 3
        outp = os.path.join(a.out, 'output-%d.md' % k)
        open(outp, 'w', encoding='utf-8').write(text if text.endswith('\n') else text + '\n')
        json.dump({'meta': meta, 'seconds': round(dt, 2), 'raw_keys': list(resp)}, open(os.path.join(a.out, 'meta-%d.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        stats = {}
        f = hc.run_verify(hc.read_lines(outp), srclines, stats)
        hc.report(f, stats, '실행 %d (%.1f초) %s' % (k, dt, outp))
        worst = max(worst, 1 if f else 0)
    return worst


if __name__ == '__main__':
    sys.exit(main())
