# -*- coding: utf-8 -*-
"""14장 계산 14-1 ~ 14-6. 입력은 논문이 적은 숫자이고, 가상 값은 '시연값'이다.
실행(작업 폴더 /home/claude/book4): python3 ms/code/ch14/calc14.py > ms/code/ch14/calc14.log
"""
import os, json
import numpy as np
from scipy.stats import binomtest

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}
YEAR = 2026   # 이 책을 쓰는 해. '몇 년 전'은 이 해 기준의 산술이다

print('=== 계산 14-1. 초기 인류 기원 온실기체 가설의 산술(Ruddiman, Kaplan, Elsig의 숫자) ===')
co2_peak, co2_8ka = 268.0, 261.0
pre_lo, pre_hi = 280.0, 285.0
exp_lo, exp_hi = 240.0, 245.0
print('Ruddiman(2003) 초록 쪽: CO2 정점 %.0f ppm(11~10 ka), 8 ka에 %.0f ppm, 산업화 이전 %.0f~%.0f ppm, 이전 간빙기 기준 기대 %.0f~%.0f ppm' % (co2_peak, co2_8ka, pre_lo, pre_hi, exp_lo, exp_hi))
print('  8 ka 이후 관측 증가: %.0f~%.0f ppm (논문 20~25)' % (pre_lo - co2_8ka, pre_hi - co2_8ka))
print('  정점 대비 증가: %.0f~%.0f ppm (논문 약 15)' % (pre_lo - co2_peak, pre_hi - co2_peak))
print('  기대 하락(8 ka → 기대값): %.0f~%.0f ppm' % (co2_8ka - exp_hi, co2_8ka - exp_lo))
print('  이상(관측 - 기대): %.0f~%.0f ppm (논문 약 40)' % (pre_lo - exp_hi, pre_hi - exp_lo))
ch4_obs, ch4_exp = 700.0, 450.0
print('  CH4: 관측 %.0f ppb - 기대 %.0f ppb = %.0f ppb (논문 약 250)' % (ch4_obs, ch4_exp, ch4_obs - ch4_exp))
print('  온도: CH4 0.25 + CO2 0.55 = %.2f ℃ (논문 약 0.8)' % (0.25 + 0.55))
print('  탄소: 산업화 이전 개간 합 약 320 GtC, 2 ka까지 224~249 GtC → 2 ka 이후 몫 %.0f~%.0f GtC' % (320 - 249, 320 - 224))
OUT['ruddiman'] = dict(co2_peak=co2_peak, co2_8ka=co2_8ka, pre=(pre_lo, pre_hi), exp=(exp_lo, exp_hi), ch4=(ch4_obs, ch4_exp))

k_lo, k_hi, k_ppm = 84.0, 102.0, 7.0
print('Kaplan 등(2011): 3 ka까지 누적 %.0f~%.0f Pg = 약 %.0f ppm; 서기 1850년까지 325~357 Pg(새 시나리오) 대 137~189 Pg(HYDE 3.1)' % (k_lo, k_hi, k_ppm))
r_lo, r_hi = k_ppm / k_hi, k_ppm / k_lo
print('  비율 %.4f~%.4f ppm/Pg (= %.1f~%.1f Pg/ppm). 이 비율을 그대로 늘리는 선형 환산(시연값, 바다 완충과 시차를 무시):' % (r_lo, r_hi, 1 / r_hi, 1 / r_lo))
for nm, a, b in (('새 시나리오 325~357 Pg', 325, 357), ('HYDE 3.1 137~189 Pg', 137, 189), ('Ruddiman 320 GtC', 320, 320)):
    print('    %s → %.1f~%.1f ppm' % (nm, a * r_lo, b * r_hi))
OUT['kaplan_lin'] = dict(new=(325 * r_lo, 357 * r_hi), hyde=(137 * r_lo, 189 * r_hi), rud=(320 * r_lo, 320 * r_hi))
print('  1850년까지 새 시나리오 / HYDE: 중앙 %.2f배 (341 / 163)' % (341 / 163))

