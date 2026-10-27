# -*- coding: utf-8 -*-
"""10장 주장 장부 v2. out/ledger.json(v1의 산출)을 읽어 새로 읽은 근거로 고친 행과 새 행(10-24~10-27)을 더해 out/ledger-v2.json, out/ledger-table-v2.md 를 만든다.
번호 10-1~10-23은 바꾸지 않는다(v1과 같은 번호). 판정 다섯 등급: 지지 / 부분 지지 / 반증 / 시험 불가 / 근거 확인 필요."""
import json, os
from collections import Counter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
rows = json.load(open(os.path.join(OUT, 'ledger.json'), encoding='utf-8'))
by = {r['no']: r for r in rows}
def upd(no, **kw):
    assert no in by, no
    by[no].update(kw)
VERD = ['지지', '부분 지지', '반증', '시험 불가', '근거 확인 필요']
upd('10-10', who='구전과 영묘 이름. Golden Horde 엘리트 프리프린트(bioRxiv 2025)와 Askapuli 등(2026) 프리프린트가 시험. 본문 추출문 수준',
    test='Jochi 사망은 1227년(역사 연대기). CKZ002는 14세기 CE(보정 구간 미확인), 간격 74~173년. 영묘 목재 1298~1398 CE, 관 목재 약 1245 CE(계산 10-5). Y는 C3*(F1918) 세 남성. 저자들은 정체를 미결로 결론',
    verdict='근거 확인 필요')
