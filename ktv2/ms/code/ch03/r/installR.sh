#!/usr/bin/env bash
# R 과 R 패키지 설치 (이 책의 컨테이너: Ubuntu 24.04, apt 와 GitHub 만 열려 있고 CRAN 은 쓰지 않았다).
# apt 의 R 4.3.3 은 maps 3.4.2, Rcpp 1.0.12 를 주는데 rice 2.3.1 은 maps >= 3.4.2.1, rbacon 4.0.2 는 Rcpp >= 1.1.1 을 요구한다.
# 이 책은 두 요구 조건을 DESCRIPTION 에서 풀고(sed) 설치했다. 즉 패키지 제작자가 시험하지 않은 조합이다.
# 결과가 이 조합에서 맞는지는 이 책이 확인하지 못했다(실행은 되었고 아래 실습 3-5 의 로그가 있다).
set -u
LIB="${1:-$HOME/Rlib}"
mkdir -p "$LIB"
apt-get install -y -q r-base-core r-cran-data.table r-cran-jsonlite r-cran-rcpp r-cran-rcpparmadillo r-cran-ggplot2 r-cran-coda r-cran-maps r-cran-rlang || echo "apt 실패"
TMP="$(mktemp -d)"; cd "$TMP"
for r in rintcal rice rbacon clam; do git clone -q --depth 1 "https://github.com/Maarten14C/$r" && echo "$r $(git -C $r rev-parse --short HEAD)"; done
sed -i 's/maps (>= 3.4.2.1)/maps/' rice/DESCRIPTION
sed -i 's/Rcpp (>= 1.1.1)/Rcpp/' rbacon/DESCRIPTION
for p in rintcal rice rbacon clam; do R CMD INSTALL --library="$LIB" "$p" 2>&1 | tail -1; done
R_LIBS="$LIB" Rscript -e 'for (p in c("rintcal","rice","rbacon","clam")) cat(p, as.character(packageVersion(p)), "\n")'
