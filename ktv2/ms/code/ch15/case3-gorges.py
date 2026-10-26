# -*- coding: utf-8 -*-
"""사례 3: 삼협댐은 유사를 얼마나 붙잡았나, 장강 퇴적물의 풍화 지수는 얼마인가 (제1권 10장 10.2절, 10.5절).
입력(제1권 10장 표 4, 5, 6, 10) -> Brune 포획 효율(8장 sedkit) -> 구간 수지와 실측 포획 효율(제1권 계산 10-2, 10-3의 산술)
-> 연 단위 변동과 연 재표집(5장 방식) -> CIA 30개 재계산(8장 sedkit) -> 제1권 값과 대조.
앞 장의 모듈(ch08/sedkit.py)을 그대로 불러 쓴다. 새로 짠 부분은 이 파일의 산술, 연 재표집, 진단 계산이다.
실행: python3 case3-gorges.py > case3.log   (먼저 00-extract-inputs.py를 한 번 실행해 data/를 만든다)
로그에 시간을 적지 않는다. 난수 시드는 코드에 고정했다."""
import csv, hashlib, json, math, os, platform, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'ch08'))
import numpy as np, scipy
from scipy import stats
import sedkit as K             # 8장
import v1tables as V

print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
print('앞 장 모듈: ch08/sedkit.py(%s, sha256 %s)' % (K.VERSION, hashlib.sha256(open(K.__file__, 'rb').read()).hexdigest()[:16]))
OUT = {}
SUM = []


def add(item, v1, mine, ok, note=''):
    SUM.append((item, v1, mine, ok, note))


def same(mine, printed):
    printed = printed.replace(',', '')
    nd = len(printed.split('.')[1]) if '.' in printed else 0
    return round(mine, nd) == float(printed)


def rd(fn):
    return list(csv.DictReader(open(os.path.join(HERE, 'data', fn), encoding='utf-8')))


# ------------------------------------------------------------------ A. Brune
print('\n== A. Brune 포획 효율 TE = 1 - 0.05 / sqrt(V/Q)  (입력: 제1권 10장 표 4, data/hu2009-table4-v1.csv)')
t4 = rd('hu2009-table4-v1.csv')
print('%-11s %6s %5s | %8s %8s | %9s %9s %7s | %s' % ('대상', 'V', 'Q', 'V/Q 표', 'V/Q 계산', 'TE 계산 %', 'TE 제1권계산', 'TE 표 %', '반올림이 표와 같은가 / 제1권 계산 열과 같은가'))
BR = []
for r in t4:
    Vv, Q = float(r['V_km3']), float(r['Q_km3yr'])
    te = 100 * float(K.brune_te(Vv, Q))
    vq = Vv / Q
    okt = round(te) == round(float(r['TE_table_pct']))
    okv = round(te, 2) == round(float(r['TE_calc_vol1_pct']), 2)
    BR.append(dict(name=r['name'], V=Vv, Q=Q, vq=vq, te=te, te_table=float(r['TE_table_pct'])))
    print('%-11s %6.1f %5.0f | %8.2f %8.4f | %9.2f %9.2f %7.0f | %s / %s' % (r['name'], Vv, Q, float(r['VQ_table']), vq, te, float(r['TE_calc_vol1_pct']), float(r['TE_table_pct']), '같다' if okt else '다르다', '같다' if okv else '다르다'))
    add('Brune TE, ' + r['name'], '%s (표 %s)' % (r['TE_calc_vol1_pct'], r['TE_table_pct']), '%.2f' % te, okt and okv)
