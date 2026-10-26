# -*- coding: utf-8 -*-
"""5장 계산 5-3 ~ 5-7: 카스피해. 입력은 논문 표(Kroonenberg 등 2007 표 1, Naderi Beni 등 2013 표 2·3·4·5·7 중 읽은 값, Leroy 등 2014·2022, Kakroodi 등 2015 초록)이다.
방사성탄소 보정 곡선(IntCal20, Marine20 등)을 이 컨테이너에서 구하지 못했으므로 보정은 하지 않는다. 보정 연대는 논문이 적은 값을 그대로 쓴다.
실행: python3 ch05-calc-caspian.py (numpy 사용)"""
import json, math
import numpy as np
out = {}

def wmean(vals, sig):
    v = np.array(vals, float); s = np.array(sig, float)
    w = 1 / s ** 2
    m = (v * w).sum() / w.sum()
    e = 1 / math.sqrt(w.sum())
    chi2 = (((v - m) / s) ** 2).sum()
    return m, e, chi2, len(v) - 1

# ------------------------------------------------------------------ 계산 5-3: 저수지 효과 대조 시료
print('== 계산 5-3: 현대 대조 시료로 저수지 연령 구하기 ==')
ctrl = [(299, 41), (283, 35)]   # UtC-11479, UtC-11477 (Kroonenberg 등 2007, 표 1)
m, e, chi2, dof = wmean([c[0] for c in ctrl], [c[1] for c in ctrl])
print('가중평균 %.1f ± %.1f, chi2 = %.3f (자유도 %d)' % (m, e, chi2, dof))
print('단순평균 %.1f, 두 값 차 %d, 두 값 오차의 합성 %.1f' % (np.mean([299, 283]), 299 - 283, math.hypot(41, 35)))
print('논문이 쓴 저수지 보정은 290 ± 30. 가중평균 오차 %.1f 는 이 값과 다르다(논문이 오차를 어떻게 정했는지 읽은 쪽에 없다).' % e)
out['5-3-ctrl'] = dict(wmean=m, err=e, chi2=chi2)
d = 351 - 290
print('Leroy 등(2022)의 저수지 보정 351 ± 33 과 Kroonenberg 등의 290 ± 30 의 차 = %d ± %.1f년 (z = %.2f)' % (d, math.hypot(33, 30), d / math.hypot(33, 30)))
print('같은 14C 나이에서 저수지 보정을 %d년 더 빼면 14C 나이가 %d년 젊어진다(곡선 효과는 보정 곡선이 있어야 계산할 수 있다).' % (d, d))
out['5-3-dr'] = dict(diff=d, sigma=math.hypot(33, 30), z=d / math.hypot(33, 30))

# ------------------------------------------------------------------ 계산 5-4: 석호 시료 14C 나이의 일치
print('\n== 계산 5-4: Kroonenberg 등(2007) 표 1의 석호 시료 14C 나이는 한 사건인가 ==')
T1 = [  # (시료, 고도 m, 14C, 오차, 논문 보정범위 cal BP)
 ('HV#06a', -24.10, 525, 33, (240, 360)), ('HV#08b', -24.70, 2603, 33, (2340, 2470)),
 ('HVDag14a', -27.30, 2747, 35, (2560, 2710)), ('HV#04c', -24.00, 2350, 43, (2020, 2190)),
 ('HV#03a', -24.60, 837, 33, (510, 600)), ('HV#01a', -26.50, 2373, 38, (2080, 2240)),
 ('HV#02c', -26.50, 2366, 30, (2050, 2210)), ('HVDag8a', -28.00, 2504, 34, (2210, 2230)),
 ('HVDag9B', -25.15, 2370, 40, (2060, 2240)), ('HVDag1T', -25.25, 2322, 37, (2000, 2140)),
 ('HVDag10A', -25.55, 2517, 41, (2240, 2390)), ('HVDagK', -26.00, 2507, 35, (2210, 2230)),
]
print('표 1에서 대조 시료 2개를 뺀 시료 수:', len(T1))
old = [t for t in T1 if t[2] > 2000]
young = [t for t in T1 if t[2] < 2000]
print('2000 BP 보다 오래된 시료 %d개, 젊은 시료(LIA 쪽) %d개' % (len(old), len(young)))
m, e, chi2, dof = wmean([t[2] for t in old], [t[3] for t in old])
from scipy.stats import chi2 as C2
print('오래된 %d개 전체: 가중평균 %.1f ± %.1f, chi2 = %.1f, 자유도 %d, p = %.2e' % (len(old), m, e, chi2, dof, C2.sf(chi2, dof)))
lowc = [t for t in old if t[2] < 2400]
highc = [t for t in old if 2400 <= t[2] < 2700]
for nm, g in (('2300대(<2400)', lowc), ('2500대(2400~2700)', highc)):
    mm, ee, cc, dd = wmean([t[2] for t in g], [t[3] for t in g])
    print('  %-18s n=%d 가중평균 %.1f ± %.1f chi2=%.2f 자유도 %d p=%.3f' % (nm, len(g), mm, ee, cc, dd, C2.sf(cc, dd)))
    out['5-4-' + nm] = dict(n=len(g), m=mm, e=ee, chi2=cc, dof=dd, p=float(C2.sf(cc, dd)))
