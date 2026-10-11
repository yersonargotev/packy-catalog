"""Controlled subprocess fixtures; these tests never execute Pack content."""
import importlib.util
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "probes/content_probe_process.py"
spec = importlib.util.spec_from_file_location("probe_process", SCRIPT)
process = importlib.util.module_from_spec(spec)
spec.loader.exec_module(process)


class ProbeProcessTests(unittest.TestCase):
    def run_child(self, source, **kwargs):
        with tempfile.TemporaryDirectory() as scratch:
            return process.run_child([sys.executable, "-c", source], cwd=Path(scratch),
                                     env={"HOME": scratch, "PATH": ""}, timeout=1, **kwargs)

    def test_exact_prompt_is_answered_through_terminal_stdin(self):
        result = self.run_child(
            "import os,json; assert os.isatty(0); "
            "print('Approve fixture? [y/N] ',end='',flush=True); "
            "assert input() == 'y'; print(json.dumps({'result':'passed'}))",
            approval="Approve fixture? [y/N] ")
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '{"result": "passed"}\n')

    def test_unexpected_prompt_is_never_approved(self):
        with self.assertRaisesRegex(RuntimeError, "unexpected child approval"):
            self.run_child("print('Activate personal state? [y/N] ',end='',flush=True); input()",
                           approval="Approve fixture? [y/N] ")

    def test_structured_preview_before_prompt_is_preserved(self):
        result = self.run_child(
            "print('{\"report\":\"preview\"}'); "
            "print('Approve fixture? [y/N] ',end='',flush=True); "
            "assert input() == 'y'; print('{\"result\":\"passed\"}')",
            approval="Approve fixture? [y/N] ")
        self.assertEqual(result[1], '{"report":"preview"}\n{"result":"passed"}\n')

    def test_missing_prompt_cannot_claim_success(self):
        with self.assertRaisesRegex(RuntimeError, "without expected approval"):
            self.run_child("print('{}')", approval="Approve fixture? [y/N] ")

    def test_child_failure_preserves_diagnostic_and_status(self):
        result = self.run_child("import sys; print('fixture failed',file=sys.stderr); sys.exit(7)")
        self.assertEqual(result, (7, "", "fixture failed\n"))

    def test_timeout_cleans_descendants(self):
        with tempfile.TemporaryDirectory() as scratch:
            sentinel = Path(scratch) / "late-write"
            source = ("import subprocess,time; subprocess.Popen([" + repr(sys.executable) +
                      ",'-c'," + repr("import time; from pathlib import Path; time.sleep(2); Path(" +
                                      repr(str(sentinel)) + ").touch()") + "]); time.sleep(30)")
            with self.assertRaisesRegex(RuntimeError, "timeout"):
                self.run_child(source)
            time.sleep(2)
            self.assertFalse(sentinel.exists())

    def test_repeated_prompt_is_never_approved(self):
        with self.assertRaisesRegex(RuntimeError, "unexpected child approval"):
            self.run_child("print('Approve fixture? [y/N] ',end='',flush=True); input(); "
                           "print('Approve fixture? [y/N] ',end='',flush=True); input()",
                           approval="Approve fixture? [y/N] ")


class ProbeCommandTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.temp = self.root / "owned-temp"
        self.temp.mkdir()
        self.catalog = self.root / "catalog"
        scripts = self.catalog / "scripts"
        (scripts / "probes").mkdir(parents=True)
        for name in ("content-probes.py", "content_probe_process.py"):
            shutil.copyfile(SCRIPT.parent / name, scripts / "probes" / name)
        shutil.copyfile(SCRIPT.parents[1] / "packy_tool.py", scripts / "packy_tool.py")
        self.command = [sys.executable, "-B", str(scripts / "probes/content-probes.py"), "--scenario", "adoption"]
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name in ("git", "curl", "uname"):
            (self.bin / name).symlink_to(shutil.which(name))
        self.env = {"PATH": str(self.bin), "TMPDIR": str(self.temp), "HOME": str(self.root),
                    "GH_TOKEN": "must-not-reach-child"}

    def invoke(self):
        result = subprocess.run(self.command, env=self.env, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        import json
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["result"], "failed")
        self.assertEqual(list(self.temp.iterdir()), [])
        return evidence

    def test_missing_prerequisite_fails_and_cleans_owned_state(self):
        (self.bin / "git").unlink()
        evidence = self.invoke()
        self.assertIn("missing prerequisite: git", evidence["error"])

    def test_optional_html_packing_requires_node_and_cleans_owned_state(self):
        self.command = [*self.command[:-1], "claude", "--html-pack"]
        evidence = self.invoke()
        self.assertIn("missing prerequisite: node", evidence["error"])

    def test_dirty_candidate_fails_without_acquisition(self):
        subprocess.run([shutil.which("git"), "init", "-q", str(self.catalog)], check=True)
        evidence = self.invoke()
        self.assertIn("clean committed Catalog candidate", evidence["error"])
        self.assertEqual(len(evidence["commands"]), 1)

    def test_interruption_cleans_state_processes_and_strips_token(self):
        ready = self.root / "ready"
        late = self.root / "late"
        (self.bin / "git").unlink()
        child = "import time; from pathlib import Path; time.sleep(2); Path(" + repr(str(late)) + ").touch()"
        (self.bin / "git").write_text(
            "#!" + sys.executable + "\nimport os,subprocess,time\n"
            "assert 'GH_TOKEN' not in os.environ\n"
            "subprocess.Popen([" + repr(sys.executable) + ",'-c'," + repr(child) + "])\n"
            "from pathlib import Path\nPath(" + repr(str(ready)) + ").touch()\ntime.sleep(30)\n")
        (self.bin / "git").chmod(0o700)
        child = subprocess.Popen(self.command, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(ready.exists(), "controlled child did not start")
            child.send_signal(signal.SIGTERM)
            stdout, stderr = child.communicate(timeout=5)
            self.assertNotEqual(child.returncode, 0, stderr)
            self.assertIn('probe interrupted by signal', stdout)
            self.assertEqual(list(self.temp.iterdir()), [])
            time.sleep(2)
            self.assertFalse(late.exists())
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
            child.stdout.close()
            child.stderr.close()


if __name__ == "__main__":
    unittest.main()
