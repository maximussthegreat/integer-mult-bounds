import sys
"""Independent source-bound response kernel and F2/frame checker.
All external Python remains inert. The only input is the pinned R715 JSON
and an explicit response-relation witness discovered by our own search.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
import json,hashlib,copy
P=Path(sys.argv[1]).resolve()
w=json.loads((P/'raw_word.json').read_text()); sel=json.loads((P/'best_kernel_selection.json').read_text())
V=120;N=955
assert (w['R'],w['v'],w['h'])==(715,120,8)
def rbasis(vs):
 B={}
 for v in vs:
  a=list(map(Q,v))
  for p,b in sorted(B.items()):
   if a[p]:
    x=a[p];a=[u-x*v for u,v in zip(a,b)]
  if any(a):
   p=next(i for i,x in enumerate(a) if x);x=a[p];B[p]=[y/x for y in a]
 return B
def inside(v,B):
 a=list(map(Q,v))
 for p,b in sorted(B.items()):
  if a[p]:
   c=a[p];a=[x-c*y for x,y in zip(a,b)]
 return not any(a)
fr=[];dims=[]
for f in w['frames']:
 B=rbasis(w['lines'][i] for i in f);dims.append(len(B));fr.append(sum(1<<i for i,v in enumerate(w['lines']) if inside(v,B)))
print('rational frames',len(fr),flush=True)
lookup={m:i for i,m in enumerate(fr)};resp=defaultdict(int);first={}
for f,d,ss in w['D']:
 assert dims[f]==0
 for s in ss:resp[s]^=1<<(d-V)
for ph in 'ABC':
 for f,d,ss in w[ph]:
  for x in [d]+ss:
   if x>=240 and dims[f]>0:first.setdefault(x,fr[f])
piv={};donorE={};by=defaultdict(list)
for es,p,ds,claimed_dim in sel:
 B=rbasis(w['lines'][i] for i in es);E=sum(1<<i for i,v in enumerate(w['lines']) if inside(v,B));dim=len(B)
 assert dim==claimed_dim and p not in w['ret'] and p not in piv and p not in donorE
 if E not in lookup:
  lookup[E]=len(fr);fr.append(E);dims.append(dim);w['frames'].append([i for i in range(V) if E>>i&1])
 r=resp[p]
 for d in ds:
  assert d not in w['ret'] and d not in piv and donorE.setdefault(d,E)==E
  r^=resp[d];by[d,E].append(p)
 assert r==0
 for x in [p]+ds:assert first[x]&E==E
 piv[p]=E
assert not set(piv)&set(donorE)
k=copy.deepcopy(w)
for p,E in piv.items():k['start'][p]=lookup[E]
k['D']=[[f,d,[x for x in ss if x not in piv]] for f,d,ss in w['D']]
k['A']=[[lookup[E],d,ps] for (d,E),ps in sorted(by.items())]+w['A']
full=lookup[(1<<V)-1]
k['C']=w['C']+[[full,d,ps] for (d,E),ps in sorted(by.items())]
def replay(k):
 states=k['start'][:];val=[1<<i for i in range(N)];hist=Counter();rec=[];support=[(1<<i) if i<V else 0 for i in range(N)];viol=[];f2viol=[]
 def move(x,f):
  old=states[x]
  assert fr[old]&~fr[f]==0,('nonnested',x,old,f)
  if old!=f:
   gap=dims[f]-dims[old]
   if gap:hist[gap]+=1;rec.append([0,x,old,f,gap,0])
   states[x]=f
 def run(phase):
  for num,(f,d,ss) in enumerate(k[phase]):
   assert d not in ss and len(set(ss))==len(ss)
   for x in [d]+ss:move(x,f)
   for x in ss:
    if x<V or x>=240:
     if support[x]&~fr[f]:viol.append((phase,num,x))
     if (val[x]&((1<<V)-1))&~fr[f]:f2viol.append((phase,num,x))
    support[d]|=support[x];val[d]^=val[x];rec.append([1,d,x,1,f,0])
   if d>=240:
    if support[d]&~fr[f]:viol.append((phase,num,d))
    if (val[d]&((1<<V)-1))&~fr[f]:f2viol.append((phase,num,d))
 run('D');run('A')
 assert all(dims[states[120+t]]==0 for t in range(120))
 for j,q in enumerate(k['ret']):
  assert dims[states[q]]==8
  hist[8]+=1;rec.append([2,q,N,states[q],0,8,0])
  for t,row in enumerate(k['scatter']):
   if j in row:val[V+t]^=val[q];rec.append([1,V+t,N,1,0,0])
  rec.append([3,q,N,states[q],0,0,0])
 run('B');run('C')
 for x in range(N):move(x,k['final'][x])
 expected=[(1<<i)^((1<<(i-V)) if V<=i<2*V else 0) for i in range(N)]
 assert val==expected
 return hist,rec,viol,f2viol
for name,word in [('raw',w),('kernel',k)]:
 H,rec,viol,f2viol=replay(word)
 print(name,'profile',dict(sorted(H.items())),'integer support failures',len(viol),'F2 support failures',len(f2viol),'records',len(rec),'adds',sum(z[0]==1 for z in rec),flush=True)
 if name=='kernel':
  (P/'kernel_word.json').write_text(json.dumps(word,separators=(',',':')))
  (P/'kernel_records.json').write_text(json.dumps(rec,separators=(',',':')))
  (P/'frame_metadata.json').write_text(json.dumps({'dims':dims,'closures':[str(m) for m in fr]}))
  (P/'kernel_check.json').write_text(json.dumps({'rank':sum(dims[word['start'][i]] for i in range(240,N)),'pivot_count':len(piv),'donor_count':len(donorE),'widths':dict(Counter(8-dims[word['start'][i]] for i in range(240,N))),'profile':dict(H),'integer_support_violations':len(viol),'f2_support_violations':len(f2viol),'all_formal_F2_columns':N},indent=2))
