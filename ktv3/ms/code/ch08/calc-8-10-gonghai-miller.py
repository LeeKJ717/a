# -*- coding: utf-8 -*-
"""계산 8-10. Chen 등(2015)의 복원 강수(Gonghai, 산시 북부 Ningwu)를 Miller 등(2016)의 5~10월 125 mm 문턱(계산 8-4)에 대 본다.
Chen 등(2015) 본문 추출문의 값: 현재 연강수량 445 mm, 6~9월 비율 77%, 14.7 ka 380 mm, 7.0 ka 570 mm, 몬순 최대기(7.8~5.3 ka) 평균 574 mm(현재보다 약 30% 높음),
 영거 드라이아스 약 100 mm 감소, 소빙기-중세온난기 약 100 mm(약 20%) 적음, 변환함수 RMSEP 86 mm.
6~9월은 5~10월의 부분 집합이므로 6~9월 비율 77%는 5~10월 비율의 하한이다(이 책의 읽기). 문턱 125 mm는 Miller 등(2016) 초록의 값이며, 그것이 Gonghai 같은 곳에 적용되는지는 논문이 말하지 않는다.
"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
out = {}
TH = 125.0; share = 0.77
P0, P147, P70, Pmax = 445.0, 380.0, 570.0, 574.0
print('(a) 논문 안의 산술 점검')
print('  14.7→7.0 ka: (570−380)/380 = %+.1f%%  [논문: "50%% 증가"]' % ((P70 - P147) / P147 * 100))
print('  몬순 최대기 574 대 현재 445: %+.1f%%  [논문: 약 30%%]; 7.0 ka 570 대 445: %+.1f%%' % ((Pmax - P0) / P0 * 100, (P70 - P0) / P0 * 100))
print('  100 mm 는 현재의 %.1f%%  [논문: 약 20%%]' % (100 / P0 * 100))
print('(b) 문턱')
for nm, P in [('현재', P0), ('14.7 ka', P147), ('7.0 ka', P70), ('몬순 최대기 평균', Pmax)]:
    jjas = P * share
    fmin = TH / P
    print('  %-10s 연 %.0f mm: 6~9월 %.0f mm(77%% 가정, 5~10월은 이보다 많거나 같음). 문턱 125 mm에 필요한 5~10월 비율 f ≥ %.3f. 6~9월만으로도 문턱의 %.2f배' % (nm, P, jjas, fmin, jjas / TH))
    out[nm] = dict(P=P, jjas=jjas, fmin=fmin, jjas_over_threshold=jjas / TH)
Pcrit = TH / share
print('  6~9월 비율을 77%%로 고정하면 6~9월 강수가 125 mm 아래가 되는 연강수량은 %.0f mm. 현재(445)에서 %.0f%% 줄어야 한다.' % (Pcrit, (1 - Pcrit / P0) * 100))
print('  복원 범위 380~574 mm 중 가장 낮은 값(380)에서도 문턱의 %.2f배(6~9월만으로). 변환함수 오차 86 mm를 빼도(380−86=%d) %.2f배' % (380 * share / TH, 380 - 86, (380 - 86) * share / TH))
out['Pcrit'] = Pcrit; out['crit_drop_pct'] = (1 - Pcrit / P0) * 100
print('(c) 이 점검이 말하는 것: Gonghai의 복원 범위는 문턱을 어느 쪽에서도 넘으므로, 이 문턱으로는 Gonghai 일대의 곡물 재배 가능성의 변화를 가리지 못한다. 문턱이 의미를 갖는 곳은 연강수량 약 200 mm 근처(계산 8-4)이다.')
json.dump(out, open(os.path.join(HERE, 'calc-8-10-gonghai-miller.json'), 'w'), ensure_ascii=False, indent=1)
