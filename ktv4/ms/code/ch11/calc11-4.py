# -*- coding: utf-8 -*-
"""계산 11-4: 빙하 전진 시간창의 비교. 입력은 논문 초록이 적은 구간(ka BP)만.
Menounos 등(2009) 캐나다 코르디예라: 8.59~8.18, 7.36~6.45, 4.40~3.97, 3.54~2.77, 1.71~1.30 ka, 그리고 지난 천 년.
Solomina 등(2015) 전지구 189 시계열: 4.4~4.2, 3.8~3.4, 3.3~2.8, 2.6, 2.3~2.1, 1.5~1.4, 1.2~1.0, 0.7~0.5 ka (2.6 은 한 점).
논문이 오차를 초록에 주지 않으므로 오차는 넣지 않는다.
"""
M = [(8.59, 8.18), (7.36, 6.45), (4.40, 3.97), (3.54, 2.77), (1.71, 1.30)]
S = [(4.4, 4.2), (3.8, 3.4), (3.3, 2.8), (2.6, 2.6), (2.3, 2.1), (1.5, 1.4), (1.2, 1.0), (0.7, 0.5)]
def ov(a, b):
    return max(0.0, min(a[0], b[0]) - max(a[1], b[1]))
print('=== Menounos 등 전진 기간 길이(ka) ===')
tot = 0
for a in M:
    print('%.2f~%.2f  %.2f' % (a[0], a[1], a[0] - a[1])); tot += a[0] - a[1]
print('합 %.2f ka. 지난 천 년(1.0 ka)을 더하면 %.2f ka' % (tot, tot + 1.0))
print('Holocene 11.7 ka 대비 %.1f %% (지난 천 년 포함)' % (100 * (tot + 1.0) / 11.7))
print()
print('=== Solomina 등 전진 기간 길이(ka), 점은 0 ===')
ts = 0
for a in S:
    print('%.1f~%.1f  %.2f' % (a[0], a[1], a[0] - a[1])); ts += a[0] - a[1]
print('합 %.2f ka' % ts)
print()
print('=== 두 논문 창의 겹침(ka) ===')
for m in M:
    for s in S:
        o = ov(m, s)
        if o > 0 or (m[1] <= s[0] <= m[0] and s[0] == s[1]):
            print('Menounos %.2f~%.2f 와 Solomina %.1f~%.1f: 겹침 %.2f ka' % (m[0], m[1], s[0], s[1], o))
print('Solomina 점 2.6 ka 는 Menounos 3.54~2.77 와 겹치지 않음(2.6 < 2.77):', not (2.77 <= 2.6 <= 3.54))
print('Menounos 8.59~8.18 와 7.36~6.45 는 Solomina 목록(4.4 ka 이후)에 대응 없음 (초록이 이른 홀로세 전진을 적지 않음)')
n_hit = sum(1 for m in M if any(ov(m, s) > 0 for s in S))
print('Menounos 5개 중 Solomina 와 겹치는 것: %d 개' % n_hit)
print('Menounos 8.4 ka 에 숲을 덮는 전진 시작: 첫 전진 창 8.59~8.18 안: %s' % (8.18 <= 8.4 <= 8.59))
print('8.2 ka 사건 한랭 8.4~8.0(Barber, 5장) 과 Menounos 첫 창의 겹침 %.2f ka' % ov((8.4, 8.0), M[0]))
