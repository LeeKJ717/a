#!/usr/bin/env python3
# usage: build.py [color|bw]  -> build/book-<mode>-v1.pdf
import sys,re,glob,html,os,markdown
from weasyprint import HTML
mode=sys.argv[1] if len(sys.argv)>1 else 'color'
VER='v23'
CSS='''
@page{size:182mm 257mm;margin:20mm 16mm 22mm 36.4mm;
 @bottom-center{content:counter(page);font:9pt "Noto Serif CJK KR",serif}}
@page:first{@bottom-center{content:none}}
@page:blank{@bottom-center{content:none}}
body{margin:0;font:10.5pt/1.8 "Noto Serif CJK KR","Noto Serif CJK JP",serif;word-break:keep-all;text-align:justify}
h1{font:700 18pt/1.4 "Noto Sans CJK KR",sans-serif;break-before:page;margin:0 0 8mm;string-set:chap content()}
h3{font:700 11pt/1.5 'Noto Sans CJK KR',sans-serif;margin:5mm 0 2mm}
h2{font:700 13pt/1.5 "Noto Sans CJK KR",sans-serif;margin:7mm 0 3mm}
p{margin:0 0 3mm;orphans:2;widows:2}
figure{margin:4mm 0;break-inside:avoid;page-break-inside:avoid;text-align:left}
figure img{width:130mm;max-width:100%;max-height:185mm;display:block}
figcaption{font:9pt/1.5 "Noto Sans CJK KR",sans-serif;margin-top:2mm}
.tcap{font:9pt/1.5 'Noto Sans CJK KR',sans-serif;margin:4mm 0 1.5mm;break-after:avoid}
table{border-collapse:collapse;font:8.2pt/1.45 'Noto Sans CJK KR',sans-serif;margin:0 0 4mm;width:100%;break-inside:auto}
th,td{border:0.4pt solid #666;padding:1mm 1.5mm;vertical-align:top;text-align:left;word-break:keep-all}
th{background:#eee}
tr{break-inside:avoid}
.method{border:0.6pt solid #444;background:#f4f4f4;padding:2.5mm 3.5mm;margin:3mm 0 4mm;font:9.5pt/1.65 "Noto Sans CJK KR",sans-serif}
.theory{border:0.6pt dashed #444;background:#fafafa;padding:2.5mm 3.5mm;margin:3mm 0 4mm;font:9.5pt/1.65 "Noto Sans CJK KR",sans-serif}
.theory h4,.method h4,.story h4,.bio h4{margin:0 0 1.5mm;font-size:10pt}
.story{border-left:2pt solid #444;padding:1mm 0 1mm 4mm;margin:3mm 0 4mm;font:9.8pt/1.7 "Noto Serif CJK KR",serif}
.bio{margin:3mm 0 5mm}
.bio figure img{width:38mm;float:left;margin:0 4mm 1mm 0}
.refs p{padding-left:8mm;text-indent:-8mm;font-size:9.5pt;line-height:1.5}
.toc{break-before:page}
.toc h1{break-before:auto}
.toc a{display:block;text-decoration:none;color:#000;font:10pt/2 "Noto Sans CJK KR",sans-serif}
.toc a::after{content:leader('.') target-counter(attr(href),page);}
.guide h2{break-before:page;font:700 15pt/1.5 'Noto Sans CJK KR',sans-serif;margin:0 0 6mm;padding:3mm 0;border-top:2pt solid #444;border-bottom:0.6pt solid #444}
.guide ul{margin:0 0 3mm 0;padding-left:5mm}
.guide li{margin-bottom:1.5mm}
.toc a.sub{padding-left:8mm;font-size:9pt;line-height:1.8}
.opener{break-before:right;height:213mm;display:flex;flex-direction:column}
.oband{background:%BAND%;color:#fff;padding:5mm 6mm 5mm;font-family:"Noto Sans CJK KR",sans-serif}
.onum{font:500 9pt/1 "Noto Sans CJK KR";letter-spacing:.3em;color:%ACC%;margin-bottom:2.5mm}
.otitle{font:700 19pt/1.3 "Noto Serif CJK KR",serif}
.osub{font:400 9.5pt/1.5 "Noto Sans CJK KR";margin-top:2mm;color:#e9e9e9}
.oart{width:129.6mm;height:64mm;display:block;margin:0}
.onote{font:7.5pt/1.4 "Noto Sans CJK KR";color:#666;margin:1.2mm 0 4mm}
.ohead{font:700 10.5pt/1.4 "Noto Sans CJK KR";border-bottom:0.8pt solid #444;padding-bottom:1.2mm;margin-bottom:1.5mm}
.otoc a{display:block;text-decoration:none;color:#000;font:8.8pt/1.62 "Noto Sans CJK KR"}
.otoc a::after{content:leader('.') target-counter(attr(href),page)}
.chh{break-before:right}
h1,h2,h3,h4{break-after:avoid;page-break-after:avoid}
table.keep{break-inside:avoid}
.tb{break-inside:avoid;page-break-inside:avoid}
thead{display:table-header-group}
pre{font:8pt/1.45 'DejaVu Sans Mono','Noto Sans Mono CJK KR',monospace;white-space:pre-wrap;word-break:break-all;background:#f4f4f4;padding:2mm;margin:2mm 0 4mm}
pre code,code{font:inherit;white-space:pre-wrap;word-break:break-all}
.cover{height:200mm;display:flex;flex-direction:column;justify-content:center}
.cover h1{break-before:auto;font-size:24pt}
'''
CSS=CSS.replace('%BAND%','#0f2a3f' if mode=='color' else '#2b2b2b').replace('%ACC%','#e07a3f' if mode=='color' else '#dddddd')

