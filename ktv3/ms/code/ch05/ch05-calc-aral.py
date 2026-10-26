# -*- coding: utf-8 -*-
"""5장 계산 5-1, 5-2: 아랄해. 논문이 적은 연대 구간과 수치만 입력으로 쓴다.
계산 5-1: 지난 2천 년 아랄해 수위 단계의 서로 다른 기록(Krivonogov 등 2010, 2014; Sorrel 등 2006, 2007)을 해마다 맞춰 본다.
계산 5-2: Letolle 등(2007)의 수치로 우즈보이 수로와 아무다리야 유량의 단위 환산·비율·문턱 높이를 계산한다.
실행: python3 ch05-calc-aral.py  (표준 라이브러리만 쓴다)"""
import json, math
out = {}

# ------------------------------------------------------------------ 계산 5-1
# 연대는 서기(AD, 기원전은 음수)로 통일한다. cal BP -> AD = 1950 - BP.
def bp(x): return 1950 - x
# 기록별 구간: (시작, 끝, 상태) 상태는 'L'(낮음) 'H'(높음). 논문 서술 그대로.
K10 = [(301, 1100, 'H'), (1101, 1500, 'L'), (1501, 2000, 'H')]          # 4~11세기 높음, 12~15세기 낮음, 16~20세기 높음
K14_sed = [(bp(2100), bp(1300), 'L'), (bp(1300) + 1, bp(1100) - 1, 'H'), (bp(1100), bp(350), 'L'), (bp(350) + 1, 2000, 'H')]  # 퇴적물·동물상: 2.1~1.3, 1.1~0.35 ka
K14_arch = [(bp(2100), bp(1450), 'L'), (bp(1450) + 1, 949, 'H'), (950, 1500, 'L'), (1501, 2000, 'H')]  # 고고·역사: 2.1~1.45, 1.0~0.45 ka (0.85이면 1100)
S06 = [(0, 425, 'L'), (920, 1230, 'L'), (1500, 1500, 'L'), (1600, 1650, 'L')]  # 와편모충 L. machaerophorum 우세 = 낮은 수위
S07_dry = [(0, 400), (900, 1150), (1500, 1650)]
S07_wet = [(400, 900), (1150, 1450)]

def state_series(spec, lo, hi, default=None):
    s = {}
    for y in range(lo, hi + 1):
        s[y] = default
    for a, b, st in spec:
        for y in range(max(a, lo), min(b, hi) + 1):
            s[y] = st
    return s

LO, HI = 0, 1650
sK10 = state_series(K10, LO, HI)
sK14s = state_series(K14_sed, LO, HI)
sK14a = state_series(K14_arch, LO, HI)
sS06 = state_series(S06, LO, HI, default='H')  # L 이 아닌 해는 '낮지 않음'으로 본다(논문은 높음을 I. caspienense 로 연결)
sS07 = {y: None for y in range(LO, HI + 1)}
for a, b in S07_dry:
    for y in range(a, b + 1): sS07[y] = 'L'     # 건조 = 낮음 (가설)
for a, b in S07_wet:
    for y in range(a, b + 1): sS07[y] = 'H'     # 습윤 = 높음 (가설). 400, 900, 1150 같은 경계 해는 뒤의 구간 값이 덮어쓴다
series = {'K10': sK10, 'K14sed': sK14s, 'K14arch': sK14a, 'S06': sS06, 'S07': sS07}
names = list(series)
res51 = {}
print('== 계산 5-1: 아랄해 수위 단계 해마다 맞추기 (AD %d~%d) ==' % (LO, HI))
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = series[names[i]], series[names[j]]
        both = [y for y in range(LO, HI + 1) if a[y] and b[y]]
        agree = sum(1 for y in both if a[y] == b[y])
        res51['%s-%s' % (names[i], names[j])] = dict(years=len(both), agree=agree, agree_frac=round(agree / len(both), 3) if both else None)
        print('%-8s vs %-8s : 비교 가능 %4d년, 일치 %4d년 (%.1f%%)' % (names[i], names[j], len(both), agree, 100 * agree / len(both) if both else float('nan')))
