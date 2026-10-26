# -*- coding: utf-8 -*-
"""13장 그림: 지도 2장 + 그래프 5장. 좌표는 Gakuhari 등(2020) 본문의 이카와즈 패총 좌표와 Natural Earth 도시 위치.
그래프 값은 각 논문 표·본문의 값이거나 ms/ch13-calc-v1.py 의 계산 결과다."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomap as G
from geomap import basemap, area, city, scalebar, north, legend, Fig, FS, FS_S, FS_I, f1, PAL
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
def dms(d, m=0, s=0): return d + m / 60 + s / 3600

def hav(lo1, la1, lo2, la2):
    R = 6371.0088
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def note(f, x, y, s):
    sh = getattr(f, '_sh', 0)
    maxw = f.w - x - 2
    lines, cur = [], ''
    for ch in s:
        if G.tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    if len(lines) > 1 and len(lines[-1]) <= 2:
        last = lines.pop(); lines[-1] += last
    for i, ln in enumerate(lines):
        f.text(x, y + sh + i * 36, ln, FS_I, 'start', f.P['soft'], 400, False)
    f._sh = sh + 36 * (len(lines) - 1)

IK = (dms(137, 8, 52), dms(34, 38, 43))
REB = (141.0314, 45.3811)

# ----------------------------------------------------------------- 지도 1: 일본열도
def map_japan(mode):
    bbox = (128.0, 30.0, 146.6, 46.0)
    f, pr = basemap(bbox, pad=470, mode=mode, grid=5, latside='right')
    P = f.P
    area(f, pr, 134.5, 38.6, '동해', FS_S, P['soft'], 700, 2.0, where='sea')
    area(f, pr, 143.6, 34.0, '태평양', FS_S, P['soft'], 700, 2.0, where='sea')
    for nm, lo, la, dx, dy, an in (
            ('삿포로', 141.338, 43.077, 14, 8, 'start'), ('하코다테', 140.74, 41.795, 14, 8, 'start'), ('아오모리', 140.71, 40.825, 14, 8, 'start'),
            ('센다이', 140.87, 38.268, 14, 8, 'start'), ('도쿄', 139.749, 35.687, 14, 8, 'start'), ('나고야', 136.913, 35.157, -14, -10, 'end'),
            ('오사카', 135.504, 34.691, -14, 24, 'end'), ('히로시마', 132.441, 34.39, 14, 28, 'start'), ('후쿠오카', 130.408, 33.597, -14, -12, 'end'),
            ('사세보', 129.718, 33.163, -14, 8, 'end'), ('가고시마', 130.561, 31.586, 14, 8, 'start')):
        city(f, pr, lo, la, nm, dx, dy, an)
    x, y = pr(*IK)
    f.marker(x, y, 'star', 1.1, P['hot'])
    f.text(x + 16, y + 52, '이카와즈 패총', FS_S, 'start', P['hot'], 700)
    x, y = pr(*REB)
    f.marker(x, y, 'tri', 1.0, P['hot'])
    f.text(x - 16, y + 8, '레분섬(섬 전체)', FS_S, 'end', P['hot'], 700)
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('dot', '도시(Natural Earth 위치)'), ('star', '이카와즈 패총(Gakuhari 등, 2020 본문 좌표)'), ('tri', '레분섬 중심(Natural Earth 섬 다각형, 유적 좌표 아님)')])
    scalebar(f, pr, 40, last + 76, 300)
    note(f, 30, last + 150, '※ 후나도마리는 "레분섬 북부", 산간지는 "후쿠시마현 북부", 헤기 동굴은 "규슈 북부"라고만 적혀 있어 점으로 찍지 않았다(근거 논문 확보 필요).')
    return f, pr

# ----------------------------------------------------------------- 지도 2: 아쓰미반도 둘레
def map_atsumi(mode):
    bbox = (136.4, 34.3, 138.3, 35.4)
    f, pr = basemap(bbox, pad=360, mode=mode, grid=0.5, latside='right')
    P = f.P
    x1, y1 = pr(*IK)
    f.marker(x1, y1, 'star', 1.2, P['hot'])
    f.text(x1 - 18, y1 + 54, '이카와즈 패총', FS_S, 'end', P['hot'], 700)
    for nm, lo, la, dx, dy, an in (('하마마쓰', 137.7327, 34.7181, 14, 28, 'start'), ('나고야', 136.913, 35.157, 14, 8, 'start')):
        city(f, pr, lo, la, nm, dx, dy, an)
        x2, y2 = pr(lo, la)
        f.line(x1, y1, x2, y2, P['hot'], 2.4, '10 8')
        d = hav(IK[0], IK[1], lo, la)
        f.text((x1 + x2) / 2 + 16, (y1 + y2) / 2 - 8, '%.1f km' % d, FS_S, 'start', P['hot'], 700)
    area(f, pr, 137.2, 34.45, '태평양(엔슈나다)', FS_S, P['soft'], 700, 2.0, where='sea')
    north(f, 70, 90, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('star', '이카와즈 패총(논문 좌표 34°38′43″N, 137°8′52″E)'), ('dot', '도시(Natural Earth)')])
    scalebar(f, pr, 40, last + 76, 20)
    note(f, 30, last + 150, '※ 점선은 직선거리(계산 13-14). 호비 패총은 "이카와즈에서 지리적으로 매우 가깝다"는 서술뿐이어서 그리지 않았다. 좌표 확인 필요.')
    return f, pr

# ----------------------------------------------------------------- 그래프 공통
def base(mode, H=1060.0):
    W = 1300.0
    f = Fig(W, H, mode)
    f.rect(0, 0, W, H, '#FFFFFF')
    return f, f.P

def cols(P, mode):
    if mode == 'color':
        return {'a': P['hot'], 'b': P['river'], 'c': P['site'], 'd': '#6B7A82', 'e': '#B4B4B4'}
    return {'a': '#111111', 'b': '#555555', 'c': '#888888', 'd': '#333333', 'e': '#CCCCCC'}

def frame_x(f, L, T, R, B, X, ticks, lab, fmt=str):
    P = f.P
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in ticks:
        f.line(X(v), T, X(v), B, P['grid'], 1.0, '8 8')
        f.line(X(v), B, X(v), B + 10, P['frame'], 2.0)
        f.text(X(v), B + 44, fmt(v), FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, lab, FS_S, 'middle', P['text'], 400, False)

# ----------------------------------------------------------------- 그래프 1: 달력 창
def chart_window(mode):
    f, P = base(mode, 1180.0)
    L, R, T, B = 560.0, 1250.0, 80.0, 800.0
    a0, a1 = -2100.0, 400.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    fmt = lambda v: '%d' % v
    frame_x(f, L, T, R, B, X, [-2000, -1500, -1000, -500, 0, 250], '달력 연대 (기원전은 음수, 막대는 논문이 적은 구간)', fmt)
    C = cols(P, mode)
    rows = [('F23 후나도마리 (조몬)', -2010, -1600, 'a'), ('산간지 조몬(약 3000 BP, 점)', -1050, -1050, 'a'), ('IK001 이카와즈 (조몬)', -749, -417, 'a'), ('IK002 이카와즈 (조몬)', -770, -468, 'a'),
            ('허드슨 야요이 정의(-1000~250)', -1000, 250, 'e'), ('미야모토 유스 1기', -900, -701, 'b'), ('미야모토 유스 2기', -700, -501, 'b'),
            ('미야모토 이타즈케 확산', -600, -401, 'b'), ('미야모토 우키쿤덴 쌀(9세기 후반)', -850, -801, 'c'), ('14C 생산 냉량 850~700', -850, -700, 'd'),
            ('ALDER 혼슈 일본인(2020 기준)', -213, 280, 'c')]
    rh = (B - T) / len(rows)
    for i, (lab, s, e, k) in enumerate(rows):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, lab, FS_I, 'end', P['text'], 400, False)
        if s == e:
            f.marker(X(s), y, 'dot', 1.0, C[k])
        else:
            f.rect(X(s), y - 17, max(X(e) - X(s), 5), 34, C[k], P['frame'], 1.4)
    ly = B + 150
    note(f, 40, ly, '조몬 계열 네 줄이 위, 야요이 정의와 미야모토의 단계가 가운데, 아래 둘은 보조 창. 같은 달력 구간에 놓인 이름이 서로 다른 문화를 가리킨다는 점을 보이는 그림(계산 13-1, 13-2, 13-5). "허드슨"은 Hudson의 한글 표기.')
    return f

# ----------------------------------------------------------------- 그래프 2: 조몬 계통 몫 추정
EST = [('산간지 TreeMix', 12, None, None), ('후나도마리 f4 비율(한국인 기준)', 12.7, None, None), ('후나도마리 TreeMix', 15.7, None, None), ('후나도마리 qpGraph', 9, None, None),
       ('IK002 qpGraph(일본인에 대한 몫)', 8, None, None), ('Jinam f4 비율 13~21(인용)', 13, 13, 21), ('Jinam ADMIXTURE(인용)', 17, None, None),
       ('ABC 36(22~53, 인용)', 36, 22, 53), ('부분 mtDNA 35(인용)', 35, None, None), ('인구 모형 23~40(인용)', 31.5, 23, 40), ('허드슨 요약 약 10', 10, None, None)]
def chart_jomon(mode):
    f, P = base(mode, 1100.0)
    L, R, T, B = 560.0, 1250.0, 80.0, 760.0
    X = lambda v: L + v / 60.0 * (R - L)
    frame_x(f, L, T, R, B, X, [0, 10, 20, 30, 40, 50, 60], '혼슈 일본인의 조몬 계통 몫 (%)')
    C = cols(P, mode)
    rh = (B - T) / len(EST)
    for i, (lab, m, lo, hi) in enumerate(EST):
        y = T + (i + 0.5) * rh
        quote = '인용' in lab
        c = C['b'] if quote else C['a']
        f.text(L - 14, y + 10, lab, FS_I, 'end', P['text'], 400, False)
        if lo is not None:
            f.line(X(lo), y, X(hi), y, c, 6.0)
            f.line(X(lo), y - 14, X(lo), y + 14, c, 4.0)
            f.line(X(hi), y - 14, X(hi), y + 14, c, 4.0)
        if lab.startswith('인구 모형') or lab.startswith('Jinam f4'):
            pass
        else:
            f.marker(X(m), y, 'dot', 1.0, c)
    f.line(X(20), T, X(20), B, P['text'], 2.4, '14 8')
    f.text(X(20) + 10, T + 30, '"20% 미만"', FS_I, 'start', P['text'], 700, False)
    ly = B + 150
    f.marker(150, ly - 8, 'dot', 1.0, C['a']); f.text(180, ly, '이 책이 읽은 논문의 직접 추정', FS_I, 'start', P['text'], 400, False)
    f.marker(620, ly - 8, 'dot', 1.0, C['b']); f.text(650, ly, '논문이 인용한 다른 연구(원문 확인 필요)', FS_I, 'start', P['text'], 400, False)
    note(f, 40, ly + 56, '점은 점 추정, 가로선은 논문이 적은 범위(Jinam, 인구 모형은 범위만). 점선은 산간지 논문의 결론 "20% 미만"(계산 13-12).')
    return f

# ----------------------------------------------------------------- 그래프 3: 표 5의 비교 집단 의존
ROWS = [('혼슈 일본인', '한국인', 0.127, 0.024), ('혼슈 일본인', '베이징 한족', 0.137, 0.015), ('혼슈 일본인', '남부 한족', 0.184, 0.016),
        ('류큐', '한국인', 0.266, 0.024), ('류큐', '베이징 한족', 0.274, 0.018), ('류큐', '남부 한족', 0.314, 0.018),
        ('아이누', '한국인', 0.662, 0.040), ('아이누', '베이징 한족', 0.666, 0.039), ('아이누', '남부 한족', 0.684, 0.037),
        ('아이누', '울치', 0.491, 0.053), ('아이누', '헤젠', 0.543, 0.049), ('아이누', '이텔멘', 0.131, 0.127),
        ('아이누', '코랴크', 0.219, 0.100), ('아이누', '혼슈 일본인', 0.612, 0.043), ('아이누', '류큐', 0.539, 0.048)]
def chart_table5(mode):
    f, P = base(mode, 1300.0)
    L, R, T, B = 560.0, 1250.0, 80.0, 940.0
    X = lambda v: L + (v + 20) / 100.0 * (R - L)
    frame_x(f, L, T, R, B, X, [-20, 0, 20, 40, 60, 80], '1 - alpha (%): 조몬(F23) 쪽 몫. 가로선은 ±1.96 SE')
    C = cols(P, mode)
    f.line(X(0), T, X(0), B, P['text'], 2.4)
    rh = (B - T) / len(ROWS)
    cm = {'혼슈 일본인': C['a'], '류큐': C['b'], '아이누': C['d']}
    for i, (x, b, v, se) in enumerate(ROWS):
        y = T + (i + 0.5) * rh
        c = cm[x]
        f.text(L - 14, y + 10, '%s 대 %s' % (x, b), FS_I, 'end', P['text'], 400, False)
        f.line(X(100 * (v - 1.96 * se)), y, X(100 * (v + 1.96 * se)), y, c, 6.0)
        f.marker(X(100 * v), y, 'dot', 1.0, c)
    ly = B + 150
    note(f, 40, ly, '표 5를 이 책이 재구성한 값(계산 13-11). "혼슈 일본인 대 한국인"은 시험 집단이 혼슈 일본인이고 비교 집단이 한국인이라는 뜻. 이텔멘과 코랴크 줄은 구간이 0 아래로 내려간다. 같은 아이누가 비교 집단에 따라 13%에서 68%까지 움직인다.')
    return f

# ----------------------------------------------------------------- 그래프 4: 갈라진 때와 계통 나이
DIV = [('MSMC F23~한족 18~38', 18, 38, 'a'), ('MSMC F23~프랑스 40', 40, 40, 'a'), ('MSMC 한족~프랑스 40', 40, 40, 'a'), ('MSMC 카리티아나~F23 39', 39, 39, 'a'),
       ('MSMC 카리티아나~한족 38', 38, 38, 'a'), ('아메리카 원주민 갈래 36±1.5(인용)', 34.5, 37.5, 'b'), ('아메리카 원주민 흐름 25±1.1(인용)', 23.9, 26.1, 'b'),
       ('Gakuhari 인용 26', 26, 26, 'b'), ('mtDNA N9b 22(인용)', 22, 22, 'c'), ('mtDNA M7a 23(인용)', 23, 23, 'c'), ('Y 염색체 D1b 19.4(인용)', 19.4, 19.4, 'c')]
def chart_div(mode):
    f, P = base(mode, 1180.0)
    L, R, T, B = 600.0, 1250.0, 80.0, 800.0
    X = lambda v: L + v / 50.0 * (R - L)
    frame_x(f, L, T, R, B, X, [0, 10, 20, 30, 40, 50], '천 년 전 (ka)')
    C = cols(P, mode)
    rh = (B - T) / len(DIV)
    for i, (lab, s, e, k) in enumerate(DIV):
        y = T + (i + 0.5) * rh
        f.text(L - 14, y + 10, lab, FS_I, 'end', P['text'], 400, False)
        if s == e:
            f.marker(X(s), y, 'dot', 1.0, C[k])
        else:
            f.line(X(s), y, X(e), y, C[k], 8.0)
            f.line(X(s), y - 14, X(s), y + 14, C[k], 4.0)
            f.line(X(e), y - 14, X(e), y + 14, C[k], 4.0)
    ly = B + 150
    note(f, 40, ly, '위 다섯 줄은 Kanzawa-Kiriyama 등(2019)의 MSMC(세대 30년, 돌연변이율 1.25e-8). 가운데 둘은 같은 논문 또는 Gakuhari 등(2020)이 인용한 아메리카 원주민 갈래. 아래 셋은 한 계통의 공통 조상 나이로, 집단이 갈라진 때와 다른 사건이다(계산 13-9).')
    return f

# ----------------------------------------------------------------- 그래프 5: 미야모토 네 단계
def chart_miya(mode):
    f, P = base(mode, 1080.0)
    L, R, T, B = 130.0, 1250.0, 80.0, 640.0
    a0, a1 = -3800.0, -300.0
    X = lambda a: L + (a - a0) / (a1 - a0) * (R - L)
    fmt = lambda v: '기원전 %d' % -v
    frame_x(f, L, T, R, B, X, [-3500, -3000, -2500, -2000, -1500, -1000, -500], '달력 연대 (기원전). 각 단계는 논문의 "대략" 연대', fmt)
    C = cols(P, mode)
    st = [('1단계', '조 농사: 중국 동북에서 한반도 남부로', -3400, -3400), ('2단계', '논벼: 산둥에서 랴오둥으로', -2400, -2400),
          ('3단계', '관개 농업: 산둥에서 한반도로', -1500, -1500), ('4단계', '북부 규슈', -900, -700)]
    ys = [T + 70, T + 200, T + 330, T + 480]
    for (nm, lab, s, e), y in zip(st, ys):
        if s == e:
            f.marker(X(s), y, 'dot', 1.2, C['a'])
            if s == -1500:
                f.text(X(s) - 22, y + 10, '%s %s' % (nm, lab), FS_I, 'end', P['text'], 400, False)
            else:
                f.text(X(s) + 22, y + 10, '%s %s' % (nm, lab), FS_I, 'start', P['text'], 400, False)
        else:
            f.rect(X(s), y - 17, X(e) - X(s), 34, C['a'], P['frame'], 1.4)
            f.text(X(s) - 14, y + 10, '%s %s' % (nm, lab), FS_I, 'end', P['text'], 400, False)
    for (a, b, y, t) in ((-3400, -2400, ys[0] + 60, '1000년'), (-2400, -1500, ys[1] + 60, '900년'), (-1500, -800, ys[2] + 60, '600~800년')):
        f.line(X(a), y, X(b), y, C['d'], 2.4, '10 8')
        f.text((X(a) + X(b)) / 2, y + 30, t, FS_I, 'middle', C['d'] if mode == 'color' else '#111111', 700, False)
    ly = B + 150
    note(f, 40, ly, '네 단계 연대는 Miyamoto(2019)의 서술. 점선은 단계 사이의 간격(계산 13-13). 4단계는 기원전 9~8세기(900~700). 이 책이 읽은 논문은 이 네 단계에서 아이치현을 따로 다루지 않는다.')
    return f

if __name__ == '__main__':
    maps = [('map-japan13-v1', map_japan), ('map-atsumi13-v1', map_atsumi)]
    charts = [('chart-window13-v1', chart_window), ('chart-jomon13-v1', chart_jomon), ('chart-table513-v1', chart_table5),
              ('chart-div13-v1', chart_div), ('chart-miya13-v1', chart_miya)]
    for mode in ('color', 'bw'):
        for nm, fn in maps:
            f, pr = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
        for nm, fn in charts:
            f = fn(mode)
            print(nm, mode, 'warn', f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode))))
