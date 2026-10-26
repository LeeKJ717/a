# -*- coding: utf-8 -*-
"""제2권 그림 공용 도구(11, 12장). geomap.Fig 위에 축, 눈금, 색 띠, 범례, 주석 줄바꿈을 얹는다."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geomap import Fig, FS, FS_S, FS_I, tw

def base(mode, H=1130.0, W=1300.0):
    f = Fig(W, H, mode)
    f.rect(0, 0, W, H, '#FFFFFF')
    return f, f.P

def series_colors(mode):
    return ['#9C4F2E', '#3A7CA5', '#8A6A2C', '#4F7F4A'] if mode == 'color' else ['#111111', '#666666', '#999999', '#BBBBBB']

def lin(v0, v1, p0, p1):
    return lambda v: p0 + (v - v0) / (v1 - v0) * (p1 - p0)

def logmap(v0, v1, p0, p1):
    a, b = math.log10(v0), math.log10(v1)
    return lambda v: p0 + (math.log10(v) - a) / (b - a) * (p1 - p0)

def frame(f, L, T, R, B):
    f.rect(L, T, R - L, B - T, 'none', f.P['frame'], 2.4)

def yticks(f, L, R, Y, ticks, labels=None, grid=True, size=FS_I):
    P = f.P
    for i, v in enumerate(ticks):
        y = Y(v)
        if grid: f.line(L, y, R, y, P['grid'], 1.0, '8 8')
        f.line(L - 8, y, L, y, P['frame'], 2.0)
        f.text(L - 14, y + 10, labels[i] if labels else ('%g' % v), size, 'end', P['soft'], 400, False)

def xticks(f, B, X, ticks, labels=None, T=None, grid=False, size=FS_I):
    P = f.P
    for i, v in enumerate(ticks):
        x = X(v)
        if grid and T is not None: f.line(x, T, x, B, P['grid'], 1.0, '8 8')
        f.line(x, B, x, B + 10, P['frame'], 2.0)
        f.text(x, B + 44, labels[i] if labels else ('%g' % v), size, 'middle', P['soft'], 400, False)

def wrap(s, size, maxw):
    lines, cur = [], ''
    for ch in s:
        if tw(cur + ch, size) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    return lines

def note(f, x, y, s, maxw=None, size=FS_I, lh=38):
    maxw = maxw or (f.w - x - 40)
    for i, ln in enumerate(wrap(s, size, maxw)):
        f.text(x, y + i * lh, ln, size, 'start', f.P['soft'], 400, False)
    return y + len(wrap(s, size, maxw)) * lh

def dash_line(f, pts, color, sw=3.0, dash=None):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        f.line(x1, y1, x2, y2, color, sw, dash)

def hollow(f, x, y, kind, color, size=1.0):
    f.marker(x, y, kind, size, '#FFFFFF', color)

def ramp(mode, u):
    """0..1 -> 색. color: 연한 모래색에서 짙은 갈색, bw: 흰색에서 검정."""
    u = max(0.0, min(1.0, u))
    if mode == 'color':
        c0, c1, c2 = (0xF1, 0xEB, 0xDD), (0xD9, 0xA0, 0x6B), (0x7A, 0x2E, 0x14)
        if u < 0.5:
            a, b, t = c0, c1, u / 0.5
        else:
            a, b, t = c1, c2, (u - 0.5) / 0.5
    else:
        a, b, t = (0xF4, 0xF4, 0xF4), (0x22, 0x22, 0x22), u
    return '#%02X%02X%02X' % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