mm1, ee1, _, _ = wmean([t[2] for t in lowc], [t[3] for t in lowc])
mm2, ee2, _, _ = wmean([t[2] for t in highc], [t[3] for t in highc])
z = (mm2 - mm1) / math.hypot(ee1, ee2)
print('두 군의 평균 차 = %.1f ± %.1f 년 (z = %.1f)' % (mm2 - mm1, math.hypot(ee1, ee2), z))
out['5-4-all'] = dict(n=len(old), m=m, e=e, chi2=chi2, dof=dof, p=float(C2.sf(chi2, dof)), gap=mm2 - mm1, gap_z=z)
lo = min(t[4][0] for t in old); hi = max(t[4][1] for t in old)
print('오래된 시료의 논문 보정범위 최소 %d, 최대 %d cal BP (폭 %d년)' % (lo, hi, hi - lo))
# 고도: 오래된 시료의 고도 범위
el = [t[1] for t in old]
print('오래된 시료의 고도(Kronshtadt 기준) %.2f ~ %.2f m' % (min(el), max(el)))
# 보정범위가 서로 겹치는 쌍 수(정확한 겹침)
def ovl(a, b): return max(0, min(a[1], b[1]) - max(a[0], b[0]))
pairs = [(i, j) for i in range(len(old)) for j in range(i + 1, len(old))]
cnt = sum(1 for i, j in pairs if ovl(old[i][4], old[j][4]) > 0)
print('오래된 시료 쌍 %d개 중 보정범위가 겹치는 쌍 %d개 (%.0f%%)' % (len(pairs), cnt, 100 * cnt / len(pairs)))
out['5-4-pairs'] = dict(pairs=len(pairs), overlapping=cnt)
# 2600 BP 근방 시료: 보정범위가 2600 cal BP 를 품는 시료
inc = [t[0] for t in old if t[4][0] <= 2600 <= t[4][1]]
print('보정범위가 2600 cal BP 를 품는 시료: %s' % inc)
out['5-4-incl2600'] = inc

# ------------------------------------------------------------------ 계산 5-5: Naderi Beni 코어 연대와 수위
print('\n== 계산 5-5: Naderi Beni 등(2013) 표 2: 코어 연대와 수위 ==')
core = [('A', 'Poz-51062', -25.3, 145, 665, 35), ('B', 'Poz-51060', -24.8, 100, 790, 30)]
for c, lab, elev, dep, a14, s in core:
    lvl = elev - dep / 100
    print('코어 %s %s: 고도 %.1f m - 시료 깊이 %d cm = %.2f m' % (c, lab, elev, dep, lvl))
    for RE, rs in ((407, 27), (383, 0)):
        age = a14 - RE; sg = math.hypot(s, rs)
        print('   저수지 %d ± %d 를 뺀 14C 나이 = %d ± %.0f BP' % (RE, rs, age, sg))
out['5-5'] = {'A': -25.3 - 1.45, 'B': -24.8 - 1.0}

# ------------------------------------------------------------------ 계산 5-6: 세 문헌 계열의 대조
print('\n== 계산 5-6: Bruckner(1890), Karpychev(1998, 2001), Varushchenko 등(1987)의 연도별 수위 (표 3, 5, 4) ==')
# 같은 해(구간)에 대한 세 값 (논문이 옮긴 표에서 읽은 것, 단위 m). 값이 없는 칸은 None.
M = [  # (구간 라벨, 시각(중간연도), Bruckner, Karpychev, Varushchenko)
 ('1715~1720', 1717.5, -25.9, -26.0, -25.5),
 ('1735~1750', 1742.0, -22.7, -23.0, -23.0),   # B 1735~43, K 1740~50 '역사 증거' -23, V 1745
 ('1795~1810', 1802.0, -22.7, -22.0, -22.85),  # B 1805, K 1795~1810, V 1796 (-22.7~-23 의 중간)
 ('1809~1817', 1813.0, -23.8, None, -23.85),   # B 1816, V 1809~1817 (-23.7~-24 의 중간)
 ('1819~1821', 1820.0, None, None, -24.2),
]
rows = [m_ for m_ in M if sum(1 for v in m_[2:] if v is not None) >= 2]
diffs = []
for lab, t, b, k, v in rows:
    vals = [x for x in (b, k, v) if x is not None]
    print('%-10s B=%s K=%s V=%s 최대-최소 = %.2f m' % (lab, b, k, v, max(vals) - min(vals)))
    diffs.append(max(vals) - min(vals))
