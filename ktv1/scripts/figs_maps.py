# -*- coding: utf-8 -*-
"""figs_maps v1 - 기본 지도 6장 (지리 사실만: 해안선·강·산·도시·유적 좌표)
실행: python3 scripts/figs_maps.py  -> fig/<이름>-color.svg, fig/<이름>-bw.svg
지명은 한국 한자음으로 쓰고, 한자 정자와 병음은 본문의 지명 대조표에 둔다.
자료: Natural Earth (퍼블릭 도메인). 도시 좌표는 공개 지리 좌표, 유적 좌표는 geo.md 의 요하문명 목록.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomap as G
from geomap import basemap, city, area, scalebar, north, inset, legend, on_river, range_label, peak, FS, FS_S, FS_I

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
os.makedirs(OUT, exist_ok=True)

# 산(Natural Earth 표고점) 좌표를 자료에서 읽는다
PEAK = {}
for g, p in G.layer('ne_10m_geography_regions_elevation_points'):
    if p.get('name'):
        PEAK[p['name']] = (g.x, g.y)

RIV_ALL = {'Huang', 'Wei', 'Fen', 'Luan', 'Hai', 'Huai', 'Yangtze', 'Chang Jiang', 'Liao', 'Xiliao', 'Songhua',
           'Di’er Songhua', 'Nen', 'Amur', 'Yalu', 'Tumen', 'Han', 'Namhan', 'Nakdong'}

# 도시 (경도, 위도) - 한국 한자음
C = dict(서울=(126.98, 37.57), 평양=(125.75, 39.02), 부산=(129.08, 35.18), 북경=(116.40, 39.90),
         상해=(121.47, 31.23), 서안=(108.94, 34.34), 낙양=(112.45, 34.62), 성도=(104.07, 30.67),
         심양=(123.43, 41.80), 대련=(121.62, 38.92), 합이빈=(126.64, 45.76), 남경=(118.80, 32.06),
         무한=(114.31, 30.59), 도쿄=(139.69, 35.69), 오사카=(135.50, 34.69), 후쿠오카=(130.40, 33.59),
         삿포로=(141.35, 43.06), 장춘=(125.32, 43.88), 적봉=(118.96, 42.29), 조양=(120.45, 41.57),
         난주=(103.83, 36.06), 은천=(106.23, 38.49), 태원=(112.55, 37.87), 정주=(113.62, 34.75),
         천진=(117.20, 39.13), 항주=(120.16, 30.27), 울란바토르=(106.92, 47.92))
SITE = {'우하량': (119.50, 41.33), '흥륭와': (120.63, 42.40), '조보구': (120.20, 42.33), '부하구문': (119.35, 43.95)}
ULLEUNG = (130.87, 37.50)


def finish(f, pr, name, warns, extra=None):
    w = f.save(os.path.join(OUT, '%s-%s.svg' % (name, f.mode)))
    warns.extend('[%s %s] %s' % (name, f.mode, x) for x in w)


def check_points():
    bad = []
    for k, (lo, la) in list(C.items()) + list(SITE.items()) + [('울릉도', ULLEUNG)]:
        if not G.pt_check(lo, la, True):
            bad.append(k)
    return bad


def stamp(f, pr, pad_items, km, sb_x=40):
    """아래 띠: 범례 + 축척 막대."""
    y0 = pr.h + 56
    last = legend(f, 30, y0, pad_items)
    scalebar(f, pr, sb_x, last + 76, km)


# ------------------------------------------------------------------ 1. 연구 범위
def map_study(mode):
    bbox = (100.0, 24.0, 146.0, 54.0)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers=RIV_ALL, lakes=True, grid=10,
                    ranges=['GREATER KHINGAN RANGE', 'Lesser Khingan Range', 'SIKHOTE-ALIN’ RANGE', 'Taihang Mts.', 'Qinling Mountains', 'Yin Mts.', 'Hamgyong Mts.'])
    P = f.P
    for lon, lat, s in [(123.6, 35.7, '황해'), (133.0, 40.6, '동해'), (126.0, 28.6, '동중국해')]:
        area(f, pr, lon, lat, s, FS, P['soft'], where='sea')
    for lon, lat, s in [(106.0, 46.2, '몽골고원'), (108.3, 35.4, '황토고원'), (123.8, 44.6, '송요평원'),
                        (105.8, 29.3, '사천분지'), (118.0, 38.0, '화북평원')]:
        area(f, pr, lon, lat, s, FS_S, P['soft'], 700, 2.0, where='land')
    area(f, pr, 108.0, 39.9, '오르도스', FS_S, P['soft'], 700, 1.0, where='land')
    for key, nm, hint, dx, dy, an in [('Huang', '황하', (116.2, 36.9), 14, -8, 'start'),
                                      ('Yangtze', '장강', (112.4, 30.1), 14, 28, 'start'),
                                      ('Liao', '요하', (122.4, 41.5), 12, -6, 'start')]:
        names = {key, 'Chang Jiang'} if key == 'Yangtze' else {key}
        pt, d = on_river(names, hint)
        x, y = pr(*pt)
        f.text(x + dx, y + dy, nm, FS_S, an, P['river'], 700)
    for nm, dx, dy, an, big in [('서울', 14, 8, 'start', True), ('평양', -14, -4, 'end', False), ('북경', -14, -8, 'end', True),
                                ('서안', -14, -8, 'end', True), ('낙양', 14, 28, 'start', False), ('상해', 14, 10, 'start', False),
                                ('도쿄', 14, 8, 'start', True), ('심양', -14, -6, 'end', False), ('성도', 14, -10, 'start', False)]:
        city(f, pr, *C[nm], nm, dx, dy, an, big=big)
    peak(f, pr, 'Paektu-san', '백두산', 14, -8)
    for ne, ko, pos in [('GREATER KHINGAN RANGE', '대흥안령', None), ('Lesser Khingan Range', '소흥안령', None),
                        ('SIKHOTE-ALIN’ RANGE', '시호테알린산맥', (134.2, 44.9)), ('Taihang Mts.', '태행산맥', None),
                        ('Qinling Mountains', '진령산맥', (110.6, 33.0)), ('Yin Mts.', '음산산맥', None)]:
        range_label(f, pr, bbox, ne, ko, pos)
    x, y = pr(*SITE['우하량'])
    f.marker(x, y, 'star', 0.9, P['site'])
    f.text(x - 14, y - 10, '우하량', FS_S, 'end', P['site'], 700)
    inset(f, (40, 0, 160, 75), bbox, pr.w - 290, 28, 260, marks=[(116, 40, '동아시아', -2, -22, 'middle')], title='이 그림의 위치')
    north(f, pr.w - 70, 560, 100)
    stamp(f, pr, [('river', '강'), ('range', '산지(개략 범위)'), ('tri', '봉우리(높이)'), ('star', '유적'), ('dot', '도시')], 500)
    return f, pr


# ------------------------------------------------------------------ 2. 한반도와 주변 바다
def map_korea(mode):
    bbox = (123.3, 32.3, 132.4, 43.7)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Yalu', 'Tumen', 'Han', 'Namhan', 'Nakdong'}, grid=2, ranges=['Hamgyong Mts.'])
    P = f.P
    area(f, pr, 124.6, 36.2, '황해', FS, P['soft'], where='sea')
    area(f, pr, 130.9, 40.3, '동해', FS, P['soft'], where='sea')
    area(f, pr, 127.3, 32.75, '남해', FS_S, P['soft'], 700, 2.0, where='sea')
    area(f, pr, 128.3, 34.1, '대한해협', FS_I, P['soft'], 700, 0.0, where='sea')
    for nm, dx, dy, an, big in [('서울', -14, 22, 'end', True), ('평양', -14, 8, 'end', True), ('부산', -10, 30, 'end', False)]:
        city(f, pr, *C[nm], nm, dx, dy, an, big=big)
    for nm, key, dx, dy, an in [('백두산', 'Paektu-san', -14, -12, 'end'), ('한라산', 'Halla-san', 14, 8, 'start'),
                                ('설악산', 'Sorak-san', -14, 6, 'end'), ('지리산', 'Chiri-san', -14, 8, 'end')]:
        peak(f, pr, key, nm, dx, dy, an)
    range_label(f, pr, bbox, 'Hamgyong Mts.', '함경산맥')
    x, y = pr(*ULLEUNG)
    f.marker(x, y, 'tri', 0.9, P['hot'])
    f.text(x + 14, y + 8, '울릉도', FS_S, 'start', P['hot'], 700)
    for key, nm, hint, dx, dy, an in [('Yalu', '압록강', (125.6, 40.3), -12, -6, 'end'),
                                      ('Tumen', '두만강', (129.3, 42.5), 14, 4, 'start'),
                                      ('Nakdong', '낙동강', (128.7, 35.9), 14, 6, 'start')]:
        pt, d = on_river({key}, hint)
        x, y = pr(*pt)
        f.text(x + dx, y + dy, nm, FS_S, an, P['river'], 700)
    pt, d = on_river({'Han', 'Namhan'}, (127.6, 37.4))
    x, y = pr(*pt)
    f.text(x + 14, y - 12, '한강', FS_S, 'start', P['river'], 700)
    inset(f, (95, 15, 150, 55), bbox, pr.w - 290, 560, 270, marks=[(126.9, 37.5, '한반도', 8, 28, 'start')], title='이 그림의 위치')
    north(f, 70, 80, 100)
    stamp(f, pr, [('river', '강'), ('range', '산지(개략 범위)'), ('tri', '봉우리(높이)·화산'), ('dot', '도시')], 200)
    f.text(330, pr.h + 150, '※ 태백·소백산맥은 자료에 없어 음영 생략', FS_I, 'start', P['soft'], 400, False)
    return f, pr


# ------------------------------------------------------------------ 3. 황하·황토고원·화북
def map_yellow(mode):
    bbox = (100.0, 31.5, 122.6, 42.8)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Huang', 'Wei', 'Fen', 'Luan', 'Hai', 'Huai', 'Yangtze', 'Chang Jiang'},
                    lakes=True, grid=5, latside='right',
                    ranges=['Taihang Mts.', 'Lüliang Mts.', 'Qinling Mountains', 'Yin Mts.', 'QUILIAN MOUNTAINS'])
    P = f.P
    area(f, pr, 119.6, 38.55, '발해만', FS_I, P['soft'], 700, 0.0, where='sea')
    area(f, pr, 121.4, 34.6, '황해', FS, P['soft'], where='sea')
    for lon, lat, s in [(107.9, 36.0, '황토고원'), (116.3, 38.0, '화북평원')]:
        area(f, pr, lon, lat, s, FS_S, P['soft'], 700, 2.0, where='land')
    area(f, pr, 108.6, 38.0, '오르도스', FS_S, P['soft'], 700, 1.0, where='land')
    for key, nm, hint, dx, dy, an in [('Huang', '황하', (108.5, 40.7), 0, -14, 'middle'),
                                      ('Wei', '위하', (106.4, 34.9), 0, -14, 'middle'),
                                      ('Fen', '분하', (111.7, 37.1), -12, 0, 'end'),
                                      ('Huai', '회하', (114.6, 32.4), 0, -14, 'middle'),
                                      ('Hai', '해하', (117.1, 39.2), -14, 34, 'end'),
                                      ('Luan', '난하', (118.4, 40.0), 14, 6, 'start')]:
        pt, d = on_river({key}, hint)
        x, y = pr(*pt)
        f.text(x + dx, y + dy, nm, FS_S, an, P['river'], 700)
    pt, d = on_river({'Huang'}, (116.9, 36.9))
    x, y = pr(*pt)
    f.text(x + 12, y + 26, '황하', FS_S, 'start', P['river'], 700)
    for nm, dx, dy, an, big in [('서안', 14, 30, 'start', True), ('낙양', 14, 26, 'start', True), ('정주', 14, 22, 'start', False),
                                ('태원', -14, 8, 'end', False), ('북경', 14, -8, 'start', True), ('난주', 14, 8, 'start', False),
                                ('은천', 14, -8, 'start', False), ('천진', 14, 8, 'start', False)]:
        city(f, pr, *C[nm], nm, dx, dy, an, big=big)
    for ne, ko, pos in [('Taihang Mts.', '태행산맥', (114.1, 35.6)), ('Lüliang Mts.', '여량산맥', (111.0, 35.6)),
                        ('Qinling Mountains', '진령산맥', (111.6, 33.3)), ('Yin Mts.', '음산산맥', None)]:
        range_label(f, pr, bbox, ne, ko, pos)
    peak(f, pr, 'Hua Shan', '화산', 12, -30, 'start')
    peak(f, pr, 'Taibai Shan', '태백산(진령)', -12, -12, 'end')
    peak(f, pr, 'Helan Shan', '하란산', -12, 26, 'end')
    peak(f, pr, 'Wutai Shan', '오대산(산서)', -12, -12, 'end')
    inset(f, (80, 10, 150, 55), bbox, 30, 30, 250, marks=[(116, 40, '북경', 4, -14, 'middle')], title='이 그림의 위치')
    stamp(f, pr, [('river', '강'), ('range', '산지(개략 범위)'), ('tri', '봉우리(높이)'), ('dot', '도시')], 200)
    north(f, pr.w - 70, 70, 100)
    return f, pr


# ------------------------------------------------------------------ 4. 요하·동북 (홍산)
def map_liao(mode):
    bbox = (115.5, 37.8, 132.5, 47.7)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Liao', 'Xiliao', 'Songhua', 'Di’er Songhua', 'Nen', 'Yalu', 'Tumen', 'Luan', 'Hai', 'Amur'},
                    lakes=True, grid=5, latside='right', ranges=['GREATER KHINGAN RANGE', 'Lesser Khingan Range', 'Hamgyong Mts.'])
    P = f.P
    area(f, pr, 119.2, 38.4, '발해만', FS_I, P['soft'], 700, 0.0, where='sea')
    area(f, pr, 124.4, 38.6, '황해', FS, P['soft'], where='sea')
    area(f, pr, 130.6, 38.9, '동해', FS, P['soft'], where='sea')
    for key, nm, hint, dx, dy, an in [('Liao', '요하', (122.2, 41.6), -12, 4, 'end'),
                                      ('Xiliao', '서요하', (122.0, 43.45), 0, 26, 'middle'),
                                      ('Nen', '눈강', (123.6, 46.5), -12, 4, 'end'),
                                      ('Yalu', '압록강', (125.7, 40.6), 14, 10, 'start'),
                                      ('Tumen', '두만강', (129.6, 42.6), 14, 6, 'start'),
                                      ('Luan', '난하', (118.4, 40.3), -12, 4, 'end')]:
        pt, d = on_river({key}, hint)
        x, y = pr(*pt)
        f.text(x + dx, y + dy, nm, FS_S, an, P['river'], 700)
    pt, d = on_river({'Songhua', 'Di’er Songhua'}, (126.8, 45.2))
    x, y = pr(*pt)
    f.text(x + 14, y - 12, '송화강', FS_S, 'start', P['river'], 700)
    for nm, dx, dy, an, big in [('심양', 14, -10, 'start', True), ('대련', -14, 30, 'end', False), ('조양', 14, 8, 'start', False),
                                ('합이빈', -14, -12, 'end', False), ('장춘', 14, -10, 'start', False), ('평양', 14, 26, 'start', False)]:
        city(f, pr, *C[nm], nm, dx, dy, an, big=big)
    for nm, dx, dy, an in [('우하량', -14, 30, 'end'), ('흥륭와', 16, -12, 'start'), ('조보구', -16, 40, 'end'), ('부하구문', 14, -8, 'start')]:
        x, y = pr(*SITE[nm])
        f.marker(x, y, 'star', 0.9, P['site'])
        f.text(x + dx, y + dy, nm, FS_S, an, P['site'], 700)
    city(f, pr, *C['적봉'], '적봉', -14, -8, 'end', kind='sq')
    peak(f, pr, 'Paektu-san', '백두산', 14, -8)
    for ne, ko, dx in [('GREATER KHINGAN RANGE', '대흥안령', 90), ('Lesser Khingan Range', '소흥안령', 0), ('Hamgyong Mts.', '함경산맥', 0)]:
        range_label(f, pr, bbox, ne, ko, dx=dx)
    inset(f, (95, 15, 150, 55), bbox, 30, 30, 260, marks=[(116, 40, '북경', 6, -12, 'middle')], title='이 그림의 위치')
    north(f, pr.w - 70, 70, 100)
    stamp(f, pr, [('river', '강'), ('range', '산지(개략 범위)'), ('star', '요하문명 유적'), ('tri', '봉우리(높이)'), ('dot', '도시')], 200)
    return f, pr


# ------------------------------------------------------------------ 5. 장강 유역
def map_yangtze(mode):
    bbox = (101.0, 24.5, 123.2, 35.6)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Yangtze', 'Chang Jiang', 'Han', 'Huai'}, lakes=True, grid=5, latside='right',
                    ranges=['Qinling Mountains', 'Dabie Mts.', 'Wuyi Mts.', 'Dalou Mts.'])
    P = f.P
    area(f, pr, 121.9, 34.6, '황해', FS_S, P['soft'], 700, 2.0, where='sea')
    area(f, pr, 106.9, 30.7, '사천분지', FS_S, P['soft'], 700, 2.0, where='land')
    for key, nm, hint, dx, dy, an in [('Yangtze', '장강', (110.9, 30.7), 0, -14, 'middle'),
                                      ('Huai', '회하', (115.3, 32.5), 0, -14, 'middle')]:
        names = {key, 'Chang Jiang'} if key == 'Yangtze' else {key}
        pt, d = on_river(names, hint)
        x, y = pr(*pt)
        f.text(x + dx, y + dy, nm, FS_S, an, P['river'], 700)
    pt, d = on_river({'Han'}, (109.7, 32.9))
    x, y = pr(*pt)
    f.text(x + 10, y - 12, '한수', FS_S, 'start', P['river'], 700)
    for nm, dx, dy, an, big in [('성도', 14, -10, 'start', True), ('무한', -14, 26, 'end', True), ('남경', 14, -8, 'start', True),
                                ('상해', 14, 8, 'start', True), ('항주', -14, 26, 'end', False)]:
        city(f, pr, *C[nm], nm, dx, dy, an, big=big)
    for nm, lon, lat, dx, dy, an in [('동정호', 112.9, 29.3, 0, 36, 'middle'), ('파양호', 116.3, 29.0, 14, 36, 'start'), ('태호', 120.2, 31.2, 0, 40, 'middle')]:
        x, y = pr(lon, lat)
        f.text(x + dx, y + dy, nm, FS_I, an, P['river'], 400)
    for ne, ko, pos in [('Qinling Mountains', '진령산맥', (112.8, 33.4)), ('Dabie Mts.', '대별산', None), ('Wuyi Mts.', '무이산', None), ('Dalou Mts.', '대루산', None)]:
        range_label(f, pr, bbox, ne, ko, pos)
    peak(f, pr, 'Taibai Shan', '태백산(진령)', 14, -10)
    peak(f, pr, 'Daba Shan', '대파산', 14, -10)
    peak(f, pr, 'Gongga Shan', '공가산', 14, 8)
    inset(f, (80, 10, 150, 55), bbox, 30, 30, 250, marks=[(116, 40, '북경', 4, -14, 'middle')], title='이 그림의 위치')
    north(f, 60, pr.h - 130, 100)
    stamp(f, pr, [('river', '강'), ('range', '산지(개략 범위)'), ('tri', '봉우리(높이)'), ('dot', '도시')], 200)
    return f, pr


# ------------------------------------------------------------------ 6. 일본열도와 동해
def map_japan(mode):
    bbox = (128.0, 30.0, 146.6, 46.0)
    f, pr = basemap(bbox, pad=190, mode=mode, grid=5)
    P = f.P
    area(f, pr, 133.4, 40.6, '동해', FS, P['soft'], where='sea')
    area(f, pr, 144.2, 37.5, '태평양', FS, P['soft'], where='sea')
    for lon, lat, s in [(143.6, 43.3, '홋카이도'), (138.3, 37.2, '혼슈'), (131.1, 32.7, '규슈'), (133.3, 33.75, '시코쿠')]:
        area(f, pr, lon, lat, s, FS_S, P['soft'], 700, 1.0, where='land')
    for nm, dx, dy, an, big in [('도쿄', 14, -8, 'start', True), ('오사카', -14, 8, 'end', True), ('후쿠오카', 14, -8, 'start', False), ('삿포로', 14, 8, 'start', False)]:
        city(f, pr, *C[nm], nm, dx, dy, an, big=big)
    x, y = pr(129.3, 34.4)
    f.marker(x, y, 'dot', 0.9, P['text'])
    f.text(x + 14, y - 8, '대마도', FS_S, 'start', P['text'], 400)
    peak(f, pr, 'Fuji', '후지산', -14, 24, 'end')
    peak(f, pr, 'Tate-yama', '다테야마', -14, -12, 'end')
    peak(f, pr, 'Iwate-san', '이와테산', 14, 8)
    peak(f, pr, 'Asahi-dake', '아사히다케', -14, 8, 'end')
    x, y = pr(*ULLEUNG)
    f.marker(x, y, 'tri', 0.9, P['hot'])
    f.text(x - 14, y - 10, '울릉도', FS_S, 'end', P['hot'], 700)
    inset(f, (95, 15, 160, 55), bbox, pr.w - 290, pr.h - 300, 260, marks=[(126.9, 37.5, '한반도', -4, 40, 'end')], title='이 그림의 위치')
    north(f, 60, pr.h - 230, 100)
    stamp(f, pr, [('tri', '봉우리(높이)·화산'), ('dot', '도시')], 200)
    return f, pr


# ------------------------------------------------------------------ 7. 2장 해수면·단구 조사 지점
SITES2 = {'김제': (126.88, 35.80), '포항 A·B': (129.397, 35.999), '동수악': (126.628, 33.361),
          '강릉': (128.896, 37.756), '주문진': (128.83, 37.89), '방어진': (129.43, 35.49), '울산': (129.315, 35.549)}


def map_sites2(mode):
    bbox = (125.4, 32.9, 130.6, 38.4)
    f, pr = basemap(bbox, pad=170, mode=mode, rivers={'Han', 'Namhan', 'Nakdong'}, grid=1)
    P = f.P
    area(f, pr, 125.9, 36.6, '황해', FS, P['soft'], where='sea')
    area(f, pr, 130.15, 36.0, '동해', FS, P['soft'], where='sea')
    area(f, pr, 128.0, 33.3, '남해', FS_S, P['soft'], 700, 2.0, where='sea')
    for nm, dx, dy, an in [('김제', 14, 8, 'start'), ('포항 A·B', 14, 8, 'start'), ('동수악', 14, 22, 'start'),
                           ('강릉', -14, 8, 'end'), ('주문진', -14, -6, 'end'), ('방어진', 14, 8, 'start'), ('울산', -14, 8, 'end')]:
        lon, lat = SITES2[nm]
        city(f, pr, lon, lat, nm, dx, dy, an, big=nm in ('김제', '포항 A·B', '동수악'))
    for nm, key, dx, dy, an in [('한라산', 'Halla-san', -14, -12, 'end'), ('지리산', 'Chiri-san', -14, 8, 'end'),
                                ('설악산', 'Sorak-san', -14, 6, 'end')]:
        peak(f, pr, key, nm, dx, dy, an)
    inset(f, (95, 15, 150, 55), bbox, pr.w - 290, pr.h - 640, 270, marks=[(127.9, 36.0, '한반도', 8, 28, 'start')], title='이 그림의 위치')
    north(f, 70, 80, 100)
    stamp(f, pr, [('river', '강'), ('tri', '봉우리(높이)'), ('dot', '조사 지점')], 100)
    f.text(330, pr.h + 150, '※ 포항·동수악은 논문 좌표, 김제·주문진·방어진은 개략', FS_I, 'start', P['soft'], 400, False)
    return f, pr


MAPS = [('map-study-area-v1', map_study), ('map-korea-v1', map_korea), ('map-yellow-river-v1', map_yellow),
        ('map-liao-v1', map_liao), ('map-yangtze-v1', map_yangtze), ('map-japan-v1', map_japan), ('map-sites2-v1', map_sites2)]

if __name__ == '__main__':
    bad = check_points()
    print('좌표 검사(육지 아님):', bad or '없음')
    warns = []
    for name, fn in MAPS:
        for mode in ('color', 'bw'):
            f, pr = fn(mode)
            finish(f, pr, name, warns)
        print(name, 'ok  %.1f x %.1f mm' % (f.w / 10, f.h / 10))
    print('경고 %d건' % len(warns))
    for w in warns:
        print(' ', w)
