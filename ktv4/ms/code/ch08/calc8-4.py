# -*- coding: utf-8 -*-
"""계산 8-4: 4.2 ka 사건 창들의 겹침, 지속, 둥거 3550 과의 거리.
입력(논문, cal BP): Booth 등(2005) 4300~4100(요약은 4.3~4.1 ka). Mayewski 등(2004) 4200~3800. Bini 등(2019) 4300~3800(약 500 년).
Railsback 등(2018, 제3권 6장) 경계 4150~3930, 중심 4070, 기록 12. Weiss(2016) 4200~3900(4.2~3.9 ka, 200~300 년이라고도 적음).
deMenocal 등(2000, ODP 658C) 육상 기원 침적의 짧은 감소 4300~4100. 제3권 6장 계산 6-4 의 유라시아 열 기록 공통 구간 4025~3970(55 년). Dykoski 등(2005) 둥거 3550 +- 59.
Weiss 의 200~300 년은 그의 4.2~3.9 ka 구간(300 년)과 맞는지도 본다."""
import numpy as np
W = {'Booth 등 북미 중부': (4100, 4300), 'deMenocal 등 ODP 658C 먼지 감소': (4100, 4300), 'Mayewski 등 급변 구간': (3800, 4200),
     'Bini 등 지중해': (3800, 4300), 'Railsback 등 종합': (3930, 4150), 'Weiss 개관': (3900, 4200), '제3권 6장 유라시아 열 기록 공통': (3970, 4025)}
names = list(W)
print('창(cal BP, 시작-끝, 길이)')
for n in names:
    a, b = W[n]; print('  %-28s %d ~ %d, %d 년' % (n, b, a, b-a))
print()
def ov(x, y):
    lo = max(W[x][0], W[y][0]); hi = min(W[x][1], W[y][1]); return max(0, hi-lo)
print('쌍별 겹침 년수 / 짧은 쪽 길이')
mat = np.zeros((len(names), len(names)))
for i, x in enumerate(names):
    for j, y in enumerate(names):
        o = ov(x, y); mat[i, j] = o/min(W[x][1]-W[x][0], W[y][1]-W[y][0])
for i, x in enumerate(names):
    print('  %-28s' % x, ' '.join('%4.2f' % v for v in mat[i]))
iu = np.triu_indices(len(names), 1)
print('쌍별 겹침 비율 평균 %.2f, 최소 %.2f, 겹침 0 인 쌍 %d / %d' % (mat[iu].mean(), mat[iu].min(), (mat[iu] == 0).sum(), len(iu[0])))
print()
glob = ['Booth 등 북미 중부', 'Mayewski 등 급변 구간', 'Bini 등 지중해', 'Railsback 등 종합', 'Weiss 개관']
lo = max(W[n][0] for n in glob); hi = min(W[n][1] for n in glob)
print('전지구 다섯 창의 공통 구간: %d ~ %d, %d 년' % (hi, lo, hi-lo))
for drop in glob:
    g2 = [n for n in glob if n != drop]
    lo2 = max(W[n][0] for n in g2); hi2 = min(W[n][1] for n in g2)
    print('  %s 를 빼면 %d ~ %d, %d 년' % (drop, hi2, lo2, max(0, hi2-lo2)))
glob2 = glob + ['deMenocal 등 ODP 658C 먼지 감소', '제3권 6장 유라시아 열 기록 공통']
lo = max(W[n][0] for n in glob2); hi = min(W[n][1] for n in glob2)
print('위에 deMenocal 과 제3권 공통까지 일곱 창을 더하면 공통 %d (음수면 공통 구간 없음: 시작 %d, 끝 %d)' % (hi-lo, hi, lo))
print()
print('사건 길이: Booth 200, Railsback 220, Weiss 300(그의 200~300), Mayewski 400, Bini 500. 최소 %d 최대 %d, 비 %.1f' % (200, 500, 500/200))
print('Weiss 의 4.2~3.9 ka 는 %d 년이고 200~300 년이라는 그의 기술과 %d 년 안' % (300, 300-200))
print()
print('둥거 3550 +- 59 와 4.2 ka 창의 거리: 4200 에서 %d 년, Railsback 끝 3930 에서 %d 년, 오차의 %.1f 배(4200 기준)' % (4200-3550, 3930-3550, (4200-3550)/59))
print('  3550 +- 2*59 = %d ~ %d 이므로 Railsback 경계 끝 3930 과도 겹치지 않는다' % (3550-118, 3550+118))
print()
print('[E] 연대 해상도: 사건 창 안에 들어가는 시료 수 (창 길이 / 시료 간격)')
print('  Weiss 가 적은 마우믈루 6년 간격: 4.2~3.9 ka 300 년 안에 %.0f 개, 사건 200 년이면 %.0f 개' % (300/6, 200/6))
print('  Weiss 가 적은 로건산 10년 간격: 300 년 안에 %.0f 개, 200 년이면 %.0f 개' % (300/10, 200/10))
print('  Wang 등(2005) 둥거 5년 해상도: 200 년 안에 %.0f 개' % (200/5))
print('  ODP 658C 시료 평균 111 년(6장 계산 6-2): 200 년 창 안에 %.1f 개, Booth 와 같은 창에 %.1f 개' % (200/111, 200/111))
print('  Bini 가 모은 지중해 석순이 4.3~3.8 ka 500 년 창을 6년 해상도로 읽는다면 %.0f 개(가정; 석순마다 간격은 확인 못함)' % (500/6))
print('  호륜호(제3권 6장 계산 6-9): 연대 점 간격 평균 704 년, 사건 375 년은 %.0f %%' % (100*375/704))
print()
print('[F] 6장이 읽은 열대 기록의 4.2 ka 즈음 값(4200 과 Railsback 경계 4150~3930 에서의 거리)')
for nm, t in (('둥거 쇠퇴 시작 3550', 3550), ('카리아코 Ti 극소 시작 3800', 3800)):
    print('  %-22s 4200 에서 %d 년, 경계 끝 3930 에서 %d 년' % (nm, 4200-t, 3930-t))
print('  ODP 658C 먼지 감소 4300~4100 은 창이 4.2 ka 와 겹치나 방향이 건조 쪽이 아님')
print('  세 기록의 시각: 4300~4100 (감소), 3800 (극소 시작), 3550 (쇠퇴 시작) 이므로 서로 최대 %d 년 차이' % (4300-3550))
