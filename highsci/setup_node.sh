#!/usr/bin/env bash
# GPU 서버(z840 / z440 / soul3 …)를 highsci 생성 노드로 준비한다. 각 서버에서 root로 실행.
#   sudo ./setup_node.sh [--model gemma4:e4b] [--parallel 2] [--coordinator 192.168.0.14] [--install]
# 하는 일:
#   1) Ollama 확인 (--install이면 없을 때 설치)
#   2) systemd override: LAN에서 접속 허용(0.0.0.0:11434), 동시 요청 수, 모델 상주 시간
#   3) 모델 pull
#   4) 방화벽: 11434 포트는 코디네이터(holymind)에서만 접속 허용
set -euo pipefail

MODEL="gemma4:e4b"; PARALLEL=2; COORD="192.168.0.14"; INSTALL=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --parallel) PARALLEL="$2"; shift 2 ;;
    --coordinator) COORD="$2"; shift 2 ;;
    --install) INSTALL=1; shift ;;
    *) echo "알 수 없는 옵션: $1"; exit 1 ;;
  esac
done
[[ $EUID -eq 0 ]] || { echo "root로 실행하세요 (sudo)"; exit 1; }
HOST=$(hostname)
echo "== $HOST: model=$MODEL parallel=$PARALLEL coordinator=$COORD"

if command -v nvidia-smi >/dev/null; then
  nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader
else
  echo "경고: GPU(nvidia-smi)가 없습니다 — CPU로 돌면 매우 느립니다."
fi

if ! command -v ollama >/dev/null; then
  if [[ $INSTALL -eq 1 ]]; then
    curl -fsSL https://ollama.com/install.sh | sh
  else
    echo "Ollama 미설치. 설치하려면 --install 옵션으로 다시 실행하세요."; exit 1
  fi
fi

mkdir -p /etc/systemd/system/ollama.service.d
cat >/etc/systemd/system/ollama.service.d/highsci.conf <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_NUM_PARALLEL=$PARALLEL"
Environment="OLLAMA_KEEP_ALIVE=24h"
EOF
systemctl daemon-reload
systemctl enable --now ollama >/dev/null 2>&1 || true
systemctl restart ollama
for i in $(seq 1 30); do curl -sf http://127.0.0.1:11434/api/tags >/dev/null && break; sleep 1; done
curl -sf http://127.0.0.1:11434/api/tags >/dev/null || { echo "Ollama 기동 실패: journalctl -u ollama"; exit 1; }

ollama pull "$MODEL"

# 방화벽: 11434는 코디네이터만. (z440처럼 공인 트래픽을 받는 서버에서 특히 중요)
if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
  ufw allow from "$COORD" to any port 11434 proto tcp comment 'highsci coordinator'
  ufw deny 11434/tcp comment 'highsci ollama block others' || true
  echo "ufw: 11434 ← $COORD 만 허용"
elif command -v firewall-cmd >/dev/null && firewall-cmd --state >/dev/null 2>&1; then
  firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address=$COORD port port=11434 protocol=tcp accept"
  firewall-cmd --reload
  echo "firewalld: 11434 ← $COORD 만 허용"
else
  if ! iptables -C INPUT -p tcp --dport 11434 -s "$COORD" -j ACCEPT 2>/dev/null; then
    iptables -I INPUT -p tcp --dport 11434 -j DROP
    iptables -I INPUT -p tcp --dport 11434 -s 127.0.0.1 -j ACCEPT
    iptables -I INPUT -p tcp --dport 11434 -s "$COORD" -j ACCEPT
  fi
  echo "iptables: 11434 ← $COORD, 127.0.0.1 만 허용 (재부팅 시 유지하려면 iptables-persistent 등으로 저장)"
fi

echo "== $HOST 준비 완료. holymind에서 확인: ./run_holymind.sh check"
