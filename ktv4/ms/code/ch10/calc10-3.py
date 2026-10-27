# -*- coding: utf-8 -*-
"""계산 10-3: IntCal20 곡선의 Δ14C가 서기 774~775년 급등을 얼마나 담는가, 그리고 곡선의 '평소' 해마다 변화.
곡선: data/intcal20.14c (PyPI 패키지 radiocarbon 0.5.0 안의 파일, SHA-256 0c553685...fbd6a8; 제3권에서 쓴 것과 같은 복사본).
열: cal BP, 14C BP, 14C 오차, Δ14C(‰), Δ14C 오차. 곡선 논문의 서지는 이 작업에서 확인하지 못했다(서지 확인 필요).
0~5000 cal BP는 1년 간격, 5000~13,900 cal BP는 5년 간격이다. 서기 연도 = 1950 − cal BP.
"""
import os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
c = np.loadtxt(os.path.join(HERE, 'data', 'intcal20.14c'), delimiter=',')
c = c[np.argsort(c[:, 0])]
t, d14, sd = c[:, 0], c[:, 3], c[:, 4]
out = {}
m = t <= 5000
tt, dd = t[m], d14[m]
print('=== 계산 10-3 (1) 0~5000 cal BP의 해마다 변화(1년 간격 구간) ===')
for step in (1, 2, 5, 10):
    ch = dd[step:] - dd[:-step]
    i = np.argmax(np.abs(ch)); j = np.argsort(-np.abs(ch))[:3]
    print('  %2d년 차: 중앙 |변화| %.2f ‰, 표준편차 %.2f ‰, 최대 |변화| %.1f ‰ (서기 %d~%d)' % (step, np.median(np.abs(ch)), ch.std(), np.abs(ch[i]), 1950 - tt[i + step], 1950 - tt[i]))
    out['max_%d' % step] = float(np.abs(ch[i])); out['med_%d' % step] = float(np.median(np.abs(ch)))
ch1 = np.abs(dd[1:] - dd[:-1])
print('  1년 변화가 가장 큰 5곳(서기):', ', '.join('%d(%.1f‰)' % (1950 - tt[k], ch1[k]) for k in np.argsort(-ch1)[:5]))
print('\n=== 계산 10-3 (2) 서기 770~780의 곡선 값 ===')
for y in range(770, 782):
    j = np.where(t == 1950 - y)[0][0]
    print('  서기 %d: Δ14C %.1f ± %.1f ‰, 14C 연대 %d BP' % (y, d14[j], sd[j], c[j, 1]))
j770 = np.where(t == 1950 - 770)[0][0]; j775 = np.where(t == 1950 - 775)[0][0]; j780 = np.where(t == 1950 - 780)[0][0]
print('  곡선의 Δ14C(서기 775) − Δ14C(서기 770) = %+.1f ‰, Δ14C(서기 780) − Δ14C(서기 775) = %+.1f ‰' % (d14[j775] - d14[j770], d14[j780] - d14[j775]))
rise = d14[j775] - d14[j770]
print('  서기 770 → 775의 상승 %.1f ‰; Brehm 등(2022) 표 1의 775 CE 상승 17.6 ± 0.5 ‰와 견주면 곡선은 %.0f%%' % (rise, 100 * rise / 17.6))
out['rise_770_775'] = float(rise); out['curve_vs_brehm'] = float(rise / 17.6)
print('\n=== 계산 10-3 (3) 서기 993~994 사건 둘레 ===')
for y in range(988, 1000):
    j = np.where(t == 1950 - y)[0][0]
    print('  서기 %d: Δ14C %.1f ‰' % (y, d14[j]))
j990 = np.where(t == 1950 - 990)[0][0]; j995 = np.where(t == 1950 - 995)[0][0]
print('  서기 990 → 995: %+.1f ‰' % (d14[j995] - d14[j990]))
out['rise_990_995'] = float(d14[j995] - d14[j990])
print('\n=== 계산 10-3 (4) 5000~11,000 cal BP(5년 간격) 10년 차이 ===')
m2 = (t >= 5000) & (t <= 11000)
t2, d2 = t[m2], d14[m2]
ch = d2[2:] - d2[:-2]
i = np.argmax(np.abs(ch))
print('  10년(두 칸) 차: 중앙 |변화| %.1f ‰, 최대 |변화| %.1f ‰ (cal BP %d~%d)' % (np.median(np.abs(ch)), np.abs(ch[i]), t2[i], t2[i + 2]))
print('  같은 10년 차의 1~5000 cal BP 구간: 중앙 %.1f ‰, 최대 %.1f ‰' % (out['med_10'], out['max_10']))
out['max10_early'] = float(np.abs(ch[i])); out['med10_early'] = float(np.median(np.abs(ch)))
print('  이 곡선은 평활화한 것이라 한 해 안의 급등(2년에 약 19‰)은 5년 간격 구간에서 보이지 않는다. 기원전 7176, 5259년 사건이 이 곡선에서 어떻게 나타나는지를 이 책은 시험하지 않았다(해당 구간은 5년 간격).')
for lab, cp in (('7176 BCE', 7176 + 1949), ('5259 BCE', 5259 + 1949)):
    j = np.argmin(np.abs(t - cp))
    print('  %s ≈ cal BP %d 둘레(곡선 값, ‰): ' % (lab, cp) + ', '.join('%d:%.1f' % (t[k], d14[k]) for k in range(j - 3, j + 4)))
json.dump(out, open('out/calc10-3.json', 'w'), ensure_ascii=False, indent=1)
