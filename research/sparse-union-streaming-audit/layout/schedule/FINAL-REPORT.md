# Final finite replay report

Status: PASS_EXACT_FINITE_RECORD_TAPE_REPLAY

Pinned source: `2569871ff906d2a2abfc86e97126ab9afe2e4a5a`. No upstream code executed.

## Coverage

- Every E_i subset of [L] for L=2,3,4 and g=1,2,3
- 5,036 support tuples; 281,312 exact input-basis columns
- Two consecutive sparse sweeps per tuple, with exact checks after each sweep
- First sweep uses rational invertible blocks; second uses rational singular blocks
- Empty/full supports, all overlap patterns, and non-dyadic supports included
- Four supplemental prefix/suffix spectator cases; separate zero-block and non-dyadic detailed traces
- 72 opaque-record selected-field permutation/round-trip controls passed
- Six malformed-stream/width/padding rejection controls passed
- Final exhaustive run: 170.084 seconds

| L | g | Support tuples | Basis columns |
|---:|---:|---:|---:|
| 2 | 1 | 4 | 8 |
| 2 | 2 | 16 | 64 |
| 2 | 3 | 64 | 512 |
| 3 | 1 | 8 | 24 |
| 3 | 2 | 64 | 576 |
| 3 | 3 | 512 | 13,824 |
| 4 | 1 | 16 | 64 |
| 4 | 2 | 256 | 4,096 |
| 4 | 3 | 4,096 | 262,144 |

## Literal movement example

L=4, g=3; E_0={0,1,3}, E_1={0,2}, E_2={1,2,3}.
V=64, |U|=62, (|U_0|,|U_1|,|U_2|)=(48,32,48).
The trace executes two sparse sweeps sharing one gather and one scatter.

| Phase | Reads | Writes | Forward head steps | Backward head steps |
|---|---:|---:|---:|---:|
| gather | 64 | 62 | 126 | 126 |
| extract | 372 | 256 | 628 | 628 |
| padding | 704 | 704 | 1408 | 1408 |
| transpose | 1280 | 1280 | 2560 | 2560 |
| arithmetic | 960 | 512 | 1472 | 1472 |
| merge | 628 | 372 | 1000 | 1000 |
| scatter | 126 | 64 | 190 | 190 |
| verification_output | 188 | 0 | 188 | 188 |

- Layout-only movement including outer scans: 11,824 record-head steps
- Local arithmetic movement: 2,944 additional record-head steps; 704 matrix-coefficient reads
- Setup and verification traffic are separately counted, not layout work
- 12 literal binary passes, covering 640 padded record-visits; exactly 5,120 head steps = 8 × 640
- 64 tagged padding records inserted and exactly 64 removed
- Peak six live payload lanes, independent of dimension in the code allocation

## Dense-interior control

L=3, g=1, J={0}, I={1,2}, E={0,1}. The dense matrix is

    [[1,0,0], [0,1,1], [0,1,2]].

It fixes the boundary coordinate. Input e_1 maps to (0,1,1). The actually
executed incorrect retained-union schedule produces (0,1,0), losing the
deep-interior coordinate 2. The correct two-window schedule passes exact
basis replay and counts exactly two gathers and two scatters. Two sparse
stages genuinely share the first gathered union.

## Verification boundary

These are exact finite algebra and emulated sequential record-tape counts.
They do not certify bit-level header/membership control, bounded rational
height, efficient boundary arithmetic, Gaussian conditioning, or the full
multiplication theorem. The host reference is random-access; the schedule
payload interface is sequential. Scratch can be overwritten and is not
restored. Arbitrary real spectator payloads are preserved. See README.md
for the full model, exact constants, reproduction commands, and caveats.
