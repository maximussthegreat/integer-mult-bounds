# Sparse-union streaming: constructive fixed-tape lemma and audit
Date: 2026-10-14  
Repository: CrocSwap/integer-mult-bounds, PR #1673  
Pinned commit: 2569871ff906d2a2abfc86e97126ab9afe2e4a5a

Attribution: The upstream capped-phase-fusion package credits Vlado
Vojdanovski with substantial AI assistance. Its complete-rectangle union
construction and inherited binary block-interchange primitive are prior
inputs to this audit. This report makes their sequential-tape schedule and
cost boundary explicit; it does not claim a new multiplication exponent,
new finite supplier, or priority for those underlying constructions.
Source-specific notices and the upstream package's stated licenses remain
applicable to copied material.

## Verdict

The proposed no-sort sparse-union **layout** bound is valid. A constant number
of sequential tapes suffices, with every payload read, write, rewind, work-tape
reset, and ordered replacement charged. The central transpose costs logarithm
of the selected field size, not logarithm of the spectator size.

For one sweep through the axes, starting with the union already gathered,
the bound is

    O(g |U| + sum_i |U_i| (1 + ceil(log2(max(1, |E_i|)))))

record movement. Consequently it is O(g|U| + sum_i |U_i| log L) for L >= 2.
Gathering and scattering add O(L^g) record movement per sparse window.
The local matrix computations and their coefficient traffic are additional,
separately charged terms. Arbitrary rational matrices give exact algebra but
do not by themselves give bounded-size records or cheap arithmetic.

This construction needs no full-union sort, no RAM lookup, no rank/select
oracle, no g-dependent tape count, and no padding of a long spectator axis.
It does not prove the separate support-local routing, dense compiler,
Gaussian precision, or boundary arithmetic theorems.

## 1. Precise contract

Let L >= 2 and g >= 1 be integers. Write [L] = {0,...,L-1}, N = L^g.
For each i in {1,...,g}, fix E_i subset [L], with e_i = |E_i|, and a matrix

T_i = I on E_i^c, direct sum an arbitrary rational e_i-by-e_i block.

Thus there are no matrix entries coupling E_i to its complement. E_i is
fixed throughout the complete microbox; it does not depend on the other
coordinates. Define

    U_i = {x : x_i in E_i},
    U   = union_i U_i,
    n_i = |U_i| = e_i L^(g-1),
    u   = |U|   = L^g - product_i (L-e_i).

Data is a complete tensor in lexicographic coordinate order. All tensor
coefficients can be arbitrary, signed, or zero. Additional complete outer
prefix fibers or inner spectator fibers are allowed: their cardinalities
multiply the counts below. They are not assumed clean or initialized to
zero.

The layout theorem is about records of width at most w payload bits plus
h header/control bits. Headers contain the local coordinate, membership
flags, and temporary ordinal/padding information. For a microbox,
h = O(g log L). With external prefix and suffix multiplicities P_ext and
S_ext, use h = O(g log L + log(P_ext+1) + log(S_ext+1)), including their
loop-counter widths and any external labels actually carried. The bit implementation
cost established here is O((w+h) times the stated record count), plus
explicit support/factor preparation and arithmetic. When h = O(w), this
is O(w times the record count). Exact rational arithmetic with unbounded
height cannot be treated as a constant-width record model.

Tapes are ordinary read/write sequential work tapes with left-end and live
end markers. Heads move one cell at a time. Work tapes can be overwritten;
their old contents need not be restored. This is not a reversible
dirty-ancilla claim. The algorithm does preserve arbitrary spectator data.
A bounded number of record buffers and control tapes is enough.

A line-operation interface must accept a complete E_i line in increasing
E_i order, apply the specified block to its coefficient values, and emit
the same line positions in that order. Coordinate headers are labels, not
part of the linear arithmetic. Charge that interface's actual work,
coefficient reads, head movement, rounding, and temporary storage separately.
A straightforward exact rational implementation exists by repeated
sequential dot products, but it need not be fast.

## 2. Exact algebra and why the rectangles are complete

