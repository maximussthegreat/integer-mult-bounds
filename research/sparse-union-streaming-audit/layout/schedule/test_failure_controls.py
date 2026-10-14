#!/usr/bin/env python3
"""Intentionally malformed streams must be rejected by schedule invariants."""
from pathlib import Path
import json
from fractions import Fraction as Q
from sequential_union import Machine, Record, Vec, axis_stage, keys_for, block_apply

controls=[]
assert not Vec((1,)).equal(Vec((1,2)))
controls.append('truncated_symbolic_vector_rejected')
assert not Vec((1,2)).equal(Vec((1,)))
controls.append('extended_symbolic_vector_rejected')

keys=keys_for(2,2)
valid=[Record(k,Vec((0,))) for k in keys]
for name,records in [('missing_real_zero_record',valid[:-1]),
                     ('duplicate_real_zero_record',valid+[valid[-1]]),
                     ('reversed_real_zero_records',list(reversed(valid)))]:
    m=Machine(); union=m.from_records(records)
    try:
        axis_stage(m,union,[[Q(1),Q(0)],[Q(0),Q(1)]],(0,1),0,2,2,1,1,1)
    except AssertionError:controls.append(name+'_rejected')
    else:raise AssertionError(name+' was not rejected')

m=Machine(); tape=m.from_records([Record(None,'DIRTY:invalid',0,True)])
try:block_apply(m,tape,[[Q(1)]],(0,),0,1)
except AssertionError:controls.append('padding_in_arithmetic_rejected')
else:raise AssertionError('padding admitted to arithmetic')

result=dict(status='PASS',controls=controls,scope='Deliberately invalid streams and verifier widths; expected rejection, not positive schedule cases.')
Path(__file__).with_name('FAILURE-CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],len(controls))
