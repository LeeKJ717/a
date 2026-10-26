# -*- coding: utf-8 -*-
"""실습 14-6: 제1권이 좌표를 적은 곳을 DB 에 적재하고, 제1권 계산의 숫자를 DB 의 후보 좌표로 다시 구해 대조한다.
대조 대상: 4.7절 개성 465.6 km 와 방위 197도, 10장 계산 10-11 의 거리 17개, 14장 계산 14-14 의 대구 두 읽기, 13장 이카와즈-도시 거리 11개,
5장 계산 5-15 의 구간 겹침 25칸, 9장·10장의 방향 서술 변위(HZ-WZ, 모산), 표기 반올림. 제1권 숫자는 원고에서 옮긴 것이다(행은 장 이름으로 적는다)."""
import os, sys, time, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placekit as P, vol1load as V
K = P.K

t0 = time.time()
con = P.connect(os.path.join(P.HERE, 'out', 'vol1.db'), fresh=True)
V.load_ch04(con); V.load_ch04_danju(con); V.load_ch09(con); V.load_ch11(con)
he = dict(V.load_he2015(con)); pk = V.load_peak_and_kaesong(con); dg = V.load_daegu(con); V.load_eras_ch05(con)
con.commit()
run = P.log_run(con, 'p06-vol1-checks-v1.py', '제1권 숫자 대조')
res = {}

def C(cid):
    r = con.execute('SELECT lon, lat FROM candidate WHERE cand_id=?', (cid,)).fetchone()
    return (r['lon'], r['lat'])

def show_row(name, expected, got, tol, unit='km', extra=''):
    ok = abs(expected - got) <= tol
    print('  %-26s 제1권 %8.1f  이번 %9.3f  차 %+7.3f %s %s' % (name, expected, got, got - expected, '맞음' if ok else '어긋남', extra))
    return ok

print('[A] 4.7절: 백두산(Lee 등 좌표)에서 개성(시연값 좌표)까지')
a, b = C(pk['peak_lee']), C(pk['kaesong'])
hv, ge, az = P.hav(a, b), P.km(a, b), P.bearing(a, b)
print('  하버사인 %.3f km, 타원체 측지선 %.3f km, 출발 방위 %.1f도(%s)' % (hv, ge, az, P.dir8(az)))
print('  제1권: 465.6 km, 197도. Yun 등(2023): 465 km')
v, out = P.check_relation(con, pk['rel'])
print('  관계 점검(서술 465±0.5 km, 후보 반경 합 %.2f km 를 허용에 더함): %s, 거리 %.2f km' % (P.rounding_km('dec2') + V.DEFAULT_RADIUS['현'], v, out[0]['dist']))
print('  반경을 빼고 서술의 반올림 ±0.5 km 만 허용하면 |%.2f - 465| = %.2f km 이므로 %s' % (out[0]['dist'], abs(out[0]['dist'] - 465), '맞음' if abs(out[0]['dist'] - 465) <= 0.5 else '어긋남'))
res['A'] = dict(hav=round(hv, 3), geod=round(ge, 3), az=round(az, 1))
P.log_res(con, run, 'ch04 개성', '백두산-개성', v, 'hav %.3f geod %.3f az %.1f' % (hv, ge, az))

print('\n[B] 백두산의 두 좌표: 서로 다른 논문, 서로 다른 이름')
d2 = P.km(C(pk['peak_lee']), C(pk['peak_du']))
print('  Lee 등(2024) 정상 41.99N 128.08E 와 Du 등(2025) 시료 지점 41.98815N 128.00491E 사이 %.2f km' % d2)
print('  두 이름은 다르고(정상, 정상부 시료 지점) 반경은 표기 반올림 %.3f km 와 %.5f km 뿐이다 -> 같은 곳으로 합치는 근거가 이 DB 에 없다' % (P.rounding_km('dec2'), P.rounding_km('dec5')))
res['B'] = dict(km=round(d2, 3))

