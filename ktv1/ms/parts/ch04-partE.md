## 4.13 도구 소개

{{T:4장 분석에 쓰이거나 같은 분석에 쓸 수 있는 도구. 확인 상태는 이 책이 논문 본문에서 읽은 범위이며, 라이선스를 적지 않은 것은 확인하지 못한 것이다}}

| 도구 | 용도 | 입력 → 출력 | 확인 상태 |
|---|---|---|---|
| OxCal 4.3 | 방사성탄소 보정과 층서 순서 연대 모형(P_Sequence) | 14C 값, 층서 순서 → 달력 연대 분포 | McLean et al. (2019)이 사용. 3.10절의 OxCal 항목 참조 |
| IntCal04, IntCal13, IntCal20 | 방사성탄소 보정 곡선 | 14C 나이 → 달력 나이 | Okuno et al. (2010)은 IntCal04, McLean et al. (2019)는 IntCal13, Du et al. (2025)는 IntCal20 NH를 썼다. 곡선 자료의 입수처는 이 책이 확인하지 못했다 |
| CALIB 5.0 | 방사성탄소 보정 | 14C 나이 → cal BP | Okuno et al. (2010)이 사용. 입수처 확인 필요 |
| HYSPLIT | 대기 입자의 전방·후방 궤적 계산 | 기상장, 출발 위치·고도 → 궤적 | Lee et al. (2024)이 NOAA ARL의 READY 사이트에서 사용. 라이선스 확인 필요 |
| GDAS 1° | 기상 재분석 자료 | 기상장 | Lee et al. (2024)이 HYSPLIT 입력으로 사용 |
| ERA5 | 기상 재분석(풍속 프로파일) | 시간별 기상장 | Costa et al. (2024)이 사용. DOI 10.24381/cds.adbb2d47(논문 표기) |
| PARFIT 2.3.1 | 테프라 두께 자료에서 분출 변수를 푸는 반전 | 두께와 위치 → 질량, 기둥 높이, 확산계수 | 입수처가 논문에 있다: datasim.ov.ingv.it의 PARFIT 2.3.1 내려받기 페이지(Costa et al., 2024). 라이선스 확인 필요 |
| FALL3D 8.2 | 3차원 화산재 이송·침적 모델 | 분출 변수, 기상장 → 침적 두께 | Costa et al. (2024)이 사용. 설정 파일과 스크립트는 Zenodo(DOI 10.5281/zenodo.10159965)에 있다고 쓴다. 프로그램의 라이선스는 확인 필요 |
| ARSTAN 49, COFECHA | 나이테 표준화, 교차 연대 검사 | 나이테 폭 → 연대기, 상관 | Du et al. (2023), Zhu et al. (2009)이 사용. 라이선스 확인 필요. R 패키지 dplR 항목은 CRAN 페이지 접근이 막혀 확인하지 못했다 |
| LINTAB 6 | 나이테 폭 측정기 | 시료 → 폭 | Du et al. (2023): 정밀도 0.001 mm |
| JEOL iSP100, JEOL-8600 | 전자현미분석기(EPMA) | 유리 파편 → 주성분 | Lee et al. (2024), McLean et al. (2019) |
| LA-ICP-MS | 유리 파편의 미량원소 분석 | 파편 → 33개 미량원소 | McLean et al. (2019). 장비는 JAMSTEC |
| ENVI SARscape | InSAR 영상 처리(지속 산란체) | 레이더 영상 → 변위 시계열 | Trasatti et al. (2021). 상용 소프트웨어로 쓰인 것으로 읽히나 라이선스는 확인하지 못했다 |
| VSM | 화산·지진 원 모형 반전 | 변위 자료 → 원의 변수 분포 | Trasatti (2019)로 인용. 입수처 확인 필요 |
| QGIS, Cartopy, Matplotlib | 지도, 그림 | 좌표 → 지도 | Costa et al. (2024)이 사용(QGIS 사이트 qgis.org). 라이선스는 이 책이 확인하지 않았다 |
| Python(numpy, scipy) | 이 책의 계산 | 표, 식 → 결과 | 이 책 계산 4-1∼4-15는 ms/ch04-calc-v1.py로 재현한다. 패키지 라이선스는 확인하지 않았다 |

**이 장의 계산을 직접 해 보는 코드(발췌).** 구면 거리와 가중평균 χ²를 계산한다. 입력은 논문 값 또는 4.11절에서 밝힌 시연값이다.

