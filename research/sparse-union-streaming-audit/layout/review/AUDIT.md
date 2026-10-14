# Independent review: sparse-union sequential schedule

Date: 2026-10-14. Verdict: **PASS within the stated record-tape and conditional
movement-lemma scope.** No schedule counterexample or unresolved blocking issue
was found. This is AI-assisted review and exact testing, not independent human
peer review, proof-assistant verification, or a new multiplication result.

## Reviewed artifacts and exact binding

- Authored simulator `sequential_union.py`: SHA-256
  `3aa055a62d9cedd9908830c2f03d20677a4f1b1cb4163d7d58b06be103e6c8e5`.
  A byte-identical snapshot is `AUTHORED-SIMULATOR-REPAIRED.py` here.
- Written lemma: SHA-256
  `be8e5cb47e1c07d86903fe91bb4d2a0d1bed59caecffff8593368a08c5dd84de`.
  A byte-identical snapshot is `REVIEWED-PROOF.md` here.
- Mathematical predecessor: PR1673,
  `2569871ff906d2a2abfc86e97126ab9afe2e4a5a`, especially
  `research/capped-phase-fusion/PHASE-LAYOUT-AUDIT.md` and
  `evidence/independent_fusion_review_ultra/union_subreview.md`.
  The latter explicitly identifies the predecessor's missing sequential
  counter/transpose/merge/batching execution evidence. No predecessor program
  was imported or executed during this review.

## Fixed finding

The first reviewed simulator's coefficient-vector comparator zipped two
vectors without checking their lengths. Thus `[1]` compared equal to `[1,2]`.
Normal schedule execution preserved vector lengths, so this was a verification
weakness rather than a demonstrated incorrect tensor operation.

The author added explicit equal-width checks, both truncation/extension
regressions, and complete output-length checks. I inspected and independently
tested the repair. The known-weak initial snapshot is excluded from the
release; every default review command uses the repaired snapshot.

## Independent executed evidence

All three reviewer programs use Python's standard library and execute only
the new authored simulator after static inspection.

1. `independent_review.py`: 297 opaque-payload transpose and inverse-round-trip
   cases, covering P=1,2,3; e=1,...,9; S=1,...,11. All 1,260 binary passes
   satisfy the exact eight-times-record-count head-movement assertion.
   Existing work-tape cells were filled with unrelated dirt before execution.
   Outputs remain correct; initial work-tape contents are deliberately not
   restored. Thirty-three additional custom rational-operator cases check
   940 basis columns using the candidate's separate tensor reference harness.
   Four injected schedule faults reject: wrong ordinal, missing rectangle
   record, omitted transpose, and corrupted merge key. The repaired vector
   width guard and the executed dense-interlude control pass.
2. `direct_scalar_audit.py`: a separately implemented dense scalar oracle
   checks 20 deterministic rational-input cases through three sparse sweeps.
   It compares 4,614 union records after individual axis operations. This
   oracle does not call the candidate's tensor-reference, extraction, ordinal,
   transpose or merge helpers. It does call the candidate scheduler being
   tested. The cases include g=4, non-dyadic fields, signed coefficients and
   prefix/suffix spectators. Peak live payload-tape count was six.
3. `cost_audit.py`: independently derived exact formulas agree with the actual
   phase counters on six cases, including an empty union, singleton support,
   non-dyadic fields, complete supports, higher-dimensional tensors and
   spectators. Movement and arithmetic are checked separately.

Receipts are `INDEPENDENT-RESULT.json`, `DIRECT-SCALAR-RESULT.json`, and
`COST-RESULT.json`. These checks supplement the author's larger exhaustive
replay; they do not claim an independently repeated 5,036-case census.

## Exact movement accounting

Let N be the number of full records, u the union size, n_i a selected rectangle
size, e its selected-field length, q its next dyadic size, k=log2(q), and
n_q the padded rectangle size. Heads start and end at the origin.

- One gather and one scatter: `6N + 4u` record-head steps.
- One extraction and ordered replacement: `6u + 4n_i` steps.
- A transpose/inverse pair, including padding/removal when e>1 and the
  following spectator count exceeds one: `8(n_i+n_q) + 16k n_q` steps.
- The naive e-by-e local arithmetic implementation separately uses
  `e n_i` coefficient reads and `2(e+3)n_i` payload head steps.

Initial input construction and independent reference/checkpoint reads are
separate verification activities. Header and symbolic-arithmetic operations
are not priced as unit-cost bits by these counters.

## Written proof review

The closure argument uses exactly the necessary premise: each sparse factor
is identity off its fixed E_i and has no cross-coupling to that complement.
Completeness of U_i then supports extraction even when every other axis is
outside its boundary set. Singular rational local blocks cause no algebraic
problem. All sparse updates retain real zero-valued records.

The split/interleave operation moves one binary field across an arbitrary
spectator in one full pass, including work-tape and source/output rewinds.
Moving selected bits rightmost first preserves their order. Inverse passes
reverse that order. Only the selected field is padded, by a factor below two;
dummy records are excluded from arithmetic. The argument gives
`O(g u + sum_i n_i log L)` inner movement and a separate `O(N)` gather/scatter
term. It extends to fixed numbers of sweeps without assuming g mu < 1.

The header/membership cost is now explicit. Header width includes external
prefix/suffix counter widths. Increasing support lists or bitmaps are required
for the displayed setup bound; unordered sorting and analytic support
generation remain separately charged. A single concatenated bitmap tape with
a lexicographic odometer needs O(N) descriptor movement: a j-coordinate carry
costs O((j+1)L), occurs at most N/L^j times, and the geometric sum is O(N).
Copying flags/counters costs O(g log L) per record. This is a written
construction, not an implemented part of the finite payload simulator.

The resulting bit statement is conditional on bounded payload/header widths,
with factor `w+h`. The candidate application separately needs h=O(p), bounded
precision and actual total bit volume. The capped substitution retains the
W/L endpoint term until B=O(L) justifies absorbing it. The local matrix oracle
and its coefficient traffic are never included for free in the movement bound.

## Important scope boundaries

- Ordinary scratch tapes are overwriteable. The work does not restore
  arbitrary original scratch contents or prove a reversible dirty-ancilla
  implementation. Arbitrary real input and spectator data is handled.
- The simulator uses host Python metadata and exact symbolic vectors.
  It is not a literal bounded-width bit-Turing-machine implementation.
- Sequential scalar block replay does not implement the fast RHS-batched
  boundary algorithm. Its work is intentionally charged separately.
- Two actual sparse windows are observed around a dense interior operation.
  Truncating that dense operation to the old union gives an exact failing
  control. This corrects an execution-evidence limitation, not an asymptotic
  counterexample to PR1673.
- Gaussian conditioning, factor generation, support-local routing,
  bounded-precision stability, all-size supplier realization and the complete
  multiplication theorem remain outside this result. No new kappa follows.

No external repository was changed by this review. The next valuable
integration would bind the actual bounded-precision boundary line/batch
routine, support/factor preparation and complete-box router to this same
record-width and scratch-tape contract.

## Reproduce this review

Run in this directory:

```
python3 -B independent_review.py
python3 -B direct_scalar_audit.py
python3 -B cost_audit.py
```

All inputs and outputs resolve relative to each script's own directory;
the commands also work when launched from an unrelated current directory.
