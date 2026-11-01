#!/usr/bin/env python3
# ktvmergev1: z840 크롤링 DB(works)를 ktvmaster에 병합하고, 책에 인용된 논문(papers.doi)과 대조
import sqlite3, sys
M='/data/safe/dball2/ktv_db/master/ktvmaster.sqlite'; C='/data/safe/dball2/ktv_db/crawl/ktvcrawl.sqlite'
m=sqlite3.connect(M); m.execute('attach ? as k',(C,))
m.executescript('''drop table if exists crawlworks;
create table crawlworks as select id,doi,title,year,authors,journal,abstract,oaurl,pdfsha,pdf,query,fetched from k.works;
create index if not exists cwdoi on crawlworks(doi);
drop table if exists crawllog; create table crawllog as select * from k.log;''')
m.execute("update crawlworks set doi=lower(replace(doi,'https://doi.org/','')) where doi is not null")
m.executescript('''drop table if exists crawlcited;
create table crawlcited as select w.id,w.doi,w.title,p.vols,p.chaps from crawlworks w join papers p on lower(p.doi)=w.doi;''')
m.commit()
for t in ('crawlworks','crawlcited'): print(t, m.execute('select count(*) from '+t).fetchone()[0])
print('pdf', m.execute('select count(*) from crawlworks where pdf is not null').fetchone()[0])
