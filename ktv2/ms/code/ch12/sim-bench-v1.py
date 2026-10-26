# -*- coding: utf-8 -*-
"""12장 실습 12-4: z840(또는 어떤 GPU 컴퓨터)에서 한 번 돌려 시뮬레이션 두 작업의 시간과 메모리를 로그로 남기는 스크립트.
10장의 gpu-bench-v1.py의 도구(env_info, timeit, mem_snapshot, is_oom)를 그대로 불러 쓴다. numpy와 cupy 어느 쪽으로든 돈다.
  python sim-bench-v1.py --xp numpy --tag cpu            # CPU 경로(이 책의 컨테이너에서 실행한 방식)
  python sim-bench-v1.py --xp cupy  --tag z840           # GPU 경로 (CuPy 설치 필요)
  python sim-bench-v1.py --xp cupy --tag z840 --P 2000,8000,32000,128000   # 매개변수 조합 수를 바꿔 메모리 한계 찾기
작업: shore(경사 x 융기 격자의 해안선 후퇴, 모형 A), diff(확산 + 해수면 + 해안선, 모형 C를 매개변수 P개 한꺼번에)
측정: 첫 반복은 준비(warm-up), 나머지 reps번의 중앙값과 최솟값. cupy는 매 반복 뒤 동기화. 메모리가 모자라면 'OOM'으로 적고 다음으로 간다.
결과 숫자(질량 보존 비, 5 ka 해안선의 평균 등)도 적어 CPU와 GPU가 같은 값을 내는지 본다(확산 계산은 난수가 없으므로 둘이 부동소수점 반올림 수준에서 같아야 한다)."""
import argparse, importlib.util, json, math, os, statistics, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
sc = load('sc', os.path.join(HERE, 'sim-core-v1.py'))
gb = load('gb', os.path.join(HERE, '..', 'ch10', 'gpu-bench-v1.py'))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xp', default='auto'); ap.add_argument('--tag', default='run'); ap.add_argument('--out', default=None)
    ap.add_argument('--P', default='500,2091,8000'); ap.add_argument('--shore-P', default='2460,24600,246000')
    ap.add_argument('--nx', type=int, default=600); ap.add_argument('--reps', type=int, default=3); ap.add_argument('--steps', type=int, default=1000)
    a = ap.parse_args()
    xp = sc.choose_xp(a.xp)
    out = a.out or os.path.join(HERE, 'sim-bench-%s.jsonl' % a.tag)
    info = gb.env_info(xp)
    print('환경:', json.dumps(info, ensure_ascii=False))
    rows = [{'kind': 'env', **info}]
    print('%-22s %-8s %-10s %-10s %-26s %s' % ('항목', 'warmup s', '중앙값 s', '최솟값 s', '결과', '메모리'))
    def do(kind, name, fn, extra):
        try:
            if xp is not np: xp.get_default_memory_pool().free_all_blocks()
            w, ts, res = gb.timeit(xp, fn, a.reps)
            rec = {'kind': kind, 'name': name, **extra, 'warmup_s': w, 'median_s': statistics.median(ts), 'min_s': min(ts), 'result': res, **gb.mem_snapshot(xp)}
            print('%-22s %-8.3f %-10.4f %-10.4f %-26s %s' % (name, w, rec['median_s'], rec['min_s'], str(res)[:26], {k: v for k, v in rec.items() if k.endswith('_mib')}))
        except Exception as e:
            if not gb.is_oom(xp, e): raise
            rec = {'kind': kind, 'name': name, **extra, 'status': 'OOM'}; print('%-22s OOM' % name)
        rows.append(rec)
    x = np.arange(0.0, 500.0001, 0.5)
    for P in [int(v) for v in a.shore_P.split(',') if v]:
        def fn(P=P):
            rng = np.random.default_rng(P)
            s = 1.0 / np.exp(rng.uniform(math.log(100), math.log(5000), P)); u = rng.uniform(-1, 1, P)
            z = sc.terrain_uniform(xp, x, -40.0, s)
            x9 = sc.shoreline(xp, z, x, float(sc.to_host(xp, sc.sea_level(xp, 9.0))))
            x5 = sc.shoreline(xp, z, x, float(sc.to_host(xp, sc.sea_level(xp, 5.0))) - xp.asarray(u) * 4.0)
            return round(float(sc.to_host(xp, xp.nanmax(x5 - x9))), 3)
        do('shore', 'shore P=%d' % P, fn, {'P': P, 'nx': len(x)})
    dx, dt = 300.0 / a.nx, 0.004
    xc = np.arange(dx / 2, 300.0, dx); nx = len(xc)
    for P in [int(v) for v in a.P.split(',') if v]:
        def fn(P=P):
            rng = np.random.default_rng(P)
            kap = np.exp(rng.uniform(0, math.log(20), P)); q = rng.uniform(0, 150, P)
            z0 = sc.terrain_uniform(xp, xc, -40.0, [1 / 1000.0]); g = sc.gauss_source(xp, xc, 25.0, 6.0, dx)
            D, out = sc.diffuse_run(xp, xp.zeros((P, nx)), kap, dx, dt, a.steps, q * dt, g, (a.steps,))
            mass = float(sc.to_host(xp, (D.sum(axis=1) * dx / (q * a.steps * dt + 1e-12)).mean()))
            xs = sc.shoreline(xp, z0 + D, xc, float(sc.to_host(xp, sc.sea_level(xp, 5.0))))
            return [round(mass, 6), round(float(sc.to_host(xp, xp.nanmean(xs))), 4)]
        do('diff', 'diff P=%d' % P, fn, {'P': P, 'nx': nx, 'steps': a.steps})
    with open(out, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('로그 파일:', out)

if __name__ == '__main__':
    main()
