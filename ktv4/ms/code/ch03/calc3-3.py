# -*- coding: utf-8 -*-
"""계산 3-3: 논문이 적은 숫자끼리의 산술 점검.
(1) Ruddiman(2003)의 이상 상승 크기(이산화탄소 40 ppm, 메탄 250 ppb, 온난화 0.8 C)가 그 논문이 적은 다른 숫자와 맞물리는가.
(2) Ruddiman 등(2016)이 적은 (탄소량 Gt, 이산화탄소 ppm) 짝에서 '1 ppm 당 탄소 Gt'를 구해, 토지 이용 추정치와 견준다.
모든 입력은 논문이 적은 숫자다. 1 ppm 당 Gt 환산은 이 책의 산술이며 그 논문의 결론이 아니다.
"""
import numpy as np
print('=== 계산 3-3 (1) Ruddiman(2003)의 산술 ===')
lo_now, hi_now = 280, 285      # 산업화 이전 이산화탄소(논문: 280~285 ppm)
lo_nat, hi_nat = 240, 245      # 자연스럽게 내려갔을 값(논문: 240~245 ppm)
print('이상(anomaly) = (최근 값) - (자연 기대값): 최소 %d - %d = %d ppm, 최대 %d - %d = %d ppm, 가운데 %.1f ppm (논문: 약 40 ppm)' % (lo_now, hi_nat, lo_now - hi_nat, hi_now, lo_nat, hi_now - lo_nat, ((lo_now - hi_nat) + (hi_now - lo_nat)) / 2))
print('관측된 상승 20~25 ppm + 자연스러웠다면 내려갔을 몫 = 40 ppm 이면, 내려갔을 몫은 %d~%d ppm (논문: 261 에서 240~245 로 약 16~21 ppm)' % (40 - 25, 40 - 20))
print('261 - 245 = %d, 261 - 240 = %d ppm' % (261 - 245, 261 - 240))
ch4_nat, ch4_obs_rise, ch4_anom = 450, 100, 250
print('메탄: 자연 기대 바닥 %d ppb, 관측 상승 %d ppb, 이상 %d ppb -> 700 - 450 = %d ppb 이고 100 + 150 = %d' % (ch4_nat, ch4_obs_rise, ch4_anom, 700 - 450, 100 + 150))
print('온난화: 메탄 0.25 + 이산화탄소 0.55 = %.2f C (논문: 약 0.8 C). 단위 환산(논문 값의 나눗셈): %.5f C/ppm, %.4f C/ppb' % (0.25 + 0.55, 0.55 / 40, 0.25 / 250))
print('Ruddiman 등(2016)은 같은 이상을 이산화탄소 40 ppm, 메탄 310 ppb 로 적었다. 메탄 값이 250 에서 310 ppb 로 %d ppb(%.0f%%) 늘었다.' % (310 - 250, (310 - 250) / 250 * 100))
print()
print('=== (2) 1 ppm 당 탄소(Gt) ===')
pairs = [('토탄 묻힘 약 300 Gt 가 상쇄하는 이산화탄소 약 21 ppm', 300, 21),
         ('이산화탄소 용해도 되먹임 84 Gt = 약 6 ppm', 84, 6),
         ('남극해 되먹임 71 Gt = 5 ppm', 71, 5),
         ('남극해 되먹임 213 Gt = 15 ppm', 213, 15),
         ('탄소 동위원소가 허용하는 순 육지 방출 약 36 Gt = 약 3 ppm', 36, 3)]
fac = []
for nm, g, p in pairs:
    fac.append(g / p); print('%-62s -> %.1f Gt/ppm' % (nm, g / p))
print('다섯 값의 범위 %.1f~%.1f, 앞 네 값 평균 %.1f Gt/ppm' % (min(fac), max(fac), np.mean(fac[:4])))
f = np.mean(fac[:4])
print('(이 환산 계수는 위 다섯 짝에서만 구했다. 짝들은 바다가 따라 움직인 몫을 이미 품은 값으로 보이지만, 그 해석은 이 책의 것이며 논문에서 확인하지 못했다.)')
print()
print('=== (3) 토지 이용 추정치를 ppm 으로 ===')
est = [('Ruddiman(2003) 이상 40 ppm', None, 40.0),
       ('KK10(Kaplan 등 2011) 산업화 이전 방출 약 340 Gt (Ruddiman 등 2016 표기: 343 Gt)', 343, None),
       ('KK10 총 방출 약 450 Gt (산업화 이전 343 + 산업화 이후 108)', 343 + 108, None),
       ('일정한 1인당 개간 모형(Pongratz, Strassmann, Stocker) 총 약 210 Gt 중 산업화 이전 약 70 Gt', 70, None),
       ('Joos 등(2004) 초기 토지 이용이 더한 몫 4~6 ppm', None, 5.0)]
for nm, g, p in est:
    if g is not None:
        print('%-90s -> %.1f ppm (환산 %.1f Gt/ppm)' % (nm, g / f, f))
    else:
        print('%-90s -> %.0f Gt (환산 %.1f Gt/ppm)' % (nm, p * f, f))
print('KK10 산업화 이전 343 Gt 를 환산하면 %.1f ppm 으로 Ruddiman 의 40 ppm 보다 작고, 40 ppm 을 환산하면 %.0f Gt 로 KK10 의 산업화 이전 방출 343 Gt 의 %.2f 배다.' % (343 / f, 40 * f, 40 * f / 343))
print('일정한 1인당 개간 70 Gt 는 %.1f ppm 이고 Joos 등의 4~6 ppm 과 같은 자릿수다.' % (70 / f))
print('이 환산을 토지 이용 방출에 그대로 쓰는 것은 이 책의 가정이다. 이 가정에서 KK10 의 산업화 이전 방출은 40 ppm 의 약 %.0f%%에 해당한다. 환산 계수가 +-20%% 이면 위 ppm 도 같은 비율로 흔들린다.' % (343 / f / 40 * 100))
