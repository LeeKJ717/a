# -*- coding: utf-8 -*-
"""사례 1: 서요하 아버지 계통, 신석기와 청동기가 다른가 (제1권 11장 11.3.3~11.3.4절).
입력 표(제1권 11장 표 4) -> 2x2 표 만들기 -> Fisher 정확검정(5장 fisher-scratch의 함수) -> 순열 검정(5장 permutation-basic의 함수와
이 장에서 일반화한 함수) -> 유전자 다양도의 부트스트랩(5장 bootstrap-basic의 함수) -> 제1권 값과 대조 -> 입력을 바꿔 보기.
앞 장의 파일은 고치지도 실행하지도 않고 함수 정의만 꺼내 쓴다(loadfuncs.py).
실행: python3 case1-seoyohe.py > case1.log   (같은 폴더에서. 먼저 00-extract-inputs.py를 한 번 실행해 data/를 만든다)
난수 시드는 모두 코드에 고정했다. 로그에는 시간을 적지 않는다(두 번 돌려 같은 로그인지 보려고). 시간은 runall.sh가 timing.log에 적는다."""
import csv, json, math, os, platform, subprocess, sys
from fractions import Fraction
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np, scipy
from scipy import stats
from scipy.stats.contingency import odds_ratio
import v1tables as V
from loadfuncs import load_funcs

CH5 = os.path.join(HERE, '..', 'ch05')
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
FS, sha_f = load_funcs(os.path.join(CH5, 'fisher-scratch.py'), ['counts', 'fisher_exact_scratch'], env={'comb': comb, 'Fraction': Fraction})
NEI, sha_b = load_funcs(os.path.join(CH5, 'bootstrap-basic.py'), ['nei', 'nei_vec'], env={'np': np})
print('앞 장에서 꺼낸 함수: ch05/fisher-scratch.py(sha256 %s) counts, fisher_exact_scratch / ch05/bootstrap-basic.py(sha256 %s) nei, nei_vec' % (sha_f, sha_b))
nei, nei_vec = NEI['nei'], NEI['nei_vec']
OUT = {}
SUM = []   # 요약표: (항목, 제1권 값, 이번 값, 일치 여부)


def same(mine, printed):
    """제1권이 적은 문자열의 소수 자릿수로 반올림해 같은지."""
    nd = len(printed.split('.')[1]) if '.' in printed else 0
    return round(mine, nd) == float(printed)


def add(item, v1, mine, ok):
    SUM.append((item, v1, mine, ok))


# ------------------------------------------------------------------ 1. 입력
print('\n== 1. 입력: 제1권 11장 표 4 (data/cui2013-table1-v1.csv)')
rows = list(csv.DictReader(open(os.path.join(HERE, 'data', 'cui2013-table1-v1.csv'), encoding='utf-8')))
S = {r['site']: dict(n=int(r['n']), c=[int(r[k]) for k in ('N1x', 'N1c', 'C', 'O3a', 'O3a3c')]) for r in rows}
print('%-8s %3s %6s %5s %4s %5s %7s' % ('유적', '시료', 'N1(x)', 'N1c', 'C', 'O3a', 'O3a3c'))
for k, v in S.items():
    print('%-8s %3d %6d %5d %4d %5d %7d' % (k, v['n'], *v['c']))
# 제1권 계산 11-2의 묶음 규칙: 신석기 = 우하량 + 합라해구, 청동기 = 대전자 + 대산전. 비교하는 형은 N1(x)
neo = (S['우하량']['c'][0] + S['합라해구']['c'][0], S['우하량']['n'] + S['합라해구']['n'])
dad = (S['대전자']['c'][0], S['대전자']['n'])
dsh = (S['대산전']['c'][0], S['대산전']['n'])
bro = (dad[0] + dsh[0], dad[1] + dsh[1])
print('\n묶음 규칙(제1권 계산 11-2): 신석기 = 우하량 + 합라해구 = N1(x) %d/%d, 청동기 = 대전자 + 대산전 = N1(x) %d/%d' % (*neo, *bro))


def tab(g1, g2):
    return [[g1[0], g1[1] - g1[0]], [g2[0], g2[1] - g2[0]]]


