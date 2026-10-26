# -*- coding: utf-8 -*-
"""실습 9-8~9-10. 층서 순서 제약을 둔 단순 베이즈 연대 모형.
(가) 격자 사후분포가 닫힌 식(가중 평균)과 맞는지 확인 (나) 제1권 오쿠노 등(2010)의 날짜에 이상치 모형과 순서 제약 적용
(다) 순서가 결과를 바꾸는 시연값 하나 (라) 기각 표집을 독립 알고리즘(Metropolis)으로 교차 확인.
14C 나이는 보정하지 않은 BP 값 그대로 쓴다(보정 곡선을 쓰지 않는다). 이것은 OxCal 같은 도구의 대체가 아니라 원리를 보이는 모형이다.
실행: python3 ex3-ordered.py > ex3-ordered.log"""
import os, sys, json, platform, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy
from scipy import stats
import tephralib as T

print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
rng = np.random.default_rng(20261026)
OUT = {}

def moments(S):
    return S.mean(axis=0), S.std(axis=0, ddof=1)

def hpd(x, mass=0.954):
    x = np.sort(x); n = len(x); k = int(np.ceil(mass * n))
    w = x[k - 1:] - x[:n - k + 1]
    i = int(np.argmin(w))
    return float(x[i]), float(x[i + k - 1])

print('\n[실습 9-8] 격자 사후분포가 가중 평균과 맞는가 (이상치 없음 q=0, 순서 제약 없음)')
grid = np.arange(3000.0, 14000.0, 0.5)
cases = {'U-2 네 날짜': ([4910, 4965, 4945, 4940], [35] * 4),
         'U-4 네 날짜(11840 제외)': ([12165, 12030, 12090, 12095], [40] * 4),
         '쉬운 예 100±10, 120±20(격자 0~300)': ([100, 120], [10, 20])}
for nm, (x, s) in cases.items():
    g = np.arange(0.0, 300.0, 0.01) if '쉬운' in nm else grid
    post, _ = T.grid_posterior(x, s, g, q=0.0)
    m = float((post * g).sum()); sd = float(np.sqrt((post * (g - m) ** 2).sum()))
    wm, we = T.wmean(x, s)
    print('  %-34s 격자 평균 %10.3f, 표준편차 %7.3f | 가중 평균 %10.3f, 오차 %7.3f | 차이 %.2e, %.2e' % (nm, m, sd, wm, we, m - wm, sd - we))

print('\n[실습 9-9] 제1권 오쿠노 등(2010)의 날짜: 이상치 모형과 순서 제약 (14C 나이, BP, 보정하지 않음)')
LAY = [('U-4(가장 오래됨)', [12165, 11840, 12030, 12090, 12095], [40, 45, 40, 40, 40]),
       ('U-3', [7525, 8030], [35, 35]),
       ('U-2(가장 젊음)', [4910, 4965, 4945, 4940, 4710], [35, 35, 35, 35, 30])]
print('  모형: 층마다 참 나이 theta는 균일 사전분포. 날짜는 확률 1-q로 N(theta, s^2), 확률 q로 N(theta, s^2+1000^2)(이상치).')
print('  층서 순서: theta(U-4) > theta(U-3) > theta(U-2).')
tab9 = {}
for q in (0.0, 0.1):
    posts, outs = [], []
    print('\n  --- 이상치 사전확률 q = %.2f ---' % q)
    for nm, x, s in LAY:
        p, po = T.grid_posterior(x, s, grid, q=q)
        posts.append(p); outs.append(po)
        m = float((p * grid).sum()); sd = float(np.sqrt((p * (grid - m) ** 2).sum()))
        print('  %-18s 순서 없이: 평균 %9.1f, 표준편차 %6.1f, 최빈 %9.1f%s' % (nm, m, sd, grid[p.argmax()],
              ('' if q == 0 else '; 날짜별 이상치 사후확률 ' + ' '.join('%.3f' % v for v in po))))
    if q > 0:
        for (nm, _, _), p in zip(LAY, posts):
            loc = [(grid[i], p[i]) for i in range(1, len(grid) - 1) if p[i] > p[i - 1] and p[i] >= p[i + 1]]
            big = [(a, b) for a, b in loc if b > 0.01 * p.max()]
            print('  %-18s 사후밀도의 국소 최댓값(최대의 1%% 넘는 것): %s' % (nm, ', '.join('%.1f(상대높이 %.3f)' % (a, b / p.max()) for a, b in big)))
    S, passrate = T.ordered_samples(posts, grid, 2_000_000, rng)
    mm, ss = moments(S)
    print('  순서 제약 통과 비율 %.5f (표본 %d개 중 %d개 남음)' % (passrate, 2_000_000, len(S)))
    for k, (nm, _, _) in enumerate(LAY):
        lo, hi = hpd(S[:, k])
        print('  %-18s 순서 있음: 평균 %9.1f, 표준편차 %6.1f, 95.4%% 최고밀도구간 %9.1f ~ %9.1f' % (nm, mm[k], ss[k], lo, hi))
    tab9['q%.2f' % q] = dict(pass_rate=passrate, mean=mm.tolist(), sd=ss.tolist(), outlier=[o.tolist() for o in outs])