print('%d개 구간에서 최대-최소 평균 %.2f m, 최대 %.2f m' % (len(diffs), np.mean(diffs), max(diffs)))
out['5-6-spread'] = dict(n=len(diffs), mean=float(np.mean(diffs)), max=float(max(diffs)))
# Bruckner 표에서 상승률: 1715~1720(-25.9) -> 1735~1743(-22.7)
t1 = (1715 + 1720) / 2; t2 = (1735 + 1743) / 2
rate = (-22.7 - -25.9) / (t2 - t1)
print('Bruckner: %.1f년 %.1f m -> %.1f년 %.1f m, 상승 %.1f m, %.1f년, 평균 %.1f cm/yr' % (t1, -25.9, t2, -22.7, 3.2, t2 - t1, 100 * rate))
out['5-6-rate'] = dict(years=t2 - t1, rise=3.2, cm_per_yr=100 * rate)
# 1843~1878 (기기 관측 직전): Bruckner 중간연도 회귀
B = [(1844.5, -26.7), (1847, -26.0), (1853, -26.4), (1858, -26.47), (1863, -26.39), (1868, -26.01), (1873, -26.03), (1877, -25.66)]
x = np.array([b[0] for b in B]); y = np.array([b[1] for b in B])
sl, ic = np.polyfit(x, y, 1)
r = np.corrcoef(x, y)[0, 1]
print('Bruckner 1844~1877 (%d점) 직선 기울기 %.1f cm/yr, r = %.2f' % (len(B), 100 * sl, r))
out['5-6-slope'] = dict(cm_per_yr=100 * sl, r=r, n=len(B))
# 915~921 (-17.4) 에서 1100~1150 (< -30.4) 로
t1 = 918; t2 = 1125
print('Bruckner: %d년경 -17.4 m 에서 %d년경 < -30.4 m 로: 하강 > %.1f m, %d년 -> 평균 > %.1f cm/yr' % (t1, t2, 30.4 - 17.4, t2 - t1, 100 * (30.4 - 17.4) / (t2 - t1)))
out['5-6-fall'] = dict(drop_min=13.0, years=t2 - t1, cm_per_yr_min=100 * 13.0 / (t2 - t1))
# Naderi Beni 가 같은 표에서 모순으로 짚은 것: 중세 온난기 저수위 초록 -28 m 대 표 7 의 -24 m
print('초록 MCA 저수위 -28 m 와 표 7 (977, 1208년) -24 m 의 차 = %d m' % 4)

# ------------------------------------------------------------------ 계산 5-7: Leroy 등(2022), Leroy 등(2014), Kakroodi 등(2015) 숫자의 정합성
print('\n== 계산 5-7: Leroy 등과 Kakroodi 등 숫자의 정합성 ==')
amp = 15.0; maxrate = 14.0
print('진폭 15 m 를 최대 속도 14 cm/yr 로 올라가려면 최소 %.0f년' % (amp * 100 / maxrate))
last = maxrate / 1.25
print('"지난 세기보다 25%% 빠르다"면 지난 세기의 최대 속도는 %.1f cm/yr' % last)
print('"진폭이 5배 이상 크다"면 지난 세기의 진폭은 최대 %.1f m (Kroonenberg 등의 3 m와 비교)' % (amp / 5))
print('Kroonenberg 등 서술 기기 관측 1837~2007: 1837~ 약 %d년' % (2007 - 1837))
out['5-7-leroy2022'] = dict(min_years=amp * 100 / maxrate, last_rate=last, last_amp_max=amp / 5)
hs = (10.55, 4.11)
print('Leroy 등(2014): 낮은 염분 = 고수위 %.2f ~ %.2f cal ka BP, 길이 %.2f ka (초록의 "약 6000년"과 비교)' % (hs[0], hs[1], hs[0] - hs[1]))
kk = [(8.4, '수위 하강(8400)'), (7.7, '후퇴(7700)')]
for t, nm in kk:
    inside = hs[1] <= t <= hs[0]
    print('Kakroodi 등(2015) %s cal BP: Leroy 등(2014)의 고수위 구간 안인가 = %s' % (nm, inside))
print('Leroy 등(2014) 8.19 ka 식생 전환, 8.83 ka(Anabaena·Botryococcus 풍부 끝): 8.83 - 8.19 = %.2f ka' % (8.83 - 8.19))
out['5-7-hs'] = dict(length=hs[0] - hs[1], kakroodi_inside=[hs[1] <= t <= hs[0] for t, _ in kk])
json.dump(out, open('ch05-calc-caspian.json', 'w'), ensure_ascii=False, indent=1, default=float)