For an axis-i operation, every coordinate outside E_i is fixed. Every
nonidentity contribution goes between two coordinates in E_i. Hence a
basis vector at a point of U is sent into the span of U, and a basis vector
outside U is fixed. U and its complement are invariant for every T_i and
therefore for every finite sequence of these sparse operations.

For each i, filtering U by the test x_i in E_i yields precisely

    [L]^(i-1) x E_i x [L]^(g-i).

No coordinate is absent: membership in E_i already places the point in U,
regardless of the other coordinates. Restricting an axis operation to this
rectangle therefore computes every nonidentity contribution it needs.
All other records of U are identity coordinates for this operation.

Induct on the executed sparse operations. Initially the gathered U agrees
with the full tensor. At each step the complete rectangle receives the
correct axis update, and the other union entries are unchanged. Its ordered
replacement therefore agrees with the full tensor on U; outside U the full
tensor was unchanged. This proves exact correctness for arbitrary rational
blocks, including singular blocks. No invertibility or stability assumption
is needed for this finite algebra statement.

Closure permits arbitrary many sparse operations, but the runtime grows
with their number. For a sequence i_1,...,i_k the corresponding layout
bound is

    O(k u + sum_{t=1}^k n_{i_t}(1+log(max(1,e_{i_t})))).

One or any fixed number of sweeps gives the claimed g-dependent bound.

## 3. A literal binary block interchange

Consider a complete stream in the order

    [P][2][B][R],

where P is any number of prefix fibers, B and R are arbitrary positive
integers, and each position stores a whole record. B and R need not be
powers of two. The desired order is

    [P][B][2][R].

For each prefix fiber, using the same two work tapes A and C:

1. Copy its first BR records to A and its second BR records to C.
2. Rewind A and C to their origins, crossing exactly BR records on each.
3. For b = 0,...,B-1, append the next R records of A and then the next
   R records of C to the output stream.
4. Rewind both work tapes and reset their live end markers before reusing
   them for the next prefix fiber.

The input and output heads move only forward during the pass. Rewind them
at the end if the next operation requires heads at the origin. Nothing is
read from a work-tape tail beyond its current live end marker, so stale
records on reused tapes cannot enter the computation.

For n = 2PBR records, there are exactly 4n forward record traversals:
input reads, work-tape writes, work-tape reads, output writes. Rewinding work
tapes after writing and after consuming them costs 2n backward traversals;
rewinding the complete input and output costs a further 2n. Thus the
literal record-head movement is 8n, plus O(n) marker/control events.
End-marker writes and loop control do not require a distant seek.

The inverse consumes [P][B][2][R], distributes alternating R-record blocks
to A and C, rewinds them, and concatenates A then C for each prefix. The
same accounting applies. A constant number of tapes is used for all P.

This is a streaming split/interleave operation. It is not sorting by B,
and its pass count does not depend on log B.

## 4. Moving one small field across an arbitrarily long spectator

Suppose the extracted stream has shape [P][e][S]. First take
q = 2^ceil(log2 e) when e >= 1. Pad only the e field to q; q < 2e unless
already dyadic. For each P fiber, append dummy S-record blocks after the e
real blocks. The total padded volume is less than twice the real volume.

Write q = 2^m. Starting from [P][q][S], move the selected field's bits
**rightmost first**. After t passes the layout is

    [P][leading m-t selected bits][S][trailing t selected bits].

For the next pass, use the binary right-interchange with

    prefix count = P * 2^(m-t-1),
    B = S,
    R = 2^t.

It transforms the rightmost remaining selected bit across S and inserts it
before the already moved trailing bits. After m passes the order is exactly
[P][S][q], with the original selected-field bit order preserved. Each pass
moves the same PqS records. Moving high bits first and inserting before the
old suffix would reverse the ordinal bits; that is not the schedule here.

Remove the dummy entries to obtain [P][S][e]. Perform the line operation.
For the reverse transpose, pad each e-line to q again, apply the inverse
binary passes in reverse order, and remove dummy blocks. This returns
[P][e][S]. Alternatively, padding can be retained through a line operation
that explicitly treats dummy rows as independent identities.

