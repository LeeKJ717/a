# -*- coding: utf-8 -*-
"""계산 7-5: Morrill 등(2013)의 사건 탐지 규칙을 잡음만 있는 시계열에 적용한 거짓 경보율(시연값).
규칙(논문): 기준 구간 평균 +- 2 표준편차를 넘는 값이 연속 2개 이상(해상도 10년 미만은 3개 이상)이면 이상.
여기서는 평균과 표준편차를 창 앞뒤에 붙인 같은 길이의 두 기준 구간(합 1200년)에서 구하는 단순화(논문의 기준 구간 7.4~7.9, 8.5~9.0 ka 와 길이는 같다).
창: 8.2 ka 부근 600년(논문의 7.9~8.5 ka 창과 같은 길이). 해상도 50/20/10/5 년, 자기상관 phi=0/0.3/0.6.
시드 20261027, 반복 20000. 양쪽(높음 또는 낮음)과 한쪽(낮음)을 따로 센다."""
import numpy as np
rng = np.random.default_rng(20261027)
def ar1(n, phi, size):
    e = rng.standard_normal((size, n))
    x = np.empty_like(e)
    x[:,0] = e[:,0]
    s = np.sqrt(1-phi**2)
    for i in range(1,n): x[:,i] = phi*x[:,i-1] + s*e[:,i]
    return x
def run_len_ok(mask, k):
    # 행마다 연속 True 가 k 개 이상 있는가
    out = np.zeros(mask.shape[0], bool)
    run = np.zeros(mask.shape[0], int)
    for i in range(mask.shape[1]):
        run = np.where(mask[:,i], run+1, 0)
        out |= run >= k
    return out
N = 20000
print('창 600 년, 반복 %d, 시드 20261027' % N)
print('해상도 | 점 수 | 연속 k | phi=0 양쪽 / 낮음만 | phi=0.3 | phi=0.6')
res = {}
for dt in (50, 20, 10, 5):
    n = 600//dt
    k = 3 if dt < 10 else 2
    line = []
    for phi in (0.0, 0.3, 0.6):
        x = ar1(n+ (600//dt)*2, phi, N)  # 기준 구간 2배 길이를 앞뒤로 붙여 평균/표준편차 추정(창 밖 기준 구간)
        base = np.concatenate([x[:, :n], x[:, -n:]], axis=1)  # 기준 구간 앞쪽 n, 뒤쪽 n
        mu = base.mean(1, keepdims=True); sd = base.std(1, ddof=1, keepdims=True)
        win = x[:, n:2*n]
        lowm = win < mu-2*sd; highm = win > mu+2*sd
        both = run_len_ok(lowm, k) | run_len_ok(highm, k)
        low = run_len_ok(lowm, k)
        res[(dt,phi)] = (both.mean(), low.mean())
        line.append('%.3f / %.3f' % (both.mean(), low.mean()))
    print('%4d년 | %3d | %d | %s | %s | %s' % (dt, n, k, line[0], line[1], line[2]))
print()
print('[해석 보조] 이론 대략값(독립, 2시그마 한쪽 확률 p=0.0228): 점 수 n, 연속 2개 이상의 기대 횟수 약 (n-1)p^2')
p = 0.02275
for dt in (50,20,10,5):
    n = 600//dt
    k = 3 if dt < 10 else 2
    print('  %2d년: n=%d, k=%d, 한쪽 기대 횟수 약 %.4f' % (dt, n, k, (n-k+1)*p**k))
print()
print('[참고] 논문이 본 262개 계열(해상도 50년 이하) 중 사건이 잡힌 수는 논문 요약에서 확인하지 못했다 -> 이 시연값과 비교하지 않는다')
print('  다만 114 지점 x 약 2.3 계열이라는 평균 %.2f 계열/지점은 계산 가능' % (262/114))
