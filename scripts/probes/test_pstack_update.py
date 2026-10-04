"""Exercise the opt-in pstack probe through its command-line interface."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROBE = Path(__file__).with_name('pstack-update.py')
PROJECT = Path(__file__).resolve().parents[2]


class PstackUpdateProbeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pstack-probe-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.baseline = self.root / 'baseline'
        self.candidate = self.root / 'candidate'
        self.scratch = self.root / 'scratch'
        self.scratch.mkdir()
        pack = self.baseline / 'packs/pstack'
        resources = []
        for name in ('sample', 'helper'):
            variants = []
            for host in ('claude', 'codex', 'opencode'):
                source = f'skills/{host}/{name}'
                folder = pack / source
                folder.mkdir(parents=True)
                (folder / 'SKILL.md').write_text(f'# {name}\n', encoding='utf-8')
                variants.append({'surface': host, 'source': source})
            resources.append({
                'kind': 'skill', 'id': name, 'source': f'skills/{name}',
                'description': name, 'requires': ['skill:helper'] if name == 'sample' else [],
                'notices': [], 'variants': variants,
                'bindings': [{'surface': host, 'name': name} for host in ('claude', 'codex', 'opencode')],
            })
        self.manifest = {'version': '1.0.0', 'origins': [{'commit': 'old'}], 'resources': resources}
        (pack / 'pack.json').write_text(json.dumps(self.manifest), encoding='utf-8')
        shutil.copytree(self.baseline, self.candidate)

    def run_probe(self, *args):
        result = subprocess.run(
            [sys.executable, str(PROBE), *args], text=True, capture_output=True,
            env={**os.environ, 'TMPDIR': str(self.scratch)}, timeout=30,
        )
        self.assertEqual(list(self.scratch.iterdir()), [], 'probe left temporary execution state')
        return result

    def contracts(self):
        return self.run_probe('contracts', '--project', str(self.candidate),
                              '--baseline', str(self.baseline),
                              '--preserve-surface', 'claude', '--preserve-surface', 'opencode')

    def write_manifest(self):
        (self.candidate / 'packs/pstack/pack.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def test_accepts_untouched_hosts_when_version_origin_and_codex_advance(self):
        self.manifest['version'] = '1.1.0'
        self.manifest['origins'][0]['commit'] = 'new'
        self.write_manifest()
        (self.candidate / 'packs/pstack/skills/codex/sample/SKILL.md').write_text('new Codex workflow\n')
        result = self.contracts()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('claude: preserved', result.stdout)
        self.assertIn('opencode: preserved', result.stdout)


    def test_rejects_preserved_host_content_drift(self):
        (self.candidate / 'packs/pstack/skills/claude/sample/SKILL.md').write_text('changed\n')
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('claude: content or executable-mode drift', result.stderr)

    def test_rejects_preserved_host_executable_mode_drift(self):
        path = self.candidate / 'packs/pstack/skills/opencode/sample/SKILL.md'
        path.chmod(path.stat().st_mode ^ 0o100)
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('opencode: content or executable-mode drift', result.stderr)

    def test_rejects_changed_inherited_dependency(self):
        self.manifest['resources'][0]['requires'] = []
        self.write_manifest()
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('claude: contract drift', result.stderr)

    def test_rejects_changed_variant_contract(self):
        self.manifest['resources'][0]['variants'][0]['description'] = 'different purpose'
        self.write_manifest()
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('claude: contract drift', result.stderr)

    def test_rejects_removed_surface_binding(self):
        self.manifest['resources'][0]['bindings'].pop(0)
        self.write_manifest()
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('claude: resource selection drift', result.stderr)

    def test_rejects_added_surface_resource(self):
        extra = json.loads(json.dumps(self.manifest['resources'][1]))
        extra['id'] = 'extra'
        for binding in extra['bindings']:
            binding['name'] = 'extra'
        self.manifest['resources'].append(extra)
        self.write_manifest()
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('claude: resource selection drift', result.stderr)

    def test_plan_scenarios_pass_without_mutating_owned_helpers(self):
        paths = [PROJECT / 'packs/pstack/skills' / host / 'poteto-mode/scripts/check-plan.mjs'
                 for host in ('', 'codex')]
        before = [p.read_bytes() for p in paths]
        result = self.run_probe('plans', '--project', str(PROJECT))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('common: 3 plan scenarios passed', result.stdout)
        self.assertIn('codex: 3 plan scenarios passed', result.stdout)
        self.assertEqual([p.read_bytes() for p in paths], before)


    def test_compares_effective_dependencies_instead_of_shadowed_common_values(self):
        for variant in self.manifest['resources'][0]['variants']:
            variant['requires'] = []
        self.write_manifest()
        shutil.copyfile(self.candidate / 'packs/pstack/pack.json', self.baseline / 'packs/pstack/pack.json')
        self.manifest['resources'][0]['requires'] = []
        self.write_manifest()
        result = self.contracts()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_drift_in_referenced_notice(self):
        notice = {'kind': 'notice', 'id': 'license', 'source': 'LICENSE',
                  'bindings': [], 'requires': [], 'notices': []}
        self.manifest['resources'].append(notice)
        self.manifest['resources'][0]['notices'] = ['notice:license']
        self.write_manifest()
        shutil.copyfile(self.candidate / 'packs/pstack/pack.json', self.baseline / 'packs/pstack/pack.json')
        (self.baseline / 'packs/pstack/LICENSE').write_text('original license\n')
        (self.candidate / 'packs/pstack/LICENSE').write_text('changed license\n')
        result = self.contracts()
        self.assertEqual(result.returncode, 1)
        self.assertIn('drift at notice:license', result.stderr)

    def test_failing_checker_removes_execution_state_without_touching_pack(self):
        folder = self.candidate / 'packs/pstack/skills/poteto-mode/scripts'
        folder.mkdir(parents=True)
        helper = folder / 'check-plan.mjs'
        body = "import fs from 'node:fs'; fs.writeFileSync('touched.txt', 'temporary'); process.exit(7);"
        helper.write_text(body)
        result = self.run_probe('plans', '--project', str(self.candidate))
        self.assertEqual(result.returncode, 1)
        self.assertIn('common/valid', result.stderr)
        self.assertIn('got exit 7', result.stderr)
        self.assertEqual(helper.read_text(), body)
        self.assertEqual(list(self.candidate.rglob('touched.txt')), [])

    def test_checker_that_accepts_everything_fails_the_negative_scenario(self):
        folder = self.candidate / 'packs/pstack/skills/poteto-mode/scripts'
        folder.mkdir(parents=True)
        (folder / 'check-plan.mjs').write_text("console.log('1 PR sections, 0 problems');")
        result = self.run_probe('plans', '--project', str(self.candidate))
        self.assertEqual(result.returncode, 1)
        self.assertIn('common/obsolete-cadence', result.stderr)


if __name__ == '__main__':
    unittest.main()
