# -*- coding: utf-8 -*-
"""표 추출 오류를 하나씩 일부러 넣고 점검기의 표 점검(T1, T2)이 잡는지 센다. 무작위가 없다. 모든 경우를 센다.
바탕 표는 제1권 11장 표 1의 재구성(6행, 시료 열과 5개 형 열)이고 합계 줄은 위쪽의 열 합으로 만든 값이다.
오류의 종류는 이 책이 표 추출에서 생길 법하다고 생각해 정한 것이며, 실제 모델이 내는 오류의 분포가 아니다(시연값)."""
import importlib.util, itertools, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hc', os.path.join(HERE, 'halluccheck-v1.py'))
hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)

HEAD = ['유적', '시료', 'N1(x)', 'N1c', 'C 또는 C3e', 'O3a', 'O3a3c']
ROWS = [('우하량', [6, 4, 0, 1, 1, 0]), ('합라해구', [12, 12, 0, 0, 0, 0]), ('대전자', [5, 3, 0, 0, 2, 0]),
        ('대산전', [9, 1, 3, 1, 2, 2]), ('금구자', [12, 0, 0, 12, 0, 0]), ('묘자구', [3, 3, 0, 0, 0, 0])]
# 먼저 바탕 표가 점검을 통과하는지 본다
def render(rows, total=True):
    L = ['| ' + ' | '.join(HEAD) + ' |', '|' + '---|' * len(HEAD)]
    for nm, v in rows:
        L.append('| ' + nm + ' | ' + ' | '.join(str(x) for x in v) + ' |')
    if total:
        cols = [sum(r[1][j] for r in ROWS) for j in range(6)]          # 원래 표의 열 합(합계 줄은 오류가 없는 값)
        L.append('| 합계 | ' + ' | '.join(str(x) for x in cols) + ' |')
    return L

def detect(rows, total):
    st = {}
    F = hc.check_tables(render(rows, total), st)
    return sorted({x['code'] for x in F})

def copy(rows): return [(n, list(v)) for n, v in rows]

base_ok = {t: detect(ROWS, t) for t in (True, False)}
print('바탕 표(오류 없음)의 점검 결과: 합계 줄 있음 %s, 없음 %s' % (base_ok[True] or '지적 없음', base_ok[False] or '지적 없음'))
print()

cases = {}
# (1) 두 형 열을 통째로 맞바꿈(본문 6행만, 머리글과 합계 줄은 그대로)
c = []
for a, b in itertools.combinations(range(1, 6), 2):
    r = copy(ROWS)
    for _, v in r: v[a], v[b] = v[b], v[a]
    if r != ROWS: c.append(r)
cases['두 형 열의 값을 통째로 맞바꿈'] = c
# (2) 한 행 안의 두 형 칸을 맞바꿈
c = []
for i in range(6):
    for a, b in itertools.combinations(range(1, 6), 2):
        r = copy(ROWS); r[i][1][a], r[i][1][b] = r[i][1][b], r[i][1][a]
        if r != ROWS: c.append(r)
cases['한 행 안의 두 형 칸을 맞바꿈'] = c
# (3) 한 칸의 값에 1을 더함(시료 열 포함)
c = []
for i in range(6):
    for j in range(6):
        r = copy(ROWS); r[i][1][j] += 1; c.append(r)
cases['한 칸의 값이 1 커짐'] = c
# (4) 한 칸을 빠뜨리고 왼쪽으로 당김(행의 마지막 칸은 0으로 채움)
c = []
for i in range(6):
    for j in range(1, 5):
        r = copy(ROWS); v = r[i][1]; del v[j]; v.append(0)
        if r != ROWS: c.append(r)
cases['한 칸이 빠져 오른쪽 값이 왼쪽으로 당겨짐'] = c
# (5) 이웃한 두 행을 하나로 합침(이름은 앞 행, 값은 합)
c = []
for i in range(5):
    r = copy(ROWS); nv = [x + y for x, y in zip(r[i][1], r[i + 1][1])]; r[i] = (r[i][0], nv); del r[i + 1]; c.append(r)
cases['이웃한 두 행이 하나로 합쳐짐'] = c
# (6) 한 행을 통째로 빠뜨림
c = []
for i in range(6):
    r = copy(ROWS); del r[i]; c.append(r)
cases['한 행이 빠짐'] = c

print('%-34s %5s | %-26s | %-26s' % ('넣은 오류', '경우 수', '합계 줄이 있을 때(잡은 수)', '합계 줄이 없을 때(잡은 수)'))
for nm, lst in cases.items():
    res = {}
    for t in (True, False):
        hit = sum(1 for r in lst if detect(r, t))
        res[t] = hit
    print('%-34s %5d | %3d (%5.1f%%)%16s | %3d (%5.1f%%)' % (nm, len(lst), res[True], 100.0 * res[True] / len(lst), '', res[False], 100.0 * res[False] / len(lst)))
