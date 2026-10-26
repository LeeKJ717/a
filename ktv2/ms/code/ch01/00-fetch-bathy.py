# -*- coding: utf-8 -*-
"""실습 1-0b: 수심 층 5개(1000~5000 m)를 Natural Earth 공식 GitHub 저장소에서 내려받는다.
제1권 geodata 에는 200 m 층(K_200)만 있다. 이미 파일이 있으면 내려받지 않고 해시만 적는다.
  python3 00-fetch-bathy.py          (없는 파일만 내려받기)
  python3 00-fetch-bathy.py --verify (모두 다시 내려받아 해시를 대조, 임시 폴더에 저장)
"""
import hashlib, os, sys, tempfile, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapkit as K

BASE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
NAMES = [nm for d, nm in K.BATHY if d != 200]
os.makedirs(K.DATA, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def get(nm, dest):
    with urllib.request.urlopen(BASE + nm + '.geojson', timeout=120) as r, open(dest, 'wb') as f:
        f.write(r.read())

verify = '--verify' in sys.argv
tmp = tempfile.mkdtemp()
for nm in NAMES + ['ne_10m_bathymetry_K_200']:
    local = os.path.join(K.DATA, nm + '.geojson') if nm != 'ne_10m_bathymetry_K_200' else os.path.join(K.GEO, nm + '.geojson')
    if verify or not os.path.exists(local):
        dest = os.path.join(tmp, nm + '.geojson') if verify else local
        get(nm, dest)
        if verify:
            print('%-28s 로컬 %s  새로 받음 %s  %s' % (nm, sha(local)[:12], sha(dest)[:12], '같음' if sha(local) == sha(dest) else '다름'))
            continue
    print('%-28s %10d 바이트  sha256 %s' % (nm, os.path.getsize(local), sha(local)[:16]))
