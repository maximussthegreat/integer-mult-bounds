# Provenance-preserving CI maintenance

Base: `fe0ac01a41956bfdf0e6ca902fb2a131ee3cbf38`.
This is a maintenance repair, with no new mathematical result or selected-frontier change.

## What is preserved

The original source manifests, historical reconciliation coverage and integration
receipts stay byte-identical. Every changed pinned source has its exact original
bytes retained under `snapshots/`, with its source commit and original SHA-256 in
`AMENDMENTS.json`. `.snapshot` files are evidence, not imported modules.

The amendment checker accepts only eight explicitly named group/path bindings.
For live-source amendments it verifies both the original snapshot against the
original manifest pin and the current file against the reviewed replacement pin.
A changed current source, changed snapshot, missing or unknown binding, wrong
original pin, path traversal or symlink alias is rejected. Each adapter checks
the helper's exact SHA-256 before importing it.

- Reconciliation92: the historical Makefile is preserved; the live Makefile has
  five appended targets. Its complete current bytes remain pinned. The amended
  verifier is separately bound to its original snapshot and current digest.
- R420: selected-result.json was historical PR626 context at the package's
  declared base, never a computational input to the finite D construction. The
  original context is authenticated from its snapshot. Other source checks,
  complete Python/C++ certificates and rejection controls remain required.
- Spectrum audit: the dependency's symmetric packed-matrix optimization leaves
  spectral_parity_bound unchanged. The live dependency is explicitly bound, and
  the fresh certificate must truthfully report its effective current digest.
- Split-skip: audit_fused_block.py only avoids redundant Fraction conversion.
  Its original and current bytes, and the amended witness itself, are checked.
- Frontier890: the two spectrum audit files have narrow live-source amendments.
  Original coverage and integration receipts remain unchanged.

Historical sources are from commits b84ba67156a01f9c2cb34fe1e3cb1dcdeab00d9c
(Makefile), 66849e1475c930fd7732b1a0067ffee7e1e95f60 (selected context and
single-intersection dependency), 3ffd4021995c959ac02d12920e0279ae97dd03c7
(fused-block dependency), or the exact pre-repair base above (verifiers/results).
Original contributor attribution and licenses are retained in those sources.
Maintenance implementation uses substantial OpenAI assistance.

The complete old-source history of rational_span_frames.py and audit_stage_pair.py
has not been reconstructed here. Their exact current base bytes are bound, and
the original certificates/digest evidence are preserved. Equality of regenerated
mathematical outputs must be established by fresh replay; source implementation
equivalence is not asserted from stale hashes alone.

## Required replay and review

Use one isolated checkout. Do not run concurrent artifact-generating suites in
it. Run repository code only with the required execution authorization. The
following commands are the bounded completion criteria; preparation alone does
not mean they have passed:

1. `python3 -B scripts/audit_mixed_point.py`
2. `python3 -B scripts/audit_stage_pair.py`
3. `python3 -B scripts/audit_rank_product_core.py`
4. `python3 -B research/single-intersection-spectrum-audit/spectrum_audit.py --write`
5. `python3 -B research/ci-provenance-maintenance/check_regeneration.py --record`
6. `python3 -B tests/test_ci_provenance_maintenance.py -v`
7. `python3 -B research/community-reconciliation92-audit/verify.py`
8. `python3 -B -m unittest discover -s tests -p test_parallel_verification.py -v`
9. `python3 -B research/r420-two-sided-basis/verify.py`
10. `python3 -B -m unittest discover -s research/r420-two-sided-basis -p 'test_*.py' -v`
11. `python3 -B research/r420-two-sided-basis/native.py` (C++17 and Boost required)
12. `python3 -B scripts/verify_pr_reconciliation.py`
13. `make verify-tests`, `make verify-clones`, `make verify-research`, sequentially
14. `python3 -B research/ci-provenance-maintenance/check_regeneration.py`

The regeneration recorder does not write any certificate. It refuses every
mathematical/scope change and every source change except the specific reviewed
digest updates. All four original certificate snapshots are authenticated
against fixed digests verified from the exact base commit; reviewed live-source
and spectrum-implementation digests are also fixed independently of the mutable
amendment manifest. Changing both a snapshot and fresh result, or changing a
source and its reported digest together, is rejected. It records the spectrum
result's exact new digest only after these comparisons pass.

All effective source files are independently rehashed, including unchanged
source-map entries and the spectrum audit's historical BASE-CHECKPOINT mapping.
Snapshot, source, result and amendment paths reject symlink aliases and escapes;
the amendment write target is rechecked and opened without following a symlink.
Repeating generation after recording must leave all tracked artifact bytes
unchanged. Inspect the final diff, then run exact-head
CI on Python 3.11, 3.13 and 3.14 before claiming repository-wide green.

## Open next questions

- Can future reviewed integration changes record explicit historical/current
  bindings when they are introduced, avoiding stale live-path pins?
- Can source inventories distinguish computational inputs from historical
  context without relaxing integrity checks?

Those broader changes are outside this bounded repair.
