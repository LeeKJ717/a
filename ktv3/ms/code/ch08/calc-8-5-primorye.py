# -*- coding: utf-8 -*-
"""계산 8-5. 연해주(Primorye) 기장의 시작: 같은 편집 서문(Leipe 등 2022)이 요약한 두 논문의 서술을 달력 연대로 옮겨 간격을 잰다.
입력(서문의 요약, 2차): Sergusheva 등(2022) 방사성탄소 27개가 기장을 기원전 3천년기 초로 놓고, 4천년기 후반(기원전 3500~3000년)은 확인되지 않았다.
                        Lyashchevskaya 등(2022) 기장 농경 약 6000~3600 cal yr BP, 약 4000 cal yr BP부터 집약.
읽는 법(시연값, 이 책의 해석): '기원전 3천년기 초'를 기원전 3000~2700년으로 둔다. 서문에 정확한 구간이 없다. BC = cal BP - 1949.
"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
def bc2cal(bc): return bc + 1949
A = dict(early3_bc=(3000, 2700), late4_bc=(3500, 3000))
L = (6000, 3600)
out = {}
for k, (hi, lo) in A.items():
    ch, cl = bc2cal(hi), bc2cal(lo)           # cal BP, ch 가 오래된 쪽
    gap_min, gap_max = L[0] - ch, L[0] - cl    # Lyashchevskaya 시작이 몇 년 더 오래되었나
    out[k] = dict(cal_BP=[ch, cl], gap_years=[gap_min, gap_max])
    print('%s: 기원전 %d~%d년 = %d~%d cal BP. Lyashchevskaya 시작 %d cal BP(기원전 %d년)보다 %d~%d년 젊다' % (k, hi, lo, ch, cl, L[0], L[0] - 1949, gap_min, gap_max))
print('Lyashchevskaya 구간 6000~3600 cal BP = 기원전 %d~%d년, 폭 %d년' % (L[0] - 1949, L[1] - 1949, L[0] - L[1]))
print('집약 시작 4000 cal BP = 기원전 %d년. 4200 cal BP와 200년 차이' % (4000 - 1949))
json.dump(out, open(os.path.join(HERE, 'calc-8-5-primorye.json'), 'w'), ensure_ascii=False, indent=1)
