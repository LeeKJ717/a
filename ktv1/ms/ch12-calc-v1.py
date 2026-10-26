# -*- coding: utf-8 -*-
"""12장 계산 재현 v1. 표준 라이브러리 + numpy + scipy (+ geomap의 shapely, 12-17만).
입력은 Kim 등(2021, 6106·4623), Kim 등(2025, 121), Lee J.(2017, 6127), Lee 등(2011, 120),
Nelson 등(2020, 13), Robbeets 등(2021, 1)의 본문에서 옮긴 값이다.
'시연값'은 절차를 보이기 위해 이 책이 정한 값이며 논문의 값이 아니다.
'이 책의 계산'은 논문에 없는 계산이며, 가정을 그 자리에 적었다."""
import math, os, sys
from math import sqrt, log, exp
import numpy as np
from scipy import stats

def hdr(s): print('\n' + '=' * 8, s)
def pct(a, b): return 100.0 * a / b
def bc(calbp):                      # 연대 = 1950 - cal BP. 음수는 기원전
    y = 1950 - calbp
    return ('기원전 %d' % -y) if y <= 0 else ('기원후 %d' % y)
def yr(calbp): return 1950 - calbp  # 음수 = BC
def overlap(a0, a1, b0, b1):        # 두 구간(연 단위, 작은 값이 앞)의 겹치는 길이
    return max(0, min(a1, b1) - max(a0, b0))

# ================================================================== 계산 12-1: 연대 눈금 옮기기와 시기 구분 대응표
hdr('계산 12-1 시기 구분 대응: 6106의 cal BP를 기원전으로 옮겨 121의 기원전 구분과 겹침을 잰다 (연대 = 1950 - cal BP)')
K = [('Incipient', 10000, 8000), ('Initial', 8000, 6500), ('Early', 6500, 5500), ('Middle', 5500, 5000), ('Late', 5000, 4000), ('Final', 4000, 3500)]
Kbc = [(n, -yr(a), -yr(b)) for n, a, b in K]               # (이름, 시작 기원전, 끝 기원전) 양수 = 기원전
for (n, a, b), (_, x, y) in zip(K, Kbc):
    print('6106 %-9s %5d~%5d cal BP = 기원전 %4d~%4d (길이 %d)' % (n, a, b, x, y, a - b))
Y = [('Initial', 8000, 6200), ('Early', 6200, 4500), ('Middle', 4500, 3000), ('Late', 3000, 1500)]     # 기원전
print('121 Chulmun 4단계(기원전):', ', '.join('%s %d~%d' % t for t in Y))
print('\n겹침표(행: 6106 단계, 열: 121 단계, 단위 년). 각 행의 합은 6106 단계 길이와 같다')
print('%-10s' % '' + ''.join('%9s' % t[0] for t in Y) + '   밖')
for n, x, y in Kbc:
    row = [overlap(-x, -y, -ya, -yb) for _, ya, yb in Y]       # 음수 연도로 바꾸어 비교
    tot = (x - y)
    print('%-10s' % n + ''.join('%9d' % v for v in row) + '%6d' % (tot - sum(row)))
print('→ 6106의 Early(6,500~5,500 cal BP)는 기원전 %d~%d이며 121의 Middle(4500~3000 BC)에 %d년, 121의 Early에 %d년 걸친다' % (
    Kbc[2][1], Kbc[2][2], overlap(-Kbc[2][1], -Kbc[2][2], -4500, -3000), overlap(-Kbc[2][1], -Kbc[2][2], -6200, -4500)))
print('→ 6106의 Initial(8,000~6,500 cal BP)은 기원전 %d~%d로 121의 Early(6200~4500 BC)와 %d년 겹친다' % (
    Kbc[1][1], Kbc[1][2], overlap(-Kbc[1][1], -Kbc[1][2], -6200, -4500)))
print('이름이 같은 단계끼리의 어긋남 (6106의 이름 vs 121의 같은 이름, 시작 연도 차이, 년):')
for n, x, y in Kbc:
    for m, ya, yb in Y:
        if n == m:
            print('  %-8s 6106 기원전 %d~%d  /  121 기원전 %d~%d  (시작 차 %d, 끝 차 %d)' % (n, x, y, ya, yb, abs(x - ya), abs(y - yb)))
# 끝(무문토기 시작) 비교
print('Chulmun의 끝: 6106 3,500 cal BP = %s, 121 기원전 1500 → 차이 %d년' % (bc(3500), abs(-yr(3500) - 1500)))
print('Chulmun의 시작: 6106 10,000 cal BP = %s, 121 기원전 8000 → 차이 %d년' % (bc(10000), abs(-yr(10000) - 8000)))

hdr('계산 12-1b 무문토기(Mumun) 시기 구분의 대응')
MU121 = [('Early', 1500, 800), ('Middle', 800, 400), ('Late', 400, 100)]
MU13 = [('Early', 1300, 800), ('Middle', 800, 500)]                       # 기원전(BCE)
print('121:', MU121, ' 13: ', MU13)
print('Early 시작: 121 1500 vs 13 1300 → 차이 %d년; Middle 끝: 121 400 vs 13 500 → 차이 %d년' % (1500 - 1300, 500 - 400))
b0, b1 = 3300, 2800
print('Robbeets 등(2021) "Early Bronze Age 3300~2800 bp" = 기원전 %d~%d (bp 표기, 보정 여부 확인 필요); 121의 Early Mumun(1500~800 BC)과 겹침 %d년(구간 길이 %d년)' % (
    -yr(b0), -yr(b1), overlap(yr(b0), yr(b1), -1500, -800), b0 - b1))
print('Robbeets 등: 일본으로 "after 3000 bp" = 기원전 %d 이후; Nelson 등: 일본으로 기원전 900년' % -yr(3000))
print('Robbeets 등: 3300 bp 한반도로 이주 = 기원전 %d. 121: 기원전 1500년경 쌀이 갑자기 나타남 → 차이 %d년' % (-yr(3300), 1500 - (-yr(3300))))

