# Independent coordinate-entrance, concrete owner-route and rational moment checks.
import json,gzip,hashlib
from pathlib import Path
import os
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent))
ROOT.mkdir(parents=True,exist_ok=True)
DATA=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'))
from fractions import Fraction as Q
from collections import Counter,deque
P=DATA;c=json.load(open(P/'candidate111.json'));receipt=json.load(open(P/'candidate111_receipt.json'));price=json.load(open(P/'price111.json'))
# Read independentlyaudited coordinatebases from original line data; exactrowelimination.
def axes(roots):
 B={}
 for r in roots:
  x=list(map(Q,c['lines'][r]))
  for j,b in sorted(B.items()):
   if x[j]:q=x[j];x=[u-q*v for u,v in zip(x,b)]
  j=next((i for i,v in enumerate(x) if v),None)
  if j is not None:
   q=x[j];x=[v/q for v in x]
   for k,b in list(B.items()):
    if b[j]:q=b[j];B[k]=[u-q*v for u,v in zip(b,x)]
   B[j]=x
 assert all(row==[Q(i==j) for i in range(8)] for j,row in B.items())
 return sorted(B)
ext={r:axes(c['frames'][f]) for r,f in enumerate(c['start']) if r>=240 and f!=0}
assert len(ext)==111 and Counter(len(z) for z in ext.values())==Counter({1:95,4:16})
roles={d:deque() for d in (4,7,8)}
for rep in range(8):
 for r in range(240,1062):
  complement=[i for i in range(8) if i not in ext.get(r,[])];roles[len(complement)].append((rep,r,complement))
assert {d:len(v) for d,v in roles.items()}=={4:128,7:760,8:5688}
placements=[];bank=0
for count,counts in [(95,{7:8,8:2}),(64,{4:2,8:8}),(554,{8:9})]:
 for _ in range(count):
  used=set();off=0
  for d,num in sorted(counts.items()):
   for _ in range(num):
    rep,r,A=roles[d].popleft();slot=list(range(off,off+d));off+=d
    route=dict(zip(A,slot));freein=[i for i in range(72) if i not in route];freeout=[i for i in range(72) if i not in slot];route.update(zip(freein,freeout));perm=[route[i] for i in range(72)];inv=[0]*72
    for i,j in enumerate(perm):inv[j]=i
    assert sorted(perm)==list(range(72)) and all(inv[perm[i]]==i for i in range(72))
    assert {perm[i] for i in A}==set(slot) and not used&set(slot);used.update(slot)
    placements.append(dict(replica=rep,register=r,bank=bank,entrance_axes=ext.get(r,[]),residual_axes=A,slot=slot,owner_permutation=perm,inverse_owner_permutation=inv))
  assert off==72 and used==set(range(72));bank+=1
assert bank==713 and all(not q for q in roles.values()) and len(placements)==6576
assert len({(x['replica'],x['register']) for x in placements})==6576
with gzip.open(str(ROOT / 'e8_bit_gauge_owner_routes.json.gz'),'wt') as f:json.dump(placements,f,separators=(',',':'))
# Rebuildfullpaidprofile from independentlyreplayedlocalH,not priceinput.
audit=json.load(open(str(ROOT / 'e8_bit_gauge_independent_audit_results.json')));H=Counter({int(r):72*n for r,n in audit['local_histogram'].items()})
for r in [14,7,28,7,42,7,50,36,22,8]:H[r]+=1920
W=2*4*120*8+9*713;mass=sum(r*n for r,n in H.items());N=sum(H.values());assert W==14097 and mass==1012488 and N==325488 and 72*W-mass==2496
assert dict(sorted(H.items()))=={int(r):n for r,n in price['profile'].items()}
assert 72**2>2*max(H)**2
# Exact positive rational logarithm/exponential interval at nominatedrootbracket.
def logsmall(x):
 z=(x-1)/(x+1);tot=Q(0);term=z
 for k in range(40):tot+=2*term/(2*k+1);term*=z*z
 return tot,tot+2*term/(81*(1-z*z))
def logbounds(x):
 k=0
 while x>=2:x/=2;k+=1
 lo,hi=logsmall(x);a,b=logsmall(Q(2));return lo+k*a,hi+k*b
def expbounds(lo,hi):
 def partial(x):
  t=s=Q(1)
  for k in range(1,15):t*=x/k;s+=t
  return s,t
 lower,_=partial(lo);upper,t=partial(hi);upper+=t*hi/15/(1-hi/16)
 return lower,upper
def moment(s):
 lo=hi=Q(0)
 for r,n in H.items():
  l,u=logbounds(Q(72,r));a,b=expbounds(s*l,s*u);weight=Q(r*n,72*W);lo+=weight*a;hi+=weight*b
 l,u=logbounds(Q(72));a,b=expbounds(s*l,s*u);weight=Q(32*72*N,10**16*W);return lo+weight*a,hi+weight*b
lo=Q(1028490312861249899907,10**24);hi=lo+Q(1,10**24)
ml=moment(lo);mh=moment(hi);assert ml[1]<1 and mh[0]>1
out=dict(status='PASS_COORDINATE_ENTRANCES_CONCRETE_OWNER_ROUTES_EXACT_CONDITIONAL_MOMENT',gauges=111,entrance_dimensions={1:95,4:16},replicas=8,banks_per_stage=713,residual_roles=6576,padding=0,live=W,profile=dict(sorted(H.items())),rank_mass=mass,deficit=2496,child_count=N,coarse_lower=str(lo),coarse_upper=str(hi),moment_lower_endpoint_upper_minus_one=str(float(ml[1]-1)),moment_upper_endpoint_lower_minus_one=str(float(mh[0]-1)),scope='Exact formalcoordinate residual packing and inversepermutations. Residualphysicalmeaning and fallbackengine portability remain assumptions; no literal phase/compiler/invoice admission, no assembledkappa claim.')
json.dump(out,open(str(ROOT / 'e8_bit_gauge_packing_price_audit_results.json'),'w'),indent=2);print(json.dumps(out,indent=2))
# Explicit address partial-swap permutations on two8-coordinate blocks.
# This proves the coordinate residual identity itself, without inheritingPR382phaseadmission.
def swapperm(A,width=8):
 perm=list(range(2*width))
 for i in A:perm[i],perm[width+i]=perm[width+i],perm[i]
 return perm
def compose(a,b):return [a[b[i]] for i in range(len(a))]
full=swapperm(range(8));chart_checks=0
for p,E in ext.items():
 entrance=swapperm(E);complement=swapperm([i for i in range(8) if i not in E])
 assert compose(entrance,entrance)==list(range(16))
 assert compose(full,entrance)==compose(entrance,full)==complement
 assert compose(complement,complement)==list(range(16))
 # An address permutation is coefficient+1, so its inverse-adjoint is itself here.
 chart_checks+=1
out.update(explicit_coordinate_partial_swap_charts=chart_checks,partial_swap_both_orientations=True,coordinate_chart_scope='Exact16-coordinate addresspermutation matrices D_full D_E=D_complement, including signs(+1). Applies when supplierendpoint normalization is the specifiedpartialswapmodel; fullglobalwrapper/compiler stillunverified.')
json.dump(out,open(str(ROOT / 'e8_bit_gauge_packing_price_audit_results.json'),'w'),indent=2);print('Explicitaddress charts PASS',chart_checks)
