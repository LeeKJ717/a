# -*- coding: utf-8 -*-
"""실습 8-5: 유사량과 포획 효율.
(가) Hu 등(2009) 표 4의 Brune 포획 효율 8줄 (제1권 10장 계산 10-1)
(나) 삼협댐 139 m의 본문 73 %를 만들려면 필요한 저수량 (이 책의 계산)
(다) 표 3의 구간 수지와 포획 효율의 산술 (제1권 계산 10-2, 10-3), 표 1의 유출 깊이와 유사 수율 (계산 10-5)
(라) 퇴적률과 질량 집적률 (제1권 8장 계산 8-9, 8-11; 밀도는 시연값)
(마) 오차 전파: 관측 오차 5 %는 시연값. 해석적 합성과 몬테카를로를 비교한다."""
import csv, os, sys, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sedkit as K
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
def rd(fn):
    return list(csv.DictReader(open(os.path.join(HERE, 'data', fn), encoding='utf-8')))

print('== (가) Brune 포획 효율 TE = 1 - 0.05 / sqrt(V/Q)  (입력: data/hu2009-table4.csv)')
t4 = rd('hu2009-table4.csv')
print('%-11s %6s %5s %8s %8s %9s %7s %8s' % ('대상', 'V', 'Q', 'V/Q표', 'V/Q계산', 'TE계산%', 'TE표%', '반올림=표'))
allok = True
for r in t4:
    V, Q, vq, te = float(r['V_km3']), float(r['Q_km3yr']), float(r['VQ_table']), float(r['TE_table_pct'])
    c = 100 * float(K.brune_te(V, Q))
    ok = round(c) == round(te)
    allok &= ok
    print('%-11s %6.1f %5.0f %8.2f %8.4f %9.2f %7.0f %8s' % (r['name'], V, Q, vq, V / Q, c, te, '예' if ok else '아니오'))
print('8줄 모두 반올림한 값이 표와 같다: %s' % ('예' if allok else '아니오'))
print('제1권 계산 10-1의 TE: 77.45 86.92 82.69 73.45 90.64 71.69 78.28 83.35')
mine = [round(100 * float(K.brune_te(float(r['V_km3']), float(r['Q_km3yr']))), 2) for r in t4]
v1 = [77.45, 86.92, 82.69, 73.45, 90.64, 71.69, 78.28, 83.35]
print('이 책 계산:             ' + ' '.join('%.2f' % x for x in mine) + '   일치: %s' % ('예' if mine == v1 else '아니오'))
print('시연값 V = 2, 8 km3, Q = 100 km3/yr: TE = %.2f %%, %.2f %% (제1권 10.10.1절 64.64, 82.32)' % tuple(100 * float(K.brune_te(v, 100)) for v in (2, 8)))
print('4개 댐 저수량 합: 소수 첫째 자리 값 %.1f, 소수 둘째 자리 값(5.86+19.01+11.57+4.98) %.2f (표·본문 41.4)' % (sum(float(r['V_km3']) for r in t4[:4]), 5.86 + 19.01 + 11.57 + 4.98))

print('\n== (나) 삼협댐(Q = 436 km3/yr)의 TE가 72.5~73.5 %가 되려면 필요한 저수량 (이 책의 계산)')
for te in (0.725, 0.73, 0.735):
    print('   TE %.1f %% -> V/Q = (0.05/%.3f)^2 = %.5f -> V = %.2f km3' % (100 * te, 1 - te, (0.05 / (1 - te)) ** 2, float(K.v_for_te(te, 436.0))))
print('   표 4의 139 m 단계 V = 13.6 km3는 TE %.2f %%.' % (100 * float(K.brune_te(13.6, 436.0))))