e_gtc, e_d13c = 290.0, 0.25
print('Elsig 등(2009): 이른 홀로세 δ13C +%.2f ‰ ← 육상 생물권 흡수 약 %.0f GtC. 이후 CO2 +20 ppmv, δ13C -0.05 ‰' % (e_d13c, e_gtc))
per = e_d13c / e_gtc
print('  선형 환산(시연값): %.5f ‰/GtC. 320 GtC → %.3f ‰, 224~249 GtC → %.3f~%.3f ‰. 관측 -0.05 ‰는 그 %.0f%%' % (per, per * 320, per * 224, per * 249, 0.05 / (per * 320) * 100))
print('  (이 환산은 바다와 대기의 교환, 탄산염 보상을 무시한다. 이를 따지는 것이 Elsig 등의 역모형 계산이다. Ruddiman 등(2016)이 이 비교를 다루는 마지막 절의 결론은 이 책이 읽지 못했다)')
OUT['elsig_lin'] = dict(per=per, v320=per * 320, v224=per * 224, v249=per * 249)

print()
print('=== 계산 14-2. ArchaeoGLOBE와 HYDE의 비교: 숫자의 산술과 부호 검정 ===')
resp, assess, regions = 255, 711, 146
print('응답자 %d명, 평가 %d건, 지역 %d개 → 응답자당 %.2f건, 지역당 %.2f건' % (resp, assess, regions, assess / resp, assess / regions))
i6, i2 = 12, 65
print('집약 농업이 흔한 지역: 6 ka %d개(%.1f%%), 2 ka %d개(%.1f%%), 배수 %.1f' % (i6, i6 / regions * 100, i2, i2 / regions * 100, i2 / i6))
ea3, pa3 = 75, 64
print('3 ka: 조방 농업이 흔한 지역 %d개(%.1f%%), 목축이 흔한 지역 %d개(%.1f%%)' % (ea3, ea3 / regions * 100, pa3, pa3 / regions * 100))
hyde_n, earlier, early1000, late1000 = 130, 69, 27, 13
print('HYDE 비교: 농업 지역 %d개 중 고고 시작이 더 이른 곳 %d개(%.1f%%), 그중 1,000년 넘게 이른 곳 %d개(%.1f%% of 이른 곳), 1,000년 넘게 늦은 곳 %d개' % (hyde_n, earlier, earlier / hyde_n * 100, early1000, early1000 / earlier * 100, late1000))
n = early1000 + late1000
bt = binomtest(early1000, n, 0.5)
print('  부호 검정: 1,000년 넘게 이른 %d대 늦은 %d (n=%d), 균등(0.5) 기준 양측 p = %.4f, 이른 쪽 비율 %.1f%%' % (early1000, late1000, n, bt.pvalue, early1000 / n * 100))
ci = bt.proportion_ci(confidence_level=0.95)
print('  이른 쪽 비율의 95%% 신뢰구간(정확 이항): %.2f~%.2f' % (ci.low, ci.high))
print('  남는 지역: %d - %d - %d = %d개는 두 범주 밖이다. 그중 HYDE보다 이르되 1,000년 이내인 곳이 %d - %d = %d개이고 나머지 %d개는 같거나 늦되 1,000년 이내 등이다(분해는 이 책이 확인하지 못함). 부호 검정은 이들을 버린다' % (hyde_n, early1000, late1000, hyde_n - early1000 - late1000, earlier, early1000, earlier - early1000, hyde_n - early1000 - late1000 - (earlier - early1000)))
print('  (응답자가 토지 이용을 과대 평가했을 수 있다는 저자들의 경고는 이 부호 검정이 시험하는 방향과 같은 방향의 편향이다)')
OUT['archaeoglobe'] = dict(i6=i6, i2=i2, regions=regions, earlier=earlier, e1000=early1000, l1000=late1000, hyde_n=hyde_n, p=bt.pvalue)
fa = (40, 63, 73)
print('수렵채집이 "흔함" 아래로 내려간 지역 비율: 8 ka %d%%, 3 ka %d%%, 서기 1850 %d%%' % fa)
print('Ellis 등(2021): 12,000년 전 육지의 거의 75%, 온대 삼림 95% 이상, 열대 삼림 90%. ArchaeoGLOBE는 10 ka부터 평가: 시작점이 2 ka 다르고 "거주하며 영향"(Ellis)과 "토지 이용 유형"(ArchaeoGLOBE)의 정의도 다르다.')

