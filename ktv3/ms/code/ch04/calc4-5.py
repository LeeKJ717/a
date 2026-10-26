# -*- coding: utf-8 -*-
"""계산 4-5: 논문 초록이 적은 습윤·건조(또는 숲 확대·개방) 서술을 1000년 칸(cal BP)에 옮겨 겹침을 센다.
이것은 이 책의 코딩이다. 논문이 낸 숫자도, 논문의 판정도 아니다. 칸 하나에 구간이 절반 이상 걸쳐야 그 부호를 받는다.
부호: +1 = 논문이 습윤, 숲 확대, 호수 수위 상승 쪽으로 서술, -1 = 건조, 개방, 수위 하강 쪽으로 서술, 0 = 서술 없음 또는 반대 부호가 섞임.
구간은 (오래된 쪽 ka, 젊은 쪽 ka, 부호, 논문 서술 요지)로 적는다. 다른 지표(온도 등)만 말한 서술은 넣지 않았다.
"""
import json, itertools
import numpy as np
R = {
 'Hoton-Nur(Rudaya 2009)': [(11.5, 10.0, -1, '열린 식생, 강수 200~250 mm'), (10.0, 5.0, +1, '숲, 강수 300~550 mm'), (5.0, 0.0, -1, '숲 감소, 강수 250~300 mm')],
 'Ugii Nuur(Wang 2009)': [(8.66, 7.8, +1, '온화, 반습윤'), (7.8, 6.86, -1, '건조성 식물 증가, 점점 따뜻하고 건조'), (6.86, 3.17, -1, '반사막 스텝 확대'), (3.17, 2.34, +1, '삼림 스텝 확대, 서늘하고 습윤'), (2.34, 1.6, +1, '서늘하고 습윤')],
 'Hulun(Wen 2010)': [(11.0, 8.0, -1, '건조 스텝'), (8.0, 6.4, +1, '초본과 자작나무 확대, 강수 증가'), (6.4, 4.4, -1, '서늘하고 건조'), (4.4, 3.35, -1, '명아주과 우세, 극도 건조'), (3.35, 2.05, +1, '쑥 회복, 조건 개선'), (2.05, 1.0, -1, '기온과 강수 모두 감소')],
 'Bayan Nuur(Tian 2014)': [(12.9, 8.5, -1, '건조한 영거 드라이아스, 비교적 건조한 이른 홀로세'), (8.5, 3.0, +1, '강수 최적기'), (3.0, 0.0, -1, '건조한 늦은 홀로세')],
 'Minusinsk(Dirksen 2007)': [(11.7, 7.6, -1, '건조기'), (7.6, 5.1, +1, '유효 수분 증가'), (3.6, 3.3, -1, '건조 간격'), (1.5, 0.0, -1, '대체로 더 건조')],
 'Kotokel(Tarasov 2009)': [(12.8, 11.6, -1, '열린 스텝과 툰드라, 연강수 270~300 mm'), (10.8, 7.3, +1, '타이가 최대, 연강수 500~550 mm')],
 'Teletskoye(Rudaya 2016)': [(3.9, 3.6, -1, '서늘하고 건조, 스텝 비슷한 식생'), (3.5, 1.6, +1, '침엽수 산림 확대')],
 'Ulaan(Mischke 2020)': [(12.3, 9.4, +1, '수위 상승, 염분 감소, 습윤 최고'), (6.8, 3.2, -1, '수위 하강 뒤 염분 상승'), (3.2, 0.0, -1, '호수 축소')],
 'Ulagan(Blyakharchuk 2004)': [(12.0, 9.5, +1, '더 따뜻하고 습윤, 숲 형성')],
 'Altai 상부숲(Huang 2018)': [(10.0, 7.0, +1, '숲 면적 최대')],
 'Hovsgol(Prokopenko 2007)': [(11.0, 7.0, +1, '강수와 유출 증가'), (6.0, 3.5, -1, '여름 따뜻, 수분 낮아 숲 감소')],
 'Kulunda 꽃가루(Rudaya 2012)': [(4.4, 3.75, -1, '따뜻하고 건조, 반사막과 건조 스텝'), (3.75, 0.09, +1, '침엽수 확대(가장 큼은 PZ IV)'), (0.09, 0.0, -1, 'AD 1860 이후 스텝과 반사막 복귀')],
 'Kulunda 규조(Rudaya 2012)': [(3.96, 1.92, -1, '얕고 어쩌면 마른 호수, 규조 거의 없음')],
 '건조 중앙아시아 종합(Chen 2008)': [(11.7, 8.0, -1, '많은 호수가 매우 낮은 수위, 마름'), (8.0, 0.0, +1, '그 뒤 더 습윤(초기~중기 더 습윤, 늦은 홀로세 중간 습윤)')],
}
BINS = [(k, k + 1) for k in range(0, 12)]      # (젊은 쪽, 오래된 쪽) ka
def state(intervals, lo, hi):
    pos = neg = 0.0
    for a, b, s, _ in intervals:       # a 오래된, b 젊은
        ov = max(0.0, min(a, hi) - max(b, lo))
        if s > 0: pos += ov
        else: neg += ov
    full = hi - lo
    if pos >= full / 2 and neg < full / 2: return +1
    if neg >= full / 2 and pos < full / 2: return -1
    return 0
