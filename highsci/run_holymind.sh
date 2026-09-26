#!/usr/bin/env bash
# holymind에서 분산 생성 코디네이터를 백그라운드로 시작한다 (GPU 서버 목록: nodes.json).
#   ./run_holymind.sh              # 시작 (이미 생성된 문항은 건너뛰고 이어서)
#   ./run_holymind.sh check        # z840·z440·soul3 Ollama 접속·모델 확인
#   ./run_holymind.sh status       # 진행 현황
#   ./run_holymind.sh stop         # 중지 (다시 시작하면 이어서 생성)
#   ./run_holymind.sh log          # 실시간 로그
# 추가 옵션은 generate.py로 그대로 전달된다. 예) ./run_holymind.sh --only-nodes z840 soul3
set -euo pipefail
cd "$(dirname "$0")"

OUT="${HIGHSCI_OUT:-$(python3 -c 'import generate; print(generate.default_out_dir())')}"
mkdir -p "$OUT/logs"
PIDFILE="$OUT/logs/generate.pid"
LOG="$OUT/logs/generate.log"

case "${1:-start}" in
  status) exec python3 generate.py --out "$OUT" --status ;;
  check)  shift; exec python3 generate.py --out "$OUT" --check-nodes "$@" ;;
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
  *) echo "사용법: $0 [start|check|status|stop|log] [generate.py 옵션]"; exit 1 ;;
esac

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "이미 실행 중 (pid $(cat "$PIDFILE")). 로그: $LOG"; exit 0
fi

python3 generate.py --out "$OUT" --check-nodes "$@" || { echo "사용 가능한 GPU 서버가 없습니다 (./deploy_nodes.sh 로 준비)"; exit 1; }

nohup python3 -u generate.py --out "$OUT" "$@" >>"$LOG" 2>&1 &
echo $! >"$PIDFILE"
echo "시작 pid $(cat "$PIDFILE") → 저장: $OUT/highsci.db  로그: $LOG"
