# -*- coding: utf-8 -*-
"""계산 10-5: 이론 상자의 시연값. 어느 논문의 값도 아니다.
(1) 주기 없는 무작위 계열에서도 '문턱 아래 30년 이상' 같은 규칙이 큰 극소기를 만든다. 10년 간격 시연 계열(AR(1))을 만들어 센다.
(2) 문턱을 20에서 15, 25로 바꾸면 사건 수와 시간 비율이 어떻게 변하는가.
(3) 푸아송 계수 오차 시연: 사건 5개에서 평균 간격의 신뢰구간.
시연 계열: x(t) = 평균 + 표준편차 × AR(1), 평균 40, 표준편차 25, 자기상관 0.8(10년 간격), 음수는 0으로 자른다. 값은 모두 시연값이다.
"""
import json
import numpy as np
from scipy import stats
rng = np.random.default_rng(11)
out = {}
def series(n, mu=40.0, sd=25.0, rho=0.8):
    e = rng.normal(size=n); x = np.empty(n); x[0] = e[0]
    for i in range(1, n): x[i] = rho * x[i - 1] + np.sqrt(1 - rho ** 2) * e[i]
    return np.clip(mu + sd * x, 0, None)
def runs(x, thr, minlen, below=True):
    f = (x < thr) if below else (x > thr)
    ev = []; i = 0
    while i < len(f):
        if f[i]:
            j = i
            while j + 1 < len(f) and f[j + 1]: j += 1
            if j - i + 1 >= minlen: ev.append((i, j - i + 1))
            i = j + 1
        else: i += 1
    return ev
n = 900   # 9000년, 10년 간격
print('=== 계산 10-5 (1)(2) 주기 없는 시연 계열의 큰 극소기 ===')
for thr in (15, 20, 25):
    cnts = []; frac = []; first = None
    for _ in range(2000):
        x = series(n); ev = runs(x, thr, 3)
        cnts.append(len(ev)); frac.append(sum(l for _, l in ev) / n)
    print('  문턱 SN<%d, 30년(3칸) 이상: 9000년당 사건 수 중앙 %.0f (5~95%% %.0f~%.0f), 시간 비율 중앙 %.1f%%' % (thr, np.median(cnts), np.percentile(cnts, 5), np.percentile(cnts, 95), 100 * np.median(frac)))
    out['thr%d' % thr] = dict(n=float(np.median(cnts)), frac=float(np.median(frac)))
x = series(n)
print('  한 번의 시연 계열(문턱 20): 사건 %d개' % len(runs(x, 20, 3)))
print('  이 시연은 주기가 없는 계열에서도 문턱 규칙이 사건을 만든다는 것만 보인다. 실제 태양 계열의 분포와 비교하려는 것이 아니다.')
print('\n=== 계산 10-5 (3) 사건 수가 적을 때의 간격 추정(시연값) ===')
for k in (2, 5, 10, 20):
    lo = stats.chi2.ppf(0.025, 2 * k) / 2; hi = stats.chi2.ppf(0.975, 2 * (k + 1)) / 2
    print('  사건 %2d개를 1000년에서 센 경우: 평균 간격 %.0f년, 95%% 구간 %.0f~%.0f년 (비 %.1f)' % (k, 1000 / k, 1000 / hi, 1000 / lo, hi / lo))
    out['k%d' % k] = [1000 / hi, 1000 / lo]
print('\n=== 계산 10-5 (4) Δ14C 와 14C 연대의 환산 시연 ===')
tau = 8033.0
for dd in (1, 5, 10, 20):
    print('  Δ14C %2d ‰ ≈ %.0f 14C년 (작은 값 근사)' % (dd, dd * tau / 1000))
json.dump(out, open('out/calc10-5.json', 'w'), ensure_ascii=False, indent=1)
