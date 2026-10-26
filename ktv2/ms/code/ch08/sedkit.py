# -*- coding: utf-8 -*-
"""sedkit v1: 제2권 8장의 계산 모음. numpy와 scipy만 쓴다. 이 폴더의 실습 스크립트가 불러다 쓴다.
 (1) 풍화 지수: CIA, CIW, PIA, A-CN-K 좌표
 (2) 끝 성분 혼합: 두 성분(농도 가중), 세 성분(두 동위원소 계 + 질량 보존)
 (3) 입도: 누적 곡선, 백분위, Folk와 Ward 도해 통계, 적률 통계
 (4) 유사량: Brune 포획 효율, 구간 수지, 퇴적률·질량 집적률·유사 수율
각 함수의 식은 8장 본문에 같이 적혀 있다."""
import math
import numpy as np
from scipy import interpolate

VERSION = 'sedkit v1'

# ------------------------------------------------------------------ 1. 풍화 지수
MW = dict(Al2O3=101.961, CaO=56.077, Na2O=61.979, K2O=94.196, P2O5=141.945)   # 제1권 10장 계산 10-8과 같은 값(g/mol)


def to_mol(Al2O3, CaO, Na2O, K2O, P2O5=0.0):
    """산화물 질량 %를 100 g당 몰로 바꾼다."""
    return (Al2O3 / MW['Al2O3'], CaO / MW['CaO'], Na2O / MW['Na2O'], K2O / MW['K2O'], P2O5 / MW['P2O5'])


def cao_star(c, n, p, rule='A'):
    """규산염 광물의 CaO(몰)를 구하는 규칙.
    A: min(CaO - 10/3 P2O5, Na2O), 음수 허용 (제1권 10장이 쓴 규칙)
    B: CaO* = CaO (인회석 보정 없음)
    C: A에서 음수이면 0
    D: min(CaO, Na2O)"""
    if rule == 'A':
        return min(c - 10.0 / 3.0 * p, n)
    if rule == 'B':
        return c
    if rule == 'C':
        return max(0.0, min(c - 10.0 / 3.0 * p, n))
    if rule == 'D':
        return min(c, n)
    raise ValueError(rule)


def cia(Al2O3, CaO, Na2O, K2O, P2O5=0.0, rule='A'):
    a, c, n, k, p = to_mol(Al2O3, CaO, Na2O, K2O, P2O5)
    cs = cao_star(c, n, p, rule)
    return 100.0 * a / (a + cs + n + k)


def ciw(Al2O3, CaO, Na2O, K2O, P2O5=0.0, rule='A'):
    """CIW = 100 Al / (Al + CaO* + Na). K를 뺀 지수. 식은 일반적으로 알려진 꼴이며 원문은 확인하지 못했다."""
    a, c, n, k, p = to_mol(Al2O3, CaO, Na2O, K2O, P2O5)
    cs = cao_star(c, n, p, rule)
    return 100.0 * a / (a + cs + n)


def pia(Al2O3, CaO, Na2O, K2O, P2O5=0.0, rule='A'):
    """PIA = 100 (Al - K) / (Al - K + CaO* + Na). 식은 일반적으로 알려진 꼴이며 원문은 확인하지 못했다."""
    a, c, n, k, p = to_mol(Al2O3, CaO, Na2O, K2O, P2O5)
    cs = cao_star(c, n, p, rule)
    return 100.0 * (a - k) / (a - k + cs + n)


def ack(Al2O3, CaO, Na2O, K2O, P2O5=0.0, rule='A'):
    """A-CN-K 삼각도의 세 좌표(합 100). A = Al2O3, CN = CaO* + Na2O, K = K2O (모두 몰)."""
    a, c, n, k, p = to_mol(Al2O3, CaO, Na2O, K2O, P2O5)
    cs = cao_star(c, n, p, rule)
    s = a + cs + n + k
    return 100.0 * a / s, 100.0 * (cs + n) / s, 100.0 * k / s


# ------------------------------------------------------------------ 2. 끝 성분 혼합
def mix_x(f, e1, e2, c1=1.0, c2=1.0):
    """끝 성분 1의 질량 몫이 f일 때 혼합물의 값. 원소 농도 c1, c2로 가중."""
    f = np.asarray(f, dtype=float)
    return (f * c1 * e1 + (1 - f) * c2 * e2) / (f * c1 + (1 - f) * c2)


def mix_f(x, e1, e2, c1=1.0, c2=1.0):
    """관측값 x에서 끝 성분 1의 질량 몫 f를 푼다. c1 = c2이면 (x - e2)/(e1 - e2)."""
    x = np.asarray(x, dtype=float)
    return c2 * (x - e2) / (c1 * (e1 - x) + c2 * (x - e2))


def conc_ratio_needed(f, x, e1, e2):
    """질량 몫이 f이고 관측값이 x가 되려면 필요한 c2/c1."""
    return f * (e1 - x) / ((1 - f) * (x - e2))


def unmix(c, R, obs):
    """세 끝 성분과 두 동위원소 계의 질량 몫을 푼다.
    c: (계 수 2, 끝 성분 수 3)의 농도, R: 같은 모양의 동위원소 값, obs: 계마다 혼합물의 값(길이 2).
    식 k: sum_i f_i c_ki (R_ki - obs_k) = 0, 그리고 sum f_i = 1. 3원 1차 연립방정식이다."""
    c = np.asarray(c, float); R = np.asarray(R, float); obs = np.asarray(obs, float)
    A = np.vstack([c * (R - obs[:, None]), np.ones(c.shape[1])])
    b = np.array([0.0, 0.0, 1.0])
    return np.linalg.solve(A, b), A


