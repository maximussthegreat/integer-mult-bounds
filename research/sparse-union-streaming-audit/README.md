# Explicit sparse-union streaming and boundary-interface audit

**Scoped verification supplement; no new exponent claim.** Prepared 14 October 2026 by Dr. Maksym Kitsera with substantial OpenAI ChatGPT assistance in research, implementation, proof drafting and adversarial checking. The internal independent checks are AI-assisted checks, not independent human peer review or proof-assistant verification.

## Result

This package supplies an explicit sequential record-tape construction and finite checks for the sparse-union layout proposed in PR #1673. It separates record movement, arithmetic, coefficient traffic, and analytic precision assumptions.

- The layout uses a fixed tape set and charges reads, writes, rewinds, selected-field padding, transposition and ordered replacement. Inner movement is O(g|U| + sum_i |U_i| log L); gathering/scattering adds O(L^g).
- The executable census checks all 5,036 support tuples for L=2,3,4 and g=1,2,3, with 281,312 exact basis columns. Additional independent scalar, corruption and movement checks are included.
- The RHS supplement checks the E-versus-J distinction, local panel geometry, batching, and Schur solves. Its 48 tape-layout and 8 small exact rational algebra cases do not constitute a complete arithmetic tape compiler.
- The analytic addendum distinguishes the actual broad-forward/narrow-inverse schedule from an optional stronger broad-inverse interface. Read prefix/RELATION_TO_PRIOR_AUDIT.md before interpreting the RHS audit's conditioning discussion.

## Sources and attribution

The predecessor is Vlado Vojdanovski's capped-phase-fusion work, PR #1673, pinned to `2569871ff906d2a2abfc86e97126ab9afe2e4a5a`. Its sparse-union decomposition, selected-field transpose and inherited routing constructions remain credited to their original authors. This package adds explicit replay and interface audits; it does not claim those underlying ideas as new.

https://github.com/CrocSwap/integer-mult-bounds/pull/1673

Source manifests in each section record exact source paths and hashes. No upstream program was imported or executed. The package is based on main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; it does not alter the selected result or frozen predecessor sources. All new code uses Python's standard library. New contributions follow the repository's Apache-2.0 license.

## Reproduce

Python 3.10+; tested with Python 3.12. Run from any directory:

    python3 /path/to/research/sparse-union-streaming-audit/verify.py

The runner copies the package into temporary storage, strips PYTHONOPTIMIZE, and runs only authored checks. It leaves repository evidence unchanged. Do not use -O or -OO. Allow several minutes for the exhaustive replay.

## Evidence boundaries

Scratch tapes are ordinary overwriteable work storage. Real input and spectator values are preserved; arbitrary initial scratch contents need not be restored. Record-header/counter widths and bounded-precision arithmetic require separate charges. Exact rational test matrices are not tests of every rounded Gaussian parameter. No runtime speedup, new kappa, selected supplier admission, or complete multiplication theorem follows from these tests.

## Open next questions

1. Can the actual bounded-precision local arithmetic compiler be implemented on fixed tapes with the stated coefficient/page schedule? Start from rhs/AUDIT.md and replace its host-array arithmetic oracle with a charged implementation. This matters because only the layout is currently simulated literally; full precision/error propagation remains a blocker.
2. For any proposed fixed broad rounded table, does its concrete row-error certificate satisfy the prefix addendum's uniform threshold? First identify the truncation/periodization convention and actual rounding constants. This is useful for the optional stronger inverse interface; the published broad forward-only schedule does not require broad Schur inversion.
3. Does later pending work already supply the same scoped replay? Refresh PR and Discussion overlap before publication. The initial limited search found no explicit equivalent, but incomplete search coverage does not establish novelty.

## Publication status

Prepared and checked for a local commit. No upstream publication is asserted. GitHub integration posting returned HTTP 403 during this session; no denied write was retried through another route.
