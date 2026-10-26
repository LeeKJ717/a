# -*- coding: utf-8 -*-
"""6장 실습 6-11: 제1권 11장 노백산(Lyu 등, 2016) 나이테 계산을 ringlib-v1.py의 함수로 다시 하고, 제1권 계산 스크립트
(/home/claude/book/ms/ch11-calc-v1.py)의 출력과 항목마다 견준다. 그다음 제1권이 하지 않은 계산(유효 평균 상관 rbar.eff를 쓴 EPS와 SNR)을 더한다.

입력은 제1권 11.5절이 옮긴 논문의 본문 값뿐이다(표 1의 통계, 변환식, 표 3의 R, 표 4의 기간). 논문의 연별 나이테 폭 자료는
제1권에도 이 책에도 없으므로 노백산 연대기 414년의 복원 자체는 되풀이하지 못한다(입수 확인 필요).
실행: python3 lyu-recheck-v1.py | tee lyu-recheck.log
"""
import os, re, subprocess, sys, platform, importlib.util
from math import sqrt
import numpy as np
import scipy
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
V1 = '/home/claude/book/ms/ch11-calc-v1.py'
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
out = subprocess.run([sys.executable, '-I', V1], capture_output=True, text=True, encoding='utf-8')
V = out.stdout
print('제1권 계산 스크립트 실행: 종료 코드 %d, 출력 %d줄' % (out.returncode, V.count('\n')))

rows = []   # (항목, 이 장의 값, 제1권 출력에서 읽은 값, 허용 오차)


def v1(pat, group=1, which=0):
    ms = re.findall(pat, V)
    if not ms:
        return None
    m = ms[which]
    return float(m[group - 1] if isinstance(m, tuple) else m)


def add(label, mine, pat, tol, group=1, which=0):
    theirs = v1(pat, group, which)
    rows.append((label, mine, theirs, tol))


# ---------------------------------------------------------------- 표 1과 변환식 (계산 11-5)
N, r_ = 58, 0.757
R2 = r_ * r_
adj = 1 - (1 - 0.573) * (N - 1) / (N - 2)
F_r2 = R2 * (N - 2) / (1 - R2)
F_573 = 0.573 * (N - 2) / (1 - 0.573)
t_ = r_ * sqrt(N - 2) / sqrt(1 - R2)
add('11-5 r^2', R2, r'r\^2 = ([\d.]+)', 5e-6)
add('11-5 조정 R2', adj, r'R2adj = .*?= ([\d.]+)', 5e-5)
add('11-5 F (R2=0.573)', F_573, r'F = R2 \(N-2\)/\(1-R2\) = ([\d.]+)\s+\(R2=0.573\)', 5e-4)
add('11-5 F (R2=r^2)', F_r2, r'; ([\d.]+) \(R2=r\^2\)', 5e-4)
add('11-5 t', t_, r't = r sqrt.*? = ([\d.]+) ;', 5e-5)
add('11-5 t^2', t_ * t_, r't\^2 = ([\d.]+)', 5e-4)
add('11-5 임계 r (N=58, 5%)', L.crit_r(58, 0.05), r'임계 r \(N=58, 양쪽 0.05\) = ([\d.]+)', 5e-5)
add('11-5 임계 r (N=58, 1%)', L.crit_r(58, 0.01), r'임계 r \(N=58, 양쪽 0.01\) = ([\d.]+)', 5e-5)
add('11-5 Y(X=0.80)', 2.987 * 0.8 + 4.829, r'X=0\.80: ([\d.]+)', 5e-4)
add('11-5 Y(X=1.20)', 2.987 * 1.2 + 4.829, r'X=1\.20: ([\d.]+)', 5e-4)
add('11-5 X(복원 평균 7.66)', (7.66 - 4.829) / 2.987, r'\(7\.66-4\.829\)/2\.987 = ([\d.]+)', 5e-5)
add('11-5 2.987 x 0.20', 2.987 * 0.20, r'2\.987\*0\.20 = ([\d.]+)', 5e-4)
p_two = 2 * stats.t.sf(t_, N - 2)
rows.append(('11-5 양쪽 p (x 1e-12)', p_two * 1e12, v1(r'p\(t\) 양쪽 = ([\d.]+)e-12') if v1(r'p\(t\) 양쪽 = ([\d.]+)e-12') else None, 5e-3))

