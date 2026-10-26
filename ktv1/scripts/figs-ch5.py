# -*- coding: utf-8 -*-
"""5장 지도: Park et al.(2017) 표 1의 기록 지점 21곳 + 물영아리 + Shi et al.(2014) CSH1 코어. 좌표는 논문 표(Park) 및 본문(Shi)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomap as G
from geomap import basemap, area, scalebar, north, legend, FS, FS_S, FS_I
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig')
S = [(1,129.87,30.85),(2,126.68,33.37),(3,122.49,24.80),(4,121.70,24.75),(5,121.60,24.50),(6,117.84,32.36),(7,117.00,27.50),
     (8,112.80,16.75),(9,110.67,19.30),(10,110.28,21.15),(11,139.70,39.93),(12,126.35,42.30),(13,122.88,42.87),(14,118.03,36.40),
     (15,116.60,43.26),(16,115.12,36.40),(17,112.23,38.90),(18,110.42,30.45),(19,108.08,25.28),(20,105.00,33.58),(21,104.78,35.45)]
CSH1 = (128.7233, 31.2283)   # 31°13.70′N, 128°43.40′E
def make(mode):
    bbox = (100.0, 14.0, 144.0, 46.0)
    f, pr = basemap(bbox, pad=190, mode=mode, rivers={'Huang','Yangtze','Chang Jiang','Yalu','Han'}, grid=10)
    P = f.P
    area(f, pr, 124.5, 36.0, '황해', FS_S, P['soft'], where='sea')
    area(f, pr, 133.5, 40.5, '동해', FS, P['soft'], where='sea')
    area(f, pr, 116.8, 19.2, '남중국해', FS, P['soft'], where='sea')
    area(f, pr, 127.0, 26.5, '동중국해', FS_S, P['soft'], 700, 2.0, where='sea')
    for n, lo, la in S:
        x, y = pr(lo, la)
        coast = n <= 10
        f.marker(x, y, 'dot' if coast else 'sq', 1.15 if n == 2 else 0.95, P['hot'] if n == 2 else P['text'])
        dy = 26 if n == 5 else -8
        f.text(x + 12, y + dy, str(n), FS_S, 'start', P['hot'] if n == 2 else P['text'], 700)
    x, y = pr(*CSH1)
    f.marker(x, y, 'star', 1.2, P['site'])
    f.text(x - 12, y + 26, 'CSH1', FS_I, 'end', P['site'], 700)
    north(f, 70, 80, 100)
    y0 = pr.h + 56
    last = legend(f, 30, y0, [('dot', '해안 지점(1~10)'), ('sq', '내륙 지점(11~21)'), ('star', 'CSH1 코어'), ('river', '강')])
    scalebar(f, pr, 40, last + 76, 500)
    f.text(30, pr.h + 160, '※ 번호는 5.3절 표의 지점 번호. 2번 물영아리(주황)는 제주 습지', FS_I, 'start', P['soft'], 400, False)
    return f, pr
if __name__ == '__main__':
    for mode in ('color', 'bw'):
        f, pr = make(mode)
        w = f.save(os.path.join(OUT, 'map-monsoon-sites-v1-%s.svg' % mode))
        print(mode, 'warn', w)
