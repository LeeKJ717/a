# -*- coding: utf-8 -*-
"""5장 실습 5-9: 재표집 횟수를 늘리면 CPU가 어디까지 가는가 (제2권 11장 GPU 몬테카를로의 출발점).
GPU 없이 이 컨테이너의 CPU에서 실제로 시간과 메모리를 잰다. GPU 시간은 z840 실행 필요.
각 측정은 별도 프로세스에서 한다(최대 메모리 ru_maxrss가 다른 측정과 섞이지 않게).
사용: python3 scale-cpu.py            (표준 범위: 1e8까지)
      python3 scale-cpu.py big        (1e9 부트스트랩, 약 수 분)
"""
import sys, os, time, json, platform, subprocess, resource
import numpy as np

n = 18
rs = np.random.default_rng(42)
X = np.round(rs.lognormal(1.0, 0.8, n), 3)          # bootstrap-basic.py의 시연 표본과 같다


def hist_quantiles(h, lo, hi, qs):
    c = np.cumsum(h) / h.sum()
    w = (hi - lo) / len(h)
    out = []
    for q in qs:
        i = int(np.searchsorted(c, q))
        prev = c[i - 1] if i > 0 else 0.0
        frac = (q - prev) / max(c[i] - prev, 1e-300)
        out.append(lo + (i + frac) * w)
    return out