print('\n[C] 10장 계산 10-11: He 등(2015) 시료 사이 거리(하버사인 R=6371.0088 km 와 타원체 측지선)')
exp = [('의빈 1', '민강 1', 0.0), ('의빈 1', '의빈 2', 130.4), ('의빈 1', '대도하', 7.8), ('반지화 1', '반지화 2', 32.8), ('반지화 1', '아롱강', 38.4),
       ('부릉 1', '부릉 2', 5.6), ('부릉 1', '오강', 14.7), ('파동', '의창', 115.0), ('악양 1', '악양 2', 27.1), ('무한 1', '무한 2', 28.1),
       ('무한 1', '한수', 78.2), ('구강', '호구', 38.9), ('호구', '남경', 349.3), ('남경', '장흥도', 323.0), ('중경 1', '가릉강', 18.2),
       ('가릉강', '중경 2', 14.7), ('중경 1', '중경 2', 28.1)]
cid = dict(he)
nok = 0; rows = []
for x, y, e in exp:
    h = P.hav(C(cid[x]), C(cid[y])); g = P.km(C(cid[x]), C(cid[y]))
    ok = abs(h - e) <= 0.05
    nok += ok
    rows.append((x, y, e, round(h, 3), round(g, 3)))
    print('  %-8s - %-8s 제1권 %6.1f  하버사인 %8.3f  측지선 %8.3f  하버-제1권 %+6.3f %s' % (x, y, e, h, g, h - e, '맞음' if ok else '어긋남'))
print('  17개 가운데 하버사인이 제1권 값(소수 첫째 자리)과 0.05 km 이내로 맞는 것 %d개' % nok)
mg = max(abs(r[3] - r[4]) / max(r[3], 1e-9) for r in rows if r[3] > 1)
print('  하버사인과 측지선의 차는 최대 %.2f%% (1 km 이상 거리만)' % (mg * 100))
res['C'] = dict(ok=nok, n=len(exp), rows=rows)
P.log_res(con, run, 'ch10 계산 10-11', '17쌍', '%d/%d 맞음' % (nok, len(exp)))

print('\n[D] 같은 이름의 후보 사이 거리(후보 퍼짐), 같은 좌표의 다른 이름')
for nm, era, n, pr, d in P.candidate_spread(con):
    print('  %-6s %-4s 후보 %d개: %s - %s  %.1f km' % (nm, era, n, pr[0], pr[1], d))
for x in P.same_coordinate_diff_name(con):
    print('  같은 좌표 다른 이름: %s(%s) = %s(%s)  %.3f km' % x)
    P.log_res(con, run, 'same-coord', '%s/%s' % (x[0], x[2]), '이름과 좌표 불일치 의심', '%.3f km' % x[4])

print('\n[E] 도분초 읽기: 표기 오류와 모호한 표기')
for s in ['112° 55′ 7.60′', '31° 11′ 16.00′', '104° 41′ 26.40″', '128°60′E', '35°52′N']:
    v, w, alts = P.parse_dms(s.replace(' ', ''))
    print('  %-18s -> %.5f  경고 %s  다른 읽기 %s' % (s, v, w or '-', [(round(a, 4), t) for a, t in alts] or '-'))
sa, sb = C(dg['seoul']), C(dg['daegu_a'])
sc = C(dg['daegu_b'])
d_a, d_b = P.hav(sa, sb), P.hav(sa, sc)
d_ab = P.hav(sb, sc)
print('  서울까지 거리: 129.00E 읽기 %.1f km, 128.60E 읽기 %.1f km (제1권 14.10절: 261.9, 238.7)' % (d_a, d_b))
print('  두 거리의 차 %.1f km. 두 읽기가 가리키는 두 점 사이의 거리 %.1f km (제1권은 "두 읽기의 차는 36.0 km"라 썼다)' % (d_a - d_b, d_ab))
print('  -> 제1권의 36.0 km 는 서울까지 거리의 차가 아니라 두 후보 점 사이의 거리이다. 숫자는 맞고 문장이 모호하다.')
res['E'] = dict(a=round(d_a, 1), b=round(d_b, 1), diff=round(d_a - d_b, 1), between=round(d_ab, 1))
print('  DB 의 대구: 채택 후보 1개, 기각 후보 1개. cands_of() 는 기각을 빼고 include_rejected=True 면 둘 다 낸다:',
      len(P.cands_of(con, con.execute("SELECT ne_id FROM name_era JOIN name USING(name_id) WHERE name_ko='대구'").fetchone()[0])), '/',
      len(P.cands_of(con, con.execute("SELECT ne_id FROM name_era JOIN name USING(name_id) WHERE name_ko='대구'").fetchone()[0], True)))

