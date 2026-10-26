# -*- coding: utf-8 -*-
"""1장 그림 v1. 그림의 자료는 논문의 표와 본문 숫자를 다시 그린 것이며, 계산 값은 ms/code/ch01/calc-ch01-v1.py 의 결과다.
지도는 Natural Earth(geodata)로 그렸고 점의 좌표는 논문 본문 또는 제1권 표에 적힌 값이다. 좌표를 읽지 못한 곳은 그리지 않았다.
실행: python3 figs-ch01.py   (미리보기 PNG: PREVDIR=경로 python3 figs-ch01.py)
"""
import os, sys, io, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import figkit12 as K
import mapkit as mk
import matplotlib.pyplot as plt
from scipy import stats

CODE = os.path.join(os.path.dirname(HERE), 'ms', 'code', 'ch01')
sys.path.insert(0, CODE)
spec = importlib.util.spec_from_file_location('calc1', os.path.join(CODE, 'calc-ch01-v1.py'))
calc = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(calc)
import rcal

MODES = ('color', 'bw')

# ---------------------------------------------------------------- 그림 1: 위치 지도
SITES = [  # 번호, 이름, 경도, 위도, 출처
    (1, '호톤 호', 88.346, 48.617), (2, '사이람 호', 81.15, 44.60), (3, '텔멘 호', 97.32, 48.82), (4, '시레트 나이만 호', 101.82, 46.53),
    (5, '울란 호', 103.654, 44.514), (6, '차간 누르', 115.027, 43.436), (7, '달리호', 116.60, 43.26), (8, '호륜호', 117.506, 49.127),
    (9, '공해', 112.23, 38.90), (10, '기련산 사구', 100.84, 37.97), (11, '감남 사구', 102.078, 33.961)]

def fig_map(mode):
    import geopandas as gpd
    from pyproj import Transformer
    P = mk.PAL[mode]; Cc = K.C[mode]
    epsg = '+proj=aea +lat_1=33 +lat_2=52 +lat_0=42 +lon_0=102 +datum=WGS84 +units=m'
    bbox = (76.0, 31.0, 124.0, 53.0)
    f = K.fig(130, 108)
    ax = f.add_axes([0.075, 0.30, 0.90, 0.68])
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    land = mk.read('ne_10m_land', (bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3)).to_crs(epsg)
    lakes = mk.read('ne_10m_lakes', bbox).to_crs(epsg)
    riv = mk.read('ne_10m_rivers_lake_centerlines', bbox).to_crs(epsg)
    x0, y0, x1, y1 = mk.proj_bounds(bbox, epsg)
    ax.set_facecolor(P['ocean'])
    land.plot(ax=ax, color=P['land'], edgecolor=P['coast'], linewidth=0.4, zorder=2)
    lakes.plot(ax=ax, color=P['lake'], edgecolor=P['coast'], linewidth=0.25, zorder=3)
    riv.plot(ax=ax, color=P['river'], linewidth=0.5, zorder=3)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal')
    ax.set_xlabel(''); ax.set_ylabel('')
    mk.graticule(ax, bbox, epsg, 10, mode)
    mk.edge_ticks(ax, bbox, epsg, 10, mode)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_color(P['frame']); sp.set_linewidth(0.6)
    OFF = {6: (-8.5, -9.5), 7: (9.0, -5.5)}        # 서로 가까운 두 점은 번호 원을 비껴 두고 가는 선으로 잇는다(포인트 단위)
    for n, nm, lo, la in SITES:
        x, y = tr.transform(lo, la)
        dx, dy = OFF.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            ax.plot(x, y, 'o', ms=2.6, color=Cc['ink'], zorder=12)
            ax.annotate(str(n), (x, y), xytext=(dx, dy), textcoords='offset points', fontsize=8, ha='center', va='center', color=Cc['ink'], fontweight='bold', zorder=13,
                        bbox=dict(boxstyle='circle,pad=0.18', fc='#FFFFFF', ec=Cc['ink'], lw=0.8), arrowprops=dict(arrowstyle='-', color=Cc['ink'], lw=0.6, shrinkA=4, shrinkB=1))
        else:
            ax.plot(x, y, 'o', ms=9.5, mfc='#FFFFFF', mec=Cc['ink'], mew=0.8, zorder=10)
            ax.text(x, y, str(n), fontsize=8, ha='center', va='center', color=Cc['ink'], zorder=11, fontweight='bold')
    # 도시(위치 참고)
    pp = mk.read('ne_10m_populated_places_simple', bbox)
    for en, ko, dx, dy in (('Ulaanbaatar', '울란바토르', 6, -11), ('Ürümqi', '우루무치', 6, -11)):
        r = pp[pp['name'] == en]
        if len(r):
            x, y = tr.transform(float(r.iloc[0]['longitude']), float(r.iloc[0]['latitude']))
            ax.plot(x, y, 's', ms=3.5, color=P['text'], zorder=9)
            mk.label(ax, x, y, ko, 8, P['soft'], dx=dx, dy=dy, ha='left', mode=mode)
    mk.scalebar(ax, 1000, 0.04, 0.05, mode)
    mk.north_arrow(ax, 0.95, 0.80, mode)
    # 범례(번호 목록): 그림 아래 2열
    names = ['%d %s' % (n, nm) for n, nm, lo, la in SITES]
    col = 4
    rows = (len(names) + col - 1) // col
    for i, s in enumerate(names):
        c = i // rows; r = i % rows
        f.text(0.06 + c * 0.245, 0.215 - r * 0.052, s, fontsize=8, color=Cc['ink'], va='center')
    f.text(0.06, 0.04, '번호는 점 안의 숫자. 점 위치는 논문 본문 또는 제1권 표의 좌표.', fontsize=8, color=Cc['soft'], va='center')
    f.text(0.06, 0.003 + 0.0, '', fontsize=8)
    return f

