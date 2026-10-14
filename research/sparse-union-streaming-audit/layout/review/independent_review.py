#!/usr/bin/env python3
"""Adversarial checks of the independently authored schedule, never upstream code."""
from pathlib import Path
from itertools import product
from fractions import Fraction
import importlib.util, sys, json, hashlib, random, time

HERE=Path(__file__).resolve().parent
SOURCE=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'AUTHORED-SIMULATOR-REPAIRED.py'
if not SOURCE.is_absolute():SOURCE=HERE/SOURCE
spec=importlib.util.spec_from_file_location('authored_schedule_under_review',SOURCE)
s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)

def read(t):
    t.rewind();out=[]
    while not t.eof():out.append(t.read())
    t.rewind();return out

def transpose_checks():
    count=0;passes=0;max_lanes=0
    for P,e,R in product((1,2,3),range(1,10),range(1,12)):
        m=s.Machine()
        # Work cells contain arbitrary junk. Their original contents are not
        # required to be restored, and the test makes no such claim.
        for t in m.tapes:
            t.cells=[s.Record(None,f'PREEXISTING-DIRT:{t.lane}:{i}',padded=True) for i in range(17)]
            t.length=17;t.pos=17
        original=[s.Record((p,j,r),f'PAYLOAD:{p}:{j}:{r}',j) for p in range(P) for j in range(e) for r in range(R)]
        expected=[s.Record((p,j,r),f'PAYLOAD:{p}:{j}:{r}',j) for p in range(P) for r in range(R) for j in range(e)]
        t=m.from_records(original)
        t=s.move_field(m,t,P,e,R)
        assert read(t)==expected,('forward',P,e,R)
        t=s.move_field(m,t,P,e,R,inverse=True)
        assert read(t)==original,('inverse',P,e,R)
        m.release(t)
        assert not m.live
        assert m.stats['padding_records_created']==m.stats['padding_records_removed']
        for event in m.events:
            if event['event']=='bit_swap':
                assert event['head_steps']==8*event['records']
                passes+=1
        max_lanes=max(max_lanes,m.stats['peak_live_lanes']);count+=1
    return dict(cases=count,binary_passes=passes,maximum_live_tapes=max_lanes,work_dirt_invariant='Output independent of prior work cells; no restoration claim.')

def operator_checks():
    # Independent, deterministic dense rational operators, including a zero
    # matrix followed by a nonzero map and distinct arbitrary maps per sweep.
    original=s.matrix_for
    def custom(e,family,seed):
        if family=='zero':return [[Fraction(0) for j in range(e)] for i in range(e)]
        return [[Fraction(((i+2)*(j+3)+5*seed+int(family))%11-5,(i+j)%4+1) for j in range(e)] for i in range(e)]
    s.matrix_for=custom
    count=0;columns=0
    try:
        for L,g in ((2,4),(3,3),(5,2),(6,2)):
            rng=random.Random(714+L*100+g)
            for _ in range(8):
                E=[tuple(j for j in range(L) if rng.randrange(2)) for i in range(g)]
                r=s.run_case(L,g,E,families=('0','1','2'))
                assert r['exact_sweep_checkpoints']==3
                count+=1;columns+=r['basis_columns']
        r=s.run_case(3,3,[(0,1,2),(0,2),(1,2)],families=('zero','1'),P=2,S=2)
        count+=1;columns+=r['basis_columns']
    finally:s.matrix_for=original
    return dict(cases=count,basis_columns=columns,scope='Random source supports, exact all-basis comparisons, custom dense rational maps; seeded proposal selection only.')

def fail_controls():
    failures=[]
    def must_fail(name,fn):
        try:fn()
        except (AssertionError,IndexError,ValueError):failures.append(name);return
        raise AssertionError('undetected mutation: '+name)
    def run():return s.run_case(4,3,[(0,1,3),(1,2,3),(0,2)],P=2,S=2)
    original=s.extract
    def wrong_ordinal(*args,**kwargs):
        t=original(*args,**kwargs)
        # Controlled corruption of one produced header, not normal tape access.
        if t.length:t.cells[0]=s.replace(t.cells[0],ordinal=1)
        return t
    s.extract=wrong_ordinal
    try:must_fail('wrong_ordinal',run)
    finally:s.extract=original
    def missing_record(*args,**kwargs):
        t=original(*args,**kwargs)
        if t.length:t.length-=1
        return t
    s.extract=missing_record
    try:must_fail('missing_rectangle_record',run)
    finally:s.extract=original
    original_move=s.move_field
    s.move_field=lambda m,t,*args,**kwargs:t
    try:must_fail('omitted_transpose',run)
    finally:s.move_field=original_move
    original_block=s.block_apply
    def changed_key(*args,**kwargs):
        t=original_block(*args,**kwargs)
        if t.length:t.cells[0]=s.replace(t.cells[0],key=(('corrupt',0),t.cells[0].key[1],t.cells[0].key[2]))
        return t
    s.block_apply=changed_key
    try:must_fail('corrupted_merge_key',run)
    finally:s.block_apply=original_block
    # Scope-control finding is recorded even on the initial weak snapshot.
    width_control=not s.Vec((1,)).equal(s.Vec((1,2))) and not s.Vec((1,2)).equal(s.Vec((1,)))
    return dict(detected=failures,coefficient_width_guard=width_control,dense_interlude=s.dense_interlude()['negative_control'])

start=time.time()
result=dict(source=SOURCE.name,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),transpose=transpose_checks(),operators=operator_checks(),negative_controls=fail_controls(),elapsed_seconds=time.time()-start)
result['status']='PASS_SCOPED_REVIEW' if result['negative_controls']['coefficient_width_guard'] else 'PASS_SCHEDULE_WITH_VERIFIER_WIDTH_FINDING'
(HERE/'INDEPENDENT-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