TESTS = [('신석기 대 청동기(대전자 + 대산전)', tab(neo, bro)), ('신석기 대 대전자(하가점하층)', tab(neo, dad)), ('신석기 대 대산전(하가점상층)', tab(neo, dsh))]
t6 = list(csv.DictReader(open(os.path.join(HERE, 'data', 'vol1-table11-6.csv'), encoding='utf-8')))
for (nm, t), r in zip(TESTS, t6):
    printed = r['table'].replace(' ', '')
    mine = str(t).replace(' ', '')
    print('  %-34s 만든 표 %-22s 제1권 표 11-6의 표 %-22s %s' % (nm, str(t), r['table'], '일치' if printed == mine else '불일치'))
    add('표 11-6의 2x2 표: ' + nm, r['table'], str(t), printed == mine)

# ------------------------------------------------------------------ 2. Fisher 정확검정
print('\n== 2. Fisher 정확검정 (정수 계산 fisher_exact_scratch, scipy와 대조)')
v1out = subprocess.run([sys.executable, '-I', os.path.join(V.V1, 'ch11-calc-v1.py')], capture_output=True, text=True, cwd='/tmp', timeout=300).stdout
print('제1권 계산 스크립트 ch11-calc-v1.py 출력 %d줄, 원고 ch11-v1.md sha256 %s' % (v1out.count('\n'), V.ms_sha(11)[:16]))
import re
R2 = {}
print('%-34s %-16s %12s %12s %12s %8s %8s | %s' % ('비교', '표', '양쪽 p', '한쪽 p', 'scipy 양쪽', '표본 OR', '', '제1권 표 11-6(p, OR) / 제1권 스크립트의 p'))
for (nm, t), r in zip(TESTS, t6):
    (a, b), (c, d) = t
    p2 = FS['fisher_exact_scratch'](a, b, c, d)
    p1 = FS['fisher_exact_scratch'](a, b, c, d, 'greater')
    sp = stats.fisher_exact(t)
    orr = (a * d) / (b * c)
    m = re.search(re.escape('[[%d,%d],[%d,%d]]' % (a, b, c, d)) + r'\s+이 책 p = ([\d.]+)', v1out)
    pv1 = m.group(1) if m else None
    okp, oko = same(p2, r['p_two']), same(orr, r['OR'])
    print('%-34s %-16s %12.6e %12.6e %12.6e %8.3f | 표 %s, %s  %s / 스크립트 %s %s' % (nm, str(t), p2, p1, sp.pvalue, orr, r['p_two'], r['OR'], '일치' if okp and oko else '불일치', pv1, '일치' if pv1 and same(p2, pv1) else '불일치'))
    add('Fisher 양쪽 p, ' + nm, r['p_two'], '%.6g' % p2, okp)
    add('표본 오즈비, ' + nm, r['OR'], '%.3f' % orr, oko)
    cm = odds_ratio(t, kind='conditional'); ci = cm.confidence_interval(0.95)
    R2[nm] = dict(table=t, p_two=p2, p_one=p1, scipy_p=float(sp.pvalue), OR=orr, cmle=float(cm.statistic), ci=[float(ci.low), float(ci.high)])
    print('    조건부 최대가능도 오즈비 %.3f, 95%% 구간 %.3f ~ %.3f (표본 오즈비 %.1f와 다르다)  한쪽 p의 2배 %.6e  양쪽 p와 scipy의 차 %.1e' % (cm.statistic, ci.low, ci.high, orr, 2 * p1, abs(p2 - sp.pvalue)))
chi = stats.chi2_contingency(TESTS[0][1], correction=False)
print('같은 첫 표의 카이제곱(보정 없음) = %.3f, p = %.5f, 기대도수 최소 %.2f' % (chi[0], chi[1], chi[3].min()))
add('카이제곱(보정 없음) 첫 표', '12.224, p = 0.00047, 기대도수 최소 5.25', '%.3f, p = %.5f, %.2f' % (chi[0], chi[1], chi[3].min()), V.has(11, '12.224, p = 0.00047') and V.has(11, '5.25') and same(chi[0], '12.224') and same(chi[1], '0.00047') and same(chi[3].min(), '5.25'))
ways, tot = FS['counts'](16, 2, 4, 10)
exact_one = sum(w for x, w in ways.items() if x >= 16) / tot
print('첫 표의 경우의 수: 전체 C(32,20) = %s, 관측 a=16은 %s, 한쪽 p = %.6e' % ('{:,}'.format(tot), '{:,}'.format(ways[16]), exact_one))
add('한쪽 p(신석기가 더 큼) 첫 표', '7.08e-4', '%.3e' % exact_one, V.has(11, '7.08 × 10⁻⁴') and same(exact_one * 1e4, '7.08'))
OUT['fisher'] = R2
OUT['pmf1'] = {str(x): w / tot for x, w in ways.items()}

