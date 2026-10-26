# -*- coding: utf-8 -*-
"""실습 15-0: 세 사례의 입력을 제1권 원고에서 옮긴다. 손으로 옮기지 않고 원고의 표를 번호로 읽는다.
읽는 파일: /home/claude/book/ms/ch04-v1.md, ch10-v1.md, ch11-v1.md (읽기만 한다).
쓰는 파일: data/*.csv. 옮긴 표가 앞 장(8장)이 제1권 계산 스크립트에서 뽑아 둔 CSV와 같은지 대조한다.
표가 아니라 계산 상자의 문장에 있는 14C 날짜는 원고에 같은 문자열이 있는지 확인한 뒤 옮긴다.
실행: python3 00-extract-inputs.py > 00-extract-inputs.log"""
import csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v1tables as V
D = os.path.join(HERE, 'data')
C8 = os.path.join(HERE, '..', 'ch08', 'data')
os.makedirs(D, exist_ok=True)
FAIL = []


def w(fn, head, rows):
    with open(os.path.join(D, fn), 'w', encoding='utf-8', newline='') as f:
        cw = csv.writer(f); cw.writerow(head); cw.writerows(rows)
    print('  -> data/%s  %d행' % (fn, len(rows)))


def rd(fn):
    return list(csv.DictReader(open(os.path.join(C8, fn), encoding='utf-8')))


def chk(name, ok, detail=''):
    print('  %-58s %s %s' % (name, '일치' if ok else '불일치', detail))
    if not ok:
        FAIL.append(name)


def short(s):
    return s.split('(')[0].strip()


for ch in (4, 10, 11):
    print('제1권 %d장 원고 sha256 %s  표 %d개' % (ch, V.ms_sha(ch)[:16], V.table(ch, 1)['n_tables']))

# ------------------------------------------------------------ 사례 1: 11장 표 4, 표 6
print('\n[사례 1] 제1권 11장 표 4(Cui 등 2013 표 1의 재구성), 표 6(Fisher 시연)')
t = V.table(11, 4)
rows = []
for r in t['rows']:
    n, c = int(V.num(r[3])), [int(V.num(x)) for x in r[4:9]]
    rows.append([short(r[0]), n] + c)
    chk('행의 합 = 시료 수: %s' % short(r[0]), sum(c) == n, '(%d = %d)' % (sum(c), n))
w('cui2013-table1-v1.csv', ['site', 'n', 'N1x', 'N1c', 'C', 'O3a', 'O3a3c'], rows)
t6 = V.table(11, 6)
w('vol1-table11-6.csv', ['comparison', 'table', 'p_two', 'OR'], [[r[0], r[1], r[2], r[3]] for r in t6['rows']])

# ------------------------------------------------------------ 사례 2: 4장 표 5와 계산 4-6 상자
print('\n[사례 2] 제1권 4장 표 5(울릉도 테프라층 연대)와 계산 4-6 상자의 14C 날짜')
t5 = V.table(4, 5)
lay = []
for r in t5['rows']:
    m = re.search(r'([\d,]+)∼([\d,]+)\(([^)]*)\)', r[2])
    hi, lo = (int(x.replace(',', '')) for x in m.groups()[:2])
    lay.append([r[0].split('(')[0].strip(), r[1], lo, hi, m.group(3)])
w('ulleung-layers-v1.csv', ['layer', 'okuno_adopted_text', 'mclean_lo_calBP', 'mclean_hi_calBP', 'mclean_code'], lay)
for l in lay:
    print('    %-4s 오쿠노 채택: %-40s McLean %d~%d (%s)' % (l[0], l[1], l[2], l[3], l[4]))
need = ['(4910, 4965, 4945, 4940 BP, 모두 ±35)', '4710 ± 30', '7525 ± 35, 8030 ± 35',
        '12,165 ± 40, 11,840 ± 45, 12,030 ± 40, 12,090 ± 40, 12,095 ± 40', '9785 ± 35']
for s in need:
    chk('계산 4-6 상자·4.4절에 문자열 있음: %s' % s, V.has(4, s))
