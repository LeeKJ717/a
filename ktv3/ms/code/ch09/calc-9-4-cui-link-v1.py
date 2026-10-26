# -*- coding: utf-8 -*-
"""계산 9-4. 제1권 11장(Cui 등, 2013)의 서요하 Y 염색체 개수를 이 장의 몽골·바이칼 개수와 이어 본다.
제1권 값은 /home/claude/book/ms/ch11-v1.md 의 표 11.3.1(대산전 9명: N1(x) 1, N1c 3, C 1, O3a 2, O3a3c 2; 금구자 12명 전원 C; 합라해구 12명 전원 N1(x); 신석기 합 18명 중 N1(x) 16)이다.
Jeong 등(2018)의 값은 본문 요약의 '주로 Q1a, 한 명 N1c1a'이다. Y를 판정한 남성 수가 요약에 없어 성별을 센 12명을 상한으로 두고 10~12명의 민감도를 본다."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stathelp import fisher_two_sided, wilson, clopper_pearson, gene_diversity
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}
print('== 계산 9-4 (a) 전원이 한 형인 시료에서 모집단 비율의 하한 ==')
for lab, k, n in [('제1권 금구자 C 계열', 12, 12), ('제1권 합라해구 N1(x)', 12, 12), ('제1권 묘자구 N1(x)', 3, 3), ('제1권 신석기 합 N1(x)', 16, 18)]:
    cp = clopper_pearson(k, n); w = wilson(k, n)
    print('%-26s %2d/%2d = %.3f, Clopper-Pearson 95%% %.3f ~ %.3f, Wilson %.3f ~ %.3f' % (lab, k, n, k / n, cp[0], cp[1], w[0], w[1]))
    res['a_' + lab] = dict(k=k, n=n, cp=cp, wilson=w)
print('12/12가 나와도 모집단 비율의 95%% 하한은 %.3f이다. "전원이 C3e였다"는 시료의 서술이고, 집단 전체가 100%%라는 뜻이 아니다.' % clopper_pearson(12, 12)[0])
print('\n== 계산 9-4 (b) 대산전 N1c 3/9 대 몽골 후기 청동기 Khövsgöl N1c1a 1/n (Jeong 2018) ==')
rows = []
for n in (10, 11, 12):
    p2, ph, pl, den = fisher_two_sided(3, 6, 1, n - 1)
    w1 = wilson(3, 9); w2 = wilson(1, n)
    print('n = %2d: 표 [[3, 6], [1, %d]], 양쪽 p = %.4f, 대산전 Wilson %.3f ~ %.3f, Khövsgöl 1/%d Wilson %.3f ~ %.3f' % (n, n - 1, p2, w1[0], w1[1], n, w2[0], w2[1]))
    rows.append(dict(n=n, p_two=p2, w1=w1, w2=w2))
res['b'] = rows
print('두 구간이 겹치고 p가 0.05보다 크므로, 두 자료의 N1c 비율이 다르다고 말할 수 없다. 같다고 말할 수도 없다(검정력이 낮다).')
print('\n== 계산 9-4 (c) 같은 표에서 하플로그룹 수준 유전자 다양도: 제1권 계산 11-4의 값 재현 ==')
sets = {'우하량': [4, 1, 1], '합라해구': [12], '대전자': [3, 2], '대산전': [1, 3, 1, 2, 2], '신석기 합': [16, 1, 1], '금구자': [12]}
res['c'] = {}
for k, v in sets.items():
    h = gene_diversity(v) if len(v) > 0 and sum(v) > 1 else float('nan')
    print('%-8s %-18s n = %2d, H = %.4f' % (k, v, sum(v), h))
    res['c'][k] = h
print('제1권 값: 우하량 0.6000, 합라해구 0, 대전자 0.6000, 대산전 0.8611, 신석기 합 0.2157. 같다.')
json.dump(res, open(os.path.join(OUT, 'calc-9-4.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
