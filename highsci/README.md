# highsci — 통합과학1·2 문제은행 (2022 개정)

holymind가 코디네이터가 되어 **z840·z440·soul3 GPU 서버(Ollama gemma)에 작업을 나눠** 통합과학1·2의 **물리·화학·생물·지구과학 중단원별 1,000문항**을 생성해
`~/Downloads/highsci_db/`에 저장합니다. 나중에 웹에서 **문항반응이론(IRT)**과 **개념 그래프**로 문제를 풀게 할 수 있도록 설계했습니다.

## 규모

| 과목 | 중단원 | 문항 |
|---|---|---|
| 물리 | 1-1, 1-2, 2-5, 3-3, 5-3, 5-4, 5-5 | 7,000 |
| 화학 | 2-2, 2-3, 4-3, 4-4, 4-5 | 5,000 |
| 생물 | 2-4b, 3-4, 3-5, 3-6, 4-2, 5-1 | 6,000 |
| 지구과학 | 2-1, 2-4a, 3-1, 3-2, 4-1, 5-2 | 6,000 |
| **합계** | **24개 중단원** | **24,000** |

`6-1 과학 기술과 미래 사회`(융합)는 기본적으로 제외합니다. 넣으려면 `--subjects 물리 화학 생물 지구과학 융합` 옵션을 쓰세요.
단원 체계, 성취기준, 개념, 선수 관계는 `curriculum.json`에서 수정합니다.

## 분산 구조

```
            holymind (코디네이터 + GPU 16GB)                     GPU 서버 (Ollama)
  ┌───────────────────────────────────────┐   생성·검증 요청   ┌──────────────────────┐
  │ generate.py  작업 풀(Scheduler)        │ ─────────────────▶ │ holymind 16GB 슬롯 3  │
  │  └ ~/Downloads/highsci_db/highsci.db   │ ─────────────────▶ │ z840     12GB 슬롯 2  │
  │    (DB는 여기 한 곳에만 저장)            │ ─────────────────▶ │ z440     12GB 슬롯 2  │
  │                                       │ ─────────────────▶ │ soul3    12GB 슬롯 2  │
  └───────────────────────────────────────┘                    └──────────────────────┘
        ▲ 프롬프트: ssh soul3 → prompt_db
```

**GPU 서버 네 대가 모두 생성에 참여합니다** (holymind 16GB, z840·z440·soul3 각 12GB). 12GB 서버는 동시 요청 2개, holymind는 3개로 잡았습니다. 실행 중 `nvidia-smi`로 메모리 여유를 보고 `nodes.json`에서 조정하세요. z440은 공개 웹 서버이므로 사이트가 느려지면 1로 낮추세요. 일부 서버만 쓰려면 `./run_holymind.sh --only-nodes holymind z840`를 씁니다.

- **5문항 단위 배치**로 작업을 나눠 줍니다. 요청을 먼저 끝낸 서버가 다음 배치를 가져가므로 GPU가 빠른 서버가 더 많이 만듭니다.
- 진행 중인 배치를 예약분으로 계산하므로 여러 서버가 동시에 일해도 목표 문항 수와 난이도 비율을 넘지 않습니다.
- 한 서버가 연속으로 실패하면 잠시 쉬게 하고, 그 서버의 배치는 다른 서버가 이어받습니다. 50회 연속 실패하면 그 실행에서 제외합니다.
- DB 쓰기는 코디네이터에서만 합니다. 서버별 결과를 합칠 필요가 없습니다. 문항마다 `node` 컬럼에 어느 서버가 만들었는지 기록합니다.
- 서버 목록, 동시 요청 수(slots), 제한 시간(timeout), 서버별 모델은 `nodes.json`에서 바꿉니다.

## 실행 순서

```bash
# 1) soul3: 프롬프트 등록 (최초 1회, 수정 후 다시 실행해도 됨)
mysql -u prompt_user -p'prompt2026!' --socket=/home/mysql/mysql.sock prompt_db < highsci/sql/register_prompts.sql

# 2) holymind: 코드 받기
git clone -b claude/common-science-problem-bank-fkflws https://github.com/LeeKJ717/a.git ~/highsci_src
cd ~/highsci_src/highsci

# 3) holymind → 각 서버 ssh 키 접속 확인
for h in 192.168.0.84 192.168.0.6 192.168.0.20; do ssh -o BatchMode=yes $h true && echo "$h OK"; done

# 4) 시작 — 이것 하나면 됩니다. 준비 안 된 서버(holymind·z840·z440·soul3)는 자동으로 설정한 뒤
#    4대에 작업을 나눠 백그라운드로 생성합니다 (처음 1회는 서버마다 sudo 비밀번호를 물을 수 있음)
./run_holymind.sh
./run_holymind.sh check                 # 서버 점검만
./run_holymind.sh status                # 중단원별 진행 + 서버별 배치·채택·거부·속도
./run_holymind.sh log
./run_holymind.sh stop
```

