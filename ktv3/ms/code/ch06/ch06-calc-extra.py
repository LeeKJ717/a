# -*- coding: utf-8 -*-
"""계산 6-8: 서아시아 점추정의 독립성 점검과 Scuderi 등(2019)의 사이트 집계. 입력은 6장 본문 표의 논문 값."""
import numpy as np
from scipy import stats

def wmean(v, s):
    v = np.array(v, float); s = np.array(s, float); w = 1 / s**2
    m = (v * w).sum() / w.sum(); e = (1 / w.sum())**0.5
    q = (w * (v - m)**2).sum(); df = len(v) - 1
    return m, e, q, df, 1 - stats.chi2.cdf(q, df)

print('== 계산 6-8: 서아시아 점추정의 독립성 점검 ==')
sets = {
 '넷 모두(골, 오만만 초록, 홍해, 오만만 인용)': ([4260, 4025, 4200, 4100], [66, 125, 100, 100]),
 '오만만 인용값을 뺀 셋(오만만이 같은 코어라면)': ([4260, 4025, 4200], [66, 125, 100]),
 '오만만 초록값을 뺀 셋': ([4260, 4200, 4100], [66, 100, 100]),
 '골과 홍해만': ([4260, 4200], [66, 100]),
}
for k, (v, s) in sets.items():
    m, e, q, df, p = wmean(v, s)
    print('  %-34s 가중평균 %.1f ± %.1f, Q = %.2f, 자유도 %d, p = %.3f' % (k, m, e, q, df, p))
print('  Carolin 등이 인용한 오만만 값(4100 ± 100)과 Cullen 등 초록(4025 ± 125)의 차 = %d, 합성 오차 %.1f, z = %.2f' % (75, (100**2 + 125**2)**0.5, 75 / (100**2 + 125**2)**0.5))
print()
print('== Scuderi 등(2019) 사이트 집계 ==')
print('  4.2 ka 증거가 불분명하거나 없는 사이트 18곳 / 77곳 = %.1f%%' % (18 / 77 * 100))
print('  뒷받침하는 사이트(77 - 18) = %d곳 (%.1f%%)' % (77 - 18, (77 - 18) / 77 * 100))
lo, hi = stats.beta.ppf([0.025, 0.975], [18, 18 + 1][0:1] * 1 + [0], [1, 1]) if False else (None, None)
# Clopper-Pearson 95% 구간
k, n = 18, 77
lo = stats.beta.ppf(0.025, k, n - k + 1); hi = stats.beta.ppf(0.975, k + 1, n - k)
print('  비율 18/77 의 95%% 정확 구간(Clopper-Pearson) = %.1f%% ~ %.1f%%' % (lo * 100, hi * 100))
print('  Railsback 등(2018) 4.15~3.93 ka 구간 길이 = %d년, 중심 4070' % (4150 - 3930))
