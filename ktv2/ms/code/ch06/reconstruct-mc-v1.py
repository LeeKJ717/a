# -*- coding: utf-8 -*-
"""6장 실습 6-9: 검증 통계(RE, CE)가 참 복원 능력을 얼마나 알려 주는가. 시연값 자료를 시드만 바꿔 되풀이 생성(몬테카를로).
각 되풀이: 가상 자료 생성 -> 음의 지수 표준화 -> 이중 가중 연대기 -> 1956~2013 보정·분할 검증 -> 복원 -> 참 기후와 비교.
공통 신호의 세기 b(0.085 = 이 장의 기본값, 0.060 = 더 약함)를 둘로 한다. 날짜 오류는 넣지 않는다.
실행: python3 reconstruct-mc-v1.py [되풀이 수=1000] | tee reconstruct-mc.log
"""
import os, sys, json, time, platform, importlib.util
import numpy as np
import scipy
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
def load(fn, nm):
    spec = importlib.util.spec_from_file_location(nm, os.path.join(HERE, fn)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
L = load('ringlib-v1.py', 'ringlib')
SY = load('synth-rings-v1.py', 'synthrings')
NREP = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
print('환경: python %s, numpy %s, scipy %s, 되풀이 %d회(공통 신호 b마다)' % (platform.python_version(), np.__version__, scipy.__version__, NREP))


def one(seed, b):
    S = SY.simulate(seed, corrupt=False, params=dict(b=b))
    years, X, T, O, tree = S['years'], S['X'], S['T'], S['O'], S['tree']
    I, _ = L.detrend(X, 'ModNegExp')
    c, dep = L.chron(I, True)
    cal = years >= 1956
    a_, b_, r_, _ = L.linfit(c[cal], O)
    est = a_ + b_ * c
    out = dict(r_cal=r_)
    A = (years >= 1956) & (years <= 1984); B = (years >= 1985) & (years <= 2013)
    Oy = np.full(len(years), np.nan); Oy[cal] = O
    res = []
    for cs, vs in ((A, B), (B, A)):
        a2, b2, _, _ = L.linfit(c[cs], Oy[cs])
        e2 = a2 + b2 * c[vs]
        re, ce = L.re_ce(Oy[vs], e2, Oy[cs].mean())
        res.append((re, ce, float(np.corrcoef(Oy[vs], e2)[0, 1])))
    out['re'] = min(x[0] for x in res); out['ce'] = min(x[1] for x in res); out['rv'] = min(x[2] for x in res)
    for lab, lo, hi in (('e', 1600, 1699), ('m', 1700, 1799), ('l', 1800, 1955)):
        sel = (years >= lo) & (years <= hi)
        out['rt_' + lab] = float(np.corrcoef(est[sel], T[sel])[0, 1])
        sse = np.sum((T[sel] - est[sel]) ** 2)
        out['ret_' + lab] = float(1 - sse / np.sum((T[sel] - O.mean()) ** 2))   # RE(참값): 보정 기간 관측 평균을 기준으로
    return out

allres = {}
t0 = time.time()
for b in (0.085, 0.060):
    rs = [one(1000 + s, b) for s in range(NREP)]
    allres[b] = rs
    print('b = %.3f: %d회 완료, 누적 %.1f초' % (b, len(rs), time.time() - t0))

def q(v, p): return float(np.percentile(v, p))
for b, rs in allres.items():
    g = lambda k: np.array([r[k] for r in rs])
    print('\n== 공통 신호 b = %.3f (%d회)' % (b, len(rs)))
    print('  변수                          2.5%      중앙값     97.5%')
    for lab, k in (('보정 r(1956~2013)', 'r_cal'), ('분할 검증 r(두 방향 중 작은 값)', 'rv'), ('분할 검증 RE(작은 값)', 're'), ('분할 검증 CE(작은 값)', 'ce'),
                   ('복원-참값 r, 1600~1699', 'rt_e'), ('복원-참값 r, 1700~1799', 'rt_m'), ('복원-참값 r, 1800~1955', 'rt_l'),
                   ('RE(참값), 1600~1699', 'ret_e'), ('RE(참값), 1700~1799', 'ret_m'), ('RE(참값), 1800~1955', 'ret_l')):
        v = g(k)
        print('  %-30s %7.3f  %7.3f  %7.3f' % (lab, q(v, 2.5), q(v, 50), q(v, 97.5)))
    ver_ok = (g('re') > 0) & (g('ce') > 0)
    print('  분할 검증에서 RE와 CE가 모두 0보다 큰 되풀이: %d회(%.1f%%)' % (ver_ok.sum(), 100 * ver_ok.mean()))
    bad_early = g('ret_e') < 0
    print('  그 가운데 1600~1699의 RE(참값)가 0보다 작은 되풀이: %d회(%.1f%% of 검증 통과)' % ((ver_ok & bad_early).sum(), 100 * (ver_ok & bad_early).sum() / max(1, ver_ok.sum())))
    print('  검증 통과 여부와 상관없이 1600~1699의 RE(참값) < 0: %d회(%.1f%%)' % (bad_early.sum(), 100 * bad_early.mean()))
    rho = stats.spearmanr(g('ce'), g('rt_e'))[0]
    rho2 = stats.spearmanr(g('ce'), g('rt_l'))[0]
    print('  스피어만 순위 상관: 검증 CE와 복원-참값 r(1600~1699) %.3f, 검증 CE와 복원-참값 r(1800~1955) %.3f' % (rho, rho2))
json.dump({str(b): rs for b, rs in allres.items()}, open(os.path.join(HERE, 'reconstruct-mc.json'), 'w'))
print('\n총 %.1f초. 저장: reconstruct-mc.json' % (time.time() - t0))