자동 설정은 `deploy_nodes.sh`가 `setup_node.sh`를 각 서버에 ssh로 보내 실행하는 방식입니다. holymind 자신은 바로 실행합니다. 수동으로 하려면 `./deploy_nodes.sh [서버명…]`를 쓰고, 자동 설정을 끄려면 `HIGHSCI_AUTO_SETUP=0 ./run_holymind.sh`를 씁니다. `setup_node.sh`가 각 서버에서 하는 일은 다음과 같습니다.
- Ollama를 `0.0.0.0:11434`로 열고, `OLLAMA_NUM_PARALLEL`을 slots 값으로 맞춥니다. 모델은 24시간 메모리에 상주시킵니다.
- 11434 포트는 **코디네이터(holymind)에서만 접속을 허용**하도록 ufw, firewalld, iptables 중 사용 중인 방화벽에 규칙을 추가합니다.
- Ollama가 없는 서버가 있으면 `INSTALL=1 ./run_holymind.sh`로 실행하세요. 설치까지 자동으로 합니다.

단일 서버로만 돌리려면 `./run_holymind.sh --ollama http://localhost:11434 --workers 2`를 쓰세요.

### 예시 문항(few-shot)

`seeds/<중단원코드>.jsonl` 파일이 있으면 생성 요청마다 같은 난이도의 예시 2개를 넣어 줍니다. 한 줄에 `stem`, `choices`, `answer`, `explanation`, `difficulty`를 담습니다. gemma는 예시의 형식과 수준을 따르되 그대로 베끼지는 않도록 지시받습니다.

## 생성 방식

- **1회 호출에 5문항**을 생성합니다. 이때 성취기준, 대상 개념(적게 출제된 개념부터), 난이도, 인지 수준, 문항 유형(개념·자료 해석·계산·ㄱㄴㄷ 합답형·실생활·탐구)을 지정하고, 최근 출제한 문제 본문도 함께 보내 중복을 피하게 합니다.
- **난이도 목표 비율**은 1:2:3:4:5 = 10:25:30:25:10%입니다. 중단원당 100/250/300/250/100문항입니다.
- **품질 관리**: 형식 검사(5지선다, 정답 1~5, 보기 중복 금지)와 본문 해시 중복 제거를 거칩니다. 그다음 `highsci_item_verify`로 **모델이 문항을 따로 풀어 정답이 일치하고 오류가 없는 문항만** 저장합니다. `--no-verify`로 끄면 속도는 약 2배가 되지만 품질이 떨어집니다.
- 소요 시간은 `./run_holymind.sh status`의 서버별 초/배치로 계산하세요. 예를 들어 배치 하나에 40초가 걸리고 GPU 슬롯이 모두 9개(holymind 3, z840 2, z440 2, soul3 2)면 24,000문항에 약 6시간이 걸립니다. 한 GPU에서 동시 요청을 늘리면 요청 하나의 속도는 조금 떨어지므로 실제로는 이보다 길어질 수 있습니다.

## 저장 구조 (`~/Downloads/highsci_db/`)

```
highsci.db                 SQLite — 웹에서 바로 사용
exports/
  통합과학1_3-3_물리.jsonl  중단원별 문항 (JSON Lines)
  concept_graph.json       개념 그래프 (노드: 개념, 간선: 선수 관계)
  manifest.json
logs/generate.log
```

`highsci.db` 주요 테이블 (`sql/schema.sql`):

| 테이블 | 용도 |
|---|---|
| `items` | 문항. IRT 3PL 사전값 `irt_a=1.0`, `irt_b`(난이도 1~5 → -2~+2), `irt_c=0.2` |
| `concepts`, `concept_edges` | 그래프 노드와 간선. `intra`는 중단원 안의 개념 순서, `inter`는 중단원 사이의 선수 관계 |
| `item_concepts` | 문항 ↔ 개념 (Q-matrix) |
| `responses` | 웹 단계의 학생 응답 로그 → IRT 보정(`irt_calibrated`, `irt_n`) |
| `user_concept_mastery` | 학생별 개념 능력치 θ → 그래프 기반 다음 문항·선수 개념 추천 |

