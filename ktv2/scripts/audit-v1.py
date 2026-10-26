#!/usr/bin/env python3
# usage: audit-v1.py HTML  -> 쪽 배치 점검: 가로 넘침, 쪽 걸침 표/그림, 쪽 끝 제목, 쪽 끝 표 제목
import sys,collections
from weasyprint import HTML
doc=HTML(sys.argv[1],base_url='.').render()
L=36.4*96/25.4; R=(182-16)*96/25.4; TOL=1.5
sparse=[];over=[];seen=collections.defaultdict(list);orph=[];capend=[]
def walk(b,chain=()):
    yield b,chain
    for c in getattr(b,'children',[]) or []:
        yield from walk(c,chain+((getattr(b,'element_tag',None),(getattr(b,'element',None).get('class') if getattr(b,'element',None) is not None and hasattr(b.element,'get') else None) or ''),))
def txt(b):
    t=''
    for d in b.descendants():
        if hasattr(d,'text'): t+=d.text
    return t.strip()[:50]
for pi,pg in enumerate(doc.pages,1):
    root=pg._page_box.children[0]
    texts=[]
    for b,chain in walk(root):
        tag=getattr(b,'element_tag',None)
        if hasattr(b,'text') and b.text.strip():
            texts.append((b.position_y+b.height,b,chain))
            if b.position_x+b.width>R+TOL or b.position_x<L-TOL: over.append((pi,'text',b.text[:30],round(b.position_x+b.width-R,1)))
        if tag in('table','img'):
            x0=b.position_x;x1=x0+b.margin_width()
            if x1>R+TOL or x0<L-TOL: over.append((pi,tag,txt(b) if tag!='img' else 'img',round(max(x1-R,L-x0),1)))
        if tag=='table': seen[id(b.element)].append((pi,b))
    if not texts: continue
    texts.sort(key=lambda z:z[0]);chain=texts[-1][2]
    fill=(texts[-1][0]-20*96/25.4)/(215*96/25.4)
    if fill<0.45: sparse.append((pi,round(fill,2)))
    for t,cl in reversed(chain):
        if t in('h1','h2','h3','h4'): orph.append((pi,t,texts[-1][1].text[:50]));break
        if t=='p' and 'tcap' in cl: capend.append((pi,texts[-1][1].text[:50]));break
        if t in('td','th','li','figcaption'): break
split=[]
for k,v in seen.items():
    pgs=sorted(set(p for p,_ in v))
    if len(pgs)>1:
        rows=len(v[0][1].element.findall('.//tr')) if hasattr(v[0][1].element,'findall') else 0
        first=''.join(v[0][1].element.itertext()).strip()[:40]
        hmm=sum(b.height for _,b in v if b.__class__.__name__=='TableBox')*25.4/96
        split.append((pgs,rows,round(hmm),first[:28].replace(chr(10),'|')))
print('OVER',len(over));[print(' ',o) for o in over[:40]]
print('SPLIT',len(split));[print(' ',s) for s in split]
print('ORPHAN-HEADING',len(orph));[print(' ',o) for o in orph]
print('CAPTION-END',len(capend));[print(' ',o) for o in capend]
print('SPARSE(<45% filled)',len(sparse));print(' ',sparse)
