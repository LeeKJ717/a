# -*- coding: utf-8 -*-
"""계산 9-5. (a) Damgaard 등(2018, Science)의 D 통계 Z 값을 p로 바꾸고, 검정이 여러 개일 때의 기준을 본다.
(b) Narasimhan 등(2019)이 적은 구성 비율의 곱셈 산술. 이 산술은 논문의 검정이 아니다."""
import json, os, math
from scipy.stats import norm
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
print('== 계산 9-5 (a) D 통계 Z -> 양쪽 p ==')
zs = [('D(Baikal_EN, Mbuti; Botai_CA, Okunevo_EMBA) = -0.025', -12.0), ('D(Baikal_EN, Mbuti; Botai_CA, Sholpan) = -0.028', -8.34),
      ('D(Baikal_EN, Mbuti; Botai_CA, Gregorievka) = -0.026', -7.1), ('D(EHG, Mbuti; Namazga_CA, Iran_N)', 4.49),
      ('D(CHG, Mbuti; Anatolia_EBA, Anatolia_N)', 3.95), ('D(EHG, Mbuti; Anatolia_EBA, Anatolia_MLBA)', -1.83),
      ('Namazga_CA 대 Turkmenistan_IA', -4.04), ('Namazga_CA 조상 대 CHG', 1.65)]
rows = []
for n, z in zs:
    p = 2 * norm.sf(abs(z))
    print('%-60s Z = %6.2f, 양쪽 p = %.3g, |Z|>3: %s' % (n, z, p, '예' if abs(z) > 3 else '아니오'))
    rows.append(dict(name=n, z=z, p=p))
res['a'] = rows
m = len(zs)
print('이 표의 검정 %d개에 |Z| > 3 기준(양쪽 p = %.5f)을 쓰면 우연히 하나라도 넘을 확률은 약 %.4f이다 (독립 가정, 1-(1-p)^%d).' % (m, 2 * norm.sf(3), 1 - (1 - 2 * norm.sf(3)) ** m, m))
print('Z = 1.65와 -1.83은 5퍼센트 수준(|Z| > 1.96)을 넘지 못한다. 위 확률은 서로 다른 가설의 검정을 한 줄에 놓은 시연이며 논문이 이 여덟 개를 한 묶음으로 보정했다는 뜻이 아니다.')

print('\n== 계산 9-5 (b) Narasimhan 등(2019)의 구성 비율 곱셈 ==')
ws_emba, ws_ef = 2 / 3, 1 / 3                   # Western_Steppe_MLBA = 약 2/3 Western_Steppe_EMBA + 약 1/3 유럽 농부 계열
cs = dict(WS_MLBA=1 - 0.09, CS_EMBA=0.09)       # Central_Steppe_MLBA = Western_Steppe_MLBA + 약 9% 추가 Central_Steppe_EMBA
comp = dict(WS_EMBA=cs['WS_MLBA'] * ws_emba, EF=cs['WS_MLBA'] * ws_ef, CS_EMBA=cs['CS_EMBA'])
print('Central_Steppe_MLBA 구성: 서쪽 초원 EMBA %.1f%%, 유럽 농부 계열 %.1f%%, 중앙 초원 EMBA(주로 WSHG 계열) %.1f%%, 합 %.1f%%' % (comp['WS_EMBA'] * 100, comp['EF'] * 100, comp['CS_EMBA'] * 100, sum(comp.values()) * 100))
sw = 0.41
print('Swat 계곡 초원 구배의 41%%가 Central_Steppe_MLBA이면, 그 안의 서쪽 초원 EMBA 몫은 %.1f%%, 유럽 농부 계열 %.1f%%, 중앙 초원 EMBA %.1f%%' % (sw * comp['WS_EMBA'] * 100, sw * comp['EF'] * 100, sw * comp['CS_EMBA'] * 100))
print('이 값은 논문의 "서쪽 초원 EMBA 계열이 최대 약 20%" 같은 다른 집단의 서술과 같은 대상이 아니어서 대조하지 않는다.')
gen = 26; print('Swat 초원 혼합이 개체들이 산 때보다 26세대 앞이라면, 세대 길이 25~30년에서 %d~%d년 앞이다 (논문은 혼합 시기의 95퍼센트 구간을 대략 1900~1500 BCE로 적음)' % (gen * 25, gen * 30))
res['b'] = dict(comp=comp, sw=sw)
json.dump(res, open(os.path.join(OUT, 'calc-9-5.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
