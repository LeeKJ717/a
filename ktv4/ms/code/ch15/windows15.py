# -*- coding: utf-8 -*-
"""15장 공용 입력: 4.2 ka 창(cal BP). 값은 8장 계산 8-4(ms/code/ch08/calc8-4.py)의 입력을 그대로 옮긴 것이다.
형식: 이름 -> (젊은 끝, 오래된 끝). 8장 8.1.1절 표와 같다. 읽은 수준은 8장 8.10절의 표를 따른다.
이 장은 새 논문을 읽지 않았다."""
W = {'Booth 등 북미 중부': (4100, 4300), 'deMenocal 등 ODP 658C 먼지 감소': (4100, 4300), 'Mayewski 등 급변 구간': (3800, 4200),
     'Bini 등 지중해': (3800, 4300), 'Railsback 등 종합': (3930, 4150), 'Weiss 개관': (3900, 4200), '제3권 6장 유라시아 열 기록 공통': (3970, 4025)}
GLOBAL5 = ['Booth 등 북미 중부', 'Mayewski 등 급변 구간', 'Bini 등 지중해', 'Railsback 등 종합', 'Weiss 개관']
ALL7 = list(W)
SHORT = {'Booth 등 북미 중부': 'Booth', 'deMenocal 등 ODP 658C 먼지 감소': 'deMenocal', 'Mayewski 등 급변 구간': 'Mayewski',
         'Bini 등 지중해': 'Bini', 'Railsback 등 종합': 'Railsback', 'Weiss 개관': 'Weiss', '제3권 6장 유라시아 열 기록 공통': '유라시아 공통'}
def inter(names, delta=0.0):
    lo = max(W[n][0] - delta for n in names); hi = min(W[n][1] + delta for n in names)
    return lo, hi, hi - lo
