import math
from math import exp, sqrt, erfc
try:
    from scipy import stats
except Exception:
    stats = None
def p2(z): return erfc(abs(z) / sqrt(2))
print('== 5-1 상관과 회귀 (Elsner & Liu 2003, n=58)')
n = 58
for r in (-0.37, -math.sqrt(0.140)):
    t = r * sqrt(n - 2) / sqrt(1 - r * r)
    print(' r=%.4f r2=%.4f t=%.3f p=%.4f' % (r, r * r, t, 2 * stats.t.sf(abs(t), n - 2) if stats else -1))
print(' slope t', -0.452 / 0.1499, ' (d) t', 0.277 / 0.0585, ' r', sqrt(0.286), ' t from r', sqrt(0.286) * sqrt(56) / sqrt(1 - 0.286))
print('== 5-2 연평균, 합')
print(409 + 378 + 215, [round(x / 58, 2) for x in (409, 378, 215)])
print('== 5-3 표 3 ENSO')
for nm, a, b in (('SM', 152, 127), ('R', 120, 147), ('NO', 52, 89)):
    print(nm, a / 20, b / 20)
for z in (1.014, -1.747, -2.730, 0.612, -0.723, 0.602, 0.777, -0.649, -0.877):
    print(' z', z, 'p2=%.3f' % p2(z))
print(' p=0.099 -> z', stats.norm.isf(0.099 / 2))
print('== 5-4 포아송 (Table 4)')
cold = [1,3,0,3,7,0,4,0,1,0,0,1,5,1,5,0,2,0,4,1]; warm = [1,1,1,1,0,2,4,0,0,0,2,2,2,1,0,3,0,0,3,1]
def pge(k, l): return 1 - sum(exp(-l) * l**i / math.factorial(i) for i in range(k))
lc, lw = sum(cold) / 20, sum(warm) / 20
print(' rates', lc, lw, 'grand', (lc + lw) / 2, 'ratio', lc / lw, 'increase %', (lc / lw - 1) * 100)
print(' P(>=3)', pge(3, lc), pge(3, lw), ' P(0)', exp(-lc), exp(-lw))
print(' reported 35%,15% -> lambda', [l / 100 for l in range(100, 300) if abs(pge(3, l / 100) - 0.35) < 0.003][:1], [l / 100 for l in range(60, 200) if abs(pge(3, l / 100) - 0.15) < 0.003][:1])
k, N = 38, 62
pb = sum(math.comb(N, i) for i in range(k, N + 1)) / 2**N
print(' conditional binomial p(one-sided)', pb, ' z', (k - N / 2) / sqrt(N / 4))
print('== 5-5 k-means')
x = [2, 4, 5, 9, 10, 12]; c = [2.0, 12.0]
for it in range(5):
    g = [min((0, 1), key=lambda j: abs(v - c[j])) for v in x]
    nc = [sum(v for v, gg in zip(x, g) if gg == j) / g.count(j) for j in (0, 1)]
    ss = sum((v - nc[gg]) ** 2 for v, gg in zip(x, g))
    print(' iter', it, g, nc, round(ss, 3))
    if nc == c: break
    c = nc
