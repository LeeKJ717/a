# -*- coding: utf-8 -*-
"""6장 지도: 이 장의 8개 기록 지점. 좌표는 각 논문 본문의 도분초 표기를 십진도로 바꾼 값."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomap as G
from geomap import basemap, area, scalebar, north, legend, FS, FS_S, FS_I
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
def dms(d, m=0, s=0): return d + m/60 + s/3600
S = [(1, dms(125,54,36), dms(34,44,5), 'dot'),      # 비금도 (Park 2018)
     (2, dms(127,46,40.94), dms(35,0,20.48), 'dot'),  # 섬진강 하구 GY-1 (Park 2019)
     (3, dms(126,37,40), dms(33,21,41), 'dot'),       # 동수악 (Park 2023)
     (4, dms(117,30.356,0), dms(49,7.615,0), 'sq'),   # HL06 (Xiao 2018)
     (5, dms(117,15), dms(28,42), 'tri'),             # Shennong cave (Zhang 2018)
     (6, dms(108,5), dms(25,17), 'tri'),              # Dongge cave (Liu & Hu 2016)
     (7, dms(110,25), dms(30,27), 'tri'),             # Heshang cave (Liu & Hu 2016)
     (8, dms(108,3), dms(26,16), 'tri')]              # Liangfeng cave (Liu & Hu 2016)
def make(mode):
    bbox = (100.0, 22.0, 134.0, 52.0)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Huang','Yangtze','Chang Jiang','Yalu','Han'}, grid=10)
    P = f.P
    area(f, pr, 124.0, 36.5, '황해', FS_S, P['soft'], where='sea')
    area(f, pr, 132.5, 40.5, '동해', FS, P['soft'], where='sea')
    for n, lo, la, k in S:
        x, y = pr(lo, la)
        f.marker(x, y, k, 1.0, P['hot'] if n in (1, 2, 3) else P['text'])
        dx, dy = 12, -8
        if n == 8: dx, dy = -12, 26
        f.text(x + dx, y + dy, str(n), FS_S, 'end' if n == 8 else 'start', P['hot'] if n in (1, 2, 3) else P['text'], 700)
    north(f, 1220, 120, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('dot', '한반도의 퇴적물 코어(1~3)'), ('sq', '호수 코어(4)'), ('tri', '동굴 석순(5~8)'), ('river', '강')])
    scalebar(f, pr, 40, last + 76, 500)
    f.text(30, pr.h + 160, '※ 번호는 6.1절 표의 지점 번호', FS_I, 'start', P['soft'], 400, False)
    return f, pr
if __name__ == '__main__':
    for mode in ('color', 'bw'):
        f, pr = make(mode)
        w = f.save(os.path.join(OUT, 'map-events-sites-v1-%s.svg' % mode))
        print(mode, 'warn', w)
