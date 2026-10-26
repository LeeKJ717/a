# 2장 계산 재현 코드 (ch02-v2 계산 2-1 ~ 2-21). python3 ch02-calc-v1.py
import math
import numpy as np

print("== 방법 1: 속도 ==")
print("8 m / 3800 yr =", 8000/3800, "mm/yr")
print("15 m / 3000 yr =", 15000/3000, "mm/yr;  25 m / 4000 yr =", 25000/4000)

print("== 방법 2: 단구 융기 속도 (H-S)/T ==")
for H, S, T in [(13, 0, 12060), (15, 0, 12060), (13, -70, 12060), (15, -70, 12000)]:
    print(H, S, T, round((H - S) * 1000 / T, 3), "mm/yr")
print("0.032~0.112:", 4000/125000, 14000/125000)

print("== 방법 3: 선형 보간 ==")
print(7660 + (8 - 14.5) / (2 - 14.5) * (6020 - 7660))

print("== 방법 4: phi ==")
for d in (0.125, 0.25, 0.0625, 0.18):
    print(d, -math.log2(d))
print("phi 2.5 ->", 2 ** -2.5, "mm")

print("== 방법 5: 오차 합성, 최소제곱 ==")
print(math.hypot(3, 4), math.hypot(160, 135), math.hypot(160, 160))
s = math.hypot(160, 135)
print("rate", 12500/1640, 12500/(1640+s), 12500/(1640-s))
x = np.array([8000, 7000, 6000.0]); y = np.array([8.0, 6.4, 4.9])
b = ((x-x.mean())*(y-y.mean())).sum()/((x-x.mean())**2).sum()
print("slope mm/yr", b*1000, "np.polyfit", np.polyfit(x, y, 1)[0]*1000)

print("== 방법 6: 방사성 붕괴 ==")
for T in (5730, 5568):
    lam = math.log(2)/T
    print(T, lam, [round(math.exp(-lam*t), 5) for t in (12060, 12000, 52000, 11460, 12660)])
lam = math.log(2)/5730
print("age f=0.3:", -math.log(0.3)/lam, "(5568:", -math.log(0.3)/(math.log(2)/5568), ")")
print("pMC 101.38 ->", -math.log(1.0138)/lam)

print("== 방법 7: 스토크스 ==")
rs, rf, g, eta = 2650, 1000, 9.81, 1e-3
for phi in (5, 6, 7, 8):
    d = 2 ** -phi * 1e-3
    v = (rs-rf)*g*d*d/(18*eta)
    print(phi, round(d*1e6, 3), "um", round(v*1e3, 4), "mm/s", round(0.1/v), "s", "Re", rf*v*d/eta)

print("== 방법 8: 인먼 백분위 ==")
p16 = 2+(16-10)/(30-10); p50 = 3+(50-30)/(62-30); p84 = 4+(84-62)/(90-62)
M = (p16+p84)/2; sg = (p84-p16)/2
print(p16, p50, p84, M, sg, (M-p50)/sg)

print("== 동수악 표 1 구간 속도 (14C 연대) ==")
dep = [5, 20, 40, 60, 80, 100, 120, 140, 160, 200]
age = [0, 400, 1400, 1960, 2350, 2660, 3130, 3730, 4080, 4220]
for i in range(1, len(dep)):
    print(dep[i-1], dep[i], round((dep[i]-dep[i-1])*10/(age[i]-age[i-1]), 3))
print("mean 5-140:", 1350/3730, " 20-140:", 1200/3330)
print("t(1) check:", (4273-1910)/144, (4273-10)/144, (4273+40)/144, "years; 1470 mm/0.36 =", 1470/0.36)
print("Nyquist", 2*29, " Welch segment", 2*4263/4)
print("CAR demo", 15/1.25*0.036, " pollen conc demo", 300/150*10000/50)