```python
from math import radians, sin, cos, asin, sqrt
def hav(lat1, lon1, lat2, lon2, R=6371.0):
    p1, p2 = radians(lat1), radians(lat2)
    a = sin((p2-p1)/2)**2 + cos(p1)*cos(p2)*sin(radians(lon2-lon1)/2)**2
    return 2*R*asin(sqrt(a))
print(hav(41.99, 128.08, 35+35/60, 135+53/60))   # 981.5 km (계산 4-1)

def wmean(xs, sig):
    w = [1/s**2 for s in sig]
    m = sum(x*wi for x, wi in zip(xs, w))/sum(w)
    return m, 1/sqrt(sum(w)), sum(((x-m)/s)**2 for x, s in zip(xs, sig))
print(wmean([4910, 4965, 4945, 4940], [35]*4))   # (4940.0, 17.5, 1.27) (계산 4-6 예 1)
```

## 4.14 데이터 입수처

{{T:4장 관련 공개 데이터. 확인 상태: 원문 확인 = 논문의 데이터 가용성 문구에서 읽음. 실제 내려받기는 시험하지 않았다}}

| 데이터 | 제공처와 주소(논문 표기) | 내용 | 사용 조건 | 확인 상태 |
|---|---|---|---|---|
| NGRIP1 빙하 코어 보충 자료 | Figshare, DOI 10.6084/m9.figshare.26549344.v1 (보충 자료), 10.6084/m9.figshare.26550304.v1 (보충 표) | 입자, 황산염, 유리 파편 화학, Δ³³S | 논문 라이선스 CC BY-NC-ND 4.0 | Lee et al. (2024). 원문 확인 |
| GICC05 연층 깊이 | PANGAEA, DOI 10.1594/PANGAEA.943195 | NGRIP 연층 깊이 | 확인 필요 | Lee et al. (2024)이 연대 연결에 사용. 원문 확인 |
| NGRIP ECM H⁺ | PANGAEA, DOI 10.1594/PANGAEA.831526 | 산도 전도도 | 확인 필요 | Lee et al. (2024). 원문 확인 |
| 탄화목 나이테 연대기와 기후 | Zenodo, DOI 10.5281/zenodo.6633856 | 연대기, 기상 자료 | 확인 필요 | Du et al. (2023). 원문 확인 |
| 숲 구성·툰드라·규산체 자료와 코드 | Zenodo, DOI 10.5281/zenodo.16984691 | Du 등(2025)의 데이터와 코드 | 확인 필요 | Du et al. (2025). 원문 확인 |
| FALL3D 설정과 스크립트 | Zenodo, DOI 10.5281/zenodo.10159965 | 앙상블 설정 | 확인 필요 | Costa et al. (2024). 원문 확인. 두께 자료는 논문 보충표 1에 있다고 쓰며 이 책은 읽지 못했다 |
| 백두산 평균 지반 속도(InSAR) | reliance.rohub.org, DOI 10.24424/vfp6-r230 | 2018∼2020 평균 속도 | 원자료는 JAXA 소유라고 밝힌다 | Trasatti et al. (2021). 원문 확인 |
| ALOS-2 영상 | JAXA, 연구 협약 ER2A2N173A | SAR 영상 | 연구 협약에 따른 제공 | Trasatti et al. (2021). 원문 확인 |
| ERA5 | Copernicus 기후 데이터 저장소 | 기상 재분석 | 확인 필요 | Costa et al. (2024). DOI는 4.13절 |
| Landsat 5, 7 | USGS EarthExplorer(earthexplorer.usgs.gov) | 위성 영상 | 확인 필요 | Du et al. (2025). 원문 확인 |
| 동강 기상 자료 | China Meteorological Data Network(data.cma.gov.cn) | 월별 기온·강수 | 확인 필요 | Du et al. (2023). 원문 확인 |
| 엘니뇨 1+2 해수면 온도 | NOAA PSL(psl.noaa.gov, 시계열 NINO12) | 월별 | 확인 필요 | Du et al. (2023). 원문 확인 |
| 스이게쓰호 SG14 코어 자료 | McLean et al. (2019) 보충 자료 | 유리 화학 | 논문에 별도 가용성 문구 없음 | 입수처 확인 필요 |
| 오쿠노 등(2010) 14C 표 | 논문 표 1 | 날짜 13개 | 확인 필요 | 이 책이 가진 OCR에서 행 대응이 깨졌다. 원문 확인 필요 |
| 사료(日本紀略, 高麗史, 朝鮮王朝實錄 등) | 논문은 일본 국립국회도서관 디지털 컬렉션(日本紀略)과 규장각(조선 계열) 소장을 밝힌다 | 한문 원문 | 확인 필요 | 이 책은 직접 접근하지 못했다. 국사편찬위원회 등 제공처는 확인 필요 |

## 4.15 더 읽을 책

{{T:4장 관련 교재와 편람. 서지는 이 책이 출판사 페이지에서 확인한 항목}}