Dummy payload values need not be zero: the line arithmetic must exclude
them or fix them. They are temporary layout positions, not fabricated
missing input coordinates. Removing/reinserting them around arithmetic is
the simplest contract. No spectator field is padded.

Both transposes and both padding cycles cost O(PeS(1+m)). e = 0 is skipped;
e = 1 or S = 1 needs no permutation. The construction works for arbitrary
non-dyadic e and S and arbitrary external prefix fibers.

## 5. Extraction, ordinals, and ordered replacement

Keep the current union master in its original lexicographic order, with its
coordinate/membership header. To apply axis i:

1. Scan U once, copying precisely the records whose i-th membership flag
   is set. Keep the full original coordinate header with the copied record.
2. Add an ordinal 0,...,e_i-1 to the selected coordinate. An ordinal advances
   only when x_i changes, and resets when the preceding coordinate prefix
   changes. It does not advance on every payload record. Completeness makes
   each ordinal occur exactly L^(g-i) times per prefix, times any suffix
   spectator multiplicity. Equivalently, known rectangle dimensions supply
   nested counters, with no rank/select lookup.
3. Perform the small-field transpose, line operation, and inverse transpose.
4. Scan the old U into a fresh union tape. If its i-th flag is zero, copy
   its old value. If the flag is one, consume exactly the next updated
   rectangle record and write that value with the same coordinate header.

The extracted stream and the returned stream enumerate exactly the same
ordered positions. Replacement can therefore be driven by membership
flags alone. A header-equality check is optional validation, not a search.
Even an explicit comparison costs O(h) per consumed record, not a radix
pass per key bit. There is no sort and no key of length g log s is used.

All master, update, and output rewinds cross O(u+n_i) records per axis.
The union master can be double-buffered; rectangle input/output and the
two binary work tapes are recycled. Six live payload tapes suffice inside
a window, with a separate retained full-tensor tape if desired. A
conservative fixed allocation of ten tapes covers full input/output,
union input/output, rectangle input/output, two transpose work tapes,
descriptor and control storage, before any fixed additional arithmetic
work tapes. The count does not grow with g or L.

Auxiliary layout storage is O(u+max_i n_i) records, plus support descriptors.
If a fresh full output is desired at scatter, one extra O(N) stream is
used. Ordinary sequential in-place scatter also works when record widths
are fixed.

## 6. Gather/scatter and support membership without hidden random access

Gather U by one forward full-tensor scan, copying a record once when the OR
of its flags is one. Keep the full tensor with its old union values until
scatter. Scatter by another ordered full scan, replacing each marked
position with the next updated union value. The complement is copied or
left unchanged. Each procedure and its head resets cost O(N+u) movement.

The theorem can take the membership header as input. It can also construct
it without a RAM membership oracle once supports are supplied as increasing
lists or bitmaps. Sorting an unordered support representation, or generating
supports from another description, is a separate preparation cost.

For example, store the g length-L membership bitmaps consecutively on one
descriptor tape. Enumerate [L]^g with a lexicographic odometer, keeping the
current coordinates and g flags in O(g log L) control space. Usually only
the last coordinate changes: its bitmap head moves one cell. When a carry
resets j trailing coordinates, move back to the new next coordinate bit,
then forward through the starts of the reset fields to restore their
flags. This costs O((j+1)L) head movement and occurs at most N/L^j times.

    sum_{j>=1} O((j+1)L N/L^j) = O(N), for L >= 2.

Initial positioning and final reset cost O(gL), also O(N), since gL <= 2L^g.
Copying/scanning the current coordinate/flag header and conservative counter
maintenance costs O(g log L) bit work per payload record. Increasing support
lists can be converted into bitmaps in O(gL log L) conservative bit work, absorbed
by O(N(w+h)) when h includes log L. If supports are generated from analytic
descriptors rather than explicitly supplied, their generation is still a
separately charged setup obligation.

