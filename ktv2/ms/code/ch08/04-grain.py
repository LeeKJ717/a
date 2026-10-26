# -*- coding: utf-8 -*-
"""실습 8-4: 입도 분석. 제1권에는 입도 분포의 원자료가 없다(제1권 8장은 40 μm 이상의 비율과 석영 중앙 입경을 말만 한다).
그래서 이 실습의 입력은 두 가지다.
 (A) 해석적으로 답을 아는 분포(φ 단위의 정규분포): sedkit의 구현이 맞는지 가르는 시험. 값은 계산해서 만든 것이다.
 (B) 황토 비슷한 분포를 만든 시연값: 두 정규 성분의 혼합. 실제 시료의 값이 아니다.
용어: φ = -log2(입경 mm). 입경 1 mm가 0 φ, 62.5 μm가 4 φ. φ가 클수록 곱다."""
import os, sys, time, math, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import stats, optimize
import sedkit as K
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
z = stats.norm.ppf

print('== (A) 정규 분포 시험: 평균 5.0 φ, 표준편차 1.0 φ')
print('   정규 분포에서 식의 기대값(상수 6.6, 2.44의 영향을 보기 위해 정규분포의 백분위로 계산):')
q = {p: 5.0 + 1.0 * z(p / 100) for p in (5, 16, 25, 50, 75, 84, 95)}
exp = K.folk_ward(q[5], q[16], q[25], q[50], q[75], q[84], q[95])
print('   φ5 %.4f φ16 %.4f φ25 %.4f φ50 %.4f φ75 %.4f φ84 %.4f φ95 %.4f' % tuple(q[p] for p in (5, 16, 25, 50, 75, 84, 95)))
print('   Folk와 Ward 식에 정확한 백분위를 넣으면: 평균 %.5f 분급 %.5f 왜도 %.5f 첨도 %.5f' % exp)
print('   (정규 분포에서도 분급과 첨도가 정확히 1은 아니다. 상수 6.6과 2.44는 정규 분포에서 1에 가깝게 되도록 정한 근삿값이다.)')
print('   z95 - z5 = %.5f, z75 - z25 = %.5f, 비 = %.5f' % (z(.95) - z(.05), z(.75) - z(.25), (z(.95) - z(.05)) / (z(.75) - z(.25))))
print()
print('   등급 너비를 바꿔 표로 만든 뒤 sedkit으로 다시 계산 (범위 0~10 φ). 선형 보간과 pchip 보간')
print('   %6s %-6s %8s %8s %8s %8s | %8s %8s' % ('너비', '보간', '평균', '분급', '왜도', '첨도', '적률평균', '적률표준'))
for wd in (0.25, 0.5, 1.0):
    edges = np.arange(0, 10 + 1e-9, wd)
    w = K.class_weights_from_cdf(edges, lambda x: stats.norm.cdf(x, 5.0, 1.0))
    for m in ('linear', 'pchip'):
        fw, qq = K.fw_from_table(edges, w, m)
        mo = K.moments_phi(edges, w)
        print('   %6.2f %-6s %8.4f %8.4f %8.4f %8.4f | %8.4f %8.4f' % (wd, m, *fw, mo[0], mo[1]))
print('   기대값                %8.4f %8.4f %8.4f %8.4f | %8.4f %8.4f' % (*exp, 5.0, 1.0))
print('   등급 중점으로 계산한 표준편차의 기대값 sqrt(1 + w^2/12): ' + ', '.join('w=%.2f -> %.4f' % (wd, math.sqrt(1 + wd * wd / 12)) for wd in (0.25, 0.5, 1.0)))

