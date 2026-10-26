# -*- coding: utf-8 -*-
"""8장 지도: 황토고원·한강 중류·동해 코어 지점. 좌표는 각 논문 본문의 표기."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomap as G
from geomap import basemap, area, scalebar, north, legend, FS, FS_S, FS_I
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
def dms(d, m=0, s=0): return d + m/60 + s/3600
S = [(1, dms(109,25), dms(35,45), 'tri'),            # 뤄촨 (Lu 2007)
     (2, dms(108,54,14.4), dms(37,29,52.8), 'tri'),  # 징볜 구역 A (Stevens 2018)
     (3, 103.63, 35.15, 'tri'),                       # 위안바오 (Rao 2013)
     (4, 104.6, 36.35, 'tri'),                        # 징위안 (Rao 2013)
     (5, dms(127,10,39.8), dms(37,34,25.0), 'dot'),   # 하남 망월동 (Ahn 2024)
     (6, dms(134,44), dms(42,56), 'sq')]              # 동해 코어 LV53-18-2 (Dou 2021)
def make(mode):
    bbox = (100.0, 30.0, 138.0, 46.0)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Huang','Han','Yalu'}, grid=10)
    P = f.P
    area(f, pr, 122.0, 36.0, '황해', FS_S, P['soft'], where='sea')
    area(f, pr, 133.0, 39.2, '동해', FS, P['soft'], where='sea')
    for n, lo, la, k in S:
        x, y = pr(lo, la)
        f.marker(x, y, k, 1.0, P['hot'] if n in (5, 6) else P['text'])
        dx, dy = 12, -8
        if n == 3: dx, dy = -12, 24
        f.text(x + dx, y + dy, str(n), FS_S, 'end' if n == 3 else 'start', P['hot'] if n in (5, 6) else P['text'], 700)
    north(f, 70, 130, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('tri', '황토 단면(1~4)'), ('dot', '한강 중류 고토양(5)'), ('sq', '동해 퇴적물 코어(6)'), ('river', '강')])
    scalebar(f, pr, 40, last + 76, 500)
    f.text(30, pr.h + 160, '※ 번호는 8.1절 표의 지점 번호', FS_I, 'start', P['soft'], 400, False)
    return f, pr
if __name__ == '__main__':
    for mode in ('color', 'bw'):
        f, pr = make(mode)
        w = f.save(os.path.join(OUT, 'map-loess-sites-v1-%s.svg' % mode))
        print(mode, 'warn', w)
