# -*- coding: utf-8 -*-
"""실습 2-7: 열이 흩어진 표 글자열을 산술로 다시 짝짓고(재구성), 점검 함수로 걸러 본다.
입력 1: 제1권 DB papers.fulltext(논문 PDF에서 뽑은 글자열)의 표 2(Yang 등, 2025, DOI 10.3389/fmars.2024.1490990)가 있던 부분.
        이 글자열을 만든 추출 도구는 DB에서 확인하지 못했다.
입력 2: 정답으로 제1권 ms/ch09-calc-v1.py의 값(제1권이 이 표를 옮겨 적은 것).
실행: python3 07-scatter-repair.py | tee 07-scatter-repair.log"""
import itertools, re, sqlite3, json
import tablecheck as tc

db = sqlite3.connect('file:/home/claude/book/db/ktv1bookdb-v14.sqlite?mode=ro', uri=True)
t = db.execute("SELECT fulltext FROM papers WHERE doi='10.3389/fmars.2024.1490990'").fetchone()[0]
i = t.find('TABLE 2 The Coastline')
lines = [l.strip() for l in t[i:].splitlines() if l.strip()]
NUM = re.compile(r'^[-+]?\d[\d.,]*%?$|^[–-]$')
# 표 부분: 캡션 다음부터 '[p.7]' 앞의 본문 문장이 시작하기 전까지의 숫자·머리글 줄
stream = []
for l in lines[1:201]:
    stream.append(l)
tok = [l for l in stream if NUM.match(l)]
dash = sum(1 for l in tok if l in '–-')
km = [float(l) for l in tok if re.fullmatch(r'\d+\.\d+', l)]                  # 단위 없는 소수
pc = [float(l.rstrip('%')) for l in tok if l.endswith('%')]                    # 퍼센트 칸
yr = [int(l) for l in tok if re.fullmatch(r'(19|20)\d\d', l)]
print('글자열(표 2 쪽): 줄 %d, 숫자 줄 %d (km 꼴 %d, %% 꼴 %d, 연도 꼴 %d, 줄표 %d)' % (len(stream), len(tok), len(km), len(pc), len(yr), dash))
print('글자열에 나온 연도 줄:', yr)
print('글자열 앞쪽 12개 숫자 줄:', tok[:12])

# 정답: 제1권 ch09-calc의 배열
src = open('/home/claude/book/ms/ch09-calc-v1.py', encoding='utf-8').read()
def arr(name):
    m = re.search(r'^%s = \[(.*?)\]' % name, src, re.M)
    return [None if x.strip() == 'None' else float(x) for x in m.group(1).split(',')]
Y = [int(x) for x in arr('Y')]
AC, NC, TOT, ACP, NCP = arr('AC'), arr('NC'), arr('TOT'), arr('ACP'), arr('NCP')
print('\n정답(제1권): 연도 %d개, 합계 17개 중 글자열에 있는 값: %d개' % (len(Y), sum(1 for v in TOT if v in km)))
print('정답의 AC %d개 중 글자열에 있는 값 %d, NC %d개 중 %d, AC%% %d개 중 %d, NC%% %d개 중 %d' % (
    len(AC), sum(v in km for v in AC), len(NC), sum(v in km for v in NC), len(ACP), sum(v in pc for v in ACP), len(NCP), sum(v in pc for v in NCP)))

print('\n== 1. 글자열 순서대로 접어 읽기(열이 흩어졌다는 것을 보임)')
# km 숫자를 읽힌 순서대로 (AC, NC, 합계) 세 칸씩 접어 행을 만든다
rows = [list(km[k:k + 3]) for k in range(0, len(km) - 2, 3)]
ok, n, bad = tc.row_sum(rows, [0, 1], 2, 0.02)
print('  km 숫자 %d개를 3개씩 접은 %d행에서 AC + NC = 합계가 성립하는 행: %d / %d' % (len(km), len(rows), ok, n))

print('\n== 2. 제약으로 다시 짝짓기: AC + NC = 합계(+-0.02), AC%% = 100 AC / 합계(+-0.01), NC%% 도 마찬가지')
pcs = set(pc)
kms = sorted(set(km))
pos = {}
for k_, l in enumerate(tok):                      # 글자열에서 처음 나온 위치(표의 행 순서를 짐작하는 데 쓴다)
    if re.fullmatch(r'\d+\.\d+', l):
        pos.setdefault(float(l), k_)