out['5-1'] = res51
# 2010 의 '초기 중세 높음(4~11세기)'이 2014 의 첫 후퇴(퇴적물·동물상 2.1~1.3 ka, 곧 AD -150~650)와 겹치는 해 수
def ov(a, b, c, d): return max(0, min(b, d) - max(a, c) + 1)
o1 = ov(301, 1100, bp(2100), bp(1300))
o2 = ov(301, 1100, bp(2100), bp(1450))
o3 = ov(1101, 1500, bp(1100), bp(350))
o4 = ov(1101, 1500, 950, 1500)
print('2010 높음(AD301~1100) 과 2014 첫 후퇴(퇴적물, AD%d~%d) 겹침: %d년; (고고, AD%d~%d): %d년' % (bp(2100), bp(1300), o1, bp(2100), bp(1450), o2))
print('2010 낮음(AD1101~1500) 과 2014 둘째 후퇴(퇴적물, AD%d~%d) 겹침: %d년 (낮음 구간 400년 중); (고고, AD950~1500): %d년' % (bp(1100), bp(350), o3, o4))
out['5-1-overlap'] = dict(high2010_vs_reg1_sed=o1, high2010_vs_reg1_arch=o2, low2010_vs_reg2_sed=o3, low2010_vs_reg2_arch=o4)
# 2014 첫 후퇴 시작 연대가 기원전/후로 어디인지
print('2.1 ka cal BP = AD %d (기원전 %d년), 1.3 ka = AD %d, 0.35 ka = AD %d' % (bp(2100), -bp(2100), bp(1300), bp(350)))

# ------------------------------------------------------------------ 계산 5-2
print('\n== 계산 5-2: 우즈보이와 아무다리야 (Letolle 등 2007) ==')
SEC = 365.25 * 24 * 3600
def km3_to_m3s(v): return v * 1e9 / SEC
def m3s_to_km3(v): return v * SEC / 1e9
conv = {
 '평균유량 56 km3/yr -> m3/s': km3_to_m3s(56),
 '30 km3/yr -> m3/s': km3_to_m3s(30),
 '20 km3/yr -> m3/s': km3_to_m3s(20),
 '60 m3/s (Kugunek 작은 하상) -> km3/yr': m3s_to_km3(60),
 '100 m3/s (Igdy) -> km3/yr': m3s_to_km3(100),
 '900 m3/s (홍수) 가 1년 이어지면 -> km3/yr': m3s_to_km3(900),
 '10 km3/yr (Igdy 협곡 최대) -> m3/s': km3_to_m3s(10),
}
for k, v in conv.items(): print('%-48s %10.2f' % (k, v))
out['5-2-conv'] = conv
frac = {}
for tot_name, tot in (('평균 56', 56.0), ('하한 60', 60.0), ('상한 70', 70.0)):
    for cap_name, cap in (('용량 20', 20.0), ('용량 30', 30.0)):
        frac['%s / %s' % (cap_name, tot_name)] = cap / tot
print('우즈보이 쪽으로 보낼 수 있는 몫(용량/총유량):')
for k, v in frac.items(): print('  %-18s %.3f' % (k, v))
out['5-2-frac'] = frac
# 높이 차
hi_old = (72, 73); hi_new = (54, 55)
d_old_new = (hi_old[0] - hi_new[1], hi_old[1] - hi_new[0])
print('이전 제안 정점 72~73 m 와 수정 정점 54~55 m 의 차: %d~%d m' % d_old_new)
sill = 70.0
print('아무 삼각주 문턱(최대 70 m) - 수정 정점(54~55 m) = %.0f~%.0f m' % (sill - hi_new[1], sill - hi_new[0]))
print('사리카미시 월류 시작 53~58 m, 수정 아랄 정점 54~55 m: 두 구간이 겹치는 폭 = %d m' % (min(58, 55) - max(53, 54)))
print('2006년 아랄 약 30 m 와 정점 52~54 m (Krivonogov 2014) 의 차: %d~%d m' % (52 - 30, 54 - 30))
out['5-2-levels'] = dict(old_minus_new=d_old_new, sill_minus_new=(sill - 55, sill - 54), overlap_spill=min(58, 55) - max(53, 54), drop_2006=(22, 24))
json.dump(out, open('ch05-calc-aral.json', 'w'), ensure_ascii=False, indent=1)
