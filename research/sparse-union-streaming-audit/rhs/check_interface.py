#!/usr/bin/env python3
"""Independent finite checks. No upstream program is imported or executed.

Tape checks implement literal record-head moves. Algebra checks use host
arrays and exact fractions: their page count is real, but they are not a
physical tape implementation of Strassen or a bounded-precision Gaussian test.
"""
from fractions import Fraction as F
from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent


class Tape:
    def __init__(self, stats, values=()):
        self.stats = stats
        self.cells = list(values)
        self.length = len(self.cells)
        self.pos = 0

    def read(self):
        assert self.pos < self.length
        x = self.cells[self.pos]
        self.pos += 1
        self.stats['reads'] += 1
        self.stats['forward'] += 1
        return x

    def write(self, x):
        assert self.pos == self.length
        if self.length < len(self.cells):
            self.cells[self.length] = x
        else:
            self.cells.append(x)
        self.pos += 1
        self.length += 1
        self.stats['writes'] += 1
        self.stats['forward'] += 1

    def rewind(self):
        self.stats['backward'] += self.pos
        self.pos = 0

    def clear(self):
        self.rewind()
        self.length = 0

    def snapshot(self):
        # Test oracle only, not used by the tape algorithm.
        return self.cells[:self.length]


def swap_bit(src, dst, a, c, P, B, T, inverse=False):
    """[P][2][B][T] <-> [P][B][2][T]; all heads start/end at origin."""
    assert src.pos == dst.pos == a.pos == c.pos == 0
    n = 2 * P * B * T
    assert src.length == n
    dst.clear()
    start = src.stats['forward'] + src.stats['backward']
    for _ in range(P):
        a.clear()
        c.clear()
        if not inverse:
            for _ in range(B*T):
                a.write(src.read())
            for _ in range(B*T):
                c.write(src.read())
        else:
            for _ in range(B):
                for _ in range(T):
                    a.write(src.read())
                for _ in range(T):
                    c.write(src.read())
        a.rewind()
        c.rewind()
        if not inverse:
            for _ in range(B):
                for _ in range(T):
                    dst.write(a.read())
                for _ in range(T):
                    dst.write(c.read())
        else:
            for _ in range(B*T):
                dst.write(a.read())
            for _ in range(B*T):
                dst.write(c.read())
        a.clear()
        c.clear()
    src.rewind()
    dst.rewind()
    moved = src.stats['forward'] + src.stats['backward'] - start
    assert moved == 8*n, (moved, n)
    src.stats['binary_passes'] += 1
    return dst, src


