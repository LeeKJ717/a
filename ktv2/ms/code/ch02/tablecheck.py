# -*- coding: utf-8 -*-
"""tablecheck v1 (제2권 2장): 추출한 표가 '열이 흩어지지 않았는가'를 산술로 점검하는 함수들. 숫자 표가 대상이다."""
import re


def num(s):
    """'1,234.5', '30.65%', '-0.02', '+0.01', '−3'을 실수로. 못 읽으면 None."""
    if s is None:
        return None
    t = str(s).strip().replace(',', '').replace('−', '-').replace('%', '')
    return float(t) if re.fullmatch(r'[-+]?\d+\.?\d*', t) else None


def row_sum(rows, parts, total, tol):
    """각 행에서 parts 열의 합이 total 열과 tol 안에서 같은가. 돌려주는 값: (통과 행 수, 검사한 행 수, 실패한 행 번호)"""
    ok = n = 0
    bad = []
    for i, r in enumerate(rows):
        v = [num(r[j]) for j in parts]
        t = num(r[total])
        if t is None or any(x is None for x in v):
            continue
        n += 1
        if abs(sum(v) - t) <= tol:
            ok += 1
        else:
            bad.append(i)
    return ok, n, bad


def col_sum(rows, col, total_row, tol):
    """total_row(합계 행) 위의 값을 더해 합계 행의 값과 견준다."""
    v = [num(r[col]) for i, r in enumerate(rows) if i != total_row]
    v = [x for x in v if x is not None]
    t = num(rows[total_row][col])
    return abs(sum(v) - t) <= tol, sum(v), t


def ratio(rows, a, b, pct, tol):
    """100 * a / b 가 pct 열(%)과 tol(%p) 안에서 같은가."""
    ok = n = 0
    bad = []
    for i, r in enumerate(rows):
        x, y, p = num(r[a]), num(r[b]), num(r[pct])
        if None in (x, y, p) or y == 0:
            continue
        n += 1
        if abs(100 * x / y - p) <= tol:
            ok += 1
        else:
            bad.append(i)
    return ok, n, bad


def in_range(rows, col, lo, hi):
    """값 범위: lo <= 값 <= hi 를 벗어난 행 번호."""
    out = []
    for i, r in enumerate(rows):
        v = num(r[col])
        if v is not None and not (lo <= v <= hi):
            out.append((i, v))
    return out
