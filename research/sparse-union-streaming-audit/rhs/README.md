# Boundary RHS interface audit

Read AUDIT.md for the mathematical result and its assumptions. REVIEW.md is
the independent proof review. RESULTS.json contains reproducible finite checks.

Run locally, with Python's standard library only:

    python check_interface.py

The program runs original local tests only. It never imports or executes any
file in inert_sources, makes no network calls, and writes only RESULTS.json.

Final result: 48 tape-layout cases, 8 exact rational algebra cases, 622 local
Strassen page products, and 53,998 scalar products passed. Controls demonstrate
why completed conditioning alone, partial-separator elimination, and too few
common-factor RHS cannot be silently substituted for the proof's premises.

The tests cover local band and cyclic Schur algebra and literal batch
permutations. Exact arithmetic uses host arrays and fractions, so elapsed
test time is not the proved asymptotic bound and no bounded-precision Gaussian
implementation is claimed.

The final capped arithmetic cost remains

    O(V (d/Bcap) W^(omega-1) polylog p),

under the explicit analytic, coefficient-generation, and multiplication
interfaces. There is no new exponent or external repository update.
