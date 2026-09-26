#!/usr/bin/env bash
# holymind에서 실행: nodes.json의 활성 서버마다 setup_node.sh를 복사해 실행한다.
#   ./deploy_nodes.sh                 # enabled 서버 전부
#   ./deploy_nodes.sh z840 soul3      # 지정 서버만
#   MODEL=gemma4:27b ./deploy_nodes.sh
# 각 서버에서 sudo 비밀번호를 물을 수 있다.
set -euo pipefail
cd "$(dirname "$0")"
MODEL="${MODEL:-gemma4:e4b}"
COORD="${COORD:-$(hostname -I | awk '{print $1}')}"

mapfile -t ROWS < <(python3 - "$@" <<'EOF'
import json, sys
want = set(sys.argv[1:])
for n in json.load(open("nodes.json", encoding="utf-8"))["nodes"]:
    if n.get("ssh") and ((n["name"] in want) if want else n.get("enabled", True)):
        print(n["name"], n["ssh"], n.get("slots", 1), n.get("model") or "")
EOF
)
[[ ${#ROWS[@]} -gt 0 ]] || { echo "대상 서버가 없습니다."; exit 1; }

for row in "${ROWS[@]}"; do
  read -r name host slots model <<<"$row"
  echo; echo "######## $name ($host) ########"
  scp -q setup_node.sh "$host:/tmp/highsci_setup_node.sh"
  ssh -t "$host" "sudo bash /tmp/highsci_setup_node.sh --model '${model:-$MODEL}' --parallel '$slots' --coordinator '$COORD'" \
    || echo "!! $name 준비 실패 — 위 메시지를 확인하세요"
done
echo; echo "완료. 확인: ./run_holymind.sh check"
