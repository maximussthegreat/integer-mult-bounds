# Boundary RHS batching: constructive conditional interface audit

Date: 2026-10-14. Source pin: `2569871ff906d2a2abfc86e97126ab9afe2e4a5a`,
the head source of upstream CrocSwap/integer-mult-bounds PR #1673, read from
the Vlado-V/integer-mult-bounds source fork. These are distinct repositories,
not a rename or redirect. No upstream program was executed. No external
repository state was changed. This audit asserts no new multiplication exponent.

## Result and scope

The boundary-batching cost can be obtained by a concrete sequential-page
algorithm. Its matrices are **many local O(W)-square pages**, rather than one
dense matrix on E, and its Schur inverse is applied by a block solve rather
than being treated as banded. Factor loading, page rewinds, incomplete RHS
batches, and the E-versus-J distinction fit the stated cost.

This is a conditional interface result. It assumes the source's effective
coefficient generation and analytic bounds on physical-prefix inverses of
the actual rounded Gaussian operator. The source does more than assert a
bound on the completed inverse: CAPPED-GAUGE-AUDIT.md section 5 supplies the
whole-boundary-group elimination geometry needed to invoke its inherited
finite contiguous Gaussian inverse theorem. We independently check that
geometry and its algebraic implication here; we do not independently prove
that inherited analytic theorem or verify its constants for all Gaussian
parameters. Completed-matrix conditioning alone would be insufficient.

The already completed sparse-union proof supplies extraction and ordered
replacement of E lines. This audit starts at those lines and supplies the
previously unspecified batching/solve interface. Its finite experiment
checks exact rational block algebra and literal batch-layout tape movement.
It is not a complete bit-Turing implementation or a Gaussian error certificate.

## 1. Actual objects, sizes, and coefficient reuse

For one fixed axis and complete microbox, let H be its length-L physical
matrix of half-bandwidth W. A periodic matrix may have the usual wrap edges.
Carving partitions its coordinates into dyadic interiors and retained
boundary groups. Write I for the interiors, J for the boundary, j=|J|, and

    H in I,J order = [ A  B ; C  D ],    S = D - C A^-1 B.

Here B is |I|-by-j, C is j-by-|I|, and S is j-by-j. A is a direct sum of
interior blocks. Let E consist of J together with every interior coordinate
incident to an original B or C entry, and set e=|E|. Consequently the sparse
shears on E are I plus masked copies of ORIGINAL B or C. They do not use
A^-1 B or C A^-1. Applying S or S^-1 touches only J; every E\J value must be
copied unchanged. In particular e can greatly exceed W and S^-1 can be dense.

The sources' capped carving gives groups of W to cW consecutive retained
coordinates, for an absolute c, with at most short clipped endpoint groups.
Join a short endpoint group to its neighbor, or keep it in an O(W)-size
endpoint border. This changes constants only. Original phase endpoints,
holes, and period cuts belong to retained groups. With Bcap>W eventually,
interiors are longer than W, and separators contain at least W vertices.

An interior elimination joins only its two adjacent boundary groups.
Original width-W edges cannot cross a complete W-vertex separator. Thus S
is block tridiagonal in physical boundary-group order, with a possible
first/last wrap block. Merging adjacent small end groups preserves constant
block bandwidth. Equivalently one can use a constant-width block band and
an O(W)-size border. The number of pages is O(j/W+1), each has O(W^2) entries,
and total factor storage is O((j+W)W) coefficients. This is NOT O(W^2) storage
for the entire line.

Deleting coordinates to pass to E order cannot increase ordinal distance
of an original width-W edge. Thus each B/C shear, viewed as an e-square
masked matrix plus identity, is still width-W banded in E order, apart from
the same wrap border. Dividing E into consecutive q-row panels with q=Theta(W)
needs O(e/q+1) panels and O(1) off-diagonal pages per ordinary panel. This
does not require E to be one interval or have only one endpoint component.

For the minimal incident E above, the carving also gives e=O(j): each
boundary group adds at most O(W) incident interior coordinates and itself
contains Omega(W) vertices, except the constant-size endpoint exceptions.
Both have the stated upper bound

    e,j = O(L W/Bcap polylog p + W polylog p).

