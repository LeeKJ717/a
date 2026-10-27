# -*- coding: utf-8 -*-
"""계산 10-2: 14C 급등 사건의 크기와 빈도. Brehm 등(2022, Nat. Commun. 13, 1196)의 표 1과 본문 숫자, Brehm 등(2021)의 초록 숫자.
입력: Δ14C 상승(‰) 7176 BCE 19.5 ± 0.6, 5259 BCE 19.1 ± 0.6, 775 CE 17.6 ± 0.5; 5410 BCE 5.6 ± 0.8(Miyake 등 2021 인용 값).
초과 14C(kg): 28.7 ± 0.9, 29.2 ± 0.9, 26.2 ± 1.0; 5410 BCE 9.0 ± 1.1. 지자기 정규화 값(kg): Knudsen, Panovska 두 모형.
"""
import json, math
import numpy as np
from scipy import stats
out = {}
ev = {'7176 BCE': (19.5, 0.6, 28.7, 0.9), '5259 BCE': (19.1, 0.6, 29.2, 0.9), '775 CE': (17.6, 0.5, 26.2, 1.0)}
print('=== 계산 10-2 (1) 세 사건의 Δ14C 상승과 초과 14C ===')
def z(a, sa, b, sb): return (a - b) / math.hypot(sa, sb)
for k, (d, sd, kg, skg) in ev.items():
    print('  %-9s Δ14C %.1f ± %.1f ‰ (= %.2f%%), 초과 14C %.1f ± %.1f kg, kg/‰ = %.3f' % (k, d, sd, d / 10, kg, skg, kg / d))
for a, b in (('7176 BCE', '775 CE'), ('5259 BCE', '775 CE'), ('7176 BCE', '5259 BCE')):
    zd = z(ev[a][0], ev[a][1], ev[b][0], ev[b][1]); zk = z(ev[a][2], ev[a][3], ev[b][2], ev[b][3])
    print('  %s − %s: Δ14C 차 %.1f ‰ (%.1fσ), 초과 14C 차 %.1f kg (%.1fσ)' % (a, b, ev[a][0] - ev[b][0], zd, ev[a][2] - ev[b][2], zk))
    out['z_%s_%s' % (a, b)] = dict(dC=zd, kg=zk)
print('  5410 BCE(Miyake 등 2021): Δ14C 5.6 ± 0.8 ‰ → 7176 BCE의 %.2f배, 초과 14C 9.0 ± 1.1 kg → 775 CE의 %.2f배' % (5.6 / 19.5, 9.0 / 26.2))
print('\n=== 계산 10-2 (2) 지자기 정규화 값(kg)의 서로 비교 ===')
norm = {'7176 BCE': {'Knudsen': (30.1, 3.6), 'Panovska': (28.0, 1.2)}, '5259 BCE': {'Knudsen': (27.6, 1.4), 'Panovska': (28.4, 1.2)}, '775 CE': {'Knudsen': (31.5, 1.4), 'Panovska': (29.0, 1.4)}}
for m in ('Knudsen', 'Panovska'):
    for a in ('7176 BCE', '5259 BCE'):
        va, sa = norm[a][m]; vb, sb = norm['775 CE'][m]
        print('  %-8s %-8s − 775 CE: %.1f − %.1f = %+.1f kg (%.1fσ)' % (m, a, va, vb, va - vb, z(va, sa, vb, sb)))
        out['n_%s_%s' % (m, a)] = z(va, sa, vb, sb)
zs = [out['n_%s_%s' % (m, a)] for m in ('Knudsen', 'Panovska') for a in ('7176 BCE', '5259 BCE')]
print('  네 비교의 |z|: ' + ', '.join('%.1f' % abs(v) for v in zs) + ' → 1σ 이내 %d개, 1~2σ %d개, 2σ 이상 %d개' % (sum(abs(v) < 1 for v in zs), sum(1 <= abs(v) < 2 for v in zs), sum(abs(v) >= 2 for v in zs)))
print('  정규화 전 초과 14C 차이는 1.9σ, 2.2σ(계산 10-2 (1))였고 정규화 뒤에는 한 비교(Knudsen, 5259 BCE)만 2.0σ로 남는다.')
print('  정규화 전후의 7176 BCE 값: 28.7 → %.1f(Knudsen), %.1f(Panovska); 775 CE: 26.2 → %.1f, %.1f' % (30.1, 28.0, 31.5, 29.0))
print('  775 CE는 정규화에서 +%.1f, +%.1f kg 커지고, 7176 BCE는 +%.1f, %+.1f kg 달라진다' % (31.5 - 26.2, 29.0 - 26.2, 30.1 - 28.7, 28.0 - 28.7))
print('\n=== 계산 10-2 (3) 사건 사이의 시간과 빈도 ===')
print('  7176 BCE → 5259 BCE = %d년; 5259 BCE → 775 CE = %d년(0년 없음)' % (7176 - 5259, 5259 + 775 - 1))
print('  Brehm 등(2021): 연도별 14C 기록 AD 969~1933 = %d년, 11년 주기 %d개(%.1f) 분량; 사건 AD 993, 1052, 1279 간 간격 %d, %d년' % (1933 - 969 + 1, (1933 - 969 + 1) // 11, (1933 - 969 + 1) / 11, 1052 - 993, 1279 - 1052))
n_ev, T = 5, 2030
lam = n_ev / T
lo = stats.chi2.ppf(0.025, 2 * n_ev) / 2; hi = stats.chi2.ppf(0.975, 2 * (n_ev + 1)) / 2
print('  논문: 강한 사건 5개와 2030년 → 평균 %.0f년에 한 번(%.4f/년)' % (T / n_ev, lam))
print('  푸아송 정확 95%% 신뢰구간(개수 %.2f~%.2f) → 평균 간격 %.0f~%.0f년. 논문의 범위 "400~2400년에 한 번"과 견주면 상한이 %.0f년으로 더 길다' % (lo, hi, T / hi, T / lo, T / lo))
out['poisson'] = dict(lo=lo, hi=hi, gap_lo=T / hi, gap_hi=T / lo)
print('  논문의 "발견된 사건이 전부라면 약 2400년에 한 번"과 견주면: 12,000년/5 = %.0f, 12,460년(논문이 적은 가장 긴 절대 연대 합성 나이테)/5 = %.0f년. 이 책은 논문이 어떻게 2400을 얻었는지 확인하지 못했다(위 두 값은 어림)' % (12000 / 5, 12460 / 5))
print('  5/2030 = 1/%.0f년은 초신성·슈퍼플레어 기준 3000~6000년에 한 번(논문)의 %.1f~%.1f배 잦다' % (2030 / 5, 3000 / (2030 / 5), 6000 / (2030 / 5)))
print('  이 계산은 사건이 균일하게 무작위로 온다고 놓는다. 이미 알려진 사건 수는 연도별 14C를 잰 구간에 의존한다(논문도 목표 표집의 편향을 쓴다).')
print('\n=== 계산 10-2 (4) 14C 연수로 바꾼 크기 ===')
tau = 8033.0
for k, (d, sd, kg, skg) in ev.items():
    print('  %-9s %.1f ‰ ↔ %.0f 14C년(평균 수명 %.0f년 관례, 작은 값 근사 %.1f ‰ × %.2f 년/‰)' % (k, d, d * tau / 1000, tau, d, tau / 1000))
out['ev'] = ev
json.dump(out, open('out/calc10-2.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: float(o))
