# -*- coding: utf-8 -*-
"""계산 10-1: Usoskin 등(2016, A&A 587, A150)의 표 1(큰 극소기 20개)과 표 2(큰 극대기 14개)를 다시 세고 시험한다.
입력은 표의 중심 연대(기원전은 음수)와 지속 기간(년). 표에 적힌 것은 중심과 지속이며 시작과 끝은 이 책이 중심 ± 지속/2로 놓은 것이다.
논문의 문턱: 극소기 SN < 20이 30년 이상, 극대기 SN > 55가 30년 이상. 논문 본문의 합계: 극소기 20개 1460년 약 17%, 극대기 14개 750년 약 8%.
"""
import json, math
import numpy as np
from scipy import stats
rng = np.random.default_rng(20261027)
mn = [(1680, 80), (1470, 160), (1310, 80), (1030, 80), (690, 80), (-360, 80), (-750, 120), (-1385, 70), (-2450, 40), (-2855, 90), (-3325, 90),
      (-3495, 50), (-3620, 50), (-4220, 30), (-4315, 50), (-5195, 50), (-5300, 50), (-5460, 40), (-5610, 40), (-6385, 130)]
mx = [(1970, 80), (505, 50), (305, 30), (-245, 70), (-435, 50), (-2065, 50), (-2955, 30), (-3170, 100), (-3405, 50), (-3860, 50), (-6120, 40), (-6280, 40), (-6515, 70), (-6710, 40)]
out = {'minima': mn, 'maxima': mx}
dm = np.array([d for _, d in mn], float); dx = np.array([d for _, d in mx], float)
cm = np.array([c for c, _ in mn], float); cx = np.array([c for c, _ in mx], float)
print('=== 계산 10-1 (1) 합계와 시간 비율 ===')
print('  극소기 %d개, 지속 합 %d년 (논문 1460), 평균 %.1f, 중앙 %.0f, 최소 %d, 최대 %d' % (len(mn), dm.sum(), dm.mean(), np.median(dm), dm.min(), dm.max()))
print('  극대기 %d개, 지속 합 %d년 (논문 750), 평균 %.1f, 중앙 %.0f, 최소 %d, 최대 %d' % (len(mx), dx.sum(), dx.mean(), np.median(dx), dx.min(), dx.max()))
for lab, span in (('기원전 7000~기원후 2000(논문 GMAG.9k 범위) 9000년', 9000), ('기원전 7000~기원후 1900 8900년', 8900), ('기원전 6700~기원후 2000 8700년', 8700), ('8600년', 8600)):
    print('  %-48s 극소기 %.1f%%, 극대기 %.1f%%' % (lab, 100 * dm.sum() / span, 100 * dx.sum() / span))
out['sum_min'] = float(dm.sum()); out['sum_max'] = float(dx.sum())
print('  극소기 합 1460년이 정확히 17%%가 되는 기간 = %.0f년; 극대기 750년이 8%%가 되는 기간 = %.0f년' % (1460 / 0.17, 750 / 0.08))
print('  Maunder형(30~90년) 극소기 %d개, Spörer형(110년 초과) %d개, 그 사이(91~110) %d개' % (((dm >= 30) & (dm <= 90)).sum(), (dm > 110).sum(), ((dm > 90) & (dm <= 110)).sum()))
print('  Maunder(1680, 80년) 중심 ± 40 = %d~%d; Spörer(1470, 160년) = %d~%d; 두 극소기는 %d년 떨어져 있다(중심 사이)' % (1680 - 40, 1680 + 40, 1470 - 80, 1470 + 80, 1680 - 1470))
print('  표 1과 표 2 끝 연대의 합계 확인: 극소기 중심이 기원전인 것 %d개, 기원후 %d개; 극대기 기원전 %d개, 기원후 %d개' % ((cm < 0).sum(), (cm > 0).sum(), (cx < 0).sum(), (cx > 0).sum()))
print('\n=== 계산 10-1 (2) 극소기 사이의 기다림(중심 사이 간격) ===')
cs = np.sort(cm); gaps = np.diff(cs)
print('  정렬한 중심 연대: ' + ', '.join('%d' % c for c in cs))
print('  간격(년): ' + ', '.join('%d' % g for g in gaps))
cv = gaps.std(ddof=1) / gaps.mean()
print('  간격 평균 %.0f, 중앙 %.0f, 표준편차 %.0f, 변동계수 CV = %.2f (푸아송 과정의 기대는 약 1)' % (gaps.mean(), np.median(gaps), gaps.std(ddof=1), cv))
span = (-7000, 2000)
N = 20000; cvs = np.empty(N)
for i in range(N):
    p = np.sort(rng.uniform(*span, 20)); g = np.diff(p); cvs[i] = g.std(ddof=1) / g.mean()
