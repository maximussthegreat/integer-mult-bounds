# Independent review of Gaussian physical-prefix audit

Date: 2026-10-14. Source pin under review: `2569871ff906d2a2abfc86e97126ab9afe2e4a5a`.

## Verdict

**PASS, conditional analytic scope.** The stated finite-to-physical-prefix argument is valid with the explicit width, complement-gap, exact-hole, and rounding assumptions. No counterexample to its finite inverse formulas, parameter estimates, or phase-cut reduction was found. This is not a certificate for the historical rounded coefficient tables, an implementation audit, or an integer-multiplication theorem.

The review identified an ambiguity in the initial truncation definition. The author corrected it before signoff: `M_W` now truncates each unwrapped physical displacement before periodization. Keeping all aliases in circularly near entries is a different convention, and the revised audit explicitly charges its additional tail. This correction matters for the literal no-alias claim and the factor-rounding construction; it does not obstruct the intended asymptotic lemma.

## Analytic checks

1. **Finite LDU and inverse formulas.** The shifted Newton basis begins at the interval's left endpoint. Direct Newton evaluation gives the stated diagonal pivots and lower factor; divided-difference inversion gives the lower-inverse expression. The upper inverse is the stated elementary-symmetric expression. Neither integrality of `q` nor a nonnegative origin is used. The two exponent envelopes follow from `|beta| <= 1/2`, with decay `b*rho*(rho-1)` per index distance. The lower, diagonal, and upper inverse bounds contribute respectively `c_b^-2`, `c_b^-1`, and `c_b^-1`, giving the stated `c_b^-4` product. No missing dimension factor was found.

2. **Small parameter and p-dependence.** The positive-term logarithm expansion gives `log(c_b^-1) <= pi^2/(12*b*rho)` for every `b>0`. At `b=pi/(alpha^2*rho^2)`, multiplication by four gives the stated exponential `exp(pi*alpha^2*rho/3)`. The inverse gap estimate is valid because `b*rho*theta<1`. The claimed conservative `p^(22/3)*(log p)^(5/2)` bound follows from `alpha^2 <= (8/pi)log(16p)+2`, `rho<=2`, and `theta^-1<=4p`. It is loose but sufficient and uniform.

3. **Phase cuts and holes.** Strictly increasing nearest-grid coordinates make the source indices selected by any lifted contiguous physical interval consecutive. This remains true across phase cuts and at hole endpoints. Simultaneous selected/hole ordering gives exactly `[K,0;R,I]`. The selected block has the correct column normalization `K=alpha^-1*G*diag(exp(-b*beta^2))`. The lattice-sum estimate supplies `||R||<=1+1/alpha`; therefore `B=1+(1+1/alpha)K_b` bounds the completed inverse. Empty selected sets are harmless. The argument does not apply merely by analogy to arbitrary masked coordinate sets.

4. **Cycles and tails.** Bilateral absolute row summability and simultaneous period invariance justify periodization of products and inverses; a full cycle is handled by that argument, not by finite-section convergence. For a proper lifted arc with at least `W` vertices in its complement, every nonzero physical image has displacement at least `W+1`. The corrected truncate-before-periodizing definition consequently has no retained alias inside that arc. Bounding the discarded positive coefficients by the integer physical lattice and then integrating yields the stated `T_W`. Its chosen width gives an exponentially small tail. A width upper bound alone would be insufficient, and the audit correctly says so.

5. **Rounding transfer.** With the same support and exact hole columns, principal restriction cannot increase the rounding row norm. The identity `Q_P=M_P(I+M_P^-1(Q_P-M_P))` proves the simultaneous `2B` inverse bound under `B(T_W+delta_round)<=1/2`; it needs no union bound over prefixes. Three downward-rounded nonnegative factors with diagonal magnitudes at most `exp(D)` have entry error at most `(2exp(D)+exp(2D))*2^-P`. At most `2W+1` selected coefficients occur in a row. Thus the advertised existential construction has exponentially small error at sufficiently large fixed `P=Cp`, since `D=o(p)`. This proves asymptotic attainability, not that an unexamined historical table meets the threshold.

6. **Whole-group geometry and direction.** Complete separators of at least `W` coordinates and a retained wrap border make eliminated components contiguous intervals plus future interiors. The relevant pivot inverse is a principal block of the enlarged eliminated-set inverse. The revised audit appropriately limits page-counting claims for complete factor norms to polynomial-size local windows; a superpolynomial full-cycle border row cannot be bounded just by counting polynomially bounded individual pages. The main proof's line 233 explicitly uses the broad Schur complement forward. Broad phase-interior inverses suffice for that direction. The actual boundary inverse uses the narrow rounded `H`, whose diagonal-one strict row dominance yields `||H_P^-1||<=16p` for every principal restriction. Broad prefix inversion is a sufficient extra interface, not a necessary missing hypothesis of that forward schedule.

## Independent controls and provenance

- Reviewed the local `EXACT_CHECK.py` before execution and replayed a copy in this review directory: 20 finite LDU/inverse cases and 5 physical completion cases passed.
- Authored `INDEPENDENT_CHECK.py` without importing upstream code. It builds the lower factor from Newton-basis evaluation, derives the upper factor by multiplication, independently inverts both, and checks the claimed inverse formulas and exponent envelopes. All **442** admissible four-index cases passed, using nonintegral real `q`, both beta endpoints, exact unit gaps, and origins -3 and 2. These finite checks corroborate algebra; they do not establish all-size bounds.
- All nine inert source files match the supplied manifest's byte lengths, SHA-256 values, and Git blob IDs. This checks the local manifest's consistency; the reviewer did not independently authenticate its remote commit association.
- No upstream program was executed. No external write or publication was made.

## Remaining limits and release wording

- Preserve the explicit threshold and the fact that it has not been measured or reconstructed for the exact fixed historical broad tables. Additional quotient formation and coefficient errors must be charged.
- The rounded result covers the stated physical components. It does not claim every proper cyclic arc with complement smaller than `W`, or arbitrary partial consumption of separators.
- `B` is the inverse bound for the unnormalized broad completion `M`. For the source's runtime normalization `M/4`, use `4B` before perturbation or `8B` after it. Dividing the corresponding perturbation by four leaves the stability product unchanged.
- No finite cutoff, shallow-circuit implementation, simultaneous tensor routing, tensor error accumulation, integer recovery, supplier, or final exponent was independently certified here.

Safe summary: “The ideal finite Gaussian argument and its uniform perturbation transfer check under the stated hypotheses. The actual source uses broad Schur application and narrow Schur inversion. No construction counterexample was found, and exact historical broad tables remain outside this audit.”

Reviewed-file hashes are recorded separately in `REVIEWED_HASHES.json` so the signoff applies to an immutable snapshot.
