#!/usr/bin/env python3
"""Separate dense scalar oracle for the authored sequential sparse scheduler."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import importlib.util,sys,hashlib,json,random
HERE=Path(__file__).resolve().parent
SRC=HERE/'AUTHORED-SIMULATOR-REPAIRED.py'
spec=importlib.util.spec_from_file_location('reviewed_simulator',SRC)
s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)

def direct_axis(values,keys,axis,E,block):
    # Independent dense operator: every output sums over the entire original
    # tensor. No scheduler helpers, tensor-reference helpers or ordinal fields.
    answer={}
    for out in keys:
        z=Q(0)
        for inp in keys:
            if out[0]!=inp[0] or out[2]!=inp[2]:continue
            if any(out[1][j]!=inp[1][j] for j in range(len(out[1])) if j!=axis):continue
            a,b=out[1][axis],inp[1][axis]
            if a in E and b in E:c=block[E.index(a)][E.index(b)]
            else:c=Q(a==b)
            z+=c*values[inp]
        answer[out]=z
    return answer

rng=random.Random(2941713);count=0;checks=0;peak=0
for L,g,P,S in ((2,4,1,1),(3,3,1,1),(4,2,2,2),(5,2,1,2)):
    for fixture in range(5):
        E=[tuple(x for x in range(L) if rng.randrange(2)) for _ in range(g)]
        keys=[(('P',p),x,('S',z)) for p in range(P) for x in product(range(L),repeat=g) for z in range(S)]
        values={k:Q(rng.randrange(-8,9),rng.randrange(1,6)) for k in keys}
        m=s.Machine();full=m.from_records(s.Record(k,s.Vec((v.numerator,),v.denominator)) for k,v in values.items())
        union=s.gather(m,full,E)
        for sweep in range(3):
            m.event('review_sparse_sweep',index=sweep)
            for axis in range(g):
                block=[[Q(rng.randrange(-3,4),rng.randrange(1,5)) for j in E[axis]] for i in E[axis]]
                union=s.axis_stage(m,union,block,E[axis],axis,L,g,P,S,1)
                values=direct_axis(values,keys,axis,E[axis],block)
                union.rewind()
                while not union.eof():
                    r=union.read();assert len(r.value.a)==1 and Q(r.value.a[0],r.value.d)==values[r.key]
                    checks+=1
                union.rewind()
        full=s.scatter(m,full,union,E);full.rewind();observed=[]
        while not full.eof():
            r=full.read();observed.append(r.key)
            assert len(r.value.a)==1 and Q(r.value.a[0],r.value.d)==values[r.key]
        assert observed==keys and m.stats['gathers']==m.stats['scatters']==1
        peak=max(peak,m.stats['peak_live_lanes']);m.release(full);assert not m.live
        count+=1
result=dict(status='PASS_SEPARATE_DENSE_SCALAR_ORACLE',source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),cases=count,per_axis_union_record_comparisons=checks,peak_live_tapes=peak,scope='Twenty deterministic rational scalar cases; complete values checked after every axis in three sweeps. Separate oracle, shared candidate scheduler.')
(HERE/'DIRECT-SCALAR-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
