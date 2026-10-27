# -*- coding: utf-8 -*-
"""계산 15-6: 대조 사례. 같은 "정의 의존성"이 8.2 ka 사건에서도 나타나는가.
calc2-3-copy.py 는 ms/code/ch02/calc2-3.py(2장 계산 2-3, GISP2 δ18O에서 8.2 ka 사건을 다시 찾음)를 글자 그대로 복사한 것이고, io2.py 와 GISP2 csv 도 2장 폴더의 사본이다.
복사본을 실행해 2장 로그와 대조하고, 사건 길이가 기준에 달린 정도를 4.2 ka 창의 길이 비(계산 15-1)와 나란히 놓는다.
7장 계산 7-5(탐지 규칙의 거짓 경보율)의 숫자는 7장 로그에서 옮겨 적기만 한다(이 폴더에서 다시 돌리지 않았다)."""
import subprocess, sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run([sys.executable, os.path.join(HERE, 'calc2-3-copy.py')], capture_output=True, text=True, check=True, cwd=HERE).stdout
ref = open(os.path.join(HERE, '..', 'ch02', 'calc2-3.log'), encoding='utf-8').read()
print('=== 계산 15-6 (1) 2장 계산 2-3의 되풀이(복사본 실행 출력) ===')
print(out)
a = out.rstrip('\n').split('\n'); b = ref.rstrip('\n').split('\n')
diff = [i for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
print('=== 2장 로그와의 대조: 출력 %d 줄, 2장 로그 %d 줄, 다른 줄 %d 개 ===' % (len(a), len(b), len(diff)))
assert not diff, '2장 로그와 다르다'
print('일치한다.')
print()
print('=== 계산 15-6 (2) 사건 길이가 정의에 달린 정도 ===')
lens = [int(x) for x in re.findall(r'k=(?:1\.0|1\.5|2\.0|3\.0) .*?길이 (\d+) 년', out)]
print('  8.2 ka (GISP2, 기준 k = 1.0, 1.5, 2.0, 3.0 표준편차): 길이', lens, '년. 최대 대 최소 = %.2f 배' % (max(lens) / min(lens)))
print('  8.2 ka 논문 값: Rasmussen 등(2007) 160 ± 10 년, Thomas 등(2007) 160.5 년(2장 로그)')
print('  4.2 ka (계산 15-1, 8장): 창 길이 200~500 년. 최대 대 최소 = %.2f 배' % (500 / 200))
print('  두 사건 모두 "길이"는 정의에 따라 2배 안팎으로 바뀐다. 8.2 ka 는 한 자료(GISP2) 안에서 기준만 바꾼 것이고, 4.2 ka 는 서로 다른 논문의 정의를 나란히 놓은 것이다.')
print()
print('=== 계산 15-6 (3) 7장 계산 7-5 로그에서 옮긴 숫자(여기서 다시 돌리지 않음) ===')
ref7 = open(os.path.join(HERE, '..', 'ch07', 'calc7-5.log'), encoding='utf-8').read()
for ln in ref7.split('\n')[:6]: print('  ' + ln)
