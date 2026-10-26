#!/bin/bash
# 9장 실습 스크립트를 차례로 실행하고 걸린 시간을 timing.log에 적는다. 실행: bash runall.sh (이 폴더에서)
cd "$(dirname "$0")"
{ date; python3 --version; python3 -c "import numpy, scipy, platform; print('numpy', numpy.__version__, 'scipy', scipy.__version__, platform.platform())"; nproc; } > env.log 2>&1
: > timing.log
for s in ex1-oxides ex2-agree ex3-ordered ex4-gap ex5-radius ex6-check-vol1; do
  t0=$(date +%s.%N)
  python3 $s.py > $s.log 2>&1
  rc=$?
  t1=$(date +%s.%N)
  printf '%s 종료코드 %d 걸린시간 %.1f초\n' $s $rc $(echo "$t1 - $t0" | bc) >> timing.log
done
cat timing.log
