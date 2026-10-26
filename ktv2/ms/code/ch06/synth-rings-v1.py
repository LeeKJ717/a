# -*- coding: utf-8 -*-
"""6장 실습 6-1: 시연값(가상 나이테 폭 자료) 만들기. 시드 고정.

이 자료는 노백산 자료가 아니다. 제1권이 옮긴 Lyu 등(2016)의 크기(414년, 41그루 71코어, 복원 평균 7.66 °C와 표준편차
0.53 °C, 기상 관측 58년)를 흉내 낸 가상의 자료이며, 참 기후를 알고 있다는 점이 실제 자료와 다르다.
  참 기후 T(t)        : 1600~2013년, AR(1) 기후 + 느린 변동 (평균 7.66, 표준편차 0.53 °C로 맞춤)
  기상 관측 O(t)      : 1956~2013년, T + 측정 오차(표준편차 0.20 °C)
  테 너비(mm), 코어 k : log w = log G(나이) + b zT(t) + u(나무, t) + v(코어) + e(t)
                        G = 나무 고유 성장률 x (0.35 + 1.8 exp(-나이/40)) (mm), zT = 표준화한 참 기후
                        u = 나무 수준의 AR(1) 교란(코어끼리 공유), v = 코어 수준의 느린 AR(1), e = 해마다의 잡음
  교차 연대 결정 연습용으로 세 계열의 날짜를 일부러 틀리게 만든다(lib 함수 simulate의 corrupt=True).
실행: python3 synth-rings-v1.py | tee synth-rings.log
"""
import os, sys, platform, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261026
Y0, Y1 = 1600, 2013
OBS0 = 1956
PARAMS = dict(b=0.085, tree_ar=0.6, tree_sd=0.12, core_ar=0.3, core_sd=0.08, noise_sd=0.10, obs_sd=0.20,
              clim_mean=7.66, clim_sd=0.53, clim_ar=0.5)


def _load_ringlib():
    spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ar1(rng, n, phi, sd):
    """정상 AR(1) 열(정상 분포에서 시작), 표준편차 sd."""
    e = rng.normal(0, sd * np.sqrt(1 - phi ** 2), n)
    x = np.empty(n)
    x[0] = rng.normal(0, sd)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x


def simulate(seed=SEED, corrupt=False, params=None):
    """가상 자료 한 벌. 반환 dict: years, names, tree(코어별 나무 번호), X(너비, mm), T(참 기후), O(기상 관측, 1956~),
    corrupt=True이면 세 계열의 날짜를 틀리게 한 X와 그 내용(info)도 돌려준다."""
    P = dict(PARAMS)
    if params:
        P.update(params)
    rng = np.random.default_rng(seed)
    years = np.arange(Y0, Y1 + 1)
    ny = len(years)
    # 참 기후
    base = ar1(rng, ny, P['clim_ar'], 1.0)
    slow = 0.9 * np.sin(2 * np.pi * (years - Y0) / 75.0 + rng.uniform(0, 2 * np.pi))
    raw = base + slow
    z = (raw - raw.mean()) / raw.std()
    T = P['clim_mean'] + P['clim_sd'] * z
    obs = T[years >= OBS0] + rng.normal(0, P['obs_sd'], np.sum(years >= OBS0))
    # 나무: 41그루(30그루는 코어 2개, 11그루는 1개 = 71코어). 가장 오래된 나무는 1600년 시작.
    ntree = 41
    ncore = [2] * 30 + [1] * 11
    rng.shuffle(ncore)
    ages = np.round(90 + (ny - 90) * rng.beta(1.0, 2.2, ntree)).astype(int)
    ages[:6] = [414, 400, 380, 360, 340, 320]          # 오래된 나무 6그루(1600년대 표본 깊이)
    ends = np.full(ntree, Y1)
    dead = rng.random(ntree) < 0.15                    # 일부 나무는 2010~2012년에 끝난다
    dead[:6] = False
    ends[dead] = Y1 - rng.integers(1, 4, int(dead.sum()))
    zT = (T - T.mean()) / T.std()
    names, tree, cols = [], [], []
    start_of = []
    for k in range(ntree):
        end = ends[k]
        start = max(Y0, end - ages[k] + 1)
        yrs = np.arange(start, end + 1)
        age = np.arange(1, len(yrs) + 1)
        rate = np.exp(rng.normal(0, 0.30))
        G = rate * (0.35 + 1.8 * np.exp(-age / 40.0))
        u = ar1(rng, len(yrs), P['tree_ar'], P['tree_sd'])
        for c in range(ncore[k]):
            v = ar1(rng, len(yrs), P['core_ar'], P['core_sd'])
            e = rng.normal(0, P['noise_sd'], len(yrs))
            # 코어 시작은 수심(pith) 근처에서 몇 년 어긋날 수 있다: 코어 B는 처음 0~12년을 놓친다
            skip = 0 if c == 0 else int(rng.integers(0, 13))
            skip = min(skip, max(0, len(yrs) - 60))
            lw = np.log(G) + P['b'] * zT[yrs - Y0] + u + v + e
            w = np.exp(lw)
            col = np.full(ny, np.nan)
            col[(yrs - Y0)[skip:]] = w[skip:]
            cols.append(col)
            names.append('T%02d%s' % (k + 1, 'AB'[c]))
            tree.append(k + 1)
        start_of.append(start)
    X = np.array(cols).T
    X = np.round(X, 3)
    out = dict(years=years, names=names, tree=np.array(tree), X=X, T=T, O=obs, obs_years=years[years >= OBS0], params=P)
    if corrupt:
        L = _load_ringlib()
        Xc = X.copy()
        info = []
        # 날짜를 일부러 틀리게 만든 세 계열(1700년 이전에 시작하고 2013년까지 이어지는 계열 가운데 둘째, 넷째, 여섯째)
        cand = [i for i in range(X.shape[1]) if (~np.isnan(X[:, i])).argmax() <= 1700 - Y0 and not np.isnan(X[-1, i])]
        iA, iB, iC = cand[1], cand[3], cand[5]
        # (가) 빠진 테: 1850년의 테가 빠졌다. 바깥(2013)에서 세어 날짜를 붙이면 1850년 이전의 테는 한 해씩 늦게 붙는다.
        Xc[:, iA] = L.corrupt_missing(X[:, iA], years, 1850)
        info.append((names[iA], 'missing', 1850, '빠진 테: 1850년의 테가 측정에서 빠졌다. 1850년보다 오래된 부분의 날짜가 한 해 늦게 붙었다.'))
        # (나) 통째로 3년 어긋남: 날짜가 모두 3년 늦다.
        Xc[:, iB] = L.corrupt_shift(X[:, iB], 3)
        info.append((names[iB], 'shift', 3, '날짜가 통째로 3년 늦게 붙었다(각 해의 값이 참 연도보다 3년 뒤 연도에 놓였다).'))
        # (다) 거짓 테: 1790년의 테가 둘로 갈라져 두 개로 측정되었다. 1790년보다 오래된 테는 한 해씩 일찍 붙는다.
        Xc[:, iC] = L.corrupt_false(X[:, iC], years, 1790)
        info.append((names[iC], 'false', 1790, '거짓 테: 1790년의 테가 둘로 갈라져 두 개로 측정되었다. 1790년보다 오래된 부분의 날짜가 한 해 일찍 붙었다.'))
        out['Xc'] = Xc
        out['info'] = info
    return out


