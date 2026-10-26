# -*- coding: utf-8 -*-
"""계산 7-1. 논문 표의 14C 나이를 IntCal20으로 다시 보정해 논문이 낸 95.4% 구간과 대조한다.
목적: (1) 이 책의 보정 코드가 논문의 구간을 되풀이하는가, (2) 옮김 오류와 논문 안의 불일치를 찾는다."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, c14lib as c, c14data as d

def row(age, err):
    p = c.calibrate(age, err); a, b = c.outer(p)
    return c.to_year(b), c.to_year(a), p        # 오래된 쪽(큰 cal BP), 젊은 쪽

out = {}
for name, tab, kind in (('Liu2017', d.LIU, 'liu'), ('Deng2019', d.DENG, 'deng'), ('Begash2007', d.BEGASH, 'beg')):
    diffs = []; bad = []
    print('== %s: %d행' % (name, len(tab)))
    for r in tab:
        if kind == 'liu':
            region, site, lab, age, err, s, e = r; ps, pe = -s, -e      # 논문 구간(기원전 양수 -> 부호 있는 연도)
        elif kind == 'deng':
            site, lab, ctx, mat, age, err, ps, pe = r
        else:
            lab, ph, age, err, ps, pe = r
        ms, me, p = row(age, err)
        ds, de = ms - ps, me - pe          # 이 책 - 논문 (양수 = 이 책이 더 늦다)
        diffs.append((ds, de))
        flag = '' if max(abs(ds), abs(de)) <= 60 else '  <-- 60년 초과'
        if flag: bad.append((lab, age, err, ps, pe, float(ms), float(me)))
        print('%-14s %5d±%-4d 논문 %6d..%-6d  이 책 %6d..%-6d  차 %+5d/%+5d%s' % (lab, age, err, ps, pe, ms, me, ds, de, flag))
    D = np.array(diffs)
    stats = dict(n=len(tab), mean_start=float(D[:,0].mean()), mean_end=float(D[:,1].mean()),
                 med_abs_start=float(np.median(abs(D[:,0]))), med_abs_end=float(np.median(abs(D[:,1]))),
                 max_abs=float(abs(D).max()), n_over60=len(bad),
                 n_within30_both=int((abs(D)<=30).all(axis=1).sum()))
    print('요약', json.dumps(stats, ensure_ascii=False))
    out[name] = dict(stats=stats, over60=bad)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-1-recalib.json'), 'w'), ensure_ascii=False, indent=1)