# ================================================================== 계산 12-2: 6106 자료 걸러내기
hdr('계산 12-2 Kim 등(2021) 자료 흐름과 합계 (6106 본문과 4623 방법)')
d0, s0, d1, s1 = 894, 163, 683, 136
dc, sc, di, si = 363, 51, 319, 85
print('초기 %d개/%d유적 → 분석 %d개/%d유적. 제외 %d개(%.1f%%), %d유적(%.1f%%)' % (d0, s0, d1, s1, d0 - d1, pct(d0 - d1, d0), s0 - s1, pct(s0 - s1, s0)))
print('해안 %d + 내륙 %d = %d (본문 683). 유적 %d + %d = %d (본문 136)' % (dc, di, dc + di, sc, si, sc + si))
print('→ 날짜 합은 682이며 본문 683과 1 어긋난다(밀레 검정은 n_total = 682를 쓴다)')
print('밀레 45/682 = %.3f%%,  45/683 = %.3f%% (논문 6.59%%)' % (pct(45, 682), pct(45, 683)))
print('유적당 날짜: 해안 %.2f, 내륙 %.2f, 전체 %.2f' % (dc / sc, di / si, d1 / s1))
tc, ti = 197, 179
print('성기게 한 자료: 해안 %d(%.1f%%) + 내륙 %d(%.1f%%) = %d, 분석 자료 683 대비 %.1f%%' % (tc, pct(tc, dc), ti, pct(ti, di), tc + ti, pct(tc + ti, d1)))
print('날짜 14C 연령 범위 6200~2800(14C 연령). 분석 창 7000~3000 cal BP는 보정 연대. 두 눈금이 다르므로 같은 구간이 아니다(보정 곡선 필요, 이 책은 곡선이 없어 환산하지 않음)')
print('분석 창 길이 %d년 = 기원전 %d~%d' % (7000 - 3000, -yr(7000), -yr(3000)))

# ================================================================== 계산 12-3: 성장률의 단위와 비
hdr('계산 12-3 사후 중앙값 성장률의 단위와 비 (6106)')
r_in, d_in, r_co, d_co = 0.0018, -0.0014, 0.0006, -0.0005     # 본문 approx 0.18%, -0.14%, 0.06%, -0.05%
sig = 0.0004
print('사전분포 r ~ Normal(0, %.4f) = 연 %.2f%%. 사후 중앙값 내륙 성장 %.2f%% = 사전 표준편차의 %.2f배, 내륙 감소 %.2f%% = %.2f배, 해안 성장 %.2f%% = %.2f배, 해안 감소 %.2f%% = %.2f배' % (
    sig, 100 * sig, 100 * r_in, r_in / sig, 100 * d_in, d_in / sig, 100 * r_co, r_co / sig, 100 * d_co, d_co / sig))
print('→ 내륙 성장률은 사전 0 주위 4.5 표준편차 밖이다. 자료가 사전을 이긴 것인지, 단위가 %%가 아닌 다른 것인지(예: ‰) 원문 확인 필요')
print('감소율의 비 내륙/해안 = 0.14/0.05 = %.2f (본문 "roughly 2.5배")' % (0.14 / 0.05))
lo, hi = 0.135 / 0.055, 0.145 / 0.045
print('두 값이 소수 둘째 자리 반올림이라면 비는 %.2f ~ %.2f. 2.5는 이 범위의 아래쪽 끝(0.135/0.055 = %.2f)에서만 나온다' % (lo, hi, lo))
print('성장률의 비 내륙/해안 = 0.18/0.06 = %.2f' % (0.18 / 0.06))
for r, nm in ((r_in, '내륙 성장'), (d_in, '내륙 감소'), (r_co, '해안 성장'), (d_co, '해안 감소')):
    print('  %s 연 %.2f%%가 2000년 이어지면 (1+r)^2000 = %.4g배, 1000년이면 %.4g배' % (nm, 100 * r, (1 + r) ** 2000, (1 + r) ** 1000))
print('→ 이 값은 모형의 밀도 비이며 인구의 배수가 아니다(이 책의 설명). 날짜 수 밀도에 대한 것')

# ================================================================== 계산 12-4: 이중 지수 성장 모형 시연
hdr('계산 12-4 truncated double-exponential 모형의 밀도: 시연값(변화점 c는 시연값)')
A, B = 7000, 3000
def model_p(r1, r2, c, a=A, b=B):
    """i = a - t (0..a-b). t > c 이면 r1, t <= c 이면 r2. 경계에서 이어지도록 가중치를 곱한다(이 책의 해석)."""
    i = np.arange(0, a - b + 1)
    d = a - c
    w = np.where(i <= d, (1 + r1) ** i, (1 + r1) ** d * (1 + r2) ** (i - d))
    return w / w.sum()
for nm, r1, r2, c in (('내륙(c=5000 시연값)', r_in, d_in, 5000), ('해안(c=5200 시연값, 내륙보다 200년 이름)', r_co, d_co, 5200), ('내륙(c=5000), 대조: 해안의 비율 r', r_co, d_co, 5000)):
    p = model_p(r1, r2, c)
    t = A - np.arange(0, A - B + 1)
    pk = np.argmax(p)
    print('%s: 합 %.6f, 최대 밀도 t = %d cal BP, p(7000) = %.3e, p(최대) = %.3e, p(3000) = %.3e' % (nm, p.sum(), t[pk], p[0], p[pk], p[-1]))
    print('    최대/7000 = %.2f배, 3000/최대 = %.3f, 변화점보다 오래된 쪽(t > c)에 놓인 확률 질량 = %.3f' % (p[pk] / p[0], p[-1] / p[pk], p[t > c].sum()))
print('→ 같은 변화점에서도 내륙은 오름과 내림이 가팔라 최대 밀도가 훨씬 높다. 해안은 평평하다. 모형의 변화점 c가 어디인지는 논문 그림 2에 있고 본문에 수치가 없다. 원문 확인 필요')
print('논문 식의 연속성: 논문 본문 식은 r이 c 앞뒤로 바뀐다고만 쓰고 경계의 연속 조건을 쓰지 않았다. 위 시연은 연속이 되도록 곱했다(이 책의 해석).')

# ================================================================== 계산 12-5: 변화점과 냉각 사건의 순서 시연
hdr('계산 12-5 변화점이 냉각보다 200~800년 앞섰다는 서술의 환산 (냉각 시점 X는 시연값)')
print('논문 본문: 꽃가루(AP/TP) 냉각 사건이 변화점 뒤에 일어난 확률이 0.95 위, 중앙값 차이 200~800년. 냉각 구간은 5,500~4,500 cal BP(서론). 사건의 시작 연대 d1, f1, g1은 보충 자료에 있고 이 책이 읽지 못함')
print('%8s %12s %12s' % ('X(cal BP)', 'c = X + 200', 'c = X + 800'))
for X in (5500, 5000, 4500):
    print('%8d %8d(%s) %8d(%s)' % (X, X + 200, bc(X + 200), X + 800, bc(X + 800)))
print('121의 서술과 나란히(기원전→cal BP: cal BP = 1950 + 기원전):')
for nm, bcy in (('Paju Daeneung-ri 3700~3600 BC', (3700, 3600)), ('Gimpo Sinan-ri 3700~3500 BC', (3700, 3500)), ('가장 큰 마을은 3500~3400 BC 이전', (3500, 3400))):
    print('  %-34s = %d~%d cal BP' % (nm, 1950 + bcy[0], 1950 + bcy[1]))
print('  121: 마을 규모와 수의 감소는 4.2 ka 사건(%s)보다 "적어도 천 년" 앞선다 → 감소의 시작은 %d cal BP(%s)보다 오래됨' % (bc(4200), 4200 + 1000, bc(5200)))
print('→ 6106의 변화점 서술(냉각보다 앞섬)과 121의 서술(마을 감소가 4.2 ka보다 천 년 이상 앞섬)은 같은 방향이다. 다만 X와 c의 실제 수치가 본문에 없다')

