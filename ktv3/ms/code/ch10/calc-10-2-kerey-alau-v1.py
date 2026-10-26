# -*- coding: utf-8 -*-
"""계산 10-2. 카자흐 씨족 계보의 연대 주장 두 가지를 논문의 숫자로 점검한다.
(a) Abilev 등(2012): Kerey의 두 하위 씨족(Abakh-Kerey, Ashmaily-Kerey)이 계보 기록으로 20~22세대 전에 갈라졌다. 17개 STR 네트워크에서 두 하위 군집은 DYS448 한 자리만 다르다.
(b) Zhabagin 등(2021): Alimuly와 Baiuly 씨족이 약 650년 전의 Emir Alau에게서 내려온다. STR 700 ± 200년, 염기서열 500 ± 200년.
돌연변이율 2.1e-3 / 자리 / 세대는 Zhunussova 등(2025)의 값이며 Abilev 등이 쓴 값이 아니다. 시연 적용이다."""
import json, os, math
from scipy.stats import poisson
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
print('== 계산 10-2 (a) Kerey 하위 씨족 분기: 세대 수 -> 연도, 기대 돌연변이 수 ==')
mu, loci = 2.1e-3, 17
for g in (20, 21, 22):
    for L in (25, 30):
        yrs = g * L
        print('%d세대 x %d년 = %d년 전 -> 논문 발표(2012)를 기준으로 %d CE' % (g, L, yrs, 2012 - yrs))
rows = []
for g in (20, 21, 22):
    lam = 2 * g * loci * mu
    p0 = poisson.pmf(0, lam); p1 = poisson.cdf(1, lam)
    print('분기 후 %d세대: 두 줄기 합쳐 기대 돌연변이 수 2 x %d x %d x %.4f = %.3f, P(0) = %.3f, P(<=1) = %.3f' % (g, g, loci, mu, lam, p0, p1))
    rows.append(dict(g=g, lam=lam, p0=float(p0), p_le1=float(p1)))
res['a'] = rows
print('관측: 두 하위 군집은 17자리 가운데 1자리만 다르다. 두 하위 군집의 차이를 두 줄기 사이의 쌍별 거리로 읽으면 기대치(약 1.4~1.6)와 어긋나지 않는다.')
print('그러나 논문의 "하위 군집"은 네트워크의 묶음이며 쌍별 거리 하나가 아니다. 이 점검은 크기의 어림이다.')
print('\n== 계산 10-2 (b) Emir Alau: 650년 전 대 STR 700 +- 200, 염기서열 500 +- 200 ==')
for n, m, s in [('STR', 700, 200), ('염기서열', 500, 200)]:
    lo, hi = m - s, m + s
    z = (650 - m) / s
    print('%-6s %d +- %d 년 전 -> 구간 %d~%d, 650은 구간 안: %s, z = %.2f' % (n, m, s, lo, hi, lo <= 650 <= hi, z))
    res['b_' + n] = dict(m=m, s=s, z=z)
w = (700 / 200 ** 2 + 500 / 200 ** 2) / (2 / 200 ** 2); sw = (1 / (2 / 200 ** 2)) ** 0.5
print('두 추정이 독립이라고 가정한 역분산 가중 평균: %.0f +- %.0f 년 전 (두 추정은 같은 시료에서 나와 독립이 아니므로 이 평균은 형식적이다)' % (w, sw))
print('논문 발췌(보도 자료)에는 ± 200이 표준오차인지 95퍼센트 구간인지 적혀 있지 않다. 확인 필요.')
res['b_mean'] = (w, sw)
json.dump(res, open(os.path.join(OUT, 'calc-10-2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
