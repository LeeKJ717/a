import math
# ---------- 계산 6-1: Bigeum OSL 나이 = 등가선량 / 선량률 ----------
osl=[(142,3.30,0.19,21.40,0.10,6.5,0.4),(255,3.36,0.19,22.24,0.33,6.6,0.4),(355,3.23,0.18,22.82,0.12,7.1,0.4),
(453,3.25,0.18,24.38,0.35,7.5,0.4),(553,3.34,0.19,24.03,0.36,7.2,0.4),(654,3.31,0.19,24.32,0.34,7.4,0.4),
(734,3.28,0.19,25.34,0.45,7.7,0.5),(834,3.35,0.20,24.42,0.41,7.3,0.5),(955,3.18,0.19,25.18,0.29,7.9,0.5),
(1054,3.19,0.19,26.45,0.62,8.3,0.5),(1135,3.11,0.18,26.01,0.31,8.4,0.5),(1215,3.19,0.19,25.84,0.46,8.1,0.5),
(1323,3.35,0.20,33.54,0.75,10.0,0.6)]
print("[계산 6-1] OSL 나이")
for d,dr,se,De,sD,age,sa in osl:
    a=De/dr; rel=math.sqrt((se/dr)**2+(sD/De)**2); print(d,round(a,3),'paper',age,'err calc',round(a*rel,3),'paper',sa)
used=[o for o in osl if o[0] not in (453,834,1215)]
print("[계산 6-2] 구간 퇴적률(사용 10점), 오차 합성 대비")
for p,q in zip(used,used[1:]):
    dz=q[0]-p[0]; dt=q[5]-p[5]; s=math.sqrt(p[6]**2+q[6]**2)
    print(p[0],q[0],'dz',dz,'dt',round(dt,2),'rate',round(dz/dt,1) if dt>0 else None,'sigma_dt',round(s,3))
# ---------- 6-3 GY-1 14C 퇴적률 ----------
gy=[(363,1625,1819),(739,2846,2997),(889,4578,4825),(917,6863,7157),(1416,7956,8158),(1839,8595,8976),(2060,8649,8990),(2351,8764,9024),(2892,9785,10173)]
print("[계산 6-4] GY-1")
mid=[(d,(a+b)/2) for d,a,b in gy]
for p,q in zip(mid,mid[1:]): print(p[0],q[0],round((q[0]-p[0])/(q[1]-p[1]),4),'cm/yr')
print('REDFIT 간격',(10020-1658)/168)
# ---------- 6-4 Dongsuak ----------
zones=[(150,55,4350,1700),(55,37,1700,1150),(37,26,1150,700),(26,8,700,100),(8,0,100,0)]
print("[계산 6-6] Dongsuak")
for a,b,t0,t1 in zones: print(a,b,round((a-b)/(t0-t1),4),'cm/yr',round((t0-t1)/(a-b),1),'yr/cm')
print('평균 0.36 mm/yr 로 150cm',150/0.036)
print('[계산 6-10] TPIT demo',(10+5)/(10+5+20+15))
# ---------- 6-5 상관 신뢰구간 -> 유효 표본 ----------
def eff(r,lo,hi):
    z=math.atanh(r); zl,zh=math.atanh(lo),math.atanh(hi); se=(zh-zl)/(2*1.96); return z,se,3+1/se**2
print("[계산 6-11] Table2")
res={}
for name,r,lo,hi in [('Dongge<5.6',-0.543,-0.846,-0.024),('Dongge>5.6',0.05,-0.15,0.25),('WTP<5.6',0.16,-0.01,0.32),('WTP>5.6',0.35,0.04,0.60)]:
    z,se,n=eff(r,lo,hi); res[name]=(z,se); print(name,round(z,3),round(se,3),round(n,1))
for a,b in [('Dongge<5.6','Dongge>5.6'),('WTP<5.6','WTP>5.6')]:
    za,sa=res[a];zb,sb=res[b];d=zb-za;s=math.sqrt(sa**2+sb**2);zz=d/s;p=math.erfc(abs(zz)/math.sqrt(2));print(a,b,round(d,3),round(s,3),round(zz,2),round(p,3))
# ---------- 6-6 REDFIT 해상 ----------
T=10020-1658; L=T/2
print("[계산 6-12]",T,L,'Nyquist',2*49.8, 'cycles800 in T',T/800)
T2=4250; print('Dongsuak dt',T2/144,'Nyquist',2*T2/144)
for ev in ([4.7,4.2,3.7,3.2,2.8,2.4],[4.2,3.7,3.2,2.8,2.3,1.8,1.2,0.6],[9.8,9.2,8.2,7.3,5.3]):
    iv=[round((a-b)*1000) for a,b in zip(ev,ev[1:])]; print(ev,iv,sum(iv)/len(iv))
