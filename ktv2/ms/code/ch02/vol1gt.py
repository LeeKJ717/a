# -*- coding: utf-8 -*-
"""제1권 원고(markdown)의 표를 정답(ground truth)으로 읽는다. 제1권 build.py와 같은 규칙으로 표 번호를 센다."""
import glob, re, html
import markdown
from lxml import html as LH

BOOK = '/home/claude/book'


def latest():
    lat = {}
    for p in glob.glob(BOOK + '/ms/ch*-v*.md'):
        m = re.search(r'ch(\d+)-v(\d+)\.md$', p)
        if m and int(m.group(2)) >= lat.get(m.group(1), (0, ''))[0]:
            lat[m.group(1)] = (int(m.group(2)), p)
    return {int(k): v[1] for k, v in lat.items()}


def norm(s):
    s = html.unescape(s or '')
    s = re.sub(r'\s+', '', s)
    return s.replace('−', '-').replace('–', '-').replace('—', '-')


def tables(ch, path):
    """[(번호, 캡션, [[셀...]...])]  번호는 {{T:}}가 나온 순서."""
    t = open(path, encoding='utf-8').read()
    main = t.partition('## 참고문헌')[0]
    tb = [0]

    def g(m):
        tb[0] += 1
        return '\n<p class="tcap" data-n="%d">%s</p>\n' % (tb[0], html.escape(m.group(1)))
    main = re.sub(r'\{\{T:(.*?)\}\}', g, main)
    h = markdown.markdown(main, extensions=['md_in_html', 'tables'])
    root = LH.fromstring('<div>' + h + '</div>')
    out = []
    for cap in root.xpath('//p[@class="tcap"]'):
        nxt = cap.getnext()
        if nxt is None or nxt.tag != 'table':
            continue
        rows = []
        for tr in nxt.xpath('.//tr'):
            rows.append([c.text_content().strip() for c in tr.xpath('./th|./td')])
        out.append((int(cap.get('data-n')), cap.text_content()[:60], rows))
    return out


if __name__ == '__main__':
    n = 0
    for ch, p in sorted(latest().items()):
        ts = tables(ch, p)
        n += len(ts)
        print(ch, p.split('/')[-1], len(ts))
    print('합계', n)
