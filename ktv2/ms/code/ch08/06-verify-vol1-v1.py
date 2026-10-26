# -*- coding: utf-8 -*-
"""실습 8-6: 이 장(sedkit)의 계산이 제1권의 계산과 같은 값을 내는가를 줄 단위로 대조한다.
제1권의 계산 스크립트(ch08-calc-v1.py, ch10-calc-v1.py)를 읽기 전용으로 실행해 출력을 받고(python3 -I, 파일 쓰기 없음),
이 폴더의 02-cia.log, 03-mixing.log, 05-flux.log 에서 같은 양을 꺼내 숫자를 비교한다.
각 검사 = (이름, 제1권 출력에서 뽑을 정규식, 이 장 로그에서 뽑을 정규식, 비교 자릿수). 정규식의 모든 그룹을 실수로 바꿔 같은지 본다.
이 검사는 '같은 입력에서 같은 식을 쓰면 같은 값이 나온다'만 확인한다. 입력의 옮김 자체가 맞는지는 01-extract-inputs 가 소스에서 직접 뽑아 보장한다."""
import os, re, subprocess, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
V1 = '/home/claude/book/ms'

def run(script):
    p = os.path.join(V1, script)
    print('%s sha256 %s' % (script, hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]))
    r = subprocess.run([sys.executable, '-I', p], capture_output=True, text=True, cwd='/tmp')
    if r.returncode != 0:
        print(r.stderr[-500:]); sys.exit(2)
    return r.stdout

v10 = run('ch10-calc-v1.py')
v08 = run('ch08-calc-v1.py')
M = {k: open(os.path.join(HERE, f), encoding='utf-8').read() for k, f in (('cia', '02-cia.log'), ('mix', '03-mixing.log'), ('flux', '05-flux.log'))}
V = {'c10': v10, 'c08': v08}

def nums(text, rx, flags=0):
    m = re.search(rx, text, flags)
    if not m:
        return None
    return [float(g) for g in m.groups()]

def allnums(text, rx):
    return [float(x) for x in re.findall(rx, text)]

CH = []
def chk(name, a, b, nd):
    ok = a is not None and b is not None and len(a) == len(b) and all(abs(round(x, nd) - round(y, nd)) < 10 ** (-nd) * 0.51 for x, y in zip(a, b))
    CH.append(ok)
    print('%-52s 제1권 %-34s 이 장 %-34s %s' % (name, a if a is None else ' '.join('%g' % x for x in a)[:34], b if b is None else ' '.join('%g' % x for x in b)[:34], '일치' if ok else '불일치'))

