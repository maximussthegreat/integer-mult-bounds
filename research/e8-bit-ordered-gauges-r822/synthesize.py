# Independent literal entrance-gauge composition onto the frozen R822 bit word.
import json,copy,hashlib
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).parent;b=json.load(open(P/'bit_r822.json'));p=json.load(open(P/'pools.json'));v=120;R=822;n=1062
sel=[x for x in p['transferred382'] if x['response_ok'] and x['first_frame_ok'] and x['distinct']];sel.sort(key=lambda x:(x['dimension'],tuple(x['entrance_roots']),x['pivot']))
piv={x['pivot'] for x in sel};don={z for x in sel for z in x['donors']};assert len(piv)==len(sel) and not piv&don
frames=[frozenset(x) for x in b['frames']];dims=p['frame_dimensions'][:];prefix=[];c=copy.deepcopy(b)
for x in sel:
 E=frozenset(x['entrance_roots'])
 if E not in frames:frames.append(E);c['frames'].append(sorted(E));dims.append(x['dimension'])
 f=frames.index(E);c['start'][x['pivot']]=f;x['frame']=f
 for d in x['donors']:prefix.append([f,d,[x['pivot']]])
c['A']=prefix+c['A'];c['C']=[[1,t,list(ss)] for f,t,ss in (c['A']+c['B'])[::-1] if t>=240]
def phase(rows,ops):
 for f,t,ss in ops:
  for s in ss:rows[t]^=rows[s]
def scat(rows):
 temp=[rows[r] for r in c['ret']]
 for t,ks in enumerate(c['scatter']):
  for k in ks:rows[120+t]^=temp[k]
raw=[0]*240+[1<<j for j in range(R)];phase(raw,c['A']);scat(raw);phase(raw,c['B']);K=raw[120:240]
assert all(not(row>>(q-240)&1) for q in piv for row in K)
c['D']=[[0,120+t,[240+j for j in range(R) if row>>j&1]] for t,row in enumerate(K) if row]
rows=[1<<i for i in range(n)];phase(rows,c['D']);phase(rows,c['A']);scat(rows);phase(rows,c['B']);phase(rows,c['C']);want=[1<<i for i in range(n)]
for t in range(v):want[v+t]^=1<<t
assert rows==want
# Literal prefix inversion check independent of target cancellation.
rows=[1<<i for i in range(n)];phase(rows,prefix);phase(rows,prefix[::-1]);assert rows==[1<<i for i in range(n)]
# Chronological exact frame chain. Original closed rootsets make inclusion literal setinclusion.
cur=list(c['start']);H=Counter()
for phase_name in ['D','A','B']:
 if phase_name=='B':
  for r in c['ret']:H[dims[cur[r]]]+=1
 for f,t,ss in c[phase_name]:
  for r in [t]+ss:
   assert frames[cur[r]]<=frames[f],(phase_name,r,cur[r],f)
   if cur[r]!=f:H[dims[f]-dims[cur[r]]]+=1;cur[r]=f
for r,f in enumerate(c['final']):
 assert frames[cur[r]]<=frames[f]
 if cur[r]!=f:H[dims[f]-dims[cur[r]]]+=1;cur[r]=f
for f,t,ss in c['C']:assert all(cur[r]==f for r in [t]+ss)
residual=Counter(8-dims[c['start'][r]] for r in range(240,n));assert sum(r*z for r,z in residual.items())==6417
assert sum(r*z for r,z in H.items())==1680+6417+72
blob=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(P/'candidate111.json').write_bytes(blob)
receipt=dict(status='PASS_LITERAL_111_GAUGE_LOCAL_SCALAR_FRAMES',word_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((P/'bit_r822.json').read_bytes()).hexdigest(),formal_columns=n,gauges=len(sel),entrance_mass=159,entrance_gates=len(prefix),donors=len(don),entrance_rank_histogram=dict(Counter(x['dimension'] for x in sel)),local_histogram=dict(sorted(H.items())),local_rank_mass=sum(r*z for r,z in H.items()),residual_inventory=dict(sorted(residual.items())),selection=sel,scope='F2 dirty scalar/inverse prefix and rootset frame nesting; independent rational geometric audit, changed entrance-completion/global routes and invoice still required.')
(P/'candidate111_receipt.json').write_text(json.dumps(receipt,indent=2));print({k:x for k,x in receipt.items() if k!='selection'})
