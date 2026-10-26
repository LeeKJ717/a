import re,html,sys,markdown
from weasyprint import HTML
src,out=sys.argv[1],sys.argv[2]
t=open(src,encoding='utf-8').read()
n=[0]
def cap(m):
    n[0]+=1
    return f'<p class="cap"><b>표 {n[0]}.</b> {html.escape(m.group(1))}</p>'
t=re.sub(r'^\{\{T:(.*?)\}\}$',cap,t,flags=re.M)
h=markdown.markdown(t,extensions=['tables'])
toc=[];c=[0]
def hid(m):
    c[0]+=1;i=f'h{c[0]}'
    toc.append((m.group(1),i,m.group(2)))
    return f'<h{m.group(1)} id="{i}">{m.group(2)}</h{m.group(1)}>'
h=re.sub(r'<h([12])>(.*?)</h\1>',hid,h)
tocs=''.join(f'<a class="l{l}" href="#{i}">{html.escape(re.sub("<.*?>","",x))}</a>' for l,i,x in toc[1:])
title=toc[0][2]
CSS='''@page{size:182mm 257mm;margin:20mm 16mm 22mm 36.4mm;@bottom-center{content:counter(page);font:9pt "Noto Serif CJK KR",serif}}
@page:first{@bottom-center{content:none}}
body{font:10pt/1.7 "Noto Serif CJK KR",serif;word-break:keep-all}
h1{font:700 17pt/1.4 "Noto Sans CJK KR",sans-serif;margin:30mm 0 6mm}
h2{font:700 12.5pt/1.5 "Noto Sans CJK KR",sans-serif;margin:7mm 0 3mm;break-after:avoid}
h3{font:700 10.5pt/1.5 "Noto Sans CJK KR",sans-serif;margin:4mm 0 2mm;break-after:avoid}
p{margin:0 0 2.5mm}
.sub{font:10pt "Noto Sans CJK KR",sans-serif;color:#444}
.cap{font:700 8.5pt/1.4 "Noto Sans CJK KR",sans-serif;margin:4mm 0 1.5mm;break-after:avoid}
table{border-collapse:collapse;width:100%;font:8pt/1.4 "Noto Sans CJK KR",sans-serif;margin-bottom:4mm}
th,td{border:0.4pt solid #888;padding:1.2mm 1.5mm;vertical-align:top;word-break:break-all}
th{background:#e8e8e8}tr{break-inside:avoid}
.toc{break-after:page}.toc h2{margin-top:0}
.toc a{display:block;text-decoration:none;color:#000;font:9pt/1.9 "Noto Sans CJK KR",sans-serif}
.toc a.l2{padding-left:0;font-weight:700}
.toc a::after{content:leader('.') target-counter(attr(href),page)}
.refs p,.refp{padding-left:8mm;text-indent:-8mm;font-size:9pt;line-height:1.5;word-break:break-all}
'''
h1=re.search(r'<h1.*?</h1>',h,re.S).group(0)
m=re.search(r'<p>(시리즈 구성안 v1[^<]*)</p>',h);sub=f'<p class="sub">{m.group(1)}</p>' if m else ''
body=h.replace(h1,'',1)
if m: body=body.replace(m.group(0),'',1)
h1=h1+sub
# 참고문헌 이후 단락은 내어쓰기
head,_,refs=body.partition('<h2 id="h')
doc=f'<html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{h1}<div class="toc"><h2 style="break-before:avoid">차례</h2>{tocs}</div>{body}</body></html>'

HTML(string=doc).write_pdf(out)
print(out)
