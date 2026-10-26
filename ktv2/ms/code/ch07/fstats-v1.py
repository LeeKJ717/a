# -*- coding: utf-8 -*-
"""실습 7-10, 7-11, 7-12. f 통계(f3, f4, D, f4 비율)와 블록 잭나이프.
(가) 제1권 13장 계산 13-4, 13-5, 13-11의 시연값과 표 5를 같은 입력으로 되풀이해 맞추고,
(나) 유전자 빈도가 가지 위에서 표류하는 모의 자료(Balding-Nichols, 이 책의 시연값)에 직접 구현한 f4 비율과 D를 적용해
    참 혼합 비율을 되찾는지, 블록 잭나이프의 SE가 모의 반복의 표준편차와 맞는지 보고, (다) scikit-allel의 D와 f3와 대조한다.
사용: python fstats-v1.py"""
import math, sys, time
import numpy as np
import scipy
from scipy import stats
from gentools import f4_snp, f3_unbiased, wjack, block_sums, blocks

t0 = time.time()
print('numpy', np.__version__, '| scipy', scipy.__version__, '| python', sys.version.split()[0])

print('\n[1] 제1권 13장 계산 13-4의 시연값 되풀이 (SNP 8개)')
pO = np.array([0.10, 0.20, 0.15, 0.30, 0.25, 0.10, 0.20, 0.35])
pX = np.array([0.30, 0.45, 0.40, 0.50, 0.55, 0.30, 0.45, 0.60])
pY = np.array([0.35, 0.60, 0.30, 0.65, 0.70, 0.20, 0.60, 0.70])
pZ = np.array([0.25, 0.35, 0.45, 0.55, 0.40, 0.45, 0.30, 0.55])
print('  f4(O,X;Y,Z) = %.5f (제1권 -0.02719), 순서를 바꾼 f4(O,X;Z,Y) = %.5f (제1권 0.02719)' % (f4_snp(pO, pX, pY, pZ).mean(), f4_snp(pO, pX, pZ, pY).mean()))
print('  외집단 f3(O;X,Y) = %.5f (제1권 0.07500), X와 Z %.5f (0.04781), Y와 Z %.5f (0.05531)' % (((pX - pO) * (pY - pO)).mean(), ((pX - pO) * (pZ - pO)).mean(), ((pY - pO) * (pZ - pO)).mean()))
ab = np.array([118, 112, 121, 109, 117, 113, 120, 108, 116, 116], float)
ba = np.array([102, 98, 105, 95, 103, 97, 106, 94, 100, 100], float)
th, thj, se = wjack(ab - ba, ab + ba, np.ones(10))
print('  D = (ABBA-BABA)/(ABBA+BABA) = %.4f (제1권 0.0698); 이 책의 잭나이프 SE = %.4f (제1권 0.0015), Z = %.2f (제1권 46.18), 잭나이프 평균 %.4f' % (th, se, th / se, thj))
print('  (블록 크기가 같을 때 가중 블록 잭나이프는 제1권의 SE = sqrt((n-1)/n sum (D_i - 평균)^2)와 같아야 한다)')
th_i = np.array([((ab.sum() - ab[i]) - (ba.sum() - ba[i])) / ((ab.sum() - ab[i]) + (ba.sum() - ba[i])) for i in range(10)])
print('  제1권 식: %.6f, 이 책의 wjack: %.6f' % (math.sqrt(9 / 10 * ((th_i - th_i.mean()) ** 2).sum()), se))
print('  f4 비율 시연: alpha = 0.00040/0.00300 = %.3f (제1권 0.133)' % (0.00040 / 0.00300))
print('  Z -> 양쪽 p: |Z|=3.0 %.3e (제1권 2.700e-03), 4.541 %.3e (5.599e-06), 10.148 %.3e (3.382e-24), 1.96 %.3e (5.000e-02)' % tuple(2 * stats.norm.sf(z) for z in (3.0, 4.541, 10.148, 1.96)))
print('  다중 검정(|Z|>3, 참인 영가설 k개): ' + ', '.join('k=%d: %.1f%%' % (k, 100 * (1 - (1 - 2 * stats.norm.sf(3)) ** k)) for k in (20, 50, 100, 200)) + ' (제1권 5.3, 12.6, 23.7, 41.8)')
print('  블록 하나의 크기 3.1e9/714 = %.2f Mb (제1권 4.34, 게놈 길이 3.1e9는 외부 가정)' % (3.1e9 / 714 / 1e6))

