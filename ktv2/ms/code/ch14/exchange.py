# -*- coding: utf-8 -*-
"""exchange: 다른 책(동아시아 고전 지명 추정서)과 주고받는 CSV 내보내기·가져오기.
이쪽 DB 의 뷰 v_geonames 가 지명, 시대, 후보, 근거등급 네 열을 그대로 낸다. 가져올 때는 시대의 숫자 창(시작, 끝 연도)을 따로 받는다.
다른 책의 실제 DB 파일은 이 컨테이너에 없어 그쪽 열 이름과 값 집합은 확인하지 못했다. 네 열 이름만 지시문에서 옮겼다."""
import csv, os
import placekit as P

GEO_HEAD = ['지명', '시대', '후보', '근거등급', '경도', '위도', '반경km', '좌표출처', '층위', '신고등급']
EV_HEAD = ['지명', '시대', '후보', '증거종류', '독립출처', '지지반대', '출처']
ERA_HEAD = ['시대', '시작', '끝', '정의한 곳']


def export(con, outdir, tag):
    os.makedirs(outdir, exist_ok=True)
    g = os.path.join(outdir, tag + '-geonames.csv'); e = os.path.join(outdir, tag + '-evidence.csv'); a = os.path.join(outdir, tag + '-eras.csv')
    with open(g, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(GEO_HEAD)
        for r in con.execute('''SELECT n.name_ko, er.label, COALESCE(c.modern_name,''), COALESCE(gr.grade_computed,'가설'), c.lon, c.lat, c.radius_km, COALESCE(c.coord_origin,'없음'), n.layer, c.grade_claimed
                                FROM name_era ne JOIN name n USING(name_id) JOIN era er USING(era_id) LEFT JOIN candidate c ON c.ne_id=ne.ne_id
                                LEFT JOIN v_cand_grade gr ON gr.cand_id=c.cand_id ORDER BY n.name_ko, er.t0, c.cand_id'''):
            w.writerow(['' if x is None else x for x in r])
    with open(e, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(EV_HEAD)
        for r in con.execute('''SELECT n.name_ko, er.label, c.modern_name, ev.ev_type, ev.indep_group, ev.support, ev.source_ref FROM evidence ev JOIN candidate c USING(cand_id)
                                JOIN name_era ne ON ne.ne_id=c.ne_id JOIN name n USING(name_id) JOIN era er USING(era_id) ORDER BY ev.ev_id'''):
            w.writerow(['' if x is None else x for x in r])
    with open(a, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(ERA_HEAD)
        for r in con.execute('SELECT label, t0, t1, defined_by FROM era ORDER BY era_id'):
            w.writerow(list(r))
    return g, e, a


class ImportError_(Exception):
    pass


def import_csv(con, geo_path, era_path=None, ev_path=None, default_layer='옛지명', is_demo=0):
    """geo_path 는 최소 네 열(지명, 시대, 후보, 근거등급)이 있어야 한다. 근거등급은 '신고등급'으로 들어가고, 계산 등급은 증거에서 다시 구한다.
    era_path 가 없으면 시대 창을 알 수 없어 오류를 낸다(시대 창을 지어내지 않는다)."""
    rows = list(csv.DictReader(open(geo_path, encoding='utf-8')))
    for col in ('지명', '시대', '후보', '근거등급'):
        if col not in rows[0]:
            raise ImportError_('열 "%s" 이(가) 없다' % col)
    eras = {}
    if era_path:
        for r in csv.DictReader(open(era_path, encoding='utf-8')):
            eras[r['시대']] = (int(r['시작']), int(r['끝']), r['정의한 곳'])
    stats = dict(rows=0, names=0, cands=0)
    seen = set()
    for r in rows:
        if r['시대'] not in eras:
            raise ImportError_('시대 "%s" 의 숫자 창(시작, 끝)을 모른다. 시대 목록 파일이 필요하다' % r['시대'])
        t0, t1, by = eras[r['시대']]
        ei = P.add_era(con, r['시대'], t0, t1, by)
        ni = P.add_name(con, r['지명'], r.get('층위') or default_layer, None, is_demo)
        nei = P.add_ne(con, ni, ei)
        stats['rows'] += 1
        if r['후보'] in ('', '(후보 없음)'):
            continue
        lon = float(r['경도']) if r.get('경도') not in (None, '') else None
        lat = float(r['위도']) if r.get('위도') not in (None, '') else None
        rad = float(r['반경km']) if r.get('반경km') not in (None, '') else None
        claimed = r.get('신고등급') or r['근거등급']
        claimed = claimed if claimed in ('A', 'B', 'C', '가설') else None
        origin = r.get('좌표출처') or ('없음' if lon is None else '시연값')
        key = (r['지명'], r['시대'], r['후보'])
        if key in seen:
            continue
        seen.add(key)
        P.add_cand(con, nei, '점' if lon is not None else '미상', origin if lon is not None else '없음', r['후보'], lon, lat, rad if lon is not None else None,
                   '가져옴: ' + os.path.basename(geo_path), None, claimed, is_demo=is_demo)
        stats['cands'] += 1
    if ev_path:
        for r in csv.DictReader(open(ev_path, encoding='utf-8')):
            cid = P.one(con, '''SELECT c.cand_id FROM candidate c JOIN name_era ne USING(ne_id) JOIN name n USING(name_id) JOIN era er USING(era_id)
                                WHERE n.name_ko=? AND er.label=? AND c.modern_name=?''', r['지명'], r['시대'], r['후보'])
            if cid is not None:
                P.add_ev(con, cid, r['증거종류'], r['독립출처'], r['지지반대'], r['출처'])
    con.commit()
    return stats
