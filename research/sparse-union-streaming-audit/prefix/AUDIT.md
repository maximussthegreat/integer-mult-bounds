# Gaussian physical-prefix conditioning: scoped analytic validation

Date: 2026-10-14. Source fork: Vlado-V/integer-mult-bounds.
Upstream: CrocSwap/integer-mult-bounds. These are distinct repositories.
Source pin for upstream PR #1673:
`2569871ff906d2a2abfc86e97126ab9afe2e4a5a`.

## Result first

The finite Gaussian LDU argument does cover the ideal selected blocks inside
arbitrary contiguous physical prefixes, including prefixes crossing phase
cuts. Identity-hole completion preserves a uniform polynomial inverse bound.
A single explicit row-error threshold transfers this result to every rounded
prefix at once. Below we prove that statement, including its cyclic alias
condition, and show why the source's bandwidth and precision scales can meet
it uniformly.

This is a **scoped validation**, not a counterexample or a new exponent proof.
The exact fixed broad coefficient tables and their final numerical constants
were not independently reconstructed. A claim about one such particular
rounded table must still show the row-error inequality in section 5. The
source's existential instruction to use sufficiently accurate rounding is
compatible with that inequality; lack of a table-specific certificate is not
evidence that the analytic implication is false or absent.

There is also an important direction correction. The pinned main proof,
`phase_fusion_note.tex:225-239`, explicitly applies the broad Schur matrix
forward and does **not** require its inverse or broad LU-prefix bounds. The
actual boundary solve is for the narrow operator, whose rounded principal
blocks are controlled by strict row dominance. Thus the stronger broad
inverse interface in the preceding independent RHS audit is not an additional
necessary hypothesis of the published forward-only schedule.

## 1. Source-to-hypothesis map

All line references are at the stated immutable pin, under
`research/capped-phase-fusion/`.

| Required statement | Source and actual hypotheses | Finding |
|---|---|---|
| Finite contiguous Gaussian inverse | `BILATERAL-LDU.md:25-79`: a finite consecutive integer index interval; increasing q with successive gaps at least one; beta_i=rho*i-q_i in [-1/2,1/2); positive parameter; rho=1+theta>1 | Its finite Newton factors and inverse estimates are uniform in both interval endpoints and length. The last numerical simplification needs parameter >=1; the factor/inverse proof does not. |
| Small positive Gaussian parameter | `FORWARD-SMALL-A-AUDIT.md:13-33`: b=pi/(alpha^2 rho^2), alpha>=2, 0<theta<=1 | The infinite product estimate gives an explicit polynomial bound when alpha^2=O(log p) and theta^-1=poly(p). |
| Selected block within a phase | `FORWARD-SMALL-A-AUDIT.md:35-55` | Correct. One can also avoid its auxiliary nonintegral q' by relabeling physical selected coordinates with their original consecutive source indices, as below. |
| Identity-hole completion | `FORWARD-SMALL-A-AUDIT.md:57-73` | Exact block identity. The Gaussian lattice sum supplies a dimension-free bound for the lower-left block. |
| Whole-group physical geometry | `CAPPED-GAUGE-AUDIT.md:105-119` | Needs exact width-W support, remaining separators of at least W vertices, a retained wrap border, and the stated complement gap for clipped windows. Under these conditions the eliminated principal matrix is a direct sum of one contiguous prefix and future interiors. |
| Rounded operator | `FORWARD-SMALL-A-AUDIT.md:67`, `phase_fusion_note.tex:203,219,279-285` | States exponentially small truncation/structure-preserving rounding and sufficiently large Cp precision. Section 5 below makes the needed uniform row-error threshold explicit; it is attainable at those asymptotic scales. |
| Narrow solve | `LOG-A-PHASE-SCHUR-AUDIT.md:46-81` | Specifies the actual rounded H, a concrete perturbation allowance, positive diagonal 1, row gap >=1/(16p), norm <2. Every principal block inherits the gap, including cyclic/clipped ones. |
| Actual operator direction | `phase_fusion_note.tex:227-233` | Broad Q uses its Schur complement F as a matrix application. Only narrow Q^-1 needs F^-1. Broad prefix inversion is a stronger optional interface. |

The supplied source files are inert text. No upstream program was executed.

