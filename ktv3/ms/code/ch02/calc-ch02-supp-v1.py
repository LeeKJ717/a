# -*- coding: utf-8 -*-
"""2장 보충 계산. 입력 숫자는 논문(요약 도구를 거쳐 읽은 본문과 초록)에서 옮겼다.
실행: python3 calc-ch02-supp-v1.py | tee calc-ch02-supp-v1.log
"""
import math
import numpy as np

def hdr(s):
    print('\n' + '=' * 78 + '\n' + s + '\n' + '=' * 78)

def overlap(a, b):
    a0, a1 = sorted(a); b0, b1 = sorted(b)
    return max(0.0, min(a1, b1) - max(a0, b0))

hdr('계산 2-10. 텔멘 호 코어의 시간 해상도와 역사 사건의 시험 (Struck 등, 2022)')
core, span = 161.0, 4250.0
yr_cm = span / core
print('코어 길이 %.0f cm, 바닥 나이 약 %.0f BP(기원전 2300년 = 4249 BP)' % (core, span))
print('평균 퇴적 시간 = %.0f / %.0f = %.1f 년/cm (1 cm 시료 한 개가 평균 %.1f 년)' % (span, core, yr_cm, yr_cm))
print('논문 연대 모형 두 가지(14C 모형과 총일사량 대비 모형)의 중앙값 차이는 최대 246 년, 하드워터 효과 190 ± 83 년')
for nm, w in (('1211~1225 서기(14년)', 14), ('1211~1225 서기와 건조 시작(1300 서기)까지의 거리', 1300 - 1225), ('저장 효과 오차 83년', 83)):
    print('  %-48s %5.0f 년 = %.2f cm = 모형 차이 246 년의 %.1f%%' % (nm, w, w / yr_cm, w / 246 * 100))
print('모형 차이 246 년은 1 cm 시료 %.1f 개분이다' % (246 / yr_cm))
def ce(y): return 1950 - y if y > 0 else 1949 - y
dry = (ce(700), ce(1300)); wet_a = (ce(-1200), ce(700)); wet_b = (ce(1300), 0)
ev = [('흉노(기원전 200~서기 100)', (ce(-200), ce(100))), ('위구르 제국의 가뭄(서기 783~850)', (ce(783), ce(850))), ('몽골 제국 부상기의 습윤(서기 1211~1225)', (ce(1211), ce(1225)))]
print('\n논문이 인용한 사건 구간과 이 코어의 단계(Struck 등: 습윤 1200 BCE~700 CE, 건조 700~1300 CE, 습윤 1300 CE~):')
for nm, iv in ev:
    lo, hi = min(iv), max(iv)
    L = hi - lo
    print('  %-34s %4d~%4d BP (%d년): 습윤 1200BCE~700CE 와 겹침 %3.0f%%, 건조 700~1300CE 와 겹침 %3.0f%%' % (nm, hi, lo, L, overlap(iv, wet_a) / L * 100, overlap(iv, dry) / L * 100))
print('  (사건 연대는 논문이 다른 문헌에서 인용한 것으로 요약에 적혀 있다. 이 책은 원문을 읽지 못했다.)')

hdr('계산 2-11. 울란 호 주변의 큰 호수 가설의 규모 (Mischke 등, 2020이 인용한 Sternberg & Paillou, Lehmkuhl 등)')
vol, area = 3150.0, 19000.0
print('Sternberg & Paillou(2015) 인용: 호수 최대 %.0f km2, 부피 %.0f km3 -> 평균 깊이 = %.0f m (고지 해안선 44, 124, 259 m)' % (area, vol, vol / area * 1000))
print('  Mischke 의 현대 기록: 1960년대 65 km2, 큰 비 뒤 최대 175 km2 -> 19000 / 175 = %.0f 배, 19000 / 65 = %.0f 배' % (area / 175, area / 65))
print('Lehmkuhl 등(2018) 인용: 4.4 ka 에 약 500 km2 -> 현대(1960년대 65 km2)의 %.1f 배, 최대 175 km2 의 %.1f 배' % (500 / 65, 500 / 175))
print('Mischke 의 구간 5(6.8~3.2 ka) 패충류: 거의 없고 대부분 외래(Ilyocypris). 큰 호수에 맞는 증거라고 보지 않는다고 논문이 쓴다.')