M = {n: [state(iv, lo, hi) for lo, hi in BINS] for n, iv in R.items()}
print('=== 계산 4-5 (1) 코딩 표(칸: 0~1, 1~2, ..., 11~12 ka) ===')
print('%-34s %s' % ('기록', ' '.join('%2d' % (lo + 1) for lo, hi in BINS)))
for n, v in M.items():
    print('%-34s %s' % (n, ' '.join({1: ' +', -1: ' -', 0: ' .'}[x] for x in v)))
print()
print('=== 계산 4-5 (2) 칸마다 + 기록 수, - 기록 수 ===')
print('%-8s %4s %4s %6s %8s %s' % ('칸(ka)', '+', '-', '서술수', '다수 비율', '판정'))
conf = []
for j, (lo, hi) in enumerate(BINS):
    p = sum(1 for v in M.values() if v[j] > 0); m = sum(1 for v in M.values() if v[j] < 0)
    tag = '서로 다름' if p and m else ('한쪽만' if p + m else '서술 없음')
    if p and m: conf.append(j)
    print('%2d~%-2d     %4d %4d %6d %8.2f %s' % (lo, hi, p, m, p + m, max(p, m) / (p + m), tag))
print('양쪽 부호가 모두 나온 칸: %d / 12 → %s ka' % (len(conf), [('%d~%d' % BINS[j]) for j in conf]))
print()
print('=== 계산 4-5 (3) 두 기록이 함께 서술한 칸에서의 일치율 (공통 칸 3개 이상인 쌍) ===')
rows = []
for a, b in itertools.combinations(M, 2):
    both = [j for j in range(12) if M[a][j] != 0 and M[b][j] != 0]
    if len(both) >= 3:
        agree = sum(1 for j in both if M[a][j] == M[b][j])
        rows.append((agree / len(both), len(both), a, b))
rows.sort(reverse=True)
tot_n = sum(r[1] for r in rows); tot_a = sum(round(r[0] * r[1]) for r in rows)
for fr, n, a, b in rows:
    print('  %.2f (%d칸)  %s  |  %s' % (fr, n, a, b))
print('쌍 %d 개, 공통 칸 합 %d, 일치 칸 합 %d: 합친 일치율 %.3f ; 쌍마다 일치율의 평균 %.3f' % (len(rows), tot_n, tot_a, tot_a / tot_n, np.mean([r[0] for r in rows])))
# 무작위 부호 기준선(이 책의 점검): 같은 코딩 칸에서 부호를 섞어 일치율의 분포를 본다
rng = np.random.default_rng(4105)
def mean_agree(MM):
    rr = []
    for a, b in itertools.combinations(MM, 2):
        both = [j for j in range(12) if MM[a][j] != 0 and MM[b][j] != 0]
        if len(both) >= 3: rr.append(sum(1 for j in both if MM[a][j] == MM[b][j]) / len(both))
    return np.mean(rr), len(rr)
obs, npair = mean_agree(M)
sims = []
for _ in range(5000):
    MM = {n: [int(rng.choice([1, -1])) if x != 0 else 0 for x in v] for n, v in M.items()}   # 칸마다 부호를 임의로(서술 있는 칸의 위치는 그대로)
    sims.append(mean_agree(MM)[0])
sims = np.array(sims)
print('\n이 책의 순열형 점검: 서술이 있는 칸의 위치는 그대로 두고 부호만 임의(±1 같은 확률)로 5000번 바꾸면 평균 일치율은 중앙 %.2f (95%%: %.2f~%.2f). 관측(쌍마다 평균) %.2f 는 위 분포의 %.1f%% 위치.' % (np.median(sims), *np.percentile(sims, [2.5, 97.5]), obs, (sims < obs).mean() * 100))
print('주의: 부호를 칸마다 독립으로 섞으면 시간적으로 이어진 구간이라는 구조를 무시한다. 기준선이 지나치게 느슨하다. 이 값은 "논문들이 서로 같은 쪽을 말하는 정도"의 대략 감각이다.')
json.dump(dict(bins=BINS, M=M, R={n: [list(x) for x in iv] for n, iv in R.items()}), open('calc4-5-out.json', 'w'), ensure_ascii=False)