# ================================================================== 계산 12-6: SPD 자료 규모
hdr('계산 12-6 한국 고고학 14C 자료의 규모 (논문별로 자료가 다름)')
rows = [('Kim 등 2021(6106) 분석 자료', 683, '136유적, 동 -해안/내륙'), ('Kim 등 2025(121) 그림 2, 신석기 SPD', 603, '327칸(100년 bin)'),
        ('Kim 등 2025(121) 그림 4, 청동기 집자리 SPD', 3453, '같은 집자리의 여러 날짜는 하나로 처리'), ('Park 등 2019(6장), 5.9~2.2 ka SPD', 2190, '513개 취락 집자리')]
for nm, n, cm in rows: print('%-44s %5d  %s' % (nm, n, cm))
print('121: 한국 방사성탄소 자료는 17,000개 넘음. 신석기 603 + 청동기 3453 = %d = 17000의 %.1f%% 이하' % (603 + 3453, pct(603 + 3453, 17000)))
print('121 그림 2: 603개 날짜 → 327칸, 칸당 %.2f개; 6106: 683 → 136유적, 유적당 %.2f개' % (603 / 327, 683 / 136))
print('6106(683)과 121(603)의 차이 = %d개(%.1f%%): 선택 기준이 다르다는 뜻이며 어느 쪽이 맞는지의 문제가 아니다. 원자료 확인 필요' % (683 - 603, pct(683 - 603, 683)))
print('121: 신석기 유적 약 900곳(2017년까지) 중 체계적 식물 시료 20곳 미만 → %.1f%% 미만' % pct(20, 900))
print('121: 800곳 넘는 신석기 유적, 3200곳 넘는 청동기 유적. 청동기/신석기 유적 수 비 ≥ %.1f' % (3200 / 800))

# ================================================================== 계산 12-7: DBSCAN과 binPrep 시연
hdr('계산 12-7 공간 군집(DBSCAN, eps=1 km, minPts=1)과 시간 칸 묶기(h=100년) 시연: 시연값')
rng = np.random.default_rng(12)
# 시연 유적 8곳(좌표 km) 과 날짜(중앙값 cal BP). 실제 유적이 아니다.
SITES = {'가': (0.0, 0.0), '나': (0.6, 0.4), '다': (0.9, 0.0), '라': (5.0, 5.0), '마': (5.5, 5.2), '바': (12.0, 1.0), '사': (12.0, 2.5), '아': (20.0, 20.0)}
DATES = [('가', 5600), ('가', 5580), ('가', 5540), ('나', 5520), ('다', 5100), ('다', 5060), ('라', 5000), ('라', 4980), ('마', 4950), ('마', 4700), ('바', 4400), ('바', 4390), ('사', 4350), ('아', 3900)]
names = list(SITES)
pts = np.array([SITES[n] for n in names])
D = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
lab = {n: n for n in names}
# minPts=1 의 DBSCAN은 거리 eps 이하로 이어진 점들의 연결 성분과 같다
par = list(range(len(names)))
def find(x):
    while par[x] != x:
        par[x] = par[par[x]]; x = par[x]
    return x
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        if D[i, j] <= 1.0:
            par[find(i)] = find(j)
cl = {}
for i, n in enumerate(names): cl.setdefault(find(i), []).append(n)
print('군집:', list(cl.values()), '(유적 8곳 → 군집 %d개)' % len(cl))
site2cl = {n: k for k, v in cl.items() for n in v}
# 시간 칸: 같은 군집 안에서 날짜를 정렬해 완전연결 거리 100년 이내로 묶는 단순화 규칙(rcarbon binPrep의 실제 구현과 같다고 확인하지 못함)
from scipy.cluster.hierarchy import linkage, fcluster
bins = []
for k, v in cl.items():
    dd = [d for s, d in DATES if site2cl[s] == k]
    if len(dd) == 1:
        bins.append((k, [dd[0]])); continue
    Z = linkage(np.array(dd, dtype=float)[:, None], 'complete')
    f = fcluster(Z, 100, 'distance')
    for g in set(f):
        bins.append((k, [d for d, ff in zip(dd, f) if ff == g]))
print('날짜 %d개 → 칸 %d개' % (len(DATES), len(bins)))
for k, b in bins: print('  군집', cl[k], '칸 날짜', b)
grid = np.arange(6000, 3500, -10)
def spd(dates_groups, sd=40):
    tot = np.zeros(len(grid))
    for g in dates_groups:
        s = np.zeros(len(grid))
        for d in g: s += stats.norm.pdf(grid, d, sd)
        tot += s / s.sum() * 1.0            # 칸 하나의 합이 1이 되도록 정규화
    return tot
raw = spd([[d] for _, d in DATES])
bnd = spd([b for _, b in bins])
print('SPD의 최대/평균: 칸 묶기 전 %.2f, 후 %.2f (시연: 날짜가 몰린 유적의 영향이 줄어든다)' % (raw.max() / raw.mean(), bnd.max() / bnd.mean()))
print('가장 높은 곳: 전 %d cal BP, 후 %d cal BP. 정규분포 sd=40은 시연값이며 보정 곡선이 아니다.' % (grid[raw.argmax()], grid[bnd.argmax()]))

# ================================================================== 계산 12-8: 표지 순열 검정 시연
hdr('계산 12-8 표지 순열 검정(mark-permutation test)의 절차 시연: 날짜 682개, 표지 45개, 1000회. 날짜 분포는 시연값')
rs = np.random.default_rng(2021)
N, M = 682, 45
# 시연: 전체 날짜는 7000~3000에서 5000 근처 봉우리를 가진 분포에서 뽑음. 밀레 표지는 무작위로 붙음(귀무 가정이 참인 경우)
allt = np.clip(rs.normal(5200, 800, N), 3000, 7000)
edges = np.arange(7000, 2999, -200)
def prop_by_bin(t, mark):
    out = []
    for x0, x1 in zip(edges[:-1], edges[1:]):
        m = (t <= x0) & (t > x1)
        out.append(mark[m].sum() / max(m.sum(), 1))
    return np.array(out)
def stat(t, mark):
    # 전체 구간에서 표지 비율 대비 칸별 편차 제곱합(이 책의 단순 통계; 논문은 SPD 편차를 쓴다)
    p = prop_by_bin(t, mark)
    base = mark.mean()
    return float(((p - base) ** 2).sum())
