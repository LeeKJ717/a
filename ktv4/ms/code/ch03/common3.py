# -*- coding: utf-8 -*-
"""3장 계산 공용: 얼음 코어 이산화탄소 표(Dome C, Taylor Dome)와 메탄 표(Greenland)를 읽는다.
표는 같은 폴더의 csv. 출처: edc-co2.csv = Monnin 등(2004) 자료표(NOAA 고기후 자료 센터 edc-co2.txt)의 첫째 표,
taylor-co2.csv = Indermuhle 등(1999) 자료표(isolab.ess.washington.edu/data/taylor/data/tdco2.dat),
beck-ch4-sub.csv = Beck 등(2018) 자료표(NOAA beck2018north-ch4.txt)를 도구로 읽어 옮긴 것(약 3행마다 한 행. 전체 아님).
숫자는 웹 도구(WebFetch)가 돌려준 표를 그대로 옮긴 것이며 원본 파일을 셸에서 직접 내려받아 대조하지는 못했다.
"""
import os, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))

def load(name):
    rows = list(csv.reader(open(os.path.join(HERE, name), encoding='utf-8')))
    hdr, body = rows[0], rows[1:]
    cols = {h: [] for h in hdr}
    for r in body:
        for h, v in zip(hdr, r):
            try: cols[h].append(float(v))
            except ValueError: cols[h].append(v)
    return {h: (np.array(v) if isinstance(v[0], float) else np.array(v, dtype=object)) for h, v in cols.items()}

def edc():
    d = load('edc-co2.csv'); return d['age_yrBP'], d['co2_ppmv'], d['sigma_mean_ppmv'], d['depth_m']
def taylor():
    d = load('taylor-co2.csv'); return d['age_yrBP'], d['co2_ppmv'], d['sd_ppmv'], d['depth_m']
def ch4():
    d = load('beck-ch4-sub.csv'); return d['age_calBP'], d['ch4_ppb'], d['origin']

def hinge_fit(t, y, lo, hi, step=50):
    """연속 꺾은선(두 직선이 꺾는 점에서 이어짐) 최소제곱. 꺾는 점 t0 를 lo~hi 에서 step 간격으로 훑어 잔차제곱합이 최소인 t0 를 고른다."""
    best = None
    for t0 in np.arange(lo, hi + 1e-9, step):
        X = np.column_stack([np.ones_like(t), t - t0, np.maximum(t - t0, 0.0)])
        beta, res, *_ = np.linalg.lstsq(X, y, rcond=None)
        sse = float(np.sum((y - X @ beta) ** 2))
        if best is None or sse < best[0]:
            best = (sse, t0, beta)
    return best   # sse, t0, (y0, slope1, slope change)