All other coordinates are RHS labels only. Within one fixed microbox the
factor coefficients do not depend on those labels. Batch only this common
factor class. Do not silently batch across microboxes with different coarse
origins. The R=L^(g-1) inner RHS stock, with any additional complete spectators,
is superpolynomial for the application g=p^beta. In particular R>=q eventually.
This RHS lower bound is a genuine amortization premise.

## 2. Block factorization and its actual frontier

For a nonperiodic block tridiagonal S, ordinary block Gaussian elimination
in increasing group order gives S=LU. L has identity diagonal and one lower
block diagonal; U has invertible diagonal pivots and one upper block diagonal.
For a periodic S, leave the last group as a border until the end. At step k,
the only future neighbors are the next group and that border. Elimination
adds only the edge between them. L may therefore have a dense LAST BLOCK ROW,
and U a dense LAST BLOCK COLUMN, but each contains only O(j/W+1) nonzero pages.
It does not create a dense j-by-j factor. Constant-width initial block bands
give the same conclusion with a constant-size frontier and border.

Precompute every pivot inverse as one O(W)-square page; online diagonal
solves are then page multiplications. This is legitimate polynomial setup
only under the coefficient-generation and conditioning hypotheses below.
Do not use scalar pivoting inside a boundary group as a replacement for that
hypothesis. Dense local inversion is an offline polynomial-cost operation.

For one RHS batch of b=q columns, the forward solve maintains the preceding
O(1) solved panels and an O(W)-by-b border accumulator. As each ordinary
panel y_k is written, its contribution to the final border equation is
accumulated immediately. No second scan over all earlier y panels is needed
for each boundary row. Solve the border equation last.

The backward solve holds the solved border panel, reads the y panels in
decreasing group order, and maintains the next O(1) solved panels. At group k
it subtracts the next-group and border products, then applies its stored
pivot-inverse page. Each panel uses O(1) square products. Write outputs in
decreasing group order and reverse that panel order once at the end.

A tape can read a whole panel backward into a scratch tape and read that
scratch backward to recover its forward internal order, crossing each panel
only O(1) times. This implements decreasing panel traversal and final panel
order reversal with O(jb) record movement, including resets, without sorting.
Scratch panel tapes and the fixed number of frontier tapes are reused.

Applying S itself is simpler: retain a three-panel input window (or constant
bandwidth equivalent), keep the first/last border panels, and write each
output after its O(1) page products. A B/C shear uses the corresponding
three-panel E window and original input values, with the same page ledger.

## 3. Small-field batching with literal head costs

The prior union lemma emits complete E lines in order [R][e]. Choose a dyadic
q between cW and 2cW, large enough for every boundary group, and split R into
batches of q independent RHS. Only the last batch is padded; its dummy RHS
columns are zero. Let R'=q ceil(R/q). If R>=q then R'<2R. No tensor coordinate
is added by this temporary arithmetic padding.

The stream is now [batch][q][e]. Transpose the q field across e to obtain
[batch][e][q]. Move its binary digits rightmost first. One binary pass is

    [P][2][B][T] -> [P][B][2][T].

For each prefix copy the first BT records to one work tape and the next BT
to another, rewind both, then interleave their T-record subblocks. Reset both
work tapes before the next prefix. For n=2PBT records, reads and writes cost
4n forward traversals, work-tape rewinds 2n backward traversals, and the input
and output resets 2n backward traversals: exactly 8n record-head movements,
plus O(n) control/marker events. The inverse distributes alternating blocks
and concatenates them with the same cost.

Each of log2 q passes sees eR' records. After arithmetic, reverse the passes
and remove only the known dummy RHS columns. Thus both transposes cost

    16 e R' log2(q) record-head movements,

