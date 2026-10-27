#!/usr/bin/env python3
# usage: ART=그림파일 cover-v2.py PAGES [VER]  (GPU 그림 표지판; cover-v1.py의 지도 표지를 그림으로 바꿈)
# usage(v1): cover-v1.py PAGES [VER]  -> cover/front-VER.pdf/.png, back-VER.pdf, spread-VER.pdf (3 mm bleed), colophon is in build.py
import sys, json, math, os, subprocess
from shapely.geometry import shape, box
from weasyprint import HTML
pages = int(sys.argv[1]); ver = sys.argv[2] if len(sys.argv) > 2 else 'v1'
MM_PER_PAGE = 0.055; SPINE = round(pages * MM_PER_PAGE + 0.5, 1)    # 용지 두께는 인쇄소 값을 받으면 이 상수만 바꾼다
TW, TH, BL = 182.0, 257.0, 3.0
NAVY, NAVY2, SAND, ORANGE, TEAL, TEAL2 = '#0f2a3f', '#17384f', '#eadfc6', '#e07a3f', '#2d7f98', '#215f75'
BBOX = (104.0, 24.0, 146.0, 50.0)
def load(n): return json.load(open(f'geodata/{n}.geojson'))['features']
def path(g, X, Y):
    polys = [g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))
    d = ''
    for p in polys:
        if p.geom_type != 'Polygon' or p.is_empty: continue
        for r in [p.exterior] + list(p.interiors):
            c = list(r.coords)
            d += 'M' + 'L'.join(f'{X(x):.2f},{Y(y):.2f}' for x, y in c) + 'Z'
    return d
def lines(g, X, Y):
    ls = [g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))
    return ''.join('M' + 'L'.join(f'{X(x):.2f},{Y(y):.2f}' for x, y in l.coords) for l in ls if not l.is_empty)
