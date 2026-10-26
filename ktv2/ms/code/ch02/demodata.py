# -*- coding: utf-8 -*-
"""시연값 만들기(v1). 아래의 모든 논문, DOI(10.9999/ 접두어), 저자, 초록, 숫자는 이 책이 만든 가상의 값이다.
실제 논문이 아니며 어떤 서비스의 실제 응답도 아니다. 응답의 모양(필드 이름)은 이 책이 알던 구조를 흉내 냈다."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')

ABS = {
    'demo.001': 'DEMO abstract one. A made up ring width series is compared with a made up temperature record.',
    'demo.002': 'DEMO abstract two. A made up loess section is dated with made up luminescence ages.',
    'demo.004': 'DEMO abstract four. A made up lake core is summarised.',
    'demo.005': 'DEMO abstract five. A made up table of haplogroup counts is given.',
}


def inverted(text):
    inv = {}
    for i, w in enumerate(text.split()):
        inv.setdefault(w, []).append(i)
    return inv


def oa_work(key, title, year, authors, journal, is_oa, oa_status, pdf_url=None, with_abs=True, doi_style='https'):
    doi = '10.9999/' + key.upper() if doi_style == 'https' else '10.9999/' + key
    w = {
        'id': 'https://openalex.org/WDEMO' + key[-3:],
        'doi': 'https://doi.org/' + doi,
        'title': title, 'display_name': title,
        'publication_year': year,
        'authorships': [{'author': {'display_name': a}} for a in authors],
        'primary_location': {'source': {'display_name': journal}, 'landing_page_url': 'https://example.org/landing/' + key},
        'open_access': {'is_oa': is_oa, 'oa_status': oa_status, 'oa_url': pdf_url},
        'best_oa_location': ({'is_oa': True, 'pdf_url': pdf_url, 'landing_page_url': 'https://example.org/landing/' + key} if pdf_url else None),
        'locations': [],
        'abstract_inverted_index': inverted(ABS[key]) if with_abs and key in ABS else None,
        'cited_by_count': {'demo.001': 7, 'demo.002': 3, 'demo.004': 0, 'demo.005': 12}.get(key, 0),
        'referenced_works': ['https://openalex.org/WDEMO900', 'https://openalex.org/WDEMO901'][:{'demo.001': 2, 'demo.002': 1}.get(key, 0)],
    }
    return w


def cr_work(key, title, year, authors, journal, with_abs=False):
    fam = lambda a: a.split()[-1]
    giv = lambda a: ' '.join(a.split()[:-1])
    m = {
        'DOI': '10.9999/' + key,
        'title': [title],
        'author': [{'given': giv(a), 'family': fam(a)} for a in authors],
        'container-title': [journal],
        'issued': {'date-parts': [[year, 5]]},
        'is-referenced-by-count': {'demo.001': 6, 'demo.003': 1}.get(key, 0),
    }
    if with_abs:
        m['abstract'] = '<jats:p>' + ABS[key] + '</jats:p>'
    return {'status': 'ok', 'message-type': 'work', 'message': m}


def build(port):
    base = 'http://127.0.0.1:%d' % port
    oa = {
        'demo.001': oa_work('demo.001', 'DEMO 001 Ring widths and temperature in a made up forest', 2022, ['Ann Doe', 'Bo Roe'], 'Journal of Demo Rings', True, 'gold', base + '/pdf/demo001.pdf'),
        'demo.002': oa_work('demo.002', 'DEMO 002 Luminescence ages of a made up loess section', 2020, ['Cy Poe'], 'Demo Quaternary Letters', False, 'closed'),
        'demo.004': oa_work('demo.004', 'DEMO 004 A made up lake core', 2019, ['Di Moe'], 'Demo Limnology', True, 'green', base + '/landing/demo004'),
        'demo.005': oa_work('demo.005', 'DEMO 005 Haplogroup counts in made up burials', 2018, ['Ed Loe', 'Fay Zoe'], 'Demo Genetics Reports', True, 'gold', base + '/pdf/demo005.pdf'),
    }
    cr = {
        'demo.001': cr_work('demo.001', 'DEMO 001 Ring widths and temperature in a made up forest', 2021, ['Ann Doe', 'Bo Roe'], 'Journal of Demo Rings'),
        'demo.003': cr_work('demo.003', 'DEMO 003 A made up note on map projections', 2017, ['Gus Hoe'], 'Demo Cartography'),
    }
    return oa, cr


REFLIST = [
    # (서지 한 줄, 장)  DOI를 여러 모양으로 적은 시연 참고문헌 목록
    ('Doe, A., & Roe, B. (2022). DEMO 001 Ring widths and temperature in a made up forest. Journal of Demo Rings. https://doi.org/10.9999/DEMO.001', 3),
    ('Poe, C. (2020). DEMO 002 Luminescence ages of a made up loess section. Demo Quaternary Letters. doi:10.9999/demo.002', 4),
    ('Poe, C. (2020). DEMO 002 Luminescence ages ... Demo Quaternary Letters. https://dx.doi.org/10.9999/demo.002.', 6),
    ('Hoe, G. (2017). DEMO 003 A made up note on map projections. Demo Cartography. (10.9999/Demo.003)', 1),
    ('Noe, H. (2016). DEMO 006 A made up paper nobody indexes. Demo Letters. 10.9999/demo.006', 9),
    ('Woe, J. (2015). DEMO 007 A made up book without DOI. Demo Press.', 9),
]


def pdf_files():
    """시연 PDF 두 개를 reportlab로 만든다. 1번은 선이 있는 표, 5번은 선이 없는 표."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    os.makedirs(os.path.join(OUT, 'pdf'), exist_ok=True)
    paths = {}
    # 1번
    p = os.path.join(OUT, 'pdf', 'demo001.pdf')
    c = canvas.Canvas(p, pagesize=A4, invariant=1)
    c.setFont('Helvetica', 11)
    c.drawString(72, 780, 'DEMO 001 Ring widths and temperature in a made up forest (demo value, not a real paper)')
    c.drawString(72, 760, 'Table 1. Made up counts per site.')
    rows = [('Site', 'Cores', 'Trees', 'Span'), ('A', '12', '8', '1650-2010'), ('B', '9', '6', '1700-2012'), ('C', '15', '10', '1600-2013')]
    y = 735
    for r in rows:
        for j, v in enumerate(r):
            c.drawString(80 + j * 90, y, v)
        y -= 20
    c.grid([72, 162, 252, 342, 432], [y + 12, y + 32, y + 52, y + 72, y + 92])
    c.save(); paths['demo001'] = p
    # 5번: 선 없는 표
    p = os.path.join(OUT, 'pdf', 'demo005.pdf')
    c = canvas.Canvas(p, pagesize=A4, invariant=1)
    c.setFont('Helvetica', 11)
    c.drawString(72, 780, 'DEMO 005 Haplogroup counts in made up burials (demo value, not a real paper)')
    c.drawString(72, 760, 'Table 2. Made up haplogroup counts.')
    rows = [('Group', 'n', 'O', 'C', 'N'), ('East', '30', '18', '8', '4'), ('West', '24', '9', '10', '5'), ('North', '20', '6', '9', '5')]
    y = 735
    for r in rows:
        for j, v in enumerate(r):
            c.drawString(80 + j * 70, y, v)
        y -= 20
    c.save(); paths['demo005'] = p
    return paths


if __name__ == '__main__':
    print(pdf_files())
