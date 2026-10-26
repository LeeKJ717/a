# -*- coding: utf-8 -*-
"""6장 계산 6-7: 구간들이 서로 겹치는 정도는 우연과 어떻게 다른가. 무작위 배치의 창 너비에 따라 답이 어떻게 바뀌는지를 보인다.
입력: ch06-records.py 의 건조 구간 10개(길이만 사용). 무작위 배치: 각 구간을 같은 길이로, 시작을 창 안에서 고르게 뽑아 놓는다.
이 검정은 '창'을 사람이 정하며, 기록이 4.2 ka 를 포함하기 때문에 골라졌다는 선택 편향을 다루지 못한다. 실행: python3 ch06-calc-null.py"""
import numpy as np, json, os, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rec', os.path.join(here, 'ch06-records.py'))
rec = importlib.util.module_from_spec(spec); spec.loader.exec_module(rec)
R = {r['id']: r for r in rec.R}
ids = ['Hulun', 'Dali', 'Daihai', 'Hunsh', 'Dongge', 'Gol', 'GOman', 'Roberts', 'Kotla', 'Altai']
L = np.array([R[i]['start'] - R[i]['end'] for i in ids], float)
S = np.array([R[i]['start'] for i in ids], float)
def mean_pair(st):
    n = len(st); en = st - L; vals = []
    for a in range(n):
        for b in range(a + 1, n):
            o = max(0.0, min(st[a], st[b]) - max(en[a], en[b])); sh = min(L[a], L[b]); vals.append(o / sh)
    return np.mean(vals)
obs = mean_pair(S)
print('관측 평균 쌍별 겹침 비율 %.3f (구간 길이 %s)' % (obs, L.astype(int).tolist()))
rng = np.random.default_rng(20261026)
out = dict(obs=obs)
for W in (800, 1500, 3000):
    N = 20000; hit = 0; vals = []
    for _ in range(N):
        st = rng.uniform(L, W) + (4200 - W / 2)      # 창 [4200 - W/2, 4200 + W/2] 안에 구간 전체가 들어가게 (시작이 큰 쪽)
        # 시작 st 는 4200-W/2+L .. 4200+W/2 사이
        v = mean_pair(st); vals.append(v)
    vals = np.array(vals)
    p = (vals >= obs).mean()
    print('창 너비 %4d년: 무작위 평균 %.3f, 95%% 구간 %.3f~%.3f, P(무작위 >= 관측) = %.4f' % (W, vals.mean(), *np.percentile(vals, [2.5, 97.5]), p))
    out[str(W)] = dict(mean=float(vals.mean()), p=float(p))
json.dump(out, open('ch06-calc-null.json', 'w'), indent=1)
