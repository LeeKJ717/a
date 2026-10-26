#!/usr/bin/env bash
# 0장 재현 스크립트: 가상환경을 처음부터 만들고, requirements.txt 대로 설치하고,
# 제1권 11장 계산 스크립트를 실행해, 출력의 SHA-256이 기대값과 같은지 본다.
# 사용: bash repro-ch00-v1.sh [작업폴더]   (기본: 임시 폴더)
# 단계 하나가 실패해도 다음 단계로 간다. 마지막에 요약한다.
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$(mktemp -d)}"
FAIL=0
step() { echo; echo "[단계] $1"; }
step "1 가상환경 만들기 ($WORK/venv)"
python3 -m venv "$WORK/venv" && echo "  성공" || { echo "  실패"; FAIL=1; }
step "2 requirements.txt 설치"
"$WORK/venv/bin/pip" install -q -r "$HERE/requirements.txt" 2>&1 | grep -v notice
"$WORK/venv/bin/pip" freeze > "$WORK/freeze.txt"
if diff -q "$HERE/requirements.txt" "$WORK/freeze.txt" >/dev/null; then echo "  설치된 버전이 requirements.txt와 같다"; else echo "  버전이 다르다"; diff "$HERE/requirements.txt" "$WORK/freeze.txt"; FAIL=1; fi
step "3 계산 스크립트 실행"
"$WORK/venv/bin/python" -I "$HERE/vol1-ch11-calc-v1.py" > "$WORK/out.log" 2>&1 && echo "  종료 코드 0, $(wc -l < "$WORK/out.log")줄" || { echo "  실패"; FAIL=1; }
step "4 출력 해시 대조"
GOT="$(sha256sum "$WORK/out.log" | awk '{print $1}')"; WANT="$(cat "$HERE/expected.sha256")"
echo "  기대 $WANT"; echo "  실제 $GOT"
[ "$GOT" = "$WANT" ] && echo "  같다" || { echo "  다르다"; FAIL=1; }
step "5 제1권 원고와 대조"
if [ -f /home/claude/book/ms/ch11-v1.md ]; then "$WORK/venv/bin/python" -I "$HERE/verify-vol1-v1.py" "$WORK/out.log" /home/claude/book/ms/ch11-v1.md | tail -1; else echo "  제1권 원고 경로 없음, 건너뜀"; fi
echo; [ $FAIL = 0 ] && echo "요약: 모두 통과" || echo "요약: 실패한 단계가 있다"
exit $FAIL
