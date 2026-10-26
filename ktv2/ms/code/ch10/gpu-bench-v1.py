# -*- coding: utf-8 -*-
"""10장 실습 3: z840(또는 어떤 GPU 컴퓨터)에서 한 번 돌려 시간과 메모리를 로그로 남기는 스크립트.
같은 폴더의 xp-demo-v1.py의 함수(boot_h, haversine_matrix)를 불러 쓴다. numpy와 cupy 어느 쪽으로든 돈다.

사용 예
  python gpu-bench-v1.py --xp numpy --tag cpu          # CPU 경로(이 책의 컨테이너에서 실행한 방식)
  python gpu-bench-v1.py --xp cupy  --tag z840         # GPU 경로 (CuPy 설치 필요)
  python gpu-bench-v1.py --xp cupy --tag z840 --hav-sizes 4000,8000,12000,16000   # 메모리 한계 찾기
결과: 화면 표 + --out 파일(기본 gpu-bench-<tag>.jsonl, 한 줄에 한 측정)
측정 방식: 첫 반복은 준비(warm-up)로 따로 적고, 나머지 reps번의 중앙값과 최솟값을 적는다.
           cupy는 매 반복 뒤 장치를 동기화(synchronize)한 뒤 시계를 읽는다. 동기화를 빼면 계산이 끝나기 전의 시간을 읽게 된다.
메모리: cupy는 메모리 풀이 확보한 바이트(total_bytes)와 쓰는 중인 바이트(used_bytes), 장치 전체와 남은 바이트(memGetInfo)를 적는다.
        numpy는 프로세스의 최대 상주 메모리(ru_maxrss, 지금까지의 최댓값)를 적는다.
메모리가 모자라면 그 항목을 'OOM'으로 적고 다음 항목으로 간다."""
import argparse, importlib.util, json, os, platform, resource, shutil, statistics, subprocess, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('xpd', os.path.join(HERE, 'xp-demo-v1.py'))
xpd = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(xpd)

def env_info(xp):
    info = {'python': sys.version.split()[0], 'platform': platform.platform(), 'numpy': np.__version__, 'backend': xp.__name__,
            'cpu_count': os.cpu_count()}
    try:
        with open('/proc/meminfo') as f: info['ram_total_kib'] = int(f.readline().split()[1])
    except Exception: pass
    if xp is not np:
        info['cupy'] = xp.__version__
        try:
            rt = xp.cuda.runtime
            info['cuda_runtime'] = rt.runtimeGetVersion(); info['cuda_driver'] = rt.driverGetVersion()
            pr = rt.getDeviceProperties(0)
            info['gpu_name'] = pr['name'].decode() if isinstance(pr['name'], bytes) else str(pr['name'])
            info['gpu_total_bytes'] = int(pr['totalGlobalMem'])
            info['gpu_cc'] = '%d.%d' % (pr['major'], pr['minor'])
        except Exception as e:
            info['gpu_query_error'] = '%s: %s' % (type(e).__name__, str(e).splitlines()[0])
    if shutil.which('nvidia-smi'):
        try:
            info['nvidia_smi'] = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'],
                                                capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception as e:
            info['nvidia_smi'] = 'error %s' % type(e).__name__
    else:
        info['nvidia_smi'] = '없음(명령을 찾지 못함)'
    return info

def sync(xp):
    if xp is not np: xp.cuda.Device().synchronize()

def mem_snapshot(xp):
    if xp is np:
        return {'peak_rss_mib': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)}
    mp = xp.get_default_memory_pool(); free, total = xp.cuda.runtime.memGetInfo()
    return {'pool_used_mib': round(mp.used_bytes() / 2**20, 1), 'pool_total_mib': round(mp.total_bytes() / 2**20, 1),
            'dev_free_mib': round(free / 2**20, 1), 'dev_total_mib': round(total / 2**20, 1)}

def is_oom(xp, e):
    if isinstance(e, MemoryError): return True
    return xp is not np and type(e).__name__ == 'OutOfMemoryError'

