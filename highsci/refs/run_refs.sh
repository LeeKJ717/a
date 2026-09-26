#!/usr/bin/env bash
# holymind에서 참고 자료 수집을 백그라운드로 실행한다 (이어하기 가능).
#   ./refs/run_refs.sh                 # 전체: 찾기 → 내려받기 → 본문 추출
#   ./refs/run_refs.sh --discover      # 링크만 찾아 목록화
#   ./refs/run_refs.sh status | log | stop
#   ./refs/run_refs.sh search 自由落下
#   NEIS_API_KEY=... ./refs/run_refs.sh --schools   # 서울 중·고 학교별 기출
set -euo pipefail
cd "$(dirname "$0")"
OUT="${HIGHSCI_OUT:-$(cd .. && python3 -c 'import generate; print(generate.default_out_dir())')}"
mkdir -p "$OUT/logs"
PIDFILE="$OUT/logs/refs.pid"; LOG="$OUT/logs/refs.log"
case "${1:-}" in
  status) exec python3 fetch_refs.py --out "$OUT" --status ;;
  search) shift; exec python3 fetch_refs.py --out "$OUT" --search "$*" ;;
  log)    exec tail -f "$LOG" ;;
  stop)   [[ -f "$PIDFILE" ]] && kill "$(cat "$PIDFILE")" 2>/dev/null && echo "중지함" || echo "실행 중이 아님"; exit 0 ;;
esac
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then echo "이미 실행 중 (pid $(cat "$PIDFILE"))"; exit 0; fi
command -v pdftotext >/dev/null || echo "참고: 본문 검색을 쓰려면 sudo apt install poppler-utils (나중에 --extract로 추출 가능)"
nohup python3 -u fetch_refs.py --out "$OUT" "$@" >>"$LOG" 2>&1 &
echo $! >"$PIDFILE"
echo "시작 pid $(cat "$PIDFILE") → 파일: $OUT/references  DB: $OUT/highsci.db  로그: $LOG"
