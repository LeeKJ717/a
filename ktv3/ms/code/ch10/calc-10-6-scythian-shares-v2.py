# -*- coding: utf-8 -*-
"""계산 10-6. Damgaard 등(2018)이 본문에 적은 스키타이 계열의 조상 성분 비율을 세 가설이 예측하는 모양과 맞댄다.
본문 추출문(Leiden 저장소)의 값: Central Sakas 후기 청동기 목축민 약 56%, 남시베리아 수렵채집민 약 44%. Tagar 83.5%, 7.5%, Mal'ta(MA1)류 9%. Tian Shan Sakas 70%, 25%, 신석기 이란계 5%.
 FST: 헝가리 스키타이와 내륙 아시아 Sakas 사이 0.24~0.3, 내륙 아시아 Sakas 안 0.15~0.2.
세 가설(논문이 소개): (1) 북 카프카스·스텝의 단일 근원, (2) 남시베리아·중앙 아시아 동부의 단일 근원, (3) 여러 지역 기원. 저자들은 (3)을 선호한다고 추출문에 적혀 있다.
오차 구간이 추출문에 없다. '후기 청동기 목축민'이 어느 개체군인지 추출문에서 확인하지 못했다. 아래는 비율의 산술이며 가설의 판정이 아니다.
"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
G = {'Central Sakas': dict(LBA=56.0, SSHG=44.0, other=0.0, other_name='-'),
     'Tagar': dict(LBA=83.5, SSHG=7.5, other=9.0, other_name='Mal\'ta(MA1)류'),
     'Tian Shan Sakas': dict(LBA=70.0, SSHG=25.0, other=5.0, other_name='신석기 이란계')}
out = {}
print('성분 합과 후기 청동기 목축민(LBA) 몫을 뺀 나머지')
for k, v in G.items():
    s = v['LBA'] + v['SSHG'] + v['other']
    non = 100 - v['LBA']
    print('  %-16s 합 %.1f%%, LBA %.1f%%, 남시베리아 수렵채집민 %.1f%%, 기타 %.1f%%(%s) → LBA가 아닌 몫 %.1f%%' % (k, s, v['LBA'], v['SSHG'], v['other'], v['other_name'], non))
    out[k] = dict(sum=s, non_LBA=non)
print('\n(a) 가설 (1) "한 근원(후기 청동기 목축민)이 전부"가 예측하는 LBA 몫은 100%. 관측은 56.0, 83.5, 70.0%이고, 100%에서 모자라는 몫은 44.0, 16.5, 30.0%.')
print('(b) 가설 (2) "남시베리아 계열 한 근원이 전부"가 예측하는 남시베리아 수렵채집민 몫은 100%. 관측은 44.0, 7.5, 25.0%.')
print('    두 단일 근원 모형 모두 세 집단 어디에서도 100%에 못 미친다. 단, 이 성분 이름이 가설 (1), (2)의 "근원"과 같은지는 추출문에서 확인하지 못했다.')
print('(c) LBA 몫의 범위: 56.0~83.5%%, 폭 %.1f%%p. 같은 이름의 문화(스키타이)로 묶이는 집단들 사이에서 성분 비율이 이만큼 다르다.' % (83.5 - 56.0))
lo, hi = 0.24, 0.30
print('(d) FST: 헝가리 스키타이 대 내륙 아시아 Sakas %.2f~%.2f는 내륙 아시아 Sakas 안 0.15~0.20의 %.2f~%.2f배(구간 끝끼리 비교).' % (lo, hi, 0.24 / 0.20, 0.30 / 0.15))
out['fst_ratio'] = [0.24 / 0.20, 0.30 / 0.15]
json.dump(out, open(os.path.join(HERE, 'out', 'calc-10-6.json'), 'w'), ensure_ascii=False, indent=1)