sol = set()
for T in kms:
    for a in kms:
        if a >= T:
            continue
        for b in kms:
            if b < a or b >= T or abs(a + b - T) > 0.020001:
                continue
            pa, pn = 100 * a / T, 100 * b / T
            if any(abs(pa - p) <= 0.0101 for p in pcs) and any(abs(pn - p) <= 0.0101 for p in pcs):
                sol.add((T, a, b))              # a <= b 로 세워 순서를 따지지 않은 짝
sol = sorted(sol, key=lambda s: pos[s[0]])
print('  조건을 모두 만족하는 (합계, 작은 쪽, 큰 쪽) 조합: %d개' % len(sol))
print('  합계 값이 겹치는 조합: %d개' % (len(sol) - len({s[0] for s in sol})))
hit = 0; miss = []
for y, a, n_, t_ in zip(Y, AC, NC, TOT):
    lo, hi = sorted((a, n_))
    if any(s[0] == t_ and abs(s[1] - lo) < 0.005 and abs(s[2] - hi) < 0.005 for s in sol):
        hit += 1
    else:
        miss.append(y)
print('  제1권이 옮긴 17개 행 가운데 (합계, 작은 쪽, 큰 쪽)이 조합에 그대로 있는 행: %d / 17 %s' % (hit, ('못 찾은 연도 ' + str(miss)) if miss else ''))
truth = {(t_, min(a, n_), max(a, n_)) for a, n_, t_ in zip(AC, NC, TOT)}
extra = [s for s in sol if s not in truth]
print('  제1권 17개 행에 해당하지 않는 조합(거짓 짝 후보): %d개 %s' % (len(extra), extra[:4]))
print('  글자열 속의 위치 순서로 세운 합계 열의 앞 6개: %s (제1권 표의 앞 6개: %s)' % ([s[0] for s in sol][:6], TOT[:6]))
print('  위 순서가 제1권 연도 순서와 같은가:', [s[0] for s in sol] == TOT)

print('\n== 2b. 그래도 남는 모호함: 어느 쪽이 AC이고 어느 쪽이 NC인가')
print('  행 합(AC + NC)과 합계 사이의 점검은 두 칸을 서로 바꾸어도 똑같이 통과한다. 17행이면 방향의 경우의 수는 2^17 = %d가지.' % 2 ** 17)
# 이웃 연도 사이의 변화 강도(퍼센트 칸에 있는 값)로 방향을 잇는다: LCI = 100 (L_i - L_j) / (L_j (i - j))
rows = [(s[0], s[1], s[2]) for s in sol]
def lci_ok(x, y, dy):
    v = 100 * (y - x) / (x * dy)
    return any(abs(v - p) <= 0.0101 for p in pcs)
# 동적 계획: 행 k의 방향 o(0: 작은 쪽이 AC, 1: 큰 쪽이 AC)
NEG = -1
score = [[0, 0]]
back = [[None, None]]
for k in range(1, len(rows)):
    dy = Y[k] - Y[k - 1]
    sc, bk = [], []
    for o in (0, 1):
        best, arg = -1, None
        for o0 in (0, 1):
            ac0, nc0 = (rows[k - 1][1], rows[k - 1][2]) if o0 == 0 else (rows[k - 1][2], rows[k - 1][1])
            ac1, nc1 = (rows[k][1], rows[k][2]) if o == 0 else (rows[k][2], rows[k][1])
            m = int(lci_ok(ac0, ac1, dy)) + int(lci_ok(nc0, nc1, dy))
            if score[k - 1][o0] + m > best:
                best, arg = score[k - 1][o0] + m, o0
        sc.append(best); bk.append(arg)
    score.append(sc); back.append(bk)
o = 0 if score[-1][0] >= score[-1][1] else 1
orient = [o]
for k in range(len(rows) - 1, 0, -1):
    o = back[k][o]; orient.append(o)
orient = orient[::-1]
tie = score[-1][0] == score[-1][1]
print('  이웃한 두 연도의 변화 강도(AC와 NC 둘 다)가 퍼센트 칸에 있는 값과 맞는 쌍의 수를 최대로 하는 방향을 골랐다.')
print('  최고 점수 %d (가능한 최대 %d = 16쌍 x 2). 마지막 행의 두 방향 점수가 같은가(= 전체를 뒤집어도 점수가 같은가): %s' % (max(score[-1]), 32, tie))
def build(orient):
    return [(r[1], r[2]) if o_ == 0 else (r[2], r[1]) for r, o_ in zip(rows, orient)]
