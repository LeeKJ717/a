import math
# 1장 계산 재현 (시연값은 표시)
print('A-1 평균 수심', 2.35e5/1.249e6*1000, 'm')              # 188.2
print('A-2 해수준', -(93-15), 'm')                             # -78
print('A-3 두 값의 차', 120-80, math.hypot(5,10), 40/math.hypot(5,10))
for s in (120,80): print('A-4 안부 위 수심', 130-s)
print('B-1 회수 길이', 82.9*0.89)                              # 73.78
print('B-2 심도', 1650*0.100/2)                                # 82.5
print('B-3 OSL', 75-64.96, (75-64.96)/8)
print('B-4 평균 퇴적률 시연', 40/ (10-6.5), 40/(10-7), 40/(10-6))
print('C-1 합성 평균방위', end=' ')
a=[math.radians(2*x) for x in (170,10)]
x=sum(math.cos(t) for t in a); y=sum(math.sin(t) for t in a)
print(math.degrees(math.atan2(y,x))/2%180, ' 단순평균', (170+10)/2)
print('C-2 총길이/개수 시연', 12279/ 16)
print('C-3 MWP-1A 상승 속도', (95-78)/(14.5-13.7))
print('C-4 나이 차', 200-12, 320-12)
print('D-1', 9300-7300, 9300-5180)
