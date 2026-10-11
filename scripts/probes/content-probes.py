"""Opt-in Catalog content acceptance through the verified released CLI."""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile

from content_probe_process import run_child


ROOT = Path(__file__).resolve().parents[2]
SURFACES = ("codex", "claude", "opencode")
SKILL_DIRECTORIES = {"codex": ".agents/skills", "claude": ".claude/skills", "opencode": ".opencode/skills"}
SKILLS = ("ponytail", "ponytail-review", "ponytail-audit", "ponytail-debt", "ponytail-gain", "ponytail-help")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def tree(root):
    """Observe complete owned filesystem effects, including modes and directories."""
    return {str(path.relative_to(root)): (path.stat().st_mode, path.read_bytes() if path.is_file() else None)
            for path in sorted(root.rglob("*"))}


def isolated_environment(root):
    env = {"HOME": str(root / "ambient-home"), "PATH": os.environ.get("PATH", ""),
           "TMPDIR": str(root / "tmp"), "XDG_CONFIG_HOME": str(root / "ambient-config"),
           "XDG_DATA_HOME": str(root / "ambient-data"), "XDG_CACHE_HOME": str(root / "ambient-cache"),
           "PACKY_CACHE_DIR": str(root / "tool-cache"), "PYTHONDONTWRITEBYTECODE": "1",
           "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": os.devnull}
    # Network transport settings are explicit; tokens and host settings are absent.
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY", "https_proxy", "http_proxy",
                "all_proxy", "no_proxy", "SSL_CERT_FILE", "SSL_CERT_DIR", "CURL_CA_BUNDLE"):
        if key in os.environ:
            env[key] = os.environ[key]
    for key in ("HOME", "TMPDIR", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME"):
        Path(env[key]).mkdir()
    return env


class Probe:
    def __init__(self, executable, snapshot, root, env, evidence, timeout):
        self.executable, self.snapshot, self.root = executable, snapshot, root
        self.env, self.evidence, self.timeout = env, evidence, timeout

    def execute(self, command, *, approval=None, failure=False, timeout=None):
        receipt = {"command": [str(value) for value in command], "outcome": "failed"}
        self.evidence["commands"].append(receipt)
        try:
            status, stdout, stderr = run_child(command, cwd=self.root, env=self.env,
                                              timeout=timeout or self.timeout, approval=approval)
        except (Exception, KeyboardInterrupt) as error:
            receipt["error"] = str(error) or "interrupted"
            raise
        receipt.update(exit_status=status, stdout_sha256=hashlib.sha256(stdout.encode()).hexdigest(),
                       diagnostic=stderr.strip())
        require((status != 0) if failure else (status == 0), "unexpected child exit: " + json.dumps(receipt) + "\n" + stdout)
        receipt["outcome"] = "expected-rejection" if failure else "passed"
        return stdout, stderr

    def candidate(self, workspace, args, *, snapshot=None, approval=None, failure=False):
        stdout, stderr = self.execute([str(self.executable), "catalog", "candidate", "--snapshot",
                                      str(snapshot or self.snapshot), "--workspace", str(workspace), "--", *args],
                                     approval=approval, failure=failure)
        if not failure:
            require("not an official Catalog Publication" in stderr, "missing local candidate provenance")
        if failure:
            return stdout, stderr
        reports = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        require(bool(reports), "missing structured candidate report")
        report = reports[-1]
        require(isinstance(report, dict), "incomplete structured candidate report")
        return report

    def apply(self, workspace, args):
        preview = self.candidate(workspace, [*args, "--dry-run", "--json"])
        observation = preview["observation"]
        require(isinstance(observation, str) and observation, "missing exact preview observation")
        operation = "project installation" if args[0] == "install" else "project surface uninstall"
        prompt = f"Approve {operation} for exact preview {observation}? [y/N] "
        return self.candidate(workspace, [*args, "--json"], approval=prompt)

    def prepare(self, name):
        workspace = self.root / name
        listing = self.candidate(workspace, ["list", "--json"])
        actual = {pack["id"] for pack in listing["packs"]}
        require(actual == set(self.evidence["pack_ids"]), "complete catalog consumption lost Packs")
        project = workspace / "project"
        for name in ("AGENTS.md", "CLAUDE.md", "unrelated.txt"):
            (project / name).write_text("# Existing project guidance\n\nKeep local conventions.\n")
        for root in (workspace / "home", workspace / "config"):
            (root / "personal-sentinel").write_text("Preserve personal state.\n")
        return workspace

    def verify(self, workspace):
        report = self.candidate(workspace, ["verify", "--json"])
        require(report["result"] == "passed", "portable project verification failed")


def incompatible_snapshot(snapshot, output):
    """A controlled negative fixture; its altered bytes are never a built candidate."""
    output.mkdir()
    with tarfile.open(snapshot / "catalog-snapshot.tar.gz", "r:gz") as source:
        with tarfile.open(output / "catalog-snapshot.tar.gz", "w:gz") as target:
            for member in source.getmembers():
                data = source.extractfile(member).read() if member.isfile() else None
                if member.name == "catalog-index.json":
                    index = json.loads(data)
                    index["schema_version"] = 999
                    data = json.dumps(index).encode()
                    member.size = len(data)
                target.addfile(member, io.BytesIO(data) if data is not None else None)
    digest = hashlib.sha256((output / "catalog-snapshot.tar.gz").read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(digest + "  catalog-snapshot.tar.gz\n")


def adoption(probe, surfaces):
    bad = probe.root / "incompatible-fixture"
    incompatible_snapshot(probe.snapshot, bad)
    for surface in surfaces:
        workspace = probe.prepare("adoption-" + surface)
        before = tree(workspace)
        out, diagnostic = probe.candidate(workspace, ["list", "--json"], snapshot=bad, failure=True)
        require("newer Packy engine" in diagnostic + out or "schema_version" in diagnostic + out,
                "incompatible input failed for an unrelated reason")
        require(tree(workspace) == before, "incompatible candidate changed previous state")
        probe.candidate(workspace, ["list", "--json"])
        fresh = probe.root / ("rejected-" + surface)
        probe.candidate(fresh, ["list", "--json"], snapshot=bad, failure=True)
        require(not fresh.exists(), "rejected candidate created a workspace")
        original = tree(workspace / "project")
        probe.apply(workspace, ["install", "emil", "--surface", surface])
        probe.verify(workspace)
        probe.apply(workspace, ["uninstall", "emil", "--surface", surface])
        assert_retired(workspace / "project", original, surface)
        probe.evidence["outcomes"].append({"scenario": "adoption", "surface": surface, "result": "passed"})


def assert_retired(project, original, surface):
    for name in ("packy.json", "packy.lock.json", "PACKY-NOTICES.md"):
        require(not (project / name).exists(), "last Pack removal retained " + name)
    for name in ("AGENTS.md", "CLAUDE.md", "unrelated.txt"):
        require((project / name).read_bytes().rstrip(b"\n") == original[name][1].rstrip(b"\n"),
                "uninstall changed unrelated document " + name)
        require((project / name).stat().st_mode == original[name][0], "uninstall changed unrelated mode " + name)
    skill_root = project / SKILL_DIRECTORIES[surface]
    require(not skill_root.exists() or not list(skill_root.iterdir()), "uninstall retained managed skills")


def ponytail(probe, surfaces):
    for surface in surfaces:
        for selection in ("complete", "skill", "instruction"):
            workspace = probe.prepare("ponytail-" + surface + "-" + selection)
            project = workspace / "project"
            instruction = project / ("CLAUDE.md" if surface == "claude" else "AGENTS.md")
            skill_root = project / SKILL_DIRECTORIES[surface]
            original_project = tree(project)
            if selection == "skill":
                probe.apply(workspace, ["install", "argote", "--surface", surface, "--resource", "instruction:guidance"])
            original_instructions = instruction.read_bytes()
            personal = (tree(workspace / "home"), tree(workspace / "config"))
            args = ["install", "ponytail", "--surface", surface]
            if selection != "complete":
                args += ["--resource", "skill:ponytail" if selection == "skill" else "instruction:ponytail-guidance"]
            before = tree(workspace)
            probe.candidate(workspace, [*args, "--dry-run", "--json"])
            require(tree(workspace) == before, "preview changed workspace")
            probe.apply(workspace, args)
            probe.verify(workspace)
            instructions = instruction.read_bytes()
            require(original_instructions.strip() in instructions, "installation replaced existing instructions")
            require((b"# Ponytail, lazy senior dev mode" in instructions) == (selection != "skill"),
                    "guidance does not match selected resources")
            for name in SKILLS:
                path = skill_root / name / "SKILL.md"
                want = selection == "complete" or selection == "skill" and name == "ponytail"
                require(path.exists() == want, "wrong skill selection: " + name)
                if want:
                    require("name: " + name + "\n" in path.read_text(), "wrong skill body: " + name)
            require("Copyright (c) 2026 DietrichGebert" in (project / "PACKY-NOTICES.md").read_text(),
                    "upstream notice missing")
            if selection != "skill":
                before = tree(workspace)
                out, diagnostic = probe.candidate(workspace, ["install", "argote", "--surface", surface,
                                                            "--resource", "instruction:guidance", "--dry-run", "--json"], failure=True)
                require("projection_collision" in out, "shared instruction ownership conflict not rejected: " + diagnostic)
                require(tree(workspace) == before, "ownership rejection changed workspace")
            probe.apply(workspace, ["uninstall", "ponytail", "--surface", surface])
            require(instruction.read_bytes().strip() == original_instructions.strip(), "uninstall changed retained guidance")
            require(not list(skill_root.glob("ponytail*")), "uninstall retained Ponytail skills")
            require(personal == (tree(workspace / "home"), tree(workspace / "config")), "lifecycle changed personal state")
            if selection == "skill":
                probe.verify(workspace)
                probe.apply(workspace, ["uninstall", "argote", "--surface", surface])
            assert_retired(project, original_project, surface)
            probe.evidence["outcomes"].append({"scenario": "ponytail", "surface": surface,
                                              "selection": selection, "result": "passed"})


def pack_html(probe, workspace, skill):
    output = workspace / "html-packing"
    output.mkdir()
    page = output / "plan.html"
    shutil.copyfile(skill / "examples/scheduled-send.html", page)
    stdout, stderr = probe.execute(["node", str(skill / "runtime/pack.mjs"), str(page), "--root", str(skill)])
    require("✗" not in stdout + stderr, "HTML packing reported errors")
    packed = (output / "plan.packed.html").read_text()
    for tag, name in (("style", "htmlplan.css"), ("script", "htmlplan.js")):
        asset = (skill / "runtime" / name).read_text()
        if tag == "script":
            asset = re.sub(r"</script", lambda match: "<\\/script", asset, flags=re.IGNORECASE)
        require(f"<{tag} data-htmlplan>\n{asset}\n</{tag}>" in packed, "packed HTML missing runtime asset: " + name)
    require(not re.search(r'(?:href|src)=["\'][^"\']*htmlplan\.(?:css|js)["\']', packed),
            "packed HTML retained an external runtime link")
    warnings = [line.strip() for line in (stdout + stderr).splitlines() if "⚠" in line]
    fictional = [line for line in warnings if re.search(r"<doc-calls>: \d+ rows point at files not found under ", line)]
    return {"result": "passed", "packed_sha256": hashlib.sha256(packed.encode()).hexdigest(),
            "fictional_source_warnings": fictional, "other_warnings": [line for line in warnings if line not in fictional]}


def claude(probe, surfaces):
    for surface in surfaces:
        for selection in ("complete", "eli5", "html-plan"):
            workspace = probe.prepare("claude-" + surface + "-" + selection)
            project = workspace / "project"
            original_project = tree(project)
            instruction = project / ("CLAUDE.md" if surface == "claude" else "AGENTS.md")
            skill_root = project / SKILL_DIRECTORIES[surface]
            probe.apply(workspace, ["install", "argote", "--surface", surface, "--resource", "instruction:guidance"])
            original_instructions = instruction.read_bytes()
            personal = (tree(workspace / "home"), tree(workspace / "config"))
            args = ["install", "claude", "--surface", surface]
            if selection != "complete":
                args += ["--resource", "skill:" + selection]
            before = tree(workspace)
            probe.candidate(workspace, [*args, "--dry-run", "--json"])
            require(tree(workspace) == before, "Claude preview changed workspace")
            probe.apply(workspace, args)
            probe.verify(workspace)
            for name in ("eli5", "html-plan"):
                path = skill_root / name / "SKILL.md"
                want = selection == "complete" or selection == name
                require((skill_root / name).exists() == want, "wrong Claude skill selection: " + name)
                if want:
                    require("name: " + name + "\n" in path.read_text(), "wrong Claude skill body: " + name)
            if selection != "eli5":
                for name in ("runtime/htmlplan.js", "runtime/htmlplan.css", "runtime/pack.mjs",
                             "references/blocks.md", "examples/scheduled-send.html"):
                    require((skill_root / "html-plan" / name).is_file(), "missing HTML runtime closure: " + name)
            notices = (project / "PACKY-NOTICES.md").read_text()
            require("Apache License" in notices, "Claude repository license missing")
            for name in ("eli5", "html-plan"):
                require(('"name": "' + name + '"' in notices) == (selection == "complete" or selection == name),
                        "wrong Claude notice selection: " + name)
            require(instruction.read_bytes() == original_instructions, "Claude install changed retained guidance")
            require(personal == (tree(workspace / "home"), tree(workspace / "config")),
                    "Claude install changed personal state")
            outcome = {"scenario": "claude", "surface": surface, "selection": selection, "result": "passed"}
            if probe.evidence["html_pack"] and selection != "eli5":
                outcome["html_packing"] = pack_html(probe, workspace, skill_root / "html-plan")
            probe.apply(workspace, ["uninstall", "claude", "--surface", surface])
            probe.verify(workspace)
            require(instruction.read_bytes() == original_instructions, "Claude uninstall changed retained guidance")
            require(all(not (skill_root / name).exists() for name in ("eli5", "html-plan")),
                    "Claude uninstall retained skills")
            require(personal == (tree(workspace / "home"), tree(workspace / "config")),
                    "Claude uninstall changed personal state")
            probe.apply(workspace, ["uninstall", "argote", "--surface", surface])
            assert_retired(project, original_project, surface)
            probe.evidence["outcomes"].append(outcome)


def interrupted(signum, frame):
    raise KeyboardInterrupt("probe interrupted by signal " + str(signum))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", choices=("adoption", "ponytail", "claude"), required=True)
    parser.add_argument("--surface", action="append", choices=SURFACES)
    parser.add_argument("--html-pack", action="store_true", help="optionally execute the installed Claude HTML packer with Node")
    parser.add_argument("--timeout", type=float, default=30, help="lifecycle deadline in seconds (default: 30)")
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    scenarios = list(dict.fromkeys(args.scenario))
    if args.html_pack and "claude" not in scenarios:
        parser.error("--html-pack requires --scenario claude")
    surfaces = list(dict.fromkeys(args.surface or SURFACES))
    evidence = {"schema_version": 1, "report": "catalog-content-probes", "provenance": "local-candidate",
                "official_publication": False, "scenarios": scenarios, "surfaces": surfaces, "html_pack": args.html_pack,
                "commands": [], "outcomes": [], "result": "failed"}
    root = None
    previous_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        with tempfile.TemporaryDirectory(prefix="catalog-content-probes-") as directory:
            root = Path(directory).resolve()
            env = isolated_environment(root)
            probe = Probe(root / "packy", root / "dist", root, env, evidence, args.timeout)
            for name in ("git", "curl", "uname", *(("node",) if args.html_pack else ())):
                require(shutil.which(name, path=env["PATH"]) is not None, "missing prerequisite: " + name)
            checkout_state, _ = probe.execute(["git", "-C", str(ROOT), "status", "--porcelain"])
            require(not checkout_state.strip(), "content probes require a clean committed Catalog candidate")
            commit, _ = probe.execute(["git", "-C", str(ROOT), "rev-parse", "HEAD"])
            evidence["candidate_commit"] = commit.strip()
            probe.execute([sys.executable, "-B", str(ROOT / "scripts/packy_tool.py"), "--pin",
                           str(ROOT / "packy-release.json"), "--executable-output", str(probe.executable)], timeout=180)
            version, _ = probe.execute([str(probe.executable), "version", "--json"])
            evidence["verified_packy_identity"] = json.loads(version)
            built, _ = probe.execute([str(probe.executable), "catalog", "build", "--project", str(ROOT),
                                      "--source-repository", "yersonargotev/packy-catalog", "--source-commit",
                                      commit.strip(), "--out-dir", str(probe.snapshot), "--json"], timeout=600)
            build = json.loads(built)
            require(build["result"] == "built", "incomplete candidate build")
            evidence["archive_sha256"] = build["archive_sha256"]
            evidence["builder"] = build["index"]["builder"]
            evidence["pack_ids"] = [pack["id"] for pack in build["index"]["packs"]]
            ambient = {key: tree(Path(env[key])) for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME")}
            for scenario in scenarios:
                print("Running reviewed content scenario: " + scenario, file=sys.stderr, flush=True)
                {"adoption": adoption, "ponytail": ponytail, "claude": claude}[scenario](probe, surfaces)
            require(ambient == {key: tree(Path(env[key])) for key in ambient}, "candidate changed ambient user state")
            checkout_state, _ = probe.execute(["git", "-C", str(ROOT), "status", "--porcelain"])
            final_commit, _ = probe.execute(["git", "-C", str(ROOT), "rev-parse", "HEAD"])
            require(not checkout_state.strip() and final_commit == commit, "Catalog candidate changed during probes")
            evidence["result"] = "passed"
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        evidence["error"] = str(error) or "probe interrupted"
        print("Content probes: " + evidence["error"], file=sys.stderr)
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
        evidence["cleanup"] = "removed" if root is None or not root.exists() else "failed: owned state remains at " + str(root)
        if evidence["cleanup"] != "removed":
            evidence["result"] = "failed"
        print(json.dumps(evidence, indent=2))
    return 0 if evidence["result"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