print()
print('=== 계산 14-3. 폴리네시아 정착 연대와 보정 곡선(IntCal20, SHCal20) ===')
print('Wilmshurst 등(2011): 날짜 1,434개, 두 단계: 소사이어티 제도 서기 1025~1120, 나머지 섬 1190~1290. 사이 간격 %d~%d년 (논문 70~265)' % (1190 - 1120, 1290 - 1025))
print('  Wilmshurst 등(2008): 쥐의 뉴질랜드 도착 약 서기 1280. 이전 제안 기원전 200~서기 1000 → 차이 %d~%d년' % (1280 - 1000, 1280 + 200))
def load(f):
    c = np.loadtxt(os.path.join(HERE, 'data', f), delimiter=',')
    c = c[np.argsort(c[:, 0])]
    return c[:, 0], c[:, 1], c[:, 2]
NH, SH = load('intcal20.14c'), load('shcal20.14c')
tg = np.arange(0, 1500)
def c14_at(curve, ad):
    return np.interp(1950 - ad, curve[0], curve[1]), np.interp(1950 - ad, curve[0], curve[2])
def cal_range(curve, c, e, lvl=0.954):
    mu = np.interp(tg, curve[0], curve[1]); sg = np.interp(tg, curve[0], curve[2])
    s2 = e ** 2 + sg ** 2
    p = np.exp(-0.5 * (c - mu) ** 2 / s2) / np.sqrt(s2); p /= p.sum()
    o = np.argsort(-p); cum = np.cumsum(p[o]); sel = np.sort(tg[o[cum <= lvl]])
    if sel.size == 0:
        sel = np.array([tg[o[0]]])
    return 1950 - sel.max(), 1950 - sel.min()
print('같은 달력 연도에서 두 곡선의 방사성탄소 연대 차(SHCal20 - IntCal20, 14C 연):')
diffs = []
for ad in range(1000, 1301, 25):
    a = c14_at(NH, ad)[0]; b = c14_at(SH, ad)[0]
    diffs.append(b - a)
    print('  서기 %d: 북 %.0f, 남 %.0f, 차 %.0f' % (ad, a, b, b - a))
print('  서기 1000~1300 평균 차 %.1f년 (최소 %.0f, 최대 %.0f)' % (np.mean(diffs), min(diffs), max(diffs)))
print('가상 방사성탄소 연대 ±30(시연값)를 두 곡선으로 보정한 95.4% 범위:')
rows = []
for c in (950, 900, 850, 800, 750, 700):
    a = cal_range(NH, c, 30); b = cal_range(SH, c, 30)
    rows.append((c, a, b))
    print('  %d ± 30 BP: IntCal20 서기 %d~%d(%d년폭), SHCal20 서기 %d~%d(%d년폭), 범위 가운데 차 %.0f년' % (c, a[0], a[1], a[1] - a[0], b[0], b[1], b[1] - b[0], (b[0] + b[1]) / 2 - (a[0] + a[1]) / 2))
OUT['calib'] = rows
print('속에 든 나이(old wood) 시연: 실제 달력 연도 서기 1250에 죽은 식물의 방사성탄소 연대에 속 나이를 더하면 SHCal20 보정이 얼마나 이른 쪽으로 가는가')
c0 = c14_at(SH, 1250)[0]
base = cal_range(SH, c0, 30)
print('  속 나이 0: 14C %.0f BP → 서기 %d~%d(가운데 %.0f)' % (c0, base[0], base[1], (base[0] + base[1]) / 2))
shift = []
for age in (50, 100, 200, 300):
    r = cal_range(SH, c0 + age, 30)
    shift.append((age, (r[0] + r[1]) / 2 - (base[0] + base[1]) / 2))
    print('  속 나이 %d년: 14C %.0f BP → 서기 %d~%d(가운데 %.0f), 가운데가 %.0f년 이르다' % (age, c0 + age, r[0], r[1], (r[0] + r[1]) / 2, (base[0] + base[1]) / 2 - (r[0] + r[1]) / 2))
