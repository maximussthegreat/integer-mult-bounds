# Independent chronological ordered175gauge audit; frozen111control functions are independently authored.
import json,copy,hashlib
from collections import Counter
from pathlib import Path
import os
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent))
ROOT.mkdir(parents=True,exist_ok=True)
DATA=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'))
from e8_bit_gauge_independent_audit import basis,contained
P=DATA;base=json.load(open(P/'bit_r822.json'));c=json.load(open(P/'candidate111.json'));stated=json.load(open(P/'ordered_result.json'));final=json.load(open(P/'candidate_ordered.json'));n=1062;v=120
F=[basis([c['lines'][i] for i in fr]) for fr in c['frames']]
def response(w):
 Y=[]
 for y in range(120,240):
  row=1<<y
  for f,t,ss in reversed(w['B']):
   if row>>t&1:
    for s in ss:row^=1<<s
  for j,ks in enumerate(w['scatter']):
   if row>>(120+j)&1:
    for k in ks:row^=1<<w['ret'][k]
  for f,t,ss in reversed(w['A']):
   if row>>t&1:
    for s in ss:row^=1<<s
  Y.append(row)
 return Y,[sum(((r>>h)&1)<<i for i,r in enumerate(Y)) for h in range(240,n)]
for layer in stated['layers']:
 Y,K=response(c);oldp={r for r in range(240,n) if c['start'][r]};newp={e['pivot'] for e in layer['relations']};ds={d for e in layer['relations'] for d in e['donors']}
 assert not oldp&newp and not oldp&ds and not newp&ds
 first={}
 for f,t,ss in c['A']+c['B']:
  for r in [t]+ss:first.setdefault(r,f)
 f=layer['frame'];pre=[]
 for e in layer['relations']:
  p=e['pivot'];z=K[p-240]
  for d in e['donors']:z^=K[d-240];pre.append([f,d,[p]])
  assert z==0 and c['start'][p]==0
  assert all(contained(F[f],F[first[r]]) for r in [p]+e['donors'])
  c['start'][p]=f
 c['A']=pre+c['A'];c['C']=[[1,t,ss] for f,t,ss in reversed(c['A']+c['B']) if t>=240]
 Y,K=response(c);c['D']=[[0,120+i,[h for h in range(240,n) if r>>h&1]] for i,r in enumerate(Y) if r>>240]
 assert all(not K[p-240] for p in oldp|newp)
assert c==final
prefix=final['A'][:len(final['A'])-len(base['A'])];written=set()
for f,t,ss in prefix:
 for s in ss:assert s not in written
 written.add(t)
# Literalreverse is required: recordwhetherdoubleapplyingtheprefixisincorrect.
z=[1<<i for i in range(n)]
for _ in range(2):
 for f,t,ss in prefix:
  for s in ss:z[t]^=z[s]
noninvolutive=[i for i in range(n) if z[i]!=(1<<i)]
assert noninvolutive
# Exact total prefix nilpotence, independently of its layer decomposition.
prefix_rows=[1<<i for i in range(n)]
for f,t,ss in prefix:
 for source in ss:prefix_rows[t]^=prefix_rows[source]
N=[row^(1<<i) for i,row in enumerate(prefix_rows)]
def product(A,B):
 result=[]
 for row in A:
  value=0
  while row:
   bit=row&-row;value^=B[bit.bit_length()-1];row^=bit
  result.append(value)
 return result
