# -*- coding: utf-8 -*-
"""계산 15-3: 다섯 전지구 창의 겹침은 우연과 구별되는가. 제3권 6장 계산 6-7(ch06-calc-null.py)과 같은 방식의 무작위 배치.
입력: 다섯 창의 길이 [200, 400, 500, 220, 300](8장 표). 통계량 둘: (i) 다섯 창의 공통 구간 길이, (ii) 쌍별 겹침 비율의 평균(겹친 년수 / 짧은 쪽 길이).
영 모형 1(창 너비 W): 각 창을 같은 길이로, 4200 을 가운데로 한 너비 W 의 틀 안에 시작을 고르게 뽑아 놓는다.
영 모형 2(선택): 각 창이 4200 을 반드시 덮도록 시작을 고르게 뽑는다. "4.2 ka 를 말하는 논문만 모았다"는 선택을 거칠게 흉내 낸 것이다.
두 영 모형 모두 이 책의 시연값이며 논문의 값이 아니다. 시드 20261027, 반복 100000."""
import numpy as np, json
from windows15 import *
L = np.array([W[n][1] - W[n][0] for n in GLOBAL5], float)
S = np.array([W[n][1] for n in GLOBAL5], float)      # 오래된 끝
def pair_mean(st):   # st: (N, 5)
    en = st - L; n = st.shape[1]; v = []
    for a in range(n):
        for b in range(a + 1, n):
            o = np.maximum(0.0, np.minimum(st[:, a], st[:, b]) - np.maximum(en[:, a], en[:, b]))
            v.append(o / min(L[a], L[b]))
    return np.mean(v, axis=0)
def common_len(st):
    en = st - L
    return st.min(axis=1) - en.max(axis=1)
obs_c = float(common_len(S[None, :])[0]); obs_p = float(pair_mean(S[None, :])[0])
print('관측: 다섯 창 길이 %s, 공통 구간 %.0f 년, 쌍별 겹침 평균 %.3f (10쌍)' % (L.astype(int).tolist(), obs_c, obs_p))
rng = np.random.default_rng(20261027)
N = 100000
out = dict(obs_common=obs_c, obs_pair=obs_p, null1={}, null2={})
print()
print('영 모형 1: 4200 을 가운데로 한 너비 W 의 틀 안에 창 전체를 놓는다')
print('   W(년) | P(공통>=%d년) | P(공통구간 있음) | 무작위 쌍별 평균 [95%% 구간] | P(쌍별 평균 >= %.3f)' % (obs_c, obs_p))
for Wd in (600, 800, 1000, 1500, 3000):
    st = rng.uniform(L, Wd, size=(N, 5)) + (4200 - Wd / 2)     # 오래된 끝: 틀 안에 창 전체가 들어가게
    c = common_len(st); pm = pair_mean(st)
    out['null1'][Wd] = dict(p_common=float((c >= obs_c).mean()), p_any=float((c > 0).mean()), pm_mean=float(pm.mean()), p_pair=float((pm >= obs_p).mean()))
    print('  %5d  |   %.4f   |   %.4f   |   %.3f [%.3f~%.3f]   |   %.4f' % (Wd, (c >= obs_c).mean(), (c > 0).mean(), pm.mean(), *np.percentile(pm, [2.5, 97.5]), (pm >= obs_p).mean()))
print()
print('영 모형 2: 각 창이 4200 을 덮는다(오래된 끝이 4200 ~ 4200 + 길이 사이에서 고르게)')
st = 4200 + rng.uniform(0, 1, size=(N, 5)) * L
c = common_len(st); pm = pair_mean(st)
out['null2'] = dict(p_common=float((c >= obs_c).mean()), p_any=float((c > 0).mean()), pm_mean=float(pm.mean()), p_pair=float((pm >= obs_p).mean()),
                    c_mean=float(c.clip(0).mean()), c_med=float(np.median(c)))
print('   P(공통>=%d년) = %.4f, P(공통구간 있음) = %.4f, 공통 길이 중앙값 %.0f 년, 무작위 쌍별 평균 %.3f [%.3f~%.3f], P(쌍별 평균 >= %.3f) = %.4f' % (
    obs_c, (c >= obs_c).mean(), (c > 0).mean(), np.median(c), pm.mean(), *np.percentile(pm, [2.5, 97.5]), obs_p, (pm >= obs_p).mean()))
print()
print('읽기: 영 모형 1 에서 틀이 좁을수록(W 가 가장 긴 창 500 에 가까울수록) 창 다섯이 겹치는 것은 당연하다. 영 모형 2 는 창이 4200 을 덮는다고 미리 정하므로 공통 구간이 있는 것(1.0000)은 설계의 결과이다.')
json.dump(out, open('calc15-3-out.json', 'w'), ensure_ascii=False)
