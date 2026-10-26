import re,html,markdown,sys
from weasyprint import HTML
t=open('vol2/vol2-toc-v1.md',encoding='utf-8').read()
n=[0]
def g(m):
    n[0]+=1; return f'\n<p class="tcap"><b>표 {n[0]}.</b> {html.escape(m.group(1))}</p>\n'
t=re.sub(r'\{\{T:(.*?)\}\}',g,t)
h=markdown.markdown(t,extensions=['tables'])
css='''@page{size:182mm 257mm;margin:20mm 16mm 22mm 36.4mm;@bottom-center{content:counter(page);font:9pt "Noto Serif CJK KR"}}
body{font:10.5pt/1.8 "Noto Serif CJK KR";word-break:keep-all}h1{font:700 17pt/1.4 "Noto Sans CJK KR"}h2{font:700 13pt "Noto Sans CJK KR";margin:7mm 0 3mm}
.tcap{font:9pt "Noto Sans CJK KR";margin:4mm 0 1.5mm}table{border-collapse:collapse;font:8pt/1.5 "Noto Sans CJK KR";width:100%}th,td{border:.4pt solid #666;padding:1.2mm 1.6mm;vertical-align:top;text-align:left}th{background:#eee}tr{break-inside:avoid}'''
HTML(string=f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{h}</body></html>').write_pdf('vol2/vol2-toc-v1.pdf')
