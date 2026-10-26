# -*- coding: utf-8 -*-
"""10장 실습 4: float32와 float64의 차이. 같은 점들로 거리 행렬을 두 정밀도로 계산해 차이를 잰다(CPU, numpy)."""
import importlib.util, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('xpd', os.path.join(HERE, 'xp-demo-v1.py'))
xpd = importlib.util.module_from_spec(spec); spec.loader.exec_module(xpd)
print('float32: 가수 비트 24개, 기계 입실론 %.3e / float64: 기계 입실론 %.3e' % (np.finfo(np.float32).eps, np.finfo(np.float64).eps))
lon2 = [128 + 3 / 60, 128 + 12 / 60]; lat2 = [44 + 6 / 60, 43 + 22 / 60]
for dt in ('float64', 'float32'):
    d = xpd.haversine_matrix(np, lon2, lat2, dtype=dt)
    print('노백산-돈화 %s: %.6f km (dtype 결과 %s)' % (dt, float(d[0, 1]), d.dtype))
for N in (1000, 4000):
    rng = np.random.default_rng(N)
    lon = rng.uniform(100, 130, N); lat = rng.uniform(30, 50, N)
    d64 = xpd.haversine_matrix(np, lon, lat, dtype='float64'); d32 = xpd.haversine_matrix(np, lon, lat, dtype='float32')
    err = np.abs(d64 - d32.astype(np.float64))
    print('N=%d 두 정밀도의 차이: 최대 %.4f km, 평균 %.5f km' % (N, err.max(), err.mean()))
# 가까운 두 점(약 1 m 떨어짐)에서의 상대 오차
lon = [128.0, 128.0 + 1.0e-5]; lat = [44.0, 44.0]
for dt in ('float64', 'float32'):
    d = xpd.haversine_matrix(np, lon, lat, dtype=dt)
    print('경도 차 1e-5도(약 0.8 m) %s: %.6f km' % (dt, float(d[0, 1])))
