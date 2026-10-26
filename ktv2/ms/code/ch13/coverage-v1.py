# -*- coding: utf-8 -*-
"""원문이 넓을수록 '원문에 있는 숫자' 점검이 약해진다. 그 정도를 센다.
원문 대역(11.3절)과 11장 전체에서, 한 자리·두 자리·세 자리 정수가 숫자 토큰으로 몇 개나 나오는지 센다."""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hc', os.path.join(HERE, 'halluccheck-v1.py'))
hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)
for nm, fn in (('11.3절(원문 대역)', 'vol1-ch11-sec3-v1.md'), ('11장 전체', 'vol1-ch11-v1.md')):
    lines = hc.read_lines(os.path.join(HERE, 'input', fn))
    toks = hc.extract_numbers(lines, skip_meta=False)
    ints = {int(v) for (_, v, raw, u, d) in toks if d == 0 and v == int(v) and v >= 0}
    all_vals = {v for (_, v, raw, u, d) in toks}
    n1 = sum(1 for k in range(1, 10) if k in ints)
    n2 = sum(1 for k in range(10, 100) if k in ints)
    n3 = sum(1 for k in range(100, 1000) if k in ints)
    print('%-18s 숫자 토큰 %5d개, 서로 다른 값 %4d개 | 한 자리 정수 %d/9, 두 자리 정수 %d/90 (%.0f%%), 세 자리 정수 %d/900 (%.0f%%)' % (nm, len(toks), len(all_vals), n1, n2, 100.0 * n2 / 90, n3, 100.0 * n3 / 900))
