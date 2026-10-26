# -*- coding: utf-8 -*-
"""계산 9-1. 논문이 적은 시료 수와 비율의 산술 점검(되풀이 가능한 것만).
입력은 이 장이 읽은 논문 본문·초록의 숫자이다. 읽은 수준이 요약 발췌인 항목은 장의 읽은 수준 표를 본다."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stathelp import wilson
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
def say(*a):
    print(*a)

say('== 계산 9-1 시료 수와 비율의 산술 점검 ==')
checks = []
def chk(name, lhs_expr, lhs, rhs, note='', partial=False):
    # partial=True: 논문이 일부만 열거한 경우. 열거한 합이 전체를 넘지 않으면 모순이 아니다.
    ok = (lhs <= rhs) if partial else (lhs == rhs)
    checks.append(dict(name=name, expr=lhs_expr, value=lhs, paper=rhs, ok=ok, partial=partial, note=note))
    lab = ('열거 합 <= 전체: 모순 없음' if ok else '열거 합이 전체 초과') if partial else ('일치' if ok else '불일치')
    say('%-58s %-28s = %-6s 논문 %-6s %s %s' % (name, lhs_expr, lhs, rhs, lab, note))

# Jeong 등(2020) Cell
chk('Jeong2020 흉노 시기 개체', '13 + 47', 13 + 47, 60)
chk('Jeong2020 후기 흉노 47의 분류', '26 + 11 + 8 + 2', 26 + 11 + 8 + 2, 47)
chk('Jeong2020 초기 흉노 두 무리', '6 + 6', 6 + 6, 13, '시기 100 BCE 이전 13명과 1명 차이. 원문 확인 필요')
chk('Jeong2020 early Xiongnu rest 구간 끝(39+61)', '39 + 61', 39 + 61, 100)
chk('Jeong2020 early Xiongnu rest 구간 끝(75+25)', '75 + 25', 75 + 25, 100)
chk('Jeong2020 Fofonovo ANE 상한과 ANA 하한', '17 + 83', 17 + 83, 100)
chk('Jeong2020 Fofonovo ANE 하한과 ANA 상한', '12 + 87', 12 + 87, 100, '1%p 어긋남. 개체마다 값이 다르거나 반올림일 수 있다')
lo = 15 + 55 + 21; hi = 18 + 64 + 27
say('Jeong2020 몽골 시대 3원천 구간 합의 범위: %d ~ %d (100 포함 여부: %s)' % (lo, hi, lo <= 100 <= hi))
res['jeong2020_threeway_sum_range'] = [lo, hi]
for k, n, lab in [(56, 61, '3원천 모형이 맞는 몽골 시대 개체'), (34, 61, '현생 몽골계 한 집단 이상과 같은 가지'), (26, 47, '후기 흉노 중 초기형 모형이 맞는 개체')]:
    w = wilson(k, n)
    say('Jeong2020 %s: %d/%d = %.3f, Wilson 95%% 구간 %.3f ~ %.3f' % (lab, k, n, k / n, w[0], w[1]))
    res['wilson_%d_%d' % (k, n)] = dict(k=k, n=n, p=k / n, lo=w[0], hi=w[1], label=lab)

# Damgaard 등(2018) Nature
chk('Damgaard2018N 중앙 사카', '56 + 44', 56 + 44, 100)
chk('Damgaard2018N 시베리아 타가르', '83.5 + 7.5 + 9', 83.5 + 7.5 + 9, 100.0)
chk('Damgaard2018N 톈산 사카', '70 + 25 + 5', 70 + 25 + 5, 100)

# Damgaard 등(2018) Science
sci = dict(Botai=3, Yamnaya_Karagash=1, Sidelkino=1, Central_Steppe_EMBA=2, Okunevo=19, Baikal=31, Namazga=4, Turkmenistan_IA=1, Anatolia=12)
chk('Damgaard2018S 표시된 무리의 합', ' + '.join(str(v) for v in sci.values()), sum(sci.values()), 74)

# Narasimhan 등(2019)
chk('Narasimhan2019 지역별 합', '182 + 209 + 132', 182 + 209 + 132, 523)

# Jeong 등(2018) PNAS
chk('Jeong2018 비이상치 16명 = 주 무리 14 + 제외 2(ARS009, ARS015)', '14 + 2', 14 + 2, 16)
chk('Jeong2018 분석에 쓴 개체(비이상치 16 + 이상치 2)', '16 + 2', 16 + 2, 18)
chk('Jeong2018 성별 합', '12 + 8', 12 + 8, 18, '분석 개체 18명과 2명 차이. 성별을 센 모집단(DNA 보존 좋은 20명)이 다를 수 있다')

# Maróti 등(2022)
chk('Maróti2022 아바르 선형 구배 76의 분류', '26 + 9 + 40', 26 + 9 + 40, 76, '프리프린트 본문 기준. 출판본 확인 필요')
chk('Maróti2022 Avar_Asia_Core 12의 분할', '3 + 9', 3 + 9, 12)
chk('Maróti2022 Conq_Asia_Core 12의 분할', '4 + 8', 4 + 8, 12)
chk('Maróti2022 Conq_Asia_Core 성별', '6 + 6', 6 + 6, 12)
chk('Maróti2022 ARK 남성의 Y', '8 + 2', 8 + 2, 10)
chk('Maróti2022 Hun 선형 구배 6명 가운데 Y 보고', '4 + 1', 4 + 1, 6, '6명 중 Y가 보고된 것은 5명. 나머지 1명은 발췌에 없음', partial=True)
chk('Maróti2022 후흉노 시기 공개 Y 23명 가운데', '10 + 9', 10 + 9, 23, '나머지 4명의 하플로그룹은 발췌에 없음', partial=True)

chk('Maróti2022 출판본 초록의 세 집단 합 대 프리프린트 본문의 새 개체 수', '9 + 143 + 113', 9 + 143 + 113, 271, '프리프린트 본문은 새로 분석한 개체를 271명으로 적고 출판본 초록의 세 집단 합은 265명이다. 판이 다르거나 다른 시료가 들어 있을 수 있다. 확인 필요')

# Zhang 등(2021)
chk('Zhang2021 개체 수', '5 + 13', 5 + 13, 18, '초록의 두 지역 합. 논문 전체 시료 수와 같은지는 확인 필요')

bad = [c for c in checks if not c['ok']]
say('\n검사 %d개(완전 분할 %d개, 부분 열거 %d개), 모순 없음 %d개, 어긋남 %d개' % (len(checks), sum(1 for c in checks if not c['partial']), sum(1 for c in checks if c['partial']), len(checks) - len(bad), len(bad)))
for c in bad:
    say('  불일치:', c['name'], c['expr'], '=', c['value'], '논문', c['paper'])
res['checks'] = checks
json.dump(res, open(os.path.join(OUT, 'calc-9-1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
