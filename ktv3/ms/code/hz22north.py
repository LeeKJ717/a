import pandas as pd
d=pd.read_pickle('/home/claude/data/hz22/hz22.pkl')
for c in 'SPOWG': d[c]=pd.to_numeric(d[c],errors='coerce').fillna(0)
d['mil']=d.S+d.P
print('rows',len(d),'sites',d.site.nunique(),'age NaN',d.age.isna().sum(),'lat range',d.lat.min(),d.lat.max())
print('rows with mil>0',(d.mil>0).sum(),'rows with any crop>0',((d.S+d.P+d.O+d.W+d.G)>0).sum())
m=d[d.mil>0]
anyc=d[(d.S+d.P+d.O+d.W+d.G)>0]
print('max lat any crop',anyc.lat.max(),'max lat millet',m.lat.max())
print('bin lo hi rows sites maxlat site age n41')
for lo in range(2000,10000,500):
    g=m[(m.age>=lo)&(m.age<lo+500)]
    if len(g)==0: continue
    t=g.sort_values('lat',ascending=False).iloc[0]
    print(lo,lo+499,len(g),g.site.nunique(),round(t.lat,2),t.site,int(t.age),int((g.lat>=41).sum()))
hi=m[m.lat>=41].sort_values('age')
print('rows >=41N',len(hi),'sites',hi.site.nunique())
a=hi[hi.age>=5000].age.min(); 
older=hi[hi.age>=5000]; younger=hi[hi.age<5000]
print('older>=41N: ages',older.age.min(),older.age.max(),'n',len(older))
print('younger>=41N: ages',younger.age.min(),younger.age.max(),'n',len(younger))
gap=(older.age.min(),younger.age.max())
print('gap years',older.age.min()-younger.age.max(),'between',older.age.min(),'(',older.sort_values('age').iloc[0].site,') and',younger.age.max(),'(',younger.sort_values('age').iloc[-1].site,')')
# Liaoxi rows in the gap
lx=d[(d.region=='Liaoxi region')]
print('Liaoxi rows',len(lx),'ages',lx.age.min(),lx.age.max())
w=lx[(lx.age<5400)&(lx.age>3731)]
print('Liaoxi rows strictly between 3731 and 5400',len(w)); print(w[['site','lat','age','culture','mil']].to_string())
# chapter event window
for lo,hi_ in [(3900,4200)]:
    g=m[(m.age>=lo)&(m.age<=hi_)]
    t=g.sort_values('lat',ascending=False).iloc[0]
    print('window',lo,hi_,'rows',len(g),'sites',g.site.nunique(),'max',t.lat,t.site,int(t.age))
    allg=d[(d.age>=lo)&(d.age<=hi_)]
    print(' all rows in window',len(allg),'by region',allg.region.value_counts().to_dict())
# rows by region before/after
for nm,(lo,hi_) in {'5000-5400':(5000,5400),'4000-4999':(4000,4999),'3731-3999':(3731,3999)}.items():
    g=d[(d.age>=lo)&(d.age<=hi_)]
    print(nm,len(g),g.region.value_counts().to_dict())
