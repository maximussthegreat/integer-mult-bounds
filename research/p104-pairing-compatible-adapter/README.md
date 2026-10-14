# Pairing-compatible P104 adapter with a new puncture

14 October 2026. Exact, self-authored finite arithmetic certificate. No downloaded code execution or changes to the selected record or predecessor artifacts.

## Result

A pairing-preserving adapter exists for the **entire selected 112-port set**. It also identifies the full 120-label extensions. The previously fixed 104-port obstruction is avoided by changing the puncture, not by relabeling the same 104 ports.

Replace PR1746's matrix F, stated by columns, with:

```
F_corrected = [199, 276, 493, 400, 362, 134, 143, 148, 167]
```

Keep the published convention `p = F_corrected^T phi`. Then:

- The resulting 112 physical ports are exactly the original selected 112-port set.
- For every pair of E8 labels i,j, covering all 14,400 entries of the full 120-label extension, `parity(p_i AND p_j) = (inner_product(root_i, root_j) + 1) mod 2`.
- The abstract deleted frame F1 becomes the physical puncture `{11,22,140,145,261,280,386,415}`.
- Every one of the eight actual reader/source support-pair matrices is 52 by 52 and has binary rank 7. Their rank sum is **56**.
- The new 104-port pairing matrix has row weight 56 on all 104 rows.

The previous puncture was `{22,38,145,161,280,296,415,431}`. The two punctures share `{22,145,280,415}`. Therefore the prior impossibility certificate for those two fixed 104-element sets remains valid; the candidate uses a different selected 104-element set.

## Compact construction and proof

All arithmetic in this section is over F2. Integers encode nine-bit column vectors; addition is XOR and the dot product is bit-parity of AND.

Let the old map from PR1746 be `p_i = F_old^T phi_i`, with

```
F_old columns = [5,276,303,338,362,68,143,148,167].
u = 45
c = 511
w = c + u = 466
```

Every old port has odd parity, so `c dot p_i = 1`. Exact reconstruction shows the old discrepancy has the rank-two form

```
B(i,j) + p_i dot p_j = u dot p_i + u dot p_j.
```

This identity is checked on all 120 squared entries. Also `u dot u = 0`. Thus translating all ports by u restores every pairing: `(p_i+u) dot (p_j+u) = B(i,j)`. Translation alone fails to preserve the selected port set.

Compose that translation with the orthogonal transvection `T_u(x) = x + (u dot x)u`. Since `u dot u = 0`, T_u preserves the standard dot pairing. On the odd ports the composite is

```
H(p) = p + (1 + u dot p)u.
```

It extends to the globally linear map

```
H(p) = p + (w dot p)u = (I + u w^T)p.
H columns = [1,47,4,8,61,32,109,173,301].
```

Because `w dot u = 0`, H is an involution and is invertible. Exact set equality confirms that H permutes the selected 112 ports, the extended 120 ports, and the eight excluded F0 ports. Therefore `F_corrected^T = H F_old^T` has the required pairing and set properties. Equivalently `F_corrected = F_old H^T`. In the published column notation this changes columns 0,2,3,5 by XOR 194 and leaves the other columns unchanged, producing the matrix above.

The discovery search was bounded to the 512 possible translations, of which u=45 was the only pairing-correcting translation on the full set. The final transvection/set checks are exact; no graph-isomorphism heuristic or unbounded search was used.

## Transported terms

E8 F0 is `[0,1,26,27,44,45,54,55]`; F1 is `[11,17,28,52,60,74,102,112]`. The 104 live labels exclude both. For a term (a,b), readers are live i with `inner_product(root_a, root_i) != 0`; sources are live j with `inner_product(root_b, root_j) != 0`.

| Published term | Reader count | Source count | Corrected actual dot rank | Previous fixed-support dot rank |
|---|---:|---:|---:|---:|
| (1,11) | 52 | 52 | 7 | 7 |
| (26,60) | 52 | 52 | 7 | 8 |
| (27,74) | 52 | 52 | 7 | 7 |
| (44,52) | 52 | 52 | 7 | 8 |
| (17,0) | 52 | 52 | 7 | 8 |
| (28,45) | 52 | 52 | 7 | 7 |
| (102,54) | 52 | 52 | 7 | 8 |
| (112,55) | 52 | 52 | 7 | 7 |
| Total | | | **56** | **60** |

