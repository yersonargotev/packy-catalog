"""Regression scenarios at the public ordinary test command."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
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

    def run_checks(self, **environment):
        result = subprocess.run([str(self.project / "scripts/test.sh")], cwd=self.project,
                                env={**os.environ, "PACKY_TEST_ARCHIVE": str(self.archive),
                                     "PYTHONPATH": str(Path(yaml.__file__).parent.parent), **environment},
                                text=True, capture_output=True, timeout=30)
        self.assertEqual({helper: helper.read_bytes() for helper in self.helpers}, self.before)
        return result

    def test_fixture_identity_is_required_for_every_commit(self):
        self.fixture.write_text('''import subprocess, tempfile, unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_identity(self):
        with tempfile.TemporaryDirectory() as repo:
            def git(*args):
                return subprocess.run(["git", "-C", repo, *args], text=True,
                                      capture_output=True, timeout=10)
            prepare(["git", "-C", repo, "init", "-q"], label="git init")
            for _ in range(2):
                missing = git("commit", "--allow-empty", "-m", "Missing identity")
                self.assertEqual(missing.returncode, 128, missing.stderr)
                self.assertIn("auto-detection is disabled", missing.stderr)
                prepare(["git", "-C", repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "commit", "--allow-empty", "-m", "Fixture"], label="git commit")
''')
        result = self.run_checks(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                                 GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="user.useConfigOnly",
                                 GIT_CONFIG_VALUE_0="false")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fixture_command_failure_exposes_captured_cause(self):
        child = Path(self.temp.name) / "controlled-git.py"
        child.write_text("import sys\nsys.stderr.buffer.write(b'fatal: author identity unknown\\xff\\n')\nsys.exit(128)\n")
        self.fixture.write_text(f'''import unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        prepare([{sys.executable!r}, {str(child)!r}], label="git commit")
''')
        result = self.run_checks()
        self.assertEqual(result.returncode, 1)
        self.assertIn("fixture command git commit: exit status 128", result.stderr)
        self.assertIn("fatal: author identity unknown", result.stderr)

    def test_fixture_deadline_cleans_descendants_and_preserves_unrelated_state(self):
        late = Path(self.temp.name) / "late-write"
        child = Path(self.temp.name) / "controlled-slow.py"
        descendant = f"import time; from pathlib import Path; time.sleep(1.5); Path({str(late)!r}).touch()"
        child.write_text("import subprocess, sys, time\n"
                         f"subprocess.Popen([sys.executable, '-c', {descendant!r}])\n"
                         "print('waiting for fixture input', file=sys.stderr, flush=True)\ntime.sleep(30)\n")
        self.fixture.write_text(f'''import tempfile, unittest
from pathlib import Path
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        with tempfile.TemporaryDirectory() as owned:
            print("OWNED=" + owned, flush=True)
            prepare([{sys.executable!r}, {str(child)!r}], label="slow fixture", cwd=owned, timeout=0.5)
''')
        marker = Path(self.temp.name) / "unrelated-marker"
        marker.write_text("preserve")
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            result = self.run_checks()
            self.assertEqual(result.returncode, 1)
            self.assertIn("fixture command slow fixture: deadline expired", result.stderr)
            self.assertIn("waiting for fixture input", result.stderr)
            owned = [line.removeprefix("OWNED=") for line in result.stdout.splitlines() if line.startswith("OWNED=")]
            self.assertEqual(len(owned), 1, result.stdout)
            self.assertFalse(Path(owned[0]).exists())
            time.sleep(1.5)
            self.assertFalse(late.exists())
            self.assertIsNone(unrelated.poll())
            self.assertEqual(marker.read_text(), "preserve")
        finally:
            unrelated.terminate()
            unrelated.wait(timeout=5)

    def test_fixture_spawn_failure_has_distinct_diagnostic(self):
        self.fixture.write_text('''import os, unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        prepare([os.environ["MISSING_EXECUTABLE"]], label="git init")
''')
        missing = str(Path(self.temp.name) / "private-missing-executable")
        result = self.run_checks(MISSING_EXECUTABLE=missing)
        self.assertEqual(result.returncode, 1)
        self.assertIn("fixture command git init: spawn failed", result.stderr)
        self.assertIn("No such file or directory", result.stderr)
        self.assertNotIn(missing, result.stderr)

    def test_fixture_requires_a_finite_positive_deadline_before_spawn(self):
        marker = Path(self.temp.name) / "must-not-run"
        child = Path(self.temp.name) / "invalid-deadline.py"
        child.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
        self.fixture.write_text(f'''import os, unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        prepare([{sys.executable!r}, {str(child)!r}], label="invalid deadline", timeout=float(os.environ["DEADLINE"]))
''')
        for value in ("0", "-1", "inf", "nan"):
            with self.subTest(deadline=value):
                result = self.run_checks(DEADLINE=value)
                self.assertEqual(result.returncode, 1)
                self.assertIn("deadline must be finite and positive", result.stderr)
                self.assertFalse(marker.exists())

    def test_fixture_diagnostics_redact_declared_data_and_credentials(self):
        child = Path(self.temp.name) / "controlled-sensitive.py"
        child.write_text("import os, sys, time\n"
                         "print('fatal: author identity unknown; ' + sys.argv[1] + ' ' + os.environ['FIXTURE_TOKEN'], file=sys.stderr, flush=True)\n"
                         "if os.environ['SLOW']: time.sleep(30)\n"
                         "sys.exit(128)\n")
        self.fixture.write_text(f'''import os, unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        value = os.environ["PRIVATE_DATA"]
        prepare([{sys.executable!r}, {str(child)!r}, value], label="git commit", redact=[value], timeout=0.5)
''')
        for slow in ("", "1"):
            with self.subTest(timeout=bool(slow)):
                result = self.run_checks(PRIVATE_DATA="private-argument-73", FIXTURE_TOKEN="credential-73",
                                         UNRELATED_ENV="environment-must-not-be-dumped", SLOW=slow)
                self.assertEqual(result.returncode, 1)
                self.assertIn("fatal: author identity unknown; [redacted] [redacted]", result.stderr)
                for value in ("private-argument-73", "credential-73", "environment-must-not-be-dumped"):
                    self.assertNotIn(value, result.stdout + result.stderr)

    def test_fixture_success_returns_output_and_releases_descendants(self):
        late = Path(self.temp.name) / "success-late-write"
        child = Path(self.temp.name) / "controlled-success.py"
        descendant = f"import time; from pathlib import Path; time.sleep(1.5); Path({str(late)!r}).touch()"
        child.write_text("import subprocess, sys\n"
                         f"subprocess.Popen([sys.executable, '-c', {descendant!r}], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
                         "print('fixture data [y/N]')\n")
        self.fixture.write_text(f'''import unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        result = prepare([{sys.executable!r}, {str(child)!r}], label="successful fixture")
        self.assertEqual(result, "fixture data [y/N]\\n")
''')
        result = self.run_checks()
        self.assertEqual(result.returncode, 0, result.stderr)
        time.sleep(1.5)
        self.assertFalse(late.exists())

    def test_failed_fixture_retains_primary_error_when_cleanup_also_fails(self):
        late = Path(self.temp.name) / "failure-late-write"
        child = Path(self.temp.name) / "controlled-failure.py"
        descendant = f"import time; from pathlib import Path; time.sleep(1.5); Path({str(late)!r}).touch()"
        child.write_text("import subprocess, sys\n"
                         f"subprocess.Popen([sys.executable, '-c', {descendant!r}])\n"
                         "print('fatal: fixture cause', file=sys.stderr)\nsys.exit(128)\n")
        self.fixture.write_text(f'''import tempfile, unittest
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_prepare(self):
        owned = tempfile.TemporaryDirectory()
        print("OWNED=" + owned.name, flush=True)
        self.addCleanup(owned.cleanup)
        self.addCleanup(self.failing_cleanup)
        prepare([{sys.executable!r}, {str(child)!r}], label="git commit", timeout=0.5)
    def failing_cleanup(self):
        raise RuntimeError("secondary fixture cleanup failure")
''')
        result = self.run_checks()
        self.assertEqual(result.returncode, 1)
        self.assertIn("fixture command git commit: exit status 128", result.stderr)
        self.assertIn("fatal: fixture cause", result.stderr)
        self.assertIn("secondary fixture cleanup failure", result.stderr)
        owned = [line.removeprefix("OWNED=") for line in result.stdout.splitlines() if line.startswith("OWNED=")]
        self.assertEqual(len(owned), 1, result.stdout)
        self.assertFalse(Path(owned[0]).exists())
        time.sleep(1.5)
        self.assertFalse(late.exists())

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

    def test_conflicting_caller_git_state_is_ignored_and_preserved(self):
        caller = Path(self.temp.name) / "caller"
        caller.mkdir()
        config = caller / ".gitconfig"
        config.write_text("[user]\n name = Ambient\n email = ambient@example.invalid\n"
                          "[commit]\n gpgsign = true\n[core]\n bare = true\n")
        before = config.read_bytes()
        self.fixture.write_text('''import os, tempfile, unittest
from pathlib import Path
from scripts.fixture_commands import prepare
class Fixture(unittest.TestCase):
    def test_isolation(self):
        home = Path.home()
        self.assertNotEqual(str(home), os.environ["CALLER_HOME"])
        home.mkdir(parents=True, exist_ok=True)
        (home / "owned-marker").write_text("fixture")
        print("OWNED_HOME=" + str(home), flush=True)
        with tempfile.TemporaryDirectory() as repo:
            def git(*args):
                return prepare(["git", "-C", repo, *args], label="git isolation fixture").strip()
            git("init", "-q")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "--allow-empty", "-m", "Fixture")
            self.assertEqual(git("log", "-1", "--format=%an <%ae>|%cn <%ce>"),
                             "Fixture <fixture@example.invalid>|Fixture <fixture@example.invalid>")
            if os.environ.get("FAIL_FIXTURE"):
                self.fail("controlled failure after fixture commit")
''')
        for fail in ("", "1"):
            with self.subTest(failure=bool(fail)):
                result = self.run_checks(
                    HOME=str(caller), XDG_CONFIG_HOME=str(caller), CALLER_HOME=str(caller),
                    GIT_CONFIG_GLOBAL=str(config), GIT_CONFIG_SYSTEM=str(config),
                    GIT_CONFIG_NOSYSTEM="0", GIT_CONFIG_COUNT="2",
                    GIT_CONFIG_KEY_0="user.useConfigOnly", GIT_CONFIG_VALUE_0="false",
                    GIT_CONFIG_KEY_1="core.bare", GIT_CONFIG_VALUE_1="true",
                    GIT_CONFIG_PARAMETERS="'core.bare=true'", GIT_CONFIG=str(config),
                    GIT_AUTHOR_NAME="Ambient", GIT_AUTHOR_EMAIL="ambient@example.invalid",
                    GIT_COMMITTER_NAME="Ambient", GIT_COMMITTER_EMAIL="ambient@example.invalid",
                    EMAIL="ambient@example.invalid", GIT_DIR=str(caller / "do-not-create"),
                    GIT_WORK_TREE=str(caller), FAIL_FIXTURE=fail)
                self.assertEqual(result.returncode, 1 if fail else 0, result.stdout + result.stderr)
                if fail:
                    self.assertIn("controlled failure after fixture commit", result.stderr)
                homes = [line.removeprefix("OWNED_HOME=") for line in result.stdout.splitlines()
                         if line.startswith("OWNED_HOME=")]
                self.assertEqual(len(homes), 1, result.stdout + result.stderr)
                self.assertFalse(Path(homes[0]).exists())
                self.assertEqual(config.read_bytes(), before)
                self.assertEqual(list(caller.iterdir()), [config])

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
