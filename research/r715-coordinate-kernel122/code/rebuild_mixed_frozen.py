import sys
"""Reconstruct target mixing from a frozen witness; no floating search."""
from pathlib import Path
from collections import defaultdict
import json,copy,hashlib
P=Path(sys.argv[1]).resolve();c=json.loads((P/'kernel_word.json').read_text());s=json.loads((P/'mix_selection.json').read_text());f=json.loads((P/'frame_metadata.json').read_text());dims=f['dims'];cl=list(map(int,f['closures']))
sub=lambda x,y:cl[x]&~cl[y]==0
parent={a:b for a,b,g in s};at={a:g for a,b,g in s};order=[a for a,b,g in s]
assert len(parent)==len(s)==84
position={a:i for i,a in enumerate(order)}
for a,b,g in s:
 assert a!=b and (b not in position or position[b]<position[a])
 assert sub(g,c['final'][a])
 if b in at:assert sub(at[b],g)
 seq={t:[z for z in c['B'] if z[1]==t] for t in [a,b]}
 def prefix(t):
  v=0
  for ff,_,ss in seq[t]:
   if sub(ff,g):
    for x in ss:v^=1<<x
  return v
 assert prefix(a)==prefix(b)!=0
 assert all(sub(g,ff) for ff,_,ss in seq[a] if not sub(ff,g))
w=copy.deepcopy(c);w['D'] += [[0,a,[parent[a]]] for a in reversed(order)]
for a in order:w['scatter'][a-120]=sorted(set(c['scatter'][a-120])^set(c['scatter'][parent[a]-120]))
kept=[z for z in c['B'] if z[1] not in parent or not sub(z[0],at[z[1]])]
w['B']=[]
for d in range(9):
 w['B'] += [z for z in kept if dims[z[0]]==d]
 w['B'] += [[at[a],a,[parent[a]]] for a in order if dims[at[a]]==d]
expected=json.loads((P/'mixed_word.json').read_text());assert w==expected
print('PASS frozen 84-target mixing reconstruction',hashlib.sha256((P/'mixed_word.json').read_bytes()).hexdigest())