def same(g):
    return sum(1 for (a, n_), ta, tn in zip(g, AC, NC) if abs(a - ta) < 0.005 and abs(n_ - tn) < 0.005)
g1, g2 = build(orient), build([1 - o_ for o_ in orient])
print('  방향 사슬이 정한 두 가지 전체 방향(서로 정반대)과 제1권 표의 일치 행 수: %d / 17, %d / 17' % (same(g1), same(g2)))
# 남은 하나의 선택은 본문의 서술로 정한다: "artificial coastlines expanded from 80.19 km to 320.06 km"
m = re.search(r'length\s+of\s+arti.{1,2}cial\s+coastlines\s+expanded\s+from\s+([\d.]+)\s+km\s+to\s+([\d.]+)\s+km', t)
anc = (float(m.group(1)), float(m.group(2))) if m else None
print('  본문 서술에서 읽은 기준값(1984년 AC, 2000년 AC):', anc)
def fits(g):
    return anc is not None and abs(g[0][0] - anc[0]) < 0.005 and abs(g[7][0] - anc[1]) < 0.005
pick = g1 if fits(g1) else g2 if fits(g2) else None
okrow = same(pick) if pick else -1
print('  기준값에 맞는 방향을 고르면 제1권 표와 같은 행: %s / 17' % okrow)

print('\n== 3. 점검 함수가 흩어진 표를 걸러내는가')
good = [[a, n_, t_, p] for a, n_, t_, p in zip(AC, NC, TOT, ACP)]
print('  제1권의 표(정답): 행합 %s, 비율 %s' % (tc.row_sum(good, [0, 1], 2, 0.02)[:2], tc.ratio(good, 0, 2, 3, 0.01)[:2]))
sh = [r[:] for r in good]
for k in range(len(sh)):                       # NC 열을 한 행씩 밀어 넣은 표(열이 한 칸 어긋난 경우)
    sh[k][1] = good[(k + 1) % len(good)][1]
print('  NC 열을 한 행 밀면: 행합 %s, 비율 %s' % (tc.row_sum(sh, [0, 1], 2, 0.02)[:2], tc.ratio(sh, 0, 2, 3, 0.01)[:2]))
sw = [r[:] for r in good]
sw[5][0], sw[5][1] = sw[5][1], sw[5][0]        # 한 행에서 AC와 NC가 서로 바뀐 표
print('  한 행에서 AC와 NC가 바뀌면: 행합 %s(합은 그대로), 비율 %s 실패 행 %s' % (tc.row_sum(sw, [0, 1], 2, 0.02)[:2], tc.ratio(sw, 0, 2, 3, 0.01)[:2], tc.ratio(sw, 0, 2, 3, 0.01)[2]))
print('  값 범위: 비율 열 [0, 100] 밖: %s, 합계 열 [200, 500] 밖: %s' % (tc.in_range(good, 3, 0, 100), tc.in_range(good, 2, 200, 500)))
ac100 = [r[:] for r in good]; ac100[3][3] = '540.0'      # 쉼표나 소수점이 어긋난 값
print('  비율 54.00 -> 540.0 으로 어긋난 표: 값 범위 위반 %s, 비율 실패 행 %s' % (tc.in_range(ac100, 3, 0, 100), tc.ratio(ac100, 0, 2, 3, 0.01)[2]))
json.dump(dict(n_tokens=len(tok), km=len(km), pc=len(pc), solutions=len(sol), hit=hit, orient_ok=okrow), open('out/scatter-result.json', 'w'))

print('\n== 4. 합 점검의 허용 오차')
print('  세 값(AC, NC, 합계)이 모두 소수 둘째 자리로 반올림되었다면 AC + NC - 합계는 0.015를 넘을 수 없다.')
ok15, n15, bad15 = tc.row_sum(good, [0, 1], 2, 0.015)
print('  허용 오차 0.015로 제1권 표 17행을 점검: 통과 %d / %d, 넘는 행: %s' % (ok15, n15, [(Y[k], round(AC[k] + NC[k] - TOT[k], 3)) for k in bad15]))
print('  글자열에도 같은 세 값이 있는가(1986년 행):', all(v in km for v in (AC[1], NC[1], TOT[1])), '(합계 %.2f, AC %.2f, NC %.2f)' % (TOT[1], AC[1], NC[1]))
