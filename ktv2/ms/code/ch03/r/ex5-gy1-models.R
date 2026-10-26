# 실습 3-5: GY-1 코어(제1권 표 6-5)의 9개 14C 날짜를 R 패키지 clam, rbacon 으로 모형화한다.
# 실행: R_LIBS=<설치 폴더> Rscript ex5-gy1-models.R <작업 폴더>
# 곡선은 IntCal20 (rintcal 1.4.2 에 들어 있는 것). 제1권(Park 등, 2019)은 IntCal13 을 썼다.
args <- commandArgs(trailingOnly = TRUE)
work <- if (length(args) >= 1) args[1] else tempdir()
dir.create(work, showWarnings = FALSE, recursive = TRUE)
suppressMessages({library(rintcal); library(clam); library(rbacon)})
cat("R", R.version.string, "\n")
for (p in c("rintcal", "rice", "clam", "rbacon", "Rcpp", "data.table")) cat(p, as.character(packageVersion(p)), "\n")
d <- data.frame(
  labID = paste0("GY", c(363, 739, 889, 917, 1416, 1839, 2060, 2351, 2892)),
  age   = c(1800, 2810, 4150, 6100, 7210, 7900, 7960, 8030, 8870),
  error = c(30, 30, 30, 40, 40, 40, 40, 40, 40),
  depth = c(363, 739, 889, 917, 1416, 1839, 2060, 2351, 2892))
# ---- Bacon: 베이즈 연령-깊이 (rbacon). 설정 두 가지: A(기본에 가까운 값), B(누적률의 변화를 더 허용)
run_bacon <- function(tag, thick, acc.mean, acc.shape, mem.mean, mem.strength) {
  bdir <- file.path(work, "Bacon_runs", tag); dir.create(bdir, showWarnings = FALSE, recursive = TRUE)
  write.csv(cbind(d, cc = 1), file.path(bdir, paste0(tag, ".csv")), row.names = FALSE, quote = FALSE)
  set.seed(20261026)
  t0 <- Sys.time()
  cat("\n==== Bacon 설정", tag, ": thick", thick, "acc.mean", acc.mean, "acc.shape", acc.shape, "mem.mean", mem.mean, "mem.strength", mem.strength, "\n")
  invisible(capture.output(
    Bacon(tag, coredir = file.path(work, "Bacon_runs"), thick = thick, acc.mean = acc.mean, acc.shape = acc.shape, mem.mean = mem.mean, mem.strength = mem.strength,
          d.min = 363, d.max = 2892, cc = 1, ask = FALSE, suggest = FALSE, plot.pdf = FALSE, save.info = FALSE, close.connections = TRUE, ssize = 6000, th0 = 1000, normal = FALSE, run = TRUE),
    type = "output"))
  cat("Bacon 실행 시간(초):", round(as.numeric(difftime(Sys.time(), t0, units = "secs")), 1), "\n")
  af <- list.files(bdir, pattern = "_ages\\.txt$", full.names = TRUE)
  ages <- read.table(af[1], header = TRUE)
  cat("출력 열:", paste(colnames(ages), collapse = ", "), " 행 수:", nrow(ages), "\n")
  for (dep in c(363, 917, 1416, 1500, 1600, 1839, 2060, 2351, 2892)) {
    r <- ages[which.min(abs(ages$depth - dep)), ]
    cat(sprintf("  깊이 %d cm: 중앙값 %.0f, 95%% [%.0f, %.0f] cal BP (폭 %.0f)\n", r$depth, r$median, r$qmin, r$qmax, r$qmax - r$qmin))
  }
  cross <- function(col) { o <- order(ages[[col]]); approx(ages[[col]][o], ages$depth[o], xout = 8200, ties = "ordered")$y }
  cat(sprintf("  8200 cal BP 의 깊이: 중앙값 곡선 %.0f cm, 95%% 띠의 두 선 %.0f cm, %.0f cm\n", cross("median"), cross("qmax"), cross("qmin")))
  write.csv(ages, file.path(work, paste0("GY1-bacon-", tag, "-ages.csv")), row.names = FALSE)
  s <- readLines(file.path(bdir, list.files(bdir, pattern = "_summary\\.txt$")[1]))
  cat("  요약 파일 앞부분:", paste(head(s, 6), collapse = " | "), "\n")
}
run_bacon("GY1A", 25, 10, 1.5, 0.7, 4)
run_bacon("GY1B", 25, 10, 0.5, 0.7, 4)
# ---- clam: 고전적 연령-깊이 (선형 보간, 보정 분포에서 반복 추출). 순서가 뒤집힌 모형은 버린다.
cdir <- file.path(work, "Cores", "GY1"); dir.create(cdir, showWarnings = FALSE, recursive = TRUE)
cc <- data.frame(ID = d$labID, C14_age = d$age, cal_BP = NA, error = d$error, reservoir = NA, depth = d$depth)
write.csv(cc, file.path(cdir, "GY1.csv"), row.names = FALSE, quote = FALSE, na = "")
set.seed(20261026)
t0 <- Sys.time()
txt <- tryCatch(capture.output(clam("GY1", coredir = file.path(work, "Cores"), type = 1, prob = 0.95, its = 5000, cc = 1, dmin = 363, dmax = 2892, every = 1,
                                    ask = FALSE, plotpdf = FALSE, plotpng = FALSE, storedat = FALSE, depths.file = FALSE, BCAD = FALSE, remove.reverse = 0.6), type = "output"),
                error = function(e) paste("오류:", conditionMessage(e)))
cat("\n==== clam 2.6.3 (type=1 선형 보간, its=5000, remove.reverse=0.6)\n")
cat(paste("  [clam]", txt), sep = "\n")
cat("clam 시간(초):", round(as.numeric(difftime(Sys.time(), t0, units = "secs")), 1), "\n")
cat("clam 출력 파일:", paste(list.files(cdir), collapse = ", "), "\n")
cal <- readLines(file.path(cdir, "GY1_calibrated.txt"))
cat("clam 이 보정한 95% 범위(파일 내용):\n"); cat(paste("  ", cal), sep = "\n")
cl <- read.delim(file.path(cdir, "GY1_interpolated_ages.txt"))
cat("clam 열:", paste(colnames(cl), collapse = ", "), " 행 수:", nrow(cl), "\n")
for (dep in c(363, 917, 1416, 1500, 1600, 1839, 2060, 2351, 2892)) {
  r <- cl[which.min(abs(cl$depth - dep)), ]
  cat(sprintf("  깊이 %d cm: 최선 %.0f, 95%% [%.0f, %.0f] cal BP (폭 %.0f)\n", r$depth, r$best, r[["min95."]], r[["max95."]], r[["max95."]] - r[["min95."]]))
}
crossc <- function(col) { o <- order(cl[[col]]); approx(cl[[col]][o], cl$depth[o], xout = 8200, ties = "ordered")$y }
cat(sprintf("  8200 cal BP 의 깊이: 최선 %.0f cm, 95%% 띠의 두 선 %.0f cm, %.0f cm\n", crossc("best"), crossc("min95."), crossc("max95.")))
write.csv(cl, file.path(work, "GY1-clam-ages.csv"), row.names = FALSE)