OUT['oldwood'] = shift
ov = lambda a, b: max(0, min(a[1], b[1]) - max(a[0], b[0]))
print('창 겹침: 두 번째 단계(1190~1290)와 남반구가 북반구보다 따뜻했던 때(1280~1350, Neukom 등 2014) 겹침 %d년, 소빙기 급한 시작(1275~1300, Miller 등 2012)과 %d년, 첫 단계(1025~1120)와 같은 때 %d년' % (ov((1190, 1290), (1280, 1350)), ov((1190, 1290), (1275, 1300)), ov((1025, 1120), (1280, 1350))))
print('  쥐 도착 약 1280은 위 세 창 가운데 (1190~1290)과 (1280~1350)과 (1275~1300) 모두 안에 든다')
OUT['poly'] = dict(w1=(1025, 1120), w2=(1190, 1290), rat=1280, shwarm=(1280, 1350), miller=(1275, 1300), earlier=(-200, 1000))

print()
print('=== 계산 14-4. 기후와 사회 사건의 우연한 일치(Kennett 등 2012의 창으로 눈금 잡기) ===')
rec = 2000.0
wet = (440, 660); dry = [(660, 1000), (1020, 1100)]
lens = [b - a for a, b in dry]
f_dry = sum(lens) / rec
print('Kennett 등(2012): 기록 약 %d년. 습함 %d~%d(%d년, %.1f%%), 건조 경향 660~1000(%d년), 가뭄 1020~1100(%d년). 건조 합 %d년 = 기록의 %.1f%%' % (rec, wet[0], wet[1], wet[1] - wet[0], (wet[1] - wet[0]) / rec * 100, lens[0], lens[1], sum(lens), f_dry * 100))
print('  습함과 건조 창을 모두 합치면 %d년 = %.1f%%' % (sum(lens) + wet[1] - wet[0], (sum(lens) + wet[1] - wet[0]) / rec * 100))
print('독립인 사회 사건 K개를 무작위로 놓을 때 적어도 하나가 건조 창(%.1f%%)에 드는 확률 1-(1-f)^K:' % (f_dry * 100))
inflate = []
for K in (1, 2, 3, 5, 10, 20):
    pr = 1 - (1 - f_dry) ** K
    inflate.append((K, pr))
    print('  K=%2d: %.1f%%   (모두 K개가 든 확률 f^K = %.4f%%)' % (K, pr * 100, f_dry ** K * 100))
OUT['inflate'] = inflate; OUT['f_dry'] = f_dry
def union_len(iv):
    iv = sorted(iv); tot = 0; cur = None
    for a, b in iv:
        if cur is None: cur = [a, b]
        elif a <= cur[1]: cur[1] = max(cur[1], b)
        else:
            tot += cur[1] - cur[0]; cur = [a, b]
    if cur: tot += cur[1] - cur[0]
    return tot
print('사건 날짜에 ±U년의 오차가 있을 때 오차 범위가 건조 창과 조금이라도 겹칠 확률(창을 양쪽으로 U만큼 넓힌 합집합):')
dil = []
for U in (0, 10, 25, 50, 100, 200):
    L = union_len([(a - U, b + U) for a, b in dry])
    dil.append((U, L / rec))
    print('  ±%3d년: 합집합 %d년 = %.1f%%' % (U, L, L / rec * 100))
OUT['dilate'] = dil
print('Medina-Elizalde와 Rohling(2012): 마야 해체 약 200년 사이에 연 강수량 최대 40%% 감소(네 기록의 정량 분석). Kennett 등의 건조 경향 660~1000은 %d년, 논문의 약 200년과 %.1f배 차이(구간이 같은 때를 가리키는지 이 책은 확인하지 못함)' % (lens[0], lens[0] / 200))
print('Buckley 등(2010): 앙코르, 14~15세기(서기 1300~1499로 이 책이 환산 = 200년), 나이테 기록 약 750년 → 창이 기록에서 차지하는 비율 %.1f%%(기록의 정확한 연대 범위는 확인하지 못해 비율만 산술)' % (200 / 750 * 100))
print('Degroot 등(2021): 저자 19명, 인구가 기후 압력을 견딘 다섯 경로(초록)')
print('Zhang 등(2007): 저자 5명, 초록에 수치 없음(PNAS 104(49):19214-19219)')

