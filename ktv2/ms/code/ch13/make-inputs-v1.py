# -*- coding: utf-8 -*-
"""제1권 11장 원고를 입력 폴더로 복사하고 11.3절만 잘라 원문 대역을 만든다. 해시를 적는다."""
import hashlib, os, re, sys
SRC = '/home/claude/book/ms/ch11-v1.md'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'input')
os.makedirs(OUT, exist_ok=True)
txt = open(SRC, encoding='utf-8').read()
open(os.path.join(OUT, 'vol1-ch11-v1.md'), 'w', encoding='utf-8').write(txt)
lines = txt.split('\n')
def idx(prefix):
    return next(i for i, l in enumerate(lines) if l.startswith(prefix))
a, b = idx('## 11.3 '), idx('## 11.4 ')
sl = '\n'.join(lines[a:b]) + '\n'
open(os.path.join(OUT, 'vol1-ch11-sec3-v1.md'), 'w', encoding='utf-8').write(sl)
l0 = idx('## 11.15 ')
l1 = idx('## 참고문헌')
open(os.path.join(OUT, 'vol1-ch11-ledger-v1.md'), 'w', encoding='utf-8').write('\n'.join(lines[l0:l1]) + '\n')
open(os.path.join(OUT, 'vol1-ch11-body-v1.md'), 'w', encoding='utf-8').write('\n'.join(lines[:l0]) + '\n')
for n in ('vol1-ch11-v1.md', 'vol1-ch11-body-v1.md', 'vol1-ch11-sec3-v1.md', 'vol1-ch11-ledger-v1.md'):
    p = os.path.join(OUT, n)
    d = open(p, 'rb').read()
    print('%-28s %7d 바이트 %5d 줄 sha256=%s' % (n, len(d), d.count(b'\n'), hashlib.sha256(d).hexdigest()))
print('11.3절은 원문(%d줄 시작)에서 %d줄 길이' % (a + 1, b - a))
