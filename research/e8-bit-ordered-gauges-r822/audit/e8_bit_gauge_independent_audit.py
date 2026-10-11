# Independent exact reverse-response, rational-frame and dirty-bracket audit.
import json,hashlib,copy
from pathlib import Path
import os
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent))
ROOT.mkdir(parents=True,exist_ok=True)
DATA=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'))
from fractions import Fraction as Q
from collections import Counter
P=DATA;base=json.load(open(P/'bit_r822.json'));pool=json.load(open(P/'pools.json'));n=1062;v=120
# Rational address bases. Do not reduce root coordinates modulo2.
def basis(vecs):
 B={}
 for vec in vecs:
  x=list(map(Q,vec))
  for p,b in sorted(B.items()):
   if x[p]:z=x[p];x=[a-z*c for a,c in zip(x,b)]
  k=next((i for i,z in enumerate(x) if z),None)
  if k is not None:
   z=x[k];x=[a/z for a in x]
   for p,b in list(B.items()):
    if b[k]:z=b[k];B[p]=[a-z*c for a,c in zip(b,x)]
   B[k]=x
 return tuple(tuple(B[p]) for p in sorted(B))
def contained(A,B):return basis(A+B)==B
F=[basis([base['lines'][i] for i in fr]) for fr in base['frames']]
assert len(F[0])==0 and len(F[1])==8
# Reverse covectors for every outputtarget of A/scatter/B, excluding precancel/cleanup.
Y=[]
for y in range(120,240):
 row=1<<y
 for f,t,ss in reversed(base['B']):
  if row>>t&1:
   for s in ss:row^=1<<s
 for j,ks in enumerate(base['scatter']):
  if row>>(v+j)&1:
   for k in ks:row^=1<<base['ret'][k]
 for f,t,ss in reversed(base['A']):
  if row>>t&1:
   for s in ss:row^=1<<s
 Y.append(row)
K=[sum(((row>>j)&1)<<i for i,row in enumerate(Y)) for j in range(240,n)]
assert K==[int(z,16) for z in json.load(open(P/'response.json'))['response_columns_hex']]
selection=[e for e in pool['transferred382'] if e['response_ok'] and e['first_frame_ok'] and e['distinct']]
# Recheck every published eligibilityflag, not just selectedones.
first={}
for f,t,ss in base['A']+base['B']:
 for r in [t]+ss:first.setdefault(r,f)
for e in pool['transferred382']:
 er=basis([base['lines'][i] for i in e['entrance_roots']]);ks=K[e['pivot']-240]
 for d in e['donors']:ks^=K[d-240]
 assert (ks==0)==e['response_ok']
 assert all(contained(er,F[first[r]]) for r in [e['pivot']]+e['donors'])==e['first_frame_ok']
 assert len(er)==e['dimension']
piv=[e['pivot'] for e in selection];don={d for e in selection for d in e['donors']}
assert len(piv)==len(set(piv))==111 and not set(piv)&don
assert sum(e['dimension'] for e in selection)==159
word=copy.deepcopy(base);pre=[];ext=[]
for e in selection:
 E=basis([base['lines'][i] for i in e['entrance_roots']])
 if E not in F:F.append(E);word['frames'].append(e['entrance_roots'])
 f=F.index(E);p=e['pivot'];word['start'][p]=f;ext.append([p,f])
 for d in e['donors']:pre.append([f,d,[p]])
pre.sort(key=lambda g:(len(F[g[0]]),g[0],g[1],g[2]))
word['A']=pre+word['A'];word['ext']=sorted(ext)
# Recompute rawdirty targetrows by multiplying covectors by elementary entrance shears onright.
YP=Y[:]
for f,t,ss in reversed(pre):
 for k,row in enumerate(YP):
  if row>>t&1:
   for s in ss:row^=1<<s
  YP[k]=row
assert all(not(row>>p&1) for row in YP for p in piv)
word['D']=[[0,120+i,[h for h in range(240,n) if row>>h&1]] for i,row in enumerate(YP)]
word['C']=[[1,t,ss] for f,t,ss in reversed(word['A']+word['B']) if t>=240]
# All1062independent dirty columns, including111gauged inputs.
rows=[1<<i for i in range(n)]
def apply(ops):
 for f,t,ss in ops:
  for s in ss:rows[t]^=rows[s]
apply(word['D']);apply(word['A']);ret=[rows[h] for h in word['ret']]
for j,ks in enumerate(word['scatter']):
 for k in ks:rows[v+j]^=ret[k]
apply(word['B']);apply(word['C'])
expected=[1<<i for i in range(n)]
for i in range(v):expected[v+i]^=1<<i
assert rows==expected
# Precancellationmustnotreadgaugedslotsatframe0. LiteralA/B and finalwalks.
assert all(word['start'][r]==0 for _,t,ss in word['D'] for r in [t]+ss)
cur=word['start'][:];H=Counter();record=[]
for phase in ('A','B'):
 if phase=='B':
  assert all(cur[y]==0 for y in range(120,240))
  for r in word['ret']:assert len(F[cur[r]])==8;H[8]+=1
 for pos,(f,t,ss) in enumerate(word[phase]):
  assert len(set([t]+ss))==1+len(ss)
  for r in [t]+ss:
   if cur[r]!=f:
    assert contained(F[cur[r]],F[f]),(phase,pos,r,cur[r],f)
    delta=len(F[f])-len(F[cur[r]]);assert delta>0
    H[delta]+=1;cur[r]=f
for r,f in enumerate(word['final']):
 if cur[r]!=f:
  assert contained(F[cur[r]],F[f]);delta=len(F[f])-len(F[cur[r]]);assert delta>0
  H[delta]+=1;cur[r]=f
