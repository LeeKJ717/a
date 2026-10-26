# -*- coding: utf-8 -*-
"""9장 점검: 제1권 4장의 계산과 이 장의 계산이 맞는가.
제1권 ms/ch04-calc-v1.py 를 그대로 실행해 출력한 값을 읽고, 이 장의 tephralib 로 다시 구한 값과 견준다.
스크립트가 출력하지 않는 값(방위, 이동 시간)은 제1권 원고 ms/ch04-v1.md 의 본문 숫자와 견준다(출처를 표시).
실행: python3 ex6-check-vol1.py > ex6-check-vol1.log"""
import os, re, sys, subprocess, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy
from scipy import stats
import tephralib as T

V1 = '/home/claude/book/ms'
print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
out = subprocess.run([sys.executable, '-I', os.path.join(V1, 'ch04-calc-v1.py')], capture_output=True, text=True, cwd=V1, timeout=300).stdout
ms = open(os.path.join(V1, 'ch04-v1.md'), encoding='utf-8').read()
print('제1권 스크립트 출력 %d줄, 원고 %d자' % (out.count('\n'), len(ms)))
rows = []
def add(item, v1, mine, tol, src):
    ok = abs(v1 - mine) <= tol
    rows.append((item, v1, mine, ok, src))
    print('  %-46s 제1권 %-12s 이 장 %-12s %s  [%s]' % (item, '%.6g' % v1, '%.6g' % mine, '일치' if ok else '차이 %+.4g' % (mine - v1), src))
def grab(pat, n=1, flags=0):
    m = re.search(pat, out, flags)
    if not m: raise SystemExit('제1권 출력에서 못 찾음: ' + pat)
    return [float(m.group(i + 1)) for i in range(n)]

print('\n[거리] 계산 4-1')
BD = (41.99, 128.08); SG = (35 + 35 / 60, 135 + 53 / 60); UL = (37.5, 130 + 52 / 60); KS = (37.97, 126.55)
add('백두산-스이게쓰호 (km)', grab(r'Baekdu-Suigetsu ([\d.]+)')[0], float(T.hav(*BD, *SG)), 1e-6, '스크립트')
add('울릉도-스이게쓰호 (km)', grab(r'Ulleungdo-Suigetsu ([\d.]+)')[0], float(T.hav(*UL, *SG)), 1e-6, '스크립트')
add('백두산-울릉도 (km)', grab(r'Baekdu-Ulleungdo ([\d.]+)')[0], float(T.hav(*BD, *UL)), 1e-6, '스크립트')
add('백두산-개성 시연값 (km)', grab(r'Baekdu-Kaesong\(demo coords\) ([\d.]+)')[0], float(T.hav(*BD, *KS)), 1e-6, '스크립트')
print('\n[방위] 제1권 원고 계산 4-1 본문: 스이게쓰호 134도, 개성 197도')
add('백두산→스이게쓰호 방위 (도)', 134.0, float(T.bearing(*BD, *SG)), 0.5, '원고 4.11.0절(정수로 적힘, 허용 0.5)')
add('백두산→개성 방위 (도)', 197.0, float(T.bearing(*BD, *KS)), 0.5, '원고 4.11.0절(정수로 적힘, 허용 0.5)')

print('\n[가중 평균과 카이제곱] 계산 4-6')
m, e, c = grab(r'U-2 four \(([\d.]+), ([\d.]+), ([\d.]+)\)', 3); r = T.tprime([4910, 4965, 4945, 4940], [35] * 4)
add('U-2 네 날짜 평균', m, r['mean'], 1e-9, '스크립트'); add('U-2 네 날짜 오차', e, r['err'], 1e-9, '스크립트'); add('U-2 네 날짜 T\'', c, r['T'], 1e-9, '스크립트')
m, e, c = grab(r'U-2 five \(([\d.]+), ([\d.]+), ([\d.]+)\)', 3); r = T.tprime([4910, 4965, 4945, 4940, 4710], [35] * 4 + [30])
add('U-2 다섯 날짜 평균', m, r['mean'], 1e-6, '스크립트'); add('U-2 다섯 날짜 오차', e, r['err'], 1e-6, '스크립트'); add('U-2 다섯 날짜 T\'', c, r['T'], 1e-6, '스크립트')
d, sd, z = grab(r'U-3 diff ([\d.]+) ([\d.]+) ([\d.]+)', 3); d2, sd2, z2 = T.pair_z(8030, 35, 7525, 35)
add('U-3 차이 (년)', d, d2, 1e-9, '스크립트'); add('U-3 차이의 σ', sd, sd2, 1e-9, '스크립트'); add('U-3 z', z, z2, 1e-9, '스크립트')
m, e, c = grab(r'U-4 five \(([\d.]+), ([\d.]+), ([\d.]+)\)', 3); r = T.tprime([12165, 11840, 12030, 12090, 12095], [40, 45, 40, 40, 40])
add('U-4 다섯 날짜 평균', m, r['mean'], 1e-6, '스크립트'); add('U-4 다섯 날짜 오차', e, r['err'], 1e-6, '스크립트'); add('U-4 다섯 날짜 T\'', c, r['T'], 1e-6, '스크립트')
m, e, c = grab(r'U-4 four \(([\d.]+), ([\d.]+), ([\d.]+)\)', 3); r = T.tprime([12165, 12030, 12090, 12095], [40] * 4)
add('U-4 네 날짜 평균', m, r['mean'], 1e-9, '스크립트'); add('U-4 네 날짜 오차', e, r['err'], 1e-9, '스크립트'); add('U-4 네 날짜 T\'', c, r['T'], 1e-9, '스크립트')
mm = T.tprime([100, 120], [10, 20])
add('쉬운 예 평균(원고 이론 배경 3: 104)', 104.0, mm['mean'], 1e-9, '원고'); add('쉬운 예 오차(원고 8.9)', 8.9, mm['err'], 0.05, '원고(소수 첫째 자리)'); add('쉬운 예 T\'(원고 0.80)', 0.80, mm['T'], 0.005, '원고')
print('  원고의 5%% 임계값: 자유도 3에서 7.81, 4에서 9.49, 1에서 3.84 → 이 장(scipy.stats.chi2.ppf): %.3f, %.3f, %.3f' % tuple(stats.chi2.ppf(0.95, k) for k in (3, 4, 1)))
for k, v in ((3, 7.81), (4, 9.49), (1, 3.84)): add('χ² 5%% 임계값 df=%d' % k, v, float(stats.chi2.ppf(0.95, k)), 0.005, '원고(표 값)')

