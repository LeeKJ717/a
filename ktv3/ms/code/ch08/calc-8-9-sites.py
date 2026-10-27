# -*- coding: utf-8 -*-
"""계산 8-9. 유적 수의 변화를 두 논문의 숫자로 다시 계산한다. 숫자는 모두 본문 추출문에서 옮긴 것이며 원문 표 대조가 필요하다.
Zhang & Zhang(2023): 4.2 ka BP 사건 4200~3900 BP. 문화별 유적 수 Majiayao→Qijia 1,036→1,795, Longshan→Yueshi 1,409→314. 문화 연대 Majiayao 5.8~4, Qijia 4~3.6, Longshan 4.6~3.9, Yueshi 3.9~3.5 ka BP.
    4100~4000 구간에서 끝난 유적 2,445, 새로 생긴 유적 2,109.
Hosner 등(2016): 51,074곳(기원전 약 8000~500년, 27개 지역). 칭하이 3000~2500 BC 198, 2500~2200 BC 49, 2200~2000 BC 307. 북중국 밀도 약 30(3750 BC), 45(2350 BC), 80(1750 BC) 곳/1000 km².
    산시 서주 134 → 동주 1,680, 간쑤 서주 115 → 동주 14, 섬서 서주 1,008 → 동주 768, 내몽골 동부 1,103 → 4,782(전환 시기 미확인).
논문의 BP가 보정 연대인지 확인하지 못했다. 유적 수는 조사의 강도와 보존에 좌우되며 이 계산이 그것을 보정하지 않는다.
"""
import os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
out = {}
def pct(a, b): return (b - a) / a * 100
print('(a) Zhang & Zhang(2023)')
cult = {'Majiayao': (1036, 5800, 4000), 'Qijia': (1795, 4000, 3600), 'Longshan': (1409, 4600, 3900), 'Yueshi': (314, 3900, 3500)}
for k, (n, a, b) in cult.items():
    print('  %-9s %5d곳, %d~%d BP(%d년), 100년당 %.1f곳' % (k, n, a, b, a - b, n / ((a - b) / 100)))
    out[k] = dict(n=n, years=a - b, per_century=n / ((a - b) / 100))
print('  Majiayao→Qijia: 유적 수 배율 %.3f (%+.1f%%), 100년당 배율 %.2f' % (1795 / 1036, pct(1036, 1795), out['Qijia']['per_century'] / out['Majiayao']['per_century']))
print('  Longshan→Yueshi: 유적 수 배율 %.3f (%+.1f%%), 100년당 배율 %.2f' % (314 / 1409, pct(1409, 314), out['Yueshi']['per_century'] / out['Longshan']['per_century']))
print('  끝난 2,445 대 새로 생긴 2,109: 새 유적은 끝난 유적의 %.3f배(%+.1f%%)  [논문: "약 14%% 적다"]' % (2109 / 2445, pct(2445, 2109)))
out['ended_vs_new'] = 2109 / 2445
print('  Longshan(4.6~3.9)과 Majiayao(5.8~4)·Qijia(4~3.6)는 시기가 겹치지만 지역이 다르다(간쑤·칭하이 대 산둥). 같은 사건 창 안에서 한 곳은 늘고 한 곳은 줄었다.')
print('(b) Hosner 등(2016)')
q = [(198, 3000, 2500), (49, 2500, 2200), (307, 2200, 2000)]
for n, a, b in q:
    print('  칭하이 %d~%d BC (%d년): %d곳, 100년당 %.1f곳, cal BP로 %d~%d' % (a, b, a - b, n, n / ((a - b) / 100), a + 1949, b + 1949))
out['qinghai_per_century'] = [n / ((a - b) / 100) for n, a, b in q]
print('  2500~2200 BC 대비 2200~2000 BC 100년당 배율 %.1f; 2200~2000 BC(cal BP %d~%d)는 4200~3900 창과 겹침 %d년(창 300년 중)' % (out['qinghai_per_century'][2] / out['qinghai_per_century'][1], 2200 + 1949, 2000 + 1949, max(0, min(4149, 4200) - max(3949, 3900))))
ov = max(0, min(4149, 4200) - max(3949, 3900))
print('  (3949~4149 cal BP 와 3900~4200 의 겹침: %d년)' % ov)
dens = [(3750, 30), (2350, 45), (1750, 80)]
for (t1, d1), (t2, d2) in zip(dens, dens[1:]):
    yrs = t1 - t2
    print('  북중국 밀도 %d BC %d → %d BC %d (곳/1000 km²): 배율 %.2f, 연 증가율 %.3f%% (%d년)' % (t1, d1, t2, d2, d2 / d1, (math.log(d2 / d1) / yrs) * 100, yrs))
    out['dens_%d_%d' % (t1, t2)] = dict(ratio=d2 / d1, rate_pct_per_yr=(math.log(d2 / d1) / yrs) * 100)
for nm, a, b in [('산시 서주→동주', 134, 1680), ('간쑤 서주→동주', 115, 14), ('섬서 서주→동주', 1008, 768), ('내몽골 동부', 1103, 4782)]:
    print('  %-12s %5d → %5d : 배율 %.2f (%+.1f%%)' % (nm, a, b, b / a, pct(a, b)))
    out[nm] = dict(a=a, b=b, ratio=b / a)
print('  같은 서주→동주 전환에서 산시는 %.1f배 늘고 간쑤는 %.2f배, 섬서는 %.2f배이다. 방향이 지역마다 다르다.' % (1680 / 134, 14 / 115, 768 / 1008))
json.dump(out, open(os.path.join(HERE, 'calc-8-9-sites.json'), 'w'), ensure_ascii=False, indent=1)
