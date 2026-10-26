# -*- coding: utf-8 -*-
"""0장 실행 환경 기록."""
import sys, platform, pyproj, geopandas, shapely, matplotlib, numpy
print('python', sys.version.split()[0], platform.platform())
for m in (numpy, shapely, geopandas, pyproj, matplotlib):
    print(m.__name__, m.__version__)
print('PROJ', pyproj.proj_version_str)