def latest(pat):
    best={}
    for p in glob.glob(pat):
        m=re.search(r'-v(\d+)\.md$',p)
        k=re.sub(r'-v\d+\.md$','',p)
        if m and int(m.group(1))>=best.get(k,(0,''))[0]: best[k]=(int(m.group(1)),p)
    return {k:v[1] for k,v in best.items()}
def render_plain(t,label):
    cnt={'f':0,'t':0}
    def f(m):
        cnt['f']+=1
        cap=html.escape(m.group(1));n=m.group(2)
        src=f'fig/{n}-{mode}.svg' if os.path.exists(f'fig/{n}-{mode}.svg') else f'fig/{n}.svg'
        return f'<figure><img src="{src}"><figcaption><b>그림 {label}-{cnt["f"]}.</b> {cap}</figcaption></figure>'
    t=re.sub(r'!\[(.*?)\]\((.*?)\)',f,t)
    def g(m):
        cnt['t']+=1
        return f'\n<p class="tcap"><b>표 {label}-{cnt["t"]}.</b> {html.escape(m.group(1))}</p>\n'
    t=re.sub(r'\{\{T:(.*?)\}\}',g,t)
    return markdown.markdown(t,extensions=['md_in_html','tables'])
GUIDE=latest('ms/front/guide-ch*-v*.md')
front_html='';front_toc=[]
for p in sorted(latest('ms/front/front-*-v*.md').values()):
    t=open(p,encoding='utf-8').read()
    h=render_plain(t,'서')
    k=[0]
    def idh(m):
        k[0]+=1;i=f'fr{k[0]}_{abs(hash(p))%1000}'
        front_toc.append(f'<a href="#{i}">{html.escape(m.group(1))}</a>')
        return f'<h1 id="{i}">{m.group(1)}</h1>'
    h=re.sub(r'<h1>(.*?)</h1>',idh,h)
    front_html+=h
back_html='';back_toc=[]
for p in sorted(latest('ms/front/back-*v*.md').values()):
    t=open(p,encoding='utf-8').read()
    h=render_plain(t,'맺')
    def idb(m):
        back_toc.append(f'<a href="#bk1">{html.escape(m.group(1))}</a>')
        return f'<h1 id="bk1">{m.group(1)}</h1>'
    back_html+=re.sub(r'<h1>(.*?)</h1>',idb,h,count=1)

