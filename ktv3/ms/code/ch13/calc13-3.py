# -*- coding: utf-8 -*-
"""계산 13-3: 396년 어긋남의 대안 설명을 하나씩 수치로 시험한다.
(가) 젊은 탄소 혼입: 측정 14C 연대 9130 BP 가 경계 연대 10,700 cal BP 의 참 14C 연대보다 젊게 나오려면 현대 탄소가 몇 % 섞여야 하는가.
(나) 오래된 탄소(저장 효과): 저장 효과를 빼면 보정 연대가 어떻게 달라지는가. 값은 1장이 다른 호수에서 옮긴 숫자이며 호톤 호의 값이 아니다(시연).
(다) 경계가 다른 값이었다면 구역 퇴적 속도의 모양이 어떻게 달라지는가.
곡선: data/intcal20.14c (c14cal.py).
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c14cal as C

TAU = 8033.0   # 리비 평균 수명(년). 14C 연대 = -8033 ln(F)
print('=== 계산 13-3 (가) 젊은 탄소(현대 탄소) 혼입 ===')
a_obs = 9130.0; F_obs = np.exp(-a_obs / TAU)
rows = []
for target in (10304, 10500, 10700, 10900):
    mu = float(np.interp(float(target), C.CAL, C.C14)); F_true = np.exp(-mu / TAU)
    f = (F_obs - F_true) / (1.0 - F_true)
    rows.append(dict(target=target, mu=mu, f=float(f)))
    print('참 연대 %d cal BP → 곡선의 14C 연대 %.0f BP, F = %.4f. 측정 F = %.4f. 현대 탄소(F=1) 혼입 비율 f = %.2f %%' % (target, mu, F_true, F_obs, f * 100))
# 측정 오차 ±40 을 넣어 f 가 얼마나 흔들리는가: 측정이 1시그마 오래/젊게 나왔다면
for da in (-40, 40):
    F2 = np.exp(-(a_obs + da) / TAU); mu = float(np.interp(10700.0, C.CAL, C.C14)); Ft = np.exp(-mu / TAU)
    print('측정 연대가 %+d 년이면 f = %.2f %%' % (da, (F2 - Ft) / (1 - Ft) * 100))
print('해석: 이 계산은 어떤 비율이 "필요한지"만 말한다. 호톤 호 시료의 물질(벌크 퇴적물, 식물 조각 등)과 전처리는 이 책이 읽지 못했다.')

print('\n=== 계산 13-3 (나) 오래된 탄소(저장 효과)를 뺀 보정(시연값) ===')
res = []
for R, who in ((0, '없음'), (400, '시연값 400'), (685, '호륜호의 값(1장)'), (1060, '군 호의 값(1장)'), (1920, '텅거 호의 값(1장)')):
    s = C.summary(9130 - R, 40)
    top = max(h[0] for h in s['hpd'])
    res.append(dict(R=R, who=who, mean=s['mean'], top=int(top), gap=10700 - s['mean']))
    print('저장 효과 %4d 년(%s): 14C %d BP → 보정 평균 %.0f cal BP, 95.4%% 구간의 오래된 끝 %d, 경계 10,700 과의 차 %.0f 년' % (R, who, 9130 - R, s['mean'], top, 10700 - s['mean']))
print('→ 오래된 탄소가 섞였다면 참 연대는 더 젊어져서 어긋남이 커진다. 이 방향으로는 396년을 설명할 수 없다.')

print('\n=== 계산 13-3 (다) 경계 연대에 따른 구역 퇴적 속도(깊이는 논문 표) ===')
dz = {'H4': 30.0, 'H3': 77.5, 'H2': 57.5, 'H1': 40.0}
def rates(b):
    ages = {'H4': (11.5, b), 'H3': (b, 7.9), 'H2': (7.9, 4.9), 'H1': (4.9, 0.0)}
    return {k: dz[k] / ((a0 - a1) * 1000.0) for k, (a0, a1) in ages.items()}, {k: (a0 - a1) * 1000.0 for k, (a0, a1) in ages.items()}
out = {}
for b in (10.7, 10.304, 10.0):
    r, L = rates(b)
    mono = all(r[x] > r[y] for x, y in (('H4', 'H3'), ('H3', 'H2'), ('H2', 'H1')))
    out[str(b)] = r
    print('H4/H3 경계 %.3f ka: ' % b + ', '.join('%s %.4f cm/년(%d년)' % (k, r[k], round(L[k])) for k in ('H4', 'H3', 'H2', 'H1')) + '  → 위로 갈수록 느려지는 순서 %s' % ('유지' if mono else '깨짐'))

print('\n=== 계산 13-3 (라) 시연값: 참 F = 0.30 인 시료에 현대 탄소가 섞이면 14C 연대가 얼마나 젊어지는가 ===')
Ft = 0.30
for f in (0.0, 0.005, 0.01, 0.02, 0.05):
    F = (1 - f) * Ft + f
    print('혼입 %4.1f %%: F = %.4f → 14C 연대 %.0f BP (참값 %.0f BP, 젊어진 폭 %.0f 년)' % (f * 100, F, -TAU * np.log(F), -TAU * np.log(Ft), -TAU * np.log(Ft) + TAU * np.log(F)))
json.dump(dict(contam=rows, reservoir=res, rates=out), open(os.path.join(HERE, 'calc13-3-out.json'), 'w'), ensure_ascii=False)