# ---------------------------------------------------------------- 표 3과 부호 검정 (계산 11-6)
add('11-6 임계 r (n=29, 5%)', L.crit_r(29, 0.05), r'임계 r \(n=29, 양쪽 0.05\) = ([\d.]+)', 5e-5)
add('11-6 임계 r (n=29, 1%)', L.crit_r(29, 0.01), r'임계 r \(n=29, 양쪽 0.01\) = ([\d.]+)', 5e-5)
add('11-6 부호 (20, 9) 양쪽 p', stats.binomtest(20, 29, 0.5).pvalue, r'\(20, 9\): n=29, p\(양쪽\) = ([\d.]+)', 5e-5)
add('11-6 부호 (22, 7) 양쪽 p', stats.binomtest(22, 29, 0.5).pvalue, r'\(22, 7\): n=29, p\(양쪽\) = ([\d.]+)', 5e-5)
add('11-6 부호 (20, 9) 한쪽 p', stats.binom.sf(19, 29, 0.5), r'한쪽 p: \(20, 9\) = ([\d.]+)', 5e-5)

# ---------------------------------------------------------------- 냉기·온기 (계산 11-8)
mean, sd = 7.66, 0.53
add('11-8 온기 기준', mean + 0.5 * sd, r'온기 기준 = .*? = ([\d.]+) ;', 5e-4)
add('11-8 냉기 기준', mean - 0.5 * sd, r'냉기 기준 = ([\d.]+)', 5e-4)
cold = [(1605, 1616), (1645, 1677), (1684, 1691), (1911, 1924), (1930, 1942), (1951, 1969)]
warm = [(1767, 1785), (1787, 1793), (1795, 1807), (1819, 1826), (1838, 1848), (1856, 1873), (1991, 2008)]
cy = sum(b - a + 1 for a, b in cold)
wy = sum(b - a + 1 for a, b in warm)
add('11-8 냉기 합(년)', cy, r'냉기 합 (\d+)년', 0)
add('11-8 온기 합(년)', wy, r'온기 합 (\d+)년', 0)
add('11-8 냉기 비율(%)', 100 * cy / 414, r'냉기 합 \d+년 \(([\d.]+)%', 5e-2)
add('11-8 온기 비율(%)', 100 * wy / 414, r'온기 합 \d+년 \(([\d.]+)% of 414\), 온기 합 \d+년 \(([\d.]+)%', 5e-2, group=1) if False else None
rows.append(('11-8 온기 비율(%)', 100 * wy / 414, v1(r'온기 합 (\d+)년 \(([\d.]+)%', 2), 5e-2))

# ---------------------------------------------------------------- 상관의 유의성과 유효 표본 (계산 11-9)
for n in (57, 100, 414):
    ms = re.search(r'n=%3d 임계 r \(양쪽 0.05\) = ([\d.]+) , \(0.01\) = ([\d.]+)' % n, V)
    rows.append(('11-9 임계 r(5%%) n=%d' % n, L.crit_r(n, 0.05), float(ms.group(1)) if ms else None, 5e-4))
    rows.append(('11-9 임계 r(1%%) n=%d' % n, L.crit_r(n, 0.01), float(ms.group(2)) if ms else None, 5e-4))
t12 = 0.12 * sqrt(55) / sqrt(1 - 0.12 ** 2)
rows.append(('11-9 1차 차분 t', t12, v1(r'r=0.12, n=57: t = ([\d.]+)'), 5e-4))
rows.append(('11-9 1차 차분 p', 2 * stats.t.sf(t12, 55), v1(r'r=0.12, n=57: t = [\d.]+, p = ([\d.]+)'), 5e-4))
rows.append(('11-9 유효 표본(두 계열 0.72)', L.n_eff(414, 0.72, 0.72), v1(r'= 414 × [\d.]+ / [\d.]+ = ([\d.]+)'), 5e-2))
rows.append(('11-9 유효 표본(한 계열만 0.72)', 414 * (1 - 0.72) / (1 + 0.72), v1(r'한 계열만 자기상관 0.72이면: n_eff = ([\d.]+)'), 5e-2))