def mix_forward(c, R, f):
    """질량 몫 f에서 계마다 혼합물의 값."""
    c = np.asarray(c, float); R = np.asarray(R, float); f = np.asarray(f, float)
    return (c * R * f).sum(axis=-1) / (c * f).sum(axis=-1)


# ------------------------------------------------------------------ 3. 입도
def mm_to_phi(d_mm):
    return -np.log2(np.asarray(d_mm, float))


def phi_to_um(phi):
    return 1000.0 * 2.0 ** (-np.asarray(phi, float))


def cumulative(edges_phi, wt):
    """등급 경계(φ, 오름차순 = 거친 쪽에서 고운 쪽)와 등급별 무게 %에서 누적 %(거친 쪽부터)를 만든다.
    반환: 경계 φ 배열(길이 n+1)과 누적 %(길이 n+1, 첫 값 0, 끝 값 100)."""
    wt = np.asarray(wt, float)
    cum = np.concatenate([[0.0], np.cumsum(wt)])
    return np.asarray(edges_phi, float), 100.0 * cum / cum[-1]


def percentile_phi(edges_phi, cum, p, method='linear'):
    """누적 %가 p가 되는 φ. 누적은 거친 쪽(작은 φ)부터이다. 즉 φ16은 16 %가 그보다 거친 φ이다."""
    p = np.atleast_1d(np.asarray(p, float))
    if method == 'linear':
        return np.interp(p, cum, edges_phi)
    if method == 'pchip':
        # 누적이 같은 값으로 이어지는 구간이 있으면 pchip의 x가 단조 증가가 아니므로 중복을 없앤다
        keep = np.concatenate([[True], np.diff(cum) > 0])
        f = interpolate.PchipInterpolator(cum[keep], edges_phi[keep])
        return f(p)
    raise ValueError(method)


def folk_ward(phi5, phi16, phi25, phi50, phi75, phi84, phi95):
    """Folk와 Ward의 도해 통계(φ 단위). 평균, 분급(포괄 도해 표준편차), 왜도, 첨도."""
    mean = (phi16 + phi50 + phi84) / 3.0
    sort = (phi84 - phi16) / 4.0 + (phi95 - phi5) / 6.6
    skew = (phi16 + phi84 - 2 * phi50) / (2 * (phi84 - phi16)) + (phi5 + phi95 - 2 * phi50) / (2 * (phi95 - phi5))
    kurt = (phi95 - phi5) / (2.44 * (phi75 - phi25))
    return mean, sort, skew, kurt


def fw_from_table(edges_phi, wt, method='linear'):
    edges, cum = cumulative(edges_phi, wt)
    q = percentile_phi(edges, cum, [5, 16, 25, 50, 75, 84, 95], method)
    return folk_ward(*q), q


def moments_phi(edges_phi, wt):
    """등급 가운데 값(중점)으로 구한 적률 통계: 평균, 표준편차, 왜도, 첨도(초과 아님, 정규 분포에서 3)."""
    e = np.asarray(edges_phi, float)
    mid = 0.5 * (e[:-1] + e[1:])
    w = np.asarray(wt, float); w = w / w.sum()
    m = (w * mid).sum()
    s = math.sqrt((w * (mid - m) ** 2).sum())
    sk = (w * (mid - m) ** 3).sum() / s ** 3
    ku = (w * (mid - m) ** 4).sum() / s ** 4
    return m, s, sk, ku


def class_weights_from_cdf(edges_phi, cdf):
    """연속 분포의 누적분포함수에서 등급별 무게 %를 만든다. 표 바깥의 꼬리는 버리고 합을 100으로 맞춘다."""
    c = np.array([cdf(x) for x in edges_phi])
    w = np.diff(c)
    return 100.0 * w / w.sum()


# ------------------------------------------------------------------ 4. 유사량
def brune_te(V, Q):
    """Hu 등(2009)이 쓴 꼴의 Brune 포획 효율. TE = 1 - 0.05 / sqrt(V/Q). V, Q의 단위는 같은 부피 단위(km3, km3/yr)."""
    V = np.asarray(V, float); Q = np.asarray(Q, float)
    return 1.0 - 0.05 / np.sqrt(V / Q)


def v_for_te(te, Q):
    """포획 효율 te(0~1)가 되는 저수량: V/Q = (0.05/(1-te))^2."""
    return Q * (0.05 / (1.0 - te)) ** 2


def lsr(thick_cm, years):
    """선형 퇴적률 cm/ka."""
    return thick_cm / years * 1000.0


def mar(lsr_cm_ka, dbd):
    """질량 집적률 g/cm2/ka = 선형 퇴적률(cm/ka) x 건조 부피 밀도(g/cm3)."""
    return lsr_cm_ka * dbd


def yield_t_km2_yr(S_Mt, A_1e4km2):
    """유사 수율 t/km2/yr. 유사량 Mt/yr, 면적 10^4 km2."""
    return S_Mt * 1e6 / (A_1e4km2 * 1e4)


def runoff_mm(Q_km3, A_1e4km2):
    """유출 깊이 mm/yr. 유량 km3/yr, 면적 10^4 km2. 1 km3 / 1 km2 = 1000 m = 10^6 mm."""
    return Q_km3 / (A_1e4km2 * 1e4) * 1e6
