# Sparse-union sequential schedule: independent finite experiment

Source pin: `CrocSwap/integer-mult-bounds`, PR #1673 head
`2569871ff906d2a2abfc86e97126ab9afe2e4a5a`.

## What this adds

This independently written checker implements the previously unexecuted
stream schedule: one union gather; repeated complete-rectangle extraction;
ordinal renaming; selected-field binary transposition; exact rational local
block application; inverse transposition; ordered replacement; and one
scatter. It also executes two sparse windows separated by a full dense
interior stage. No upstream program is imported or executed. Pinned source
copies are inert `.txt` files and are listed in `SOURCES.json`.

The upstream `check_union.py` uses dictionaries. Its consecutive C and
S-inverse calls each gather and scatter despite metadata claiming one
shared gather. That algebraic implementation does not establish the
literal two-window schedule. The present traces count the actual gathers
and scatters and retain the same union between consecutive sparse sweeps.

## Scope and execution model

This is a finite exact algebra and sequential **record-tape** experiment.
It is not a certified bit-machine implementation or an all-size complexity
proof. The accompanying proof document gives a conditional movement lemma.

Eight tape lanes are reserved. Payload movement is through `Tape.read`,
`Tape.write`, and `Tape.rewind`; no arbitrary payload seek, coordinate-key
sort, or random-access update appears in the schedule. Python lists emulate
the tape cells, so their host indexing is an implementation device. Every
emulated read/write advances one record; every rewind charges the actual
traversed record distance. Live end markers prevent reads of stale tails.

Headers, membership descriptors, dimensions, end markers, and loop counters
are Python control data. Their bit-level encoding, bit comparisons, and
uniform arithmetic costs are not measured by record-head counters. In
particular tuple membership and tuple equality are host operations, not
unit-cost bit-machine claims. The exact reference uses dictionaries and
direct tensor entries; it is deliberately separate from the schedule.

A symbolic payload carries all basis columns together as an exact rational
coefficient vector. Thus a count of one moved record represents one
symbolic coefficient record, not one bit or one ordinary scalar coefficient
of constant width. Symbolic rational arithmetic and its storage are an
algebraic verification oracle. The arithmetic phase separately counts
coefficient reads, payload reads/writes/rewinds, and scalar products.

Scratch tapes may be overwritten. Arbitrary original contents of scratch
storage are **not restored**. Real input records, including arbitrary
spectator values, are preserved by layout operations. Padded records carry
nonzero opaque `DIRTY` tags and are removed before arithmetic; they are
never substituted for missing real coordinates. These tags test padding
isolation, not dirty-ancilla restoration. The pinned retained tape supplier
explicitly uses two work tapes, rewinds them, and reuses them per prefix;
this is the ordinary reusable-scratch contract used here.

## Schedule and exact record movement

For an axis with `e=|E_i|`, let `N_i=|U_i|`, `P` be the preceding-fiber
count, and `S` the following-spectator count. Extraction scans U and emits
all `P e S` records. Its ordinal advances only when the selected coordinate
changes, and resets when the preceding prefix changes.

For `e>1` and `S>1`, set `q=2^ceil(log2 e)` and `k=log2 q`. Pad only this
field, so `N_q=P q S<2N_i` for non-dyadic e. Moving the rightmost remaining
field bit first maintains

`[P][remaining high bits][S][already moved low bits]`.

Pass r swaps `[P q/2^(r+1)][2][S][2^r]` to
`[P q/2^(r+1)][S][2][2^r]` using two work tapes. The inverse reverses the
same passes. Each literal binary pass costs exactly `8 N_q` record-head
steps: `4 N_q` forward read/write steps and `4 N_q` backward rewind steps.
This equality is asserted in every executed pass, including per-prefix
resets and source/output restoration. The long spectator field is never
padded, sorted, or moved bit by bit. The `e<=1` and `S=1` cases need no
transpose.

A transpose plus inverse, including padding and removal, uses
`8(N_i+N_q)+16 k N_q` head steps. Extraction and ordered replacement add
`6|U|+4N_i` steps. Hence, excluding local arithmetic and the outer full
scans, one sparse sweep has the record-movement bound

`O(g |U| + sum_i N_i (1+log |E_i|))`.

One outer gather plus scatter costs exactly `6V+4|U|` record-head steps in
this implementation. These full scans are separate from per-window work.
The naive arbitrary e-by-e rational block replay costs `e N_i` coefficient
reads and `2(e+3)N_i` payload head steps. This cost is explicitly outside
the layout-only bound; arbitrary dense local arithmetic is not declared
free. No Strassen/RHS-batching arithmetic claim is tested here.

## Reproduce

Run with the standard Python library only:

```
python sequential_union.py
python test_transpose_controls.py
python test_failure_controls.py
```

The first command stops on a discrepancy, otherwise writes `RESULTS.json`.
Its exhaustive grid enumerates every subset E_i for L=2,3,4 and g=1,2,3,
with two consecutive rational sweeps: a strictly diagonally dominant
invertible block and a singular block (rank at most one for e>=2; zero
for e=1). Exact reference checks after both sweeps prevent a later singular
map from hiding an earlier invertible-stage error. A separate zero-block
case checks that actual zero-valued records remain present. All input basis
columns are tested simultaneously by exact rational coefficient vectors.

Supplemental cases use prefix/suffix cardinalities (1,3), (3,1), (2,3),
and (3,2), with non-dyadic middle fields and overlapping supports. These
are finite spectator tests; the all-size spectator claim belongs to the
written conditional proof, not finite enumeration.

The second command tests 72 pure selected-field permutations and inverse
round trips with arbitrary opaque, nonzero real-record payloads:
P=1,2,3; e=1,2,3,4,5,7; S=1,2,3,5. It writes
`TRANSPOSE-CONTROLS.json`.

The dense-interlude case has L=3, g=1, boundary J={0}, interior I={1,2},
and E={0,1}. The dense interior matrix fixes J but sends the basis vector
at coordinate 1 to coordinates 1 and 2. The intentionally wrong schedule
that retains U and truncates the dense matrix is actually executed and
must disagree at coordinate 2. The correct trace must contain exactly two
gathers and two scatters, with two sparse stages sharing the first window.

`Vec.equal` rejects mismatched vector widths. The main test includes both
truncation and extension rejection controls, and verifies complete output
lengths before row-by-row comparisons. `test_failure_controls.py` adds six
expected-rejection controls: truncated/extended symbolic vectors; missing,
duplicated, and reversed real zero records; and padding admitted to local
arithmetic. The malformed-stream controls confirm that zeros are still
records, and cannot be silently omitted.

## Boundaries

No counterexample to this finite sparse-union layout is claimed. This
artifact does not prove Gaussian conditioning, phase factor generation,
precision, the separate support-router theorem, efficient boundary
arithmetic, a multiplication exponent, or the whole candidate theorem.
It does not publish, modify, merge, or execute the upstream repository.