print('\n== (다-1) 구간 수지 (입력: data/hu2009-table3.csv, 단위 Mt/yr)')
t3 = rd('hu2009-table3.csv')
cols = ['JS', 'MJ', 'JL', 'WJ', 'CT', 'YC', 'U1', 'U2', 'U3', 'D1', 'D2', 'D3']
T = {c: [float(r[c]) for r in t3] for c in cols}
per = [r['period'] for r in t3]
d1 = [T['JS'][i] + T['MJ'][i] + T['JL'][i] + T['U1'][i] - T['CT'][i] for i in range(8)]
d2 = [T['CT'][i] + T['WJ'][i] + T['U2'][i] - T['YC'][i] for i in range(8)]
d3 = [T['D1'][i] + T['D2'][i] for i in range(8)]
print('   촌탄-병산 D1 = 금사강+민강+가릉강+미관측 U1-촌탄: 계산 %s' % ' '.join('%d' % x for x in d1))
print('                                                   표 %s   최대 차이 %d' % (' '.join('%d' % x for x in T['D1']), max(abs(a - b) for a, b in zip(d1, T['D1']))))
print('   의창-촌탄 D2 = 촌탄+오강+미관측 U2-의창:       계산 %s' % ' '.join('%d' % x for x in d2))
print('                                                   표 %s   최대 차이 %d (%s)' % (' '.join('%d' % x for x in T['D2']), max(abs(a - b) for a, b in zip(d2, T['D2'])), ', '.join(per[i] for i in range(8) if d2[i] != T['D2'][i])))
print('   의창-병산 D3 = D1 + D2:                        계산 %s' % ' '.join('%d' % x for x in d3))
print('                                                   표 %s   최대 차이 %d' % (' '.join('%d' % x for x in T['D3']), max(abs(a - b) for a, b in zip(d3, T['D3']))))
print('   6개 연 평균과 표의 2003-2008 열:')
for c in cols:
    print('     %-3s 평균 %7.2f  표 %3.0f' % (c, sum(T[c][:6]) / 6, T[c][6]))
t1_, t2_, t3_ = (T[c][6] - T[c][7] for c in ('D1', 'D2', 'D3'))
print('   삼협댐이 만든 퇴적 = (2003-2008) - (1956-2002): D1 %.0f, D2 %.0f, D3 %.0f (표 15, 152, 167)' % (t1_, t2_, t3_))
print('   하상 침식: (61 - 58)/(44 - 13) = %.4f Mt/km/yr; 0.1 x 44 = %.1f; 167 + 4.4 = %.1f' % (3 / 31, 0.1 * 44, 167 + 4.4))
print('   하류 구간 비율 (152+4.4)/(167+4.4) = %.1f %%, 상류 15/171.4 = %.1f %% (논문 본문 88 / 12)' % (100 * 156.4 / 171.4, 100 * 15 / 171.4))

print('\n== (다-2) 회귀식으로 가정한 의창 유사량과 포획 효율 (식과 계수는 제1권 계산 10-3이 옮긴 것: 1.125 x (4대 지류 합) - 20)')
ST = [T['JS'][i] + T['MJ'][i] + T['JL'][i] + T['WJ'][i] for i in range(6)]
est = [1.125 * s - 20 for s in ST]
yc = T['YC'][:6]
dif = [e - y for e, y in zip(est, yc)]
for i in range(6):
    print('   %s: 4대 지류 합 %3.0f -> %6.1f ; 실측 %3.0f ; 차 %6.1f' % (per[i], ST[i], est[i], yc[i], dif[i]))
print('   평균: 추정 %.1f, 실측 %.1f, 차 %.1f ; 최대 %.1f (%s), 최소 %.1f (%s)' % (np.mean(est), np.mean(yc), np.mean(dif), max(dif), per[dif.index(max(dif))], min(dif), per[dif.index(min(dif))]))
print('   포획 효율 = 172/228 = %.2f %% (논문 75) ; 167.4/228.4 = %.2f %%' % (100 * 172 / 228, 100 * 167.4 / 228.4))
print('   같은 삼협댐 139 m: Brune %.2f %%, 수지 %.2f %%, 논문 본문 73 %%, 표 72 %%' % (100 * float(K.brune_te(13.6, 436)), 100 * 172 / 228))

print('\n== (다-3) 지점별 유출 깊이와 유사 수율 (입력: data/hu2009-table1.csv)')
t1 = rd('hu2009-table1.csv')
print('   %-4s %8s %6s %6s %12s %14s' % ('지점', '면적(1e4km2)', 'Q', 'S', '유출깊이mm/yr', '수율 t/km2/yr'))
for r in t1:
    A, Q, S = float(r['area_1e4km2']), float(r['Q_km3yr']), float(r['S_Mtyr'])
    print('   %-4s %8.2f %6.0f %6.0f %12.0f %14.0f' % (r['station'], A, Q, S, K.runoff_mm(Q, A), K.yield_t_km2_yr(S, A)))

print('\n== (라) 퇴적률, 해상도, 질량 집적률')
print('   Guo 등(2009)의 Xifeng (제1권 계산 8-9): 시료 723개 x 10 cm = %d cm, 800 ka / 723 = %.1f 년/시료' % (723 * 10, 800 / 723 * 1000))
for lab, yr in (('황토 800년/10 cm', 800), ('고토양 2000년/10 cm', 2000)):
    l_ = K.lsr(10, yr)
    m_ = K.mar(l_, 2.5)
    print('   %-20s 퇴적률 %.2f cm/ka, 플럭스 %.2f g/cm2/ka = %.1f g/m2/yr (밀도 2.5 g/cm3는 논문의 평균 먼지 밀도)' % (lab, l_, m_, m_ * 10000 / 1000))