## 국내·해외 참고 자료 수집 (`refs/`)

한국 수능·모의평가·학력평가와 일본·미국·인도·프랑스·영국의 입시 기출과 교과 자료를 **참고용으로** holymind에 내려받아 DB에 저장합니다. 문항 유형 분석, 책 목차 설계, 생성 프롬프트 개선에 씁니다.

```bash
sudo apt install poppler-utils      # PDF 본문 추출용 (최초 1회)
./refs/run_refs.sh                  # 백그라운드 수집 (이어하기 가능, 사이트당 1.5초 간격, robots.txt 준수)
./refs/run_refs.sh status           # 출처별 대기·완료·중복·오류·용량·본문 추출 수
./refs/run_refs.sh search 運動量     # 모든 자료 본문 검색 (한·일·영·불)
./refs/run_refs.sh --discover       # 내려받지 않고 링크만 찾아 목록 확인
```

| 나라 | 출처 (`refs/sources.json`) |
|---|---|
| 한국 | 평가원 수능 기출 게시판 / 6·9월 모의평가 / **2028 수능 통합과학 예시문항** / EBSi 전국연합학력평가 고1~3 / 서울시교육청·서울진로진학정보센터 학력평가 자료 |
| 일본 | 대학입시센터 공통테스트 이과 (최근 3년) |
| 미국 | AP 물리1·2, 화학, 생물, 환경과학 서술형 기출과 채점기준 / OpenStax 교과서 (CC BY) / NAEP 과학 / NGSS 과제 |
| 인도 | NCERT 교과서 9~12학년 / NCERT Exemplar / NTA JEE Main·NEET 기출 |
| 프랑스 | 에듀스콜 Physique-chimie / 전국 문제은행(BNS)의 Enseignement scientifique·SVT |
| 영국 | AQA GCSE Combined·A-level / OCR Gateway / Pearson Edexcel / Cambridge IGCSE |
| 네덜란드 | Examenblad 중앙시험 VWO·HAVO 물리·화학·생물·지리 (2016~2026, 채점기준 포함) |
| 스웨덴 | Skolverket 9학년 국가시험 (생물·물리·화학) / 고등학교 평가 지원 자료 (naturkunskap 포함) / 예테보리대학 예시 과제 |
| 독일 | IQB 주 공동 아비투어 문제 풀 (2025/26부터 생물·화학·물리) / IQB 중등 교육표준 자연과학 예시 과제 / 베를린·브란덴부르크 아비투어 (최근 베를린 과제는 CC BY) / 브레멘 / 바이에른 ISB |
| 대만 | 대학입시센터 학측 자연과 기출·정답과 신교육과정 예시 시험지 |
| 국제 | OECD PISA 과학 공개 문항 / IEA TIMSS·TIMSS Advanced 공개 문항 |
| 캐나다·호주·뉴질랜드 | 앨버타 졸업시험 공개 문항 (Science 30 등) / NSW HSC / VCE / NCEA |
| 싱가포르 | SEAB 교육과정 문서·예시 시험지 (역대 기출은 판매용이라 제외) |

