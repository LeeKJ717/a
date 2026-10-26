# -*- coding: utf-8 -*-
"""실습 1-0: 실행 환경 기록. 이 장의 모든 실행 로그가 어떤 버전에서 나온 것인지 남긴다."""
import sys, platform, shutil, subprocess
import numpy, pandas, scipy, shapely, pyproj, geopandas, pyogrio, matplotlib
print('python      ', sys.version.split()[0], platform.platform())
for m in (numpy, pandas, scipy, shapely, pyproj, geopandas, pyogrio, matplotlib):
    print('%-12s' % m.__name__, m.__version__)
print('GEOS        ', shapely.geos_version_string)
print('PROJ        ', pyproj.proj_version_str)
print('GDAL(pyogrio)', pyogrio.__gdal_version_string__)
print('PROJ 자료 폴더', pyproj.datadir.get_data_dir())
print('GPU(nvidia-smi)', shutil.which('nvidia-smi') or '없음')
from matplotlib import font_manager as fm
fs = sorted({f.fname for f in fm.fontManager.ttflist if 'Noto Sans CJK KR' == f.name})
print('Noto Sans CJK KR 파일', len(fs), '개')
for f in fs: print('  ', f)
