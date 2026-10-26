# -*- coding: utf-8 -*-
"""계산 9-3. 작은 표본의 비율 비교: Fisher 정확검정(정수 구현, scipy와 대조), Wilson 구간, 순열·부트스트랩.
입력은 Maróti 등(2022), Damgaard 등(2018, Science), Jeong 등(2020)의 개수이다. 논문이 이 비교를 한 것이 아니라 논문의 개수로 이 책이 만든 시연 비교이다."""
import json, os, sys
import numpy as np
from scipy.stats import fisher_exact
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stathelp import fisher_two_sided, wilson, clopper_pearson
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}

def report(name, tab, note=''):
    (a, b), (c, d) = tab
    p2, ph, pl, den = fisher_two_sided(a, b, c, d)
    orr, p_sp = fisher_exact(tab)
    ok = abs(p_sp - p2) < 1e-12
    print('%s\n  표 %s, 합이 고정된 표의 분모 C(n, c1) = %d' % (name, tab, den))
    print('  이 책 구현: 양쪽 p = %.6f, 한쪽(첫 칸이 크다) p = %.6f, 한쪽(첫 칸이 작다) p = %.9f, scipy 양쪽 p = %.6f (%s), 표본 오즈비 = %.3f' % (p2, ph, pl, p_sp, '일치' if ok else '불일치', orr))
    if note: print('  주:', note)
    return dict(table=tab, p_two=p2, p_hi=ph, p_lo=pl, p_scipy=p_sp, odds=orr, match=ok, den=den)

print('== 계산 9-3 (a) Maróti 등(2022)의 Y 하플로그룹: 흉노·훈 계열 조상을 가진 세 아바르 시기 묘지 대 훈 시기 공개 자료 ==')
# ARK 남성 10명 중 Q 8명, MM 2명 중 Q 2명, SZRV 3명 중 Q 0(R1a-Z94 3명). 훈 시기 공개 Y 23명 중 Q 9명, R1a-Z93 10명.
q_av, n_av = 8 + 2 + 0, 10 + 2 + 3
q_hun, n_hun = 9, 23
print('아바르 시기 세 묘지: Q %d / %d = %.3f, Wilson 구간 %.3f ~ %.3f' % (q_av, n_av, q_av / n_av, *wilson(q_av, n_av)))
print('훈 시기 공개 자료  : Q %d / %d = %.3f, Wilson 구간 %.3f ~ %.3f' % (q_hun, n_hun, q_hun / n_hun, *wilson(q_hun, n_hun)))
res['a'] = report('Q 대 Q 아님', [[q_av, n_av - q_av], [q_hun, n_hun - q_hun]],
                  '한 묘지의 남성은 친족일 수 있어 독립 표본이 아니다. ARK 8명이 한 가계일 가능성을 이 책은 배제하지 못한다.')
res['a']['q_av'] = [q_av, n_av]; res['a']['q_hun'] = [q_hun, n_hun]
# 묘지 하나(ARK)만 뺀 민감도
q2, n2 = 2 + 0, 2 + 3
res['a_noARK'] = report('ARK를 뺀 민감도(MM, SZRV 5명)', [[q2, n2 - q2], [q_hun, n_hun - q_hun]], 'ARK를 빼면 5명뿐이라 검정력이 거의 없다.')
# 부트스트랩: 비율 차이
rng = np.random.default_rng(20261026)
B = 100000
b1 = rng.binomial(n_av, q_av / n_av, B) / n_av
b2 = rng.binomial(n_hun, q_hun / n_hun, B) / n_hun
diff = b1 - b2
lo, hi = np.percentile(diff, [2.5, 97.5])
print('비율 차이 (아바르 시기 - 훈 시기) = %.3f, 부트스트랩 %d회 2.5~97.5%% 구간 %.3f ~ %.3f (씨앗 20261026)' % (q_av / n_av - q_hun / n_hun, B, lo, hi))
res['a_boot'] = dict(diff=q_av / n_av - q_hun / n_hun, lo=float(lo), hi=float(hi), B=B)
# 순열 검정
lab = np.array([1] * q_av + [0] * (n_av - q_av) + [1] * q_hun + [0] * (n_hun - q_hun))
g = np.array([0] * n_av + [1] * n_hun)
obs = abs(lab[g == 0].mean() - lab[g == 1].mean())
cnt = 0; P = 100000
for _ in range(P):
    perm = rng.permutation(lab)
    if abs(perm[:n_av].mean() - perm[n_av:].mean()) >= obs - 1e-12: cnt += 1
print('순열 검정 %d회: 양쪽 p = %.5f (Fisher 정확값 %.5f와 비교)' % (P, (cnt + 1) / (P + 1), res['a']['p_two']))
res['a_perm'] = dict(p=(cnt + 1) / (P + 1), P=P)

print('\n== 계산 9-3 (b) Damgaard 등(2018, Science): Okunevo 남성 10명 중 R1b 1명 ==')
k, n = 1, 10
print('R1b 1/10 = %.2f, Wilson 95%% 구간 %.3f ~ %.3f, Clopper-Pearson %.3f ~ %.3f' % (k / n, *wilson(k, n), *clopper_pearson(k, n)))
print('논문의 Okunevo 상염색체 Yamnaya/Afanasievo 계열 10~20%%는 이 구간 안에 들어간다: %s' % (wilson(k, n)[0] <= 0.10 and 0.20 <= wilson(k, n)[1]))
res['b'] = dict(k=k, n=n, wilson=wilson(k, n), cp=clopper_pearson(k, n))

print('\n== 계산 9-3 (c) Jeong 등(2020): 한 가지 모형으로 설명되는 개체의 비율, 몽골 시대 대 후기 흉노 ==')
res['c'] = report('몽골 시대 56/61 대 후기 흉노 26/47', [[56, 5], [26, 21]],
                  '두 값의 "맞는 모형"이 같은 모형 집합이 아니다(몽골 시대는 3원천 모형, 후기 흉노는 초기형 모형). 정의가 달라 비교의 의미는 약하다. 절차를 보이는 시연이다.')
print('\n== 계산 9-3 (d) 절차 점검: 제1권 11장 계산 11-3의 값을 같은 코드로 재현 ==')
res['d1'] = report('제1권 [[16, 2], [4, 10]]', [[16, 2], [4, 10]])
res['d2'] = report('위키백과 예 [[1, 9], [11, 3]] (한쪽 p 0.001379728)', [[1, 9], [11, 3]])
json.dump(res, open(os.path.join(OUT, 'calc-9-3.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