print('\n[2] 제1권 13장 계산 13-5 ALDER 시연 되풀이(시드 13, 같은 호출 순서)')
rng = np.random.default_rng(13)
d_m = np.array([0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10])
obs = 0.004 * np.exp(-60 * d_m) * (1 + 0.04 * rng.standard_normal(len(d_m)))
sl, ic, r, pv, ses = stats.linregress(d_m, np.log(obs))
print('  로그 직선의 기울기 %.1f (SE %.1f) (제1권 -59.6, 0.8), n = %.1f세대, 29년 -> %.0f년 전 (제1권 1727)' % (sl, ses, -sl, -sl * 29))
print('  60~77세대 x 29년 = %d~%d년 전, x 25년 = %d~%d, x 30년 = %d~%d (제1권 1740~2233, 1500~1925, 1800~2310)' % (60 * 29, 77 * 29, 60 * 25, 77 * 25, 60 * 30, 77 * 30))

print('\n[3] 제1권 13.4.6절 표 5(후나도마리 f4 비율) 점검: 15줄')
T5 = [('혼슈 일본인', 'Korean', 0.873, 0.127, 0.024, 36.76), ('혼슈 일본인', 'CHB', 0.863, 0.137, 0.015, 56.33), ('혼슈 일본인', 'CHS', 0.816, 0.184, 0.016, 52.48),
      ('류큐', 'Korean', 0.734, 0.266, 0.024, 30.71), ('류큐', 'CHB', 0.726, 0.274, 0.018, 39.87), ('류큐', 'CHS', 0.686, 0.314, 0.018, 37.63),
      ('아이누', 'Korean', 0.338, 0.662, 0.040, 8.53), ('아이누', 'CHB', 0.334, 0.666, 0.039, 8.62), ('아이누', 'CHS', 0.316, 0.684, 0.037, 8.57),
      ('아이누', 'Ulchi', 0.509, 0.491, 0.053, 9.57), ('아이누', 'Hezhen', 0.457, 0.543, 0.049, 9.29), ('아이누', 'Itelmen', 0.869, 0.131, 0.127, 6.87),
      ('아이누', 'Koryak', 0.781, 0.219, 0.100, 7.80), ('아이누', '혼슈 일본인', 0.388, 0.612, 0.043, 9.10), ('아이누', '류큐', 0.461, 0.539, 0.048, 9.57)]
print('  alpha + (1-alpha) = 1: %s' % all(abs(a + b - 1) < 1e-9 for _, _, a, b, _, _ in T5))
mx = max(abs(a / s - z) for _, _, a, b, s, z in T5)
print('  alpha/SE와 표의 Z의 최대 차 = %.2f (제1권 1.48)' % mx)
# SE의 반올림 한도로 설명되는가: SE가 [SE-0.0005, SE+0.0005]에 있을 때 alpha/SE의 범위에 표의 Z가 드는가
ok1 = ok2 = 0
bad = []
for x, c, a, b, s, z in T5:
    lo, hi = a / (s + 0.0005), a / (s - 0.0005)
    ok1 += lo - 1e-9 <= z <= hi + 1e-9
    if lo - 0.005 <= z <= hi + 0.005:
        ok2 += 1
    if not (lo - 1e-9 <= z <= hi + 1e-9):
        bad.append((x, c, z, round(lo, 3), round(hi, 3)))
print('  SE가 소수 셋째 자리로 반올림되었다고 보고(+-0.0005) alpha/SE의 범위가 표의 Z를 포함하는 줄: %d/15' % ok1)
print('  Z도 소수 둘째 자리로 반올림되었다고 보고(+-0.005) 포함하는 줄: %d/15; 첫 기준에서 벗어난 줄: %s' % (ok2, bad))
for lab, key in (('혼슈 일본인', '혼슈 일본인'), ('류큐', '류큐')):
    v = [b for x, _, a, b, s, z in T5 if x == key]
    print('  %s의 조몬(F23) 몫 = %s -> %.1f~%.1f%%' % (lab, v, 100 * min(v), 100 * max(v)))
