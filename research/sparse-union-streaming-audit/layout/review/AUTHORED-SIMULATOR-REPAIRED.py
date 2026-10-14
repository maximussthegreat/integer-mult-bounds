#!/usr/bin/env python3
"""Independent exact record-tape experiment. No upstream code imported or run.

Tape payload IO is sequential. Python storage, headers, descriptors, and exact
symbolic arithmetic are a host implementation, not a bit-Turing-machine proof.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction as Q
from itertools import product
from collections import Counter
from math import gcd, lcm, prod
from pathlib import Path
import json, argparse, time, hashlib

ROOT = Path(__file__).resolve().parent
PIN = '2569871ff906d2a2abfc86e97126ab9afe2e4a5a'

@dataclass(frozen=True)
class Vec:
    a: tuple[int, ...]
    d: int = 1
    def equal(self, other):
        return len(self.a) == len(other.a) and all(x*other.d == y*self.d for x,y in zip(self.a, other.a))
    @staticmethod
    def combination(terms, width):
        den = lcm(*(v.d*c.denominator for c,v in terms)) if terms else 1
        out = [0]*width
        for c,v in terms:
            k = c.numerator*(den//(c.denominator*v.d))
            for j,x in enumerate(v.a): out[j] += k*x
        common = gcd(den, gcd(*out))
        return Vec(tuple(x//common for x in out), den//common)

@dataclass(frozen=True)
class Record:
    # External prefix, logical active tensor tuple, external suffix.
    key: tuple | None
    value: Vec | str
    ordinal: int = -1
    padded: bool = False

class Tape:
    """Only this class directly indexes physical payload storage.

    Logical length is an explicit end marker. Reset does not clean physical
    storage; old dirty records remain beyond it and must never be read.
    """
    def __init__(self, machine, lane):
        self.m, self.lane = machine, lane
        self.cells=[]; self.pos=0; self.length=0
    def rewind(self):
        self.m.add('rewind_calls',1)
        self.m.add('head_steps_back',self.pos)
        self.pos=0
    def clear(self):
        self.rewind(); self.length=0
    def read(self):
        assert self.pos < self.length, ('past live end marker',self.lane,self.pos,self.length)
        x=self.cells[self.pos]; self.pos+=1
        self.m.add('record_reads',1); self.m.add('head_steps_forward',1)
        return x
    def write(self,x):
        assert self.pos == self.length, 'only append to the live stream'
        if self.pos == len(self.cells): self.cells.append(x)
        else: self.cells[self.pos]=x
        self.pos+=1; self.length+=1
        self.m.add('record_writes',1); self.m.add('head_steps_forward',1)
    def eof(self):
        self.m.add('end_marker_tests',1)
        return self.pos == self.length

class Machine:
    def __init__(self):
        self.stats=Counter(); self.events=[]; self.phase='setup'
        self.tapes=[Tape(self,i) for i in range(8)]
        self.free=set(range(8)); self.live=set()
    def add(self,k,n):
        self.stats[k]+=n; self.stats[self.phase+'.'+k]+=n
    def alloc(self):
        assert self.free, 'fixed eight-tape budget exceeded'
        i=min(self.free); self.free.remove(i); self.live.add(i)
        self.stats['peak_live_lanes']=max(self.stats['peak_live_lanes'],len(self.live))
        t=self.tapes[i]; t.clear(); return t
    def release(self,t):
        assert t.lane in self.live
        t.clear(); self.live.remove(t.lane); self.free.add(t.lane)
    def from_records(self,records):
        t=self.alloc()
        for r in records:t.write(r)
        t.rewind(); return t
    def output(self,t):
        self.phase='verification_output'; t.rewind(); out=[]
        while not t.eof():out.append(t.read())
        t.rewind(); return out
    def event(self,name,**kw): self.events.append(dict(event=name,**kw))


def selected(r, E):
    return any(r.key[1][i] in E[i] for i in range(len(E)))


def gather(m,full,E):
    m.phase='gather'; out=m.alloc(); full.rewind()
    while not full.eof():
        r=full.read(); m.add('membership_tests',len(E))
        if selected(r,E):out.write(r)
    full.rewind(); out.rewind(); m.add('gathers',1)
    m.event('gather',full=full.length,union=out.length)
    return out


def extract(m,union,E,axis):
    m.phase='extract'; out=m.alloc(); union.rewind()
    prefix=None; coordinate=None; ordinal=-1; completed=0
    for _ in range(union.length):
        r=union.read(); m.add('membership_tests',1)
        if r.key[1][axis] not in E:continue
        p=(r.key[0],r.key[1][:axis]); x=r.key[1][axis]
        if p != prefix:
            if prefix is not None:assert ordinal+1 == len(E)
            prefix=p; coordinate=None; ordinal=-1; completed+=1
            m.add('ordinal_prefix_resets',1)
        if x != coordinate:
            ordinal+=1; coordinate=x; m.add('ordinal_advances',1)
        assert ordinal < len(E) and E[ordinal] == x
        out.write(replace(r,ordinal=ordinal))
    if prefix is not None:assert ordinal+1 == len(E)
    union.rewind(); out.rewind()
    m.event('extract',axis=axis,records=out.length,prefix_fibers=completed)
    return out


def pad_field(m,src,outer,e,q,suffix,tag):
    m.phase='padding'; dst=m.alloc(); src.rewind()
    for p in range(outer):
        for j in range(q):
            for s in range(suffix):
                if j < e:
                    r=src.read(); assert not r.padded
                    dst.write(r)
                else:
                    # Deliberately nonzero, unusable padding: never a missing
                    # data coordinate and never an input to arithmetic.
                    dst.write(Record(None,f'DIRTY:{tag}:{p}:{j}:{s}',j,True))
                    m.add('padding_records_created',1)
    assert src.eof(); dst.rewind(); m.release(src)
    return dst


def remove_padding(m,src):
    m.phase='padding'; dst=m.alloc(); src.rewind()
    while not src.eof():
        r=src.read()
        if r.padded:
            assert isinstance(r.value,str) and r.value.startswith('DIRTY:')
            m.add('padding_records_removed',1)
        else:dst.write(r)
    dst.rewind(); m.release(src); return dst


def bit_swap(m,src,prefix,B,R,to_right):
    """[P][2][B][R] <-> [P][B][2][R], two work tapes, no seeks."""
    m.phase='transpose'; dst=m.alloc(); a=m.alloc(); b=m.alloc()
    src.rewind(); before=m.stats['head_steps_forward']+m.stats['head_steps_back']
    for _ in range(prefix):
        a.clear(); b.clear()
        if to_right:
            for _ in range(B*R):a.write(src.read())
            for _ in range(B*R):b.write(src.read())
        else:
            for _ in range(B):
                for _ in range(R):a.write(src.read())
                for _ in range(R):b.write(src.read())
        a.rewind(); b.rewind()
        if to_right:
            for _ in range(B):
                for _ in range(R):dst.write(a.read())
                for _ in range(R):dst.write(b.read())
        else:
            for _ in range(B*R):dst.write(a.read())
            for _ in range(B*R):dst.write(b.read())
        assert a.eof() and b.eof()
        a.clear(); b.clear()
    assert src.eof()
    # All head restoration is charged before the primitive returns.
    dst.rewind(); m.release(a); m.release(b); m.release(src)
    steps=m.stats['head_steps_forward']+m.stats['head_steps_back']-before
    n=prefix*2*B*R
    assert steps == 8*n, (steps,8*n)
    m.add('binary_passes',1); m.add('binary_pass_records',n)
    m.event('bit_swap',direction='right' if to_right else 'left',prefix=prefix,B=B,R=R,records=n,head_steps=steps)
    return dst


def move_field(m,src,outer,e,suffix,inverse=False):
    if e<=1 or suffix==1:return src
    q=1<<(e-1).bit_length(); k=q.bit_length()-1
    if inverse:
        src=pad_field(m,src,outer*suffix,e,q,1,'inverse')
        for r in reversed(range(k)):
            src=bit_swap(m,src,outer*(q//(2**(r+1))),suffix,2**r,False)
    else:
        src=pad_field(m,src,outer,e,q,suffix,'forward')
        for r in range(k):
            src=bit_swap(m,src,outer*(q//(2**(r+1))),suffix,2**r,True)
    return remove_padding(m,src)


def block_apply(m,src,block,E,axis,width):
    """Sequential local dot products; e^2 coefficient traffic is explicit."""
    m.phase='arithmetic'; dst=m.alloc(); line=m.alloc(); e=len(E)
    assert e and src.length%e == 0; src.rewind()
    for _ in range(src.length//e):
        line.clear(); first=None
        for j in range(e):
            r=src.read(); assert not r.padded and r.ordinal==j
            if first is None:first=r
            assert (r.key[0],r.key[1][:axis],r.key[1][axis+1:],r.key[2]) == (first.key[0],first.key[1][:axis],first.key[1][axis+1:],first.key[2])
            line.write(r)
        for j in range(e):
            line.rewind(); terms=[]
            for c in block[j]:
                r=line.read(); terms.append((c,r.value))
                m.add('coefficient_reads',1); m.add('symbolic_scalar_products',width)
            # This arithmetic oracle works on coefficient vectors; its bit
            # and register-space costs are NOT certified by movement counts.
            value=Vec.combination(terms,width)
            x=first.key[1][:axis]+(E[j],)+first.key[1][axis+1:]
            dst.write(Record((first.key[0],x,first.key[2]),value,j))
        line.clear()
    assert src.eof(); dst.rewind(); m.release(line); m.release(src)
    return dst


def ordered_replace(m,base,updates,predicate,phase):
    m.phase=phase; dst=m.alloc(); base.rewind(); updates.rewind(); last=None
    for _ in range(base.length):
        old=base.read(); assert last is None or last < old.key; last=old.key
        m.add('membership_tests',1)
        if predicate(old):
            new=updates.read(); m.add('header_equality_tests',1)
            assert new.key==old.key and not new.padded
            dst.write(replace(new,ordinal=-1))
        else:dst.write(old)
    assert base.eof() and updates.eof()
    dst.rewind(); m.release(base); m.release(updates)
    return dst


def axis_stage(m,union,block,E,axis,L,g,prefix_count,suffix_count,width):
    if not E:
        m.event('empty_axis',axis=axis); return union
    extracted=extract(m,union,E,axis)
    expected=prefix_count*suffix_count*len(E)*L**(g-1)
    assert extracted.length==expected, ('incomplete rectangle',axis,extracted.length,expected)
    outer=prefix_count*L**axis; suffix=L**(g-axis-1)*suffix_count
    exposed=move_field(m,extracted,outer,len(E),suffix)
    applied=block_apply(m,exposed,block,E,axis,width)
    restored=move_field(m,applied,outer,len(E),suffix,True)
    return ordered_replace(m,union,restored,lambda r:r.key[1][axis] in E,'merge')


def scatter(m,full,union,E):
    out=ordered_replace(m,full,union,lambda r:selected(r,E),'scatter')
    m.add('scatters',1); m.event('scatter',full=out.length)
    return out


def matrix_for(e,family,seed=0):
    if family=='singular':
        if e == 1:return [[Q(0)]]
        # Rank <= 1, includes signed nonintegral coefficients and zero rows.
        return [[Q((i%3-1)*(j+seed+1),3) for j in range(e)] for i in range(e)]
    if family=='invertible':
        # Strict diagonal dominance guarantees invertibility.
        return [[Q((3*e+2) if i==j else ((i+j+seed)%3-1),2) for j in range(e)] for i in range(e)]
    if family=='zero':return [[Q(0) for _ in range(e)] for _ in range(e)]
    raise ValueError(family)


def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def embed(block,E,L):
    out=eye(L)
    for i,a in enumerate(E):
        for j,b in enumerate(E):out[a][b]=block[i][j]
    return out

def mm(a,b):return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]


def reference_tensor_rows(mats,keys):
    """Independent direct tensor entries; no extract/transpose/merge code."""
    out=[]
    for p,x,s in keys:
        row=[]
        for pp,y,ss in keys:
            c=prod((mats[i][x[i]][y[i]] for i in range(len(x))),start=Q(1)) if p==pp and s==ss else Q(0)
            row.append(c)
        d=lcm(*(v.denominator for v in row))
        out.append(Vec(tuple(v.numerator*(d//v.denominator) for v in row),d))
    return out


def keys_for(L,g,P=1,S=1):
    return [(('prefix',p),x,('suffix',s)) for p in range(P) for x in product(range(L),repeat=g) for s in range(S)]


def run_case(L,g,E,families=('invertible','singular'),P=1,S=1,trace=False):
    keys=keys_for(L,g,P,S); width=len(keys); m=Machine()
    full=m.from_records(Record(k,Vec(tuple(int(j==i) for j in range(width)))) for i,k in enumerate(keys))
    union=gather(m,full,E); u=union.length
    ref=[eye(L) for _ in range(g)]
    expected_U=P*S*(L**g-prod(L-len(e) for e in E))
    assert u==expected_U
    checkpoints=0
    for sweep,family in enumerate(families):
        m.event('sparse_sweep',index=sweep,family=family)
        for axis in range(g):
            block=matrix_for(len(E[axis]),family,axis+sweep)
            union=axis_stage(m,union,block,E[axis],axis,L,g,P,S,width)
            ref[axis]=mm(embed(block,E[axis],L),ref[axis])
        # Exact checkpoint prevents a later singular sweep from masking an
        # error in the preceding invertible sweep. Verification IO is separate.
        expected_rows=reference_tensor_rows(ref,keys)
        expected_map=dict(zip(keys,expected_rows))
        for r in m.output(union):
            assert r.value.equal(expected_map[r.key]), ('sweep mismatch',L,g,E,sweep,r.key)
        checkpoints+=1
    full=scatter(m,full,union,E)
    actual=m.output(full); reference=reference_tensor_rows(ref,keys)
    assert len(actual)==len(keys)==len(reference)
    for r,k,v in zip(actual,keys,reference):
        assert r.key==k and r.value.equal(v), ('basis mismatch',L,g,E,families,k)
    m.release(full)
    assert m.stats['gathers']==m.stats['scatters']==1
    assert m.stats['padding_records_created']==m.stats['padding_records_removed']
    result=dict(L=L,g=g,E=[list(x) for x in E],P=P,S=S,basis_columns=width,exact_sweep_checkpoints=checkpoints,sweeps=list(families),union_records=u,stats=dict(m.stats))
    if trace:result['trace']=m.events
    return result


def supports(L):return [tuple(i for i in range(L) if mask>>i&1) for mask in range(1<<L)]


def dense_interlude():
    # Nonempty boundary J={0}, interior I={1,2}, closed sparse E={0,1}.
    # The dense interior block fixes J but moves near-interior 1 to deep 2.
    L=3; E=[(0,1)]; keys=keys_for(L,1); width=3; m=Machine()
    full=m.from_records(Record(k,Vec(tuple(int(i==j) for j in range(width)))) for i,k in enumerate(keys))
    ref=eye(L)
    union=gather(m,full,E)
    for block in ([[Q(2),Q(1,3)],[Q(0),Q(1)]],[[Q(1),Q(0)],[Q(1,2),Q(1)]]):
        union=axis_stage(m,union,block,E[0],0,L,1,1,1,width)
        ref=mm(embed(block,E[0],L),ref)
    full=scatter(m,full,union,E)
    A=[[Q(1),Q(0),Q(0)],[Q(0),Q(1),Q(1)],[Q(0),Q(1),Q(2)]]
    # Full dense stage is explicitly outside the retained sparse window.
    m.event('dense_interlude',matrix=[[str(x) for x in row] for row in A])
    full=axis_stage(m,full,A,(0,1,2),0,L,1,1,1,width)
    ref=mm(A,ref)
    union=gather(m,full,E)
    block=[[Q(3,2),Q(0)],[Q(1,3),Q(2)]]
    union=axis_stage(m,union,block,E[0],0,L,1,1,1,width)
    ref=mm(embed(block,E[0],L),ref)
    full=scatter(m,full,union,E)
    actual=m.output(full)
    assert len(actual)==len(ref)==L
    assert all(all(Q(a,actual[i].value.d)==b for a,b in zip(actual[i].value.a,row)) for i,row in enumerate(ref))
    assert m.stats['gathers']==2 and m.stats['scatters']==2
    # Execute the intentionally wrong retained-union schedule, rather than
    # merely putting expected failure values into metadata.
    probe=[Q(0),Q(1),Q(0)]
    correct=[sum(a*b for a,b in zip(row,probe)) for row in A]
    bad=Machine()
    badfull=bad.from_records(Record(k,Vec((int(i==1),))) for i,k in enumerate(keys))
    badunion=gather(bad,badfull,E)
    badunion=axis_stage(bad,badunion,[[A[i][j] for j in E[0]] for i in E[0]],E[0],0,L,1,1,1,1)
    badfull=scatter(bad,badfull,badunion,E)
    invalid=[Q(r.value.a[0],r.value.d) for r in bad.output(badfull)]
    bad.release(badfull)
    assert correct != invalid and correct[2] != 0
    m.release(full)
    return dict(status='PASS',L=L,g=1,J=[0],I=[1,2],E=[[0,1]],stats=dict(m.stats),trace=m.events,negative_control=dict(input_basis=[0,1,0],dense_A=[[int(x) for x in row] for row in A],correct_full_output=[str(x) for x in correct],invalid_retained_union_output=[str(x) for x in invalid],first_escaping_coordinate=2,detected=True,wrong_schedule_executed=True))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--quick',action='store_true');args=ap.parse_args()
    assert not Vec((1,)).equal(Vec((1,2)))
    assert not Vec((1,2)).equal(Vec((1,)))
    started=time.time(); totals=Counter(); groups=[]; case_count=0; basis_count=0
    for L in (2,3,4):
        for g in (1,2,3):
            local=Counter(); count=0; bases=0
            for E in product(supports(L),repeat=g):
                if args.quick and count>=10:break
                receipt=run_case(L,g,E)
                count+=1; case_count+=1;bases+=receipt['basis_columns'];basis_count+=receipt['basis_columns']
                for k,v in receipt['stats'].items():
                    if k=='peak_live_lanes':local[k]=max(local[k],v);totals[k]=max(totals[k],v)
                    else:local[k]+=v;totals[k]+=v
            groups.append(dict(L=L,g=g,support_tuples=count,basis_columns=bases,stats=dict(local)))
            print(json.dumps(dict(progress=[L,g],cases=count,elapsed_seconds=round(time.time()-started,2))),flush=True)
    spectators=[]
    for P,S in ((1,3),(3,1),(2,3),(3,2)):
        spectators.append(run_case(4,3,[(0,2,3),(1,),(0,3)],P=P,S=S,trace=True))
    zero=run_case(3,3,[(0,2),(1,),(0,1,2)],families=('zero',),P=2,S=3,trace=True)
    non_dyadic=run_case(4,3,[(0,1,3),(0,2),(1,2,3)],trace=True)
    interlude=dense_interlude()
    result=dict(status='PASS_EXACT_FINITE_RECORD_TAPE_REPLAY',source_pin=PIN,scope='Finite exact symbolic-basis replay plus measured sequential record-tape IO. No upstream code executed; not a bit-machine, asymptotic, Gaussian, or multiplication-exponent certificate.',complete_exhaustive=not args.quick,support_tuples=case_count,basis_columns=basis_count,sparse_sweeps_per_case=2,all_subset_grid=[2,3,4],dimensions=[1,2,3],families=['strictly_diagonally_dominant_rational_invertible','signed_rank_at_most_one_rational_singular'],totals=dict(totals),groups=groups,spectator_cases=spectators,zero_matrix_case=zero,non_dyadic_trace=non_dyadic,dense_interlude=interlude,elapsed_seconds=round(time.time()-started,3))
    path=ROOT/('QUICK-RESULTS.json' if args.quick else 'RESULTS.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','support_tuples','basis_columns','elapsed_seconds')},indent=2))

if __name__=='__main__':main()
