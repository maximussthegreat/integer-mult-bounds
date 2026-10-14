"""Validate a fresh generator replay before recording its provenance amendment.

This does not run generators or replace certificate contents. It rejects every
change outside the exact source/implementation digest fields listed below.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

from provenance_pins import BINDINGS, read_contained, unique_object

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = 'fe0ac01a41956bfdf0e6ca902fb2a131ee3cbf38'
SPECTRUM = 'research/single-intersection-spectrum-audit/RESULT.json'
# Authenticated with git show BASE_COMMIT:path before this maintenance repair.
# These anchors are deliberately independent of mutable AMENDMENTS.json.
ORIGINAL_CERTIFICATES = {
    'certificates/mixed-point-audit.json': '4053408adcd8de22edd9ac2b9dde491338f210540ac3a00e8dae9276b3cc2d3b',
    'certificates/rank-product-core.json': 'e0d2cb39be3502251f8f8c4a62e0fe6b743be50eef41dda35646762daaec40b9',
    'certificates/stage-pair-audit.json': '36ed3437fb3502bb90fdf9cd9357a09b0dda018d868fbf41ea25c55fb0c5b440',
    SPECTRUM: '9cb2210e148b2cce3fe59cf529fbf99f3b663dc7673db2e3969246595692f580',
}
REVIEWED_SOURCES = {
    'scripts/rational_span_frames.py': '7386947406d5dc4322a39fb7ccd886876a2fa1d163e823f0f231e11cf9ca0cec',
    'scripts/audit_stage_pair.py': '67cd9f046e257d7889b7574ca70db983d2414e93dcac34d9a555bc688cff6097',
    'scripts/experiments/single_intersection.py': '6874d41b75590369182ed61e0c6da5b547e035e0e43b50ea2b39e1f3861dca6d',
}
SPECTRUM_IMPLEMENTATION = 'd1d1fd8d55640a4319c176089f5511dddc56362fa82898fd779fb55193e9c981'
EXPECTED_UPDATES = {
    'certificates/mixed-point-audit.json': ['scripts/rational_span_frames.py'],
    'certificates/rank-product-core.json': ['scripts/audit_stage_pair.py'],
    'certificates/stage-pair-audit.json': ['scripts/audit_stage_pair.py'],
    SPECTRUM: ['scripts/experiments/single_intersection.py'],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def effective_source_path(certificate_path, source):
    if certificate_path == SPECTRUM and source == 'certificates/selected-result.json':
        return 'research/single-intersection-spectrum-audit/BASE-CHECKPOINT.json'
    return source


def validated_regeneration(root=ROOT):
    root = Path(root)
    receipts = []
    for path, sources in EXPECTED_UPDATES.items():
        snapshot = 'research/ci-provenance-maintenance/snapshots/' + path + '.snapshot'
        historical = read_contained(root, snapshot)
        require(sha(historical) == ORIGINAL_CERTIFICATES[path],
                'Changed immutable certificate snapshot at ' + BASE_COMMIT + ': ' + path)
        fresh = read_contained(root, path)
        original = json.loads(historical, object_pairs_hook=unique_object)
        current = json.loads(fresh, object_pairs_hook=unique_object)
        expected_pins = dict(original['source_sha256'])
        for source in sources:
            require(sha(read_contained(root, source)) == REVIEWED_SOURCES[source],
                    'Changed reviewed generator dependency: ' + source)
            expected_pins[source] = REVIEWED_SOURCES[source]
        for source, expected in expected_pins.items():
            effective = effective_source_path(path, source)
            require(sha(read_contained(root, effective)) == expected,
                    'Changed effective certificate source: ' + source)
        require(current['source_sha256'] == expected_pins,
                'Fresh source digests differ from exactly the reviewed changes: ' + path)
        if path == SPECTRUM:
            require(sha(read_contained(root, 'research/single-intersection-spectrum-audit/spectrum_audit.py'))
                    == SPECTRUM_IMPLEMENTATION, 'Changed reviewed spectrum verifier')
            require(current['implementation_sha256'] == SPECTRUM_IMPLEMENTATION,
                    'Spectrum result was not regenerated with the current verifier')
            del current['implementation_sha256']
            del original['implementation_sha256']
        del current['source_sha256']
        del original['source_sha256']
        require(canonical(current) == canonical(original),
                'A mathematical or scope field changed: ' + path)
        receipts.append({'path': path, 'source_commit': BASE_COMMIT,
                         'original_sha256': ORIGINAL_CERTIFICATES[path],
                         'current_sha256': sha(fresh), 'changed_source_paths': sources})
    return receipts


def record_regeneration(root=ROOT, *, record=False):
    root = Path(root).resolve()
    receipts = validated_regeneration(root)
    relative = 'research/ci-provenance-maintenance/AMENDMENTS.json'
    path = root / relative
    manifest = json.loads(read_contained(root, relative), object_pairs_hook=unique_object)
    require(manifest['base_commit'] == BASE_COMMIT, 'Amendment base commit changed')
    identities = [(row['group'], row['path']) for row in manifest['bindings']]
    require(len(identities) == len(set(identities)) and set(identities) == BINDINGS,
            'Missing, duplicate or unexpected provenance binding')
    row = next(row for row in manifest['bindings']
               if row['group'] == 'frontier890-integrated' and row['path'] == SPECTRUM)
    require(row['original_sha256'] == ORIGINAL_CERTIFICATES[SPECTRUM] and
            row['source_commit'] == BASE_COMMIT and row['mode'] == 'reviewed-live-source' and
            row['snapshot'] == 'research/ci-provenance-maintenance/snapshots/' + SPECTRUM + '.snapshot',
            'Changed historical spectrum-result binding')
    fresh = next(row for row in receipts if row['path'] == SPECTRUM)['current_sha256']
    if record:
        require(row['current_sha256'] in {ORIGINAL_CERTIFICATES[SPECTRUM], fresh},
                'Unreviewed preexisting spectrum-result amendment')
        row['current_sha256'] = fresh
        manifest['regenerated_artifacts'] = receipts
        # Check the target again immediately before writing, and refuse a final
        # symlink even if it was substituted after the contained read.
        read_contained(root, relative)
        descriptor = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, 'w') as output:
            output.write(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
            output.truncate()
    else:
        require(row['current_sha256'] == fresh, 'Generated-result binding has not been recorded')
        require(manifest.get('regenerated_artifacts') == receipts,
                'Regeneration receipts have not been recorded')
    print('PASS: four regenerated certificates preserve every mathematical and scope field')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true',
                        help='After validation, record only the generated-result binding and receipts')
    args = parser.parse_args()
    record_regeneration(record=args.record)


if __name__ == '__main__':
    main()
