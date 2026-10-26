# -*- coding: utf-8 -*-
"""사례 2: 울릉도 홀로세 화산재층의 연대는 합치하는가 (제1권 4장 4.4절, 계산 4-6, 4-7).
입력(제1권 4장 계산 4-6 상자의 14C 날짜 13개와 표 5의 McLean 등 구간) -> 날짜 묶음의 합치 시험(9장 tephralib)
-> 보정(3장 c14lib, 곡선 IntCal04/13/20) -> McLean 등의 구간과 대조 -> 순서 제약 연대 모형(9장 tephralib) -> 제1권 값과 대조.
앞 장의 모듈을 그대로 불러 쓴다(수정 없음). 이 장에서 새로 짠 것은 이 파일의 대조·요약 코드뿐이다.
실행: python3 case2-ulleung.py > case2.log   (먼저 00-extract-inputs.py를 한 번 실행해 data/를 만든다)
로그에 시간을 적지 않는다. 난수 시드는 코드에 고정했다."""
import csv, hashlib, json, math, os, platform, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for ch in ('ch09', 'ch03'):
    sys.path.insert(0, os.path.join(HERE, '..', ch))
import numpy as np, scipy
from scipy import stats
import tephralib as T          # 9장
import c14lib as C             # 3장
import v1tables as V


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
print('앞 장 모듈: ch09/tephralib.py(sha256 %s), ch03/c14lib.py(sha256 %s)' % (sha(T.__file__), sha(C.__file__)))
for nm in ('intcal04', 'intcal13', 'intcal20'):
    print('  곡선 파일 3Col_%s.14C sha256 %s' % (nm, sha(os.path.join(C.DATA, '3Col_%s.14C' % nm))))
OUT = {}
SUM = []


def add(item, v1, mine, ok, note=''):
    SUM.append((item, v1, mine, ok, note))


def same(mine, printed):
    printed = printed.replace(',', '')
    nd = len(printed.split('.')[1]) if '.' in printed else 0
    return round(mine, nd) == float(printed)


# ------------------------------------------------------------------ 1. 입력
print('\n== 1. 입력: 제1권 4장 계산 4-6 상자의 날짜 (data/okuno2010-dates-v1.csv), 표 5의 McLean 등 구간 (data/ulleung-layers-v1.csv)')
dates = list(csv.DictReader(open(os.path.join(HERE, 'data', 'okuno2010-dates-v1.csv'), encoding='utf-8')))
ML = {r['layer']: (int(r['mclean_lo_calBP']), int(r['mclean_hi_calBP']), r['mclean_code']) for r in csv.DictReader(open(os.path.join(HERE, 'data', 'ulleung-layers-v1.csv'), encoding='utf-8'))}
D = {}
for r in dates:
    D.setdefault(r['layer'], []).append((float(r['c14_BP']), float(r['sigma']), r['source']))
print('%-4s %8s %6s  %s' % ('층', '14C BP', '시그마', '출처(제1권 4장)'))
for r in dates:
    print('%-4s %8.0f %6.0f  %s' % (r['layer'], float(r['c14_BP']), float(r['sigma']), r['source']))
print('McLean 등 구간(IntCal13 cal BP, 95.4%):', '; '.join('%s %d~%d' % (k, v[0], v[1]) for k, v in ML.items()))

# ------------------------------------------------------------------ 2. 합치 시험
print('\n== 2. 날짜 묶음의 합치 시험 (tephralib.tprime: 가중 평균, T\' = sum(((x - 평균)/s)^2), 자유도 n-1)')
v1out = subprocess.run([sys.executable, '-I', os.path.join(V.V1, 'ch04-calc-v1.py')], capture_output=True, text=True, cwd='/tmp', timeout=300).stdout
print('제1권 계산 스크립트 ch04-calc-v1.py 출력 %d줄, 원고 ch04-v1.md sha256 %s' % (v1out.count('\n'), V.ms_sha(4)[:16]))


def grab(pat):
    m = re.search(pat, v1out)
    return [float(x) for x in m.groups()] if m else None


def sel(layer, skip=()):
    rows = [d for d in D[layer] if d[0] not in skip]
    return [d[0] for d in rows], [d[1] for d in rows]


