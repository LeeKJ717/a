# -*- coding: utf-8 -*-
"""실습 1-3: 두 점 사이의 거리를 다섯 가지 방법으로 잰다. 제1권 11.5.6절(계산 11-13)의 거리를 되풀이한다.
방법: (가) 손계산 피타고라스(제1권), (나) 구면 대원 거리 haversine, (다) 타원체 측지선 pyproj.Geod,
      (라) 투영 평면 거리(UTM 52N, EPSG:5179), (마) 경위도를 평면 좌표로 착각한 거리."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K

lb = (K.dms(128, 3), K.dms(44, 6))          # 노백산: 128°03′E, 44°06′N (Lyu 등, 2016 본문 표기)
dh = (K.dms(128, 12), K.dms(43, 22))        # 돈화 기상대: 128°12′E, 43°22′N
print('== 1. 제1권 계산 11-13 되풀이 ==')
print('노백산 (%.4f, %.4f) 돈화 기상대 (%.4f, %.4f)' % (lb + dh))
dlat = lb[1] - dh[1]; dlon = dh[0] - lb[0]
ns = dlat * 111.2; ew = dlon * 111.2 * math.cos(math.radians(43.7))
print('(가) 손계산: 위도차 %.4f° x 111.2 = %.1f km ; 경도차 %.4f° x 111.2 x cos 43.7° = %.1f km ; 피타고라스 = %.1f km' % (dlat, ns, dlon, ew, math.hypot(ns, ew)))
hv = K.haversine(*lb, *dh)
print('(나) haversine (R = %.4f km) = %.4f km' % (K.R_MEAN, hv))
ge = K.geodesic_km(*lb, *dh)
print('(다) WGS84 측지선 = %.4f km' % ge)
print('(라) 투영 평면: UTM 52N = %.4f km ; EPSG:5179 = %.4f km' % (K.projected_km(*lb, *dh, 32652), K.projected_km(*lb, *dh, 5179)))
nv = math.hypot(dlon, dlat) * 111.2
print('(마) 경위도를 평면으로 착각해 도를 111.2 km 로 곱함 = %.4f km  (경도도 cos 없이 111.2 곱함)' % nv)
print('제1권 값: 82.4 km(손계산), 82.43 km(대원 거리). 이번 (나) %.2f km → %s' % (hv, '일치' if round(hv, 2) == 82.43 else '불일치'))
print('(나)-(다) 차이 %.3f km (%.3f%%)' % (hv - ge, 100 * (hv - ge) / ge))
dn = K.geodesic_km(128.22, 43.35, *dh)
print('Natural Earth 돈화시(128.22, 43.35) ~ 돈화 기상대 = %.2f km (제1권 2.46 km)' % dn)
print('좌표를 분 단위로 적은 반올림 크기 1′ = %.4f° = 위도 방향 %.2f km (제1권은 0.0167° x 111.2 = %.2f km)' % (1 / 60, K.geodesic_km(128, 43, 128, 43 + 1 / 60), 0.0167 * 111.2))

print()
print('== 2. 거리가 다른 쌍들: 다섯 방법의 차이 ==')
P = {'서울': (126.997785, 37.568295), '부산': (129.008102, 35.096999), '제주': (126.521931, 33.510137), '평양': (125.752745, 39.021385),
     '도쿄': (139.749462, 35.686963), '북경': (116.386340, 39.930838), '합이빈': (126.648, 45.752), '노백산': lb, '돈화 기상대': dh}
pairs = [('노백산', '돈화 기상대'), ('서울', '제주'), ('서울', '부산'), ('서울', '평양'), ('서울', '북경'), ('서울', '도쿄'), ('부산', '합이빈')]
print('기준은 WGS84 측지선(다). 열 값은 (다) 대비 % 차이.')
print('%-14s %9s | %8s %8s %8s %8s %10s' % ('쌍', '측지선 km', '구면', 'UTM52N', 'EPSG5179', 'Web Merc', '도를111.2km'))
rows = []
for a, b in pairs:
    pa, pb = P[a], P[b]
    g = K.geodesic_km(*pa, *pb)
    h = K.haversine(*pa, *pb)
    u = K.projected_km(*pa, *pb, 32652)
    k = K.projected_km(*pa, *pb, 5179)
    m = K.projected_km(*pa, *pb, 3857)
    n = math.hypot(pb[0] - pa[0], pb[1] - pa[1]) * 111.2
    rows.append((a, b, g, h, u, k, m, n))
    print('%-14s %9.2f | %+7.2f%% %+7.2f%% %+7.2f%% %+7.1f%% %+9.1f%%' % ('%s-%s' % (a, b), g, *(100 * (x / g - 1) for x in (h, u, k, m, n))))

print()
print('== 3. 위도 44°에서 동서 방향 80 km 두 점: 투영마다 다른 값 ==')
la = 44.0
lo2 = 128.0
# 동쪽으로 정확히 80 km 떨어진 점(측지선 직접 문제)
lo_e, la_e, _ = K.GEOD.fwd(lo2, la, 90, 80000)
print('출발 (%.4f, %.4f) → 방위 90°로 80 km → (%.4f, %.4f) (pyproj.Geod.fwd)' % (lo2, la, lo_e, la_e))
print('측지선 거리 %.4f km ; haversine %.4f ; UTM52N %.4f ; EPSG5179 %.4f ; Web Merc %.4f' % (
    K.geodesic_km(lo2, la, lo_e, la_e), K.haversine(lo2, la, lo_e, la_e), K.projected_km(lo2, la, lo_e, la_e, 32652), K.projected_km(lo2, la, lo_e, la_e, 5179), K.projected_km(lo2, la, lo_e, la_e, 3857)))
print('정동(방위 90°)으로 출발해도 측지선은 대원 위를 가므로 도착 위도가 %.4f° 로 출발(44°)보다 약간 낮다' % la_e)

print()
print('== 4. 대원 경로의 중간 점: 서울-도쿄를 5등분 ==')
pts = K.GEOD.npts(*P['서울'], *P['도쿄'], 4)
print('서울 (126.9978, 37.5683) → 도쿄 (139.7495, 35.6870) 사이 4점:')
for lo, la in pts:
    print('  %.4fE %.4fN' % (lo, la))
print('직선(경위도 평면) 중간점은 (%.4f, %.4f) ; 대원 경로 가운데 점의 위도는 %.4f° (북쪽으로 휜다)' % ((P['서울'][0] + P['도쿄'][0]) / 2, (P['서울'][1] + P['도쿄'][1]) / 2, K.GEOD.npts(*P['서울'], *P['도쿄'], 1)[0][1]))
