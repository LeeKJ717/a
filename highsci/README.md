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
  │    (DB는 여기 한 곳에만 저장)            │ ─────────────────▶ │ z440     GPU  슬롯 2  │
  │                                       │ ─────────────────▶ │ soul3    GPU  슬롯 2  │
  └───────────────────────────────────────┘                    └──────────────────────┘
        ▲ 프롬프트: ssh soul3 → prompt_db
```

**GPU 서버 네 대가 모두 생성에 참여합니다.** z440과 soul3의 동시 요청 수(slots)는 VRAM을 확인하기 전이라 2로 두었습니다. `nvidia-smi`로 메모리 여유를 본 뒤 `nodes.json`에서 조정하세요. z440은 공개 웹 서버이므로 사이트가 느려지면 1로 낮추세요. 일부 서버만 쓰려면 `./run_holymind.sh --only-nodes holymind z840`를 씁니다.

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

# 4) GPU 서버 준비 (Ollama 외부 접속·동시 처리·모델 pull·방화벽) — 서버마다 sudo 비밀번호를 물을 수 있음
sudo ./setup_node.sh --parallel 3      # holymind 자신 (slots 3과 맞춤)
./deploy_nodes.sh                       # nodes.json의 enabled 원격 서버 (z840, z440, soul3)
MODEL=gemma4:27b ./deploy_nodes.sh z840 # 특정 서버만, 모델 지정

# 5) 서버 상태 확인 → 생성 시작
./run_holymind.sh check
./run_holymind.sh                       # 백그라운드 시작 (중단 후 재실행하면 이어서 생성)
./run_holymind.sh status                # 중단원별 진행 + 서버별 배치·채택·거부·속도
./run_holymind.sh log
./run_holymind.sh stop
```

`setup_node.sh`가 각 서버에서 하는 일은 다음과 같습니다.
- Ollama를 `0.0.0.0:11434`로 열고, `OLLAMA_NUM_PARALLEL`을 slots 값으로 맞춥니다. 모델은 24시간 메모리에 상주시킵니다.
- 11434 포트는 **코디네이터(holymind)에서만 접속을 허용**하도록 ufw, firewalld, iptables 중 사용 중인 방화벽에 규칙을 추가합니다.
- Ollama가 없는 서버에서는 `--install` 옵션으로 설치할 수 있습니다. 직접 실행할 때는 `sudo ./setup_node.sh --install --model gemma4:e4b --parallel 2`처럼 씁니다.

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

## 테스트 (GPU 없이)

```bash
python3 highsci/tests/test_pipeline.py   # 가짜 Ollama 서버 4대로 분산·장애 전환·중복 제거·이어하기·내보내기 확인
```