SETS = [
    ('U-2 네 날짜', 'U-2', (4710,), r'U-2 four \(([\d.]+), ([\d.]+), ([\d.]+)', ('4,940', '17.5', '1.27')),
    ('U-2 다섯 날짜(4710 포함)', 'U-2', (), r'U-2 five \(([\d.]+), ([\d.]+), ([\d.]+)', ('4,881.6', '15.1', '45.1')),
    ('U-3 두 날짜', 'U-3', (), None, None),
    ('U-4 다섯 날짜(12,000 BP대)', 'U-4', (9785,), r'U-4 five \(([\d.]+), ([\d.]+), ([\d.]+)', ('12,052.9', '18.3', '32.5')),
    ('U-4 네 날짜(11,840 제외)', 'U-4', (9785, 11840), r'U-4 four \(([\d.]+), ([\d.]+), ([\d.]+)', ('12,095', '20', '5.7')),
    ('U-4 여섯 날짜(9,785 포함, 이 장의 새 계산)', 'U-4', (), None, None),
]
print('%-38s %2s %10s %7s %9s %3s %10s %8s  %s' % ('묶음', 'n', '가중 평균', '오차', "T'", 'df', 'p', '5% 한계', '판정'))
AG = {}
for nm, ly, skip, rx, v1txt in SETS:
    x, s = sel(ly, skip)
    r = T.tprime(x, s)
    AG[nm] = dict(layer=ly, x=x, s=s, **r)
    print('%-38s %2d %10.2f %7.2f %9.3f %3d %10.3e %8.3f  %s' % (nm, len(x), r['mean'], r['err'], r['T'], r['df'], r['p'], r['crit5'], '합치' if r['agree'] else '불일치'))
    if v1txt:
        okt = all(V.has(4, t) for t in v1txt[:1]) and same(r['mean'], v1txt[0]) and same(r['err'], v1txt[1]) and same(r['T'], v1txt[2])
        g = grab(rx)
        oks = g is not None and abs(g[0] - r['mean']) < 1e-4 and abs(g[1] - r['err']) < 1e-4 and abs(g[2] - r['T']) < 1e-4
        print('     제1권 원고 (평균, 오차, T\') = (%s, %s, %s) %s | 제1권 스크립트 %s %s' % (*v1txt, '일치' if okt else '불일치', ('(%.6g, %.6g, %.6g)' % tuple(g)) if g else '없음', '일치' if oks else '불일치'))
        add("합치 시험 (평균, 오차, T'): " + nm, '(%s, %s, %s)' % v1txt, '(%.2f, %.2f, %.2f)' % (r['mean'], r['err'], r['T']), okt and oks)
x, s = sel('U-3')
d = x[1] - x[0]; sd = math.hypot(*s); z = d / sd
print('U-3 쌍별: 차이 %.0f년, 차이의 시그마 %.2f, z = %.2f (제1권 계산 4-6 예 3: 505, 49.5, 10.2)' % (d, sd, z))
add('U-3 두 날짜의 차이, 시그마, z', '505, 49.5, 10.2', '%.0f, %.2f, %.2f' % (d, sd, z), V.has(4, '505 ÷ 49.5 = 10.2σ') and same(sd, '49.5') and same(z, '10.2'))
print('임계값: 자유도 3에서 %.3f, 4에서 %.3f (제1권 7.81, 9.49)' % (stats.chi2.ppf(0.95, 3), stats.chi2.ppf(0.95, 4)))
add('5% 임계값 df = 3, 4', '7.81, 9.49', '%.2f, %.2f' % (stats.chi2.ppf(0.95, 3), stats.chi2.ppf(0.95, 4)), same(stats.chi2.ppf(0.95, 3), '7.81') and same(stats.chi2.ppf(0.95, 4), '9.49'))
print("\nU-4의 12,000 BP대 다섯 날짜에서 한 개씩 뺀 T' (제1권은 11,840을 뺄 때만 합치라고 적음)")
x, s = sel('U-4', (9785,))
LOO = {}
for i in range(len(x)):
    r = T.tprime(np.delete(x, i), np.delete(s, i))
    LOO[int(x[i])] = r['T']
    print('  %6.0f ± %2.0f 를 뺀 T\' = %7.3f (df = %d, p = %.4f) %s' % (x[i], s[i], r['T'], r['df'], r['p'], '합치' if r['agree'] else '불일치'))