OUT['brune'] = BR
print('삼협댐 139 m: 제1권은 "논문 본문은 73%, 표 4는 72%, 이 책 계산은 71.69%"라고 적었다(계산 10-1 판정).')
print('  본문 73%%를 만들려면 Q = 436에서 필요한 저수량(sedkit.v_for_te): TE 72.5%% -> %.2f km3, 73.0%% -> %.2f km3, 73.5%% -> %.2f km3 (표 4의 139 m 단계 V = 13.6 km3)' % tuple(float(K.v_for_te(x, 436.0)) for x in (0.725, 0.73, 0.735)))
add('삼협댐 139 m의 포획 효율: 본문 73 대 이 계산', '본문 73, 표 72', '%.2f' % BR[5]['te'], False, '미결: 본문 73의 출처를 찾지 못함(제1권 계산 10-1과 같은 결론)')

# ------------------------------------------------------------------ B. 유사 수지
print('\n== B. 유사 수지 (입력: 제1권 10장 표 5, 표 6, data/hu2009-budget-v1.csv, 단위 Mt/yr)')
bud = rd('hu2009-budget-v1.csv')
S5 = {r['period']: [float(r['c%d' % i]) for i in range(1, 8)] for r in bud if r['segment'] == 'D1'}   # JS MJ JL U1 CT D1표 D1계산
S6 = {r['period']: [float(r['c%d' % i]) for i in range(1, 7)] for r in bud if r['segment'] == 'D2'}   # CT WJ U2 YC D2표 D2계산
per = list(S5)
print('%-10s | %5s %5s %5s %5s %5s -> %5s (표 %4s, 제1권계산 %4s) | %5s %5s %5s %5s -> %5s (표 %4s, 제1권계산 %4s)' % ('기간', '금사강', '민강', '가릉강', '미관측', '촌탄', '수지', '', '', '촌탄', '오강', '미관측', '의창', '수지', '', ''))
D1, D2, YC, CT = {}, {}, {}, {}
for p in per:
    a = S5[p]; b = S6[p]
    D1[p] = a[0] + a[1] + a[2] + a[3] - a[4]
    D2[p] = b[0] + b[1] + b[2] - b[3]
    YC[p] = b[3]; CT[p] = a[4]
    print('%-10s | %5.0f %5.0f %5.0f %5.0f %5.0f -> %5.0f (표 %4.0f, 제1권계산 %4.0f) | %5.0f %5.0f %5.0f %5.0f -> %5.0f (표 %4.0f, 제1권계산 %4.0f)' % (p, *a[:5], D1[p], a[5], a[6], *b[:4], D2[p], b[4], b[5]))
