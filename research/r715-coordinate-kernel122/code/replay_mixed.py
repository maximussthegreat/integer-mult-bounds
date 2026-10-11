"""Rebuild literal local records/profile and verify all formal F2 columns."""
import sys,json
from pathlib import Path
from collections import Counter
P=Path(sys.argv[1]).resolve();w=json.loads((P/'mixed_word.json').read_text());k=json.loads((P/'kernel_word.json').read_text());f=json.loads((P/'frame_metadata.json').read_text());dim=f['dims'];cl=list(map(int,f['closures']))
assert w['frames']==k['frames'] and w['start']==k['start'] and w['final']==k['final'] and w['lines']==k['lines']
cur=w['start'][:];value=[1<<i for i in range(955)];records=[];hist=Counter();fullmask=(1<<120)-1
# Source-support check for original source and helper operands; target operands
# use the separately checked common-frame mutable-label interface.
def move(i,f):
 old=cur[i];assert not(cl[old]&~cl[f])
 if dim[f]>dim[old]:records.append([0,i,old,f,dim[f]-dim[old],0]);hist[dim[f]-dim[old]]+=1
 cur[i]=f

def phase(name):
 for f,d,ss in w[name]:
  assert d>=120 and d not in ss and len(set(ss))==len(ss)
  for i in [d]+ss:move(i,f)
  for i in ss:
   if i<120 or i>=240:assert not((value[i]&fullmask)&~cl[f])
   value[d]^=value[i];records.append([1,d,i,1,f,0])
  if d>=240:assert not((value[d]&fullmask)&~cl[f])
phase('D');phase('A');assert all(dim[cur[i]]==0 for i in range(120,240))
for j,q in enumerate(w['ret']):
 assert dim[cur[q]]==8;records.append([2,q,955,cur[q],0,8,0]);hist[8]+=1
 for t,seq in enumerate(w['scatter']):
  if j in seq:value[120+t]^=value[q];records.append([1,120+t,955,1,0,0])
 records.append([3,q,955,cur[q],0,0,0])
phase('B');phase('C')
for i in range(955):move(i,w['final'][i])
assert value==[(1<<i)^((1<<(i-120)) if 120<=i<240 else 0) for i in range(955)]
assert records==json.loads((P/'mixed_records.json').read_text())
claim=json.loads((P/'mixed_check.json').read_text());assert hist==Counter({int(r):n for r,n in claim['profile'].items()})
width=Counter(8-dim[w['start'][i]] for i in range(240,955));assert width==Counter({int(r):n for r,n in claim['widths'].items()})
assert claim['adds']==sum(r[0]==1 for r in records) and claim['records']==len(records)
print('PASS reconstructed mixed records, exact frames, F2 source support and all955 formal columns')
