# -*- coding: utf-8 -*-
"""실습 9-12~9-14. 화산재 확산 반경의 거리 계산: 분출구에서 지점까지의 거리와 방위, 반경 r 안의 면적, 부채꼴, 도달 시간.
좌표는 제1권 4장 4.1절 표와 계산 4-1에서 옮겼다. 개성(37.97N, 126.55E)은 제1권이 "시연값"이라 한 좌표이다.
이 계산은 분출구에서 같은 거리에 있으면 같은 정도로 재가 닿는다는 가정이 아니다. 거리와 면적의 기하일 뿐이다.
실행: python3 ex5-radius.py > ex5-radius.log"""
import os, sys, json, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy
import tephralib as T
print('파이썬 %s, numpy %s, scipy %s' % (platform.python_version(), np.__version__, scipy.__version__))
V = {'백두산(Lee 등 2024)': (41.99, 128.08), '백두산(McLean 등 2019: 41°00′N, 128°03′E)': (41.0, 128.05)}
S = {'스이게쓰호': (35 + 35 / 60.0, 135 + 53 / 60.0), '울릉도': (37.5, 130 + 52 / 60.0), '개성(시연값 좌표)': (37.97, 126.55),
     'Du 등(2025) 정상부 시료 지점': (41.98815, 128.00491)}
res = {}
vent = V['백두산(Lee 등 2024)']
print('\n[실습 9-12] 분출구(%.2f N, %.2f E)에서 각 지점까지: 구면 거리와 처음 방위' % vent)
print('  %-30s %10s %8s' % ('지점', '거리(km)', '방위(도)'))
res['sites'] = {}
for k, (la, lo) in S.items():
    d = float(T.hav(vent[0], vent[1], la, lo)); b = float(T.bearing(vent[0], vent[1], la, lo))
    res['sites'][k] = dict(lat=la, lon=lo, d=d, b=b)
    print('  %-30s %10.2f %8.1f' % (k, d, b))
d_uls = float(T.hav(S['울릉도'][0], S['울릉도'][1], *S['스이게쓰호']))
d_bu = float(T.hav(vent[0], vent[1], *S['울릉도']))
print('  울릉도 → 스이게쓰호 %.2f km (방위 %.1f도), 백두산 → 울릉도 %.2f km (방위 %.1f도)' % (
    d_uls, T.bearing(*S['울릉도'], *S['스이게쓰호']), d_bu, T.bearing(vent[0], vent[1], *S['울릉도'])))

print('\n[실습 9-12b] 분출구 좌표가 두 가지(제1권 4.1절 표)일 때 스이게쓰호까지 거리')
d_a = float(T.hav(*vent, *S['스이게쓰호'])); d_b = float(T.hav(*V['백두산(McLean 등 2019: 41°00′N, 128°03′E)'], *S['스이게쓰호']))
d_vv = float(T.hav(*vent, *V['백두산(McLean 등 2019: 41°00′N, 128°03′E)']))
print('  Lee 등 좌표: %.2f km, McLean 등 좌표: %.2f km, 두 분출구 좌표 사이 %.2f km, 거리 차이 %.2f km' % (d_a, d_b, d_vv, d_a - d_b))
print('  McLean 등은 약 1000 km, Costa 등은 약 950 km로 쓴다(제1권 4.1절). Lee 등의 좌표로는 이 두 서술 사이에 들고, McLean 등의 좌표(위도 약 1° 낮음)로는 두 서술보다 짧다.')
res['vent2'] = dict(a=d_a, b=d_b, between=d_vv)

try:
    import pyproj
    g = pyproj.Geod(ellps='WGS84')
    print('\n[실습 9-12c] 구면(반지름 6371 km)과 WGS84 타원체(pyproj %s) 거리의 차이 (이 비교에만 pyproj를 쓴다)' % pyproj.__version__)
    for k, (la, lo) in S.items():
        _, _, dm = g.inv(vent[1], vent[0], lo, la)
        ds = float(T.hav(vent[0], vent[1], la, lo))
        print('  %-30s 구면 %9.3f km, 타원체 %9.3f km, 차이 %+.3f km (%.2f%%)' % (k, ds, dm / 1000, ds - dm / 1000, 100 * (ds - dm / 1000) / (dm / 1000)))
except Exception as e:
    print('pyproj를 쓸 수 없음:', e)

print('\n[실습 9-13] 반지름 r 안의 면적: 평면 원 pi r^2 대 구면 모자 2 pi R^2 (1 - cos(r/R))')
print('  %8s %16s %16s %10s' % ('r(km)', '평면 원(km²)', '구면 모자(km²)', '비(구면/평면)'))
res['area'] = {}
for r in (30.0, 465.6, 553.1, 981.5, 3000.0):
    ap = np.pi * r ** 2; ac = float(T.cap_area(r))
    res['area'][str(r)] = (ap, ac)
    print('  %8.1f %16.1f %16.1f %10.5f' % (r, ap, ac, ac / ap))
print('  지구 전체 표면적 4 pi R^2 = %.1f km²' % (4 * np.pi * T.R_EARTH ** 2))
print('  (면적 비는 r이 작으면 1에 가깝다. 이 장의 반경 981.5 km에서는 약 %.3f이다.)' % (T.cap_area(981.5) / (np.pi * 981.5 ** 2)))

print('\n[실습 9-13b] 부채꼴: 축 방위와 반각을 주고 그 안에 드는 면적과 지점')
axis = res['sites']['스이게쓰호']['b']
print('  축 = 분출구 → 스이게쓰호 방위 %.1f도. 반각 α와 반경 R은 시연값(α = 20, 30, 45도, R = 981.5 km)' % axis)
def sector_area(R, alpha):
    return float(T.cap_area(R) * (2 * alpha / 360.0))
