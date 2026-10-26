# -*- coding: utf-8 -*-
"""15장 공용: 제1권 원고(ms/chNN-v1.md)에서 표를 번호로 읽는다.
표 번호는 build.py와 같은 규칙이다. 한 장 안에서 {{T:...}} 표지를 위에서부터 센 순서가 표 N-k이다.
표지 바로 뒤에 오는 첫 마크다운 표(| 로 시작하는 줄 묶음)가 그 표의 내용이다.
원고는 읽기만 한다. 쓰지 않는다."""
import hashlib, os, re

V1 = '/home/claude/book/ms'
_cache = {}


def ms_path(ch):
    return os.path.join(V1, 'ch%02d-v1.md' % ch)


def ms_text(ch):
    if ch not in _cache:
        _cache[ch] = open(ms_path(ch), encoding='utf-8').read()
    return _cache[ch]


def ms_sha(ch):
    return hashlib.sha256(open(ms_path(ch), 'rb').read()).hexdigest()


def num(s):
    """표 칸의 문자열을 실수로. 유니코드 빼기, 쉼표, 퍼센트, 앞의 부호 +를 처리한다."""
    s = s.strip().replace('−', '-').replace(',', '').replace('%', '').replace('+', '')
    return float(s)


def table(ch, k):
    """제1권 ch장 표 ch-k. 반환 dict(caption, header, rows). rows는 문자열 칸의 목록."""
    t = ms_text(ch)
    marks = list(re.finditer(r'\{\{T:(.*?)\}\}', t))
    if not (1 <= k <= len(marks)):
        raise KeyError('제1권 %d장에는 표가 %d개뿐이다(요청 %d)' % (ch, len(marks), k))
    m = marks[k - 1]
    lines = t[m.end():].split('\n')
    i = 0
    while i < len(lines) and not lines[i].lstrip().startswith('|'):
        i += 1
    blk = []
    while i < len(lines) and lines[i].lstrip().startswith('|'):
        blk.append(lines[i]); i += 1
    cells = [[c.strip() for c in ln.strip().strip('|').split('|')] for ln in blk]
    return dict(caption=m.group(1), header=cells[0], rows=cells[2:], n_tables=len(marks))


def has(ch, s):
    """원고 ch장 본문에 문자열 s가 그대로 있는가."""
    return s in ms_text(ch)
