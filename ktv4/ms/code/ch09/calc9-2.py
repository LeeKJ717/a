# -*- coding: utf-8 -*-
"""계산 9-2: eVolv2k(Toohey & Sigl 2017, ESSD 9, 809)의 가장 큰 열 개와 불확도, 복사강제력 대비(Büntgen 등 2016), 냉각 크기 서술(McConnell 등 2020 외).
입력은 논문 표와 본문의 숫자. 불확도가 논문에 없는 사건의 1시그마는 20%로 둔 시연값이다.
"""
import json, math
import numpy as np
rng = np.random.default_rng(20261027)
out = {}
top = [('1257 사말라스', 59.4, 0.18), ('기원전 426', 59.3, None), ('기원전 44', 38.6, None), ('1458', 33.0, 0.15), ('540', 31.8, 0.24),
       ('1815 탐보라', 28.1, 0.16), ('682', 27.2, None), ('574', 24.1, None), ('1230', 23.8, None), ('266', 21.9, None)]
print('=== 계산 9-2 (1) 사말라스와 탐보라 ===')
S, T = 59.4, 28.1; sS, sT = 0.18 * S, 0.16 * T
print('  VSSI: 사말라스 %.1f ± %.1f (1σ 18%%), 탐보라 %.1f ± %.1f (1σ 16%%) Tg S' % (S, sS, T, sT))
ratio = S / T; sr = ratio * math.sqrt(0.18 ** 2 + 0.16 ** 2)
print('  비 S/T = %.2f, 오차 전파(두 오차가 독립이라 가정) 1σ = %.2f → 비의 1σ 구간 %.2f~%.2f. Guillet 등(2017)의 "탐보라의 두 배"가 이 구간에 든다' % (ratio, sr, ratio - sr, ratio + sr))
d = S - T; sd = math.hypot(sS, sT)
print('  차이 %.1f ± %.1f Tg S → %.1fσ' % (d, sd, d / sd))
out['ratio'] = ratio; out['ratio_sd'] = sr; out['diff_sigma'] = d / sd
print('\n=== 계산 9-2 (2) 상위 열 개의 순위는 오차 안에서 얼마나 흔들리는가(시연) ===')
names = [t[0] for t in top]; mu = np.array([t[1] for t in top]); sg = np.array([(t[2] if t[2] is not None else 0.20) for t in top]) * mu
N = 200000
draw = rng.normal(mu, sg, size=(N, len(top)))
rank = (-draw).argsort(axis=1).argsort(axis=1) + 1
print('  1σ 비율: 사말라스 18%%, 1458 15%%, 540 24%%, 탐보라 16%%(논문), 나머지 20%%(시연값). 정규분포 %d번 추출' % N)
print('  %-14s %6s %6s %9s %9s %9s' % ('사건', 'VSSI', '1σ', '중앙순위', '순위 5~95%', 'P(1위)'))
res = []
for i, nm in enumerate(names):
    r = rank[:, i]
    p1 = (r == 1).mean()
    print('  %-14s %6.1f %6.1f %9.0f %5d~%-4d %9.3f' % (nm, mu[i], sg[i], np.median(r), np.percentile(r, 5), np.percentile(r, 95), p1))
    res.append(dict(name=nm, vssi=mu[i], sd=sg[i], med=float(np.median(r)), lo=float(np.percentile(r, 5)), hi=float(np.percentile(r, 95)), p1=float(p1)))
out['rank'] = res
pS_gt_426 = (draw[:, 0] > draw[:, 1]).mean()
print('  P(사말라스 > 기원전 426) = %.3f (59.4 대 59.3)' % pS_gt_426)
pT_top5 = (rank[:, 5] <= 5).mean()
print('  P(탐보라가 이 열 개 가운데 5위 이내) = %.3f' % pT_top5)
out['pT_top5'] = pT_top5
out['p_S_gt_426'] = pS_gt_426
print('  상위 열 개에서 가장 작은 값(21.9)과 가장 큰 값(59.4)의 비 = %.2f' % (59.4 / 21.9))
print('  참고: 탐보라 대비 각 사건의 VSSI 비: ' + ', '.join('%s %.2f' % (n, v / T) for n, v, _ in top))
print('\n=== 계산 9-2 (3) 복사강제력 대비 VSSI (Büntgen 등 2016의 강제력, 두 편찬본의 VSSI) ===')
rows = [('탐보라 1815', 17.2, 28.1, 'eVolv2k 표 2'), ('540', 19.1, 31.8, 'eVolv2k 표 2'), ('536', 11.3, 19.0, 'HolVol 표 4(다른 편찬본)')]
for n, f, v, src in rows:
    print('  %-10s 강제력 −%.1f W/m², VSSI %.1f Tg S → %.3f W/m² per Tg S (%s)' % (n, f, v, f / v, src))
