# -*- coding: utf-8 -*-
"""계산 1-1: 같은 사건(영거 드라이아스 끝, 홀로세 시작)을 여섯 종류의 기록이 적은 나이로 비교한다.
모든 값은 Walker 등(2009)의 표에서 옮긴 것(호수 바브, 호수 방사성탄소, 해양 방사성탄소, 화산재)과 Friedrich 등(2004)의 나이테 값이다.
BP(1950년 기준)를 b2k(2000년 기준)로 바꾸려면 50을 더한다(Walker 등 2009, 2018).
논문이 적은 오차의 정의(1시그마, 2시그마 등)는 이 장이 확인하지 못한 것이 많다. 아래에서는 적힌 숫자를 그대로 쓰고 정의를 단정하지 않는다.
"""
import numpy as np
ICE = 11703.0; ICE_MCE = 99.0   # GICC05 b2k, 최대 계수 오차(Walker 2009: 2시그마로 다룸)
rows = [
 # (이름, 종류, 기준, 값, 오차 하한쪽, 오차 상한쪽, 비고)
 ('NGRIP 얼음 GICC05 (중수소 과잉)', '빙핵', 'b2k', 11703, 99, 99, 'MCE, Walker 등 2009'),
 ('GISP2 얼음 경계', '빙핵', 'b2k', 11690, None, None, '계수 오차 1~2%, Walker 등 2009'),
 ('호이츠마르(Holzmaar) 호수 바브', '호수 퇴적물(연층)', 'BP', 11600, None, None, '바브 햇수 BP, 오차 없음'),
 ('메이어펠더 마르(Meerfelder Maar) 호수 바브', '호수 퇴적물(연층)', 'BP', 11590, None, None, '바브 햇수 BP, 오차 없음'),
 ('호엔하임 나이테(Hohenheim) 영거 드라이아스-프리보레알 경계', '나이테', 'BP', 11590, None, None, '나이테 너비로 정함, Friedrich 등 2004, 오차 없음'),
 ('스플랜 연못(Splan Pond) 방사성탄소', '호수 퇴적물(14C)', 'BP', (11385 + 11981) / 2, 298, 298, '2시그마 범위 11,385~11,981 cal BP의 한가운데와 반폭'),
 ('스이게쓰 호수(Suigetsu) 11,552 ± 88', '호수 퇴적물(연층+14C)', 'BP', 11552, 88, 88, 'cal BP, 오차 정의 확인 못 함'),
 ('카리아코 분지(Cariaco) 11,578 ± 32', '해양 퇴적물', 'BP', 11578, 32, 32, 'cal BP, 오차 정의 확인 못 함'),
 ('마라토토(Maratoto) 호수의 코니니 화산재', '호수 퇴적물(화산재)', 'BP', 11720, 220, 220, 'cal BP, 오차 정의 확인 못 함'),
]
print('=== 계산 1-1 (1) 같은 사건의 나이를 b2k 로 통일 ===')
print('%-52s %-20s %10s %10s %10s' % ('기록', '종류', '값(원래)', 'b2k', '얼음과의 차'))
vals = []
for n, k, b, v, lo, hi, note in rows:
    b2k = v + (50 if b == 'BP' else 0)
    vals.append(b2k)
    print('%-52s %-20s %7.0f %-3s %10.0f %10.0f   %s' % (n, k, v, b, b2k, b2k - ICE, ('± %d' % lo) if lo else ''))
vals = np.array(vals)
print()
print('=== 계산 1-1 (2) 퍼짐 ===')
oth = vals[1:]
print('GISP2 를 포함한 아홉 값(b2k): 최소 %.0f, 최대 %.0f, 폭 %.0f 년, 평균 %.1f, 표본 표준편차 %.1f' % (vals.min(), vals.max(), vals.max() - vals.min(), vals.mean(), vals.std(ddof=1)))
print('얼음 GICC05 를 뺀 여덟 값: 평균 %.1f, 표준편차 %.1f, 얼음 11,703 과의 차 %.1f' % (oth.mean(), oth.std(ddof=1), oth.mean() - ICE))
ice_sd = ICE_MCE / 2.0
print('GICC05 MCE %d 를 2시그마로 보면 1시그마 %.1f. 위 표준편차는 그 %.2f 배' % (ICE_MCE, ice_sd, oth.std(ddof=1) / ice_sd))
print()
print('=== 계산 1-1 (3) 오차가 있는 여섯 값만: 얼음 11,703 ± 99 와 겹치는가(오차를 단순히 더하는 거친 시험) ===')
for n, k, b, v, lo, hi, note in rows[1:]:
    if lo is None: continue
    b2k = v + (50 if b == 'BP' else 0)
    d = b2k - ICE
    tol = ICE_MCE + lo
    print('  %-44s 차 %+6.0f 년, 오차 합(선형) %5.0f -> %s' % (n[:44], d, tol, '겹침' if abs(d) <= tol else '벗어남'))
print()
print('(주의) 오차의 정의가 서로 달라 위의 겹침 시험은 거칠다. 오차 없이 적힌 값(바브, 나이테, GISP2)은 이 시험에서 뺐다.')
