# -*- coding: utf-8 -*-
"""계산 1-4: 나이테의 '조각 길이의 저주'(segment length curse, Cook 등 1995)를 사인파로 시연한다.
논문 값(Cook 등 1995, 본문 요약): 조각 길이 1000, 500, 200년, 제약 없는 직선 제거에서 1000년 조각은 낮은 주파수 변동의 약 47%만 남기고,
  200년 조각에서는 원래 변동과의 낮은 주파수 상관이 부호가 뒤집혀 R^2 = -0.372 이다. Esper 등(2002): 개별 나이테 열은 보통 200~400년이고
  개체별 성장 곡선으로 표준화하면 복원할 수 있는 가장 긴 주기는 그 열의 길이로 제한된다.
이 계산은 같은 숫자를 되풀이하지 않는다(그 논문의 7104년 나이테 열은 이 책에 없다). 대신 '무작위 시작 나이의 조각들을 평균 제거 또는 직선 제거해 겹쳐 평균한 연대기'가
주기 P 의 사인파(진폭 1)를 얼마나 남기는지를 센다. 모든 값은 시연값이다.
"""
import numpy as np
rng = np.random.default_rng(20261027)

def chrono(P, L, method, N=6000, n_seg=400):
    """길이 N 년 사인파 위에 길이 L 의 조각 n_seg 개를 뽑고(시작 무작위) 각 조각을 처리해 해마다 평균. 남은 진폭 = 연대기와 원 신호의 회귀 기울기."""
    t = np.arange(N)
    sig = np.sin(2 * np.pi * t / P + rng.uniform(0, 2 * np.pi))
    num = np.zeros(N); cnt = np.zeros(N)
    for _ in range(n_seg):
        s = rng.integers(0, N - L)
        x = sig[s:s + L].copy()
        if method == 'mean':
            x = x - x.mean()
        elif method == 'lin':
            tt = np.arange(L); c = np.polyfit(tt, x, 1); x = x - np.polyval(c, tt)
        num[s:s + L] += x; cnt[s:s + L] += 1
    ok = cnt > 20
    ch = num[ok] / cnt[ok]
    ref = sig[ok]
    b = (ch * ref).sum() / (ref * ref).sum()     # 원 신호 위로의 회귀 기울기(남은 진폭 비율)
    return b

print('=== 계산 1-4 (1) 사인파(주기 P)의 진폭이 조각 길이 L 의 조각 평균 연대기에 남는 비율 (평균 제거) ===')
Ps = (100, 200, 400, 800, 1600, 3200)
Ls = (200, 500, 1000)
print('  L \\ P  ' + ''.join('%8d' % P for P in Ps))
res = {}
for method, name in (('mean', '평균만 제거'), ('lin', '직선 제거')):
    print('  [%s]' % name)
    for L in Ls:
        vals = [np.mean([chrono(P, L, method) for _ in range(5)]) for P in Ps]
        res[(method, L)] = vals
        print('  %5d  ' % L + ''.join('%8.2f' % v for v in vals))
print()
print('=== 계산 1-4 (2) 남는 비율이 0.5 아래로 내려가는 주기(로그 눈금 보간) ===')
lp = np.log(np.array(Ps, float))
for method, name in (('mean', '평균만 제거'), ('lin', '직선 제거')):
    for L in Ls:
        v = np.array(res[(method, L)])
        # 주기가 길어질수록 줄어드는 곡선에서 0.5 를 지나는 점
        k = int(np.argmax(v < 0.5))
        x0, x1, y0, y1 = lp[k - 1], lp[k], v[k - 1], v[k]
        p50 = np.exp(x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0))
        print('  %s, 조각 %4d년: 0.5 를 지나는 주기 약 %.0f 년 (조각 길이의 %.1f 배)' % (name, L, p50, p50 / L))
print('  (Cook 등의 47%와 R^2 -0.372 는 7104년 나이테 열 한 개로 센 값이며 이 사인파 시연과 같은 양이 아니므로 견주지 않는다.)')