# ---------------------------------------------------------------- EPS와 SNR (계산 11-14, 제1권의 단순 식)
for rb, tag in ((0.22, 'std'), (0.28, 'RES')):
    ms = re.search(r'r=%s: EPS\(n=11\)=([\d.]+) EPS\(n=15\)=([\d.]+) EPS\(n=20\)=([\d.]+) ; EPS 0.85 에 필요한 n = ([\d.]+)' % rb, V)
    for k, nn in enumerate((11, 15, 20)):
        rows.append(('11-14 %s EPS(n=%d), rbar=%.2f' % (tag, nn, rb), L.eps_from_rbar(nn, rb), float(ms.group(k + 1)) if ms else None, 5e-4))
    rows.append(('11-14 %s EPS 0.85에 필요한 n' % tag, L.n_for_eps(0.85, rb), float(ms.group(4)) if ms else None, 5e-3))
for tag, snr, rb in (('std', 8.72, 0.22), ('RES', 11.81, 0.28)):
    ms = re.search(r'%s: SNR=%s, r=%s -> n = SNR\(1-r\)/r = ([\d.]+); 그 n 의 EPS = ([\d.]+)' % (tag, snr, rb), V)
    n_ = snr * (1 - rb) / rb
    rows.append(('11-14 %s SNR에서 되짚은 n' % tag, n_, float(ms.group(1)) if ms else None, 5e-3))
    rows.append(('11-14 %s 그때의 EPS = SNR/(1+SNR)' % tag, snr / (1 + snr), float(ms.group(2)) if ms else None, 5e-5))
rows.append(('11-14 n=11에서 EPS 0.85가 되는 r', 0.85 / (0.15 * 11 + 0.85), v1(r'n=11: EPS 0.85 에 필요한 평균 상관 r = 0.85/\(0.15 n \+ 0.85\) = ([\d.]+)'), 5e-4))

print('\n== 제1권 계산 출력과의 항목별 대조 (이 장의 함수로 다시 계산한 값 대 제1권 스크립트 출력에서 읽은 값)')
print('  항목                                     이 장        제1권 출력     허용 오차   결과')
nok = 0
for lab, mine, theirs, tol in rows:
    if theirs is None:
        print('  %-40s %-12.5g %-12s %-10g  제1권 출력에서 값을 찾지 못함' % (lab, mine, '(없음)', tol))
        continue
    ok = abs(mine - theirs) <= tol
    nok += ok
    print('  %-40s %-12.5g %-12.5g %-10g  %s' % (lab, mine, theirs, tol, '일치' if ok else '차이'))
print('  전체 %d개 항목 중 일치 %d개, 차이 또는 값 없음 %d개' % (len(rows), nok, len(rows) - nok))

