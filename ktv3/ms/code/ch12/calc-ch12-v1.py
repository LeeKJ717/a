# -*- coding: utf-8 -*-
"""12장 계산 12-1 ~ 12-8. 입력 숫자는 논문에서 옮긴 값이고 줄마다 출처를 붙였다.
실행: python3 calc-ch12-v1.py > calc-ch12-v1.log
시드는 모두 고정. AR(1) 시뮬레이션의 자기상관 값은 논문 값이 아니라 이 책이 바꿔 보는 시연값이다.
"""
import numpy as np
from math import comb
from scipy import stats

def ar1(n, rho, rng, burn=200, size=1):
    e = rng.standard_normal((size, n + burn))
    x = np.zeros_like(e)
    for t in range(1, n + burn):
        x[:, t] = rho * x[:, t - 1] + e[:, t]
    x = x[:, burn:]
    return x / x.std(axis=1, keepdims=True)

print("=== 계산 12-1: Büntgen 등(2016) 알타이, 가장 추운 해의 쏠림 ===")
# 입력: 나이테 600여 계열의 시작·끝이 기원전 359년 ~ 기원후 2011년 사이. 해 수 = 359 + 2011 = 2370 (0년 없음)
N = 359 + 2011
K = 599 - 536 + 1          # '536년 이후 6세기' = 536~599 = 64년
n = 20                      # 가장 추운 여름 20개
obs = 13                    # 알타이에서 그중 13개가 이 창 안(논문 서술)
print("해 수 N =", N, "| 창 길이 K =", K, "| 뽑은 해 n =", n, "| 관측 =", obs)
print("기대값 n*K/N = %.3f" % (n * K / N))
p_hyp = stats.hypergeom.sf(obs - 1, N, K, n)
print("초기하 분포(독립 가정) P(X>=13) = %.3e" % p_hyp)
alp_obs = 5
print("알프스 5개: P(X>=5) = %.3e" % stats.hypergeom.sf(alp_obs - 1, N, K, n))
# 10년 단위(겹치지 않게): 237개 10년, 6~7세기 = 20개 10년, 가장 추운 20개 중 13개
Nd = N // 10
Kd = 20
print("10년 단위 Nd =", Nd, "Kd =", Kd, "기대값 %.3f" % (20 * Kd / Nd), "초기하 P(X>=13) = %.3e" % stats.hypergeom.sf(12, Nd, Kd, 20))
print("알프스 10년 5개: P(X>=5) = %.3e" % stats.hypergeom.sf(4, Nd, Kd, 20))
rng = np.random.default_rng(12)
print("-- 자기상관 AR(1) 가정에서 같은 사건이 우연히 나올 비율 (시연값 rho, 반복 20000번, 시드 12) --")
# 연 인덱스: 0 = 기원전 359, 기원후 536 = 359 + 536 - 1 = 894 (0년 없음)
i0 = 359 + 536 - 1
print("536년의 위치 인덱스", i0, "→ 창 인덱스", i0, "~", i0 + K - 1)
for rho in (0.0, 0.3, 0.5, 0.7):
    reps = 20000
    X = ar1(N, rho, rng, size=reps)
    cold = np.argpartition(X, n, axis=1)[:, :n]       # 가장 낮은 20개(가장 추운 해로 간주)
    cnt = ((cold >= i0) & (cold < i0 + K)).sum(axis=1)
    # 어느 창이든(64년) 가장 많이 담은 값: 사후 선택 반영
    # 슬라이딩: 각 반복에서 임의 64년 창 중 최대 개수
    sel = np.zeros((reps, N), dtype=np.int8)
    rr = np.arange(reps)[:, None]
    sel[rr, cold] = 1
    cs = np.cumsum(sel, axis=1, dtype=np.int32)
    mx = np.empty(reps, dtype=np.int32)
    win = cs[:, K - 1:] - np.concatenate([np.zeros((reps, 1), dtype=np.int32), cs[:, :N - K]], axis=1)
    mx = win.max(axis=1)
    print("rho=%.1f : 고정 창에서 13개 이상 %d/%d (%.5f) | 아무 64년 창에서 최대 13개 이상 %d/%d (%.5f) | 고정 창 평균 %.3f" % (
        rho, int((cnt >= obs).sum()), reps, (cnt >= obs).mean(), int((mx >= obs).sum()), reps, (mx >= obs).mean(), cnt.mean()))
