# -*- coding: utf-8 -*-
"""계산 3-5: 논문들이 적은 홀로세 이산화탄소 변화량(초기 약 5 ppm 감소, 후기 약 20 ppm 상승)을 두 코어 표로 다시 구하고,
후기 상승의 속도(ppm/ka)를 부트스트랩 구간과 함께 낸다.
논문 숫자: Elsig 등(2009) 초기 약 5 ppm 감소, 후기 약 20 ppm 상승. Joos 등(2004) 8 ka~산업화 이전 20 ppm. Ruddiman(2003) 관측된 상승 20~25 ppm, 최근 8000년.
"""
import numpy as np
import common3 as C
te, ye, se, de = C.edc(); tt, yt, st, dt = C.taylor()
def binmean(t, y, a, b):
    k = (t >= a) & (t < b); return k.sum(), y[k].mean(), y[k].std(ddof=1)
print('=== 계산 3-5 (1) 초기 감소와 후기 상승 ===')
for nm, t, y, hi in (('Dome C', te, ye, 11000), ('Taylor Dome', tt, yt, 11200)):
    n1, m1, s1 = binmean(t, y, 10000, hi)
    n2, m2, s2 = binmean(t, y, 7000, 8500)
    n3, m3, s3 = binmean(t, y, 390 if nm.startswith('T') else 170, 2000)
    print('%-12s 정점 칸(10 ka~) %.1f (n=%d) -> 7~8.5 ka 칸 %.1f (n=%d): 변화 %+.1f ppm.  7~8.5 ka 칸 -> 최근 2 ka 칸 %.1f (n=%d): 변화 %+.1f ppm' % (nm, m1, n1, m2, n2, m2 - m1, m3, n3, m3 - m2))
    # 단순 표준오차
    se_ = np.sqrt(s2 ** 2 / n2 + s3 ** 2 / n3)
    print('             후기 상승의 단순 표준오차(두 칸 평균의 표준오차 합성) %.2f ppm' % se_)
print('논문: Elsig 등(2009)의 초기 감소 약 5 ppm, 후기 상승 약 20 ppm; Joos 등(2004) 20 ppm; Ruddiman(2003) 관측 상승 20~25 ppm')
print()
print('=== (2) 후기 상승 속도: 선형 맞춤(나이 400~6000 yr BP) ===')
rng = np.random.default_rng(3405)
for nm, t, y in (('Dome C', te, ye), ('Taylor Dome', tt, yt)):
    k = (t >= 400) & (t <= 6000)
    x = -t[k] / 1000.0        # 시간 방향(과거->현재)으로 증가
    p = np.polyfit(x, y[k], 1)
    r = y[k] - np.polyval(p, x)
    bs = []
    for _ in range(2000):
        i = rng.integers(0, k.sum(), k.sum()); bs.append(np.polyfit(x[i], y[k][i], 1)[0])
    print('%-12s n=%d  기울기 %.2f ppm/ka (부트스트랩 95%% 구간 %.2f~%.2f)  잔차 표준편차 %.2f ppm' % (nm, k.sum(), p[0], *np.percentile(bs, [2.5, 97.5]), r.std(ddof=2)))
print('Ruddiman(2003) 20~25 ppm 이 8000년에 걸쳤다면 평균 %.2f~%.2f ppm/ka.  Joos 등(2004) 20 ppm/8 ka = %.2f ppm/ka' % (20 / 8, 25 / 8, 20 / 8))
print('(꺾는 점 이후 구간에서 직선 맞춤은 구간 고르기에 민감하다. 위는 400~6000 yr BP 한 가지 선택이다.)')
print()
print('=== (3) 서로 다른 두 코어의 칸별 평균 차 ===')
print('칸        Dome C   Taylor   차(T - D)')
DIFFS = []
for a in range(0, 11000, 1000):
    n1, m1, _ = binmean(te, ye, a, a + 1000)
    kk = (tt >= a) & (tt < a + 1000)
    n2 = int(kk.sum()); m2 = yt[kk].mean() if n2 else float('nan')
    DIFFS.append((a, n2, m2 - m1))
    print('%5d~%5d  %.1f(%2d)  %.1f(%2d)  %+.1f' % (a, a + 1000, m1, n1, m2, n2, m2 - m1))
ok = [d for d in DIFFS if d[1] >= 4]
print('Taylor Dome 점이 4개 이상인 칸만 보면 차는 %+.1f~%+.1f ppm (평균 %+.1f). 20 ppm 상승에 견주면 작지만 5 ppm 감소와는 비슷한 크기다.' % (min(d[2] for d in ok), max(d[2] for d in ok), np.mean([d[2] for d in ok])))
