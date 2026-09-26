# highsci — 통합과학1·2 문제은행 (2022 개정)

holymind GPU(Ollama gemma)로 통합과학1·2의 **물리·화학·생물·지구과학 중단원별 1,000문항**을 생성해
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

## holymind 실행 순서

```bash
# 1) soul3: 프롬프트 등록 (prompt_db 표준, 최초 1회)
mysql -u prompt_user -p'prompt2026!' --socket=/home/mysql/mysql.sock prompt_db < highsci/sql/register_prompts.sql

# 2) holymind: 코드 받기
git clone -b claude/common-science-problem-bank-fkflws https://github.com/LeeKJ717/a.git ~/highsci_src
cd ~/highsci_src/highsci

# 3) holymind → soul3 ssh 키 접속 확인 (프롬프트 조회용)
ssh -o BatchMode=yes 192.168.0.20 true && echo OK

# 4) 생성 시작 (백그라운드, 중단 후 재실행하면 이어서 생성)
./run_holymind.sh                          # 기본: 모델은 prompt_db 값(gemma4:e4b), 동시 2개
./run_holymind.sh --workers 4 --model gemma4:27b   # GPU 여유가 있으면
./run_holymind.sh status                   # 진행 현황
./run_holymind.sh log                      # 실시간 로그
./run_holymind.sh stop                     # 중지
```

`--workers`는 Ollama의 `OLLAMA_NUM_PARALLEL` 값과 맞추세요. 기본값으로는 요청이 순서대로 처리됩니다.

## 생성 방식

- **1회 호출에 5문항**을 생성합니다. 이때 성취기준, 대상 개념(적게 출제된 개념부터), 난이도, 인지 수준, 문항 유형(개념·자료 해석·계산·ㄱㄴㄷ 합답형·실생활·탐구)을 지정하고, 최근 출제한 문제 본문도 함께 보내 중복을 피하게 합니다.
- **난이도 목표 비율**은 1:2:3:4:5 = 10:25:30:25:10%입니다. 중단원당 100/250/300/250/100문항입니다.
- **품질 관리**: 형식 검사(5지선다, 정답 1~5, 보기 중복 금지)와 본문 해시 중복 제거를 거칩니다. 그다음 `highsci_item_verify`로 **모델이 문항을 따로 풀어 정답이 일치하고 오류가 없는 문항만** 저장합니다. `--no-verify`로 끄면 속도는 약 2배가 되지만 품질이 떨어집니다.
- 소요 시간은 모델과 GPU에 따라 크게 달라집니다. 로그의 호출당 초(`…s`)로 계산하세요. 예를 들어 5문항 생성과 검증에 40초가 걸리면 24,000문항에 약 53시간이 걸립니다.

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
python3 highsci/tests/test_pipeline.py   # 가짜 Ollama 서버로 생성·검증·중복 제거·이어하기·내보내기 확인
```
