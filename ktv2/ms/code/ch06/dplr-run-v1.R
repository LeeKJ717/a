# 6장 실습 6-10: R의 dplR로 같은 계산을 하고, 비교용 숫자를 work/ 폴더의 CSV로 남긴다(파이썬 쪽 비교는 compare-dplr-v1.py).
# 실행: RLIB=/tmp/claude-0/rlib Rscript dplr-run-v1.R | tee dplr-run.log
#   (RLIB는 dplR를 사용자 폴더에 설치했을 때만 지정한다. 일반 설치에서는 install.packages("dplR") 뒤 필요 없다.)
# 먼저 python3 synth-rings-v1.py, python3 crossdate-v1.py, Rscript export-co021-v1.R를 실행해 입력 파일을 만들어 둔다.
rl <- Sys.getenv("RLIB", unset = "")
if (nzchar(rl)) .libPaths(c(rl, .libPaths()))
suppressMessages(library(dplR))
cat("R:", R.version.string, "\n")
cat("dplR:", as.character(packageVersion("dplR")), "\n")
dir.create("work", showWarnings = FALSE)
t0 <- proc.time()[["elapsed"]]

dump_mat <- function(m, file) write.csv(m, file, na = "NA")
run_set <- function(rwl, tag, ids = NULL) {
  cat("\n=== 자료", tag, ": 계열", ncol(rwl), "개, 연도", min(as.numeric(rownames(rwl))), "~", max(as.numeric(rownames(rwl))), "\n")
  sp67 <- detrend(rwl, method = "Spline", make.plot = FALSE, verbose = FALSE)
  sp32 <- detrend(rwl, method = "Spline", nyrs = 32, make.plot = FALSE, verbose = FALSE)
  mne  <- suppressWarnings(detrend(rwl, method = "ModNegExp", make.plot = FALSE, verbose = FALSE))
  mean_ <- detrend(rwl, method = "Mean", make.plot = FALSE, verbose = FALSE)
  for (nm in c("sp67", "sp32", "mne", "mean_")) {
    m <- get(nm); dump_mat(m, sprintf("work/r-%s-%s.csv", tag, sub("_", "", nm)))
  }
  for (nm in c("sp67", "mne")) {
    m <- get(nm)
    crn <- chron(m, biweight = TRUE, prewhiten = (nm == "mne"))
    dump_mat(crn, sprintf("work/r-%s-chron-%s.csv", tag, nm))
  }
  # 연대기 통계: 피어슨, 전 기간(윈도 없음)
  for (nm in c("mne", "sp67")) {
    m <- get(nm)
    st <- rwi.stats(m, ids = ids, method = "pearson", round.decimals = NA_real_)
    cat(sprintf("rwi.stats(%s, ids=%s, pearson):\n", nm, if (is.null(ids)) "NULL" else "있음"))
    print(st, digits = 6)
    write.csv(st, sprintf("work/r-%s-stats-%s.csv", tag, nm), row.names = FALSE)
  }
  # SSS (ids가 있을 때)
  if (!is.null(ids)) {
    s <- sss(mne, ids)          # 이 버전의 sss()는 내부에서 rwi.stats()를 기본값(스피어만)으로 부른다
    # 같은 식을 피어슨 rbar.eff로 직접 계산한 것(파이썬과 견주기 위해)
    stp <- rwi.stats(mne, ids = ids, method = "pearson", round.decimals = NA_real_)
    nn <- sapply(seq_len(nrow(mne)), function(i) length(unique(ids$tree[rownames(ids) %in% colnames(mne)[!is.na(mne[i, ])]])))
    sp <- (nn * (1 + (stp$n.trees - 1) * stp$rbar.eff)) / (stp$n.trees * (1 + (nn - 1) * stp$rbar.eff))
    write.csv(data.frame(year = as.numeric(rownames(mne)), sss = s, sss.pearson = sp), sprintf("work/r-%s-sss-mne.csv", tag), row.names = FALSE)
    cat("sss(): dplR 기본값과 피어슨 rbar.eff로 직접 계산한 값의 최대 차이", format(max(abs(s - sp)), digits = 3), "\n")
  }
  # 평균 민감도 sens1 (ModNegExp 지수의 계열별)
  s1 <- sapply(mne, sens1)
  write.csv(data.frame(series = names(mne), sens1 = s1), sprintf("work/r-%s-sens1.csv", tag), row.names = FALSE)
  # 계열 사이 상관(교차 연대 결정의 점검)
  ic <- interseries.cor(rwl, nyrs = 32, prewhiten = TRUE, biweight = TRUE, method = "pearson")
  write.csv(ic, sprintf("work/r-%s-interseries.csv", tag))
  cat("interseries.cor(nyrs=32, pearson): 계열별 r 중앙값", round(median(ic$res.cor), 4), ", 최소", round(min(ic$res.cor), 4), "\n")
  invisible(NULL)
}

# ---- 자료 A: co021 (dplR 꾸러미에 든 ITRDB 자료)
data(co021)
run_set(co021, "co021", ids = NULL)

# ---- 자료 B: 시연값 (날짜를 고친 파일을 dplR로 읽는다)
rwlB <- read.rwl("synth-demo-fixed.rwl", verbose = FALSE)
idsB <- read.csv("synth-ids.csv")
idsB <- data.frame(tree = idsB$tree, core = idsB$core, row.names = idsB$series)
run_set(rwlB, "synth", ids = idsB)

# ---- dplR의 구간 상관 함수로 날짜 오류 찾기 (오류를 넣은 자료)
bad <- read.rwl("synth-demo-bad.rwl", verbose = FALSE)
rs <- corr.rwl.seg(bad, seg.length = 50, bin.floor = 0, nyrs = 32, prewhiten = TRUE, pcrit = 0.01,
                   biweight = TRUE, method = "pearson", make.plot = FALSE, lag.max = 10)
cat("\ncorr.rwl.seg(seg.length=50, bin.floor=0, nyrs=32, pcrit=0.01, pearson, lag.max=10): 구간은 0, 25, 50...년에 맞춘 25년 간격이다.\n")
for (nm in c("T01B", "T02B", "T04A", "T10A")) {
  cat(nm, "의 구간별 최고 상관 lag:\n"); print(rs$best.lag[nm, ])
}
write.csv(rs$best.lag, "work/r-synth-bestlag.csv")
write.csv(rs$spearman.rho, "work/r-synth-segrho.csv")   # 방법을 pearson으로 지정했으므로 이 표는 피어슨 r (열 이름만 spearman.rho)
fl <- rs$flags
cat("flags: 구간 상관이 pcrit 수준에서 유의하지 않아 표시된 구간. 표시된 계열 수", length(fl), "/", ncol(bad), "; T10A는", if ("T10A" %in% names(fl)) fl[["T10A"]] else "표시된 구간 없음", "\n")
tru <- read.rwl("synth-demo-true.rwl", verbose = FALSE)
rt <- corr.rwl.seg(tru, seg.length = 50, bin.floor = 0, nyrs = 32, prewhiten = TRUE, pcrit = 0.01,
                   biweight = TRUE, method = "pearson", make.plot = FALSE, lag.max = 10)
cat("참 날짜 자료에서 flags가 표시한 계열 수:", length(rt$flags), "/", ncol(tru), "\n")
cat("전체 소요 시간(초):", round(proc.time()[["elapsed"]] - t0, 1), "\n")
cat("\n세션 정보 요약\n"); print(sessionInfo()$R.version$version.string); print(packageVersion("dplR"))