ai = [(c, b) for x, c, a, b, s, z in T5 if x == '아이누']
print('  아이누: 한국, CHB, CHS 기준 %.1f~%.1f%%, 북쪽 집단 4개 기준 %.1f~%.1f%%, 전체 폭 %.1f 퍼센트포인트 (제1권 66.2~68.4, 13.1~54.3, 55.3)' % (
    100 * min(b for _, b in ai[:3]), 100 * max(b for _, b in ai[:3]), 100 * min(b for _, b in ai[3:7]), 100 * max(b for _, b in ai[3:7]), 100 * (max(b for _, b in ai) - min(b for _, b in ai))))
print('  이텔멘 기준 SE 0.127은 혼슈-한국 SE 0.024의 %.1f배 (제1권 5.3)' % (0.127 / 0.024))

# ------------------------------------------------------------------ 모의
def bn(p, F, rng):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return rng.beta(p * (1 - F) / F, (1 - p) * (1 - F) / F)

def make(L, rng, alpha=0.3, nal=40, F=None):
    F = F or dict(O=0.05, s=0.04, C=0.03, A=0.02, B=0.02, X=0.01)
    p0 = rng.beta(2, 2, L)
    pO = bn(p0, F['O'], rng); ps = bn(p0, F['s'], rng); pC = bn(p0, F['C'], rng)
    pA = bn(ps, F['A'], rng); pB = bn(ps, F['B'], rng)
    pX = bn(alpha * pB + (1 - alpha) * pC, F['X'], rng)
    k = {nm: rng.binomial(nal, np.clip(p, 0, 1)) for nm, p in dict(O=pO, A=pA, B=pB, C=pC, X=pX).items()}
    tot = sum(k.values())
    keep = (tot > 0) & (tot < 5 * nal)
    return {nm: v[keep] for nm, v in k.items()}, nal

def stats_from(k, nal, nb):
    f = {nm: v / nal for nm, v in k.items()}
    num = f4_snp(f['O'], f['A'], f['X'], f['C'])
    den = f4_snp(f['O'], f['A'], f['B'], f['C'])
    sn, m = block_sums(num, nb); sd, _ = block_sums(den, nb)
    a, aj, se = wjack(sn, sd, m)
    dn = (f['A'] - f['X']) * (f['C'] - f['O'])                    # D(A,X;C,O)
    dd = (f['A'] + f['X'] - 2 * f['A'] * f['X']) * (f['C'] + f['O'] - 2 * f['C'] * f['O'])
    s1, _ = block_sums(dn, nb); s2, _ = block_sums(dd, nb)
    D, Dj, Dse = wjack(s1, s2, m)
    nn = (f['A'] - f['B']) * (f['C'] - f['O'])                    # D(A,B;C,O): 영가설이 참인 비교
    nd = (f['A'] + f['B'] - 2 * f['A'] * f['B']) * (f['C'] + f['O'] - 2 * f['C'] * f['O'])
    s3, _ = block_sums(nn, nb); s4, _ = block_sums(nd, nb)
    D0, D0j, D0se = wjack(s3, s4, m)
    return dict(a=a, aj=aj, se=se, D=D, Dse=Dse, D0=D0, D0se=D0se, f4den=sd.sum() / m.sum())

print('\n[4] 모의: 뿌리에서 O, (A,B), C가 갈라지고 X = 0.3 B + 0.7 C(참 alpha = 0.3). 표류 F: O 0.05, (A,B)공유 0.04, C 0.03, A 0.02, B 0.02, X 0.01')
rng = np.random.default_rng(2026)
k, nal = make(200000, rng)
print('  SNP %d개(표본에서 다형인 것), 집단마다 대립유전자 %d개(이배체 20명), 블록 100개 (시연값, 시드 2026)' % (len(k['O']), nal))
s = stats_from(k, nal, 100)
print('  f4 비율 alpha = f4(O,A;X,C)/f4(O,A;B,C) = %.4f, 잭나이프 SE = %.4f, 잭나이프 평균 = %.4f, 참값 0.3 -> (추정-참)/SE = %+.2f' % (s['a'], s['se'], s['aj'], (s['a'] - 0.3) / s['se']))
print('  분모 f4(O,A;B,C) = %.5f (부호가 음수이면 A와 B가 O와 C보다 함께 표류했다는 뜻)' % s['f4den'])
print('  D(A,X;C,O) = %.4f, SE = %.4f, Z = %.2f (X가 C와 섞였으므로 영가설이 거짓)' % (s['D'], s['Dse'], s['D'] / s['Dse']))
print('  D(A,B;C,O) = %.4f, SE = %.4f, Z = %.2f (A와 B는 자매이므로 영가설이 참)' % (s['D0'], s['D0se'], s['D0'] / s['D0se']))