print("주의: 이 시뮬레이션은 값의 크기와 계열 길이가 어디서나 같은 가상 계열이다. 실제 계열의 표본 수 변화와 보정 오차는 반영하지 않는다.")
print("해석 주의: '536년 이후'라는 창은 536년 폭발 연대가 이미 알려진 뒤에 정한 것이다(사전 가설이 아님).")

print("\n=== 계산 12-2: Hantemirov 등(2022) 야말 수치의 내부 점검과 이항 검정 ===")
print("냉각 추세: 0.08 °C/천년 x (5618+1850-1)/1000 천년 = %.3f °C (논문 약 0.6 °C)" % (0.08 * (5618 + 1850 - 1) / 1000))
print("연대 길이: 5618 BCE ~ 2019 CE = %d년(0년 없이 셈), 0년을 넣어 셈하면 %d년 (논문 7,638년)" % (5618 + 2019, 5618 + 2019 + 1))
print("온난화율 0.0173 °C/년 x 169년(1850~2019) = %.3f °C" % (0.0173 * 169))
print("중앙값 증가 12.96-12.43 = %.2f, 95%% 분위 증가 15.43-14.80 = %.2f (논문 0.53, 0.63)" % (12.96 - 12.43, 15.43 - 14.80))
print("1920~2019 평균 13.47 - 1850~2019 평균 12.83 = %.2f" % (13.47 - 12.83))
b1 = stats.binom.sf(26, 100, 0.05)
b2 = stats.binom.sf(18, 40, 0.05)
b3 = stats.binom.cdf(3, 100, 0.10)
print("최근 100년 중 95%% 분위 초과 27년: 독립·무추세 가정 기대 5년, P(X>=27) = %.3e" % b1)
print("1980~2019 40년 중 19년: 기대 2년, P(X>=19) = %.3e" % b2)
print("10%% 분위 미만 3년(100년): 기대 10년, P(X<=3) = %.4f" % b3)
print("재현 주기 4,850년 이상 → 연 확률 1/4850 = %.2e; 7,638년 안에서 한 번 이상 나올 기대 횟수 = %.2f" % (1 / 4850, 7638 / 4850))
print("주의: 연 값은 앞뒤 해와 상관이 있고 추세가 있어 이항 검정은 '독립이면 이렇다'는 기준선일 뿐이다.")

print("\n=== 계산 12-3: Pederson 등(2014) 몽골 우기 15년과 EPS ===")
m_long, sd_long = -0.546, 1.550
m_p, sd_p = 0.600, 0.589
nwin = 15
print("우기 평균 0.600 은 장기 평균 대비 %.3f 표준편차 (장기 SD 1.550). 논문은 'nearly 1 SD'" % ((m_p - m_long) / sd_long))
z_ind = (m_p - m_long) / (sd_long / np.sqrt(nwin))
print("15개 독립 가정 평균의 z = %.3f, 양쪽 p = %.4f" % (z_ind, 2 * stats.norm.sf(z_ind)))
print("21세기 온도 0.74 °C: (0.74+0.311)/0.292 = %.2f 표준편차 (논문 'more than 3.5 SD')" % ((0.74 + 0.311) / 0.292))
print("우기 기간 온도 -0.118 vs 장기 -0.311±0.292: %.2f SD" % ((-0.118 + 0.311) / 0.292))
rng = np.random.default_rng(14)
L = 1112
print("-- AR(1) 시연: 길이 1112년 가상 계열에서 15년 이동평균 (반복 20000번, 시드 14) --")
for rho in (0.0, 0.2, 0.4, 0.6):
    reps = 20000
    X = ar1(L, rho, rng, size=reps) * sd_long + m_long
    cs = np.cumsum(X, axis=1)
    cs = np.concatenate([np.zeros((reps, 1)), cs], axis=1)
    ma = (cs[:, nwin:] - cs[:, :-nwin]) / nwin
    p_fixed = (ma[:, 300] >= m_p).mean()           # 임의의 한 시작점(고정)
    p_max = (ma.max(axis=1) >= m_p).mean()          # 기록 어디선가 최대
    print("rho=%.1f : 정해진 한 시작점에서 15년 평균>=0.600 비율 %.5f | 1112년 어디선가 최대>=0.600 비율 %.4f" % (rho, p_fixed, p_max))