# ------------------------------------------------------------------ 3. 순열 검정
print('\n== 3. 순열 검정: 이름표를 섞어 Fisher 값을 되찾는다')
lab1 = np.array([1] * 20 + [0] * 12)
PC, sha_p = load_funcs(os.path.join(CH5, 'permutation-basic.py'), ['perm_counts'], env={'np': np, 'lab': lab1, 'obs_a': 16})
print('앞 장에서 꺼낸 함수: ch05/permutation-basic.py(sha256 %s) perm_counts (표 [[16,2],[4,10]] 전용: 32명, 집단 1은 18명, 관측 16)' % sha_p)


def perm_gen(t, B, seed, chunk=200000):
    """일반화한 순열 검정(이 장의 새 코드). 2x2 표 t에서 집단 1의 이름표를 섞어 왼쪽 위 칸 a의 분포를 센다.
    난수를 쓰는 방식은 perm_counts와 같다(같은 모양의 난수 행렬, argpartition). 반환: a가 나온 횟수의 길이 N+1 배열."""
    (a, b), (c, d) = t
    n1, N, K = a + b, a + b + c + d, a + c
    lab = np.array([1] * K + [0] * (N - K))
    rng = np.random.default_rng(seed)
    freq = np.zeros(N + 1, dtype=np.int64)
    left = B
    while left > 0:
        m = min(chunk, left)
        idx = np.argpartition(rng.random((m, N)), n1, axis=1)[:, :n1]
        freq += np.bincount(lab[idx].sum(axis=1), minlength=N + 1)
        left -= m
    return freq


f1 = perm_gen(TESTS[0][1], 100000, 5000)
ge_gen = int(f1[16:].sum())
ge_old = PC['perm_counts'](100000, 5000)
print('새 함수 대 앞 장 함수(표 1, B = 100,000, 시드 5000): a >= 16인 횟수 %d 대 %d  %s' % (ge_gen, ge_old, '같다' if ge_gen == ge_old else '다르다'))
add('순열 함수 일반화가 앞 장 함수와 같은 횟수를 냄', 'perm_counts = %d' % ge_old, 'perm_gen = %d' % ge_gen, ge_gen == ge_old)
B = 1000000
SEED = 20261026
P3 = {}
print('B = %s, 시드 %d. p(한쪽) = (b+1)/(B+1), b = a가 관측 이상인 횟수. 양쪽은 확률이 관측 표 이하인 a의 합(Fisher와 같은 순서)으로 센다.' % ('{:,}'.format(B), SEED))
print('%-34s %10s %12s %12s | %12s %12s' % ('비교', 'b(한쪽)', 'p 한쪽', 'p 양쪽', 'Fisher 한쪽', 'Fisher 양쪽'))
for i, (nm, t) in enumerate(TESTS):
    (a, b_), (c, d) = t
    fr = perm_gen(t, B, SEED + i)
    w2, tt = FS['counts'](a, b_, c, d)
    pm = {x: w / tt for x, w in w2.items()}
    bone = int(fr[a:].sum())
    # 양쪽: 정확한 확률이 관측 표의 확률 이하(상대 1e-9 허용)인 a에 나온 횟수
    bt = int(sum(fr[x] for x in pm if w2[x] <= w2[a]))
    p1h, p2h = (bone + 1) / (B + 1), (bt + 1) / (B + 1)
    P3[nm] = dict(B=B, seed=SEED + i, b_one=bone, b_two=bt, p_one=p1h, p_two=p2h, freq={str(x): int(fr[x]) for x in pm})
    print('%-34s %10d %12.4e %12.4e | %12.4e %12.4e' % (nm, bone, p1h, p2h, R2[nm]['p_one'], R2[nm]['p_two']))
OUT['perm'] = P3
# 시드를 바꿔 흔들림 재기: 첫 표, 시드 5개
ps = []
for s in range(5):
    fr = perm_gen(TESTS[0][1], B, 7000 + s)
    ps.append((int(fr[16:].sum()) + 1) / (B + 1))
