# -*- coding: utf-8 -*-
"""6장 공용 입력: 4.2 ka 사건 기록 목록. 모든 연대는 보정 연대(cal yr BP, 1950년 기준). 값은 논문 초록·본문에서 읽은 것이며 '읽은 수준'과 '출처'를 함께 둔다.
dir: 'dry'(건조), 'wet'(습윤), 'none'(이상 없음), 'melt'(따뜻함, 녹은 물 많음). start 가 더 오래된 값. s_sd 는 논문이 적은 시작 연대의 오차(1 표준편차로 가정, 표시한 경우만).
읽은 수준: 전=본문 읽음, 초=초록 읽음, 2=2차 쪽(요약·색인)만, 제=서지·제목만."""
R = [
 # id, 지역, 지점, 방향, 시작, 끝, 시작 오차, 읽은 수준, 출처, 메모
 dict(id='Hulun', reg='동아시아', site='호륜호(내몽골 북동)', dir='dry', start=4210, end=3840, s_sd=None, lvl='전', src='Xiao 등(2018)', memo='PCA F1, 깊이 88~83 cm'),
 dict(id='Dali', reg='동아시아', site='달리호', dir='dry', start=4450, end=3750, s_sd=None, lvl='전(재인용)', src='Xiao 등(2018)이 Xiao 등(2008) 인용', memo='TOC 감소, 저수위'),
 dict(id='Daihai', reg='동아시아', site='다이하이호', dir='dry', start=4060, end=3690, s_sd=None, lvl='전(재인용)', src='Xiao 등(2018)', memo='가뭄'),
 dict(id='Hunsh', reg='동아시아', site='훈산다크 모래땅', dir='dry', start=4200, end=3800, s_sd=None, lvl='전', src='Scuderi 등(2019)', memo='4.2~3.8 ka 급격한 건조'),
 dict(id='Shennong', reg='동아시아', site='신농동굴(장시)', dir='wet', start=4200, end=3900, s_sd=None, lvl='초', src='Zhang 등(2018)', memo='4.5~3.57 ka 건조 속의 습윤 구간'),
 dict(id='Xianglong', reg='동아시아', site='상룡동굴', dir='wet', start=4300, end=3800, s_sd=None, lvl='재인용(제1권 6장)', src='Zhang 등(2018), 제1권 6장', memo=''),
 dict(id='Dongge', reg='동아시아', site='동거동굴', dir='dry', start=4400, end=3950, s_sd=None, lvl='재인용(제1권 6장)', src='Zhang 등(2018), 제1권 6장', memo=''),
 dict(id='KoreaAP', reg='동아시아', site='한국 남해안 코어', dir='dry', start=4200, end=3600, s_sd=None, lvl='초', src='Park 등(2019)', memo='교목 꽃가루 두 차례 감소 4.2~3.6, 중심 4.2'),
 dict(id='Gol', reg='서아시아', site='골에자르드 동굴(이란)', dir='dry', start=4260, end=3970, s_sd=66, lvl='전', src='Carolin 등(2019)', memo='Mg/Ca 먼지, U-Th 25개'),
 dict(id='GolP1', reg='서아시아', site='골에자르드 동굴 첫 사건', dir='dry', start=4510, end=4400, s_sd=None, lvl='전', src='Carolin 등(2019)', memo='110년'),
 dict(id='GOman', reg='서아시아', site='오만만 코어 M5-422', dir='dry', start=4025, end=3625, s_sd=125, lvl='전', src='Cullen 등(2000)', memo='먼지 급증. 본문 4025 ± 150, 약 400년(초록 ± 125, 약 300년)'),
 dict(id='Roberts', reg='지중해', site='동지중해 종합', dir='dry', start=4500, end=3900, s_sd=None, lvl='초', src='Roberts 등(2011)', memo='건조 국면 4500~3900 BP'),
 dict(id='Bosten1', reg='중앙아시아', site='보스텐호', dir='dry', start=4600, end=4300, s_sd=None, lvl='초', src='Wunnemann 등(2006)', memo='4.6~4.3'),
 dict(id='Bosten2', reg='중앙아시아', site='보스텐호', dir='dry', start=3900, end=3600, s_sd=None, lvl='초', src='Wunnemann 등(2006)', memo='3.9~3.6'),
 dict(id='Bosten0', reg='중앙아시아', site='보스텐호 사이 구간(건조 아님)', dir='none', start=4300, end=3900, s_sd=None, lvl='초', src='Wunnemann 등(2006)에서 이 책이 계산', memo='두 건조기 사이 400년'),
 dict(id='Karakul', reg='중앙아시아', site='카라쿨(파미르)', dir='melt', start=4200, end=3500, s_sd=None, lvl='초', src='Mischke 등(2010)', memo='따뜻하고 녹은 물 많음. 코어가 4200년에서 시작'),
 dict(id='LopNur', reg='중앙아시아', site='롭노르', dir='dry', start=4000, end=1300, s_sd=None, lvl='초', src='Wang 등(2026)', memo='4000년 전 이후 건조화(7800~4000은 습함)'),
 dict(id='Altai', reg='중앙아시아', site='하르 노르(몽골 알타이)', dir='dry', start=4200, end=3700, s_sd=None, lvl='초', src='Bliedtner 등(2021)', memo='"약 3.7 ka 이전 건조 증가"; 코어가 4.2 ka부터'),
 dict(id='Aral', reg='중앙아시아', site='아랄해', dir='dry', start=4500, end=4500, s_sd=None, lvl='초', src='Krivonogov 등(2010)', memo='묻힌 사주, 약 38 m. 점'),
 dict(id='Kotla', reg='남아시아', site='코틀라다하르(인도 하리아나)', dir='dry', start=4100, end=3900, s_sd=None, lvl='초(+2차)', src='Dixit 등(2014)', memo='δ18O +4‰ 약 4.1 ka; 기간 약 200년은 보도 요약'),
]
RAILSBACK = dict(center=4070, lo=3930, hi=4150, n_records=12, src='Railsback 등(2018)')   # 사건 중심과 경계