print("  (한 개씩 빼 보는 일은 자료를 보고 날짜를 고르는 일이다. 9장 실습 9-6의 모의에서 이런 절차는 5% 한계를 지키지 못했다.)")
print('14C 나이와 남은 탄소 비율(제1권 계산 4-6 예 5, 리비 평균 수명 8033년): ', end='')
pm = [(4940, '54.1'), (7525, '39.2'), (9785, '29.6'), (12090, '22.2')]
oks = []
for age, pr in pm:
    f = C.F_from_age(age) * 100
    oks.append(same(f, pr))
    print('%d BP -> %.1f%% (제1권 %s)  ' % (age, f, pr), end='')
print()
add('14C 나이 -> 남은 탄소 비율(%)', '54.1, 39.2, 29.6, 22.2', ', '.join('%.1f' % (C.F_from_age(a) * 100) for a, _ in pm), all(oks) and V.has(4, '54.1%. 7525 BP → 39.2%'))

# ------------------------------------------------------------------ 3. 보정
print('\n== 3. 보정 (c14lib.calibrate: 곡선 위 1년 격자의 가우스 가능도, 곡선 오차를 더해 합성; 95.4% 최고밀도구간)')
CURV = {k: C.load_curve(k) for k in ('intcal04', 'intcal13', 'intcal20')}


def calib(age, sig, curve):
    g, p = C.calibrate(age, sig, CURV[curve])
    segs = C.hpd(g, p, 0.954)
    return g, p, segs


def outer(segs):
    return int(round(min(s[0] for s in segs))), int(round(max(s[1] for s in segs)))


def segtxt(segs):
    return '; '.join('%.0f~%.0f (%.1f%%)' % (a, b, 100 * pr) for a, b, pr in segs)


CAL = {}
print('%-34s %-9s %-12s  %s' % ('대상', '곡선', '외곽 95.4%', '구간들(확률)'))
targets = [('U-2 네 날짜 가중 평균 4940 ± 17.5', 4940.0, 17.5), ('U-2 한 날짜 4940 ± 35(제1권 4.11.2절)', 4940.0, 35.0), ('U-4 9785 ± 35', 9785.0, 35.0),
           ('U-4 네 날짜 가중 평균 12095 ± 20', 12095.0, 20.0)]
for nm, a, sg in targets:
    for cv in ('intcal04', 'intcal13', 'intcal20'):
        g, p, segs = calib(a, sg, cv)
        CAL[(nm, cv)] = dict(outer=outer(segs), segs=segs, med=C.median_age(g, p))
        print('%-34s %-9s %5d~%-6d  %s' % (nm, cv, *outer(segs), segtxt(segs)))
