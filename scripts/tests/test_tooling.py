"""Contract tests for the documented Catalog entry points and workflow guard."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = os.environ.get("PACKY_TEST_ARCHIVE")


@unittest.skipUnless(ARCHIVE, "set PACKY_TEST_ARCHIVE to the pinned native release archive")
class ToolingContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.project = self.work / "catalog"
        shutil.copytree(ROOT, self.project, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.bin = self.work / "bin"
        self.bin.mkdir()
        for name in ("bash", "python3", "uname", "git"):
            (self.bin / name).symlink_to(shutil.which(name))
        curl = self.bin / "curl"
        curl.write_text(f'''#!{sys.executable}
import os, pathlib, shutil, sys
if os.environ.get("TEST_DOWNLOAD_FAIL"):
    sys.exit(22)
args = sys.argv[1:]
shutil.copyfile(os.environ["PACKY_TEST_ARCHIVE"], args[args.index("--output") + 1])
with open(os.environ["TEST_DOWNLOAD_LOG"], "a") as log:
    log.write(args[-1] + "\\n")
''')
        curl.chmod(0o755)
        (self.bin / "packy").write_text("#!/bin/sh\necho unexpected-PATH-fallback >&2\nexit 99\n")
        (self.bin / "packy").chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(Path(yaml.__file__).parent.parent), "HOME": str(self.work / "home"),
                    "PACKY_CACHE_DIR": str(self.work / "cache"), "PACKY_TEST_ARCHIVE": str(Path(ARCHIVE).resolve()),
                    "TEST_DOWNLOAD_LOG": str(self.work / "downloads")}

    def run_cli(self, *args):
        return subprocess.run([str(self.project / "scripts/packy.sh"), *args], env=self.env,
                              text=True, capture_output=True, timeout=30)

    def test_cold_and_warm_use_declared_release_without_go_or_path_fallback(self):
        for _ in range(2):
            result = self.run_cli("version", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {
                "schema_version": 1, "report": "packy-version", "version": "v0.2.27",
                "source_commit": "1b8d04ddee510b24adcb12906914240bd7063aa6"})
        self.assertEqual(len((self.work / "downloads").read_text().splitlines()), 1)
        self.assertFalse((self.work / "home").exists())

    def make_fixture(self):
        shutil.rmtree(self.project / "packs")
        pack = self.project / "packs/demo"
        pack.mkdir(parents=True)
        source = json.loads((ROOT / "packs/argote/pack.json").read_text())
        guidance = source["resources"][0]
        guidance["bindings"] = [binding for binding in guidance["bindings"] if binding["surface"] == "codex"]
        guidance["source"] = "instructions/guidance.md"
        guidance["bindings"][0]["capabilities"][0]["project_instruction"]["source"] = "instructions/guidance.md"
        manifest = {"schema_version": 3, "id": "demo", "version": "1.0.0", "description": "Test fixture",
                    "selectable": True, "surfaces": ["codex"], "readiness_obligations": [],
                    "external_requirements": [], "origins": [], "resources": [guidance]}
        (pack / "pack.json").write_text(json.dumps(manifest))
        (pack / "instructions").mkdir()
        (pack / "instructions/guidance.md").write_text("# Test guidance\n")
        return pack

    def test_local_validation_and_baseline_are_source_free_and_inert(self):
        pack = self.make_fixture()
        baseline = self.work / "baseline"
        shutil.copytree(self.project, baseline)
        command = [str(self.project / "scripts/validate.sh"), str(baseline), "--json"]
        valid = subprocess.run(command, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(json.loads(valid.stdout)["result"], "valid")
        (pack / "instructions/guidance.md").write_text("# Changed guidance\n")
        invalid = subprocess.run(command, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertEqual(json.loads(invalid.stdout)["result"], "invalid")
        manifest = json.loads((pack / "pack.json").read_text())
        manifest["version"] = "1.0.1"
        (pack / "pack.json").write_text(json.dumps(manifest))
        bumped = subprocess.run(command, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(bumped.returncode, 0, bumped.stderr)
        self.assertEqual(json.loads(bumped.stdout)["result"], "valid")
        manifest["schema_version"] = 999
        (pack / "pack.json").write_text(json.dumps(manifest))
        malformed = subprocess.run(command, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(malformed.returncode, 0)
        self.assertEqual(json.loads(malformed.stdout)["result"], "invalid")

    def test_guard_rejects_catalog_script_execution_with_publication_authority(self):
        workflow = self.project / ".github/workflows/publish.yml"
        workflow.write_text(workflow.read_text() + "\n      - name: Execute untrusted script\n        run: ./scripts/untrusted.py\n")
        result = subprocess.run([str(self.project / "scripts/validate-publication-workflows.sh")],
                                env=self.env, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def write_pin(self, pin):
        (self.project / "packy-release.json").write_text(json.dumps(pin))

    def pin(self):
        return json.loads((self.project / "packy-release.json").read_text())

    def assert_rejected(self, result, diagnostic):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn("unexpected-PATH-fallback", result.stderr)

    def test_malformed_pin_is_rejected_before_download(self):
        self.write_pin({"version": "latest"})
        self.assert_rejected(self.run_cli("version", "--json"), "malformed release declaration")
        self.assertFalse((self.work / "downloads").exists())

    def test_unsupported_platform_is_rejected_before_download(self):
        (self.bin / "uname").unlink()
        (self.bin / "uname").write_text("#!/bin/bash\necho unsupported\n")
        (self.bin / "uname").chmod(0o755)
        self.assert_rejected(self.run_cli("version", "--json"), "unsupported Packy platform")
        self.assertFalse((self.work / "downloads").exists())

    def test_unavailable_cold_download_does_not_fall_back(self):
        self.env["TEST_DOWNLOAD_FAIL"] = "1"
        self.assert_rejected(self.run_cli("version", "--json"), "non-zero exit status")
        self.assertEqual(list((self.work / "cache").iterdir()), [])

    def test_warm_cache_does_not_require_artifact_network(self):
        self.assertEqual(self.run_cli("version", "--json").returncode, 0)
        self.env["TEST_DOWNLOAD_FAIL"] = "1"
        self.assertEqual(self.run_cli("version", "--json").returncode, 0)

    def test_checksum_mismatch_is_rejected_before_any_execution(self):
        archive = self.work / "untrusted.tar.gz"
        archive.write_bytes(b"not the declared release")
        self.env["PACKY_TEST_ARCHIVE"] = str(archive)
        self.assert_rejected(self.run_cli("version", "--json"), "checksum mismatch")
        self.assertEqual(list((self.work / "cache").iterdir()), [])

    def test_embedded_version_and_commit_must_match_pin(self):
        original = self.pin()
        for key, mismatch in (("version", "v0.0.1"), ("source_commit", "0" * 40)):
            with self.subTest(key=key):
                self.write_pin({**original, key: mismatch})
                self.assert_rejected(self.run_cli("version", "--json"), "identity mismatch")
                self.assertEqual(list((self.work / "cache").iterdir()), [])

    def test_corrupt_and_partial_cache_fail_without_redownload(self):
        self.assertEqual(self.run_cli("version", "--json").returncode, 0)
        archive = next((self.work / "cache").glob("*/release.tar.gz"))
        archive.write_bytes(b"corrupted")
        self.assert_rejected(self.run_cli("version", "--json"), "checksum mismatch")
        archive.unlink()
        self.assert_rejected(self.run_cli("version", "--json"), "partial or unsafe")
        self.assertEqual(len((self.work / "downloads").read_text().splitlines()), 1)

    def test_all_four_platforms_select_only_declared_artifact(self):
        for system, machine, key in (("Darwin", "x86_64", "darwin_amd64"), ("Darwin", "arm64", "darwin_arm64"),
                                     ("Linux", "x86_64", "linux_amd64"), ("Linux", "aarch64", "linux_arm64")):
            with self.subTest(key=key):
                (self.bin / "uname").unlink()
                (self.bin / "uname").write_text(f'#!/bin/bash\nif [[ "$1" == -s ]]; then echo {system}; else echo {machine}; fi\n')
                (self.bin / "uname").chmod(0o755)
                result = self.run_cli("version", "--json")
                # The native archive can execute only on its real platform; others reject its checksum.
                if result.returncode:
                    self.assert_rejected(result, "checksum mismatch")
                self.assertTrue((self.work / "downloads").read_text().splitlines()[-1].endswith(
                    "packy_v0.2.27_" + key + ".tar.gz"))

    def workflow(self):
        return yaml.load((self.project / ".github/workflows/publish.yml").read_text(), Loader=yaml.BaseLoader)

    def build_with_preparation_workflow(self):
        self.make_fixture()
        for args in (("init", str(self.project)), ("-C", str(self.project), "add", "."),
                     ("-C", str(self.project), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-m", "Fixture")):
            subprocess.run(["git", *args], env=self.env, check=True, capture_output=True)
        commit = subprocess.check_output(["git", "-C", str(self.project), "rev-parse", "HEAD"], env=self.env, text=True).strip()
        self.env.update({"CATALOG_COMMIT": commit, "GITHUB_WORKSPACE": str(self.work),
                         "GITHUB_REPOSITORY": "yersonargotev/packy-catalog", "RUNNER_TEMP": str(self.work / "runner")})
        Path(self.env["RUNNER_TEMP"]).mkdir()
        step = self.workflow()["jobs"]["prepare"]["steps"][1]
        result = subprocess.run(["bash", "-c", step["run"]], env=self.env, cwd=self.project,
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], "built")
        self.assertEqual(report["index"]["builder"], "yersonargotev/packy@1b8d04ddee510b24adcb12906914240bd7063aa6")
        self.assertEqual(set(p.name for p in (self.work / "dist").iterdir()), {"catalog-snapshot.tar.gz", "SHA256SUMS"})
        self.assertEqual(report["archive_sha256"], hashlib.sha256((self.work / "dist/catalog-snapshot.tar.gz").read_bytes()).hexdigest())
        return report

    def test_exact_preparation_workflow_builds_and_rejects_source_drift(self):
        self.build_with_preparation_workflow()
        (self.project / "packs/demo/instructions/guidance.md").write_text("changed after validation")
        result = subprocess.run(["bash", "-c", self.workflow()["jobs"]["prepare"]["steps"][1]["run"]],
                                env=self.env, cwd=self.project, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_credentialed_workflow_reacquires_release_and_publishes_idempotently(self):
        self.build_with_preparation_workflow()
        transport = self.bin / "gh"
        transport.write_text(f'''#!{sys.executable}
import json, os, pathlib, shutil, sys
args = sys.argv[1:]
root = pathlib.Path(os.environ["TEST_REMOTE"])
root.mkdir(exist_ok=True)
metadata = root / "release.json"
with (root / "calls.jsonl").open("a") as log:
    log.write(json.dumps(args) + "\\n")
if args[0] == "api":
    if any("/contents/packy-release.json?ref=" in arg for arg in args):
        print(pathlib.Path(os.environ["TEST_REVIEWED_PIN"]).read_text())
    elif metadata.exists():
        print(metadata.read_text())
    elif "--paginate" not in args:
        sys.exit(1)
elif args[:2] == ["release", "create"]:
    metadata.write_text(json.dumps({{"tag_name": args[2], "target_commitish": os.environ["CATALOG_COMMIT"],
        "draft": True, "immutable": False, "assets": []}}))
elif args[:2] == ["release", "upload"]:
    if os.environ.get("TEST_UPLOAD_FAIL"):
        sys.exit(22)
    source = pathlib.Path(args[3])
    shutil.copyfile(source, root / source.name)
    value = json.loads(metadata.read_text())
    value["assets"].append({{"name": source.name}})
    metadata.write_text(json.dumps(value))
elif args[:2] == ["release", "download"]:
    for name in ("catalog-snapshot.tar.gz", "SHA256SUMS"):
        if (root / name).exists():
            shutil.copyfile(root / name, pathlib.Path(args[args.index("--dir") + 1]) / name)
elif args[:2] == ["release", "edit"]:
    value = json.loads(metadata.read_text())
    value.update(draft=False, immutable=True)
    metadata.write_text(json.dumps(value))
else:
    sys.exit("unexpected gh transport request: " + str(args))
''')
        transport.chmod(0o755)
        self.env.update({"TEST_REMOTE": str(self.work / "remote"),
                         "TEST_REVIEWED_PIN": str(self.project / "packy-release.json")})
        steps = self.workflow()["jobs"]["publish"]["steps"]
        # Run the exact credentialed shell steps from an assets-only directory.
        # The attestation action remains GitHub-owned; this test has no real credentials.
        shutil.rmtree(self.project / "scripts")
        for step in steps[1:3]:
            env = dict(self.env)
            if step == steps[2]:
                env["PACKY_CACHE_DIR"] = str(self.work / "runner/publisher-cache")
            result = subprocess.run(["bash", "-c", step["run"]], env=env, cwd=self.work,
                                    text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len((self.work / "downloads").read_text().splitlines()), 2)
        for expected in ("published", "unchanged"):
            result = subprocess.run(["bash", "-c", steps[4]["run"]], env=self.env, cwd=self.work,
                                    text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["result"], expected)
        calls = [json.loads(line) for line in (self.work / "remote/calls.jsonl").read_text().splitlines()]
        self.assertEqual(sum(call[:2] == ["release", "create"] for call in calls), 1)
        # Resume a controlled interrupted draft, preserving its matching existing archive.
        remote = self.work / "remote"
        (remote / "SHA256SUMS").unlink()
        metadata = json.loads((remote / "release.json").read_text())
        metadata.update(draft=True, immutable=False, assets=[{"name": "catalog-snapshot.tar.gz"}])
        (remote / "release.json").write_text(json.dumps(metadata))
        self.env["TEST_UPLOAD_FAIL"] = "1"
        failed = subprocess.run(["bash", "-c", steps[4]["run"]], env=self.env, cwd=self.work,
                                text=True, capture_output=True, timeout=30)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(json.loads(failed.stdout)["error"]["code"], "transport_failed")
        del self.env["TEST_UPLOAD_FAIL"]
        resumed = subprocess.run(["bash", "-c", steps[4]["run"]], env=self.env, cwd=self.work,
                                 text=True, capture_output=True, timeout=30)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)["result"], "resumed")
        (self.work / "dist/SHA256SUMS").write_text("corrupted assets")
        result = subprocess.run(["bash", "-c", steps[4]["run"]], env=self.env, cwd=self.work,
                                text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "assets_invalid")

    def test_missing_baseline_is_not_silently_ignored(self):
        result = subprocess.run([str(self.project / "scripts/validate.sh"), str(self.work / "missing"), "--json"],
                                env=self.env, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.work / "downloads").exists())

    def test_symlinked_cache_is_rejected_without_execution_or_download(self):
        self.assertEqual(self.run_cli("version", "--json").returncode, 0)
        archive = next((self.work / "cache").glob("*/release.tar.gz"))
        archive.unlink()
        archive.symlink_to(Path(ARCHIVE).resolve())
        self.assert_rejected(self.run_cli("version", "--json"), "unsafe Packy cache")
        self.assertEqual(len((self.work / "downloads").read_text().splitlines()), 1)

    def test_guard_rejects_each_weakened_publication_boundary(self):
        original = self.workflow()
        mutations = [
            ("event gate", lambda jobs: jobs["prepare"].update({"if": "true"})),
            ("source gate", lambda jobs: jobs["prepare"]["steps"][1].update({"run": "echo fake"})),
            ("pin commit", lambda jobs: jobs["publish"]["steps"][1].update({"run": "gh api repos/example/contents/packy-release.json"})),
            ("unchecked executable", lambda jobs: jobs["publish"]["steps"][4].update({"run": "packy catalog publish"})),
            ("transferred cache", lambda jobs: jobs["publish"]["steps"][2].update({"env": {"PACKY_CACHE_DIR": "dist/cache"}})),
            ("unchecked shell", lambda jobs: jobs["publish"].update({"defaults": {"run": {"shell": "bash -c '{0}; evil'"}}})),
            ("extra write job", lambda jobs: jobs.update({"extra": {"permissions": {"contents": "write"}, "steps": []}})),
        ]
        for label, mutate in mutations:
            with self.subTest(boundary=label):
                workflow = json.loads(json.dumps(original))
                mutate(workflow["jobs"])
                (self.project / ".github/workflows/publish.yml").write_text(yaml.safe_dump(workflow, sort_keys=False))
                result = subprocess.run([str(self.project / "scripts/validate-publication-workflows.sh")],
                                        env=self.env, text=True, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0, label)
