## 11.11 도구 소개

{{T:11장 분석에 쓰이거나 같은 분석에 쓸 수 있는 도구. 도구 이름은 논문이 밝힌 것이며, 라이선스와 입수처는 이 책이 확인하지 못한 항목을 그렇게 표시}}

| 도구 | 용도 | 근거 | 라이선스·입수처 |
|---|---|---|---|
| Arlequin v3.5 | AMOVA, Φ 통계 | Duggan 등(2013) | 입수처와 이용 조건 확인 필요 |
| Network 4.6, Network Publisher 1.3 | 중간 결합(median-joining) 네트워크, rho 연대(전이보다 전환에 3배 가중) | Duggan 등(2013) | 입수처와 이용 조건 확인 필요 |
| BEAST v1.6 | 베이즈 스카이라인(BSP). 돌연변이율 1.708 × 10⁻⁸, 9.883 × 10⁻⁸ | Duggan 등(2013) | 입수처와 이용 조건 확인 필요 |
| STATISTICA v10 | 대응 분석(CA), 다차원 척도법(MDS) | Duggan 등(2013) | 상용. 입수처 확인 필요 |
| R 패키지 ade4(Mantel 검정), geosphere(대원 거리) | 거리 행렬 상관, 지리 거리 | Duggan 등(2013) | 입수처와 이용 조건 확인 필요 |
| YHRD(Y Chromosome Haplotype Reference Database) | Y-STR 하플로타입 조회 | Cui 등(2013) | 웹 서비스(yhrd.org). 이용 조건 확인 필요 |
| COFECHA | 나이테 교차 연대 결정의 점검 | Lyu 등(2016), Holmes(1983) | 입수처와 이용 조건 확인 필요 |
| ARSTAN | 나이 경향 제거, 연대기 | Lyu 등(2016), Cook(1985) | 입수처와 이용 조건 확인 필요 |
| Velmex 측정기 | 테 너비 0.001 mm | Lyu 등(2016) | 장비 |
| SPSS 12.0 | 상관, 회귀 | Lyu 등(2016) | 상용 |
| Python(math, scipy, numpy) | 이 장의 계산 재현(ch11-calc-v1.py, figs-ch11.py) | 이 책 | 표준 라이브러리, numpy, scipy |

**이 장의 계산을 직접 해 보는 코드.** Fisher 정확검정, 유전자 다양도, ρ 연대 환산, 상관의 임계값, RE와 CE, EPS이다. 숫자는 11장의 계산 상자와 같다.

```python
import math
from math import comb
def fisher_two_sided(a, b, c, d):                                   # 합계 고정, 초기하분포
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    pr = lambda x: comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9))
print(round(fisher_two_sided(16, 2, 4, 10), 5))                      # 0.00079
def nei_h(counts):
    n = sum(counts)
    return n / (n - 1) * (1 - sum((c / n) ** 2 for c in counts))
print(round(nei_h([4, 1, 1]), 4), round(nei_h([16, 1, 1]), 4))       # 0.6 0.2157
def years_per_step(mu, loci, gen): return gen / (mu * loci)
print(round(years_per_step(0.0025, 9, 30), 1))                       # 1333.3
def re_ce(obs, est, cal_mean):
    sse = sum((o - e) ** 2 for o, e in zip(obs, est))
    m = sum(obs) / len(obs)
    return 1 - sse / sum((o - cal_mean) ** 2 for o in obs), 1 - sse / sum((o - m) ** 2 for o in obs)
print([round(v, 4) for v in re_ce([7.0, 7.4, 7.9, 7.2, 8.1, 7.6], [7.2, 7.3, 7.6, 7.5, 7.8, 7.5], 7.5)])   # [0.625, 0.6221]
def eps(n, r): return n * r / (1 + (n - 1) * r)
print(round(eps(15, 0.28), 3), round(0.85 * (1 - 0.22) / (0.15 * 0.22), 2))   # 0.854 20.09
def n_eff(n, r1, r2): return n * (1 - r1 * r2) / (1 + r1 * r2)
print(round(n_eff(414, 0.72, 0.72), 1))                              # 131.3
```

## 11.12 데이터 입수처

{{T:11장 관련 데이터 입수처. 논문 인용 = 논문이 사용했다고 밝힌 자료, 본서 조사 = 이 책이 직접 확인}}

