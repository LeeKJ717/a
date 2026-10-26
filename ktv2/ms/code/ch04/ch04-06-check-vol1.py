# -*- coding: utf-8 -*-
"""4장 점검: 제1권 계산과 이 장의 계산이 맞는가
제1권 계산 스크립트(ch02, ch10, ch11)를 실행해 출력한 값을 읽고, 이 장의 도구(scipy, statsmodels)로 다시 계산한 값과 견준다.
임계 상관은 제1권과 다른 경로(상관계수의 귀무분포 = 베타분포)로 구한다.
실행: python3 ch04-06-check-vol1.py   (먼저 ch04-03을 실행해 results/ch04-03.json이 있어야 모의 판정을 읽는다)
"""
import re, subprocess, json, os, time, platform, sys
import numpy as np, scipy, scipy.signal as ss, scipy.fft as sf
from scipy import stats
from numpy.lib.stride_tricks import sliding_window_view

V1 = '/home/claude/book/ms'
print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
def run(name):
    r = subprocess.run([sys.executable, '-I', os.path.join(V1, name)], capture_output=True, text=True, cwd=V1, timeout=300)
    return r.stdout
o11, o10, o02 = run('ch11-calc-v1.py'), run('ch10-calc-v1.py'), run('ch02-calc-v1.py')
rows = []
def add(item, v1, mine, tol, note=''):
    ok = abs(v1 - mine) <= tol
    rows.append((item, v1, mine, ok, note))
    print('  %-52s 제1권 %-10s 이 장 %-10s %s %s' % (item, ('%.5g' % v1), ('%.5g' % mine), '일치' if ok else '차이', note))

# ---- 계산 11-9: 임계 상관(제1권 스크립트 출력 대 베타분포 경로)
print('\n[계산 11-9] 임계 상관, 베타분포 경로')
def rcrit_beta(n, a):
    d = stats.beta(n / 2 - 1, n / 2 - 1, loc=-1, scale=2)
    return d.isf(a / 2)
for n in (57, 100, 130, 414):
    m = re.search(r'n=\s*%d 임계 r \(양쪽 0\.05\) = ([\d.]+) , \(0\.01\) = ([\d.]+)' % n, o11)
    add('n=%d 5%% 임계 r' % n, float(m.group(1)), rcrit_beta(n, .05), 0.0006)
    add('n=%d 1%% 임계 r' % n, float(m.group(2)), rcrit_beta(n, .01), 0.0006)
m = re.search(r'1차 차분 상관 r=0.12, n=57: t = ([\d.]+), p = ([\d.]+)', o11)
p_beta = 2 * stats.beta(57 / 2 - 1, 57 / 2 - 1, loc=-1, scale=2).sf(0.12)
add('차분 r=0.12, n=57의 양쪽 p', float(m.group(2)), p_beta, 0.0006)
m = re.search(r'독립이면 t = ([\d.]+), p = ([\d.e+-]+)', o11)
p_beta = 2 * stats.beta(414 / 2 - 1, 414 / 2 - 1, loc=-1, scale=2).sf(0.18)
add('r=-0.18, n=414의 양쪽 p (독립 가정)', float(m.group(2)), p_beta, 2e-6)
m = re.search(r'414 × [\d.]+ / [\d.]+ = ([\d.]+)', o11)
rho = 0.72
add('n_eff (rho1=rho2=0.72, n=414)', float(m.group(1)), 414 * (1 - rho * rho) / (1 + rho * rho), 0.06)

