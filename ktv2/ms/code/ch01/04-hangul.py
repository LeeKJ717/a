# -*- coding: utf-8 -*-
"""실습 1-4: 한글 지명 지도의 글꼴 문제. (1) 기본 글꼴에서 글자가 깨지는 것을 재현하고 (2) Noto CJK 로 고치고
(3) 글꼴 안에 글자가 실제로 있는지 검사하고 (4) 한글 이름표(CSV)를 Natural Earth 자료와 대조한다."""
import os, sys, re, csv, warnings, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, ft2font
from fontTools.ttLib import TTCollection
from fontTools.pens.recordingPen import RecordingPen

LABELS = ['서울', '부산', '제주', '평양', '동해', '황해', '대한해협', '백두산']

print('== 1. matplotlib 기본 글꼴로 한글을 그리면 (이 컨테이너의 기본 후보는 Inter, DejaVu Sans) ==')
plt.rcParams.update(plt.rcParamsDefault)
print('기본 font.family =', plt.rcParams['font.family'], ' sans-serif 후보 앞부분 =', plt.rcParams['font.sans-serif'][:3])
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    fig = plt.figure(figsize=(3, 1)); fig.text(0.1, 0.4, ' '.join(LABELS[:4]), fontsize=12)
    fig.savefig('/dev/null', format='svg')
    plt.close(fig)
miss = [str(x.message) for x in w if 'missing from font' in str(x.message)]
print('"서울 부산 제주 평양"을 그리자 나온 경고 %d개. 처음 2개:' % len(miss))
for m in miss[:2]:
    print('  ', m[:120])

print()
print('== 2. Noto Sans CJK KR 로 바꾸기 ==')
path = K.use_font()
print('fm.findfont("%s") →' % K.FONT, path)
ff = ft2font.FT2Font(path)
print('이 파일(ttc)에는 얼굴(face)이 %d개 들어 있고, matplotlib 이 연 얼굴의 이름은 "%s"이다.' % (ff.num_faces, ff.family_name))
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    fig = plt.figure(figsize=(3, 1)); fig.text(0.1, 0.4, ' '.join(LABELS[:4]), fontsize=12)
    fig.savefig('/dev/null', format='svg')
    plt.close(fig)
print('같은 글을 다시 그리자 나온 글꼴 경고 %d개' % len([x for x in w if 'missing from font' in str(x.message)]))

print()
print('== 3. 글꼴 파일 안에 글자가 있는가 + 얼굴 0(JP)과 얼굴 1(KR)의 한글 모양이 같은가 ==')
col = TTCollection(path)
f0, f1 = col.fonts[0], col.fonts[1]
print('얼굴 0 = %s, 얼굴 1 = %s' % (f0['name'].getDebugName(4), f1['name'].getDebugName(4)))
chars = sorted({c for s in LABELS for c in s})
cm0, cm1 = f0.getBestCmap(), f1.getBestCmap()
gs0, gs1 = f0.getGlyphSet(), f1.getGlyphSet()
def outline(gs, name):
    p = RecordingPen(); gs[name].draw(p); return p.value
same = 0
for c in chars:
    assert ord(c) in cm0 and ord(c) in cm1, c
    same += outline(gs0, cm0[ord(c)]) == outline(gs1, cm1[ord(c)])
print('검사한 글자 %d개, 두 얼굴 모두에 있음, 윤곽선이 같은 글자 %d개' % (len(chars), same))

print()
print('== 4. 한글 이름표를 Natural Earth 와 대조 ==')
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'names-ko-v1.csv'), encoding='utf-8')))
bb = (122.0, 31.0, 134.0, 45.0)
pp = K.read('ne_10m_populated_places_simple', bb)
rv = K.read('ne_10m_rivers_lake_centerlines', bb)
ep = K.read('ne_10m_geography_regions_elevation_points', bb)
print('%-8s %-12s %-6s %s' % ('한글', 'NE 이름', '종류', '자료에서 찾은 것'))
ok = 0
for r in rows:
    ko, ne, kind = r['ko'], r['ne_name'], r['kind']
    assert re.fullmatch(r'[가-힣]+', ko), '한글 아닌 글자: ' + ko
    assert not re.search(r'[一-鿿]', ko), '한자 있음: ' + ko
    if kind == 'city':
        h = pp[pp['name'].str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('ascii') == ne]
        info = '; '.join('(%.3f, %.3f) 인구 %s' % (x.longitude, x.latitude, format(int(x.pop_max), ',')) for x in h.itertuples())
    elif kind == 'river':
        h = rv[rv['name'] == ne]
        info = '선 %d개, 범위 %s' % (len(h), [round(float(v), 1) for v in h.total_bounds]) if len(h) else ''
    else:
        h = ep[ep['name'] == ne]
        info = '; '.join('(%.3f, %.3f) %s m' % (x.long_x, x.lat_y, x.elevation) for x in h.itertuples())
    ok += len(h) > 0
    print('%-8s %-12s %-6s %s' % (ko, ne, kind, info or '찾지 못함'))
print('이름표 %d행 중 자료에서 찾은 것 %d행' % (len(rows), ok))
print('(한글 글자 수 검사와 한자 없음 검사는 assert 로 통과했다)')

print()
print('== 5. 바다 이름 위치가 정말 바다인가 ==')
land = K.read('ne_10m_land', bb)
from shapely.geometry import Point
seas = {'황해': (124.0, 36.0), '동해': (131.5, 39.5), '동중국해': (126.0, 31.8), '대한해협': (129.6, 34.3)}
for nm, (lo, la) in seas.items():
    inl = bool(land.contains(Point(lo, la)).any())
    print('%-6s (%.1f, %.1f) → %s' % (nm, lo, la, '육지(위치를 옮겨야 함)' if inl else '바다'))
