# -*- coding: utf-8 -*-
"""계산 7-1b. 논문이 낸 95.4% 구간 안에 이 책의 IntCal20 보정 확률이 얼마나 들어가는가, 그리고 반대 방향의 점검.
논문 구간이 맞다면 그 안에 든 이 책의 확률 질량은 0.954 근처여야 한다(보정 곡선 판이 다르면 줄어든다)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, c14lib as c, c14data as d

def mass_in(p, y0, y1):
    """부호 있는 연도 y0<=y<=y1 안의 질량. GRID(cal BP)를 연도로 바꿔 더한다."""
    yr = c.to_year(c.GRID)
    m = (yr >= y0 - 0.5) & (yr <= y1 + 0.5)
    return float(p[m].sum())

res = {}
for name, tab, kind in (('Liu2017', d.LIU, 'liu'), ('Deng2019', d.DENG, 'deng'), ('Begash2007', d.BEGASH, 'beg')):
    ms = []; low = []
    for r in tab:
        if kind == 'liu': region, site, lab, age, err, s, e = r; ps, pe = -s, -e
        elif kind == 'deng': site, lab, ctx, mat, age, err, ps, pe = r
        else: lab, ph, age, err, ps, pe = r
        p = c.calibrate(age, err); m = mass_in(p, ps, pe); ms.append(m)
        if m < 0.80: low.append((lab, age, err, ps, pe, round(m, 3)))
    ms = np.array(ms)
    res[name] = dict(n=len(tab), median=float(np.median(ms)), min=float(ms.min()), n_ge90=int((ms >= 0.90).sum()), n_lt80=len(low), low=low)
    print(name, json.dumps(res[name], ensure_ascii=False))
# Liu 2017 본문과 표가 다른 한 줄: Zhaogezhuang Beta-427237 2650±30
p = c.calibrate(2650, 30)
print('Zhaogezhuang 2650±30: 표 구간 895~791 BC 안의 질량 %.3f, 본문 구간 895~751 BC 안의 질량 %.3f' % (mass_in(p, -895, -791), mass_in(p, -895, -751)))
print('  이 책의 95.4% 구간들(HPD):', [(float(c.to_year(b)), float(c.to_year(a)), round(float(m), 3)) for a, b, m in c.hpd(p)])
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-1b-mass.json'), 'w'), ensure_ascii=False, indent=1)
