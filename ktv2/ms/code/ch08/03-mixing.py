# -*- coding: utf-8 -*-
"""실습 8-3: 끝 성분 혼합 모형.
(가) 두 성분 혼합: 제1권 8장 계산 8-12(Dou 등, 2021의 끝 성분)와 10장 계산 10-9(He 등, 2015의 합류)를 되풀이한다.
(나) 농도가 다를 때: 끝 성분의 Nd, Sr 농도는 제1권에 없다. 아래 농도는 모두 시연값이다.
(다) 세 성분 혼합: 입력 전부가 시연값(끝 성분 셋의 값과 농도, 오차). 연립방정식으로 풀고 오차를 몬테카를로로 전파한다.
난수는 numpy.random.default_rng(시드 고정)."""
import csv, os, sys, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import optimize
import sedkit as K
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))

em = {r['name']: (float(r['eNd']), float(r['Sr87_86'])) for r in csv.DictReader(open(os.path.join(HERE, 'data', 'dou2021-endmembers.csv'), encoding='utf-8'))}
JA, GB = em['JA'], em['GB']
print('끝 성분(제1권 8장이 Dou 등에서 옮김): JA εNd %.2f, 87Sr/86Sr %.6f ; GB εNd %.1f, 87Sr/86Sr %.4f' % (*JA, *GB))

print('\n== (가-1) 시연값: Nd 농도 JA 30 ppm, GB 20 ppm, 질량 몫 0.5')
x_c = float(K.mix_x(0.5, JA[0], GB[0], 30.0, 20.0)); x_l = float(K.mix_x(0.5, JA[0], GB[0]))
print('   농도 가중 εNd = %.3f ; 농도를 같게 둔 직선 평균 = %.3f   (제1권 8장 -0.006, -0.905)' % (x_c, x_l))
print('   손계산 점검: (0.5x30x3.59 + 0.5x20x(-5.4)) / (0.5x30 + 0.5x20) = (%.2f + %.2f)/%.1f = %.4f' % (0.5 * 30 * 3.59, 0.5 * 20 * -5.4, 25.0, (0.5 * 30 * 3.59 + 0.5 * 20 * -5.4) / 25))

print('\n== (가-2) 농도가 같다고 두고 JA 몫 f를 읽기 (Dou 등의 코어 값, 제1권 계산 8-12의 입력)')
V1_ND = {-4.9: 0.056, -3.6: 0.200, -2.5: 0.323}
V1_SR = {0.711713: 0.269, 0.708164: 0.612, 0.708265: 0.602, 0.706346: 0.787}
allok = True
for e, v1 in V1_ND.items():
    f = float(K.mix_f(e, JA[0], GB[0]))
    print('   εNd %5.1f -> f = (%.1f - (%.1f)) / (%.2f - (%.1f)) = %.4f   제1권 %.3f %s' % (e, e, GB[0], JA[0], GB[0], f, v1, '일치' if abs(round(f, 3) - v1) < 1e-9 else '불일치'))
    allok &= abs(round(f, 3) - v1) < 1e-9
for r, v1 in V1_SR.items():
    f = float(K.mix_f(r, JA[1], GB[1]))
    print('   Sr %.6f -> f = (%.4f - %.6f) / (%.4f - %.6f) = %.4f   제1권 %.3f %s' % (r, GB[1], r, GB[1], JA[1], f, v1, '일치' if abs(round(f, 3) - v1) < 1e-9 else '불일치'))
    allok &= abs(round(f, 3) - v1) < 1e-9
print('   제1권 값 7개와 모두 일치: %s' % ('예' if allok else '아니오'))

print('\n== (가-3) 하천 합류 (He 등, 2015 표 6의 εNd, 제1권 10장 계산 10-9). 두 지류의 Nd 농도가 같다고 둔 값')
for nm, up, tr, dn, v1 in (('중경: 위 중경1, 가릉강, 아래 중경2', -11.70, -15.18, -13.30, 0.46), ('무한: 위 무한1, 한수, 아래 무한2', -11.72, -10.73, -11.10, 0.63)):
    f = float(K.mix_f(dn, tr, up))
    print('   %-30s 지류 몫 f = %.4f  (제1권 %.2f)' % (nm, f, v1))

print('\n== (나) 시연값: 끝 성분의 Nd 농도가 JA 30 ppm, GB 20 ppm이면 같은 εNd에서 읽히는 JA 몫')
print('   %6s %12s %12s' % ('εNd', 'f(농도 같음)', 'f(30/20)'))
for e in V1_ND:
    print('   %6.1f %12.4f %12.4f' % (e, float(K.mix_f(e, JA[0], GB[0])), float(K.mix_f(e, JA[0], GB[0], 30.0, 20.0))))
print('   농도 비가 1이면 두 열이 같고, 1이 아니면 읽히는 f가 달라진다.')

print('\n== (나-2) 시연: 같은 f가 Nd와 Sr 양쪽에서 나오려면 필요한 농도 비 c(GB)/c(JA)')
print('   짝 시연: εNd -3.6, 87Sr/86Sr 0.708164 (Dou 등의 범위 값을 하나씩 골랐을 뿐 같은 시료라는 뜻이 아니다)')
print('   %5s %14s %14s' % ('f', 'Nd의 c비', 'Sr의 c비'))
for f in (0.2, 0.3, 0.4, 0.5, 0.6):
    print('   %5.1f %14.4f %14.4f' % (f, K.conc_ratio_needed(f, -3.6, JA[0], GB[0]), K.conc_ratio_needed(f, 0.708164, JA[1], GB[1])))

