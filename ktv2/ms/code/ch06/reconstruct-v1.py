# -*- coding: utf-8 -*-
"""6장 실습 6-8: 기후 복원(보정, 검증, 복원)과 그 결과를 참 기후와 견주기. 시연값 자료(참 기후를 안다).
입력: synth-chron.csv (detrend-chron-v1.py), synth-truth.csv, synth-demo-bad.rwl/-true.rwl/-fixed.rwl, synth-ids.csv
출력: recon-fig.json(그림용), reconstruct.log
실행: python3 reconstruct-v1.py | tee reconstruct.log
"""
import os, csv, json, platform, importlib.util
import numpy as np
import scipy
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ringlib', os.path.join(HERE, 'ringlib-v1.py'))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
print('환경: python %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))

ch = list(csv.DictReader(open(os.path.join(HERE, 'synth-chron.csv'), encoding='utf-8')))
tr = list(csv.DictReader(open(os.path.join(HERE, 'synth-truth.csv'), encoding='utf-8')))
years = np.array([int(r['year']) for r in ch])
X = np.array([float(r['std']) if r['std'] != '' else np.nan for r in ch])
depth = np.array([int(r['depth']) for r in ch])
T = np.array([float(r['temp_true']) for r in tr])
O = np.array([float(r['temp_obs']) if r['temp_obs'] != '' else np.nan for r in tr])
cal = years >= 1956
pre = ~cal
print('연대기(std, 음의 지수 표준화, 이중 가중 평균) %d~%d, 기상 관측 %d~%d(%d년)' % (years[0], years[-1], years[cal][0], years[-1], cal.sum()))

# ---------------------------------------------------------------- 1. 전 기간 보정
print('\n== 1. 전 기간(1956~2013) 보정: 관측 Y를 연대기 X로 회귀')
a, b, r, se = L.linfit(X[cal], O[cal])
n = int(cal.sum())
R2 = r * r
adj = 1 - (1 - R2) * (n - 1) / (n - 2)
F = R2 * (n - 2) / (1 - R2)
t = r * np.sqrt(n - 2) / np.sqrt(1 - R2)
p = 2 * stats.t.sf(abs(t), n - 2)
res = O[cal] - (a + b * X[cal])
s = np.sqrt(np.sum(res ** 2) / (n - 2))
dw = L.durbin_watson(res)
print('  Y = %.3f X + %.3f (N = %d)' % (b, a, n))
print('  r = %.3f, R2 = %.3f, 조정 R2 = %.3f, F = %.2f, t = %.2f, 양쪽 p = %.2e' % (r, R2, adj, F, t, p))
print('  기울기의 표준오차 %.3f (95%% 구간 %.3f ~ %.3f), 잔차 표준편차 %.3f °C' % (se, b - stats.t.isf(0.025, n - 2) * se, b + stats.t.isf(0.025, n - 2) * se, s))
print('  임계 r(N=%d): 5%% %.3f, 1%% %.3f' % (n, L.crit_r(n, .05), L.crit_r(n, .01)))
print('  Durbin-Watson d = %.3f (2에 가까우면 잔차의 1차 자기상관이 작다; 잔차의 1차 자기상관 %.3f)' % (dw, L.acf1(res)))
rX, rY = L.acf1(X[cal]), L.acf1(O[cal])
ne = L.n_eff(n, rX, rY)
rc = L.crit_r(max(int(round(ne)), 3), 0.01)
print('  1차 자기상관: X %.3f, Y %.3f -> 유효 표본 n_eff = %.1f, 그때의 임계 r(1%%) = %.3f (r = %.3f는 %s)' % (rX, rY, ne, rc, r, '넘는다' if r > rc else '넘지 못한다'))
print('  (비교: 제1권이 옮긴 노백산 변환식은 Y = 2.987 X + 4.829, N = 58, R = 0.757. 이 시연값의 계수는 노백산과 아무 관계가 없다)')

# ---------------------------------------------------------------- 2. 분할 보정·검증
print('\n== 2. 분할 보정·검증 (제1권 11.5.3절의 방식: 1956~1984와 1985~2013)')
A = (years >= 1956) & (years <= 1984)
B = (years >= 1985) & (years <= 2013)
rows = []
for lab, c, v in (('보정 1956~1984 -> 검증 1985~2013', A, B), ('보정 1985~2013 -> 검증 1956~1984', B, A)):
    a2, b2, rc_, se2 = L.linfit(X[c], O[c])
    est = a2 + b2 * X[v]
    obs = O[v]
    cm = O[c].mean()
    re, ce = L.re_ce(obs, est, cm)
    same, diff = L.sign_test(obs, est, cm)
    pst = stats.binomtest(max(same, diff), same + diff, 0.5).pvalue
    rv = float(np.corrcoef(obs, est)[0, 1])
    print('  %s' % lab)
    print('    보정 r = %.3f, 검증 r = %.3f, RE = %.3f, CE = %.3f, 부호 검정 (같은 방향 %d, 다른 방향 %d) 양쪽 p = %.4f' % (rc_, rv, re, ce, same, diff, pst))
    rows.append(dict(lab=lab, r_cal=rc_, r_ver=rv, RE=re, CE=ce, same=same, diff=diff, p=float(pst)))
print('  RE와 CE가 모두 0보다 크면 \"보정 평균을 그냥 쓰는 것\"과 \"검증 평균을 그냥 쓰는 것\"보다 낫다는 뜻이다. 이 두 검증은 58년 안에서의 시험이다.')

# ---------------------------------------------------------------- 3. 복원과 참값 비교
print('\n== 3. 복원(1600~1955)과 참 기후의 비교 (참값을 아는 시연값 자료여서 가능한 점검)')
est_all = a + b * X
rec = est_all.copy()
for lab, sel in (('1600~1955 전체', pre), ('1600~1699', (years >= 1600) & (years <= 1699)), ('1700~1799', (years >= 1700) & (years <= 1799)),
                 ('1800~1899', (years >= 1800) & (years <= 1899)), ('1900~1955', (years >= 1900) & (years <= 1955))):
    ok = sel & ~np.isnan(est_all)
    rt = float(np.corrcoef(est_all[ok], T[ok])[0, 1])
    rmse = float(np.sqrt(np.mean((est_all[ok] - T[ok]) ** 2)))
    # 참값에 대한 RE(보정 기간의 관측 평균 기준)와 CE
    sse = np.sum((T[ok] - est_all[ok]) ** 2)
    re_t = 1 - sse / np.sum((T[ok] - O[cal].mean()) ** 2)
    ce_t = 1 - sse / np.sum((T[ok] - T[ok].mean()) ** 2)
    # 95% 예측 구간에 참값이 들어간 비율
    xbar = X[cal].mean(); sxx = np.sum((X[cal] - xbar) ** 2)
    half = stats.t.isf(0.025, n - 2) * s * np.sqrt(1 + 1 / n + (X[ok] - xbar) ** 2 / sxx)
    cover = float(np.mean(np.abs(T[ok] - est_all[ok]) <= half))
    print('  %-14s 연수 %3d: 참 기후와 r = %.3f, RMSE = %.3f °C, RE(참값) = %.3f, CE(참값) = %.3f, 95%% 예측 구간이 참값을 덮은 비율 %.1f%%, 평균 코어 수 %.0f' % (
        lab, ok.sum(), rt, rmse, re_t, ce_t, 100 * cover, depth[sel].mean()))
print('  참고: 참 기후의 표준편차 %.3f °C, 복원의 표준편차(1600~1955) %.3f °C (복원은 회귀 때문에 변동이 작아진다)' % (T[pre].std(ddof=1), est_all[pre].std(ddof=1)))

# ---------------------------------------------------------------- 4. 표준화 방법과 날짜 오류의 영향
print('\n== 4. 표준화 방법과 날짜 오류가 복원에 미치는 영향 (같은 보정 절차, 참 기후와의 r)')
ids = list(csv.DictReader(open(os.path.join(HERE, 'synth-ids.csv'), encoding='utf-8')))
def chron_from(path, method, **kw):
    y, nm, Xr = L.read_rwl(path)
    I, _ = L.detrend(Xr, method, **kw)
    c, d = L.chron(I, True)
    return c


def calib_and_score(c):
    a_, b_, r_, _ = L.linfit(c[cal], O[cal])
    est = a_ + b_ * c
    ok = pre & ~np.isnan(est)
    return r_, float(np.corrcoef(est[ok], T[ok])[0, 1]), float(np.sqrt(np.mean((est[ok] - T[ok]) ** 2)))
print('  자료 / 표준화          보정 r   복원-참값 r(1600~1955)   RMSE(°C)')
cases = [('참 날짜 / 음의 지수', 'synth-demo-true.rwl', 'ModNegExp', {}),
         ('찾은 것만 고침 / 음의 지수(이 장의 사슬)', 'synth-demo-fixed.rwl', 'ModNegExp', {}),
         ('오류 그대로 / 음의 지수', 'synth-demo-bad.rwl', 'ModNegExp', {}),
         ('찾은 것만 고침 / 스플라인 67%', 'synth-demo-fixed.rwl', 'Spline', {}),
         ('찾은 것만 고침 / 스플라인 32년', 'synth-demo-fixed.rwl', 'Spline', dict(nyrs=32)),
         ('찾은 것만 고침 / 표준화 없음(평균)', 'synth-demo-fixed.rwl', 'Mean', {})]
case_out = []
for lab, f, m, kw in cases:
    c = chron_from(os.path.join(HERE, f), m, **kw)
    r_, rt, rm = calib_and_score(c)
    print('  %-38s %6.3f   %12.3f            %8.3f' % (lab, r_, rt, rm))
    case_out.append(dict(lab=lab, r_cal=r_, r_true=rt, rmse=rm))

# ---------------------------------------------------------------- 5. 냉기와 온기
print('\n== 5. 냉기와 온기 (제1권 11.5.4절의 규칙: 11년 이동평균이 평균 ± 0.5 표준편차를 넘는 연속 기간)')
def ma(v, w=11):
    out = np.full(len(v), np.nan); h = w // 2
    for i in range(h, len(v) - h): out[i] = v[i - h:i + h + 1].mean()
    return out
def periods(v, minlen=7):
    m, sd = np.nanmean(v), np.nanstd(v, ddof=1)
    sm = ma(v)
    cls = np.where(sm < m - 0.5 * sd, -1, np.where(sm > m + 0.5 * sd, 1, 0)); cls[np.isnan(sm)] = 0
    out = []
    i = 0
    while i < len(cls):
        if cls[i] != 0:
            j = i
            while j + 1 < len(cls) and cls[j + 1] == cls[i]: j += 1
            if j - i + 1 >= minlen:
                out.append((int(years[i]), int(years[j]), int(cls[i])))
            i = j + 1
        else:
            i += 1
    return out, cls, (m, sd)
pt, ct, (mt, sdt) = periods(T)
pr, cr, (mr, sdr) = periods(est_all)
print('  참 기후: 평균 %.2f, 표준편차 %.2f, 냉기 %d개, 온기 %d개 (7년 이상)' % (mt, sdt, sum(1 for p_ in pt if p_[2] < 0), sum(1 for p_ in pt if p_[2] > 0)))
print('  복  원 : 평균 %.2f, 표준편차 %.2f, 냉기 %d개, 온기 %d개 (7년 이상)' % (mr, sdr, sum(1 for p_ in pr if p_[2] < 0), sum(1 for p_ in pr if p_[2] > 0)))
print('  연도별 분류(냉기/보통/온기)가 일치한 비율(1606~2008): %.1f%%' % (100 * np.mean(ct[(years >= 1606) & (years <= 2008)] == cr[(years >= 1606) & (years <= 2008)])))
both_cold = np.sum((ct == -1) & (cr == -1)); any_cold = np.sum((ct == -1) | (cr == -1))
both_warm = np.sum((ct == 1) & (cr == 1)); any_warm = np.sum((ct == 1) | (cr == 1))
print('  냉기로 분류된 해: 참 %d년, 복원 %d년, 둘 다 %d년(겹침 %.1f%%); 온기: 참 %d년, 복원 %d년, 둘 다 %d년(겹침 %.1f%%)' % (
    np.sum(ct == -1), np.sum(cr == -1), both_cold, 100 * both_cold / any_cold, np.sum(ct == 1), np.sum(cr == 1), both_warm, 100 * both_warm / any_warm))
print('  참 기후의 냉기·온기 기간(7년 이상): %s' % ', '.join('%d~%d%s' % (a_, b_, '(냉)' if c_ < 0 else '(온)') for a_, b_, c_ in pt))
print('  복원의 냉기·온기 기간(7년 이상):    %s' % ', '.join('%d~%d%s' % (a_, b_, '(냉)' if c_ < 0 else '(온)') for a_, b_, c_ in pr))

# ---------------------------------------------------------------- 6. 자기상관이 있으면 거짓 양성이 늘어난다
print('\n== 6. 자기상관이 있는 두 계열에서 \"유의한\" 상관이 우연히 나오는 비율 (서로 독립인 AR(1) 두 계열, N = 58, 20000번, 시드 11)')
rng = np.random.default_rng(11)
nn = 58
reps = 20000
crit5, crit1 = L.crit_r(nn, 0.05), L.crit_r(nn, 0.01)
print('  임계 r(독립 가정): 5%% %.3f, 1%% %.3f' % (crit5, crit1))
print('  phi    |r| > 5% 임계   |r| > 1% 임계   |r|>0.5의 비율   n_eff(식)')
fp = []
for phi in (0.0, 0.3, 0.5, 0.7, 0.9):
    e1 = rng.normal(size=(reps, nn)); e2 = rng.normal(size=(reps, nn))
    x1 = np.zeros((reps, nn)); x2 = np.zeros((reps, nn))
    x1[:, 0] = e1[:, 0]; x2[:, 0] = e2[:, 0]
    for k in range(1, nn):
        x1[:, k] = phi * x1[:, k - 1] + e1[:, k] * np.sqrt(1 - phi ** 2)
        x2[:, k] = phi * x2[:, k - 1] + e2[:, k] * np.sqrt(1 - phi ** 2)
    xc = x1 - x1.mean(axis=1, keepdims=True); yc = x2 - x2.mean(axis=1, keepdims=True)
    rr = (xc * yc).sum(axis=1) / np.sqrt((xc ** 2).sum(axis=1) * (yc ** 2).sum(axis=1))
    f5, f1, f50 = float(np.mean(np.abs(rr) > crit5)), float(np.mean(np.abs(rr) > crit1)), float(np.mean(np.abs(rr) > 0.5))
    print('  %.1f    %9.1f%%   %9.1f%%   %9.2f%%   %8.1f' % (phi, 100 * f5, 100 * f1, 100 * f50, L.n_eff(nn, phi, phi)))
    fp.append(dict(phi=phi, f5=f5, f1=f1))
print('  (표본의 1차 자기상관이 실제 phi와 다르다는 점, 58년이라는 짧은 기간의 추정 오차는 이 시험에 들어 있다)')

json.dump(dict(years=years.tolist(), est=[round(float(v), 4) for v in est_all], truth=[round(float(v), 4) for v in T],
               obs=[None if np.isnan(v) else round(float(v), 4) for v in O], depth=depth.tolist(), splits=rows, cases=case_out,
               pt=pt, pr=pr, a=a, b=b), open(os.path.join(HERE, 'recon-fig.json'), 'w'))
print('\n저장: recon-fig.json')
