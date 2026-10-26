#!/usr/bin/env bash
# 보정 곡선 내려받기 (이 책이 실제로 실행해 확인한 경로).
# 공식 입수처 intcal.org 는 이 책의 실행 환경에서 막혀 있어(프록시 403) 직접 받지 못했다.
# 대신 GitHub 의 rintcal 저장소(Blaauw 관리, IntCal 운영진의 허락을 받아 곡선을 모은 것)에서 받는다.
# 곡선 자료의 이용 조건은 공식 페이지에서 확인하지 못했다. 그래서 이 책의 폴더에는 곡선을 넣지 않고,
# 독자가 이 스크립트로 직접 받게 한다.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/data"
mkdir -p "$DEST"
TMP="$(mktemp -d)"
git clone --quiet --depth 1 https://github.com/Maarten14C/rintcal "$TMP/rintcal" || { echo "clone 실패: 입수 확인 필요"; exit 1; }
echo "rintcal 커밋: $(git -C "$TMP/rintcal" rev-parse HEAD)"
for f in 3Col_intcal20.14C 3Col_intcal13.14C 3Col_intcal04.14C 3Col_marine20.14C 3Col_marine13.14C; do
  cp "$TMP/rintcal/inst/extdata/$f" "$DEST/$f"
done
( cd "$DEST" && sha256sum 3Col_*.14C | tee SHA256SUMS.txt )
rm -rf "$TMP"