DATES = [  # 층, 14C 나이(BP), 1시그마, 출처
    ('U-2', 4910, 35, '계산 4-6 예 1'), ('U-2', 4965, 35, '계산 4-6 예 1'), ('U-2', 4945, 35, '계산 4-6 예 1'), ('U-2', 4940, 35, '계산 4-6 예 1'),
    ('U-2', 4710, 30, '계산 4-6 예 2(같은 층이라 가정한 날짜)'),
    ('U-3', 7525, 35, '계산 4-6 예 3'), ('U-3', 8030, 35, '계산 4-6 예 3'),
    ('U-4', 12165, 40, '계산 4-6 예 4'), ('U-4', 11840, 45, '계산 4-6 예 4'), ('U-4', 12030, 40, '계산 4-6 예 4'),
    ('U-4', 12090, 40, '계산 4-6 예 4'), ('U-4', 12095, 40, '계산 4-6 예 4'), ('U-4', 9785, 35, '4.4절, 계산 4-6 예 7'),
]
w('okuno2010-dates-v1.csv', ['layer', 'c14_BP', 'sigma', 'source'], DATES)

# ------------------------------------------------------------ 사례 3: 10장 표 4, 5, 6, 10
print('\n[사례 3] 제1권 10장 표 4(Brune), 표 5와 6(유사 수지), 표 10(CIA)')
t4 = V.table(10, 4)
b = []
for r in t4['rows']:
    b.append([r[0], V.num(r[1]), V.num(r[2]), V.num(r[3]), V.num(r[4]), V.num(r[5]), V.num(r[6])])
w('hu2009-table4-v1.csv', ['name', 'V_km3', 'Q_km3yr', 'VQ_table', 'VQ_calc_vol1', 'TE_table_pct', 'TE_calc_vol1_pct'], b)
c8 = rd('hu2009-table4.csv')
chk('표 4의 V, Q, V/Q(표), TE(표)가 8장 CSV와 같음',
    all(abs(x[1] - float(y['V_km3'])) < 1e-9 and abs(x[2] - float(y['Q_km3yr'])) < 1e-9 and abs(x[3] - float(y['VQ_table'])) < 1e-9 and abs(x[5] - float(y['TE_table_pct'])) < 1e-9 for x, y in zip(b, c8)) and len(b) == len(c8) == 8)
t5b, t6b = V.table(10, 5), V.table(10, 6)
bud = []
for r in t5b['rows']:
    bud.append(['D1', r[0]] + [V.num(x) for x in r[1:]])
for r in t6b['rows']:
    bud.append(['D2', r[0]] + [V.num(x) for x in r[1:]])
w('hu2009-budget-v1.csv', ['segment', 'period', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7'],
  [x + [''] * (9 - len(x)) for x in bud])
h8 = rd('hu2009-table3.csv')
ok1 = all(abs(V.num(r[1]) - float(h['JS'])) + abs(V.num(r[2]) - float(h['MJ'])) + abs(V.num(r[3]) - float(h['JL'])) + abs(V.num(r[4]) - float(h['U1'])) + abs(V.num(r[5]) - float(h['CT'])) + abs(V.num(r[6]) - float(h['D1'])) < 1e-9 for r, h in zip(t5b['rows'], h8))
ok2 = all(abs(V.num(r[1]) - float(h['CT'])) + abs(V.num(r[2]) - float(h['WJ'])) + abs(V.num(r[3]) - float(h['U2'])) + abs(V.num(r[4]) - float(h['YC'])) + abs(V.num(r[5]) - float(h['D2'])) < 1e-9 for r, h in zip(t6b['rows'], h8))
chk('표 5(촌탄-병산)가 8장 CSV의 JS, MJ, JL, U1, CT, D1과 같음', ok1)
chk('표 6(의창-촌탄)이 8장 CSV의 CT, WJ, U2, YC, D2와 같음', ok2)
t10 = V.table(10, 10)
cia = []
for r in t10['rows']:
    cia.append([r[1]] + [V.num(x) for x in r[2:11]])
w('he2015-table2-v1.csv', ['sample', 'Al2O3', 'CaO', 'Na2O', 'K2O', 'P2O5', 'SiO2', 'CIA_table', 'CIA_calc_vol1', 'diff_vol1'], cia)
h2 = rd('he2015-table2.csv')
ok = len(cia) == len(h2) == 30 and all(
    x[0].replace(' ', '') == y['sample'] and all(abs(x[i + 1] - float(y[k])) < 1e-9 for i, k in enumerate(['Al2O3', 'CaO', 'Na2O', 'K2O', 'P2O5', 'SiO2'])) and abs(x[7] - float(y['CIA_table'])) < 1e-9
    for x, y in zip(cia, h2))
chk('표 10의 시료명(공백 뺀 이름), 6개 산화물, CIA(표)가 8장 CSV와 같음', ok, '(30행)')
print('\n입력 대조 실패 %d건%s' % (len(FAIL), (': ' + '; '.join(FAIL)) if FAIL else ''))
sys.exit(1 if FAIL else 0)