print('  구간 기원전 7000~기원후 2000에 20개를 고르게 흩뿌린 %d번의 CV: 중앙 %.2f, 5~95%% %.2f~%.2f, P(CV >= 관측) = %.3f' % (N, np.median(cvs), np.percentile(cvs, 5), np.percentile(cvs, 95), (cvs >= cv).mean()))
out['cv_min'] = float(cv); out['cv_p'] = float((cvs >= cv).mean())
hh, ee = np.histogram(cvs, bins=np.linspace(0.3, 1.8, 31)); out['cv_hist'] = dict(counts=hh.tolist(), edges=ee.tolist()); out['gaps_min'] = gaps.tolist()
gx = np.diff(np.sort(cx)); cvx = gx.std(ddof=1) / gx.mean()
cvs2 = np.empty(N)
for i in range(N):
    p = np.sort(rng.uniform(*span, 14)); g = np.diff(p); cvs2[i] = g.std(ddof=1) / g.mean()
print('  극대기 14개 간격 평균 %.0f, CV = %.2f; 같은 방식의 기준선 중앙 %.2f, P(CV >= 관측) = %.3f' % (gx.mean(), cvx, np.median(cvs2), (cvs2 >= cvx).mean()))
out['cv_max'] = float(cvx); out['cv_max_p'] = float((cvs2 >= cvx).mean())
win = (690, 1680)
inwin = ((cm >= win[0]) & (cm <= win[1])).sum()
lam = 20 / 9000 * (win[1] - win[0])
print('  기원후 %d~%d(%d년)에 극소기 중심 %d개. 평균 빈도로 기대 %.2f개, 푸아송 P(>= %d) = %.4f' % (win[0], win[1], win[1] - win[0], inwin, lam, inwin, stats.poisson.sf(inwin - 1, lam)))
out['recent5_p'] = float(stats.poisson.sf(inwin - 1, lam))
big = (cm >= -6500) & (cm <= -5000)
print('  기원전 6500~5000(1500년)에 극소기 중심 %d개, 기대 %.2f개' % (big.sum(), 20 / 9000 * 1500))
gap_bigs = np.sort(cm)
print('  가장 긴 간격: %d년(기원전 %d에서 %d)' % (gaps.max(), abs(cs[np.argmax(gaps)]), abs(cs[np.argmax(gaps) + 1])))
print('\n=== 계산 10-1 (3) 2400년 주기의 위상 시험(레일리) ===')
def rayleigh(t, P):
    ph = 2 * np.pi * (t % P) / P
    return np.hypot(np.cos(ph).sum(), np.sin(ph).sum()) / len(t), (np.degrees(np.arctan2(np.sin(ph).sum(), np.cos(ph).sum())) % 360) / 360 * P
Ps = np.arange(1500, 3601, 50)
def scan(t):
    return np.array([rayleigh(t, P)[0] for P in Ps])
for lab, t in (('극소기', cm), ('극대기', cx)):
    R = scan(t)
    iP = Ps.tolist().index(2400)
    mxs = np.empty(4000)
    for i in range(4000):
        mxs[i] = scan(rng.uniform(*span, len(t))).max()
    p_fixed = np.mean([rayleigh(rng.uniform(*span, len(t)), 2400)[0] >= R[iP] for _ in range(4000)])
    print('  %s(n=%d): P = 2400년에서 R = %.3f (위상 중심 %.0f년 지점), 1500~3600년 훑었을 때 최대 R = %.3f (P = %d년)' % (lab, len(t), R[iP], rayleigh(t, 2400)[1], R.max(), Ps[R.argmax()]))
    print('       2400년만 미리 정했다면 P(R >= 관측) = %.3f; 주기를 훑는 경우의 최대 R 기준으로 P(max R >= 관측 최대) = %.3f' % (p_fixed, (mxs >= R.max()).mean()))
    out['ray_' + lab] = dict(R2400=float(R[iP]), p_fixed=float(p_fixed), Rmax=float(R.max()), Pbest=int(Ps[R.argmax()]), p_scan=float((mxs >= R.max()).mean()))
print('  (극소기가 홀레하임 주기의 한 위상에 모이면 R이 커진다. 시험은 중심 연대만 쓰며 지속 기간과 연대 오차를 쓰지 않는다)')
# 레일리 R(P) 곡선과 점별 95% 기준선(그림용)
Rm = scan(cm); Rx = scan(cx)
nullm = np.array([scan(rng.uniform(*span, 20)) for _ in range(3000)]); nullx = np.array([scan(rng.uniform(*span, 14)) for _ in range(3000)])
out['ray_curve'] = dict(P=Ps.tolist(), Rmin=Rm.tolist(), Rmax=Rx.tolist(), nullmin95=np.percentile(nullm, 95, axis=0).tolist(), nullmax95=np.percentile(nullx, 95, axis=0).tolist())
json.dump(out, open('out/calc10-1.json', 'w'), ensure_ascii=False, indent=1)
