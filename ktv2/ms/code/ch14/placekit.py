# -*- coding: utf-8 -*-
"""placekit v1 - 제2권 14장 실습 공용 도우미: DB 만들기, 적재, 인용 점검, 도분초 읽기, 위상 추정 검사.
파일 이름에 밑줄을 쓰지 않으려고 모듈 이름은 placekit 이다. 거리 계산은 1장의 mapkit 을 그대로 쓴다.
이 모듈은 사료 구절을 만들지 않는다. 구절은 호출하는 쪽이 넘겨준 것만 DB 에 들어간다."""
import os, re, sys, math, json, sqlite3, hashlib, itertools, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ch01'))
import mapkit as K                       # 1장: haversine, geodesic_km, GEOD

SCHEMA = os.path.join(HERE, 'schema-v1.sql')


# ------------------------------------------------------------------ DB
def connect(path=':memory:', fresh=False):
    if fresh and path != ':memory:' and os.path.exists(path):
        os.remove(path)
    new = path == ':memory:' or not os.path.exists(path)
    con = sqlite3.connect(path)
    con.execute('PRAGMA foreign_keys = ON')
    con.row_factory = sqlite3.Row
    if new:
        con.executescript(open(SCHEMA, encoding='utf-8').read())
        con.commit()
    return con


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def one(con, sql, *a):
    r = con.execute(sql, a).fetchone()
    return r[0] if r else None