def layout_case(e, R, q):
    assert q and q & (q-1) == 0
    batches = (R+q-1)//q
    Rp = batches*q
    # Explicit logical input and dummy RHS. Setup is not in the binary-pass ledger.
    values = [(row, rhs, 17*row-3*rhs) for rhs in range(Rp) for row in range(e)]
    stats = Counter()
    src, dst, a, c = [Tape(stats, values), Tape(stats), Tape(stats), Tape(stats)]
    m = q.bit_length()-1
    for t in range(m):
        src, dst = swap_bit(src, dst, a, c, batches*(q//(2**(t+1))), e, 2**t)
    expected = [(row, batch*q+rhs, 17*row-3*(batch*q+rhs))
                for batch in range(batches) for row in range(e) for rhs in range(q)]
    assert src.snapshot() == expected
    for t in reversed(range(m)):
        src, dst = swap_bit(src, dst, a, c, batches*(q//(2**(t+1))), e, 2**t, True)
    assert src.snapshot() == values
    assert stats['forward']+stats['backward'] == 16*e*Rp*m
    if R >= q:
        assert Rp < 2*R or R == Rp
    return {'e': e, 'R': R, 'q': q, 'R_padded': Rp,
            'movement': stats['forward']+stats['backward'],
            'passes': stats['binary_passes']}


def zero(n, m):
    return [[F(0) for _ in range(m)] for _ in range(n)]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def add(A, B, sign=1):
    return [[a+sign*b for a,b in zip(ar,br)] for ar,br in zip(A,B)]


def dense_mm(A, B):
    if not A:
        return []
    return [[sum((a*b for a,b in zip(row,col)), F(0))
             for col in zip(*B)] for row in A]


def sub(A, rows, cols):
    return [[A[i][j] for j in cols] for i in rows]


def inv(A):
    n = len(A)
    X = [list(row)+list(erow) for row,erow in zip(A,identity(n))]
    for k in range(n):
        # Dense reference/setup may pivot. Online block solve never scalar-pivots.
        r = next(r for r in range(k,n) if X[r][k])
        X[k], X[r] = X[r], X[k]
        p = X[k][k]
        X[k] = [x/p for x in X[k]]
        for i in range(n):
            if i != k:
                t = X[i][k]
                X[i] = [a-t*b for a,b in zip(X[i],X[k])]
    return [row[n:] for row in X]


def norm(A):
    return max((sum(map(abs,row),F(0)) for row in A), default=F(0))


def nonzero(A):
    return any(x for row in A for x in row)


def strassen(A, B, stats):
    n = len(A)
    assert n == len(B) and all(len(r)==n for r in A+B)
    stats['recursive_nodes'] += 1
    if n == 1:
        stats['scalar_products'] += 1
        return [[A[0][0]*B[0][0]]]
    h = n//2
    ix, jx = list(range(h)), list(range(h,n))
    a,b,c,d = sub(A,ix,ix),sub(A,ix,jx),sub(A,jx,ix),sub(A,jx,jx)
    e,f,g,hb = sub(B,ix,ix),sub(B,ix,jx),sub(B,jx,ix),sub(B,jx,jx)
    p1 = strassen(add(a,d),add(e,hb),stats)
    p2 = strassen(add(c,d),e,stats)
    p3 = strassen(a,add(f,hb,-1),stats)
    p4 = strassen(d,add(g,e,-1),stats)
    p5 = strassen(add(a,b),hb,stats)
    p6 = strassen(add(c,a,-1),add(e,f),stats)
    p7 = strassen(add(b,d,-1),add(g,hb),stats)
    c11 = add(add(add(p1,p4),p5,-1),p7)
    c12 = add(p3,p5)
    c21 = add(p2,p4)
    c22 = add(add(add(p1,p2,-1),p3),p6)
    return [x+y for x,y in zip(c11,c12)] + [x+y for x,y in zip(c21,c22)]


def page_product(A, B, q, stats):
    """One loaded factor page, reused by local recursion; zero-pad only here."""
    rows, inner, cols = len(A), len(B), len(B[0])
    assert all(len(r)==inner for r in A) and max(rows,inner,cols)<=q
    aa,bb = zero(q,q),zero(q,q)
    for i,row in enumerate(A):
        aa[i][:len(row)] = row
    for i,row in enumerate(B):
        bb[i][:len(row)] = row
    stats['page_products'] += 1
    stats['coefficient_records_loaded'] += q*q
    before = stats['scalar_products']
    cc = strassen(aa,bb,stats)
    assert stats['scalar_products']-before == 7**(q.bit_length()-1)
    out = [r[:cols] for r in cc[:rows]]
    assert out == dense_mm(A,B)
    return out


def carve(n, W, cap):
    assert cap & (cap-1) == 0 and cap>W and n>6*W
    interiors=[]
    p=W
    remainder=n-2*W
    while remainder>4*W:
        b=min(cap,1<<((remainder-W).bit_length()-1))
        assert b>W
        interiors.append(list(range(p,p+b)))
        p += b+W
        remainder -= b+W
    I=[x for z in interiors for x in z]
    J=[x for x in range(n) if x not in set(I)]
    groups=[]
    for x in J:
        if not groups or x != groups[-1][-1]+1:
            groups.append([])
        groups[-1].append(x)
    assert all(W<=len(z)<=6*W for z in groups)
    return interiors,I,J,groups


def make_h(n,W,cyclic):
    H=zero(n,n)
    for i in range(n):
        for j in range(n):
            dist=min(abs(i-j),n-abs(i-j)) if cyclic else abs(i-j)
            if i!=j and dist<=W:
                H[i][j]=F(((13*i+7*j)%5)-2,8)
        H[i][i]=1+sum(map(abs,H[i]),F(0))
    return H


def block_factor(S, sizes):
    groups=[]
    k=0
    for size in sizes:
        groups.append(list(range(k,k+size)))
        k+=size
    m=len(groups)
    work=[[sub(S,a,b) for b in groups] for a in groups]
    L=[[zero(len(a),len(b)) for b in groups] for a in groups]
    U=[[zero(len(a),len(b)) for b in groups] for a in groups]
    Din=[]
    for k in range(m):
        L[k][k]=identity(sizes[k])
        Din.append(inv(work[k][k]))
        for j in range(k,m):
            U[k][j]=work[k][j]
        for i in range(k+1,m):
            L[i][k]=dense_mm(work[i][k],Din[k])
            for j in range(k+1,m):
                work[i][j]=add(work[i][j],dense_mm(L[i][k],U[k][j]),-1)
    denseL=zero(len(S),len(S)); denseU=zero(len(S),len(S))
    for i,a in enumerate(groups):
        for j,b in enumerate(groups):
            for x,ix in enumerate(a):
                for y,jx in enumerate(b):
                    denseL[ix][jx]=L[i][j][x][y]
                    denseU[ix][jx]=U[i][j][x][y]
    assert dense_mm(denseL,denseU)==S
    return groups,L,U,Din,denseL,denseU


def solve_batch(X, groups, L, U, Din, q, stats):
    m=len(groups)
    cols=list(range(len(X[0])))
    Y=[]
    for i in range(m):
        yi=sub(X,groups[i],cols)
        for k in range(i):
            if nonzero(L[i][k]):
                yi=add(yi,page_product(L[i][k],Y[k],q,stats),-1)
        Y.append(yi)
    Z=[None]*m
    for i in reversed(range(m)):
        zi=Y[i]
        for k in range(i+1,m):
            if nonzero(U[i][k]):
                zi=add(zi,page_product(U[i][k],Z[k],q,stats),-1)
        Z[i]=page_product(Din[i],zi,q,stats)
    return [row for block in Z for row in block]


def band_product(K,X,q,stats):
    n=len(K)
    panels=[list(range(k,min(k+q,n))) for k in range(0,n,q)]
    cols=list(range(len(X[0])))
    out=zero(n,len(cols))
    for rr in panels:
        yy=zero(len(rr),len(cols))
        for ss in panels:
            a=sub(K,rr,ss)
            if nonzero(a):
                yy=add(yy,page_product(a,sub(X,ss,cols),q,stats))
        for i,row in zip(rr,yy):
            out[i]=row
    return out


def algebra_case(n,W,cap,R,cyclic):
    interiors,I,J,physical_groups=carve(n,W,cap)
    H=make_h(n,W,cyclic)
    A,B,C,D=sub(H,I,I),sub(H,I,J),sub(H,J,I),sub(H,J,J)
    S=add(D,dense_mm(dense_mm(C,inv(A)),B),-1)
    E=sorted(set(J)|{i for i in I if any(H[i][j] or H[j][i] for j in J)})
    groups,L,U,Din,denseL,denseU=block_factor(S,list(map(len,physical_groups)))
    m=len(groups)
    q=1<<(max(W,max(map(len,physical_groups)))-1).bit_length()
    assert len(E)>q, 'ensure test distinguishes E from a single factor page'
    for i in range(m):
        for k in range(m):
            if i>k and nonzero(L[i][k]):
                assert i==k+1 or (cyclic and i==m-1)
            if i<k and nonzero(U[i][k]):
                assert k==i+1 or (cyclic and k==m-1)
    # The finite eliminated-set component argument, including wrap frontier.
    geometry_checks=0
    for upto in range(m+1):
        eliminated=set(I)|{x for g in physical_groups[:upto] for x in g}
        if upto==m:
            blocks=[sorted(eliminated)]
        else:
            prefix=list(range(physical_groups[upto][0]))
            blocks=[prefix]+[z for z in interiors if z[0]>physical_groups[upto][-1]]
            assert set(x for z in blocks for x in z)==eliminated
        for a,ba in enumerate(blocks):
            for bb in blocks[a+1:]:
                assert not any(H[i][j] or H[j][i] for i in ba for j in bb)
        geometry_checks+=1
    # Global physical E-order input, arbitrary signed identity spectator entries.
    X=[[F((7*row+11*rhs)%23-11,3) for rhs in range(R)] for row in E]
    ej=[E.index(j) for j in J]
    xj=sub(X,ej,list(range(R)))
    expect=dense_mm(inv(S),xj)
    stats=Counter()
    observed=zero(len(J),R)
    page_counts=[]
    for start in range(0,R,q):
        ids=list(range(start,min(start+q,R)))
        before=stats['page_products']
        out=solve_batch(sub(xj,list(range(len(J))),ids),groups,L,U,Din,q,stats)
        page_counts.append(stats['page_products']-before)
        for i in range(len(J)):
            observed[i][start:start+len(ids)]=out[i]
    assert observed==expect
    assert len(set(page_counts))==1
    assert page_counts[0]<=5*m, (page_counts,m)
    merged=[list(row) for row in X]
    for i,ei in enumerate(ej):
        merged[ei]=observed[i]
    for i,row in enumerate(E):
        if row not in J:
            assert merged[i]==X[i]
    # Original B and C shears on E, never A^-1 B or C A^-1.
    shear_counts=[]
    for cstage in (False,True):
        K=zero(len(E),len(E))
        for ei,i in enumerate(E):
            for ek,k in enumerate(E):
                if (i in J and k in I) if cstage else (i in I and k in J):
                    K[ei][ek]=-H[i][k]
        expected=add(X,dense_mm(K,X))
        observed=[list(row) for row in X]
        per_batch=[]
        for start in range(0,R,q):
            ids=list(range(start,min(start+q,R)))
            before=stats['page_products']
            out=band_product(K,sub(X,list(range(len(E))),ids),q,stats)
            per_batch.append(stats['page_products']-before)
            for i,row in enumerate(out):
                for jj,val in enumerate(row):
                    observed[i][start+jj]+=val
        assert observed==expected
        npanels=(len(E)+q-1)//q
        assert max(per_batch)<=5*npanels
        shear_counts.append(per_batch)
    return {'n':n,'W':W,'cap':cap,'R':R,'cyclic':cyclic,'j':len(J),'e':len(E),
            'groups':list(map(len,physical_groups)),'q':q,
            'solve_products_per_batch':page_counts,
            'shear_products_per_batch':shear_counts,
            'geometry_prefixes_checked':geometry_checks,
            'factor_norms':{k:str(v) for k,v in {'L':norm(denseL),'U':norm(denseU),
                'L_inverse':norm(inv(denseL)),'U_inverse':norm(inv(denseU))}.items()},
            'counts':dict(stats)}


def controls():
    bad=[]
    for k in (2,8,32,128):
        eps=F(1,2**k)
        S=[[eps,F(1)],[F(1),F(0)]]
        Si=inv(S)
        assert norm(S)<=2 and norm(Si)<=2
        assert 1/eps==2**k
        bad.append({'k':k,'matrix_norm':str(norm(S)),'inverse_norm':str(norm(Si)),
                    'first_pivot_inverse':str(1/eps)})
    # With separator {3,4}, consume only 4; 2--4--5 bridges both interiors.
    eliminated={0,1,2,4,5,6,7}
    assert all(a in eliminated and b in eliminated and abs(a-b)<=2
               for a,b in [(2,4),(4,5)])
    assert 3 not in eliminated
    return {'bounded_completed_norm_unbounded_pivot':bad,
            'partial_separator_bridge':[[2,4],[4,5]],
            'one_rhs_padding_ratio_for_W_64':64}


def main():
    layout=[layout_case(e,R,q) for e in (1,3,17,41)
            for q in (1,2,4,8) for R in (1,q,2*q+1)]
    cases=[algebra_case(n,W,cap,R,cyc) for n,W,cap,R in
           [(24,1,4,7),(34,2,8,11),(44,2,8,19),(35,2,8,11)] for cyc in (False,True)]
    result={'status':'PASS','scope':'independent finite interface checks; no upstream execution',
            'layout_cases':len(layout),'algebra_cases':len(cases),
            'layout':layout,'algebra':cases,'rejecting_controls':controls()}
    (ROOT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','layout_cases':len(layout),'algebra_cases':len(cases),
                      'page_products':sum(x['counts']['page_products'] for x in cases),
                      'scalar_products':sum(x['counts']['scalar_products'] for x in cases)},indent=2))


if __name__=='__main__':
    main()
