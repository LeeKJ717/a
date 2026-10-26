# -*- coding: utf-8 -*-
"""계산 8-4. Miller 등(2016)이 쓴 문턱 '5~10월 강수 약 125 mm 이상'을 연강수량 P에서 넘으려면 5~10월에 내려야 하는 비율 f = 125 / P.
P는 논문이 적은 값: 200 mm(Semirech'ye 저지; Spengler 등 2014b), 500 mm(초원 평균의 상한; 같음), 550 mm(Zhuanglang 연평균, 7~9월에 최대; Li 등 2022), 1000 mm(산기슭이 흔히 넘는다는 서술; Spengler 등 2014b).
f의 의미는 이 책의 산술이다. 어떤 관측소의 5~10월 비율도 이 책은 읽지 못했다. 가정한 f(0.5, 0.7, 0.9)는 시연값이다.
"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
TH = 125.0; Ps = [200, 500, 550, 1000]
out = {}
print('문턱 %.0f mm, 5~10월 6개월 평균 월강수 %.1f mm' % (TH, TH / 6))
for P in Ps:
    fmin = TH / P
    row = dict(P=P, fmin=fmin, apr_sep_if=dict((str(f), f * P) for f in (0.5, 0.7, 0.9)), pass_if=dict((str(f), f * P >= TH) for f in (0.5, 0.7, 0.9)))
    out[str(P)] = row
    print('P=%4d mm: 필요한 5~10월 비율 f >= %.3f | f=0.5 -> %.0f mm(%s), f=0.7 -> %.0f mm(%s), f=0.9 -> %.0f mm(%s)' % (
        P, fmin, 0.5 * P, '통과' if 0.5 * P >= TH else '미달', 0.7 * P, '통과' if 0.7 * P >= TH else '미달', 0.9 * P, '통과' if 0.9 * P >= TH else '미달'))
# f 가 1을 넘지 않는 최소 연강수량
print('f=1(연강수 전부가 5~10월)이어도 문턱이 되는 연강수량 = %.0f mm' % TH)
json.dump(out, open(os.path.join(HERE, 'calc-8-4-rain.json'), 'w'), ensure_ascii=False, indent=1)
