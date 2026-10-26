#!/bin/bash
# 7장 실습을 처음부터 끝까지 다시 실행해 로그를 만든다.
# 사용: VENV=가상환경경로 PP=PyPopART가설치된가상환경경로 bash repro-ch07-v1.sh
# VENV에는 requirements-ch07-v1.txt가, PP에는 pypopart-install.log의 설치가 되어 있어야 한다. PP를 비우면 대조를 건너뛴다.
cd "$(dirname "$0")" || exit 1
PY="${VENV:-.venv}/bin/python"
: > run-times.log
for f in gentools.py hgtab-v1.py fisher-v1.py distmat-v1.py amova-v1.py mantel-v1.py network-v1.py fstats-v1.py hand-v1.py mytable-v1.py recon-v1.py sens-v1.py pypopart-run-v1.py; do
  "$PY" -m py_compile "$f" && echo "py_compile $f 통과" >> run-times.log || echo "py_compile $f 실패" >> run-times.log
done
run() { # 이름, 로그, 명령...
  local s e; s=$(date +%s.%N); "$PY" "$1" "${@:3}" > "$2" 2>&1; local rc=$?; e=$(date +%s.%N)
  printf '%-16s 종료코드 %d  %.1f s\n' "$1" "$rc" "$(echo "$e - $s" | bc)" >> run-times.log
}
run hgtab-v1.py hgtab.log
run fisher-v1.py fisher.log
run distmat-v1.py distmat.log
run amova-v1.py amova.log
run mantel-v1.py mantel.log
if [ -n "$PP" ]; then run network-v1.py network.log --pp "$PP/bin/python"; else run network-v1.py network.log; fi
run fstats-v1.py fstats.log
run hand-v1.py hand.log
run recon-v1.py recon.log
run sens-v1.py sens.log
run mytable-v1.py mytable.log demo-table-v1.csv
run mytable-v1.py mytable-bad.log demo-bad-v1.csv   # 일부러 틀린 입력: 종료 코드 2가 정상
"$PY" /home/claude/book/ms/ch13-calc-v1.py > vol1-ch13-calc.log 2>&1
sha256sum /home/claude/book/ms/ch11-calc-v1.py /home/claude/book/ms/ch13-calc-v1.py cui-table1-v1.csv demo-table-v1.csv demo-bad-v1.csv > inputs.sha256
cat run-times.log