# ------------------------------------------------------------------ (다) 세 성분
print('\n== (다) 세 성분 혼합: 모든 값이 시연값')
rng = np.random.default_rng(20261026)
names = ['끝성분1(JA값 차용)', '끝성분2(GB값 차용)', '끝성분3(시연)']
R = np.array([[JA[0], GB[0], -12.0],            # εNd
              [JA[1], GB[1], 0.7200]])          # 87Sr/86Sr
C = np.array([[30.0, 20.0, 25.0],               # Nd ppm (시연)
              [300.0, 180.0, 120.0]])           # Sr ppm (시연)
ftrue = np.array([0.5, 0.3, 0.2])
obs = K.mix_forward(C, R, ftrue)
print('   끝 성분 값 R(εNd; Sr비)와 농도 C(Nd ppm; Sr ppm):')
for j in range(3):
    print('     %-18s εNd %6.2f  Sr비 %.4f  Nd %5.1f  Sr %5.1f' % (names[j], R[0, j], R[1, j], C[0, j], C[1, j]))
print('   가상의 참값 f = %s -> 혼합물 εNd = %.4f, 87Sr/86Sr = %.6f' % (ftrue, obs[0], obs[1]))
fh, A = K.unmix(C, R, obs)
print('   연립방정식을 풀어 되찾은 f = %s ; 참값과 최대 차이 %.2e' % (np.array2string(fh, precision=6), np.abs(fh - ftrue).max()))
print('   계수 행렬의 조건수 %.2f' % np.linalg.cond(A))

sig = np.array([0.3, 0.0005])
N = 100000
draw = obs + rng.normal(size=(N, 2)) * sig
F = np.empty((N, 3))
for i in range(N):
    F[i], _ = K.unmix(C, R, draw[i])
neg = (F < 0).any(axis=1).mean()
print('   관측 오차(1 표준편차, 시연값) εNd %.1f, Sr비 %.4f 를 정규분포로 %d번 뽑아 다시 풀기 (시드 20261026):' % (sig[0], sig[1], N))
for j in range(3):
    q = np.percentile(F[:, j], [2.5, 50, 97.5])
    print('     f%d: 2.5 %% %.3f  중앙 %.3f  97.5 %% %.3f   표준편차 %.3f' % (j + 1, *q, F[:, j].std()))
print('   음수 몫이 하나라도 나온 비율 %.4f' % neg)

# 끝 성분 3이 1-2 혼합 곡선 근처에 놓인 경우
f_line = 0.4
x_line = K.mix_forward(C[:, :2], R[:, :2], np.array([f_line, 1 - f_line]))
R2 = R.copy(); C2 = C.copy()
R2[:, 2] = [x_line[0] + 0.3, x_line[1] + 0.0003]
C2[:, 2] = [25.0, 150.0]
obs2 = K.mix_forward(C2, R2, ftrue)
fh2, A2 = K.unmix(C2, R2, obs2)
print('\n   끝성분3을 끝성분1-2 혼합 곡선 바로 옆(εNd %+.1f, Sr비 %+.4f 어긋남)에 둔 경우: 조건수 %.1f' % (0.3, 0.0003, np.linalg.cond(A2)))
print('   끝성분3 = εNd %.3f, Sr비 %.6f ; 같은 참값 f에서 되찾은 f = %s' % (R2[0, 2], R2[1, 2], np.array2string(fh2, precision=6)))
draw2 = obs2 + rng.normal(size=(N, 2)) * sig
F2 = np.empty((N, 3))
for i in range(N):
    F2[i], _ = K.unmix(C2, R2, draw2[i])
print('   같은 관측 오차로 %d번:' % N)
for j in range(3):
    q = np.percentile(F2[:, j], [2.5, 50, 97.5])
    print('     f%d: 2.5 %% %.3f  중앙 %.3f  97.5 %% %.3f' % (j + 1, *q))
print('   음수 몫이 하나라도 나온 비율 %.4f' % (F2 < 0).any(axis=1).mean())

# 경계 밖의 해: 오차가 큰 한 번의 관측을 범위 안으로 끌어오기
i_neg = int(np.argmax((F2 < 0).any(axis=1)))
print('\n   음수 몫이 나온 한 번의 뽑기(두 번째 배치): 관측 εNd %.3f, Sr비 %.6f -> 풀이 f = %s' % (*draw2[i_neg], np.array2string(F2[i_neg], precision=4)))
# 비음수 제약 최소제곱: [농도 가중 식 2개; 합=1(큰 가중)]
Wt = 1e3
Aj = np.vstack([C2 * (R2 - draw2[i_neg][:, None]), Wt * np.ones(3)])
bj = np.array([0.0, 0.0, Wt])
sol = optimize.lsq_linear(Aj, bj, bounds=(0.0, 1.0))
print('   scipy.optimize.lsq_linear(경계 0~1, 합 = 1 에 가중 %g) 풀이 f = %s, 합 %.4f, 식 잔차 노름 %.4g' % (Wt, np.array2string(sol.x, precision=4), sol.x.sum(), np.linalg.norm((Aj @ sol.x - bj)[:2])))
np.savez(os.path.join(HERE, 'out-mix.npz'), R=R, C=C, R2=R2, C2=C2, obs=obs, obs2=obs2, sig=sig, d1=draw[:400], d2=draw2[:400], ftrue=ftrue, JA=np.array(JA), GB=np.array(GB))
print('걸린 시간 %.3f초' % (time.time() - t0))