def get_or_add(con, table, keycols, row):
    """keycols 가 같은 행이 있으면 그 id, 없으면 넣고 id. NULL 도 같은 값으로 비교한다(IS)."""
    where = ' AND '.join('%s IS ?' % k for k in keycols)
    idcol = {'name_era': 'ne_id', 'attestation': 'att_id'}.get(table, table + '_id')
    r = con.execute('SELECT %s FROM %s WHERE %s' % (idcol, table, where), [row.get(k) for k in keycols]).fetchone()
    if r:
        return r[0]
    cols = list(row)
    cur = con.execute('INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(cols), ','.join('?' * len(cols))), [row[c] for c in cols])
    return cur.lastrowid


def add_work(con, title_ko, title_orig=None, kind='기타', note=None, is_demo=0):
    return get_or_add(con, 'work', ['title_ko', 'title_orig'], dict(title_ko=title_ko, title_orig=title_orig, kind=kind, note=note, is_demo=is_demo))


def add_edition(con, work_id, label, how_seen, holder=None, note=None, is_demo=0):
    return get_or_add(con, 'edition', ['work_id', 'label'], dict(work_id=work_id, label=label, how_seen=how_seen, holder=holder, note=note, is_demo=is_demo))


def add_section(con, work_id, juan=None, pyeon=None):
    return get_or_add(con, 'section', ['work_id', 'juan', 'pyeon'], dict(work_id=work_id, juan=juan, pyeon=pyeon))


def add_passage(con, section_id, edition_id, status, text=None, paraphrase=None, date_text=None, year_from=None, year_to=None,
                secondary_source=None, locator=None, collation='교감전', collation_note=None, is_demo=0):
    cur = con.execute(
        'INSERT INTO passage (section_id,edition_id,date_text,year_from,year_to,text,text_sha256,paraphrase,status,secondary_source,locator,collation,collation_note,is_demo)'
        ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (section_id, edition_id, date_text, year_from, year_to, text, sha(text) if text is not None else None, paraphrase, status,
         secondary_source, locator, collation, collation_note, is_demo))
    return cur.lastrowid


def add_era(con, label, t0, t1, defined_by):
    return get_or_add(con, 'era', ['label', 'defined_by'], dict(label=label, t0=t0, t1=t1, defined_by=defined_by))


def add_name(con, name_ko, layer, orig_form=None, is_demo=0):
    return get_or_add(con, 'name', ['name_ko', 'orig_form', 'layer'], dict(name_ko=name_ko, orig_form=orig_form, layer=layer, is_demo=is_demo))


def add_ne(con, name_id, era_id):
    return get_or_add(con, 'name_era', ['name_id', 'era_id'], dict(name_id=name_id, era_id=era_id))


def add_att(con, ne_id, passage_id, note=None):
    return get_or_add(con, 'attestation', ['ne_id', 'passage_id'], dict(ne_id=ne_id, passage_id=passage_id, note=note))


def add_cand(con, ne_id, level, coord_origin, modern_name=None, lon=None, lat=None, radius_km=None, coord_ref=None, coord_note=None,
             grade_claimed=None, status='후보', valid_from=None, valid_to=None, is_demo=0):
    cur = con.execute(
        'INSERT INTO candidate (ne_id,modern_name,lon,lat,radius_km,level,coord_origin,coord_ref,coord_note,valid_from,valid_to,grade_claimed,status,is_demo)'
        ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (ne_id, modern_name, lon, lat, radius_km, level, coord_origin, coord_ref, coord_note, valid_from, valid_to, grade_claimed, status, is_demo))
    return cur.lastrowid


def add_ev(con, cand_id, ev_type, indep_group, support, source_ref, passage_id=None, note=None):
    cur = con.execute('INSERT INTO evidence (cand_id,ev_type,indep_group,support,passage_id,source_ref,note) VALUES (?,?,?,?,?,?,?)',
                      (cand_id, ev_type, indep_group, support, passage_id, source_ref, note))
    return cur.lastrowid


def add_rel(con, passage_id, source_ref, ne_a, ne_b, kind, bearing_deg=None, bearing_tol=None, dist_km=None, dist_tol_km=None, variant_id=None, note=None):
    cur = con.execute('INSERT INTO relation (passage_id,source_ref,variant_id,ne_a,ne_b,kind,bearing_deg,bearing_tol,dist_km,dist_tol_km,note) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                      (passage_id, source_ref, variant_id, ne_a, ne_b, kind, bearing_deg, bearing_tol, dist_km, dist_tol_km, note))
    return cur.lastrowid


# ------------------------------------------------------------------ 인용: DB 에 넣은 것만 인용한다
def cite(con, passage_id):
    """구절 한 건을 인용문으로 돌려준다. 원문(text)이 DB 에 없으면 원문을 돌려주지 않고 그렇다고 말한다.
    상태가 '재인용', '시연', '입력미대조'면 꼬리표를 앞에 붙인다. 없는 id 는 오류."""
    r = con.execute('SELECT p.*, w.title_ko, s.juan, s.pyeon, e.label AS ed, e.how_seen FROM passage p JOIN section s USING(section_id) '
                    'JOIN work w ON w.work_id=s.work_id JOIN edition e ON e.edition_id=p.edition_id WHERE p.passage_id=?', (passage_id,)).fetchone()
    if r is None:
        raise KeyError('passage_id %s 는 DB 에 없다. 기억에서 인용하지 않는다' % passage_id)
    where = r['title_ko'] + (' ' + r['juan'] if r['juan'] else '') + (' ' + r['pyeon'] if r['pyeon'] else '')
    tag = {'원문대조': '', '입력미대조': '[입력 후 미대조] ', '재인용': '[재인용: %s] ' % r['secondary_source'], '시연': '[가상 시연 구절] '}[r['status']]
    if r['text'] is None:
        return '%s(%s, %s) 원문은 DB 에 없다. 서술만 있다: %s' % (tag, where, r['ed'], r['paraphrase'])
    return '%s%s (%s, %s; 교감 %s)' % (tag, r['text'], where, r['ed'], r['collation'])


def norm(s):
    return re.sub(r'\s+', '', s)


def quote_audit(con, quote):
    """원고에 따옴표로 넣으려는 구절이 DB 의 원문에 글자 그대로 들어 있는가. 들어 있는 passage_id 목록(없으면 빈 목록)."""
    q = norm(quote)
    if len(q) < 2:
        return []
    return [r[0] for r in con.execute('SELECT passage_id, text FROM passage WHERE text IS NOT NULL') if q in norm(r[1])]


def verify_hashes(con):
    bad = [r[0] for r in con.execute('SELECT passage_id, text, text_sha256 FROM passage WHERE text IS NOT NULL') if sha(r[1]) != r[2]]
    return bad


# ------------------------------------------------------------------ 좌표 읽기와 기하
_DMS = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*°\s*(?:(\d+(?:\.\d+)?)\s*[′'’]\s*)?(?:(\d+(?:\.\d+)?)\s*(″|′′|''|\"|′|’)\s*)?\s*([NSEW])?\s*$")


def parse_dms(s):
    """도분초 문자열을 십진도로. 반환: (값, 경고 목록, 다른 읽기 목록).
    경고: '분이 60 이상', '초 기호가 분 기호(′)로 적힘'. 다른 읽기: 모호한 표기를 달리 읽은 값들(값, 설명)."""
    m = _DMS.match(s)
    if not m:
        raise ValueError('도분초로 읽지 못함: %r' % s)
    d, mi, se, mark, hemi = m.groups()
    d = float(d); mi = float(mi) if mi else 0.0; se = float(se) if se else 0.0
    warns, alts = [], []
    if mi >= 60:
        warns.append('분이 60 이상(%g′)' % mi)
        alts.append((d + mi / 60 + se / 3600, '60′ 를 1° 로 올려 읽기'))
        alts.append((d + (mi / 100), '분 자리를 십진 소수로 읽기'))
    if mark in ("′", "’") and se:
        warns.append('초 기호가 분 기호로 적힘: 초로 읽었다')
    val = d + mi / 60 + se / 3600
    if hemi in ('S', 'W'):
        val = -val
    return val, warns, alts


def rounding_km(unit):
    """표기 단위의 절반이 위도 방향으로 몇 km 인가. unit: 'deg','min','sec' 또는 십진 자리 수 'dec2' 같은 것."""
    half_deg = {'deg': 0.5, 'min': 0.5 / 60, 'sec': 0.5 / 3600}.get(unit)
    if half_deg is None and unit.startswith('dec'):
        half_deg = 0.5 * 10 ** (-int(unit[3:]))
    return half_deg * 111.195


def km(a, b):
    """두 점 (lon, lat) 사이 WGS84 측지선 거리(km). 1장 mapkit."""
    return K.geodesic_km(a[0], a[1], b[0], b[1])


def hav(a, b):
    return K.haversine(a[0], a[1], b[0], b[1])


def bearing(a, b):
    """a 에서 b 를 본 초기 방위(도, 북 0 시계 방향)."""
    az, _, _ = K.GEOD.inv(a[0], a[1], b[0], b[1])
    return az % 360


def dest(a, az, dist_km):
    lo, la, _ = K.GEOD.fwd(a[0], a[1], az, dist_km * 1000.0)
    return (lo, la)


DIR8 = ['북', '북동', '동', '남동', '남', '남서', '서', '북서']
DIR8_DEG = {n: i * 45.0 for i, n in enumerate(DIR8)}


def dir8(az):
    return DIR8[int(((az % 360) + 22.5) // 45) % 8]


def angdiff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def overlap(a0, a1, b0, b1):
    """두 구간의 겹침 길이(제1권 계산 5-15). 겹치지 않으면 0."""
    return max(0, min(a1, b1) - max(a0, b0))


# ------------------------------------------------------------------ 위상 추정 검사
def cands_of(con, ne_id, include_rejected=False):
    q = ('SELECT c.*, g.grade_computed, g.rank_computed FROM candidate c JOIN v_cand_grade g USING(cand_id) WHERE c.ne_id=?'
         + ('' if include_rejected else " AND c.status<>'기각'"))
    return [dict(r) for r in con.execute(q, (ne_id,))]


def pair_verdict(ca, cb):
    """두 (이름, 시대)의 후보 목록 ca, cb 가 같은 땅을 가리킬 수 있는가.
    확인 후보 = 좌표가 있고 등급이 가설이 아닌 후보(계산 등급 순위 1 이상). 판정은 확인 후보끼리만 낸다.
      '판정 불가'  : 한쪽에 좌표 있는 후보가 아예 없다 (좌표 없으면 찍지 않는다)
      '겹침'       : 확인 후보 쌍 가운데 거리 <= 반경 합인 쌍이 있다 (같은 곳일 수 있다)
      '분리'       : 확인 후보끼리 모든 쌍이 반경 합보다 멀다
      '겹침(가설)' / '분리(가설)' : 한쪽에 확인 후보가 없어 가설 후보까지 넣고 낸 판정. 참고용이며 묶음에 쓰지 않는다
    확인 후보끼리는 '분리'인데 가설 후보를 넣으면 겹치는 경우는 설명에 적는다. 같은 이름이라는 사실은 어느 판정도 바꾸지 않는다.
    반환: (판정, 설명, 가장 가까운 쌍의 거리 km, 틈 km)"""
    pa = [c for c in ca if c['lon'] is not None]
    pb = [c for c in cb if c['lon'] is not None]
    if not pa or not pb:
        return '판정 불가', '좌표가 있는 후보가 없는 쪽이 있다', None, None

    def closest(xs, ys):
        best = None
        for x, y in itertools.product(xs, ys):
            d = km((x['lon'], x['lat']), (y['lon'], y['lat']))
            gap = d - (x['radius_km'] + y['radius_km'])
            if best is None or gap < best[0]:
                best = (gap, d, x, y)
        return best
    sa = [c for c in pa if c['rank_computed'] >= 1]
    sb = [c for c in pb if c['rank_computed'] >= 1]
    if sa and sb:
        gap, d, x, y = closest(sa, sb)
        v = '겹침' if gap <= 0 else '분리'
        why = '가장 가까운 확인 후보 쌍 %.1f km, 반경 합 %.1f km' % (d, x['radius_km'] + y['radius_km'])
        if v == '분리':
            g2, d2, _, _ = closest(pa, pb)
            if g2 <= 0:
                why += ' (가설 후보까지 넣으면 %.1f km 로 겹친다)' % d2
        return v, why, d, gap
    gap, d, x, y = closest(pa, pb)
    return ('겹침(가설)' if gap <= 0 else '분리(가설)'), '확인 후보가 없는 쪽이 있어 가설 후보로 낸 판정: %.1f km, 반경 합 %.1f km' % (d, x['radius_km'] + y['radius_km']), d, gap


def referent_clusters(con, name_id):
    """한 이름의 시대들을 '같은 땅일 수 있는' 관계로 묶는다.
    반환: dict(eras=[(ne_id, era_label, t0)...시간순], pairs=[(i, j, 판정, 설명, 거리, 틈)], clusters=[[era_label,...]], chain_warnings=[...])
    묶음은 '겹침' 관계의 연결 성분이다. 겹침은 이행적이지 않으므로(가 나와 겹치고 나가 다와 겹쳐도 가와 다는 떨어질 수 있다)
    성분 안에 '분리' 쌍이 있으면 사슬 경고를 낸다."""
    rows = con.execute('SELECT ne.ne_id, e.label, e.t0 FROM name_era ne JOIN era e USING(era_id) WHERE ne.name_id=? ORDER BY e.t0', (name_id,)).fetchall()
    eras = [(r[0], r[1], r[2]) for r in rows]
    cs = {ne: cands_of(con, ne) for ne, _, _ in eras}
    pairs = []
    parent = list(range(len(eras)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i, j in itertools.combinations(range(len(eras)), 2):
        v, why, d, gap = pair_verdict(cs[eras[i][0]], cs[eras[j][0]])
        pairs.append((i, j, v, why, d, gap))
        if v == '겹침':
            parent[find(i)] = find(j)
    comp = {}
    for i in range(len(eras)):
        comp.setdefault(find(i), []).append(i)
    clusters = [[eras[i][1] for i in idx] for idx in comp.values()]
    chain = []
    for idx in comp.values():
        for p in pairs:
            if p[0] in idx and p[1] in idx and p[2].startswith('분리'):
                chain.append('%s 와 %s 는 같은 묶음이지만 서로는 %s' % (eras[p[0]][1], eras[p[1]][1], p[2]))
    unresolved = [eras[i][1] for i in range(len(eras)) if not cs[eras[i][0]] or all(c['lon'] is None for c in cs[eras[i][0]])]
    return dict(eras=eras, pairs=pairs, clusters=clusters, chain_warnings=chain, no_point=unresolved)


def check_relation(con, rel_id):
    """글의 방향·거리 서술이 두 (이름, 시대)의 후보 좌표와 맞는가.
    후보 쌍마다 방위 차와 거리 차를 허용 오차와 견주어 '부합/위배'를 내고, 하나라도 부합하면 '부합 가능',
    모두 위배면 '위배', 좌표 있는 후보 쌍이 없으면 '판정 불가'."""
    r = con.execute('SELECT * FROM relation WHERE rel_id=?', (rel_id,)).fetchone()
    pa = [c for c in cands_of(con, r['ne_a']) if c['lon'] is not None]
    pb = [c for c in cands_of(con, r['ne_b']) if c['lon'] is not None]
    if not pa or not pb:
        return '판정 불가', []
    out = []
    for x, y in itertools.product(pa, pb):
        A, B = (x['lon'], x['lat']), (y['lon'], y['lat'])
        d = km(A, B); az = bearing(A, B)
        ok_d = ok_b = True
        if r['dist_km'] is not None:
            tol = (r['dist_tol_km'] or 0) + x['radius_km'] + y['radius_km']
            ok_d = abs(d - r['dist_km']) <= tol
        if r['bearing_deg'] is not None:
            # 방위 허용 오차에 후보의 불확실 반경이 만드는 각도 폭을 더한다(작은 각 근사: asin(반경 합 / 거리))
            slack = math.degrees(math.asin(min(1.0, (x['radius_km'] + y['radius_km']) / max(d, 1e-9))))
            ok_b = angdiff(az, r['bearing_deg']) <= r['bearing_tol'] + slack
        out.append(dict(a=x['cand_id'], b=y['cand_id'], dist=d, az=az, ok_dist=ok_d, ok_bearing=ok_b, ok=ok_d and ok_b))
    return ('부합 가능' if any(o['ok'] for o in out) else '위배'), out


def relation_by_reading(con, passage_id, ne_a, ne_b):
    """같은 구절의 관계가 이문(variant)마다 다르게 적혀 있으면 읽기별 판정을 모아, 판정이 갈리면 '교감 의존'을 낸다."""
    rels = con.execute('SELECT rel_id, variant_id FROM relation WHERE passage_id=? AND ne_a=? AND ne_b=?', (passage_id, ne_a, ne_b)).fetchall()
    res = {}
    for rid, vid in rels:
        res[vid if vid is not None else 0] = check_relation(con, rid)[0]
    kinds = set(res.values())
    return ('교감 의존' if len(kinds) > 1 else (kinds.pop() if kinds else '관계 없음')), res


def same_coordinate_diff_name(con, tol_km=0.05):
    """좌표가 같은(tol_km 이내) 서로 다른 이름의 후보 쌍. 제1권 10장의 의빈 1과 민강 1처럼 이름과 좌표가 어긋나는 곳을 찾는다."""
    rows = con.execute('SELECT c.cand_id, c.lon, c.lat, n.name_id, n.name_ko, e.label FROM candidate c JOIN name_era ne USING(ne_id) JOIN name n USING(name_id) '
                       'JOIN era e USING(era_id) WHERE c.lon IS NOT NULL AND c.status<>\'기각\'').fetchall()
    out = []
    for a, b in itertools.combinations(rows, 2):
        if a['name_id'] != b['name_id'] and km((a['lon'], a['lat']), (b['lon'], b['lat'])) <= tol_km:
            out.append((a['name_ko'], a['label'], b['name_ko'], b['label'], km((a['lon'], a['lat']), (b['lon'], b['lat']))))
    return out


def window_conflicts(con):
    """후보가 가리키는 시기(valid_from~valid_to)가 그 (이름, 시대)의 시대 창과 겹치지 않는 후보."""
    out = []
    for r in con.execute('SELECT c.cand_id, n.name_ko, e.label, e.t0, e.t1, c.valid_from, c.valid_to FROM candidate c JOIN name_era ne USING(ne_id) '
                         'JOIN name n USING(name_id) JOIN era e USING(era_id) WHERE c.valid_from IS NOT NULL AND c.valid_to IS NOT NULL'):
        if overlap(r['t0'], r['t1'], r['valid_from'], r['valid_to']) == 0:
            out.append(tuple(r))
    return out


def no_point_ne(con):
    """후보가 하나도 없거나 좌표 있는 후보가 없는 (이름, 시대). 지도에 찍지 않고 '좌표 없음'으로 남기는 목록."""
    return [tuple(r) for r in con.execute(
        "SELECT n.name_ko, e.label, ne.ne_id FROM name_era ne JOIN name n USING(name_id) JOIN era e USING(era_id) "
        "WHERE NOT EXISTS (SELECT 1 FROM candidate c WHERE c.ne_id=ne.ne_id AND c.lon IS NOT NULL AND c.status<>'기각') ORDER BY n.name_ko, e.t0")]


def log_run(con, tool, note=None):
    cur = con.execute('INSERT INTO check_run (tool, ran_at, note) VALUES (?,?,?)', (tool, datetime.datetime.now().isoformat(timespec='seconds'), note))
    return cur.lastrowid


def log_res(con, run_id, rule, subject, verdict, detail=None):
    con.execute('INSERT INTO check_result (run_id,rule,subject,verdict,detail) VALUES (?,?,?,?,?)', (run_id, rule, subject, verdict, detail))


def candidate_spread(con):
    """한 (이름, 시대)에 좌표 있는 후보가 둘 이상일 때, 후보 사이의 가장 먼 거리. 이름 하나로 한 점을 찍으면 이만큼 틀릴 수 있다.
    반환: [(이름, 시대, 후보 수, 가장 먼 쌍의 이름 둘, 거리 km)]"""
    out = []
    for r in con.execute("SELECT ne.ne_id, n.name_ko, e.label FROM name_era ne JOIN name n USING(name_id) JOIN era e USING(era_id)").fetchall():
        cs = [c for c in cands_of(con, r['ne_id'], include_rejected=True) if c['lon'] is not None]
        if len(cs) < 2:
            continue
        best = max(((km((a['lon'], a['lat']), (b['lon'], b['lat'])), a, b) for a, b in itertools.combinations(cs, 2)), key=lambda t: t[0])
        out.append((r['name_ko'], r['label'], len(cs), (best[1]['modern_name'], best[2]['modern_name']), best[0]))
    return out
