# Sparse-union sequential-tape verification supplement

14 October 2026. Independently authored construction, finite replay, and adversarial review of the layout contract in PR1673, pinned to 2569871ff906d2a2abfc86e97126ab9afe2e4a5a.

The underlying sparse-union method and retained transpose constructions are credited to their authors in PROOF.md and the source manifest. This supplement makes the sequential record movement explicit. It establishes no new multiplication exponent and does not prove the separate dense compiler, Gaussian precision, boundary arithmetic, or complete bit-machine implementation.

## Reproduce
Python 3.10+ standard library only. From any directory, run:

    python /path/to/packet/run_all.py

This executes only the independently authored code included here. No network or upstream code is needed. Read PROOF.md, schedule/FINAL-REPORT.md and review/AUDIT.md for claims and limitations.

The exhaustive grid covers all 5,036 support tuples for L=2,3,4 and g=1,2,3, with 281,312 exact basis columns. Independent checks include separate scalar oracles and exact movement recounts. These finite tests support, but do not substitute for, the constructive proof.

Publication status: prepared locally; no new GitHub comment or PR published. The connected GitHub integration returned HTTP403 when posting a separate status clarification.
