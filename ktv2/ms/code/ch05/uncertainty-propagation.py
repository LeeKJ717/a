# -*- coding: utf-8 -*-
"""5장 실습 5-7: 불확실성 전파. 식으로 합치기(1차 근사)와 난수로 합치기(몬테카를로)를 맞대어 본다.
A. 제1권 2장 계산 2-5(퇴적속도의 오차), 2-8(뒤집힌 연대 두 개).
B. 제1권 9장 계산 9-10(OSL 나이 = De / DR의 오차 전파).
C. 비 X/Y에서 분모의 상대오차가 커지면 1차 근사가 어디서 무너지는가(시연값).
입력의 +-는 모두 1 표준편차이고 서로 독립인 정규분포로 놓는다(이것이 이 계산의 가정이다).
실행: python3 uncertainty-propagation.py | tee uncertainty-propagation.log
"""
import time, platform, json
J = {}
from math import sqrt, erf
import numpy as np
import scipy
from scipy import stats

T0 = time.perf_counter()
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))


def draw(rg, mu, sd, B):
    return rg.normal(mu, sd, B)


print('\n== A. 제1권 2장: 두 시료 사이의 퇴적속도 (계산 2-5) ==')
t1, s1, t2, s2 = 7660.0, 160.0, 6020.0, 135.0      # TH-237, TH-236 (Jo, 1980의 표를 제1권이 옮긴 값)
dt = t1 - t2; sd_dt = sqrt(s1 ** 2 + s2 ** 2)
depth = 12500.0                                      # mm
rate = depth / dt
print('연대 차이 = %.0f년, 오차 = sqrt(160^2+135^2) = %.2f년 (제1권 209.3)' % (dt, sd_dt))
print('속도 = 12500/1640 = %.3f mm/yr (제1권 7.62)' % rate)
print('제1권의 양끝 값: 1640+209 -> %.2f, 1640-209 -> %.2f (제1권 6.76, 8.74)' % (depth / (dt + 209), depth / (dt - 209)))
sd_rate = depth * sd_dt / dt ** 2
print('1차 근사(델타 방법): 속도의 표준편차 = 12500 x 209.34 / 1640^2 = %.4f -> %.3f +- %.3f (대칭 구간 %.3f ~ %.3f)' % (sd_rate, rate, sd_rate, rate - sd_rate, rate + sd_rate))
print('몬테카를로: 연대 차이를 정규분포에서 B번 뽑아 속도를 구한다 (시드 20260, 시간 측정)')
print('%12s %10s %10s %10s %24s %10s' % ('B', '평균', '표준편차', '중앙값', '15.87~84.13% (1시그마)', '시간(초)'))
for B in (1000, 10000, 100000, 1000000, 10000000):
    t = time.perf_counter()
    rg = np.random.default_rng(20260)
    x = draw(rg, t1, s1, B) - draw(rg, t2, s2, B)
    v = depth / x
    q = np.percentile(v, [15.865, 84.135])
    print('%12s %10.4f %10.4f %10.4f %12.4f ~ %-10.4f %10.2f' % ('{:,}'.format(B), v.mean(), v.std(ddof=1), np.median(v), q[0], q[1], time.perf_counter() - t))
print('2.5~97.5% (B=10,000,000): ', end='')
rg = np.random.default_rng(20260); x = draw(rg, t1, s1, 10000000) - draw(rg, t2, s2, 10000000); v = depth / x
hh, ee = np.histogram(v, bins=60, range=(4.5, 13.5))
J['rate'] = dict(counts=[int(c) for c in hh], edges=[float(e) for e in ee], B=10000000, rate=rate, sd=sd_rate, q1=[float(c) for c in np.percentile(v, [15.865, 84.135])], mean=float(v.mean()), median=float(np.median(v)))
print('%.3f ~ %.3f, 연대 차이가 0 이하인 추출 수 %d, 왜도 %.3f' % (*np.percentile(v, [2.5, 97.5]), int((x <= 0).sum()), stats.skew(v)))
print('양끝 값(제1권 방식)과 몬테카를로 1시그마 구간 비교: 양끝 6.76 ~ 8.74는 연대 차이를 +-1시그마로 움직인 것이라 속도의 15.87~84.13%% 구간과 거의 같고, 평균은 %.3f로 중앙값 %.3f보다 크다(오른쪽으로 꼬리).' % (v.mean(), np.median(v)))

print('\n== A2. 뒤집힌 연대 두 개가 오차 안인가 (계산 2-8) ==')
u1, u2 = 7660.0, 7870.0                              # TH-237(아래, 해면하 14.5 m), TH-266(위, 2 m 위)
d = u2 - u1; sdd = sqrt(160 ** 2 + 160 ** 2)
print('차이 %.0f, 합친 오차 %.2f, 비 = %.3f (제1권 0.93배)' % (d, sdd, d / sdd))
print('두 시료의 참 나이가 같다면, 관측한 차이가 +210 이상 뒤집힐 확률: 한쪽 %.4f, 양쪽 %.4f' % (Phi(-d / sdd), 2 * Phi(-d / sdd)))
for B in (10000, 1000000, 10000000):
    rg = np.random.default_rng(31)
    dd = rg.normal(0, 160, B) - rg.normal(0, 160, B)
    print('  몬테카를로 B=%s: P(차이 >= 210) = %.4f, 양쪽 %.4f' % ('{:,}'.format(B), (dd >= d).mean(), (np.abs(dd) >= d).mean()))

