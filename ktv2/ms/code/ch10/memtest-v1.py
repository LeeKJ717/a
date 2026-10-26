# -*- coding: utf-8 -*-
"""10장 실습 2: 메모리 한계. 같은 계산을 한 번에 하는 경우와 나눠서 하는 경우의 최대 상주 메모리(RSS)를 잰다.
각 경우를 새 파이썬 프로세스에서 돌려 resource.getrusage의 ru_maxrss(리눅스에서 KB)를 읽는다.
이 값은 CPU 메모리(RAM)이며 GPU 메모리가 아니다. GPU에서는 같은 배열 크기 계산이 장치 메모리에 그대로 적용된다."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CHILD = r'''
import sys, resource, importlib.util, numpy as np
spec = importlib.util.spec_from_file_location("xpd", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
kind = sys.argv[2]; a = int(sys.argv[3]); b = int(sys.argv[4])
if kind == "boot":
    h = m.boot_h(np, [1, 3, 1, 2, 2], a, 11, b)
    res = float(np.percentile(h, 50))
elif kind == "hav":
    rng = np.random.default_rng(1)
    lon = rng.uniform(100, 130, a); lat = rng.uniform(30, 50, a)
    d = m.haversine_matrix(np, lon, lat); res = float(d.max())
else:
    res = 0.0
print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, res)
'''
def run(kind, a, b):
    out = subprocess.run([sys.executable, '-I', '-c', CHILD, os.path.join(HERE, 'xp-demo-v1.py'), kind, str(a), str(b)],
                         capture_output=True, text=True, check=True).stdout.split()
    return int(out[0]) / 1024.0, float(out[1])      # MiB
base, _ = run('none', 0, 0)
print('기준: numpy를 읽기만 한 파이썬 프로세스의 최대 RSS = %.1f MiB' % base)
print()
print('부트스트랩 B=4,000,000 (n=9, k=5): chunk를 바꿔 본다')
print('%-12s %-14s %-14s' % ('chunk', '최대 RSS MiB', '기준 대비 MiB'))
for ch in (4000000, 1000000, 200000, 50000):
    r, med = run('boot', 4000000, ch)
    print('%-12d %-14.1f %-14.1f' % (ch, r, r - base))
print()
print('하버사인 N x N 거리 행렬 (float64): 행렬 하나의 크기 8 N^2 바이트와 실측 비교')
print('%-8s %-16s %-14s %-12s' % ('N', '행렬 하나 MiB', '실측 증가 MiB', '배율'))
for N in (1000, 2000, 4000, 8000):
    r, mx = run('hav', N, 0)
    one = 8 * N * N / 2**20
    print('%-8d %-16.1f %-14.1f %-12.2f' % (N, one, r - base, (r - base) / one))
