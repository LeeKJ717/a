# -*- coding: utf-8 -*-
"""실습 2-8: 제1권 원고에서 '원문 쪽 확인 필요'가 적힌 줄과 표 캡션을 센다. 실행: python3 12-flag-count.py | tee 12-flag-count.log"""
import re
import vol1gt
tot_l = tot_t = 0
for ch, p in sorted(vol1gt.latest().items()):
    t = open(p, encoding='utf-8').read().partition('## 참고문헌')[0]
    lines = [l for l in t.splitlines() if '원문 쪽 확인 필요' in l]
    caps = [l for l in lines if l.startswith('{{T:')]
    scatter = [l for l in t.splitlines() if re.search(r'열이 흩어|흩어져 읽|글자가 흩어', l)]
    if lines or scatter:
        print('%2d장 %-14s 확인 필요 줄 %2d (그중 표 캡션 %d), 열이 흩어졌다는 서술 줄 %d' % (ch, p.split('/')[-1], len(lines), len(caps), len(scatter)))
    tot_l += len(lines); tot_t += len(caps)
print('합계: 줄 %d, 표 캡션 %d' % (tot_l, tot_t))
