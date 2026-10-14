#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact certificate. Executes only this self-authored file and stdlib.
Public input is a base64-encoded gzip JSON payload, never executable code.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path

OLD_F = [5,276,303,338,362,68,143,148,167]
CLAIMED_F = [199,276,493,400,362,134,143,148,167]
F0 = [0,1,26,27,44,45,54,55]
F1 = [11,17,28,52,60,74,102,112]
PAIRS = [(1,11),(26,60),(27,74),(44,52),(17,0),(28,45),(102,54),(112,55)]
Z_SHA = '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'
DATA_SHA = '4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c'

def parity(n): return n.bit_count() % 2

def xor(values):
    out=0
    for x in values: out ^= x
    return out

def apply(columns,vector):
    return xor(c for j,c in enumerate(columns) if (vector>>j)&1)

def transpose(columns):
    n=len(columns)
    return [sum(((columns[j]>>k)&1)<<j for j in range(n)) for k in range(n)]

def rref(rows,ncols=None):
    a=list(rows)
    ncols = max((x.bit_length() for x in a),default=0) if ncols is None else ncols
    pivots=[]
    for c in range(ncols):
        r=next((r for r in range(len(pivots),len(a)) if (a[r]>>c)&1),None)
        if r is None: continue
        p=len(pivots)
        a[p],a[r]=a[r],a[p]
        for j in range(len(a)):
            if j != p and ((a[j]>>c)&1): a[j] ^= a[p]
        pivots.append(c)
    return a[:len(pivots)],pivots

def rank(rows): return len(rref(rows)[0])

def inverse_columns(columns):
    n=len(columns)
    a=[v|(1<<(n+i)) for i,v in enumerate(transpose(columns))]
    for c in range(n):
        p=next(i for i in range(c,n) if (a[i]>>c)&1)
        a[c],a[p]=a[p],a[c]
        for i in range(n):
            if i!=c and ((a[i]>>c)&1): a[i]^=a[c]
    assert [v&((1<<n)-1) for v in a] == [1<<i for i in range(n)]
    return transpose([v>>n for v in a])

def all_span(generators):
    s={0}
    for v in generators: s|={x^v for x in s}
    return s

def roots():
    allroots=[]
    for a,b in itertools.combinations(range(8),2):
        for sa,sb in itertools.product((1,-1),repeat=2):
            r=[0]*8;r[a]=2*sa;r[b]=2*sb
            allroots.append(tuple(r))
    allroots += list(s for s in itertools.product((1,-1),repeat=8) if s.count(-1)%2==0)
    reps=[];seen=set()
    for r in allroots:
        key=max(r,tuple(-x for x in r))
        if key not in seen: seen.add(key);reps.append(r)
    assert len(allroots)==240 and len(reps)==120
    return reps

def exact_ip(a,b):
    v=sum(x*y for x,y in zip(a,b))
    assert v%4==0
    return v//4

def rank_witness(rows,row_labels,col_labels):
    # Greedy original-row basis; explicit expressions of every row give an
    # independently inspectable rank upper bound. An invertible minor gives lower.
    idx=[]
    for j,row in enumerate(rows):
        if rank([rows[k] for k in idx]+[row])>len(idx): idx.append(j)
    basis=[rows[j] for j in idx]
    expansions={xor(b for k,b in enumerate(basis) if (mask>>k)&1):mask for mask in range(1<<len(basis))}
    assert all(row in expansions for row in rows)
    cols=rref(basis,len(col_labels))[1]
    minor=[[((rows[r]>>c)&1) for c in cols] for r in idx]
    assert rank([sum(x<<k for k,x in enumerate(row)) for row in minor])==len(idx)
    return {'rank':len(idx),'minor_row_ports':[row_labels[j] for j in idx],
            'minor_col_ports':[col_labels[j] for j in cols],'minor':minor,
            'row_order_ports':row_labels,'column_order_ports':col_labels,
            'basis_rows_bitmasks':basis,'row_basis_coefficients':[expansions[x] for x in rows]}

