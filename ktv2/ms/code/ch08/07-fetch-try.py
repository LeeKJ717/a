# -*- coding: utf-8 -*-
"""실습 8-7: 공개 지구화학·입도 자료 입수처가 이 컨테이너의 셸에서 내려받아지는가.
각 주소에 curl을 한 번씩 보내 상태 코드와 받은 바이트 수를 적는다. 막히면 우회하지 않는다.
대조용으로 패키지 저장소(pypi.org)도 한 번 시도한다."""
import subprocess, time
URLS = [
    ('PANGAEA 첫 화면', 'https://www.pangaea.de/'),
    ('PANGAEA DOI 해석 서버 첫 화면', 'https://doi.pangaea.de/'),
    ('NOAA NCEI 고기후 첫 화면', 'https://www.ncei.noaa.gov/products/paleoclimatology'),
    ('NOAA NCEI 고기후 검색', 'https://www.ncei.noaa.gov/access/paleo-search/'),
    ('NOAA NCEI 자료 폴더(Temperature 12k)', 'https://www.ncei.noaa.gov/pub/data/paleo/reconstructions/climate12k/temperature/version1.0.0/'),
    ('GEOROC', 'https://georoc.eu/'),
    ('(대조) PyPI numpy 목록', 'https://pypi.org/simple/numpy/'),
]
for name, u in URLS:
    t = time.time()
    p = subprocess.run(['curl', '-sS', '-m', '25', '-o', '/dev/null', '-w', '%{http_code} %{size_download}', '-L', u],
                       capture_output=True, text=True)
    out = p.stdout.strip()
    err = p.stderr.strip().replace('\n', ' ')
    print('%-60s 종료코드 %d  상태/바이트 [%s]  %s  (%.1f초)' % (name, p.returncode, out, err, time.time() - t))
