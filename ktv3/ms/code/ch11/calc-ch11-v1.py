# -*- coding: utf-8 -*-
"""11장 계산 11-1 ~ 11-5. 입력 숫자는 모두 논문(또는 논문을 요약한 쪽)에서 옮긴 것이고 각 줄에 출처를 적었다.
실행: python3 calc-ch11-v1.py > calc-ch11-v1.log
"""
import numpy as np, math
from math import comb, sqrt

print("=== 입력 (출처) ===")
EV = {  # 사건 연대(서기). 점 사건은 (시작, 끝) 같은 값
 "훈 첫 확실한 유럽 출현(약 370)": (370, 370),   # Maróti 등(2022): 'ca 370 CE'; 백과 요약(History of the Huns): 약 370
 "고트인 도나우 도하(376)": (376, 376),            # 백과 요약
 "훈 습격 422": (422, 422), "훈 습격 442": (442, 442), "훈 습격 447": (447, 447),
 "훈 침공 451": (451, 451), "훈 침공 452": (452, 452),   # Hakenbeck·Büntgen(2022) 보도자료
 "유연 패망 551(Büntgen 2016)": (551, 551), "유연 패망 555(보도 요약)": (555, 555),
 "아바르 카르파티아 정착 567/568": (567, 568),     # Gnecchi-Ruscone 등(2022) 초록
 "마자르 카르파티아 도하 894/895": (894, 895),     # 백과 요약(Hungarian prehistory); Maróti 등(2022) '9세기 말'
}
WIN = {  # 기후 창
 "중부유럽 기후 변동 큼 250~550": (250, 550),      # Büntgen 등(2011) 본문. 초록은 250~600
 "알타이 나무 새로 자람 감소 약 350~650": (350, 650),  # Büntgen 등(2016) 'about 350 and 650'
 "헝가리 건조 여름 420~450": (420, 450),            # Hakenbeck·Büntgen(2022) 보도자료
 "알타이 빙하 전진 마셰이 433~595": (433, 595),      # Solomina 등(2016)
 "알타이 빙하 전진 멘수 435~767": (435, 767),        # Solomina 등(2016)
 "후기 고대 소빙기 536~660": (536, 660),            # Büntgen 등(2016)
 "알타이 최저온 10년 540년대": (540, 549),           # Büntgen 등(2016): -3.2 °C
 "몽골 소나무 한랭 536~545": (536, 545),             # D'Arrigo 등(2001)
 "텔멘호 고수위 +4.8 m 600~700": (600, 700),         # Struck 등(2022)
}
for k, v in EV.items(): print("사건", k, v)
for k, v in WIN.items(): print("창  ", k, v)

print("\n=== 계산 11-1: 사건이 창 안에 드는가, 우연히 들 확률 ===")
BASE = [(300, 900), (200, 1000)]
def inside(ev, w):
    return ev[0] >= w[0] and ev[1] <= w[1]
print("기준 구간 두 가지(이 책이 정한 값):", BASE)
rows = []
for en, ev in EV.items():
    for wn, w in WIN.items():
        if inside(ev, w):
            L = w[1] - w[0] + 1
            ps = ["%.3f" % (L / (b - a + 1)) for a, b in BASE]
            rows.append((en, wn, L, ps))
            print("안:", en, "|", wn, "| 창 길이", L, "년 | 무작위 한 해가 창 안일 확률", ps)
print("창 안에 든 (사건,창) 쌍:", len(rows), "/ 전체", len(EV) * len(WIN))
print("-- 창별 요약: 창 이름 | 길이 | 안에 든 사건 수(11개 중) | 무작위 한 해가 안일 확률 [300,900], [200,1000] --")
for wn, w in WIN.items():
    L = w[1] - w[0] + 1
    k = sum(1 for en, ev in EV.items() if inside(ev, w))
    print("창요약 | %s | %d년 | %d | %.4f, %.4f" % (wn, L, k, L / (BASE[0][1] - BASE[0][0] + 1), L / (BASE[1][1] - BASE[1][0] + 1)))