| 자료 | 내용 | 근거 | 확인 상태 |
|---|---|---|---|
| 서요하 유적 조사 자료(cadb.pitt.edu/shelach, cadb.pitt.edu/chifeng) | 적봉 지역 조사 자료 | Shelach-Lavi 등(2019)이 밝힌 입수처 | 이 책이 접속하지 못함. 확인 필요 |
| DANS 저장소 doi 10.17026/dansxs7-rmqh | 논문의 자료 | Shelach-Lavi 등(2019)이 밝힌 입수처 | 이 책이 접속하지 못함. 확인 필요 |
| 보충 자료 S1 Text, S2~S6 그림 | 논문의 보충 | Shelach-Lavi 등(2019) | 이 책이 읽지 못함 |
| Cui 등(2013)의 보충 표 | 시료별 STR 하플로타입 | Cui 등(2013) | 이 책이 읽지 못함. 확보 필요 |
| YHRD | Y-STR 하플로타입 참조 | Cui 등(2013) | 접속하지 못함. 확인 필요 |
| Duggan 등(2013)의 표 S1~S3 | 서열, 하플로타입 사람 수 | Duggan 등(2013) | 이 책이 읽지 못함 |
| 노백산 연대기와 돈화 기상 자료 | 연륜 지수, 월 기온 | Lyu 등(2016)이 NOAA 고기후 자료실에 두었다고 밝힘 | 이 책이 접속하지 못함. 확인 필요 |
| 복원값(1600~2013) | 4~7월 평균 최저기온 | Lyu 등(2016) | 연별 값은 이 책이 읽은 본문에 수치로 없음. 확보 필요 |
| 서요하 신석기·청동기 기후 자료 | 호소 퇴적물 등 | — | 이 책이 아직 읽지 못함(11.10절) |
| Natural Earth 벡터 지도 | 이 장의 지도 바탕(육지, 하천, 호수, 도시) | 이 책 | 지도 제작에 사용. 라이선스 문구는 공식 페이지에서 확인하지 않았다. 확인 필요 |

## 11.13 더 읽을 책

{{T:11장 관련 교재와 편람. 10장 목록을 재사용하며 이 장 연결을 적음. 내용은 이 책이 읽은 것이 아니다}}

| 책 | 서지 | 이 장과의 연결 |
|---|---|---|
| Paleoclimatology: Reconstructing Climates of the Quaternary | Bradley, R. S. (2013). 제3판. Elsevier. ISBN 9780123869135 | 나이테 등 대리 지표와 기후 복원 11.5 |
| Quaternary Dating Methods | Walker, M. (2005). John Wiley & Sons. ISBN 9780470869277 | 14C와 보정 11.2, 11.9.9 |
| Reconstructing Quaternary Environments | Lowe, J. J., & Walker, M. (2015). 제3판. Routledge. ISBN 9780131274686 | 환경 복원과 연대 11.2, 11.5 |

이 표의 책은 이 책이 내용을 읽은 것이 아니다. 11장의 수치는 위 책에서 가져오지 않았다. 집단유전학과 통계 교재는 이 책이 아직 목록을 확보하지 못했다.

## 11.14 인물로 읽는 이 장

<div class="bio" markdown="1">

![사진 자리: 피셔(Ronald A. Fisher). 공용 저작물 확인 후 삽입](portrait-fisher-v1)

#### 로널드 피셔(Ronald Aylmer Fisher): Fisher 정확검정의 이름이 된 사람

**연결.** 11.3.3절의 검정은 이 사람의 이름을 쓴다. Cui 등(2013)은 고대 집단의 작은 표본을 비교하는 데 이 검정을 썼다고 방법에 적었다. 아래 서술은 이 책이 읽은 영어 위키백과 "Ronald Fisher" 항목과 "Fisher's exact test" 항목이며 2차 자료이다.

**생애.** 1890년 2월 17일 런던 이스트 핀칠리에서 태어나 1962년 7월 29일 오스트레일리아 애들레이드에서 사망했다. 해로 학교를 거쳐 1909년 케임브리지 대학 곤빌 앤 케이어스 칼리지에 들어가 1912년 우등으로 졸업했다. 평생 시력이 나빠 군에 지원했으나 받아들여지지 않았다고 항목은 쓴다. 1919년 로담스테드 실험장에 들어가 14년 일했고, 1933년 유니버시티 칼리지 런던의 골턴 교수가 되었으며, 1943년 케임브리지의 발포어 유전학 교수가 되었다.

