# -*- coding: utf-8 -*-
"""실습 2-3b: DOI 정규화 함수의 시험. 입력과 기대값은 이 책이 정했다(시연값). 실행: python3 10-doi-test.py | tee 10-doi-test.log"""
import paperlib as pl
CASES = [
    ('https://doi.org/10.9999/DEMO.001', '10.9999/demo.001', '접두어(https)와 대문자'),
    ('http://dx.doi.org/10.9999/demo.001', '10.9999/demo.001', '옛 주소 dx.doi.org'),
    ('doi:10.9999/demo.001', '10.9999/demo.001', 'doi: 접두어'),
    ('DOI: 10.9999/demo.001', '10.9999/demo.001', '대문자 DOI: 와 공백'),
    ('  10.9999/demo.001\n', '10.9999/demo.001', '앞뒤 공백, 줄바꿈'),
    ('10.9999/demo.001.', '10.9999/demo.001', '문장 끝의 마침표'),
    ('(10.9999/demo.001)', '10.9999/demo.001', '바깥 괄호'),
    ('10.9999%2Fdemo.001', '10.9999/demo.001', '/가 %2F로 인코딩됨'),
    ('10.1016/s1367-9120(99)00080-2', '10.1016/s1367-9120(99)00080-2', 'DOI 안의 괄호는 보존'),
    ('(10.1016/s1367-9120(99)00080-2).', '10.1016/s1367-9120(99)00080-2', '짝이 맞는 괄호는 보존, 바깥 것만 제거'),
    ('openalex:W3187374414', None, 'DOI가 아닌 식별자(제1권 papers에 실제로 있었다)'),
    ('Woe, J. (2015). A book. Demo Press.', None, 'DOI 없는 서지 줄'),
    ('', None, '빈 문자열'),
    (None, None, 'None'),
]
ok = 0
for raw, want, why in CASES:
    got = pl.doi_norm(raw)
    flag = 'ok ' if got == want else 'FAIL'
    ok += got == want
    print('%s %-52r -> %-34r %s' % (flag, raw, got, why))
print('통과 %d / %d' % (ok, len(CASES)))
