## 8.13 도구 소개

{{T:8장 분석에 쓰이거나 같은 분석에 쓸 수 있는 도구. 도구 이름은 논문이 밝힌 것이며, 라이선스와 입수처는 이 책이 확인하지 못한 항목을 그렇게 표시}}

| 도구 | 용도 | 근거 | 라이선스·입수처 |
|---|---|---|---|
| Daybreak 2200 OSL 판독기 | 석영 OSL 측정(청색·적외 LED) | Lu 등(2007) | 장비. 해당 없음 |
| Risø TL/OSL 판독기, 감마 분광기 | OSL, pIRIR 측정과 선량률(Aarhus) | Stevens 등(2018) | 장비. 해당 없음 |
| Bacon(R) | 베이즈 연대-깊이 모형 | Stevens 등(2018) | 입수처 확인 필요 |
| Undatable | 연대 불확실성을 넣은 연대-깊이 모형 | Ahn 등(2024) | 입수처 확인 필요 |
| IntCal20 | 방사성탄소 보정 곡선 | Ahn 등(2024) | 확인 필요 |
| MaxUnmix | IRM 획득 곡선의 성분 분해 | Ahn 등(2024) | 확인 필요 |
| Bartington MS2 자화율계 | 자화율 측정(저주파 0.47 kHz, 고주파 4.7 kHz) | Ahn 등(2024), Stevens 등 | 장비 |
| MicroMag 3900 AGM/VSM | 자기 이력 곡선, 등온 잔류 자화, FORC | Ahn 등(2024) | 장비 |
| ICP-MS(Thermo X SERIES 2) | 미량 원소와 희토류 | Dou 등(2021) | 장비 |
| Python(math, 직접 작성한 최소제곱·하버사인) | 이 장의 계산 재현(ch08-calc-v1.py) | 이 책 | 표준 라이브러리만 사용 |

**이 장의 계산을 직접 해 보는 코드.** 계산 8-3의 기울기와 오차, 계산 8-5의 하버사인이다.

```python
import math
def ols(pts):
    n=len(pts); mx=sum(p[0] for p in pts)/n; my=sum(p[1] for p in pts)/n
    sxx=sum((p[0]-mx)**2 for p in pts); sxy=sum((p[0]-mx)*(p[1]-my) for p in pts)
    b=sxy/sxx; a=my-b*mx
    res=sum((p[1]-a-b*p[0])**2 for p in pts)
    return b, a, math.sqrt(res/(n-2)/sxx)
print(ols([(10,100),(20,250),(30,340)]))        # (12.0, -10.0, 1.732...)
def hav(la1,lo1,la2,lo2,R=6371.0088):
    p1,p2=math.radians(la1),math.radians(la2)
    a=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(a))
print(round(hav(37.4980,108.9040,37.49965,108.90076)*1000,1))   # 340.0 m
```

## 8.14 데이터 입수처

{{T:8장 관련 데이터 입수처. 논문 인용 = 논문이 사용했다고 밝힌 자료, 본서 조사 = 이 책이 직접 확인}}

| 자료 | 내용 | 근거 | 확인 상태 |
|---|---|---|---|
| Jingbian 발광 연대 220개, 자화율, 입도 | 구역 A~E | Stevens 등(2018)의 Supplementary Data 1 | 입수 경로 확인 필요 |
| 해저 퇴적물 LR04 δ18O 스택 | 바다 기준 곡선 | Lisiecki & Raymo(2005), Guo 등과 Stevens 등이 인용 | 입수처 확인 필요 |
| NGRIP δ18O(GICC05 연대) | 그린란드 온도 | Rao 등(2013)이 인용 | 입수처 확인 필요 |
| 남극 EDC 먼지, δD | 남극 먼지 플럭스와 온도 | Lambert 등(2008), Jouzel 등(2007), Guo 등(2009)이 인용 | 입수처 확인 필요 |
| 북위 65° 7월 일사량 | 천문 강제력 | Stevens 등(2018)이 인용 | 입수처 확인 필요 |
| SRTM 90 m, RESDC 자료 | 지형, 행정 자료 | Stevens 등(2018) 그림 1 | 입수처 확인 필요 |
| 기상청 기후 자료 | 서울 1981~2010년 평균 | Ahn 등(2024)이 접속한 날짜(2022-02-02) | 접속 확인하지 못했다 |
| 동해 코어 LV53-18-2의 원소·동위원소 | 120개 시료 | Dou 등(2021) | 입수 경로 확인 필요 |

