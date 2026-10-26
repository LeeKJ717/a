# -*- coding: utf-8 -*-
"""6장 실습 6-0b: 손으로 따라 할 수 있는 크기의 작은 예(시연값). 본문의 "쉬운 예"가 쓰는 숫자를 이 스크립트가 계산한다.
  (1) 지수 = 너비 / 곡선, (2) 이중 가중 평균과 보통 평균, (3) 한 해 어긋난 계열의 lag별 상관, (4) 빠진 테가 날짜를 어긋나게 하는 모습,
  (5) EPS와 필요한 나무 수.
실행: python3 handcalc-v1.py | tee handcalc.log
"""
import os, platform, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
print('환경: python %s, numpy %s' % (platform.python_version(), np.__version__))

print('\n== (1) 지수 = 너비 / 곡선')
w = np.array([1.00, 0.36])
g = np.array([0.80, 0.30])
print('  너비 %s mm, 그 나이에서 기대되는 곡선 값 %s mm -> 지수 %s' % (w, g, np.round(w / g, 3)))

print('\n== (2) 이중 가중 평균(tbrm)과 보통 평균. 같은 해의 지수 6개 중 하나가 이상치')
x = np.array([4.8, 5.1, 5.0, 4.9, 5.2, 20.0])
print('  값 %s' % x)
print('  보통 평균 %.3f, 중앙값 %.3f, 이중 가중 평균 %.3f' % (x.mean(), np.median(x), L.tbrm(x)))
x2 = x[:5]
print('  이상치를 뺀 5개: 보통 평균 %.3f, 이중 가중 평균 %.3f' % (x2.mean(), L.tbrm(x2)))

print('\n== (3) 한 해 어긋난 계열: lag별 상관')
rng = np.random.default_rng(6)
master = rng.normal(0, 1, 40)
true_series = master + rng.normal(0, 0.5, 40)          # 마스터와 같은 해에 같은 방향으로 움직이는 계열(잡음 0.5)
shifted = np.roll(true_series, 1)                       # 날짜가 한 해 늦게 붙은 계열(값이 한 해 뒤 연도에 놓임)
shifted[0] = np.nan
print('  마스터 40년(표준정규 난수, 시드 6), 계열 = 마스터 + 잡음(표준편차 0.5), 날짜가 한 해 늦게 붙은 계열은 값을 한 칸 뒤로 밀어 만듦')
print('  lag   바른 날짜의 계열과 마스터의 상관   한 해 어긋난 계열과 마스터의 상관')
for lag in range(-3, 4):
    out = []
    for s in (true_series, shifted):
        a, b = [], []
        for i in range(40):
            j = i + lag
            if 0 <= j < 40 and not np.isnan(s[i]):
                a.append(s[i]); b.append(master[j])
        out.append(np.corrcoef(a, b)[0, 1])
    print('  %+d     %8.3f                          %8.3f' % (lag, out[0], out[1]))
print('  (lag > 0은 계열의 연도 y가 마스터의 y + lag에 해당한다는 뜻. 어긋난 계열의 최고 상관은 lag = -1에서 나와야 한다)')

print('\n== (4) 빠진 테 한 개가 날짜를 어긋나게 하는 모습 (10개 테의 계열)')
years = np.arange(1991, 2001)
true_w = np.array([0.8, 1.1, 0.9, 1.4, 1.0, 0.7, 1.2, 1.3, 0.9, 1.0])
print('  참 연도 %s' % years.tolist())
print('  참 너비 %s' % true_w.tolist())
miss = 1995
keep = years != miss
meas = true_w[keep]
print('  %d년의 테를 측정에서 놓쳤다. 측정된 테 %d개를 마지막 해(2000)에 맞춰 날짜를 붙이면' % (miss, meas.size))
lab = np.arange(2000 - meas.size + 1, 2001)
for y, v in zip(lab, meas):
    print('    라벨 %d년 = 측정값 %.1f' % (y, v))
print('  %d년보다 오래된 값(참 1991~1994)은 라벨이 한 해씩 늦어진다(1992~1995). 이 오류는 한 계열 안에서는 보이지 않는다.' % miss)

print('\n== (5) EPS = n r / ((n-1) r + 1) 과 EPS 0.85에 필요한 나무 수')
print('  r      n=1    n=2    n=5    n=10   n=20   EPS 0.85에 필요한 n')
for r in (0.1, 0.2, 0.3, 0.5):
    print('  %.1f  ' % r + ' '.join('%6.3f' % L.eps_from_rbar(n, r) for n in (1, 2, 5, 10, 20)) + '   %6.2f' % L.n_for_eps(0.85, r))

print('\n== (6) 50년 구간 하나의 상관은 얼마나 흔들리는가 (자기상관을 무시한 피셔 z 근사, 표본 크기 n = 50)')
from scipy import stats
n = 50
crit = L.crit_r(n, 0.01)
print('  양쪽 1%% 임계 상관(n = %d) = %.3f. 피셔 z = atanh(r)의 표준오차는 1/sqrt(n-3) = %.3f' % (n, crit, 1 / np.sqrt(n - 3)))
print('  참 상관 rho   구간 상관 r의 대략의 범위(95%)   구간 r이 임계값을 넘을 확률')
for rho in (0.15, 0.313, 0.5, 0.881):
    se = 1 / np.sqrt(n - 3)
    lo, hi = np.tanh(np.arctanh(rho) - 1.96 * se), np.tanh(np.arctanh(rho) + 1.96 * se)
    p_over = stats.norm.sf((np.arctanh(crit) - np.arctanh(rho)) / se)
    print('  %.3f         %.3f ~ %.3f                     %.1f%%' % (rho, lo, hi, 100 * p_over))
print('  (참 상관 0.313은 시연값 자료의 계열과 나머지 사이 상관의 중앙값, 0.881은 co021의 중앙값이다. 실제 계열은 자기상관이 있어 이 근사보다 더 흔들린다)')
