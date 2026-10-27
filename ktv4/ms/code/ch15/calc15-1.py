# -*- coding: utf-8 -*-
"""계산 15-1: 8장 계산 8-4를 되풀이한다. calc8-4-copy.py 는 ms/code/ch08/calc8-4.py 를 글자 그대로 복사한 것이다.
이 스크립트는 복사본을 실행해 출력을 그대로 보이고, 8장 로그(ms/code/ch08/calc8-4.log)와 한 줄씩 대조한다."""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run([sys.executable, os.path.join(HERE, 'calc8-4-copy.py')], capture_output=True, text=True, check=True).stdout
ref = open(os.path.join(HERE, '..', 'ch08', 'calc8-4.log'), encoding='utf-8').read()
print('=== 계산 15-1: 8장 계산 8-4의 되풀이(복사본 실행 출력) ===')
print(out)
a = out.rstrip('\n').split('\n'); b = ref.rstrip('\n').split('\n')
diff = [i for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
print('=== 8장 로그와의 대조: 출력 %d 줄, 8장 로그 %d 줄, 다른 줄 %d 개 ===' % (len(a), len(b), len(diff)))
assert not diff, '8장 로그와 다르다: %s' % diff[:5]
print('일치한다.')