| 책 | 서지 | 이 장과의 연결 | 확인한 내용 |
|---|---|---|---|
| The Encyclopedia of Volcanoes | Sigurdsson, H., Houghton, B., McNutt, S., Rymer, H., & Stix, J. (Eds.). (2015). 제2판. Academic Press(Elsevier). ISBN 9780123859389 | 4.0, 4.3, 4.5절: 분출 과정, 테프라, 규모 | 출판사 설명: 마그마 생성과 분출 과정에서 재해, 감시, 사회·생태·경제 영향까지 다루는 참고서 |
| Methods of Dendrochronology: Applications in the Environmental Sciences | Cook, E. R., & Kairiukstis, L. A. (Eds.). (1990). Springer. 소프트커버 ISBN 978-90-481-4060-2 | 4.9, 4.11.7절, 이론 배경 7 | 출판사 설명: 나이테 분석의 최신 방법을 환경과학 응용 중심으로 정리. 그 이전의 Fritts(1976)가 절판되었다고 쓴다 |
| Volcano Deformation: New Geodetic Monitoring Techniques | Dzurisin, D. (2006). Springer(Praxis). 하드커버 ISBN 978-3-540-42642-4 | 4.8절, 이론 배경 6 | 출판사 설명: 화산 측지학을 다룬 최초의 단행본으로 소개 |
| Tree Rings and Climate | Fritts, H. C. (1976). | Zhu et al. (2009)이 교차 연대 방법으로 인용 | 이 책은 서지를 출판사 페이지에서 확인하지 못했다. 판·출판사 확인 필요 |

## 4.16 인물과 이야기로 읽는 이 장

앞 절의 방법들은 각각 누군가가 처음 생각해 낸 것이다. 아래 서술은 위키백과 영문판 해당 항목에서 이 책이 읽은 내용이며 일차 자료가 아니다. 읽지 못한 부분은 "확인하지 못했다"고 적는다. 사진은 공용 저작물 이미지의 파일 이름과 이용 조건을 확인한 뒤 넣는다.

<div class="bio" markdown="1">

![사진 자리: 앤드루 더글러스. 공용 저작물 확인 후 삽입](portrait-douglass-v1)

#### 앤드루 엘리콧 더글러스 (1867–1962): 나이테를 달력으로 만든 천문학자

**연결.** 이 장의 나이테 연대기(Du et al., 2023; Zhu et al., 2009)와 탄화목 연륜 연대의 방법(연대기를 이어 해마다 연대를 매기는 것)은 더글러스가 세운 연륜 연대학에서 출발한다.

**생애.** 1867년 7월 5일 미국 버몬트주 윈저에서 태어나 1962년 3월 20일 애리조나주 투손에서 죽었다. 직업은 천문학자이자 고고학자이다. 1894년 애리조나 플래그스태프의 로웰 천문대에서 퍼시벌 로웰의 조수로 일하며 나이테 연구를 시작했다. 나이테 폭과 태양 흑점 주기의 상관을 발견한 것이 연륜 연대학의 창시로 이어졌다고 한다. 화성의 "운하"와 금성의 바큇살 모양에 대한 실험 결과 그 존재를 의심하게 되어 로웰과 갈라섰다. 1906년 플래그스태프를 떠나 애리조나 대학의 물리학·지리학 조교수가 되었고 뒤에 물리·천문학과 과장, 임시 총장, 문리대 학장을 맡았다. 1941년 미국철학회 회원으로 선출되었고 달과 화성의 크레이터에 그의 이름이 붙었다.

**어려웠던 과정.** 큰 망원경 연구비를 대학과 준주·주 의회에서 10년쯤 얻지 못했다. 1차 세계대전이 망원경 계약을 늦추었고 거울 주조는 몇 번 실패한 뒤에야 성공했다. 1920년에는 미국자연사박물관이 그의 연구 지원을 끊었다. 1922년 내셔널지오그래픽 협회가 지원처가 될 수 있다는 것을 알았다.

**발견의 상황.** 1909년 클라크 위슬러가 허팅턴 조사를 조직하고 이어 남서부 유적의 연대 측정을 더글러스에게 문의했다. 1916년 뉴멕시코 북서부 고고 시료 분석을 시작했고, 1919년 푸에블로 보니토가 아즈텍 유적보다 40∼45년 앞선다고 결론지었다. 이어 1929년 6월 22일 애리조나 쇼 로우에서 들보 HH-39를 뽑아 두 연대기 사이의 틈을 이었고, 그해 12월 내셔널지오그래픽에 보고했다. 위키백과는 HH-39가 이집트의 로제타석에 견줄 자리를 차지할 것이라고 쓴다. 1937년 애리조나 대학에 연륜 연구소를 세웠다.

