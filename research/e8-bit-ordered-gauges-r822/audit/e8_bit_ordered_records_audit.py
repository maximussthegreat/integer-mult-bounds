"""Independent PR249-format emitter/readback. Upstream format specification only."""
import os,json,struct,hashlib
from pathlib import Path
from fractions import Fraction as Q
from math import lcm,gcd
from collections import Counter
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent));ROOT.mkdir(parents=True,exist_ok=True)
DATA=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'))
w=json.loads((DATA/'candidate_ordered.json').read_text());h=w['h'];v=w['v'];n=2*v+w['R']
def rref(rows):
 a=[list(map(Q,row)) for row in rows];p=[];i=0
 for c in range(h):
  j=next((j for j in range(i,len(a)) if a[j][c]),None)
  if j is None:continue
  a[i],a[j]=a[j],a[i];d=a[i][c];a[i]=[x/d for x in a[i]]
  for k in range(len(a)):
   if k!=i:
    d=a[k][c];a[k]=[x-d*y for x,y in zip(a[k],a[i])]
  p.append(c);i+=1
 return a[:i],p
F={}
for f,ids in enumerate(w['frames']):
 B=[]
 for k in ids:
  if len(rref(B+[w['lines'][k]])[0])>len(B):B.append(w['lines'][k])
 rr,p=rref(B);A=[]
 for c in set(range(h))-set(p):
  a=[Q(int(i==c)) for i in range(h)]
  for row,j in zip(rr,p):a[j]=-row[c]
  d=lcm(*(x.denominator for x in a));a=[int(x*d) for x in a];g=gcd(*a);A.append([x//g for x in a])
 assert len(A)+len(B)==h and all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B)
 F[str(f)]={'dim':len(B),'B':B,'A':A}
dim=lambda f:F[str(f)]['dim']
cur=w['start'][:];records=[]
def advance(r,f):
 if cur[r]!=f:records.append((0,r,cur[r],f,dim(f)-dim(cur[r]),0));cur[r]=f
for phase,tag in [('D',1),('A',2),('scatter',3),('B',4),('C',5)]:
 if phase=='scatter':
  for k,r in enumerate(w['ret']):
   records.append((2,r,n,cur[r],0,dim(cur[r])))
   records.extend((1,v+j,n,1,0,3) for j,ks in enumerate(w['scatter']) if k in ks)
   records.append((3,r,n,cur[r],0,0))
 else:
  for f,t,ss in w[phase]:
   for r in [t]+ss:advance(r,f)
   records.extend((1,t,s,1,f,tag) for s in ss)
for r,f in enumerate(w['final']):advance(r,f)
out=ROOT/'ordered175-pr249';out.mkdir(exist_ok=True)
(out/'249-records.bin').write_bytes(b''.join(struct.pack('<6i',*r) for r in records))
(out/'frames.json').write_text(json.dumps({'frames':F},sort_keys=True,separators=(',',':')))
st={'n':n,'v':v,'h':h,'R':w['R'],'ZERO':0,'initial':dict(enumerate(w['start'])),'final':dict(enumerate(w['final'])),'retained_totals':w['ret'],'source_owned_roles':[],'regs':[]}
(out/'249-states.json').write_text(json.dumps(st,sort_keys=True,separators=(',',':')))
# Read the serialized representation anew. Validate address-frame incidences and
# arbitrary-dirty F2 columns, COPY source immutability, and exact inverse.
fresh=json.loads((out/'frames.json').read_text())['frames'];raw=(out/'249-records.bin').read_bytes();assert len(raw)%24==0
parsed=list(struct.iter_unpack('<6i',raw));assert parsed==records
H=Counter();counts=Counter();cur=w['start'][:];z=[1<<i for i in range(n)]+[0];opened=None
for kind,a,b,c,d,e in parsed:
 counts[kind]+=1
 if kind==0:
  assert cur[a]==b and d==dim(c)-dim(b)>0
  assert len(rref(fresh[str(c)]['B']+fresh[str(b)]['B'])[0])==dim(c)
  cur[a]=c;H[d]+=1
 elif kind==1:
  assert c==1 and a!=b and cur[a]==d and (b==n and opened is not None or b<n and cur[b]==d)
  assert opened is None or a!=opened[0]
  z[a]^=z[b]
 elif kind==2:
  assert opened is None and b==n and cur[a]==c and d==0 and e==8
  z[n]=z[a];opened=(a,z[a]);H[e]+=1
 elif kind==3:
  assert opened==(a,z[a]) and b==n and cur[a]==c and d==e==0 and z[n]==z[a]
  z[n]=0;opened=None # ERASE has rank zero in PR249 accounting.
 else:raise AssertionError(kind)
assert cur==w['final'] and opened is None
expected=[1<<i for i in range(n)]
for j in range(v):expected[v+j]^=1<<j
assert z[:n]==expected and z[n]==0
# Reverse chronological scalar records, preserving exact COPY/ERASE binding.
for kind,a,b,c,d,e in reversed(parsed):
 if kind==0:assert cur[a]==c;cur[a]=b
 elif kind==1:z[a]^=z[b]
 elif kind==3:assert opened is None;opened=(a,z[a]);z[n]=z[a]
 elif kind==2:assert opened==(a,z[a]) and z[n]==z[a];z[n]=0;opened=None
assert cur==w['start'] and z==[1<<i for i in range(n)]+[0]
assert H==Counter({1:2294,2:1047,3:362,4:407,5:155,8:18}) and counts[1]==14976 and counts[2]==counts[3]==9
receipt={'pass':True,'records':len(parsed),'record_bytes':len(raw),'opcode_counts':dict(counts),'local_histogram':dict(H),'all_dirty_columns':n,'literal_inverse':True,'frames':len(F),'files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},'scope':'PR249-style local logical instruction artifact with exact rational frames; global owner-bank routes and finite invoice are independently certified by companion audits.'}
(ROOT/'e8_bit_ordered_records_audit_results.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
