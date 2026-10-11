from collections import Counter
from pathlib import Path
from decimal import Decimal as D,localcontext
import json
P=Path(__file__).parent;c=json.load(open(P/'candidate111_receipt.json'));T=8;L=9;m=72
patterns=[dict(count=95,ranks={7:8,8:2}),dict(count=64,ranks={4:2,8:8}),dict(count=554,ranks={8:9})]
used=Counter()
for p in patterns:
 assert sum(r*n for r,n in p['ranks'].items())==72
 for r,n in p['ranks'].items():used[r]+=n*p['count']
assert used==Counter({int(r):T*n for r,n in c['residual_inventory'].items()});B=sum(p['count'] for p in patterns);W=960*T+L*B
H=Counter({int(r):T*L*n for r,n in c['local_histogram'].items()})
for r in [14,7,28,7,42,7,50,36,22,8]:H[r]+=240*T
mass=sum(r*n for r,n in H.items());assert m*W-mass==312*T;assert m*m>2*max(H)**2
with localcontext() as ctx:
 ctx.prec=70
 def f(a):return sum(D(r*n)/(m*W)*(D(m)/r)**a for r,n in H.items())+D(32*m*sum(H.values()))/(D(10)**16*W)*D(m)**a
 lo,hi=D(0),D('.01')
 for _ in range(220):
  a=(lo+hi)/2
  if f(a)<1:lo=a
  else:hi=a
 a=(lo+hi)/2
 out=dict(status='PASS_ZERO_PADDING_INTEGER_PACKING_AND_DISCOVERY_PRICE',candidate_sha256=c['word_sha256'],replicas=T,banks_per_stage=B,patterns=patterns,live=W,m=m,profile=dict(sorted(H.items())),rank_mass=mass,deficit=312*T,child_count=sum(H.values()),fallback_rank1=32*m*m*sum(H.values()),coarse_discovery=str(a),old_bit_coarse='0.001021539410806988',relative_bit_coarse_gain=str(a/D('0.001021539410806988')-1),scope='Exact integerpacking/mass, discoveryDecimalprice; nofullphysicalbankownerorfiniteinvoiceadmission and noassembledkappaclaim.')
(P/'price111.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