## 8.15 더 읽을 책

{{T:8장 관련 교재와 편람. 5장 목록을 재사용하며 이 장 연결을 적음. 내용은 이 책이 읽은 것이 아니다}}

| 책 | 서지 | 이 장과의 연결 |
|---|---|---|
| Paleoclimatology: Reconstructing Climates of the Quaternary | Bradley, R. S. (2013). 제3판. Elsevier. ISBN 9780123869135 | 황토, 고토양, 안정 동위원소 8.11.4 |
| Quaternary Dating Methods | Walker, M. (2005). John Wiley & Sons. ISBN 9780470869277 | OSL, 발광 연대 8.11.1 |
| Reconstructing Quaternary Environments | Lowe, J. J., & Walker, M. (2015). 제3판. Routledge. ISBN 9780131274686 | 퇴적 환경과 연대 8.11.2 |

이 표의 책은 이 책이 내용을 읽은 것이 아니다. 8장의 수치는 위 책에서 가져오지 않았다.

## 8.16 인물로 읽는 이 장

<div class="bio" markdown="1">

![사진 자리: 유동생(劉東生). 공용 저작물 확인 후 삽입](portrait-liu-v1)

#### 유동생(劉東生, 1917–2008): 황토를 환경의 기록으로 읽은 지질학자

**연결.** Lu 등(2007)은 Luochuan 단면의 층서와 환경 연구를 인용하면서 「Liu, T.S. (Ed.), 1985. Loess and the Environment. China Ocean Press, Beijing」을 든다. 이 서지의 저자 이니셜 T.S. Liu가 아래의 인물과 같은 사람이라는 점은 이 책이 서지로 확인하지 못했다. 이름의 로마자 표기(Tungsheng/Dongsheng) 때문에 그렇게 읽었을 뿐이다. 아래 서술은 위키백과 "Liu Dongsheng" 항목을 읽은 내용이며 2차 자료이다.

**생애.** 1917년 11월 22일 랴오닝 성 선양에서 태어나 2008년 3월 6일 베이징에서 90세로 죽었다. 1942년 국립서남연합대학 지질학과를 졸업했고 1946~1949년에는 국립중앙대학(지금의 난징대학)에서 생물학을 공부했다. 칭화대학 화학과 교수를 지냈고, 중국과학원의 척추고생물·고인류학 연구소와 지질지구물리 연구소의 연구원이었다. 연구 분야는 고생물학, 제4기 지질학, 환경 지질학으로 적혀 있다.

**수상.** 1980년 중국과학원 원사, 1991년 제3세계 과학원 회원, 2002년 타일러 환경 업적상, 2003년 국가 최고 과학기술상. 국제제4기학연합(INQUA)이 2011년부터 4년마다 "Liu Tungsheng 공로 메달"을 준다고 적혀 있다.

**이 책이 확인하지 못한 것.** 이 항목에는 황토 연구의 내용이 적혀 있지 않았다. 그가 황토 연구에서 한 일은 이 책이 아는 범위에서 위 서지 한 줄로만 연결된다. 사진은 공용 저작물 여부를 확인하지 못했다.

</div>

<div class="bio" markdown="1">

![사진 자리: 페르디난트 폰 리히트호펜. 공용 저작물 확인 후 삽입](portrait-richthofen-v1)