**이 책이 확인하지 못한 것.** 학력, 연륜 연대 방법의 구체적 절차(교차 연대의 수학), 흑점과 나이테 상관을 처음 발표한 연도(위키백과 항목에 연도가 없다)는 읽지 못했다. 1929년 논문(Douglass, 1929, National Geographic Magazine, 56(6), 736–770)은 읽지 못했다.

</div>

<div class="bio" markdown="1">

![사진 자리: 모기 기요오. 공용 저작물 확인 후 삽입](portrait-mogi-v1)

#### 모기 기요오 (茂木清夫, 1929–2021): 땅이 부푸는 식을 화산에 쓴 지진학자

**연결.** 4.8절의 점원 모형과 이론 배경 6의 식이 그의 1958년 논문에서 화산에 쓰였다.

**생애.** 1929년 일본 야마가타현에서 태어나 2021년 6월 6일 91∼92세로 죽었다. 도쿄대학 지진연구소 소장, 니혼대학 교수, 도쿄대학 명예교수를 지냈다. 일본 지진예지연락회 회장, 1978년부터 지진평가위원회 위원이었고 1991년부터 1996년까지 위원장을 맡았다.

**업적.** 1958년 논문 "Relations between the eruptions of various volcanoes and the deformations of the ground surfaces around them"을 도쿄대학 지진연구소 휘보 36권 99∼134쪽에 실었다. 1955년 야마카와의 해를 바탕으로 마그마방의 압력 변화가 지표 변형을 만드는 모형으로 쓸 수 있음을 보였다. 이 모형은 화산학에서 처음으로 널리 쓰인 정량적 방법이 되었고 지금도 쓰인다고 한다. 1969년에는 큰 지진이 지진 활동이 조용한 지역을 둘러싼 활발한 고리 안쪽에서 일어나는 경향이 있다는 "도넛 가설"을 제안했고, 같은 해 도카이 지역의 얕은 규모 8.0 지진 가능성을 예측했다. 저서로 『지진예지』(1985), 『실험 암석역학』(2006)이 있다.

**어려웠던 과정.** 위키백과 항목에는 개인적 어려움의 서술이 없다. 가까운 사례로 1996년 지진평가위원회 위원장직 사임이 있는데, 정부가 지진 경고의 불확실성을 설명에 반영하게 하는 데 실패한 뒤였다고 쓴다. 2007년 주에쓰오키 지진으로 가시와자키 가리와 원전이 손상된 뒤 하마오카 원전의 즉시 폐쇄를 촉구했다고도 한다.

**이 책이 확인하지 못한 것.** 학력, 1958년 논문의 본문(식과 도해), 야마카와 1955년 해의 서지는 읽지 못했다. 이 책이 읽은 교육용 페이지(gscommunitycodes.usf.edu)가 같은 식을 압력 변화 형태로 싣는다.

</div>

<div class="story" markdown="1">

#### 이야기 상자. 775년의 나이테가 946년을 고정하다

**연결.** 4.2절에서 "775 CE 우주선 급증 사건의 확인"이 밀레니엄 분출 연대 946년의 근거로 인용된다(Costa et al., 2024; Du et al., 2023이 Oppenheimer et al., 2017을 인용).

**읽은 내용.** 위키백과 영문판은 미야케 후사(Fusa Miyake)를 나고야대학의 우주선 물리학자로 소개하고 그의 연구가 "미야케 사건"의 인식으로 이어졌다고 쓴다. 미야케 사건은 역사 기록과 빙하 코어·나이테의 연대를 맞추는 데 쓰인다고 한다. 2012년 『네이처』 486권 240∼242쪽에 미야케, 나가야, 마스다, 나카무라가 "A signature of cosmic-ray increase in AD 774–775 from tree rings in Japan"을 냈다. 그는 1987년생이고 2013년 나고야대학에서 박사 학위(주제: 나이테 14C로 과거 우주선 강도 복원)를 받았다고 한다.

**왜 이 장에서 중요한가.** 우주선이 만든 14C가 한 해에 갑자기 늘어난 일이 나이테에 남기 때문에, 세계 어디의 나이테에서도 그 해를 같은 눈금으로 찾을 수 있다. 백두산 탄화목의 연륜 14C 곡선을 이 눈금에 맞추어 해마다의 연대를 얻는 방법이 4.2절의 "나이테 무늬 맞춤"이다(Costa 등이 Xu et al., 2013 인용).

**이 책이 확인하지 못한 것.** 위키백과 항목은 774∼775년 14C 급증이 어떻게 발견되었는지를 서술하지 않는다. 발견의 과정, 연구의 어려움, Oppenheimer et al. (2017)의 구체적 방법은 읽지 못했다.

</div>

<div class="story" markdown="1">

#### 이야기 상자. 일본 북부의 화산재에서 백두산을 찾다

**연결.** 4.3절 이후의 B-Tm은 이름 자체가 이 이야기에서 나왔다.