def work(mode, B, seed, chunk):
    t0 = time.perf_counter()
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    if mode in ('boot-idx', 'boot-multi'):
        nb = 4000; lo, hi = 0.0, 8.0
        h = np.zeros(nb); s = 0.0; ss = 0.0; left = B
        wts = np.full(n, 1.0 / n)
        while left > 0:
            m = min(chunk, left)
            if mode == 'boot-idx':
                v = X[rng.integers(0, n, size=(m, n))].mean(axis=1)
            else:
                v = rng.multinomial(n, wts, size=m) @ X / n
            h += np.histogram(v, bins=nb, range=(lo, hi))[0]
            s += v.sum(); ss += (v * v).sum(); left -= m
        mean = s / B; sd = (ss / B - mean * mean) ** 0.5
        q = hist_quantiles(h, lo, hi, [0.025, 0.975])
        res = dict(stat1=mean, stat2=sd, lo=q[0], hi=q[1])
    elif mode == 'perm-shuffle':
        lab = np.array([1] * 20 + [0] * 12)
        ge = 0; left = B
        while left > 0:
            m = min(chunk, left)
            idx = np.argpartition(rng.random((m, 32)), 18, axis=1)[:, :18]
            ge += int((lab[idx].sum(axis=1) >= 16).sum()); left -= m
        res = dict(stat1=(ge + 1) / (B + 1), stat2=ge)
    elif mode == 'perm-hyper':
        ge = 0; left = B
        while left > 0:
            m = min(chunk, left)
            ge += int((rng.hypergeometric(20, 12, 18, size=m) >= 16).sum()); left -= m
        res = dict(stat1=(ge + 1) / (B + 1), stat2=ge)
    res['sec'] = time.perf_counter() - t0
    res['rss_mb'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    res['B'] = B; res['mode'] = mode
    return res


JSONL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scale-cpu.jsonl')


def run(mode, B, seed=1, chunk=100000):
    p = subprocess.run([sys.executable, __file__, '--worker', mode, str(B), str(seed), str(chunk)], capture_output=True, text=True)
    r = json.loads(p.stdout.strip().splitlines()[-1])
    r['chunk'] = chunk
    with open(JSONL, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(r) + '\n')
    return r


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        print(json.dumps(work(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))))
        sys.exit(0)
    big = len(sys.argv) > 1 and sys.argv[1] == 'big'
    if not big and os.path.exists(JSONL):
        os.remove(JSONL)
    print('환경: python %s, numpy %s, CPU 코어 %d, 메모리 %.1f GB, 장치: CPU만 (GPU 없음)' % (
        platform.python_version(), np.__version__, os.cpu_count(), os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2 ** 30))
    T0 = time.perf_counter()
    if big:
        print('\n== 1e9 부트스트랩 (인덱스 방식, 덩이 100,000) ==')
        r = run('boot-idx', 10 ** 9)
        print('B = 1,000,000,000: %.1f초, %.1f M 재표집/초, 최대 메모리 %.0f MB, 평균 %.4f 표준편차 %.4f 구간 %.4f ~ %.4f' % (r['sec'], r['B'] / r['sec'] / 1e6, r['rss_mb'], r['stat1'], r['stat2'], r['lo'], r['hi']))
        sys.exit(0)
    print('\n== E1. 부트스트랩(표본 n=18의 평균), 인덱스 방식. 덩이 크기 100,000 ==')
    print('%14s %10s %16s %12s %10s %10s %18s' % ('B', '시간(초)', '재표집/초(백만)', '최대 메모리MB', '평균', '표준편차', '2.5~97.5% 구간'))
    for B in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8):
        r = run('boot-idx', B)
        print('%14s %10.2f %16.2f %12.0f %10.4f %10.4f %9.4f ~ %-8.4f' % ('{:,}'.format(B), r['sec'], B / r['sec'] / 1e6, r['rss_mb'], r['stat1'], r['stat2'], r['lo'], r['hi']))
    print('\n== E1b. 덩이 크기가 시간과 메모리에 주는 영향 (B = 10,000,000) ==')
    print('%12s %10s %16s %12s' % ('덩이 크기', '시간(초)', '재표집/초(백만)', '최대 메모리MB'))
    for ch in (1000, 10000, 100000, 1000000, 10000000):
        r = run('boot-idx', 10 ** 7, 1, ch)
        print('%12s %10.2f %16.2f %12.0f' % ('{:,}'.format(ch), r['sec'], 1e7 / r['sec'] / 1e6, r['rss_mb']))
    print('\n== E2. 같은 부트스트랩을 다항분포로 (B = 10,000,000) ==')
    r = run('boot-multi', 10 ** 7)
    print('시간 %.2f초, %.2f M/초, 최대 메모리 %.0f MB, 평균 %.4f 표준편차 %.4f 구간 %.4f ~ %.4f' % (r['sec'], 1e7 / r['sec'] / 1e6, r['rss_mb'], r['stat1'], r['stat2'], r['lo'], r['hi']))
    print('\n== E3. 2x2 표 이름표 섞기(32명 순열), 한쪽 p ([[16,2],[4,10]]; 정확한 값 7.0771e-04) ==')
    print('%14s %10s %16s %12s %12s' % ('B', '시간(초)', '순열/초(백만)', '최대 메모리MB', '추정 p'))
    for B in (10 ** 5, 10 ** 6, 10 ** 7):
        r = run('perm-shuffle', B)
        print('%14s %10.2f %16.3f %12.0f %12.4e' % ('{:,}'.format(B), r['sec'], B / r['sec'] / 1e6, r['rss_mb'], r['stat1']))
    print('\n== E4. 같은 p를 초기하분포에서 바로 뽑기 (이름표를 섞은 결과의 분포가 초기하분포이므로 정확히 같은 분포) ==')
    print('%16s %10s %16s %12s %12s %14s' % ('B', '시간(초)', '추출/초(백만)', '최대 메모리MB', '추정 p', '표준오차'))
    for B in (10 ** 6, 10 ** 7, 10 ** 8, 10 ** 9):
        r = run('perm-hyper', B)
        p = r['stat1']
        print('%16s %10.2f %16.2f %12.0f %12.4e %14.2e' % ('{:,}'.format(B), r['sec'], B / r['sec'] / 1e6, r['rss_mb'], p, (p * (1 - p) / B) ** 0.5))
    print('\n== E5. 코어 두 개 (부트스트랩 B = 10^8, 독립 난수열 SeedSequence 둘) ==')
    t = time.perf_counter()
    procs = [subprocess.Popen([sys.executable, __file__, '--worker', 'boot-idx', str(5 * 10 ** 7), str(s), '100000'], stdout=subprocess.PIPE, text=True) for s in (11, 12)]
    outs = [json.loads(p.communicate()[0].strip().splitlines()[-1]) for p in procs]
    wall = time.perf_counter() - t
    print('두 프로세스(각 5x10^7)의 벽시계 시간 %.1f초, 각 프로세스 시간 %.1f / %.1f초, 합친 재표집/초 %.2f M' % (wall, outs[0]['sec'], outs[1]['sec'], 1e8 / wall / 1e6))
    print('\n전체 걸린 시간 %.0f초' % (time.perf_counter() - T0))
