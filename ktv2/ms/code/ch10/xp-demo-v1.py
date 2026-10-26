# -*- coding: utf-8 -*-
"""10장 실습 1: 같은 코드를 xp = numpy 또는 cupy로 바꿔 쓰는 방식.
제1권 11장의 두 계산을 배열 연산으로 다시 쓴 것이다.
  (가) 계산 11-4: 대산전 [1,3,1,2,2]의 유전자 다양도 H 부트스트랩 (제1권은 2만 회 반복문, 여기서는 배열)
  (나) 계산 11-13: 하버사인 거리 (제1권 R = 6371.0088 km). 점 N개의 N x N 거리 행렬
사용:  python xp-demo-v1.py --xp numpy|cupy|auto  [--B 1000000] [--chunk 200000] [--seed 11]
이 컨테이너에는 GPU가 없어 numpy 경로만 실행했다. cupy 경로는 실행하지 못했다."""
import argparse, math, sys, time
import numpy as np

def choose_xp(name):
    """name: 'numpy', 'cupy', 'auto'. cupy가 없거나 GPU가 없으면 auto는 numpy로 내려간다."""
    if name in ('cupy', 'auto'):
        try:
            import cupy as cp
            cp.cuda.runtime.getDeviceCount()          # 드라이버가 없으면 여기서 예외
            return cp
        except Exception as e:
            if name == 'cupy':
                raise SystemExit('cupy 경로를 쓸 수 없다: %s: %s' % (type(e).__name__, str(e).splitlines()[0]))
            print('[알림] cupy를 쓸 수 없어 numpy로 내려간다 (%s)' % type(e).__name__, file=sys.stderr)
    return np

def to_host(xp, a):
    """장치 배열을 NumPy 배열로. numpy 경로에서는 그대로."""
    return xp.asnumpy(a) if xp is not np else a

def boot_h(xp, counts, B, seed, chunk):
    """같은 빈도에서 n명을 복원추출하는 부트스트랩으로 Nei 다양도 H를 B번 구한다.
    H = n/(n-1) * (1 - sum p^2). 메모리를 제한하려고 chunk개씩 나눠 계산한다."""
    counts = list(counts); k = len(counts); n = sum(counts)
    labels = xp.asarray(np.repeat(np.arange(k), counts))        # 사람 n명의 하플로그룹 번호
    ks = xp.arange(k)
    rng = xp.random.default_rng(seed)
    out = []
    for start in range(0, B, chunk):
        m = min(chunk, B - start)
        idx = rng.integers(0, n, size=(m, n))                   # (m, n) 복원추출 번호
        cat = labels[idx]                                       # (m, n)
        c = (cat[:, :, None] == ks[None, None, :]).sum(axis=1)  # (m, k) 각 형의 수
        p = c / n
        out.append(n / (n - 1) * (1.0 - (p * p).sum(axis=1)))
    return xp.concatenate(out)

def haversine_matrix(xp, lon, lat, R=6371.0088, dtype=None):
    """lon, lat(도)의 N개 점 사이의 N x N 대원 거리(km)."""
    lon = xp.asarray(lon, dtype=dtype); lat = xp.asarray(lat, dtype=dtype)
    la = xp.radians(lat); lo = xp.radians(lon)
    dla = la[:, None] - la[None, :]
    dlo = lo[:, None] - lo[None, :]
    a = xp.sin(dla / 2) ** 2 + xp.cos(la)[:, None] * xp.cos(la)[None, :] * xp.sin(dlo / 2) ** 2
    return 2 * R * xp.arcsin(xp.sqrt(a))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xp', default='numpy'); ap.add_argument('--B', type=int, default=1000000)
    ap.add_argument('--chunk', type=int, default=200000); ap.add_argument('--seed', type=int, default=11)
    a = ap.parse_args()
    xp = choose_xp(a.xp)
    print('백엔드:', xp.__name__, '| numpy', np.__version__, '| python', sys.version.split()[0])
    t = time.perf_counter()
    h = boot_h(xp, [1, 3, 1, 2, 2], a.B, a.seed, a.chunk)
    q = to_host(xp, xp.percentile(h, xp.asarray([2.5, 50, 97.5])))
    print('(가) 대산전 H 부트스트랩 B=%d chunk=%d: 2.5%% %.3f 중앙 %.3f 97.5%% %.3f  (제1권 0.556 0.778 0.889)' % (a.B, a.chunk, q[0], q[1], q[2]))
    print('    H 평균 %.4f, 표본의 H(관측) = %.4f' % (float(h.mean()), 9 / 8 * (1 - 19 / 81)))
    # 노백산(128°03′E, 44°06′N)과 돈화 기상대(128°12′E, 43°22′N)
    lon = [128 + 3 / 60, 128 + 12 / 60]; lat = [44 + 6 / 60, 43 + 22 / 60]
    d = to_host(xp, haversine_matrix(xp, lon, lat))
    print('(나) 노백산-돈화 기상대 거리 = %.2f km  (제1권 82.43 km)' % d[0, 1])
    ok = (abs(q[0] - 0.556) < 5e-4 and abs(q[1] - 0.778) < 5e-4 and abs(q[2] - 0.889) < 5e-4 and abs(d[0, 1] - 82.43) < 5e-3)
    print('제1권 값과 일치:', '예' if ok else '아니오')
    print('총 걸린 시간 %.3f s' % (time.perf_counter() - t))

if __name__ == '__main__':
    main()