# ---------------------------------------------------------------- 제1권이 하지 않은 계산: 유효 평균 상관 rbar.eff
print('\n== 추가 계산. 표 1의 rbar.bt(나무 사이)와 rbar.wt(나무 안)로 유효 평균 상관 rbar.eff를 구하고 EPS와 SNR을 다시 본다')
print('  식(dplR의 정의): rbar.eff = rbar.bt / (rbar.wt + (1 - rbar.wt)/c.eff), c.eff = 나무 한 그루에서 평균해 쓰는 코어 수의 유효 값.')
print('  EPS = n rbar.eff / ((n-1) rbar.eff + 1), SNR = n rbar.eff / (1 - rbar.eff). 논문이 어떤 식과 어떤 c.eff를 썼는지는 이 책이 확인하지 못했다.')
T1 = {'std': dict(bt=0.22, wt=0.68, snr=8.72, n_eps=11, first=1660), 'RES': dict(bt=0.28, wt=0.51, snr=11.81, n_eps=15, first=1685)}
for tag, d in T1.items():
    lo = d['bt']                       # c.eff = 1
    hi = d['bt'] / d['wt']             # c.eff -> 무한대
    print('\n  [%s] rbar.bt = %.2f, rbar.wt = %.2f -> rbar.eff는 c.eff = 1에서 %.3f, c.eff가 한없이 크면 %.3f (이 범위 밖의 값은 두 평균 상관과 맞지 않는다)' % (tag, d['bt'], d['wt'], lo, hi))
    print('   c.eff   rbar.eff   EPS 0.85에 필요한 n   SNR %.2f를 주는 n   n=41에서 SNR   n=11에서 EPS   n=15에서 EPS' % d['snr'])
    for c in (1.0, 1.5, 71 / 41, 2.0, 3.0, 1e9):
        re_ = d['bt'] / (d['wt'] + (1 - d['wt']) / c)
        print('   %5s  %8.4f   %18.2f   %17.2f   %12.2f   %12.3f   %12.3f' % ('무한' if c > 1e6 else ('%.3f' % c), re_, L.n_for_eps(0.85, re_), d['snr'] * (1 - re_) / re_,
              L.snr_from_rbar(41, re_), L.eps_from_rbar(11, re_), L.eps_from_rbar(15, re_)))
    print('   (c.eff = 1.732는 코어 71개를 나무 41그루로 나눈 71/41이며, 이 값이 dplR의 c.eff 정의와 같은지는 확인하지 않은 가정이다)')
    need_r = d['n_eps'] and 0.85 / (0.15 * d['n_eps'] + 0.85)
    print('   표의 \"EPS 0.85를 처음 넘는 해: %d년(나무 %d그루)\"가 전 기간 평균 상관으로 재현되려면 rbar = %.3f가 필요하다. rbar.eff의 가능한 범위의 위쪽 끝은 %.3f이다.' % (
        d['first'], d['n_eps'], need_r, hi))
    print('   -> %s' % ('범위 안에 들어 있어 c.eff의 값에 따라 가능하다' if lo <= need_r <= hi else ('필요한 rbar가 범위보다 높아, 전 기간 평균 상관으로는 어떤 c.eff에서도 재현되지 않는다(그 해들의 상관이 평균보다 높았다는 설명이 필요하다)' if need_r > hi else '필요한 rbar가 범위보다 낮다: c.eff = 1에서도 n=%d이면 EPS가 0.85를 넘으므로, 그 해에 처음 넘었다는 서술과는 그 해의 상관이 평균보다 낮았다는 설명이 필요하다' % d['n_eps'])))
print('\n  요약: 제1권 계산 11-14는 rbar.bt를 그대로 EPS의 평균 상관으로 썼다(c.eff = 1과 같다). 그 가정에서 RES의 15그루는 재현되고(EPS 0.854) std의 11그루는 재현되지 않았다.')
print('        유효 평균 상관(c.eff > 1)을 쓰면 RES는 15그루보다 적은 나무로도 0.85에 닿으므로 "15그루에서 처음 넘는다"는 서술은 전 기간 평균 상관만으로는 설명되지 않고, std는 c.eff가 한없이 커도 11그루에서 EPS 0.840으로 0.85에 닿지 못한다.')

# ---------------------------------------------------------------- 추가 계산 2: 표 1의 SNR이 어떤 나무 수와 짝인가
print('\n== 추가 계산 2. 표 1의 SNR(std 8.72, RES 11.81)을 나무 41그루(또는 코어 71개) 전체에 쓴 SNR이라고 하면 평균 상관은 얼마여야 하는가')
print('  SNR = n r / (1 - r) 을 r에 대해 풀면 r = SNR / (n + SNR)')
for tag, snr, rb in (('std', 8.72, 0.22), ('RES', 11.81, 0.28)):
    for n in (41, 71):
        r_need = snr / (n + snr)
        print('  %s: n = %d이면 r = %.4f (표 1의 rbar.bt = %.2f, 차이 %+.4f)' % (tag, n, r_need, rb, r_need - rb))
print('  두 경우 모두 표 1의 rbar.bt보다 작다. 곧 표의 SNR은 41그루(또는 71코어)에 표의 평균 상관을 넣어 얻은 값이 아니다. 어떤 나무 수와 짝인지는 이 책이 확인하지 못했다(미결).')
