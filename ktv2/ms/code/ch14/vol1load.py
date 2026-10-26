# -*- coding: utf-8 -*-
"""vol1load: 제1권 원고(/home/claude/book/ms/chNN-v1.md)의 표에서 사료 재인용 행을 읽어 DB 에 '재인용'으로 적재한다.
구절은 제1권 원고에 적힌 글자를 그대로 옮긴다(이 모듈이 만들거나 고치지 않는다). 서명의 한글 독음과 편명의 독음만 이 책이 붙인다."""
import os, re
import placekit as P

VOL1 = os.environ.get('VOL1DIR', '/home/claude/book/ms')

READ = {'日本紀略': '일본기략', '高麗史': '고려사', '興福寺年代記': '흥복사연대기', '貞信公記': '정신공기', '太宗實錄': '태종실록', '宣祖實錄': '선조실록',
        '孝宗實錄': '효종실록', '顯宗改修實錄': '현종개수실록', '肅宗實錄': '숙종실록', '長白山江崗志略': '장백산강강지략',
        '左傳': '좌전', '史記': '사기', '後漢書': '후한서', '資治通鑑': '자치통감', '明史': '명사'}
PYEON = {'世家': '세가', '河渠書': '하거서', '王景傳': '왕경전', '河渠志': '하거지'}
# 제1권 4.6절이 밝힌 판본 정보(논문이 밝힌 것). 밝히지 않은 서명은 '판본 미특정'
EDITION = {'日本紀略': ('일본 국립국회도서관 디지털 컬렉션(논문이 밝힘)', '디지털 컬렉션'),
           '長白山江崗志略': ('길림성 도서관 소장본(논문이 밝힘)', '길림성 도서관')}
JOSEON = {'太宗實錄', '宣祖實錄', '孝宗實錄', '顯宗改修實錄', '肅宗實錄'}


def read_md(ch):
    return open(os.path.join(VOL1, 'ch%02d-v1.md' % ch), encoding='utf-8').read().split('\n')


def table_after(lines, marker):
    """marker 로 시작하는 {{T:...}} 줄 뒤의 마크다운 표를 (줄 번호, 칸 목록)으로 돌려준다. 머리 줄과 구분 줄은 뺀다."""
    start = next(i for i, l in enumerate(lines) if l.startswith('{{T:' + marker))
    rows, i = [], start + 1
    while i < len(lines) and not lines[i].startswith('|'):
        i += 1
    while i < len(lines) and lines[i].startswith('|'):
        rows.append((i + 1, [c.strip() for c in lines[i].strip().strip('|').split('|')]))
        i += 1
    return rows[2:]


def year_of(s):
    m = re.match(r'\D*(\d{3,4})', s)
    return int(m.group(1)) if m else None


def load_ch04(con):
    """4.6절 표(Yun 등 2023 의 사료 기록 13행)를 적재. 반환: passage_id 목록."""
    lines = read_md(4)
    rows = table_after(lines, 'Yun 등(2023)이 든 사료 기록')
    out = []
    for ln, c in rows:
        date_text, src, text, interp, limit = c
        m = re.match(r'^([^\s(]+)(?:\s+(권\d+))?(?:\((.*)\))?$', src)
        orig, juan, remark = m.group(1), m.group(2), m.group(3)
        pyeon = None
        if orig == '高麗史世家':
            orig, pyeon = '高麗史', '세가'
        w = P.add_work(con, READ[orig], orig, '실록' if orig in JOSEON else ('사서' if orig in ('日本紀略', '高麗史', '興福寺年代記', '貞信公記') else '지리지'),
                       '제1권 4.6절 표 경유. 서명 독음은 이 책이 붙임', 0)
        if orig in EDITION:
            ed = P.add_edition(con, w, EDITION[orig][0], '2차문헌인용', EDITION[orig][1], '이 책은 판본을 직접 열람하지 못했다. 구절은 Yun 등(2023) 인쇄본의 OCR 판독(제1권 표)', 0)
        else:
            ed = P.add_edition(con, w, '판본 미특정', '2차문헌인용', None, '논문이 밝힌 판본 정보를 제1권에서 이 서명에 연결하지 못했다. 구절은 Yun 등(2023) 인쇄본의 OCR 판독(제1권 표)', 0)
        sec = P.add_section(con, w, juan, pyeon)
        note = '제1권 표의 "원문 구절(OCR 판독)" 칸을 그대로 옮김. 직접 대조하지 못함' + ('; 서명 칸의 괄호 주: ' + remark if remark else '')
        pid = P.add_passage(con, sec, ed, '재인용', text=text, paraphrase=interp, date_text=date_text, year_from=year_of(date_text), year_to=year_of(date_text),
                            secondary_source='Yun et al. (2023) 인쇄본 OCR, 제1권 4.6절 표 경유', locator='제1권 ch04 원고 %d행' % ln,
                            collation='교감전', collation_note=note, is_demo=0)
        out.append(pid)
    return out