upd('10-11', who='구전. Golden Horde 엘리트 프리프린트(본문 추출문)가 시험', test='1·2촌 관계 없음. CKZ004는 남성들과 공유 구간이 없고 CKZ002의 딸이 아니라고 저자들이 씀. 부녀라면 공유 길이의 기대치가 약 3500 cM(계산 10-4)')
upd('10-12', who='구전. Golden Horde 엘리트 프리프린트(본문 추출문)의 가설', test='주성분·f 통계에서 고대 북동아시아 성분이 주 성분, 몽골 고원 조상을 "강하게 시사"한다고 저자들이 씀. 숫자(그림 값)는 읽지 못함')
upd('10-13', test='변이 분할(본문 추출문): 주즈 사이 8.91%, 주즈 안 부족 사이 19.68%, 부족 안 71.40%. 저자들은 주즈 구분이 "사회·영토적이라기보다 관습적"이라고 씀. ΦST가 본문과 표에서 다름(계산 10-7)')
upd('10-14', who='Blaramberg(1848)의 서술을 Zhunussova 등(2025)이 전함(본문의 인용). 인용된 서술은 10.6.2절', test='네 씨족의 우세 하플로그룹이 서로 다르고(J2a2, C2a1a3, N1a2, R1a1a), 부족 수준 최다는 14%(계산 10-3). 씨족 사이 FST 0.29. 저자는 "공통 부계 기원"이 확인을 요한다고도 적음')
upd('10-15', who='Tevkelev(1748)의 서술을 Zhunussova 등(2025)이 Erofeeva(2005)를 인용해 전함', test='독립 창시 계통이라는 예측과 맞음. 저자들은 주요 군집이 최소 1000년간 안정적이라고 적음(rho 통계, 돌연변이율 2.1×10^-3, 세대 30년). 17세기 연합의 시기는 시험하지 못함. Y 염색체만의 결과')
upd('10-16', who='Abilev 등(2012)이 적은 계보 기록(초록: 두 하위 씨족의 분기는 역사 자료로 20~22세대)', test='별무리 76.5%. 두 하위 군집이 DYS448에서만 다르고 하위 씨족과 일치(초록). 기대 돌연변이 1.4~1.6개 대 관측 1자리(계산 10-2)')
upd('10-18', who='카자흐 전통 계보. Zhabagin 등(2021, J Hum Genet)이 시험. 이 책은 보도 자료와 위키백과의 서지만 읽음(2차)', test='두 씨족은 공통 조상을 공유하고 Jetiru 씨족은 아니다. TMRCA 700 ± 200(STR), 500 ± 200(염기서열) 모두 650년을 포함(계산 10-2). 별도 논문 Genes 2022 초록: C2a1a2가 Alimuly 67%, Baiuly 74.6%, Zhetiru 25.8%')
upd('10-23', who='Golden Horde 엘리트 프리프린트가 적은 표준형', test='프리프린트는 Töre의 Y 자료가 없어 시험하지 못했다고 씀. Khussainova 등(2022)의 Tore는 6명이고 N-M231 1명(16.7%) 외 분포를 읽지 못함', verdict='근거 확인 필요')
upd('10-19', who='Zhabagin, Sabitov, Agdzhoyan 외의 Argyn 연구(출판 연도 확인 필요). 재게시된 웹 페이지(2차). 위키백과 표(2차)와 대조', test='재게시 페이지는 G1-M285가 약 67%이고 아홉 씨족 모두에서 나타난다고 적음. 위키백과 표는 머리글이 깨져 있으나 값을 순서대로 맞추면 Argyn의 G1-M285는 4(N=45)이고 67(N=384)은 다른 열에 놓임(표 읽기는 이 책의 추정). 두 서술이 어긋나며 논문 미독. Wang 등(2023)은 Argyn을 다루지 않음', verdict='근거 확인 필요')
new = [
 ('카자흐 씨족', 'Xinjiang의 Altay·Ili 카자흐는 Kerey 씨족의 18세기 이주·확장의 후손이다', 'Wang 등(2023)이 인용한 역사 서술(1757년 Ablai Sultan, Perdue 2005를 인용한 문장. 추출문은 문장이 끊겨 서술의 나머지를 읽지 못함)', 'DYS448-23 하위 군집 TMRCA 289.4 ± 202.65년(ASD, 세대 25년) → 달력 1734년(1531~1936). 1757년은 구간 안(계산 10-7). 같은 논문의 몫 숫자가 서로 어긋남', '부분 지지'),
 ('고대 유전체', '스키타이는 한 지역(북 카프카스·스텝 또는 남시베리아·중앙 아시아 동부)의 단일 근원에서 나왔다', 'Damgaard 등(2018)이 소개한 세 모형 중 둘(학계 가설이며 사료의 서술이 아님)', 'Central Sakas 56/44%, Tagar 83.5/7.5/9%, Tian Shan Sakas 70/25/5%(계산 10-6). 저자들은 여러 지역 기원을 선호. 성분 이름이 가설의 근원과 같은지 미확인', '근거 확인 필요'),
 ('집사', '칭기즈 칸은 파란 눈에 숱 많은 수염을 가졌다', '『집사』(Rashid al-Din). 원전 미독. 프리프린트 저자들의 문장이 인용한 서술(주석 13번)', '칭기즈 칸의 유골이 없어 시험할 시료가 없다', '시험 불가'),
 ('칭기즈 Y', '칭기즈계(황금 씨족) 남성의 Y는 C3*(C2a1a3-F1918)이다', 'Zerjal 등(2003) 이래의 가설. Golden Horde 엘리트 프리프린트가 시험(R1b는 Sukhbaatar 엘리트 묘의 보고로 인용됨)', 'Ulitau 세 남성이 모두 C3*이며 서로 부계 친족(Kenggir 계통). 한 부계 줄기의 세 개체이고 Töre 표준형은 시험 못 함. 저자들은 단정하지 않음', '부분 지지'),
]
for g, claim, who, test, v in new:
    assert v in VERD
    n = len(rows) + 1
    r = dict(no='10-%d' % n, group=g, claim=claim, who=who, test=test, verdict=v)
    rows.append(r)
for r in rows: assert r['verdict'] in VERD
json.dump(rows, open(os.path.join(OUT, 'ledger-v2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
md = ['| 번호 | 주장 | 주장한 곳과 읽은 수준 | 시험 방법과 읽은 증거 | 판정 |', '|---|---|---|---|---|']
for r in rows: md.append('| %s | %s | %s | %s | **%s** |' % (r['no'], r['claim'], r['who'], r['test'], r['verdict']))
open(os.path.join(OUT, 'ledger-table-v2.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
c = Counter(r['verdict'] for r in rows)
print('주장 %d개' % len(rows))
for v in VERD: print('  %-8s %d' % (v, c.get(v, 0)))
print(dict(Counter(r['group'] for r in rows)))