# --- Brune
chk('Brune TE 8줄(계산 10-1)', allnums(v10, r'TE = ([\d.]+) % \(표'), [float(x) for x in re.search(r'이 책 계산:\s+([\d. ]+?)\s+일치', M['flux']).group(1).split()], 2)
chk('Brune 시연 V=2, 8 (10.10.1)', [64.64, 82.32], nums(M['flux'], r'TE = ([\d.]+) %, ([\d.]+) % \(제1권'), 2)
# --- 수지
chk('최대 차이(촌탄-병산)', nums(v10, r'촌탄-병산: .*?\n(?:.*\n){8}\s+최대 차이 (\d+)'), nums(M['flux'], r'표 61 49 56 15 23 53 43 28\s+최대 차이 (\d+)'), 0)
chk('최대 차이(의창-촌탄)', nums(v10, r'의창-촌탄: .*?\n(?:.*\n){8}\s+최대 차이 (\d+)'), nums(M['flux'], r'표 133 127 175 105 176 189 151 -1\s+최대 차이 (\d+)'), 0)
chk('TGD 퇴적 D1,D2,D3 = 15, 152, 167', nums(v10, r'촌탄-병산 \d+-\d+ = (\d+), 의창-촌탄 [\d-]+-\(-?\d+\) = (\d+), 의창-병산 \d+-\d+ = (\d+)'), nums(M['flux'], r'D1 (\d+), D2 (\d+), D3 (\d+) \(표'), 0)
chk('하상 침식 3/31', nums(v10, r'= 3/31 = ' ) or nums(v10, r'3/31 = ([\d.]+) Mt/km/yr'), nums(M['flux'], r'= ([\d.]+) Mt/km/yr;'), 3)
chk('하류 구간·상류 비율(91.2, 8.8)', nums(v10, r'\(152 \+ 4\.4\)/\(167 \+ 4\.4\) = ([\d.]+) %, 상류 15/171\.4 = ([\d.]+) %'), nums(M['flux'], r'= ([\d.]+) %, 상류 15/171\.4 = ([\d.]+) %'), 1)
chk('포획 효율 172/228, 167.4/228.4', nums(v10, r'172/228 = ([\d.]+) %.*?167\.4/228\.4 = ([\d.]+) %'), nums(M['flux'], r'172/228 = ([\d.]+) % \(논문 75\) ; 167\.4/228\.4 = ([\d.]+) %'), 1)
chk('회귀 평균 228.4, 61.0, 167.4(계산 10-3)', nums(v10, r'추정 평균 ([\d.]+) \(본문 228\), 실측 평균 ([\d.]+) \(본문 61\), 차 평균 ([\d.]+)'), nums(M['flux'], r'평균: 추정 ([\d.]+), 실측 ([\d.]+), 차 ([\d.]+)'), 1)
chk('회귀 최대·최소 214.6, 102.6', nums(v10, r'최대 ([\d.]+) \(2008, 본문 215\), 최소 ([\d.]+)'), nums(M['flux'], r'최대 ([\d.]+) \(2008\), 최소 ([\d.]+) \(2006\)'), 1)
chk('유출 깊이 7곳(계산 10-5)', allnums(v10, r'유출 깊이 (\d+) mm/yr'), [float(x) for x in re.findall(r'^\s+\S+\s+[\d.]+\s+\d+\s+\d+\s+(\d+)\s+\d+\s*$', M['flux'], re.M)], 0)
chk('유사 수율 7곳(계산 10-5)', allnums(v10, r'수율 (\d+) t/km2/yr'), [float(x) for x in re.findall(r'^\s+\S+\s+[\d.]+\s+\d+\s+\d+\s+\d+\s+(\d+)\s*$', M['flux'], re.M)], 0)
# --- CIA
chk('CIA 0.1 이하 개수·초과 개수', nums(v10, r'차이 0\.1 이하 (\d+)개, 초과 (\d+)개'), nums(M['cia'], r'차이 0\.1 이하 (\d+)개, 초과 (\d+)개'), 0)
chk('CIA 불일치 3개(원강, 상강, 감강)', nums(v10, r'원강 ([+-][\d.]+), 상강 ([+-][\d.]+), 감강 ([+-][\d.]+)'), nums(M['cia'], r'원강 ([+-][\d.]+), 상강 ([+-][\d.]+), 감강 ([+-][\d.]+)'), 2)
chk('CIA(표) 평균·최소·최대', nums(v10, r'CIA\(표\) 평균 ([\d.]+), 최소 ([\d.]+) \(대도하\), 최대 ([\d.]+)'), nums(M['cia'], r'표 평균 ([\d.]+), 최소 ([\d.]+) \(대도하\), 최대 ([\d.]+)'), 2)
chk('규칙 A~D 대체 규칙 상강(표, A, B, C, D)', nums(v10, r'상강\s+표 ([\d.]+) \| A ([\d.]+) \| B ([\d.]+) \| C ([\d.]+) \| D ([\d.]+)'), nums(M['cia'], r'상강\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+-?[\d.]+\n'), 2)
chk('r(SiO2/Al2O3, CIA표) 30개, 28개', nums(v10, r'r = (-?[\d.]+) \(30개\), 감강·원강 제외 r = (-?[\d.]+) \(28개\)'), nums(M['cia'], r'30개: r = (-?[\d.]+) \(p = [\d.e-]+\)\s+감강·원강 제외 28개: r = (-?[\d.]+)'), 3)
chk('r(SiO2/Al2O3, K2O/Al2O3)', nums(v10, r'K2O/Al2O3 r = ([\d.]+)'), nums(M['cia'], r'K2O/Al2O3: r = ([\d.]+)'), 3)
chk('무한2에서 장흥도 -9.64', nums(v10, r'장흥도 [\d.]+: ([+-][\d.]+)'), nums(M['cia'], r'= ([+-][\d.]+)\n걸린'), 2)
# --- 혼합
chk('Nd 몫 f 세 개(계산 8-12)', allnums(v08, r'eNd [-\d.]+ -> f_JA \(equal \[Nd\]\) ([\d.]+)'), [float(x) for x in re.findall(r'εNd\s+-[\d.]+ -> f = .*? = ([\d.]+)\s+제1권', M['mix'])], 3)
chk('Sr 몫 f 네 개(계산 8-12)', allnums(v08, r'Sr [\d.]+ -> f_JA \(equal \[Sr\]\) ([\d.]+)'), [float(x) for x in re.findall(r'Sr [\d.]+ -> f = .*? = ([\d.]+)\s+제1권', M['mix'])], 3)
chk('혼합 시연 -0.006, -0.905', nums(v08, r'eNd mix (-?[\d.]+) vs linear (-?[\d.]+)'), nums(M['mix'], r'농도 가중 εNd = (-?[\d.]+) ; 농도를 같게 둔 직선 평균 = (-?[\d.]+)'), 3)
chk('합류 몫 중경 0.46, 무한 0.63(계산 10-9)', nums(v10, r'중경.*?= ([\d.]+)\n.*무한.*?= ([\d.]+)\n'), [round(float(x), 2) for x in re.findall(r'지류 몫 f = ([\d.]+)', M['mix'])], 2)
# --- 퇴적률
chk('Guo: 황토·고토양 퇴적률과 플럭스', nums(v08, r'loess rate cm/ka ([\d.]+) flux g/cm2/ka ([\d.]+) g/m2/yr ([\d.]+)'), nums(M['flux'], r'황토 800년/10 cm\s+퇴적률 ([\d.]+) cm/ka, 플럭스 ([\d.]+) g/cm2/ka = ([\d.]+) g/m2/yr'), 2)
chk('Guo: 고토양 몫 0.255', nums(v08, r'soil fraction needed for mean 1106 yr/sample: ([\d.]+)'), nums(M['flux'], r'고토양 몫 f = ([\d.]+)'), 3)
chk('Dou: 13.09 cm/ka, 76.4 년/cm', nums(v08, r'393 cm/30\.03 ka = ([\d.]+) cm/ka; yr/cm ([\d.]+)'), nums(M['flux'], r'= ([\d.]+) cm/ka, 해상도 ([\d.]+) 년/cm'), 2)
chk('Dou: 년/cm 48.3, 93.5, 97.1', allnums(v08, r'(?:glacial|deglac|Holocene) [\d.]+ cm/ka -> ([\d.]+) yr/cm'), [float(x) for x in re.findall(r'(?:빙하기|탈빙기|홀로세) [\d.]+ cm/ka -> ([\d.]+) 년/cm', M['flux'])], 1)
chk('Dou: 시료 간격 3.27 cm, 250 년', nums(v08, r'= ([\d.]+) cm per sample -> (\d+) yr'), nums(M['flux'], r'간격 ([\d.]+) cm, 시간 간격 (\d+) 년'), 2)
print('일치 %d / %d' % (sum(CH), len(CH)))
sys.exit(0 if all(CH) else 1)