print('\n[F] 13장 이카와즈(논문 좌표 34°38′43″N, 137°8′52″E)에서 현대 도시까지(Natural Earth 도시 위치, 하버사인)')
lo, w, _ = P.parse_dms('137°8′52″E'); la, w2, _ = P.parse_dms('34°38′43″N')
ne_city = {'하마마쓰': 'Hamamatsu', '나고야': 'Nagoya', '오사카': 'Ōsaka', '도쿄': 'Tokyo', '후쿠시마': 'Fukushima', '이와키': 'Iwaki', '센다이': 'Sendai',
           '후쿠오카': 'Fukuoka', '나가사키': 'Nagasaki', '사세보': 'Sasebo', '삿포로': 'Sapporo'}
exp13 = {'하마마쓰': 54.1, '나고야': 60.8, '오사카': 150.4, '도쿄': 263.3, '후쿠시마': 455.2, '이와키': 430.7, '센다이': 522.5, '후쿠오카': 631.1, '나가사키': 703.4, '사세보': 705.1, '삿포로': 1005.0}
pp = K.read('ne_10m_populated_places_simple', (125, 30, 146, 46))
nok13 = 0; r13 = []
for ko, en in ne_city.items():
    rows_ = pp[pp['name'] == en]
    if len(rows_) != 1:
        print('  %s: Natural Earth 에서 %d개 찾음 -> 건너뜀' % (ko, len(rows_))); continue
    pt = rows_.geometry.iloc[0]
    d = P.hav((lo, la), (pt.x, pt.y))
    ok = abs(d - exp13[ko]) <= 0.15
    nok13 += ok
    r13.append((ko, exp13[ko], round(d, 1), round(pt.x, 4), round(pt.y, 4)))
    print('  이카와즈 ~ %-5s 제1권 %7.1f  이번 %8.1f  차 %+6.1f %s  (NE 좌표 %.4f, %.4f)' % (ko, exp13[ko], d, d - exp13[ko], '맞음' if ok else '어긋남', pt.x, pt.y))
print('  %d / %d 개가 제1권 값과 0.15 km 이내' % (nok13, len(ne_city)))
res['F'] = dict(ok=nok13, rows=r13)

print('\n[G] 5장 계산 5-15: 시대 창(Park 등 2017, Zhou 등 2011)의 겹침 — era 표에서 SQL 로')
q = '''SELECT a.label AS a, b.label AS b, MAX(0, MIN(a.t1, b.t1) - MAX(a.t0, b.t0)) AS ov
       FROM era a JOIN era b ON a.defined_by LIKE 'Park%' AND b.defined_by LIKE 'Zhou%' ORDER BY a.t0, a.label, b.era_id'''
tab = {}
for r in con.execute(q):
    tab.setdefault(r['a'], []).append(r['ov'])
exp5 = {'제주 D1 건조': [0, 0, 80, 80, 0], '제주 D2 건조': [0, 0, 120, 50, 0], '제주 D3 건조': [0, 60 + 0, 0, 0, 90], '제주 D4 건조': [0, 0, 0, 0, 0], '제주 W 습윤': [105, 50, 0, 0, 80]}
# 제1권 표 열 순서: 약한(1420~1625), 최저(1450~1570), 강한(1000~1300), 최고(1000~1230), 남중국(1400~1600). D3 의 약한 몬순 겹침은 90, 최저는 60
exp5['제주 D3 건조'] = [90, 60, 0, 0, 90]
print('  열 순서: 약한 몬순, 최저 몬순, 강한 몬순, 최고 몬순, 남중국 홍수 많음')
n5 = 0
for k in ['제주 D1 건조', '제주 D2 건조', '제주 D3 건조', '제주 D4 건조', '제주 W 습윤']:
    got = tab[k]
    # era 행은 era_id 순으로 약한, 최저, 강한, 최고, 남중국
    ok = got == exp5[k]; n5 += sum(1 for x, y in zip(got, exp5[k]) if x == y)
    print('  %-10s 이번 %-24s 제1권 %-24s %s' % (k, got, exp5[k], '모두 맞음' if ok else '어긋남'))
