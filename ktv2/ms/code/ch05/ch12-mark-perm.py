# -*- coding: utf-8 -*-
"""5장 실습 5-3: 제1권 12장 계산 12-8(표지 순열 검정 시연)을 같은 시드로 되풀이하고,
순열 횟수를 늘리면 p가 어디로 모이는지 잰다. 날짜 분포와 표지는 제1권과 같은 시연값이다(논문 자료가 아니다).
실행: python3 ch12-mark-perm.py | tee ch12-mark-perm.log
"""
import time, platform
import numpy as np

T0 = time.perf_counter()
print('환경: python %s, numpy %s' % (platform.python_version(), np.__version__))

# ---- 제1권 ch12-calc-v1.py 계산 12-8 코드(같은 시드, 같은 순서) ----
rs = np.random.default_rng(2021)
N, M = 682, 45
allt = np.clip(rs.normal(5200, 800, N), 3000, 7000)
edges = np.arange(7000, 2999, -200)


def prop_by_bin(t, mark):
    out = []
    for x0, x1 in zip(edges[:-1], edges[1:]):
        m = (t <= x0) & (t > x1)
        out.append(mark[m].sum() / max(m.sum(), 1))
    return np.array(out)


def stat(t, mark):
    p = prop_by_bin(t, mark)
    base = mark.mean()
    return float(((p - base) ** 2).sum())


mk = np.zeros(N, bool); mk[rs.choice(N, M, replace=False)] = True
obs = stat(allt, mk)
t = time.perf_counter()
perm = np.array([stat(allt, rs.permutation(mk)) for _ in range(1000)])
p_one = (1 + (perm >= obs).sum()) / (1 + len(perm))
print('\n== A. 제1권 계산 12-8의 되풀이 (순열 1000회, 시드 2021) ==')
print('관측 통계 %.4f, 순열 중앙 %.4f, 95%% %.4f, p = %.3f   (%.1f초)' % (obs, np.median(perm), np.percentile(perm, 95), p_one, time.perf_counter() - t))
print('제1권: 관측 0.1477, 순열 중앙 0.0653, 95% 0.1724, p = 0.110')
mk2 = np.zeros(N, bool); late = np.where(allt < 4500)[0]
mk2[rs.choice(N, M - 10, replace=False)] = True
mk2[:] = mk2; mk2[late[:10]] = True
obs2 = stat(allt, mk2)
perm2 = np.array([stat(allt, rs.permutation(mk2)) for _ in range(1000)])
print('표지 10개를 4500 이후에 몰았을 때: 관측 %.4f, p = %.3f (제1권: 0.1405, p = 0.120)' % (obs2, (1 + (perm2 >= obs2).sum()) / 1001))
print('표지 수(몰기 뒤) = %d (몰린 자리가 이미 표지였다면 45보다 작아진다)' % mk2.sum())

# ---- 빠른 구현: 날짜가 속한 칸 번호를 한 번만 구해 두고 표지 자리만 섞는다 ----
nb = len(edges) - 1
binid = np.full(N, nb)                           # nb = 어느 칸에도 속하지 않음(t == 3000 등)
for i, (x0, x1) in enumerate(zip(edges[:-1], edges[1:])):
    binid[(allt <= x0) & (allt > x1)] = i
nbin = np.bincount(binid, minlength=nb + 1)[:nb].astype(float)
print('\n칸 %d개, 칸에 속한 날짜 %d개, 어느 칸에도 속하지 않은 날짜 %d개 (제1권 구현과 같은 규칙)' % (nb, int((binid < nb).sum()), int((binid == nb).sum())))


def stat_fast(counts, nmark):
    p = counts[:, :nb] / np.maximum(nbin, 1)
    base = nmark / N
    return ((p - base) ** 2).sum(axis=1)


def obs_fast(mark):
    c = np.bincount(binid[mark], minlength=nb + 1)[None, :].astype(float)
    return float(stat_fast(c, int(mark.sum()))[0])


print('빠른 구현의 관측 통계: %.4f (느린 구현 %.4f), 몰기 뒤 %.4f (느린 구현 %.4f)' % (obs_fast(mk), obs, obs_fast(mk2), obs2))
# 느린 구현과 같은 순열 1000개의 통계가 같은지 점검: 같은 시드로 순열을 만들어 두 구현에 넣는다
rs_chk = np.random.default_rng(99)
perms = [rs_chk.permutation(mk) for _ in range(200)]
slow = np.array([stat(allt, q) for q in perms])
fast = np.array([stat_fast(np.bincount(binid[q], minlength=nb + 1)[None, :].astype(float), int(q.sum()))[0] for q in perms])
print('같은 순열 200개에서 두 구현의 통계 최대 차 = %.2e' % np.abs(slow - fast).max())


def perm_p(mark, B, seed, chunk=20000):
    rng = np.random.default_rng(seed)
    o = obs_fast(mark); nm = int(mark.sum())
    ge = 0; left = B
    while left > 0:
        m = min(chunk, left)
        keys = rng.random((m, N))
        sel = np.argpartition(keys, nm, axis=1)[:, :nm]
        cnt = np.zeros((m, nb + 1))
        rows = np.repeat(np.arange(m), nm)
        np.add.at(cnt, (rows, binid[sel].ravel()), 1)
        ge += int((stat_fast(cnt, nm) >= o - 1e-12).sum())
        left -= m
    return (ge + 1) / (B + 1)


print('\n== B. 순열 횟수에 따른 p의 안정 (표지가 무작위로 붙은 경우: 제1권의 mk) ==')
print('%10s %10s %10s %10s %10s %10s %10s' % ('B', '평균 p', '최소 p', '최대 p', '표준편차', '되풀이', '시간(초)'))
for B in (1000, 10000, 100000, 1000000):
    reps = 20 if B <= 10000 else (10 if B == 100000 else 3)
    t = time.perf_counter()
    ps = np.array([perm_p(mk, B, 31000 + s) for s in range(reps)])
    print('%10s %10.4f %10.4f %10.4f %10.4f %10d %10.1f' % ('{:,}'.format(B), ps.mean(), ps.min(), ps.max(), ps.std(ddof=1), reps, time.perf_counter() - t))
print('\n== C. 표지를 4500 이후로 몬 경우(제1권의 mk2) ==')
for B in (1000, 10000, 100000):
    reps = 20 if B <= 10000 else 10
    ps = np.array([perm_p(mk2, B, 32000 + s) for s in range(reps)])
    print('%10s %10.4f %10.4f %10.4f %10.4f' % ('{:,}'.format(B), ps.mean(), ps.min(), ps.max(), ps.std(ddof=1)))
print('\n걸린 시간 %.1f초' % (time.perf_counter() - T0))
