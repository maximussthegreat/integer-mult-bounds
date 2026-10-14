"""Explicit, bounded amendments to historical source pins.

Original manifests remain unchanged. A live-source amendment authenticates both
the exact historical bytes and the reviewed current bytes; it is not a fallback
that accepts arbitrary newer files. Historical-context bindings authenticate a
snapshot which was never a computational dependency on the current selection.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath


HERE = Path(__file__).resolve().parent
AMENDMENTS = 'research/ci-provenance-maintenance/AMENDMENTS.json'
BINDINGS = frozenset({
    ('community92-evidence', 'research/community-reconciliation92-audit/verify.py'),
    ('community92-integrated', 'Makefile'),
    ('r420-sources', 'certificates/selected-result.json'),
    ('spectrum-sources', 'scripts/experiments/single_intersection.py'),
    ('split-skip-sources', 'research/split-skip/witness.py'),
    ('split-skip-sources', 'scripts/audit_fused_block.py'),
    ('frontier890-integrated', 'research/single-intersection-spectrum-audit/spectrum_audit.py'),
    ('frontier890-integrated', 'research/single-intersection-spectrum-audit/RESULT.json'),
})


class SourcePinError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise SourcePinError(message)


def read_contained(root, relative):
    """Reject aliases and traversal, including symlinks within the repository."""
    root = Path(root).resolve()
    need(isinstance(relative, str), 'Source path must be a string')
    path = PurePosixPath(relative)
    need(not path.is_absolute() and
         '..' not in path.parts and str(path) == relative,
         'Unsafe source path: ' + str(relative))
    target = root / relative
    need(target.resolve().is_relative_to(root) and target.resolve() == target,
         'Aliased or escaping source path: ' + relative)
    return target.read_bytes()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate amendment key: ' + key)
        result[key] = value
    return result


def source_digest(root, group, path, original_sha256):
    """Check a historical pin and return the digest of the source actually used."""
    key = (group, path)
    if key not in BINDINGS:
        actual = digest(read_contained(root, path))
        need(actual == original_sha256, 'Changed pinned source: ' + path)
        return actual

    manifest = json.loads(read_contained(root, AMENDMENTS), object_pairs_hook=unique_object)
    need(manifest.get('schema') == 1, 'Unknown provenance amendment schema')
    rows = manifest['bindings']
    identities = [(row['group'], row['path']) for row in rows]
    need(len(identities) == len(set(identities)) and set(identities) == BINDINGS,
         'Missing, duplicate or unexpected provenance binding')
    row = rows[identities.index(key)]
    need(row['original_sha256'] == original_sha256,
         'Amendment disagrees with original source pin: ' + path)
    snapshot = 'research/ci-provenance-maintenance/snapshots/' + path + '.snapshot'
    need(row['snapshot'] == snapshot, 'Unexpected historical snapshot path: ' + path)
    need(digest(read_contained(root, snapshot)) == original_sha256,
         'Changed historical source: ' + path)
    need(len(row['source_commit']) == 40 and
         all(c in '0123456789abcdef' for c in row['source_commit']),
         'Invalid historical commit: ' + path)

    if key == ('r420-sources', 'certificates/selected-result.json'):
        need(row['mode'] == 'historical-context' and 'current_sha256' not in row,
             'Historical context cannot be repinned to the live selection')
        return original_sha256

    need(row['mode'] == 'reviewed-live-source', 'Expected a reviewed live source: ' + path)
    actual = digest(read_contained(root, path))
    need(actual == row['current_sha256'], 'Changed amended live source: ' + path)
    return actual
