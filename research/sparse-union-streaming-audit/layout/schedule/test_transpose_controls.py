#!/usr/bin/env python3
"""Reproducible opaque-record permutation checks, independent of arithmetic."""
from itertools import product
from pathlib import Path
import json
from sequential_union import Machine, Record, move_field

rows=[]
for P,e,S in product((1,2,3),(1,2,3,4,5,7),(1,2,3,5)):
    m=Machine()
    originals=[Record((p,j,s),f'DIRTY_REAL:{p}:{j}:{s}',j)
               for p in range(P) for j in range(e) for s in range(S)]
    tape=m.from_records(originals)
    tape=move_field(m,tape,P,e,S)
    expected=[Record((p,j,s),f'DIRTY_REAL:{p}:{j}:{s}',j)
              for p in range(P) for s in range(S) for j in range(e)]
    assert m.output(tape)==expected,(P,e,S)
    tape=move_field(m,tape,P,e,S,True)
    assert m.output(tape)==originals
    m.release(tape)
    assert m.stats['padding_records_created']==m.stats['padding_records_removed']
    rows.append(dict(P=P,e=e,S=S,records=len(originals),stats=dict(m.stats)))
result=dict(status='PASS',cases=len(rows),scope='Pure selected-field permutation, nonzero opaque dirty records, exact round trip, no arithmetic.',cases_detail=rows)
Path(__file__).with_name('TRANSPOSE-CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],result['cases'])