o = CAL[('U-2 한 날짜 4940 ± 35(제1권 4.11.2절)', 'intcal04')]['outer']
print('제1권 4.11.2절: "4940 ± 35 BP는 보정하면 5,600~5,734 cal BP" -> IntCal04 외곽 %d~%d, 끝의 차 %+d, %+d년' % (*o, o[0] - 5600, o[1] - 5734))
add('4940 ± 35 BP의 보정 구간(IntCal04)', '5,600~5,734 cal BP', '%d~%d' % o, V.has(4, '5,600∼5,734 cal BP') and abs(o[0] - 5600) <= 2 and abs(o[1] - 5734) <= 2)
o = CAL[('U-4 9785 ± 35', 'intcal04')]['outer']
print('제1권 계산 4-6 예 7: "9785 ± 35 BP는 보정 후 11,177~11,126 cal BP(중간 11,151.5)" -> IntCal04 외곽 %d~%d, 끝의 차 %+d, %+d년' % (*o, o[0] - 11126, o[1] - 11177))
print('  IntCal13 외곽 %d~%d, IntCal20 외곽 %d~%d. 어느 곡선으로도 제1권의 구간(11,126~11,177)은 나오지 않는다. 제1권 구간의 위쪽 끝 11,177이 이 계산의 아래쪽 끝이다.' % (*CAL[('U-4 9785 ± 35', 'intcal13')]['outer'], *CAL[('U-4 9785 ± 35', 'intcal20')]['outer']))
okc = V.has(4, '11,177∼11,126 cal BP') and abs(o[0] - 11126) <= 2 and abs(o[1] - 11177) <= 2
add('9785 ± 35 BP의 보정 구간(IntCal04)', '11,126~11,177 cal BP', '%d~%d' % o, okc, '어긋남: 제1권 구간이 이 계산의 아래쪽 끝에서 끝난다')
mid_mine = (o[0] + o[1]) / 2
print('  이 계산의 중간 (%d + %d)/2 = %.1f, 제1권의 중간 11,151.5, 차 %+.1f년' % (o[0], o[1], mid_mine, mid_mine - 11151.5))
gap_v1 = 11151.5 - 10200.5
mcl_mid = (ML['U-4'][0] + ML['U-4'][1]) / 2
print('  McLean 등 U-Oki 중간 (%d + %d)/2 = %.1f. 제1권 예 7: 11,151.5 - 10,200.5 = %.1f년(원고 951). 이 계산: %.1f - %.1f = %.1f년' % (ML['U-4'][0], ML['U-4'][1], mcl_mid, gap_v1, mid_mine, mcl_mid, mid_mine - mcl_mid))
add('오쿠노 대 McLean의 U-4 중간값 차이(년)', '951 (예 7), 949.5 (스크립트 11,150으로 반올림)', '%.1f (이 계산의 중간 %.1f 사용)' % (mid_mine - mcl_mid, mid_mine), False, '어긋남: 제1권 안에서도 원고 951과 스크립트 949.5가 다르다')
g49 = grab(r'Okuno U-4 11,150 vs McLean 10,200 ([\d.]+)')
print('  제1권 스크립트의 같은 양: %s (원고 951과 1.5년 차이: 스크립트는 11,150으로 반올림해 계산, 9장 실습 9-15)' % (g49[0] if g49 else '없음'))
OUT['cal'] = {'%s|%s' % k: dict(outer=list(v['outer']), med=v['med']) for k, v in CAL.items()}
OUT['gap'] = dict(v1=gap_v1, mine=mid_mine - mcl_mid, mid_mine=mid_mine, mcl_mid=mcl_mid)

# ------------------------------------------------------------------ 4. McLean 등과 대조: 날짜마다
print('\n== 4. 날짜마다 보정해 McLean 등의 층 구간과 맞대 보기 (IntCal13, McLean 등이 쓴 곡선)')
print('"안쪽 확률"은 보정한 확률 가운데 McLean 등의 구간 안에 드는 몫이다. 0에 가까우면 그 날짜는 McLean 등의 층 연대와 맞지 않는다.')
print('%-4s %7s %4s | %-12s %-26s %9s %s' % ('층', '14C BP', '±', '외곽 95.4%', 'McLean 구간', '안쪽 확률', '겹침'))
INS = []
CUR = {}


def keep(key, g, p):
    """그림용: 확률이 최댓값의 1e-5 이상인 범위만 1년 격자 그대로 저장한다."""
    ix = np.where(p >= p.max() * 1e-5)[0]
    lo_, hi_ = int(ix.min()), int(ix.max())
    CUR[key] = dict(x0=float(g[lo_]), p=[round(float(v), 7) for v in p[lo_:hi_ + 1]])


for r in dates:
    ly, a, sg = r['layer'], float(r['c14_BP']), float(r['sigma'])
    g, p, segs = calib(a, sg, 'intcal13')
    lo, hi, code = ML[ly]
    keep('%s|%d' % (ly, int(a)), g, p)
    ins = float(p[(g >= lo) & (g <= hi)].sum())
    ov = not (outer(segs)[1] < lo or hi < outer(segs)[0])
    INS.append(dict(layer=ly, c14=a, sigma=sg, outer=list(outer(segs)), inside=ins, overlap=ov))
    print('%-4s %7.0f %4.0f | %5d~%-6d %5d~%-5d (%-9s) %9.4f %s' % (ly, a, sg, *outer(segs), lo, hi, code, ins, '겹침' if ov else '겹치지 않음'))
