# Independently authored F2 ordered kernel promotion with exact full-word checks.
import json,math,copy,hashlib
from collections import Counter
from pathlib import Path
P=Path(__file__).parent;c=json.load(open(P/'candidate111.json'));pools=json.load(open(P/'pools.json'));dims=pools['frame_dimensions'];v=120;R=822;n=1062;ret=set(c['ret'])
# candidate111 introduces no new frame in this witness.
assert len(c['frames'])==len(dims)
frames=[frozenset(x) for x in c['frames']];mask=[sum(1<<r for r in f) for f in frames]
def w(r):return r*math.log(72/r) if r else 0

def phase(z,ops):
 for f,t,ss in ops:
  for s in ss:z[t]^=z[s]
def scat(z,c):
 snap=[z[r] for r in c['ret']]
 for t,ks in enumerate(c['scatter']):
  for k in ks:z[v+t]^=snap[k]
def derive(c):
 first=[None]*n
 for f,t,ss in c['A']+c['B']:
  for r in [t]+ss:
   if first[r] is None:first[r]=f
 z=[0]*240+[1<<i for i in range(R)];phase(z,c['A']);scat(z,c);phase(z,c['B']);rows=z[120:240];cols=[sum((row>>i&1)<<t for t,row in enumerate(rows)) for i in range(R)]
 return first,cols,rows

def evaluate(c):
 cur=c['start'][:];H=Counter()
 for ph in ['D','A','B']:
  if ph=='B':
   for r in c['ret']:H[dims[cur[r]]]+=1
  for f,t,ss in c[ph]:
   for r in [t]+ss:
    assert frames[cur[r]]<=frames[f]
    if cur[r]!=f:H[dims[f]-dims[cur[r]]]+=1;cur[r]=f
 for r,f in enumerate(c['final']):
  assert frames[cur[r]]<=frames[f]
  if cur[r]!=f:H[dims[f]-dims[cur[r]]]+=1
 res=Counter(8-dims[c['start'][r]] for r in range(240,n));return H,res

layers=[]
for iteration in range(20):
 first,cols,rows=derive(c);available=[r for r in range(240,n) if c['start'][r]==0 and r not in ret]
 best=None
 for f,M in enumerate(mask):
  if not M or dims[f]>=8:continue
  ids=[r for r in available if M&~mask[first[r]]==0]
  if len(ids)<2:continue
  # Prefer old entry donors (already low firstframe) as basis; sparse relations remain literal XORs.
  ids.sort(key=lambda r:(dims[first[r]],cols[r-240].bit_count(),r))
  basis={};relations=[];donors=set()
  for r in ids:
   x=cols[r-240];use=0
   while x:
    k=x.bit_length()-1
    if k in basis:x^=basis[k][0];use^=basis[k][1]
    else:basis[k]=(x,use^(1<<r));break
   if not x:
    ds=[d for d in ids if use>>d&1];relations.append((r,ds));donors.update(ds)
  if not relations:continue
  gain=sum(w(dims[first[r]])-w(dims[first[r]]-dims[f]) for r,ds in relations)
  gain-=sum(w(dims[f])+w(dims[first[d]]-dims[f])-w(dims[first[d]]) for d in donors)
  if best is None or gain>best[0]:best=(gain,f,relations,donors)
 if best is None or best[0]<=1e-8:break
 gain,f,relations,donors=best;old=copy.deepcopy(c);prefix=[]
 for r,ds in relations:
  c['start'][r]=f
  for d in ds:prefix.append([f,d,[r]])
 c['A']=prefix+c['A'];c['C']=[[1,t,ss[:]] for ff,t,ss in (c['A']+c['B'])[::-1] if t>=240]
 _,_,kr=derive(c);c['D']=[[0,120+t,[240+j for j in range(R) if row>>j&1]] for t,row in enumerate(kr) if row]
 z=[1<<i for i in range(n)];phase(z,c['D']);phase(z,c['A']);scat(z,c);phase(z,c['B']);phase(z,c['C']);expect=[1<<i for i in range(n)]
 for t in range(v):expect[120+t]^=1<<t
 assert z==expect
 H,res=evaluate(c);layer=dict(iteration=iteration,frame=f,dimension=dims[f],predicted_entropy_gain=gain,relations=[dict(pivot=r,donors=ds) for r,ds in relations],donors=sorted(donors),prefix_gates=len(prefix),local_histogram=dict(H),residual_inventory=dict(res));layers.append(layer)
 print('layer',iteration,'rank',dims[f],'pivots',len(relations),'gates',len(prefix),'gain',gain,flush=True)
blob=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(P/'candidate_ordered.json').write_bytes(blob);H,res=evaluate(c)
out=dict(status='PASS_ORDERED_LOCAL_REPLAY_AND_FRAMES',sha256=hashlib.sha256(blob).hexdigest(),layers=layers,gauges=sum(c['start'][r]!=0 for r in range(240,n)),entrance_mass=sum(dims[c['start'][r]] for r in range(240,n)),local_histogram=dict(H),residual_inventory=dict(res),scope='Exact1062dirtycolumns,nestingperlayer; discoveryentropyselection; simultaneouspacking/rationalchart/invoiceadmissionrequired.')
(P/'ordered_result.json').write_text(json.dumps(out,indent=2));print('DONE',out['gauges'],out['entrance_mass'],out['local_histogram'],out['residual_inventory'])
