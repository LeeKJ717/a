# -*- coding: utf-8 -*-
"""11장 실습 11-4b: cupy의 난수 API를 설치본의 설명문(docstring)에서 읽는다. GPU가 없어도 읽을 수 있는 정보만 적는다.
사용: (cupy를 설치한 가상환경의 파이썬으로) python p04b-cupy-api-v1.py"""
import sys
import cupy as cp
print('python', sys.version.split()[0], '| cupy', cp.__version__)
G = cp.random.Generator
print('Generator의 공개 메서드:', [m for m in dir(G) if not m.startswith('_')])
for m in ('integers', 'random', 'standard_normal', 'uniform', 'hypergeometric', 'normal', 'permutation', 'shuffle', 'choice'):
    print('  Generator.%-16s %s' % (m, '있음' if hasattr(G, m) else '없음'))
print('비트 생성기 클래스:', [x for x in dir(cp.random) if x[0].isupper() and x not in ('RandomState',)], '(+ BitGenerator의 하위 클래스)')
print('default_rng 설명 첫 줄:', cp.random.default_rng.__doc__.strip().splitlines()[0])
print('Generator 설명 중 호환성 문구:', [l.strip() for l in G.__doc__.splitlines() if 'Compatibility' in l or 'bit stream' in l or 'version compatibility' in l])
for n in ('argsort', 'sort', 'take_along_axis', 'searchsorted', 'histogram', 'percentile', 'cumsum', 'sqrt', 'arcsin', 'radians'):
    print('  cupy.%-16s %s' % (n, '있음' if hasattr(cp, n) else '없음'))
try:
    g = cp.random.default_rng(11)
    print('default_rng(11) 생성 성공:', type(g).__name__)
except Exception as e:
    print('default_rng(11) 생성 실패(GPU 없음):', type(e).__name__, str(e).splitlines()[0])
