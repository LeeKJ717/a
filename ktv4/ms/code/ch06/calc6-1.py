# -*- coding: utf-8 -*-
"""계산 6-1: 여름 햇빛(일사) 문턱과 아프리카 습윤기 종료 연대.
입력은 deMenocal 등(2000)이 적은 숫자뿐이다: 20°N 6~8월 일사의 현재값 451 W/m2, 문턱 470 W/m2, 정점은 현재보다 약 8% 높고 10~11 cal ka BP에 도달.
세차 주기는 Haug 등(2001)이 적은 '약 21 ky'를 기본으로 하고 19~23 ky를 민감도로 본다(교과서 범위, 이 책의 가정).
이 계산은 일사 곡선 자체(궤도 해)를 쓰지 않는다. 정현파 하나로 줄인 시연값이다."""
import numpy as np
S0, THR = 451.0, 470.0
print('문턱의 현재 대비 비율 = (%.0f-%.0f)/%.0f = %.2f %%  (논문: 약 4.2 %%)' % (THR, S0, S0, 100*(THR-S0)/S0))
pk_pct = 8.0
thr_pct = 100*(THR-S0)/S0
print('정점 +%.1f %% 는 %.1f W/m2 에 해당 (451의 8%%)' % (pk_pct, S0*pk_pct/100))
print()
print('[A] 정점 T 에서 현재(0)까지 직선으로 줄어든다고 가정')
for T in (10.0, 10.5, 11.0):
    t = T*thr_pct/pk_pct
    print('  정점 %.1f ka -> 문턱 통과 %.2f ka' % (T, t))
print()
print('[B] 정현파 dS(t) = A[cos(2pi(t-T)/P) - cos(2pi T/P)], dS(T)=정점, dS(0)=0 (현재와 같게)')
res = {}
for P in (19.0, 21.0, 23.0):
    for T in (10.0, 10.5, 11.0):
        c0 = np.cos(2*np.pi*T/P)
        A = pk_pct/(1-c0)
        arg = thr_pct/A + c0
        if abs(arg) > 1:
            print('  P=%.0f T=%.1f: 문턱에 닿지 않음' % (P, T)); continue
        th = np.arccos(arg)
        t_cross = T - th*P/(2*np.pi)      # 정점보다 젊은 시각(t < T). cos 는 짝함수이므로 t = T - th*P/2pi
        slope = A*(2*np.pi/P)*np.sin(th)       # %/ka
        res[(P, T)] = (t_cross, A, slope)
        print('  P=%2.0f ka, T=%4.1f ka: A=%.2f %%, 문턱 통과 %.2f ka, 그 때 기울기 %.2f %%/ka = %.1f W/m2/ka' % (P, T, A, t_cross, slope, slope*S0/100))
print()
P, T = 21.0, 10.5
t_cross, A, slope = res[(P, T)]
dS400 = slope*0.4
print('[C] 기본값(P=21, T=10.5) 통과 시점의 400년 일사 변화 = %.2f %% = %.2f W/m2' % (dS400, dS400*S0/100))
print('    deMenocal 등(2000)의 퇴적물 육상기원 플럭스 변화 +47 %% (7.64 -> 11.22 g/cm2/ka, 계산 6-2). 비 = %.0f 배 (플럭스 %% / 일사 %%)' % (47.0/dS400))
print()
print('[D] 논문 종료 연대와의 비교')
term, tsd = 5490.0, 190.0
for name, val in (('직선 T=10.5', 10.5*thr_pct/pk_pct*1000), ('정현파 P=21,T=10.5', res[(21.0, 10.5)][0]*1000), ('정현파 P=23,T=10.5', res[(23.0, 10.5)][0]*1000), ('정현파 P=19,T=10.5', res[(19.0, 10.5)][0]*1000)):
    print('  %-20s %5.0f yr  | 5490 와의 차 %+5.0f yr = %+.2f sigma(190)' % (name, val, val-term, (val-term)/tsd))
print()
print('[E] Prell과 Kutzbach(1987) 인용: 일사 8%% 증가가 강수 40%% 증가 -> 이득 40/8 = %.1f 배 (논문: 다섯 배)' % (40/8))
