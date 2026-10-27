# -*- coding: utf-8 -*-
"""계산 8-2: 홀로세 냉각 사건의 간격과 "주기" 주장.
입력(논문): Wanner 등(2011) 사건 8200, 6300, 4700, 2700, 1550, 550 BP, "뚜렷한 주기 없음". Mayewski 등(2004) 구간 중심 8500, 5500, 4000, 3000, 1100, 375.
Bond 등(2001): 약 12,000 년 동안 홀로세 순환 아홉 개(0~8), 평균 1340 년(요약에서 읽은 값), "순환이 주기성을 뜻하지 않는다".
무작위 시험: 창 안에 사건 n 개를 균일하게 놓았을 때 이웃 간격의 변동계수(표준편차/평균)가 관측만큼 작은(규칙적인) 비율."""
import numpy as np
rng = np.random.default_rng(20261027)
def gaps(ts):
    ts = np.sort(ts)[::-1]
    return -np.diff(ts)
def cv(g): return g.std(ddof=1)/g.mean()
sets = {'Wanner 등 사건': [8200, 6300, 4700, 2700, 1550, 550],
        'Mayewski 등 구간 중심': [8500, 5500, 4000, 3000, 1100, 375]}
for nm, ts in sets.items():
    g = gaps(np.array(ts, float))
    print('%s: 간격 %s, 평균 %.0f, 표준편차 %.0f, 변동계수 %.3f, 최소 %.0f 최대 %.0f' % (nm, [int(x) for x in g], g.mean(), g.std(ddof=1), cv(g), g.min(), g.max()))
    lo, hi = min(ts), max(ts)
    # 무작위: 같은 범위(lo~hi)의 양 끝을 고정하고 가운데 n-2 개를 균일하게
    N = 200000
    n = len(ts)
    cvs = np.empty(N)
    for i in range(N):
        mid = rng.uniform(lo, hi, n-2)
        t = np.sort(np.concatenate([[lo, hi], mid]))
        gg = np.diff(t)
        cvs[i] = gg.std(ddof=1)/gg.mean()
    print('   끝을 고정한 무작위 배치의 변동계수 중앙값 %.3f, 관측 이하의 비율 %.3f (작을수록 규칙적)' % (np.median(cvs), (cvs <= cv(g)).mean()))
print()
print('Bond 등(2001): 12000 / 9 = %.1f 년 (요약에서 읽은 평균 1340 과 %.1f %% 차)' % (12000/9, 100*abs(12000/9-1340)/1340))
print('   아홉 순환이면 간격은 여덟 개이므로 12000 / 8 = %.0f 년 (순환 수와 간격 수를 헷갈리면 이 정도 달라진다)' % (12000/8))
print()
print('Wanner 의 평균 간격과 비교')
g = gaps(np.array(sets['Wanner 등 사건'], float))
print('   Wanner 평균 간격 %.0f 년은 Bond 의 1340 보다 %.0f 년 길다 (비 %.2f)' % (g.mean(), g.mean()-1340, g.mean()/1340))
m = gaps(np.array(sets['Mayewski 등 구간 중심'], float))
print('   Mayewski 중심 평균 간격 %.0f 년은 Bond 의 1340 보다 %.0f 년 길다 (비 %.2f)' % (m.mean(), m.mean()-1340, m.mean()/1340))
print()
print('Wanner 의 사건이 놓인 길이 8200-550 = %d 년 안에 1340 년 간격은 %.1f 번 들어간다(사건은 여섯, 간격은 다섯)' % (8200-550, (8200-550)/1340))
print('Bond 의 창 12000 년 대 Wanner 의 창 7650 년의 비 %.2f, 순환 수 9 대 사건 수 6 의 비 %.2f' % (12000/7650, 9/6))
print('주의: 변동계수 0.29 는 간격이 1000~2000 년 사이라는 뜻이며, 같은 간격이 되풀이되는 주기(변동계수 0 에 가까움)는 아니다. 사건 선정이 저자 몫이므로 검정의 p 는 선택 효과를 반영하지 못한다')
