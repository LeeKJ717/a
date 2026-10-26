# -*- coding: utf-8 -*-
"""제2권 10장 그림 2장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch10 의 실행 로그에서 읽는다.
  fig-ch10-time-v1   : 거리 행렬 계산의 CPU 시간(두 번 실행한 중앙값의 범위), float64 대 float32
  fig-ch10-mem-v1    : 거리 행렬 계산의 최대 상주 메모리 실측과 외삽(12 GiB 선)
사용: python figs-ch10.py"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geomap import Fig, FS, FS_S, FS_I
ROOT = os.path.dirname(HERE)
CODE = os.path.join(ROOT, 'ms', 'code', 'ch10')
OUT = os.path.join(ROOT, 'fig')

def jl(name):
    return [json.loads(l) for l in open(os.path.join(CODE, name), encoding='utf-8') if l.strip()]

def note(f, x, y, s, maxw=None):
    from geomap import tw
    maxw = maxw or (f.w - x - 40)
    lines, cur = [], ''
    for ch in s:
        if tw(cur + ch, FS_I) > maxw and cur:
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    lines.append(cur)
    for i, ln in enumerate(lines):
        f.text(x, y + i * 38, ln, FS_I, 'start', f.P['soft'], 400, False)

def base(mode, H=1130.0):
    f = Fig(1300.0, H, mode)
    f.rect(0, 0, 1300.0, H, '#FFFFFF')
    return f, f.P

def fig_time(mode):
    f, P = base(mode)
    runs = [jl('gpu-bench-cpu.jsonl'), jl('gpu-bench-cpu2.jsonl')]
    data = {}
    for r in runs:
        for row in r:
            if row.get('kind') == 'hav' and 'median_s' in row:
                data.setdefault((row['dtype'], row['N']), []).append(row['median_s'])
    Ns = sorted({k[1] for k in data})
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    lo, hi = math.log10(0.005), math.log10(10.0)
    Y = lambda v: B - (math.log10(v) - lo) / (hi - lo) * (B - T)
    X = lambda i: L + (i + 0.5) / len(Ns) * (R - L)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for v in (0.01, 0.1, 1, 10):
        f.line(L, Y(v), R, Y(v), P['grid'], 1.0, '8 8'); f.line(L - 8, Y(v), L, Y(v), P['frame'], 2.0)
        f.text(L - 14, Y(v) + 10, ('%g' % v), FS_I, 'end', P['soft'], 400, False)
    f.text(L - 150, T - 30, '걸린 시간 (초, 로그 눈금)', FS_S, 'start', P['text'], 400, False)
    for i, N in enumerate(Ns):
        f.line(X(i), B, X(i), B + 10, P['frame'], 2.0)
        f.text(X(i), B + 44, '%d' % N, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '점의 수 N (거리 행렬은 N x N)', FS_S, 'middle', P['text'], 400, False)
    cols = {'float64': (P['hot'] if mode == 'color' else '#111111'), 'float32': (P['river'] if mode == 'color' else '#777777')}
    off = {'float64': -26, 'float32': 26}
    for dt in ('float64', 'float32'):
        pts = []
        for i, N in enumerate(Ns):
            v = data[(dt, N)]
            x = X(i) + off[dt]
            f.line(x, Y(min(v)), x, Y(max(v)), cols[dt], 5.0)
            m = sum(v) / len(v)
            pts.append((x, Y(m)))
            f.marker(x, Y(m), 'dot' if dt == 'float64' else 'sq', 1.0, cols[dt])
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            f.line(x1, y1, x2, y2, cols[dt], 2.5, None if dt == 'float64' else '14 8')
    ly = B + 150
    f.marker(170, ly - 8, 'dot', 1.0, cols['float64']); f.text(196, ly, 'float64', FS_I, 'start', P['text'], 400, False)
    f.marker(400, ly - 8, 'sq', 1.0, cols['float32']); f.text(426, ly, 'float32', FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 56, '같은 스크립트(gpu-bench-v1.py)를 numpy로 두 번 실행한 중앙값의 범위(세로 막대)와 평균(표지). 2 코어 컨테이너이며 다른 작업과 자원을 나눠 쓰므로 실행마다 시간이 다르다. GPU 시간이 아니다.')
    return f

def fig_mem(mode):
    f, P = base(mode)
    rows = {}
    base_mib = None
    for line in open(os.path.join(CODE, 'memtest.log'), encoding='utf-8'):
        m = re.match(r'\s*(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$', line)
        if m and int(m.group(1)) in (1000, 2000, 4000, 8000):
            rows[int(m.group(1))] = float(m.group(3))
    ratio = rows[8000] / (8 * 8000 * 8000 / 2**20)
    L, T, R, B = 190.0, 90.0, 1240.0, 700.0
    n0, n1 = math.log10(1000), math.log10(24000)
    X = lambda n: L + (math.log10(n) - n0) / (n1 - n0) * (R - L)
    ymax = 14.0
    Y = lambda g: B - g / ymax * (B - T)
    f.rect(L, T, R - L, B - T, 'none', P['frame'], 2.4)
    for g in (0, 2, 4, 6, 8, 10, 12, 14):
        f.line(L, Y(g), R, Y(g), P['grid'], 1.0, '8 8'); f.line(L - 8, Y(g), L, Y(g), P['frame'], 2.0)
        f.text(L - 14, Y(g) + 10, '%d' % g, FS_I, 'end', P['soft'], 400, False)
    f.text(L - 150, T - 30, '최대 상주 메모리 (GiB)', FS_S, 'start', P['text'], 400, False)
    for n in (1000, 2000, 4000, 8000, 16000):
        f.line(X(n), B, X(n), B + 10, P['frame'], 2.0); f.text(X(n), B + 44, '%d' % n, FS_I, 'middle', P['soft'], 400, False)
    f.text((L + R) / 2, B + 92, '점의 수 N (로그 눈금)', FS_S, 'middle', P['text'], 400, False)
    c1 = P['hot'] if mode == 'color' else '#111111'
    c2 = P['river'] if mode == 'color' else '#777777'
    # 외삽 선
    pts = [(n, ratio * 8 * n * n / 2**30) for n in range(1000, 24001, 500)]
    for (n1_, g1), (n2_, g2) in zip(pts, pts[1:]):
        if g2 <= ymax:
            f.line(X(n1_), Y(g1), X(n2_), Y(g2), c2, 3.0, '14 8')
    f.line(L, Y(12), R, Y(12), c1, 3.0, '18 8')
    f.text(L + 14, Y(12) - 14, '12 GiB (z840급 장치 메모리, 확인 필요)', FS_I, 'start', c1, 700, False)
    ncross = math.sqrt(12 * 2**30 / (ratio * 8))
    f.line(X(ncross), Y(12), X(ncross), B, c1, 2.0, '8 8')
    f.text(L + 14, Y(12) + 50, '세로 점선: N = %d 부근에서 교차(외삽)' % (round(ncross, -2)), FS_I, 'start', c1, 400, False)
    for n, mib in sorted(rows.items()):
        f.marker(X(n), Y(mib / 1024.0), 'dot', 1.1, c2)
    f.text(X(8000) - 18, Y(rows[8000] / 1024.0) - 18, '실측 N=8000: %.2f GiB' % (rows[8000] / 1024.0), FS_I, 'end', P['text'], 700, False)
    ly = B + 150
    f.marker(170, ly - 8, 'dot', 1.0, c2); f.text(196, ly, '실측(CPU, 기준 프로세스 제외)', FS_I, 'start', P['text'], 400, False)
    f.line(150, ly + 38, 210, ly + 38, c2, 3.0, '14 8'); f.text(222, ly + 46, '외삽: 행렬 하나의 %.2f배(N=8000 실측 배율)로 가정' % ratio, FS_I, 'start', P['text'], 400, False)
    note(f, 150, ly + 104, 'CPU 메모리(RAM)에서 잰 값이다. 같은 계산이 GPU 메모리에서도 같은 배율이라는 보장은 없으며, 선의 오른쪽은 측정이 아니라 연장이다. z840 실행 필요.')
    return f

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in (('fig-ch10-time-v1', fig_time), ('fig-ch10-mem-v1', fig_mem)):
            f = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, '경고:', w)