rb = 0.728
for ns in (25, 12):
    print("EPS = n*rbar/(1+(n-1)*rbar), rbar=0.728, n=%d : %.4f" % (ns, ns * rb / (1 + (ns - 1) * rb)))
print("논문 EPS 0.990 (n>=25 에서). 이 식으로 0.990 이 되려면 n = %.1f 계열 필요 (rbar=0.728 고정)" % ((0.990 * (1 - rb)) / (rb * (1 - 0.990))))
print("rbar 0.728±0.044 에서 n=25 의 EPS: rbar=0.684 → %.4f, rbar=0.772 → %.4f" % tuple(25 * r / (1 + 24 * r) for r in (0.684, 0.772)))
print("r^2 = 55.8%% → r = %.3f (논문 1959~2009 교정)" % np.sqrt(0.558))
print("주의: 가상 계열의 SD를 1.550으로 맞췄을 뿐 실제 계열의 자기상관은 이 책이 구하지 못했다(근거 논문 보충자료 확보 필요).")

print("\n=== 계산 12-4: Solomina 등(2016) 알타이 나무 피해 연대 군집 ===")
clusters = [(1200, 1260, 3), (1320, 1380, 4), (1440, 1510, 5), (1640, 1740, 8)]
tot = sum(c[2] for c in clusters)
print("군집 연대 합 =", tot)
for a, b, c in clusters:
    print("군집 %d~%d : %d개, 길이 %d년, 100년당 %.1f개" % (a, b, c, b - a, c / (b - a) * 100))
rng = np.random.default_rng(16)
for lo, hi in [(1200, 1750), (1000, 1850), (1200, 1900)]:
    T = hi - lo
    reps = 20000
    ev = rng.uniform(0, T, size=(reps, tot))
    ev.sort(axis=1)
    mxs = np.empty(reps, dtype=int)
    for r in range(reps):
        e = ev[r]
        right = np.searchsorted(e, e + 100.0, side='right')
        mxs[r] = (right - np.arange(tot)).max()
    print("균등 가정 [%d,%d] 에 %d개: 100년 창 최대 >=8 비율 %.4f, 최대 평균 %.2f" % (lo, hi, tot, (mxs >= 8).mean(), mxs.mean()))
print("고정한 100년 창에 8개 이상 (독립, 이항): p=100/550 → %.5f" % stats.binom.sf(7, tot, 100 / 550))
print("주의: 이 20개는 논문이 군집으로 적은 연대만이다. 군집 밖 연대 수와 나무 피해 한 건이 한 번의 전진인지는 확인하지 못했다. 시연값이다.")

print("\n=== 계산 12-5: 복원이 설명하는 분산(r과 r^2) ===")
tab = [
    ("Pederson 2014 몽골 PDSI (r^2=0.558)", None, 0.558),
    ("D'Arrigo 2001 몽골 온도 (분산 33%)", None, 0.33),
    ("Hantemirov 2022 야말 6~7월 온도 (r=0.75)", 0.75, None),
    ("PAGES 2k 2013 아시아 (r=0.52)", 0.52, None),
    ("Chen 2022 톈산 유량 1차 차분 (r=0.50)", 0.50, None),
    ("Büntgen 2011 알프스 온도 (r=0.72~0.92)", None, None),
    ("Büntgen 2011 오크 4~6월 강수 합성 (r=0.50~0.59)", None, None),
]
for nm, r, r2 in tab:
    if r is not None:
        print("%s → r^2 = %.3f" % (nm, r * r))
    elif r2 is not None:
        print("%s → r = %.3f" % (nm, np.sqrt(r2)))