**저작과 상.** 『연구자를 위한 통계 방법』(1925), 『자연선택의 유전 이론』(1930), 『실험의 설계』(1935)가 있다. 『실험의 설계』에 차 맛 보기 일화가 실렸고 이 책에서 정확검정이 소개되었다고 한다. 1952년 기사 작위, 1955년 코플리 메달.

**이 책이 확인하지 못한 것.** 일화의 세부와 1922년 논문의 쪽수. 사진은 공용 저작물 여부를 확인하지 못했다.

</div>

<div class="bio" markdown="1">

![사진 자리: 피어슨(Karl Pearson). 공용 저작물 확인 후 삽입](portrait-pearson-v1)

#### 칼 피어슨(Karl Pearson): 상관계수를 적률 상관으로 정의한 사람

**연결.** 11.5절의 R = 0.757은 피어슨 상관계수이다. 아래 서술은 이 책이 읽은 영어 위키백과 "Karl Pearson" 항목과 "Pearson correlation coefficient" 항목이며 2차 자료이다.

**생애.** 1857년 3월 27일 런던 이즐링턴에서 태어나 1936년 4월 27일 서리의 콜드하버에서 사망했다. 1876년 케임브리지 킹스 칼리지에 입학해 1879년 수학 우등 시험 3등(Third Wrangler)이었다. 하이델베르크와 베를린에서 공부하고 이너 템플에서 법을 공부했다. 1884년 유니버시티 칼리지 런던의 골드스미드 교수가 되었고 1911년 UCL에 통계학과를 세웠다. 1896년 왕립학회 회원, 1898년 다윈 메달을 받았다. 1920년 OBE, 1935년 기사 작위를 사양했다.

**저작.** 『Biometrika』 창간(연도는 1901년 또는 1902년이며 이 책은 확정하지 못했다), 골턴의 전기(1914~1930). 상관계수는 Bravais(1844)와 Galton(1880년대)이 먼저 다루었고 Pearson이 적률 상관으로 정의했다고 위키백과는 쓴다.

**논쟁.** 항목은 Pearson의 우생학과 사회 다윈주의 입장을 적고, UCL이 2020년 6월 두 건물의 이름을 바꾸었다고 쓴다.

**이 책이 확인하지 못한 것.** Biometrika 창간 연도의 확정. 사진은 공용 저작물 여부를 확인하지 못했다.

</div>

## 11.15 11장 주장 검증 장부

{{T:11장 주장 검증 장부. 수준: 직접 = 이 책에서 원문을 읽고 확인, 재인용 = 다른 논문이 인용(원문 미확인), 해석 = 저자의 해석, 본서계산 = 이 책의 산술, 시연값 = 절차를 보이기 위한 가정값, 2차 = 백과사전, 미결 = 근거 불충분}}