mk = np.zeros(N, bool); mk[rs.choice(N, M, replace=False)] = True
obs = stat(allt, mk)
perm = np.array([stat(allt, rs.permutation(mk)) for _ in range(1000)])
p_one = (1 + (perm >= obs).sum()) / (1 + len(perm))
print('관측 통계 %.4f, 순열 중앙 %.4f, 95%% %.4f, p = %.3f (표지가 무작위로 붙은 시연이므로 큰 p가 정상)' % (obs, np.median(perm), np.percentile(perm, 95), p_one))
mk2 = np.zeros(N, bool); late = np.where(allt < 4500)[0]
mk2[rs.choice(N, M - 10, replace=False)] = True
mk2[:] = mk2; mk2[late[:10]] = True
obs2 = stat(allt, mk2)
perm2 = np.array([stat(allt, rs.permutation(mk2)) for _ in range(1000)])
print('표지 10개를 일부러 4500 이후에 몰면: 관측 %.4f, p = %.3f (이 시연의 통계와 자료로는 몰림을 잡아내지 못함. 칸마다 날짜가 적어 검정력이 낮다는 뜻이며, 6106이 p=0.63을 두고 한 말과 같은 방향)' % (obs2, (1 + (perm2 >= obs2).sum()) / 1001))
print('논문: 전체 682개 중 밀레 45개(6.59%%), 전역 p = 0.63. 시료가 작아 검정력이 낮다고 논문도 썼다. 45/682 = %.3f%%' % pct(45, 682))
# 검정력 감각: 45개 표지가 있을 때 칸 하나에서 비율이 얼마나 흔들리는가
for n_bin in (50, 100, 200):
    e = 0.0659
    sd = sqrt(e * (1 - e) / n_bin)
    print('  칸의 날짜 %d개이면 비율의 표준오차 %.3f (6.59%% ± %.1f%%포인트)' % (n_bin, sd, 100 * sd))

# ================================================================== 계산 12-9: MCMC와 R-hat 시연
hdr('계산 12-9 베이즈 추정(Metropolis MCMC)과 Gelman-Rubin 진단 시연: 모의 날짜 179개, 사전분포는 6106과 같음')
rg = np.random.default_rng(7)
TRUE = (0.0018, -0.0014, 5000)          # 시연값(내륙 중앙값과 가정 변화점)
p_true = model_p(*TRUE)
t_vals = A - np.arange(0, A - B + 1)
sim = rg.choice(t_vals, size=179, p=p_true)
idx = (A - sim).astype(int)             # i 값
def loglik(r1, r2, c, idx=idx):
    if not (B < c < A): return -np.inf
    p = model_p(r1, r2, c)
    return float(np.log(p[idx]).sum())
def logprior(r1, r2, c):
    lp = stats.norm.logpdf(r1, 0, 0.0004) + stats.norm.logpdf(r2, 0, 0.0004)
    lp += stats.truncnorm.logpdf(c, (B - 5000) / 1000, (A - 5000) / 1000, loc=5000, scale=1000)
    return lp
def run_chain(seed, n=6000, init=None):
    r = np.random.default_rng(seed)
    cur = np.array(init, float)
    lc = loglik(*cur) + logprior(*cur)
    out = []
    step = np.array([0.00025, 0.00025, 150.0])
    acc = 0
    for it in range(n):
        prop = cur + r.normal(0, 1, 3) * step
        lp = loglik(*prop) + logprior(*prop)
        if np.log(r.random()) < lp - lc:
            cur, lc = prop, lp; acc += 1
        out.append(cur.copy())
    return np.array(out), acc / n
chains, accs = [], []
for sd_, init in ((1, (0.0, 0.0, 4000.0)), (2, (0.001, -0.001, 5500.0)), (3, (-0.001, 0.001, 6200.0))):
    ch, ac = run_chain(sd_, init=init)
    chains.append(ch[1000:][::6]); accs.append(ac)         # 번인 1000, 솎기 6
C = np.array(chains)                                       # (체인, 표본, 모수)
n = C.shape[1]
def rhat(x):                                               # x: (체인, 표본)
    m_, n_ = x.shape
    W = x.var(axis=1, ddof=1).mean()
    Bm = n_ * x.mean(axis=1).var(ddof=1)
    var = (n_ - 1) / n_ * W + Bm / n_
    return sqrt(var / W)
names3 = ['r1', 'r2', 'c']
print('체인 3개, 각 6000회(번인 1000, 솎기 6 → 체인당 %d개). 수용률 %s' % (n, ', '.join('%.2f' % a for a in accs)))
for k, nm in enumerate(names3):
    allv = C[:, :, k].ravel()
    srt = np.sort(allv)
    w = int(0.9 * len(srt))
    j = np.argmin(srt[w:] - srt[:len(srt) - w])             # 가장 짧은 90% 구간(HPD)
    print('  %-3s 사후 중앙값 %.5f, 90%% HPD [%.5f, %.5f], R-hat %.3f (참값 %s)' % (nm, np.median(allv), srt[j], srt[j + w], rhat(C[:, :, k]), TRUE[k]))
