# -*- coding: utf-8 -*-
"""6장 실습 6-3(자료 A, 실제 공개 자료 co021)과 6-4(자료 B, 시연값): 교차 연대 결정.
날짜 오류를 일부러 만들어 넣고(참 날짜를 알기 때문에 판정을 채점할 수 있다) 구간 상관으로 찾아내고 고친다.
입력: work/co021.rwl (export-co021-v1.R가 만든다), synth-demo-bad.rwl, synth-demo-true.rwl (synth-rings-v1.py)
출력: synth-demo-fixed.rwl (자료 B에서 찾아낸 오류만 고친 자료), crossdate-segs.json(그림용), crossdate.log
실행: python3 crossdate-v1.py | tee crossdate.log
"""
import os, sys, json, platform, importlib.util
import numpy as np
import scipy

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)

print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
CRIT50 = L.crit_r(50, 0.01)
print('판정에 쓰는 임계 상관(겹친 해 50년, 양쪽 1%%) = %.3f. 이 값은 자료에 자기상관이 없다는 가정의 값이다(사전 백색화로 줄였을 뿐 없애지 못한다)' % CRIT50)
OUT = {}


def scan_all(X, years, names, label):
    P = L.xdate_prep(X, 32, True)
    M = L.loo_master(P, True)
    S, F = {}, {}
    for j, nm in enumerate(names):
        S[nm] = L.seg_scan(P, M, years, j, 50, 25, 10)
        F[nm] = L.flag_series(S[nm], CRIT50)
    return P, M, S, F


def show_rows(nm, rows, only_bad=False):
    print('   %-6s 구간          lag 0의 r  최고 r의 lag  그때의 r' % nm)
    for a, b, r0, lag, rb, _ in rows:
        bad = lag != 0 and rb > CRIT50 and (np.isnan(r0) or r0 < CRIT50)
        if only_bad and not bad and r0 >= CRIT50:
            continue
        print('          %d~%d   %8.3f   %8d   %8.3f%s' % (a, b, r0, lag, rb, '   <- 의심' if bad else ''))


def part(label, years, names, Xtrue, Xbad, truth_errors):
    """truth_errors: [(계열 이름, 종류, 인수)] 일부러 넣은 오류. 반환: 고친 행렬, 요약."""
    print('\n' + '=' * 70)
    print(label)
    print('=' * 70)
    Pt, Mt, St, Ft = scan_all(Xtrue, years, names, 'clean')
    Pb, Mb, Sb, Fb = scan_all(Xbad, years, names, 'bad')
    r_t, _ = L.interseries_cor(Xtrue, 32)
    r_b, _ = L.interseries_cor(Xbad, 32)
    print('계열 %d개. 전 기간 상관(스플라인 32년, AR 백색화, 하나 뺀 이중 가중 마스터): 오류 없는 자료 중앙값 %.3f(최소 %.3f), 오류를 넣은 자료 중앙값 %.3f(최소 %.3f)' % (
        len(names), np.nanmedian(r_t), np.nanmin(r_t), np.nanmedian(r_b), np.nanmin(r_b)))
    flag_t = [nm for nm in names if Ft[nm][0]]
    flag_b = [nm for nm in names if Fb[nm][0]]
    print('의심 규칙(이웃한 두 구간에서 같은 lag): 오류가 없는 자료에서 의심된 계열 %d개 %s' % (len(flag_t), flag_t))
    print('                                      오류를 넣은 자료에서 의심된 계열 %d개 %s' % (len(flag_b), flag_b))
    summary = dict(flag_clean=flag_t, flag_bad=flag_b, errors=[], ncrit=CRIT50)
    for nm, kind, arg in truth_errors:
        j = names.index(nm)
        det = Fb[nm][0]
        r_before = r_b[j]
        r_clean = r_t[j]
        print('\n -- 일부러 넣은 오류: %s %s(%s). 전 기간 상관: 오류 없을 때 %.3f, 오류 있을 때 %.3f. 의심 규칙으로 찾았는가: %s%s' % (
            nm, {'missing': '빠진 테', 'shift': '통째 어긋남', 'false': '거짓 테'}[kind], arg, r_clean, r_before,
            '예' if det else '아니오', (' (lag %+d)' % Fb[nm][1]) if det else ''))
        show_rows(nm, Sb[nm])
        summary['errors'].append(dict(name=nm, kind=kind, arg=arg, detected=bool(det), lag=Fb[nm][1], r_clean=float(r_clean), r_bad=float(r_before)))
    miss = [e['name'] for e in summary['errors'] if not e['detected']]
    hit = [e['name'] for e in summary['errors'] if e['detected']]
    fa = [nm for nm in flag_b if nm not in [e['name'] for e in summary['errors']]]
    print('\n채점: 찾은 오류 %d개 %s, 놓친 오류 %d개 %s, 오류가 없는데 의심된 계열(거짓 경보) %d개 %s' % (len(hit), hit, len(miss), miss, len(fa), fa))
    summary.update(hit=hit, miss=miss, false_alarm=fa)
    return dict(Pb=Pb, Mb=Mb, Sb=Sb, Fb=Fb, r_b=r_b, r_t=r_t, summary=summary)