**읽은 내용.** Costa 등(2024)은 Machida와 Arai(1983)가 일본 북부에서 B-Tm 화산재를 발견하고, 칼륨장석의 존재와 두께가 줄어드는 방향으로 백두산을 근원으로 지목했다고 쓴다. 이어 Xu 등(2013)이 나이테 파형 맞춤으로 946 ± 3 CE를, Oppenheimer 등(2017)이 775 CE 우주선 사건의 확인으로 946 CE를 확정했고, Sun 등(2014)이 그린란드 빙하 코어에서 유리 파편을 보고했다고 소개한다. McLean 등(2019)은 오래전부터 동해 해양 코어에서 알칼리성 화산재가 확인되었고(Arai et al., 1981 이래) 초기에는 pre-AT 울릉도 층을 단일 분출로 보았으나 나이가 논쟁적이었으며, Chun et al.(2007)이 두 층(SKPI, SKPII)으로 정리했다고 쓴다.

**이 책이 확인하지 못한 것.** 위 인용 논문들의 원문. 발견자들의 삶은 확인하지 못했다.

</div>

## 4.17 주장 검증 장부

{{T:4장 주장 검증 장부. 수준: 직접 = 이 책이 읽은 논문의 자체 서술, 재인용 = 그 논문이 다른 연구를 인용한 것(원문 미확인), 해석 = 저자의 해석, 본서계산 = 이 책의 산술, 시연값 = 절차를 보이기 위한 가정값, 2차 = 백과사전·해설, 본서 조사 = 이 책이 공식 페이지를 읽음, 미결 = 확인되지 않음}}

