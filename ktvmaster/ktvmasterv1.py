#!/usr/bin/env python3
# ktvmasterv1: 1~4권 원고·코드·자료·근거논문·파싱결과를 한 DB로 통합
import os, re, sqlite3, zlib, hashlib, glob, time
R='/home/claude'; OUT='/home/claude/out/ktvmaster/ktvmaster.sqlite'
if os.path.exists(OUT): os.remove(OUT)
c=sqlite3.connect(OUT)
c.executescript('''
create table meta(k text primary key, v text);
create table files(id integer primary key, vol int, rel text, kind text, bytes int, sha256 text, zdata blob, note text);
create index fi on files(vol,rel);
create table refs(id integer primary key, vol int, chap text, srcfile text, entry text, firstauthor text, year text, doi text, needcheck int);
create table papers(key text primary key, firstauthor text, year text, doi text, entry text, vols text, chaps text, status text);
create table pdfs(vol int, mode text, ver text, file text, bytes int, sha256 text, pages int, src text);
create table pages(vol int, ver text, page int, nchar int, text text);
create table captions(vol int, ver text, kind text, num text, title text, page int);
create table chapters(vol int, ver text, chap text, title text, page int);
create table msrows(vol int, file text, chap text, version int, islatest int, nchar int, text text);
''')
BOOKS={1:'book',2:'book2',3:'book3',4:'book4'}
SKIP={'build','out','cover','fig','preview','gpucover','logo','__pycache__','bundle','stage','.git','parts'}
KIND={'.md':'text','.py':'code','.sh':'code','.txt':'text','.csv':'data','.json':'data','.geojson':'data','.xlsx':'data','.pkl':'data','.sqlite':'db','.14c':'data','.png':'image','.jpg':'image','.pdf':'doc'}
LIM=45*1024*1024; n=0; skipped=[]
for v,d in BOOKS.items():
    base=os.path.join(R,d)
    for dp,dn,fn in os.walk(base):
        dn[:]=[x for x in dn if x not in SKIP]
        rel0=os.path.relpath(dp,base)
        for f in fn:
            p=os.path.join(dp,f); rel=os.path.normpath(os.path.join(rel0,f))
            if rel.startswith('vol2'+os.sep): continue
            ext=os.path.splitext(f)[1].lower()
            if ext=='.sqlite' and f.startswith('ktv1bookdb-v') and f!='ktv1bookdb-v15.sqlite': continue
            if ext in ('.png','.jpg') and 'plan' in rel: continue
            sz=os.path.getsize(p)
            if sz>LIM: skipped.append((v,rel,sz)); continue
            b=open(p,'rb').read()
            c.execute('insert into files(vol,rel,kind,bytes,sha256,zdata) values(?,?,?,?,?,?)',(v,rel,KIND.get(ext,'other'),sz,hashlib.sha256(b).hexdigest(),zlib.compress(b,9))); n+=1
# 제3권 8장 He 2022 자료표 등 별도 자료
for p in glob.glob(R+'/data/hz22/*'):
    b=open(p,'rb').read()
    c.execute('insert into files(vol,rel,kind,bytes,sha256,zdata,note) values(?,?,?,?,?,?,?)',(3,'data/hz22/'+os.path.basename(p),'data',len(b),hashlib.sha256(b).hexdigest(),zlib.compress(b,9),'He 2022 자료표(ESSD 14, 4777), Zenodo 10.5281/zenodo.6669730'))
for p in glob.glob(R+'/out/errata/*')+glob.glob(R+'/out/*.py')+glob.glob(R+'/*.py'):
    b=open(p,'rb').read()
    c.execute('insert into files(vol,rel,kind,bytes,sha256,zdata,note) values(?,?,?,?,?,?,?)',(0,'shared/'+os.path.basename(p),'code' if p.endswith('.py') else 'text',len(b),hashlib.sha256(b).hexdigest(),zlib.compress(b,9),'공통'))
# 참고문헌 추출(장별 최신판)
def latest(d):
    best={}
    for p in glob.glob(d+'/ms/ch*-v*.md'):
        m=re.match(r'(ch\d+)-v(\d+)\.md$',os.path.basename(p))
        if m and (m.group(1) not in best or int(m.group(2))>best[m.group(1)][0]): best[m.group(1)]=(int(m.group(2)),p)
    return best
