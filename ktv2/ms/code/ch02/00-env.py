# -*- coding: utf-8 -*-
"""2장 실습 2-0: 실행 환경과 네트워크 접속 확인. 실행: python3 00-env.py | tee 00-env.log"""
import sys, platform, importlib.metadata as md, subprocess, shutil, os, time

print('파이썬', sys.version.split()[0], platform.platform())
for pkg in ['pdfplumber', 'pdfminer.six', 'pypdf', 'pypdfium2', 'camelot-py', 'numpy', 'requests', 'reportlab', 'matplotlib', 'CairoSVG']:
    try:
        print('%-14s %s' % (pkg, md.version(pkg)))
    except md.PackageNotFoundError:
        print('%-14s 없음' % pkg)
import sqlite3
print('sqlite3 모듈', sqlite3.sqlite_version)
print('pdftotext', shutil.which('pdftotext'))
r = subprocess.run(['pdftotext', '-v'], capture_output=True, text=True)
print((r.stderr or r.stdout).strip().splitlines()[0])
print('nvidia-smi', shutil.which('nvidia-smi'))

# 접속 확인: 우회하지 않고 상태 코드만 적는다(셸 프록시를 거친다)
urls = [
    'https://api.openalex.org/works/doi:10.7717/peerj.4375',
    'https://api.crossref.org/works/10.7717/peerj.4375',
    'https://api.unpaywall.org/v2/10.7717/peerj.4375?email=x@example.org',
    'https://pypi.org/simple/pdfplumber/',
]
for u in urls:
    t0 = time.time()
    r = subprocess.run(['curl', '-sS', '-m', '20', '-o', '/dev/null', '-w', 'http=%{http_code} bytes=%{size_download}', u],
                       capture_output=True, text=True)
    print('%-70s %s %s (%.1f초)' % (u[:70], r.stdout.strip(), r.stderr.strip()[:80], time.time() - t0))
