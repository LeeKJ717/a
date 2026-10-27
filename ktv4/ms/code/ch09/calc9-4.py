# -*- coding: utf-8 -*-
"""계산 9-4: 이론 상자의 시연값. 어느 논문의 값도 아니다.
(1) 빙핵 황산염 플럭스에서 성층권 황 주입량(VSSI)을 구하는 식의 크기감(Toohey & Sigl 2017의 식 구조: 황산염 질량 = 3 × 황 질량, 전달 함수 L).
    식의 꼴은 요약 도구가 돌려준 것이므로 원문 식 확인이 필요하다. 아래 플럭스는 시연값이다.
(2) 푸아송 분화 시연: 평균 간격 20년, 1000년 동안의 간격.
(3) 비율의 오차 전파 시연.
"""
import numpy as np, json
rng = np.random.default_rng(7)
out = {}
print('=== 계산 9-4 (1) 플럭스 → VSSI 크기감(시연값) ===')
for lab, L in (('열대 L = 1.0e9 km²', 1.0e9), ('중고위도 L = 0.57e9 km²', 0.57e9)):
    for f in (10.0, 50.0, 100.0):
        mS = L * f / 3.0 / 1e9      # kg 를 Tg(1e9 kg)로. 한 반구의 플럭스 f(kg/km²) 하나만 쓴 값
        print('  %-24s 플럭스 %5.0f kg/km² → 황 %.2f Tg S (한 반구 항 하나)' % (lab, f, mS))
print('  같은 플럭스에서 중고위도 분화의 황은 열대의 0.57배. 플럭스가 두 배면 황도 두 배(선형).')
print('  3은 황산염(SO4, 분자량 96)과 황(S, 32)의 질량비 96/32 = %.1f' % (96 / 32))
print('  양 극의 두 플럭스를 합하는 식(논문 식 5의 꼴)이 맞다면 두 항이 더해진다. 탐보라 시연: 두 극 모두 50 kg/km², 열대 → %.1f Tg S (논문 VSSI 28.1과 견주면 %.2f배; 논문의 플럭스 값은 이 책이 읽지 못함)' % (2 * 1.0e9 * 50 / 3 / 1e9, 2 * 1.0e9 * 50 / 3 / 1e9 / 28.1))
print('\n=== 계산 9-4 (2) 푸아송 분화(시연값) ===')
lam = 1 / 20.0; T = 1000
gaps_all = []
for _ in range(2000):
    n = rng.poisson(lam * T); t = np.sort(rng.uniform(0, T, n)); g = np.diff(np.r_[0, t, T]); gaps_all.append(g.max())
print('  평균 간격 20년, 1000년: 시뮬레이션 2000회에서 최대 간격 중앙값 %.0f년, 5~95%% %.0f~%.0f년 (근사식 ln(N)/λ = %.0f년, N = 50)' % (np.median(gaps_all), np.percentile(gaps_all, 5), np.percentile(gaps_all, 95), np.log(50) / lam))
out['demo_max_gap'] = float(np.median(gaps_all))
print('  평균 간격 20년에서 간격이 120년 이상일 확률 %.4f, 1000년의 간격 약 50개 중 기대 개수 %.2f (시뮬레이션에서 최대 간격이 120년 이상인 비율 %.3f)' % (np.exp(-lam * 120), 50 * np.exp(-lam * 120), (np.array(gaps_all) >= 120).mean()))
print('\n=== 계산 9-4 (3) 비율의 오차 전파(시연값) ===')
a, sa, b, sb = 60.0, 0.18, 30.0, 0.16
x = rng.normal(a, a * sa, 400000); y = rng.normal(b, b * sb, 400000)
r = x / y
print('  A = 60 ± 18%%, B = 30 ± 16%%: A/B = %.2f, 해석적 1σ = %.2f, 시뮬레이션 평균 %.2f 표준편차 %.2f, 95%% 구간 %.2f~%.2f' % (a / b, a / b * np.hypot(sa, sb), r.mean(), r.std(), np.percentile(r, 2.5), np.percentile(r, 97.5)))
json.dump(out, open('out/calc9-4.json', 'w'), ensure_ascii=False, indent=1)
