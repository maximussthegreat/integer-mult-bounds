# Independent proof review

Review date: 2026-10-14. A separate reviewer read AUDIT.md and its pinned inert
sources. No upstream programs were executed and no source files were changed
by the reviewer.

Verdict: scoped pass, conditional on the explicitly inherited Gaussian
conditioning/rounding and stable square-product interfaces.

- E/J: original B/C shears remain width-W after deleting unused coordinates;
  S and S^-1 operate only on J, with E\J copied unchanged.
- Cyclic factors: retaining the last group produces one dense block row and
  one dense block column, containing O(j/W+1) pages rather than a dense j-square
  factor.
- Batching and tapes: the 8n binary-pass ledger is consistent. Factor rewinds
  fit O((j+W)W ceil(R/q)). A fixed-formula depth-first recursive multiplication
  can restore/scan each suspended O(n^2) frame a constant number of times per
  fixed-formula child, preserving the displayed recurrence.
- Conditioning: CAPPED-GAUGE-AUDIT section 5 genuinely supplies whole-group
  separation geometry. A contiguous physical component selects a contiguous
  source-index interval and reduces, in selected/hole order, to [K 0; R I].
  Retaining the wrap group prevents premature cyclic coupling; final
  elimination invokes the full periodic inverse. Thus the eliminated-set
  inverse bounds follow conditionally from the inherited analytic theorem
  and rounding estimates. Completed inverse bounds alone would not suffice.

The reviewer requested clarification of the partial-separator example:
eliminating 3 connects 2--3--5, while eliminating 4 connects 2--4--5.
That wording correction is included in the final AUDIT.md. The correction
does not change the lemma or its costs.

This review is of the written interface proof. It does not independently
validate Gaussian constants or turn the finite checker into a bit-Turing
implementation.