print('첫 표, 시드 7000~7004, B = 100만의 한쪽 p: ' + ' '.join('%.3e' % p for p in ps) + '  (평균 %.3e, 표준편차 %.2e, 정확한 값 %.3e)' % (np.mean(ps), np.std(ps, ddof=1), exact_one))
print('B = 1,000에서는 가능한 가장 작은 p가 1/1001 = %.2e이므로 정확한 값 %.2e를 해상할 수 없다(5장 5.4.2절).' % (1 / 1001, exact_one))
OUT['perm_seeds'] = ps

# ------------------------------------------------------------------ 4. 부트스트랩
print('\n== 4. 유전자 다양도 H와 부트스트랩 구간')
GROUPS = [('신석기 합', [16, 1, 1]), ('대산전', [1, 3, 1, 2, 2]), ('대전자', [3, 2])]
print('입력: 신석기 합 = 우하량 [4,1,1] + 합라해구 [12] -> [16, 1, 1] (N1(x) 16, C 1, O3a 1), 대산전 = 표 4의 한 줄, 대전자 = 표 4의 한 줄')
chk1 = (S['우하량']['c'][0] + S['합라해구']['c'][0], S['우하량']['c'][2] + S['합라해구']['c'][2], S['우하량']['c'][3] + S['합라해구']['c'][3])
print('표 4에서 합친 값: N1(x) %d, C %d, O3a %d  %s' % (*chk1, '[16, 1, 1]과 같다' if chk1 == (16, 1, 1) else '다르다'))
add('신석기 합의 하플로그룹 수 [16,1,1]', '[16, 1, 1]', str(list(chk1)), chk1 == (16, 1, 1))
hv1 = {'신석기 합': '0.2157', '대산전': '0.8611', '대전자': '0.6000'}
for nm, c in GROUPS:
    h = nei(c)
    ok = V.has(11, '= ' + hv1[nm]) and same(h, hv1[nm])
    print('  %-8s H = %.4f (제1권 계산 11-4의 %s)  %s' % (nm, h, hv1[nm], '일치' if ok else '불일치'))
    add('관측 H, ' + nm, hv1[nm], '%.4f' % h, ok)
# 제1권과 같은 구현·같은 시드 11·2만 번, 세 집단을 같은 난수열로 차례로(앞 장의 boot_v1을 같은 방식으로)
rng = np.random.default_rng(11)
BT, sha_bt = load_funcs(os.path.join(CH5, 'bootstrap-basic.py'), ['boot_v1'], env={'np': np, 'math': math, 'rng': rng, 'nei': nei})
V1B = {'신석기 합': ('0.000', '0.209', '0.464'), '대산전': ('0.556', '0.778', '0.889'), '대전자': ('0.000', '0.600', '0.600')}
for s_ in ('0.000~0.464(중앙 0.209)', '0.556~0.889(중앙 0.778)', '대전자 0.000~0.600'):
    print('  제1권 원고에 "%s" 있음: %s' % (s_, V.has(11, s_)))
HB = {}
for nm, c in GROUPS:
    lo, md, hi = BT['boot_v1'](c, 20000)
    exp = V1B[nm]
    ok = same(lo, exp[0]) and same(md, exp[1]) and same(hi, exp[2])
    HB[nm] = dict(c=c, H=nei(c), q=[float(lo), float(md), float(hi)])
    print('  %-8s 부트스트랩(시드 11, 2만 번): 2.5%% %.3f 중앙 %.3f 97.5%% %.3f | 제1권 %s / %s / %s  %s' % (nm, lo, md, hi, *exp, '일치' if ok else '불일치'))
    add('부트스트랩 H 2.5~97.5% (중앙), ' + nm, '%s ~ %s (%s)' % (exp[0], exp[2], exp[1]), '%.3f ~ %.3f (%.3f)' % (lo, hi, md), ok)
# 한 번에 size=B로 뽑는 벡터 구현과 B를 100만으로 키운 값
print('\nB를 100만으로 키우면 (벡터 구현 nei_vec, 시드 12): 구간 끝이 얼마나 움직이는가')
for nm, c in GROUPS:
    n = sum(c)
    cnt = np.random.default_rng(12).multinomial(n, np.array(c) / n, size=1000000)
    hh = nei_vec(cnt)
    q = np.percentile(hh, [2.5, 50, 97.5])
    HB[nm]['q1m'] = [float(x) for x in q]
    HB[nm]['p_h0'] = float((hh < 1e-12).mean())
    print('  %-8s 2.5%% %.3f 중앙 %.3f 97.5%% %.3f   (2만 번 값 %.3f / %.3f / %.3f)   H = 0인 재표집 비율 %.4f' % (nm, *q, *HB[nm]['q'], HB[nm]['p_h0']))