#### 페르디난트 폰 리히트호펜(Ferdinand von Richthofen, 1833–1905): 중국을 지질학으로 읽고 "비단길"이라는 말을 만든 지리학자

**연결.** 황토고원은 서양 지질학이 처음 본 이 지역의 대표적 퇴적물이다. 그러나 이 책이 확인한 위키백과 "Ferdinand von Richthofen" 항목은 황토나 바람 퇴적설을 전혀 언급하지 않는다. 그가 황토의 기원에 대해 어떤 주장을 했는지는 이 책이 읽은 자료에 없으므로 쓰지 않는다. 근거 논문 확보 필요. 아래는 그 항목에서 읽은 것이다(2차 자료).

**생애.** 1833년 5월 5일 프로이센령 슐레지엔의 카를스루에(지금의 폴란드 포쿠이)에서 태어나 1905년 10월 6일 베를린에서 72세로 죽었다. 브레슬라우의 가톨릭 김나지움을 다니고 브레슬라우 대학과 베를린 대학에서 공부했다. 1860~1862년 프로이센 오일렌부르크 탐사대와 동·동남아시아를 방문했고(항목은 기록과 수집품을 잃어 이렇다 할 성과가 없었다고 적는다), 1862~1868년 미국에서 지질학자로 일하며 캘리포니아에서 금광을 찾았다. 그 뒤 중국을 여러 차례 여행했고 일본, 미얀마, 자바도 갔다. 항목에는 중국 여행의 날짜가 따로 없다. 1879년 본 대학, 1883년 라이프치히 대학, 1886년 베를린 대학 교수가 되었고 베를린 대학 교수직을 죽을 때까지 지켰다. 독일 지리학회장을 오래 맡았고 베를린 수로학 연구소를 세웠다. 제자로 스벤 헤딘, 알프레트 필리프슨 등이 적혀 있다.

**업적.** 1877년 "Seidenstraße"(비단길)라는 말을 만들었다고 한다. 롭노르의 말라붙은 호수 바닥을 찾았고 산둥의 탄전과 자오저우 항에 처음 주목했다고 적혀 있다. 울러스턴 메달(1892)과 베가 메달(1903)을 받았고 치롄 산맥이 한때 그의 이름으로 불렸다.

**이 책이 확인하지 못한 것.** 이 항목은 중국 저작의 출판 연도를 본문(1877~85)과 서지(1877~1912년, 5권)에서 다르게 적는다. 사진은 공용 저작물 여부를 확인하지 못했다.

</div>

## 8.17 8장 주장 검증 장부

{{T:8장 주장 검증 장부. 수준: 직접 = 이 책에서 원문을 읽고 확인, 재인용 = 다른 논문이 인용(원문 미확인), 해석 = 저자의 해석, 본서계산 = 이 책의 산술, 시연값 = 절차를 보이기 위한 가정값, 2차 = 백과사전, 본서 조사 = 공식 페이지 확인, 미결 = 근거 불충분}}

