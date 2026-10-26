# ch08 calculations (values from Lu et al. 2007 Table 1; Stevens 2018 etc. appended below)
import math
L=[("IEE208",0.1,3.48,3.6,1.0),("IEE209",0.3,3.60,3.0,0.8),("IEE210",0.5,3.57,4.3,1.2),("IEE211",0.8,3.66,29.2,8.0),
("IEE213",1.4,2.97,34.6,11.7),("IEE214",1.8,3.22,51.9,16.1),("IEE215",2.0,3.44,79.8,23.2),("IEE216",2.3,3.55,93.5,26.4),("IEE217",2.6,3.45,96.5,28.0),
("IEE218",3.0,3.57,113,31.6),("IEE219",3.5,3.35,110,32.8),("IEE220",4.0,3.34,124,37.2),("IEE221",4.5,3.39,135,39.9),("IEE222",5.0,3.54,151,42.5),
("IEE223",5.5,3.32,168,50.7),("IEE224",6.0,3.57,189,53.0),("IEE225",6.5,3.57,190,53.1),("IEE226",7.0,3.34,189,56.5),
("IEE227",7.5,3.33,190,57.2),("IEE273",7.7,3.42,208,60.8),("IEE272",8.0,3.50,214,61.2),("IEE228",8.5,3.59,232,64.6),("IEE229",8.7,3.10,221,71.1),("IEE230",9.0,3.31,233,70.4),
("IEE232",9.5,3.35,270,80.6),("IEE233",9.8,3.48,281,80.8),("IEE234",10.0,3.63,303,83.6),("IEE270",10.6,3.51,341,97.3),("IEE269",11.0,3.43,322,94.0),
("IEE268",11.5,3.48,354,102),("IEE267",11.9,3.40,390,115),("IEE266",12.3,3.24,409,126),("IEE263",12.9,3.16,397,126)]
print("== 8-1 OSL age = De/DR")
mx=0;bad=[]
for n,d,dr,de,a in L:
    c=de/dr; diff=c-a; mx=max(mx,abs(diff))
    print(f"{n} {d:5.1f} m  De {de:6.1f}/DR {dr:.2f} = {c:7.2f} ka  table {a:6.1f}  diff {diff:+.2f}")
    if abs(diff)>0.25: bad.append((n,round(c,2),a))
print("max |diff|",round(mx,2),"flagged >0.25:",bad)
def ols(pts):
    n=len(pts);mx=sum(p[0] for p in pts)/n;my=sum(p[1] for p in pts)/n
    sxx=sum((p[0]-mx)**2 for p in pts);sxy=sum((p[0]-mx)*(p[1]-my) for p in pts)
    b=sxy/sxx;a=my-b*mx
    res=sum((p[1]-a-b*p[0])**2 for p in pts);se=math.sqrt(res/(n-2)/sxx) if n>2 else float('nan')
    return b,a,se,n
print("== 8-2 accumulation rate: depth(cm) vs table age(ka) OLS")
for lab,(d0,d1) in {"L1-1 1.4-2.6 m":(1.4,2.6),"L1-2(S) 2.6-7.0 m":(2.6,7.0),"L1-3 7.5-9.0 m":(7.5,9.0)}.items():
    pts=[(a,d*100) for n,d,dr,de,a in L if d0<=d<=d1]
    b,a0,se,n=ols(pts); print(f"{lab}: n={n} slope {b:.2f} +/- {se:.2f} cm/ka (paper 6.4/14.5/10.1)")
    # 2-point endpoints
    print("   endpoint rate", round((pts[-1][1]-pts[0][1])/(pts[-1][0]-pts[0][0]),2))
print("== 8-3 boundaries and S1/L1 reference test")
print("L1-2(S)/L1-1 midpoint (28.0,31.6):",(28.0+31.6)/2," L1-3/L1-2(S) (56.5,57.2):",(56.5+57.2)/2)
print("S1/L1 reference 73.9+-2.6; IEE229 71.1+-3.4 diff",round(73.9-71.1,1),"combined sigma",round(math.hypot(2.6,3.4),2),"IEE230 70.4+-2.6 diff",round(73.9-70.4,1),"sigma",round(math.hypot(2.6,2.6),2))
print("== 8-4 SAR underestimation: 13% of 409 Gy ->",round(409*0.87,1)," 8% of 300 ->",round(300*.92,1))
# ---------- 8-5 Stevens 2018: coordinates
def dms(d,m=0,s=0): return d+m/60+s/3600
def hav(lat1,lon1,lat2,lon2):
    R=6371.0088; p1,p2=math.radians(lat1),math.radians(lat2)
    dphi=p2-p1; dl=math.radians(lon2-lon1)
    a=math.sin(dphi/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))
