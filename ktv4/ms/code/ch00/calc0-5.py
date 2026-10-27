# -*- coding: utf-8 -*-
"""계산 0-5: 이 장의 지도와 본문에 쓴 한글 지명의 표를 만들고, 각 이름의 근거를 적는다.
이 장을 쓰는 동안 웹 검색 한도가 끝나 한국어 표기를 새로 확인하지 못했다. 그래서 지도에는 일반 독자에게 익숙한 대륙, 대양 이름과 이 책 앞 장들이 이미 쓴 이름만 둔다.
근거 칸의 '일반 표기'는 이 책이 쓰는 널리 알려진 한글 이름이라는 뜻이며 사전이나 위키백과 항목으로 이 장에서 대조하지 않았다."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [('아시아', 'Asia', '대륙', '일반 표기'), ('유럽', 'Europe', '대륙', '일반 표기'), ('아프리카', 'Africa', '대륙', '일반 표기'), ('북아메리카', 'North America', '대륙', '일반 표기'),
        ('남아메리카', 'South America', '대륙', '일반 표기'), ('오세아니아', 'Oceania', '대륙', '일반 표기'), ('남극 대륙', 'Antarctica', '대륙', '일반 표기'), ('그린란드', 'Greenland', '섬', '일반 표기'),
        ('태평양', 'Pacific Ocean', '대양', '일반 표기'), ('대서양', 'Atlantic Ocean', '대양', '일반 표기'), ('인도양', 'Indian Ocean', '대양', '일반 표기'),
        ('북극해', 'Arctic Ocean', '대양', '일반 표기'), ('남극해', 'Southern Ocean', '대양', '일반 표기(남빙양이라고도 함)'),
        ('캠프 센추리', 'Camp Century', '빙핵 지점', '2장이 쓴 표기'), ('다이3', 'Dye 3', '빙핵 지점', '2장이 쓴 표기'), ('렌란', 'Renland', '빙핵 지점', '2장이 쓴 표기'),
        ('보스토크', 'Vostok', '빙핵 지점', '2장이 쓴 표기'), ('돔 C', 'Dome C (EPICA)', '빙핵 지점', '2장이 쓴 표기'), ('로 돔', 'Law Dome', '빙핵 지점', '2장이 쓴 표기'),
        ('제임스 로스 섬', 'James Ross Island', '빙핵 지점', '2장이 쓴 표기')]
with open(os.path.join(HERE, 'names-table.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['한글', '원어', '종류', '근거']); w.writerows(rows)
print('이름 | 원어 | 종류 | 근거')
for r in rows: print(' | '.join(r))
print('이름 수 %d, 이 장에서 웹으로 대조한 것 0개' % len(rows))
