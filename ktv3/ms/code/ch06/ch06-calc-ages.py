# -*- coding: utf-8 -*-
"""6장 계산 6-1 ~ 6-3: 연대 점추정의 일치, Carolin 등의 검정 되풀이, 호륜호 사건 경계의 재현과 몬테카를로.
실행: python3 ch06-calc-ages.py (numpy, scipy)"""
import json, math
import numpy as np
from scipy.stats import chi2, norm
out = {}

def wmean(vals, sig):
    v = np.array(vals, float); s = np.array(sig, float); w = 1 / s ** 2
    m = (v * w).sum() / w.sum(); e = 1 / math.sqrt(w.sum()); q = (((v - m) / s) ** 2).sum()
    return m, e, q, len(v) - 1

print('== 계산 6-1: 서아시아 점추정들은 한 시각을 가리키는가 (연대 cal yr BP, 오차는 논문 표기를 1 표준편차로 가정) ==')
A = [('골에자르드 먼지 둘째 사건 시작(Carolin 등 2019)', 4260, 66), ('오만만 먼지 급증(Cullen 등 2000 초록)', 4025, 125),
     ('홍해 건조 사건(Carolin 등이 인용)', 4200, 100), ('오만만 먼지 급증(Carolin 등이 인용)', 4100, 100)]
for n, v, s in A: print('  %-52s %d ± %d' % (n, v, s))
m, e, q, df = wmean([a[1] for a in A], [a[2] for a in A])
print('가중평균 %.1f ± %.1f, Q = %.2f, 자유도 %d, p = %.3f' % (m, e, q, df, chi2.sf(q, df)))
out['6-1-A'] = dict(m=m, e=e, Q=q, df=df, p=float(chi2.sf(q, df)))
A2 = [(a if a[0].find('초록') < 0 else ('오만만 먼지 급증(Cullen 등 2000 본문 ± 150)', 4025, 150)) for a in A]
m2, e2, q2, df2 = wmean([a[1] for a in A2], [a[2] for a in A2])
print('Cullen 등을 본문 값 4025 ± 150 으로 바꾸면: 가중평균 %.1f ± %.1f, Q = %.2f, p = %.3f' % (m2, e2, q2, chi2.sf(q2, df2)))
out['6-1-A2'] = dict(m=m2, e=e2, Q=q2, p=float(chi2.sf(q2, df2)))
B = [('북메소포타미아 정착지 포기(Carolin 등 2019)', 4190, 20), ('아카드 붕괴(Cullen 등 2000)', 4170, 150)]
m3, e3, q3, df3 = wmean([b[1] for b in B], [b[2] for b in B])
print('고고 연대 둘: 가중평균 %.1f ± %.1f, Q = %.3f, p = %.3f' % (m3, e3, q3, chi2.sf(q3, df3)))
out['6-1-B'] = dict(m=m3, e=e3, Q=q3, p=float(chi2.sf(q3, df3)))
# 건조·먼지 연대의 가중평균과 고고 연대의 차
d = m - m3; sd = math.hypot(e, e3)
print('먼지·건조 가중평균 %.1f 와 고고 가중평균 %.1f 의 차 = %.1f ± %.1f (z = %.2f)' % (m, m3, d, sd, d / sd))
out['6-1-diff'] = dict(d=d, sd=sd, z=d / sd)
print('정의가 다른 값(시작, 급증 시점, 중심)을 한데 묶었으므로 이 평균은 "서로 맞는지"를 보는 시연이다.')

print('\n== 계산 6-2: Carolin 등(2019) 검정 되풀이 ==')
on = (4260, 66); ab = (4190, 20)
dz = (on[0] - ab[0]) / math.hypot(on[1], ab[1])
print('먼지 시작 %d ± %d 와 정착지 포기 %d ± %d: 차 %d, 합성 오차 %.1f, z = %.2f, 양쪽 p = %.3f' % (on + ab + (on[0] - ab[0], math.hypot(on[1], ab[1]), dz, 2 * norm.sf(abs(dz)))))
out['6-2-onset-vs-abandon'] = dict(z=dz, p=float(2 * norm.sf(abs(dz))))
cu = (4025, 125)
dz2 = (on[0] - cu[0]) / math.hypot(on[1], cu[1])
print('골에자르드 시작 %d ± %d 와 오만만 %d ± %d: 차 %d, 합성 %.1f, z = %.2f, 양쪽 p = %.3f' % (on + cu + (on[0] - cu[0], math.hypot(on[1], cu[1]), dz2, 2 * norm.sf(abs(dz2)))))
out['6-2-gol-vs-oman'] = dict(z=dz2, p=float(2 * norm.sf(abs(dz2))))
print('Carolin 등: 둘째 사건 4.26 ka ~ 3.97 ka = %d년 (논문 290년), 첫째 사건 4.51 ka, 110년 -> 끝 %d' % (4260 - 3970, 4510 - 110))
print('두 사건 사이 간격: 첫째 끝 %d, 둘째 시작 %d -> %d년' % (4510 - 110, 4260, 4510 - 110 - 4260))
print('U-Th 25개가 5.2~3.7 ka(%d년)를 덮는다 -> 날짜 간격 평균 %.0f년; 사건 290년 안에 날짜 약 %.1f개' % (1500, 1500 / 25, 290 / (1500 / 25)))
out['6-2-density'] = dict(years_per_age=1500 / 25, ages_in_event=290 / (1500 / 25))
print('Cullen 등: 초록 4025 ± 125, 약 300년 / 본문 4025 ± 150, 4025~3625 = %d년 -> 초록과 본문이 다르다' % (4025 - 3625))
print('Meghalayan 시작 4250 yr b2k = 4250 - 50 = %d cal BP (b2k 는 2000년 기준, BP 는 1950년 기준)' % (4250 - 50))
out['6-2-b2k'] = 4250 - 50