# ---------------------------------------------------------------- 그림 2: 텅거 호 보정 비교
def fig_tengger(mode):
    P = K.C[mode]
    f = K.fig(130, 100)
    ax = f.add_axes([0.16, 0.50, 0.80, 0.40])
    ax2 = f.add_axes([0.16, 0.09, 0.80, 0.22])
    K.style_ax(ax, mode, 'x'); K.style_ax(ax2, mode, 'y')
    TG = calc.TG; RES = calc.RES
    for i, (dep, c, s, pub) in enumerate(TG):
        r = rcal.summary(c - RES, s, 'intcal13')
        y = len(TG) - 1 - i
        mid = (pub[0] + pub[1]) / 2
        for a, b, m in r['h68']:
            ax.barh(y + 0.17, b - a + 4, left=a - mid - 2, height=0.30, color=P['a'], edgecolor=P['ink'], linewidth=0.3, zorder=3)
        ax.barh(y - 0.17, pub[1] - pub[0] + 4, left=pub[0] - mid - 2, height=0.30, color=P['b'], edgecolor=P['ink'], linewidth=0.3, hatch='////' if mode == 'bw' else None, zorder=3)
    ax.axvline(0, color=P['ink'], lw=0.6, zorder=2)
    ax.set_yticks(range(len(TG)))
    ax.set_yticklabels(['%d~%d cm' % (d[0][0], d[0][1]) for d in TG][::-1], fontsize=8)
    ax.set_xlabel('논문 구간의 가운데에서 잰 차이 (년)', fontsize=8)
    ax.set_xlim(-120, 120)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=P['a'], ec=P['ink'], lw=0.3), plt.Rectangle((0, 0), 1, 1, fc=P['b'], ec=P['ink'], lw=0.3, hatch='////' if mode == 'bw' else None)],
              labels=['이 책 계산, 68.2% 구간(여러 조각)', '논문 표 1의 1시그마'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=1, handlelength=1.4)
    f.text(0.02, 0.975, '(가) 저장 효과 1920년을 뺀 뒤 IntCal13 보정', fontsize=8, va='top', color=P['ink'])
    # (나) 구간 퇴적률
    tgm = []
    for dep, c, s, pub in TG:
        tgm.append(((dep[0] + dep[1]) / 2, (pub[0] + pub[1]) / 2))
    rates = [(tgm[i][0] - tgm[i - 1][0]) / (tgm[i][1] - tgm[i - 1][1]) for i in range(1, len(tgm))]
    lab = ['%d→%d' % (tgm[i - 1][0], tgm[i][0]) for i in range(1, len(tgm))]
    ax2.bar(range(len(rates)), rates, color=P['a'], edgecolor=P['ink'], linewidth=0.4, zorder=3)
    ax2.axhline(0.14, color=P['acc'], lw=1.0, ls='--', zorder=4)
    ax2.text(len(rates) - 0.55, 0.15, '논문의 외삽 가정 0.14', fontsize=8, ha='right', va='bottom', color=P['acc'])
    ax2.set_xticks(range(len(rates))); ax2.set_xticklabels(lab, fontsize=8)
    ax2.set_ylabel('퇴적률 (cm/년)', fontsize=8)
    ax2.set_xlabel('깊이 구간 (cm)', fontsize=8)
    f.text(0.02, 0.365, '(나) 인접한 두 연대 사이의 퇴적률', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 3: 대해호 OSL
def fig_daihai(mode):
    P = K.C[mode]
    f = K.fig(130, 100)
    ax = f.add_axes([0.12, 0.45, 0.84, 0.46])
    ax2 = f.add_axes([0.12, 0.09, 0.84, 0.25], sharex=ax)
    K.style_ax(ax, mode, 'x'); K.style_ax(ax2, mode, 'y')
    a = np.array(calc.DH); s = np.array(calc.DHs)
    o = np.argsort(a)
    ax.axvspan(5.2, 8.1, color=P['grid'], zorder=1)
    ax.errorbar(a[o], range(len(a)), xerr=s[o], fmt='o', ms=3.4, color=P['ink'], ecolor=P['soft'], elinewidth=0.8, capsize=1.6, zorder=3)
    ax.set_yticks([])
    ax.set_ylabel('시료 22개를 나이순으로', fontsize=8)
    ax.invert_xaxis()
    ax.text(6.65, len(a) - 0.5, '고수위 구간 8.1~5.2 ka', fontsize=8, ha='center', va='top', color=P['soft'])
    t = np.arange(4.5, 11.0001, 0.05)
    spd = sum(stats.norm.pdf(t, m, e) for m, e in zip(a, s))
    ax2.fill_between(t, spd, color=P['a'], alpha=0.75 if mode == 'color' else 0.6, linewidth=0, zorder=3)
    ax2.plot(t, spd, color=P['ink'], lw=0.7, zorder=4)
    ax2.set_xlabel('OSL 나이 (ka, 큰 쪽이 왼쪽)', fontsize=8)
    ax2.set_ylabel('합산 밀도', fontsize=8)
    f.text(0.02, 0.975, '대해호 삼각주 OSL 22개 (Huang & Chun, 2021 표를 다시 그림)', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 4: 치롄산 사구 나이 막대
def fig_qilian(mode):
    P = K.C[mode]
    f = K.fig(130, 85)
    ax = f.add_axes([0.11, 0.17, 0.85, 0.70])
    K.style_ax(ax, mode, 'y')
    Q = calc.Q
    bins = np.arange(0, 15, 1.0)
    e1 = np.array([q[5] for q in Q if q[0] == 'E1']); e2 = np.array([q[5] for q in Q if q[0] == 'E2'])
    c1, _ = np.histogram(e1, bins); c2, _ = np.histogram(e2, bins)
    ax.axvspan(4, 8, color=P['grid'], zorder=1)
    ax.bar(bins[:-1] + 0.5, c1, width=0.86, color=P['a'], edgecolor=P['ink'], linewidth=0.4, label='단면 EBD1 (27개)', zorder=3)
    ax.bar(bins[:-1] + 0.5, c2, width=0.86, bottom=c1, color=P['b'], edgecolor=P['ink'], linewidth=0.4, hatch='////' if mode == 'bw' else None, label='단면 EBD2 (22개)', zorder=3)
    ax.set_xlabel('pIRIR170 나이 (ka, 1 ka 칸)', fontsize=8)
    ax.set_ylabel('시료 수', fontsize=8)
    ax.set_xlim(0, 15)
    ax.text(6.0, 12.5, '4~8 ka: 49개 중 2개', fontsize=8, ha='center', va='bottom', color=P['ink'])
    ax.legend(fontsize=8, frameon=False, loc='upper right')
    f.text(0.02, 0.975, '기련산 사구 pIRIR 나이 49개의 분포 (Yang N. 등, 2022 표를 다시 그림)', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 5: 습윤 구간 판독
SHORT = {'대해호(Huang & Chun 2021)': '대해호', '달리호(Huang & Chun 2021이 인용)': '달리호(인용)', '차간 누르(Wang Z. 2021)': '차간 누르',
         '호륜호 꽃가루(Wen 2010)': '호륜호 꽃가루', '텅거 호(Zhang C. 2020)': '텅거 호', '무우스(Li D. 2022)': '무우스 사막', '훈산다크(Scuderi 2019)': '훈산다크',
         '내몽골 중부 사구(Sun 2006)': '내몽골 중부 사구', '후른부이르 사구(Yang & Ding 2013)': '호륜부이르 사구', '치롄산 사구(Yang N. 2022)': '기련산 사구',
         '간난 사구(Yang S. 2021)': '감남 사구', '텅거리 사막 호수(Sun & Zhu 2026)': '텅거리 호수', '우란부허 고호수(Sun & Zhu 2026)': '우란부허 호수'}

def gantt(ax, rec, mode, short=None, xmax=12.0):
    P = K.C[mode]
    names = list(rec)
    for i, nm in enumerate(names):
        y = len(names) - 1 - i
        for a, b, sgn in rec[nm]:
            K.wet_dry_bar(ax, y, min(a, xmax), b, sgn, mode)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([(short or {}).get(n, n) for n in names][::-1], fontsize=8)
    ax.set_xlim(xmax, 0)
    ax.set_ylim(-0.7, len(names) - 0.3)

def fig_windows(mode):
    P = K.C[mode]
    f = K.fig(130, 126)
    ax = f.add_axes([0.25, 0.34, 0.72, 0.58])
    ax2 = f.add_axes([0.25, 0.10, 0.72, 0.15], sharex=ax)
    K.style_ax(ax, mode, 'x'); K.style_ax(ax2, mode, 'y')
    gantt(ax, calc.REC, mode, SHORT)
    plt.setp(ax.get_xticklabels(), visible=False)
    edges = np.arange(2.0, 12.0, 1.0)
    for lo in edges:
        vals = []
        for nm, iv in calc.REC.items():
            v = [s for (a, b, s) in iv if calc.overlap((a, b), (lo, lo + 1)) >= 0.5]
            if v: vals.append(np.mean(v))
        if vals:
            m = np.mean(vals)
            ax2.bar(lo + 0.5, m, width=0.86, color=P['wet'] if m > 0 else P['dry'], edgecolor=P['ink'], linewidth=0.4, hatch=K.HATCH[mode]['wet'] if m > 0 else None, zorder=3)
    ax2.axhline(0, color=P['ink'], lw=0.6)
    ax2.set_ylim(-1.1, 1.1); ax2.set_yticks([-1, 0, 1])
    ax2.set_ylabel('칸 평균', fontsize=8)
    ax2.set_xlabel('연대 (ka, 오래된 쪽이 왼쪽)', fontsize=8)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=P['wet'], ec=P['ink'], lw=0.5, hatch=K.HATCH[mode]['wet']), plt.Rectangle((0, 0), 1, 1, fc=P['dry'], ec=P['ink'], lw=0.5)],
              labels=['습윤으로 판독', '건조로 판독'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=2)
    f.text(0.02, 0.975, '몬순 가장자리 기록 13개의 습윤·건조 구간 (이 책의 판독)', fontsize=8, va='top', color=P['ink'])
    return f

# ---------------------------------------------------------------- 그림 6: 4.2 ka 구간 겹침
def fig_overlap(mode):
    P = K.C[mode]
    f = K.fig(130, 88)
    ax = f.add_axes([0.36, 0.27, 0.60, 0.65])
    K.style_ax(ax, mode, 'x')
    rows = [('호륜호 PCA (제1권 6장)', (4210, 3840), 'v'), ('달리호 유기탄소 (제1권 6장)', (4450, 3750), 'v'), ('대해호 가뭄 (제1권 6장)', (4060, 3690), 'v'),
            ('호륜호 꽃가루 (Wen)', (4400, 3350), 't'), ('텅거 호 저수위 1', (4300, 3980), 't'), ('훈산다크 극건조', (4200, 3800), 't'), ('달리·대해 최저 수위', (4500, 3800), 't')]
    for i, (nm, iv, k) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, iv[0] - iv[1], left=iv[1], height=0.58, color=P['b'] if k == 'v' else P['a'], edgecolor=P['ink'], linewidth=0.5,
                hatch='////' if (mode == 'bw' and k == 't') else None, zorder=3)
    ax.axvspan(3840, 4060, color=P['grid'], zorder=1)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
    ax.set_xlim(4600, 3200)
    ax.set_xlabel('cal yr BP (오래된 쪽이 왼쪽)', fontsize=8)
    ax.text(3950, len(rows) - 0.35, '제1권 세 구간의 공통\n3840~4060', fontsize=8, ha='center', va='bottom', color=P['soft'])
    ax.set_ylim(-0.6, len(rows) + 0.6)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=P['b'], ec=P['ink'], lw=0.5), plt.Rectangle((0, 0), 1, 1, fc=P['a'], ec=P['ink'], lw=0.5, hatch='////' if mode == 'bw' else None)],
              labels=['제1권 6장이 옮긴 구간', '이 장이 읽은 구간'], fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.45, -0.17), ncol=2)
    return f