# ---------- 6-7 Hulun ----------
print("[계산 6-7] Hulun")
iv={'sand':(4430,3860),'ostr':(4200,3420),'cheno':(4300,3830),'map':(4240,3750),'pca':(4210,3840)}
for k,(a,b) in iv.items(): print(k,a-b)
common=(min(a for a,b in list(iv.values())[:4]),max(b for a,b in list(iv.values())[:4])); print('4 proxies common',common,common[0]-common[1])
for nm,mu,sd,ex,av in [('sand',7.5,6.3,21.1,15.5),('ostr',22,22,70,44),('cheno',42.9,10.7,60.2,56.5),('map',297.3,20.3,264.0,272.3),('pca',0,1.02,1.71,1.54)]:
    print(nm,'thr',round(mu+sd if nm!='map' else mu-sd,2),'z ext',round((ex-mu)/sd,2),'z avg',round((av-mu)/sd,2))
ev=[0.745,0.154,0.979-0.745-0.154]; print('PCA',[round(x*4,3) for x in ev+[1-0.979]],round(0.745+0.154,3))
for c14,c in [(3222,2537),(3630,2945),(4034,3349),(4575,3890),(5304,4619)]: print(c14-685,c)
cal=[(59.5,2480,2650),(69.5,2970,3220),(79.5,3470,3690),(89.5,4230,4430),(101.5,5290,5470)]
m=[(d,(a+b)/2) for d,a,b in cal]
for p,q in zip(m,m[1:]): print(p[0],q[0],round((q[0]-p[0])/(q[1]-p[1])*1000,2),'cm/ka')
# ---------- 6-8 신농동굴 U-Th ----------
print("[계산 6-8] U-Th")
l230=9.1705e-6;l234=2.82206e-6;l238=1.55125e-10
def ratio(T,d234):
    return 1-math.exp(-l230*T)+(d234/1000)*(l230/(l230-l234))*(1-math.exp(-(l230-l234)*T))
def solve(R,d234,f=ratio):
    lo,hi=0,5e5
    for _ in range(200):
        m=(lo+hi)/2
        if f(m,d234)<R: lo=m
        else: hi=m
    return lo
th232=[1025,2511,984,132,195,1814,151,1169,82,66,225,1031,56,873,2221]
u238=[2063,1146,1757,2617,2535,3572,1122,1035,2976,4619,4640,2993,6380,4436,6886]
r32=[1388,320,1302,14960,10103,1560,6034,763,31024,61740,19262,2810,114548,5189,3273]
d234=[235.5,235.3,233.6,243.2,252.1,247.1,265.5,279.4,264.4,268.8,290.3,312.9,322.2,323.7,331.7]
R=[0.0418,0.0426,0.0442,0.0457,0.0472,0.0481,0.0492,0.0522,0.0519,0.0532,0.0566,0.0587,0.0608,0.0619,0.0640]
unc=[3736,3820,3979,4076,4187,4279,4319,4540,4560,4668,4883,4980,5120,5216,5363]
cor=[3668,3707,3897,4007,4117,4268,4248,4452,4491,4600,4814,4910,5052,5149,5294]
dist=[3,7,12,17,32,36,44,51,56,75,120,143,190,227,317]
for i in range(15):
    T=solve(R[i],d234[i])
    # 보정: 232Th/238U 원자비
    a32_38=(th232[i]*1e-12/232.038)/(u238[i]*1e-9/238.05)
    def f(T,d,i=i):
        det=4.4e-6*a32_38*math.exp(-l230*T)*(l230/l238)
        return ratio(T,d)+det   # 측정비 = 진짜비 + 쇄설 기여
    Tc=solve(R[i],d234[i],lambda T,d: f(T,d))
    print(dist[i],'T',round(T,0),'paper unc',unc[i],'diff',round(T-unc[i],0),'| corr',round(Tc,0),'paper',cor[i],'diff',round(Tc-cor[i],0),'| 232Th/238U',round(a32_38,6),'check 230/232',round(1/ (1) ,0) if False else '')
print('[계산 6-9] 성장률')
t=[(3,3668),(7,3707),(12,3897),(17,4007),(32,4117),(36,4268),(44,4248),(51,4452),(56,4491),(75,4600),(120,4814),(143,4910),(190,5052),(227,5149),(317,5294)]
for p,q in zip(t,t[1:]): 
    dt=q[1]-p[1]; print(p[0],q[0],'dt',dt,'rate',round((q[0]-p[0])/dt,3) if dt>0 else 'reversal(<=0)','mm/yr')
