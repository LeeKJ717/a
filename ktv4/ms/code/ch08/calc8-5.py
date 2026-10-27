# -*- coding: utf-8 -*-
"""계산 8-5: 5.5~5.0 ka 열대 기록의 모임.
입력(cal BP, 논문): deMenocal 등(2000) 종료 5490 +- 190; Claussen 등(1999) 모형 5440 +- 30(모형이어서 관측 평균에서 따로); Haug 등(2001) 건조 경향 시작 약 5400;
Tierney 등(2017) 남쪽 세 코어 5000, 5300, 5300, 북쪽 31N 약 6500; Thompson 등(2006) 약 5200년 전 급변(열대 빙하 여럿), Thompson 등(2002) 킬리만자로 약 5.2 ka; Mayewski 등(2004) 구간 6000~5000(중심 5500).
오차는 deMenocal 과 Claussen 만 있다."""
import numpy as np
rng = np.random.default_rng(20261027)
obs = {'deMenocal 5490': 5490, 'Haug 5400': 5400, 'Tierney 남 5000': 5000, 'Tierney 남 5300 a': 5300, 'Tierney 남 5300 b': 5300, 'Thompson 2006 5200': 5200, 'Thompson 2002 5200': 5200, 'Mayewski 중심 5500': 5500}
v = np.array(list(obs.values()), float)
print('관측 값 %d 개: %s' % (len(v), list(map(int, v))))
print('평균 %.0f, 표준편차 %.0f, 범위 %d ~ %d, 폭 %d' % (v.mean(), v.std(ddof=1), v.min(), v.max(), v.max()-v.min()))
print()
print('북쪽 Tierney 31N 6500 을 더하면(아홉 값): 평균 %.0f, 표준편차 %.0f' % (np.append(v, 6500).mean(), np.append(v, 6500).std(ddof=1)))
print('Claussen 모형 5440 을 더하면(아홉 값, 6500 제외): 평균 %.0f, 표준편차 %.0f' % (np.append(v, 5440).mean(), np.append(v, 5440).std(ddof=1)))
print()
print('오차가 있는 두 값 deMenocal 5490 +- 190 와 Claussen 5440 +- 30: 차 50, 합성 %.0f, z=%.2f' % (np.hypot(190, 30), 50/np.hypot(190, 30)))
w = np.array([1/190**2, 1/30**2]); m = (w*np.array([5490, 5440])).sum()/w.sum(); print('  역분산 가중 평균 %.0f +- %.0f (모형이 한 값 5440 에 가깝다)' % (m, w.sum()**-0.5))
print()
print('무작위 시험: 관측 여덟 값을 3000 년 창(7000~4000)에 균일하게 놓았을 때 표준편차가 관측 이하인 비율')
N = 200000
sds = rng.uniform(4000, 7000, size=(N, len(v))).std(axis=1, ddof=1)
print('  관측 표준편차 %.0f, 무작위 중앙값 %.0f, 관측 이하의 비율 %.4f' % (v.std(ddof=1), np.median(sds), (sds <= v.std(ddof=1)).mean()))
print('  창을 6000 년(8000~2000)으로 넓히면')
sds = rng.uniform(2000, 8000, size=(N, len(v))).std(axis=1, ddof=1)
print('  무작위 중앙값 %.0f, 관측 이하의 비율 %.5f' % (np.median(sds), (sds <= v.std(ddof=1)).mean()))
print('  (두 값은 저자들이 이 시기를 보려고 고른 기록이므로 선택 편향이 들어 있다. 이 비율은 우연 확률이 아니라 "얼마나 모여 보이는가"의 기준선이다.)')
print()
print('독립성 점검: Thompson 2006 과 Thompson 2002 의 5200 은 같은 연구실의 다른 빙하 코어일 수 있으나 요약에서 코어 대응을 확인하지 못했고, Tierney 남쪽 세 값은 같은 논문의 같은 방법(잎 왁스)이다.')
print('  논문 단위로 세면 독립한 출처는 deMenocal, Haug, Tierney, Thompson, Mayewski 의 다섯이다. 논문 단위 값: %s' % [5490, 5400, round(float(np.mean([5000, 5300, 5300]))), 5200, 5500])
pu = np.array([5490, 5400, round(float(np.mean([5000, 5300, 5300]))), 5200, 5500])
print('  논문 단위 평균 %.0f, 표준편차 %.0f' % (pu.mean(), pu.std(ddof=1)))
print()
print('[이웃 사건과의 거리] 여덟 값의 평균 5299 에서')
for nm, t in (('Wanner 6300', 6300), ('Wanner 4700', 4700), ('4.2 ka 공통 구간 중심 4125', 4125), ('Mayewski 4200~3800 중심 4000', 4000)):
    print('  %-28s %d 년' % (nm, abs(5299-t)))
print('  5299 는 Mayewski 6000~5000 구간 안(구간 끝 5000 까지 %d 년), Wanner 의 사건 목록에는 5300 근처 사건이 없다(가장 가까운 4700 까지 %d 년, 6300 까지 %d 년)' % (5299-5000, 5299-4700, 6300-5299))
print('  5.5~5.0 ka 모임의 폭 500 년은 4.2 ka 전지구 창의 공통 구간 50 년의 %d 배, 가장 긴 창 500 년과 같다' % (500/50))
