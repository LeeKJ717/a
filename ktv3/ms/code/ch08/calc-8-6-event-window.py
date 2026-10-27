# -*- coding: utf-8 -*-
"""계산 8-6. 4.2 ka 사건을 점(4200)이 아니라 창으로 놓고 7장 보리 표를 다시 본다.
창의 숫자는 Zhang & Zhang(2023)이 4.2 ka BP 사건으로 적은 4200~3900 BP와, 같은 논문의 Delingha 나이테 δ18O 강수 이상치 최저 약 3950 BP이다(본문 추출문에서 확인).
논문의 BP가 보정 연대인지 이 책은 확인하지 못해 cal BP로 두었다. 보리 날짜는 계산 8-1과 같은 7장 Liu 등(2017) 88행이고 보정은 IntCal20이다.
방법은 계산 8-1과 같다(날짜마다 독립 추출, 지역 안의 가장 오래된 값, 20만 번, 시드 20261029).
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'ch07'))
import numpy as np, c14lib as c, c14data as d
rng = np.random.default_rng(20261029); N = 200000
def reg(r):
    g = r[0]; return '중앙아시아' if g.startswith('중앙아시아') else ('중·동부 중국' if g.startswith('중·동부') else g)
regs = {}
for r in d.LIU: regs.setdefault(reg(r), []).append(r)
order = ['북서인도', '갠지스', '남인도', '티베트', '청해', '감숙', '중앙아시아', '신강', '중·동부 중국']
HI, LO, MID = 4200, 3900, 3950
out = {}
print('창 %d~%d cal BP, Delingha 최저 %d. 지역별 가장 이른 보리: 창보다 오램 / 창 안 / 창보다 젊음 / 3950보다 오램' % (HI, LO, MID))
print('%-10s %3s %10s %8s %10s %12s   가장 이른 값 95%% 구간' % ('지역', 'n', '>4200', '창 안', '<3900', 'P(>3950)'))
for g in order:
    rows = regs[g]
    cds = [np.cumsum(c.calibrate(r[3], r[4])) for r in rows]
    S = np.stack([c.GRID[np.minimum(np.searchsorted(cd, rng.random(N)), len(c.GRID) - 1)] for cd in cds])
    e = S.max(axis=0)
    a = float((e > HI).mean()); b = float(((e <= HI) & (e >= LO)).mean()); y = float((e < LO).mean()); m = float((e > MID).mean())
    lo, md, hi = np.percentile(e, [2.5, 50, 97.5])
    # 날짜 하나하나의 질량이 창 안에 든 몫의 평균
    inwin = float(np.mean([c.calibrate(r[3], r[4])[(c.GRID <= HI) & (c.GRID >= LO)].sum() for r in rows]))
    out[g] = dict(n=len(rows), first_older_than_4200=a, first_in_window=b, first_younger_than_3900=y, P_first_older_3950=m, dates_mass_in_window_mean=inwin, first_calBP=[float(lo), float(md), float(hi)])
    print('%-10s %3d %10.3f %8.3f %10.3f %12.3f   %d ~ %d   (날짜 질량 평균 중 창 안 %.3f)' % (g, len(rows), a, b, y, m, lo, hi, inwin))
# 전체 88행에서 날짜 하나하나의 질량이 창 안에 든 몫
allp = [c.calibrate(r[3], r[4])[(c.GRID <= HI) & (c.GRID >= LO)].sum() for g in order for r in regs[g]]
print('88행 전체: 날짜 하나하나의 질량 중 창(4200~3900) 안 평균 %.3f, 창 안에 질량 0.5 이상인 날짜 %d행' % (np.mean(allp), sum(1 for x in allp if x >= 0.5)))
out['all'] = dict(mean_mass_in_window=float(np.mean(allp)), n_rows=len(allp), n_mass_ge_half=int(sum(1 for x in allp if x >= 0.5)))
json.dump(out, open(os.path.join(HERE, 'calc-8-6-event-window.json'), 'w'), ensure_ascii=False, indent=1)
