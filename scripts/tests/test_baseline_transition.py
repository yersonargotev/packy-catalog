"""Version comparison across the explicitly reviewed engine contract cut."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('baseline_transition', ROOT / 'scripts/baseline_transition.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def pack(version='1.0.0', description='fixture', digest='a', mode='100644'):
    return {'manifest': {'id': 'fixture', 'version': version, 'description': description},
            'files': [{'path': 'pack.json', 'mode': '100644', 'sha256': 'ignored'},
                      {'path': 'skills/example/SKILL.md', 'mode': mode, 'sha256': digest}]}


class TransitionVersions(unittest.TestCase):
    def test_changed_bytes_or_mode_require_strictly_greater_version(self):
        for current in (pack(digest='b'), pack(mode='100755'), pack(description='changed')):
            with self.subTest(current=current), self.assertRaisesRegex(ValueError, 'requires a version greater'):
                module.compare_packs({'fixture': current}, {'fixture': pack()})
        module.compare_packs({'fixture': pack('1.0.1', digest='b')}, {'fixture': pack()})

    def test_unchanged_content_must_keep_version_and_new_pack_is_allowed(self):
        with self.assertRaisesRegex(ValueError, 'must retain version'):
            module.compare_packs({'fixture': pack('1.0.1')}, {'fixture': pack()})
        module.compare_packs({'fixture': pack()}, {'fixture': pack()})
        module.compare_packs({'fixture': pack()}, {})


class VersionOrdering(unittest.TestCase):
    def test_semver_prerelease_and_build_metadata_ordering(self):
        self.assertLess(module.version_key('1.0.0-rc.2'), module.version_key('1.0.0-rc.10'))
        self.assertLess(module.version_key('1.0.0-rc.10'), module.version_key('1.0.0'))
        self.assertEqual(module.version_key('1.0.0+one'), module.version_key('1.0.0+two'))
        with self.assertRaises(ValueError):
            module.version_key('1.0.0-01')