N2=product(N,N);N3=product(N2,N)
assert sum(bool(x) for x in N)==103 and sum(x.bit_count() for x in N)==408
assert sum(bool(x) for x in N2)==4 and sum(x.bit_count() for x in N2)==12
assert not any(N3)
for orientation in ['forward','inverse_adjoint','literal_inverse']:
 z=[1<<i for i in range(n)]
 events=[]
 for ph in ['D','A']:
  events += [('add',t,s) for f,t,ss in final[ph] for s in ss]
 for k,r in enumerate(final['ret']):
  events.append(('copy',n,r))
  events += [('add',120+j,n) for j,ks in enumerate(final['scatter']) if k in ks]
  events.append(('erase',n,r))
 for ph in ['B','C']:events += [('add',t,s) for f,t,ss in final[ph] for s in ss]
 z.append(0)
 if orientation=='literal_inverse':events=list(reversed(events))
 for kind,t,s in events:
  if orientation=='literal_inverse' and kind!='add':kind='erase' if kind=='copy' else 'copy'
  if kind=='copy':z[t]=z[s]
  elif kind=='erase':z[t]=0
  elif orientation=='inverse_adjoint':z[s]^=z[t]
  else:z[t]^=z[s]
 # Inverseadjointcentrecopies must use transposedscatterexplicitly, not transposethecopyblock.
 if orientation=='inverse_adjoint':
  z=[1<<i for i in range(n)]
  for ph in ['D','A']:
   for f,t,ss in final[ph]:
    for s in ss:z[s]^=z[t]
  ys=z[120:240]
  for j,ks in enumerate(final['scatter']):
   for k in ks:z[final['ret'][k]]^=ys[j]
  for ph in ['B','C']:
   for f,t,ss in final[ph]:
    for s in ss:z[s]^=z[t]
  z.append(0)
 expected=[1<<i for i in range(n)]+[0]
 for i in range(v):expected[i if orientation=='inverse_adjoint' else v+i]^=1<<(v+i if orientation=='inverse_adjoint' else i)
 assert z==expected,orientation
cur=final['start'][:];H=Counter();supp=[1<<i if i<v else 0 for i in range(n)];masks=[sum(1<<j for j in f) for f in final['frames']]
for ph in ['D','A','B','C']:
 if ph=='B':
  assert all(cur[y]==0 for y in range(120,240))
  for r in final['ret']:assert len(F[cur[r]])==8;H[8]+=1
 for f,t,ss in final[ph]:
  assert t>=v and t not in ss
  for r in [t]+ss:
   if cur[r]!=f:assert contained(F[cur[r]],F[f]);H[len(F[f])-len(F[cur[r]])]+=1;cur[r]=f
  for s in ss:
   if s<v or s>=240:assert not supp[s]&~masks[f]
   supp[t]|=supp[s]
  if t>=240:assert not supp[t]&~masks[f]
for r,f in enumerate(final['final']):
 if cur[r]!=f:assert contained(F[cur[r]],F[f]);H[len(F[f])-len(F[cur[r]])]+=1;cur[r]=f
assert H==Counter({int(k):v for k,v in stated['local_histogram'].items()})
assert sum(k*v for k,v in H.items())==8021
ext={r:F[f] for r,f in enumerate(final['start']) if r>=240 and f}
assert len(ext)==175 and sum(len(B) for B in ext.values())==307
for B in ext.values():assert all(sum(x!=0 for x in row)==1 and sum(row)==1 for row in B)
out=dict(status='PASS_ORDERED175_EXACT_LITERAL_SEQUENCE_AND_DIRTY_FRAMES',sha256=hashlib.sha256(json.dumps(final,sort_keys=True,separators=(',',':')).encode()).hexdigest(),layers=len(stated['layers']),gauges=175,entrance_mass=307,prefix_gates=len(prefix),N_nonzero_rows=103,N_entries=408,N2_nonzero_rows=4,N2_entries=12,N3_zero=True,head_read_before_write=True,prefix_is_involutive=False,double_prefix_failure_registers=noninvolutive,forward_inverse_adjoint_and_literal_inverse_all_columns=True,formal_columns=n,local_histogram=dict(sorted(H.items())),rank_mass=8021,coordinate_entrance_dimensions=dict(Counter(len(B) for B in ext.values())))
json.dump(out,open(str(ROOT / 'e8_bit_ordered_independent_audit_results.json'),'w'),indent=2);print(json.dumps(out,indent=2))