| 번호 | 주장 | 주장자 | 근거 | 수준 |
|---|---|---|---|---|
| 4-1 | 밀레니엄 분출 연대 946 ± 3 CE | Xu et al. (2013) | 나이테 14C 파형 맞춤(Costa et al., 2024가 인용) | 재인용 |
| 4-2 | 775 CE 우주선 사건 확인으로 946 CE | Oppenheimer et al. (2017) | 나이테 14C 급증 | 재인용 |
| 4-3 | 빙하 코어 연대 939∼940 CE | Costa et al. (2024) 인용 | GICC05 연층 | 재인용 |
| 4-4 | 늦은 946 CE, 218.527 ± 0.005 m(분출일은 11월 1일로 가정) | Lee et al. (2024) | NGRIP1 입자·황산염 | 직접 |
| 4-5 | 946-11-03 나라에서 흰 재가 내림 | 興福寺年代記(Yun et al., 2023) | 사료 | 재인용 |
| 4-6 | 947-02-07 공중에서 천둥 같은 소리 | 貞信公記, 日本紀略(Yun et al., 2023) | 사료 | 재인용 |
| 4-7 | 탄화목 14C: 지점 A 770∼970 CE, B 890∼1020 CE(2σ) | Du et al. (2023) | 표 1 AMS | 직접 |
| 4-8 | 두 단계 간격 31 ± 25일(2σ) | Lee et al. (2024) | 빙하 코어 깊이 환산 | 직접 |
| 4-9 | 간격이 1주 이내 2.5%, 4주 이내 42.7%, 8주 이내 97.9% | Lee et al. (2024) | 몬테카를로 | 직접 |
| 4-10 | 정규 가정으로 같은 확률을 재현: 0.027, 0.405, 0.977 | 본서 | 계산 4-4 | 본서계산 |
| 4-11 | 두 시점 오차의 암묵 상관 약 0.36 | 본서 | 계산 4-4 | 본서계산 |
| 4-12 | 두 낙하 단계 각 약 15시간, 약 20시간, 기둥 30∼40 km, 부피 7.2와 9.3 km³ DRE | Costa et al. (2024) | PARFIT과 FALL3D 반전 | 직접 |
| 4-13 | 동쪽 약 15 km의 라하르 층이 두 단계 사이에서 관찰됨(몇 달의 쉼) | Costa et al. (2024), Lee et al. (2024) 인용 | 근역 퇴적물 | 재인용 |
| 4-14 | NS-4와 NS-5 사이에 퇴적 단절이 없다 | Sun et al. (2017) | McLean et al. (2019) 인용 | 재인용 |
| 4-15 | NS-5는 분출 이후의 사건이며 1668 또는 1702년 기록과 연결 가능 | Cui et al. (1995), Liu et al. (1998) | McLean et al. (2019) 인용 | 재인용 |
| 4-16 | 947년 2월 소리는 2상과 무관 | Lee et al. (2024) | 14주 지연, 낙진 체류 | 해석 |
| 4-17 | 947년 초에 다른 단계나 활동이 있었을 수 있다 | Costa et al. (2024) | 사료 | 해석 |
| 4-18 | 분출 규모 VEI 7 | McLean et al. (2019), Du et al. (2023) | 서술 | 직접(서술) |
| 4-19 | VEI 6 또는 7 | Lee et al. (2024) | 서술 | 직접(서술) |
| 4-20 | VEI 6, not 7 | Yang et al. (2021) | 참고문헌 제목 | 재인용 |
| 4-21 | 총 DRE 약 23 km³(13∼47), 규모 M6.5∼7.0 | Costa et al. (2024) | 반전 | 직접 |
| 4-22 | 테프라 약 100 km³, DRE 약 25 km³ | McLean et al. (2019) | 서술 | 직접(서술) |
| 4-23 | 테프라 96 ± 19 km³, 마그마 DRE 7∼36 km³ | Du et al. (2025) | 서술 | 직접(서술) |
| 4-24 | 황 방출 2∼11 Tg, 최대 45 Tg, 2∼7 Tg | Lee et al. (2024) | 문헌 값 소개 | 재인용 |
| 4-25 | 황 45 Tg | McLean et al. (2019) | Iacovino et al. (2016) 인용 | 재인용 |
| 4-26 | 분출 중 황 0.5∼2.6 Tg S, 빙하 코어 환산 약 2 Tg S | Costa et al. (2024) | 휘발분과 코어 | 직접 |
| 4-27 | 성층권 황 1.7 ± 0.6 Tg | Toohey & Sigl | Lee et al. (2024) 인용 | 재인용 |
| 4-28 | U-4 약 11, U-3 8.3 또는 9, U-2 5.6 cal ka BP | Okuno et al. (2010) | 토양·목탄 AMS 14C | 직접 |
| 4-29 | U-Oki/U-4 10,230∼10,171, U-3 8,455∼8,367, U-2 5,681∼5,619, U-1 2,737∼2,620 | McLean et al. (2019) | 스이게쓰호 연대 모형 | 직접 |
| 4-30 | U-3의 두 날짜는 10.2σ 일치하지 않음 | 본서 | 계산 4-6 | 본서계산 |
| 4-31 | U-2 네 날짜 가중평균 4940 ± 17.5, χ² 1.27 | 본서 | 계산 4-6 | 본서계산 |
| 4-32 | U-4 다섯 날짜 χ² 32.5, 하나를 빼면 5.7 | 본서 | 계산 4-6 | 본서계산 |
| 4-33 | 오쿠노 등과 McLean 등의 U-4 차이 약 800∼951년 | 본서 | 계산 4-6 예 7 | 본서계산 |
| 4-34 | 새 백두산 층 B-Sg-42(42,750∼42,323), B-Sg-08(8,166∼8,099) | McLean et al. (2019) | 크립토테프라와 연대 모형 | 직접 |
| 4-35 | 86 ka 이후 백두산 광역 분출 최소 8회 | McLean et al. (2019) | 스이게쓰호 | 직접 |
| 4-36 | 위안츠 호 테프라와 SG14-1058의 연결 | Sun et al. (2018) | McLean et al. (2019) 인용 | 재인용 |
| 4-37 | McLean 등 내부 표기 불일치(B-Sado 67.6 대 70 ka, B-V 25 대 29 ka, 백두산 좌표 41°00′ 대 41.99°) | 본서 | 원문 대조 | 본서 조사 |
| 4-38 | 946년 뒤 90건 넘는 분출 | Yun et al. (2023) | 사료 9종 | 직접(저자 주장) |
| 4-39 | 946년 뒤 어느 분출에도 직접 물리 증거가 없다 | Pan et al. (2020) | Yun et al. (2023) 인용 | 재인용 |
| 4-40 | 1702년 VEI 5, 최소 1.2 km³ | Yun & Lee (2011) | 140 km 지점 등후선과 경험식 | 재인용 |
| 4-41 | 고려사 우토 56회 연도 목록이 1724년까지, 연도 수 43 | 본서 | Yun et al. (2023) 대조 | 본서 조사 |
| 4-42 | 986년 ÷ 22건 = 44.8년, ÷ 90건 = 11.0년 | 본서 | 계산 4-8 | 본서계산 |
| 4-43 | 사료의 한문 구절(4.6절 표) | Yun et al. (2023) 인쇄본 | OCR 판독, 판본은 논문 밝힘 | 재인용 |
| 4-44 | 백두산 → 스이게쓰호 981 km, 울릉도 → 스이게쓰호 496 km, 백두산 → 울릉도 553 km | 본서 | 계산 4-1 | 본서계산 |
| 4-45 | 백두산 → 개성 465.6 km, 방위 197° | 본서 | 계산 4-1(개성 좌표는 시연값) | 시연값 |
| 4-46 | 분출일이 약 11월 1∼3일(재가 나라에 도착한 날 11월 3일, 풍속 5∼20 m/s) | 본서 | 4.7절 계산 2 | 시연값 |
| 4-47 | 율리우스력과 그레고리력의 5일 차 | 본서 | 계산 4-8 | 본서계산 |
| 4-48 | 소리 도달 지연 개성 22.8분, 981 km 지점 48.1분 | 본서 | 4.7절 계산 3, 음속 340 m/s 가정 | 시연값 |
| 4-49 | 세 원(구상체 7.7 km, 판형 저장고 14 km, 정단층 creep) | Trasatti et al. (2021) | InSAR 19장 반전 | 직접 |
| 4-50 | 2002∼2006 융기원 깊이 4.4∼9.2 km | 여러 연구 | Trasatti et al. (2021) 정리 | 재인용 |
| 4-51 | 수축량이 팽창량의 약 1.92배 | 본서 | 계산 4-11 | 본서계산 |
| 4-52 | 상향 힘 13∼27 MPa는 h = 6.3 km에서 재현되지 않음 | 본서 | 계산 4-11 (5) | 미결 |
| 4-53 | 체적탄성률 K = 51 GPa의 식을 복원하지 못함 | 본서 | 계산 4-11 (6) | 미결 |
| 4-54 | 점원 모형의 17.3 cm 시연이 논문 6.5 cm와 어떻게 맞는지 | 본서 | 계산 4-12 | 미결 |
| 4-55 | 회귀 y = 4.34·CHRON + 1.33, r = 0.45 | Du et al. (2023) | 4월 기온과 연대기 | 직접 |
| 4-56 | 변동 표준편차 0.61 °C(847∼946) 대 0.69 °C(1913∼2012), +13% | Du et al. (2023) | 나이테 복원 | 직접 |
| 4-57 | 탄화목 연대기 SD 0.288 × 4.34 = 1.25 °C와 복원 SD 0.61 °C의 어긋남 | 본서 | 계산 4-13 (7) | 미결 |
| 4-58 | 근대의 변동 증가는 인간 활동 때문일 가능성 | Du et al. (2023) | 복원 비교 | 해석 |
| 4-59 | 2∼4월 기온 모형 Tem = −10.9 + 2.35·CBₜ + 4.12·CBₜ₊₁, RE 0.376 | Zhu et al. (2009) | 4개 지점 연대기 | 직접 |
| 4-60 | 설명 분산이 초록 45.7%, 표 0.457, 본문 46.2%로 불일치 | 본서 | 계산 4-14 | 본서 조사 |
| 4-61 | 동아시아 겨울 몬순 지수와 r = −0.342(1874∼2000), −0.503(1951∼2000) | Zhu et al. (2009) | 상관 | 직접 |
| 4-62 | 분출 전 저고도 숲은 침엽수 약 87%, 현재 약 54% | Du et al. (2025) | 탄화목 91그루와 방형구 | 직접 |
| 4-63 | 숲 구성 차이는 분출 이후의 회복 과정의 결과 | Du et al. (2025) | 위 자료와 이탄 | 해석 |
| 4-64 | Du 등(2025) 내부 불일치(툰드라 고도, 채취 연도, 종 비율, 이탄 연대 선형성) | 본서 | 계산 4-15 | 본서 조사 |
| 4-65 | ME는 북반구 기후에 약한 영향 | Xu et al. (2013) | Du et al. (2025) 인용 | 재인용 |
| 4-66 | 규모 M6.48∼7.03(13∼47 km³ DRE) | 본서 | 계산 4-10 | 본서계산 |
| 4-67 | 기둥 높이 36.6 km(Mastin), 38.0 km(Sparks) | 본서 | 계산 4-10, 외부 식(원문 미확인) | 본서계산 |
| 4-68 | 더글러스의 생애와 HH-39 | 위키백과 영문판 | 2차 자료 | 2차 |
| 4-69 | 모기의 생애와 1958년 논문 | 위키백과 영문판 | 2차 자료 | 2차 |
| 4-70 | 미야케 2012년 논문과 774∼775년 14C 급증 | 위키백과 영문판 | 2차 자료 | 2차 |
| 4-71 | 4.13∼4.15절의 도구, 데이터, 책 | 논문 본문과 출판사 페이지 | 이 책이 직접 읽음 | 본서 조사 |