## 2. Finite inverse lemma, with the precise parameter dependence

Use the induced infinity norm. Fix rho=1+theta in (1,2], b>0, and any finite
consecutive integer interval J. Let q_i be real numbers satisfying

    q_(i+1)-q_i >= 1,
    beta_i = rho*i-q_i in [-1/2,1/2].

Set

    G_ij = exp(-b*((rho*j-q_i)^2-beta_j^2)),
    c_b = product_(m>=1) (1-exp(-2*b*rho*m)),
    Q_b = c_b^-4 * exp(b/2) / (1-exp(-b*rho*theta))^2.

Then G_J is invertible and ||G_J^-1|| <= Q_b, independently of the location
and length of J.

Here is the finite proof obligation rather than a citation-only invocation.
Let l be J's left endpoint, x_i=exp(2*b*rho*q_i), and
v_i=exp(-b*rho^2*i^2+b*beta_i^2). Newton interpolation gives G=L C U, with
unit triangular L,U and

    C_i = product_(l<=k<i) (1-x_k/x_i).

The source's displayed finite inverse formulas give

    |Linv_ij| <= c_b^-2 exp(b/4) exp(-b*rho*theta*(i-j)), i>=j,
    |Uinv_ij| <= c_b^-1 exp(b/4) exp(-b*rho*theta*(j-i)), j>=i.

For the lower factor the controlling exponent is

    b*(-beta_i^2+beta_j^2-rho^2*(i-j)
       +2*rho*sum_(j<k<=i) beta_k)
    <= b/4-b*rho*theta*(i-j).

For the upper factor, after its elementary-symmetric polynomial is divided
by the product of its largest nodes, the exponent is

    b*(beta_j^2-beta_i^2-rho^2*(j-i)
       -2*rho*sum_(i<=k<j) beta_k)
    <= b/4-b*rho*theta*(j-i).

The normalized symmetric-polynomial sums are bounded by c_b^-1: node ratios
are at most exp(-2*b*rho*distance), and the index deficits enumerate
partitions. Also c_b<=C_i<=1. Summing the two geometric envelopes and using
G^-1=Uinv C^-1 Linv proves Q_b. Every step works for b>0. No right-endpoint,
phase-length, integrality-of-q, or interval-origin constant is introduced.
The finite proof suffices here; no finite-section convergence assertion is
needed.

The product is strictly positive for each b>0 because its omitted logarithms
are summable. The nonnegative power-series expansion gives

    log(c_b^-1)
      = sum_(h>=1) 1/[h*(exp(2*b*rho*h)-1)]
      <= pi^2/(12*b*rho).

Consequently, at b=pi/(alpha^2*rho^2),

    c_b^-4 <= exp(pi*alpha^2*rho/3).

Since x=b*rho*theta<1 for alpha>=2, 1-exp(-x)>=x/2. Define

    K_b = alpha*exp(3*b/4)*c_b^-4 / (1-exp(-b*rho*theta))^2.

Then

    K_b <= (4/pi^2)*alpha^5*rho^2*theta^-2
           *exp(3*b/4+pi*alpha^2*rho/3).

This is the bound needed for the unnormalized selected broad block.

For the source's actual alpha=ceil(sqrt((4/pi)*log(16p))) and d<=p eventually,
alpha^2 <= (8/pi)*log(16p)+2 and theta^-1<=4d<=4p. A conservative consequence
is K_b <= C*p^(22/3)*(log p)^(5/2), with one absolute eventual constant C.
In particular K_b is polynomial uniformly over every axis, period, cell,
source origin, prefix length, and dyadic cap. No fixed-alpha assumption is
being used in this growing-alpha conclusion.

## 3. Every ideal physical interval, including phase cuts and holes

Lift the physical target grid to the integers. Let

    q_j = floor(rho*j+1/2), beta_j=rho*j-q_j.

For any consecutive physical interval P=[u,v], let

    J = {j : q_j in P},
    H = P minus {q_j : j in J}.

Monotonicity and injectivity of q make J a consecutive source interval,
possibly empty. This remains true when P begins or ends at a hole or crosses
many phase changes. It does not require q_j-j to be constant on P.

Define the ideal unwrapped square broad completion M_P: its selected column
q_j has row-k entry

    alpha^-1 exp(-b0*(j-k/rho)^2), b0=pi/alpha^2,

