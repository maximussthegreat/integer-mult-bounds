"""Positive replay invariants and corruption controls for CI pin maintenance."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from fractions import Fraction
from random import Random

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/ci-provenance-maintenance'
sys.path.insert(0, str(PACKAGE))
import provenance_pins as pins
import check_regeneration as regeneration


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PinContractTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest = json.loads((ROOT / pins.AMENDMENTS).read_text())
        self.rows = self.manifest['bindings']
        for row in self.rows:
            for relative in (row['path'], row['snapshot']):
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
        self.save_manifest()

    def save_manifest(self):
        target = self.root / pins.AMENDMENTS
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.manifest))

    def check(self, row, expected=None):
        return pins.source_digest(self.root, row['group'], row['path'],
                                  row['original_sha256'] if expected is None else expected)

    def test_all_fixed_bindings_authenticate_old_and_effective_sources(self):
        for row in self.rows:
            with self.subTest(path=row['path'], group=row['group']):
                self.assertEqual(self.check(row), row.get('current_sha256', row['original_sha256']))

    def test_each_historical_snapshot_corruption_is_rejected(self):
        for row in self.rows:
            path = self.root / row['snapshot']
            original = path.read_bytes()
            path.write_bytes(original + b'\ncorruption')
            with self.subTest(path=row['path'], group=row['group']):
                with self.assertRaisesRegex(pins.SourcePinError, 'Changed historical source'):
                    self.check(row)
            path.write_bytes(original)

    def test_each_current_source_corruption_is_rejected(self):
        for row in self.rows:
            if row['mode'] != 'reviewed-live-source':
                continue
            path = self.root / row['path']
            original = path.read_bytes()
            path.write_bytes(original + b'\ncorruption')
            with self.subTest(path=row['path'], group=row['group']):
                with self.assertRaisesRegex(pins.SourcePinError, 'Changed amended live source'):
                    self.check(row)
            path.write_bytes(original)

    def test_original_manifest_pin_cannot_be_silently_replaced(self):
        for row in self.rows:
            with self.subTest(path=row['path'], group=row['group']):
                with self.assertRaisesRegex(pins.SourcePinError, 'disagrees with original'):
                    self.check(row, '0' * 64)

    def test_missing_duplicate_unknown_and_renamed_bindings_are_rejected(self):
        row = self.rows[0]
        mutations = [self.rows[1:], self.rows + [self.rows[0]],
                     self.rows + [dict(self.rows[0], group='unreviewed')],
                     [dict(self.rows[0], path='elsewhere.py')] + self.rows[1:]]
        for rows in mutations:
            self.manifest['bindings'] = rows
            self.save_manifest()
            with self.assertRaisesRegex(pins.SourcePinError, 'provenance binding'):
                self.check(row)

    def test_duplicate_json_key_is_rejected(self):
        path = self.root / pins.AMENDMENTS
        path.write_text('{"schema": 1, "schema": 1, "bindings": []}')
        with self.assertRaisesRegex(pins.SourcePinError, 'Duplicate amendment key'):
            self.check(self.rows[0])

    def test_snapshot_alias_and_mode_changes_are_rejected(self):
        for field, value in [('snapshot', '../outside'), ('mode', 'ignore')]:
            old = self.rows[0][field]
            self.rows[0][field] = value
            self.save_manifest()
            with self.assertRaises(pins.SourcePinError):
                self.check(self.rows[0])
            self.rows[0][field] = old

    def test_symlink_sources_are_rejected_even_when_bytes_match(self):
        row = self.rows[0]
        for relative in (row['path'], row['snapshot']):
            path = self.root / relative
            original = path.read_bytes()
            alias = self.root / 'alias'
            alias.write_bytes(original)
            path.unlink()
            path.symlink_to(alias)
            with self.assertRaisesRegex(pins.SourcePinError, 'Aliased or escaping'):
                self.check(row)
            path.unlink()
            path.write_bytes(original)
            alias.unlink()

    def test_unknown_sources_still_require_the_original_hash(self):
        source = self.root / 'unamended.py'
        source.write_bytes(b'original')
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(pins.source_digest(self.root, 'other', 'unamended.py', expected), expected)
        source.write_bytes(b'changed')
        with self.assertRaisesRegex(pins.SourcePinError, 'Changed pinned source'):
            pins.source_digest(self.root, 'other', 'unamended.py', expected)

    def test_r420_historical_context_is_independent_of_live_selection(self):
        row = next(row for row in self.rows if row['group'] == 'r420-sources')
        (self.root / row['path']).write_bytes(b'future live selection')
        self.assertEqual(self.check(row), row['original_sha256'])
        row['current_sha256'] = hashlib.sha256(b'future live selection').hexdigest()
        self.save_manifest()
        with self.assertRaisesRegex(pins.SourcePinError, 'cannot be repinned'):
            self.check(row)

    def test_paths_cannot_escape_or_alias_repository(self):
        for path in ('../outside', '/tmp/outside', 'a/../b', './file'):
            with self.assertRaises(pins.SourcePinError):
                pins.read_contained(self.root, path)


class ReplayInvariantTests(unittest.TestCase):
    def test_historical_manifests_and_receipts_are_unchanged(self):
        expected = {
            'research/community-reconciliation92-audit/MANIFEST.json': '5f501f3c118131e7d069f30ad77186eb2ad6961f9680a0ef105f4514ed41808a',
            'research/r420-two-sided-basis/SOURCES.json': 'd9810b0d139c5a1211fd2c1f0d142187cc1fca30026e1e7bc4f9ecfacf1596d1',
            'research/single-intersection-spectrum-audit/SOURCE.json': '610fb9887add31b4f597a39dc58b3beff0e14c91a5fd7ee340c3b2e7d4b0fb4c',
            'research/split-skip/SOURCE.json': '7c2b4646a3ecfef6f881da5c43e4bd0fa9a4d1b00548b8ab458d897e16735134',
            'research/community-frontier890-audit/CONTENT-COVERAGE.json': '6b185a9902652f893f3ebd8ada92d2f11b6de6533a9a4d11718a8a4496101128',
            'docs/research/community-frontier890-integration.json': '10c7756d470170451b7f333e830c4b94916f04a5e8affd8380de6e0b9adb9770',
        }
        for path, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_every_adapter_pins_the_maintenance_checker_before_import(self):
        expected = hashlib.sha256((PACKAGE / 'provenance_pins.py').read_bytes()).hexdigest()
        paths = ['research/community-reconciliation92-audit/verify.py',
                 'research/r420-two-sided-basis/verify.py',
                 'research/single-intersection-spectrum-audit/spectrum_audit.py',
                 'research/split-skip/witness.py', 'scripts/verify_pr_reconciliation.py']
        for path in paths:
            source = (ROOT / path).read_text()
            self.assertIn("!= '" + expected + "'", source)
            self.assertLess(source.index("!= '" + expected + "'"),
                            source.index('from provenance_pins import'))

    def test_regenerated_certificates_preserve_every_mathematical_field(self):
        for path, fields in [
            ('certificates/mixed-point-audit.json', {'source_sha256'}),
            ('certificates/rank-product-core.json', {'source_sha256'}),
            ('certificates/stage-pair-audit.json', {'source_sha256'}),
            ('research/single-intersection-spectrum-audit/RESULT.json',
             {'source_sha256', 'implementation_sha256'}),
        ]:
            original = json.loads((PACKAGE / 'snapshots' / (path + '.snapshot')).read_text())
            current = json.loads((ROOT / path).read_text())
            for field in fields:
                original.pop(field)
                current.pop(field)
            self.assertEqual(current, original, path)

    def test_makefile_only_appends_targets_to_retained_integration(self):
        original = (PACKAGE / 'snapshots/Makefile.snapshot').read_bytes()
        self.assertTrue(original.endswith(b'\n'))
        self.assertTrue((ROOT / 'Makefile').read_bytes().startswith(original))

    def test_spectral_function_is_unchanged_by_matrix_optimization(self):
        old = ast.parse((PACKAGE / 'snapshots/scripts/experiments/single_intersection.py.snapshot').read_text())
        current = ast.parse((ROOT / 'scripts/experiments/single_intersection.py').read_text())
        def function(tree):
            return next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'spectral_parity_bound')
        self.assertEqual(ast.dump(function(old)), ast.dump(function(current)))

    def test_optimized_matrix_matches_literal_definition(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        current = load_module('ci_current_single_intersection', ROOT / 'scripts/experiments/single_intersection.py')
        rng = Random(20261014)
        for h in range(2, 11):
            labels = list(range(1, 1 << h))
            for count in (1, min(9, len(labels)), min(80, len(labels))):
                selected = rng.sample(labels, count)
                for intersection in range(h + 1):
                    expected = [sum(1 << b for b, other in enumerate(selected)
                                    if label == other or (label & other).bit_count() == intersection)
                                for label in selected]
                    self.assertEqual(current.minor_rows(selected, intersection), expected)

    def test_fraction_conversion_preserves_exact_rank(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        current = load_module('ci_current_fused_block', ROOT / 'scripts/audit_fused_block.py')
        historical_path = PACKAGE / 'snapshots/scripts/audit_fused_block.py.snapshot'
        # Use a .py filename only in an isolated temporary directory; no source is changed.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'historical_fused.py'
            path.write_bytes(historical_path.read_bytes())
            old = load_module('ci_historical_fused_block', path)
            rng = Random(20261014)
            for rows in range(1, 8):
                for columns in range(1, 8):
                    matrix = [[Fraction(rng.randrange(-9, 10), rng.randrange(1, 7))
                               if (i + j) % 2 else rng.randrange(-9, 10)
                               for j in range(columns)] for i in range(rows)]
                    self.assertEqual(current.rational_rank(matrix), old.rational_rank(matrix))


class RegenerationRecorderTests(unittest.TestCase):
    """Synthetic fixtures test the recorder; they are not generator receipts."""
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.results = []
        manifest = self.root / pins.AMENDMENTS
        manifest.parent.mkdir(parents=True, exist_ok=True)
        # Fixtures start at the authenticated pre-replay state regardless of
        # whether the real checkout has already recorded a successful replay.
        fixture = json.loads((ROOT / pins.AMENDMENTS).read_text())
        fixture.pop('regenerated_artifacts', None)
        for row in fixture['bindings']:
            if row['group'] == 'frontier890-integrated' and row['path'] == regeneration.SPECTRUM:
                row['current_sha256'] = regeneration.ORIGINAL_CERTIFICATES[regeneration.SPECTRUM]
        manifest.write_text(json.dumps(fixture))
        for path, sources in regeneration.EXPECTED_UPDATES.items():
            snapshot = 'research/ci-provenance-maintenance/snapshots/' + path + '.snapshot'
            target = self.root / snapshot
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / snapshot).read_bytes())
            current = json.loads(target.read_text())
            for source in current['source_sha256']:
                relative = regeneration.effective_source_path(path, source)
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            for source in sources:
                target = self.root / source
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / source).read_bytes())
                current['source_sha256'][source] = hashlib.sha256(target.read_bytes()).hexdigest()
            if path == regeneration.SPECTRUM:
                source = 'research/single-intersection-spectrum-audit/spectrum_audit.py'
                target = self.root / source
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / source).read_bytes())
                current['implementation_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(current))
            self.results.append(target)

    def test_only_the_exact_reviewed_metadata_changes_are_accepted(self):
        self.assertEqual(len(regeneration.validated_regeneration(self.root)), 4)

    def test_recording_then_checking_changes_only_result_binding_and_receipts(self):
        target = self.root / pins.AMENDMENTS
        before = json.loads(target.read_text())
        regeneration.record_regeneration(self.root, record=True)
        regeneration.record_regeneration(self.root)
        after = json.loads(target.read_text())
        self.assertEqual(len(after.pop('regenerated_artifacts')), 4)
        for row in after['bindings']:
            if row['group'] == 'frontier890-integrated' and row['path'] == regeneration.SPECTRUM:
                row['current_sha256'] = next(item['current_sha256'] for item in before['bindings']
                                            if item['group'] == row['group'] and item['path'] == row['path'])
        self.assertEqual(after, before)

    def test_recording_is_idempotent_with_already_recorded_metadata(self):
        target = self.root / pins.AMENDMENTS
        regeneration.record_regeneration(self.root, record=True)
        recorded = target.read_bytes()
        regeneration.record_regeneration(self.root, record=True)
        regeneration.record_regeneration(self.root)
        self.assertEqual(target.read_bytes(), recorded)

    def test_all_read_paths_reject_symlinks_even_to_matching_bytes(self):
        paths = set(regeneration.REVIEWED_SOURCES)
        paths.add('research/single-intersection-spectrum-audit/spectrum_audit.py')
        for path in regeneration.EXPECTED_UPDATES:
            paths.add(path)
            paths.add('research/ci-provenance-maintenance/snapshots/' + path + '.snapshot')
            current = json.loads((self.root / path).read_text())
            for source in current['source_sha256']:
                paths.add(regeneration.effective_source_path(path, source))
        for relative in sorted(paths):
            target = self.root / relative
            original = target.read_bytes()
            alias = self.root / 'alias'
            alias.write_bytes(original)
            target.unlink()
            target.symlink_to(alias)
            with self.subTest(path=relative):
                with self.assertRaisesRegex(pins.SourcePinError, 'Aliased or escaping'):
                    regeneration.validated_regeneration(self.root)
            target.unlink()
            target.write_bytes(original)
            alias.unlink()

    def test_manifest_symlink_is_rejected_before_write(self):
        target = self.root / pins.AMENDMENTS
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / 'outside.json'
            original = target.read_bytes()
            outside.write_bytes(original)
            target.unlink()
            target.symlink_to(outside)
            with self.assertRaisesRegex(pins.SourcePinError, 'Aliased or escaping'):
                regeneration.record_regeneration(self.root, record=True)
            self.assertEqual(outside.read_bytes(), original)

    def test_unamended_dependency_corruption_with_unchanged_report_is_rejected(self):
        for certificate_path in regeneration.EXPECTED_UPDATES:
            current = json.loads((self.root / certificate_path).read_text())
            source = next(source for source in current['source_sha256']
                          if source not in regeneration.REVIEWED_SOURCES)
            path = self.root / regeneration.effective_source_path(certificate_path, source)
            original = path.read_bytes()
            path.write_bytes(original + b'\ncorruption')
            with self.subTest(path=source, certificate=certificate_path):
                with self.assertRaisesRegex(ValueError, 'Changed effective certificate source'):
                    regeneration.validated_regeneration(self.root)
            path.write_bytes(original)

    def test_each_changed_mathematical_result_is_rejected(self):
        for target in self.results:
            original = target.read_text()
            current = json.loads(original)
            current['status'] += ' CHANGED'
            target.write_text(json.dumps(current))
            with self.assertRaisesRegex(ValueError, 'mathematical or scope field'):
                regeneration.validated_regeneration(self.root)
            target.write_text(original)

    def test_coordinated_snapshot_and_fresh_mathematical_changes_are_rejected(self):
        for target in self.results:
            relative = target.relative_to(self.root).as_posix()
            snapshot = self.root / 'research/ci-provenance-maintenance/snapshots' / (relative + '.snapshot')
            original_result, original_snapshot = target.read_bytes(), snapshot.read_bytes()
            for path in (target, snapshot):
                changed = json.loads(path.read_text())
                changed['status'] += ' COORDINATED CHANGE'
                path.write_text(json.dumps(changed))
            with self.subTest(path=relative):
                with self.assertRaisesRegex(ValueError, 'immutable certificate snapshot'):
                    regeneration.validated_regeneration(self.root)
            target.write_bytes(original_result)
            snapshot.write_bytes(original_snapshot)

    def test_coordinated_source_and_reported_digest_changes_are_rejected(self):
        for source in regeneration.REVIEWED_SOURCES:
            path = self.root / source
            original_source = path.read_bytes()
            path.write_bytes(original_source + b'\n# unreviewed change\n')
            changed_results = []
            for result in self.results:
                data = json.loads(result.read_text())
                if source in regeneration.EXPECTED_UPDATES[result.relative_to(self.root).as_posix()]:
                    changed_results.append((result, result.read_bytes()))
                    data['source_sha256'][source] = hashlib.sha256(path.read_bytes()).hexdigest()
                    result.write_text(json.dumps(data))
            with self.subTest(path=source):
                with self.assertRaisesRegex(ValueError, 'Changed reviewed generator dependency'):
                    regeneration.validated_regeneration(self.root)
            path.write_bytes(original_source)
            for result, original in changed_results:
                result.write_bytes(original)

    def test_coordinated_implementation_and_reported_digest_changes_are_rejected(self):
        source = self.root / 'research/single-intersection-spectrum-audit/spectrum_audit.py'
        source.write_bytes(source.read_bytes() + b'\n# unreviewed change\n')
        result = self.root / regeneration.SPECTRUM
        data = json.loads(result.read_text())
        data['implementation_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        result.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Changed reviewed spectrum verifier'):
            regeneration.validated_regeneration(self.root)

    def test_unreviewed_source_digest_change_is_rejected(self):
        target = self.results[0]
        current = json.loads(target.read_text())
        current['source_sha256']['unreviewed.py'] = '0' * 64
        target.write_text(json.dumps(current))
        with self.assertRaisesRegex(ValueError, 'exactly the reviewed changes'):
            regeneration.validated_regeneration(self.root)

    def test_stale_implementation_digest_is_rejected(self):
        target = self.root / regeneration.SPECTRUM
        current = json.loads(target.read_text())
        current['implementation_sha256'] = '0' * 64
        target.write_text(json.dumps(current))
        with self.assertRaisesRegex(ValueError, 'not regenerated with the current verifier'):
            regeneration.validated_regeneration(self.root)


if __name__ == '__main__':
    unittest.main()
