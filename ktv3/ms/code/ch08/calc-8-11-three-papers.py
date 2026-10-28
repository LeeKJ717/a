# -*- coding: utf-8 -*-
"""계산 8-11. v3에서 더 읽은 세 편(Wilkin 등 2020, Zhang 등 2021, Bao 등 2018)의 숫자로 하는 산술.
입력은 모두 초록 또는 초록에 준하는 쪽의 값이다. 달력 환산은 서기 0년이 없는 달력에서 기원전 N년 = cal BP - 1949 (1950 기준)이다.
Bao 등의 기원전 연도가 보정 연대인지 확인하지 못했으므로 달력 연도로 읽은 값과 보정 연대로 읽은 값의 차이를 함께 보인다(차이는 수백 년이 될 수 있음)."""
import json, os
OUT = os.path.dirname(os.path.abspath(__file__))
res = {}
def bce(cal_bp): return cal_bp - 1949
def calbp_of_bce(y): return y + 1949
print('== 계산 8-11 (a) Wilkin 등(2020): 시료 구간 안에서 C4 증가의 위치 ==')
start_bce, end_ce, c4_bce = 4400, 1300, 800
span = start_bce + end_ce - 1
pos = start_bce - c4_bce
print('시료 연대 구간: 기원전 %d년~서기 %d년, 길이 %d년. C4 섭취 증가 시작 기원전 %d년은 구간 시작에서 %d년 뒤(구간의 %.1f%%)이다.' % (start_bce, end_ce, span, c4_bce, pos, 100 * pos / span))
print('기원전 %d년은 %d cal BP이다. 137명 시료로 구간 5699년을 나누면 평균 %.1f년에 1명이다(시료가 시기별로 균일하지 않음).' % (c4_bce, calbp_of_bce(c4_bce), span / 137))
res['wilkin'] = dict(span=span, pos=pos, frac=pos / span, calbp=calbp_of_bce(c4_bce), yr_per_ind=span / 137)
print('\n== (b) Zhang 등(2021) Zhukaigou: 건조 구간과 혼합 생업 연대 ==')
drought = (4000, 4200); mixed = (3700, 4000); win = (3900, 4200)
def ov(a, b): return max(0, min(a[1], b[1]) - max(a[0], b[0]))
print('건조 4200~4000 cal BP = 기원전 %d~%d년. 혼합 생업 4000~3700 cal BP = 기원전 %d~%d년.' % (bce(4200), bce(4000), bce(4000), bce(3700)))
print('두 구간은 4000 cal BP에서 맞닿는다(겹침 %d년). 건조 구간이 혼합 생업 연대의 앞이다.' % ov(drought, mixed))
print('8장이 쓴 사건 창 4200~3900(Zhang & Zhang 2023)과의 겹침: 건조 구간 %d년(건조 구간의 %.1f%%), 혼합 생업 %d년(혼합 구간의 %.1f%%).' % (ov(drought, win), 100 * ov(drought, win) / 200, ov(mixed, win), 100 * ov(mixed, win) / 300))
print('소의 뼈 한 점의 중앙값 3870 cal BP는 혼합 구간 3700~4000 안: %s. 사람 뼈 2점의 δ15N 8.2과 9.7의 차이 %.1f‰ (n=2여서 통계 검정을 하지 않는다).' % (3700 <= 3870 <= 4000, 9.7 - 8.2))
print('꽃가루 약 4445알, 식물규산체 약 9630개. 두 계수의 합 %d개.' % (4445 + 9630))
res['zhang'] = dict(drought_vs_mixed=ov(drought, mixed), drought_in_win=ov(drought, win), mixed_in_win=ov(mixed, win), d15n_diff=9.7 - 8.2)
print('\n== (c) Bao 등(2018): 기장 확장 시기와 사건 창 ==')
exp_bce = (2000, 3000)
cal_a = (calbp_of_bce(2000), calbp_of_bce(3000))
print('기장 농경이 크게 확장된 기원전 3000~2000년을 달력 연도로 읽으면 %d~%d cal BP 상당이다(길이 %d년).' % (cal_a[0], cal_a[1], cal_a[1] - cal_a[0]))
print('사건 창 4200~3900 cal BP(300년)는 이 구간 안에 완전히 들고 구간의 %.1f%%이다.' % (100 * 300 / (cal_a[1] - cal_a[0])))
print('만약 기원전 연도가 보정 연대가 아니라 보정 전 14C 나이를 달력으로 옮긴 것이라면 보정 뒤 구간은 수백 년 달라질 수 있어 이 포함 관계는 확인 필요이다.')
print('15개 유적 중 기장이 우세한 곳의 수는 초록에 없다. 초록은 우세하다고만 쓰므로 비율을 계산하지 않는다.')
res['bao'] = dict(span=cal_a[1] - cal_a[0], win_share=300 / (cal_a[1] - cal_a[0]))
print('\n== (d) 몽골 고원 기장 시기의 두 서술을 나란히 ==')
print('Ventresca Miller & Makarewicz(2019): 몽골 초원의 기장 섭취는 기원전 1천년기 말까지 늦다. Wilkin 등(2020): C4 섭취는 기원전 약 800년부터 증가. 기원전 800년과 기원전 1천년기 말(기원전 약 1년)은 %d년 떨어져 있다. 한쪽은 증가의 시작, 다른 쪽은 늦은 확산을 말하는 서술일 수 있어 이 책은 어긋남으로 단정하지 않는다.' % (800 - 1))
res['mongolia_gap'] = 799
json.dump(res, open(os.path.join(OUT, 'calc-8-11.json'), 'w'), ensure_ascii=False, indent=1)
