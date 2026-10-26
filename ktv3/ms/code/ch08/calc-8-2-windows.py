# -*- coding: utf-8 -*-
"""계산 8-2. 논문이 적은 기후 창(window)과 낟알 연대의 겹침. 모든 창의 숫자는 논문이 적은 것이고(출처는 아래 W), 낟알 확률은 이 책의 IntCal20 보정이다.
창: Li 등(2022)이 쓴 시추 코어 기록 '6200~2900 cal BP 비교적 습윤, 이후 건조 증가, 약 1100 cal BP 정점'(중국 서부 황토 고원의 Zhuanglang 일대 연구구역). 기록의 지점과 낟알 유적이 같은 곳이 아니다.
계산: (a) Liu 보리 88행과 Begash 숯 34행에서 각 날짜 확률이 습윤 창 안에, 창보다 젊은 쪽(2900 cal BP보다 젊음)에 든 질량의 지역별 평균
      (b) 논문들의 구간 서술이 습윤 창과 겹치는 길이(년)와 4200 cal BP와의 위치 관계
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'ch07'))
import numpy as np, c14lib as c, c14data as d
WET = (2900, 6200)
def reg(r):
    g = r[0]; return '중앙아시아' if g.startswith('중앙아시아') else ('중·동부 중국' if g.startswith('중·동부') else g)
regs = {}
for r in d.LIU: regs.setdefault(reg(r), []).append(r)
order = ['북서인도', '갠지스', '남인도', '티베트', '청해', '감숙', '중앙아시아', '신강', '중·동부 중국']
G = c.GRID; inw = (G >= WET[0]) & (G <= WET[1]); old = G > WET[1]; young = G < WET[0]
res = {}
print('(a) 날짜 확률의 평균 질량: 습윤 창(%d~%d cal BP) 안 / 창보다 오래됨 / 창보다 젊음' % WET)
for g in order:
    ps = [c.calibrate(r[3], r[4]) for r in regs[g]]
    a = [float(np.mean([p[m].sum() for p in ps])) for m in (inw, old, young)]
    res[g] = dict(n=len(ps), inside=a[0], older=a[1], younger=a[2])
    print('%-10s n=%2d  안 %.3f  오래됨 %.3f  젊음 %.3f' % (g, len(ps), *a))
ps = [c.calibrate(r[3], r[4]) for r in regs['청해'] + regs['감숙']]
a = [float(np.mean([p[m].sum() for p in ps])) for m in (inw, old, young)]
res['청해+감숙'] = dict(n=len(ps), inside=a[0], older=a[1], younger=a[2]); print('청해+감숙   n=%2d  안 %.3f  오래됨 %.3f  젊음 %.3f' % (len(ps), *a))
ps = [c.calibrate(r[2], r[3]) for r in d.BEGASH]
a = [float(np.mean([p[m].sum() for p in ps])) for m in (inw, old, young)]
res['Begash 숯'] = dict(n=len(ps), inside=a[0], older=a[1], younger=a[2]); print('Begash 숯   n=%2d  안 %.3f  오래됨 %.3f  젊음 %.3f' % (len(ps), *a))
print()
print('(b) 논문 구간 서술(cal BP로 적힌 것만; BP 표기가 cal BP인지 불분명한 것은 비고)과 습윤 창의 겹침, 4200과의 관계')
S = [('Zhou 등(2020) Tongtian 동굴 점유', 3200, 5200, 'cal BP'),
     ('Ren 등(2021) 기장만(Gansu-Qinghai)', 4000, 5900, 'BP(보정 여부 초록에 없음)'),
     ('Ren 등(2021) 보리·밀 보조 작물기', 3600, 4000, 'BP(보정 여부 초록에 없음)'),
     ('Ren 등(2021) 보리 중요성 증가기', 2100, 3600, 'BP(보정 여부 초록에 없음)'),
     ('Ren 등(2021) 기장 중심기(Jinchankou)', 3700, 4100, 'BP(보정 여부 초록에 없음)'),
     ('Spengler 등(2014b) Tasbas 2a', 1490+1949-1950+0, 1260+1949-1950+0, '기원전 1490~1260년에서 옮김')]
S.append(('Cui 등(2013) 북방 유목 단계(제1권 11장)', 2500, 3000, 'BP(보정 여부 제1권 표에 없음)'))
S[-2] = ('Spengler 등(2014b) Tasbas 2a', 1260 + 1949, 1490 + 1949, '기원전 1490~1260년을 cal BP로 옮김(BC+1949)')
rows = []
for nm, lo, hi, note in S:
    ov = max(0, min(hi, WET[1]) - max(lo, WET[0])); w = hi - lo
    rel = '4200을 포함' if lo <= 4200 <= hi else ('4200보다 젊음' if hi < 4200 else '4200보다 오래됨')
    rows.append(dict(name=nm, lo=lo, hi=hi, width=w, overlap_years=ov, overlap_share=ov / w, rel4200=rel, note=note))
    print('%-34s %5d~%5d cal BP 폭 %4d  습윤 창과 겹침 %4d년(%.2f)  %s  [%s]' % (nm, lo, hi, w, ov, ov / w, rel, note))
res['intervals'] = rows
json.dump(res, open(os.path.join(HERE, 'calc-8-2-windows.json'), 'w'), ensure_ascii=False, indent=1)
