# -*- coding: utf-8 -*-
"""제2권 13장 그림 4장(색·흑백 SVG 두 벌). 값은 모두 ms/code/ch13 의 실행 결과에서 읽는다.
  fig-ch13-flow-v1 : 환각 점검 절차(어느 단계를 이 컨테이너에서 실행했고 어느 단계가 z840 실행 필요인가)
  fig-ch13-demo-v1 : 시연 출력에 심은 오류와 점검기의 지적(eval-demo-result.json)
  fig-ch13-vol1-v1 : 제1권 11장의 미결 항목 11개를 점검기가 지적했는가(eval-vol1-result.json, vol1-targets-v1.json)
  fig-ch13-grim-v1 : 백분율과 표본 수 n 으로 만들 수 있는 값(58.8%, n = 176 등)
사용: python figs-ch13.py"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figkit import *
ROOT = os.path.dirname(HERE); CODE = os.path.join(ROOT, 'ms', 'code', 'ch13'); OUT = os.path.join(ROOT, 'fig')
J = lambda n: json.load(open(os.path.join(CODE, n), encoding='utf-8'))


def ink(mode, P):
    return (P['hot'], P['river'], P['site']) if mode == 'color' else ('#111111', '#555555', '#666666')


def fig_flow(mode):
    f, P = base(mode, 1210.0)
    hot, river, site = ink(mode, P)
    steps = [
        ('1', '원문을 고정한다', '파일의 SHA-256 해시를 적는다. 점검은 이 파일에 대해서만 한다.', '직접 실행 확인', hot),
        ('2', '모델을 부른다', '온도 0, 시드 고정, 원문 전체를 넣고 한 줄에 주장 하나로 쓰게 한다. 인용은 따옴표, 계산값은 [계산].', 'z840 실행 필요', site),
        ('3', '모델 출력을 받는다', '이 책은 받지 못했다. 대신 모델이 틀리게 쓴 값을 일부러 섞은 시연값으로 3단계를 대신했다.', '시연값', site),
        ('4', '글자 점검: 인용, 숫자, 단위', '인용이 원문에 글자 그대로 있는가, 숫자가 원문에 있는가, 단위가 같은가.', '직접 실행 확인', hot),
        ('5', '계산 점검: 식, 백분율, 표, 범위', '산술식, 백분율과 표본 수, 표의 행 합과 열 합, 확률과 연대의 범위.', '직접 실행 확인', hot),
        ('6', '같은 입력으로 두 번 돌려 견준다', '숫자가 달라지는 줄은 모델이 흔들린 곳이다. 시연 출력 두 개로 실행했다.', '직접 실행 확인', hot),
        ('7', '사람이 원문 쪽을 본다', '뜻의 오류(항목을 바꿔 붙임, 부정문 뒤집기)는 점검기가 보지 못한다. 지적된 줄과 통과한 줄 모두 표본으로 본다.', '사람', river),
    ]
    L0, W0, TX, TW = 80.0, 840.0, 960.0, 260.0
    y = 60.0
    ys = []
    for n, head, body, tag, col in steps:
        lines = wrap(body, FS_I, W0 - 120)
        h = 56 + 38 * len(lines) + 20
        f.rect(L0, y, W0, h, '#FFFFFF', P['frame'], 2.4)
        f.circle(L0 + 44, y + 44, 24, col, '#FFFFFF', 2.0)
        f.text(L0 + 44, y + 55, n, FS_S, 'middle', '#FFFFFF', 700, False)
        f.text(L0 + 92, y + 48, head, FS_S, 'start', P['text'], 700, False)
        for i, ln in enumerate(lines):
            f.text(L0 + 92, y + 48 + 40 + i * 38, ln, FS_I, 'start', P['soft'], 400, False)
        # 태그
        f.rect(TX, y + h / 2 - 34, TW, 68, '#FFFFFF' if tag in ('사람',) else col, col, 2.4)
        f.text(TX + TW / 2, y + h / 2 + 10, tag, FS_I, 'middle', col if tag in ('사람',) else '#FFFFFF', 700, False)
        ys.append((y, h)); y += h + 52
    for (y1, h1), (y2, h2) in zip(ys, ys[1:]):
        xm = L0 + W0 / 2
        f.line(xm, y1 + h1, xm, y2 - 6, P['frame'], 3.0)
        f.poly([(xm - 12, y2 - 20), (xm + 12, y2 - 20), (xm, y2 - 4)], P['frame'], P['frame'], 1.0)
    f.rect(L0, y - 20, 14, 14, hot, hot, 1.0); f.text(L0 + 30, y - 6, '이 컨테이너에서 실행해 로그를 남김', FS_I, 'start', P['text'], 400, False)
    f.rect(L0 + 520, y - 20, 14, 14, site, site, 1.0); f.text(L0 + 550, y - 6, '실행하지 못함 또는 시연값', FS_I, 'start', P['text'], 400, False)
    f.H = y + 20
    f.h = y + 30
    return f


def fig_demo(mode):
    f, P = base(mode, 1210.0)
    hot, river, site = ink(mode, P)
    res = J('eval-demo-result.json')
    rows = {r['id']: r for r in res['rows']}
    lab = {'D01': '78을 87로', 'D02': 'bp를 kb로', 'D03': '표 행 합', 'D04': '표 열 합', 'D05': '66.7%를 0.667%로', 'D06': '11.1%를 111%로',
           'D07': 'BP 구간 순서', 'D08': 'p 0.00079를 0.0079로', 'D09': '의역을 인용으로', 'D10': '뜻을 뒤집은 인용',
           'X01': '항목을 바꿔 붙임', 'X02': '문화 이름 바꿈', 'X03': '21을 12로(원문에 12 있음)', 'X04': '따옴표 없는 부정 서술',
           'S01': '원문의 23 = 21 + 5', 'S02': '원문의 58.8%, n = 176'}
    groups = [('찾도록 설계한 심은 오류', ['D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10']),
              ('설계상 못 찾는 심은 오류', ['X01', 'X02', 'X03', 'X04']),
              ('원문 결함의 충실한 옮김', ['S01', 'S02'])]
    cols = [('Q', '인용'), ('N', '숫자'), ('U', '단위'), ('A', '산술'), ('G', '백분율'), ('T', '표'), ('R', '범위')]
    LX, CX0, CW, RH = 80.0, 560.0, 82.0, 50.0
    y = 70.0
    for i, (c, nm) in enumerate(cols):
        f.text(CX0 + i * CW + CW / 2, y, nm, FS_I, 'middle', P['text'], 700, False)
    f.text(CX0 + len(cols) * CW + 40, y, '결과', FS_I, 'start', P['text'], 700, False)
    y += 26
    f.line(LX, y, 1240, y, P['frame'], 2.0)
    for gname, ids in groups:
        y += 50
        f.text(LX, y, gname, FS_I, 'start', P['soft'], 700, False)
        for id_ in ids:
            y += RH
            r = rows[id_]
            f.text(LX + 10, y, '%s  %s' % (id_, lab[id_]), FS_I, 'start', P['text'], 400, False)
            got = {c[0] for c in r['codes']}
            for i, (c, nm) in enumerate(cols):
                cx = CX0 + i * CW + CW / 2
                f.rect(cx - 30, y - 34, 60, 44, 'none', P['grid'], 1.2)
                if c in got:
                    f.rect(cx - 30, y - 34, 60, 44, hot, hot, 1.0)
                    f.text(cx, y - 2, c, FS_I, 'middle', '#FFFFFF', 700, False)
            f.text(CX0 + len(cols) * CW + 40, y, '찾음' if r['hit'] else '못 찾음', FS_I, 'start', (hot if r['hit'] else P['soft']), 700 if r['hit'] else 400, False)
    y += 70
    ctl = [r for r in res['rows'] if r['kind'] == '정상']
    fp = sum(1 for r in ctl if r['codes'])
    y = note(f, LX, y, '정상으로 심어 둔 %d줄 중 점검기가 지적한 줄은 %d줄이다. 칸에 글자가 있으면 그 점검이 그 줄을 지적했다는 뜻이다. 모델 출력은 모델이 쓴 것이 아니라 이 책이 만든 시연값이다.' % (len(ctl), fp), 1160)
    f.h = y + 20
    return f


def fig_vol1(mode):
    f, P = base(mode, 1210.0)
    hot, river, site = ink(mode, P)
    tg = J('vol1-targets-v1.json')['targets']
    ev = J('eval-vol1-result.json')
    import importlib.util
    spec = importlib.util.spec_from_file_location('hc', os.path.join(CODE, 'halluccheck-v1.py'))
    hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)
    inp = {'본문': 'vol1-ch11-body-v1.md', '장부': 'vol1-ch11-ledger-v1.md'}
    lines = {k: hc.read_lines(os.path.join(CODE, 'input', v)) for k, v in inp.items()}
    lab = {'11-3': '23 = 21 + 5', '11-5': '13.7% 대 16.7%', '11-7': '71%의 짝', '11-8': '본문과 표의 불일치', '11-25': 'Mantel 표의 짝',
           '11-32': '56.6%, n = 127', '11-36': 'EPS 0.756 대 0.85', '11-39': '0.597 대 0.53', '11-41': '부호 검정 p = 0.0614',
           '11-43': '평균 7.41 대 기준 7.395', '11-46': '27/30 대 27개'}
    LX, C1, C2, CW = 80.0, 640.0, 900.0, 200.0
    y = 70.0
    f.text(C1 + CW / 2, y, '본문 입력', FS_I, 'middle', P['text'], 700, False)
    f.text(C2 + CW / 2, y, '장부 입력', FS_I, 'middle', P['text'], 700, False)
    y += 26
    f.line(LX, y, 1240, y, P['frame'], 2.0)
    found = {}
    for t in tg:
        for nm, key in (('본문', 'loc_body'), ('장부', 'loc_ledger')):
            ls = [i for i, l in enumerate(lines[nm], 1) if re.search(t[key], l)]
            # 같은 줄에 다른 항목의 식도 함께 적힌 경우(11-43 의 851줄)는 그 항목의 지적으로 세지 않는다
            if t['id'] == '11-43' and nm == '본문':
                ls = [l for l in ls if l != 851]
            codes = sorted({x['code'] for x in ev[nm]['findings'] if x['line'] in ls})
            found[(t['id'], nm)] = codes
    for t in tg:
        y += 50
        f.text(LX + 10, y, '%s  %s' % (t['id'], lab[t['id']]), FS_I, 'start', P['text'], 400, False)
        for nm, cx in (('본문', C1 + CW / 2), ('장부', C2 + CW / 2)):
            codes = found[(t['id'], nm)]
            f.rect(cx - 70, y - 34, 140, 44, hot if codes else 'none', hot if codes else P['grid'], 2.0 if codes else 1.2)
            f.text(cx, y - 2, ','.join(codes) if codes else '없음', FS_I, 'middle', '#FFFFFF' if codes else P['soft'], 700 if codes else 400, False)
    y += 70
    f.text(LX, y, '제1권이 지적하지 않았으나 점검기가 새로 지적한 것(후보)', FS_I, 'start', P['soft'], 700, False)
    for id_, txt, b, l in (('N1', '58.8%, n = 176', 'G1', 'G1'), ('N2', '50.7%, n = 285', 'G1', '없음')):
        y += 50
        f.text(LX + 10, y, '%s  %s' % (id_, txt), FS_I, 'start', P['text'], 400, False)
        for v, cx in ((b, C1 + CW / 2), (l, C2 + CW / 2)):
            on = v != '없음'
            f.rect(cx - 70, y - 34, 140, 44, site if on else 'none', site if on else P['grid'], 2.0 if on else 1.2)
            f.text(cx, y - 2, v, FS_I, 'middle', '#FFFFFF' if on else P['soft'], 700 if on else 400, False)
    y += 70
    y = note(f, LX, y, '채운 칸은 점검기가 그 항목이 적힌 줄을 지적했다는 뜻이다. 11개 가운데 본문 입력에서 1개(11-3), 장부 입력에서 2개(11-3, 11-32)를 지적했고 나머지는 지적하지 못했다. 11-32 는 본문에서도 다른 줄(866줄)에서 지적되었다.', 1160)
    f.h = y + 20
    return f


def fig_grim(mode):
    f, P = base(mode, 1190.0)
    hot, river, site = ink(mode, P)
    panels = [('58.8%, n = 176', 58.8, 176, 1), ('50.7%, n = 285', 50.7, 285, 1), ('56.6%, n = 127', 56.6, 127, 1)]
    L, R = 120.0, 1200.0
    y0 = 70.0
    for title, p, n, d in panels:
        half = 1.25
        lo, hi = p - half, p + half
        X = lin(lo, hi, L, R)
        f.text(L, y0, title, FS_S, 'start', P['text'], 700, False)
        yl = y0 + 150
        f.line(L, yl, R, yl, P['frame'], 2.4)
        # 반올림 구간(소수 첫째 자리)
        bw = 0.05
        f.rect(X(p - bw), yl - 70, X(p + bw) - X(p - bw), 70, river if mode == 'color' else '#BBBBBB', 'none', 1.0, 'opacity="0.55"')
        f.line(X(p), yl - 80, X(p), yl, river if mode == 'color' else '#555555', 3.0)
        f.text(X(p), yl - 92, '적힌 값 %.1f' % p, FS_I, 'middle', P['text'], 700, False)
        ks = [k for k in range(int(lo * n / 100) - 1, int(hi * n / 100) + 3) if lo <= k * 100.0 / n <= hi]
        for k in ks:
            v = k * 100.0 / n
            f.line(X(v), yl - 22, X(v), yl + 22, hot, 3.0)
            f.text(X(v), yl + 64, '%.2f' % v, FS_I, 'middle', P['text'], 400, False)
        ok = any(abs(k * 100.0 / n - p) <= 0.05 + 1e-9 for k in range(n + 1))
        f.text(L, yl + 120, '가장 가까운 두 값 %.2f, %.2f 사이에 적힌 값의 반올림 구간(±0.05)이 %s.' % (
            max(k * 100.0 / n for k in ks if k * 100.0 / n < p), min(k * 100.0 / n for k in ks if k * 100.0 / n > p), '걸린다' if ok else '들어 있지 않다'), FS_I, 'start', P['soft'], 400, False)
        y0 += 360
    f.h = y0 - 20
    return f


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for mode in ('color', 'bw'):
        for nm, fn in (('fig-ch13-flow-v1', fig_flow), ('fig-ch13-demo-v1', fig_demo), ('fig-ch13-vol1-v1', fig_vol1), ('fig-ch13-grim-v1', fig_grim)):
            f = fn(mode)
            w = f.save(os.path.join(OUT, '%s-%s.svg' % (nm, mode)))
            print(nm, mode, '크기 %d x %d' % (f.w, f.h), '경고:', w)
