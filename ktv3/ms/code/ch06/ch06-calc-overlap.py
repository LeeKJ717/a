# -*- coding: utf-8 -*-
"""6장 계산 6-4 ~ 6-6: 구간 겹침 행렬, 지역별 방향 집계와 Fisher 검정, 두 펄스 맞춤.
입력은 ch06-records.py. 실행: python3 ch06-calc-overlap.py (numpy, scipy)"""
import json, math, itertools, sys, os
import numpy as np
from scipy.stats import fisher_exact
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('rec', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ch06-records.py'))
rec = importlib.util.module_from_spec(spec); spec.loader.exec_module(rec)
R = {r['id']: r for r in rec.R}
out = {}

def ov(a, b):
    return max(0, min(a['start'], b['start']) - max(a['end'], b['end']))

# ------------------------------------------------------------------ 계산 6-4
print('== 계산 6-4: 건조로 읽힌 기록들의 구간 겹침 ==')
dry_ids = ['Hulun', 'Dali', 'Daihai', 'Hunsh', 'Dongge', 'Gol', 'GOman', 'Roberts', 'Kotla', 'Altai']
print('구간 기록(점이 아닌 것) %d개: %s' % (len(dry_ids), dry_ids))
for i in dry_ids:
    r = R[i]; print('  %-8s %5d ~ %5d (%3d년) %s %s' % (i, r['start'], r['end'], r['start'] - r['end'], r['site'], r['src']))
# 전체 공통 구간
st = min(R[i]['start'] for i in dry_ids); en = max(R[i]['end'] for i in dry_ids)
print('\n열 개 건조 구간의 공통 부분: %d ~ %d = %d년 (시작은 가장 젊은 시작, 끝은 가장 오래된 끝)' % (st, en, max(0, st - en)))
out['6-4-all10'] = dict(start=st, end=en, years=max(0, st - en))
for drop, nm in ((['Roberts', 'Altai', 'Dongge'], '지중해·알타이·동거 제외'), (['Altai'], '알타이 제외'), (['GOman'], '오만만 제외'), (['GOman', 'Altai'], '오만만·알타이 제외')):
    ids = [i for i in dry_ids if i not in drop]
    st = min(R[i]['start'] for i in ids); en = max(R[i]['end'] for i in ids)
    print('%-22s 공통 부분 %d ~ %d = %d년 (기록 %d개)' % (nm, st, en, max(0, st - en), len(ids)))
    out['6-4-' + nm] = dict(start=st, end=en, years=max(0, st - en), n=len(ids))
# 한 기록씩 빼는 민감도
print('\n한 기록씩 빼고 공통 부분을 다시 구하기(10개 기록):')
sens = {}
for d in dry_ids:
    ids = [i for i in dry_ids if i != d]
    st = min(R[i]['start'] for i in ids); en = max(R[i]['end'] for i in ids)
    sens[d] = max(0, st - en)
    print('  %-8s 뺌 -> %3d년' % (d, sens[d]))
out['6-4-sens'] = sens
# 쌍별 겹침(년)과 짧은 쪽 대비 비율
print('\n쌍별 겹침(년) / 짧은 구간 길이:')
M = np.zeros((len(dry_ids), len(dry_ids)))
for a, b in itertools.combinations(range(len(dry_ids)), 2):
    A, B = R[dry_ids[a]], R[dry_ids[b]]
    o = ov(A, B); sh = min(A['start'] - A['end'], B['start'] - B['end'])
    M[a, b] = M[b, a] = o / sh if sh else float('nan')
print('       ' + ' '.join('%7s' % i[:6] for i in dry_ids))
for a in range(len(dry_ids)):
    print('%-7s' % dry_ids[a][:7] + ' '.join(('%7.2f' % M[a, b]) if a != b else '   --  ' for b in range(len(dry_ids))))
out['6-4-matrix'] = dict(ids=dry_ids, m=M.tolist())
mean_pair = float(np.nanmean(M[np.triu_indices(len(dry_ids), 1)]))
print('쌍 %d개의 평균 겹침 비율 %.2f, 최소 %.2f' % (len(dry_ids) * (len(dry_ids) - 1) // 2, mean_pair, np.nanmin(M[np.triu_indices(len(dry_ids), 1)])))
out['6-4-meanpair'] = mean_pair
# 시작·끝의 퍼짐
S = np.array([R[i]['start'] for i in dry_ids]); E = np.array([R[i]['end'] for i in dry_ids])
print('시작 연대: 최소 %d 최대 %d 평균 %.0f 표준편차 %.0f; 끝 연대: 최소 %d 최대 %d 평균 %.0f 표준편차 %.0f' % (S.min(), S.max(), S.mean(), S.std(ddof=1), E.min(), E.max(), E.mean(), E.std(ddof=1)))
out['6-4-spread'] = dict(S=[int(S.min()), int(S.max()), float(S.mean()), float(S.std(ddof=1))], E=[int(E.min()), int(E.max()), float(E.mean()), float(E.std(ddof=1))])
# Railsback 경계와의 관계
rb = rec.RAILSBACK
print('\nRailsback 등(2018) 종합 경계 %d ~ %d (중심 %d)' % (rb['hi'], rb['lo'], rb['center']))
for i in dry_ids:
    r = R[i]; o = max(0, min(r['start'], rb['hi']) - max(r['end'], rb['lo']))
    print('  %-8s 겹침 %3d년 (경계 길이 %d년 중 %.0f%%)' % (i, o, rb['hi'] - rb['lo'], 100 * o / (rb['hi'] - rb['lo'])))
# 습윤 구간과 건조 구간의 겹침 (제1권 계산 6-14 재현)
print('\n제1권 계산 6-14 재현: 건조 네 기록(Hulun, Dali, Daihai, Dongge) 공통 = %d년; 습윤 둘(Shennong, Xianglong) 공통 = %d년' % (
    max(0, min(R[i]['start'] for i in ('Hulun', 'Dali', 'Daihai', 'Dongge')) - max(R[i]['end'] for i in ('Hulun', 'Dali', 'Daihai', 'Dongge'))),
    max(0, min(R[i]['start'] for i in ('Shennong', 'Xianglong')) - max(R[i]['end'] for i in ('Shennong', 'Xianglong')))))
print('Hulun 과 Shennong 겹침 %d년 (제1권 300년)' % ov(R['Hulun'], R['Shennong']))
print('Hulun 과 Dongge 겹침 %d년 (제1권 260년)' % ov(R['Hulun'], R['Dongge']))

# ------------------------------------------------------------------ 계산 6-5
print('\n== 계산 6-5: 지역별 방향 집계 ==')
# 중국 북쪽·남서쪽 대 중남부·남동부: 제1권 6장(Zhang 등 2018)의 서술을 옮긴 분류
north_dry = ['Lianhua', 'Nuanhe', 'Dongge', 'Daihai', 'Hulun', 'Dali']
south_wet = ['Sanbao', 'Heshang', 'Shennong', 'Xiangshui', 'Xianglong']
south_dry = ['Jiuxian']
t = [[len(north_dry), 0], [len(south_dry), len(south_wet)]]
o, p = fisher_exact(t)
print('북쪽·남서쪽(건조 %d, 습윤 0) 대 남쪽(건조 %d, 습윤 %d): Fisher 양쪽 p = %.4f, 오즈비 %s' % (len(north_dry), len(south_dry), len(south_wet), p, 'inf' if o == float('inf') else '%.1f' % o))
out['6-5-fisher'] = dict(table=t, p=float(p))
print('주의: 북·남 분류, 4.2~3.9 ka 구간 방향은 Zhang 등(2018)과 Xiao 등(2018)의 저자가 정했다(제1권 6.5절, 6.6절이 옮김). 같은 자료로 분류를 만든 뒤 검정했으므로 p 는 낮게 나오는 방향으로 치우친다.')
# 4.3~3.9 ka 창에서 지점별 방향 (이 장이 읽은 논문들. 읽은 논문만의 집계이며 표본이 아니다)
W = [('Hulun', 'dry', '동아시아'), ('Dali', 'dry', '동아시아'), ('Daihai', 'dry', '동아시아'), ('Hunsh', 'dry', '동아시아'), ('Dongge', 'dry', '동아시아'),
     ('KoreaAP', 'dry', '동아시아'), ('Shennong', 'wet', '동아시아'), ('Xianglong', 'wet', '동아시아'),
     ('Gol', 'dry', '서아시아'), ('GOman', 'dry', '서아시아'), ('Roberts', 'dry', '지중해'), ('Kotla', 'dry', '남아시아'),
     ('LopNur', 'dry', '중앙아시아'), ('Altai', 'dry', '중앙아시아'), ('Bosten', 'none', '중앙아시아'), ('Karakul', 'melt', '중앙아시아'), ('IssykKul', 'none', '중앙아시아'),
     ('NAtlantic', 'none', '북대서양'), ('Namibia', 'wet', '남반구')]
cnt = {}
for i, d, rg in W: cnt.setdefault(d, []).append(i)
print('4.3~3.9 ka 창에서 이 장이 읽은 지점 %d곳의 방향: %s' % (len(W), {d: len(v) for d, v in cnt.items()}))
for rg in ('지중해', '서아시아', '남아시아', '중앙아시아', '동아시아', '북대서양', '남반구'):
    c = {}
    for i, d, r_ in W:
        if r_ == rg: c[d] = c.get(d, 0) + 1
    print('  %-8s %s' % (rg, c))
out['6-5-window'] = {d: len(v) for d, v in cnt.items()}
ca = {}
for i, d, rg in W:
    if rg == '중앙아시아': ca[d] = ca.get(d, 0) + 1
print('중앙아시아 5곳 가운데 건조 %d곳, 건조 아님 %d곳 (보스텐: 4.3~3.9 ka 비건조, 카라쿨: 따뜻함, 이식쿨: 이상 없음)' % (ca.get('dry', 0), 5 - ca.get('dry', 0)))
out['6-5-ca'] = ca

# ------------------------------------------------------------------ 계산 6-6
print('\n== 계산 6-6: 두 펄스 맞춤 (Railsback 등 2018의 주장을 이 장의 기록에 대어 보기) ==')
p1 = R['GolP1']; p2 = R['Gol']
b1 = R['Bosten1']; bn = R['Bosten0']; b2 = R['Bosten2']
print('골 첫째(4510~4400)와 보스텐 첫 건조(4600~4300)의 겹침 %d년 (골 첫째 110년 중)' % ov(p1, b1))
print('골 둘째(4260~3970)와 보스텐 사이 비건조(4300~3900)의 겹침 %d년 (골 둘째 290년 중)' % ov(p2, bn))
print('골 둘째와 보스텐 둘째 건조(3900~3600)의 겹침 %d년' % ov(p2, b2))
print('골 둘째와 호륜호 건조의 겹침 %d년, 골 첫째와 호륜호의 겹침 %d년' % (ov(p2, R['Hulun']), ov(p1, R['Hulun'])))
print('아랄 묻힌 사주 약 4500: 골 첫째 구간(4510~4400)에 들어가는가 = %s; 보스텐 첫 건조 4600~4300 에 들어가는가 = %s' % (4400 <= 4500 <= 4510, 4300 <= 4500 <= 4600))
print('카라쿨(4200~3500, 녹은 물 많음) 와 골 둘째의 겹침 %d년: 같은 때 방향이 반대로 읽힘' % ov(R['Karakul'], p2))
print('롭노르: 습함 7.8~4.0 ka, 건조화 시작 4.0 ka. 골 둘째(4260~3970)와 롭노르 건조화 시작(4000) 사이 %d년' % (4000 - 3970 if 3970 <= 4000 <= 4260 else 0))
out['6-6'] = dict(gol1_bosten1=ov(p1, b1), gol2_bosten0=ov(p2, bn), gol2_bosten2=ov(p2, b2), gol2_hulun=ov(p2, R['Hulun']), gol2_karakul=ov(R['Karakul'], p2))
json.dump(out, open('ch06-calc-overlap.json', 'w'), ensure_ascii=False, indent=1, default=float)
