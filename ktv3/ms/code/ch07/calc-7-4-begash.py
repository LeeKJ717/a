# -*- coding: utf-8 -*-
"""계산 7-4. Begash 숯 AMS 연대 34개(Frachetti & Mar'yashev 2007 표 1)를 IntCal20으로 보정해 단계별 연대와 점유의 빈 틈을 센다.
이 연대는 숯이며 곡물이 아니다. 기장·밀의 직접 연대(Frachetti 등 2010)는 이 표에 없다."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, c14lib as c, c14data as d
rows = []
for lab, ph, age, err, ps, pe in d.BEGASH:
    p = c.calibrate(age, err); a, b = c.outer(p); m = c.median(p)
    rows.append((lab, ph, age, err, float(c.to_year(b)), float(c.to_year(a)), float(c.to_year(m)), p))
print('단계별 (보정 95.4% 바깥 구간, 중앙값 연도)')
phases = []
for ph in ['1a', '1b', '2', '3a', '3b', '4', '5', '6']:
    R = [r for r in rows if r[1] == ph]
    lo = min(r[4] for r in R); hi = max(r[5] for r in R); meds = sorted(r[6] for r in R)
    phases.append((ph, len(R), lo, hi, meds[0], meds[-1]))
    print('단계 %-2s n=%2d  가장 이른 구간 시작 %s, 가장 늦은 구간 끝 %s | 중앙값 %s ~ %s' % (ph, len(R), c.fmt_year(lo), c.fmt_year(hi), c.fmt_year(meds[0]), c.fmt_year(meds[-1])))
# 날짜 순서 점검: 14C 나이가 단계 안에서 단조 감소하는가(표의 순서)
print('\n표에 적힌 순서대로 14C 나이가 줄어드는가(젊어지는가):')
ages = [r[2] for r in rows]; viol = [(rows[i][0], ages[i], rows[i + 1][0], ages[i + 1]) for i in range(len(ages) - 1) if ages[i + 1] > ages[i]]
print('  역전 %d건' % len(viol), viol)
# 가장 큰 빈 틈: 이웃 중앙값 사이의 간격과, 95.4% 구간이 겹치지 않는 간격
srt = sorted(rows, key=lambda r: r[6])
gaps = [(srt[i + 1][6] - srt[i][6], srt[i][0], srt[i + 1][0]) for i in range(len(srt) - 1)]
gaps.sort(reverse=True)
print('\n이웃한 날짜 중앙값 사이 가장 큰 간격 5개(년, 앞, 뒤):')
for g in gaps[:5]: print('  %5.0f  %s -> %s' % g)
# 구간 기준 빈 틈: 어느 날짜의 95.4% 구간에도 들지 않는 연도 구간 중 가장 긴 것
yrs = np.arange(-2600, 2001)
cov = np.zeros(len(yrs), bool)
for r in rows:
    cov |= (yrs >= r[4]) & (yrs <= r[5])
runs = []; i = 0
while i < len(yrs):
    if not cov[i]:
        j = i
        while j + 1 < len(yrs) and not cov[j + 1]: j += 1
        runs.append((j - i + 1, int(yrs[i]), int(yrs[j]))); i = j + 1
    else: i += 1
runs.sort(reverse=True)
print('\n어느 날짜의 95.4% 구간에도 들지 않는 연도 구간(긴 순서 5개; 길이, 시작, 끝):')
for r in runs[:5]: print('  %5d년  %s ~ %s' % (r[0], c.fmt_year(r[1]), c.fmt_year(r[2])))
# 합산 확률분포(SPD) 세기: 100년 칸. 표본이 숯 34개뿐이라 점유 강도가 아니라 '날짜가 있는 곳'을 보인다.
bins = np.arange(-2600, 2001, 100); spd = np.zeros(len(bins) - 1)
yr_grid = c.to_year(c.GRID)
for r in rows:
    pr = r[7]
    h, _ = np.histogram(yr_grid, bins=bins, weights=pr); spd += h
print('\n합산 확률(34개 날짜의 100년 칸, 합=34): 가장 큰 칸 5개')
top = np.argsort(spd)[::-1][:5]
for k in top: print('  %s ~ %s : %.2f' % (c.fmt_year(bins[k]), c.fmt_year(bins[k + 1]), spd[k]))
print('합 확인: %.3f (34에서 모자란 몫은 기원전 2600 이전 꼬리, AA52926의 구간이 기원전 3493까지 뻗는다)' % spd.sum())
# 가장 이른 날짜 OS-54364(3870±35)가 기원전 2200보다 오래된 확률(Frachetti 등 2010의 '약 기원전 2200' 서술과 비교하는 데 쓰는 참고값)
p = c.calibrate(3870, 35); m = c.to_year(c.GRID) <= -2200
print('\nOS-54364 3870±35: 기원전 2200보다 오래됐을 확률 %.3f, 중앙값 %s, 평균±SD %s' % (p[m].sum(), c.fmt_year(c.to_year(c.median(p))), tuple(round(float(x),1) for x in c.mean_sd(p))))
p = c.calibrate(1600, 35); a, b = c.outer(p)
q = c.calibrate(715, 33); a2, b2 = c.outer(q)
print('6세기 중반의 마지막 점유(OS-54330 1600±35) 구간 끝 %s, 몽골 시기 첫 날짜(AA52921 715±33) 구간 시작 %s, 간격 %d년' % (c.fmt_year(c.to_year(a)), c.fmt_year(c.to_year(b2)), int(c.to_year(a) - c.to_year(b2)) * -1))
json.dump(dict(phases=phases, gaps=gaps[:5], runs=runs[:5], spd=spd.tolist(), bins=bins.tolist()), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc-7-4-begash.json'), 'w'), ensure_ascii=False, indent=1)
