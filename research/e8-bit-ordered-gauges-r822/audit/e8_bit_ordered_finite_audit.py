# Independent finiteinvoice and wholeB4 formalcolumn audit; upstream files remain inert.
import json,hashlib,gzip
from pathlib import Path
import os
ROOT=Path(os.environ.get('E8_AUDIT_ROOT',Path(__file__).resolve().parent))
ROOT.mkdir(parents=True,exist_ok=True)
DATA=Path(os.environ.get('E8_DATA_ROOT',ROOT/'e8_bit_gauge_search_20261011'))
from fractions import Fraction as Q
from collections import Counter,deque
from math import gcd
P=DATA;w=json.load(open(P/'candidate_ordered.json'));pk=json.load(open(str(ROOT / 'e8_bit_ordered_packing_audit_results.json')));n=1062;v=120;R=822;T=8;S=9;KP=4;m=72;W=13953;nc=9
# Literal expanded scalarstream, immutable freshcentres and exact signedinverse ordering.
events=[]
for ph in ['D','A']:events += [('add',t,s) for f,t,ss in w[ph] for s in ss]
for k,r in enumerate(w['ret']):
 events.append(('copy',n,r));events += [('add',120+j,n) for j,ks in enumerate(w['scatter']) if k in ks];events.append(('erase',n,r))
for ph in ['B','C']:events += [('add',t,s) for f,t,ss in w[ph] for s in ss]
assert sum(k=='copy' for k,t,s in events)==nc
norms=[]
for reverse in [False,True]:
 row=[1]*(n+1);largest=1;opened=None
 for kind,t,s in (events[::-1] if reverse else events):
  if reverse and kind!='add':kind='erase' if kind=='copy' else 'copy'
  if kind=='copy':assert opened is None;opened=s;row[t]=row[s]
  elif kind=='erase':assert opened==s;opened=None;row[t]=0
  else:
   assert t!=n and (s!=n or opened is not None) and (opened is None or t!=opened)
   row[t]+=row[s];largest=max(largest,row[t])
 assert opened is None;norms.append(largest)
adds=sum(kind=='add' for kind,t,s in events);assert adds==14976 and norms==[783,9654]
payload=64*norms[0]**3*norms[1]**2;assert payload<2**104
# Entire nine-stage bridgedword on1782independent uncompressedlogical-rolecolumns.
globaln=2*KP*v+R;z=[1<<i for i in range(globaln)]+[0];after=[[] for _ in range(S)]
X=lambda p:2*p;Y=lambda p:2*p+1
for p in range(1,KP):
 after[2*p-1]+=[(X(p-1),X(p)),(Y(p),Y(p-1))]
 after[2*p]+=[(Y(p),Y(p-1)),(X(p-1),X(p))]
for p in range(KP-1,0,-1):after[-1]+=[(Y(p-1),Y(p)),(X(p),X(p-1))]
assert sum(map(len,after))==18
for stage in range(S):
 p=0 if stage<3 else (stage-1)//2;rev=stage%2==1;active=(Y(p),X(p)) if rev else (X(p),Y(p))
 def mapped(r):return active[0]*v+r if r<v else active[1]*v+r-v if r<2*v else 2*KP*v+r-2*v if r<n else globaln
 opened=None
 for kind,t,s in (events[::-1] if rev else events):
  if rev and kind!='add':kind='erase' if kind=='copy' else 'copy'
  t,s=mapped(t),mapped(s)
  if kind=='copy':assert opened is None;opened=s;z[t]=z[s]
  elif kind=='erase':assert opened==s;opened=None;z[t]=0
  else:assert opened is None or t!=opened;z[t]^=z[s]
 assert opened is None and z[-1]==0
 for a,b in after[stage]:
  for i in range(v):z[a*v+i]^=z[b*v+i]
for p in range(KP):
 for i in range(v):z[X(p)*v+i],z[Y(p)*v+i]=z[Y(p)*v+i],z[X(p)*v+i]
assert z==[1<<i for i in range(globaln)]+[0]
for omitted in range(18):
 r=[1<<i for i in range(8)];counter=0
 for stage in range(S):
  p=0 if stage<3 else (stage-1)//2;a,b=(Y(p),X(p)) if stage%2 else (X(p),Y(p));r[b]^=r[a]
  for a,b in after[stage]:
   if counter!=omitted:r[a]^=r[b]
   counter+=1
 for p in range(KP):r[X(p)],r[Y(p)]=r[Y(p)],r[X(p)]
 assert r!=[1<<i for i in range(8)]
