# Independent review of the corrected selected P104 adapter

14 October 2026. Self-authored exact finite arithmetic only. No downloaded code was executed during this independent check. Publication of this portable review does not expand its mathematical scope.

## Result

The corrected assignment closes the specific selected-port binary-pairing gap. It is a bijection from abstract E8 P112 to the **actual hash-pinned selected 112-port set**, preserves the binary pairing entrywise, and yields eight actual support-pair ranks of seven on a different physical P104 puncture. Their total is 56.

The review independently checked:

- both the compressed and decompressed selected-payload SHA-256 hashes;
- equality with the actual 112 payload ports;
- all 112 actual source start-frame spans `{0,p}`;
- all 112 actual target final-frame spans `{x : parity(x AND p)=0}`;
- invertibility and explicit inverse of the corrected 9-dimensional linear map;
- all 14,400 full-root pairing entries, including all 12,544 selected P112 entries;
- all eight 52-by-52 actual physical support matrices, with exact rank seven each;
- all 10,816 entries of the real decoder identity `D T^T = 2G` after the stated reindexing.

The check uses existing payload frame records; it does not infer the boundary frames from a fallback convention. The result file includes each rank-seven matrix's invertible 7-by-7 minor and explicit expressions of every matrix row in a seven-row basis, so both the lower and upper rank bounds are inspectable.

## Exact map and the affine nuance

Use the published dual coordinates `phi`, based on roots `[0,1,2,4,6,8,10,12,56]`, and the original F columns

`[5,276,303,338,362,68,143,148,167]`.

The original assignment is `p=F^T phi`. Let `u=45`, `w=511`, and `v=w XOR u=466`. All 120 original port vectors have odd parity, so `dot(w,p)=1`. Consequently the initially affine formula

`A(p)=p XOR ((1 XOR dot(u,p))*u)`

agrees on every relevant port with the globally linear map

`H(p)=p XOR (dot(v,p)*u)`.

`A(0)=45`, while `H(0)=0`; they are not the same function on all of F2^9. Since `dot(v,u)=0`, `H^2=I`, hence H is invertible. Its columns are

`[1,47,4,8,61,32,109,173,301]`.

The corrected assignment is `q=M phi`, with `M=H F^T`. Equivalently `q=Fnew^T phi`, where `Fnew=F H^T` has columns

`[199,276,493,400,362,134,143,148,167]`.

The columns of M itself are

`[325,369,487,84,138,276,21,493,30]`,

and its inverse, the physical-port-to-phi map, has columns

`[452,278,493,402,105,391,396,148,420]`.

## A global label-space isometry, with precise qualifications

Let K be the 9-by-9 E8 pairing matrix on the chosen nine basis roots. Since phi consists of pairings against those roots, the E8 bilinear form in phi coordinates is `J=K^-1`. The columns of J are

`[258,259,4,8,16,32,64,128,3]`.

The review directly checks the full matrix identity

`M^T M = J`, equivalently `Fnew Fnew^T = J`.

Thus M is a genuine global isometry **from the E8 label-space bilinear form J to the standard-dot form**. This is stronger than a finite pairing coincidence or an arbitrary GL set bijection. No unsupported global-isometry claim is needed for the affine A.

H itself is **not** an orthogonal automorphism of the standard-dot space. For example, `dot(1,2)=0` but `dot(H(1),H(2))=dot(1,47)=1`. Applying H to every phase subspace of an already-existing physical word does not automatically preserve its source/target pairing: a source basis change and a covector basis change require the appropriate dual transformations. Nothing here certifies that such an operation is free or legal.

The useful interpretation is to assign E8 root i directly to the existing physical port `q_i=M phi_i`. Since these q values are exactly the already-available selected ports, the source and target boundary pairing for that new assignment is verified without asserting that H has been physically executed on the old word.

## Different puncture, same earlier obstruction

The original deleted physical ports were

`{22,38,145,161,280,296,415,431}`.

The corrected deleted physical ports are

`{11,22,140,145,261,280,386,415}`.

Four ports change. The original fixed 104-set still has row-weight histogram `{52:12,56:88,60:4}`, so its earlier non-isomorphism obstruction remains valid. The corrected 104-set has row weight 56 on all 104 rows. The new result escapes the old obstruction by changing which physical ports are omitted; it does not refute that obstruction.

For the published term pairs

`[(1,11),(26,60),(27,74),(44,52),(17,0),(28,45),(102,54),(112,55)]`,

the old physical ranks are `[7,8,7,8,8,7,8,7]`, and the corrected physical ranks are `[7,7,7,7,7,7,7,7]`.

## Decoder identity: what was proved and what was not

Let `G_ij` be the real inner product of the chosen E8 root representatives, and let `(a_k,b_k)` be the eight pairs above. Their diagonal pairing signs are `[1,1,-1,1,1,1,1,1]`. Define

`D_ik=G_(i,a_k)` and `T_jk=2 G_(a_k,b_k) G_(j,b_k)`.

The review checks cross-duality and independently checks `sum_k D_ik T_jk=2G_ij` on all 104 squared live entries. `result.json` gives the exact D and T row assigned to every live physical port. This is an exact real decoder certificate for the **transported signed Gram matrix**.

A binary pairing isometry alone does not establish that this transported signed Gram matrix is the required full real transformation of the original selected word. This review did not replay the original complete scalar word or verify that target equality. It also did not construct a legal phase schedule, centre construction/reads, parity correction, restoration, or hosting. The result is a verified pairing-compatible decoder candidate and rank-56 screen, not complete replacement-supplier admission or a new end-to-end bound.

## Reproduction

Run:

`python check_adapter.py > result.json`

To use another copy of the same pinned input, pass `--payload /path/to/selected_payload.b64`.

The public selected payload is JSON compressed with gzip and then base64 encoded. The verifier checks its two hashes before reading data. The included `inputs/selected_payload.b64` is the verified public input; the hash pins, not the local path, establish its identity. The verifier imports only the Python standard library.

The JSON report contains the verifier's SHA-256, complete root-to-port maps, all decoder rows, exact rank certificates, and scope flags. Only the newly authored `check_adapter.py` was run; the candidate author's verifier and repository verifier were read as source but not executed in this independent review.

## Pinned sources

- [Original adapter certificate, PR1746 head 23bae0f8d16246862524581b742c7a922514bfd5](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/CERTIFICATE.json).
- [Original adapter construction and transpose convention](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/verify.py).
- [E8 root numbering, pairing, and exact real decoder definitions](https://github.com/CrocSwap/integer-mult-bounds/blob/0b1cccf86e2f5132ed286a26ef0a681a495740ea/research/complex-frame-pair-decoders/verify.py).
- [Selected physical boundary convention](https://github.com/CrocSwap/integer-mult-bounds/blob/0b1cccf86e2f5132ed286a26ef0a681a495740ea/research/complex-block-rank-optimum/verify.py#L95-L102).
- [Selected payload pins](https://github.com/CrocSwap/integer-mult-bounds/blob/23bae0f8d16246862524581b742c7a922514bfd5/research/selected-p104-port-adapter/SOURCES.json): compressed SHA-256 `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219`; decompressed SHA-256 `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.

Prepared with OpenAI assistance. Independently authored computational review, not independent human review.