print("Büntgen 2011 알프스 r^2 범위: %.3f ~ %.3f" % (0.72 ** 2, 0.92 ** 2))
print("Büntgen 2011 오크 합성 r^2 범위: %.3f ~ %.3f" % (0.50 ** 2, 0.59 ** 2))
print("주의: 세 가지 다른 종류의 값(r, r^2, 차분 r)을 같은 줄에 놓았다. 교정 기간과 대상 변수가 서로 다르므로 순위를 매기지 않는다.")

print("\n=== 계산 12-6: 최근 천 년 알타이 일대 기록의 시기 겹침 ===")
rec = {
    "Teletskoye 소빙기 국면 1560~1820 (Andreev 2007 본문)": (1560, 1820),
    "Teletskoye 온난·습윤 1200~1410": (1200, 1410),
    "Teletskoye 냉·건 1100~1200": (1100, 1200),
    "알타이 빙하 최대 1640~1740 (Solomina 2016)": (1640, 1740),
    "알타이 나무피해 군집 1200~1260": (1200, 1260),
    "알타이 나무피해 군집 1320~1380": (1320, 1380),
    "알타이 나무피해 군집 1440~1510": (1440, 1510),
    "알타이 빙하 후퇴 8~12세기 700~1199 (Solomina 2016)": (700, 1199),
    "Telmen 건조 700~1300 (Struck 2022)": (700, 1300),
    "Telmen 습윤 1300~ (Struck 2022)": (1300, 2000),
    "Pederson 우기 1211~1225": (1211, 1225),
    "Chen 높은 유량 1225~1239": (1225, 1239),
    "Chen 높은 유량 1361~1400": (1361, 1400),
    "Belukha 빙핵 기록 1250~2001 (Eichler 2009)": (1250, 2001),
    "PAGES 2k 화산·태양 저하 1251~1310": (1251, 1310),
    "PAGES 2k 화산·태양 저하 1431~1520": (1431, 1520),
    "PAGES 2k 화산·태양 저하 1581~1610": (1581, 1610),
    "PAGES 2k 화산·태양 저하 1641~1700": (1641, 1700),
}
def ov(a, b):
    lo = max(a[0], b[0]); hi = min(a[1], b[1])
    return max(0, hi - lo + 1)
names = list(rec)
def pair(a, b):
    A = rec[a]; B = rec[b]
    o = ov(A, B)
    u = (A[1] - A[0] + 1) + (B[1] - B[0] + 1) - o
    print("겹침 %4d년 / 합집합 %4d년 (자카드 %.2f) | %s ↔ %s" % (o, u, o / u, a, b))
pair(names[0], names[3])
pair(names[1], names[4]); pair(names[1], names[5]); pair(names[1], names[6])
pair(names[2], names[7])
pair(names[8], names[1]); pair(names[9], names[0])
pair(names[8], names[7])
pair(names[10], names[8]); pair(names[10], names[1])
pair(names[11], names[10])
pair(names[0], names[17]); pair(names[3], names[17])
print("해석 주의: 창 경계는 논문이 '대략'으로 적은 값이다. 겹침 연수는 경계를 어떻게 읽느냐에 따라 10~50년 달라질 수 있다.")

print("\n=== 계산 12-7: 카스피해 수위 두 논문의 숫자 ===")
print("Naderi Beni 2013: 소빙기 고수위 약 -21 m, 중세 온난기 저수위 약 -28 m → 차이 %.1f m, 현재 -26.5 m" % (-21 - (-28)))
print("현재와 비교: 소빙기 고수위는 %.1f m 위, 중세 저수위는 %.1f m 아래" % (-21 - (-26.5), -28 - (-26.5)))
print("Kroonenberg 2007 초록: 최근 천 년 동안 변동 약 25 m. Naderi Beni 의 7 m 와 %.1f배 차이" % (25 / 7))
print("두 값의 차이를 이 책은 해소하지 못했다(Kroonenberg 초록은 중간에서 끊김; 기준 구간과 정의 확인 필요).")

