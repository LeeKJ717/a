# -*- coding: utf-8 -*-
"""실습 2-9: 이 장이 쓴 파이썬 꾸러미의 라이선스를 설치된 꾸러미의 메타데이터에서 읽는다(인터넷 접속 없음).
메타데이터의 License 칸과 분류(classifier)를 그대로 옮기며, 공식 저장소의 라이선스 파일과 대조하지는 않았다.
실행: python3 13-licenses.py | tee 13-licenses.log"""
import importlib.metadata as md, subprocess, os
for pkg in ['pdfplumber', 'pdfminer.six', 'pypdf', 'camelot-py', 'reportlab', 'weasyprint', 'requests', 'numpy']:
    m = md.metadata(pkg)
    lic = (m.get('License-Expression') or m.get('License') or '').strip().splitlines()
    cls = [c.split('::')[-1].strip() for c in m.get_all('Classifier', []) if c.startswith('License')]
    print('%-12s %-8s License=%r  분류=%s' % (pkg, md.version(pkg), (lic[0][:60] if lic else ''), cls))
r = subprocess.run(['dpkg', '-s', 'poppler-utils'], capture_output=True, text=True)
print('poppler-utils', [l for l in r.stdout.splitlines() if l.startswith('Version')])
cp = '/usr/share/doc/poppler-utils/copyright'
print('poppler-utils copyright 파일:', os.path.exists(cp))
if os.path.exists(cp):
    txt = open(cp, encoding='utf-8', errors='replace').read()
    print('  앞 줄들에서 GPL 언급:', [l.strip() for l in txt.splitlines() if 'GPL' in l or 'GNU General' in l][:3])