print('→ R-hat이 1에 가까우면 체인들이 같은 분포를 그린다는 신호다. 6106은 100,000번 3체인, 번인 10,000, 솎기 6을 썼고 R-hat의 값은 보충 표 S5에 있어 이 책이 읽지 못함')
print('6106 설정으로 환산: (100000 - 10000)/6 = %d개/체인' % ((100000 - 10000) // 6))
# 날짜 수가 줄면 HPD가 넓어짐 (해안 자료가 불확실했다는 서술의 감각)
sim50 = rg.choice(t_vals, size=50, p=p_true); idx50 = (A - sim50).astype(int)
def post_c_grid(idx_):
    cs = np.arange(3500, 6600, 50)
    ll = []
    for c in cs:
        best = -1e18
        for r1 in (0.0010, 0.0014, 0.0018, 0.0022):
            for r2 in (-0.0020, -0.0014, -0.0008):
                best = max(best, loglik(r1, r2, c, idx_) + logprior(r1, r2, c))
        ll.append(best)
    ll = np.array(ll); pp = np.exp(ll - ll.max()); pp /= pp.sum()
    cdf = np.cumsum(pp)
    return cs, pp, cs[np.searchsorted(cdf, 0.05)], cs[np.searchsorted(cdf, 0.95)]
for lab_, ix in (('179개', idx), ('50개', idx50)):
    cs, pp, lo, hi = post_c_grid(ix)
    print('  변화점의 근사 사후(r은 격자 최대값, 간이): 날짜 %s → 90%% 구간 [%d, %d] cal BP (폭 %d년)' % (lab_, lo, hi, hi - lo))

# ================================================================== 계산 12-10: 마을 규모 산술(121)
hdr('계산 12-10 Kim 등(2025) 마을 규모 산술')
print('가옥 수: Incheon Unseo-dong 66, Paju Daeneung-ri 39(3700~3600 BC), Gimpo Sinan-ri 35(3700~3500 BC)')
print('Daeneung-ri 날짜 구간 100년, 가옥 39채 → 가옥당 %.1f년의 간격이 아니라 \'동시에 살았다\'는 뜻이 아니다(논문도 동시 점유 여부를 논쟁이라 씀)' % (100 / 39))
print('Cheonan Baekseok-dong: 192채(본문 192, 다른 곳 \'약 200\', \'80~200\'); 대부분 기원전 1000~900. 100년에 대부분이면 최소 %d채가 이 구간의 날짜(동시 거주 아님)' % (192 // 2 + 1))
print('Baekseok-dong 소멸: 기원전 750년까지. 최대 규모(1000~900 BC)에서 750 BC까지 %d~%d년' % (1000 - 750, 900 - 750))
print('Chuncheon Jungdo: 1273채가 기원전 1200~400(%d년). 단일 단계에 600채 넘음. 600/1273 = %.1f%%' % (1200 - 400, pct(600, 1273)))
print('  Jungdo 급증 구간 850~750 BC: 100년. 이 구간의 앞 50년(850~800)은 Hallstatt 고원(800~400) 앞이고 뒤 50년(800~750)은 고원 안에 있다(계산 12-11)')
print('Ulsan: 468채/5유적 = 평균 %.1f채(유적별 값은 본문에 없음)' % (468 / 5))
print('Buyeo Songguk-ri: 110채 넘게 발굴, 더 클 것으로 추정')
print('Mumun 초기 집: 20~100 m², 최대 250 m²; 송국리형 평균 약 20 m². 250/20 = %.1f배, 20~100의 가운데 60/20 = %.1f배' % (250 / 20, 60 / 20))
print('논바닥: 40~90 m² (Nonsan Majeon-ri). 송국리형 집 20 m²의 %.1f~%.1f배' % (40 / 20, 90 / 20))
print('고인돌: 5만 기 넘음, 덮개돌 5~25 t. 10 t에 50명 넘게 필요(Lee 2003 인용). 선형 가정(시연, 논문에 없음)으로 5 t = %d명, 25 t = %d명' % (50 * 5 / 10, 50 * 25 / 10))
print('고인돌 5만 기 / 청동기 유적 3200곳 이상 = 유적당 평균 ≤ %.1f기(고인돌은 무덤이고 마을 유적과 단위가 다르다. 단순 나눗셈은 의미가 크지 않음)' % (50000 / 3200))
print('Gadeok-do Janghang: 매장 최소 48명, 야외 화덕 약 90개 → 화덕/사람 %.2f' % (90 / 48))
print('고산리: 토기 직접 연대 기원전 7800~7500, 집·구덩이 연대 기원전 약 6200 → 공백 %d~%d년' % (7500 - 6200, 7800 - 6200))
print('고산리 시작: 6106 10,000 cal BP(%s) vs 121 기원전 7800 → 차이 %d년' % (bc(10000), -yr(10000) - 7800))
print('서해안 조개더미: 굴 90~99%%; 100곳 넘는 동시기 유적에 장기 점유 증거 없음; 남해안 조개더미 250곳 넘음')

# ================================================================== 계산 12-11: Hallstatt 고원
hdr('계산 12-11 보정 곡선의 고원(Hallstatt plateau)과 시기 구분의 해상도')
h0, h1 = 800, 400
print('121: 기원전 %d~%d 고원 = %d~%d cal BP, 길이 %d년' % (h0, h1, 1950 + h1, 1950 + h0, h0 - h1))
print('Middle Mumun(121) 기원전 800~400과 같은 구간: 겹침 %d년, 단계 길이 %d년 → 단계 전체가 고원 안에 놓임' % (overlap(-800, -400, -h0, -h1), 400))
print('Jungdo 급증 850~750 BC 중 고원 안: %d년 (%.0f%%)' % (overlap(-850, -750, -h0, -h1), pct(overlap(-850, -750, -h0, -h1), 100)))
print('Baekseok-dong 1000~900 BC, 감소 \'900 BC 이후\' → 고원 시작(800 BC) 앞 %d년' % (900 - 800))
print('→ 고원 안의 날짜 사이 간격(수십 년~백 년 단위)은 날짜의 불확도가 더 클 수 있다. 얼마나 큰지는 보정 곡선과 날짜의 14C 오차가 있어야 하며 이 책은 읽지 못함')
print('이 시연: 14C 오차 ±30년의 날짜 둘이 같은 14C 연령이면 달력 연대의 겹침은 고원 길이 %d년까지 퍼질 수 있다(개념 설명, 곡선 값이 아님)' % (h0 - h1))

# ================================================================== 계산 12-12: 콩 크기(120)
hdr('계산 12-12 Lee 등(2011) 콩의 크기 숫자와 연대의 산술')
L_W = [('Jiahu 258개 평균 (신석기 초, 9000~8600 cal BP 첫 단계)', 3.1, 2.2), ('Yuezhuang 2개 평균', 2.6, 1.8), ('Jiaochangpu 평균(용산)', 3.4, 2.6),
       ('Yamanokami 토기 눌린 자국(초창기 조몬)', 5.62, 3.86), ('Usujiri Shogakko 후기 조몬 1알(L, W, T=3.1)', 4.5, 2.3)]
print('길이 L, 폭 W (mm). 길이×폭(mm²)과 길이/폭')
for nm, l, w in L_W:
    print('  %-52s L=%.2f W=%.2f  L×W=%.2f  L/W=%.2f' % (nm, l, w, l * w, l / w))
print('  Usujiri는 두께 3.1이 폭 2.3보다 큼. 논문은 "씨눈이 보이는 면의 최대 치수를 폭이 아닌 두께로 적는" 관례를 따랐다고 쓴다 → 이 값의 W는 관례상의 폭')
print('Kyushu 후기 조몬 토기 눌린 자국 10.2~11.8 × 6.5~7.9: L×W = %.1f ~ %.1f mm², L/W = %.2f ~ %.2f' % (10.2 * 6.5, 11.8 * 7.9, 10.2 / 7.9, 11.8 / 6.5))
print('무문토기 콩 길이 3.8~9.9 mm: 길이 비(최대/최소) = %.2f; L/W 1.0~2.1' % (9.9 / 3.8))
print('Jiahu 평균 길이 3.1 대비 Mumun 최대 9.9 = %.2f배, 구 모양 가정(시연)이면 부피 %.0f배' % (9.9 / 3.1, (9.9 / 3.1) ** 3))
print('회귀식 y = 0.2 + 1.4x (논문은 길이와 폭의 선형 상관이라고만 씀; x, y의 배정이 본문에 없음)')
for nm, l, w in L_W[:3]:
    print('   x=폭, y=길이: 폭 %.1f → 길이 %.2f (관측 %.2f, 차이 %+.2f);  x=길이, y=폭: 길이 %.1f → 폭 %.2f (관측 %.2f, 차이 %+.2f)' % (w, 0.2 + 1.4 * w, l, 0.2 + 1.4 * w - l, l, 0.2 + 1.4 * l, w, 0.2 + 1.4 * l - w))
print('   → x=폭, y=길이가 훨씬 잘 맞는다. 이 책의 추정이며 원문 확인 필요')
print('탄화 수축 15%%(논문이 인용한 한 추정): 탄 길이 3.1 mm의 생체 길이 = 3.1/0.85 = %.2f mm, 9.9 mm → %.2f mm. 논문은 조건을 모르면 환산이 어렵다고 썼다. 시연' % (3.1 / 0.85, 9.9 / 0.85))
print('현대 표본: 재배 30 + 야생 60 = %d개(한국 농업 유전자원). 논문 전체 현대 표본 180개 → 나머지 %d개의 출처(Huizui 야생 등)와 개수는 본문에 없음' % (30 + 60, 180 - 90))
print('Daundong: 구덩이 바닥 흙에서 퇴적물 1리터당 콩 307개 → 100 L면 %d개(비례 가정, 시연)' % (307 * 100))
print('분석 자료: 949개 / 22유적 = 유적당 평균 %.1f개(유적별 개수는 논문 표 S1에 있고 이 책은 읽지 못함)' % (949 / 22))
print('\n연대 옮기기 (cal BP → 기원전/후):')
for nm, a, b in (('Pyeonggeodong 콩 AMS(본문)', 4840, 4650), ('Pyeonggeodong 팥·콩 구덩이(보충 그림 S3 설명)', 4830, 4650),
                 ('Jiahu 가장 이른 단계', 9000, 8600), ('Late Longshan 콩(이 책은 본문에 연대 없음)', None, None),
                 ('Sannai Maruyama 초기 조몬', 5800, 5300), ('중기 조몬 Shimoyakebe(약 5000 cal BP)', 5000, 5000), ('후기 조몬 Usujiri(약 3500 cal BP)', 3500, 3500),
                 ('한(漢)(본문)', 2170, 1730), ('초기 무문(논문 초록 3000 cal BP)', 3000, 3000)):
    if a is None:
        continue
    print('  %-48s %5d~%5d cal BP = %s ~ %s' % (nm, a, b, bc(a), bc(b)))
print('  Daundong·Okbang 1/9 AMS "2720~2380 BP"(본문 서론, 보정 여부 불명) = 기원전 %d~%d (1950-BP 단순 환산, 보정 전이면 달력 연대와 다름)' % (-yr(2720), -yr(2380)))
print('  → 121의 시기 구분과 대조: Pyeonggeodong 콩 %s~%s는 121의 Late Chulmun(3000~1500 BC)의 앞쪽, 6106의 Late Chulmun(5000~4000 cal BP)의 앞쪽에 든다' % (bc(4840), bc(4650)))
print('  → Daundong 기원전 770~430은 121의 Middle Mumun(800~400 BC) 안. 그러나 논문 초록은 \'3000 cal BP(Early Mumun)\'에 큰 콩이 있다고 씀(차이 %d~%d년). 근거 시료 확인 필요' % (3000 - 2720, 3000 - 2380))
print('  120 본문: 청동기 시작 \'약 3500 BP\' = %s; 121: 기원전 1500 → 차이 %d년' % (bc(3500), abs(-yr(3500) - 1500)))
print('  120: 한국 조 기장 5500 cal BP = %s; 121: 기원전 약 3500; 1: 5500 bp = %s' % (bc(5500), bc(5500)))

# ================================================================== 계산 12-13: 방직 표 1(13)
hdr('계산 12-13 Nelson 등(2020) 표 1의 한국 10행 점검 (1 있음, 0 없음, ? 불확실, N 자료 없음)')
# 열: 기장 재배, 농기구, 삼 재배, (쌍)원뿔 가락바퀴, 납작 가락바퀴, 뼈바늘·송곳
T = {   # 본문에서 확인한 한국 10행만 넣는다. 중국·연해주·일본 행은 표가 쪽마다 흩어져 이 책이 전부 확인하지 못해 넣지 않는다
 'Osan-li': ('한국', [0, 1, 0, 1, 0, 'N']), 'Pibong-li': ('한국', [1, 1, 0, 1, 1, 'N']), 'Amsadong': ('한국', [1, 1, 0, 1, 1, 'N']),
 'Sopohang': ('한국', [0, 1, 0, 1, 0, 0]), 'Nongpodong': ('한국', [0, 1, 0, 1, 0, 'N']), 'Sinam-li': ('한국', [0, 1, 0, 1, 1, 0]),
 'Upper Kungsan-li': ('한국', ['?', 1, 0, 1, 1, 1]), 'Tongsamdong': ('한국', [1, 1, 0, 1, 1, 1]), 'Jungsandong': ('한국', [1, 1, 0, 1, 1, 'N']),
 'Pangokdong': ('한국', [1, 1, 0, 1, 0, 'N']),
}
cols = ['기장', '농기구', '삼', '원뿔', '납작', '뼈바늘']
print('입력한 유적 수 =', len(T), '(논문 표는 34행: 중국 12, 연해주 4, 한국 10, 일본 8. 한국 10행만 계산)')
def cnt(rows, k):
    v = [r[1][k] for r in rows]
    return {s: v.count(s) for s in (1, '?', 0, 'N')}
for reg in ('한국',):
    rows = [r for r in T.values() if reg is None or r[0] == reg]
    print('%-4s n=%2d ' % (reg or '전체', len(rows)) + ' | '.join('%s %s' % (c, cnt(rows, k)) for k, c in enumerate(cols[:5])))
# 가락바퀴(원뿔 또는 납작)가 있는 유적 수와 그 중 기장 있음
whorl = [r for r in T.values() if r[1][3] == 1 or r[1][4] == 1 or r[1][4] == '?']
print('한국 10행 중 가락바퀴 있는 유적 = %d' % len(whorl))
mil_yes = sum(1 for r in whorl if r[1][0] == 1); mil_q = sum(1 for r in whorl if r[1][0] == '?'); mil_no = sum(1 for r in whorl if r[1][0] == 0); mil_n = sum(1 for r in whorl if r[1][0] == 'N')
tool_yes = sum(1 for r in whorl if r[1][1] == 1); tool_n = sum(1 for r in whorl if r[1][1] == 'N'); tool_no = sum(1 for r in whorl if r[1][1] == 0)
print('  기장 직접 증거 1: %d, ?: %d, 0: %d, 자료 없음: %d' % (mil_yes, mil_q, mil_no, mil_n))
print('  농기구 1: %d, 0: %d, 자료 없음: %d → 농기구 열이 1인 유적 %.1f%%' % (tool_yes, tool_no, tool_n, pct(tool_yes, len(whorl))))
print('  기장 또는 농기구가 1: %d / %d' % (sum(1 for r in whorl if r[1][0] == 1 or r[1][1] == 1), len(whorl)))
kr = [(k, v[1]) for k, v in T.items() if v[0] == '한국']
print('한국 10유적: 기장 1 = %s' % [k for k, v in kr if v[0] == 1])
print('            기장 0인데 가락바퀴 있음(논문 예측 3의 반례 후보) = %s' % [k for k, v in kr if v[0] == 0])
print('            그 4곳은 모두 농기구 열이 1이다 → 논문은 농기구로 예측을 구제함. 농기구는 수확칼 등으로 야생 식물 채집에도 쓸 수 있다고 논문도 인정')
print('예측 3의 검정력: 표에 있는 유적은 가락바퀴가 있는 유적으로 골랐으므로, \'가락바퀴 없고 농업 있음\' 칸이 표에 없다. 2×2 표를 만들 수 없어 Fisher 검정을 하지 못한다')
print('연대의 어긋남 (13 본문 vs 표):')
print('  Pibong-li 본문 4670 ± 60 BCE(구간 %d~%d), 표 5010~3050 BCE; 표 구간 길이 %d년' % (4670 - 60 * 2, 4670 + 60 * 2, 5010 - 3050))
print('  Xinglongwa 본문 6200~5400 BC(800년), 표 6400~5200 BCE(1200년)')
print('  Haminmangha 본문 3500~3000 BCE vs 표 4000~3000(그림 2·표 1); Zuojiashan 표 \'2600~3000 BCE\'는 앞뒤가 뒤바뀐 표기 (그림 2는 3000~2600)')
print('  Pibong-li 4670 BCE와 Xinglongwa 시작 차이 %d~%d년, Zhaobaogou(5400~4500) 가운데와의 차이 %d년' % (6200 - 4670, 6400 - 4670, 4950 - 4670))
print('  13: \'한국 가락바퀴 약 4600 BCE는 서요하보다 약 천 년 늦다\' → 6200-4600 = %d, 5400-4600 = %d' % (6200 - 4600, 5400 - 4600))

# ================================================================== 계산 12-14: 언어 연대 눈금 옮기기
hdr('계산 12-14 언어 분기 연대의 비교: Robbeets 등(2021, 논문 1)의 bp와 Nelson 등(2020, 논문 13)의 BCE')
L1 = [('Proto-Transeurasian', 9181, 5595, 12793), ('Proto-Altaic', 6811, 4404, 10166), ('Mongolo-Tungusic', 4491, 2599, 6373), ('Japano-Koreanic', 5458, 3335, 8024)]
L13 = {'Proto-Transeurasian': 4700, 'Proto-Altaic': 3293, 'Proto-Turko-Mongolic': 1552, 'Japano-Koreanic': 1850}
print('논문 1 (bp, 95%% HPD) → 기원전(1950 - bp, bp가 1950 기준이라는 가정; 보정 여부는 언어 연대에 해당하지 않음)')
for nm, m, lo, hi in L1:
    print('  %-20s %5d bp (%5d~%5d) = 기원전 %5d (%5d~%5d), HPD 폭 %d년' % (nm, m, lo, hi, -yr(m), -yr(hi), -yr(lo), hi - lo))
print('논문 13이 Robbeets & Bouckaert(2018)를 인용해 적은 값(BCE):', L13)
for nm, m, lo, hi in L1:
    if nm in L13:
        print('  %-20s 논문 13 기원전 %d vs 논문 1 기원전 %d → 차이 %d년; 13의 값이 논문 1의 95%% HPD(기원전 %d~%d) 안인가: %s' % (
            nm, L13[nm], -yr(m), abs(-yr(m) - L13[nm]), -yr(hi), -yr(lo), (-yr(hi) >= L13[nm] >= -yr(lo))))
print('  논문 13 안: Japano-Koreanic = 1850 BCE(표기)이면서 \'Altaic 단일체에서 약 4700 BCE에 갈라졌다\'(논의): 두 값의 차 %d년' % (4700 - 1850))
print('  논문 13 안: Tungusic 3300 BCE(논의) vs Proto-Altaic 3293 BCE → 차이 %d년' % (3300 - 3293))
print('  논문 13의 요하→한반도 확산: 기원전 3500; 논문 1: 5500 bp = %s → 차이 %d년' % (bc(5500), abs(3550 - 3500)))
print('  Primorye: 13 기원전 3000, 1은 5000 bp = %s' % bc(5000))

# ================================================================== 계산 12-15: 논문 1 표본 합산
hdr('계산 12-15 Robbeets 등(2021)의 표본 합산')
P = [('West Liao', 36), ('Amur', 32), ('Primorye', 4), ('Liaodong', 37), ('East steppe', 1), ('Shandong', 4), ('Yellow R.', 2), ('Korea', 58), ('Japan', 85)]
print('지역별 합 = %s = %d (본문 255)' % ('+'.join(str(n) for _, n in P), sum(n for _, n in P)))
print('차이 = %d' % (sum(n for _, n in P) - 255))
C14 = [('China', 82), ('Primorye', 12), ('Korea', 31), ('Japan', 120), ('Ryukyu', 24)]
print('작물 14C 표본: %s = %d (본문 269) → %s' % ('+'.join(str(n) for _, n in C14), sum(n for _, n in C14), '맞음' if sum(n for _, n in C14) == 269 else '어긋남'))
TR = [('ceramics', 70), ('stone tools', 38), ('buildings', 9), ('plant and animal', 26), ('shell and bone', 17), ('burials', 12)]
print('특성 합 = %s = %d (본문 172)' % ('+'.join(str(n) for _, n in TR), sum(n for _, n in TR)))
print('언어 자료: 3193 cognate sets / 254 개념 / 98 변종 → 개념당 %.1f개, 변종당 %.1f개(개념 수 대비)' % (3193 / 254, 3193 / 98))
print('한국 유적 58 / 255 = %.1f%%, 일본 85 / 255 = %.1f%%' % (pct(58, 255), pct(85, 255)))
print('유전: 새 개체 19(본문), 방법 단락의 개체 33(한국·일본 라이브러리 83개). 19와 33은 서로 다른 단계(분석 통과 개체 대 처리 개체)로 보이나 본문 대응 확인 필요')
print('Yokchido ≈ 95%% 조몬; 한국 신석기 조몬 비율 0~95%%; Taejungni 조몬 혼합 P = 0.228(유의하지 않음)')

# ================================================================== 계산 12-16: 소리리 쌀 (6127)
hdr('계산 12-16 소리리 쌀의 연대와 위치 (6127)')
G = [('불탄 쌀알 18 + 쌀로 추정 41', 59), ]
print('알 수: 18 + 41 = %d (본문 59)' % (18 + 41))
for nm, m, s in (('상층 이탄 쌀알(1998 보고)', 13010, 190), ('상층 이탄 쌀알(1998 보고)', 12520, 150), ('하층 이탄 \'쌀로 추정\' 알', 17310, 310)):
    print('  %-26s %6d ± %3d BP → 1시그마 범위 %d~%d BP' % (nm, m, s, m - s, m + s))
print('2001 추가 조사: 상층 이탄 14,800~12,500 BP(길이 %d년), 하층 17,300~16,300 BP(길이 %d년); 고도 32.13~31.36 m(층 두께 %.2f m)' % (14800 - 12500, 17300 - 16300, 32.13 - 31.36))
print('초록의 요약: 17,000~13,000 L.N.(이 책은 \'년 전\'으로 읽음); 본문 값의 범위는 %d~%d BP → 요약의 구간은 본문의 1시그마 범위를 넘나든다' % (12520 - 150, 17310 + 310))
print('알 수 59개의 분류: 18 / 59 = %.1f%% 쌀(알의 형태로 판단)' % pct(18, 59))
for nm, bpv in (('121: 쌀이 한반도에 갑자기 나타남(기원전 1500)', 3450), ('6127: 한국 최초 논 3400~3000 BP', 3400), ('6127: 건조 밭 기장·쌀 5500~4000 BP', 5500)):
    print('  소리리 상층 13,010 BP는 %s(%d cal BP 상당)보다 %d년 앞, 하층 17,310 BP는 %d년 앞(보정 전 BP와 cal BP를 섞은 개략값)' % (nm, bpv, 13010 - bpv, 17310 - bpv))
print('소리리 위치: 북위 36~37°, 미호천(금강 지류)에서 약 2 km. 위도 1° = %.1f km → 북위 36~37° 띠의 남북 폭 약 %.0f km' % (6371.0088 * math.pi / 180, 6371.0088 * math.pi / 180))
print('보고된 DNA 유사도 39.6%(현생 야생·재배 벼와). 기후: 15,000~7,000 BP에 남부 3~4 °C 높았다는 서술(Smith 인용)')
print('꽃가루: 16,680~13,010 BP 낙엽·혼합림, 습지; 소리리 이탄 쌀알 층은 이 구간과 겹침 %d년' % overlap(12520, 14800, 13010, 16680))

# ================================================================== 계산 12-17: 위상 추정(도시 앵커)과 해안 거리
hdr('계산 12-17 위상 추정의 산술: 도시 앵커 사이 거리, 위도 띠, 해안까지의 거리')
def hav(lo1, la1, lo2, la2):
    R = 6371.0088
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
CITY = {'서울': (126.998, 37.568), '인천': (126.640, 37.478), '춘천': (127.734, 37.875), '울산': (129.315, 35.549), '부산': (129.008, 35.097), '청주': (127.501, 36.644), '제주': (126.522, 33.510)}
print('도시 앵커는 Natural Earth 도시 위치. 유적의 위치가 아니라 \'행정구역의 대표점\'이다.')
for a, b in (('서울', '인천'), ('서울', '춘천'), ('울산', '부산'), ('서울', '청주')):
    print('  %s - %s: %.1f km' % (a, b, hav(*CITY[a], *CITY[b])))
print('소리리 띠: 북위 36~37° → 청주 앵커 북위 %.3f는 띠 안. 서울 앵커 북위 %.3f는 띠 밖(%.2f° = %.0f km 북쪽)' % (CITY['청주'][1], CITY['서울'][1], CITY['서울'][1] - 37, hav(0, 37, 0, CITY['서울'][1])))
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
    import geomap as G_
    from shapely.geometry import Point
    from shapely.ops import unary_union, nearest_points
    land = [g for g, p in G_.layer('ne_10m_land')]
    box = Point(127.5, 36.5).buffer(6.0)
    kor = unary_union([g.intersection(box) for g in land if g.intersects(box)])
    bd = kor.boundary
    def coast_km(lon, lat):
        p = Point(lon, lat)
        q = nearest_points(p, bd)[1]
        return hav(lon, lat, q.x, q.y)
    for nm in ('서울', '춘천', '청주', '인천', '울산'):
        print('  %s 앵커에서 가장 가까운 해안선까지 %.1f km (Natural Earth 10m 육지 경계, 현재 해안)' % (nm, coast_km(*CITY[nm])))
    print('  논문 6106: Amsadong은 \'해안에서 약 50 km 내륙\'(Han River valley). 논문 13은 Amsadong을 Seoul로 적음 → 서울 앵커의 해안 거리와 비교(위 값)')
    print('  논문 121: Paju Daeneung-ri는 서해안에서 약 20 km 내륙. 파주 앵커가 Natural Earth에 없어 이 책은 좌표를 정하지 못함(좌표 확인 필요)')
    print('  6106의 분류: 해안 = 현재 해안선에서 2 km 이내(해안 363개), 내륙 = 2 km 초과(319개). 당시 해안선은 현재와 다를 수 있다(1·2장)')
except Exception as e:
    print('  (shapely/geodata가 없어 해안 거리 계산을 건너뜀)', repr(e)[:80])
print('좌표 불확도의 크기 감각: 위도 0.01° = %.2f km, 경도 0.01°(북위 37°) = %.2f km, 도·분 단위 반올림(±0.5분) = ±%.2f km(위도)' % (
    6371.0088 * math.pi / 180 * 0.01, 6371.0088 * math.pi / 180 * 0.01 * math.cos(math.radians(37)), 6371.0088 * math.pi / 180 * (0.5 / 60)))

# ================================================================== 계산 12-18: 조·기장 시작 주장 모음
hdr('계산 12-18 한반도 조·기장(와 쌀)의 시작에 관한 서술을 기원전 눈금으로 모으기')
C = [('6106 Early Chulmun에 이미 조·기장·팥', 6500, 5500), ('4623 Initial Chulmun에 이미 조·기장·팥', 8000, 6500), ('121 직접 연대: Middle Chulmun에서야 재배(기원전)', None, None),
     ('13 요하→한반도 조 농사 기원전 약 3500(Lee 2011 인용)', None, None), ('1 한반도로 5500 bp까지', 5500, 5500), ('120 조·기장 5500 cal BP', 5500, 5500),
     ('6127 가장 오래된 재배 조·기장·벼 5500~4000 BP', 5500, 4000)]
for nm, a, b in C:
    if a is None:
        if nm.startswith('121'):
            print('  %-58s 기원전 4500~3000' % nm)
        else:
            print('  %-58s 기원전 3500' % nm)
    else:
        print('  %-58s %5d~%5d (cal) BP = %s ~ %s' % (nm, a, b, bc(a), bc(b)))
print('  Pibong-li(13): 직접 조 있음, 유적 연대 기원전 5010~3050; Osan-li(13): 조 없음')
print('  121 Pot: \'약 3500 BC\'에 한국·연해주에 조·기장 도착(Lee 2017, Leipe 등 2019 등 인용). 120·1·13과 같은 쪽에 모임')
print('→ 5500 cal BP = 기원전 3550. 4623과 6106, 121은 시기 이름이 다르지만 6106의 Early(6,500~5,500 cal BP)를 121의 눈금으로 옮기면 Middle Chulmun 앞부분과 겹침(계산 12-1).')
print('→ 4623의 Initial(8,000~6,500 cal BP, 기원전 6050~4550)은 121의 직접 연대 서술(Middle Chulmun)과 어긋남. 6106은 Early로 고침(출판본). 근거 직접 연대 표 확인 필요')