def lag_matrix(rows):
    lags = sorted(rows[0][5].keys())
    return dict(lags=lags, segs=[dict(a=a, b=b, r=[None if np.isnan(rl[k]) else round(float(rl[k]), 4) for k in lags]) for a, b, _, _, _, rl in rows])


# ====================================================================== 자료 A: 실제 자료 co021
pathA = os.path.join(HERE, 'work', 'co021.rwl')
if os.path.exists(pathA):
    yA, nA, XA = L.read_rwl(pathA)
    print('자료 A: 실제 공개 자료 co021(미국 메사 베르데, 더글러스전나무 35계열, ITRDB에서 온 것을 dplR 꾸러미가 담은 것), 연도 %d~%d' % (yA[0], yA[-1]))
    n_ok = np.sum(~np.isnan(XA), axis=0)
    cand = [i for i in range(XA.shape[1]) if (~np.isnan(XA[:, i])).argmax() <= 1400 - yA[0] and not np.isnan(XA[-1, i]) and n_ok[i] > 500]
    iA, iB, iC = cand[1], cand[3], cand[5]
    errs = [(nA[iA], 'missing', 1600), (nA[iB], 'shift', 3), (nA[iC], 'false', 1700)]
    XAb = XA.copy()
    XAb[:, iA] = L.corrupt_missing(XA[:, iA], yA, 1600)
    XAb[:, iB] = L.corrupt_shift(XA[:, iB], 3)
    XAb[:, iC] = L.corrupt_false(XA[:, iC], yA, 1700)
    resA = part('자료 A. 실제 자료 co021에 날짜 오류 세 개를 넣은 경우(원래 날짜는 이 자료를 만든 연구자들이 맞춘 것이라고 보고, 그것을 참으로 둔다)', yA, nA, XA, XAb, errs)
    OUT['A_missing'] = dict(name=nA[iA], year=1600, **lag_matrix(resA['Sb'][nA[iA]]))
    OUT['A_shift'] = dict(name=nA[iB], **lag_matrix(resA['Sb'][nA[iB]]))
    OUT['A_false'] = dict(name=nA[iC], year=1700, **lag_matrix(resA['Sb'][nA[iC]]))
    OUT['A_summary'] = resA['summary']
else:
    print('work/co021.rwl이 없어 자료 A는 건너뛴다(export-co021-v1.R을 먼저 실행한다).')

# ====================================================================== 자료 B: 시연값
yB, nB, XBb = L.read_rwl(os.path.join(HERE, 'synth-demo-bad.rwl'))
yT, nT, XBt = L.read_rwl(os.path.join(HERE, 'synth-demo-true.rwl'))
assert (yB == yT).all() and nB == nT
# 어느 계열에 어떤 오류를 넣었는지는 synth-rings.log에 있다(여기서는 같은 규칙으로 다시 고른다)
candB = [i for i in range(XBt.shape[1]) if (~np.isnan(XBt[:, i])).argmax() <= 1700 - yB[0] and not np.isnan(XBt[-1, i])]
errsB = [(nB[candB[1]], 'missing', 1850), (nB[candB[3]], 'shift', 3), (nB[candB[5]], 'false', 1790)]
resB = part('자료 B. 시연값(가상 나이테 폭, 나무 사이 평균 상관 약 0.2로 노백산 표 1과 같은 크기). 오류 세 개를 넣은 경우', yB, nB, XBt, XBb, errsB)
OUT['B_missing'] = dict(name=errsB[0][0], year=1850, **lag_matrix(resB['Sb'][errsB[0][0]]))
OUT['B_shift'] = dict(name=errsB[1][0], **lag_matrix(resB['Sb'][errsB[1][0]]))
OUT['B_false'] = dict(name=errsB[2][0], year=1790, **lag_matrix(resB['Sb'][errsB[2][0]]))
OUT['B_summary'] = resB['summary']