# Coordinate entrancecompletion acrossninewindows, includingmissing-window control.
ext={r:[i for i in range(8) if any(row[i] for row in [w['lines'][j] for j in w['frames'][f]])] for r,f in enumerate(w['start']) if r>=240 and f}
assert len(ext)==175
for r,E in ext.items():
 residuals=[{8*stage+i for i in range(8) if i not in E} for stage in range(9)];completion={8*stage+i for stage in range(9) for i in E}
 assert not any(residuals[i]&residuals[j] for i in range(9) for j in range(i))
 assert set().union(*residuals)==set(range(72))-completion
 assert set().union(*residuals[:-1],residuals[-2])!=set(range(72))-completion
# Finite source formula reconstructed with concrete chart count instead of identitycharts.
H={int(r):n for r,n in pk['profile'].items()};E=sum(H.values());mass=sum(r*n for r,n in H.items());maxops=pk['max_owner_address_transpositions'];assert maxops==128
factors=maxops+(m-1)+m;selectors=2*S*T*((W-1)+R*m*factors)
J=T*(2*S*(2*v+R)+2*KP*v);d=m*m;N=2*m;good=8*m*m+8;high=16*(d+1)**2
units=T*(S*adds+6*(KP-1)*v)
coefficient=units+J*high+J*(W+nc)+E*good+E*128*N**3+16*m**3+S*nc*T+E+selectors+1
fallback=6*N*(N-1)+3*N+6*(N-1)
assert coefficient<2**80 and 2*m**3*10**16<2**80 and selectors<2**40 and fallback<32*m*m
assert m**2>2*max(H)**2 and m*W-mass==2496
row_reserve=2*(m*m+1);assert row_reserve<20161
# Uniform moment engine onlydepends onactualprofile,m,W andexistingfallbackbound.
# Reuse solely independent intervalimplementation, neverupstreamengine.
from e8_bit_ordered_packing_audit import moment
c=Q(1036212382904051,10**18);ml,mh=moment(c);delta_tau=1-mh;delta_linear=1-Q(mass,m*W)-Q(32*m*E,10**16*W);assert delta_tau>0 and delta_linear>0
chain=[Q(384599,10**10)];cutoffs=[]
ceil=lambda x:-((-x.numerator)//x.denominator)
for _ in range(3):
 old=chain[-1];a=(1-c)*c+c*old;delta=min(c-a,1-a-c,1-a-c*(1-old),1-c);assert old<a<c<1-a and delta>0
 cutoff=max(1,ceil(36/delta**2),ceil(2*(4+(coefficient-1).bit_length())/delta));assert cutoff*delta**2>=36 and cutoff*delta>=2*(4+(coefficient-1).bit_length());cutoffs.append(dict(minimum_gap=str(delta),cutoff_log2=str(cutoff)));chain.append(a)
out=dict(status='PASS_CHANGED_FINITE_COUNTS_BRIDGE_AND_MOMENT_UNDER_IDENTIFIED_GENERIC_CONTRACT',candidate_sha256=hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest(),Kpairs=4,replicas=8,local_scalar_additions=adds,prefix_entry_xors=408,prefix_inverse_xors=408,forward_inverse_row_l1=norms,payload_prefix_upper=str(payload),payload_prefix_bits=payload.bit_length(),global_abstract_role_columns=globaln,all_nine_stage_columns_restored=True,omitted_bridge_controls=18,coordinate_entrance_windows=9,entrance_completion_checks=175,unit_expanded_global_additions=units,route_families=J,copy_erase_episodes=S*nc*T,private_centres_bound=nc,live=W,live_plus_centres=W+nc,owner_adapter_calls=2*S*T*R,owner_address_transpositions_total=2*S*pk['total_oneway_owner_address_transpositions'],max_owner_chart_elementary_factors=maxops,selector_overcharge=selectors,finite_coefficient=str(coefficient),finite_coefficient_bits=coefficient.bit_length(),coefficient_ceiling='2^80',q_power_upper='q^5185',fallback_actual=fallback,fallback_ceiling=32*m*m,halving_degree=2,row_reserve=row_reserve,external_row_coefficient=20161,row_slack=20161-row_reserve,coarse_certified_grid=str(c),delta_tau_lower_decimal=str(float(delta_tau)),delta_linear=str(delta_linear),bootstrap_chain=list(map(str,chain)),bootstrap_cutoffs=cutoffs,remaining_standing_assumptions=['Generic scalar-payload/address-window lifting theorem and correlated bank semantics','Generic ADD/MOVE/COPY/ERASE recursive compiler and unit-cost row interfaces used by finite_k','Existing good/bad-prime engines, common-grid precision and all-size analytic bootstrap'],finite_caveat='Full physical source-emitter machinecode and exhaustive globaladdresspayloadcombined replay are not supplied; this is independent symbolic finitecontract closure, not unconditionalmultiplicationtheorem.')
json.dump(out,open(str(ROOT / 'e8_bit_ordered_finite_audit_results.json'),'w'),indent=2);print(json.dumps(out,indent=2))