d1max = max(abs(D1[p] - S5[p][5]) for p in per)
d2bad = [p for p in per if D2[p] != S6[p][4]]
print('표 5: 계산과 표의 최대 차이 %.0f. 표 6: 계산과 표가 다른 기간 %s (차이 %s)' % (d1max, d2bad, [D2[p] - S6[p][4] for p in d2bad]))
add('구간 수지 표 5(촌탄-병산)의 계산과 표의 최대 차이', '0', '%.0f' % d1max, d1max == 0)
add('구간 수지 표 6(의창-촌탄)의 계산과 표가 다른 기간', '2003~2008에서 1(반올림)', '%s에서 %s' % (d2bad, [int(D2[p] - S6[p][4]) for p in d2bad]), d2bad == ['2003~2008'] and (D2['2003~2008'] - S6['2003~2008'][4]) == 1.0)
# 가동 후 - 가동 전 (표의 값 그대로)
post, pre = '2003~2008', '1956~2002'
t1 = S5[post][5] - S5[pre][5]
t2 = S6[post][4] - S6[pre][4]
d3_post = S5[post][5] + S6[post][4]; d3_pre = S5[pre][5] + S6[pre][4]
t3 = d3_post - d3_pre
print('\n삼협댐이 만든 퇴적 = (2003~2008) - (1956~2002), 표의 수지 열: 촌탄-병산 %.0f - %.0f = %.0f, 의창-촌탄 %.0f - (%.0f) = %.0f, 의창-병산 %.0f - %.0f = %.0f' % (S5[post][5], S5[pre][5], t1, S6[post][4], S6[pre][4], t2, d3_post, d3_pre, t3))
add('삼협댐이 만든 퇴적 15, 152, 167 (Mt/yr)', '15, 152, 167', '%.0f, %.0f, %.0f' % (t1, t2, t3), (t1, t2, t3) == (15, 152, 167) and V.has(10, '표 15, 152, 167'))
eros = 3 / 31
print('하상 침식: (61 - 58)/(44 - 13) = %.4f Mt/km/yr(논문 0.1), 0.1 x 44 = %.1f, 167 + 4.4 = %.1f (논문 총량 172), 0.097 x 44을 쓰면 %.2f' % (eros, 0.1 * 44, 167 + 4.4, 167 + eros * 44))
add('하상 침식 3/31, 167 + 4.4', '0.097, 171.4', '%.3f, %.1f' % (eros, 167 + 4.4), same(eros, '0.097') and V.has(10, '167 + 4.4 = 171.4'))
dn, up = (152 + 4.4) / 171.4 * 100, 15 / 171.4 * 100
print('하류 구간 몫 (152 + 4.4)/171.4 = %.1f%%, 상류 15/171.4 = %.1f%% (논문 본문 88%%, 12%%). 하상 침식을 빼면 152/172 = %.1f%%, 15/172 = %.1f%%이고 합이 %.1f%%' % (dn, up, 152 / 172 * 100, 15 / 172 * 100, (152 + 15) / 172 * 100))
add('하류 구간 몫 대 상류 구간 몫 (%)', '논문 88, 12 / 제1권 계산 91.2, 8.8', '%.1f, %.1f' % (dn, up), same(dn, '91.2') and same(up, '8.8'), '미결: 논문의 88, 12는 재현되지 않음(제1권 계산 10-2 판정과 같은 결론)')

# 회귀식 (3)으로 "삼협댐이 없었다면"
print('\n식 (3) QSY = 1.125 QST - 20 (1986~2002 회귀, 계수는 제1권 계산 10-3이 옮긴 값) 로 가동 후 6개 연의 의창 유사량 추정')
print('식의 문자열이 제1권 원고에 있음:', V.has(10, 'QSY = 1.125 QST − 20'))
yrs = [p for p in per if p[0] == '2' and '~' not in p]
QST = np.array([S5[y][0] + S5[y][1] + S5[y][2] + S6[y][1] for y in yrs])
meas = np.array([YC[y] for y in yrs])
est = 1.125 * QST - 20
print('%-6s %6s %8s %6s %8s %9s' % ('연', 'QST', '추정', '실측', '차', '연 TE %'))
for y, q_, e_, m_ in zip(yrs, QST, est, meas):
    print('%-6s %6.0f %8.1f %6.0f %8.1f %9.1f' % (y, q_, e_, m_, e_ - m_, 100 * (e_ - m_) / e_))
