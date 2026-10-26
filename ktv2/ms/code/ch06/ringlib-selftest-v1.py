# -*- coding: utf-8 -*-
"""6장 실습 6-0: ringlib-v1.py의 자체 점검. dplR 없이 확인할 수 있는 것만 본다(dplR와의 대조는 compare-dplr-v1.py).
실행: python3 ringlib-selftest-v1.py | tee ringlib-selftest.log"""
import os, platform, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
print('환경: python %s, numpy %s' % (platform.python_version(), np.__version__))
ok_all = True
def chk(name, cond, detail=''):
    global ok_all
    ok_all &= bool(cond)
    print('  [%s] %s %s' % ('통과' if cond else '실패', name, detail))

rng = np.random.default_rng(1)
print('1. 평활 스플라인의 주파수 반응')
n = 2000
t = np.arange(n)
for per in (50, 100, 200):
    y = np.sin(2 * np.pi * t / per)
    g = L.caps(y, nyrs=per)
    mid = slice(n // 4, 3 * n // 4)
    amp = np.sqrt(2 * np.mean(g[mid] ** 2))
    chk('파장 %d년 사인파, nyrs=%d: 곡선의 진폭 비 = %.3f (기대 0.5)' % (per, per, amp), abs(amp - 0.5) < 0.02)
y = 3.0 + 0.02 * t[:300]
g = L.caps(y, nyrs=100)
chk('직선은 그대로 따라간다(최대 차이 %.2e)' % np.abs(g - y).max(), np.abs(g - y).max() < 1e-8)

print('2. 이중 가중 평균')
x = np.array([5.0, 5.1, 4.9, 5.0, 5.2, 4.8, 20.0])
chk('이상치 하나(20.0)가 있어도 이중 가중 평균 %.3f는 5 근처, 보통 평균 %.3f' % (L.tbrm(x), x.mean()), abs(L.tbrm(x) - 5.0) < 0.1)

print('3. AR 사전 백색화')
phi = 0.7
z = np.zeros(5000)
e = rng.normal(0, 1, 5000)
for i in range(1, 5000):
    z[i] = phi * z[i - 1] + e[i]
res, xm, order, ar = L.ar_yw(z)
chk('AR(1) 자료에서 선택된 차수 %d, 계수 %.3f (참 0.7)' % (order, ar[0]), order >= 1 and abs(ar[0] - phi) < 0.05)
chk('잔차의 1차 자기상관 %.3f (0에 가까워야 함)' % L.acf1(res[~np.isnan(res)]), abs(L.acf1(res[~np.isnan(res)])) < 0.05)

print('4. 날짜 오류 만들기와 고치기의 왕복')
years = np.arange(1700, 2014)
col = np.full(len(years), np.nan)
col[20:] = rng.uniform(0.5, 2.0, len(years) - 20)
c = L.corrupt_shift(col, 3); r = L.repair_shift(c, 3)
both = ~np.isnan(r) & ~np.isnan(col)
chk('통째 어긋남: 고친 뒤 겹친 %d해가 모두 같다' % both.sum(), np.allclose(r[both], col[both]))
c = L.corrupt_missing(col, years, 1850); r = L.repair_missing(c, years, 1850)
d = np.abs(r - col); d[np.isnan(d)] = 0
chk('빠진 테: 고친 뒤 차이가 큰 해는 끼운 1850년뿐(%d개)' % int(np.sum(d > 1e-12)), np.sum(d > 1e-12) == 1 and d[1850 - 1700] > 0)
c = L.corrupt_false(col, years, 1790); r = L.repair_false(c, years, 1790)
d = np.abs(r - col); d[np.isnan(d)] = 0
chk('거짓 테: 고친 뒤 값이 같다(최대 차이 %.1e)' % d.max(), d.max() < 1e-12)

print('5. Tucson 형식 왕복(끝 표시 -9999 형식에 999 값이 들어 있는 경우 포함)')
X = np.full((40, 2), np.nan)
X[:, 0] = np.round(rng.uniform(0.3, 2.0, 40), 3)
X[5, 0] = 0.999
X[3:, 1] = np.round(rng.uniform(0.3, 2.0, 37), 3)
p = os.path.join(HERE, 'work', 'selftest.rwl')
os.makedirs(os.path.dirname(p), exist_ok=True)
L.write_rwl(p, np.arange(1901, 1941), ['S1', 'S2'], X)
y2, n2, X2 = L.read_rwl(p)
chk('0.999 mm 값이 끝 표시로 오인되지 않고 왕복한다', np.allclose(np.nan_to_num(X2), np.nan_to_num(X), atol=1e-9) and y2[0] == 1901 and n2 == ['S1', 'S2'])
print('전체: %s' % ('모두 통과' if ok_all else '실패가 있다'))