print("\n=== 계산 12-8: Chen 등(2022) 톈산 유량의 내부 점검 ===")
mean_flow, sd_flow = 358.9, 51.1
a, b = 96.051, 266.905
print("평균 유량 358.9 → 회귀식 Y = %.3f + %.3f X 에서 X 평균 = %.3f" % (a, b, (mean_flow - a) / b))
print("유량 SD 51.1 / 기울기 266.905 → 지수 X 의 SD = %.3f" % (sd_flow / b))
print("20세기 평균 332.0 vs 전체 358.9: %.1f%% (%.2f SD)" % ((332.0 - 358.9) / 358.9 * 100, (332.0 - 358.9) / sd_flow))
print("복원 길이 1225~2009 = %d년 (논문 785년)" % (2009 - 1225 + 1))
for nm, (x, y) in {"높은 1225~1239": (1225, 1239), "낮은 1240~1251": (1240, 1251), "높은 1252~1260": (1252, 1260), "높은 1361~1400": (1361, 1400)}.items():
    print(nm, ": 길이", y - x + 1, "년")
print("높은 유량 창 길이 합 = %d년 (복원의 %.1f%%)" % (15 + 9 + 40 + 31 + 13 + 29, (15 + 9 + 40 + 31 + 13 + 29) / 785 * 100))
print("(1225~1239 15, 1252~1260 9, 1361~1400 40, 1437~1467 31, 1693~1705 13, 1731~1759 29)")

print("\n=== 계산 12-9: 기록 기후와 극값의 숫자 (Büntgen 2011, Gaceu 2025, Büntgen 2016) ===")
from math import sqrt
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
p, lo, hi = wilson(30, 32)
print("Büntgen 2011: 서기 1013~1504 나이테 극값 32개 중 30개를 목격 기록 88건이 뒷받침: %.3f (95%% 구간 %.3f~%.3f)" % (p, lo, hi))
print("같은 구간의 기록 16건은 나이테 극값과 어긋남(논문 서술). 뒷받침 88 : 어긋남 16 = %.2f : 1" % (88 / 16))
print("Büntgen 2011: 오크 계열 수 최대 550(로마 시대)에서 400년경 44로 감소: %.1f배" % (550 / 44))
print("Gaceu 2025: 16세기 기록 62%%가 덮는 해 ≈ %.0f년, 빈 해 ≈ %.0f년" % (0.62 * 100, 0.38 * 100))
print("Gaceu 2025: 더운 여름 40 : 추운 겨울 8 (겨울 대 여름은 종류가 달라 비교하지 않는다), 건조 29 : 홍수 25 : 비 많은 해 14")
print("Gaceu 2025: 전염병 30년, 기근 23년, 메뚜기 9년 → 기근/전염병 = %.2f" % (23 / 30))
print("Gaceu 2025: 더운 여름 40개가 모두 서로 다른 해라면 덮인 62년 중 %.0f%%. (같은 해 중복 가능; 상한)" % (40 / 62 * 100))
print("Büntgen 2016 알타이 극값 범위: 최난 +1.6(982년) ~ 최한 -4.6(172년) = %.1f °C, 알프스 +3.5(2003년) ~ -3.3(1821년) = %.1f °C" % (1.6 + 4.6, 3.5 + 3.3))
print("Büntgen 2016 540년대 알타이 -3.2 °C 는 최한 해(-4.6)보다 %.1f °C 덜 춥고, 알프스 -1.9 °C" % (4.6 - 3.2))
print("Büntgen 2016 알타이 계열 수 최소 10(98년) ~ 최대 240(1279년): %.0f배; 고리 수 234,399 / 계열 660 = 계열당 평균 %.0f개" % (240 / 10, 234399 / 660))
print("Büntgen 2016 살아 있는 나무 152 + 유물 508 = %d (논문 660)" % (152 + 508))
