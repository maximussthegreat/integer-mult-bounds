#!/usr/bin/env python3
"""Independent closed-form recount of the authored tape's movement counters."""
from pathlib import Path
from math import prod
import importlib.util,sys,json,hashlib
HERE=Path(__file__).resolve().parent;SRC=HERE/'AUTHORED-SIMULATOR-REPAIRED.py'
spec=importlib.util.spec_from_file_location('cost_review_simulator',SRC)
s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
cases=[]
for L,g,E,P,S in [(2,1,[()],1,1),(3,1,[(2,)],1,1),(4,1,[(0,1,3)],2,3),(4,3,[(0,1,3),(0,2),(1,2,3)],1,1),(3,3,[(0,1,2),(0,1),(2,)],2,2),(2,4,[(0,1),(0,),(1,),(0,1)],1,3)]:
    r=s.run_case(L,g,E,P=P,S=S);c=r['stats'];N=P*S*L**g;u=P*S*(L**g-prod(L-len(e) for e in E))
    def movement(phase):return c.get(phase+'.head_steps_forward',0)+c.get(phase+'.head_steps_back',0)
    expected_outer=6*N+4*u
    expected_inner=0;expected_transpose=0;expected_arith=0;expected_coef=0
    for i,ei in enumerate(E):
        e=len(ei)
        if not e:continue
        ni=P*S*e*L**(g-1)
        expected_inner+=2*(6*u+4*ni)
        expected_arith+=2*2*(e+3)*ni;expected_coef+=2*e*ni
        suffix=L**(g-i-1)*S
        if e>1 and suffix>1:
            q=1<<(e-1).bit_length();k=q.bit_length()-1;nq=ni*q//e
            expected_transpose+=2*(8*(ni+nq)+16*k*nq)
    observed=dict(outer=movement('gather')+movement('scatter'),inner=movement('extract')+movement('merge'),transpose=movement('padding')+movement('transpose'),arithmetic=movement('arithmetic'),coefficient_reads=c.get('coefficient_reads',0))
    expected=dict(outer=expected_outer,inner=expected_inner,transpose=expected_transpose,arithmetic=expected_arith,coefficient_reads=expected_coef)
    assert observed==expected,(L,g,E,P,S,observed,expected)
    cases.append(dict(L=L,g=g,E=E,P=P,S=S,N=N,U=u,observed=observed,expected=expected))
out=dict(status='PASS_EXACT_MOVEMENT_FORMULAS',source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),cases=cases,scope='Origin-aligned record-tape counters; setup, reference-check IO and symbol/header arithmetic excluded, local arithmetic charged separately.')
(HERE/'COST-RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
