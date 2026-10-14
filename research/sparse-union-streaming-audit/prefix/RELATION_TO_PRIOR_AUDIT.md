# Relation to the earlier boundary-RHS audit

The earlier report is `/workspace/shared/sparse_rhs_interface_20261014/AUDIT.md`.
Its page/stream and block-algebra result remains valid as a conditional
symmetric interface supporting either S or S^-1. The present audit does not
invalidate its batching counts or finite controls.

Two qualifications should accompany any new release or summary:

1. **Actual directions.** The pinned main `phase_fusion_note.tex:233` uses the
   broad Schur complement forward only. Its necessary Gaussian conditions are
   the narrow boundary-solve bounds and the broad phase-interior inverse bounds.
   Broad physical-prefix inversion is sufficient for the stronger generic
   interface, but is not necessary for this published schedule.
2. **Meaning of the previous analytic boundary.** “Not independently verified”
   described the earlier audit's verification scope. It should not be converted
   into “the source lacks a proof” or “a current counterexample was found.” The
   present report checks the finite LDU hypotheses and derives a uniform
   physical-prefix perturbation threshold. No counterexample to the current
   rounded construction was found. A fixed-table-specific rounding certificate
   remains outside this bounded audit.

A corrected/addended release is appropriate if the earlier deliverable was
summarized as depending necessarily on broad Schur solves or as exposing an
absent Gaussian theorem. There is no reason to retract the completed
conditional tape/layout result. Preserve the original as dated history and
add this scope note, rather than silently replacing its claims.

Suggested concise addendum:

> The preceding report analyzes a symmetric boundary interface supporting
> both forward application and inversion. The pinned construction uses a
> narrower subset: broad Schur application and narrow Schur inversion.
> Broad prefix-inverse bounds are therefore a sufficient extra interface,
> not a necessary gap in the main schedule. A further bounded audit verifies
> the ideal finite-to-physical-prefix reduction and its uniform perturbation
> condition, B(T_W+delta_round)<=1/2. It finds no construction counterexample;
> fixed historical broad coefficient tables and final rounding constants were
> not independently regenerated.

No upstream change, comment, or publication was made by this audit.