for v,d in BOOKS.items():
    for ch,(ver,p) in sorted(latest(os.path.join(R,d)).items()):
        t=open(p,encoding='utf-8').read()
        m=re.search(r'^## 참고문헌\s*$(.*?)(?=^## |\Z)',t,re.S|re.M)
        if not m: continue
        for e in re.split(r'\n\s*\n',m.group(1).strip()):
            e=e.strip()
            if len(e)<20: continue
            fa=re.match(r'([^,(]+)',e); yr=re.search(r'\((\d{4}[a-z]?|n\.d\.)\)',e); dm=re.search(r'10\.\d{4,9}/[^\s)]+',e)
            c.execute('insert into refs(vol,chap,srcfile,entry,firstauthor,year,doi,needcheck) values(?,?,?,?,?,?,?,?)',(v,ch,os.path.basename(p),e,fa.group(1).strip() if fa else '',yr.group(1) if yr else '',dm.group(0).rstrip('.') if dm else '',1 if '확인 필요' in e else 0))
# 통합 논문표
rows=c.execute('select vol,chap,entry,firstauthor,year,doi,needcheck from refs').fetchall(); P={}
for v,ch,e,fa,yr,doi,nc in rows:
    k=doi.lower() if doi else (re.sub(r'\W+','',fa.lower())+yr+re.sub(r'\W+','',e[e.find(')')+1:][:40].lower()))
    q=P.setdefault(k,[fa,yr,doi,e,set(),set(),0]); q[4].add(str(v)); q[5].add('%d:%s'%(v,ch)); q[6]|=nc
for k,(fa,yr,doi,e,vs,cs,nc) in P.items():
    c.execute('insert into papers values(?,?,?,?,?,?,?,?)',(k,fa,yr,doi,e,','.join(sorted(vs)),','.join(sorted(cs)),'서지 확인 필요' if nc else ''))
# 파싱 DB(PDF 쪽·캡션·장·원고) 통합: v1(제1·2·4권, 제3권 v4) + v2(제3권 v5)
for src in (R+'/out/ktvparsev2/ktvparse.sqlite',R+'/out/ktvparsev1/ktvparse.sqlite'):
    s=sqlite3.connect(src); tag=os.path.basename(os.path.dirname(src)); W='' if tag=='ktvparsev2' else ' where vol=3'
    for r in s.execute('select vol,mode,ver,file,bytes,sha256,pages from pdfs'+W): c.execute('insert into pdfs values(?,?,?,?,?,?,?,?)',r+(tag,))
    for r in s.execute('select vol,ver,page,nchar,text from pages'+W): c.execute('insert into pages values(?,?,?,?,?)',r)
    for r in s.execute('select vol,ver,kind,num,title,page from captions'+W): c.execute('insert into captions values(?,?,?,?,?,?)',r)
    for r in s.execute('select vol,ver,chap,title,page from chapters'+W): c.execute('insert into chapters values(?,?,?,?,?)',r)
    if tag=='ktvparsev1':
        for r in s.execute('select vol,file,chap,version,islatest,nchar,text from ms'): c.execute('insert into msrows values(?,?,?,?,?,?,?)',r)
c.execute('create index pgi on pages(vol,ver,page)')
c.executemany('insert into meta values(?,?)',[('built',time.ctime()),('name','ktvmaster v1'),('series','1만 년의 기후와 땅 1~4권'),
 ('vols','1 동아시아 v23 / 2 방법편 v1 / 3 유라시아 v5 / 4 지구 v2'),('rule','근거 논문 확보 필요/원문 확인 필요/서지 확인 필요는 status·entry에 그대로 보존'),
 ('files_skipped_over_30MB',repr(skipped)),('note','그림 PNG·표지·빌드 산출물은 코드와 자료로 재생성. PDF는 pdfs 표의 sha256으로 백업본과 대조'),('crawl','z840 crawl/ktvcrawl.sqlite는 ktvmergev1.py로 병합')])
c.commit(); c.execute('vacuum')
for t in ('files','refs','papers','pdfs','pages','captions','chapters','msrows'): print(t,c.execute('select count(*) from '+t).fetchone()[0])
print('integrity',c.execute('pragma integrity_check').fetchone()[0],'skipped',skipped)
