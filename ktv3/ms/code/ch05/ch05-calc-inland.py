# -*- coding: utf-8 -*-
"""5장 계산 5-8 ~ 5-12: 보스텐호, 롭노르와 누란, 이식쿨, 카라쿨, 그리고 기록 사이의 동시성.
입력은 논문 초록·본문이 적은 연대와 수치뿐이다. 실행: python3 ch05-calc-inland.py (numpy, scipy)"""
import json, math
import numpy as np
from scipy.stats import fisher_exact
out = {}

# ------------------------------------------------------------------ 계산 5-8: 보스텐호 건조기 (Wunnemann 등 2006)
print('== 계산 5-8: 보스텐호 건조기 (Wunnemann 등 2006, 단위 cal ka BP) ==')
dry = [(8.5, 8.1), (7.3, 7.1), (6.0, 6.0), (5.4, 5.0), (4.6, 4.3), (3.9, 3.6), (3.4, 3.2), (2.6, 2.5), (1.9, 1.1), (0.5, 0.3), (0.18, 0.05)]
span = 8.6
dur = [round(a - b, 3) for a, b in dry]
tot = sum(dur)
print('건조기 %d개, 길이(ka): %s' % (len(dry), dur))
print('건조기 길이 합 %.2f ka / 기록 길이 %.1f ka = %.1f%%' % (tot, span, 100 * tot / span))
print('6.0 ka 는 구간이 아닌 한 시점(길이 0)으로 적혀 있다.')
starts = [a for a, b in dry]
gaps = [round(starts[i] - starts[i + 1], 3) for i in range(len(starts) - 1)]
print('이웃 건조기 시작 간격(ka):', gaps, '평균 %.2f ka, 표준편차 %.2f' % (np.mean(gaps), np.std(gaps, ddof=1)))
# 4.2 ka 창(4.3~3.9)과의 관계
for lo, hi, nm in ((3.9, 4.3, '4.3~3.9 ka'), (3.8, 4.4, '4.4~3.8 ka (=4.1±0.3 ka)')):
    ov = sum(max(0, min(a, hi) - max(b, lo)) for a, b in dry)
    print('%s 창(%.1f ka)에서 건조기와 겹치는 길이 %.2f ka (%.0f%%)' % (nm, hi - lo, ov, 100 * ov / (hi - lo)))
    out['5-8-' + nm] = dict(window=hi - lo, overlap=ov)
print('4.6~4.3 ka 건조기 끝(4.3)과 3.9~3.6 ka 건조기 시작(3.9) 사이 비건조 구간 = %.1f ka = %d년' % (4.3 - 3.9, round((4.3 - 3.9) * 1000)))
out['5-8'] = dict(n=len(dry), durations=dur, total=tot, frac=tot / span, gap_mean=float(np.mean(gaps)), gap_sd=float(np.std(gaps, ddof=1)))
# 1천년 단위 건조 비율
bins = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 8.6)]
bf = []
for lo, hi in bins:
    ov = sum(max(0, min(a, hi) - max(b, lo)) for a, b in dry)
    bf.append((lo, hi, ov / (hi - lo)))
    print('  %.0f~%.1f ka: 건조 비율 %.0f%%' % (lo, hi, 100 * ov / (hi - lo)))
out['5-8-bins'] = bf

# ------------------------------------------------------------------ 계산 5-9: 아랄해 저수위 표지와 보스텐 건조기의 동시성
print('\n== 계산 5-9: 아랄해 얕은 물 표지 4개(Krivonogov 등 2010)가 보스텐 건조기와 우연보다 자주 겹치는가 ==')
aral = [8.0, 7.2, 5.6, 4.5]
tol = 0.1
def hit(t, dry, tol): return any(b - tol <= t <= a + tol for a, b in dry)
hits = [hit(t, dry, tol) for t in aral]
print('아랄 표지 %s ka, 허용 ±%.1f ka: 건조기 안 %s, 적중 %d/%d' % (aral, tol, hits, sum(hits), len(aral)))
for t, h in zip(aral, hits):
    near = min(dry, key=lambda ab: min(abs(t - ab[0]), abs(t - ab[1])) if not (ab[1] <= t <= ab[0]) else 0)
    print('   %.1f ka: 가장 가까운 건조기 %s' % (t, near))
rng = np.random.default_rng(20261026)
lo, hi = 4.0, 8.5
N = 1_000_000
cnt = 0
obs = sum(hits)
# 같은 구간(4.0~8.5 ka)에서 표지 4개를 무작위로 놓았을 때 적중 수의 분포
U = rng.uniform(lo, hi, size=(N, 4))
H = np.zeros((N, 4), bool)
for a, b in dry:
    H |= (U >= b - tol) & (U <= a + tol)
hs = H.sum(1)
p = (hs >= obs).mean()
print('무작위 %d회: 적중 수 분포 %s, P(적중 >= %d) = %.4f' % (N, [round(float((hs == k).mean()), 4) for k in range(5)], obs, p))
cov = sum(max(0, min(a + tol, hi) - max(b - tol, lo)) for a, b in dry) / (hi - lo)
print('허용폭을 포함한 건조기의 덮개 비율(4.0~8.5 ka) = %.3f' % cov)
out['5-9'] = dict(hits=hits, p=float(p), cover=cov, dist=[float((hs == k).mean()) for k in range(5)])

