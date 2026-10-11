# Independent ordered175 bank ledger and exactrational moment certification.
import json,gzip
from collections import Counter,deque
from fractions import Fraction as Q
from pathlib import Path
import os
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent))
ROOT.mkdir(parents=True,exist_ok=True)
DATA=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'))
from e8_bit_gauge_independent_audit import basis
from e8_bit_gauge_packing_price_audit import logbounds,expbounds
P=DATA;c=json.load(open(P/'candidate_ordered.json'));audit=json.load(open(str(ROOT / 'e8_bit_ordered_independent_audit_results.json')));p=json.load(open(P/'price_ordered.json'))['results'][0]
ext={r:[next(i for i,x in enumerate(row) if x) for row in basis([c['lines'][j] for j in c['frames'][f]])] for r,f in enumerate(c['start']) if r>=240 and f}
roles={d:deque() for d in [4,7,8]}
for rep in range(8):
 for r in range(240,1062):
  A=[i for i in range(8) if i not in ext.get(r,[])];roles[len(A)].append((rep,r,A))
assert {d:len(v) for d,v in roles.items()}=={4:352,7:1048,8:5176}
placements=[];bank=0;maxops=0;totalops=0
for pattern in p['patterns']:
 for _ in range(pattern['count']):
  covered=set();off=0
  for d,num in sorted((int(k),v) for k,v in pattern['ranks'].items()):
   for _ in range(num):
    rep,r,A=roles[d].popleft();slot=list(range(off,off+d));off+=d
    route=dict(zip(A,slot));route.update(zip([i for i in range(72) if i not in route],[i for i in range(72) if i not in slot]));perm=[route[i] for i in range(72)];inv=[0]*72
    for i,j in enumerate(perm):inv[j]=i
    assert sorted(perm)==list(range(72)) and all(inv[perm[i]]==i for i in range(72));assert {perm[i] for i in A}==set(slot) and not covered&set(slot);covered.update(slot)
    # Explicit transposition decomposition on each of the two addresscoordinate blocks.
    live=list(range(72));ops=[]
    for i in range(72):
     if live[i]!=perm[i]:
      j=live.index(perm[i]);live[i],live[j]=live[j],live[i];ops.append([i,j])
    assert live==perm
    elementary=[[i,j] for i,j in ops]+[[72+i,72+j] for i,j in ops]
    maxops=max(maxops,len(elementary));totalops+=len(elementary)
    placements.append(dict(replica=rep,register=r,bank=bank,entrance_axes=ext.get(r,[]),residual_axes=A,slot=slot,owner_permutation=perm,inverse_owner_permutation=inv,address_transpositions=elementary))
  pad=list(range(off,72));assert len(pad)==pattern.get('padding',0);assert covered|set(pad)==set(range(72));bank+=1
assert bank==697 and all(not q for q in roles.values()) and len(placements)==6576
with gzip.open(str(ROOT / 'e8_bit_ordered_owner_routes.json.gz'),'wt') as f:json.dump(placements,f,separators=(',',':'))
H=Counter({int(r):72*n for r,n in audit['local_histogram'].items()})
for r in [14,7,28,7,42,7,50,36,22,8]:H[r]+=1920
H[32]+=9;W=2*4*120*8+9*697;mass=sum(r*n for r,n in H.items());N=sum(H.values());assert W==13953 and mass==1002120 and N==327585 and 72*W-mass==2496
assert dict(H)=={int(r):n for r,n in p['profile'].items()}
def moment(s):
 lo=hi=Q(0)
 for r,n in H.items():
  a,b=logbounds(Q(72,r));u,v=expbounds(s*a,s*b);w=Q(r*n,72*W);lo+=w*u;hi+=w*v
 a,b=logbounds(Q(72));u,v=expbounds(s*a,s*b);w=Q(32*72*N,10**16*W);return lo+w*u,hi+w*v
lo=Q(1036212382904051313190,10**24);hi=lo+Q(1,10**24);ml=moment(lo);mh=moment(hi);assert ml[1]<1<mh[0]
out=dict(status='PASS_ORDERED175_T8_PACKING_EXACT_MOMENT',replicas=8,banks_per_stage=697,padding_rank_per_stage=32,live=W,rank_mass=mass,deficit=2496,child_count=N,profile=dict(sorted(H.items())),owner_routes=6576,max_owner_address_transpositions=maxops,total_oneway_owner_address_transpositions=totalops,coarse_lower=str(lo),coarse_upper=str(hi),strict_moment_endpoint_residuals=[str(float(ml[1]-1)),str(float(mh[0]-1))])
json.dump(out,open(str(ROOT / 'e8_bit_ordered_packing_audit_results.json'),'w'),indent=2);print(json.dumps(out,indent=2))