def load_ch04_danju(con):
    """4.7절 지명 표의 '단주' 행에 따옴표로 인용된 두 구절(1401년, 1406년)을 적재하고, 같은 이름의 두 시대로 등록한다. 좌표 후보는 없다."""
    lines = read_md(4)
    ln, row = next((i + 1, l) for i, l in enumerate(lines) if l.startswith('| 端州 |'))
    quotes = re.findall(r'(\d{4})년\s*["“]([^"”]+)["”]', row)
    w = P.add_work(con, '서명 미확인(단주 인용)', None, '기타', '제1권이 단주 구절의 서명을 적지 않았다', 0)
    ed = P.add_edition(con, w, '판본 미특정', '2차문헌인용', None, 'Yun 등(2023)을 인용한 제1권 4.7절 표', 0)
    sec = P.add_section(con, w, None, None)
    era = {}
    nm = P.add_name(con, '단주', '옛지명', '端州', 0)
    pids = []
    for yr, q in quotes:
        y = int(yr)
        pid = P.add_passage(con, sec, ed, '재인용', text=q, date_text='%d년' % y, year_from=y, year_to=y, secondary_source='Yun et al. (2023), 제1권 4.7절 표 경유',
                            locator='제1권 ch04 원고 %d행' % ln, collation='교감전', collation_note='서명·권·판본 모두 제1권에 없음', is_demo=0)
        e = P.add_era(con, '%d년' % y, y, y, '제1권 4.7절의 연도')
        n = P.add_ne(con, nm, e)
        P.add_att(con, n, pid, '제1권: 같은 이름이 두 해에 나온다. 같은 곳으로 합치는 근거를 확인하지 못했다')
        pids.append(pid)
    return pids


def load_ch09(con):
    lines = read_md(9)
    rows = table_after(lines, '9장 사료 목록')
    out = []
    for ln, c in rows:
        src, when, said, textcell, state = c
        m = re.match(r'^『(.+?)』(?:\s*「(.+?)」)?$', src)
        orig, pyeon = m.group(1), m.group(2)
        w = P.add_work(con, READ[orig], orig, '사서', '편찬 시기(Ma 등 2025 서술, 제1권 9.6절 표): ' + when, 0)
        ed = P.add_edition(con, w, '판본 미확인', '미확인', None, '제1권이 판본·권을 확인하지 못했다("확인 필요")', 0)
        sec = P.add_section(con, w, None, PYEON[pyeon] if pyeon else None)
        pid = P.add_passage(con, sec, ed, '재인용', text=None, paraphrase=said, secondary_source='Ma et al. (2025), 제1권 9.6절 표 경유',
                            locator='제1권 ch09 원고 %d행' % ln, collation='교감전', collation_note='원문 구절 없음(제1권 칸: "%s")' % textcell, is_demo=0)
        out.append(pid)
    return out