print('평균: 추정 %.1f, 실측 %.1f, 차 %.1f, 최대 차 %.1f(%s), 최소 차 %.1f(%s)' % (est.mean(), meas.mean(), (est - meas).mean(), (est - meas).max(), yrs[int(np.argmax(est - meas))], (est - meas).min(), yrs[int(np.argmin(est - meas))]))
add('식 (3)의 추정 평균, 실측 평균, 차 평균', '228.4, 61.0, 167.4', '%.1f, %.1f, %.1f' % (est.mean(), meas.mean(), (est - meas).mean()), V.has(10, '228.4(논문 228)') and same(est.mean(), '228.4') and same(meas.mean(), '61.0') and same((est - meas).mean(), '167.4'))
add('최대·최소 차 (2008, 2006)', '214.6, 102.6', '%.1f, %.1f' % ((est - meas).max(), (est - meas).min()), same((est - meas).max(), '214.6') and same((est - meas).min(), '102.6'))
te_ratio = (est.mean() - meas.mean()) / est.mean() * 100
print('포획 효율: 172/228 = %.2f%% (논문 75%%), 167.4/228.4 = %.2f%% (이 계산의 추정 평균으로 %.2f%%)' % (100 * 172 / 228, 100 * 167.4 / 228.4, te_ratio))
add('포획 효율 172/228, 167.4/228.4 (%)', '75.4, 73.3', '%.1f, %.1f' % (100 * 172 / 228, 100 * 167.4 / 228.4), same(100 * 172 / 228, '75.4') and same(100 * 167.4 / 228.4, '73.3'))
# 식 (4)
lr = stats.linregress(QST, meas)
print('식 (4) QSY = 0.554 QST - 61 (2003~2008, 논문 R² = 0.71)을 6개 점에 최소제곱으로 맞추면: 기울기 %.3f, 절편 %.1f, R² = %.3f' % (lr.slope, lr.intercept, lr.rvalue ** 2))
add('식 (4)를 6개 점에 맞춘 기울기, 절편, R²', '0.554, -61.4, 0.713', '%.3f, %.1f, %.3f' % (lr.slope, lr.intercept, lr.rvalue ** 2), same(lr.slope, '0.554') and same(lr.intercept, '-61.4') and same(lr.rvalue ** 2, '0.713'))

# ------------------------------------------------------------------ C. 포획 효율 비교와 연 재표집
print('\n== C. 두 방법의 포획 효율을 맞대고, 연 단위 변동으로 불확실성을 본다 (이 책의 시연)')
v75 = float(K.v_for_te(0.7544, 436.0)); v733 = float(K.v_for_te(0.7329, 436.0))
print('실측 포획 효율 75.44%%를 Brune로 내는 저수량 V = %.2f km3, 73.29%%이면 %.2f km3. 표 4의 단계 V = 13.6(TE %.2f), 23.1(TE %.2f), 39.3(TE %.2f) km3' % (v75, v733, BR[5]['te'], BR[6]['te'], BR[7]['te']))
print('따라서 실측 TE는 139 m 단계와 156 m 단계 사이에 있다(Brune 71.69% < 실측 73.3~75.4% < 78.28%).')
yte = 100 * (est - meas) / est
print('연 TE = (추정 - 실측)/추정: ' + ', '.join('%s %.1f' % (y, t) for y, t in zip(yrs, yte)) + ' (%%) | 평균 %.1f, 표준편차 %.1f, 최소 %.1f, 최대 %.1f' % (yte.mean(), yte.std(ddof=1), yte.min(), yte.max()))
print('합쳐 계산한 TE(합계의 비) %.2f%%와 연 TE의 평균 %.2f%%는 같지 않다.' % (te_ratio, yte.mean()))
rng = np.random.default_rng(20261026)
B = 100000
idx = rng.integers(0, len(yrs), size=(B, len(yrs)))
bt = (est[idx].sum(axis=1) - meas[idx].sum(axis=1)) / est[idx].sum(axis=1) * 100
q = np.percentile(bt, [2.5, 50, 97.5])
print('연을 복원추출로 다시 뽑은 합계 비 TE(%d번, 시드 20261026): 2.5%% %.1f, 중앙 %.1f, 97.5%% %.1f  (관측 %.2f)' % (B, *q, te_ratio))
jk = [100 * ((est.sum() - est[i]) - (meas.sum() - meas[i])) / (est.sum() - est[i]) for i in range(len(yrs))]
print('한 해씩 빼고 다시 계산한 TE: ' + ', '.join('%s 제외 %.1f' % (y, t) for y, t in zip(yrs, jk)) + ' (%)')
lo_in = [b['name'] for b in BR[5:8] if q[0] <= b['te'] <= q[2]]
print('이 구간(%.1f~%.1f%%) 안에 든 Brune 값: %s' % (q[0], q[2], ', '.join('%s %.2f' % (b['name'], b['te']) for b in BR[5:8] if q[0] <= b['te'] <= q[2])))
OUT['te'] = dict(years=yrs, est=est.tolist(), meas=meas.tolist(), yte=yte.tolist(), te_ratio=te_ratio, boot_q=[float(x) for x in q], jack=jk, brune3=[BR[5]['te'], BR[6]['te'], BR[7]['te']], te_paper=100 * 172 / 228, te_167=100 * 167.4 / 228.4)