print('\n[오쿠노 등 대 McLean 등의 U-4 차이] 제1권 안에서도 값이 둘이다')
v_script = grab(r'Okuno U-4 11,150 vs McLean 10,200 ([\d.]+)')[0]
mine = (11126 + 11177) / 2 - (10171 + 10230) / 2
add('U-4 중간값 차이: 스크립트(11,150으로 반올림해 계산)', v_script, mine, 0.05, '스크립트')
add('U-4 중간값 차이: 원고 4.11.2절 예 7(951년)', 951.0, mine, 0.05, '원고')

print('\n[두 분출 단계] 계산 4-3, 4-4')
add('간격 불확도 독립 합성 2σ (일)', grab(r'indep sd combo \(2sigma\) ([\d.]+)')[0], 2 * float(np.hypot(21 / 2, 23 / 2)), 1e-9, '스크립트')
s1, s2 = 21 / 2, 23 / 2; sg = 25 / 2
add('암묵 상관 ρ', grab(r'implied rho ([\d.]+)')[0], (s1 ** 2 + s2 ** 2 - sg ** 2) / (2 * s1 * s2), 1e-12, '스크립트')
for d in (7, 28, 56):
    add('P(간격<%d일), 정규 근사' % d, grab(r'P\(gap<%d d\)= ([\d.]+)' % d)[0], float(stats.norm.cdf((d - 31) / sg)), 1e-12, '스크립트')
import json
J4 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex4.json')))
r0 = J4['rho0.357']
for d, key in ((7, 'p7'), (28, 'p28'), (56, 'p56')):
    add('P(간격<%d일), 몬테카를로 200만 번(ρ=0.357)' % d, grab(r'P\(gap<%d d\)= ([\d.]+)' % d)[0], r0[key], 0.0015, '스크립트(몬테카를로 허용 0.0015)')
add('11월 1일 → 2월 7일 (일)', grab(r'1Nov->7Feb days (\d+)')[0], 98.0, 0, '스크립트')
add('2월 7일 - Spike 2 (일)', grab(r'7Feb minus spike2 (\d+)')[0], 98.0 - 77.0, 0, '스크립트')
print('\n[이동 시간과 소리] 제1권 4.7절 계산 2, 3의 본문 숫자')
d_sg = float(T.hav(*BD, *SG)); d_ks = float(T.hav(*BD, *KS))
add('20 m/s 이동 시간 (일), 원고 0.57', 0.57, d_sg * 1000 / 20 / 86400, 0.005, '원고(소수 둘째 자리)')
add('5 m/s 이동 시간 (일), 원고 2.27', 2.27, d_sg * 1000 / 5 / 86400, 0.005, '원고(소수 둘째 자리)')
add('소리 개성까지 (초), 원고 1,369', 1369.0, d_ks * 1000 / 340, 0.5, '원고')
add('소리 스이게쓰호까지 (초), 원고 2,887', 2887.0, d_sg * 1000 / 340, 0.5, '원고')
print('\n[몬테카를로 간격의 σ] 제1권 이론 배경 4: 독립 15.6, ρ=0.357 → 12.5, ρ=1 → 1.0')
add('독립(ρ=0) 간격 σ, 원고 15.6', 15.6, J4['rho0.000']['sd'], 0.05, '원고(소수 첫째 자리, 10만 번 대 이 장 200만 번)')
add('ρ=0.357 간격 σ, 원고 12.5', 12.5, J4['rho0.357']['sd'], 0.05, '원고')
add('ρ=1 간격 σ, 원고 1.0', 1.0, J4['rho1.000']['sd'], 0.05, '원고')
n_ok = sum(1 for r in rows if r[3])
print('\n요약: 비교 %d개, 일치 %d개, 차이 %d개' % (len(rows), n_ok, len(rows) - n_ok))
for r in rows:
    if not r[3]: print('  차이: %s 제1권 %.6g 이 장 %.6g [%s]' % (r[0], r[1], r[2], r[4]))
