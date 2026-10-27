# -*- coding: utf-8 -*-
"""계산 2-6: 홀로세 '최적기' 서술 구간의 산술, 두 파일의 칸 평균 비교, 시간 눈금을 밀었을 때 상관의 변화.
논문 값(구간, ka): Johnsen 등(2001) NorthGRIP 홀로세 최적 약 8.6~4.3; Vinther 등(2009) 홀로세 기후 최적(온도 최대) 약 9~6 (b2k); Masson 등(2000) 남극 11개 코어 초기 최적 11.5~9,
         로스해 쪽 2차 최적 7~5, 동남극 후기 최적 6~3; Mulvaney 등(2012) 제임스 로스섬 따뜻하고 안정한 시기 9.2~2.5.
"""
import numpy as np
from io2 import gisp2, edc
W = [('Johnsen 등(2001) NorthGRIP 최적', 8.6, 4.3), ('Vinther 등(2009) 그린란드 최적', 9.0, 6.0), ('Masson 등(2000) 남극 초기 최적(전 코어)', 11.5, 9.0),
     ('Masson 등(2000) 로스해 쪽 2차', 7.0, 5.0), ('Masson 등(2000) 동남극 후기', 6.0, 3.0), ('Mulvaney 등(2012) 제임스 로스섬', 9.2, 2.5)]
print('=== 계산 2-6 (1) 서술된 최적기 구간의 길이와 겹침 (ka, 서로 다른 기준 연대의 혼합이며 각 끝점의 불확실성은 쓰지 않음) ===')
for nm, a, b in W: print('  %-40s %.1f ~ %.1f ka  길이 %.1f ka' % (nm, a, b, a - b))
print('  겹침(ka):')
for i in range(len(W)):
    for j in range(i + 1, len(W)):
        lo = max(W[i][2], W[j][2]); hi = min(W[i][1], W[j][1])
        ov = max(0.0, hi - lo)
        print('    %-40s x %-40s %.1f ka' % (W[i][0], W[j][0], ov))
print()
g = gisp2(); e = edc()
def binned(t, y, a, b, w):
    edges = np.arange(a, b + w, w); c = []; v = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (t >= lo) & (t < hi)
        if m.sum() >= 3: c.append((lo + hi) / 2); v.append(y[m].mean())
        else: c.append((lo + hi) / 2); v.append(np.nan)
    return np.array(c), np.array(v)
print('=== 계산 2-6 (2) GISP2 d18O 와 EDC 온도의 500년 칸 평균 상관과 시간 눈금 이동 ===')
def corr_shift(s, lo=500, hi=11000, w=500, use='T'):
    # GISP2 나이에 s 년을 더한다(양수면 더 오래된 쪽으로 이동)
    c, a = binned(g.age.values + s, g.d18o.values, lo, hi, w)
    c2, b = binned(e.age.values, e[use].values, lo, hi, w)
    m = ~np.isnan(a) & ~np.isnan(b)
    return np.corrcoef(a[m], b[m])[0, 1], m.sum()
for lo, hi, lab in ((500, 11000, '0.5~11 ka'), (500, 10000, '0.5~10 ka'), (500, 9000, '0.5~9 ka')):
    r, n = corr_shift(0, lo, hi)
    r2, _ = corr_shift(0, lo, hi, use='dD')
    print('  %-10s 칸 %d개: 상관(GISP2 d18O, EDC 파일 T) %.2f, 상관(GISP2 d18O, EDC dD) %.2f' % (lab, n, r, r2))
print('  시간 눈금을 GISP2 에서만 s 년 이동(0.5~11 ka, 500년 칸):')
for s in (-300, -200, -99, -47, 0, 47, 99, 200, 300):
    r, n = corr_shift(s)
    print('    s = %+4d 년: r = %.2f' % (s, r))
print('  500년 칸은 99년 이동에 둔감하다. 같은 이동을 160년짜리 사건(8.2 ka 사건)에 적용하면:')
for s in (47, 99):
    print('    이동 %d 년이면 160년 구간의 겹침 %d 년 (%.0f%%)' % (s, 160 - s, 100 * (160 - s) / 160))
print()
print('=== 계산 2-6 (3) 1000년 칸 평균 GISP2 d18O 의 칸 사이 차이 대 사건 크기 ===')
c, v = binned(g.age.values, g.d18o.values, 0, 12000, 1000)
inner = v[1:9]
print('  1~9 ka 칸 평균 범위 %.2f 퍼밀. 8.2 ka 사건 가장 낮은 표본의 기준선 대비 %.2f 퍼밀(계산 2-3), 영거 드라이아스 계단 5.55 퍼밀(계산 2-2)' % (inner.max() - inner.min(), 1.86))
print('  칸 사이 범위 / 8.2 ka 사건 깊이 = %.2f, / 영거 드라이아스 계단 = %.3f' % ((inner.max() - inner.min()) / 1.86, (inner.max() - inner.min()) / 5.55))