def map_svg(w, h):
    x0, y0, x1, y1 = BBOX
    k = math.cos(math.radians(37))
    sx = w / ((x1 - x0) * k); sy = h / (y1 - y0); s = min(sx, sy)
    ox = (w - (x1 - x0) * k * s) / 2; oy = (h - (y1 - y0) * s) / 2
    X = lambda lon: ox + (lon - x0) * k * s
    Y = lambda lat: oy + (y1 - lat) * s
    bx = box(*BBOX)
    out = [f'<rect width="{w}" height="{h}" fill="#3b8ca6" rx="3"/>']
    # 경위선
    for lon in range(105, 146, 5):
        out.append(f'<path d="M{X(lon):.2f},0L{X(lon):.2f},{h}" stroke="#ffffff" stroke-opacity="0.14" stroke-width="0.25"/>')
    for lat in range(25, 50, 5):
        out.append(f'<path d="M0,{Y(lat):.2f}L{w},{Y(lat):.2f}" stroke="#ffffff" stroke-opacity="0.14" stroke-width="0.25"/>')
    d = ''
    for f in load('ne_10m_bathymetry_K_200'):
        g = shape(f['geometry']).intersection(bx)
        if not g.is_empty: d += path(g, X, Y)
    out.append(f'<path d="{d}" fill="#1b4d66" fill-rule="evenodd"/>')
    d = ''
    for n in ('ne_10m_land', 'ne_10m_minor_islands'):
        for f in load(n):
            g = shape(f['geometry'])
            if not g.intersects(bx): continue
            g = g.intersection(bx)
            if not g.is_empty: d += path(g, X, Y)
    out.append(f'<path d="{d}" fill="{SAND}" fill-rule="evenodd"/>')
    keep = {'Huang', 'Chang Jiang', 'Yangtze', 'Liao', 'Xiliao', 'Han', 'Nakdong', 'Yalu', 'Tumen', 'Songhua', "Di’er Songhua", 'Amur', 'Huai', 'Xi', 'Xiang'}
    d = ''
    for f in load('ne_10m_rivers_lake_centerlines'):
        n = f['properties'].get('name')
        if n in keep:
            g = shape(f['geometry']).intersection(bx)
            if not g.is_empty: d += lines(g, X, Y)
    out.append(f'<path d="{d}" fill="none" stroke="#2a7390" stroke-width="0.5" stroke-linejoin="round" stroke-linecap="round"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">' + ''.join(out) + '</svg>'
def strata_svg(w, h):
    cols = ['#d9c9a3', '#b89b6a', '#e6dcc2', '#8f7451', '#c7ae80', '#6f5a40', '#d4c096', '#a98a5c', '#4d3f2e']
    ws = [0.9, 1.6, 0.7, 2.1, 1.2, 1.8, 0.8, 1.5, 1.4]
    tot = sum(ws); y = 0; o = []
    for c, q in zip(cols, ws):
        hh = h * q / tot
        o.append(f'<rect x="0" y="{y:.2f}" width="{w}" height="{hh + 0.05:.2f}" fill="{c}"/>'); y += hh
    # 나이테식 동심 호
    for i, r in enumerate(range(8, 70, 7)):
        o.append(f'<circle cx="{w * 0.82:.1f}" cy="{h * 1.05:.1f}" r="{r}" fill="none" stroke="#0f2a3f" stroke-opacity="0.16" stroke-width="0.35"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">' + ''.join(o) + '</svg>'
FONT = '''@font-face{font-family:x;src:local("Noto Serif CJK KR")}'''
def front_html(bleed):
    W, H = TW + bleed, TH + 2 * bleed          # 오른쪽 도련만 (펼침에서 쓰는 앞표지 상자)
    return f'''<div class="pg" style="width:{W}mm;height:{H}mm;background:{NAVY}">
<div style="position:absolute;left:0;top:0;width:{W}mm;height:{H}mm">
<div style="position:absolute;left:16mm;top:{bleed + 15}mm;font:500 8pt 'Noto Sans CJK KR';letter-spacing:.35em;color:{SAND}">1만 년의 기후와 땅 · 제4권</div>
<div style="position:absolute;left:16mm;top:{bleed + 27}mm;font:700 46pt/1.1 'Noto Serif CJK KR';color:#fff">지구</div>
<div style="position:absolute;left:16mm;top:{bleed + 47}mm;font:700 29pt/1.2 'Noto Serif CJK KR';color:#fff">1만 년의 기후와 땅</div>
<div style="position:absolute;left:16mm;top:{bleed + 63}mm;width:30mm;height:1.3mm;background:{ORANGE}"></div>
<div style="position:absolute;left:16mm;top:{bleed + 68}mm;font:400 11pt 'Noto Sans CJK KR';color:{SAND}">빙핵에서 해수면까지, 지난 1만 년의 전지구 기록</div>
<div style="position:absolute;left:0;top:{bleed + 80}mm;width:{W}mm;height:{H - bleed - 80}mm;overflow:hidden"><img src="{os.environ['ART']}" style="width:{W}mm;height:{H - bleed - 80}mm;object-fit:cover;object-position:center bottom"></div>
<div style="position:absolute;left:0;top:{bleed + 80}mm;width:{W}mm;height:26mm;background:linear-gradient(180deg,{NAVY},rgba(15,42,63,0))"></div>
<div style="position:absolute;z-index:3;left:16mm;top:{bleed + 230}mm;font:500 13pt 'Noto Sans CJK KR';color:#fff;letter-spacing:.08em">이광조 지음</div>
<div style="position:absolute;left:0;top:{bleed + 220}mm;width:{W}mm;height:{H - bleed - 220}mm;background:rgba(15,42,63,.9)"></div>
<img src="/home/claude/book/logo/ssp-logo-h-dark-v1.svg" style="position:absolute;right:14mm;top:{bleed + 238}mm;width:46mm">
</div></div>'''
def back_html(bleed):
    W, H = TW + bleed, TH + 2 * bleed
    li = lambda t: f'<div style="margin:0 0 2.2mm 0;padding-left:4mm;text-indent:-4mm">· {t}</div>'
    return f'''<div class="pg" style="width:{W}mm;height:{H}mm;background:{NAVY};color:#fff">
<div style="position:absolute;left:{16 + bleed}mm;top:{bleed + 18}mm;width:148mm;font:400 10pt/1.75 'Noto Sans CJK KR'">
<div style="font:700 15pt/1.5 'Noto Serif CJK KR';color:#fff;margin-bottom:4mm">물리 기록을 먼저 읽고,<br>문자 기록은 시험할 주장으로 놓는다</div>
<div style="width:30mm;height:1.1mm;background:{ORANGE};margin-bottom:6mm"></div>
<div style="color:{SAND};word-break:keep-all">그린란드와 남극의 빙핵, 온실기체, 해수면과 해안선, 몬순과 열대, 8.2ka와 4.2ka 사건, 화산과 태양, 아메리카와 남반구, 최근 이천 년. 이 책은 전지구 기록을 논문의 숫자로 다시 계산하며 읽고, 기록마다 연대 오차와 해석의 한계를 함께 적는다.</div>
<div style="margin-top:6mm;font:700 10.5pt 'Noto Sans CJK KR';color:#fff">이 책이 중요한 다섯 가지</div>
<div style="margin-top:2mm;color:{SAND};word-break:keep-all;font-size:9.4pt;line-height:1.7">
{li('옛 해안선과 땅이 움직였음을 전지구 해수면 기록의 숫자로 보인다.')}
{li('연대의 오차가 해석을 바꾸는 과정을 직접 계산해 보인다.')}
{li('기후와 사회를 잇는 주장을 물리 기록과 연대로 시험하는 방법을 보인다.')}
{li('빙핵, 해양, 석순, 나이테 기록을 같은 틀에서 읽는 법을 익힌다.')}
{li('미결 항목을 남겨 후속 연구의 목록으로 삼는다.')}
</div>
<div style="margin-top:5mm;font:700 10.5pt 'Noto Sans CJK KR';color:#fff">이런 분께</div>
<div style="margin-top:2mm;color:{SAND};word-break:keep-all;font-size:9.4pt;line-height:1.7">
{li('역사학, 인류학, 고고학에서 기후·지형 기록을 쓰려는 연구자')}
{li('지리·지질·해양·기후를 공부하는 학생과 연구자')}
{li('고등학교 과학과 수학으로 따라갈 수 있게 쉬운 예를 달았다')}
</div></div>
<div style="position:absolute;left:{16 + bleed}mm;top:{bleed + 224}mm;font:400 8.5pt/1.7 'Noto Sans CJK KR';color:{SAND}">정가 (추후 기입)</div>
<img src="/home/claude/book/logo/ssp-logo-h-dark-v1.svg" style="position:absolute;left:{16 + bleed}mm;top:{bleed + 232}mm;width:46mm">
<div style="position:absolute;right:{16}mm;top:{bleed + 219}mm;width:52mm;height:30mm;border:0.4mm dashed {SAND};background:#fff;color:#555;font:400 7.5pt/30mm 'Noto Sans CJK KR';text-align:center">ISBN · 바코드 자리</div>
</div>'''
def spine_html(w, H):
    return f'''<div class="pg" style="width:{w}mm;height:{H}mm;background:{NAVY2}">
<div style="position:absolute;left:0;top:0;width:{w}mm;height:{H}mm">
<div style="position:absolute;left:0;top:{BL + 8}mm;width:{w}mm;text-align:center;font:700 14pt 'Noto Serif CJK KR';color:{ORANGE}">4</div>
<div style="position:absolute;left:{w / 2 - 80}mm;top:{H / 2 - 4.5}mm;width:160mm;height:9mm;transform:rotate(90deg);text-align:center;white-space:nowrap;font:700 {min(16, max(9, w * 0.55)):.1f}pt/9mm 'Noto Serif CJK KR';color:#fff">1만 년의 기후와 땅<span style="font:400 9pt 'Noto Sans CJK KR';color:{SAND};margin-left:6mm">이광조 지음</span></div>
<img src="/home/claude/book/logo/ssp-symbol-dark-v1.svg" style="position:absolute;left:{w / 2 - min(w - 5, 14) / 2}mm;top:{H - BL - 21}mm;width:{min(w - 5, 14)}mm">
</div></div>'''

FW = 95.0
def flap_front(h):   # 앞날개(오른쪽): 저자 소개
    li = lambda t: f'<div style="margin:0 0 2mm 0;padding-left:3.5mm;text-indent:-3.5mm">· {t}</div>'
    return f"""<div class="pg" style="width:{FW + BL}mm;height:{h}mm;background:{NAVY2};color:#fff">
<div style="position:absolute;left:9mm;top:{BL + 18}mm;width:{FW - 17}mm;font:400 8.6pt/1.7 'Noto Sans CJK KR';word-break:keep-all">
<div style="font:500 7.5pt 'Noto Sans CJK KR';letter-spacing:.3em;color:{SAND}">저자 소개</div>
<div style="font:700 17pt/1.3 'Noto Serif CJK KR';margin:2mm 0 3mm">이광조</div>
<div style="width:20mm;height:1mm;background:{ORANGE};margin-bottom:5mm"></div>
<div style="color:{SAND}">서울대학교에서 식품영양학 박사학위를 받았다. 한국식품영양연구소 대표로, 약 30년 동안 식물성 영양, 단식 생리, 동양의 수행 전통을 현대 과학과 이어 연구해 왔다. 통계 전문가이며 특허 2건을 보유하고 있고, SCIE 학술지에 논문을 발표했다. 한국생활건강학원을 운영하고 있다.</div>
<div style="margin-top:5mm;font:700 9pt 'Noto Sans CJK KR'">지은 책</div>
<div style="margin-top:1.5mm;color:{SAND}">{li('『채식치유학』')}{li('『역사속의 채식인』')}{li('『과학과 초월의 길목에서』(2015)')}</div>
<div style="margin-top:5mm;color:{SAND}">이 시리즈에서는 논문의 숫자를 다시 계산하고, 확인한 것과 확인하지 못한 것을 가려 적는 방식으로 기후와 지형, 옛 지명의 위치를 읽는다.</div>
</div></div>"""
def flap_back(h):    # 뒷날개(왼쪽): 집필 중인 책 4권 소개, 썸네일 세로 배열
    P = '/home/claude/book/cover/'
    items = [
     (P + 'thumb-seogyeong1.png', '고려 서경(西京)의 위치를 추정하다', '1권 방법편 · 집필 중',
      '옛 문헌의 방위와 거리, 이웃 지명, 산과 강의 서술을 좌표와 면적으로 바꾸는 여덟 가지 방법(제약·구간 연산, 지오레퍼런싱, 베이즈 추정, 최소비용 경로, 그래프 이론, 지명 정합, 지명 언어학, 교차검증)을 처음부터 풀어 설명한다. 고려 서경 하나를 이 방법들로 끝까지 추정해 비교한다.'),
     (P + 'thumb-gn-1.png', '고전의 지명을 좌표로 옮기다<br>1권 기초편', '고전지명추정 · 집필 중',
      '문제 설정, 지도, 수학, 지리, 사료, 레코드, 단위(里를 km로 바꾸는 문제)까지 지명 추정에 필요한 기초를 초보자도 따라올 수 있게 차례로 쌓는다.'),
     (P + 'thumb-gn-2.png', '고전의 지명을 좌표로 옮기다<br>2권 기법편', '고전지명추정 · 집필 중',
      '지명 위치를 추정하는 여덟 가지 기법의 이론 배경과 선행연구를 정리하고, 같은 문제에 적용해 결과를 견주는 벤치마크를 싣는다.'),
     (P + 'thumb-gn-3.png', '고전의 지명을 좌표로 옮기다<br>3권 적용편', '고전지명추정 · 집필 중',
      '한반도, 요하 유역, 산동과 발해 연안, 만주와 러시아 극동, 서역과 중앙아시아에 기법을 적용한다. 여러 기법을 묶는 파이프라인, 불확실성의 표현, 재현성과 한계를 함께 다룬다.')]
    rows = ''
    for img, t, sub, d in items:
        rows += f"""<div style="display:flex;gap:4mm;align-items:flex-start;margin-bottom:5mm"><img src="{img}" style="flex:none;width:30mm;border:.3mm solid {SAND}"><div><div style="font:700 9pt/1.4 'Noto Serif CJK KR'">{t}</div><div style="color:{SAND};font-size:7.2pt;margin:.8mm 0 1.6mm">{sub}</div><div style="color:{SAND};font-size:7.4pt;line-height:1.6">{d}</div></div></div>"""
    return f"""<div class="pg" style="width:{FW + BL}mm;height:{h}mm;background:{NAVY2};color:#fff">
<div style="position:absolute;left:{BL + 8}mm;top:{BL + 14}mm;width:{FW - 17}mm;font:400 8pt/1.6 'Noto Sans CJK KR';word-break:keep-all">
<div style="font:500 7.5pt 'Noto Sans CJK KR';letter-spacing:.3em;color:{SAND}">집필 중인 책</div>
<div style="width:20mm;height:1mm;background:{ORANGE};margin:3mm 0 5mm"></div>
{rows}
<div style="color:{SAND};font-size:7.2pt;line-height:1.6;margin-top:1mm">고전지명추정에는 지도 10장을 모은 4권 지도집이 더해진다. 책의 제목과 출간 시기는 달라질 수 있다.</div>
</div></div>"""

CSS = '''@page{margin:0}body{margin:0}.pg{position:relative;overflow:hidden}'''
os.makedirs('cover', exist_ok=True)
def write(name, body, w, h):
    html = f'<html><head><meta charset="utf-8"><style>@page{{size:{w}mm {h}mm;margin:0}}{CSS}</style></head><body>{body}</body></html>'
    HTML(string=html, base_url='.').write_pdf(f'cover/{name}-{ver}.pdf')
# 앞표지·뒷표지(재단 크기, 도련 없음)
write('front', front_html(0).replace(f'width:{TW}mm', f'width:{TW}mm'), TW, TH)
write('back', back_html(0), TW, TH)
# 펼침(날개 포함): 도련 | 뒷날개 | 뒷표지 | 책등 | 앞표지 | 앞날개 | 도련
SW = BL + FW + TW + SPINE + TW + FW + BL; SH = TH + 2 * BL
def box_(x, inner): return f'<div style="position:absolute;left:{x}mm;top:0">{inner}</div>'
x_bf = 0; x_b = BL + FW - BL if False else BL + FW; 
spread = (box_(0, flap_back(SH)) + box_(BL + FW, back_html(0).replace(f'height:{TH}mm', f'height:{SH}mm').replace(f'top:{0 + 18}mm', f'top:{BL + 18}mm'))
          + box_(BL + FW + TW, spine_html(SPINE, SH)) + box_(BL + FW + TW + SPINE, front_html(BL).replace(f'width:{TW + BL}mm', f'width:{TW}mm'))
          + box_(BL + FW + TW + SPINE + TW, flap_front(SH)))
write('spreadflap', f'<div class="pg" style="width:{SW}mm;height:{SH}mm;background:{NAVY}">{spread}</div>', SW, SH)
subprocess.run(['pdftoppm', '-r', '210', '-png', '-singlefile', f'cover/front-{ver}.pdf', f'cover/front-{ver}'])
print('spine', SPINE, 'spread', SW, 'x', SH)
subprocess.run(['pdftoppm','-r','60','-png','-singlefile',f'cover/spreadflap-{ver}.pdf',f'cover/spreadflap-{ver}'])