print("\n=== 계산 11-2: 습격 5회와 건조 창 420~450 (표본 5, 창 31년) ===")
raids = np.array([422, 442, 447, 451, 452])
wlen = 31
print("창 안 습격 수(420~450):", int(((raids >= 420) & (raids <= 450)).sum()), "/ 5")
best = max(int(((raids >= s) & (raids <= s + wlen - 1)).sum()) for s in range(380, 480))
print("31년 창이 담을 수 있는 최대 습격 수:", best, "(예: 422~452)")
for a, b in [(400, 500), (380, 480), (350, 550), (300, 600)]:
    starts = np.arange(a, b - wlen + 2)
    cnt = np.array([int(((raids >= s) & (raids <= s + wlen - 1)).sum()) for s in starts])
    p3 = (cnt >= 3).mean()
    # 반대 방향: 습격 날짜 5개를 [a,b]에서 무작위로 뽑고 고정 창 420~450 이 3개 이상 담을 확률
    p = wlen / (b - a + 1)
    pb = sum(comb(5, k) * p ** k * (1 - p) ** (5 - k) for k in range(3, 6))
    print("기준 [%d,%d]: (가) 창 위치를 무작위로 옮길 때 3개 이상 담는 비율 %.3f | (나) 날짜를 무작위로 뽑을 때 고정 창이 3개 이상 담을 확률 %.4f" % (a, b, p3, pb))
print("-- 같은 보도자료의 다른 서술: 극심한 건조 '430년대~450년대' = 430~459 (30년) --")
w2 = 30
print("창 430~459 안 습격 수:", int(((raids >= 430) & (raids <= 459)).sum()), "/ 5 (442, 447, 451, 452)")
for a, b in [(400, 500), (350, 550), (300, 600)]:
    starts = np.arange(a, b - w2 + 2)
    cnt = np.array([int(((raids >= s) & (raids <= s + w2 - 1)).sum()) for s in starts])
    p4 = (cnt >= 4).mean()
    p = w2 / (b - a + 1)
    pb = sum(comb(5, k) * p ** k * (1 - p) ** (5 - k) for k in range(4, 6))
    print("기준 [%d,%d]: (가') 30년 창을 옮길 때 4개 이상 담는 비율 %.3f | (나') 날짜를 무작위로 뽑을 때 고정 창이 4개 이상 담을 확률 %.4f" % (a, b, p4, pb))
print("주의: 창 420~450 은 저자들이 날짜를 본 뒤 정했다. 위 확률은 '사후 선택'을 반영하지 않으므로 하한이 아니라 단순 참고값이다.")

print("\n=== 계산 11-3: 기후 시작과 사건 사이의 시간차(연) ===")
clim = {"536 후기 고대 소빙기 시작": 536, "540년대 한랭 시작": 540, "건조 창 시작 420": 420, "알타이 새 자람 감소 시작 약 350": 350}
evs = {"유연 패망 551": 551, "유연 패망 555": 555, "아바르 정착 567": 567, "아바르 정착 568": 568, "습격 422": 422, "훈 출현 약 370": 370}
for cn, cy in clim.items():
    for en, ey in evs.items():
        print("%s -> %s : %+d년 (사건-기후)" % (cn, en, ey - cy))
print("해석 주의: 음수는 사건이 기후 창보다 먼저라는 뜻이다. 연대 불확실성(수년~수십 년)이 이 차이보다 클 수 있다.")

print("\n=== 계산 11-3 보충: 세 이동 사이의 간격(연) ===")
print("훈 첫 출현 370 → 아바르 정착 567: %d년, 568: %d년" % (567 - 370, 568 - 370))
print("아바르 정착 567 → 마자르 도하 895: %d년, 568 → 894: %d년" % (895 - 567, 894 - 568))
print("훈 370 → 마자르 895: %d년" % (895 - 370))
print("유연 패망 551 → 아바르 정착 567: %d년, 555 → 568: %d년" % (567 - 551, 568 - 555))
print("후기 고대 소빙기 536~660 길이: %d년. 아바르 정착 567 은 시작에서 %d년째" % (660 - 536 + 1, 567 - 536 + 1))
print("가장 추운 10년(540년대) 시작에서 유연 패망(551)까지 %d년" % (551 - 540))
print("540년대의 끝(549)에서 유연 패망 551: %d년, 555: %d년, 아바르 567: %d년, 568: %d년" % (551 - 549, 555 - 549, 567 - 549, 568 - 549))
print("536~545년 한랭의 끝(545)에서 유연 패망 551: %d년, 555: %d년" % (551 - 545, 555 - 545))