and a hole column h has entry 1 at row h and zero elsewhere. Reorder rows and
columns together, selected q_j first in increasing source order, then holes.
Exactly,

    M_P = [ K_J  0 ; R_P  I ],
    K_J = alpha^-1 G_J diag(exp(-b*beta_j^2)).

Thus ||K_J^-1||<=K_b from section 2. This direct original-source labeling also
proves the phase-interior case; the auxiliary q'_k of the source is optional.

For every shift z, the elementary Gaussian lattice bound is

    sum_(j in Z) exp(-pi*(j-z)^2/alpha^2) <= 1+alpha.

For example, layer-cake integration counts at most 1+2r integer points in
an interval of radius r and gives this bound exactly. Deleting source columns
only decreases the positive row sum, so ||R_P||<=r_alpha:=1+1/alpha.
Consequently

    M_P^-1 = [ K_J^-1  0 ; -R_P K_J^-1  I ],
    ||M_P^-1|| <= B := 1+r_alpha*K_b,
    ||M_P|| <= 2+1/alpha.

If J is empty, M_P=I and the same upper bounds hold. These are independent
of all interval endpoints and sizes. Phase cuts therefore cause no missing
analytic implication. They affect the Toeplitz circuit partition, not this
completed-matrix inverse bound.

## 4. Cyclic aliases and clipping: what must be checked

For a full periodic line, q_(j+s)=q_j+t and beta_(j+s)=beta_j. The source's
periodization argument is valid for b>0: all factors and inverses have bounded
absolute row sums, their products can be rearranged absolutely, and
Pi(A B)=Pi(A) Pi(B). The full periodic normalized Gaussian inverse therefore
has the same Q_b bound. Its identity-hole completion has the same B bound.
This is the bound used for the final wrap group; it is not inferred from a
nonperiodic finite section.

For a proper contiguous arc P in a t-cycle, choose one lift of P. Suppose
its complement contains at least W physical vertices. Any nonzero alias
between two coordinates in that lifted P then has physical displacement
at least W+1. Thus a physical width-W truncation has no such alias inside P.
This condition is why a proper interval is not, merely by being proper,
automatically a nonperiodic block.

There is also a quantitative comparison with the ideal unwrapped Gaussian.
For a selected coordinate q_j and a physical row k,

    j-k/rho = (q_j-k+beta_j)/rho,
    |j-k/rho| >= (|q_j-k|-1/2)/rho.

There is at most one selected q_j at each integer target position. For W>=1,
the two-sided discarded physical tail is bounded by

    T_W := exp(-b*(W-1/2)^2) / [alpha*b*(W-1/2)].

Indeed the discarded row sum is at most
(2/alpha)*sum_(r>=W+1) exp(-b*(r-1/2)^2), and monotonicity followed by the
Gaussian tail integral gives T_W. The same proof handles aliased source
images on the cycle, including nonzero diagonal aliases.

Choosing

    W >= ceil(1/2+sqrt(K*p/b))

for one fixed positive K makes

    T_W <= 2*exp(-K*p)/sqrt(pi*K*p).

This is W=O(sqrt(p)*alpha), within the quoted broad bandwidth. A mere upper
bound W=O(sqrt(p) polylog p), by itself, would not imply a small tail; the
retained truncation must be chosen with a sufficient lower constant too.

For the source's polynomial-size cores and halo intervals, true t eventually
exceeds every fixed polynomial in p. Thus their complement-gap condition is
eventually automatic. A window crossing the true period cut is lifted as a
single arc; its selected source indices are lifted together. The original
cut stays in the retained boundary. It must not be treated as an extra
disconnected Gaussian block if retained coefficients cross that cut.

## 5. One explicit uniform rounded-prefix lemma

Define M_W by **truncating each unwrapped physical Gaussian displacement
before periodizing**: in row k and selected residue-column q_j, retain only
images j+n*s for which |q_j+n*t-k|<=W. Then sum those retained images.
Hole columns remain exact identity columns. This convention removes the
long aliases themselves, even from near residue entries; it is stronger than
merely masking entries by circular distance. With t>2W there is at most one
retained image per entry. Let the one globally fixed rounded matrix Q have
the same support and satisfy

    ||Q-M_W|| <= delta_round.