print('\n  해석: 세 층의 나이가 서로 2,900년 이상 떨어져 있어 순서 제약은 아무 것도 바꾸지 않는다(통과 비율 1).')
print('  순서 제약이 일을 하려면 층의 나이가 오차 안에서 겹쳐야 한다. 아래 시연값이 그 경우이다.')
OUT['okuno'] = tab9

print('\n[실습 9-10] 순서가 결과를 바꾸는 시연값 (모두 이 책이 정한 가상의 14C 나이, 보정하지 않음)')
DEMO = [('L1(가장 오래됨)', [3010.0], [50.0]),
        ('L2', [3035.0, 3000.0], [50.0, 50.0]),
        ('L3(가장 젊음)', [2985.0], [50.0])]
g2 = np.arange(2500.0, 3500.0, 0.25)
posts = [T.grid_posterior(x, s, g2, q=0.0)[0] for _, x, s in DEMO]
free_m = [float((p * g2).sum()) for p in posts]
free_s = [float(np.sqrt((p * (g2 - m) ** 2).sum())) for p, m in zip(posts, free_m)]
t0 = time.time()
N2 = 4_000_000
S, pr = T.ordered_samples(posts, g2, N2, rng)
t_rej = time.time() - t0
mm, ss = moments(S)
print('  입력: ' + '; '.join('%s %s' % (nm, ', '.join('%d±%d' % (a, b) for a, b in zip(x, s))) for nm, x, s in DEMO))
print('  순서 없이 (독립 사후분포):  ' + '; '.join('%s %.1f ± %.1f' % (d[0][:2], m, s) for d, m, s in zip(DEMO, free_m, free_s)))
print('  순서 제약 통과 비율 %.5f (독립 균일 사전분포에서 세 층의 순서가 맞을 사전확률은 1/6 = %.5f)' % (pr, 1 / 6))
print('  통과 비율 / (1/6) = %.3f  (순서 제약을 둔 모형 대 두지 않은 모형의 베이즈 인자와 같은 꼴. 사전 가정에 의존)' % (pr * 6))
print('  순서 있음 (기각 표집, %d개 남음, %.1f초): ' % (len(S), t_rej) + '; '.join('%s %.1f ± %.1f' % (d[0][:2], m, s) for d, m, s in zip(DEMO, mm, ss)))
for k, d in enumerate(DEMO):
    lo, hi = hpd(S[:, k]); flo, fhi = hpd(T.sample_grid(posts[k], g2, 400000, rng))
    print('    %-16s 95.4%% 구간: 순서 없이 %.0f~%.0f (폭 %.0f), 순서 있음 %.0f~%.0f (폭 %.0f)' % (d[0], flo, fhi, fhi - flo, lo, hi, hi - lo))
# 독립 알고리즘: Metropolis
def logpost(th):
    if not (th[0] > th[1] > th[2]): return -np.inf
    lp = 0.0
    for t, (_, x, s) in zip(th, DEMO):
        lp += stats.norm.logpdf(np.array(x), t, np.array(s)).sum()
    return lp
def mh(n, seed, step=25.0):
    r = np.random.default_rng(seed)
    th = np.array([3050.0, 3000.0, 2950.0]); lp = logpost(th)
    out = np.empty((n, 3)); acc = 0
    for i in range(n):
        prop = th + r.normal(0, step, 3)
        lq = logpost(prop)
        if np.log(r.random()) < lq - lp:
            th, lp = prop, lq; acc += 1
        out[i] = th
    return out, acc / n
t0 = time.time()
chains = []
for sd_ in (11, 12, 13, 14):
    c, a = mh(150000, sd_)
    chains.append(c[10000:])
print('  Metropolis 4개 사슬(각 15만, 앞 1만 버림, %.1f초): 수락률 약 %.2f' % (time.time() - t0, a))
M = np.concatenate(chains); m3, s3 = moments(M)
print('  Metropolis: ' + '; '.join('%s %.1f ± %.1f' % (d[0][:2], m, s) for d, m, s in zip(DEMO, m3, s3)))
print('  기각 표집과의 평균 차이: ' + ', '.join('%.2f' % (a - b) for a, b in zip(m3, mm)) + ' ; 표준편차 차이: ' + ', '.join('%.2f' % (a - b) for a, b in zip(s3, ss)))
cm = np.array([c.mean(axis=0) for c in chains])
print('  사슬 사이 평균의 범위(층별): ' + ', '.join('%.2f' % (cm[:, k].max() - cm[:, k].min()) for k in range(3)))
OUT['demo'] = dict(free_mean=free_m, free_sd=free_s, mean=mm.tolist(), sd=ss.tolist(), pass_rate=pr, mh_mean=m3.tolist(), mh_sd=s3.tolist())
# 그림용 밀도(1년 칸)
edges = np.arange(2800, 3251, 5.0)
dens = {}
for k in range(3):
    h, _ = np.histogram(S[:, k], bins=edges, density=True)
    fd = np.interp(0.5 * (edges[1:] + edges[:-1]), g2, posts[k] / (g2[1] - g2[0]))
    dens[k] = dict(x=(0.5 * (edges[1:] + edges[:-1])).tolist(), ordered=h.tolist(), free=fd.tolist())
OUT['demo_dens'] = dens
json.dump(OUT, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex3.json'), 'w'))
print('\n결과 저장: results/ex3.json')
