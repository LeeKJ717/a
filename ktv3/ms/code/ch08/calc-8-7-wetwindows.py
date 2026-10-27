# -*- coding: utf-8 -*-
"""계산 8-7. 몽골 고원 남쪽과 인접 지역의 호수·꽃가루 기록 일곱 곳이 저자의 해석으로 '습윤'이라고 적은 기간을 한 줄에 놓는다.
이것은 종합이 아니라 저자들이 쓴 구간의 옮겨 적기와 산술이다. 구간의 시작과 끝은 아래 W 의 숫자 그대로이며(출처와 읽은 수준은 8.10절), 지표가 서로 다르다.
단위 표기가 논문마다 다르다(cal BP, cal yr BP, 'ka'). 이 책은 모두 cal BP로 읽었고, 그 가정은 Daihai(Li 등 2004)와 Gonghai(Chen 등 2015)에서 확인하지 못했다.
계산: (a) 시작과 끝의 범위, (b) 500년 간격 시점별로 '습윤'이라고 적힌 기록의 수, (c) 4200 cal BP 시점의 상태, (d) 쌍별 겹침(년)과 Jaccard 지수.
"""
import os, json, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
# (이름, 시작(오래된 쪽), 끝(젊은 쪽), 지표, 출처)
W = [('Bayanchagan(내몽골, 41.65°N 115.21°E)', 11000, 5000, '꽃가루·거대잔존물·안정동위원소', 'Guiot 등 2008(CPD)'),
     ('Daihai(내몽골 중부)',                   10000, 7000, '꽃가루', 'Li 등 2004'),
     ('Hulun(내몽골 북동부; 8000~6400은 몬순 강수 증가 구간)', 8000, 6400, '꽃가루', 'Wen 등 2010'),
     ('Gonghai(산시 북부)',                    7800, 5300, '꽃가루 변환함수 강수 복원', 'Chen 등 2015'),
     ('Tianchi(서북 중국)',                    6200, 2900, '호수 코어(배경 서술)', 'Li 등 2022'),
     ('Bayan Nuur(몽골 중서부)',               8500, 3000, '꽃가루 변환함수', 'Tian 등 2014'),
     ('Hovsgol(몽골 북부)',                    10570, 7240, '퇴적물 화학·광물', 'Katsuta 등 2017')]
names = [w[0] for w in W]; lo = np.array([w[2] for w in W]); hi = np.array([w[1] for w in W])
out = {'records': [dict(name=w[0], start=w[1], end=w[2], proxy=w[3], source=w[4]) for w in W]}
print('(a) 습윤 구간의 시작·끝(cal BP로 읽음)')
for w in W: print('  %-40s %6d ~ %5d (길이 %5d년)  %s [%s]' % (w[0], w[1], w[2], w[1] - w[2], w[3], w[4]))
print('  시작 범위 %d~%d (중앙값 %d), 끝 범위 %d~%d (중앙값 %d), 끝의 범위 폭 %d년, 끝 평균 %.0f ± 표준편차 %.0f' % (hi.min(), hi.max(), np.median(hi), lo.min(), lo.max(), np.median(lo), lo.max() - lo.min(), lo.mean(), lo.std(ddof=1)))
out['end_range'] = [int(lo.min()), int(lo.max())]; out['end_median'] = float(np.median(lo)); out['start_range'] = [int(hi.min()), int(hi.max())]
print('\n(b) 500년 간격 시점별 습윤이라고 적힌 기록 수(7곳 중)')
sl = {}
for t in range(11000, -1, -500):
    n = int(((hi >= t) & (lo <= t)).sum()); sl[t] = n
    print('  %5d cal BP: %d곳 %s' % (t, n, '#' * n))
out['slice_counts'] = sl
t = 4200
wet = [names[i] for i in range(len(W)) if hi[i] >= t >= lo[i]]
gap = {names[i]: int(lo[i] - t) for i in range(len(W)) if lo[i] > t}
print('\n(c) 4200 cal BP 시점: 습윤이라고 적힌 곳 %d곳 %s' % (len(wet), wet))
print('    이미 끝난 기록의 끝이 4200보다 오래된 햇수: ' + ', '.join('%s %d년' % (k.split('(')[0], v) for k, v in sorted(gap.items(), key=lambda x: x[1])))
out['at4200'] = dict(wet=wet, ended_before_years={k: int(lo[names.index(k)] - 4200) for k in gap})
# Hulun 4400~3350 은 같은 논문이 '매우 건조'라고 쓴 구간
print('    Hulun의 같은 논문이 4400~3350을 매우 건조(Chenopodiaceae 우점)라고 적었으므로 4200은 그 안에 있다. Tianchi(6200~2900)와 Bayan Nuur(8500~3000)는 같은 시점을 습윤으로 적었다.')
print('\n(d) 쌍별 겹침(년) / Jaccard')
M = np.zeros((len(W), len(W))); J = np.zeros_like(M)
for i, j in itertools.combinations(range(len(W)), 2):
    ov = max(0, min(hi[i], hi[j]) - max(lo[i], lo[j])); un = max(hi[i], hi[j]) - min(lo[i], lo[j]) - max(0, max(lo[i], lo[j]) - min(hi[i], hi[j]))
    # 합집합 길이: 두 구간이 떨어져 있으면 두 길이의 합
    li = hi[i] - lo[i]; lj = hi[j] - lo[j]; un = li + lj - ov
    M[i, j] = M[j, i] = ov; J[i, j] = J[j, i] = ov / un
pairs = [J[i, j] for i, j in itertools.combinations(range(len(W)), 2)]
print('  쌍 %d개, Jaccard 평균 %.3f, 최소 %.3f, 최대 %.3f' % (len(pairs), np.mean(pairs), np.min(pairs), np.max(pairs)))
print('  겹침이 0인 쌍: %d개' % sum(1 for p in pairs if p == 0))
mn = min(((J[i, j], names[i], names[j]) for i, j in itertools.combinations(range(len(W)), 2)))
mx = max(((J[i, j], names[i], names[j]) for i, j in itertools.combinations(range(len(W)), 2)))
print('  가장 낮은 쌍: %s - %s (%.3f), 가장 높은 쌍: %s - %s (%.3f)' % (mn[1], mn[2], mn[0], mx[1], mx[2], mx[0]))
# 공통 구간: 7곳 모두 습윤이라고 적은 시기가 있는가
common = (hi.min(), lo.max())
print('  7곳이 모두 습윤인 구간: %s' % ('없음(가장 이른 끝 %d, 가장 늦은 시작 %d)' % (lo.max(), hi.min()) if lo.max() > hi.min() else '%d~%d' % (lo.max(), hi.min())))
out['jaccard_mean'] = float(np.mean(pairs)); out['jaccard_min'] = float(np.min(pairs)); out['jaccard_max'] = float(np.max(pairs)); out['n_zero_overlap_pairs'] = int(sum(1 for p in pairs if p == 0))
out['all_seven_wet_overlap'] = [int(lo.max()), int(hi.min())]
# 6000~7000 cal BP 에서의 상태
for t in (7000, 6400, 6000, 5500):
    print('  %d cal BP: 습윤 %d곳' % (t, int(((hi >= t) & (lo <= t)).sum())))
json.dump(out, open(os.path.join(HERE, 'calc-8-7-wetwindows.json'), 'w'), ensure_ascii=False, indent=1)
