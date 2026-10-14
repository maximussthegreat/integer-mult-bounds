"""Original finite algebra check. No imports or execution of upstream code.
The all-size inequalities are proved in AUDIT.md; these exact cases are controls.
"""
from fractions import Fraction as F
import json
from pathlib import Path

def mm(A,B):
    return [[sum((a*b for a,b in zip(row,col)),F(0)) for col in zip(*B)] for row in A]
def eye(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def inv(A):
    n=len(A); X=[row[:]+erow for row,erow in zip(A,eye(n))]
    for k in range(n):
        assert X[k][k], 'No-pivot fixture unexpectedly singular'
        p=X[k][k]; X[k]=[x/p for x in X[k]]
        for i in range(n):
            if i!=k:
                c=X[i][k]; X[i]=[x-c*y for x,y in zip(X[i],X[k])]
    return [r[n:] for r in X]
def norm(A): return max((sum(map(abs,r)) for r in A),default=F(0))
def prod(X):
    r=F(1)
    for x in X:r*=x
    return r
def complete(nodes,h):
    c=[F(1)]+[F(0)]*h
    for z in nodes:
        for j in range(1,h+1):c[j]+=z*c[j-1]
    return c[h]
def elementary(nodes,h):
    c=[F(1)]+[F(0)]*h
    for z in nodes:
        for j in range(h,0,-1):c[j]+=z*c[j-1]
    return c[h]

# b=16 log(257/256)>0 and rho=5/4 make every displayed
# normalized Gaussian coefficient an exact rational power of t.
t=F(257,256); rho=F(5,4)
def q(i):return (rho*i+F(1,2)).numerator//(rho*i+F(1,2)).denominator
def beta(i):return rho*i-q(i)
def ex(z):
    v=16*z
    assert v.denominator==1
    return t**v.numerator

def finite(l,n):
    I=list(range(l,l+n)); x={i:ex(2*rho*q(i)) for i in I}
    e={i:ex(-rho*rho*i*i+beta(i)**2) for i in I}
    C={i:prod(1-x[k]/x[i] for k in I if k<i) for i in I}
    G=[[ex(-((rho*j-q(i))**2-beta(j)**2)) for j in I] for i in I]
    L=[[G[ii][jj]*prod(1-x[k]/x[i] for k in I if k<j)/C[j] if i>=j else F(0) for jj,j in enumerate(I)] for ii,i in enumerate(I)]
    U=[[e[j]/e[i]*complete([x[k] for k in I if k<=i],j-i) if j>=i else F(0) for j in I] for i in I]
    D=[[C[i] if i==j else F(0) for j in I] for i in I]
    Li=[]; Ui=[]
    for i in I:
        Li.append([((-1)**(i-j)*ex(-beta(i)**2+beta(j)**2-rho*rho*(i-j)+2*rho*sum((beta(k) for k in range(j+1,i+1)),F(0)))*C[i]/C[j]/prod(1-x[j]/x[k] for k in I if j<k<=i)) if i>=j else F(0) for j in I])
        Ui.append([((-1)**(j-i)*e[j]/e[i]*elementary([x[k] for k in I if k<j],j-i)) if j>=i else F(0) for j in I])
    assert mm(mm(L,D),U)==G
    assert mm(L,Li)==eye(n)==mm(Li,L)
    assert mm(U,Ui)==eye(n)==mm(Ui,U)
    return {'origin':l,'size':n,'phase_changes':sum(q(i+1)-q(i)==2 for i in I[:-1])}

cases=[finite(l,n) for l in [-6,-2,0,3] for n in range(1,6)]
physical=[]
for left,right in [(-7,-3),(-3,3),(0,6),(2,7),(2,2)]:
    P=list(range(left,right+1)); source=[j for j in range(-20,21) if q(j) in P]
    selected=[q(j) for j in source]; holes=[k for k in P if k not in selected]
    assert source==list(range(source[0],source[-1]+1)) if source else True
    sj=dict(zip(selected,source))
    M=[[ex(-(rho*sj[col]-row)**2) if col in sj else F(row==col) for col in P] for row in P]
    order=selected+holes
    V=[[M[P.index(i)][P.index(j)] for j in order] for i in order]
    n=len(source); h=len(holes)
    if n:
        K=[row[:n] for row in V[:n]]; Ki=inv(K)
        R=[row[:n] for row in V[n:]]
        lower=mm(R,Ki) if h else []
        expected=[row+[F(0)]*h for row in Ki]+[[-x for x in row]+erow for row,erow in zip(lower,eye(h))]
        assert inv(V)==expected
        assert norm(expected)<=max(norm(Ki),1+norm(R)*norm(Ki))
    else:assert V==eye(h)
    physical.append({'physical_interval':[left,right],'source_interval':source,'holes':holes,'crosses_phase_cut':any(q(j+1)-q(j)==2 for j in source[:-1])})
result={'status':'PASS_EXACT_FINITE_CONTROLS','finite_ldu_cases':len(cases),'physical_completion_cases':len(physical),'finite_cases':cases,'physical_cases':physical,'scope':'Exact rational identities only. No upstream code executed; no all-size claim derived from finite tests.'}
Path(__file__).with_name('RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['finite_cases','physical_cases']}))
