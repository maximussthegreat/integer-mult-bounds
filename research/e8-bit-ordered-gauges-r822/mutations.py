"""Negative controls, independently authored; never executes vendored sources."""
import json,copy
from fractions import Fraction
from pathlib import Path
P=Path(__file__).resolve().parent
c=json.load(open(P/'candidate_ordered.json'));b=json.load(open(P/'bit_r822.json'));n=1062

def scalar(w):
 z=[1<<i for i in range(n)]
 for ph in ['D','A','SCATTER','B','C']:
  if ph=='SCATTER':
   snap=[z[r] for r in w['ret']]
   for j,ks in enumerate(w['scatter']):
    for k in ks:z[120+j]^=snap[k]
  else:
   for f,t,ss in w[ph]:
    for s in ss:z[t]^=z[s]
 expected=[1<<i for i in range(n)]
 for i in range(120):expected[120+i]^=1<<i
 return z==expected
assert scalar(c)
rejected=[]
w=copy.deepcopy(c);w['A'].pop(0);assert not scalar(w);rejected.append('omit first entrance XOR')
w=copy.deepcopy(c);w['C'].pop();assert not scalar(w);rejected.append('omit final inverse entrance XOR')
np=len(c['A'])-len(b['A']);w=copy.deepcopy(c);w['C'][-np:]=list(reversed(w['C'][-np:]));assert not scalar(w);rejected.append('use forward order instead of chronological inverse')
w=copy.deepcopy(c);w['D'][0][2].pop();assert not scalar(w);rejected.append('omit one dirty compensation source')
price=json.load(open(P/'price_ordered.json'))['results'][0];H={int(k):v for k,v in price['profile'].items()};assert H[32]==9
H[32]-=9;assert 72*price['live']-sum(r*n for r,n in H.items())!=price['deficit'];rejected.append('omit compulsory rank32 padding calls')
# A nonzero entrance must be contained in its first common frame. Force a missing axis.
first={}
for f,t,ss in c['D']+c['A']+c['B']:
 for r in [t]+ss:first.setdefault(r,f)
r=next(r for r in range(240,n) if c['start'][r] and len(c['frames'][first[r]])<120)
f=first[r];axis=next(i for i in range(8) if i not in c['frames'][f]);assert axis not in c['frames'][f]
def rank(rows):
 B={}
 for row in rows:
  row=list(map(Fraction,row))
  for k,b in sorted(B.items()):
   if row[k]:q=row[k];row=[x-q*y for x,y in zip(row,b)]
  k=next((k for k,x in enumerate(row) if x),None)
  if k is not None:q=row[k];B[k]=[x/q for x in row]
 return len(B)
rows=[c['lines'][i] for i in c['frames'][f]]
assert rank(rows+[c['lines'][axis]])==rank(rows)+1
rejected.append('force missing coordinate axis into entrance frame')
(P/'mutation_results.json').write_text(json.dumps({'status':'PASS','negative_controls':rejected,'columns':n},indent=2))
print('PASS',len(rejected),'negative controls')