# ---------------------------------------------------------------- 그림 7: 수위 상승과 강수 증가
def fig_lake(mode):
    P = K.C[mode]
    f = K.fig(130, 80)
    ax = f.add_axes([0.13, 0.17, 0.82, 0.70])
    K.style_ax(ax, mode, 'both')
    rows = [('대해호(꽃가루)', 40, 34.1, 34.1), ('대해호(δ13C)', 40, 41.5, 75.6), ('달리호', 60, 100, 100), ('차간 누르', 13.5, 30, 50)]
    mk_ = ['o', 's', '^', 'D']
    for (nm, lv, lo, hi), m in zip(rows, mk_):
        if hi > lo:
            ax.plot([lv, lv], [lo, hi], color=P['soft'], lw=2.2, solid_capstyle='butt', zorder=3)
        ax.plot(lv, (lo + hi) / 2, m, ms=6.5, mfc=P['a'] if m != 's' else '#FFFFFF', mec=P['ink'], zorder=4)
        dx = {'대해호(꽃가루)': (-1.5, 'right', 6), '대해호(δ13C)': (1.5, 'left', 4), '달리호': (-1.5, 'right', 6), '차간 누르': (1.5, 'left', -10)}[nm]
        ax.text(lv + dx[0], (lo + hi) / 2 + dx[2] * 0.55, nm, fontsize=8, ha=dx[1], va='center', color=P['ink'])
    ax.set_xlabel('호수 수위 상승 (m, 현재보다)', fontsize=8)
    ax.set_ylabel('강수 증가 (%, 현재 대비)', fontsize=8)
    ax.set_xlim(0, 75); ax.set_ylim(0, 115)
    f.text(0.02, 0.975, '수위 상승과 강수 증가의 짝: 논문 값, 선은 추정 범위', fontsize=8, va='top', color=P['ink'])
    return f


if __name__ == '__main__':
    todo = [('ch01-map', fig_map), ('ch01-tengger', fig_tengger), ('ch01-daihai', fig_daihai), ('ch01-qilian', fig_qilian),
            ('ch01-windows', fig_windows), ('ch01-overlap', fig_overlap), ('ch01-lake', fig_lake)]
    only = sys.argv[1:]
    bad = 0
    for nm, fn in todo:
        if only and nm not in only:
            continue
        for m in MODES:
            w = K.save(fn(m), nm, m)
            bad += len(w)
    print('경고 합계', bad)