for nm_, a_, s_ in (('U-2|wm', 4940.0, 17.5), ('U-4|wm', 12095.0, 20.0)):
    g_, p_, _ = calib(a_, s_, 'intcal13')
    keep(nm_, g_, p_)
OUT['curves'] = CUR
OUT['inside'] = INS
inside_best = {ly: max(x['inside'] for x in INS if x['layer'] == ly) for ly in ('U-2', 'U-3', 'U-4')}
print('층마다 가장 큰 안쪽 확률: ' + ', '.join('%s %.4f' % (k, v) for k, v in inside_best.items()))
print('U-4(U-Oki): 여섯 날짜 모두 안쪽 확률이 %.4f이다. 가장 젊은 날짜 9785 ± 35의 외곽(IntCal13) %d~%d와 McLean 등 구간 %d~%d의 사이는 %d년이다.' % (
    max(x['inside'] for x in INS if x['layer'] == 'U-4'), *CAL[('U-4 9785 ± 35', 'intcal13')]['outer'], *ML['U-4'][:2], CAL[('U-4 9785 ± 35', 'intcal13')]['outer'][0] - ML['U-4'][1]))
OUT['inside_best'] = inside_best

print('\n== 4b. 오쿠노 등이 채택·후보로 든 연대(제1권 표 5)는 어느 날짜의 보정 범위 안에 드는가 (곡선 IntCal04, 오쿠노 등이 쓴 곡선)')
CAND = {'U-4': [14000, 11000], 'U-3': [8300, 9000], 'U-2': [5600]}
for t_ in ('후보 14,000 또는 11,000', '8,300 또는 9,000', '5,600'):
    print('  제1권 표 5에 "%s" 있음: %s' % (t_, any(t_ in r[1] for r in V.table(4, 5)['rows'])))
CD = []
for ly, cands in CAND.items():
    for cv in cands:
        hits = []
        for r in dates:
            if r['layer'] != ly:
                continue
            a, sg = float(r['c14_BP']), float(r['sigma'])
            g4, p4, sg4 = calib(a, sg, 'intcal04')
            o4 = outer(sg4)
            if o4[0] <= cv <= o4[1]:
                hits.append('%d ± %d(%d~%d)' % (a, sg, *o4))
        CD.append(dict(layer=ly, cand=cv, hits=hits))
        print('  %s 후보 %6d cal BP: %s' % (ly, cv, ('이 범위 안에 드는 날짜: ' + '; '.join(hits)) if hits else '95.4% 외곽 안에 드는 날짜 없음'))
OUT['cand'] = CD

# ------------------------------------------------------------------ 5. 순서 제약 연대 모형
print('\n== 5. 층서 순서 제약을 둔 연대 모형 (tephralib.grid_posterior, ordered_samples; 14C 나이 BP 그대로, 보정하지 않음)')
print('층마다 참 나이는 균일 사전분포. 날짜는 확률 1-q로 N(theta, s^2), 확률 q로 N(theta, s^2 + 1000^2)(이상치). 순서: theta(U-4) > theta(U-3) > theta(U-2). 표본 2,000,000개(기각 표집, 시드 20261026).')
LAY = [('U-4', *sel('U-4', (9785,))), ('U-3', *sel('U-3')), ('U-2', *sel('U-2'))]
grid = np.arange(3000.0, 14000.0, 0.5)


def hpd(x, mass=0.954):
    x = np.sort(x); n = len(x); k = int(np.ceil(mass * n))
    w = x[k - 1:] - x[:n - k + 1]
    i = int(np.argmin(w))
    return float(x[i]), float(x[i + k - 1])


