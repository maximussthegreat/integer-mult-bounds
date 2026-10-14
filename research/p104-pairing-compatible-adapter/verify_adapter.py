#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Self-authored exact pairing-compatible selected-port adapter certificate.

Uses only Python's standard library, published mathematical definitions and
pinned constants. No network access or downloaded repository code is used.
Run: python verify_adapter.py > result.json
"""
import hashlib
import json
from pathlib import Path

OLD_F_COLUMNS = [5, 276, 303, 338, 362, 68, 143, 148, 167]
FRAME0 = [0, 1, 26, 27, 44, 45, 54, 55]
FRAME1 = [11, 17, 28, 52, 60, 74, 102, 112]
PAIRS = [(1, 11), (26, 60), (27, 74), (44, 52),
         (17, 0), (28, 45), (102, 54), (112, 55)]
MASK9 = (1 << 9) - 1


def parity(x):
    return x.bit_count() & 1


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            i = value.bit_length() - 1
            if i in pivots:
                value ^= pivots[i]
            else:
                pivots[i] = value
                break
    return len(pivots)


def root_lines():
    roots = []
    for left in range(8):
        for right in range(left + 1, 8):
            for sign in (1, -1):
                r = [0] * 8
                r[left], r[right] = 2, 2 * sign
                roots.append(r)
    for mask in range(128):
        r = [1] + [-1 if mask & (1 << k) else 1 for k in range(6, -1, -1)]
        if r.count(-1) % 2 == 0:
            roots.append(r)
    assert len(roots) == 120 and len({tuple(r) for r in roots}) == 120
    assert all(sum(x*x for x in r) == 8 for r in roots)
    return roots


def xor(values):
    answer = 0
    for value in values:
        answer ^= value
    return answer


def dual_map(columns, q):
    return sum(parity(c & q) << k for k, c in enumerate(columns))


def run():
    roots = root_lines()
    gram = [[sum(x*y for x, y in zip(r, s)) // 4 for s in roots] for r in roots]
    B = [[(g + 1) & 1 for g in row] for row in gram]
    packed = [sum(b << j for j, b in enumerate(row)) for row in B]
    basis = []
    for i in range(120):
        if rank([packed[j] for j in basis] + [packed[i]]) > len(basis):
            basis.append(i)
        if len(basis) == 9:
            break
    assert basis == [0, 1, 2, 4, 6, 8, 10, 12, 56]
    phi = [sum(B[i][j] << k for k, j in enumerate(basis)) for i in range(120)]
    old = [dual_map(OLD_F_COLUMNS, q) for q in phi]
    assert rank(phi) == rank(old) == 9
    assert all(parity(p) == 1 for p in old)
    p112 = [i for i in range(120) if i not in FRAME0]
    live = [i for i in p112 if i not in FRAME1]
    S = {old[i] for i in p112}
    assert len(S) == 112 and len(live) == 104

    # B - old-dot has the special additive, rank-two form on odd ports.
    delta = [[B[i][j] ^ parity(old[i] & old[j]) for j in range(120)]
             for i in range(120)]
    delta_rank = rank([sum(b << j for j, b in enumerate(row)) for row in delta])
    assert delta_rank == 2
    assert all(delta[i][j] == delta[i][0] ^ delta[0][j]
               for i in range(120) for j in range(120))

    # Bounded, exhaustive search over only 512 translations. It finds a
    # unique u such that old+u has exactly the E8 pairings on all 120 labels.
    translations = []
    for u in range(512):
        if all(B[i][j] == parity((old[i] ^ u) & (old[j] ^ u))
               for i in range(120) for j in range(120)):
            translations.append(u)
    assert translations == [45]
    u = translations[0]
    assert parity(u) == 0
    assert {p ^ u for p in S} != S

    # T_u is an orthogonal transvection because dot(u,u)=0. Compose it
    # after the translation to recover the selected set while retaining B.
    def transvection(p):
        return p ^ (u if parity(p & u) else 0)

    new = [transvection(p ^ u) for p in old]
    assert all(new[i] == old[i] ^ (u if not parity(old[i] & u) else 0)
               for i in range(120))
    assert {new[i] for i in p112} == S
    assert set(new) == set(old)
    assert {new[i] for i in FRAME0} == {old[i] for i in FRAME0}
    assert len(set(new)) == 120
    assert all(B[i][j] == parity(new[i] & new[j])
               for i in range(120) for j in range(120))

    # On all odd ports the composite is the restriction of the linear shear
    # H(p)=p+u*dot(p,w), w=111111111+u. This gives explicit replacement F.
    w = MASK9 ^ u
    H_columns = [(1 << k) ^ (u if (w >> k) & 1 else 0) for k in range(9)]
    v = xor(OLD_F_COLUMNS[k] for k in range(9) if (w >> k) & 1)
    new_F = [c ^ (v if (u >> k) & 1 else 0) for k, c in enumerate(OLD_F_COLUMNS)]
    assert rank(H_columns) == rank(new_F) == 9
    assert parity(u & w) == 0
    assert [dual_map(new_F, q) for q in phi] == new
    # Verify the shear is linear and involutive on the whole 9-space.
    def H(p):
        return p ^ (u if parity(p & w) else 0)
    assert all(H(H(p)) == p for p in range(512))
    assert all(H(p ^ q) == H(p) ^ H(q) for p in range(512) for q in range(512))

    terms = []
    supports = []
    for a, b in PAIRS:
        readers = [i for i in live if gram[a][i] != 0]
        sources = [j for j in live if gram[b][j] != 0]
        abstract = [sum(B[i][j] << k for k, j in enumerate(sources)) for i in readers]
        actual = [sum(parity(new[i] & new[j]) << k for k, j in enumerate(sources))
                  for i in readers]
        previous = [sum(parity(old[i] & old[j]) << k for k, j in enumerate(sources))
                    for i in readers]
        assert abstract == actual
        assert len(readers) == len(sources) == 52
        assert rank(abstract) == rank(actual) == 7
        terms.append({"pair": [a, b], "readers": len(readers), "sources": len(sources),
                      "e8_rank": rank(abstract), "corrected_selected_dot_rank": rank(actual),
                      "previous_fixed_support_dot_rank": rank(previous)})
        supports.append({"pair": [a, b], "reader_root_ids": readers, "source_root_ids": sources,
                         "reader_ports": [new[i] for i in readers],
                         "source_ports": [new[j] for j in sources]})
    new_removed = sorted(new[i] for i in FRAME1)
    old_removed = sorted(old[i] for i in FRAME1)
    assert new_removed == [11, 22, 140, 145, 261, 280, 386, 415]
    assert old_removed == [22, 38, 145, 161, 280, 296, 415, 431]
    assert sorted(set(new_removed) & set(old_removed)) == [22, 145, 280, 415]
    assert all(sum(parity(new[i] & new[j]) for j in live) == 56 for i in live)
    assert sum(t['corrected_selected_dot_rank'] for t in terms) == 56

    return {
        "status": "EXACT_PAIRING_COMPATIBLE_ADAPTER_NOT_FULL_SUPPLIER_ADMISSION",
        "coordinate_basis": basis,
        "old_F_columns": OLD_F_COLUMNS,
        "corrected_F_columns": new_F,
        "linear_shear_H_columns": H_columns,
        "translation_u": u,
        "linear_shear_w": w,
        "correction_dual_v": v,
        "all_pairing_preserving_translations_in_512_candidates": translations,
        "translation_alone_preserves_112_set": False,
        "pairing_discrepancy_rank": delta_rank,
        "corrected_map_preserves_120_set": True,
        "corrected_map_preserves_selected_112_set": True,
        "full_120_pairing_entries_checked": 120 * 120,
        "full_112_pairing_entries_checked": 112 * 112,
        "previous_removed_selected_ports": old_removed,
        "corrected_removed_selected_ports": new_removed,
        "corrected_live_selected_ports": sorted(new[i] for i in live),
        "terms": terms,
        "corrected_selected_dot_total": 56,
        "previous_fixed_support_dot_total": sum(t['previous_fixed_support_dot_rank'] for t in terms),
        "corrected_P104_row_weight_histogram": {"56": 104},
        "root_to_corrected_port": new,
        "old_to_corrected_port_on_selected_112": {str(old[i]): new[i] for i in p112},
        "supports": supports,
        "scope_exclusions": [
            "No executable phase schedule, parity correction, restoration or hosting was constructed.",
            "No complete legal supplier or end-to-end cost admission was established.",
            "No claim that the shear is a cost-free physical operation is made.",
            "No downloaded repository code was executed by this verifier."
        ],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
