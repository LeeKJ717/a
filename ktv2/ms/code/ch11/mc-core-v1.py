# -*- coding: utf-8 -*-
"""11장 공용 함수. 모든 계산 함수는 xp(numpy 또는 cupy)와 난수 생성기 rng를 받는다.
10장의 xp-demo-v1.py에서 choose_xp, to_host를 그대로 가져다 쓴다(같은 방식, 같은 이름).
이 컨테이너에는 GPU가 없어 numpy 경로만 실행했다. cupy 경로는 실행하지 못했다.
주의: cupy의 난수 생성기(Generator)에는 normal, permutation, shuffle, choice가 없다(cupy 14.2.0 설치본에서 확인, p04b 로그).
      그래서 이 파일은 integers, random, standard_normal, hypergeometric만 쓴다."""
import importlib.util, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('xpd', os.path.join(HERE, '..', 'ch10', 'xp-demo-v1.py'))
xpd = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(xpd)
choose_xp, to_host = xpd.choose_xp, xpd.to_host

def make_rng(xp, seed):
    """장치에 맞는 난수 생성기. numpy는 PCG64, cupy는 XORWOW(cupy 문서 설명)가 기본이다."""
    return xp.random.default_rng(seed)

def quantiles(xp, h, qs):
    """분위수(누적확률이 처음 q 이상이 되는 값, 'inverted cdf'). 정렬해 ceil(q*B)번째를 읽는다.
    numpy와 cupy에서 똑같이 동작하게 xp.percentile 대신 직접 쓴다."""
    s = xp.sort(h)
    B = int(s.shape[0])
    out = []
    for q in qs:
        k = max(int(math.ceil(q * B)) - 1, 0)
        out.append(float(to_host(xp, s[k])))
    return out

def boot_h_values(xp, counts, B, rng, chunk):
    """같은 빈도에서 n명을 복원추출해 Nei 다양도 H를 B번 구한다(10장 boot_h와 같은 방식, rng를 밖에서 받음)."""
    counts = list(counts); k = len(counts); n = sum(counts)
    labels = xp.asarray(np.repeat(np.arange(k), counts))
    ks = xp.arange(k)
    out = []
    for start in range(0, B, chunk):
        m = min(chunk, B - start)
        idx = rng.integers(0, n, size=(m, n))
        cat = labels[idx]
        c = (cat[:, :, None] == ks[None, None, :]).sum(axis=1)
        p = c / n
        out.append(n / (n - 1) * (1.0 - (p * p).sum(axis=1)))
    return xp.concatenate(out)

def nei_h(counts):
    n = sum(counts)
    return n / (n - 1) * (1 - sum((c / n) ** 2 for c in counts))

def exact_h_distribution(counts):
    """다항분포의 가능한 형별 수 벡터를 모두 세어 H의 값과 확률을 구한다(0장 exact-boot와 같은 방식).
    반환: (값 배열, 확률 배열, 평균)"""
    counts = list(counts); n = sum(counts); k = len(counts)
    p = [c / n for c in counts]
    from collections import defaultdict
    dist = defaultdict(float)
    def comps(total, parts):
        if parts == 1:
            yield (total,); return
        for i in range(total + 1):
            for rest in comps(total - i, parts - 1):
                yield (i,) + rest
    for v in comps(n, k):
        pr = math.factorial(n)
        for c, q in zip(v, p): pr = pr / math.factorial(c) * (q ** c)
        h = n / (n - 1) * (1 - sum((c / n) ** 2 for c in v))
        dist[round(h, 10)] += pr
    vals = np.array(sorted(dist)); pr = np.array([dist[v] for v in vals])
    return vals, pr, float((vals * pr).sum())

def exact_quantile(vals, pr, q):
    cum = np.cumsum(pr)
    return float(vals[int(np.searchsorted(cum, q - 1e-12))])

def perm_group1_counts(xp, labels01, n1, N, rng, chunk):
    """순열 검정: 0/1 표지 labels01(길이 n) 가운데 무작위로 n1명을 '1군'으로 뽑았을 때 1군의 1의 개수.
    N번 되풀이한 개수를 정수 배열로 돌려준다. 무작위 키를 만들어 열 방향으로 정렬하는 방식이다(재표본 없는 섞기)."""
    n = len(labels01)
    lab = xp.asarray(np.asarray(labels01, dtype=np.int64))
    out = []
    for start in range(0, N, chunk):
        m = min(chunk, N - start)
        keys = rng.random((m, n))
        order = xp.argsort(keys, axis=1)[:, :n1]
        out.append(lab[order].sum(axis=1))
    return xp.concatenate(out)

def hyp_pmf(a, b, c, d):
    """2x2 표 [[a,b],[c,d]]의 1행1열 칸 x에 대한 초기하분포 확률질량. 반환 (x 목록, 확률 목록)"""
    n = a + b + c + d; r1 = a + b; c1 = a + c
    lo, hi = max(0, c1 - (c + d)), min(r1, c1)
    xs = list(range(lo, hi + 1))
    ps = [math.comb(r1, x) * math.comb(c + d, c1 - x) / math.comb(n, c1) for x in xs]
    return xs, ps

def fisher_two_sided_exact(a, b, c, d):
    xs, ps = hyp_pmf(a, b, c, d)
    p0 = ps[xs.index(a)]
    return sum(p for p in ps if p <= p0 * (1 + 1e-9))

def hav_pair(xp, lon1, lat1, lon2, lat2, R=6371.0088):
    """두 점 사이의 하버사인 거리(km). 10장 haversine_matrix와 같은 식과 같은 R. 점마다 따로 짝을 지어 계산."""
    la1, la2 = xp.radians(lat1), xp.radians(lat2)
    dla = la2 - la1; dlo = xp.radians(lon2 - lon1)
    a = xp.sin(dla / 2) ** 2 + xp.cos(la1) * xp.cos(la2) * xp.sin(dlo / 2) ** 2
    return 2 * R * xp.arcsin(xp.sqrt(a))

def ar1_pair_corr(xp, n, rho, M, rng, burn=200):
    """서로 독립인 AR(1) 두 계열(길이 n, 1차 자기상관 rho, 분산 1)의 표본 상관 r을 M쌍에 대해 구한다.
    계열을 저장하지 않고 합계를 쌓아 가며 구한다(메모리 M개 분량)."""
    s = math.sqrt(1.0 - rho * rho)
    x = rng.standard_normal(M); y = rng.standard_normal(M)      # 정상 분포에서 시작
    for _ in range(burn):
        x = rho * x + s * rng.standard_normal(M); y = rho * y + s * rng.standard_normal(M)
    Sx = xp.zeros(M); Sy = xp.zeros(M); Sxx = xp.zeros(M); Syy = xp.zeros(M); Sxy = xp.zeros(M)
    for _ in range(n):
        Sx += x; Sy += y; Sxx += x * x; Syy += y * y; Sxy += x * y
        x = rho * x + s * rng.standard_normal(M); y = rho * y + s * rng.standard_normal(M)
    cov = Sxy - Sx * Sy / n
    return cov / xp.sqrt((Sxx - Sx * Sx / n) * (Syy - Sy * Sy / n))
