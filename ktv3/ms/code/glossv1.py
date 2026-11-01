#!/usr/bin/env python3
# glossv1: 한자음(漢字, 중국발음) 병기 적용. 장별 첫 등장에만 넣고 참고문헌·표·제목 줄은 건드리지 않는다.
import re,glob,os,sys
D=sys.argv[1]; WRITE=len(sys.argv)>2 and sys.argv[2]=='write'
G=[('소하연','小河沿','샤오허옌'),('소하서','小河西','샤오허시'),('하가점','夏家店','샤자뎬'),('홍산','紅山','훙산'),('적봉','赤峰','츠펑'),
   ('흥륭와','興隆洼','싱룽와'),('황하','黃河','황허'),('장강','長江','창장'),('화북','華北','화베이'),('내몽골','內蒙古','네이멍구'),('이도정자','二道井子','얼다오징쯔')]
REN=[('랴오시','요서','遼西','랴오시'),('샤자뎬','하가점','夏家店','샤자뎬')]   # 중국식으로만 적힌 것을 한자음으로 바꿈
def latest():
    b={}
    for p in glob.glob(D+'/ms/ch*-v*.md'):
        m=re.match(r'(ch\d+)-v(\d+)\.md$',os.path.basename(p))
        if m and (m.group(1) not in b or int(m.group(2))>b[m.group(1)][0]): b[m.group(1)]=(int(m.group(2)),p)
    return b
tot=0
for ch,(v,p) in sorted(latest().items()):
    t=open(p,encoding='utf-8').read(); i=t.find('## 참고문헌'); body,ref=(t[:i],t[i:]) if i>=0 else (t,'')
    lines=body.split('\n'); n=0
    def prose(k): s=lines[k]; return not (s.startswith('|') or s.startswith('#') or s.startswith('```') or s.startswith('!['))
    for k0,k1,h,py in [(a,a,b,c) for a,b,c,_ in [(r[0],r[2],r[3],0) for r in REN]]: pass
    for old,new,h,py in REN:
        lines=[l.replace(old,new) if not l.startswith('```') else l for l in lines]
    done=set()
    for old,h,py in G:
        for k in range(len(lines)):
            if not prose(k): continue
            j=lines[k].find(old)
            if j<0: continue
            after=lines[k][j+len(old):j+len(old)+1]
            if after=='(' : done.add(old); break
            lines[k]=lines[k][:j+len(old)]+'(%s, %s)'%(h,py)+lines[k][j+len(old):]; n+=1; break
    # 요서·하가점은 REN으로 한자음화한 뒤 첫 등장에 병기
    for old,h,py in [('요서','遼西','랴오시')]:
        for k in range(len(lines)):
            if not prose(k): continue
            j=lines[k].find(old)
            if j>=0:
                if lines[k][j+2:j+3]!='(': lines[k]=lines[k][:j+2]+'(%s, %s)'%(h,py)+lines[k][j+2:]; n+=1
                break
    out='\n'.join(lines)+ref
    if n and WRITE:
        q=os.path.join(D,'ms','%s-v%d.md'%(ch,v+1)); open(q,'w',encoding='utf-8').write(out)
    if n: print(ch,'v%d'%v,'->',n,'곳'); tot+=n
print('합계',tot)