def in_sector(lat, lon, R, alpha):
    d = float(T.hav(vent[0], vent[1], lat, lon)); b = float(T.bearing(vent[0], vent[1], lat, lon))
    da = abs((b - axis + 180) % 360 - 180)
    return d <= R and da <= alpha, d, da
res['sector'] = {}
for al in (20, 30, 45):
    ar = sector_area(981.5, al)
    flags = {k: in_sector(la, lo, 981.5, al) for k, (la, lo) in S.items()}
    res['sector'][str(al)] = dict(area=ar, inside={k: bool(v[0]) for k, v in flags.items()})
    print('  α=%2d도: 면적 %.1f km² (모자 면적의 %.3f)' % (al, ar, 2 * al / 360.0) + ' | 드는 지점: ' + ', '.join('%s %s(축에서 %.1f도)' % (k, '예' if v[0] else '아니오', v[2]) for k, v in flags.items()))
# 독립 점검: 구 전체에 균일하게 뿌린 점으로 부채꼴 면적을 센다
rng = np.random.default_rng(20261026)
tot = 0; hit = {20: 0, 30: 0, 45: 0}; NT = 40_000_000; chunk = 4_000_000
for _ in range(NT // chunk):
    u = rng.random(chunk); v = rng.random(chunk)
    lat = np.degrees(np.arcsin(2 * u - 1)); lon = 360 * v - 180
    d = T.hav(vent[0], vent[1], lat, lon)
    near = d <= 981.5
    b = T.bearing(vent[0], vent[1], lat[near], lon[near])
    da = np.abs((b - axis + 180) % 360 - 180)
    for al in hit: hit[al] += int((da <= al).sum())
    tot += chunk
print('  독립 점검: 구 전체에 균일하게 뿌린 점 %d개 중 반경 981.5 km 안이면서 축에서 α 이내인 점으로 면적 추정 (구 표면 %.1f km² × 비율)' % (tot, 4 * np.pi * T.R_EARTH ** 2))
for al in hit:
    est = 4 * np.pi * T.R_EARTH ** 2 * hit[al] / tot
    ex = sector_area(981.5, al)
    se = 4 * np.pi * T.R_EARTH ** 2 * np.sqrt(hit[al]) / tot
    print('    α=%2d도: 추정 %.0f ± %.0f km², 식 %.0f km², 차이 %+.0f km² (%.2f 표준오차)' % (al, est, se, ex, est - ex, (est - ex) / se))
    res['sector'][str(al)]['mc'] = (est, se)

print('\n[실습 9-14] 이동 시간: 거리 / 속도 (제1권 4.7절 계산 2, 3의 되풀이와 확장; 풍속 5~20 m/s는 제1권의 시연값)')
print('  %-30s %10s %12s %12s' % ('지점', '거리(km)', '20 m/s(일)', '5 m/s(일)'))
for k, v in res['sites'].items():
    d = v['d']
    print('  %-30s %10.2f %12.3f %12.3f' % (k, d, d * 1000 / 20 / 86400, d * 1000 / 5 / 86400))
print('  소리(340 m/s 가정): 개성 %.0f초 = %.1f분, 스이게쓰호 %.0f초 = %.1f분' % (
    res['sites']['개성(시연값 좌표)']['d'] * 1000 / 340, res['sites']['개성(시연값 좌표)']['d'] * 1000 / 340 / 60,
    res['sites']['스이게쓰호']['d'] * 1000 / 340, res['sites']['스이게쓰호']['d'] * 1000 / 340 / 60))
print('  역으로, 981.5 km를 1일, 2일, 3일에 가려면 평균 %.1f, %.1f, %.1f m/s' % tuple(981500 / (n * 86400) for n in (1, 2, 3)))

print('\n[실습 9-14b] 반경 위의 점 만들기: 분출구에서 동쪽(방위 90도)으로 15 km, 30 km (Costa 등 2024의 근역 지점, 제1권 4.7절)')
for r in (15.0, 30.0):
    la, lo = T.destination(vent[0], vent[1], 90.0, r)
    back = float(T.hav(vent[0], vent[1], la, lo))
    print('  %4.0f km 동쪽: %.5f N, %.5f E, 되돌려 잰 거리 %.4f km' % (r, la, lo, back))
la, lo = T.destination(vent[0], vent[1], res['sites']['스이게쓰호']['b'], res['sites']['스이게쓰호']['d'])
print('  분출구에서 스이게쓰호 방위·거리로 가서 닿는 점: %.5f N, %.5f E (스이게쓰호 좌표 %.5f N, %.5f E)' % (la, lo, *S['스이게쓰호']))
# 왕복 오차 조사
rt = []
for k, (la0, lo0) in S.items():
    d = float(T.hav(vent[0], vent[1], la0, lo0)); b = float(T.bearing(vent[0], vent[1], la0, lo0))
    la1, lo1 = T.destination(vent[0], vent[1], b, d)
    rt.append(float(T.hav(la0, lo0, la1, lo1)))
print('  네 지점 왕복(거리·방위 → 목적지) 오차(km): ' + ', '.join('%.2e' % v for v in rt))
res['roundtrip_km'] = rt

print('\n[실습 9-14c] 방위 서술 점검(제1권 4.11.0): 백두산에서 스이게쓰호로 가는 방위는 남동(SE)인가 남남동(SSE)인가')
b = res['sites']['스이게쓰호']['b']
print('  계산 방위 %.1f도. 16방위에서 SSE는 157.5도, SE는 135도. SSE와의 차이 %.1f도, SE와의 차이 %.1f도' % (b, abs(b - 157.5), abs(b - 135)))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'ex5.json'), 'w'), default=float)
print('\n결과 저장: results/ex5.json')
