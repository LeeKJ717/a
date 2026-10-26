# -*- coding: utf-8 -*-
"""계산 6-9: 연대 점 간격 대 사건 길이. 계산 6-10: 서쪽과 동쪽 건조 구간의 시작·끝 차이의 순열 검정.
입력은 6장 본문 표의 논문 값(계산 6-3, 6-4 와 같은 구간)."""
import itertools, numpy as np

print('== 계산 6-9: 연대 점 간격 대 사건 길이 ==')
# 호륜호 5개 14C 보정 범위 중간값(Xiao 등 2018 표 1)
mid = [5380, 4330, 3580, 3095, 2565]
gaps = np.diff(mid)
print('  호륜호 14C 중간값 사이 간격(년):', [int(-g) for g in gaps], '평균 %.0f' % (-gaps.mean()))
ev = 375.0
print('  사건 길이 %.0f년 / 평균 간격 %.0f년 = %.2f (연대 점 사이 한 칸의 %.0f%%)' % (ev, -gaps.mean(), ev / -gaps.mean(), ev / -gaps.mean() * 100))
print('  사건(4217.5~3842.5)이 놓인 칸: 4330(89.5 cm)과 3580(79.5 cm) 사이 = %d년. 사건은 그 칸의 %.0f%%' % (4330 - 3580, ev / (4330 - 3580) * 100))
print('  사건 경계 깊이 88, 83 cm 는 연대 점 89.5, 79.5 cm 사이: 깊이 차 10 cm 중 사건 5 cm')
# 골에자르드
print('  골에자르드: U-Th 25개 / 1500년 = %.0f년 간격, 사건 290년 안에 %.1f개' % (1500 / 25, 290 / 60))
print('  골에자르드 평균 오차 31년(1시그마) 대 첫째 사건 길이 110년: 길이/오차 = %.1f' % (110 / 31))
print('  호륜호 시작 1시그마 43년 대 사건 길이 375년: 길이/오차 = %.1f' % (375 / 43))
print('  오만만 오차 125~150년 대 사건 길이 300~400년: 길이/오차 = %.1f ~ %.1f' % (300 / 150, 400 / 125))
print('  이식쿨 481년 간격(5장 계산 5-11) 대 사건 길이 300년: %.2f' % (300 / 481))
print('  나미비아 DP1 오차 10~28년, 사건 35개 이상 분석(Railsback 등 2018): 길이 220년(경계) / 28 = %.1f, / 10 = %.1f' % (220 / 28, 220 / 10))
print()
print('== 계산 6-10: 서쪽(지중해·서아시아·남아시아)과 동쪽(동아시아) 건조 구간의 시작과 끝 ==')
east = {'Hulun': (4210, 3840), 'Dali': (4450, 3750), 'Daihai': (4060, 3690), 'Hunsh': (4200, 3800), 'Dongge': (4400, 3950)}
west = {'Gol': (4260, 3970), 'GOman': (4025, 3625), 'Roberts': (4500, 3900), 'Kotla': (4100, 3900)}
ids = list(east) + list(west)
S = np.array([v[0] for v in list(east.values()) + list(west.values())], float)
E = np.array([v[1] for v in list(east.values()) + list(west.values())], float)
ne = len(east)
def diff(x, idx): 
    m = np.zeros(len(x), bool); m[list(idx)] = True
    return x[m].mean() - x[~m].mean()
for name, x in (('시작', S), ('끝', E)):
    obs = diff(x, range(ne))
    allp = [diff(x, c) for c in itertools.combinations(range(len(x)), ne)]
    allp = np.array(allp)
    p = (np.abs(allp) >= abs(obs) - 1e-9).mean()
    print('  %s: 동쪽 평균 %.1f, 서쪽 평균 %.1f, 차(동−서) = %.1f년; 순열 %d가지 가운데 |차| >= 관측인 비율 = %.3f' % (name, x[:ne].mean(), x[ne:].mean(), obs, len(allp), p))
print('  제외: 알타이(코어가 4.2 ka에서 시작, 시작값이 코어 시작), 롭노르(구간이 4.0 ka부터), 보스텐(건조 구간이 둘로 갈림), 카라쿨(방향이 다름)')
print('  동쪽 시작 범위 %d~%d, 서쪽 시작 범위 %d~%d' % (S[:ne].min(), S[:ne].max(), S[ne:].min(), S[ne:].max()))
print('  동쪽 끝 범위 %d~%d, 서쪽 끝 범위 %d~%d' % (E[:ne].min(), E[:ne].max(), E[ne:].min(), E[ne:].max()))