hdr('계산 2-12. 고비 발굴지 유물 수의 산술 (Michalec 등, 2025, 요약 도구의 숫자)')
raw = {'벽옥': 50.73, '옥수': 45.85, '플린트': 3.30}
tot = 2726
cnt = {k: v / 100 * tot for k, v in raw.items()}
print('유물 총수 %d. 원료 비율을 개수로: ' % tot + ', '.join('%s %.1f개' % (k, v) for k, v in cnt.items()) + ' (반올림 %d + %d + %d = %d), 오팔 2 + 규암질 사암 1 = 3개 -> 합 %d' % (round(cnt['벽옥']), round(cnt['옥수']), round(cnt['플린트']), round(cnt['벽옥']) + round(cnt['옥수']) + round(cnt['플린트']), round(cnt['벽옥']) + round(cnt['옥수']) + round(cnt['플린트']) + 3))
a = 1711 + 661 + 290
print('폐석류 조각 1711 + 격지 661 + 작은 돌날 290 = %d. 여기에 핵석 10 + 예비 핵석 1 + 도구 36 = 47 -> %d. 총수 %d 와의 차 %d (= 덩어리 17개와 같음)' % (a, a + 47, tot, tot - a - 47))
b = 1711 + 631 + 235 + 17 + 47
print('본문의 다른 곳의 숫자(격지 631, 작은 돌날 235, 덩어리 17)로 계산하면 1711 + 631 + 235 + 17 + 47 = %d, 총수와의 차 %d' % (b, tot - b))
print('도구 36 = 작은 돌날 소재 24 + 격지 소재 11 + 기타 %d' % (36 - 24 - 11))
print('사용 흔적 분석 46개 중 사용 22개 = %.1f%%. 접합 58 덩어리 144 개 -> 덩어리당 평균 %.1f 개' % (22 / 46 * 100, 144 / 58))
print('발굴 18 m2, 20~25 cm 깊이 -> 부피 %.1f ~ %.1f m3, 유물 밀도 %.0f ~ %.0f 개/m3 (경사와 이동이 있는 지층이라 밀도는 참고값)' % (18 * 0.20, 18 * 0.25, tot / (18 * 0.25), tot / (18 * 0.20)))
print('OSL 연대 4개 중 8130 ± 83 BP 가 가장 젊은 호성 퇴적물이며, 유물 층(Unit 7, 8)과 연대의 관계는 요약에 없다. 원문 확인 필요.')

hdr('계산 2-13. 몽골 안쪽 기록과 몬순 가장자리 기록의 칸 평균을 나란히 놓고 견주기 (이 책의 판독, 계산 2-8과 1장 계산 1-6)')
from scipy import stats
bins = ['11~12', '10~11', '9~10', '8~9', '7~8', '6~7', '5~6', '4~5', '3~4', '2~3']
mon = np.array([+0.33, +0.33, +0.67, +0.17, +0.33, -0.33, -0.33, -0.67, -0.57, +0.29])
mar = np.array([-1.00, -0.75, -0.43, +0.33, +1.00, +0.77, +0.40, 0.00, -0.50, -0.43])
print('칸(ka) | 몽골 안쪽(n 3~7) | 가장자리(n 3~13) | 부호')
for b, m1, m2 in zip(bins, mon, mar):
    sg = '반대' if m1 * m2 < 0 else ('같음' if m1 * m2 > 0 else '0 포함')
    print('  %-6s | %+.2f | %+.2f | %s' % (b, m1, m2, sg))
r, p = stats.pearsonr(mon, mar); rs, ps = stats.spearmanr(mon, mar)
print('피어슨 r = %.2f (겉보기 p = %.3f), 스피어만 rho = %.2f (겉보기 p = %.3f), 칸 %d개' % (r, p, rs, ps, len(bins)))
def lag1(x):
    x = x - x.mean(); return (x[1:] * x[:-1]).sum() / (x * x).sum()
print('칸 평균 계열의 1차 자기상관: 몽골 %.2f, 가장자리 %.2f' % (lag1(mon), lag1(mar)))
rho = (lag1(mon) * lag1(mar))
ne = len(bins) * (1 - rho) / (1 + rho)
print('두 계열의 자기상관의 곱 %.2f -> 유효 표본 n_eff = n (1 - rho) / (1 + rho) = %.1f (근사)' % (rho, ne))
tc = stats.t.ppf(0.975, max(ne - 2, 1)); rc = tc / math.sqrt(max(ne - 2, 1) + tc ** 2)
print('  유효 표본 %.1f 에서 양쪽 5%% 임계 |r| = %.2f. 관측 |r| = %.2f' % (ne, rc, abs(r)))
rng = np.random.default_rng(20261026)
cnt = 0; N = 50000
for _ in range(N):
    q = rng.permutation(mar)
    if abs(np.corrcoef(mon, q)[0, 1]) >= abs(r): cnt += 1
print('칸을 무작위로 섞는 순열 검정(%d회, 시드 20261026) 양쪽 p = %.3f (자기상관을 무시한 값)' % (N, (cnt + 1) / (N + 1)))
same = int(((mon * mar) > 0).sum()); opp = int(((mon * mar) < 0).sum())
print('부호가 같은 칸 %d개, 반대인 칸 %d개, 한쪽이 0인 칸 %d개' % (same, opp, len(bins) - same - opp))
# 블록 부트스트랩(블록 길이 3) 근사
def block_boot(x, y, B=20000, L=3):
    n = len(x); out = []
    for _ in range(B):
        idx = []
        while len(idx) < n:
            s = rng.integers(0, n - L + 1); idx.extend(range(s, s + L))
        idx = idx[:n]
        a, b = x[idx], y[idx]
        if a.std() > 0 and b.std() > 0: out.append(np.corrcoef(a, b)[0, 1])
    return np.array(out)
bb = block_boot(mon, mar)
print('블록 부트스트랩(블록 3칸, 2만 회): r 의 95%% 구간 = %.2f ~ %.2f' % (np.percentile(bb, 2.5), np.percentile(bb, 97.5)))