rng = np.random.default_rng(20261026)
MOD = {}
for q in (0.0, 0.1):
    posts, outs, free = [], [], []
    for ly, x, s in LAY:
        p, po = T.grid_posterior(x, s, grid, q=q)
        posts.append(p); outs.append(po)
        m = float((p * grid).sum()); sd = float(np.sqrt((p * (grid - m) ** 2).sum()))
        free.append((m, sd))
    S, pr = T.ordered_samples(posts, grid, 2000000, rng)
    mm, ss = S.mean(axis=0), S.std(axis=0, ddof=1)
    print('\n  --- q = %.2f: 순서 제약 통과 비율 %.5f (표본 2,000,000개 중 %d개 남음) ---' % (q, pr, len(S)))
    rec = dict(pass_rate=pr, layers={})
    for k, (ly, x, s) in enumerate(LAY):
        lo, hi = hpd(S[:, k])
        print('  %-4s 순서 없이 %9.1f ± %6.1f | 순서 있음 %9.1f ± %6.1f, 95.4%% 최고밀도구간 %9.1f~%9.1f%s' % (
            ly, *free[k], mm[k], ss[k], lo, hi, ('' if q == 0 else ' | 날짜별 이상치 사후확률 ' + ' '.join('%.3f' % v for v in outs[k]))))
        rec['layers'][ly] = dict(free=list(free[k]), ordered=[float(mm[k]), float(ss[k])], hpd=[lo, hi], outlier=[float(v) for v in outs[k]], x=x)
    MOD['q%.2f' % q] = rec
print('\n  해석: 세 층의 14C 나이가 서로 2,900년 이상 떨어져 있어 순서 제약은 값을 바꾸지 않는다(통과 비율 1.000). 이상치 모형(q = 0.1)은 U-3의 두 날짜 가운데 어느 쪽이 맞는지 정하지 못하고(이상치 사후확률 0.520, 0.520) 사후분포는 두 봉우리이다.')
add('순서 제약 통과 비율(q = 0, 0.1)', '(9장 로그) 1.00000, 1.00000', '%.5f, %.5f' % (MOD['q0.00']['pass_rate'], MOD['q0.10']['pass_rate']), round(MOD['q0.00']['pass_rate'], 5) == 1.0 and round(MOD['q0.10']['pass_rate'], 5) == 1.0)
u3 = MOD['q0.10']['layers']['U-3']
add('이상치 모형에서 U-3의 두 날짜의 이상치 사후확률', '(9장 로그) 0.520, 0.520', '%.3f, %.3f' % tuple(u3['outlier']), all(same(v, '0.520') for v in u3['outlier']))
add('이상치 모형(q = 0.1)에서 11,840의 이상치 사후확률', '(9장 로그) 1.000', '%.3f' % MOD['q0.10']['layers']['U-4']['outlier'][1], same(MOD['q0.10']['layers']['U-4']['outlier'][1], '1.000'))
# 모형 결과를 보정
print('\n  모형의 결과를 보정에 넘기기(정규 근사: 평균 ± 표준편차를 14C 나이로 보고 c14lib.calibrate. U-3은 두 봉우리라 정규 근사가 맞지 않아 뺀다)')
for ly in ('U-2', 'U-4'):
    m, sd = MOD['q0.10']['layers'][ly]['ordered']
    for cv in ('intcal13',):
        g, p, segs = calib(m, sd, cv)
        print('  %s q = 0.1 순서 있음 %.1f ± %.1f BP -> %s 95.4%% 외곽 %d~%d (McLean %d~%d)' % (ly, m, sd, cv, *outer(segs), *ML[ly][:2]))
        OUT.setdefault('model_cal', {})[ly] = dict(mean=m, sd=sd, outer=list(outer(segs)), mclean=list(ML[ly][:2]))
OUT['model'] = MOD

# ------------------------------------------------------------------ 요약
print('\n== 6. 요약: 기준값(제1권 또는 앞 장 로그)과 이번 실행값')
for item, v1, mine, ok, note in SUM:
    print('  %-52s 기준 %-40s 이번 %-34s %s %s' % (item, v1, mine, '일치' if ok else '불일치', note))
print('비교 %d개, 일치 %d개, 불일치 %d개' % (len(SUM), sum(1 for x in SUM if x[3]), sum(1 for x in SUM if not x[3])))
OUT['summary'] = [dict(item=a, v1=b, mine=c, ok=bool(d), note=n) for a, b, c, d, n in SUM]
OUT['agree'] = AG
OUT['loo'] = {str(k): v for k, v in LOO.items()}
OUT['ml'] = {k: list(v[:2]) for k, v in ML.items()}
json.dump(OUT, open(os.path.join(HERE, 'case2.json'), 'w'), ensure_ascii=False, default=float)