def load_ch11(con):
    lines = read_md(11)
    rows = table_after(lines, '11장 사료·학설의 재인용 목록')
    w = P.add_work(con, '서명 미확인(11장 표)', None, '기타', '제1권이 논문의 사료 서지를 확인하지 못했다', 0)
    ed = P.add_edition(con, w, '판본 미특정', '2차문헌인용', None, '제1권 11.7절 표', 0)
    sec = P.add_section(con, w, None, None)
    out = []
    for ln, c in rows:
        paper, said, checked, level = c
        who = re.sub(r'\s*\(.*', '', paper).replace('등', ' 등').strip()
        pid = P.add_passage(con, sec, ed, '재인용', text=None, paraphrase=said, secondary_source=paper + ', 제1권 11.7절 표 경유',
                            locator='제1권 ch11 원고 %d행' % ln, collation='교감전', collation_note='제1권이 확인한 것: ' + checked, is_demo=0)
        out.append(pid)
    return out


# ------------------------------------------------------------------ 지명 쪽: 제1권이 좌표를 적은 곳
def modern_era(con):
    return P.add_era(con, '현대', 1900, 2026, '14장 설정: 현대 지명과 현대 시료 지점은 1900~2026 으로 둔다(시연 설정)')


def load_he2015(con):
    """제1권 10장 표(He 등 2015 표 1의 시료 30곳)를 시료 지점으로 적재. 같은 이름의 번호 붙은 시료(의빈 1, 의빈 2)는 한 이름의 후보 둘로 둔다.
    도분초는 제1권 표기 그대로 읽고, 초 기호가 분 기호로 적힌 두 곳은 경고를 coord_note 에 남긴다."""
    lines = read_md(10)
    rows = table_after(lines, '10장 He 등(2015) 표 1의 시료 위치')
    era = modern_era(con)
    out = []
    for ln, c in rows:
        no, eng, ko, lo, la, when, kind = c
        lon, w1, _ = P.parse_dms(lo.replace(' ', ''))
        lat, w2, _ = P.parse_dms(la.replace(' ', ''))
        base = re.sub(r'\s*\d+$', '', ko)
        nm = P.add_name(con, base, '시료지점', None, 0)
        ne = P.add_ne(con, nm, era)
        note = '표기 %s, %s' % (lo, la) + ('; ' + '; '.join(w1 + w2) if (w1 or w2) else '')
        cid = P.add_cand(con, ne, '점', '논문본문', ko, lon, lat, P.rounding_km('sec'), 'He 등(2015) 표 1, 제1권 ch10 원고 %d행' % ln, note + '; 반경은 표기 반올림만(측량 오차 아님)',
                         'C', is_demo=0)
        P.add_ev(con, cid, '좌표', 'He2015', '지지', 'He 등(2015) 표 1(제1권 10장 경유)')
        out.append((ko, cid))
    return out


def load_peak_and_kaesong(con):
    """제1권 4장: 백두산 두 좌표(서로 다른 논문, 서로 다른 이름)와 개성(시연값 좌표)을 적재."""
    era = modern_era(con)
    e946 = P.add_era(con, '946년', 946, 946, '제1권 4.6절의 연도')
    n1 = P.add_name(con, '백두산 정상', '기관·지점', None, 0)
    n2 = P.add_name(con, '백두산 정상부 시료 지점', '시료지점', None, 0)
    c1 = P.add_cand(con, P.add_ne(con, n1, era), '점', '논문본문', '백두산 정상', 128.08, 41.99, P.rounding_km('dec2'), 'Lee 등(2024), 제1권 4.7절', '반경은 표기 반올림만', 'C')
    P.add_ev(con, c1, '좌표', 'Lee2024', '지지', 'Lee 등(2024)(제1권 4.7절 경유)')
    c2 = P.add_cand(con, P.add_ne(con, n2, era), '점', '논문본문', '백두산 정상부 시료 지점', 128.00491, 41.98815, P.rounding_km('dec5'), 'Du 등(2025), 제1권 4장 표', '반경은 표기 반올림만; 고도 약 2050 m(논문)', 'C')
    P.add_ev(con, c2, '좌표', 'Du2025', '지지', 'Du 등(2025)(제1권 4장 표 경유)')
    nk = P.add_name(con, '개성', '옛지명', '開城', 0)
    nek = P.add_ne(con, nk, e946)
    ck = P.add_cand(con, nek, '현', '시연값', '개성', 126.55, 37.97, DEFAULT_RADIUS['현'], '제1권 4.7절 ③: 좌표 출처 확인 필요', '제1권이 시연값이라 적은 좌표. 반경 30 km 는 이 책의 시연 설정', 'C')
    P.add_ev(con, ck, '원문방향거리', 'Yun2023', '지지', 'Yun 등(2023): 백두산에서 465 km(제1권 4.7절 경유). 사료 구절이 아니라 논문의 서술')
    rel = P.add_rel(con, None, 'Yun 등(2023)의 서술(제1권 4.7절 경유)', P.add_ne(con, n1, era), nek, '방향거리', None, None, 465.0, 0.5, None, '구절이 아니라 논문의 서술이므로 passage_id 는 비워 둔다')
    return dict(peak_lee=c1, peak_du=c2, kaesong=ck, rel=rel)


