# -*- coding: utf-8 -*-
"""계산 5-3: 쓰시마 해협 안부 위의 물 깊이와 쓰시마난류 기록의 나이(시연). 제1권의 숫자만 사용.
제1권 1장: 안부 수심 130 m(Saito 1998; 해협 정의에 따라 달라질 수 있음). 해수면 -120(Saito) 또는 -80 m(Ohshima).
제1권이 옮긴 Gallagher 등(2015): 동해 코어에서 쓰시마난류 유입 이전의 한랭 연체동물 군집이 9,300 cal BP까지, Globigerinoides ruber 는 9,300 cal BP 이후 계속,
쓰시마 매몰 하곡의 Anodontia stearnsiana 8,610+-100 yr BP(이 해역에서 가장 오래된 기록), 현재와 같은 표층 조건은 7,300 cal BP 까지 성립.
해수면 값: 제1권 Saito: 10 ka(척도 불명) -40 m; Clark 모형(역년): 9 ka -31.7, 7 ka -12.2, 5 ka -2.4 m; Jo 동해안(14C): 10,000 BP -25 m, 7,000 BP -10 m.
이것은 시연이다: 한반도와 쓰시마의 지역 해수면과 안부 깊이의 불확실성(수 m 이상)을 넣지 않았다.
"""
import c14cal as C
SILL = 130.0
print('=== (1) 안부 위의 물 깊이 = 130 + 해수면(m) ===')
for h in (-120, -100, -80, -40, -31.7, -25, -12.2, -10, -2.4, 0):
    print('  해수면 %6.1f m -> 안부 위 %6.1f m' % (h, SILL + h))
print()
print('=== (2) 제1권 곡선 값의 시기에서 ===')
rows = [('Saito 10 ka(척도 불명)', 10.0, -40), ('Clark 모형 9 ka(역년)', 9.0, -31.7), ('Clark 모형 7 ka', 7.0, -12.2), ('Clark 모형 5 ka', 5.0, -2.4)]
for lab, t, h in rows:
    print('  %-26s 해수면 %6.1f m, 안부 위 %6.1f m' % (lab, h, SILL + h))
for lab, a, h in (('Jo 10,000 BP(14C)', 10000, -25), ('Jo 7,000 BP(14C)', 7000, -10)):
    r = C.summary(a, 100)
    print('  %-26s 보정 중앙 %5.0f cal BP, 해수면 %6.1f m, 안부 위 %6.1f m' % (lab, r['median'], h, SILL + h))
print()
print('=== (3) 평균 속도로 -120 m 에서 올라오는 데 걸리는 시간(시연) ===')
for rate in (12.0, 40.0):
    for tgt in (-100, -80, -40):
        yrs = (tgt - (-120)) / rate * 1000
        print('  평균 %5.2f mm/yr 로 -120 -> %4d m: %5.0f 년' % (rate, tgt, yrs))
print()
print('=== (4) 난류 기록의 나이와 안부 ===')
for lab, a, e in (('Anodontia stearnsiana 8,610+-100 BP', 8610, 100),):
    r = C.summary(a, e)
    print('  %-38s 중앙 %5.0f cal BP, 95%% HPD %s' % (lab, r['median'], ', '.join('%d~%d' % (s, t) for s, t, m in r['hpd'][:1])))
print('  동해 코어 9,300 cal BP(난류 유입 이전 한랭 군집의 끝), 7,300 cal BP(현재와 같은 표층 조건)')
print('  Clark 모형으로 9 ka 에 안부 위 %.1f m 이고 7 ka 에 %.1f m 이다.' % (SILL - 31.7, SILL - 12.2))
print('  이 산술이 보이는 것은 9~9.3 ka 에 안부 위 물이 이미 약 90~100 m(Saito 40 m 로는 90 m, Clark 모형 9 ka 로는 98 m)였다는 것뿐이다. 난류가 시작한 원인(해협 밖의 조건)은 가르지 못하며 제1권도 그 추정을 하지 않았다.')
print('  Saito(-120 m, 안부 위 10 m)와 Ohshima(-80 m, 50 m)의 5배 차이(제1권)는 이 산술에서도 그대로다.')