- **저장 위치**: 원본은 `highsci_db/references/<나라>/<출처>/`에 둡니다. 목록, 쪽별 본문, 전문 검색 색인은 `highsci.db`에 넣습니다. 테이블은 `ref_sources`, `ref_docs`, `ref_pages`, `ref_fts`입니다.
- **파일 처리**: 같은 내용의 파일은 하나만 보관합니다. ZIP(NCERT 교과서)은 안의 PDF까지 풉니다. 로그인 페이지나 차단 페이지는 걸러냅니다.
- **문서와 중단원 연결**: `ref_doc_subunits`에 참고 문서의 쪽과 우리 중단원(3-3 등)을 연결해 기록합니다.
- **한국 자료 범위**: 과학탐구, 통합과학(옛 공통과학 포함), 정답·해설만 받습니다. 다른 과목은 파일명을 보고 걸러냅니다. 전 과목이 필요하면 해당 출처의 `include`와 `exclude`를 빈 문자열로 바꾸세요. 2028학년도 수능부터 탐구 영역이 통합과학으로 바뀌므로 예시문항은 문제은행과 책의 1순위 기준 자료입니다.
- **시작 URL 템플릿**: 네덜란드처럼 `연도/레벨/과목` 규칙이 있는 사이트는 `seed_templates`로 시작 URL을 한꺼번에 만듭니다. 예를 들어 `"year": "2016-2026"`처럼 범위로 적을 수 있습니다.
- **게시판 처리**: 여러 쪽으로 나뉜 목록은 끝까지 따라갑니다(`paginate`). `fileDown.do`처럼 확장자가 없는 링크(`doc_url`)와 자바스크립트 다운로드(`js_links`)도 받습니다. 한글 파일명은 UTF-8, CP949, RFC 5987 방식을 모두 해석합니다.
- **robots.txt**: 공공기관 사이트 중에는 robots.txt로 자동 수집을 전부 막아 둔 곳이 있습니다. `status`에서 건너뜀이 많은 출처는 공개 파일을 개인 참고용으로 받는 경우에 한해 `./refs/run_refs.sh --sources <출처id> --ignore-robots`로 받을 수 있습니다. 요청 간격 1.5초는 그대로 유지됩니다.
- **사이트 구조가 바뀌어 못 찾을 때**: 그 출처의 `seeds`, `include`, `follow`만 고치면 됩니다. 로그인이 필요하거나 자바스크립트로만 그려지는 사이트(NAEP 문항 도구 등)는 일부만 수집될 수 있습니다.
- **저작권**: 수집한 자료는 개인 참고용입니다. 저장소 커밋, 웹 공개, 책 전재는 하지 않습니다. `.gitignore`가 PDF, ZIP, DB 파일을 막습니다. 책이나 문제에 그대로 쓸 수 있는 것은 OpenStax(CC BY 4.0, 출처 표기)뿐입니다.

### 서울 중·고등학교 학교별 기출 (`--schools`)

나이스 교육정보 개방 포털 API로 서울(B10) 중학교와 고등학교 목록, 홈페이지 주소를 받습니다. 그다음 학교마다 홈페이지에서 정기고사 기출 게시판을 찾아 과학 기출을 내려받습니다.

```bash
export NEIS_API_KEY=발급받은키          # https://open.neis.go.kr 무료 인증키
./refs/run_refs.sh --schools --school-name 경기고 서울과학고 --discover   # 몇 곳만 먼저 시험
./refs/run_refs.sh --schools                                             # 서울 전체 (백그라운드)
./refs/run_refs.sh status                                                # 학교별 기출 합계 한 줄
python3 refs/fetch_refs.py --status --schools-detail                     # 학교별 현황 (자료 많은 순)
pip install pyhwp                                                        # HWP 본문 추출 (HWPX는 도구 없이 됨)
```

- **게시판 찾기**: 학교 홈페이지는 주소 규칙이 제각각입니다. 그래서 "기출, 정기고사, 지필, 중간고사, 기말고사, 평가 자료, 자료실" 같은 **메뉴 글자**로 게시판을 찾아가고, 같은 게시판의 다음 쪽까지 따라갑니다.
- **받는 범위**: 과학(통합과학, 물리, 화학, 생명과학, 지구과학)과 정답만 받습니다. 한글 파일(HWP, HWPX)과 PDF를 받습니다.
- **공개되지 않은 학교**: 교육부 지침상 기출 공개 방법은 학교가 정합니다. 홈페이지 게시, 교내 비치, 출력물 제공 중 하나를 고를 수 있습니다. 그래서 **홈페이지에 공개하지 않거나 로그인이 필요한 학교는 받을 수 없고, 받지도 않습니다.**
- **못 찾는 학교 점검**: 기출 관련 페이지 HTML을 `logs/snapshots/kr_school_<코드>/`에 학교당 5개까지 저장합니다. 이것을 보고 `refs/sources.json`의 `kr_seoul_school_template` 규칙을 고칩니다.
- **나이스 키가 없을 때**: `--school-csv 파일`로 학교 목록을 줄 수 있습니다. 필요한 열은 학교명, 학교종류명, 표준학교코드, 홈페이지주소입니다.

## 테스트 (GPU 없이)

```bash
python3 highsci/tests/test_pipeline.py   # 가짜 Ollama 서버 4대로 분산·장애 전환·중복 제거·이어하기·내보내기 확인
python3 highsci/tests/test_refs.py       # 가짜 사이트로 수집·robots·ZIP·중복·차단 페이지·본문 검색 확인
python3 highsci/tests/test_schools.py    # 가짜 나이스 API·학교 홈페이지로 학교별 기출(HWP/HWPX) 수집 확인
```
