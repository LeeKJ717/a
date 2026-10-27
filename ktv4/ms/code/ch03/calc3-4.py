# -*- coding: utf-8 -*-
"""계산 3-4: Beck 등(2018) 북 그린란드 메탄 자료표(약 3행마다 옮긴 표본 234점)로 홀로세 메탄의 모양을 다시 본다.
논문 서술: 첫 절반에 약 100 ppb 감소, 최소는 약 5400 yr BP 부근, 이후 상승. 그린란드가 남극보다 평균 약 45 ppb 높다. Ruddiman(2003): 5 ka 부터 상승.
8.2 ka 부근의 짧은 감소도 표에서 읽는다.
"""
import numpy as np
import common3 as C
t, y, org = C.ch4()
print('=== 계산 3-4 (1) 표 점검 ===')
print('표본 %d점, 나이 %.1f~%.1f cal yr BP, 나이 오름차순 %s' % (len(t), t.min(), t.max(), bool(np.all(np.diff(t) > 0))))
u, c = np.unique(org, return_counts=True)
print('자료 출처 표시별 점 수:', dict(zip(u, c)))
print('산업화 영향을 피하려고 200 cal yr BP 보다 어린 점은 뺀다(%d점 제외).' % (t < 200).sum())
k = t >= 200; t2, y2 = t[k], y[k]
print()
print('=== (2) 500년 칸 중앙값 ===')
lo = np.arange(200, 11700, 500)
med = []
for a in lo:
    kk = (t2 >= a) & (t2 < a + 500)
    if kk.sum() < 3: continue
    med.append((a, kk.sum(), np.median(y2[kk]), y2[kk].mean()))
    print('%5d~%5d  n=%2d  중앙값 %.1f  평균 %.1f ppb' % (a, a + 500, kk.sum(), med[-1][2], med[-1][3]))
med = np.array(med)
imin = int(np.argmin(med[:, 2]))
print('중앙값이 가장 낮은 칸: %d~%d yr BP, %.1f ppb' % (med[imin, 0], med[imin, 0] + 500, med[imin, 2]))
print('칸 중앙값이 가장 높은 칸(10 ka 이전): %.1f ppb (%d~%d yr BP)' % (med[med[:, 0] >= 9000, 2].max(), med[med[:, 0] >= 9000][np.argmax(med[med[:, 0] >= 9000, 2]), 0], med[med[:, 0] >= 9000][np.argmax(med[med[:, 0] >= 9000, 2]), 0] + 500))
early = med[(med[:, 0] >= 9500) & (med[:, 0] < 11500)]
print('9.5~11.5 ka 칸 중앙값의 평균 %.1f ppb' % early[:, 2].mean())
late = med[(med[:, 0] >= 200) & (med[:, 0] < 1200)]
print('0.2~1.2 ka 칸 중앙값의 평균 %.1f ppb' % late[:, 2].mean())
mid = med[imin, 2]
print('최소 칸 -> 0.2~1.2 ka 평균: +%.1f ppb. 9.5~11.5 ka 평균 -> 최소 칸: %.1f ppb.' % (late[:, 2].mean() - mid, mid - early[:, 2].mean()))
print('(논문: 첫 절반에 약 100 ppb 감소. 이 표본은 최소 칸까지 %.0f ppb 감소. Ruddiman(2003)이 본 Dome C 의 상승 100 ppb 와 견주면 이 표본의 상승 %.0f ppb. 그린란드와 남극은 평균 약 45 ppb 차이가 있으므로 절대 값이 아니라 변화량만 견줄 수 있다.)' % (early[:, 2].mean() - mid, late[:, 2].mean() - mid))
print()
print('=== (3) 꺾는 점(연속 꺾은선, 나이 200~11,000) ===')
kk = (t2 <= 11000)
x = 11.0 - t2[kk] / 1000.0; yy = y2[kk]
sse, x0, beta = C.hinge_fit(x, yy, 1.0, 9.5, step=0.05)
print('꺾는 점 나이 %.2f ka, 앞 기울기 %.1f ppb/ka, 뒤 기울기 %.1f ppb/ka, 잔차 표준편차 %.1f ppb' % (11.0 - x0, beta[1], beta[1] + beta[2], np.sqrt(sse / (len(yy) - 4))))
rng = np.random.default_rng(3403)
bs = []
for _ in range(1000):
    i = rng.integers(0, len(x), len(x))
    _, xb, _b = C.hinge_fit(x[i], yy[i], 1.0, 9.5, step=0.1); bs.append(11.0 - xb)
print('부트스트랩 1000회(시드 3403): 꺾는 점 2.5/50/97.5 백분위 = %s ka' % np.round(np.percentile(bs, [2.5, 50, 97.5]), 2))
print('논문 서술: 최소 약 5.4 ka(Beck 등), 상승 시작 약 5 ka(Singarayer 등; Ruddiman)')
print('(8.2 ka 부근의 짧은 감소가 꺾은선 맞춤에 영향을 줄 수 있으므로 7.9~8.6 ka 의 점을 빼고 한 번 더 맞춘다)')
ex = (t2 > 7900) & (t2 < 8600) & (t2 <= 11000)
sse2, x02, b2 = C.hinge_fit(11.0 - t2[kk & ~ex] / 1000.0, y2[kk & ~ex], 1.0, 9.5, step=0.05)
print('   빼고 맞춘 꺾는 점 %.2f ka, 앞 기울기 %.1f, 뒤 기울기 %.1f ppb/ka' % (11.0 - x02, b2[1], b2[1] + b2[2]))
print()
print('=== (4) 8.2 ka 부근 감소 ===')
base = (t2 >= 7700) & (t2 <= 8140)
bm = y2[base].mean(); bsd = y2[base].std(ddof=1)
print('기준(7.7~8.14 ka 표본 %d점) 평균 %.1f, 표준편차 %.1f ppb' % (base.sum(), bm, bsd))
w = (t2 >= 8140) & (t2 <= 8420)
for a, b_, v in zip(t2[w], np.arange(w.sum()), y2[w]): pass
print('8.14~8.42 ka 표본:')
for a, v in zip(t2[w], y2[w]): print('   %.1f cal yr BP  %.1f ppb' % (a, v))
imn = np.argmin(y2[w]); print('최솟값 %.1f ppb (%.1f cal yr BP), 기준 평균과의 차 %.1f ppb (= 기준 표준편차의 %.1f 배)' % (y2[w][imn], t2[w][imn], y2[w][imn] - bm, (bm - y2[w][imn]) / bsd))
below = w & (y2 < bm - 2 * bsd)
print('기준 평균 - 2 표준편차(%.1f ppb) 아래인 표본의 나이 범위: %.1f~%.1f cal yr BP (%d점, 표본이 3행에 하나이므로 지속 시간은 아래쪽 한계 값)' % (bm - 2 * bsd, t2[below].min(), t2[below].max(), below.sum()))
print('그 범위의 길이 %.0f 년' % (t2[below].max() - t2[below].min()))