print('\n== (B) 시연값: 황토 비슷한 혼합 분포. 85 % N(5.3 φ, 0.8 φ) + 15 % N(8.0 φ, 0.9 φ), 등급 0.5 φ, 범위 2~10 φ')
cdf = lambda x: 0.85 * stats.norm.cdf(x, 5.3, 0.8) + 0.15 * stats.norm.cdf(x, 8.0, 0.9)
edges = np.arange(2.0, 10.0 + 1e-9, 0.5)
w = K.class_weights_from_cdf(edges, cdf)
w2 = np.round(w, 2)
w2[np.argmax(w2)] += round(100.0 - w2.sum(), 2)     # 합을 100.00으로 맞춘다(가장 큰 등급에 나머지)
print('   표의 합을 100.00으로 맞추려고 가장 큰 등급에 %+.2f를 더했다' % round(100.0 - np.round(w, 2).sum(), 2))
with open(os.path.join(HERE, 'data', 'grain-demo.csv'), 'w', encoding='utf-8', newline='') as f:
    cw = csv.writer(f); cw.writerow(['phi_from', 'phi_to', 'um_from', 'um_to', 'weight_pct'])
    for i in range(len(w2)):
        cw.writerow([edges[i], edges[i + 1], round(float(K.phi_to_um(edges[i])), 2), round(float(K.phi_to_um(edges[i + 1])), 2), w2[i]])
ed, cum = K.cumulative(edges, w2)
print('   %5s %5s %9s %9s %8s %8s' % ('φ에서', 'φ까지', 'μm(위)', 'μm(아래)', '무게 %', '누적 %'))
for i in range(len(w2)):
    print('   %5.1f %5.1f %9.2f %9.2f %8.2f %8.2f' % (edges[i], edges[i + 1], K.phi_to_um(edges[i]), K.phi_to_um(edges[i + 1]), w2[i], cum[i + 1]))
print('   합 = %.2f' % w2.sum())
ps = [5, 16, 25, 50, 75, 84, 95]
for m in ('linear', 'pchip'):
    fw, qq = K.fw_from_table(edges, w2, m)
    print('   [%s] φ5 %.3f φ16 %.3f φ25 %.3f φ50 %.3f φ75 %.3f φ84 %.3f φ95 %.3f' % ((m,) + tuple(qq)))
    print('   [%s] 평균 %.3f φ (%.2f μm)  분급 %.3f  왜도 %.3f  첨도 %.3f ; 중앙 입경 φ50 %.3f φ = %.2f μm' % (m, fw[0], K.phi_to_um(fw[0]), fw[1], fw[2], fw[3], qq[3], K.phi_to_um(qq[3])))
mo = K.moments_phi(edges, w2)
print('   적률(등급 중점): 평균 %.3f φ, 표준편차 %.3f φ, 왜도 %.3f, 첨도(정규=3) %.3f' % mo)
# 해석적 답
print('   --- 혼합 분포의 해석적 백분위(근 찾기)와 비교 ---')
ex = []
for p in ps:
    ex.append(optimize.brentq(lambda x: cdf(x) - p / 100, 0, 12))
print('   해석적: ' + ' '.join('φ%d %.3f' % (p, e) for p, e in zip(ps, ex)))
fx = K.folk_ward(*ex)
print('   해석적 백분위에 식을 넣으면: 평균 %.3f 분급 %.3f 왜도 %.3f 첨도 %.3f' % fx)
fl, ql = K.fw_from_table(edges, w2, 'linear')
print('   선형 보간 표 결과와의 차: 평균 %+.3f 분급 %+.3f 왜도 %+.3f 첨도 %+.3f' % tuple(np.array(fl) - np.array(fx)))
# 거친 입자 비율
d40 = float(K.mm_to_phi(0.040))
print('\n   입경 40 μm = %.4f φ. 40 μm보다 거친 몫(누적 %%): 선형 %.2f %%, 해석적 %.2f %%' % (d40, np.interp(d40, ed, cum), 100 * cdf(d40)))
print('   62.5 μm(= 4 φ)보다 거친 몫: 표 경계 4.0 φ에서 누적 %.2f %%' % np.interp(4.0, ed, cum))
print('   모래(4 φ보다 거침) %.2f %%, 실트(4~8 φ) %.2f %%, 점토(8 φ보다 고움) %.2f %%' % (np.interp(4.0, ed, cum), np.interp(8.0, ed, cum) - np.interp(4.0, ed, cum), 100 - np.interp(8.0, ed, cum)))
# 곡선 위 점: 그림용
np.savez(os.path.join(HERE, 'out-grain.npz'), edges=edges, w=w2, cum=cum, q=np.array(ql), ps=np.array(ps))
print('걸린 시간 %.3f초' % (time.time() - t0))
