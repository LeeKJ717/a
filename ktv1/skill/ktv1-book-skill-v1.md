# 『1만 년의 기후와 땅』 제작 스킬 v1 (2026-10-23)

## 1. 목적과 판형
- 시리즈 『1만 년의 기후와 땅』, 1권 『동아시아 1만 년의 기후와 땅』(부제 한반도에서 본 홀로세의 기후와 지형 변화). 과학과영성출판사, 이광조 지음.
- B5 182×257 mm, 왼쪽 여백 20%(36.4 mm), 쪽수 제한 없음, 컬러·흑백 두 판, 지도 이름은 한글만.
- 목차에 쪽번호, 모든 쪽 쪽번호, 그림·표 번호와 제목, 장마다 APA 7판 참고문헌, 파일명에 버전, 밑줄 금지.

## 2. 절대 규칙
1. 근거 없는 내용을 만들지 않는다. PDF에서 확인한 숫자만 쓰고, 나머지는 "근거 논문 확보 필요", "원문 확인 필요", "출처 확인 필요"로 적는다.
2. 서로 맞서는 주장은 지우지 않고 나란히 놓는다.
3. 물리 증거를 먼저 놓고, 문헌 사료는 시험할 주장으로 다룬다.
4. 위상 추정 절을 둔다(사료 지명과 날짜를 좌표와 시각으로 옮기는 규칙).
5. 새 DB는 z840 /data/safe/dball2/ktv_db 에 저장한다. 장마다 작업 내용을 DB에 저장한다.
6. 사용자 호칭은 "이박사님". 시각·휴식 언급 금지. 한자어는 한국 독음.

## 3. 조판 파이프라인
- ms/chNN-vK.md → build.py(python-markdown md_in_html+tables, WeasyPrint 70) → build/book-{color,bw}-vNN.pdf. 모드는 한 번에 하나씩 실행(각 2~3분 + 배치 점검 반복).
- 글꼴: 본문 Noto Serif CJK KR, 제목 Noto Sans CJK KR.
- 장 표지 쪽(.opener): 오른쪽 쪽에서 시작, 대표 그림 129.6×64 mm + 장 차례, 뒷면에 장 안내. 그림은 scripts/chapart-v1.py(Natural Earth, 도안용).
- 표: 높이 198 mm 이하는 keep 으로 쪽 나눔 방지, 초과하면 머리글 반복하며 분할. 절 제목만 쪽 끝에 남는 것은 data-hk/data-ck 표식으로 한 번씩 break-before 를 넣는 반복 보정.
- 점검: scripts/audit-v1.py (OVER, SPLIT, ORPHAN-HEADING, CAPTION-END, SPARSE). 마지막 결과 OVER 0, ORPHAN 0, CAPTION-END 0, SPLIT 23(모두 198 mm 초과 표), SPARSE 20.
- 알려진 함정: body margin 0 필요, 표 높이는 TableBox만 합산, 래퍼 정규식은 캡션을 제한된 패턴으로, 장식 순서(z-index)로 저자명이 가려지지 않게.

## 4. 표지
- scripts/cover-v3.py: `ART=그림.jpg python3 scripts/cover-v3.py 쪽수 버전` → cover/front, back, spread, spreadflap PDF.
- 날개 100 mm(교보 POD 날개 최대 100 mm, 표지 가로 최대 610 mm, A4 제외 판형, 차별화책 불가). 쪽수 522 기준 책등 29.2 mm = 쪽수×0.055+0.5 (인쇄소 용지 두께로 교체). 펼침 가로 599.2 mm.
- 앞날개: 저자 소개(저자가 밝힌 이력만). 뒷날개: 집필 중인 책 4권(서경 1권, 고전지명추정 1·2·3권) 썸네일 세로 배열 + 설명.
- 교보 업로드용 앞표지 1400 px: vol1-cover-front-c-1400px-v5.png/jpg (1400×1977).
- 그림은 z840 ComfyUI + Z-Image-Turbo(Apache 2.0). 선택안 C = 장면 k03 백두산 화산재(seed 1431483856). 고해상도 1536×1920 재생성 스크립트 gpucoverhi-v1.ps1 / run-ktv1coverhi-v1.sh.
- 로고: 출판사 로고 logo/ssp-*.svg (logo-final-v1.zip, Desktop\pod_v4\ssbook web).

## 5. 산출물 전달
- 윈도우 Desktop\daily3\climate10k, device_commit_files 로 전달(outputs 에 먼저 복사). 문서는 Downloads 에도 필요하면 복사.
- 3중 백업: z840 → z440 → NAS(/mnt/nas), SHA256 검증(triple-backup 스킬).

## 6. 남은 일
12장 한반도 신석기·청동기, 13장 일본열도, 14장 최근 천 년과 소빙기, 15장 현대, 부록. 7장은 자료 확보 전까지 공백. 책 소개·책의 지도 표·맺음·책등 갱신, 장 표지와 안내 추가, 고해상도 표지 그림, 표지 단일본 재조립, DB v14 적재(앞·안내·맺음 파일), 활자 DB v3 z840 전송, 쪽 점검.