Assume W<t/2 eventually and that every proper physical component under
consideration has complement gap at least W. If

    eta := T_W + delta_round,
    B*eta <= 1/2,                                      (R)

then **every** such rounded physical component Q_P is invertible, with

    ||Q_P^-1|| <= 2B,
    ||Q_P|| <= 2+1/alpha+eta.

For a proper component, width-W truncation has no alias inside the chosen
lift, so ||Q_P-M_P||<=eta. For the full periodic component the same bound
holds against the full periodic ideal completion. Apply

    Q_P = M_P*(I+M_P^-1*(Q_P-M_P))

and the norm-convergent Neumann series. Principal restriction never increases
the rounding-error row norm. There is no union bound over prefixes, and no
factor equal to the number of pieces, origins, or Gaussian axes.

If a different truncation convention keeps all aliases in near circular
entries, its difference from the M_W just defined is at most T_W in row norm.
Charge that difference inside delta_round, or replace eta by
2*T_W+delta_coefficient. It must not be silently identified with this M_W.

This is the exact missing *displayed interface* if a table-specific broad
prefix certificate is desired. It is not an absent mathematical mechanism:
it follows directly from the named finite bound and the source's declared
uniform small perturbation. The main forward-only schedule does not need
the broad prefix conclusion in the first place.

### Why the claimed coefficient scale can satisfy (R)

One compatible structure-preserving construction uses a fixed original-phase
anchor, the displayed Drow G Dcol factorization in each original selected
cell, directly rounded retained entries across phase cuts, and exact identity
hole columns. All choices are global and made before carving.

Let every ideal original-cell diagonal factor have magnitude at most exp(D),
where D=O(d/alpha^2+log alpha), uniformly in the original phase and its origin.
The source's derivative estimates and a selected anchor prove that bound;
using the more conservative D=O(a*d) is also sufficient. In either case D=o(p).
The ideal Gaussian Toeplitz coefficients have magnitude at most 1.

Round each of those three nonnegative factors downward to absolute error
<=2^-P. A telescoping product gives per-retained-entry error at most

    (2*exp(D)+exp(2D))*2^-P <= 3*exp(2D)*2^-P.

The directly rounded cross-cell entries have no larger error. A physical
row has at most 2W+1 retained selected coefficients, hence

    delta_round <= 3*(2W+1)*exp(2D)*2^-P.

Since log W=O(log p) and D=o(p), any sufficiently large fixed P=Cp makes
this exponentially small. Combined with the explicit width above and the
polynomial B, (R) holds for all sufficiently large p with constants uniform
across phases, cores and axes. Small p can be excluded by the source's fixed
finite fallback. If a retained table uses rational quotients or additional
coefficient rounding, those errors must be included in delta_round; the same
threshold then applies.

This construction explains the asymptotic sufficiency of the source's
rounding assertion. It is not a claim to have reproduced the exact historical
broad table or to have replaced its already-fixed coefficients. The theorem
applies to that fixed table once its stated error bound is verified.

### Gauges do not create a new inverse hypothesis

Exact recentering divides one already-rounded diagonal by a nonzero constant
and multiplies its companion by that same constant. Their product, hence Q
and every Q_P, is unchanged. The prefix bound therefore uses no product of
large gauge norms. Approximate ratio formation contributes ordinary setup
error and must be included in delta_round or the online coefficient residual,
rather than silently redefining Q for each prefix.

### The runtime factor of four

B is the bound for the unnormalized completion M. The source runs its broad
map as M/4. Its ideal inverse bound is 4B, and the rounded bound for Q/4 is
8B under (R). The perturbation is divided by four as well, so the stability
product (4B)*(eta/4)=B*eta and the sufficient precision threshold are
unchanged. This fixed normalization does not change polynomial uniformity.

## 6. Whole-group elimination and the actual narrow solve

Under the stated width-W support and complete-separator rule, eliminating all
interiors and then successive whole boundary groups yields a physical prefix
plus disconnected future interiors. Each component is one of the intervals
covered above. Before the cyclic border is added it contains at least W
uneliminated vertices; when it is added use the full periodic bound. Therefore
(R) implies a uniform bound 2B on each eliminated-set inverse. A direct sum's
infinity norm is a maximum, not a sum over components.

