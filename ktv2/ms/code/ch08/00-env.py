# -*- coding: utf-8 -*-
"""실습 8-0: 실행 환경 기록. 이 장의 모든 실행 로그가 어떤 버전에서 나온 것인지 남긴다."""
import sys, platform, shutil, os
import numpy, scipy
print('python  ', sys.version.split()[0], platform.platform())
for m in (numpy, scipy):
    print('%-10s' % m.__name__, m.__version__)
print('CPU 코어', os.cpu_count())
print('GPU(nvidia-smi)', shutil.which('nvidia-smi') or '없음')
print('sedkit.py 크기(바이트)', os.path.getsize(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sedkit.py')))
