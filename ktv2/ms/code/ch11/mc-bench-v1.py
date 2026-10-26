# -*- coding: utf-8 -*-
"""11장 실습 11-7: z840(또는 어떤 GPU 컴퓨터)에서 한 번 돌려 몬테카를로 네 작업의 시간과 메모리를 로그로 남기는 스크립트.
10장의 gpu-bench-v1.py의 도구(env_info, timeit, mem_snapshot, is_oom)를 그대로 불러 쓴다. numpy와 cupy 어느 쪽으로든 돈다.

  python mc-bench-v1.py --xp numpy --tag cpu            # CPU 경로(이 책의 컨테이너에서 실행한 방식)
  python mc-bench-v1.py --xp cupy  --tag z840           # GPU 경로 (CuPy 설치 필요)
  python mc-bench-v1.py --xp cupy --tag z840 --reps 5 --sizes small   # 작은 크기만
작업: boot(부트스트랩 H), perm(순열 검정 p), prop(불확실성 전파, 정규 난수), arnull(AR(1) 두 계열의 상관)
측정: 첫 반복은 준비(warm-up)로 따로 적고 나머지 reps번의 중앙값과 최솟값을 적는다. cupy는 매 반복 뒤 동기화한다.
      결과 숫자(p̂, 평균, 분위수)도 함께 적어 정확한 값과 맞는지 볼 수 있게 한다. 같은 시드라도 numpy와 cupy는 다른 난수를 쓰므로
      결과는 비트 단위로 같지 않고 몬테카를로 오차 안에서 같아야 한다.
메모리가 모자라면 그 항목을 'OOM'으로 적고 다음으로 간다."""
import argparse, importlib.util, json, math, os, statistics, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
mc = load('mc', os.path.join(HERE, 'mc-core-v1.py'))
gb = load('gb', os.path.join(HERE, '..', 'ch10', 'gpu-bench-v1.py'))

SIZES = {'small': dict(boot=[100000], perm=[100000], prop=[1000000], ar=[20000]),
         'full': dict(boot=[100000, 1000000, 4000000], perm=[100000, 1000000, 4000000], prop=[1000000, 10000000, 40000000], ar=[20000, 100000])}
XS16 = None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xp', default='auto'); ap.add_argument('--tag', default='run'); ap.add_argument('--out', default=None)
    ap.add_argument('--sizes', default='full'); ap.add_argument('--chunk', type=int, default=200000); ap.add_argument('--reps', type=int, default=3)
    ap.add_argument('--seed', type=int, default=11)
    a = ap.parse_args()
    xp = mc.choose_xp(a.xp); sz = SIZES[a.sizes]
    out = a.out or os.path.join(HERE, 'mc-bench-%s.jsonl' % a.tag)
    info = gb.env_info(xp)
    try:
        info['bit_generator'] = type(xp.random.default_rng(1).bit_generator).__name__ if xp is np else 'cupy 기본(문서: XORWOW)'
    except Exception as e:
        info['bit_generator'] = '확인 실패 %s' % type(e).__name__
    print('환경:', json.dumps(info, ensure_ascii=False))
    rows = [{'kind': 'env', **info}]
    print('%-20s %-8s %-10s %-10s %-22s %s' % ('항목', 'warmup s', '중앙값 s', '최솟값 s', '결과', '메모리'))
    xs, ps = mc.hyp_pmf(16, 2, 4, 10); pmf = dict(zip(xs, ps)); p0 = pmf[16]
    reg = xp.asarray(np.array([x for x in xs if pmf[x] <= p0 * (1 + 1e-9)]))
    labels = [1] * 20 + [0] * 12
    def do(kind, name, fn, extra):
        try:
            if xp is not np: xp.get_default_memory_pool().free_all_blocks()
            w, ts, res = gb.timeit(xp, fn, a.reps)
            rec = {'kind': kind, 'name': name, **extra, 'warmup_s': w, 'median_s': statistics.median(ts), 'min_s': min(ts), 'result': res, **gb.mem_snapshot(xp)}
            print('%-20s %-8.3f %-10.4f %-10.4f %-22s %s' % (name, w, rec['median_s'], rec['min_s'], str(res)[:22], {k: v for k, v in rec.items() if k.endswith('_mib')}))
        except Exception as e:
            if not gb.is_oom(xp, e): raise
            rec = {'kind': kind, 'name': name, **extra, 'status': 'OOM'}; print('%-20s OOM' % name)
        rows.append(rec)
    for B in sz['boot']:
        def fn(B=B):
            h = mc.boot_h_values(xp, [1, 3, 1, 2, 2], B, mc.make_rng(xp, a.seed), a.chunk)
            return [round(float(mc.to_host(xp, h.mean())), 5)] + [round(v, 4) for v in mc.quantiles(xp, h, (0.025, 0.975))]
        do('boot', 'boot B=%d' % B, fn, {'B': B, 'chunk': a.chunk})
    for N in sz['perm']:
        def fn(N=N):
            c = mc.perm_group1_counts(xp, labels, 18, N, mc.make_rng(xp, a.seed), a.chunk)
            return round(float(mc.to_host(xp, xp.isin(c, reg).mean())) if hasattr(xp, 'isin') else float(mc.to_host(xp, (c[:, None] == reg[None, :]).any(axis=1).mean())), 6)
        do('perm', 'perm N=%d' % N, fn, {'N': N, 'chunk': a.chunk, 'p_exact': 0.000790})
    for N in sz['prop']:
        def fn(N=N):
            rng = mc.make_rng(xp, a.seed); k = 0; s = 0.0; step = 10000000
            for st in range(0, N, step):
                m = min(step, N - st)
                d = (rng.standard_normal(m) * 5 - 80) - (rng.standard_normal(m) * 10 - 120)
                k += int(mc.to_host(xp, (d <= 0).sum())); s += float(mc.to_host(xp, d.sum()))
            return [round(s / N, 4), k / N]
        do('prop', 'prop N=%d' % N, fn, {'N': N, 'p_exact': 1.733e-4})
    for M in sz['ar']:
        def fn(M=M):
            r = mc.ar1_pair_corr(xp, 414, 0.72, M, mc.make_rng(xp, a.seed))
            return round(float(mc.to_host(xp, r.std())), 5)
        do('arnull', 'arnull M=%d' % M, fn, {'M': M, 'n': 414, 'rho': 0.72, 'sd_expected': round(1 / math.sqrt(414 * (1 - .72 ** 2) / (1 + .72 ** 2)), 5)})
    with open(out, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('로그 파일:', out)

if __name__ == '__main__':
    main()