## 참고문헌

Costa, A., Mingari, L., Smith, V. C., Macedonio, G., McLean, D., Folch, A., Lee, J., & Yun, S.-H. (2024). Eruption plumes extended more than 30 km in altitude in both phases of the Millennium eruption of Paektu (Changbaishan) volcano. *Communications Earth & Environment, 5*, Article 6. https://doi.org/10.1038/s43247-023-01162-0

Douglass, A. E. (1929). The secret of the Southwest solved by talkative tree rings. *National Geographic Magazine, 56*(6), 736–770. (위키백과 영문판의 서지에서 인용. 원문은 읽지 못했다.)

Du, H., Oppenheimer, C., Büntgen, U., Camarero, J. J., Stambaugh, M. C., Li, M.-H., Gao, G., Jie, D., Yin, H., Wu, M. M., Zong, S., He, H. S., & Wu, Z. (2025). Impacts of the Millennium Eruption and climate change on vegetation species composition of Changbaishan. *Communications Earth & Environment, 6*, Article 817. https://doi.org/10.1038/s43247-025-02787-z

Du, H., Stambaugh, M. C., Camarero, J. J., Li, M.-H., Yu, D., Zong, S., He, H. S., & Wu, Z. (2023). A comparison of pre-millennium eruption (946 CE) and modern temperatures from tree rings in Changbai Mountain, Northeast Asia. *Climate of the Past, 19*, 1295–1304. https://doi.org/10.5194/cp-19-1295-2023