# ------------------------------------------------------------------ D. CIA
print('\n== D. 풍화 지수 CIA = 100 Al2O3 / (Al2O3 + CaO* + Na2O + K2O) (몰, 입력: 제1권 10장 표 10, data/he2015-table2-v1.csv)')
t10 = rd('he2015-table2-v1.csv')
print('몰질량(sedkit.MW, g/mol): ' + ', '.join('%s %.3f' % (k, v) for k, v in K.MW.items()) + ' (제1권 계산 10-8과 같다: %s)' % V.has(10, 'Al₂O₃ 101.961, CaO 56.077, Na₂O 61.979, K₂O 94.196, P₂O₅ 141.945'))
CIA = []
for r in t10:
    v = {k: float(r[k]) for k in ('Al2O3', 'CaO', 'Na2O', 'K2O', 'P2O5', 'SiO2', 'CIA_table', 'CIA_calc_vol1', 'diff_vol1')}
    c = K.cia(v['Al2O3'], v['CaO'], v['Na2O'], v['K2O'], v['P2O5'], 'A')
    CIA.append(dict(sample=r['sample'], calc=c, **v))
diff = np.array([x['calc'] - x['CIA_table'] for x in CIA])
bad = [i for i in range(30) if abs(diff[i]) > 0.1]
okv = [abs(round(x['calc'], 2) - x['CIA_calc_vol1']) < 0.0051 for x in CIA]
print('30개 가운데 이 계산(규칙 A)이 제1권 표의 "CIA(계산)" 열과 소수 둘째 자리까지 같은 것: %d개' % sum(okv))
print('이 계산과 논문 CIA(표)의 차이가 0.1 이하인 시료 %d개, 초과 %d개: %s' % (30 - len(bad), len(bad), ', '.join('%s %+.2f' % (CIA[i]['sample'], diff[i]) for i in bad)))
print('0.1 이하 %d개의 차이: 최대 %.3f, 평균 절댓값 %.4f' % (30 - len(bad), max(abs(diff[i]) for i in range(30) if i not in bad), np.mean([abs(diff[i]) for i in range(30) if i not in bad])))
add('CIA 30개 중 차이 0.1 이하, 초과', '27, 3', '%d, %d' % (30 - len(bad), len(bad)), (30 - len(bad), len(bad)) == (27, 3) and V.has(10, '차이가 0.1 이하인 시료가 27개'))
add('어긋난 세 시료의 차이(원강, 상강, 감강)', '+1.51, +3.87, +2.82', ', '.join('%+.2f' % diff[i] for i in bad), [CIA[i]['sample'] for i in bad] == ['원강', '상강', '감강'] and all(same(diff[i], s) for i, s in zip(bad, ('1.51', '3.87', '2.82'))))
add('CIA 계산이 제1권 표의 계산 열과 같은 시료 수', '30', str(sum(okv)), sum(okv) == 30)
cia_t = np.array([x['CIA_table'] for x in CIA])
print('CIA(표) 평균 %.2f, 최소 %.2f(%s), 최대 %.2f(%s)' % (cia_t.mean(), cia_t.min(), CIA[int(np.argmin(cia_t))]['sample'], cia_t.max(), CIA[int(np.argmax(cia_t))]['sample']))
add('CIA(표) 평균, 최소, 최대', '64.84, 56.45, 80.14', '%.2f, %.2f, %.2f' % (cia_t.mean(), cia_t.min(), cia_t.max()), same(cia_t.mean(), '64.84') and same(cia_t.min(), '56.45') and same(cia_t.max(), '80.14'))
print('\n규칙 A~D(sedkit.cao_star)로 어긋난 세 시료를 다시: 표 값에 닿는 규칙이 있는가')
print('%-5s %7s %7s %7s %7s %7s' % ('시료', '표', 'A', 'B', 'C', 'D'))
RULES = {}
for i in bad:
    x = CIA[i]
    rr = [K.cia(x['Al2O3'], x['CaO'], x['Na2O'], x['K2O'], x['P2O5'], t) for t in 'ABCD']
    RULES[x['sample']] = rr
    print('%-5s %7.2f %7.2f %7.2f %7.2f %7.2f' % (x['sample'], x['CIA_table'], *rr))