This optional bitmap construction is an independent way to make the
membership interface explicit. The candidate instead charges a
O(g h_source^2 polylog p) phase-endpoint membership calculation, with
h_source = Theta(p/d). Both approaches keep the descriptor obligation visible.
The bitmap construction has not been implemented by the sibling finite
payload simulator; its claim here is the written constructive argument.

## 7. The exact movement ledger

For one complete sparse sweep, excluding local arithmetic and setup:

    extraction/replacement/resets: O(g u),
    two small-field transposes:    O(sum_i n_i(1+log(max(1,e_i)))),
    one gather and one scatter:    O(N).

Thus

    M_window = O(N + g u + sum_i n_i log L), for L >= 2.

For an already gathered union, omit the N term. With c sparse sweeps retained
in one window, multiply the inner terms by c. This includes C followed by
S^-1 with c=2. All bounds include prefix-dependent work-tape resets. Header
tests, end markers, and loop control have at most O((w+h) M_window) bit cost
under the stated conservative width model. Arithmetic and coefficient-page
traffic must then be added, not absorbed by calling them layout.

Let mu = max_i e_i/L. Then exactly

    u/N = 1-product_i(1-e_i/L) <= min(1, sum_i e_i/L) <= min(1,g mu),
    sum_i n_i = N sum_i e_i/L <= N g mu.

Hence the inner record movement is bounded by

    O(N [g^2 mu + g mu log L]).

This inequality does not require g mu < 1. That condition is relevant to a
sparse asymptotic saving, not to correctness or the movement construction.
It also imposes no condition g < h_source or g < sqrt(B).

## 8. Translation to the capped ledger

The capped support bound in CAPPED-SIGNOFF.md is

    e_i = O(L W/B polylog p + W polylog p).

Therefore

    mu = O((W/B + W/L) polylog p).

Dropping W/L requires B = O(L). That condition is present in the application:
L is about p^8, while the cap B is p^xi with xi < 1. Thus
mu = O((W/B) polylog p) is justified there. It is not an unconditional
identity for arbitrary B and L.

With L = poly(p), log L = O(log p), g >= 1, and h = O(p) for O(p)-bit
records, let V denote actual bit volume, not number of coefficients.
The per-group inner movement is

    O(V g^2 W/B polylog p).

One constant number of gathers/scatters per group adds O(V), and d/g
groups add

    union movement: O(V d g W/B polylog p),
    full scans:     O(V d/g), up to fixed logarithmic overheads.

Use a ceiling for the number of groups; the displayed simplification uses
d >= g, satisfied by the pinned exponents. Intermediate tensor bit volumes
must stay within the retained constant-factor total-volume contract.
If the endpoint term were not absorbed, it would contribute separately
O(V d g W/L polylog p).

For MATRIX-LAYOUT-SIGNOFF.md's displayed parameter choice,
g log L = p^beta polylog p with beta about .249785 < 1, so local headers
fit within O(p)-bit records. Its charged membership exponent
beta+2(1-epsilon) is about .252295 < 1. The small gap making g mu -> 0 is
xi-beta-1/2 about .000428506, but no new algorithmic assumption follows
from how small that positive gap is.

The independently supplied support router is not used as a subroutine of
the union transpose. It supplies the complete microbox in the appropriate
physical layout before this lemma begins. Its dirty-control reservoirs,
short-record suffix conjugation, and complete coarse-label hypotheses
remain separate obligations.

## 9. Dense interludes and two real sparse windows

For H = [A B; C D], with S = D-C A^-1 B, the execution order is

    diag(A^-1,I)
    [I 0; -C I]
    diag(I,S^-1)
    diag(A,I)
    [I -B; 0 I]
    diag(A^-1,I).

One gathered union can be retained across the C sweep and the S^-1 sweep.
Scatter it before the middle dense A stage. Gather a new union for B,
scatter again, and run the final dense stage. Thus there are genuinely
two sparse windows, and no dense stage is evaluated on a retained sparse
union.

A smallest tridiagonal example with a nonempty boundary and a deep interior
shows why the scatter/regather cannot be omitted. Take

    H = [[2,1,0], [1,2,1], [0,1,2]],
    J = {0}, I = {1,2}, E = {0,1},
    A^-1 = (1/3) [[2,-1],[-1,2]].

