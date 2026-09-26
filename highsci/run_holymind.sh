#!/usr/bin/env bash
# holymind에서 통합과학 문제은행 GPU 생성을 백그라운드로 시작한다.
#   ./run_holymind.sh              # 시작 (이미 생성된 문항은 건너뛰고 이어서)
#   ./run_holymind.sh status       # 진행 현황
#   ./run_holymind.sh stop         # 중지 (다시 시작하면 이어서 생성)
#   ./run_holymind.sh log          # 실시간 로그
# 추가 옵션은 generate.py로 그대로 전달된다. 예) ./run_holymind.sh --workers 4 --model gemma4:27b
set -euo pipefail
cd "$(dirname "$0")"

OUT="${HIGHSCI_OUT:-$(python3 -c 'import generate; print(generate.default_out_dir())')}"
mkdir -p "$OUT/logs"
PIDFILE="$OUT/logs/generate.pid"
LOG="$OUT/logs/generate.log"

case "${1:-start}" in
  status) exec python3 generate.py --out "$OUT" --status ;;
  log)    exec tail -f "$LOG" ;;
  stop)
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      kill -TERM "$(cat "$PIDFILE")" && echo "중지 요청 보냄 (현재 호출이 끝나면 멈춤)"
    else
      echo "실행 중이 아님"
    fi
    exit 0 ;;
  start) shift || true ;;
  -*) ;;  # 옵션만 주면 start
  *) echo "사용법: $0 [start|status|stop|log] [generate.py 옵션]"; exit 1 ;;
esac

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "이미 실행 중 (pid $(cat "$PIDFILE")). 로그: $LOG"; exit 0
fi

command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader \
  || echo "경고: nvidia-smi 없음 — GPU 확인 불가"
curl -sf "${OLLAMA_URL:-http://localhost:11434}/api/tags" >/dev/null \
  || { echo "Ollama가 응답하지 않습니다: sudo systemctl start ollama"; exit 1; }

nohup python3 -u generate.py --out "$OUT" "$@" >>"$LOG" 2>&1 &
echo $! >"$PIDFILE"
echo "시작 pid $(cat "$PIDFILE") → 저장: $OUT/highsci.db  로그: $LOG"
