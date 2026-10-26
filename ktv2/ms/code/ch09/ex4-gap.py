# -*- coding: utf-8 -*-
"""실습 9-11. 두 분출 단계의 간격: 제1권 4장 계산 4-3, 4-4의 되풀이.
입력(Lee 등 2024, 제1권 4.3절): Spike 1 = 분출일 뒤 46±21일, Spike 2 = 77±23일 (2σ), 간격 31±25일(2σ).
확률(원문): 간격 7일 이내 2.5%, 28일 이내 42.7%, 56일 이내 97.9%.
이 스크립트는 정규 근사와 상관을 넣은 몬테카를로로 같은 확률을 구하고, 상관이 값을 얼마나 바꾸는지 본다.
실행: python3 ex4-gap.py > ex4-gap.log"""
import os, sys, json, platform, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy
from scipy import stats
print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
m1, m2 = 46.0, 77.0
s1, s2 = 21.0 / 2, 23.0 / 2          # 2σ → σ
sg = 25.0 / 2
paper = {7: 2.5, 28: 42.7, 56: 97.9}
res = {}
print('\n[입력] 시점 1: %g일 σ=%.2f, 시점 2: %g일 σ=%.2f, 간격 평균 %g일, 원문 간격 σ=%.2f(=25/2)' % (m1, s1, m2, s2, m2 - m1, sg))
print('\n[실습 9-11a] 정규 근사 (간격 ~ N(31, 12.5^2))')
for d in (7, 28, 56):
    p = stats.norm.cdf((d - 31) / sg)
    print('  P(간격 < %2d일) = %.4f (원문 %.1f%%, 차이 %+.2f%%p)' % (d, p, paper[d], 100 * p - paper[d]))
rho = (s1 ** 2 + s2 ** 2 - sg ** 2) / (2 * s1 * s2)
print('\n[실습 9-11b] 원문의 간격 σ=12.5를 내려면 필요한 상관 ρ = (σ1²+σ2²-σg²)/(2σ1σ2) = %.4f' % rho)
print('  독립(ρ=0)이면 간격 σ = sqrt(σ1²+σ2²) = %.3f일, 완전 상관(ρ=1)이면 |σ2-σ1| = %.3f일' % (np.hypot(s1, s2), abs(s2 - s1)))
rng = np.random.default_rng(20261026)
N = 2_000_000
print('\n[실습 9-11c] 몬테카를로 %d번: 상관 ρ를 바꿔 간격의 분포를 본다' % N)
print('  %-12s %10s %10s %10s %10s %10s' % ('ρ', '간격 평균', '간격 σ', 'P(<7일)', 'P(<28일)', 'P(<56일)'))
for r in (0.0, rho, 0.7, 1.0):
    C = np.array([[s1 ** 2, r * s1 * s2], [r * s1 * s2, s2 ** 2]])
    L = np.linalg.cholesky(C + 1e-12 * np.eye(2))
    Z = rng.standard_normal((N, 2)) @ L.T
    t1, t2 = m1 + Z[:, 0], m2 + Z[:, 1]
    g = t2 - t1
    print('  %-12s %10.3f %10.3f %10.4f %10.4f %10.4f' % ('%.4f' % r, g.mean(), g.std(ddof=1), (g < 7).mean(), (g < 28).mean(), (g < 56).mean()))
    res['rho%.3f' % r] = dict(sd=float(g.std(ddof=1)), p7=float((g < 7).mean()), p28=float((g < 28).mean()), p56=float((g < 56).mean()))
    if abs(r - rho) < 1e-9:
        gg = g
        # 순서 조건(시점 1 < 시점 2)을 걸면
        ok = t1 < t2
        print('    └ 시점 1 < 시점 2 인 비율 %.5f; 이 조건을 걸고 다시 센 P(<7일)=%.4f, P(<28일)=%.4f, P(<56일)=%.4f' % (
            ok.mean(), (g[ok] < 7).mean(), (g[ok] < 28).mean(), (g[ok] < 56).mean()))
        res['ordered'] = dict(frac=float(ok.mean()), p7=float((g[ok] < 7).mean()), p28=float((g[ok] < 28).mean()), p56=float((g[ok] < 56).mean()))
print('\n  (ρ=%.4f 줄이 원문 간격 σ를 재현하도록 정한 것이므로 σ가 12.5로 나오는 것은 확인이 아니라 검산이다. 확률 세 개는 원문 값과 비교할 수 있다.)' % rho)
print('  원문과의 차이(ρ=%.4f): ' % rho + ', '.join('%d일 %+.2f%%p' % (d, 100 * res['rho%.3f' % rho]['p%d' % d] - paper[d]) for d in (7, 28, 56)))

print('\n[실습 9-11d] 947-02-07 의 소리(제1권 4.3절)')
d98 = (datetime.date(947, 2, 7) - datetime.date(946, 11, 1)).days
d96 = (datetime.date(947, 2, 7) - datetime.date(946, 11, 3)).days
print('  946-11-01 → 947-02-07 = %d일 = %.1f주,  946-11-03 → 947-02-07 = %d일' % (d98, d98 / 7, d96))
print('  Spike 2(77일)보다 %d일 뒤. 시점 2의 σ=%.1f일로 재면 z=%.2f, 단측 p=%.4f' % (d98 - 77, s2, (d98 - 77) / s2, stats.norm.sf((d98 - 77) / s2)))
print('  (달력 환산 5일 차이, 분출일 가정 등 입력의 불확실성은 이 계산에 들어 있지 않다. 한 사건의 시점이 이 값 이상일 확률일 뿐이다.)')
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex4.json'), 'w'))
np.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex4-gap-sample.npy'), gg[:200000].astype(np.float32))
print('\n결과 저장: results/ex4.json')