f = (800 * 1000 / 723 - 800) / (2000 - 800)
print('   평균 %.1f 년/시료가 800과 2000의 가중 평균이려면 고토양 몫 f = %.3f' % (800 * 1000 / 723, f))
print('   Dou 등(2021) 코어 LV53-18-2 (제1권 계산 8-11): 393 cm / 30.03 ka = %.2f cm/ka, 해상도 %.1f 년/cm' % (K.lsr(393, 30030), 30030 / 393))
for lab, r_ in (('빙하기', 20.7), ('탈빙기', 10.7), ('홀로세', 10.3)):
    print('   %s %.1f cm/ka -> %.1f 년/cm' % (lab, r_, 1000 / r_))
print('   시료 120개: 간격 %.2f cm, 시간 간격 %.0f 년' % (393 / 120, 393 / 120 * 30030 / 393))
print('   질량 집적률 시연: LSR 10.3 cm/ka x 건조 부피 밀도 1.0 g/cm3(시연값) = %.1f g/cm2/ka; 밀도 0.8이면 %.2f, 1.2이면 %.2f' % (K.mar(10.3, 1.0), K.mar(10.3, 0.8), K.mar(10.3, 1.2)))

print('\n== (마) 오차 전파 (시연값: 각 관측량이 독립이고 상대 오차 5 %, 정규분포)')
terms = [('금사강', 156.0, +1), ('민강', 35.0, +1), ('가릉강', 23.0, +1), ('미관측 U1', 26.0, +1), ('촌탄', 197.0, -1)]
rel = 0.05
D = sum(s * v for _, v, s in terms)
sd = math.sqrt(sum((rel * v) ** 2 for _, v, _ in terms))
print('   D1(2003-2008) = %s = %.1f Mt/yr' % (' '.join('%+d x %.0f' % (s, v) for _, v, s in terms), D))
print('   해석적 합성: 표준편차 = sqrt(%s) = %.2f Mt/yr -> 상대 %.0f %%' % (' + '.join('%.2f' % ((rel * v) ** 2) for _, v, _ in terms), sd, 100 * sd / D))
rng = np.random.default_rng(20261026)
N = 1_000_000
X = np.column_stack([rng.normal(v, rel * v, N) * s for _, v, s in terms])
S = X.sum(axis=1)
print('   몬테카를로 %d번(시드 20261026): 평균 %.2f, 표준편차 %.2f, 2.5 %% %.2f, 97.5 %% %.2f' % (N, S.mean(), S.std(), *np.percentile(S, [2.5, 97.5])))
# TE = 172/228 에서 분자, 분모 오차
num, den = 172.0, 228.0
sn, sdn = 0.05 * num, 0.05 * den
te = num / den
print('   포획 효율 TE = 172/228 = %.4f. 분자와 분모가 독립이고 각 5 %%이면 (상대 오차의 제곱합) 표준편차 = %.4f' % (te, te * math.sqrt(0.05 ** 2 + 0.05 ** 2)))
a = rng.normal(num, sn, N); b = rng.normal(den, sdn, N)
TEs = a / b
print('   몬테카를로 TE: 평균 %.4f, 표준편차 %.4f, 2.5 %% %.4f, 97.5 %% %.4f' % (TEs.mean(), TEs.std(), *np.percentile(TEs, [2.5, 97.5])))
print('   (172는 따로 잰 값이 아니라 수지에서 나온 값이어서 분자와 분모가 독립이 아니다. 아래는 오차 상관의 효과를 보이는 시연이다: 추정 228과 실측 61에 5 %를 독립으로 주고 TE = (228 - 61)/228로 계산. 논문의 172/228 계산을 그대로 흉내 낸 것이 아니다.)')
c = rng.normal(228.0, 0.05 * 228, N); d = rng.normal(61.0, 0.05 * 61, N)
TE2 = (c - d) / c
print('   TE = (228 - 61)/228 = %.4f ; 몬테카를로: 평균 %.4f, 표준편차 %.4f, 2.5 %% %.4f, 97.5 %% %.4f' % (167 / 228, TE2.mean(), TE2.std(), *np.percentile(TE2, [2.5, 97.5])))
print('걸린 시간 %.3f초' % (time.time() - t0))