# ---- 한 계열만 0.72: 제1권의 67.4와 모의
print('\n[계산 11-9 한 계열만 0.72] 제1권의 67.4와 쌍 공식, 모의')
m = re.search(r'한 계열만 자기상관 0.72이면: n_eff = ([\d.]+)', o11)
v67 = float(m.group(1))
add('제1권 67.4 = n(1-rho)/(1+rho)', v67, 414 * (1 - rho) / (1 + rho), 0.06, '(식 그대로는 일치)')
add('쌍 공식에 rho2=0을 넣은 n_eff', v67, 414 * (1 - rho * 0) / (1 + rho * 0), 0.06, '(제1권 67.4와 차이: 쌍 공식으로는 414)')
if os.path.exists('results/ch04-03.json'):
    J = json.load(open('results/ch04-03.json'))
    c1 = J['C']['one']['독립 가정']; c67 = J['C']['ps67']
    print('  모의(ch04-03): 한 계열만 AR(1) 0.72, 다른 계열은 백색일 때 독립 가정의 5%% 기각률 %.4f, 1%% 기각률 %.4f' % tuple(c1))
    print('  같은 모의에서 df를 제1권의 67.4로 쓴 5%% 기각률 %.4f, 1%% 기각률 %.4f (5%%여야 한다)' % tuple(c67))
    add('한 계열만일 때 독립 가정 5% 기각률(모의)', 0.05, c1[0], 0.005, '(모의가 5%를 지키므로 n_eff = n이 맞다)')
    both = J['C']['both']
    print('  모의(ch04-03): 두 계열 모두 0.72일 때 독립 가정 5%% 기각률 %.4f, 쌍 공식(참값 rho) 5%% 기각률 %.4f' % (both['독립 가정'][0], both['rho 참값 공식'][0]))
    add('두 계열 0.72, n_eff=131.3 공식의 5% 기각률(모의)', 0.05, both['rho 참값 공식'][0], 0.005, '(공식이 5%를 거의 지킨다)')
    print('  모의 r의 표준편차에서 얻은 n_eff = %.1f' % (1 / J['D']['sd'] ** 2 + 1))

# ---- 계산 10-6, 10.10.5절
print('\n[계산 10-6, 10.10.5절]')
m = re.search(r'= ([\d.]+) a/시료; Nyquist 주기 = ([\d.]+) a; 10 cm 입도 간격 = ([\d.]+) a', o10)
dt = 1 / 0.92
add('XRF 간격 a/시료', float(m.group(1)), dt, 0.005)
add('나이키스트 주기 a', float(m.group(2)), 2 * dt, 0.005)
add('입도 10 cm 간격 a/시료', float(m.group(3)), 10 * dt, 0.05)
x = np.array([1, 0, -1, 0, 1, 0, -1, 0.0]); X = sf.fft(x)
for k in (1, 2):
    m = re.search(r'DFT k=%d: \|X\| = ([\d.]+), 파워 \|X\|\^2/N = ([\d.]+)' % k, o10)
    add('DFT k=%d 파워 |X|^2/N' % k, float(m.group(2)), abs(X[k]) ** 2 / len(x), 0.0006)
m = re.search(r'dt=1.09, tau=5 -> ([\d.]+)', o10)
add('AR(1) 계수 exp(-1.09/5)', float(m.group(1)), float(np.exp(-1.09 / 5)), 0.0006)

# ---- 계산 2-15, 2-16
print('\n[계산 2-15, 2-16]')
m = re.search(r't\(1\) check: ([\d.]+) ([\d.]+) ([\d.]+) years', o02)
add('평균 간격: t(1)=40 CE로 읽으면', float(m.group(1)), (4273 - 1910) / 144, 0.05)
add('평균 간격: t(1)=10 cal BP', float(m.group(2)), (4273 - 10) / 144, 0.05)
m = re.search(r'Nyquist (\d+)\s+Welch segment ([\d.]+)', o02)
add('나이키스트 주기(간격 29년)', float(m.group(1)), 2 * 29, 0.5)
# Welch 구간 길이 2L/(K+1): 슬라이딩 창으로 구간 수를 센다
L = 4263
nper = 2131; hop = nper - nper // 2
nseg = sliding_window_view(np.arange(L), nper)[::hop].shape[0]
add('Welch 구간 길이 2L/4 (구간 수를 센 값: %d개)' % nseg, float(m.group(2)), 2 * L / 4, 0.6, '(nperseg=2131이면 3개 구간)')

# ---- 계산 11-5의 7번
print('\n[계산 11-5 7번]')
add('X(복원 평균 7.66)', 0.948, (7.66 - 4.829) / 2.987, 0.0006)
add('X의 sd = 0.53/2.987', 0.177, 0.53 / 2.987, 0.0006)
add('표 1 sd 0.20 x 2.987', 0.597, 0.20 * 2.987, 0.0006, '(논문 0.53과 다르다는 제1권의 미결 그대로)')

n_ok = sum(r[3] for r in rows)
print('\n요약: %d개 중 일치 %d개, 차이 %d개' % (len(rows), n_ok, len(rows) - n_ok))
for r in rows:
    if not r[3]: print('  차이:', r[0], '제1권', r[1], '이 장', r[2], r[4])
