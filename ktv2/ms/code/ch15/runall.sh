#!/bin/bash
# 15장 실습을 처음부터 끝까지 실행한다. 사용: bash runall.sh (이 폴더에서)
# 1) 입력을 제1권 원고에서 옮기고 2) 세 사례를 실행해 로그를 만들고 3) 같은 스크립트를 한 번 더 돌려 로그가 바이트 단위로 같은지 본다.
# 로그에는 시간이 없으므로 같아야 한다. 시간은 timing.log에 따로 적는다.
cd "$(dirname "$0")" || exit 1
{ date; python3 --version; python3 -c "import numpy, scipy, platform; print('numpy', numpy.__version__, 'scipy', scipy.__version__, platform.platform())"; nproc; } > env.log 2>&1
: > timing.log
t() { # 이름 명령...
  local n=$1; shift
  local t0=$(date +%s.%N)
  "$@"; local rc=$?
  local t1=$(date +%s.%N)
  awk -v n="$n" -v rc="$rc" -v a="$t0" -v b="$t1" 'BEGIN{printf "%s 종료코드 %d 걸린시간 %.1f초\n", n, rc, b-a}' >> timing.log
}
t 00-extract-inputs python3 00-extract-inputs.py > 00-extract-inputs.log 2>&1
t case1-seoyohe python3 case1-seoyohe.py > case1.log 2>&1
t case2-ulleung python3 case2-ulleung.py > case2.log 2>&1
t case3-gorges python3 case3-gorges.py > case3.log 2>&1
# 두 번째 실행과 비교
: > repro.log
for s in 00-extract-inputs case1-seoyohe case2-ulleung case3-gorges; do
  case $s in 00-extract-inputs) lg=00-extract-inputs.log;; case1-seoyohe) lg=case1.log;; case2-ulleung) lg=case2.log;; case3-gorges) lg=case3.log;; esac
  python3 $s.py > /tmp/ch15-second-$$.log 2>&1
  if cmp -s $lg /tmp/ch15-second-$$.log; then r="두 번의 로그가 같다"; else r="두 번의 로그가 다르다"; fi
  printf '%-20s %s  sha256 %s\n' "$s" "$r" "$(sha256sum $lg | cut -c1-16)" >> repro.log
done
rm -f /tmp/ch15-second-$$.log
# 입력의 지문: 제1권 원고, 앞 장 코드, 이 장이 만든 입력
sha256sum /home/claude/book/ms/ch04-v1.md /home/claude/book/ms/ch10-v1.md /home/claude/book/ms/ch11-v1.md \
  /home/claude/book/ms/ch04-calc-v1.py /home/claude/book/ms/ch11-calc-v1.py \
  ../ch03/c14lib.py ../ch05/fisher-scratch.py ../ch05/bootstrap-basic.py ../ch05/permutation-basic.py ../ch08/sedkit.py ../ch09/tephralib.py \
  ../ch03/data/3Col_intcal04.14C ../ch03/data/3Col_intcal13.14C ../ch03/data/3Col_intcal20.14C data/*.csv > inputs.sha256
cat timing.log repro.log