def timeit(xp, fn, reps):
    ts = []
    for i in range(reps + 1):
        sync(xp); t = time.perf_counter(); res = fn(); sync(xp); ts.append(time.perf_counter() - t)
    return ts[0], ts[1:], res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xp', default='auto'); ap.add_argument('--tag', default='run'); ap.add_argument('--out', default=None)
    ap.add_argument('--boot-sizes', default='100000,1000000,4000000'); ap.add_argument('--chunk', type=int, default=200000)
    ap.add_argument('--hav-sizes', default='1000,2000,4000'); ap.add_argument('--dtypes', default='float64,float32')
    ap.add_argument('--reps', type=int, default=3); ap.add_argument('--seed', type=int, default=11)
    a = ap.parse_args()
    xp = xpd.choose_xp(a.xp)
    out = a.out or os.path.join(HERE, 'gpu-bench-%s.jsonl' % a.tag)
    rows = []; info = env_info(xp)
    print('환경:', json.dumps(info, ensure_ascii=False))
    rows.append({'kind': 'env', **info})
    print('%-22s %-9s %-8s %-10s %-10s %-10s %s' % ('항목', 'dtype', 'warmup s', '중앙값 s', '최솟값 s', '결과', '메모리'))
    # (가) 부트스트랩
    for B in [int(x) for x in a.boot_sizes.split(',') if x]:
        name = 'boot B=%d' % B
        try:
            if xp is not np: xp.get_default_memory_pool().free_all_blocks()
            def fn():
                h = xpd.boot_h(xp, [1, 3, 1, 2, 2], B, a.seed, a.chunk)
                return xpd.to_host(xp, xp.percentile(h, xp.asarray([2.5, 50, 97.5])))
            w, ts, q = timeit(xp, fn, a.reps)
            rec = {'kind': 'boot', 'name': name, 'B': B, 'chunk': a.chunk, 'dtype': 'float64', 'warmup_s': w, 'median_s': statistics.median(ts),
                   'min_s': min(ts), 'q': [float(v) for v in q], **mem_snapshot(xp)}
            res = '%.3f/%.3f/%.3f' % tuple(rec['q'])
        except Exception as e:
            if not is_oom(xp, e): raise
            rec = {'kind': 'boot', 'name': name, 'B': B, 'status': 'OOM'}; w = ts = None; res = 'OOM'
        rows.append(rec)
        if 'median_s' in rec:
            print('%-22s %-9s %-8.3f %-10.4f %-10.4f %-10s %s' % (name, 'float64', rec['warmup_s'], rec['median_s'], rec['min_s'], res,
                  {k: v for k, v in rec.items() if k.endswith('_mib')}))
        else:
            print('%-22s %-9s OOM' % (name, 'float64'))
    # (나) 거리 행렬
    for dt in [x for x in a.dtypes.split(',') if x]:
        for N in [int(x) for x in a.hav_sizes.split(',') if x]:
            name = 'hav N=%d' % N
            one_mib = N * N * np.dtype(dt).itemsize / 2**20
            try:
                if xp is not np: xp.get_default_memory_pool().free_all_blocks()
                rng = np.random.default_rng(N)                     # 같은 N이면 dtype이 달라도 같은 점들
                lon = rng.uniform(100, 130, N); lat = rng.uniform(30, 50, N)
                def fn():
                    d = xpd.haversine_matrix(xp, lon, lat, dtype=dt)
                    return float(d.max())
                w, ts, mx = timeit(xp, fn, a.reps)
                rec = {'kind': 'hav', 'name': name, 'N': N, 'dtype': dt, 'one_matrix_mib': round(one_mib, 1), 'warmup_s': w,
                       'median_s': statistics.median(ts), 'min_s': min(ts), 'max_km': mx, **mem_snapshot(xp)}
                print('%-22s %-9s %-8.3f %-10.4f %-10.4f %-10.1f %s' % (name, dt, w, rec['median_s'], rec['min_s'], mx,
                      {k: v for k, v in rec.items() if k.endswith('_mib')}))
            except Exception as e:
                if not is_oom(xp, e): raise
                rec = {'kind': 'hav', 'name': name, 'N': N, 'dtype': dt, 'one_matrix_mib': round(one_mib, 1), 'status': 'OOM'}
                print('%-22s %-9s OOM (행렬 하나 %.1f MiB)' % (name, dt, one_mib))
            rows.append(rec)
    # 제1권 값과 맞는지
    xd = xpd.haversine_matrix(xp, [128 + 3 / 60, 128 + 12 / 60], [44 + 6 / 60, 43 + 22 / 60])
    km = float(xpd.to_host(xp, xd)[0, 1])
    print('제1권 값 점검: 노백산-돈화 거리 %.2f km (제1권 82.43 km) -> %s' % (km, '일치' if abs(km - 82.43) < 5e-3 else '불일치'))
    rows.append({'kind': 'check', 'distance_km': km, 'vol1_km': 82.43})
    with open(out, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('로그 파일:', out)

if __name__ == '__main__':
    main()