print("== 8-5 Jingbian coordinates")
A=(dms(37,29,52.8),dms(108,54,14.4)); D=(dms(37,29,58.74),dms(108,54,2.72))
print("sectionA",A,"Derbyshire",D,"dist m",round(hav(*A,*D)*1000,1),"(paper ~330 m)")
dlat=(D[0]-A[0])*111195; dlon=(D[1]-A[1])*111195*math.cos(math.radians(A[0]))
print(" N-S",round(dlat,1),"m  E-W",round(dlon,1),"m")
print("== 8-6 pIRIR residual, Rn, water")
print("1.43 ka x 3.5 Gy/ka =",round(1.43*3.5,2),"+/-",round(0.47*3.5,2))
print("Rn 0.80+-0.10 x2sd:",0.80-0.20,"-",0.80+0.20,"-> Rn loss up to",round((1-0.60)*100),"%")
print("water 15->30: (30-15)/5=",(30-15)/5,"SD; loess 10->25:",(25-10)/5)
import statistics
print("== 8-7 lag stats")
sem,n=0.7,9; sd=sem*math.sqrt(n)
try:
    from scipy import stats; t=stats.t.ppf(0.975,n-1)
except Exception: t=2.306
print("SD",round(sd,2),"t8",round(t,3),"95% CI",round(4.9-t*sem,2),round(4.9+t*sem,2))
print("ratio of 7 ka (max-insol ref) to 4.9:",round(7/4.9,2))
print("lag 4.9 ka in precession phase: 4.9/23*360 =",round(4.9/23*360,1),"deg (23 ka nominal)")
print("== 8-8 Rao")
def P(d13): return -58*(d13-1)-1266.5
for d in (-28.0,-27.5): print("d13C",d,"->",round(P(d),1),"mm")
for p in (150,350): print("P",p,"-> d13C",round(-(p+1266.5)/58+1,2))
print("slope 58 mm/permil; 0.2 permil err ->",round(0.2*58,1),"mm; 1 permil baseline ->",58,"mm; CI 70 mm = ",round(70/58,2),"permil")
print("YB 2574 cm /4 cm =",2574/4,"samples; 100 yr/sample -> ",2574/4*100/1000,"ka; rate",round(4/100*1000,1),"cm/ka")
print("JY 3000cm/40cm =",3000/40,"samples x1000 yr =",3000/40,"ka")
print("standard 29 reps mean -25.7 sd 0.13 vs ref -25.49+-0.72 diff",round(-25.7+25.49,2))
print("== 8-9 Guo")
print("Xifeng 723 x10cm =",7230,"cm; 800 ka/723 =",round(800/723*1000),"yr/sample")
for lab,yr in (("loess",800),("soil",2000)):
    r=10/yr*1000; print(lab,"rate cm/ka",r,"flux g/cm2/ka",r*2.5,"g/m2/yr",round(r*2.5*10000/1000,1))
f=(1106-800)/(2000-800); print("soil fraction needed for mean 1106 yr/sample:",round(f,3))
print("== 8-10 Ahn")
print("kE_MIS1 28cm/7kyr =",28/7,"cm/kyr ; kE_MIS3 30cm/9kyr =",round(30/9,2),"; vs Maher 20 cm/kyr ratio",round(20/4,1),round(20/3.33,1))
print("kFD demo kLF 120 kHF 100 -> kFD",20,"kFD%",round(20/120*100,1))
print("kE 113-140% : min 65 -> max",round(65*2.13,1),round(65*2.40,1),"(demo using kLF min 65.0)")
HN=(dms(37,34,25.0),dms(127,10,39.8)); DK=(dms(37,35,35),dms(127,12,12)); GD=(dms(37,33,47.8),dms(127,9,27.6))
print("HNM-Dukso km",round(hav(*HN,*DK),2)," HNM-Godeok km",round(hav(*HN,*GD),2)," Dukso-Godeok",round(hav(*DK,*GD),2))
print("Mean MAP 1450mm; Jangma etc. MAT 12.5")
print("134 subsamples over 2.7 m: mean spacing",round(270/134,2),"cm")
print("== 8-11 Dou")
print("393 cm/30.03 ka =",round(393/30.03,2),"cm/ka; yr/cm",round(30.03*1000/393,1),"(paper 76)")
for lab,r in (("glacial",20.7),("deglac",10.7),("Holocene",10.3)): print(lab,r,"cm/ka ->",round(1000/r,1),"yr/cm")
print("120 samples/393 cm =",round(393/120,2),"cm per sample ->",round(393/120*76.4),"yr")
JA=(3.59,0.704142); GB=(-5.4,0.7145)
def fNd(e): return (e-GB[0])/(JA[0]-GB[0])
def fSr(r): return (GB[1]-r)/(GB[1]-JA[1])
for e in (-4.9,-3.6,-2.5): print("eNd",e,"-> f_JA (equal [Nd])",round(fNd(e),3))
for r in (0.711713,0.708164,0.708265,0.706346): print("Sr",r,"-> f_JA (equal [Sr])",round(fSr(r),3))
print("MAR demo LSR 10.3 x DBD 1.0 =",10.3*1.0)
print("dEu demo Eu_N 1.2, Sm_N 1.0, Gd_N 1.0:",round(1.2/math.sqrt(1.0*1.0),3), " Eu_N 0.9 Sm 1.1 Gd 1.3:",round(0.9/math.sqrt(1.1*1.3),3))
print("== 8-12 mixing hyperbola demo: end members Nd 20 & 30 ppm; eNd 3.59 & -5.4; f mass of JA 0.5 ->")
c1,c2=30.0,20.0; fm=0.5; e=(fm*c1*3.59+(1-fm)*c2*(-5.4))/(fm*c1+(1-fm)*c2); print("eNd mix",round(e,3),"vs linear",round(fm*3.59+(1-fm)*(-5.4),3))
