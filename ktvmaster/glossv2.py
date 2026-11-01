#!/usr/bin/env python3
# glossv2: 중국 지명 한자음(漢字, 중국발음) 병기. 이름은 모든 줄에서 한자음으로 바꾸고, 병기는 장별 본문 첫 등장에만 넣는다.
import re,glob,os,sys
D=sys.argv[1]; WRITE=len(sys.argv)>2 and sys.argv[2]=='write'
REN=[('랴오시','요서'),('샤자뎬','하가점'),('양쯔강','장강'),('황허','황하'),('화이허','회하'),('산둥','산동'),('장쑤','강소'),('허난','하남'),('허베이','하북'),
     ('랴오닝','요녕'),('랴오둥','요동'),('간쑤','감숙'),('칭하이','청해'),('톈산','천산'),('싱룽거우','흥륭구'),('상샤자뎬','상하가점'),('샤오링하','소릉하'),
     ('둥거','동가'),('허샹','화상'),('뤄촨','낙천'),('쥐옌','거연'),('둥다오','동도')]
# 상하가점은 하가점보다 먼저 처리해야 한다
REN.sort(key=lambda x:-len(x[0]))
ANN=[('상하가점','上夏家店','상샤자뎬'),('하가점','夏家店','샤자뎬'),('소하연','小河沿','샤오허옌'),('소하서','小河西','샤오허시'),('홍산','紅山','훙산'),('적봉','赤峰','츠펑'),
     ('흥륭와','興隆洼','싱룽와'),('흥륭구','興隆溝','싱룽거우'),('황하','黃河','황허'),('장강','長江','창장'),('화북','華北','화베이'),('내몽골','內蒙古','네이멍구'),
     ('이도정자','二道井子','얼다오징쯔'),('요서','遼西','랴오시'),('회하','淮河','화이허'),('산동','山東','산둥'),('강소','江蘇','장쑤'),('하남','河南','허난'),('하북','河北','허베이'),
     ('요녕','遼寧','랴오닝'),('요동','遼東','랴오둥'),('감숙','甘肅','간쑤'),('청해','靑海','칭하이'),('천산','天山','톈산'),('소릉하','小凌河','샤오링허'),
     ('동가','董哥','둥거'),('화상','和尚','허샹'),('낙천','洛川','뤄촨'),('거연','居延','쥐옌'),('동도','東島','둥다오')]
def verfiles(pat):
    b={}
    for p in glob.glob(D+pat):
        m=re.match(r'(.+)-v(\d+)\.md$',os.path.basename(p))
        if m and (m.group(1) not in b or int(m.group(2))>b[m.group(1)][0]): b[m.group(1)]=(int(m.group(2)),p)
    return b
def isprose(s): return not (s.startswith('|') or s.startswith('#') or s.startswith('```') or s.startswith('!['))
tot=0
for sub,annot in (('/ms/ch*-v*.md',True),('/ms/front/*-v*.md',False)):
    for key,(v,p) in sorted(verfiles(sub).items()):
        if key.endswith('-calc') : continue
        t=open(p,encoding='utf-8').read(); i=t.find('## 참고문헌'); body,ref=(t[:i],t[i:]) if i>=0 else (t,'')
        lines=body.split('\n'); fence=False; n=0; renamed=set()
        for k,l in enumerate(lines):
            if l.startswith('```'): fence=not fence
            if fence: continue
            for old,new in REN:
                if old in l: lines[k]=l=l.replace(old,new); n+=1; renamed.add(new)
        if annot:
            fence=False; fl=[]
            for l in lines:
                if l.startswith('```'): fence=not fence
                fl.append(fence)
            SAFE={'상하가점','하가점','소하연','소하서','홍산','적봉','흥륭와','이도정자','황하','장강','화북','내몽골','요서'}
            for new,h,py in ANN:
                if new not in SAFE and new not in renamed: continue
                for k,l in enumerate(lines):
                    if fl[k] or not isprose(l): continue
                    j=l.find(new)
                    if j<0: continue
                    if l[j+len(new):j+len(new)+1]!='(' and not (j>0 and re.match(r'[가-힣]',l[j-1]) and new in ('하가점','동가','화상','천산','소릉하','낙천','거연','동도','화북')):
                        lines[k]=l[:j+len(new)]+'(%s, %s)'%(h,py)+l[j+len(new):]; n+=1
                    break
        if n:
            tot+=n
            print(os.path.relpath(p,D),'->',n)
            if WRITE: open(os.path.join(os.path.dirname(p),'%s-v%d.md'%(key,v+1)),'w',encoding='utf-8').write('\n'.join(lines)+ref)
print('합계',tot)
