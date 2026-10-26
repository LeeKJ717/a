# -*- coding: utf-8 -*-
"""계산 7-2. 지역별 '가장 이른 보리 직접 연대'의 불확실성과 지역 사이 순서 확률 (Liu 등 2017 표 1의 옮긴 88행).
방법: 날짜마다 IntCal20 보정 확률분포에서 표본을 뽑고(독립), 지역 안에서 가장 오래된 표본을 그 지역의 '가장 이른 값'으로 삼는다. 20만 번 되풀이.
주의: 표 1이 그 지역의 모든 날짜를 담았는지 이 책은 확인하지 못했다. 아래 값은 '옮긴 표 안에서의' 값이다."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, c14lib as c, c14data as d
rng = np.random.default_rng(20261026)
N = 200000
def region_of(r):
    g = r[0]
    return '중앙아시아' if g.startswith('중앙아시아') else ('중·동부 중국' if g.startswith('중·동부') else g)
regs = {}
for r in d.LIU: regs.setdefault(region_of(r), []).append(r)
order = ['북서인도', '갠지스', '남인도', '티베트', '청해', '감숙', '중앙아시아', '신강', '중·동부 중국']
cdf = {}
for r in d.LIU:
    p = c.calibrate(r[3], r[4]); cdf[r[2]] = np.cumsum(p)
def draw(lab, n):
    u = rng.random(n); return c.GRID[np.minimum(np.searchsorted(cdf[lab], u), len(c.GRID) - 1)]
E = {}; res = {}
for g in order:
    rows = regs[g]; n = len(rows)
    S = np.stack([draw(r[2], N) for r in rows])           # cal BP, 큰 값이 오래됨
    e = S.max(axis=0); who = S.argmax(axis=0)
    E[g] = e
    lo, md, hi = np.percentile(e, [2.5, 50, 97.5])
    pw = {rows[i][2] + ' ' + rows[i][1]: float((who == i).mean()) for i in range(n)}
    top = sorted(pw.items(), key=lambda kv: -kv[1])[:3]
    # 그 지역에서 중앙값이 가장 오래된 날짜 한 개의 단독 구간과 비교
    med = [c.median(c.calibrate(r[3], r[4])) for r in rows]; j = int(np.argmax(med))
    p1 = c.calibrate(rows[j][3], rows[j][4]); a1, b1 = c.outer(p1)
    res[g] = dict(n=n, earliest_median_BC=float(c.to_year(md)), earliest_lo_BC=float(c.to_year(hi)), earliest_hi_BC=float(c.to_year(lo)),
                  oldest_single=rows[j][2] + ' ' + rows[j][1], single_range_BC=[float(c.to_year(b1)), float(c.to_year(a1))], top_oldest=top)
    print('%-10s n=%2d  가장 이른 값: 중앙 %s, 95%% %s ~ %s | 단독 최고령 %s %s ~ %s | 가장 오래된 후보 확률 %s' % (
        g, n, c.fmt_year(c.to_year(md)), c.fmt_year(c.to_year(hi)), c.fmt_year(c.to_year(lo)), res[g]['oldest_single'],
        c.fmt_year(res[g]['single_range_BC'][0]), c.fmt_year(res[g]['single_range_BC'][1]), [(k, round(v, 3)) for k, v in top]))
print()
print('P(행 지역의 가장 이른 값이 열 지역보다 오래됨), N=%d' % N)
M = np.zeros((len(order), len(order)))
for i, a in enumerate(order):
    for j, b in enumerate(order):
        M[i, j] = (E[a] > E[b]).mean() if i != j else np.nan
print('%-10s' % '' + ''.join('%8s' % b[:5] for b in order))
for i, a in enumerate(order):
    print('%-10s' % a + ''.join('%8.3f' % M[i, j] if i != j else '%8s' % '-' for j in range(len(order))))
# 청해 안에서 가장 이른 값과 감숙 안에서 가장 이른 값의 차(년)
dq = (E['청해'] - E['감숙'])
print('\n청해 가장 이른 값 - 감숙 가장 이른 값(년): 중앙 %.0f, 95%% %.0f ~ %.0f' % tuple([np.median(dq)] + list(np.percentile(dq, [2.5, 97.5]))))
dn = (E['북서인도'] - E['청해'])
print('북서인도 - 청해(년): 중앙 %.0f, 95%% %.0f ~ %.0f' % tuple([np.median(dn)] + list(np.percentile(dn, [2.5, 97.5]))))
dc = (E['청해'] - E['중앙아시아'])
print('청해 - 중앙아시아(년): 중앙 %.0f, 95%% %.0f ~ %.0f' % tuple([np.median(dc)] + list(np.percentile(dc, [2.5, 97.5]))))
res['matrix'] = dict(order=order, P=[[None if np.isnan(x) else float(x) for x in row] for row in M])
res['diffs'] = dict(qinghai_minus_gansu=[float(np.median(dq))] + [float(x) for x in np.percentile(dq, [2.5, 97.5])],
                    nwindia_minus_qinghai=[float(np.median(dn))] + [float(x) for x in np.percentile(dn, [2.5, 97.5])],
                    qinghai_minus_centralasia=[float(np.median(dc))] + [float(x) for x in np.percentile(dc, [2.5, 97.5])])
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-2-earliest.json'), 'w'), ensure_ascii=False, indent=1)
