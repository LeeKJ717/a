#!/usr/bin/env python3
"""ktv3extract v1 - ktv_db에서 3권(유라시아) 주제 논문의 서지와 초록만 뽑아 ~/ktv3papers-v1.jsonl.gz로 저장. 읽기 전용, PDF는 건드리지 않는다."""
import sqlite3, re, json, gzip, os
DB = '/data/safe/dball2/ktv_db/ktv_db.sqlite'
c = sqlite3.connect('file:' + DB + '?mode=ro', uri=True); c.row_factory = sqlite3.Row
cols = [r[1] for r in c.execute('pragma table_info(papers)')]
print('papers 열:', cols)
want = [k for k in cols if k not in ('fulltext', 'pdf', 'blob', 'pdf_blob', 'text')]
T = {
 'mongol': r'Mongolia|Mongolian Plateau|Gobi|Khangai|Hovsgol|Khovsgol|Inner Mongolia|Hulun|Daihai',
 'siberia': r'Siberia|Baikal|Altai|Yenisei|Lena\b|Taimyr|Yakut|Tuva|Amur|Okhotsk',
 'central': r'Central Asia|Pamir|Tian ?[Ss]han|Tianshan|Kyrgyz|Kazakh|Uzbek|Aral|Tarim|Taklamakan|Issyk|Ferghana|Fergana|Turkmen|Tajik',
 'steppe': r'Scythian|Xiongnu|Hun[s ]|steppe|nomad|Yamnaya|Sintashta|Andronovo|Afanasievo|pastoral|Okunevo|Chemurchek|Karasuk|Slab[- ]grave',
 'climate': r'Westerlies|Caspian|Black Sea|Anatolia|Holocene.*(Eurasia|Asia)|(Eurasia|Asia).*Holocene|4\.2 ?ka|8\.2 ?ka|Little Ice Age|Medieval Climate',
 'dna': r'ancient (DNA|genom)|aDNA|paleogenom|haplogroup|Y-chromosome|population (history|turnover)|Transeurasian|Tungusic|Turkic|Mongolic',
 'migration': r'Late Antiquity|Migration Period|Hungary|Carpathian|Pannonia|Avar|Magyar|Hungarian|Germanic|Goth',
 'millet': r'millet|Panicum|Setaria|Hordeum|wheat.*(spread|dispersal)|domestication',
 'history': r'Rashid|Abu.?l.?Ghazi|Shaybani|Bichurin|Potanin|Valikhanov|Secret History|Book of Wei|Shiji|Tang dynasty|Turkic Khaganate|Kipchak|Cuman',
}
rx = {k: re.compile(v, re.I) for k, v in T.items()}
out = os.path.expanduser('~/ktv3papers-v1.jsonl.gz'); n = 0; cnt = {k: 0 for k in T}
with gzip.open(out, 'wt', encoding='utf-8') as f:
    for r in c.execute('select %s from papers' % ','.join('"%s"' % k for k in want)):
        d = dict(r); s = (d.get('title') or '') + ' ' + (d.get('abstract') or '')
        tags = [k for k, x in rx.items() if x.search(s)]
        if not tags: continue
        d['tags'] = tags; n += 1
        for k in tags: cnt[k] += 1
        if d.get('abstract'): d['abstract'] = d['abstract'][:3000]
        f.write(json.dumps(d, ensure_ascii=False) + '\n')
print('추출', n, '편 ->', out, os.path.getsize(out) // 1024, 'KB'); print(cnt)