print("\n=== 계산 11-4: 고대 DNA 비율의 신뢰구간(Wilson 95%) ===")
def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
for name, k, n in [
    ("훈 시대 공개 유전체 R1a-Z93 (Maróti 2022: 10/23)", 10, 23),
    ("훈 시대 공개 유전체 Q (9/23)", 9, 23),
    ("훈 시대 6명 중 R1a1a1b2 (4/6)", 4, 6),
    ("아바르 계열 76명 중 아시아 핵심 12명", 12, 76),
    ("ARK 남성 10명 중 Q (8/10)", 8, 10),
]:
    p, lo, hi = wilson(k, n)
    print("%s : %.3f  95%% 구간 %.3f ~ %.3f  (구간 폭 %.3f)" % (name, p, lo, hi, hi - lo))
print("확인: 아바르 계열 26 + 40 =", 26 + 40, "(76 중), 나머지", 76 - 66)
print("확인: 정복자 모형 50+35+15 =", 50 + 35 + 15)

print("\n=== 계산 11-5: 이동 속도의 범위(시연값: 이동 기간을 가정) ===")
D = 5000.0  # 보도 요약의 '5000 km 넘게'. 논문 본문 수치 아님.
for T in (5, 10, 17, 30):
    print("거리 %.0f km를 %d년에 가면: 연 %.0f km, 하루 %.2f km" % (D, T, D / T, D / T / 365.0))
print("거리 5000 km는 보도 요약의 값이며 논문 본문에서 확인하지 못했다. 이동 기간 T는 가정이다.")

print("\n=== 계산 11-6: 기후 기록 지점과 사건 지점 사이의 거리(WGS84 측지선, km) ===")
import os, geopandas as gpd
from pyproj import Geod
G = Geod(ellps='WGS84')
GEO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'geodata')
lk = gpd.read_file(os.path.join(GEO, 'ne_10m_lakes.geojson'))
pp = gpd.read_file(os.path.join(GEO, 'ne_10m_populated_places_simple.geojson'))
def lake(n):
    r = lk[lk['name_en'].astype(str) == n].iloc[0]
    c = r.geometry.centroid
    return c.x, c.y
def city(n):
    r = pp[pp['name'].astype(str) == n].iloc[0]
    return r.geometry.x, r.geometry.y
P = {
 "텔멘호(Natural Earth 호수 도형 중심)": lake("Telmen"),
 "텔레츠코예호(호수 도형 중심)": lake("Teletskoe"),
 "벨루하 빙핵(Eichler 등 2009 좌표 49.80N 86.57E)": (86 + 34 / 60, 49 + 48 / 60),
 "톈산 나이테 상자 중심(Chen 등 2022: 42~45N, 79~84E)": ((79 + 84) / 2, (42 + 45) / 2),
 "이식쿨호(호수 도형 중심)": lake("Issyk-Kul"),
 "부다페스트(도시 점; 헝가리 평원 중심이 아니다)": city("Budapest"),
 "울란바토르(도시 점)": city("Ulaanbaatar"),
}
for k, v in P.items(): print("%s : 경도 %.2f, 위도 %.2f" % (k, v[0], v[1]))
def dist(a, b):
    _, _, d = G.inv(P[a][0], P[a][1], P[b][0], P[b][1]); return d / 1000.0
bud = "부다페스트(도시 점; 헝가리 평원 중심이 아니다)"
for k in P:
    if k != bud:
        print("%s → 부다페스트 : %.0f km" % (k, dist(k, bud)))
print("텔멘호 ↔ 벨루하 : %.0f km, 텔멘호 ↔ 텔레츠코예호 : %.0f km" % (dist("텔멘호(Natural Earth 호수 도형 중심)", "벨루하 빙핵(Eichler 등 2009 좌표 49.80N 86.57E)"), dist("텔멘호(Natural Earth 호수 도형 중심)", "텔레츠코예호(호수 도형 중심)")))
print("울란바토르 → 부다페스트 : %.0f km (보도 요약의 '5000 km 넘게'와 비교; 대원 거리이며 실제 이동 경로가 아니다)" % dist("울란바토르(도시 점)", bud))
print("주의: 호수 좌표는 Natural Earth 도형의 중심이라 논문의 시추 지점과 수 km~수십 km 다르다. 부다페스트는 도시 점이다.")