The union for g=1 is {0,1}. A coefficient at coordinate 1 is sent by the
dense interior A^-1 stage to (2/3)e_1-(1/3)e_2. Its coordinate-2 contribution
lies outside the union. Bandwidth one and the actual original B/C incident
support do not prevent this leakage.

The pinned check_union.py executes union_window separately for C and S^-1,
so it actually gathers/scatters three times. Its claim of two physical
windows is metadata, not an execution property. The discrepancy does not
invalidate the exponent, because it is a constant factor; it does mean
that existing finite evidence did not demonstrate retained two-sweep reuse.

## 10. Three overbroad readings that are false

1. **No O(N) gather/scatter term.** For g=1, E={L-1}, and a nonidentity
   scalar update, a sequential head beginning at coordinate zero must travel
   Theta(L) to reach the affected final record. The gathered-union expression
   is only O(log L). It cannot be the entire full-tensor operation cost.

2. **Arbitrary matrix evaluation included for free.** Take g=1 and E=[L].
   An arbitrary explicit L-by-L matrix on an all-ones vector requires
   inspecting L^2 independently relevant coefficient entries in the worst
   case. Its coefficient traffic is not O(L log L). A supplied faster or
   structured line/batch implementation must have its own charged bound.

3. **Arbitrary rational height in fixed-width bit cost.** Already for
   L=2, g=1, E={0}, the scalar block [2^M] sends input 1 to an M+1-bit integer.
   Fixed p-bit record cost fails when M is unbounded relative to p. The
   exact algebra remains true; a uniform O(p)-bit implementation requires
   the separately proved magnitude/precision interface.

These are scope counterexamples, not counterexamples to the candidate's
properly separated sparse-layout, arithmetic, and precision ledger.

## 11. Evidence scope and recommended next verification

This report independently constructs the uniform tape schedule. It does not
claim that finitely many simulations prove its all-size complexity, or that
the original repository contains an end-to-end executable bit-Turing
implementation.

The accompanying independent experiment, sequential_union.py, was read
during development. Its bit_swap and move_field routines implement the
rightmost-bit-first schedule above and assert the exact 8n record-head
movement count. The review confirmed the e<=1/suffix==1 special cases and
the reverse pass order. Its Python metadata and exact coefficient-vector
arithmetic are host abstractions; they do not independently certify header
bit cost, factor generation, or precision.

The useful remaining interface to test next is not a full-union key sort.
It is the composition of the complete-box support router, charged support/
factor generation, the fixed-tape union layout proved here, and the actual
bounded-precision boundary line/batch routine at the same record-width
contract.

## Sources

All repository reads were pinned to the commit above. No upstream program
was executed and no external repository state was changed.

- PHASE-LAYOUT-AUDIT.md, blob bbeeee7431720817f031360f67b2186abac5cd23
- MATRIX-LAYOUT-SIGNOFF.md, blob d683e4d495330a2310e31b07c7dc896390334468
- SUPPORT-ROUTER.md, blob 4f39fa9eaf553d1df5111de8c19bcf5bf9829c2b
- CAPPED-SIGNOFF.md, blob fc3456387b9399c8108db75b46088f85c5c26f82
- CAPPED-INTERIORS.md, blob 62c3fa27b61a648c65c9e3f6fc4dc95d7b05bd3e
- MATRIX-COROLLARY.md, blob f08bb57f9c33a4b9bdca9eb8f6ea3c0862cd56d5
- README.md, blob f7f3348ee367ac0fe2a92cc48ca599869b49e306
- evidence/independent_fusion_review_ultra/union_subreview.md,
  blob 04286a6198b050bd184be8afef3a85402b3aef93
- evidence/phase_layout_audit_ultra/check_union.py, read as inert text,
  blob 0b3f0af7014dc23d8d80a82c67f2f7b24d3bd1ab

Canonical pinned source root:
https://github.com/CrocSwap/integer-mult-bounds/tree/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion
