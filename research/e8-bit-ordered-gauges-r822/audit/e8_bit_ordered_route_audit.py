# Independent standard-library Gram and explicitdyadicport-route audit.
import json,gzip,hashlib,os
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,deque
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent));P=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'));w=json.load(open(P/'candidate_ordered.json'));base=json.load(open(P/'bit_r822.json'));assert w['lines']==base['lines'] and w['frames']==base['frames']
h=8;roots=w['lines'];I=[[Q(i==j) for j in range(h)] for i in range(h)]
def mm(A,B):return [[sum((a*b for a,b in zip(row,col)),Q(0)) for col in zip(*B)] for row in A]
def tr(A):return list(map(list,zip(*A)))
def selected_basis(ids):
 echelon={};chosen=[]
 for idx in ids:
  x=list(map(Q,roots[idx]))
  for k,row in sorted(echelon.items()):
   a=x[k]
   if a:x=[u-a*v for u,v in zip(x,row)]
  k=next((j for j,a in enumerate(x) if a),None)
  if k is not None:a=x[k];echelon[k]=[v/a for v in x];chosen.append(idx)
 return chosen
def determinant(A):
 A=[r[:] for r in A];d=Q(1)
 for j in range(len(A)):
  k=next(i for i in range(j,len(A)) if A[i][j])
  if k!=j:A[k],A[j]=A[j],A[k];d=-d
  p=A[j][j];d*=p
  for i in range(j+1,len(A)):
   a=A[i][j]/p
   if a:A[i]=[u-a*v for u,v in zip(A[i],A[j])]
 return d
frames=[]
for f,ids in enumerate(w['frames']):
 B=selected_basis(ids);G=[[Q(sum(x*y for x,y in zip(roots[a],roots[b])),2) for b in B] for a in B];d=determinant(G)
 assert d>0 and d.numerator&(d.numerator-1)==0 and d.denominator&(d.denominator-1)==0
 frames.append(dict(frame=f,basis_root_ids=B,Gram_determinant=str(d)))
# BFS exact E8reflectionwords; a mapsreference root to plus/minusitself.
maps={0:I};words={0:[]};queue=deque([0])
while queue:
 a=queue.popleft()
 for b in range(120):
  if b in maps:continue
  dot=Q(sum(x*y for x,y in zip(roots[a],roots[b])),2)
  if abs(dot)!=1:continue
  d=[x-y if dot==1 else x+y for x,y in zip(roots[a],roots[b])];assert sum(x*x for x in d)==4
  refl=[[Q(i==j)-Q(d[i]*d[j],2) for j in range(8)] for i in range(8)]
  maps[b]=mm(refl,maps[a]);words[b]=words[a]+[d];queue.append(b)
assert len(maps)==120 and roots[0]==[2,0,0,0,0,0,0,0]
cert=[];denoms=set();maximum=0
for port in range(120):
 g=maps[port];assert mm(g,tr(g))==I;gq=[2*row[0] for row in g];assert gq==roots[port] or gq==[-x for x in roots[port]]
 P=[[Q(i==j==0) for j in range(8)] for i in range(8)]
 TL=[[g[i][0]*g[j][0] for j in range(8)] for i in range(8)];TR=[[g[i][j] if j else Q(0) for j in range(8)] for i in range(8)];BL=[[g[j][i] if i else Q(0) for j in range(8)] for i in range(8)]
 rho=[TL[i]+TR[i] for i in range(8)]+[BL[i]+P[i] for i in range(8)];I16=[[Q(i==j) for j in range(16)] for i in range(16)];assert mm(rho,rho)==I16
 A=[r[:] for r in rho];ops=[]
 for j in range(16):
  k=next(i for i in range(j,16) if A[i][j])
  if k!=j:A[j],A[k]=A[k],A[j];ops.append(('swap',j,k,Q(1)))
  if A[j][j]!=1:
   a=1/A[j][j];A[j]=[a*x for x in A[j]];ops.append(('scale',j,j,a))
  for i in range(16):
   if i!=j and A[i][j]:a=-A[i][j];A[i]=[x+a*y for x,y in zip(A[i],A[j])];ops.append(('add',i,j,a))
 assert A==I16
 def replay(skip=None):
  A=[r[:] for r in I16]
  for idx in reversed(range(len(ops))):
   if idx==skip:continue
   kind,i,j,a=ops[idx]
   if kind=='swap':A[i],A[j]=A[j],A[i]
   elif kind=='scale':A[i]=[x/a for x in A[i]]
   else:A[i]=[x-a*y for x,y in zip(A[i],A[j])]
  return A
 assert replay()==rho and replay(0)!=rho
 for kind,i,j,a in ops:
  assert a.denominator&(a.denominator-1)==0;denoms.add(a.denominator)
 maximum=max(maximum,len(ops));cert.append(dict(port=port,reflection_word=words[port],elimination_operations=[[k,i,j,str(a)] for k,i,j,a in ops]))
with gzip.open(ROOT/'e8_bit_ordered_port_routes.json.gz','wt') as f:json.dump(cert,f,separators=(',',':'))
json.dump(frames,open(ROOT/'e8_bit_ordered_Gram_certificate.json','w'),separators=(',',':'))
out=dict(status='PASS_ALL944_GRAMS_AND120_LITERAL_DYADIC_ROUTES',frame_count=len(frames),Gram_prime_set=[2],Gram_determinants=sorted(set(x['Gram_determinant'] for x in frames)),port_routes=120,max_elementary_factors=maximum,factor_denominators=sorted(denoms),inverse_reconstruction_checks=120,omitted_factor_controls=120,scope='Exact rationaladdressgeometry and explicitrouteprograms, unchangedfromcurrentR822roots/frames. No upstreamprogramsexecuted.')
json.dump(out,open(ROOT/'e8_bit_ordered_route_audit_results.json','w'),indent=2);print(json.dumps(out,indent=2))
