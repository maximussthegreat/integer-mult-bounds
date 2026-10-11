# Independent response-pool and transferred-witness screen; exact F2 and rational ranks.
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json
P=Path(__file__).parent;b=json.load(open(P/'bit_r822.json'));kr=json.load(open(P/'response.json'));cols=[int(x,16) for x in kr['response_columns_hex']];v=b['v'];R=b['R'];n=2*v+R
masks=[sum(1<<q for q in f) for f in b['frames']]
def rank(rs):
 B={}
 for row in rs:
  r=list(map(Q,row))
  for p,q in B.items():
   if r[p]:z=r[p];r=[x-z*y for x,y in zip(r,q)]
  for p,z in enumerate(r):
   if z:B[p]=[x/z for x in r];break
 return len(B)
dims=[rank([b['lines'][q] for q in f]) for f in b['frames']];first=[None]*n
for f,t,ss in b['A']+b['B']:
 for x in [t]+ss:
  if first[x] is None:first[x]=f
assert all(x is not None for x in first[2*v:])
def deps(ids):
 B={};rels=[]
 for j in ids:
  val=cols[j];sup=1<<j
  while val:
   p=val.bit_length()-1
   if p in B:val^=B[p][0];sup^=B[p][1]
   else:B[p]=(val,sup);break
  if val==0:rels.append(sup)
 return len(B),rels
pool=[]
for f,M in enumerate(masks):
 if not M:continue
 ids=[j for j in range(R) if M&~masks[first[2*v+j]]==0];rk,rels=deps(ids)
 if rels:pool.append(dict(frame=f,dimension=dims[f],helper_count=len(ids),response_rank=rk,nullity=len(rels),optimistic_entrance_mass=dims[f]*len(rels),helper_ids=[j+2*v for j in ids]))
# Map published382 entries through the exact43alias contractions, then recheck newresponse and common firstframe.
rs=json.load(open(P/'sources/reuse-selection.json.txt'));alias={p['new']:p['old'] for p in rs['pairs']};physical=[i for i in range(1105) if i not in alias];idx={a:i for i,a in enumerate(physical)};rename=lambda a:idx[alias.get(a,a)]
old=json.load(open(P/'sources/PR382_kernel-selection.json.txt'));trans=[]
for E,p,ds in old['entries']:
 p=rename(p);ds=[rename(x) for x in ds];x=cols[p-2*v]
 for d in ds:x^=cols[d-2*v]
 M=sum(1<<i for i in E);legal=all(M&~masks[first[q]]==0 for q in [p]+ds)
 trans.append(dict(entrance_roots=E,dimension=rank([b['lines'][q] for q in E]),pivot=p,donors=ds,response_ok=x==0,first_frame_ok=legal,distinct=p not in ds and len(ds)==len(set(ds))))
out=dict(status='EXACT_POOL_SCREEN_ONLY',word_sha256=kr['word_sha256'],helper_first_frame_dimensions=dict(Counter(dims[first[2*v+j]] for j in range(R))),frame_dimensions=dims,helper_first_frames=first[2*v:],eligible_pools=pool,transferred382=trans,transferred382_summary=dict(total=len(trans),response_ok=sum(t['response_ok'] for t in trans),first_frame_ok=sum(t['first_frame_ok'] for t in trans),both=sum(t['response_ok'] and t['first_frame_ok'] and t['distinct'] for t in trans)),scope='Individual relation/common-entrance eligibility only; simultaneous donor chains, dirty operator charts and paidprofile not yet admitted.')
(P/'pools.json').write_text(json.dumps(out,indent=2));print(out['helper_first_frame_dimensions'],out['transferred382_summary']);print('bestpools',sorted([(p['optimistic_entrance_mass'],p['dimension'],p['nullity'],p['helper_count'],p['frame']) for p in pool],reverse=True)[:20])
# Individually reachable max entrance ranks: grant every one simultaneously and all donor movement free.
maxE=[0]*R
for p in pool:
 ids=[j-2*v for j in p['helper_ids']];rk,rr=deps(ids);union=0
 for z in rr:union|=z
 for j in ids:
  if union>>j&1:maxE[j]=max(maxE[j],p['dimension'])
cur=list(b['start']);H=Counter()
for f,t,ss in b['A']+b['B']:
 for x in [t]+ss:
  if cur[x]!=f:
   assert masks[cur[x]]&~masks[f]==0
   H[dims[f]-dims[cur[x]]]+=1;cur[x]=f
for x,f in enumerate(b['final']):
 if cur[x]!=f:H[dims[f]-dims[cur[x]]]+=1
for r in b['ret']:H[dims[b['final'][r]]]+=1
assert sum(r*n for r,n in H.items())==1680+8*R+72
Hnew=Counter(H)
for j,e in enumerate(maxE):
 if e:
  d=dims[first[2*v+j]];Hnew[d]-=1
  if d>e:Hnew[d-e]+=1
from decimal import Decimal as D,localcontext
with localcontext() as ctx:
 ctx.prec=60
 def coarse(H,W):
  HH=Counter({r:9*n for r,n in H.items() if n})
  for r in [14,7,28,7,42,7,50,36,22,8]:HH[r]+=240
  def f(s):return sum(D(r*n)/(72*W)*(D(72)/r)**s for r,n in HH.items())+D(32*72*sum(HH.values()))/(D(10)**16*W)*D(72)**s
  a,z=D(0),D('.02')
  for _ in range(180):
   mid=(a+z)/2
   if f(mid)<1:a=mid
   else:z=mid
  return str((a+z)/2),dict(HH)
 base,globalH=coarse(H,D(960+R));optimistic,newH=coarse(Hnew,D(960+R)-D(sum(maxE))/8)
 out['original_local_histogram']=dict(H);out['original_global_histogram']=globalH;out['original_coarse']=base;out['independent_eligibility_upper_screen']=dict(gauge_count=sum(e>0 for e in maxE),entrance_mass=sum(maxE),max_entrance_dimensions=maxE,optimistic_local_histogram=dict(Hnew),optimistic_coarse=optimistic,scope='Not jointly realizable: grants incompatible pivots/donors and free donor motion, perfect bank packing, all existent firstframe-rootspanned pools.')
 (P/'pools.json').write_text(json.dumps(out,indent=2));print('base',base,'maxindividualmass',sum(maxE),'idealcoarse',optimistic)