| 번호 | 주장 | 주장자 | 근거 | 수준 |
|---|---|---|---|---|
| 11-1 | 6개 유적 138명 중 형태로 남성 78명, 아멜로제닌으로 8명이 여성이어서 남성 70명 | Cui 등(2013) | 본문 | 직접(주장) |
| 11-2 | 70명 중 47명이 재현 가능한 결과를 냈다(67.1%) | Cui 등(2013), 이 책 | 계산 11-1 | 직접(주장), 본서계산 |
| 11-3 | 본문의 "23명 = 21 + 5"는 26이어서 맞지 않는다 | 이 책 | 계산 11-1 | 미결 |
| 11-4 | 표 1의 행 합이 시료 수와 맞고 서요하 4곳의 합이 32, 전체 47이다 | 이 책 | 계산 11-1 | 본서계산(표는 짝을 합계로 맞춘 재구성) |
| 11-5 | 우하량의 C와 O3a의 13.7%는 1/6 = 16.7%와 다르다 | Cui 등(2013), 이 책 | 계산 11-1 | 미결 |
| 11-6 | N1(x) 20/32 = 62.5%("약 63%"), 신석기 16/18 = 88.9%("89%") | Cui 등(2013), 이 책 | 계산 11-2 | 직접(주장), 본서계산 |
| 11-7 | "가장 오래된 집단 71%"는 N1 전체 23/32 = 71.9%와 값이 맞으나 짝이 확인되지 않는다 | 이 책 | 계산 11-2 | 미결 |
| 11-8 | 본문은 O3a가 홍산과 소하연에서 한 번씩 나왔다고 쓰나 표 1의 소하연은 12명 전원 N1(x)이다 | Cui 등(2013) | 본문, 표 1 | 미결 |
| 11-9 | 진본 검증은 음성 대조, 두 번 추출과 재현, 연구자 하플로타입과의 대조, 증폭 효율의 조각 길이 의존에 의한다 | Cui 등(2013) | 방법 | 직접(주장) |
| 11-10 | 신석기 대 청동기 [[16, 2], [4, 10]]의 Fisher 양쪽 p = 0.00079, 오즈비 20 | 이 책 | 계산 11-3 | 본서계산(논문의 검정이 아님) |
| 11-11 | 신석기 대 대전자 p = 0.194, 대산전 p = 0.00017 | 이 책 | 계산 11-3 | 본서계산 |
| 11-12 | 위키백과 예([[1, 9], [11, 3]])의 한쪽 p = 0.001379728이 재현된다 | 이 책 | 계산 11-3 | 본서계산 |
| 11-13 | 유전자 다양도 H: 우하량 0.600, 합라해구 0, 대전자 0.600, 대산전 0.861, 신석기 합 0.216 | 이 책 | 계산 11-4 | 본서계산(하플로그룹 수준) |
| 11-14 | 신석기 합의 H 구간 0~0.464과 대산전 0.556~0.889는 겹치지 않는다 | 이 책 | 계산 11-4 | 본서계산(부트스트랩) |
| 11-15 | 서요하는 5000년간 부계 계통이 이어지며 이주민 유입으로 다양성이 늘었다 | Cui 등(2013) | 결론 | 해석 |
| 11-16 | 청동기에 황하의 O3a가 들어왔다 | Cui 등(2013) | 대전자 2/5와 앞선 연구 | 해석(대전자만으로는 p = 0.194) |
| 11-17 | 문화 이행은 기후 변화에 대한 적응으로 볼 가능성이 높다 | Cui 등(2013) | 이 논문에 기후 자료 없음 | 해석 |
| 11-18 | 현생 동아시아 O-M175 58.8%(n = 176), C3 23.8%, N 8.5% | Cui 등(2013) | 본문 | 직접(주장) |
| 11-19 | 고대 서요하와 현생 서요하 P < 0.001, 고대 황하 및 현생 황하와 P < 0.01 | Cui 등(2013) | 본문 | 직접(주장). 비교한 시료 수는 미확인 |
| 11-20 | Duggan 등의 표 1: 에벤키 N 130, n 53, S 287, 서열 다양도 0.98, π 0.0020 | Duggan 등(2013) | 표 1 | 직접 |
| 11-21 | AMOVA 표의 각 줄 합이 100(±0.01)이다 | 이 책 | 계산 11-12 | 본서계산 |
| 11-22 | 지리 묶음 ΦCT 0.0401, ΦSC 0.0655, ΦST 0.1030이고 1 − ΦST = (1 − ΦCT)(1 − ΦSC)이다 | 이 책 | 계산 11-12 | 본서계산 |
| 11-23 | 에벤키 대 에벤 묶음의 묶음 사이 분산이 −0.21%이다 | Duggan 등(2013) | 표 2 | 직접(음수는 0과 구별되지 않는다고 읽음) |
| 11-24 | 4개 집단의 Mantel 검정은 최소 P = 1/24 = 0.0417이고 표의 0.04가 그 값이다 | 이 책 | 계산 11-12, 11.4.2절 | 본서계산 |
| 11-25 | 에벤 지집단 Mantel r = 0.46, P = 0.11(사키리르 제외 0.71, 0.04)의 짝 | Duggan 등(2013) | 표 3(글자가 흩어짐) | 미결(원문 쪽 확인 필요) |
| 11-26 | ρ 환산: 1 ÷ (0.0025 × 9) × 30 = 1333.3년이 논문의 1333년과 같다 | Duggan 등(2013), 이 책 | 계산 11-11 | 본서계산 |
| 11-27 | 분기 1916 ± 985, 615 ± 418, 303 ± 177은 변이 1.437, 0.461, 0.227걸음에 해당한다 | 이 책 | 계산 11-11 | 본서계산 |
| 11-28 | 같은 ρ에 진화 속도와 가계 속도를 쓰면 연대가 3.59배 다르다 | 이 책 | 계산 11-11 | 본서계산 |
| 11-29 | 젊은 분기(약 390 ± 290)가 역사·언어·고고학과 맞는다 | Duggan 등(2013) | 간접 논증 | 해석 |
| 11-30 | 사키리르 에벤 mtDNA 하플로타입의 47.4%(9/19), 세비얀 37.5%(3/8)가 야쿠트와 공유된다 | Duggan 등(2013), 이 책 | 계산 11-12b | 직접(주장), 본서계산 |
| 11-31 | 사키리르 에벤 Y의 야쿠트형 32~36%(8/25, 9/25) | Duggan 등(2013), 이 책 | 계산 11-12b | 본서계산(하플로타입 = 사람 가정) |
| 11-32 | 에벤키 C3c1 56.6%는 n = 127에서 도달하지 못한다(72/127 = 56.69%) | 이 책 | 계산 11-12c | 미결 |
| 11-33 | 에벤 C3c1 43/89 = 48.31%, 에벤 지집단 합 89 | 이 책 | 계산 11-12c | 본서계산 |
| 11-34 | 노백산 41그루 71코어, 고도 950~1050 m, 한국잣나무 | Lyu 등(2016) | 방법 | 직접 |
| 11-35 | EPS 0.85 이상은 1660년부터(std 11그루), RES는 1685년(15그루) | Lyu 등(2016) | 표 1 | 직접(주장) |
| 11-36 | RES 15그루는 r̄ = 0.28에서 EPS 0.854로 재현되고 std 11그루는 r̄ = 0.22로는 0.756이어서 재현되지 않는다 | 이 책 | 계산 11-14 | 본서계산, 미결(std) |
| 11-37 | 변환식 Y = 2.987 X + 4.829, N = 58, R = 0.757 | Lyu 등(2016) | 본문 | 직접(주장) |
| 11-38 | R² 0.573, 조정 R² 0.565, F 75.16, t 8.67이 재현된다 | 이 책 | 계산 11-5 | 본서계산 |
| 11-39 | 2.987 × 0.20 = 0.597이 논문의 복원 표준편차 0.53과 다르다 | 이 책 | 계산 11-5 | 미결 |
| 11-40 | 표 3의 R²(0.171, 0.400, 0.573)와 별표가 임계 상관(n = 29)과 맞는다 | 이 책 | 계산 11-6 | 본서계산 |
| 11-41 | 부호 검정 (20, 9)의 양쪽 p = 0.0614, 한쪽 0.0307. 표는 5% 수준 | Lyu 등(2016), 이 책 | 계산 11-6 | 미결 |
| 11-42 | 냉기·온기 기준 7.395, 7.925, 연수와 합(99년, 94년), 복원 기간 414년 | Lyu 등(2016), 이 책 | 계산 11-8 | 본서계산 |
| 11-43 | 1605~1616의 기간 평균 7.41이 냉기 기준 7.395보다 높다 | 이 책 | 계산 11-8 | 미결 |
| 11-44 | 1차 차분 r = 0.12, n = 57에서 p = 0.374 | Lyu 등(2016), 이 책 | 계산 11-9 | 직접(주장), 본서계산 |
| 11-45 | 북반구와의 r = −0.18은 독립 가정이면 p = 2.3 × 10⁻⁴, 자기상관 0.72이면 n_eff = 131.3에서 1%에 미치지 못한다 | 이 책 | 계산 11-9 | 본서계산(자기상관 값은 시연 가정) |
| 11-46 | 27/30 사건 일치. 표에는 27개 사건이 있다 | Lyu 등(2016) | 본문, 표 5 | 미결 |
| 11-47 | 노백산과 돈화 기상대의 직선거리 82.43 km, 표본과 기상대의 고도 차 425~525 m | 이 책 | 계산 11-13 | 본서계산 |
| 11-48 | 기온감률 5.0, 6.5, 8.0 °C/km에서 2.1~4.2 °C 낮다 | 이 책 | 계산 11-13 | 시연값 |
| 11-49 | 흥륭와의 C4 식단(Zhang 등, 2003)은 이 논문의 결과와 맞지 않는다 | Shelach-Lavi 등(2019) | 본문 | 재인용 |
| 11-50 | 시버는 1764년 청 황제가 신장에 이주시켰다 | Cui 등(2013) | 본문 | 재인용 |
| 11-51 | 금구자 사람들이 동호와 연결된다 | Cui 등(2013)이 Wang 등(2012)을 인용 | 참고문헌 | 재인용 |
| 11-52 | 피셔의 약력 | 영어 위키백과 | 2차 자료 | 2차 |
| 11-53 | 피어슨의 약력 | 영어 위키백과 | 2차 자료 | 2차(Biometrika 창간 연도 미결) |
| 11-54 | 서요하의 신석기·청동기 기후 자료 | — | 근거 확보 필요 | 미결 |
| 11-55 | 유적의 좌표 | — | 논문에 없음 | 미결 |

