import math
import numpy as np
from math import *
def hav(lat1,lon1,lat2,lon2,R=6371.0):
    p1,p2=radians(lat1),radians(lat2); dphi=p2-p1; dl=radians(lon2-lon1)
    a=sin(dphi/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*R*asin(sqrt(a))
print("== 4-A Lee 2024")
print("0.0258*0.183 =",0.0258*0.183)
print("218.5225+0.005 =",218.5225+0.005)
print("0.016/0.183, 0.026/0.183 =",0.016/0.183,0.026/0.183)
for name,f,days in [("14d",0.0258,14),("spike1",0.085,46),("spike2",0.143,77)]:
    print(name,"uniform frac",days/365,"ratio paper/uniform",f/(days/365))
print("gap",77-46, "indep sd combo (2sigma)",sqrt(21**2+23**2))
s1,s2=21/2,23/2; sg=25/2
rho=(s1**2+s2**2-sg**2)/(2*s1*s2); print("implied rho",rho)
from statistics import NormalDist
N=NormalDist(31,12.5)
for d in (7,28,56): print("P(gap<%d d)="%d,N.cdf(d))
print("1Nov->7Feb days",(__import__('datetime').date(947,2,7)-__import__('datetime').date(946,11,1)).days)
print("7Feb minus spike2",98-77)
print("0.0915/0.183, /0.197",0.0915/0.183,0.0915/0.197,"232/365",232/365)
print("905/10770",905/10770,"ssS for ssNa=10:",10*905/10770)
print("11/40",11/40)
# delta mixing demo
print("mix demo",(2.0-0.5*4.0)/0.5)
d34=5.0;d33=2.6
print("D33S demo",d33-1000*((1+d34/1000)**0.515-1), (1+d34/1000)**0.515)
print("== distances")
BD=(41.99,128.08); SG=(35+35/60,135+53/60); UL=(37.5,130+52/60)
print("Baekdu-Suigetsu",hav(*BD,*SG)); print("Ulleungdo-Suigetsu",hav(*UL,*SG)); print("Baekdu-Ulleungdo",hav(*BD,*UL))
KS=(37.97,126.55)
print("Baekdu-Kaesong(demo coords)",hav(*BD,*KS))
print("== 4-B McLean")
for a,b in [(42750,42323),(40332,39816),(10230,10171),(8455,8367),(5681,5619),(2737,2620)]:
    print(a,b,"mid",(a+b)/2,"half",(a-b)/2)
print("diff mid",(42750+42323)/2-(40332+39816)/2, "min",42323-40332,"max",42750-39816)
print("rate mm/yr",1640/ (((42750+42323)/2-(40332+39816)/2)))  # mm per yr
mids={"U-Oki":10200.5,"U-3":8411,"U-2":5650,"U-1":2678.5}
print(10200.5-8411,8411-5650,5650-2678.5)
print("DRE/bulk",25/100)
print("== 4-C Okuno")
def wm(xs,sig):
    w=[1/s**2 for s in sig]; m=sum(a*b for a,b in zip(w,xs))/sum(w); e=1/sqrt(sum(w)); chi=sum(((x-m)/s)**2 for x,s in zip(xs,sig)); return m,e,chi
print("U-2 four",wm([4910,4965,4945,4940],[35]*4))
print("U-2 five",wm([4910,4965,4945,4940,4710],[35]*4+[30]))
print("U-3 diff",8030-7525, sqrt(35**2+35**2),(8030-7525)/sqrt(2*35**2))
print("U-4 five",wm([12165,11840,12030,12090,12095],[40,45,40,40,40]))
print("U-4 four",wm([12165,12030,12090,12095],[40,40,40,40]))
for age in (4940,7525,9785,12090):
    print("pMC",age,100*exp(-age/8033))
print("U-3 interval",11-8.3,11-9,8.3-5.6,9-5.6)
print("Okuno U-4 11,150 vs McLean 10,200",11150-10200.5)
print("== 4-D Yun")
print("2 chon",2*3.03,3*3.03,4*3.03,"5 li",5*0.42)
print("986/22,986/90,986/7,986/4",986/22,986/90,986/7,986/4)
print("98 days weeks",98/7)
print("== 4-E Costa")
rho=2300
for tem,vol in [(4.5e13,18.9),(3.6e13,15),(3.9e13,16.4),(4.9e13,20.4),(4.1e13,17.4),(8.7e13,36.5)]:
    print(tem,tem/rho/1e9,vol)
print(40.2*1000/2300,97.7*1000/2300,13.4+4.1,37.4+5.7,37.4+5.7+2.1)
print(7.2+9.3,16.5/2.4,16.5*2.4,7.2/2.4,7.2*2.4,9.3/2.4,9.3*2.4)
print("total",7.2+9.3+4.1+2.1,7.2+9.3+5.7+2.1)
print("caldera",pi*2.8**2*0.9)
for v in (13,23,47):
    m=v*1e9*2300; print(v,m,log10(m)-7)
V=4e8/2300
print("V m3/s",V,"Mastin",2.00*V**0.241,"Sparks",1.67*V**0.259)
print("MER*time",4e8*15*3600/2300/1e9,4e8*20*3600/2300/1e9, 7.2e9*2300/(15*3600),9.3e9*2300/(20*3600))
print("50yr days",50*365.25,"1mm over 7e5 km2 bulk km3",1e-6*7e5)
print("== 4-F Trasatti")
print(8.7-1.0,14-7.7,14e6/3,14/7.3,2e4/7.3e6,2e4/14e6)
print("a=hPf/mu",6300*10e6/30e9)
for drho in (100,200): print(drho*9.81*6300/1e6)
print("h for 13,27MPa",13e6/(100*9.81),27e6/(200*9.81))
print("Mw",(2/3)*(15-9.1))
print("7.3e6/300e9 m3",7.3e6/300e9)
print("days",(__import__('datetime').date(2020,10,20)-__import__('datetime').date(2018,11,20)).days/365.25)
nu=0.25
def uz(dV,d,r): return (1-nu)*dV*d/(pi*(d*d+r*r)**1.5)
print("Mogi d=4.4km dV=14e6 r=0",uz(14e6,4400,0)*100,"cm; d=5.4:",uz(14e6,5400,0)*100)
print("r for 6.5cm at d=4.4:", 4400*sqrt((uz(14e6,4400,0)/0.065)**(2/3)-1))
print("ratio",0.065/uz(14e6,4400,0))
print("== 4-G tree ring")
print("0.45^2",.45**2,.42**2)
r=0.45;n=52; t=r*sqrt(n-2)/sqrt(1-r*r); print("t",t)
from math import erf
# p-value via t dist approx using scipy if available
try:
    from scipy import stats
    print("p",2*stats.t.sf(t,n-2), "r.42 n26",2*stats.t.sf(.42*sqrt(24)/sqrt(1-.42**2),24))
except Exception as e: print("no scipy",e)
print("regression",[4.34*c+1.33 for c in (-1,0,1,1.5)])
print("0.69/0.61",0.69/0.61)
print("Zhu",[(-10.9+2.35*a+4.12*b) for a,b in [(1,1),(0.8,0.9),(1.2,1.1),(0,0)]], -4.05+10.9, (-4.05+10.9)/6.47)
print("Ra2",1-(1-0.462)*48/(49-2-1),1-(1-0.457)*48/46)
print("age=5.44DB+0.49",[5.44*d+0.49 for d in (1,2,5)],(30-0.49)/5.44)
print("1250/25",1250/25,"99/3",99/3)
print("index demo",1.2/1.5)
print("RE demo")
y=np.array([10.0,11.0,9.5,10.5]); yh=np.array([10.2,10.6,9.9,10.2]); yc=10.2
RE=1-np.sum((y-yh)**2)/np.sum((y-yc)**2); print(RE)