| 번호 | 주장 | 주장자 | 근거 | 수준 |
|---|---|---|---|---|
| 8-1 | Luochuan 33개 OSL 나이는 De ÷ 선량률과 맞는다(차이 0.37 ka 이하) | 이 책 | 계산 8-1 | 본서계산 |
| 8-2 | 표의 열이 흩어져 시료와 값의 짝은 이 책이 맞추었다 | 이 책 | 원문 표 판독 | 미결(원문 쪽 확인 필요) |
| 8-3 | 감도 보정 MAR 방법이 감도 변화를 보정하고 신호 누적을 피한다 | Lu 등(2007) | 보충자료 실험 | 해석(보충자료 미확인) |
| 8-4 | SAR은 고토양 시료에서 평균 8%, 최대 13% 낮게 읽힌다 | Lu 등(2007) | 23개 시료 비교 | 직접 |
| 8-5 | 13% 과소는 409 Gy에서 약 16 ka의 차이를 낳는다 | 이 책 | 계산 8-4 | 본서계산 |
| 8-6 | S1/L1 기준 73.9 ± 2.6 ka와 두 시료의 차이는 1 σ 안이다(비 0.65, 0.95) | 이 책 | 계산 8-2 | 본서계산 |
| 8-7 | "나이를 과소평가하지 않았다" | Lu 등(2007) | 기준 나이, TL, 기후층서 | 해석(시료 2개) |
| 8-8 | L1-1, L1-2(S), L1-3의 퇴적률은 6.4, 14.5, 10.1 cm/ka | Lu 등(2007) | 깊이-나이 회귀 | 직접 |
| 8-9 | 이 책의 회귀는 6.39 ± 0.99, 14.44 ± 0.81, 10.10 ± 1.63을 준다 | 이 책 | 계산 8-3 | 본서계산 |
| 8-10 | 퇴적률이 MIS 3의 약한 고토양에서 가장 높다 | Lu 등(2007) | OSL 회귀 | 직접 |
| 8-11 | 이 높은 퇴적률은 식생 피복이 먼지를 붙잡은 결과일 수 있다 | Lu 등(2007) | 저자 추정 | 해석 |
| 8-12 | 입도 모형은 74~12 ka의 퇴적률을 일정하게 가정하며 오차 ±1~3 ka | Porter와 An(Lu 등의 소개) | 인용 | 재인용 |
| 8-13 | 경계 29.3 ± 1.5 ka 대 시료 나이 중간값 29.8 ka | Lu 등(2007), 이 책 | 계산 8-3 | 미결 |
| 8-14 | ICS 기준 단면 Jingbian의 발광 연대 220개로 대형 휴지면(최대 약 60 ka)이 있다 | Stevens 등(2018) | 연대-깊이 모형 | 직접(해석) |
| 8-15 | 마지막 두 빙하기(MIS 2~4, 6)의 기록이 거의 없다 | Stevens 등(2018) | 연대 분포 | 직접 |
| 8-16 | 원인은 빙하 극대기의 강한 겨울 몬순과 사구 이동에 의한 침식 | Stevens 등(2018) | 모래 위치, 침식 가설 | 해석 |
| 8-17 | 이 단면의 황토는 빙하기가 아니라 간빙기 안의 추운 시기에 쌓였다 | Stevens 등(2018) | 연대, 자화율 | 해석 |
| 8-18 | 이 발견은 "바람 먹기"(aeolian cannibalism)의 첫 독립 증거이다 | Stevens 등(2018) | 저자 서술 | 해석(재인용 포함) |
| 8-19 | ICS의 Jingbian 연대는 틀렸고 개정되어야 한다 | Stevens 등(2018) | 저자 결론 | 직접(주장) |
| 8-20 | Ding 등의 단면 좌표는 틀렸다 | Stevens 등(2018) | 좌표 사슬 | 직접(주장) |
| 8-21 | 구역 A와 철탑 좌표의 거리는 340 m | 이 책 | 계산 8-5 | 본서계산(논문 약 330 m) |
| 8-22 | Ding 등의 좌표는 Guojialiang에서 약 40 km | Stevens 등(2018) | 저자 서술 | 직접(수치 미확인) |
| 8-23 | 장석 pIRIR 잔류 선량 5 ± 2 Gy | Stevens 등(2018) | 절편 1.43 ± 0.47 ka × 3.5 | 직접, 본서계산(5.01 ± 1.65) |
| 8-24 | 함수율을 약 3 σ 올려야 홀로세 지연이 사라진다 | Stevens 등(2018) | 15에서 30%, 10에서 25% | 직접, 본서계산 |
| 8-25 | Jingbian 자화율은 북위 65° 7월 일사량보다 평균 4.9 ka 늦다(표준오차 0.7, n = 9) | Stevens 등(2018) | 변곡점 비교 | 직접(보충표 2 미확인) |
| 8-26 | 이 지연의 95% 구간은 3.29~6.51 ka | 이 책 | 계산 8-7 | 본서계산 |
| 8-27 | 지연은 기준 곡선에 따라 약 7 ka까지 늘 수 있다 | Stevens 등(2018) | Clemens 등의 기준 | 직접(재인용 포함) |
| 8-28 | 몬순 가장자리는 세차 신호에 직접 반응하지 않고 빙상·해수면·CO2의 영향을 받는다 | Stevens 등(2018) | 지연 | 해석 |
| 8-29 | Yuanbao 마지막 빙하기 여름 강수는 약 150~350 mm, Jingyuan은 20~150 mm | Rao 등(2013) | δ13C(TOC) | 직접(해석) |
| 8-30 | 식 P = −58 × (δ13C − 1) − 1266.5로 읽힌다 | 이 책 | 원문 줄 판독 + 415와 385 mm 일치 | 본서계산(원문 쪽 확인 필요) |
| 8-31 | 식 기울기 58 mm/‰, ±70 mm는 δ13C로 ±1.2‰, 측정 ±0.2‰는 ±12 mm | 이 책 | 계산 8-8 | 본서계산 |
| 8-32 | 조정한 연대의 Yuanbao 강수가 Hulu δ18O와 일치하고, 동굴 δ18O가 마지막 빙하기 몬순 세기의 지표이다 | Rao 등(2013) | NGRIP 조정 | 해석(순환의 위험) |
| 8-33 | 조정 전 OSL 연대는 20~60 ka에서 NGRIP 기준보다 약 4~5 ka 젊다 | Rao 등(2013) | 저자 서술 | 직접 |
| 8-34 | 인도양 수온 모의가 동굴 δ18O의 해석에 대안을 준다 | Rao 등이 소개한 모의 | 인용 | 재인용 |
| 8-35 | MIS 13에서 남극은 상대적으로 춥고 아시아 여름 몬순은 가장 강했다 | Guo 등(2009) | 황토와 얼음 코어 대비 | 직접(해석) |
| 8-36 | Xifeng 시료 723개와 Changwu 715개, 황토 해상도 약 800년, 고토양 약 2000년 | Guo 등(2009) | 방법 | 직접 |
| 8-37 | 황토 시간은 자화율을 바다 δ18O(LR04)에 맞춘 것이다 | Guo 등(2009) | 방법 | 직접(독립 연대 아님) |
| 8-38 | 평균 해상도 1107년은 고토양 시료 비율 약 25%일 때 두 해상도와 일관한다 | 이 책 | 계산 8-9 | 본서계산(실제 비율 미확인) |
| 8-39 | 먼지 플럭스 = 퇴적률 × 2.5 g/cm³ | Guo 등(2009) | 방법 | 직접 |
| 8-40 | 하남 단면의 kE 구간 두 곳: 0.53~0.81 m(홀로세)와 1.31~1.61 m(MIS 3 말) | Ahn 등(2024) | 자화율, 연대-깊이 | 직접 |
| 8-41 | kE 구간 평균 퇴적률 약 3~4 cm/ka, 황토고원 홀로세(약 20)의 5~6분의 1 | Ahn 등(2024), 이 책 | 계산 8-10 | 직접, 본서계산 |
| 8-42 | kFD%는 홀로세 kE가 MIS 3 kE보다 평균 약 1.4배 | Ahn 등(2024) | 측정 | 직접 |
| 8-43 | 자성 광물은 SPD~PSD 크기의 토양 생성 자철석이 주된 기여자 | Ahn 등(2024) | IRM 분해, FORC, I/C | 해석 |
| 8-44 | 홀로세 kE의 kLF는 TOC(R = 0.832), δ13C(R = 0.825)와 양의 상관, MIS 3 kE는 무상관 | Ahn 등(2024) | 상관 | 직접 |
| 8-45 | 두 kE의 차이는 식생 피복과 수문 기후의 차이에서 나온다 | Ahn 등(2024) | 비교 | 해석 |
| 8-46 | kE_MIS3의 연대는 OSL 1개에 부분적으로 기대 불확실하다 | Ahn 등(2024) | 저자 인정 | 직접 |
| 8-47 | 세 단면(망월동, 덕소, 고덕동) 사이의 거리는 2~5 km | 이 책 | 계산 8-10 | 본서계산 |
| 8-48 | 연강수 1000 mm 넘는 남부 황토고원에서 자화율이 강수와 맞지 않는다 | Ahn 등이 소개한 연구 | 인용 | 재인용 |
| 8-49 | 동해 코어 퇴적률: 빙하기 20.7, 탈빙기 10.7, 홀로세 10.3 cm/ka, 평균 76년/cm | Dou 등(2021), 이 책 | 계산 8-11 | 직접, 본서계산 |
| 8-50 | 최성기에 북중국 건조 지대의 먼지와 해빙이 퇴적물을 날랐고, 8 ka 이후 리만 한류가 화산 물질을 날랐다 | Dou 등(2021) | Sr-Nd, 원소 | 해석 |
| 8-51 | 농도가 같다고 두면 Nd와 Sr가 다른 일본 열도 호 비율을 준다 | 이 책 | 계산 8-12 | 본서계산(시연) |
| 8-52 | 두 끝 성분만으로 코어를 설명할 수 있다 | Dou 등(2021) | 혼합 곡선 | 미결(끝 성분 농도 미확인) |
| 8-53 | 유동생(劉東生)의 생애와 수상 | Wikipedia | 2차 자료 | 2차 |
| 8-54 | 리히트호펜의 생애와 "비단길" 조어 | Wikipedia | 2차 자료 | 2차 |
| 8-55 | 리히트호펜의 황토 기원 주장 | — | 근거 확보 필요 | 미결 |