for f,t,ss in word['C']:assert all(cur[r]==f for r in [t]+ss)
assert sum(k*z for k,z in H.items())==8*822+2*120*7+72-159
assert all(len(F[f])==e['dimension'] for e,(_,f) in zip(sorted(selection,key=lambda e:e['pivot']),sorted(ext)))
out=dict(status='PASS_F2_DIRTY_SCALAR_AND_RATIONAL_FRAME_MODEL',base_sha256=hashlib.sha256(json.dumps(base,sort_keys=True,separators=(',',':')).encode()).hexdigest(),gauges=111,entrance_mass=159,prefix_xor_count=len(pre),all_live_columns=n,local_histogram=dict(sorted(H.items())),rank_mass=sum(k*z for k,z in H.items()),residual_inventory=dict(sorted(Counter(8-len(F[f]) for p,f in ext).items())),ungauged_full_residuals=822-111,scope='No literal endpoint Fourier/address adapters, bank packing, recursive compiler or analytic admission. Gauge method inheritedfromPR382; this audits transferredrelations onR822.')
json.dump(out,open(str(ROOT / 'e8_bit_gauge_independent_audit_results.json'),'w'),indent=2);json.dump(word,open(str(ROOT / 'e8_bit_gauge_independent_word.json'),'w'),separators=(',',':'));print(json.dumps(out,indent=2))
# Audit exact externally suppliedcandidate, not merely ourcommutingprefixconstruction.
candidate=json.load(open(P/'candidate111.json'))
assert candidate['A'][len(pre):]==base['A'] and candidate['B']==base['B']
assert Counter((f,t,tuple(ss)) for f,t,ss in candidate['A'][:len(pre)])==Counter((f,t,tuple(ss)) for f,t,ss in pre)
assert candidate['D']==word['D'] and candidate['start']==word['start'] and candidate['frames']==word['frames']
assert candidate['C']==[[1,t,ss] for f,t,ss in reversed(candidate['A']+candidate['B']) if t>=240]
for orientation in ('forward','backward'):
 rows=[1<<i for i in range(n)]
 def run(ops):
  for f,t,ss in ops:
   for s in ss:
    if orientation=='forward':rows[t]^=rows[s]
    else:rows[s]^=rows[t]
 run(candidate['D']);run(candidate['A'])
 if orientation=='forward':
  snapshot=[rows[h] for h in candidate['ret']]
  for j,ks in enumerate(candidate['scatter']):
   for k in ks:rows[v+j]^=snapshot[k]
 else:
  snapshot=rows[v:2*v]
  for j,ks in enumerate(candidate['scatter']):
   for k in ks:rows[candidate['ret'][k]]^=snapshot[j]
 run(candidate['B']);run(candidate['C']);expect=[1<<i for i in range(n)]
 for i in range(v):expect[v+i if orientation=='forward' else i]^=1<<(i if orientation=='forward' else v+i)
 assert rows==expect
cur=candidate['start'][:];HH=Counter()
for phase in ('A','B'):
 if phase=='B':
  assert all(cur[y]==0 for y in range(v,2*v))
  for r in candidate['ret']:assert len(F[cur[r]])==8;HH[8]+=1
 for f,t,ss in candidate[phase]:
  for r in [t]+ss:
   if cur[r]!=f:
    assert contained(F[cur[r]],F[f]);delta=len(F[f])-len(F[cur[r]]);assert delta>0;HH[delta]+=1;cur[r]=f
for r,f in enumerate(candidate['final']):
 if cur[r]!=f:
  assert contained(F[cur[r]],F[f]);delta=len(F[f])-len(F[cur[r]]);assert delta>0;HH[delta]+=1;cur[r]=f
assert HH==H
out.update(exact_candidate_sha256=hashlib.sha256(json.dumps(candidate,sort_keys=True,separators=(',',':')).encode()).hexdigest(),exact_candidate_both_orientations=True,exact_candidate_rational_frame_walk=True)
json.dump(out,open(str(ROOT / 'e8_bit_gauge_independent_audit_results.json'),'w'),indent=2);print('Exactcandidate bothorientations and Qframes PASS',out['exact_candidate_sha256'])
# Source-span over integer support (union, not F2cancellation), plus targetcaps.
roots=[tuple(map(Q,r)) for r in candidate['lines']]
supp=[1<<i if i<v else 0 for i in range(n)]
frame_root_masks=[sum(1<<i for i in fr) for fr in candidate['frames']]
for phase in ('D','A','B','C'):
 for f,t,ss in candidate[phase]:
  assert t>=v and t not in ss and len(ss)==len(set(ss))
  for s in ss:
   if s<v or s>=2*v:
    missing=supp[s]&~frame_root_masks[f]
    for i in range(v):
     if missing>>i&1:assert contained((roots[i],),F[f])
   supp[t]|=supp[s]
  if t>=2*v:
   missing=supp[t]&~frame_root_masks[f]
   for i in range(v):
    if missing>>i&1:assert contained((roots[i],),F[f])
for i in range(v):
 assert F[candidate['start'][i]]==basis([candidate['lines'][i]])
 cap=basis([row for row in candidate['lines'] if sum(Q(a)*b for a,b in zip(row,candidate['lines'][i]))==0])
 assert F[candidate['final'][v+i]]==cap and len(cap)==7
out.update(exact_integer_support_containment=True,exact_rational_target_caps=True)
json.dump(out,open(str(ROOT / 'e8_bit_gauge_independent_audit_results.json'),'w'),indent=2);print('Integer-source spans andrationaltargetcaps PASS')
