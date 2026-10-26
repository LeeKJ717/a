# -*- coding: utf-8 -*-
"""11장 실습 11-4: 난수. 시드, 조각 크기, 난수 생성기 종류, 독립 흐름(spawn)이 결과에 주는 영향을 numpy에서 재 본다.
대상: 제1권 11장 계산 11-4의 대산전 [1,3,1,2,2] 유전자 다양도 H 부트스트랩. 정확한 평균 E[H]는 p01과 같은 방식으로 정확히 센 값이다.
이 컨테이너에서는 numpy 생성기만 실행했다. cupy 생성기(XORWOW 등)로 같은 시험을 하는 일은 z840 실행 필요."""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'mc-core-v1.py'))
mc = importlib.util.module_from_spec(_s); _s.loader.exec_module(mc)
xp = np
CNT = [1, 3, 1, 2, 2]
vals, pr, mean_ex = mc.exact_h_distribution(CNT)
var_ex = float(((vals - mean_ex) ** 2 * pr).sum()); sd_ex = math.sqrt(var_ex)
print('numpy', np.__version__, '| python', sys.version.split()[0])
print('정확한 H: 평균 %.6f, 표준편차 %.6f (표본 평균의 표준오차 = 표준편차/sqrt(B))' % (mean_ex, sd_ex))
B = 1000000; se = sd_ex / math.sqrt(B)
print('B = %d 이면 평균의 표준오차 = %.6f' % (B, se))
rec = {}

print('\n[1] 같은 시드로 두 번: 비트 단위로 같은가')
h1 = mc.boot_h_values(xp, CNT, 200000, np.random.default_rng(11), 200000)
h2 = mc.boot_h_values(xp, CNT, 200000, np.random.default_rng(11), 200000)
print('  두 결과가 완전히 같다:', bool(np.array_equal(h1, h2)))

print('\n[2] 같은 시드, 조각(chunk) 크기만 다르게: 결과가 같은가')
res = {}
for ch in (50000, 100000, 200000, 1000000):
    h = mc.boot_h_values(xp, CNT, 1000000, np.random.default_rng(11), ch)
    res[ch] = h
    print('  chunk=%8d: 평균 %.6f, 처음 3개 %s' % (ch, h.mean(), np.round(h[:3], 4)))
print('  chunk 50000 대 100000 완전히 같다:', bool(np.array_equal(res[50000], res[100000])), '| 100000 대 200000:', bool(np.array_equal(res[100000], res[200000])),
      '| 200000 대 1000000:', bool(np.array_equal(res[200000], res[1000000])))
rec['chunk_equal'] = bool(np.array_equal(res[50000], res[1000000]))

print('\n[3] 같은 방식, 시드 20개: 평균의 흩어짐이 표준오차와 맞는가')
ms = np.array([mc.boot_h_values(xp, CNT, B, np.random.default_rng(s), 200000).mean() for s in range(1, 21)])
print('  20개 평균: 최소 %.6f, 최대 %.6f, 표준편차 %.6f (이론 표준오차 %.6f)' % (ms.min(), ms.max(), ms.std(ddof=1), se))
print('  정확한 평균 %.6f 에서의 차이를 표준오차로 나눈 값: 절댓값 최대 %.2f, 평균 제곱의 제곱근 %.2f' % (mean_ex, np.abs((ms - mean_ex) / se).max(), math.sqrt((((ms - mean_ex) / se) ** 2).mean())))
rec['seeds'] = {'mean': ms.tolist(), 'se': se, 'exact': mean_ex}

print('\n[4] 난수 생성기(비트 생성기) 종류별: 같은 시드 11, B = 1,000,000')
gens = [('PCG64 (numpy 기본)', lambda s: np.random.Generator(np.random.PCG64(s))), ('PCG64DXSM', lambda s: np.random.Generator(np.random.PCG64DXSM(s))),
        ('Philox', lambda s: np.random.Generator(np.random.Philox(s))), ('SFC64', lambda s: np.random.Generator(np.random.SFC64(s))),
        ('MT19937', lambda s: np.random.Generator(np.random.MT19937(s)))]
print('  %-20s %10s %10s %8s %8s' % ('생성기', '평균 H', '정확과의 차', 'z', '초'))
rec['gens'] = []
for nm, mk in gens:
    t = time.perf_counter(); h = mc.boot_h_values(xp, CNT, B, mk(11), 200000); dt = time.perf_counter() - t
    m = float(h.mean()); first = np.round(h[:3], 4).tolist()
    print('  %-20s %10.6f %+10.6f %+8.2f %8.2f   첫 3개 %s' % (nm, m, m - mean_ex, (m - mean_ex) / se, dt, first))
    rec['gens'].append({'name': nm, 'mean': m, 'diff': m - mean_ex, 'z': (m - mean_ex) / se, 'seconds': dt})
print('  numpy 기본 생성기의 종류:', type(np.random.default_rng(11).bit_generator).__name__)

print('\n[5] 시드 11로 만든 독립 흐름 8개 (SeedSequence.spawn): 평균과 흐름 사이 상관')
kids = np.random.SeedSequence(11).spawn(8)
st = [np.random.default_rng(k) for k in kids]
means = [mc.boot_h_values(xp, CNT, B, g, 200000).mean() for g in st]
print('  흐름별 평균 H:', ' '.join('%.5f' % m for m in means), '| 정확 %.5f, 표준오차 %.5f' % (mean_ex, se))
u = np.array([np.random.default_rng(k).random(100000) for k in kids])
cc = np.corrcoef(u); off = cc[np.triu_indices(8, 1)]
print('  난수 10만 개씩 흐름 사이 상관: 절댓값 최대 %.4f (독립이면 약 1/sqrt(1e5) = %.4f 규모)' % (np.abs(off).max(), 1 / math.sqrt(100000)))
rec['spawn'] = {'means': [float(m) for m in means], 'max_abs_corr': float(np.abs(off).max())}

print('\n[6] 옛 방식(np.random.seed)과 새 방식(default_rng)은 같은 시드 11이어도 다른 수열')
np.random.seed(11); old = np.random.random(3)
new = np.random.default_rng(11).random(3)
print('  np.random.seed(11); np.random.random(3) =', np.round(old, 6), '| default_rng(11).random(3) =', np.round(new, 6))

print('\n[7] 정수 뽑기와 실수 뽑기: 같은 시드에서 첫 값')
print('  default_rng(11).integers(0, 9, 5) =', np.random.default_rng(11).integers(0, 9, 5), '| .random(2) =', np.round(np.random.default_rng(11).random(2), 6))
with open(os.path.join(HERE, 'p04-rng.json'), 'w', encoding='utf-8') as f:
    json.dump(rec, f, ensure_ascii=False)