print('\n[5] 모의 반복으로 SE를 검증: SNP 20000개(블록 50개), 반복 400회(시드 7), 참 alpha = 0.3')
R = 400
rng = np.random.default_rng(7)
res = []
for _ in range(R):
    k, nal = make(20000, rng)
    res.append(stats_from(k, nal, 50))
a = np.array([r['a'] for r in res]); se = np.array([r['se'] for r in res])
z0 = np.array([r['D0'] / r['D0se'] for r in res])
print('  alpha 추정: 평균 %.4f, 반복 사이 표준편차 %.4f | 잭나이프 SE의 평균 %.4f, 중앙값 %.4f' % (a.mean(), a.std(ddof=1), se.mean(), np.median(se)))
print('  +-1.96 SE 구간이 참값 0.3을 포함한 비율 = %.3f (이상적으로 0.95; 모의 표준오차 약 0.011)' % np.mean(np.abs(a - 0.3) <= 1.96 * se))
print('  영가설이 참인 D(A,B;C,O)의 Z: 평균 %.3f, 표준편차 %.3f, |Z| > 3인 비율 %.3f, |Z| > 1.96인 비율 %.3f (이상적으로 0, 1, 0.003, 0.05)' % (z0.mean(), z0.std(ddof=1), np.mean(np.abs(z0) > 3), np.mean(np.abs(z0) > 1.96)))

print('\n[6] scikit-allel(MIT)의 D, f3와 대조: [4]의 같은 모의 자료(시드 2026)')
try:
    import allel
    rng = np.random.default_rng(2026)
    k, nal = make(200000, rng)
    L = len(k['O'])
    ac = {nm: np.stack([nal - v, v], 1) for nm, v in k.items()}
    nb = 100
    blen = L // nb
    d, se_a, z_a, vb, jk = allel.average_patterson_d(ac['A'], ac['X'], ac['C'], ac['O'], blen)
    f = {nm: v / nal for nm, v in k.items()}
    dn = (f['A'] - f['X']) * (f['C'] - f['O'])
    dd = (f['A'] + f['X'] - 2 * f['A'] * f['X']) * (f['C'] + f['O'] - 2 * f['C'] * f['O'])
    # scikit-allel은 길이 blen의 블록만 쓰고 남는 끝은 버린다. 같은 SNP 구간(0 ~ blen*nb)으로 맞춘다.
    n_use = blen * nb
    s1 = dn[:n_use].reshape(nb, blen).sum(1); s2 = dd[:n_use].reshape(nb, blen).sum(1)
    D, Dj, Dse = wjack(s1, s2, np.full(nb, blen))
    print('  scikit-allel %s: D(A,X;C,O) = %.6f, SE = %.6f, Z = %.3f (블록 길이 %d, 블록 %d개)' % (allel.__version__, d, se_a, z_a, blen, nb))
    print('  이 책:                 D = %.6f, SE = %.6f, Z = %.3f' % (D, Dse, D / Dse))
    T, B = allel.patterson_f3(ac['X'], ac['A'], ac['C'])
    mine = f3_unbiased(f['X'], f['A'], f['C'], nal)
    print('  f3(X; A, C): scikit-allel 평균 T = %.8f, 이 책 평균 = %.8f, 최대 절대 차 = %.2e' % (T.mean(), mine.mean(), np.abs(T - mine).max()))
except Exception as e:
    print('  scikit-allel를 불러오지 못했거나 실패:', repr(e))
print('\n총 걸린 시간 %.2f s' % (time.time() - t0))