# ------------------------------------------------------------------ 계산 5-10: 누란 (Mischke 등 2017)
print('\n== 계산 5-10: 누란 쇠퇴와 호수 기록 (Mischke 등 2017) ==')
inside_dec = 4     # Lop Nur, Bosten, Eastern Juyan, Zhuyeze: 줄거나 마름
inside_wet = 0
outside_wet = 11   # Sayram, Aibi, Wulungu, Balikun, Karakul, Karakuli, Issyk-Kul, Manas, Hurleg, Qinghai, Hala
outside_dec = 0
tab = [[inside_dec, inside_wet], [outside_dec, outside_wet]]
orr, p2 = fisher_exact(tab)
print('2x2 표 [[한 영역 안 쇠퇴, 안 습윤],[밖 쇠퇴, 밖 습윤]] =', tab, ' Fisher 양쪽 p = %.5f' % p2)
print('조합으로 확인: 1 / C(15,4) = 1/%d = %.5f' % (math.comb(15, 4), 1 / math.comb(15, 4)))
print('주의: "한 영역 안/밖"과 "쇠퇴/습윤" 분류는 논문 저자가 기록을 읽고 정했다. p 값은 분류가 독립이라는 가정 아래서만 뜻이 있다.')
out['5-10-fisher'] = dict(table=tab, p=float(p2), comb=math.comb(15, 4))
# 누란 포기 시작 230 ± 66 CE
for k, nm in ((1, '68%'), (2, '95%')):
    print('포기 시작 230 ± 66 CE 를 1표준편차로 보면 %s 구간 %d ~ %d CE' % (nm, 230 - k * 66, 230 + k * 66))
print('논문의 쇠퇴 창 200~645 CE 의 길이 = %d년; 한 제국 한나라 206 BCE ~ 220 CE 의 길이 = %d년' % (645 - 200, 220 + 205))
print('기원전 206년은 천문연대로 -205 이므로 220 - (-205) = %d년' % (220 + 205))
print('8500년 전(가장 습함)에서 7000년 전(유입 큰 감소)까지 = %d년, 7000년 전에서 2300년 전 = %d년' % (8500 - 7000, 7000 - 2300))
out['5-10-dates'] = dict(onset_68=(164, 296), onset_95=(98, 362))

# ------------------------------------------------------------------ 계산 5-11: 이식쿨, 카라쿨 해상도
print('\n== 계산 5-11: 이식쿨과 카라쿨 ==')
print('Ricketts 등(2001): 16개 AMS 14C 날짜가 8700~1000 cal BP(%d년)를 덮는다 -> 날짜 하나당 평균 %.0f년' % (8700 - 1000, (8700 - 1000) / 16))
phases = [('8700~8300', 8700, 8300), ('8300~6900', 8300, 6900), ('6900~4900 (전이)', 6900, 4900)]
for nm, a, b in phases:
    n = (a - b) / ((8700 - 1000) / 16)
    print('  %-16s %4d년, 평균 간격이면 날짜 %.1f개' % (nm, a - b, n))
print('4900 cal BP 이후 길이 4900 - 1000 = %d년' % (4900 - 1000))
print('Mischke 등(2010) 카라쿨: 코어 104 cm / 4200 cal yr = %.4f cm/yr = %.3f mm/yr' % (104 / 4200, 104 / 4200 * 10))
print('  "40년 안에" TOC 급락 = 평균 퇴적률로 %.2f cm (1 cm 시료이면 1~2개)' % (40 * 104 / 4200))
print('  4200~3500 cal BP 의 길이 %d년, 그 사이 코어 두께(평균 퇴적률) %.1f cm' % (700, 700 * 104 / 4200))
out['5-11'] = dict(ricketts_years_per_date=(8700 - 1000) / 16, karakul_cm_per_yr=104 / 4200, abrupt_cm=40 * 104 / 4200)
print('Leroy 등(2021) 이식쿨: 고도 1607 m, 빙하 봉우리는 2 km 이상 높다. 1607 + 2000 = 3607 m 이상 (논문 표현 "more than 2 km higher"의 단순 합)')

# ------------------------------------------------------------------ 계산 5-12: 카스피해-아랄-보스텐의 8~7 ka 낮은 수위
print('\n== 계산 5-12: 8.5~7 ka 구간에서 기록별 저수위 신호 ==')
events = {
 'Bosten 건조 8.5~8.1': (8.5, 8.1), 'Bosten 건조 7.3~7.1': (7.3, 7.1),
 'Aral 얕은 물 8.0': (8.0, 8.0), 'Aral 얕은 물 7.2': (7.2, 7.2),
 'Caspian SE 하강 8.4': (8.4, 8.4), 'Caspian SE 후퇴 7.7': (7.7, 7.7),
 'Issyk-Kul 수위 상승 10.0~8.0 (Leroy 2021)': (10.0, 8.0),
 'Lop Nur 가장 습함 8.5': (8.5, 8.5),
}
for k, (a, b) in events.items():
    print('  %-44s %.2f ~ %.2f ka' % (k, a, b))
print('Lop Nur 가장 습함(8.5 ka)과 Bosten 건조 8.5~8.1 ka 는 같은 때 반대 방향이다: 겹침 %.1f ka (점 대 구간 경계)' % 0)
print('Issyk-Kul 수위가 오르는 10~8 ka 와 Bosten 건조 8.5~8.1 ka 의 겹침 = %.1f ka' % (min(10, 8.5) - max(8, 8.1)))
out['5-12'] = dict(issyk_vs_bosten_overlap=min(10, 8.5) - max(8, 8.1))
json.dump(out, open('ch05-calc-inland.json', 'w'), ensure_ascii=False, indent=1, default=float)