COLO='''<div class="colo"><h1 style="break-before:page;font-size:13pt">판권지</h1><img src="logo/ssp-logo-h-light-v1.svg" style="width:58mm;display:block;margin:0 0 6mm 0">
<p style="font:700 15pt/1.5 'Noto Serif CJK KR'">동아시아 1만 년의 기후와 땅</p>
<p style="font:10pt/1.6 'Noto Sans CJK KR'">한반도에서 본 홀로세의 기후와 지형 변화<br>1만 년의 기후와 땅 시리즈 제1권</p>
<table style="width:100%;font:9pt/1.6 'Noto Sans CJK KR'"><tr><th style="width:28mm">지은이</th><td>이광조</td></tr>
<tr><th>펴낸이</th><td>이광조</td></tr>
<tr><th>펴낸곳</th><td>과학과영성출판사 (출판사 신고 2022-06-28, 신고번호 제455-251002022000060호)</td></tr>
<tr><th>주소</th><td>충남 금산군 금성면 뒷밭들길 68 A동 103호</td></tr>
<tr><th>홈페이지</th><td>www.ssbook.kr</td></tr>
<tr><th>이메일</th><td>contact@ssbook.kr</td></tr>
<tr><th>판형</th><td>B5 (182 × 257 mm)</td></tr>
<tr><th>발행</th><td>1판 1쇄 (발행일 추후 기입)</td></tr>
<tr><th>ISBN</th><td>(추후 기입)</td></tr>
<tr><th>정가</th><td>(추후 기입)</td></tr></table>
<p style="font:8.5pt/1.7 'Noto Sans CJK KR';margin-top:6mm">이 책의 저작권은 지은이에게 있으며, 무단 전재와 복제를 금합니다. 이 책이 인용한 논문과 자료의 저작권은 각 저자와 발행처에 있습니다. 지도는 Natural Earth의 벡터 자료(퍼블릭 도메인)로 만들었습니다(Made with Natural Earth). 표지 그림은 Apache License 2.0의 오픈 모델(Z-Image-Turbo)로 생성한 삽화이며, 장 표지 그림은 Natural Earth 지도에서 그린 도안입니다. 본문 글꼴은 Noto Serif CJK KR과 Noto Sans CJK KR(SIL Open Font License)입니다. 파본은 구입처에서 교환해 드립니다.</p></div>'''
body=[];toc=[];fig=0;ci=0
_lat={}
for _p in glob.glob('ms/ch*-v*.md'):
    _m=re.search(r'ch(\d+)-v(\d+)',_p)
    if _m and int(_m.group(2))>=_lat.get(_m.group(1),(0,''))[0]: _lat[_m.group(1)]=(int(_m.group(2)),_p)
for p in sorted(v[1] for v in _lat.values()):
    t=open(p,encoding='utf-8').read()
    ci=int(re.search(r'ch(\d+)',p).group(1));fig=0;tb=0
    def f(m):
        global fig;fig+=1
        cap=html.escape(m.group(1));n=m.group(2)
        ext=next((e for e in ('png','jpg','svg') if os.path.exists(f'fig/{n}-{mode}.{e}') or os.path.exists(f'fig/{n}.{e}')),'svg')
        src=f'fig/{n}-{mode}.{ext}' if os.path.exists(f'fig/{n}-{mode}.{ext}') else f'fig/{n}.{ext}'
        return f'<figure><img src="{src}"><figcaption><b>그림 {ci}-{fig}.</b> {cap}</figcaption></figure>'
    t=re.sub(r'!\[(.*?)\]\((.*?)\)',f,t)
    def g(m):
        global tb;tb+=1
        return f'\n<p class="tcap"><b>표 {ci}-{tb}.</b> {html.escape(m.group(1))}</p>\n'
    t=re.sub(r'\{\{T:(.*?)\}\}',g,t)
    main,_,refs=t.partition('## 참고문헌')
    h=markdown.markdown(main,extensions=['md_in_html','tables'])
    h=h.replace('<h1>',f'<h1 class="chh" id="c{ci}">',1)
    secs=[];_k=[0]
    def _h2(m):
        _k[0]+=1;i=f's{ci}-{_k[0]}';secs.append((i,m.group(1)));return f'<h2 id="{i}">{m.group(1)}</h2>'
    h=re.sub(r'<h2>(.*?)</h2>',_h2,h)
    title=re.search(r'^# (.+)',t,re.M).group(1)
    lab=f'{ci}장 ' if ci and not title.startswith(f'{ci}장') else ''
    toc.append(f'<a href="#o{ci}">{lab}{html.escape(title)}</a>')
    h=h.replace(f'id="c{ci}">',f'id="c{ci}">{lab}',1)
    r=markdown.markdown(refs.strip())
    secs.append((f's{ci}-ref','참고문헌'))
    _t=re.sub(r'^\d+장\s*','',title); _main,_,_sub=_t.partition(': ')
    _re=re.compile(r'<[^>]+>')
    op=(f'<div class="opener" id="o{ci}"><div class="oband"><div class="onum">제 {ci} 장</div><div class="otitle">{html.escape(_main)}</div>'
        +(f'<div class="osub">{html.escape(_sub)}</div>' if _sub else '')+'</div>'
        +f'<img class="oart" src="fig/chapart-{ci:02d}-{mode}.svg">'
        +'<div class="onote">장 표지 그림은 장의 주제를 나타낸 도안이다. 자료를 그린 그림이 아니며 선, 원, 화살표는 값을 뜻하지 않는다.</div>'
        +'<div class="ohead">이 장의 차례</div><div class="otoc">'+''.join(f'<a href="#{i}">{_re.sub("",x)}</a>' for i,x in secs)+'</div></div>')
    gk=f'ms/front/guide-ch{ci:02d}'
    gh=''
    if gk in GUIDE:
        gh=markdown.markdown(open(GUIDE[gk],encoding='utf-8').read()).replace('<h2>',f'<h2 id="g{ci}">',1)
        gh=f'<div class="guide">{gh}</div>'
        toc.insert(len(toc)-1,f'<a class="sub" href="#g{ci}">{ci}장 안내</a>')
    body.append(op+gh+h+f'<div class="refs"><h2 id="s{ci}-ref">참고문헌</h2>{r}</div>')