def load_daegu(con):
    """제1권 14장: 대구의 경도 '128°60′E' 를 두 가지로 읽어 후보 둘로 적재(제1권은 129.00 을 택함). 서울은 십진 좌표."""
    era = modern_era(con)
    lat, _, _ = P.parse_dms('35°52′N')
    lon, warns, alts = P.parse_dms('128°60′E')
    nd = P.add_name(con, '대구', '현대지명', None, 0)
    ne = P.add_ne(con, nd, era)
    cA = P.add_cand(con, ne, '점', '논문본문', '대구(60′ 를 1° 로 올려 읽기)', alts[0][0], lat, P.rounding_km('min'), 'Kim(2023) 표기 35°52′N, 128°60′E (제1권 14장 경유)', '; '.join(warns) + ' / ' + alts[0][1], 'C', status='채택')
    cB = P.add_cand(con, ne, '점', '논문본문', '대구(십진 128.60 으로 읽기)', 128.60, lat, P.rounding_km('min'), 'Kim(2023) 표기 (제1권 14장 경유)', '제1권이 택하지 않은 읽기. 지우지 않고 기각으로 둔다', 'C', status='기각')
    for c in (cA, cB):
        P.add_ev(con, c, '좌표', 'Kim2023', '지지', 'Kim(2023)의 표기 "128°60′E"(제1권 14장 경유)')
    ns = P.add_name(con, '서울', '현대지명', None, 0)
    cs = P.add_cand(con, P.add_ne(con, ns, era), '점', '논문본문', '서울(기상대)', 126.97, 37.57, P.rounding_km('dec2'), 'Hwang & Park(2026) 표기 (제1권 14장 경유)', '반경은 표기 반올림만', 'C')
    P.add_ev(con, cs, '좌표', 'HwangPark2026', '지지', 'Hwang & Park(2026)(제1권 14장 경유)')
    return dict(daegu_a=cA, daegu_b=cB, seoul=cs, warns=warns, alts=alts)


def load_eras_ch05(con):
    """제1권 5장 계산 5-15 의 구간들(두 논문이 정한 창)을 시대 표에 적재. 같은 '건조'나 '약한 몬순'도 글마다 창이 다르다는 점을 정의한 곳으로 구별한다."""
    park = [('제주 D1 건조', 1000, 1080), ('제주 D2 건조', 1180, 1320), ('제주 D3 건조', 1420, 1510), ('제주 D4 건조', 1760, 1880), ('제주 W 습윤', 1520, 1760)]
    zhou = [('약한 몬순', 1420, 1625), ('최저 몬순', 1450, 1570), ('강한 몬순', 1000, 1300), ('최고 몬순', 1000, 1230), ('남중국 홍수 많음', 1400, 1600)]
    for n, a, b in park:
        P.add_era(con, n, a, b, 'Park 등(2017), 제1권 5.8절')
    for n, a, b in zhou:
        P.add_era(con, n, a, b, 'Zhou 등(2011), 제1권 5.8절')
    return park, zhou


DEFAULT_RADIUS = {'현': 30.0, '지역': 200.0}   # 이 책의 시연 설정: 제1권 13.8절은 "현 이름이면 수십 km, 지역 이름이면 수백 km" 라고만 적었다
