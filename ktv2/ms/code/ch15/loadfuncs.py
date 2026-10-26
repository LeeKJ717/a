# -*- coding: utf-8 -*-
"""15장 공용: 앞 장의 스크립트에서 함수 정의만 꺼내 쓴다. 앞 장 파일은 고치지 않고 실행도 하지 않는다.
방법: 파이썬 ast로 소스를 읽어 최상위의 def(함수 정의)만 골라 새 이름 공간에서 실행한다.
함수가 소스의 다른 전역 값(예: rng, lab)을 쓰면 env로 넣어 준다. 이 때문에 "무엇을 넣었는가"가 호출한 쪽 코드에 드러난다."""
import ast, hashlib


def load_funcs(path, names, env=None):
    src = open(path, 'rb').read()
    tree = ast.parse(src.decode('utf-8'))
    want = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    missing = set(names) - {n.name for n in want}
    if missing:
        raise KeyError('%s 에 함수가 없다: %s' % (path, sorted(missing)))
    ns = dict(env or {})
    mod = ast.Module(body=want, type_ignores=[])
    exec(compile(mod, path, 'exec'), ns)
    sha = hashlib.sha256(src).hexdigest()[:16]
    return {n: ns[n] for n in names}, sha