doc=f'<html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="cover"><h1>동아시아 1만 년의 기후와 땅</h1><p>한반도에서 본 홀로세의 기후와 지형 변화</p><p>1만 년의 기후와 땅 시리즈 제1권</p></div>{front_html}<div class="toc"><h1 style="break-before:page">차례</h1>{"".join(front_toc)}{"".join(toc)}{"".join(back_toc)}</div>{"".join(body)}{back_html}{COLO}</body></html>'
_t=[0]
def _tk(m):
    _t[0]+=1;return f'<table data-tk="{_t[0]}">'
doc=re.sub(r'<table>',_tk,doc)
_d0=HTML(string=doc,base_url='.').render()
_hh={}
def _tw(b):
    if b.__class__.__name__=='TableBox' and b.element is not None and b.element.get('data-tk'):
        k=b.element.get('data-tk');_hh[k]=_hh.get(k,0)+b.height
    for c in getattr(b,'children',[]) or []: _tw(c)
for _pg in _d0.pages: _tw(_pg._page_box.children[0])
_LIM=198*96/25.4
def _keep(m):
    k=re.search(r'data-tk="(\d+)"',m.group(0)).group(1)
    return m.group(0).replace('<table ','<table class="keep" ',1) if _hh.get(k,0)<=_LIM else m.group(0)
doc=re.sub(r'<table data-tk.*?</table>',_keep,doc,flags=re.S)
doc=re.sub(r'((?:<p class="tcap">(?:(?!</p>).)*</p>\s*)?)(<table class="keep".*?</table>)',lambda m:'<div class="tb">'+m.group(1)+m.group(2)+'</div>',doc,flags=re.S)
_n=[0]
def _hk(m):
    _n[0]+=1;return f'<{m.group(1)} data-hk="{_n[0]}"{m.group(2)}>'
doc=re.sub(r'<(h[234])((?: [^>]*)?)>',_hk,doc)
_c=[0]
def _ck(m):
    _c[0]+=1;return f'<p class="tcap" data-ck="{_c[0]}">'
doc=re.sub(r'<p class="tcap">',_ck,doc)
def _walk(b,chain=()):
    yield b,chain
    for c in getattr(b,'children',[]) or []:
        yield from _walk(c,chain+((getattr(b,'element_tag',None),getattr(b,'element',None)),))
def _check(d):
    orph=set();cap=set()
    for pg in d.pages:
        last=None;lb=-1
        for b,ch in _walk(pg._page_box.children[0]):
            if hasattr(b,'text') and b.text.strip() and b.position_y+b.height>=lb: lb=b.position_y+b.height;last=ch
        if not last: continue
        for t,e in reversed(last):
            if e is None: continue
            if t in('td','th','li','figcaption'): break
            if t in('h2','h3','h4') and e.get('data-hk'): orph.add(e.get('data-hk'));break
            if t=='p' and e.get('data-ck'): cap.add(e.get('data-ck'));break
    return orph,cap
_fx=set();_fx2=set()
for _it in range(6):
    d=HTML(string=doc,base_url='.').render()
    o,c=_check(d)
    print('iter',_it,'orphan headings',len(o),'caption-end',len(c),'pages',len(d.pages),flush=True)
    if not o and not c: break
    for k in o-_fx: doc=doc.replace(f'data-hk="{k}"',f'data-hk="{k}" style="break-before:page"',1)
    for k in c-_fx2: doc=doc.replace(f'data-ck="{k}"',f'data-ck="{k}" style="break-before:page"',1)
    _fx|=o;_fx2|=c
open('build/book.html','w',encoding='utf-8').write(doc)
out=f'build/book-{mode}-{VER}.pdf'
d.write_pdf(out)
print(out)
