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
<div style="position:absolute;left:16mm;top:{bleed + 15}mm;font:500 8pt 'Noto Sans CJK KR';letter-spacing:.35em;color:{SAND}">1만 년의 기후와 땅 · 제1권</div>
<div style="position:absolute;left:16mm;top:{bleed + 27}mm;font:700 46pt/1.1 'Noto Serif CJK KR';color:#fff">동아시아</div>
<div style="position:absolute;left:16mm;top:{bleed + 47}mm;font:700 29pt/1.2 'Noto Serif CJK KR';color:#fff">1만 년의 기후와 땅</div>
<div style="position:absolute;left:16mm;top:{bleed + 63}mm;width:30mm;height:1.3mm;background:{ORANGE}"></div>
<div style="position:absolute;left:16mm;top:{bleed + 68}mm;font:400 11pt 'Noto Sans CJK KR';color:{SAND}">한반도에서 본 홀로세의 기후와 지형 변화</div>
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
<div style="color:{SAND};word-break:keep-all">마지막 빙기의 낮은 바다, 해안에 도착한 바다, 동해의 해협, 화산이 남긴 재, 몬순과 태풍, 황토고원과 황하와 장강, 서요하의 사람과 노백산의 나이테. 이 책은 한반도에서 본 지난 1만 년의 기후와 땅을 논문의 숫자를 다시 계산하며 읽는다.</div>
<div style="margin-top:6mm;font:700 10.5pt 'Noto Sans CJK KR';color:#fff">이 책이 중요한 다섯 가지</div>
<div style="margin-top:2mm;color:{SAND};word-break:keep-all;font-size:9.4pt;line-height:1.7">
{li('옛 해안선과 지명이 놓인 바닥이 움직였음을 숫자로 보인다.')}
{li('연대의 오차가 해석을 바꾸는 과정을 직접 계산해 보인다.')}
{li('사료를 시험할 주장으로 놓고 물리 기록과 대조하는 방법을 보인다.')}
{li('사람의 유전 기록과 환경 기록을 같은 틀에서 읽는 법을 익힌다.')}
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
<div style="position:absolute;left:0;top:{BL + 8}mm;width:{w}mm;text-align:center;font:700 14pt 'Noto Serif CJK KR';color:{ORANGE}">1</div>
<div style="position:absolute;left:{w / 2 - 80}mm;top:{H / 2 - 4.5}mm;width:160mm;height:9mm;transform:rotate(90deg);text-align:center;white-space:nowrap;font:700 {min(16, max(9, w * 0.55)):.1f}pt/9mm 'Noto Serif CJK KR';color:#fff">동아시아 1만 년의 기후와 땅<span style="font:400 9pt 'Noto Sans CJK KR';color:{SAND};margin-left:6mm">이광조 지음</span></div>
<img src="/home/claude/book/logo/ssp-symbol-dark-v1.svg" style="position:absolute;left:{w / 2 - min(w - 5, 14) / 2}mm;top:{H - BL - 21}mm;width:{min(w - 5, 14)}mm">
</div></div>'''
CSS = '''@page{margin:0}body{margin:0}.pg{position:relative;overflow:hidden}'''
os.makedirs('cover', exist_ok=True)
def write(name, body, w, h):
    html = f'<html><head><meta charset="utf-8"><style>@page{{size:{w}mm {h}mm;margin:0}}{CSS}</style></head><body>{body}</body></html>'
    HTML(string=html, base_url='.').write_pdf(f'cover/{name}-{ver}.pdf')
# 앞표지·뒷표지(재단 크기, 도련 없음)
write('front', front_html(0).replace(f'width:{TW}mm', f'width:{TW}mm'), TW, TH)
write('back', back_html(0), TW, TH)
# 펼침: 뒷표지 | 책등 | 앞표지, 사방 도련 3 mm
SW = BL + TW + SPINE + TW + BL; SH = TH + 2 * BL
def box_(x, inner): return f'<div style="position:absolute;left:{x}mm;top:0">{inner}</div>'
spread = box_(0, back_html(BL).replace(f'width:{TW + BL}mm', f'width:{TW + BL}mm')) + box_(BL + TW + SPINE, front_html(BL)) + box_(BL + TW, spine_html(SPINE, SH))
write('spread', f'<div class="pg" style="width:{SW}mm;height:{SH}mm;background:{NAVY}">{spread}</div>', SW, SH)
subprocess.run(['pdftoppm', '-r', '210', '-png', '-singlefile', f'cover/front-{ver}.pdf', f'cover/front-{ver}'])
print('spine', SPINE, 'spread', SW, 'x', SH)
