# -*- coding: utf-8 -*-
"""계산 3-1: Dome C(Monnin 등 2004 자료표)의 홀로세 이산화탄소를 1000년 칸으로 묶고, 꺾는 점을 찾는다.
논문 값(Ruddiman 2003이 Taylor Dome 에서 읽은 값: 10~11 ka 에 268 ppm 정점, 8 ka 에 261 ppm, 최근 수천 년에 280~285 ppm)과 견준다.
"""
import numpy as np
import common3 as C
t, y, s, dep = C.edc()
print('=== 계산 3-1 (1) 표 점검 ===')
print('행 %d개, 나이 %d~%d yr BP(EDC1 연대), 깊이 오름차순 %s, 나이 오름차순 %s' % (len(t), t.min(), t.max(), bool(np.all(np.diff(dep) > 0)), bool(np.all(np.diff(t) > 0))))
m = t <= 11000
print('홀로세로 쓰는 범위(나이 <= 11,000 yr BP): %d행. 11,099 yr BP 다음 행(11,144 yr BP)부터 이산화탄소가 얼음시대 쪽 값으로 떨어진다(%.1f -> %.1f ppm)' % (m.sum(), y[t == 11099][0], y[t == 11144][0]))
print()
print('=== (2) 1000년 칸 평균(칸 안 점 수, 평균, 표준편차, 점 하나의 표준편차 평균) ===')
rows = []
for lo in range(0, 11000, 1000):
    k = (t >= lo) & (t < lo + 1000)
    if k.sum() == 0: continue
    rows.append((lo, k.sum(), y[k].mean(), y[k].std(ddof=1) if k.sum() > 1 else float('nan'), s[k].mean()))
    print('%5d~%5d  n=%2d  평균 %.1f ppm  표준편차 %.2f  (표의 점별 sigma 평균 %.2f)' % (lo, lo + 1000, k.sum(), rows[-1][2], rows[-1][3], rows[-1][4]))
means = np.array([r[2] for r in rows]); lows = np.array([r[0] for r in rows])
imin = int(np.argmin(means))
print('칸 평균이 가장 낮은 칸: %d~%d yr BP, %.1f ppm' % (lows[imin], lows[imin] + 1000, means[imin]))
print()
print('=== (3) 논문이 말한 시각의 값과 견주기 ===')
def win(a, b):
    k = (t >= a) & (t <= b); return k.sum(), y[k].mean(), y[k].std(ddof=1)
for a, b, note in ((10000, 11000, 'Ruddiman(2003)의 정점 시기 10~11 ka (논문 값 268 ppm, Taylor Dome)'), (7500, 8500, 'Ruddiman 의 8 ka 부근 (논문 값 261 ppm)'), (6500, 7500, '7 ka 부근'), (0, 1000, '최근 1000년'), (1000, 2000, '1~2 ka')):
    n, mu, sd = win(a, b)
    print('%5d~%5d  n=%2d  평균 %.1f  표준편차 %.2f   %s' % (a, b, n, mu, sd, note))
n1, m1, s1 = win(10000, 11000); n2, m2, s2 = win(7500, 8500); n3, m3, s3 = win(0, 2000)
print('정점 칸 - 8 ka 칸 = %.1f ppm (논문 268 - 261 = 7 ppm)' % (m1 - m2))
print('0~2 ka 칸 - 8 ka 칸 = %.1f ppm (논문: 20~25 ppm 상승)' % (m3 - m2))
print()
print('=== (4) 꺾는 점 찾기: 나이 100~10,800 yr BP 의 점에 연속 꺾은선을 맞춘다 ===')
k = (t >= 100) & (t <= 10800)
tt, yy = t[k] / 1000.0, y[k]
# 나이를 '현재에서 거슬러 올라간 시간'으로 쓰므로, 시간 순서(과거->현재)로 바꾸려면 x = 10.8 - t 를 쓴다.
x = 10.8 - tt
sse, x0, beta = C.hinge_fit(x, yy, 1.0, 9.0, step=0.05)
age0 = 10.8 - x0
print('꺾는 점 나이 %.2f ka. 앞 직선(과거->꺾는 점) 기울기 %.2f ppm/ka, 뒤 직선(꺾는 점->현재) 기울기 %.2f ppm/ka, 잔차 표준편차 %.2f ppm' % (age0, beta[1], beta[1] + beta[2], np.sqrt(sse / (len(yy) - 4))))
print('꺾는 점에서의 값 %.1f ppm' % beta[0])
rng = np.random.default_rng(3401)
b_age = []; b_s1 = []; b_s2 = []
for _ in range(1000):
    i = rng.integers(0, len(x), len(x))
    ss, xb, bb = C.hinge_fit(x[i], yy[i], 1.0, 9.0, step=0.1)
    b_age.append(10.8 - xb); b_s1.append(bb[1]); b_s2.append(bb[1] + bb[2])
q = lambda v: np.percentile(v, [2.5, 50, 97.5])
print('점을 되뽑는 부트스트랩 1000회(시드 3401): 꺾는 점 나이 2.5/50/97.5 백분위 = %s ka' % np.round(q(b_age), 2))
print('   앞 기울기 %s ppm/ka, 뒤 기울기 %s ppm/ka' % (np.round(q(b_s1), 2), np.round(q(b_s2), 2)))
print('   (되뽑기는 점이 서로 독립이고 표 나이가 정확하다고 가정한다. 가스 나이 오차는 넣지 않았다.)')
print('논문 서술: Ruddiman(2003) 이산화탄소는 8 ka 부터 이상한 상승을 시작. 이 책 계산의 꺾는 점은 %.2f ka.' % age0)