print('\n== 계산 6-3: 호륜호 사건 경계의 재현과 몬테카를로 (Xiao 등 2018 표 1) ==')
# 보정 연대 2시그마 범위의 중간값을 점으로, (끝-시작)/4 를 1 표준편차로 근사한다(비대칭 분포이므로 근사).
pts = [  # 깊이(cm, 시료 중간), 범위
 (101.5, (5290, 5470)), (89.5, (4230, 4430)), (79.5, (3470, 3690)), (69.5, (2970, 3220)), (59.5, (2480, 2650))]
dep = np.array([p[0] for p in pts]); mid = np.array([(p[1][0] + p[1][1]) / 2 for p in pts]); sg = np.array([(p[1][1] - p[1][0]) / 4 for p in pts])
for p, m_, s_ in zip(pts, mid, sg): print('  깊이 %.1f cm: 범위 %s -> 중간 %.0f, 1시그마 근사 %.1f' % (p[0], p[1], m_, s_))
def age_at(d):
    return np.interp(-d, -dep, mid)   # 깊이는 내려갈수록 오래됨; np.interp 는 증가 x 필요
a88 = age_at(88); a83 = age_at(83)
print('선형 보간 나이: 깊이 88 cm = %.1f, 83 cm = %.1f cal yr BP (논문 4210, 3840), 길이 %.1f년' % (a88, a83, a88 - a83))
out['6-3-interp'] = dict(a88=float(a88), a83=float(a83))
rng = np.random.default_rng(20261026)
N = 200000
a = rng.normal(mid[1], sg[1], N); b = rng.normal(mid[2], sg[2], N)    # 89.5, 79.5 cm 날짜(독립으로 가정)
f88 = (89.5 - 88) / 10.0; f83 = (89.5 - 83) / 10.0
s88 = a + f88 * (b - a)   # 깊이 88 cm 나이(젊은 쪽으로 f 만큼)
s83 = a + f83 * (b - a)
# 위 식: 깊이가 얕아질수록 젊어짐. f = (89.5 - d)/10
print('몬테카를로 %d회: 사건 시작(88 cm) %.0f ± %.0f, 끝(83 cm) %.0f ± %.0f, 길이 %.0f ± %.0f' % (N, s88.mean(), s88.std(), s83.mean(), s83.std(), (s88 - s83).mean(), (s88 - s83).std()))
out['6-3-mc'] = dict(start=float(s88.mean()), start_sd=float(s88.std()), end=float(s83.mean()), end_sd=float(s83.std()), dur=float((s88 - s83).mean()), dur_sd=float((s88 - s83).std()))
gol = rng.normal(4260, 66, N)
p_younger = (s88 < gol).mean()
print('P(호륜호 시작 < 골에자르드 시작) = %.3f  (호륜호가 더 젊을 확률)' % p_younger)
diff = gol - s88
print('시작 연대 차(골 - 호륜) = %.0f ± %.0f년' % (diff.mean(), diff.std()))
lo, hi = np.percentile(diff, [2.5, 97.5])
print('95%% 구간 %.0f ~ %.0f년 (0을 %s)' % (lo, hi, '포함' if lo < 0 < hi else '포함하지 않음'))
out['6-3-vs-gol'] = dict(p_younger=float(p_younger), mean=float(diff.mean()), sd=float(diff.std()), lo=float(lo), hi=float(hi))
# 끝 연대 비교: 골 3970 (끝은 시작 오차 66 에 길이 오차는 모른다 -> 시작 오차를 그대로 쓰는 것은 과소)
print('주의: 골에자르드 끝 연대(3970)의 오차는 이 책이 읽은 쪽에 없다. 위 비교는 시작 연대만 다룬다.')
json.dump(out, open('ch06-calc-ages.json', 'w'), ensure_ascii=False, indent=1, default=float)
