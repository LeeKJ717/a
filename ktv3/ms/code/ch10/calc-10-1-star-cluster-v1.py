# -*- coding: utf-8 -*-
"""계산 10-1. "칭기즈 칸의 Y 염색체"라는 주장의 숫자를 되풀이한다.
입력: Zerjal 등(2003) 초록과 본문 발췌, Balaresque 등(2015) 초록, Askapuli 등(2026) 프리프린트 본문의 연대와 개수.
논문 값과 이 책 계산값을 구분해 적는다. 서로 다른 논문의 하플로그룹 이름은 같은 계통이 아닐 수 있어 같다고 두지 않는다."""
import json, os, math
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
print('== 계산 10-1 (a) Zerjal 등(2003): 연대, 세대 수, 증가율 ==')
G = 30
for name, mean, lo, hi in [('BATWING', 1000, 700, 1300), ('r 기반', 860, 590, 1300)]:
    print('%-8s TMRCA %d년 (95%% %d~%d) -> 세대 길이 %d년이면 %.1f세대 (%.1f~%.1f)' % (name, mean, lo, hi, G, mean / G, lo / G, hi / G))
    res['gen_' + name] = (mean / G, lo / G, hi / G)
print('논문의 퍼짐: "약 34세대"는 1000 / 30 = %.1f 의 올림이다.' % (1000 / 30))
r = 1.36
print('세대당 1.36배로 34세대: 1.36^34 = %.0f 배' % (r ** 34))
print('한 남성에서 시작해 1600만 명이 되려면 세대당 %.3f 배 (34세대), 필요한 총 배율 %.2e' % ((16e6) ** (1 / 34), 16e6))
print('1.36^34 배로 1600만이 되려면 출발 남성 수는 %.0f 명 (1.6e7 / 1.36^34)' % (16e6 / r ** 34))
res['growth'] = dict(r34=r ** 34, per_gen_from_one=(16e6) ** (1 / 34), founders=16e6 / r ** 34)
print('논문의 1.36배가 어떤 출발점(한 남성인지, 여러 남성인지)을 쓴 값인지 이 책이 읽은 발췌에는 없다. 확인 필요.')
print('\n세계 남성 수 점검: 1600만 명이 전 세계 남성의 0.5%%이면 세계 남성은 %.2e 명이다.' % (16e6 / 0.005))
print('지역 남성의 8%%가 1600만 명이면 그 지역(16개 집단이 걸친 지역)의 남성은 %.2e 명이다.' % (16e6 / 0.08))
res['world_men'] = 16e6 / 0.005; res['region_men'] = 16e6 / 0.08
print('\n칭기즈 칸의 생년 1162(논문 표기)에서 논문 발표 2003년까지 %d년. 구간 700~1300년 안에 들어간다: %s' % (2003 - 1162, 700 <= 2003 - 1162 <= 1300))
res['span_to_2003'] = 2003 - 1162
print('\n== 계산 10-1 (b) 서로 다른 논문의 연대를 한 줄에 놓기 (같은 계통이라는 뜻이 아니다) ==')
rows = [('Zerjal 등(2003) 별무리, C*(xC3c)', 'BATWING 약 1000년 전(700~1300)', 2003 - 1000, 2003 - 1300, 2003 - 700),
        ('Balaresque 등(2015) 하강 군집 DC1(Genghis Khan 대응)', '평균 TMRCA 약 1090 CE', 1090, None, None),
        ('Askapuli 등(2026) C3*(C2-F3796) 합착', '약 2500년 전', 2026 - 2500, None, None)]
for n, d, mid, a, b in rows:
    print('%-52s %-32s -> %s' % (n, d, ('%d CE' % mid) if mid > 0 else ('%d BCE' % -(mid - 1))))
res['ages'] = rows
print('Askapuli의 값은 Zerjal의 95%% 구간 끝(1300년 전)보다 %d년 앞이다.' % (2500 - 1300))
print('Zerjal의 "별무리", Balaresque의 DC1, Askapuli의 C2-F3796은 이름과 정의가 다르다. 세 이름이 가리키는 계통의 포함 관계를 이 책은 확인하지 못했고, 같다고 두지 않는다. 위 세 연대를 한 계통의 나이로 읽으면 안 된다.')
print('\n== 계산 10-1 (c) Balaresque 등(2015) 산술 ==')
print('표본 합: 461 + 4860 = %d' % (461 + 4860), '(논문 5321)')
print('DC1 비율 2.7%%: 5321 x 0.027 = %.0f 명' % (5321 * 0.027))
print('하강 군집 남성 2000명 / 5321 = %.1f%% (논문 37.8%%)' % (2000 / 5321 * 100), '; 37.8%% x 5321 = %.0f' % (0.378 * 5321))
print('고유 하플로타입 67%% x 2552 = %.0f ; 20회 넘게 나온 15개 / 2552 = %.2f%%' % (0.67 * 2552, 15 / 2552 * 100))
res['balaresque'] = dict(total=461 + 4860, dc1=5321 * 0.027, dc_share=2000 / 5321, unique=0.67 * 2552, top15=15 / 2552)
json.dump(res, open(os.path.join(OUT, 'calc-10-1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
