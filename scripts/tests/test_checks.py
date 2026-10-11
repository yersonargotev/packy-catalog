"""Regression scenarios at the public ordinary test command."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class OrdinaryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "catalog"
        shutil.copytree(ROOT, self.project, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        # A single controlled suite avoids invoking this regression suite recursively.
        shutil.rmtree(self.project / "scripts/tests")
        (self.project / "scripts/tests").mkdir()
        self.fixture = self.project / "scripts/tests/test_fixture.py"
        self.fixture.write_text("import unittest\nclass Fixture(unittest.TestCase):\n    def test_pass(self):\n        pass\n")
        self.helpers = sorted((self.project / "packs/pstack").rglob("check-plan.mjs"))
        for helper in self.helpers:
            helper.write_text("#!/bin/sh\nexit 0\n")
        self.before = {helper: helper.read_bytes() for helper in self.helpers}
        self.archive = Path(self.temp.name) / "unused-fixture.tar.gz"
        self.archive.touch()

    def run_checks(self):
        result = subprocess.run([str(self.project / "scripts/test.sh")], cwd=self.project,
                                env={**os.environ, "PACKY_TEST_ARCHIVE": str(self.archive)},
                                text=True, capture_output=True, timeout=30)
        self.assertEqual({helper: helper.read_bytes() for helper in self.helpers}, self.before)
        return result

    def test_helper_execution_fails_even_when_its_status_is_ignored(self):
        helper = self.helpers[0].relative_to(self.project).as_posix()
        self.fixture.write_text(f'''import subprocess, unittest
class Fixture(unittest.TestCase):
    def test_ignored_helper_failure(self):
        subprocess.run(["bash", "{helper}"], check=False)
''')
        result = self.run_checks()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Pack helper executed", result.stderr)

    def test_ordinary_tests_pass_without_changing_pack_helpers(self):
        result = self.run_checks()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ordinary suite passed with 4 Pack helper execution sentinels", result.stdout)

    def test_ordinary_test_failure_is_preserved(self):
        self.fixture.write_text("import unittest\nclass Fixture(unittest.TestCase):\n    def test_fail(self):\n        self.fail('controlled failure')\n")
        result = self.run_checks()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("controlled failure", result.stderr)

    def test_invalid_python_is_rejected_before_running_tests(self):
        invalid = self.project / "scripts/probes/invalid.py"
        invalid.write_text("def invalid(:\n")
        result = self.run_checks()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("scripts/probes/invalid.py", result.stderr)

    def test_invalid_shell_entry_point_is_rejected_before_running_tests(self):
        invalid = self.project / "scripts/invalid.sh"
        invalid.write_text("if\n")
        result = self.run_checks()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("scripts/invalid.sh", result.stderr)

    def test_invalid_workflow_shell_is_rejected_before_running_tests(self):
        workflow = self.project / ".github/workflows/validate.yml"
        data = yaml.load(workflow.read_text(), Loader=yaml.BaseLoader)
        data["jobs"]["validate"]["steps"][-1]["run"] = "if\n"
        workflow.write_text(yaml.safe_dump(data, sort_keys=False))
        result = self.run_checks()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(".github/workflows/validate.yml", result.stderr)
