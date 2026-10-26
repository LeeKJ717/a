#!/usr/bin/env bash
# 3장 실습을 모두 실행해 로그를 남긴다. 곡선은 getcurves.sh 로 먼저 받는다.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
{
  echo "날짜: $(date -Iseconds)"
  python3 -I -c "import sys,numpy,scipy,matplotlib;print('Python',sys.version.split()[0]);print('numpy',numpy.__version__);print('scipy',scipy.__version__);print('matplotlib',matplotlib.__version__)"
  uname -sr
  if command -v nvidia-smi >/dev/null; then echo "GPU: 있음"; else echo "GPU: 없음, nvidia-smi 없음"; fi
  nproc | sed 's/^/CPU 코어: /'
} > env.log
: > timing.log
for ex in ex1-c14-formulas ex2-calibrate ex3-agedepth ex4-osl ex6-clam-compare; do
  s=$(date +%s.%N)
  python3 -I "$ex.py" > "$ex.log" 2>&1
  rc=$?
  e=$(date +%s.%N)
  printf '%s rc=%s %.2f s\n' "$ex" "$rc" "$(echo "$e - $s" | bc)" | tee -a timing.log
done
