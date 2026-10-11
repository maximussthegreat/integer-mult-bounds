import sys
"""Independent negative controls for the new component witness."""
from pathlib import Path
from collections import defaultdict
import json,copy
P=Path(sys.argv[1]).resolve();w=json.loads((P/'mixed_word.json').read_text());kernel=json.loads((P/'kernel_word.json').read_text());sel=json.loads((P/'mix_selection.json').read_text());schedule=json.loads((P/'schedule.json').read_text());slots=json.loads((P/'whole_slots.json').read_text());width=[8-d for d in []]
fmeta=json.loads((P/'frame_metadata.json').read_text());width=[8-fmeta['dims'][w['start'][x]] for x in range(240,955)]
def replay(c):
 values=[1<<i for i in range(955)]
 for ph in ['D','A']:
  for _,d,ss in c[ph]:
   for s in ss:values[d]^=values[s]
 for j,q in enumerate(c['ret']):
  for t,row in enumerate(c['scatter']):
   if j in row:values[120+t]^=values[q]
 for ph in ['B','C']:
  for _,d,ss in c[ph]:
   for s in ss:values[d]^=values[s]
 return values==[(1<<i)^((1<<(i-120)) if 120<=i<240 else 0) for i in range(955)]
assert replay(w)
controls=[]
def reject(name,c):
 assert not replay(c),name;controls.append(name)
q=copy.deepcopy(w);q['D'].pop();reject('omit one target preconditioner',q)
q=copy.deepcopy(w);q['D'][-84:]=list(reversed(q['D'][-84:]));reject('wrong forward-topological preconditioning',q)
q=copy.deepcopy(w);q['scatter']=copy.deepcopy(kernel['scatter']);reject('omit scatter preconditioning',q)
q=copy.deepcopy(w);q['C'].pop();reject('omit final donor cleanup',q)
q=copy.deepcopy(w);q['A'].pop(0);reject('omit entrance donor injection',q)
# Verify every slot and all stage occurrences without trusting the expander.
last={};past=[];windows={}
for pos,e in enumerate(schedule):
 if e[0]=='l':past.append((pos,e[1],e[2]));last[e[2]]=pos
 elif e[0]=='b':last[e[1]]=last[e[2]]=pos
 elif e[0]=='i' and e[3]:windows[e[1]]=(e[2],e[3],set(s for p,s,j in past if p>last.get(e[2],-1) and j!=e[2]))
def valid(z):
 seen=set();occupied=defaultdict(int)
 for i,cp,off,wd,s,h in z:
  assert i in windows and s in windows[i][2] and 0<=cp<960 and 0<=h<2860
  assert wd==width[h%715] and 0<=off and off+wd<=windows[i][1]
  assert (s,h) not in seen;seen.add((s,h))
  mask=((1<<wd)-1)<<off;assert not occupied[i,cp]&mask;occupied[i,cp]|=mask
 assert seen=={(s,h) for s in range(11) for h in range(2860)}
valid(slots)
for name,change in [
 ('missing residual',lambda z:z.pop()),
 ('duplicate residual',lambda z:z.append(z[0][:])),
 ('slot outside physical family',lambda z:z[0].__setitem__(1,960)),
 ('slot negative offset',lambda z:z[0].__setitem__(2,-1)),
 ('wrong residual width',lambda z:z[0].__setitem__(3,z[0][3]+1)),
 ('slot outside untouched window',lambda z:z[0].__setitem__(4,10)),
]:
 z=copy.deepcopy(slots);change(z)
 try:valid(z)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
# Eleven stage identity over Z, retaining both signed bridge shears.
def full(skip=-1):
 a=[[int(i==j) for j in range(10)] for i in range(10)];bridge=0
 def add(d,s,c):a[d]=[x+c*y for x,y in zip(a[d],a[s])]
 for e in schedule:
  if e[0]=='l':
   _,st,p=e
   if st%2:add(2*p,2*p+1,-1)
   else:add(2*p+1,2*p,1)
  elif e[0]=='b':
   _,d,s,c=e
   for x,y,v in [(2*d,2*s,c),(2*s+1,2*d+1,-c)]:
    if bridge!=skip:add(x,y,v)
    bridge+=1
 for p in range(5):a[2*p],a[2*p+1]=a[2*p+1],[-x for x in a[2*p]]
 return a
identity=[[int(i==j) for j in range(10)] for i in range(10)];assert full()==identity
for i in range(24):assert full(i)!=identity;controls.append('omit bridge shear '+str(i))
report={'status':'PASS_NEGATIVE_CONTROLS','count':len(controls),'rejected':controls,'complete_ten_wire_signed_identity':True}
(P/'controls_certificate.json').write_text(json.dumps(report,indent=2));print(report['status'],len(controls))
