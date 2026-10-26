# -*- coding: utf-8 -*-
"""실습 9-5~9-7. 서로 다른 연대 추정치가 같은 사건을 가리키는가: 가중 평균, 카이제곱 T', 구간의 정규 근사.
입력은 제1권 4장 계산 4-6과 4.2, 4.4절의 표에서 옮긴 값이다(오쿠노 등 2010의 14C 날짜, McLean 등 2019와 오쿠노 등의 구간,
밀레니엄 분출 연대의 서술). 구간을 정규분포로 바꾸는 부분은 이 책의 가정이며 값에 "가정"이라고 표시한다.
실행: python3 ex2-agree.py > ex2-agree.log"""
import os, sys, json, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy
from scipy import stats
import tephralib as T

print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
res = {}
def show(name, x, s, key=None):
    r = T.tprime(x, s)
    ptxt = ('%.3e' % r['p']) if r['p'] > 1e-300 else '<1e-300'
    print('  %-34s n=%d  가중평균 %10.2f ± %6.2f  T\'=%8.3f  df=%d  p=%s  5%%한계 %.3f  %s' % (
        name, len(x), r['mean'], r['err'], r['T'], r['df'], ptxt, r['crit5'], '합치' if r['agree'] else '불일치'))
    if key: res[key] = dict(x=list(map(float, x)), s=list(map(float, s)), **r)
    return r

print('\n[실습 9-5] 제1권 4장 계산 4-6의 날짜 묶음(14C 나이, BP, 보정하지 않은 값)')
show('쉬운 예(100±10, 120±20)', [100, 120], [10, 20], 'toy')
show('U-2 네 날짜', [4910, 4965, 4945, 4940], [35] * 4, 'u2four')
show('U-2 다섯 날짜(4710±30 포함)', [4910, 4965, 4945, 4940, 4710], [35] * 4 + [30], 'u2five')
show('U-3 두 날짜', [7525, 8030], [35, 35], 'u3')
d, sd, z = T.pair_z(8030, 35, 7525, 35)
print('  U-3 쌍별: 차이 %.0f, 차이의 σ %.2f, z=%.3f, T\'(두 개)=z^2=%.2f' % (d, sd, z, z * z))
show('U-4 다섯 날짜', [12165, 11840, 12030, 12090, 12095], [40, 45, 40, 40, 40], 'u4five')
show('U-4 네 날짜(11840 제외)', [12165, 12030, 12090, 12095], [40] * 4, 'u4four')
print('  제1권은 U-4 날짜 "12,165, 11,840, 12,030, 12,090, 12,095"의 σ를 40, 45, 40, 40, 40으로 두었다(원문 표 대조는 제1권이 하지 못함).')

print('\n[실습 9-5b] 일치의 한계: 어느 날짜를 뺄지 자동으로 정하면?')
x = np.array([12165, 11840, 12030, 12090, 12095.]); s = np.array([40, 45, 40, 40, 40.])
for i in range(len(x)):
    r = T.tprime(np.delete(x, i), np.delete(s, i))
    print('  %d번째(%d±%d)를 뺀 T\'=%.3f (df=%d, p=%.4f)' % (i + 1, x[i], s[i], r['T'], r['df'], r['p']))
print('  → 한 개씩 빼 보면 11840을 뺄 때만 합치(5%)가 된다. 그러나 "합치될 때까지 뺀다"는 절차는 p값의 의미를 바꾼다(아래 모의).')

print('\n[실습 9-6] T\'의 영분포를 모의로 확인: 참 나이가 같은 날짜 n개를 뽑아 T\'를 계산')
rng = np.random.default_rng(20261026)
NSIM = 200000
for n, sg in ((4, 35.0), (5, 40.0), (2, 35.0)):
    xs = rng.normal(5000.0, sg, (NSIM, n))
    ss = np.full(n, sg)
    w = 1 / ss ** 2
    m = (xs * w).sum(axis=1) / w.sum()
    Tm = (((xs - m[:, None]) / ss) ** 2).sum(axis=1)
    crit = stats.chi2.ppf(0.95, n - 1)
    print('  n=%d, σ=%g: 모의 %d번 중 T\'>%.3f 인 비율 = %.4f (이론 0.05), T\' 평균 %.4f (이론 df=%d), 분산 %.4f (이론 %d)' % (
        n, sg, NSIM, crit, (Tm > crit).mean(), Tm.mean(), n - 1, Tm.var(), 2 * (n - 1)))
# 검정력: 다섯 중 한 날짜가 d만큼 어긋났을 때
print('  검정력(시연값): 다섯 날짜(σ=40), 한 날짜만 참 나이에서 d년 어긋남. T\'>5% 한계인 비율')
n, sg = 5, 40.0
crit = stats.chi2.ppf(0.95, n - 1)
pw = {}
for dd in (0, 40, 80, 120, 200, 320):
    xs = rng.normal(5000.0, sg, (NSIM, n)); xs[:, 0] += dd
    w = np.full(n, 1 / sg ** 2); m = xs.mean(axis=1)
    Tm = (((xs - m[:, None]) / sg) ** 2).sum(axis=1)
    pw[dd] = float((Tm > crit).mean())
    print('    d=%3d년: %.4f' % (dd, pw[dd]))