print('  25칸 가운데 같은 칸 %d개' % n5)
res['G'] = dict(same=n5)

print('\n[H] 방향·거리 서술을 좌표로 옮기기(제1권 9.7절 HZ-WZ, 10.9절 모산)')
A = (126.0, 36.0)       # 경도는 시연값. 제1권 9.7절은 위도 36도만 가정했다
planar_dlat = 40 * math.cos(math.radians(45)) / 111.195
planar_dlon = 40 * math.sin(math.radians(45)) / (111.195 * math.cos(math.radians(36)))
B = P.dest(A, 45.0, 40.0)
print('  북동(45도) 40 km, 위도 36도: 제1권 평면 근사 Δ위도 %.4f, Δ경도 %.4f' % (planar_dlat, planar_dlon))
print('    타원체 측지선으로 옮긴 이번 값 Δ위도 %.4f, Δ경도 %.4f (거리 되짚기 %.3f km, 방위 %.2f도)' % (B[1] - A[1], B[0] - A[0], P.km(A, B), P.bearing(A, B)))
A2 = (120.0, 30.0)
pl2 = 20 / (111.195 * math.cos(math.radians(30)))
B2 = P.dest(A2, 90.0, 20.0)
print('  동쪽 20 km, 위도 30도: 제1권 Δ경도 %.4f, 이번 측지선 Δ경도 %.4f, Δ위도 %.5f' % (pl2, B2[0] - A2[0], B2[1] - A2[1]))
print('  8방위 서술의 허용: 북동 = 45 +- 22.5도. 방위 %.1f도는 %s 이고, 동쪽(90도)과의 방위 차는 %.1f도라 %s' % (45.0, P.dir8(45.0), P.angdiff(45, 90), '허용 안' if P.angdiff(45, 90) <= 22.5 else '허용 밖'))
res['H'] = dict(planar=(round(planar_dlat, 4), round(planar_dlon, 4)), geod=(round(B[1] - A[1], 4), round(B[0] - A[0], 4)), east=(round(pl2, 4), round(B2[0] - A2[0], 4)))

print('\n[I] 표기 반올림(제1권 11장·12장·13장): 단위의 절반이 위도 방향 몇 km 인가')
for u, v1 in [('min', '12장: ±0.93 km'), ('sec', '13장: ±15 m'), ('dec2', '12장: 0.01도는 1.11 km, 절반 0.56')]:
    print('  %-5s 이번 %.4f km (%.1f m)  제1권 %s' % (u, P.rounding_km(u), P.rounding_km(u) * 1000, v1))
print('\n[J] 현대 도시 위치와 시료 좌표(Natural Earth 도시 위치, 하버사인). 도시 위치는 시료 위치가 아니다')
pp2 = K.read('ne_10m_populated_places_simple', (102, 27, 106, 31))
cityp = {}
for ko, en in (('의빈시', 'Yibin'), ('낙산시', 'Leshan')):
    r = pp2[pp2['name'] == en].iloc[0]; cityp[ko] = (r.longitude, r.latitude)
resJ = {}
for lab in ('의빈 1', '민강 1', '대도하', '의빈 2'):
    row = []
    for ko, pt in cityp.items():
        d = P.hav(C(cid[lab]), pt); row.append((ko, round(d, 1)))
    resJ[lab] = row
    print('  시료 %-6s 에서 %s' % (lab, ', '.join('%s %.1f km' % x for x in row)))
print('  관찰: 시료 이름은 의빈인데 의빈 1 의 좌표는 의빈시 위치에서 멀고 낙산시 쪽에 가깝다. 어느 쪽이 틀렸는지는 이 책이 정하지 못한다(제1권 10.9절과 같다).')
res['J'] = resJ
con.commit()
json.dump(res, open(os.path.join(P.HERE, 'p06-vol1-checks.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n걸린 시간 %.2f초' % (time.time() - t0))
