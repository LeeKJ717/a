# -*- coding: utf-8 -*-
"""실습 8-1: 제1권 계산 스크립트에서 입력 표를 그대로 뽑아 CSV로 저장한다(손으로 다시 옮기지 않기 위해).
읽는 파일: /home/claude/book/ms/ch10-calc-v1.py, ch08-calc-v1.py (읽기만 하고 고치지 않는다.)
방법: 파이썬의 ast로 소스를 파싱해 대입문의 리터럴 값을 꺼낸다. 소스를 실행하지 않는다."""
import ast, csv, hashlib, os
V1 = '/home/claude/book/ms'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'data')
os.makedirs(OUT, exist_ok=True)

def load(name):
    p = os.path.join(V1, name)
    b = open(p, 'rb').read()
    print('%s  sha256 %s  %d바이트' % (name, hashlib.sha256(b).hexdigest()[:16], len(b)))
    return ast.parse(b.decode('utf-8'))

def assigns(tree):
    d = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            d[n.targets[0].id] = n.value
    return d

def lit(node):
    return ast.literal_eval(node)

t10 = load('ch10-calc-v1.py'); a10 = assigns(t10)
t08 = load('ch08-calc-v1.py'); a08 = assigns(t08)

def w(fn, head, rows):
    with open(os.path.join(OUT, fn), 'w', encoding='utf-8', newline='') as f:
        cw = csv.writer(f); cw.writerow(head); cw.writerows(rows)
    print('  ->', fn, len(rows), '행')

# 1) Hu 등(2009) 표 4: Brune
Q, V, DT, TE, NM = (lit(a10[k]) for k in ('Q', 'V', 'DT_T', 'TE_T', 'NM'))
w('hu2009-table4.csv', ['name', 'V_km3', 'Q_km3yr', 'VQ_table', 'TE_table_pct'], [(NM[i], V[i], Q[i], DT[i], TE[i]) for i in range(8)])

# 2) Hu 등(2009) 표 3: 유사 수지(Mt/yr)
lab = lit(a10['lab'])
cols = ['JS', 'MJ', 'JL', 'WJ', 'CT', 'YC', 'U1', 'U2', 'U3', 'D1', 'D2', 'D3']
data = {c: lit(a10[c]) for c in cols}
w('hu2009-table3.csv', ['period'] + cols, [[lab[i]] + [data[c][i] for c in cols] for i in range(8)])

# 3) Hu 등(2009) 표 1: 지점별 면적·유량·유사(계산 10-5의 st 리스트는 for 안의 리터럴이어서 소스 문자열에서 꺼낸다)
for n in ast.walk(t10):
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'st' and isinstance(n.value, ast.List) and len(n.value.elts) == 7:
        st = lit(n.value)
w('hu2009-table1.csv', ['station', 'area_1e4km2', 'Q_km3yr', 'S_Mtyr'], st)

# 4) He 등(2015) 표 2(산화물 11열) — 시료 이름은 nm
nm = lit(a10['nm'])
rows_node = None
for n in ast.walk(t10):
    if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.count('|') == 300:
        rows_node = n.value
he = [r.split('|') for r in rows_node.split('\n')]
assert len(he) == 30 and all(len(r) == 11 for r in he)
w('he2015-table2.csv', ['sample', 'Al2O3', 'CaO', 'Fe', 'K2O', 'Mg', 'Mn', 'Na2O', 'P2O5', 'Ti', 'SiO2', 'CIA_table'], [[nm[i]] + he[i] for i in range(30)])

# 5) He 등(2015) 표 6: Nd
T6 = None
for n in ast.walk(t10):
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'T6':
        T6 = lit(n.value)
w('he2015-table6.csv', ['sample', 'Nd143_144', 'eNd_table'], T6)

# 6) Dou 등(2021) 끝 성분과 코어 값(제1권 8장)
JA = lit(a08['JA']); GB = lit(a08['GB'])
w('dou2021-endmembers.csv', ['name', 'eNd', 'Sr87_86'], [('JA', JA[0], JA[1]), ('GB', GB[0], GB[1])])
print('Dou 코어 값은 계산 8-11, 8-12 의 입력으로 소스에 직접 쓰인 숫자들이다(CSV로 옮기지 않고 03-mixing 스크립트에 적었다)')
