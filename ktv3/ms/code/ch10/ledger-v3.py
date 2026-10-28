# -*- coding: utf-8 -*-
"""10장 주장 장부 v3. out/ledger-v2.json을 읽어 10-7과 10-9의 증거 칸을 Wei 등(2018, 초록)으로 고친다(계산 10-8). 판정과 번호는 바꾸지 않는다.
산출: out/ledger-v3.json. 본문 표(ch10-v3.md 10.9절)와 같은 값이다."""
import json, os
from collections import Counter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
rows = json.load(open(os.path.join(OUT, 'ledger-v2.json'), encoding='utf-8'))
by = {r['no']: r for r in rows}
by['10-7'].update(who='Zerjal 등(2003). 초록과 본문 발췌. 어긋나는 값: Wei 등(2018) 초록',
    test='Zerjal: BATWING 약 1000년 전(700~1300). 1162년은 841년 전으로 구간 안. Wei 등(2018, 초록): 같은 별무리(C3*-별무리에서 C2*-ST로 개명)의 공통 조상 약 2576년 전(1975~3178), 1162년(856년 전)은 구간 밖이고 두 구간은 675년 떨어짐(계산 10-1, 10-8). 두 논문이 어긋나 나란히 둠')
by['10-9'].update(test=by['10-9']['test'].replace('원인이 칭기즈 칸 한 사람인지는', 'Wei 등(2018, 초록): 확산이 몽골어 사용 집단 전체에 맞고 칭기즈 칸과의 직접 증거는 없다고 씀. 원인이 칭기즈 칸 한 사람인지는'))
json.dump(rows, open(os.path.join(OUT, 'ledger-v3.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(rows), '개', dict(Counter(r['verdict'] for r in rows)))