print('\n== B. 제1권 9장: OSL 나이 = De / DR (계산 9-10) ==')
print('%-12s %8s %8s %8s %8s | %-26s | %-8s' % ('시료', 'De', '+-', 'DR', '+-', '식(상대오차 합성) 나이 +- 오차', '논문'))
samples = (('HZ-OSL-115', 4.64, 0.55, 2.57, 0.09, 1.80, 0.22), ('HZ-OSL-180', 5.28, 0.96, 2.39, 0.09, 2.21, 0.41))
for nm, De, sDe, DR, sDR, age, sage in samples:
    a = De / DR; rel = sqrt((sDe / De) ** 2 + (sDR / DR) ** 2)
    print('%-12s %8.2f %8.2f %8.2f %8.2f | %.3f +- %.3f (상대 %.2f%%)  | %.2f +- %.2f' % (nm, De, sDe, DR, sDR, a, a * rel, 100 * rel, age, sage))
print('\n몬테카를로 (De, DR을 독립 정규분포에서 B번)')
print('%-12s %12s %8s %8s %8s %9s %24s %24s %9s' % ('시료', 'B', '평균', '표준편차', '왜도', '중앙값', '15.87~84.13%', '2.5~97.5%', '시간(초)'))
for nm, De, sDe, DR, sDR, age, sage in samples:
    for B in (1000, 100000, 10000000):
        t = time.perf_counter()
        rg = np.random.default_rng(909)
        v = rg.normal(De, sDe, B) / rg.normal(DR, sDR, B)
        q1 = np.percentile(v, [15.865, 84.135]); q2 = np.percentile(v, [2.5, 97.5])
        print('%-12s %12s %8.4f %8.4f %8.3f %9.4f %10.4f ~ %-10.4f %10.4f ~ %-10.4f %9.2f' % (nm, '{:,}'.format(B), v.mean(), v.std(ddof=1), stats.skew(v), np.median(v), q1[0], q1[1], q2[0], q2[1], time.perf_counter() - t))
    a = De / DR; rel = sqrt((sDe / De) ** 2 + (sDR / DR) ** 2)
    print('  식의 +-1.96시그마: %.4f ~ %.4f' % (a - 1.96 * a * rel, a + 1.96 * a * rel))
print('몬테카를로 표준편차의 흔들림: B마다 시드 20개로 되풀이한 HZ-OSL-180의 표준편차')
print('%12s %10s %10s %10s' % ('B', '평균', '표준편차(되풀이)', '이론 s/sqrt(2B)'))
for B in (1000, 10000, 100000, 1000000):
    sds = []
    for s in range(20):
        rg = np.random.default_rng(6000 + s)
        sds.append((rg.normal(5.28, 0.96, B) / rg.normal(2.39, 0.09, B)).std(ddof=1))
    print('%12s %10.4f %10.5f %10.5f' % ('{:,}'.format(B), np.mean(sds), np.std(sds, ddof=1), 0.41 / sqrt(2 * B)))
print('달력 연대 환산(채취 2024년 가정, 제1권과 같음)은 이 장에서 다시 하지 않는다. 4~444년, -596~224년 구간은 제1권 계산 9-10.')

print('\n== C. 비 X/Y: 분모의 상대오차가 커지면 1차 근사가 어디서 무너지는가 (시연값: X = 10 +- 10%, Y = 5, 분모 오차만 바꿈) ==')
print('%8s %12s %12s %10s %10s %12s %12s %14s' % ('Y 상대오차', '식 sd', '몬테카를로 sd', '평균 / 식값', '왜도', '2.5% 끝', '97.5% 끝', '식의 -+1.96sd'))
B = 4000000
for relY in (0.02, 0.05, 0.10, 0.20, 0.30, 0.40):
    rg = np.random.default_rng(88)
    X = rg.normal(10, 1.0, B); Y = rg.normal(5, 5 * relY, B)
    v = X / Y
    z = 10 / 5
    sd_f = z * sqrt(0.1 ** 2 + relY ** 2)
    q = np.percentile(v, [2.5, 97.5])
    print('%8.0f%% %12.4f %12.4f %10.4f %10.2f %12.3f %12.3f %7.3f ~ %-7.3f' % (100 * relY, sd_f, v.std(ddof=1), v.mean() / z, stats.skew(v), q[0], q[1], z - 1.96 * sd_f, z + 1.96 * sd_f))
print('(분모가 0 근처까지 퍼지면 비의 평균과 분산이 정의되지 않는다: 분모가 정규분포이면 이론상 비의 분산은 무한대이고, 위 표본의 sd는 표본마다 달라진다.)')
print('\n걸린 시간 %.1f초' % (time.perf_counter() - T0))
json.dump(J, open('uncertainty-propagation.json', 'w'))