The verifier checks entrywise equality of the abstract and corrected actual support-pair matrices, not just their ranks. `result.json` records all 120 mapped ports, the 112-port bijection, all eight reader/source support lists, and the puncture.

## Exact scope

This closes the pairing-compatible port-adapter screen. It does **not** establish a legal full P104 supplier, a realizable phase schedule, parity correction, restoration, hosting, or an end-to-end cost. The value 56 is the sum of these eight actual support-pair ranks, not a completed physical cost calculation and not a lower bound for arbitrary mixed-term programs.

In particular H is an algebraic label assignment. The certificate does not claim that H can be physically executed for free. Any implementation may use the corrected assignment directly, but it must still demonstrate all needed source/target interfaces and paid operations. The independent review verifies the transported real decoder identity `D T^T = 2G` on all 10,816 entries. Equality of that transported target to the selected word's required full real transformation remains unverified. Phase correctness, including centre construction/reads and parity correction, restoration, hosting, and complete cost must still be established.

## Credit

The E8 root-line/frame model is due to DreamingOfClouds (PR717), and the exact frame-pair decoder construction to themilkman216 (PR968), as credited in [PR1746’s pinned NOTICE](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/NOTICE.md). The original selected-set GL adapter is from 1337isnot1337’s PR1746. This follow-up contributes the pairing correction and transported puncture; it does not claim the predecessor decoder or its rank proof as new.

## Reproduction and provenance

Run with Python 3.10+ and no dependencies:

```
python verify_adapter.py > reproduced.json
cmp reproduced.json result.json
```

Both newly authored standard-library verifiers pass and reproduce their captured JSON results byte-for-byte. The inherited repository-wide `make verify` and `make entrance-bank-verify` suites were not run in this isolated arithmetic task; this package does not claim a full repository or supplier validation.

The script is standalone and reconstructs the E8 root lines, published greedy coordinate basis, pairings, old/new selected ports, and supports. It executes no downloaded repository code. The only exhaustive searches are 512 candidate translations and finite 512 by 512 linearity checks. Its output includes its own SHA-256 digest.

The prior audit independently verified that the reconstructed old 112-port set equals the actual hash-pinned selected payload, and all source/target boundary frames use span(p) and standard-dot p-perp. That prior payload verification is relied upon here; this script does not re-fetch or read the compressed selected word.

Pinned public sources inherited from the preceding audit:

1. [PR1746 certificate](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/CERTIFICATE.json): old F, source frames, and original deleted ports.
2. [PR1746 verifier](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/verify.py): selected-set convention `p = F^T phi`.
3. [E8 model and coordinate numbering](https://github.com/CrocSwap/integer-mult-bounds/blob/0b1cccf86e2f5132ed286a26ef0a681a495740ea/research/complex-frame-pair-decoders/verify.py#L52-L174): root lines, B, basis numbering, and decoder supports. Pinned file SHA-256 `bdf7ee497dc04dfc634ee5b7848f6a2b39b0169668fb1a60a9715111dbd15395`.
4. [Selected boundary convention](https://github.com/CrocSwap/integer-mult-bounds/blob/0b1cccf86e2f5132ed286a26ef0a681a495740ea/research/complex-block-rank-optimum/verify.py#L95-L102).
5. [Selected payload pins](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/SOURCES.json): compressed SHA-256 `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219`; decompressed SHA-256 `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.

## Independent computational review

The separately authored [review](independent/README.md) checks the actual payload hashes, all 112 source and 112 target boundary frames, all 14,400 pairing entries, and eight rank-seven certificates with invertible minors and row-span witnesses. It additionally checks the global identity `F_corrected F_corrected^T = J`, where J is the E8 form in phi coordinates, and all 10,816 transported real-decoder entries. H itself is not standard-dot orthogonal; the corrected assignment uses existing physical ports directly and does not require claiming that H was physically executed.

Prepared with OpenAI assistance. This is independently authored computational review, not independent human review or full supplier admission. Apache-2.0.