print('mean',(317-3)/(5294-3668),'4.5-3.57: n/a')
# ---------- 6-10 Liu & Hu 강수 ----------
print("[계산 6-13] rainfall")
f=lambda d: 189.08*d+1217.4
for d in (1.3,-0.5,0.26,1.0,0.0): print(d,round(f(d),1))
print('drop',f(1.3)-f(-0.5),'central avg',f(0.26),'present 1380 diff',1380-1200)
print('err',math.sqrt(0.08**2+0.15**2+0.62**2+0.35**2),'rain err',189.08*0.53)
print('350/3.3',350/3.3,'7%/permil 350/ (1380) ',350/1380)
print('R2 0.79->r',math.sqrt(0.79),'0.62',math.sqrt(0.62),'0.71',math.sqrt(0.71),'0.72',math.sqrt(0.72),'0.47',math.sqrt(0.47),'0.56',math.sqrt(0.56))
# n=219 의 r 유의성
for r2 in (0.47,0.56):
    r=math.sqrt(r2); t=r*math.sqrt(217)/math.sqrt(1-r2); print('n=219',r2,round(t,2))
print('1950-1990 mm→', 1380-f(0.26))
# ---------- 6-11 시연값(이론 박스) ----------
print("[시연값: 이론 박스]")
print('OSL demo',20/4, 5*math.sqrt(0.01**2+0.05**2))
print('rate demo',(160-100)/(5-3),1/30*1000)
R=ratio(1000,100); print('UTh demo R',R, 1-math.exp(-l230*1000), (100/1000)*(l230/(l230-l234))*(1-math.exp(-(l230-l234)*1000)))
print('pollen demo',(120+60)/300, 300/50*10000/1)
z=math.atanh(0.5); se=1/math.sqrt(28-3); print('CI demo',z,se,math.tanh(z-1.96*se),math.tanh(z+1.96*se))
print('nyq demo',2*50,5000/500)
print('Δ demo',189.08*0.5+1217.4, (1380-1217.4)/189.08, (1200-1217.4)/189.08)
print('z demo',(13.4-10)/2)
def pdf(t,m,s): return math.exp(-0.5*((t-m)/s)**2)/(s*math.sqrt(2*math.pi))
for t in (1000,1050,1100,1200): print('SPD',t,round(sum(pdf(t,m,50) for m in (1000,1050,1200)),5))
# ---------- 6-12 GY-1 8.2ka 위치 ----------
print("[계산 6-3, 6-5] 8.2 ka 위치")
d=1416+(8200-8057)/(8785.5-8057)*423; print('8.2ka depth',d, 'dated gap cm',1839-1416,'yr',8785.5-8057)
for a in (8000,8400): print(a,1416+(a-8057)/(8785.5-8057)*423)
print('Bigeum 8.2 depth',955+(8.2-7.9)/(8.3-7.9)*99,'unc cm for 0.5 ka',0.5*247.5,'event 150yr cm',0.15*247.5)
print('AMS vs OSL',(12590+12240)/2-10000, 1340-1323)
print('Bigeum rate OSL 1054-1135 and sea level layers n/a')
# n_eff for 10-yr moving average
r=math.sqrt(0.47); ne=22; print('eff n',ne, r*math.sqrt(ne-2)/math.sqrt(1-r*r))
print('Δ Greenland',350/3.3, 350/3.3*math.sqrt((1.0/3.3)**2))
print('0.53 trial',math.sqrt(0.08**2+0.15**2+0.35**2+(0.62/math.sqrt(3))**2))
print('Greenland 7% =',0.07*1380)
r=math.sqrt(0.56); print('MgCa n_eff22 t',r*math.sqrt(20)/math.sqrt(1-r*r),'n219',r*math.sqrt(217)/math.sqrt(1-r*r))
# ---------- 6-13 4.2 ka 구간 겹침 ----------
print("[계산 6-14] 4.2 ka 구간 겹침")
dry={'Hulun':(4210,3840),'Dali':(4450,3750),'Daihai':(4060,3690),'Dongge':(4400,3950)}
wet={'SN17':(4200,3900),'Xianglong':(4300,3800)}
def common(d): o=min(a for a,b in d.values()); y=max(b for a,b in d.values()); return o,y,o-y
print('dry',common(dry),'wet',common(wet))
print('Hulun vs SN17',min(4210,4200)-max(3840,3900))
print('Hulun vs Dongge',min(4210,4400)-max(3840,3950))
print('Hulun len',4210-3840,'SN17 wet len',4200-3900)
