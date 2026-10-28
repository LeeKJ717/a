# -*- coding: utf-8 -*-
"""계산 10-8. 같은 별무리에 붙은 두 논문의 공통 조상 나이를 맞댄다.
입력: Zerjal 등(2003) BATWING 1000년(95% 700~1300), r 기반 860년(590~1300). Wei 등(2018) 초록의 TMRCA 약 2576년 전(95% 1975~3178).
Wei 등의 초록은 이 계통이 이전에 C3*-별무리로 불렸고 C2*-ST로 고쳐 불렀다고 적는다. 이 계산은 그 서술을 입력으로 받을 뿐 두 계통의 정의를 대조한 것이 아니다.
연대 눈금은 기준 연도(논문 발표 해)에서 뺀 근사이며 서기 0년이 없는 달력으로 바꾼다."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
def cal(base, age):
    y = base - age
    return '%d CE' % y if y > 0 else '%d BCE' % (1 - y)
Z = dict(mean=1000, lo=700, hi=1300, base=2003)
Zr = dict(mean=860, lo=590, hi=1300, base=2003)
W = dict(mean=2576, lo=1975, hi=3178, base=2018)
res = {}
print('== 계산 10-8 (a) 구간을 같은 "몇 년 전" 눈금에 놓기 ==')
for n, d in (('Zerjal BATWING', Z), ('Zerjal r 기반', Zr), ('Wei TMRCA', W)):
    print('%-15s %5d년 전 (95%% %d~%d), 구간 폭 %d년, 달력 %s (%s~%s)' % (n, d['mean'], d['lo'], d['hi'], d['hi'] - d['lo'], cal(d['base'], d['mean']), cal(d['base'], d['hi']), cal(d['base'], d['lo'])))
print('\n== (b) 겹침 ==')
for n, d in (('BATWING', Z), ('r 기반', Zr)):
    ov = min(d['hi'], W['hi']) - max(d['lo'], W['lo'])
    print('%s 구간과 Wei 구간의 겹침: %d년 (음수면 떨어진 간격 %d년)' % (n, ov, -ov if ov < 0 else 0))
    res['overlap_' + n] = ov
print('점추정 차이(Wei - BATWING) = %d년, 비 = %.2f배' % (W['mean'] - Z['mean'], W['mean'] / Z['mean']))
print('30년 세대로 환산한 차이 = %.1f세대' % ((W['mean'] - Z['mean']) / 30))
res['diff'] = W['mean'] - Z['mean']; res['ratio'] = W['mean'] / Z['mean']; res['gen_diff'] = (W['mean'] - Z['mean']) / 30
print('\n== (c) 칭기즈 칸 생년(논문 표기 1162)이 각 구간에 드는가 ==')
for n, d in (('Zerjal(기준 2003)', Z), ('Wei(기준 2018)', W)):
    age = d['base'] - 1162
    print('%s: 1162년은 %d년 전. 구간 %d~%d 안: %s' % (n, age, d['lo'], d['hi'], d['lo'] <= age <= d['hi']))
    res['in_' + n] = d['lo'] <= age <= d['hi']
print('Wei 구간의 가장 젊은 끝(%d년 전)은 서기 %s이고, 1162년(%d년 전)보다 %d년 앞선다.' % (W['lo'], cal(W['base'], W['lo']), 2018 - 1162, W['lo'] - (2018 - 1162)))
print('\n== (d) 읽는 법 ==')
print('공통 조상의 나이(TMRCA)는 확산의 시작 시점이 아니다. 오래된 계통에서 어느 하위 갈래가 훨씬 나중에 퍼질 수 있다.')
print('Wei 등의 초록이 확산을 몽골어 사용 집단 전체의 확산으로 읽은 것은 TMRCA만이 아니라 확산 양상에도 기댄 것이며, 그 양상의 숫자는 이 책이 읽지 못했다.')
json.dump(res, open(os.path.join(OUT, 'calc-10-8.json'), 'w'), ensure_ascii=False, indent=1)
