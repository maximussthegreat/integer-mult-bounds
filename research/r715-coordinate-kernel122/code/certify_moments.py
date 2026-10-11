import sys
"""Independent rational series certificate and balanced outer arithmetic.
No imported upstream code. Decimal is used ONLY to suggest a 1e-24 bracket;
all reported endpoints and strict inequalities are checked over Fractions.
"""
from fractions import Fraction as Q
from decimal import Decimal,localcontext,ROUND_FLOOR
from pathlib import Path
from functools import lru_cache
import json,sys
sys.set_int_max_str_digits(0)
P=Path(sys.argv[1]).resolve();C=json.loads((P/'packing_certificate.json').read_text());H={int(r):n for r,n in C['profile'].items()};m=78;W=C['live'];E=sum(H.values());S=10**90
floor=lambda q:Q((q*S).numerator//(q*S).denominator,S)
ceil=lambda q:-floor(-q)
@lru_cache(None)
def atanh(t):
 assert 0<=t<=Q(1,3)
 value=Q(0);power=t
 for n in range(100):value+=power/(2*n+1);power*=t*t
 return value,value+power/(201*(1-t*t))
@lru_cache(None)
def logbounds(x):
 k=0
 while x>=2:x/=2;k+=1
 assert 1<=x<2
 a,b=atanh((x-1)/(x+1));c,d=atanh(Q(1,3))
 return floor(2*(a+k*c)),ceil(2*(b+k*d))
def expbounds(x,y):
 assert 0<=x<=y<Q(1,10)
 def poly(z):
  v=t=Q(1)
  for n in range(1,41):t=t*z/n;v+=t
  nextterm=t*z/41
  return v,v+nextterm/(1-z/42)
 return floor(poly(x)[0]),ceil(poly(y)[1])

def moment(s):
 low=high=Q(0)
 for r,n in H.items():
  a,b=logbounds(Q(m,r));a,b=expbounds(s*a,s*b);weight=Q(r*n,m*W);low+=weight*a;high+=weight*b
 a,b=logbounds(Q(m));a,b=expbounds(s*a,s*b);weight=Q(146478*2*m**3*E,2**80*m*W)
 return floor(low+weight*a),ceil(high+weight*b)
with localcontext() as c:
 c.prec=85
 terms=[(Decimal(r*n)/Decimal(m*W),(Decimal(m)/Decimal(r)).ln()) for r,n in H.items()]
 bad=Decimal(146478*2*m**3*E)/Decimal(2**80*m*W);lm=Decimal(m).ln()
 lo=Decimal(0);hi=Decimal('.002')
 for _ in range(300):
  a=(lo+hi)/2;v=sum(t*(a*l).exp() for t,l in terms)+bad*(a*lm).exp()
  if v<1:lo=a
  else:hi=a
 lower=Q(int((lo*Decimal(10)**24).to_integral_value(rounding=ROUND_FLOOR)),10**24)
upper=lower+Q(1,10**24)
l1,u1=moment(lower);l2,u2=moment(upper);assert u1<1<l2
b=Q(1297203880559577927527,10**24);eta=beta=grid=Q(1,10**18)
cap=min(lower,(1-beta)*b)-Q(1,10**24);a=Q(384599,10**10);boot=[]
def intceil(q):return -((-q.numerator)//q.denominator)
for _ in range(6):
 old=a;a=(1-cap)*cap+cap*old
 gaps=[cap-a,1-a-cap,1-a-cap*(1-old),1-cap];gap=min(gaps)
 assert 0<old<a<cap<1-a and gap>0
 cutoff=max(intceil(36/gap**2),intceil(2*(4+C['charged_three_level_bits'])/gap))
 assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+C['charged_three_level_bits'])
 boot.append({'gap':str(gap),'cutoff_log2':str(cutoff)})
# Formula-level independent transcription of the published 40 parameter
# gaps and 7 algorithm-margin gaps in the balanced assembly.
q=a*(1-2*eta);epsilon=(1-eta)/(1+q);c=q+eta/4;r=(epsilon*q+1-epsilon)/2;delta=eta/8
tau=1-a;sigma=1-b;lam=(tau+1-q)/2;internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
margin=epsilon*q;ticks=margin/grid;kappa=grid*((ticks.numerator-1)//ticks.denominator)
parameter=[a,b-a,Q(1,32)-b,beta,1-beta,(1-beta)*b-a,q,1-internal-q,1-leaf-q,c,1-c,c-q,lam-tau,lam-sigma,lam-internal,1-q-lam,1-q-leaf,1-q-(1-c),q,epsilon,1-epsilon,1-epsilon,1-epsilon*(1+c),epsilon*c,1-epsilon,1-epsilon-delta,r-delta,1-epsilon-r,epsilon-(1-r)/2,1-epsilon,r,1-r,Q(1,4)-r,delta,Q(1,8)-delta,epsilon-a,1-epsilon-margin,8-epsilon+r-delta-margin,Q(1),Q(10**6)-Q(51*20161,25)]
margins=[1-epsilon,a,margin,a,min(1-epsilon-delta,r-delta),1-epsilon-delta,epsilon]
strict=parameter+[x-kappa for x in margins];assert len(strict)==47 and min(strict)>0
assert min(margins)==margin and margin<kappa+grid
assert (1-epsilon)-margin==eta and 1-epsilon-r==eta/2
report={'status':'PASS_RATIONAL_ENDPOINT_BOOTSTRAP_AND_47_OUTER_INEQUALITIES','bit_lower':str(lower),'bit_upper':str(upper),'moment_lower_endpoint_upper':str(u1),'moment_upper_endpoint_lower':str(l2),'complex_lower':str(b),'kappa':str(kappa),'kappa_decimal':str(Decimal(kappa.numerator)/Decimal(kappa.denominator)),'gain_over_pr465':str(kappa-Q(1283479306671789,10**18)),'binding':'bit','strict_constraint_count':47,'minimum_strict_slack':str(min(strict)),'next_grid_rejected':True,'charged_three_level_bits':C['charged_three_level_bits'],'bootstrap':boot,'method':'100-term rational atanh logs and 40-term rational exponential Taylor bounds; Decimal suggestion only','scope':'Conditional component arithmetic, not a full inherited compiler/cover reconstruction.'}
(P/'moment_certificate.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['bootstrap','moment_lower_endpoint_upper','moment_upper_endpoint_lower','minimum_strict_slack']},indent=2))
