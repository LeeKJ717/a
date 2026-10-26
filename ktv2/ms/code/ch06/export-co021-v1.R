# 6장 실습 6-3a: dplR 꾸러미에 들어 있는 ITRDB 자료 co021(Schulman Old Tree No. 1, Mesa Verde)을 Tucson 형식으로 내보낸다.
# 실행: RLIB=/tmp/claude-0/rlib Rscript export-co021-v1.R | tee export-co021.log
# (RLIB는 dplR를 사용자 폴더에 설치했을 때만 지정한다. 일반 설치라면 필요 없다.)
rl <- Sys.getenv("RLIB", unset = "")
if (nzchar(rl)) .libPaths(c(rl, .libPaths()))
suppressMessages(library(dplR))
cat("R:", R.version.string, "\n")
cat("dplR:", as.character(packageVersion("dplR")), "\n")
data(co021)
cat("co021: 계열", ncol(co021), "개, 연도", min(as.numeric(rownames(co021))), "~", max(as.numeric(rownames(co021))), "(", nrow(co021), "년 )\n")
prov <- attr(co021, "dplR.provenance")
if (!is.null(prov)) {
  cat("출처 기록(dplR.provenance$file):", prov$file, "\n")
  cat("정밀도 기록(precision):\n"); print(utils::head(prov$precision))
  cat("안쪽 결측 기록(gaps):", if (is.data.frame(prov$gaps) && nrow(prov$gaps) > 0) "있음" else "없음", "\n")
}
dir.create("work", showWarnings = FALSE)
write.tucson(co021, "work/co021.rwl", prec = 0.01)
cat("저장: work/co021.rwl, 크기", file.size("work/co021.rwl"), "바이트\n")