print('  540 대 탐보라: 강제력 비 %.3f, VSSI 비 %.3f' % (19.1 / 17.2, 31.8 / 28.1))
out['force_ratio'] = 19.1 / 17.2; out['vssi_ratio'] = 31.8 / 28.1
print('  536년의 VSSI 19 Tg S는 HolVol(2022)의 값이고, 강제력 11.3은 Büntgen 등(2016) Fig. 2c의 값이다. 두 값의 출처가 다르므로 위 비는 어림이다.')
print('\n=== 계산 9-2 (4) 나이테 숫자의 산술(Büntgen 등 2016) ===')
print('  660 = 살아 있는 나무 152 + 유물 나무 508 → %d. 측정 234,399개 / 660 계열 = %.0f 개/계열' % (152 + 508, 234399 / 660))
print('  후기 고대 소빙기 536년~약 660년 = %d 년' % (660 - 536))
print('  알타이 여름 기온 극값: 가장 추운 해 172년 −4.6, 가장 따뜻한 해 982년 +1.6 → 폭 %.1f ℃' % (4.6 + 1.6))
print('  540년대 10년: 알타이 −3.2 ℃, 알프스 −1.9 ℃ → 알타이/알프스 = %.2f' % (3.2 / 1.9))
out['altai_alps'] = 3.2 / 1.9
print('\n=== 계산 9-2 (5) 냉각 크기에 관한 서술을 한 줄에 놓기 ===')
cool = [('Stoffel 등(2015) 1257, 1815 북반구 육지 여름 냉각(재구성과 모의가 모두 같은 범위)', 0.8, 1.3),
        ('Mann 등(2012)이 1258~1259 강제력에서 "보통 기대"한 냉각', 2.0, 2.0),
        ('McConnell 등(2020) CESM 모의 43 BCE 북반구 여름', 2.0, 3.0),
        ('McConnell 등(2020) 유럽 나이테 43 BCE 여름', 3.0, 3.0),
        ('McConnell 등(2020) 지중해 모의 계절 냉각(남유럽, 북아프리카 일부)', 0.7, 7.4)]
for n, a, b in cool:
    print('  %-60s %.1f ~ %.1f ℃' % (n, a, b))
print('  Mann 등(2012)의 기대 2.0 ℃ 대 Stoffel 등(2015)의 상한 1.3 ℃ → 비 %.2f (두 값은 대상 사건과 정의가 달라 어림)' % (2.0 / 1.3))
print('  43 BCE 유럽 나이테 ">3 ℃"는 같은 논문의 북반구 모의 2~3 ℃의 상한 이상이지만 둘은 지역(유럽)과 범위(북반구)가 다르다')
print('\n=== 계산 9-2 (6) 오카모크 43 BCE의 빙핵 2년 황 침적(McConnell 등 2020) ===')
dep = {'NGRIP2': 123, 'NEEM': 110, 'GISP2': 131, 'GRIP': 135, 'Dye3': 128}
v = np.array(list(dep.values()), float)
print('  값(kg/km²): ' + ', '.join('%s %d' % kv for kv in dep.items()))
print('  평균 %.1f, 표준편차 %.1f (%.1f%%), 최대/최소 = %.2f' % (v.mean(), v.std(ddof=1), 100 * v.std(ddof=1) / v.mean(), v.max() / v.min()))
print('  Sigl 등(2022)이 적은 그린란드 플럭스 1σ 33%%와 견주면 코어 사이 흩어짐(%.1f%%)은 훨씬 작다. 코어 사이의 일치가 곧 정확도는 아니다.' % (100 * v.std(ddof=1) / v.mean()))
print('  Marshall 등(2018)이 적은 탐보라의 빙핵 유도 침적 "대략 50 kg/km²"와 견주면 평균/50 = %.2f (플럭스 정의와 기간이 다를 수 있어 어림)' % (v.mean() / 50))
out['okmok_mean'] = float(v.mean()); out['okmok_cv'] = float(v.std(ddof=1) / v.mean())
json.dump(out, open('out/calc9-2.json', 'w'), ensure_ascii=False, indent=1)