## 참고문헌

Bandelt, H.-J., Forster, P., & Röhl, A. (1999). Median-joining networks for inferring intraspecific phylogenies. *Molecular Biology and Evolution, 16*(1), 37–48. https://doi.org/10.1093/oxfordjournals.molbev.a026036

Cook, E. R. (1985). *A time series analysis approach to tree-ring standardization*. University of Arizona Press.

Cui, Y., Li, H., Ning, C., Zhang, Y., Chen, L., Zhao, X., Hagelberg, E., & Zhou, H. (2013). Y chromosome analysis of prehistoric human populations in the West Liao River Valley, Northeast China. *BMC Evolutionary Biology, 13*, Article 216. https://doi.org/10.1186/1471-2148-13-216

Duggan, A. T., Whitten, M., Wiebe, V., Crawford, M., Butthof, A., Spitsyn, V., Makarov, S., Novgorodov, I., Osakovsky, V., & Pakendorf, B. (2013). Investigating the prehistory of Tungusic peoples of Siberia and the Amur-Ussuri region with complete mtDNA genome sequences and Y-chromosomal markers. *PLoS ONE, 8*(12), Article e83570. https://doi.org/10.1371/journal.pone.0083570

Fenner, J. N. (2005). Cross-cultural estimation of the human generation interval for use in genetics-based population divergence studies. *American Journal of Physical Anthropology, 128*(2), 415–423. https://doi.org/10.1002/ajpa.20188