def run(payload_path):
    z=base64.b64decode(payload_path.read_bytes(),validate=False)
    assert hashlib.sha256(z).hexdigest()==Z_SHA
    raw=gzip.decompress(z)
    assert hashlib.sha256(raw).hexdigest()==DATA_SHA
    word=json.loads(raw)
    ports=word['ports'];v=word['v']
    assert v==112 and len(ports)==len(set(ports))==v and word['h']==9
    # Read existing frame records. Never invoke canonical() or a fallback.
    for k,p in enumerate(ports):
        assert all_span(word['frames'][word['start'][k]])=={0,p}
        assert all_span(word['frames'][word['final'][v+k]])=={x for x in range(512) if parity(x&p)==0}
    R=roots()
    G=[[exact_ip(a,b) for b in R] for a in R]
    B=[[(g+1)%2 for g in row] for row in G]
    masks=[sum(x<<j for j,x in enumerate(row)) for row in B]
    basis=[]
    for i,m in enumerate(masks):
        if rank([masks[j] for j in basis]+[m])>len(basis): basis.append(i)
    assert basis==[0,1,2,4,6,8,10,12,56]
    phi=[sum(B[i][b]<<k for k,b in enumerate(basis)) for i in range(120)]
    oldM=transpose(OLD_F)
    old=[apply(oldM,q) for q in phi]
    live112=[i for i in range(120) if i not in F0]
    live104=[i for i in live112 if i not in F1]
    assert {old[i] for i in live112}==set(ports)
    assert all(parity(p)==1 for p in old)
    def affine(p): return p^(45 if 1^parity(p&45) else 0)
    def H(p): return p^(45 if parity(p&466) else 0)
    Hcols=[H(1<<i) for i in range(9)]
    assert all(H(p)==apply(Hcols,p) and H(H(p))==p for p in range(512))
    assert all(affine(p)==H(p) for p in range(512) if parity(p))
    assert affine(0)==45 and H(0)==0
    newM=[H(c) for c in oldM]
    newF=transpose(newM)
    assert newF==CLAIMED_F
    new=[apply(newM,q) for q in phi]
    assert new==[H(p) for p in old]
    assert len(set(new))==120 and set(new)==set(old)
    assert {new[i] for i in live112}==set(ports)
    assert {new[i] for i in F0}=={old[i] for i in F0}
    inverse=inverse_columns(newM)
    assert all(apply(inverse,apply(newM,x))==x for x in range(512))
    assert all(parity(new[i]&new[j])==B[i][j] for i in range(120) for j in range(120))
    # B in phi coordinates is K^{-1}, where K is the basis-root Gram matrix.
    Kcols=[sum(B[basis[i]][basis[j]]<<i for i in range(9)) for j in range(9)]
    Jcols=inverse_columns(Kcols)
    new_gram_cols=[sum(parity(newM[i]&newM[j])<<i for i in range(9)) for j in range(9)]
    assert new_gram_cols==Jcols
    assert all(parity(phi[i]&apply(Jcols,phi[j]))==B[i][j] for i in range(120) for j in range(120))
    assert parity(1&2)==0 and parity(H(1)&H(2))==1 # H is not dot-orthogonal.
    # Exact reindexed real decoder, independent of binary support ranks.
    e=[G[a][b] for a,b in PAIRS]
    assert all(x in (-1,1) for x in e)
    assert all(G[a][bb]==(e[k] if k==l else 0)
               for k,(a,b) in enumerate(PAIRS) for l,(aa,bb) in enumerate(PAIRS))
    D=[[G[i][a] for a,b in PAIRS] for i in live104]
    T=[[2*e[k]*G[j][b] for k,(a,b) in enumerate(PAIRS)] for j in live104]
    assert all(sum(D[ii][k]*T[jj][k] for k in range(8))==2*G[i][j]
               for ii,i in enumerate(live104) for jj,j in enumerate(live104))
    # Record exact 104 physical-port rows of the decoder.
    decoder=[{'root':i,'physical_port':new[i],'D':D[ii],'T':T[ii]}
             for ii,i in enumerate(live104)]
    terms=[]
    for a,b in PAIRS:
        readers=[i for i in live104 if G[i][a]]
        sources=[j for j in live104 if G[j][b]]
        assert len(readers)==len(sources)==52
        actual=[sum(parity(new[i]&new[j])<<k for k,j in enumerate(sources)) for i in readers]
        abstract=[sum(B[i][j]<<k for k,j in enumerate(sources)) for i in readers]
        previous=[sum(parity(old[i]&old[j])<<k for k,j in enumerate(sources)) for i in readers]
        assert actual==abstract and rank(actual)==7
        witness=rank_witness(actual,[new[i] for i in readers],[new[j] for j in sources])
        terms.append({'pair':[a,b],'old_rank':rank(previous),'corrected_rank':7,'witness':witness})
    old_removed=sorted(old[i] for i in F1);new_removed=sorted(new[i] for i in F1)
    assert old_removed==[22,38,145,161,280,296,415,431]
    assert new_removed==[11,22,140,145,261,280,386,415]
    corrected_live=set(ports)-set(new_removed)
    old_live=set(ports)-set(old_removed)
    old_hist=Counter(sum(parity(p&q) for q in old_live) for p in old_live)
    new_hist=Counter(sum(parity(p&q) for q in corrected_live) for p in corrected_live)
    assert old_hist=={52:12,56:88,60:4} and new_hist=={56:104}
    return {'status':'INDEPENDENT_EXACT_FINITE_ADAPTER_REVIEW_PASS',
      'payload_sha256':DATA_SHA,'compressed_sha256':Z_SHA,
      'actual_start_frames_verified':112,'actual_final_frames_verified':112,
      'actual_selected_112_set_matches':True,'coordinate_basis':basis,
      'affine_map_zero':affine(0),'linear_H_zero':H(0),'H_columns':Hcols,
      'H_involution_on_all_512':True,'H_is_dot_orthogonal':False,
      'corrected_F_columns':newF,'root_phi_to_physical_columns':newM,
      'physical_to_root_phi_columns':inverse,'E8_form_in_phi_coordinates_columns':Jcols,
      'global_isometry_matrix_identity_verified':True,
      'full_120_pairing_entries_checked':14400,'full_112_pairing_entries_checked':12544,
      'old_removed_ports':old_removed,'corrected_removed_ports':new_removed,
      'corrected_removed_positions_in_original_payload':[ports.index(p) for p in new_removed],
      'old_live_row_weight_histogram':dict(sorted(old_hist.items())),
      'corrected_live_row_weight_histogram':dict(sorted(new_hist.items())),
      'decoder_dual_signs':e,'decoder_exact_reindexed_2G_entries_checked':10816,
      'decoder_identity_to_original_payload_real_target_checked':False,
      'copy_rank_terms':[t['corrected_rank'] for t in terms],'copy_rank_total':56,
      'old_copy_rank_terms':[t['old_rank'] for t in terms],
      'root_to_old_port':old,'root_to_corrected_port':new,
      'decoder_rows':decoder,'terms':terms,
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--payload',type=Path,default=Path(__file__).resolve().parent/'inputs'/'selected_payload.b64')
    args=parser.parse_args()
    print(json.dumps(run(args.payload),indent=2))
