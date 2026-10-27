# -*- coding: utf-8 -*-
"""계산 2-3: 8.2 ka 사건을 GISP2 d18O(2 m 표본)에서 다시 찾는다.
논문 값(b2k): 사건은 약 8300 에서 8140 b2k, 길이 160 ± 10 년, d18O 진폭 1~2 퍼밀(Rasmussen 등 2007, 세 코어 합성); 사건 구간 160.5 년, 중심부 69 년(Thomas 등 2007, 코어 네 개 합성);
         북그리피안 경계 8236 b2k, 최대 계수 오차 47 년(Walker 등 2018). BP = b2k - 50.
"""
import numpy as np
from io2 import gisp2
g = gisp2()
t = g.age.values; y = g.d18o.values
def win(a, b): return (t >= a) & (t <= b)
print('=== 계산 2-3 (1) 기준선과 사건 구간 ===')
base = y[win(8400, 9400)]; bt = t[win(8400, 9400)]
print('기준선 8.4~9.4 ka BP: 표본 %d개, 평균 %.2f, 표준편차 %.2f 퍼밀 (표본 간격 %.1f 년)' % (len(base), base.mean(), base.std(ddof=1), np.diff(bt).mean()))
sd = base.std(ddof=1); mu = base.mean()
ev = win(7900, 8400)
print('7.9~8.4 ka BP 표본:')
sel = np.where(ev)[0]
below1 = [i for i in sel if y[i] < mu - sd]
below2 = [i for i in sel if y[i] < mu - 2 * sd]
print('  기준선 평균 - 1 표준편차(%.2f) 아래인 표본 %d개: 나이 %s' % (mu - sd, len(below1), ', '.join('%.0f' % t[i] for i in below1)))
print('  기준선 평균 - 2 표준편차(%.2f) 아래인 표본 %d개: 나이 %s' % (mu - 2 * sd, len(below2), ', '.join('%.0f' % t[i] for i in below2)))
imin = sel[np.argmin(y[sel])]
print('  가장 낮은 표본: %.0f BP (= %.0f b2k), d18O %.2f, 기준선 평균보다 %.2f 퍼밀 낮음 (= %.1f 표준편차)' % (t[imin], t[imin] + 50, y[imin], y[imin] - mu, (y[imin] - mu) / sd))
print()
print('=== 계산 2-3 (2) 사건 구간: 기준선 평균 - k 표준편차 아래로 이어지는 가장 긴 묶음 ===')
def longest_run(tt, yy, mu, sd, kk, lo=7900, hi=8400):
    idx = [i for i in range(len(tt)) if lo <= tt[i] <= hi and yy[i] < mu - kk * sd]
    runs = []; cur = []
    for i in idx:
        if cur and i != cur[-1] + 1: runs.append(cur); cur = []
        cur.append(i)
    if cur: runs.append(cur)
    return max(runs, key=len) if runs else []
print('  (표본은 나이가 늘어나는 차례. 길이 = 첫 표본과 끝 표본의 나이 차 + 표본 간격 한 칸)')
RES = {}
for kk in (1.0, 1.5, 2.0, 3.0):
    G = longest_run(t, y, mu, sd, kk)
    if not G: print('  k=%.1f: 묶음 없음' % kk); continue
    sp = np.diff(t[G]).mean() if len(G) > 1 else np.nan
    a, b = t[G[0]], t[G[-1]]
    dur = b - a + (sp if sp == sp else 0)
    RES[kk] = (a, b, dur, len(G))
    print('  k=%.1f (표본 기준 %.2f 아래): %d 표본, %.0f ~ %.0f BP (%.0f ~ %.0f b2k), 길이 %.0f 년, 묶음 평균 %.2f 퍼밀' % (kk, mu - kk * sd, len(G), a, b, a + 50, b + 50, dur, y[G].mean()))
print()
print('=== 계산 2-3 (3) 논문 값과 견줌 (모두 b2k) ===')
a, b, dur, n = RES[1.0]
cen = (a + b) / 2 + 50
print('이 책(k=1, Thomas 등이 쓴 "앞선 평균보다 1 표준편차 이상 낮음"과 같은 기준): 사건 구간 %.0f ~ %.0f b2k, 길이 %.0f 년, 가장 낮은 표본 %.0f b2k, 구간 중심 %.0f b2k' % (a + 50, b + 50, dur, t[imin] + 50, cen))
print('Rasmussen 등(2007): 8300 ~ 8140 b2k, 길이 160 ± 10, 중심 8220 (산술)')
print('Thomas 등(2007): 길이 160.5 년, 중심부 69 년')
print('Walker 등(2018): 북그리피안 경계 8236 b2k ± 47 (최대 계수 오차)')
print('이 책 중심 - 8220 = %+.0f 년. 이 책 가장 낮은 표본 - 8236 = %+.0f 년. 이 책 길이(k=1) - 160 = %+.0f 년' % (cen - 8220, t[imin] + 50 - 8236, dur - 160))
print('기준을 k=2 로 바꾸면 길이는 %.0f 년(k=1 은 %.0f 년)으로 %.0f 년 줄어든다 -> 길이는 기준 선택에 따라 크게 달라진다' % (RES[2.0][2], RES[1.0][2], RES[1.0][2] - RES[2.0][2]))
print()
print('=== 계산 2-3 (4) 표본 간격 민감도: 표본을 하나 건너 뽑아(간격 약 2배) 같은 방식(k=2)으로 다시 정함 ===')
for off in (0, 1):
    tt = t[off::2]; yy = y[off::2]
    m = (tt >= 8400) & (tt <= 9400); mu2 = yy[m].mean(); sd2 = yy[m].std(ddof=1)
    G = longest_run(tt, yy, mu2, sd2, 2.0)
    if G:
        sp = np.diff(tt[G]).mean() if len(G) > 1 else np.nan
        print('  시작 표본 %d: 간격 %.0f 년, 묶음 %d 표본, %.0f ~ %.0f BP, 길이 %.0f 년' % (off, np.diff(tt[(tt >= 7900) & (tt <= 8400)]).mean(), len(G), tt[G[0]], tt[G[-1]], tt[G[-1]] - tt[G[0]] + sp))
    else:
        print('  시작 표본 %d: 묶음 없음' % off)
print()
print('=== 계산 2-3 (5) 같은 크기의 잡음만으로 이런 묶음이 생길 확률 (시연: 기준선과 같은 표준편차의 독립 잡음) ===')
rng = np.random.default_rng(20261027)
nrun = 0; N = 20000; L = []
n_samp = len(t[(t >= 7900) & (t <= 8400)])
for _ in range(N):
    z = rng.normal(mu, sd, n_samp)
    ok = z < mu - 2 * sd
    best = 0; cur = 0
    for v in ok:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    L.append(best)
L = np.array(L)
print('  7.9~8.4 ka 표본 %d개에 평균 %.2f, 표준편차 %.2f 인 정규 잡음을 %d번 만들어 -2 표준편차 아래로 이어지는 묶음의 최대 길이를 센다.' % (n_samp, mu, sd, N))
print('  (참고: 이 시험은 -2 표준편차 아래 묶음을 세므로 아래의 실제 묶음은 k=2 의 6 표본과 견주어야 한다)')
print('  실제 자료의 묶음은 %d 표본. 잡음에서 최대 묶음이 %d 표본 이상인 비율: %.5f (3 이상 %.4f, 2 이상 %.3f)' % (RES[2.0][3], RES[2.0][3], (L >= RES[2.0][3]).mean(), (L >= 3).mean(), (L >= 2).mean()))
