# -*- coding: utf-8 -*-
"""1장 보충 계산(시연값). 방법을 설명하려고 이 책이 정한 가상의 값으로 계산한 것이며 논문 값이 아니다.
실행: python3 calc-ch01-supp-v1.py | tee calc-ch01-supp-v1.log
"""
import math
import numpy as np
from scipy import stats

print('계산 1-8. 시연값으로 보는 세 가지 방법')
print('\n(가) OSL 나이 = 등가선량(De) / 선량률. 시연값: De = 20.0 ± 1.0 Gy, 선량률 = 3.00 ± 0.18 Gy/ka')
De, sDe, D, sD = 20.0, 1.0, 3.00, 0.18
age = De / D
rel = math.hypot(sDe / De, sD / D)
print('  나이 = %.2f / %.2f = %.2f ka. 상대 오차 = sqrt((%.3f)^2 + (%.3f)^2) = %.3f = %.1f%%. 나이 오차 = %.2f ka' % (De, D, age, sDe / De, sD / D, rel, rel * 100, age * rel))

print('\n(나) 오차 가중 평균과 카이제곱. 시연값 세 개: 8.0 ± 0.5, 8.2 ± 0.5, 9.5 ± 0.5 ka')
a = np.array([8.0, 8.2, 9.5]); s = np.array([0.5, 0.5, 0.5])
w = 1 / s ** 2; m = (a * w).sum() / w.sum(); sm = 1 / math.sqrt(w.sum())
chi = (((a - m) / s) ** 2).sum(); df = len(a) - 1
print('  가중 평균 = %.3f ± %.3f ka. 카이제곱 = %.2f, 자유도 %d, p = %.3f' % (m, sm, chi, df, stats.chi2.sf(chi, df)))
a2 = np.array([8.0, 8.2, 8.4]); chi2 = (((a2 - (a2 * w).sum() / w.sum()) / s) ** 2).sum()
print('  비교: 8.0, 8.2, 8.4 이면 카이제곱 = %.2f, p = %.3f' % (chi2, stats.chi2.sf(chi2, 2)))

print('\n(다) 연대 없는 구간이 우연일 가능성. 치롄산 49개, 길이 14.1 ka 중 4.0~8.0 ka(4 ka)에 2개')
n, L, win = 49, 14.1, 4.0
p = win / L
print('  나이가 0~14.1 ka에 고르게 퍼졌다고 가정하면 한 시료가 그 창에 들 확률 p = %.4f, 기대 개수 = %.1f' % (p, n * p))
print('  창에 2개 이하일 확률 P(X<=2) = %.2e' % stats.binom.cdf(2, n, p))
print('  (실제 나이는 0~1 ka에 16개가 몰려 있어 고른 분포가 아니다. 이 값은 기준선 하나일 뿐이며 사구 모래가 쌓인 시기 자체가 고르지 않다는 점은 검정하지 못한다.)')
rng = np.random.default_rng(20261026)
cnt = 0; N = 100000
for _ in range(N):
    x = rng.uniform(0, L, n)
    if ((x >= 4.0) & (x < 8.0)).sum() <= 2: cnt += 1
print('  모의 %d회(시드 20261026)에서 창에 2개 이하인 비율 = %.2e' % (N, cnt / N))
print('  창을 위치만 옮겨 0~14.1 ka 어디에 놓아도 길이 4 ka 창에 2개 이하일 확률은 위와 같다. 창 위치를 자료를 보고 정했으므로 이 확률은 낮게 나온다(사후 선택).')
best = 0
sz = np.array([0.5,0.4,0.4,0.4,0.5,0.9,0.8,0.8,0.9,0.9,1.0,2.1,2.4,3.2,3.2,3.1,3.6,3.4,3.6,5.6,8.1,9.1,9.7,9.5,8.9,8.5,8.2,
               0.2,0.3,0.4,0.7,0.4,0.8,1.8,2.0,2.4,2.6,2.8,4.0,9.1,9.6,12.3,12.5,12.7,13.7,13.1,12.0,11.9,14.1])
print('  입력 나이 개수 %d' % len(sz))
cnts = []
for st in np.arange(0, 14.1 - win + 1e-9, 0.1):
    cnts.append(((sz >= st) & (sz < st + win)).sum())
print('  이 49개 나이로 길이 4 ka 창을 0.1 ka씩 밀 때 창 안의 개수 최소 = %d (창 시작 %.1f ka)' % (min(cnts), np.arange(0, 14.1 - win + 1e-9, 0.1)[int(np.argmin(cnts))]))
mins = []
for _ in range(20000):
    x = rng.uniform(0, L, n)
    mins.append(min(((x >= st) & (x < st + win)).sum() for st in np.arange(0, L - win + 1e-9, 0.1)))
mins = np.array(mins)
print('  고른 분포에서 같은 49개를 뽑아 가장 빈 4 ka 창을 찾으면 그 개수가 2 이하인 비율 = %.3f (사후 선택까지 반영한 기준선)' % (mins <= 2).mean())

print('\n' + '=' * 70)
print('계산 1-9. 판독표의 중점을 호수 기록과 사구 기록으로 나누어 견주기 (이 책의 판독, 계산 1-6의 보충)')
print('=' * 70)
lakes = {'대해호': 6.65, '달리호': 7.55, '차간 누르': 8.75, '호륜호 꽃가루': 7.20, '텅거 호': 7.10, '무우스 고호수': 7.85, '텅거리 사막 호수': 6.20, '우란부허 고호수': 7.40}
dunes = {'훈산다크 고토양': 5.60, '내몽골 중부 사구': 7.30, '호륜부이르 사구': 7.50, '기련산 사구': 6.00, '감남 사구': 6.00}
L = np.array(list(lakes.values())); Dn = np.array(list(dunes.values()))
print('호수·고호수·꽃가루 코어 %d개: 평균 %.2f, 표준편차 %.2f, 범위 %.2f~%.2f' % (len(L), L.mean(), L.std(ddof=1), L.min(), L.max()))
print('사구·고토양 %d개: 평균 %.2f, 표준편차 %.2f, 범위 %.2f~%.2f' % (len(Dn), Dn.mean(), Dn.std(ddof=1), Dn.min(), Dn.max()))
t, pw = stats.ttest_ind(L, Dn, equal_var=False)
print('평균 차(호수-사구) = %.2f ka. Welch t = %.2f, p = %.3f' % (L.mean() - Dn.mean(), t, pw))
rng = np.random.default_rng(20261026)
allv = np.concatenate([L, Dn]); obs = L.mean() - Dn.mean(); cnt = 0; N = 50000
for _ in range(N):
    rng.shuffle(allv)
    if abs(allv[:len(L)].mean() - allv[len(L):].mean()) >= abs(obs): cnt += 1
print('순열 검정(%d회, 시드 20261026) 양쪽 p = %.3f' % (N, (cnt + 1) / (N + 1)))
print('Mann-Whitney U 양쪽 p = %.3f' % stats.mannwhitneyu(L, Dn, alternative='two-sided').pvalue)
print('기록 길이(습윤 구간 길이, ka): 호수 평균 %.2f, 사구 평균 %.2f' % (np.mean([2.90, 2.50, 3.50, 1.60, 3.30, 2.90, 2.00, 2.00]), np.mean([2.66, 3.40, 5.00, 4.00, 4.00])))
print('사구 기록은 경계를 "8~4 ka"처럼 1 ka 단위로 읽은 것이 많아(기련산, 감남) 중점이 6.00으로 같은 값이 둘이다. 연대 해상도의 차이를 판독에 담지 못했다.')
