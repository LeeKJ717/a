# -*- coding: utf-8 -*-
"""실습 14-0: 실행 환경 기록."""
import sys, platform, shutil, sqlite3
import numpy, pandas, shapely, pyproj, geopandas, matplotlib
print('python      ', sys.version.split()[0], platform.platform())
print('sqlite3     ', sqlite3.sqlite_version, '(파이썬 표준 라이브러리 sqlite3)')
for m in (numpy, pandas, shapely, pyproj, geopandas, matplotlib):
    print('%-12s' % m.__name__, m.__version__)
print('GPU(nvidia-smi)', shutil.which('nvidia-smi') or '없음')
import sqlite3 as s
c = s.connect(':memory:')
print('JSON1 함수', c.execute("SELECT json_valid('{}')").fetchone()[0] == 1, ' FTS5', any('FTS5' in r[0] for r in c.execute('PRAGMA compile_options')))
print('외래 키 기본값(PRAGMA foreign_keys)', c.execute('PRAGMA foreign_keys').fetchone()[0], '-> 연결할 때마다 켜야 한다')