Forster, P., Harding, R., Torroni, A., & Bandelt, H.-J. (1996). Origin and evolution of Native American mtDNA variation: A reappraisal. *American Journal of Human Genetics, 59*, 935–945.

Holmes, R. L. (1983). Computer-assisted quality control in tree-ring dating and measurement. *Tree-Ring Bulletin, 43*, 69–78.

Li, H., Zhao, X., Zhao, Y., Li, C., Si, D., Zhou, H., & Cui, Y. (2011). Genetic characteristics and migration history of a bronze culture population in the West Liao-River valley revealed by ancient DNA. *Journal of Human Genetics, 56*(12), 815–822.

Lyu, S., Li, Z., Zhang, Y., & Wang, X. (2016). A 414-year tree-ring-based April–July minimum temperature reconstruction and its implications for the extreme climate events, northeast China. *Climate of the Past, 12*, 1879–1888. https://doi.org/10.5194/cp-12-1879-2016

Shelach-Lavi, G., Teng, M., Goldsmith, Y., Wachtel, I., Stevens, C. J., Marder, O., Wan, X., Wu, X., Tu, D., Shavit, R., Polissar, P. J., Xu, H., & Fuller, D. Q. (2019). Sedentism and plant cultivation in northeast China emerged during affluent conditions. *PLoS ONE, 14*(7), Article e0218751. https://doi.org/10.1371/journal.pone.0218751

Stokes, M. A., & Smiley, T. L. (1968). *Tree-ring dating*. University of Chicago Press.

Wang, H., Chen, L., Ge, B., Zhang, Y., Zhu, H., & Zhou, H. (2012). Genetic data suggests that the Jinggouzi people are associated with the Donghu, an ancient nomadic group of North China. *Human Biology, 84*(4), 365–378.

Wigley, T. M. L., Briffa, K. R., & Jones, P. D. (1984). On the average value of correlated time series, with applications in dendroclimatology and hydrometeorology. *Journal of Climate and Applied Meteorology, 23*, 201–213.

Wikipedia contributors. (n.d.-a). Analysis of molecular variance. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Analysis_of_molecular_variance

Wikipedia contributors. (n.d.-b). Dendroclimatology. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Dendroclimatology

Wikipedia contributors. (n.d.-c). Fisher's exact test. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Fisher%27s_exact_test

Wikipedia contributors. (n.d.-d). Karl Pearson. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Karl_Pearson

Wikipedia contributors. (n.d.-e). Pearson correlation coefficient. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

Wikipedia contributors. (n.d.-f). Ronald Fisher. In *Wikipedia*. Retrieved October 23, 2026, from https://en.wikipedia.org/wiki/Ronald_Fisher

Zhang, X., Wang, J., Xian, Z., & Qiu, S. (2003). Gu renlei shiwu jiegou yanjiu [Research on the composition of ancient human diet]. *Kaogu, 2003*(2), 62–75.
