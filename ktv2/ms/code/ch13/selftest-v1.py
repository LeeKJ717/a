# -*- coding: utf-8 -*-
"""점검기의 단위 시험. 아래 입력은 이 책이 점검기의 동작을 보이려고 직접 만든 짧은 글이다(시연값).
맞는 글은 지적이 없어야 하고, 틀린 글은 해당 부호의 지적이 있어야 한다."""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hc', os.path.join(HERE, 'halluccheck-v1.py'))
hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)

def codes(fn, *a):
    st = {}
    return sorted({x['code'] for x in fn(*a, st)})

CASES = [
 ('A 맞는 합', hc.check_arith, [['21 + 5 = 26']], []),
 ('A 틀린 합', hc.check_arith, [['23명 = 21 + 5']], ['A1']),
 ('A 분수와 백분율 맞음', hc.check_arith, [['4/6 = 66.7%']], []),
 ('A 분수와 백분율 틀림', hc.check_arith, [['1/6 = 13.7%']], ['A1']),
 ('A 반올림 허용', hc.check_arith, [['4.01 + 6.29 + 89.71 = 100.01']], []),
 ('A 과학 표기 맞음', hc.check_arith, [['6.78 × 10⁻⁴ + 2.90 × 10⁻⁵ = 7.07 × 10⁻⁴']], []),
 ('A 과학 표기 10배 틀림', hc.check_arith, [['6.78 × 10⁻⁴ + 2.90 × 10⁻⁵ = 7.07 × 10⁻³']], ['A2']),
 ('A 과학 표기 가수 틀림', hc.check_arith, [['6.78 × 10⁻⁴ + 2.90 × 10⁻⁵ = 7.77 × 10⁻⁴']], ['A1']),
 ('A 음수 부호 보존', hc.check_arith, [['1950 − 7900 = −5950']], []),
 ('A 음수 부호 틀림', hc.check_arith, [['1950 − 7900 = 5950']], ['A1']),
 ('A 단위 환산은 경고', hc.check_arith, [['7.90 − 7.50 = 400년']], ['A2']),
 ('A 반올림 전파는 경고', hc.check_arith, [['1916 ÷ 1111 = 1.724']], ['A3']),
 ('A 함수 호출형은 건너뜀', hc.check_arith, [['P(0) = 0.6⁵ = 0.0778']], []),
 ('A 한글 뒤 괄호 식은 검사', hc.check_arith, [['남성 70명이 남았다(87 − 8 = 70).']], ['A1']),
 ('A ± 식은 건너뜀', hc.check_arith, [['7.66 ± 0.5 × 0.53 = 7.395']], []),
 ('A 닫히지 않은 괄호', hc.check_arith, [['논문 23 = 21 + 5(계산 11-1)']], ['A1']),
 ('A 연쇄식', hc.check_arith, [['1 − 0.427 × 1.0179 = 0.5654']], []),
 ('A 천 단위 쉼표', hc.check_arith, [['C(32, 20) = 225,792,840']], []),
 ('A 정수 반올림 백분율', hc.check_arith, [['16/18 = 89%']], []),
 ('A 변수 대입은 건너뜀', hc.check_arith, [['p = 0.00079, N = 58']], []),
 ('G 가능한 백분율', hc.check_grim, [['O3(53%, n = 304)']], []),
 ('G 불가능한 백분율', hc.check_grim, [['O-M175(58.8%, n = 176)']], ['G1']),
 ('G 유의 수준은 건너뜀', hc.check_grim, [['임계 상관(양쪽 5%, 1%): n = 57이면 0.261']], []),
 ('G 정수 백분율 가능', hc.check_grim, [['N1c가 94%(n = 184)']], []),
 ('R p 값 범위', hc.check_ranges, [['p = 1.2']], ['R1']),
 ('R p 값 정상', hc.check_ranges, [['p = 0.00079']], []),
 ('R 백분율 범위', hc.check_ranges, [['대산전 111%']], ['R1']),
 ('R BP 순서 맞음', hc.check_ranges, [['6500~5000 BP']], []),
 ('R BP 순서 틀림', hc.check_ranges, [['3600~4200 BP']], ['R2']),
 ('R 상관 범위', hc.check_ranges, [['r = 1.31']], ['R1']),
 ('T 행 합 맞음', hc.check_tables, [['| a | 시료 | x | y |', '|---|---|---|---|', '| u | 6 | 4 | 2 |', '| v | 5 | 3 | 2 |', '| w | 9 | 5 | 4 |']], []),
 ('T 행 합 틀림', hc.check_tables, [['| a | 시료 | x | y |', '|---|---|---|---|', '| u | 6 | 4 | 2 |', '| v | 5 | 3 | 2 |', '| w | 9 | 5 | 5 |']], ['T1']),
 ('T 열 합 틀림', hc.check_tables, [['| a | x | y |', '|---|---|---|', '| u | 4 | 2 |', '| v | 3 | 2 |', '| 합 | 7 | 5 |']], ['T2']),
]
bad = 0
for name, fn, args, want in CASES:
    got = codes(fn, *args)
    ok = got == want
    bad += (not ok)
    print('%-4s %-24s 기대 %-10s 결과 %s' % ('통과' if ok else '실패', name, want, got))

# 원문과 견주는 시험
SRC = ['논문은 여섯 유적에서 138명의 치아와 뼈를 얻었다. 형태로 남성이라 본 것이 78명이었다.', '음성 대조에 오염이 없었다. 증폭 조각은 100~200 bp 로 했다.']
tests = [
 ('N 원문에 있는 숫자', ['138명이다'], None),
 ('N 자리 바꿈', ['남성은 87명이다'], 'N1'),
 ('N 10배', ['조각은 1000 이다'], 'N1'),
 ('U 단위 바뀜', ['증폭 조각은 100~200 kb 이다'], 'U1'),
 ('Q 글자 그대로 인용', ['“음성 대조에 오염이 없었다”'], None),
 ('Q 근사 인용', ['“음성 대조에서 오염이 없었다고 한다”'], 'Q2'),
 ('Q 없는 인용', ['“고대 시료는 모두 현대인의 것이었다”'], 'Q1'),
]
for name, m, want in tests:
    st = {}
    f = hc.check_numbers(m, SRC, st) + hc.check_quotes(m, SRC, st)
    got = sorted({x['code'] for x in f})
    ok = (got == []) if want is None else (want in got)
    bad += (not ok)
    print('%-4s %-24s 기대 %-10s 결과 %s' % ('통과' if ok else '실패', name, want, got))
print('실패 %d건' % bad)
sys.exit(1 if bad else 0)
