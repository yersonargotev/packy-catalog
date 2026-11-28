"""On-demand coverage check at its public command."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class OnDemandCoverage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "catalog"
        shutil.copytree(ROOT, self.project, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.exceptions = self.project / "docs/on-demand-exceptions.json"

    def run_check(self):
        return subprocess.run([sys.executable, "-B", str(self.project / "scripts/check_on_demand_coverage.py")],
                              capture_output=True, text=True)

    def edit_exceptions(self, change):
        data = json.loads(self.exceptions.read_text())
        change(data["skills"])
        self.exceptions.write_text(json.dumps(data))

    def test_current_catalog_passes(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("on-demand coverage passed", result.stdout)

    def test_undeclared_skill_without_exception_fails(self):
        manifest = self.project / "packs/matty/pack.json"
        pack = json.loads(manifest.read_text())
        skill = next(r for r in pack["resources"] if r["id"] == "grilling")
        del skill["on_demand"]
        manifest.write_text(json.dumps(pack))
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("matty:grilling: declare on_demand", result.stderr)

    def test_stale_exception_fails(self):
        self.edit_exceptions(lambda skills: skills.update({"matty:grilling": "stale"}))
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("matty:grilling: declares on_demand; remove its exception", result.stderr)

    def test_unknown_skill_exception_fails(self):
        self.edit_exceptions(lambda skills: skills.update({"zzz:missing": "gone"}))
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("zzz:missing: exception names an unknown skill", result.stderr)


if __name__ == "__main__":
    unittest.main()
