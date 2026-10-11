# Independent frozen witness interpretation and all-column bit replay.
import json,hashlib
from pathlib import Path
P=Path(__file__).parent
b=json.load(open(P/'sources/bitE8-r865.json'));fs=json.load(open(P/'sources/frame-selection.json.txt'));rs=json.load(open(P/'sources/reuse-selection.json.txt'))
# Flatten the scalar stream once, retaining the published phase-order addressing.
address=[]
for ph in ['D','A','B','C']:
 b[ph]=[[f,t,[s]] for f,t,ss in b[ph] for s in ss]
 address += [(ph,k) for k in range(len(b[ph]))]
for x in fs['entries']:
 ph,k=address[x['scalar_index']];assert ph==x['phase'] and b[ph][k]==[x['old_frame'],x['dst'],[x['src']]];b[ph][k][0]=x['new_frame']
raw=json.dumps(b,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(raw).hexdigest()==fs['output_sha256']==rs['retimed_input_sha256']
# Disjoint alias contractions plus literal undo immediately preceding reused births.
v=b['v'];oldn=2*v+b['R'];aliases={p['new']:p['old'] for p in rs['pairs']};keep=[i for i in range(oldn) if i not in aliases];index={a:i for i,a in enumerate(keep)};rename=lambda a:index[aliases.get(a,a)]
insert={p['at']:p for p in rs['pairs']};out=[];cut=None
for k,(f,t,ss) in enumerate(b['A']+b['B']):
 if k==len(b['A']):cut=len(out)
 if k in insert:
  p=insert[k];out.append([f,rename(p['old']),[rename(s) for s in p['sources']]])
 out.append([f,rename(t),[rename(s) for s in ss]])
b['A'],b['B']=out[:cut],out[cut:];b['R']-=len(aliases);assert b['R']==822
b['start']=[b['start'][i] for i in keep];b['final']=[b['final'][i] for i in keep];b['ret']=[rename(i) for i in b['ret']];b['C']=[[1,t,ss] for f,t,ss in out[::-1] if t>=2*v]
n=2*v+b['R'];dirty=[0]*(2*v)+[1<<j for j in range(b['R'])]
def phase(rows,ops):
 for _,t,ss in ops:
  for s in ss:rows[t]^=rows[s]
def scatter(rows):
 snap=[rows[x] for x in b['ret']]
 for t,ks in enumerate(b['scatter']):
  for k in ks:rows[v+t]^=snap[k]
phase(dirty,b['A']);scatter(dirty);phase(dirty,b['B']);K=dirty[v:2*v]
b['D']=[[0,v+t,[2*v+j for j in range(b['R']) if row>>j&1]] for t,row in enumerate(K) if row]
raw=json.dumps(b,sort_keys=True,separators=(',',':')).encode();sha=hashlib.sha256(raw).hexdigest();assert sha==rs['output_sha256'];(P/'bit_r822.json').write_bytes(raw)
rows=[1<<i for i in range(n)];phase(rows,b['D']);phase(rows,b['A']);scatter(rows);phase(rows,b['B']);phase(rows,b['C'])
expect=[1<<i for i in range(n)]
for t in range(v):expect[v+t]^=1<<t
assert rows==expect
cols=[sum(((K[t]>>j)&1)<<t for t in range(v)) for j in range(b['R'])]
# Carry exact witnesses through binary Gaussian elimination.
def kernel(vectors):
 piv={};relations=[]
 for j,x in enumerate(vectors):
  witness=1<<j
  while x:
   p=x.bit_length()-1
   if p in piv:x^=piv[p][0];witness^=piv[p][1]
   else:piv[p]=(x,witness);break
  if x==0:relations.append(witness)
 return len(piv),relations
rank,rel=kernel(cols)
(P/'response.json').write_text(json.dumps(dict(word_sha256=sha,helper_count=b['R'],all_initial_columns=n,response_rank=rank,kernel_dimension=len(rel),response_columns_hex=[hex(x) for x in cols],kernel_basis_hex=[hex(x) for x in rel],helper_starts=sorted(set(b['start'][2*v:]))),indent=2));print('PASS',sha,n,rank,len(rel),set(b['start'][2*v:]))
