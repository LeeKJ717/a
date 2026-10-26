#!/bin/bash
# 14장 실습을 순서대로 돌리고 걸린 시간을 run-times.log 에 적는다. 사용: cd ms/code/ch14 && bash runall-v1.sh
cd "$(dirname "$0")"
: > run-times.log
for s in p00-env p01-schema p02-demo-load p03-vol1-quotes p04-grade p05-topo-demo p06-vol1-checks p07-exchange; do
  a=$(date +%s.%N)
  python3 -W ignore ${s}-v1.py > ${s}.log 2>&1 || echo "FAIL $s" >> run-times.log
  b=$(date +%s.%N)
  printf '%-18s %.2f초\n' "$s" "$(echo "$b - $a" | bc)" >> run-times.log
done
cat run-times.log