res['power'] = pw
# "합치할 때까지 뺀다"의 거짓 합치 보증: 참 같은 날짜 5개에서 T'가 한계를 넘으면 가장 어긋난 날짜를 하나 빼고 다시 검정
xs = rng.normal(5000.0, sg, (NSIM, n))
m = xs.mean(axis=1); Tm = (((xs - m[:, None]) / sg) ** 2).sum(axis=1)
rej = Tm > crit
dev = np.abs(xs - m[:, None]); drop = dev.argmax(axis=1)
mask = np.ones_like(xs, bool); mask[np.arange(NSIM), drop] = False
x4 = xs[mask].reshape(NSIM, n - 1)
m4 = x4.mean(axis=1); T4 = (((x4 - m4[:, None]) / sg) ** 2).sum(axis=1)
T4all = T4
print('  참 같은 날짜 5개에서 처음 검정이 불일치인 비율 %.4f (이론 0.05)' % rej.mean())
print('  항상 가장 어긋난 날짜 하나를 빼고 남은 4개를 같은 5%% 한계(df=3, %.3f)로 검정하면 불일치 비율 %.4f (0.05가 아니다), T\' 평균 %.3f (df=3이면 3)' % (stats.chi2.ppf(0.95, 3), (T4all > stats.chi2.ppf(0.95, 3)).mean(), T4all.mean()))
print('  → 데이터를 보고 뺄 날짜를 고르면 같은 χ² 한계가 더 이상 5%를 뜻하지 않는다. 뺀 뒤의 p값은 낙관적이다.')
res['dropsim'] = dict(first_reject=float(rej.mean()), always_drop_reject=float((T4all > stats.chi2.ppf(0.95, 3)).mean()), always_drop_mean=float(T4all.mean()))

print('\n[실습 9-7a] 구간을 정규분포로 바꿔 합치 시험(가정: 구간 반폭 = 2σ, 곧 95% 구간)')
def itv(lo, hi):
    mid, half = (lo + hi) / 2.0, abs(hi - lo) / 2.0
    return mid, half / 2.0
print('  울릉도 U-2: 오쿠노 등의 보정 구간 5,600~5,734 cal BP(제1권 이론 배경 3)와 McLean 등 5,681~5,619 (IntCal13 yrs BP)')
m1, s1 = itv(5600, 5734); m2, s2 = itv(5619, 5681)
print('    중간 %.1f(σ %.2f), %.1f(σ %.2f)' % (m1, s1, m2, s2))
r = show('U-2 두 보정 구간(가정)', [m1, m2], [s1, s2], 'u2cal')
print('  울릉도 U-4: 오쿠노 등 9785±35 BP의 보정 구간 11,126~11,177 cal BP(제1권)와 McLean 등 U-Oki 10,171~10,230')
m1, s1 = itv(11126, 11177); m2, s2 = itv(10171, 10230)
print('    중간 %.1f(σ %.2f), %.1f(σ %.2f), 중간값 차이 %.1f' % (m1, s1, m2, s2, m1 - m2))
show('U-4 두 보정 구간(가정)', [m1, m2], [s1, s2], 'u4cal')

print('\n[실습 9-7b] 밀레니엄 분출 연대의 서로 다른 서술(제1권 4.2절 표). 가정이 많으니 절차를 보이는 시연이다')
print('  입력: Xu 등(2013)의 나이테 맞춤 946±3 CE(σ 수준은 제1권이 확인하지 못함 → 1σ로 가정),')
print('        Du 등(2023) 탄화목 A 지점 770~970 CE, B 지점 890~1020 CE (2σ 구간으로 읽음)')
mA, sA = itv(770, 970); mB, sB = itv(890, 1020)
print('  구간→정규: A 중간 %.1f σ %.2f, B 중간 %.1f σ %.2f' % (mA, sA, mB, sB))
show('A와 B 두 탄화목', [mA, mB], [sA, sB], 'meAB')
show('나이테 맞춤 + A + B', [946, mA, mB], [3, sA, sB], 'meall')
show('나이테 맞춤 + A', [946, mA], [3, sA], 'me946A')
show('나이테 맞춤 + B', [946, mB], [3, sB], 'me946B')
print('  해석 한계: 탄화목 14C 구간은 보정 곡선 때문에 정규분포가 아니고 구간이 여럿으로 갈라질 수 있다(제1권 이론 배경 3). 이 시험이 "합치"라고 해도 두 방법이 독립으로 같은 해를 가리킨다는 뜻이 아니다.')
print('  또 이 결과는 "946±3"을 1σ로 가정한 것이다. 2σ로 읽으면 σ=1.5가 되어 가중평균이 더 946 쪽으로 붙고 T\'가 달라진다:')
show('같은 계산, 946±1.5(2σ로 읽음)', [946, mA, mB], [1.5, sA, sB], 'meall15')

json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex2.json'), 'w'))
print('\n결과 저장: results/ex2.json')