print('== 5-6 Shi 2014 식')
for U in (0.8525,): print(' SST', (U - 0.044) / 0.033)
print(' U from 24.5', 0.044 + 0.033 * 24.5, ' err', 0.006 / 0.033)
for sss in (34.7, 36.42): print(' d18Osw eq5', 0.29 * sss - 9.85, 'eq4', 0.203 * sss - 6.76)
print(' d18Osw diff eq5', 0.29 * (36.42 - 34.7))
T = 24.54; a = 0.07; b = -4.28; cc = 14.32 - T
xx = (-b - sqrt(b * b - 4 * a * cc)) / (2 * a); print(' x', xx, ' T', 14.32 - 4.28 * xx + 0.07 * xx * xx)
print(' dT effect', 0.3 / 4.28, 0.3 * 0.22, 0.066 / 0.74)
print(' SMOW', 1.03092 * (-1.0) + 30.917)
print('== 5-7 퇴적률')
tab = [(10, 3301), (106, 7542), (150, 12328), (318, 17913)]
for (d0, a0), (d1, a1) in zip(tab, tab[1:]): print(' ', (d1 - d0) / ((a1 - a0) / 1000))
print(' 178/158', 20 / (((12384 + 12491) / 2 - (12220 + 12392) / 2) / 1000), (12384 + 12491) / 2 - (12220 + 12392) / 2)
print(' ash', 7.54 - 7.5, 79.44 - 84, 79.44 - 89, 30.67)
print('== 5-8 Zhou')
print(' flood YR', 1.84 - 1.15, (1.84 / 1.15 - 1) * 100, ' south', 2.45 - 2.16, (2.45 / 2.16 - 1) * 100)
print(' r2', 0.5 ** 2, ' lag', 1700 - 1570, 1700 - 1450, 1700 - 1510, ' NC/YR', 500 - 464, 986)
print('== 5-9 Park')
print(' samples', (120 - 10) / 2 + 1, ' cm/yr', 110 / (1925 - 900), ' yr/sample', 2 / (110 / (1925 - 900)))
print(' endmember', (-20 - (-26)) / (-12 - (-26)), (-20 - (-30)) / (-10 - (-30)))
print(' sqrt', [v ** 0.5 for v in (4, 16, 25)])
print(' MCA 900-1320', 1320 - 900, 'LIA 1350-1850', 1850 - 1350, ' dry 1180-1320', 140)
print('== 시연 계산 (이론 배경 상자)')
xs = [1, 2, 3, 4, 5]; ys = [2, 1, 4, 3, 5]
mx = sum(xs) / 5; my = sum(ys) / 5
sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys)); sxx = sum((a - mx) ** 2 for a in xs); syy = sum((b - my) ** 2 for b in ys)
r = sxy / math.sqrt(sxx * syy); t = r * math.sqrt(3) / math.sqrt(1 - r * r)
print(' r', sxy, sxx, syy, r, r * r, 't', t, 'p', 2 * stats.t.sf(t, 3), 'slope', sxy / sxx, 'icpt', my - sxy / sxx * mx)
print(' poisson lam=2 P0', exp(-2), 1 - exp(-2), ' P(>=2)', 1 - exp(-2) * 3)
# z test two means (demo): 9 vs 7, sd 3, n 25 each
se = math.sqrt(3**2/25 + 3**2/25); z = (9 - 7) / se; print(' z demo', se, z, p2(z))
# interval overlap
def ov(a, b): return max(0, min(a[1], b[1]) - max(a[0], b[0]))
dry = {'D1': (1000, 1080), 'D2': (1180, 1320), 'D3': (1420, 1510), 'D4': (1760, 1880)}; wet = (1520, 1760)
Z = {'Zneg': (1420, 1625), 'Zmin': (1450, 1570), 'Zstrong': (1000, 1300), 'Zhigh': (1000, 1230), 'Zflood': (1400, 1600), 'YR_MWP': (1000, 1200)}
for dn, d in dry.items():
    print(' ', dn, d, {k: ov(d, v) for k, v in Z.items()})
print(' wet', {k: ov(wet, v) for k, v in Z.items()})
MCA = (900, 1350); LIA = (1350, 1850)
dm = sum(ov(d, MCA) for d in dry.values()); dl = sum(ov(d, LIA) for d in dry.values()); wl = ov(wet, LIA)
print(' MCA dry', dm, dm / 450, ' LIA dry', dl, dl / 500, ' LIA wet', wl, wl / 500, ' unclassified LIA', 500 - dl - wl, ' MCA', 450 - dm)
print(' MCA dry listed D3 within?', ov(dry['D3'], MCA))
# SST modern references
print(' modern', (21.43 + 22.03 + 28.43 + 26.45) / 4, 24.54 - 21.8, 24.54 - 22.02, 24.54 - 21.5, 24.87 - 21.5, 24.87 - 21.8)
print(' DOT err', math.hypot(22, 5), 160 - 140)
print(' event spacing', [(a + b) / 2 for a, b in ((15.8, 17.1), (24.3, 26), (29.9, 31.6), (37.3, 39.5), (46.9, 49.4))])
m = [(a + b) / 2 for a, b in ((15.8, 17.1), (24.3, 26), (29.9, 31.6), (37.3, 39.5), (46.9, 49.4))]
sp = [m[i + 1] - m[i] for i in range(4)]; print(' spacing', sp, sum(sp) / 4)
print(' dur', [round(b - a, 2) for a, b in ((15.8, 17.1), (24.3, 26), (29.9, 31.6), (37.3, 39.5), (46.9, 49.4))])
print(' factors', 44.84 + 22.88 + 15.73 + 12.28)
print(' APO demo', -52.0 - (-55.5))
print(' Walker etc none')
