import sys
"""Exact whole-family expansion, physical prefix and fresh conservative invoice."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as F
import json,hashlib,copy
P=Path(sys.argv[1]).resolve()
mix=json.loads((P/'mixed_word.json').read_text());fm=json.loads((P/'frame_metadata.json').read_text());dims=fm['dims']
H=json.loads((P/'mixed_check.json').read_text());pack=json.loads((P/'packing_4.json').read_text());rec=json.loads((P/'mixed_records.json').read_text());sched=json.loads((P/'schedule.json').read_text());T=4;V=120;R=715;L=11;N=955;W=4800;M=78
# Independently derive windows from chronology.
last={};seen=[];wins={}
for pos,e in enumerate(sched):
 if e[0]=='l':seen.append((pos,e[1],e[2]));last[e[2]]=pos
 elif e[0]=='b':last[e[1]]=last[e[2]]=pos
 elif e[0]=='i':
  _,i,p,r=e
  if r:wins[i]=(p,r,{s for q,s,p2 in seen if last.get(p,-1)<q<pos and p2!=p})
width=[8-dims[mix['start'][240+h]] for h in range(R)];ws=sorted(set(width));by=defaultdict(list)
for s in range(L):
 for h in range(R*T):by[s,width[h%R]].append(h)
ys=defaultdict(list);zs=defaultdict(list)
for k,count in pack['selection']:
 if k[0]=='y':ys[k[1]].append((k[2],count))
 else:
  _,i,s,w=k
  assert s in wins[i][2]
  zs[i,w].extend([s]*count)
slots=[];rems=Counter();host={};used={}
for i,(p,r,stages) in sorted(wins.items()):
 cp=0
 for pat,count in sorted(ys[i],key=lambda z:sum(w*n for w,n in zip(ws,z[0])),reverse=True):
  assert all(x>=0 and int(x)==x for x in pat)
  for _ in range(count):
   off=0
   for w,n in reversed(list(zip(ws,pat))):
    for _ in range(n):
     s=zs[i,w].pop();h=by[s,w].pop();assert (s,h) not in host
     assert off+w<=r;slot=[i,cp,off,w,s,h];slots.append(slot);host[s,h]=slot;off+=w
   rems[r-off]+=1;cp+=1
 assert cp==240*T
assert len(slots)==L*R*T and not any(by.values()) and not any(zs.values())
rems.pop(0,None)
paid=Counter({int(r):n*L*T for r,n in H['profile'].items()});paid.update(rems)
assert paid==Counter({int(r):n for r,n in pack['profile'].items() if n})
assert M*W-sum(r*n for r,n in paid.items())==408*T
owners={}
for s in range(L):
 p=max(0,(s-1)//2);reverse=s%2
 for replica in range(T):
  row=[replica*1200+(2*p+(1-x//V if reverse else x//V))*V+x%V for x in range(240)]
  for h in range(R):
   i,cp,off,w,ss,hh=host[s,replica*R+h];hostrep,within=divmod(cp,240);side,port=divmod(within,120)
   assert ss==s and hh==replica*R+h and w==width[h] and wins[i][0]!=p
   row.append(hostrep*1200+(2*wins[i][0]+side)*120+port)
  owners[s,replica]=row
# Create inverse program with signed inverse ADDs and reverse copy/erase roles.
reverse=[]
for z in reversed(rec):
 if z[0]==0:reverse.append([0,z[1],z[3],z[2],z[4],1])
 elif z[0]==1:reverse.append([1,z[1],z[2],-z[3],z[4],1])
 elif z[0]==3:reverse.append([2,z[1],z[2],z[3],z[4],8,1])
 else:reverse.append([3,z[1],z[2],z[3],z[4],0,1])
# Independent local reverse semantics, with private centre restored.
for name,program in [('forward',rec),('reverse',reverse)]:
 val=[1<<j for j in range(N)]+[0];openq=None
 for z in program:
  op=z[0]
  if op==1:val[z[1]]^=val[z[2]]
  elif op==2:assert openq is None and val[N]==0;openq=z[1];val[N]=val[z[1]]
  elif op==3:assert openq==z[1] and val[N]==val[z[1]];openq=None;val[N]=0
 assert val==[(1<<j)^((1<<(j-V)) if V<=j<240 else 0) for j in range(N)]+[0]
# Scalar full chronology on physical family upper bounds. Each literal ADD
# increases its destination by the source even if both owners coincide.
bounds=[1]*W+[0];peak=1;events=0;digest=hashlib.sha256()
for e in sched:
 if e[0]=='l':
  s=e[1];pr=reverse if s%2 else rec
  for replica in range(T):
   own=owners[s,replica]
   for z in pr:
    op=z[0];x=own[z[1]]
    if op==1:
     y=own[z[2]] if z[2]<N else W;bounds[x]+=abs(z[3])*bounds[y]
    elif op==2:bounds[W]=bounds[x]
    elif op==3:bounds[W]=0
    peak=max(peak,bounds[x],bounds[W]);events+=1
    digest.update(json.dumps([s,replica,z,own[z[1]],own[z[2]] if op and z[2]<N else W],separators=(',',':')).encode()+b'\n')
 elif e[0]=='b':
  _,d,s,c=e
  for rep in range(T):
   for port in range(V):
    for x,y in [(rep*1200+2*d*V+port,rep*1200+2*s*V+port),(rep*1200+(2*s+1)*V+port,rep*1200+(2*d+1)*V+port)]:
     bounds[x]+=abs(c)*bounds[y];peak=max(peak,bounds[x])
assert bounds[W]==0
# Formula follows the pinned finite-operation categories, newly evaluated.
# All finite address routes are generously billed 2*m^2 elementary factors.
E=sum(paid.values());physical=W+9;unit=L*T*H['adds']+24*V*T;J=8*T*L*(2*V+R)+8*W+2*L*T*R+2*(9*L*T)
selectors=2*L*T*((W-1)+R*M*(2*M*M+2*M*M+4+M-1+M))
coefficient=unit+J*(16*(M*M+1)**2)+J*physical+E*(8*M*M+8+128*(2*M)**3)+16*M**3+9*L*T+selectors+peak+1
three=(coefficient+1)**3*(E+1)**3
charge=lambda n:64*((n.bit_length()+63)//64)
over=0
while 3**over<=physical:over+=1
row=3*(M*(M+1)//2+over)+9909+252
assert row<20161 and M**3>2*max(paid)**3
report={'status':'PASS_COMPONENT_F2_FRAMES_WHOLE_PACKING_AND_NEW_SCALAR_PREFIX','replicas':T,'live':W,'physical':physical,'hosted_residuals':len(slots),'profile':dict(sorted(paid.items())),'idle_profile':dict(sorted(rems.items())),'rank_mass':sum(r*n for r,n in paid.items()),'deficit':408*T,'maxchild':max(paid),'expanded_event_count':events,'expanded_sha256':digest.hexdigest(),'prefix_bound':str(peak),'prefix_bits':peak.bit_length(),'charged_prefix_bits':charge(peak),'invoice_coefficient_bits':coefficient.bit_length(),'three_level_coefficient_bits':three.bit_length(),'charged_three_level_bits':charge(three),'row_coefficient':row,'routing_factor_charge_per_selector':2*M*M*2+4+M-1+M,'limits':['The607-bit quantity is only a scalar physical-family envelope; no full routed/literal compiler-prefix bound is certified.','Rational entrance isometries and denominator checks are handled separately.','Component invoice overcharges finite coordinate elimination; source-bound full supplier receipt remains required.']}
(P/'whole_slots.json').write_text(json.dumps(slots,separators=(',',':')));(P/'ownership.json').write_text(json.dumps([[s,r,own] for (s,r),own in sorted(owners.items())],separators=(',',':')));(P/'packing_certificate.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