## 참고문헌

Ahn, H.-S., Park, S., & Lim, J. (2024). Magnetic enhancement in paleosols with hydroclimatic and vegetation cover variabilities (Holocene vs. late MIS 3) in the central Korean Peninsula. *Scientific Reports, 14*, Article 21323. https://doi.org/10.1038/s41598-024-72347-6

Dou, R., Zou, J., Shi, X., Zhu, A., Dong, Z., Gorbarenko, S., He, L., Gao, J., Zhang, Y., & Cui, J. (2021). Geochemical and isotopic evidence for provenance of the western Sea of Japan over the last 30000 years. *Frontiers in Earth Science, 9*, Article 638178. https://doi.org/10.3389/feart.2021.638178

Guo, Z. T., Berger, A., Yin, Q. Z., & Qin, L. (2009). Strong asymmetry of hemispheric climates during MIS-13 inferred from correlating China loess and Antarctica ice records. *Climate of the Past, 5*, 21–31. https://doi.org/10.5194/cp-5-21-2009

Lu, Y. C., Wang, X. L., & Wintle, A. G. (2007). A new OSL chronology for dust accumulation in the last 130,000 yr for the Chinese Loess Plateau. *Quaternary Research, 67*, 152–160. https://doi.org/10.1016/j.yqres.2006.08.003

Rao, Z., Chen, F., Cheng, H., Liu, W., Wang, G., Lai, Z., & Bloemendal, J. (2013). High-resolution summer precipitation variations in the western Chinese Loess Plateau during the last glacial. *Scientific Reports, 3*, Article 2785. https://doi.org/10.1038/srep02785

Stevens, T., Buylaert, J.-P., Thiel, C., Újvári, G., Yi, S., Murray, A. S., Frechen, M., & Lu, H. (2018). Ice-volume-forced erosion of the Chinese Loess Plateau global Quaternary stratotype site. *Nature Communications, 9*, Article 983. https://doi.org/10.1038/s41467-018-03329-2

Wikipedia contributors. (n.d.-a). Ferdinand von Richthofen. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Ferdinand_von_Richthofen

Wikipedia contributors. (n.d.-b). Liu Dongsheng. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Liu_Dongsheng
