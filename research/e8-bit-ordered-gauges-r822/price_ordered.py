from decimal import Decimal as D,localcontext
from collections import Counter
from pathlib import Path
import json,math
P=Path(__file__).parent;c=json.load(open(P/'ordered_result.json'));res={int(r):n for r,n in c['residual_inventory'].items()};results=[]
for T in [8,16,24,32,40,48,56,64,72]:
 counts={r:T*n for r,n in res.items()};patterns=[]
 # All testedT multiples8; seven-width pieces in batches8, two4s with eight8s.
 a=counts[7]//8;assert counts[7]%8==0;counts[7]-=8*a;counts[8]-=2*a;patterns.append(dict(count=a,ranks={7:8,8:2}))
 a=counts[4]//2;assert counts[4]%2==0;counts[4]-=2*a;counts[8]-=8*a;patterns.append(dict(count=a,ranks={4:2,8:8}))
 assert counts[8]>=0;a,left=divmod(counts[8],9);patterns.append(dict(count=a,ranks={8:9}));pad=0
 if left:pad=72-8*left;patterns.append(dict(count=1,ranks={8:left},padding=pad))
 B=sum(p['count'] for p in patterns);m=72;L=9;W=960*T+9*B;H=Counter({int(r):T*9*n for r,n in c['local_histogram'].items()})
 for r in [14,7,28,7,42,7,50,36,22,8]:H[r]+=240*T
 if pad:
  if pad>50:H[50]+=9;H[pad-50]+=9
  else:H[pad]+=9
 assert m*W-sum(r*n for r,n in H.items())==312*T and m*m>2*max(H)**2
 with localcontext() as ctx:
  ctx.prec=65
  def f(s):return sum(D(r*n)/(m*W)*(D(m)/r)**s for r,n in H.items())+D(32*m*sum(H.values()))/(D(10)**16*W)*D(m)**s
  a,b=D(0),D('.01')
  for _ in range(200):
   mid=(a+b)/2
   if f(mid)<1:a=mid
   else:b=mid
  s=(a+b)/2
  results.append(dict(replicas=T,banks_per_stage=B,padding_per_stage=pad,patterns=patterns,m=m,live=W,profile=dict(sorted(H.items())),rank_mass=sum(r*n for r,n in H.items()),deficit=312*T,child_count=sum(H.values()),coarse=str(s),relative_gain=str(s/D('0.001021539410806988')-1)))
(P/'price_ordered.json').write_text(json.dumps(dict(candidate_sha256=c['sha256'],results=results,scope='Exactexplicitintegerpacking anddiscoveryarithmetic; physicalowner/emitter/finiteinvoice notadmitted.'),indent=2));print([{k:x[k] for k in ['replicas','banks_per_stage','padding_per_stage','coarse','relative_gain']} for x in results])
