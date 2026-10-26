#!/bin/bash
# 13장 실습 재실행. 모델이 필요 없다. 사용: bash run-all-v1.sh
cd "$(dirname "$0")"
t() { local out=$1; shift; local s=$(date +%s.%N); "$@" > "$out" 2>&1; local rc=$?; local e=$(date +%s.%N); printf '  -> %s: 종료 코드 %s, %.2f초\n' "$out" "$rc" "$(echo "$e - $s" | bc)"; }
echo "[1] 입력 준비";                t make-inputs.log python3 -I make-inputs-v1.py
echo "[2] 점검기 단위 시험";          t selftest.log python3 -I selftest-v1.py
echo "[3] 시연 출력 점검(좁은 원문)"; t eval-demo-narrow.log python3 -I eval-demo-v1.py
echo "[4] 시연 출력 점검(넓은 원문)"; t eval-demo-wide.log python3 -I eval-demo-v1.py input/vol1-ch11-v1.md
echo "[5] 제1권 11장 점검";          t eval-vol1.log python3 -I eval-vol1-v1.py
echo "[6] 원문 범위와 숫자 포함률";   t coverage.log python3 -I coverage-v1.py
echo "[7] 두 실행 비교";             t diffruns.log python3 -I halluccheck-v1.py diffruns demo-model-output-v1.md demo-model-output-v1b.md
echo "[8] 문법 검사";                t syntax-check.log python3 -m py_compile llm-client-v1.py halluccheck-v1.py eval-demo-v1.py eval-vol1-v1.py selftest-v1.py coverage-v1.py make-inputs-v1.py
echo "[9] 가중치 메모리 산술"; t memcalc.log python3 -I memcalc-v1.py
rm -rf __pycache__
