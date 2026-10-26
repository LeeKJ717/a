# -*- coding: utf-8 -*-
"""6장 실습 6-9b: 몬테카를로 결과(reconstruct-mc.json)를 분할 검증 CE의 사분위로 나눠, 칸마다 앞 세기(1600~1699)의 RE(참값)가 음수인 비율을 센다.
입력: reconstruct-mc.json (reconstruct-mc-v1.py가 만든다). 실행: python3 mc-strata-v1.py | tee mc-strata.log"""
import os, json, platform
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
print('환경: python %s, numpy %s' % (platform.python_version(), np.__version__))
M = json.load(open(os.path.join(HERE, 'reconstruct-mc.json'), encoding='utf-8'))
for b in ('0.085', '0.06'):
    ce = np.array([r['ce'] for r in M[b]])
    re_ = np.array([r['re'] for r in M[b]])
    ret = np.array([r['ret_e'] for r in M[b]])
    rt = np.array([r['rt_e'] for r in M[b]])
    q = np.quantile(ce, [0.25, 0.5, 0.75])
    edges = [-np.inf, q[0], q[1], q[2], np.inf]
    print('\n== 공통 신호 b = %s (되풀이 %d회). 검증 CE(두 방향 중 작은 값)의 사분위 경계 %s' % (b, len(ce), ', '.join('%.3f' % v for v in q)))
    print('  CE의 사분위     되풀이  CE 범위               앞 세기 RE(참값) < 0 의 비율   앞 세기 복원-참값 r의 중앙값')
    for k in range(4):
        sel = (ce > edges[k]) & (ce <= edges[k + 1]) if k > 0 else (ce <= edges[1])
        lo, hi = ce[sel].min(), ce[sel].max()
        print('  %d (%s)        %4d   %6.3f ~ %6.3f      %5.1f%%                       %.3f' % (k + 1, '낮음' if k == 0 else ('높음' if k == 3 else '  중'), sel.sum(), lo, hi, 100 * np.mean(ret[sel] < 0), np.median(rt[sel])))
    top = ce >= 0.7
    print('  참고: 검증 CE가 0.7 이상인 되풀이 %d회 가운데 앞 세기 RE(참값) < 0 은 %d회(%.1f%%)' % (top.sum(), int(np.sum(ret[top] < 0)), 100 * np.mean(ret[top] < 0) if top.sum() else float('nan')))