Lee, G., Burke, A., Hutchison, W. R., Sugden, P. J., Smith, C., McConnell, J. R., Sigl, M., Oppenheimer, C., Rasmussen, S. O., Steffensen, J. P., Lee, S. R., & Ahn, J. (2024). Phasing and climate forcing potential of the Millennium Eruption of Mt. Baekdu. *Communications Earth & Environment, 5*, Article 549. https://doi.org/10.1038/s43247-024-01713-z

McLean, D., Albert, P. G., Suzuki, T., Nakagawa, T., Kimura, J.-I., Chang, Q., MacLeod, A., Blockley, S. P. E., Staff, R. A., Yamada, K., Kitaba, I., Haraguchi, T., Kitagawa, J., SG14 Project Members, & Smith, V. C. (2019). Refining the eruptive history of Ulleungdo and Changbaishan volcanoes (East Asia) over the last 86 kyrs using distal sedimentary records. *Journal of Volcanology and Geothermal Research*, Article 106669. https://doi.org/10.1016/j.jvolgeores.2019.106669 (이 책이 가진 저자 수정본의 첫 쪽에는 2020년, 389권이라 표기되어 있다. 출판본의 권·연도 확인 필요.)

Miyake, F., Nagaya, K., Masuda, K., & Nakamura, T. (2012). A signature of cosmic-ray increase in AD 774–775 from tree rings in Japan. *Nature, 486*(7402), 240–242. (위키백과 영문판의 서지에서 인용. 원문은 읽지 못했다.)

Mogi, K. (1958). Relations between the eruptions of various volcanoes and the deformations of the ground surfaces around them. *Bulletin of the Earthquake Research Institute, University of Tokyo, 36*, 99–134. (위키백과 영문판의 서지에서 인용. 원문은 읽지 못했다.)

Okuno, M., Shiihara, M., Torii, M., Nakamura, T., Kim, K. H., Domitsu, H., Moriwaki, H., & Oda, M. (2010). AMS radiocarbon dating of Holocene tephra layers on Ulleung Island, South Korea. *Radiocarbon, 52*(2–3), 1465–1470. https://doi.org/10.1017/S0033822200046555

Trasatti, E., Tolomei, C., Wei, L., & Ventura, G. (2021). Upward magma migration within the multi-level plumbing system of the Changbaishan volcano (China/North Korea) revealed by the modeling of 2018–2020 SAR data. *Frontiers in Earth Science, 9*, Article 741287. https://doi.org/10.3389/feart.2021.741287

Yun, S.-H., Lee, J., Chang, C., & Oppenheimer, C. (2023). A re-assessment of historical records pertaining to the activity of Mt. Baekdu (Paektu, Tianchi) volcano. *Geoscience Letters, 10*, Article 30. https://doi.org/10.1186/s40562-023-00286-7

Zhu, H. F., Fang, X. Q., Shao, X. M., & Yin, Z. Y. (2009). Tree ring-based February–April temperature reconstruction for Changbai Mountain in Northeast China and its implication for East Asian winter monsoon. *Climate of the Past, 5*, 661–666. https://doi.org/10.5194/cp-5-661-2009

Cook, E. R., & Kairiukstis, L. A. (Eds.). (1990). *Methods of dendrochronology: Applications in the environmental sciences*. Springer.

Dzurisin, D. (2006). *Volcano deformation: New geodetic monitoring techniques*. Springer.

Sigurdsson, H., Houghton, B., McNutt, S., Rymer, H., & Stix, J. (Eds.). (2015). *The encyclopedia of volcanoes* (2nd ed.). Academic Press.

(본문에서 "인용" 또는 "재인용"으로 표시한 연구는 이 책이 원문을 읽지 못해 위 목록에 올리지 않았다. 각 인용의 서지는 해당 논문의 참고문헌에서 확인해야 한다.)

