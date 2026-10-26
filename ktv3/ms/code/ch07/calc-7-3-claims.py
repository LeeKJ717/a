# -*- coding: utf-8 -*-
"""계산 7-3. 중국 쪽 '가장 이른 밀' 서술들을 달력 연대로 모아 겹침과 순서를 센다.
입력은 모두 논문 본문 또는 초록의 서술이다(출처는 7장 표). 구간이 있는 서술은 구간 안에서 균등분포로 보아 'A가 B보다 오래됨' 확률을 구한다(시연: 균등은 가정이다).
점 서술(5200 cal BP 등)은 점으로 둔다. 시작=오래된 쪽(기원전 양수), 끝=젊은 쪽."""
import numpy as np, json, os
rng = np.random.default_rng(7)
# 이름: (오래된 쪽 BC, 젊은 쪽 BC, 출처)
CL = {
 'Zhou2020 알타이 통톈동굴(밀·보리, 점)':      (3251, 3251, '5200 cal BP = 5200-1949 BC'),
 'Li2007 시산핑 밀(점)':                        (2701, 2701, '4650 cal yr BP'),
 'Tasbas I 밀(Stevens2016 재인용)':             (2840, 2490, 'Stevens 2016'),
 'Long2018 하류 황허 밀 시작 경계(95%)':        (3600, 2200, '중앙값 기원전 2600'),
 'Zhaojiazhuang 밀(Liu2017 재인용)':            (2562, 2209, 'Liu 2017'),
 'Baligang 밀 직접 연대(Deng2019)':             (2137, 1966, 'UGAMS#27671 3670±25'),
 'Stevens2016 중국 밀 보수적 추정':             (2200, 1800, 'Stevens 2016'),
 'Dodson2013 허시 회랑 밀':                     (2100, 1800, 'Dodson 등 2013'),
 'Long2018 상류 황허 밀 시작 경계(95%)':        (2000, 1700, '중앙값 기원전 1900'),
 'Long2018 신강 밀 시작 경계(95%)':             (2100, 1700, '중앙값 기원전 1900'),
 'Long2018 중류 황허 밀 시작 경계(95%)':        (1800, 1500, '중앙값 기원전 1600'),
 'Long2018 티베트 밀 시작 경계(95%)':           (2000, 1400, '중앙값 기원전 1600'),
}
names = list(CL)
def samp(k, n=200000):
    a, b, _ = CL[k]; return rng.uniform(-a, -b, n) if a != b else np.full(n, -float(a))   # 부호 있는 연도(음수가 오래됨)
S = {k: samp(k) for k in names}
print('서술 / 오래된 쪽 BC / 젊은 쪽 BC / 폭(년) / 중점')
for k in names:
    a, b, src = CL[k]; print('%-44s %5d %5d %5d %7.0f   (%s)' % (k, a, b, a - b, (a + b) / 2, src))
oldest = max(CL[k][0] for k in names); youngest_start = min(CL[k][0] for k in names)
print('\n가장 오래된 시작: %d BC (%s), 가장 젊은 시작: %d BC (%s). 서술 시작 연대의 퍼짐 = %d년' % (
    oldest, [k for k in names if CL[k][0] == oldest][0], youngest_start, [k for k in names if CL[k][0] == youngest_start][0], oldest - youngest_start))
# 점 서술 2개를 뺀 구간 서술만의 퍼짐
iv = [k for k in names if CL[k][0] != CL[k][1]]
print('구간 서술 %d개의 시작 연대 퍼짐 = %d년(기원전 %d ~ %d)' % (len(iv), max(CL[k][0] for k in iv) - min(CL[k][0] for k in iv), max(CL[k][0] for k in iv), min(CL[k][0] for k in iv)))
# 보수적 추정 띠(기원전 2200~1800)와의 겹침
print('\n보수적 띠(기원전 2200~1800)와 겹치는 정도(서술 구간 중 띠 안에 든 비율)')
for k in names:
    a, b, _ = CL[k]
    if a == b: ov = 1.0 if 1800 <= a <= 2200 else 0.0
    else: ov = max(0, min(a, 2200) - max(b, 1800)) / (a - b)
    print('  %-44s %.2f' % (k, ov))
# 쌍 순서 확률: 대표 쌍
pairs = [('Zhou2020 알타이 통톈동굴(밀·보리, 점)', 'Tasbas I 밀(Stevens2016 재인용)'),
         ('Tasbas I 밀(Stevens2016 재인용)', 'Zhaojiazhuang 밀(Liu2017 재인용)'),
         ('Zhaojiazhuang 밀(Liu2017 재인용)', 'Dodson2013 허시 회랑 밀'),
         ('Zhaojiazhuang 밀(Liu2017 재인용)', 'Baligang 밀 직접 연대(Deng2019)'),
         ('Dodson2013 허시 회랑 밀', 'Baligang 밀 직접 연대(Deng2019)'),
         ('Long2018 하류 황허 밀 시작 경계(95%)', 'Long2018 상류 황허 밀 시작 경계(95%)'),
         ('Long2018 상류 황허 밀 시작 경계(95%)', 'Long2018 중류 황허 밀 시작 경계(95%)'),
         ('Li2007 시산핑 밀(점)', 'Zhaojiazhuang 밀(Liu2017 재인용)')]
print('\nP(앞의 서술이 뒤의 서술보다 오래됨) [균등 가정, 20만 번]')
out = {}
for a, b in pairs:
    pr = float((S[a] < S[b]).mean()); out[a + ' | ' + b] = pr; print('  %-44s > %-44s %.3f' % (a, b, pr))
json.dump(dict(claims={k: CL[k] for k in names}, pairs=out), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-3-claims.json'), 'w'), ensure_ascii=False, indent=1)