print('표의 CIA를 내려면 필요한 CaO*(몰/100 g)와 이 시료가 가진 값(진단. 논문이 쓴 입력이 무엇인지는 이 책이 모른다)')
print('%-5s %12s %12s %12s %14s %12s %10s' % ('시료', 'CaO*필요', 'CaO', 'Na2O', 'CaO-10/3 P2O5', '규칙 A의 CaO*', '필요/Na2O'))
DIAG = {}
for i in bad + [0, 1, 2]:
    x = CIA[i]
    a, c, n, k, p = K.to_mol(x['Al2O3'], x['CaO'], x['Na2O'], x['K2O'], x['P2O5'])
    need = a / (x['CIA_table'] / 100) - a - n - k
    DIAG[x['sample']] = dict(need=need, cao=c, na=n, a_rule=K.cao_star(c, n, p, 'A'), ratio=need / n)
    print('%-5s %12.6f %12.6f %12.6f %14.6f %12.6f %10.3f' % (x['sample'], need, c, n, c - 10 / 3 * p, K.cao_star(c, n, p, 'A'), need / n))
print('(앞의 세 줄이 어긋난 시료, 뒤의 세 줄은 맞는 시료 3개로 같은 계산이 규칙 A의 CaO*와 맞는지 보인다. 표의 CIA는 소수 둘째 자리로 반올림된 값이라 필요한 CaO*에는 반올림 폭의 오차가 있다.)')

print('\n규칙 E(이 장에서 새로 시험): CaO* = Na2O로 고정(인회석 보정과 CaO의 크기를 보지 않음). 자유 매개변수가 없다.')


def cia_e(Al2O3, CaO, Na2O, K2O, P2O5):
    a, c, n, k, p = K.to_mol(Al2O3, CaO, Na2O, K2O, P2O5)
    return 100.0 * a / (a + n + n + k)


ce = np.array([cia_e(x['Al2O3'], x['CaO'], x['Na2O'], x['K2O'], x['P2O5']) for x in CIA])
de = ce - cia_t
print('규칙 E의 CIA와 논문 CIA(표)의 차이: 0.1 이하 %d개, 초과 %d개, 절댓값 최대 %.3f(%s), 평균 %.4f' % (int((np.abs(de) <= 0.1).sum()), int((np.abs(de) > 0.1).sum()), np.abs(de).max(), CIA[int(np.argmax(np.abs(de)))]['sample'], np.abs(de).mean()))
print('어긋났던 세 시료: ' + ', '.join('%s 규칙 E %.2f (표 %.2f, 차 %+.2f)' % (CIA[i]['sample'], ce[i], cia_t[i], de[i]) for i in bad))
print('나머지 27개에서는 규칙 A와 규칙 E가 같다(CaO - 10/3 P2O5가 Na2O보다 커서 Na2O가 CaO*가 된다): 최대 차이 %.2e' % max(abs(ce[i] - CIA[i]['calc']) for i in range(30) if i not in bad))
print('해석의 한계: 규칙 E가 표의 값에 닿는다는 것은 이 책이 확인한 사실이지만 논문이 이 규칙을 썼다는 근거는 아니다. 논문의 방법과 입력은 이 책이 읽지 못했다.')
OUT['cia_e'] = dict(n_ok=int((np.abs(de) <= 0.1).sum()), maxabs=float(np.abs(de).max()), bad=[float(ce[i]) for i in bad], diff_bad=[float(de[i]) for i in bad])
add('규칙 E(CaO* = Na2O)로 표와 0.1 이내인 시료 수(이 장의 새 시험)', '(제1권에 없음)', '%d / 30' % int((np.abs(de) <= 0.1).sum()), int((np.abs(de) <= 0.1).sum()) == 30, '관찰: 어긋난 세 시료의 한 설명이 될 수 있으나 논문의 방법은 미확인')