After adding the next whole group, the pivot inverse is the corresponding
principal block of that newly enlarged eliminated-set inverse. Current Schur
entries are bounded by Q+Q Q_EE^-1 Q. This proves polynomial broad block pivot
inverse and individual factor-page bounds for the stronger symmetric solve
interface, without scalar pivoting inside a group. Completed factor row norms
then remain polynomial on the actual polynomial-size local windows, where
the number of pages is polynomial. We do not infer a uniform row norm for a
dense cyclic-border factor of one sequential LU across an entire
superpolynomial global period merely by counting bounded pages. The preceding independent RHS audit already checked
the block algebra and tape consequences; this note supplies its analytic
finite-to-physical-prefix implication under (R).

The source's actual inverse direction is simpler. Its narrow globally rounded
H has diagonal 1 and off-diagonal row sum <=1-1/(16p). Every principal
restriction inherits the same margin, even an arbitrary restriction with
wrap edges. Thus its inverse norm is <=16p by the elementary Neumann bound.
The target-grid identity-hole completion is permutation-similar to H direct
sum I. No broad theorem or complement-gap argument is needed for this narrow
conditioning statement. Whole-group elimination is still helpful for the
factor support and batching geometry.

The source obtains the narrow margin from the explicit rounded error bound

    ||H-N|| < 1/(16p),

following an ideal gap at least 1/(8p), with actual diagonal set to one. Its
retained allowance p*2^(16p+7)*eta0+2^(-46p), eta0=2^(-32768p), is far below
that threshold. This audit checks the implication of that bound, not an
independent reimplementation of its coefficient generator.

For broad Q itself, the forward identity needs A^-1 only on phase interiors
and the application F=D-C A^-1 B. The bound on F follows from bounded Q and
those interior inverses. A broad F^-1 or broad sequential LU solve need never
be constructed. Therefore a future failure to certify broad prefix tables
would not alone refute that forward schedule.

## 7. Independent finite controls and stopping boundary

`EXACT_CHECK.py` is original local code using only Python's exact fractions.
It imports and executes no upstream code. It checks 20 finite LDU identities
and both triangular inverse formulas, including negative origins, endpoint
rounding ties and phase changes. Its small positive parameter is represented
by b=16 log(257/256), so all Gaussian values are exact rational powers. Five
physical-window cases check the exact selected/hole reordering and the full
block inverse identity, including windows spanning phase cuts.

The all-size conclusions above come from the displayed inequalities, not from
those finite cases. They do not certify finite cutoff, exact upstream rounding
tables, the shallow-circuit implementation, tensor error accumulation, final
integer recovery, or any final multiplication exponent.

Scoped verdict: no missing phase-cut, hole, finite-size, gauge, or period
hypothesis was found beyond the explicitly stated width/support,
complement-gap, and rounding threshold. The source's finite Gaussian theorem
is mathematically adequate for the intended physical-prefix reduction, and
its asymptotic precision scales can meet the needed threshold. The stronger
broad inverse interface is optional for the pinned main forward schedule.
Stop here rather than expand into an unrelated theorem search.

## Canonical source links

- [Finite Gaussian LDU](https://github.com/Vlado-V/integer-mult-bounds/blob/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion/BILATERAL-LDU.md)
- [Broad finite and completed matrices](https://github.com/Vlado-V/integer-mult-bounds/blob/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion/FORWARD-SMALL-A-AUDIT.md)
- [Whole-group order and gauges](https://github.com/Vlado-V/integer-mult-bounds/blob/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md)
- [Actual rounded narrow operator](https://github.com/Vlado-V/integer-mult-bounds/blob/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md)
- [Main proof and operator direction](https://github.com/Vlado-V/integer-mult-bounds/blob/2569871ff906d2a2abfc86e97126ab9afe2e4a5a/research/capped-phase-fusion/phase_fusion_note.tex#L225-L239)

The upstream package credits Vlado Vojdanovski with substantial AI assistance.
Its Gaussian factorization, rounding framework, partition, and operator
schedule are prior inputs. This note independently audits their hypotheses
and supplies an explicit uniform prefix-transfer threshold; it makes no
priority claim for those underlying constructions.
