# -*- coding: utf-8 -*-
"""실습 8-2: He 등(2015) 표 2(제1권 10장 계산 10-8의 입력)에서 CIA를 sedkit으로 다시 계산해 제1권과 맞춘다.
이어서 (가) 시연값으로 CIA 한 줄을 단계별로, (나) 규칙 A~D 비교, (다) CIW와 PIA, A-CN-K 좌표, (라) 입도 대용과의 상관."""
import csv, os, sys, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import stats
import sedkit as K
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'data', 'he2015-table2.csv'), encoding='utf-8')))
N = len(rows)
print('== (가) 시연값: 몰 값이 Al2O3 0.10, CaO* 0.02, Na2O 0.02, K2O 0.02이면')
print('   CIA = 100 x 0.10 / (0.10 + 0.02 + 0.02 + 0.02) = %.4f' % (100 * 0.10 / 0.16))
r0 = rows[0]
Al, Ca, Na, Kk, P = (float(r0[k]) for k in ('Al2O3', 'CaO', 'Na2O', 'K2O', 'P2O5'))
a, c, n, k, p = K.to_mol(Al, Ca, Na, Kk, P)
print('== (나) 첫 시료(%s) 단계별' % r0['sample'])
print('   몰/100 g: Al %.5f  Ca %.5f  Na %.6f  K %.6f  P %.6f' % (a, c, n, k, p))
cs = K.cao_star(c, n, p, 'A')
print('   CaO - 10/3 P2O5 = %.5f - %.6f = %.5f ; Na2O = %.6f ; CaO* = min = %.6f' % (c, 10 / 3 * p, c - 10 / 3 * p, n, cs))
print('   분모 %.6f, CIA = 100 x %.5f / %.6f = %.2f (표 %s)' % (a + cs + n + k, a, a + cs + n + k, K.cia(Al, Ca, Na, Kk, P), r0['CIA_table']))

print('== (다) 30개 시료: 규칙 A로 계산한 CIA와 표의 CIA')
print('%2s %-6s %6s %6s %8s %8s %7s %8s' % ('번', '시료', 'Al2O3', 'CaO', 'CIA계산', 'CIA표', '차', '10산화물합'))
res = []
for i, r in enumerate(rows):
    v = {kk: float(r[kk]) for kk in r if kk != 'sample'}
    ci = K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'], 'A')
    tot = sum(v[x] for x in ('Al2O3', 'CaO', 'Fe', 'K2O', 'Mg', 'Mn', 'Na2O', 'P2O5', 'Ti', 'SiO2'))
    res.append((r['sample'], ci, v['CIA_table'], v))
    print('%2d %-6s %6.2f %6.2f %8.2f %8.2f %+7.2f %8.2f' % (i + 1, r['sample'], v['Al2O3'], v['CaO'], ci, v['CIA_table'], ci - v['CIA_table'], tot))
diff = np.array([x[1] - x[2] for x in res])
ok = [i for i in range(N) if abs(diff[i]) <= 0.1]
bad = [i for i in range(N) if abs(diff[i]) > 0.1]
print('차이 0.1 이하 %d개, 초과 %d개: %s' % (len(ok), len(bad), ', '.join('%s %+.2f' % (res[i][0], diff[i]) for i in bad)))
print('0.1 이하 27개의 차이 최대 %.3f, 평균 %.4f' % (np.abs(diff[ok]).max(), np.abs(diff[ok]).mean()))
print('이 책 계산 CIA 전체 평균 %.2f; 표 평균 %.2f, 최소 %.2f (%s), 최대 %.2f (%s)' % (
    np.mean([x[1] for x in res]), np.mean([x[2] for x in res]),
    min(x[2] for x in res), [x[0] for x in res if x[2] == min(y[2] for y in res)][0],
    max(x[2] for x in res), [x[0] for x in res if x[2] == max(y[2] for y in res)][0]))

print('== (라) 규칙 A~D 비교: 맞지 않는 세 시료')
print('%-6s %6s %6s %6s %6s %6s %12s' % ('시료', '표', 'A', 'B', 'C', 'D', 'CaO-10/3P(몰)'))
for i in bad:
    v = res[i][3]
    cc = [K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'], t) for t in 'ABCD']
    a_, c_, n_, k_, p_ = K.to_mol(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'])
    print('%-6s %6.2f %6.2f %6.2f %6.2f %6.2f %12.6f' % (res[i][0], v['CIA_table'], *cc, c_ - 10 / 3 * p_))
print('30개 시료에서 규칙별로 표와 0.1 이내인 개수:')
for t in 'ABCD':
    cnt = sum(1 for i, r in enumerate(res) if abs(K.cia(r[3]['Al2O3'], r[3]['CaO'], r[3]['Na2O'], r[3]['K2O'], r[3]['P2O5'], t) - r[2]) <= 0.1)
    print('   규칙 %s: %d / %d' % (t, cnt, N))

print('== (마) CIW, PIA (이 책의 계산. 논문의 값이 아니다) — 처음 5개와 맞지 않는 세 시료')
print('%-6s %6s %6s %6s' % ('시료', 'CIA', 'CIW', 'PIA'))
for i in list(range(5)) + bad:
    v = res[i][3]
    print('%-6s %6.2f %6.2f %6.2f' % (res[i][0], K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5']),
          K.ciw(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5']), K.pia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'])))
print('== (바) A-CN-K 좌표(합 100): 처음 3개')
for i in range(3):
    v = res[i][3]
    A, CN, KK = K.ack(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'])
    print('   %-6s A %.2f  CN %.2f  K %.2f  합 %.2f  (A는 CIA와 같다: CIA %.2f)' % (res[i][0], A, CN, KK, A + CN + KK, K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'])))

print('== (사) 입도 대용 SiO2/Al2O3 와 CIA(표)의 피어슨 상관')
sa = np.array([x[3]['SiO2'] / x[3]['Al2O3'] for x in res]); ct = np.array([x[2] for x in res]); ka = np.array([x[3]['K2O'] / x[3]['Al2O3'] for x in res])
r30 = stats.pearsonr(sa, ct)
keep = [i for i, x in enumerate(res) if x[0] not in ('감강', '원강')]
r28 = stats.pearsonr(sa[keep], ct[keep])
print('   30개: r = %.3f (p = %.2g)   감강·원강 제외 28개: r = %.3f (p = %.2g)' % (r30[0], r30[1], r28[0], r28[1]))
print('   SiO2/Al2O3 대 K2O/Al2O3: r = %.3f' % stats.pearsonr(sa, ka)[0])
# 계산 CIA(규칙 A)로 같은 상관
cc = np.array([x[1] for x in res])
print('   (참고) 표 CIA 대신 이 책 계산 CIA(규칙 A)로: 30개 r = %.3f' % stats.pearsonr(sa, cc)[0])
print('본류 17개(제1권 10장 목록) 가운데 무한2 -> 장흥도 CIA(표) 변화: %.2f -> %.2f = %+.2f' % (
    res[24][2], res[29][2], res[29][2] - res[24][2]))
print('걸린 시간 %.3f초' % (time.time() - t0))