sa = np.array([x['SiO2'] / x['Al2O3'] for x in CIA]); ka = np.array([x['K2O'] / x['Al2O3'] for x in CIA])
r30 = stats.pearsonr(sa, cia_t)
keep = [i for i, x in enumerate(CIA) if x['sample'] not in ('감강', '원강')]
r28 = stats.pearsonr(sa[keep], cia_t[keep])
rk = stats.pearsonr(sa, ka)
print('\n입도 대용 SiO2/Al2O3와 CIA(표)의 피어슨 상관: 30개 r = %.3f (p = %.2g), 감강·원강 뺀 28개 r = %.3f (p = %.2g); SiO2/Al2O3 대 K2O/Al2O3 r = %.3f' % (r30[0], r30[1], r28[0], r28[1], rk[0]))
add('r(SiO2/Al2O3, CIA표) 30개, 28개', '-0.590, -0.726', '%.3f, %.3f' % (r30[0], r28[0]), same(r30[0], '-0.590') and same(r28[0], '-0.726') and V.has(10, 'r = −0.590'))
add('r(SiO2/Al2O3, K2O/Al2O3)', '0.285', '%.3f' % rk[0], same(rk[0], '0.285'))
main = ['타타하', '금사강', '석고', '반지화 1', '의빈 2', '중경 1', '중경 2', '부릉 2', '파동', '의창', '악양 2', '무한 1', '무한 2', '구강', '호구', '남경', '장흥도']
cmap = {x['sample']: x['CIA_table'] for x in CIA}
mc = [cmap[m] for m in main]
print('본류 17개(제1권 10.5절 목록 순서)의 CIA(표): ' + ' '.join('%.2f' % v for v in mc))
print('무한 2(%.2f)에서 장흥도(%.2f)까지 %+.2f' % (cmap['무한 2'], cmap['장흥도'], cmap['장흥도'] - cmap['무한 2']))
add('본류 무한 2 -> 장흥도 CIA(표) 변화', '-9.64', '%+.2f' % (cmap['장흥도'] - cmap['무한 2']), same(cmap['장흥도'] - cmap['무한 2'], '-9.64') and V.has(10, '−9.64'))
OUT['cia'] = [dict(sample=x['sample'], calc=x['calc'], table=x['CIA_table'], sio2_al=x['SiO2'] / x['Al2O3']) for x in CIA]
OUT['cia_bad'] = [CIA[i]['sample'] for i in bad]
OUT['cia_r'] = dict(r30=r30[0], r28=r28[0], rk=rk[0])
OUT['cia_diag'] = DIAG
OUT['cia_rules'] = RULES

print('\n== E. 요약: 기준값(제1권 원고)과 이번 실행값')
for item, v1, mine, ok, note in SUM:
    print('  %-50s 제1권 %-30s 이번 %-26s %s %s' % (item, v1, mine, '일치' if ok else '불일치', note))
print('비교 %d개, 일치 %d개, 불일치 %d개' % (len(SUM), sum(1 for x in SUM if x[3]), sum(1 for x in SUM if not x[3])))
OUT['summary'] = [dict(item=a, v1=b, mine=c, ok=bool(d), note=n) for a, b, c, d, n in SUM]
json.dump(OUT, open(os.path.join(HERE, 'case3.json'), 'w'), ensure_ascii=False, default=float)
