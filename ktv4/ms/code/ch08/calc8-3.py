# -*- coding: utf-8 -*-
"""계산 8-3: 4.2 ka 즈음 전지구 기록의 방향 집계(건조 대 습윤)와 구간 폭.
입력: 제3권 6장 계산 6-5 의 유라시아 19곳(건조 12, 습윤 3, 변화 없음 3, 따뜻함과 녹은 물 1) + 이 장이 새로 읽은 기록.
새 기록의 방향(논문 서술을 한 단어로 줄임): Booth 등(2005) 북미 대륙 중부 가뭄(건조), Thompson 등(2002) 킬리만자로 약 4 ka 이동이 역사적 가뭄과 이어짐(건조),
Marchant 와 Hooghiemstra(2004) 약 4000 BP: 아프리카 대부분 지점 건조 / 남미 대부분 지점 습윤(지점 수 확인 못함, 각각 한 줄로 셈),
Bini 등(2019) 지중해: 겨울 건조 일부 지역 습윤(혼합). 나미비아 DP1(Railsback 등)은 제3권 6장의 19곳(남반구 습윤 1)에 이미 들어 있으므로 새로 세지 않는다.
분류는 이 책이 논문의 서술을 한 단어로 줄인 것이며 저자의 분류가 아니다."""
import numpy as np
from scipy import stats
def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a/2, k, n-k+1)
    hi = 1.0 if k == n else stats.beta.ppf(1-a/2, k+1, n-k)
    return lo, hi
eur = dict(dry=12, wet=3, none=3, melt=1)
new = {'Booth 등(북미 중부)':'dry', 'Thompson 등(킬리만자로)':'dry', 'Marchant 등 아프리카':'dry', 'Marchant 등 남미':'wet', 'Bini 등(지중해)':'mixed'}
cnt = {'dry':0, 'wet':0, 'mixed':0}
for k, v in new.items(): cnt[v] += 1
print('새 기록 5개의 방향:', cnt)
print('제3권 6장 유라시아 19곳:', eur)
D = eur['dry'] + cnt['dry']; W = eur['wet'] + cnt['wet']
print('건조 대 습윤만 센 합계(변화 없음, 따뜻함, 혼합 제외): 건조 %d, 습윤 %d, 합 %d' % (D, W, D+W))
lo, hi = cp(D, D+W)
print('  건조 비율 %.3f, Clopper-Pearson 95%% 구간 %.3f ~ %.3f' % (D/(D+W), lo, hi))
print('  동전 던지기(0.5) 대비 단측 이항 p=%.4f' % stats.binomtest(D, D+W, 0.5, alternative='greater').pvalue)
print()
print('새 기록 4개(혼합 제외)만: 건조 %d, 습윤 %d' % (cnt['dry'], cnt['wet']))
lo, hi = cp(cnt['dry'], cnt['dry']+cnt['wet']); print('  건조 %d/%d 의 95%% 구간 %.3f ~ %.3f' % (cnt['dry'], cnt['dry']+cnt['wet'], lo, hi))
print()
print('유라시아 19곳 안의 건조 비율: 12/19 = %.3f, 95%% 구간 %.3f ~ %.3f' % (12/19, *cp(12, 19)))
print('유라시아 19곳 + 새 5곳 = 24곳 중 방향이 건조인 곳 %d 곳 = %.1f %%' % (D, 100*D/24))
print()
print('건조 쪽을 모두 포함하되 분모를 24 로 하면 건조 %.1f %%, 습윤 %.1f %%, 변화 없음 %.1f %%, 기타(따뜻함 1, 혼합 1) %.1f %%' % (100*D/24, 100*W/24, 100*3/24, 100*2/24))
print()
print('지역별(새 기록): 건조 쪽은 북미 중부, 동아프리카 산, 아프리카 열대 일반. 습윤 쪽은 남미 열대(남아프리카 서부 나미비아는 제3권 6장의 19곳에 이미 있음).')
print('  대륙 단위 비교(아프리카 열대 건조, 남미 열대 습윤)는 지점 수가 둘뿐이어서 검정하지 않는다.')