print()
print('=== 계산 14-5. 인류세 시점 후보와 투표의 산술 ===')
cands = [
    ('초기 농경 영향(Ruddiman)', '약 8 ka(BP, 기원전 약 6050)', 8000 + (YEAR - 1950)),
    ('토지 변형 시작(Ellis 등)', '약 12,000년 전', 12000),
    ('Orbis 급락(보도 자료가 소개한 Nature 연구)', '서기 1610', YEAR - 1610),
    ('산업화 시작(서기 1850 즈음)', '서기 1850', YEAR - 1850),
    ('인류세 실무단 제안 기준선', '서기 1952', YEAR - 1952),
    ('같은 연구의 대안', '서기 1964', YEAR - 1964),
]
print('기준 연도 %d. 후보까지 몇 년 전인가(산술):' % YEAR)
for nm, lab, y in cands:
    print('  %s, %s: %d년 전' % (nm, lab, y))
OUT['cands'] = [(c[0], c[1], c[2]) for c in cands]
print('후보 사이의 간격: 8 ka와 Orbis %d년, Orbis와 1952 %d년, 1952와 1964 %d년, 8 ka와 1952 %d년' % (cands[0][2] - cands[2][2], cands[2][2] - cands[4][2], cands[4][2] - cands[5][2], cands[0][2] - cands[4][2]))
print('가장 이른 후보와 가장 늦은 후보의 비 %.0f배' % (cands[0][2] / cands[5][2]))
tot, voted, yes, no, quorum = 34, 33, 29, 4, 21
print('실무단 투표(2019년 5월): 투표권자 %d명 중 %d명 투표(%.1f%%), 정족수 %d(%.1f%%), 찬성 %d(%.1f%%), 반대 %d, 합 %d' % (tot, voted, voted / tot * 100, quorum, quorum / tot * 100, yes, yes / voted * 100, no, yes + no))
print('  60%% 초다수에 필요한 찬성 수: 투표 %d명의 60%% = %.1f → %d명 이상. 찬성 %d는 여유 %d명' % (voted, voted * 0.6, int(np.ceil(voted * 0.6)), yes, yes - int(np.ceil(voted * 0.6))))
print('IUGS 성명(2024-03-26): 국제층서위원회를 대신해 제4기층서소위원회의 부결 표결을 승인. 소위 표결 수치는 이 책이 확인하지 못함')
print('동시성 점검(ArchaeoGLOBE 숫자): 집약 농업이 흔한 지역이 6 ka에 %.1f%%, 2 ka에도 %.1f%% → 지구 전체에서 같은 해에 나타난 층서 표지가 아니다' % (i6 / regions * 100, i2 / regions * 100))

print()
print('=== 계산 14-6. 작물 길들이기의 시간 눈금(Fuller 등 2014의 본문 숫자) ===')
print('비탈락 이삭 길들이기에 걸린 시간 적어도 2,000~2,500년')
print('  중국 기장: 이용 9.5 ka, 뚜렷한 재배 8.0 ka, 정착 농경 6.5 ka (BP). 구간 %.1f천 년, %.1f천 년, 합 %.1f천 년' % (9.5 - 8.0, 8.0 - 6.5, 9.5 - 6.5))
print('  진주기장: 비탈락형이 4 ka까지 우세 → 길들이기 사건은 적어도 1,000~2,000년 이전')
print('  수수: 야생 이용 10~5.5 ka(%.1f천 년), 길들이기는 6~4 ka 사이' % (10 - 5.5))
print('  옥수수: 비탈락 식물규소체 8.7 ka(발사스). 나투프 문화 정주 약 13.5 ka. 뉴기니 덩이줄기 7.0~6.4 ka, 집약화 5.0~3.5 ka')
print('  종자 크기 증가: 20~60%%가 흔함. 보리기장 20%%에 2,000~3,000년 → %.4f~%.4f %%/년' % (20 / 3000, 20 / 2000))
print('  나투프 13.5 ka에서 중국 기장 재배 8.0 ka까지 %.1f천 년, 뉴기니 덩이줄기 6.4 ka까지 %.1f천 년(서로 다른 종류의 증거이다)' % (13.5 - 8.0, 13.5 - 6.4))
print('  비탈락에 필요한 시간 2,000~2,500년을 방사성탄소 연대 오차 ±100년과 견주면 오차가 시간의 %.1f~%.1f%%' % (100 / 2500 * 100, 100 / 2000 * 100))
OUT['dom'] = dict(millet=(9.5, 8.0, 6.5))

json.dump(OUT, open(os.path.join(HERE, 'calc14-out.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