if __name__ == '__main__':
    L = _load_ringlib()
    print('환경: python %s, numpy %s' % (platform.python_version(), np.__version__))
    print('시드 %d, 매개변수 %s' % (SEED, PARAMS))
    S = simulate(SEED, corrupt=True)
    X, Xc = S['X'], S['Xc']
    years = S['years']
    print('계열 %d개(코어), 나무 %d그루, 연도 %d~%d (%d년)' % (X.shape[1], len(set(S['tree'])), years[0], years[-1], len(years)))
    n = np.sum(~np.isnan(X), axis=0)
    print('계열 길이: 최소 %d, 중앙값 %d, 최대 %d년; 너비 평균 %.3f mm' % (n.min(), np.median(n), n.max(), np.nanmean(X)))
    cnt = np.sum(~np.isnan(X), axis=1)
    for y in (1600, 1650, 1700, 1800, 1900, 2000, 2013):
        print('  %d년의 코어 수 %d' % (y, cnt[years == y][0]))
    print('참 기후: 평균 %.3f, 표준편차 %.3f, 1차 자기상관 %.3f' % (S['T'].mean(), S['T'].std(ddof=1), L.acf1(S['T'])))
    print('기상 관측(1956~2013, %d년): 평균 %.3f, 표준편차 %.3f, 참 기후와의 상관 %.3f' % (
        len(S['O']), S['O'].mean(), S['O'].std(ddof=1), np.corrcoef(S['O'], S['T'][years >= OBS0])[0, 1]))
    for nm, kind, arg, why in S['info']:
        print('  일부러 틀린 계열 %s: %s' % (nm, why))
    # 저장: 틀린 날짜의 .rwl, 바른 날짜의 .rwl, 참 기후, 나무 번호
    L.write_rwl(os.path.join(HERE, 'synth-demo-bad.rwl'), years, S['names'], Xc)
    L.write_rwl(os.path.join(HERE, 'synth-demo-true.rwl'), years, S['names'], X)
    with open(os.path.join(HERE, 'synth-truth.csv'), 'w', encoding='utf-8') as f:
        f.write('year,temp_true,temp_obs\n')
        for i, y in enumerate(years):
            o = S['O'][i - (len(years) - len(S['O']))] if y >= OBS0 else ''
            f.write('%d,%.4f,%s\n' % (y, S['T'][i], ('%.4f' % o) if o != '' else ''))
    with open(os.path.join(HERE, 'synth-ids.csv'), 'w', encoding='utf-8') as f:
        f.write('series,tree,core\n')
        for nm, t in zip(S['names'], S['tree']):
            f.write('%s,%d,%d\n' % (nm, t, 1 if nm.endswith('A') else 2))
    print('저장: synth-demo-bad.rwl, synth-demo-true.rwl, synth-truth.csv, synth-ids.csv')
    # 진단: 표준화 후 나무 사이 평균 상관
    I, _ = L.detrend(X, 'Spline')
    st = L.rwi_stats(I, S['tree'])
    print('진단(바른 날짜, 스플라인 67%%): rbar.bt %.3f, rbar.wt %.3f, rbar.eff %.3f, EPS %.3f, SNR %.2f, n %d' % (
        st['rbar_bt'], st['rbar_wt'], st['rbar_eff'], st['eps'], st['snr'], st['n']))
    I2, _ = L.detrend(X, 'ModNegExp')
    st2 = L.rwi_stats(I2, S['tree'])
    print('진단(바른 날짜, 음의 지수): rbar.bt %.3f, rbar.wt %.3f, rbar.eff %.3f, EPS %.3f, SNR %.2f, n %d' % (
        st2['rbar_bt'], st2['rbar_wt'], st2['rbar_eff'], st2['eps'], st2['snr'], st2['n']))
