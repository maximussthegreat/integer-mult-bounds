"""Independent exact Newton/divided-difference checks; no upstream imports.

The finite cases exercise real, nonintegral q, both beta endpoints, exact
unit gaps, and negative origins. They are controls, not an all-size proof.
"""
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path
import json

t = F(257, 256)
rho = F(5, 4)

def expb(z):
    z = 16*z
    assert z.denominator == 1
    return t**z.numerator

def matmul(a, b):
    return [[sum((x*y for x,y in zip(row,col)), F(0)) for col in zip(*b)] for row in a]

def inverse(a):
    n = len(a)
    w = [row[:] + [F(i == j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        assert w[j][j]
        pivot = w[j][j]
        w[j] = [x/pivot for x in w[j]]
        for i in range(n):
            if i != j:
                factor = w[i][j]
                w[i] = [x-factor*y for x,y in zip(w[i],w[j])]
    return [row[n:] for row in w]

def check(origin, betas):
    n = len(betas)
    ids = list(range(origin,origin+n))
    beta = dict(zip(ids,betas))
    q = {i:rho*i-beta[i] for i in ids}
    x = {i:expb(2*rho*q[i]) for i in ids}
    e = {i:expb(-rho*rho*i*i+beta[i]**2) for i in ids}
    a = {i:expb(-q[i]**2)*x[i]**origin for i in ids}
    pivots = {i:a[i]*prod(x[i]-x[k] for k in ids if k<i)*e[i] for i in ids}
    c = {i:prod(1-x[k]/x[i] for k in ids if k<i) for i in ids}
    assert pivots == c
    # Build L directly from Newton basis evaluation, avoiding the audit's G-based formula.
    L = [[a[i]*prod(x[i]-x[k] for k in ids if k<j)*e[j]/c[j] if i>=j else F(0)
          for j in ids] for i in ids]
    G = [[expb(-((rho*j-q[i])**2-beta[j]**2)) for j in ids] for i in ids]
    Li = inverse(L)
    U = [[z/c[i] for z in row] for i,row in zip(ids,matmul(Li,G))]
    Ui = inverse(U)
    # Both inverse formulas are compared with independently inverted factors.
    for ii,i in enumerate(ids):
        for jj,j in enumerate(ids):
            if i >= j:
                exponent = -beta[i]**2+beta[j]**2-rho*rho*(i-j)+2*rho*sum(beta[k] for k in ids if j<k<=i)
                formula = (-1)**(i-j)*expb(exponent)*c[i]/c[j]/prod(1-x[j]/x[k] for k in ids if j<k<=i)
                assert Li[ii][jj] == formula
                assert exponent <= F(1,4)-rho*(rho-1)*(i-j)
            else:
                assert Li[ii][jj] == 0
            if j >= i:
                h = j-i
                elementary = sum((prod(subset) for subset in __import__('itertools').combinations([x[k] for k in ids if k<j],h)),F(0))
                assert Ui[ii][jj] == (-1)**h*e[j]/e[i]*elementary
                exponent = beta[j]**2-beta[i]**2-rho*rho*h-2*rho*sum(beta[k] for k in ids if i<=k<j)
                assert exponent <= F(1,4)-rho*(rho-1)*h
            else:
                assert Ui[ii][jj] == 0

count=0
values=[F(-1,2),F(-1,4),F(0),F(1,4),F(1,2)]
for betas in product(values,repeat=4):
    if any(b-a>rho-1 for a,b in zip(betas,betas[1:])):
        continue
    for origin in (-3,2):
        check(origin,betas)
        count+=1
result={'status':'PASS','independent_nonintegral_q_cases':count,'rho':'5/4','b':'16 log(257/256)','scope':'Exact finite identities and exponent envelopes; not an all-size or fixed-table certificate.'}
Path(__file__).with_name('INDEPENDENT_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