# ---- 놓친 오류를 긴 창으로 다시 본다(자료 B)
print('\n== 자료 B에서 놓친 오류를 오류 시점 앞뒤의 긴 창으로 다시 본다 (오류의 시점을 안다고 가정하는 사후 점검이다)')
Pb, Mb = resB['Pb'], resB['Mb']
long_rows = []
for nm, kind, arg in errsB:
    j = nB.index(nm)
    if kind == 'missing':
        spans = [('오류 이전(%d~%d)' % (yB[0] + 20, arg - 1), yB[0] + 20, arg - 1), ('오류 이후(%d~2013)' % (arg + 1), arg + 1, 2013)]
    elif kind == 'false':
        spans = [('오류 이전(%d~%d)' % (yB[0] + 20, arg - 1), yB[0] + 20, arg - 1), ('오류 이후(%d~2013)' % (arg + 1), arg + 1, 2013)]
    else:
        spans = [('전 기간', yB[0] + 20, 2013)]
    for lab, y0, y1 in spans:
        # 계열의 실제 첫 해를 쓴다
        col = Pb[:, j]
        first = int(yB[np.where(~np.isnan(col))[0][0]])
        y0 = max(y0, first)
        sc = L.lag_scan(Pb[:, j], Mb[:, j], yB, y0, y1, 10)
        order = sorted(sc.items(), key=lambda kv: -(-9 if np.isnan(kv[1][0]) else kv[1][0]))
        n_over = sc[0][1]
        print('  %s %s (%d~%d, 겹친 %d해): lag 0의 r = %.3f, 임계(1%%) = %.3f, 상위 lag %s' % (
            nm, lab, y0, y1, n_over, sc[0][0], L.crit_r(max(n_over, 3), 0.01), [(k, round(v[0], 3)) for k, v in order[:3]]))
        long_rows.append(dict(name=nm, label=lab, y0=y0, y1=y1, n=n_over, r0=sc[0][0], top=[(k, v[0]) for k, v in order[:3]]))
OUT['B_long'] = long_rows

# ---- 고치기: 자료 B는 찾아낸 계열만 고친다
fixed = XBb.copy()
print('\n== 고치기 (자료 B: 의심 규칙으로 찾은 계열만 고친다)')
for e in resB['summary']['errors']:
    nm, kind, arg = e['name'], e['kind'], e['arg']
    j = nB.index(nm)
    if not e['detected']:
        print('  %s: 의심 규칙이 찾지 못해 고치지 않는다' % nm)
        continue
    if kind == 'shift':
        d = -e['lag']
        fixed[:, j] = L.repair_shift(XBb[:, j], d)
        print('  %s: 최고 상관의 lag가 %+d이므로 전체를 %d년 앞으로 옮긴다(바깥 %d해의 테는 처음에 잘려 나가 되살릴 수 없다)' % (nm, e['lag'], d, d))
    else:
        print('  %s: %s는 이 규칙으로 고칠 방법을 정하지 못했다(오류 해를 모른다)' % (nm, kind))
L.write_rwl(os.path.join(HERE, 'synth-demo-fixed.rwl'), yB, nB, fixed)
r_fix, _ = L.interseries_cor(fixed, 32)
for e in resB['summary']['errors']:
    j = nB.index(e['name'])
    print('  %s 전 기간 상관: 오류 없을 때 %.3f, 오류 있을 때 %.3f, 고친 뒤 %.3f' % (e['name'], e['r_clean'], e['r_bad'], r_fix[j]))
print('저장: synth-demo-fixed.rwl (자료 B의 찾아낸 오류만 고친 것)')

json.dump(OUT, open(os.path.join(HERE, 'crossdate-segs.json'), 'w', encoding='utf-8'), ensure_ascii=False, default=float)