print('  [16,1,1]에서 H = 0이 될 확률 (16/18)^18 = %.4f' % ((16 / 18) ** 18))
print('겹침 판정(제1권 판정: 신석기 합의 구간과 대산전의 구간은 겹치지 않는다, 대전자의 구간은 신석기 합과 겹친다):')
ov = lambda x, y: not (x[2] < y[0] or y[2] < x[0])
print('  신석기 합 %.3f~%.3f 대 대산전 %.3f~%.3f: %s' % (HB['신석기 합']['q'][0], HB['신석기 합']['q'][2], HB['대산전']['q'][0], HB['대산전']['q'][2], '겹침' if ov(HB['신석기 합']['q'], HB['대산전']['q']) else '겹치지 않음'))
print('  신석기 합 %.3f~%.3f 대 대전자 %.3f~%.3f: %s' % (HB['신석기 합']['q'][0], HB['신석기 합']['q'][2], HB['대전자']['q'][0], HB['대전자']['q'][2], '겹침' if ov(HB['신석기 합']['q'], HB['대전자']['q']) else '겹치지 않음'))
add('구간 판정: 신석기 합 대 대산전, 대전자', '겹치지 않음, 겹침(11.3.4절)', '%s, %s' % ('겹치지 않음' if not ov(HB['신석기 합']['q'], HB['대산전']['q']) else '겹침', '겹침' if ov(HB['신석기 합']['q'], HB['대전자']['q']) else '겹치지 않음'),
    (not ov(HB['신석기 합']['q'], HB['대산전']['q'])) and ov(HB['신석기 합']['q'], HB['대전자']['q']))
OUT['boot'] = HB

# ------------------------------------------------------------------ 5. 입력을 바꿔 보기
print('\n== 5. 독자가 입력을 바꿀 때: 같은 함수에 다른 표를 넣는다 (이 책의 시연이며 제1권의 계산이 아니다)')
mj = (S['묘자구']['c'][0], S['묘자구']['n'])
VAR = [
    ('제1권 규칙: 신석기 = 우하량 + 합라해구, 청동기 = 대전자 + 대산전', neo, bro),
    ('신석기에 묘자구(중원 신석기, N1(x) 3/3)를 더함', (neo[0] + mj[0], neo[1] + mj[1]), bro),
    ('신석기를 합라해구만으로', (S['합라해구']['c'][0], S['합라해구']['n']), bro),
    ('청동기를 대산전만으로(= 제1권 세 번째 표)', neo, dsh),
]
for nm, g1, g2 in VAR:
    t = tab(g1, g2)
    (a, b), (c, d) = t
    p2 = FS['fisher_exact_scratch'](a, b, c, d)
    orr = (a * d) / (b * c) if b * c else float('inf')
    print('  %-62s %-22s 양쪽 p = %.3e  표본 OR = %s' % (nm, str(t), p2, ('%.1f' % orr) if orr != float('inf') else '무한(빈 칸이 있음)'))
pvals = [R2[nm]['p_two'] for nm, _ in TESTS]
order = np.argsort(pvals)
holm = [None] * 3
runmax = 0.0
for rank, i in enumerate(order):
    adj = min(1.0, (3 - rank) * pvals[i])
    runmax = max(runmax, adj)
    holm[i] = runmax
print('세 검정을 한 묶음으로 볼 때의 Holm 보정 양쪽 p(이 책의 시연):')
for (nm, _), h in zip(TESTS, holm):
    print('  %-34s 보정 전 %.3e -> 보정 후 %.3e' % (nm, R2[nm]['p_two'], h))
OUT['holm'] = holm

print('\n== 6. 요약: 제1권 값과 이번 실행값')
for item, v1, mine, ok in SUM:
    print('  %-50s 제1권 %-34s 이번 %-30s %s' % (item, v1, mine, '일치' if ok else '불일치'))
print('비교 %d개, 일치 %d개, 불일치 %d개' % (len(SUM), sum(1 for x in SUM if x[3]), sum(1 for x in SUM if not x[3])))
OUT['summary'] = [dict(item=a, v1=b, mine=c, ok=bool(d)) for a, b, c, d in SUM]
json.dump(OUT, open(os.path.join(HERE, 'case1.json'), 'w'), ensure_ascii=False)
sys.exit(0 if all(x[3] for x in SUM) else 1)
