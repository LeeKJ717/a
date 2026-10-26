# -*- coding: utf-8 -*-
"""4장 실습 4-1: 푸리에 변환의 기본 (일정한 간격의 기록)
제1권 10장 계산 10-6, 10.10.5절(이산 푸리에 변환 시연, 나이키스트 주기)을 되풀이한다.
실행: python3 ch04-01-fourier.py
"""
import sys, time, json, platform
import numpy as np, scipy, scipy.signal as ss, scipy.fft as sf

t0 = time.perf_counter()
print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))

# ---------------------------------------------------------------- A. 제1권 10.10.5절의 손계산 시연
print('\n== A. 8개 값 [1,0,-1,0,1,0,-1,0]의 이산 푸리에 변환 (제1권 10.10.5절)')
x = np.array([1, 0, -1, 0, 1, 0, -1, 0], float)
N = len(x)
def dft_manual(x, k):
    n = np.arange(len(x))
    return np.sum(x * np.exp(-2j * np.pi * k * n / len(x)))
X = sf.fft(x)
for k in range(N // 2 + 1):
    print('  k=%d  손으로 짠 합 |X|=%.3f  scipy.fft |X|=%.3f  파워 |X|^2/N=%.3f' % (k, abs(dft_manual(x, k)), abs(X[k]), abs(X[k]) ** 2 / N))
print('  제1권 값: k=1 파워 0, k=2 합 4, 파워 2.0')

# ---------------------------------------------------------------- B. 코어 YD0901 시간 눈금과 나이키스트
print('\n== B. 코어 YD0901의 시료 간격과 나이키스트 주기 (제1권 계산 10-6)')
rate = 0.92            # cm/a, 제1권이 Wang 등(2011)에서 옮긴 값
for name, dz in (('XRF', 1.0), ('입도', 10.0)):
    dt = dz / rate
    print('  %s: 간격 %.0f cm -> %.3f a/시료, 나이키스트 주기 2*dt = %.3f a' % (name, dz, dt, 2 * dt))
print('  600 a x 0.92 = %.0f cm, 401 cm / 0.92 = %.0f a' % (600 * rate, 401 / rate))
for P in (6.9, 5.2, 4.7, 4.5, 3.9):
    print('  주기 %.1f a -> 진동수 %.3f 1/a' % (P, 1 / P), end=';')
print()
print('  제1권 값: 1.09 a/시료, 2.17 a, 10.9 a/시료, 진동수 0.145 0.192 0.213 0.222 0.256')

# ---------------------------------------------------------------- C. 파워의 크기: 정확히 한 진동수에 맞는 사인파
print('\n== C. 사인파의 진폭과 파워 (scipy.signal.periodogram, scaling="spectrum")')
n = 512; dt = 1.0
t = np.arange(n) * dt
A = 2.0
f0 = 32 / (n * dt)          # 정확히 32번째 칸
y = A * np.sin(2 * np.pi * f0 * t)
f, p = ss.periodogram(y, fs=1 / dt, window='boxcar', detrend=False, scaling='spectrum')
print('  진폭 A=%.1f 사인파, 정확히 32번째 칸: 최대 파워 %.4f (A^2/2 = %.4f), 최대 위치 %.5f (f0=%.5f)' % (A, p.max(), A * A / 2, f[p.argmax()], f0))
print('  파스발: sum(y^2)=%.4f, (1/N) sum |X|^2=%.4f' % (np.sum(y ** 2), np.sum(np.abs(sf.fft(y)) ** 2) / n))

# ---------------------------------------------------------------- D. 칸에 맞지 않는 진동수: 누설과 창
print('\n== D. 진동수가 칸에 맞지 않을 때 (누설) 와 창 함수')
f1 = 32.5 / (n * dt)         # 칸과 칸 사이
y = A * np.sin(2 * np.pi * f1 * t)
rows = []
for w in ('boxcar', 'hann'):
    f, p = ss.periodogram(y, fs=1 / dt, window=w, detrend=False, scaling='spectrum', nfft=n)
    pk = p.max()
    far = p[(np.abs(f - f1) > 20 / (n * dt))].max()      # 20칸 이상 떨어진 곳의 최대
    rows.append((w, pk, far / pk))
    print('  창 %-6s 최대 파워 %.4f (A^2/2=%.4f), 20칸 밖 최대/최대 = %.2e (%.1f dB)' % (w, pk, A * A / 2, far / pk, 10 * np.log10(far / pk)))
print('  보통 창에서는 봉우리가 낮아지고 넓어지는 대신 먼 곳의 누설이 크게 준다.')

# ---------------------------------------------------------------- E. 별칭(aliasing)
print('\n== E. 별칭: 주기 3.9 a와 6.9 a의 사인파를 서로 다른 간격으로 뽑는다 (시연값)')
def apparent_period(P, dt, L=2000.0, pad=16):
    nn = int(L / dt)
    tt = np.arange(nn) * dt
    yy = np.sin(2 * np.pi * tt / P)
    m = sf.next_fast_len(nn * pad)
    F = np.abs(sf.rfft(yy * np.hanning(nn), n=m))
    fr = sf.rfftfreq(m, dt)
    k = F[1:].argmax() + 1
    return 1 / fr[k]
al = {}
for P in (3.9, 6.9):
    for dt in (1 / 0.92, 2.0, 10 / 0.92):
        ap = apparent_period(P, dt)
        fN = 0.5 / dt
        fa = abs(1 / P - round((1 / P) / (1 / dt)) * (1 / dt))
        al['%.1f/%.3f' % (P, dt)] = ap
        print('  진짜 주기 %.1f a, 간격 %.3f a (나이키스트 진동수 %.4f, 주기 %.3f a): 관측된 봉우리 주기 %.2f a; 접힘식 예측 %.2f a' % (P, dt, fN, 2 * dt, ap, 1 / fa if fa > 0 else float('inf')))

# ---------------------------------------------------------------- F. 속도: FFT 대 순수 합
print('\n== F. 계산 시간: 직접 합(O(N^2)) 대 FFT(O(N log N))')
for n_ in (1024, 4096, 16384):
    xx = np.random.default_rng(1).standard_normal(n_)
    t1 = time.perf_counter()
    if n_ <= 4096:
        k = np.arange(n_)[:, None]; m = np.arange(n_)[None, :]
        Xd = (xx[None, :] * np.exp(-2j * np.pi * k * m / n_)).sum(axis=1)
    t2 = time.perf_counter()
    Xf = sf.fft(xx)
    t3 = time.perf_counter()
    if n_ <= 4096:
        print('  N=%5d 직접 합 %.4f s, scipy.fft %.6f s, 최대 차이 %.2e' % (n_, t2 - t1, t3 - t2, np.abs(Xd - Xf).max()))
    else:
        print('  N=%5d 직접 합은 행렬이 커서 생략, scipy.fft %.6f s' % (n_, t3 - t2))

json.dump({'alias': al, 'leak': rows}, open('results/ch04-01.json', 'w'), ensure_ascii=False)
print('\n총 실행 시간 %.2f s' % (time.perf_counter() - t0))