plus O(eR') padding/record-copy movement. There is no log R term. This starts
from already extracted E lines, so it is additional to the previous union
transpose, not a substitution for that theorem's movement charge.

These are record traversals. Bit work multiplies them by the actual payload
and header/control width, including coordinate labels and counters. Use the
previous union lemma's O(p)-bit header contract in the application; an
arbitrarily long spectator counter is not silently a constant-width record.

For an S stage, filter J into its own [batch][j][q] stream and retain the
ordered E master. After the boundary operation, replace precisely J rows
in an ordered E scan. No sort, rank/select operation, or fabricated input
zero is needed. E\J payloads, including arbitrary nonzero values, are copied.
This costs O(eR') movement. Local panel row padding uses zero off-diagonal
entries and identity pivot padding; it is removed after the local product.

## 4. Factor traffic, multiplication work, and fixed tapes

Store forward-solve and backward-solve page schedules sequentially. For
each RHS batch scan each required original factor page ONCE into local
scratch; read/reuse scratch as often as the matrix multiplication routine
requires. Rewind the whole factor schedule once between batches. The cost
is O((j+W)W ceil(R/q)) coefficient-record traversal for S^-1, and
O((e+W)W ceil(R/q)) for shears. With q=Theta(W), R>=q, e>=W when nonempty,
these are O(jR+WR) and O(eR), respectively. The page rewinds are not free,
but are smaller than the charged arithmetic work for omega>2.

The matrix routine is not allowed free scratch access. A fixed bilinear
block formula admits a fixed-tape recursive implementation: arrange a
matrix's small row/column fields in recursive block order by O(n^2 log n)
record movement; at each node sequentially form the constant number of
input linear combinations, recurse, and merge their output contributions.
A depth-first stack of suspended operand/result pages is a sequential tape
stack, not a new tape per level. Each suspended frame is read/written O(1)
times per child; a node's data movement is O(n^2) once blocked. Even allowing
an O(n^2 log n) conversion at every node gives

    T(n) <= r T(n/m) + O(n^2 log n).

For Strassen, m=2,r=7, so this is O(n^log2(7)). For the additional matrix
corollary use a fixed formula of exponent rho<tau, tau>2; the possible
polylogarithmic traversal overhead is absorbed in the strict slack or in
the ledger's polylog p. Scalar arithmetic on t-bit values is charged by
M(t), rather than treating exact rational arithmetic as unit cost.

A fixed number of tapes suffice: E input/output, filtered J input/output,
the two binary-transpose tapes, two factor schedules, a panel stack, and
a fixed number of frontier/accumulator/arithmetic tapes. Their count is
independent of L, W, R, j, and the number of groups. Storage O(eR'+jW+W^2)
is sufficient using a retained batch/line stream; a whole extracted rectangle
can remain on its existing input tape. This is ordinary overwritable-tape
storage, not a reversible dirty-ancilla claim.

The conservative arithmetic count for an E shear or boundary solve is

    O((ceil(e/q)+ceil(j/q)+1) ceil(R/q) q^omega)

scalar operations. For e>=W, R>=W and q=Theta(W), it is

    O(e R W^(omega-2)).

For an S-only stage the sharper count is O(j R W^(omega-2)+eR), including
the identity-row copy. The general ceiling expression must be retained
when there are fewer than W RHS or fewer than W active rows. For example,
padding ONE RHS to W incurs a factor W overhead compared with the claimed
amortized per-RHS count; the application avoids this by its complete-box stock.

## 5. The conditioning premise and what the sources actually establish

Bounded ||S|| and ||S^-1|| do not by themselves bound block pivots or factors.
For 0<epsilon<=1, the exact matrix

    S_epsilon = [ epsilon  1 ; 1  0 ],
    S_epsilon^-1 = [ 0  1 ; 1  -epsilon ]

has both infinity norms at most 2. Elimination of its first scalar group
requires pivot inverse 1/epsilon and creates second pivot -1/epsilon.
The first eliminated principal inverse is unbounded as epsilon tends to
zero. This is a counterexample to an overbroad inference, NOT a counterexample
to the rounded Gaussian matrices in the pinned package.

The needed sufficient hypothesis is that H and the inverse of every
eliminated principal set used by the WHOLE-GROUP order have polynomial
infinity norm in p, including the set after adding the next whole group.
Future interiors are included in each eliminated set. A required pivot
inverse is a principal block of that newly enlarged eliminated-set inverse.
The current Schur entries are bounded by H + H H_EE^-1 H. These facts bound
pivot inverses and factor pages polynomially. There are polynomially many
rows in a microbox; even a dense border row has polynomial total norm.
Consequently ||L|| and ||U|| are polynomial. Finally

    L^-1 = U S^-1,       U^-1 = S^-1 L

bounds the completed factor inverses polynomially too.

For narrow H, LOG-A-PHASE-SCHUR-AUDIT.md sections 2-3 gives strict row
diagonal dominance of the actual rounded H and shows elimination preserves
the row gap and nonincreasing row norm. This directly supplies the needed
principal/pivot bounds, conditional on its preceding Gaussian rounding bound.

For broad H, FORWARD-SMALL-A-AUDIT.md sections 1-3 provides a polynomial
inverse bound for finite contiguous selected Gaussian blocks and the square
identity-hole completion. CAPPED-GAUGE-AUDIT.md section 5 then adds the
essential geometry: after eliminating all interiors and a prefix of WHOLE
boundary groups, the eliminated physical set is one contiguous prefix plus
disjoint future interiors. Every remaining complete group has at least W
vertices and blocks connections across it. The newly enlarged set has the
same structure. A clipped short endpoint can be included in its neighboring
whole group as above. On a periodic line keep the wrap group until last;
before it is added the prefix does not cross that cut, and the final set
uses the separately bounded full periodic inverse. For a proper clipped
principal window the source's complement-gap premise excludes wrap edges.

Under selected/hole ordering, the physical prefix matrix has the form

    [ K  0 ; R_hole  I ].

K is the finite contiguous selected-source Gaussian block covered by the
inherited theorem, and the Gaussian lattice-sum estimate bounds R_hole.
Its inverse is [ K^-1  0 ; -R_hole K^-1  I ]. The other components are
the already controlled principal interior blocks. Thus the source supplies
an actual reduction to named analytic bounds, not just an appeal to
||S^-1||. This audit verifies the separation and block identities; the
all-size Gaussian inequalities, perturbation constants, and effective setup
are explicit inherited assumptions.

Eliminating a PART of a separator is unsafe for this argument. With W=2,
consider a width-2 path, an interior ending at vertex 2, separator {3,4},
and the next interior starting at 5. Eliminating vertex 3 creates the
eliminated path 2--3--5; eliminating vertex 4 creates 2--4--5. Either path
connects the two interiors across the one remaining separator vertex, so
the eliminated set is no longer the required contiguous prefix plus separate
future interiors. The test checks the second path explicitly.

## 6. Error and O(p)-bit records

Assume the polynomial factor/inverse bounds from section 5 and an effective
stable square product routine. Store factors to absolute precision eta,
small enough that their total row perturbations are below the reciprocal
polynomial inverse bounds. This needs O(log p) guard bits beyond the desired
per-stage accuracy because j,W are polynomial in p. Approximate pivot
inverse pages are included in the same local residual bound.

A forward substitution result y obeys Ly=b+delta_L. Every row's residual is
bounded by a polynomial in p times eta times (1+||b||+||y||), because it has
only the charged page products (a border row may have polynomially many).
Multiplication by L^-1, and absorption of the small eta||y|| term, bounds
both the computed solution and its error by polynomial multiples of the
input/error sizes. The same argument with U^-1 applies to the backward
solve. This uses a GLOBAL triangular residual, not a product of per-row
norm bounds raised to the number of boundary groups.

The fixed bilinear product's local error and intermediate growth are
polynomial in W, at fixed formula-dependent constants, as in
ALGEBRAIC-STABILITY-INDEPENDENT.md. For inputs of magnitude <=2^h, h=O(p),
working precision P+2h+O(log W) and O(h+log W) integer bits fit O(p) records
when P=O(p). Independent RHS do not add an R multiplier to infinity-norm
error. The source's later tensor composition and anchored-gauge guard remain
separate; this audit does not rederive their final rounding-to-integer claim.

Polynomial-time preparation of all pages once per complete microbox is
amortized by the superpolynomial common-factor RHS stock. This amortizes
SETUP only. The online page reads and resets have already been counted.
Exact rational inverses with unbounded numerator/denominator length do not
constitute this bounded-precision implementation.

## 7. Translation to bit volume

Let V=p L R denote an axis's tensor bit volume up to fixed record-width
constants. The arithmetic bound is

    O(V (e/L) W^(omega-2) [M(p)/p] polylog p).

With e/L=O((W/Bcap+W/L) polylog p), Bcap=O(L), and M(p)/p=polylog p,
one axis costs O(V W^(omega-1)/Bcap polylog p). Across d axes this is

    O(V (d/Bcap) W^(omega-1) polylog p).

The uncapped Bcap=d case reduces to O(V W^(omega-1) polylog p). The capped
factor d/Bcap must not be dropped. The matrix corollary substitutes its
assumed effective tau>omega_C for omega with the same page shapes and RHS
layout. Nothing here verifies the additional matrix exponent theorem.

The batch transposes and page traffic are O(eR polylog p) per axis and
therefore fit below this arithmetic term for omega>2. Existing union
extraction/merging, complete-tensor gathers/scatters, dense stages, and
coarse routing remain separately charged by the previous proof.

## 8. Independent finite checks and remaining boundary

The accompanying test is original local code. It compares blocked Strassen
products and forward/backward block solves against exact rational dense
oracles on carved nonperiodic and cyclic band matrices. It checks E\J
identity data, disconnected endpoint components, non-dyadic group sizes,
last incomplete batches, structural factor support, and per-batch page
reuse. Its separate tape primitive counts every record read/write/rewind
and verifies the 8n binary-pass identity and round-trip batch order.

The final run passed 48 layout cases and 8 rational algebra cases, with 622
page products and 53,998 scalar Strassen products. A separate independent
proof review found no blocker in the E/J, cyclic-frontier, tape, or
conditioning-reduction arguments. See RESULTS.json and REVIEW.md.

The factor algebra oracle uses host arrays and exact fractions, including
dense reference work to discover nonzero pages. Thus the checker's elapsed
runtime is not the claimed algorithmic complexity, and it does not
independently certify bit width or the arithmetic subroutine's physical
head schedule. Those are proved conditionally above. Conversely the tape
test is a literal record-head check, not a timing benchmark or asymptotic
proof. Finite rational cases do not certify actual Gaussian analytic bounds.

Scoped verdict: the next-interface layout/count argument closes under the
source's explicit whole-group prefix-conditioning and stable-product
interfaces. No new structural blocker was found in E/J support, batching,
page reuse, or factor frontier size. A source claim omitting prefix
conditioning or sufficient common-factor RHS stock would be false in that
generality. Stop here; no new exponent or further frontier is asserted.

## Sources and attribution

The upstream package credits Vlado Vojdanovski with substantial AI assistance.
The capped partition, sparse operator order, Gaussian bounds, and matrix
product hypotheses are its prior inputs. The present contribution is an
independent explicit page/stream interface audit and test, not priority for
those underlying constructions.

All source paths below are under research/capped-phase-fusion at the pin:

- PHASE-LAYOUT-AUDIT.md, bbeeee7431720817f031360f67b2186abac5cd23
- MATRIX-LAYOUT-SIGNOFF.md, d683e4d495330a2310e31b07c7dc896390334468
- CAPPED-INTERIORS.md, 62c3fa27b61a648c65c9e3f6fc4dc95d7b05bd3e
- CAPPED-GAUGE-AUDIT.md, a2d1c5ae923db7649627dbf419434e36267e57c6
- LOG-A-PHASE-SCHUR-AUDIT.md, 3bcf490a8c164d44aff5b7e2ec2e0f4bf07d7a73
- FORWARD-SMALL-A-AUDIT.md, 0f7f80b3f74d469c2f72f3b9f338d32568b4eae3
- ALGEBRAIC-STABILITY-INDEPENDENT.md, abdd30cc1d6df2c41b9e8fda76f27f85200bbf9b
- BILATERAL-LDU.md, 5cad6ee19f60d626beb9f6d7be78cbc22fdd08c6

Canonical source root:
https://github.com/Vlado-V/integer-mult-bounds/tree/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion
