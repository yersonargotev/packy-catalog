"""Verify Addy's complete Claude native closure with the pinned released CLI.

The probe configures disposable files only. It never starts a client session,
loads a role, authenticates, or invokes a model.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile

spec = importlib.util.spec_from_file_location("content_probe", Path(__file__).with_name("content-probes.py"))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


class InstalledProbe(legacy.Probe):
    """Use ordinary installed commands after copying one exact local snapshot."""

    def candidate(self, workspace, args, *, approval=None, failure=False):
        stdout, stderr = self.execute([str(self.executable), *args], approval=approval, failure=failure)
        if failure:
            return stdout, stderr
        reports = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        legacy.require(bool(reports) and isinstance(reports[-1], dict), "missing installed CLI report")
        return reports[-1]


def installed_probe(probe, scope, commit):
    workspace = probe.prepare("addy-" + scope)
    store = workspace / "home/.local/share/packy/catalog"
    retained = store / "snapshots" / commit
    retained.parent.mkdir(parents=True)
    shutil.copytree(workspace / "snapshots" / commit, retained)
    (store / "selected.json").write_text(json.dumps({"schema_version": 1, "snapshot_id": commit}) + "\n")
    env = {**probe.env, "HOME": str(workspace / "home"), "XDG_CONFIG_HOME": str(workspace / "config"),
           "XDG_DATA_HOME": str(workspace / "home/.local/share")}
    tools = workspace / "runtime-tools"
    tools.mkdir()
    git = shutil.which("git", path=probe.env["PATH"])
    legacy.require(git is not None, "missing Git prerequisite")
    (tools / "git").symlink_to(git)
    env["PATH"] = str(tools)  # No client or content runtime is available.
    direct = InstalledProbe(probe.executable, probe.snapshot, workspace / "project", env,
                            probe.evidence, probe.timeout)
    direct.set_context("content-acceptance", scenario="addy-native", surface="claude", scope=scope)
    return workspace, direct


def require_status(probe, workspace, *, targeted=False, unrelated=False, project=False):
    args = ["status"]
    if targeted:
        args += ["addy", "--surface", "claude"]
    if project:
        args += ["--project"]
    report = probe.candidate(workspace, [*args, "--json"])
    expected = "project-status" if project else "pack-status" if targeted else "pack-status-overview"
    legacy.require(report["report"] == expected and isinstance(report["schema_version"], int),
                   "wrong structured status report")
    if not project:
        entries = report["entries"]
        legacy.require(any(entry["pack"] == "addy" and entry["surface"] == "claude" for entry in entries),
                       "status omitted Addy Claude")
        if unrelated:
            legacy.require(any(entry["pack"] == "ponytail" and entry["surface"] == "claude"
                               and entry["readiness"]["configured"] == "true" for entry in entries),
                           "general status lost unrelated installed Ponytail")
    return report


def native_closure(probe, workspace, manifest, scope):
    base = workspace / ("home" if scope == "global" else "project")
    resources = {item["kind"] + ":" + item["id"]: item for item in manifest["resources"]}
    assets = [item for item in manifest["resources"] if item["kind"] == "asset"]
    checked = []
    for skill in manifest["resources"]:
        binding = next((item for item in skill["bindings"] if item["surface"] == "claude"), None)
        if skill["kind"] != "skill" or binding is None:
            continue
        source = skill["source"]
        for variant in skill.get("variants", []):
            if variant["surface"] == "claude":
                source = variant.get("source", source)
        expected = {str(path.relative_to(legacy.ROOT / "packs/addy" / source)): (path.read_bytes(), path.stat().st_mode & 0o777)
                    for path in (legacy.ROOT / "packs/addy" / source).rglob("*") if path.is_file()}
        for capability in binding["capabilities"]:
            if capability["type"] == "claude-composite-skill":
                for reference in capability["claude_composite_skill"]["references"]:
                    asset = resources[reference["kind"] + ":" + reference["id"]]
                    asset_path = legacy.ROOT / "packs/addy" / asset["source"]
                    expected["references/" + Path(asset["source"]).name] = (asset_path.read_bytes(), asset_path.stat().st_mode & 0o777)
                checked.append(skill["id"])
        target = base / ".claude/skills" / binding["name"]
        actual = {str(path.relative_to(target)): (path.read_bytes(), path.stat().st_mode & 0o777)
                  for path in target.rglob("*") if path.is_file()}
        legacy.require(actual == expected, "native skill tree differs: " + skill["id"])
    legacy.require(len(checked) == 10 and len(assets) == 7, "incomplete Addy composition acceptance")
    notice = (legacy.ROOT / "packs/addy/notices/addy-mit").read_bytes()
    if scope == "project":
        legacy.require(notice.strip() in (base / "PACKY-NOTICES.md").read_bytes(), "project MIT legal closure missing")
        probe.verify(workspace)
    else:
        state = json.loads((base / ".packy/packs.json").read_text())
        receipt = next(item for item in state["receipts"] if item["pack"]["id"] == "addy" and item["surface"] == "claude")
        selected = {(item["kind"], item["id"]) for item in receipt["resources"]}
        legacy.require({("asset", item["id"]) for item in assets} | {("notice", "mit")} <= selected,
                       "global receipt lost supporting/legal resource ownership")
    return checked


def lifecycle(probe, manifest, commit, scope):
    workspace, direct = installed_probe(probe, scope, commit)
    before = legacy.tree(workspace)
    require_status(direct, workspace)
    require_status(direct, workspace, targeted=True)
    legacy.require(legacy.tree(workspace) == before, "clean status mutated installation state")
    direct.apply(workspace, ["activate", "ponytail", "--surface", "claude", "--resource", "skill:ponytail"])
    require_status(direct, workspace, unrelated=True)
    base = workspace / ("home" if scope == "global" else "project")
    foreign = {base / ".claude/settings.json": b'{"permissions":{"allow":["Read"]}}\n',
               base / ".claude.json": b'{"mcpServers":{"personal":{"command":"user-server"}}}\n'}
    for path, content in foreign.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    install, remove = ("activate", "deactivate") if scope == "global" else ("install", "uninstall")
    direct.apply(workspace, [install, "addy", "--surface", "claude"])
    checked = native_closure(direct, workspace, manifest, scope)
    require_status(direct, workspace, targeted=True, project=scope == "project")
    require_status(direct, workspace, unrelated=True)
    update = ["update", "addy", "--surface", "claude"] + (["--project"] if scope == "project" else [])
    if scope == "project":
        unchanged = legacy.tree(workspace)
        direct.candidate(workspace, [*update, "--dry-run", "--json"])
        output, _ = direct.execute([str(direct.executable), *update])
        legacy.require("Verified no-op: the exact project installation is already present" in output
                       and legacy.tree(workspace) == unchanged, "same-snapshot project update changed state")
    else:
        direct.apply(workspace, update)
    native_closure(direct, workspace, manifest, scope)
    drift = base / ".claude/skills/build/references/security-checklist.md"
    original = drift.read_bytes()
    drift.write_bytes(b"User changed checklist.\n")
    drifted = legacy.tree(workspace)
    stdout, stderr = direct.candidate(workspace, [remove, "addy", "--surface", "claude", "--json"], failure=True)
    legacy.require("drift" in (stdout + stderr).lower() and legacy.tree(workspace) == drifted,
                   "drifted asset removal changed state or failed for an unrelated cause")
    drift.write_bytes(original)
    direct.apply(workspace, [remove, "addy", "--surface", "claude"])
    for resource in manifest["resources"]:
        for binding in resource["bindings"]:
            if binding["surface"] != "claude":
                continue
            directory = ".claude/skills" if resource["kind"] == "skill" else ".claude/agents"
            filename = binding["name"] + (".md" if resource["kind"] == "agent" else "")
            legacy.require(not os.path.lexists(base / directory / filename), "retired Addy projection remains: " + filename)
    for path, content in foreign.items():
        legacy.require(path.read_bytes() == content, "lifecycle changed foreign configuration: " + str(path))
    if scope == "project":
        for resource in manifest["resources"]:
            if resource["kind"] == "asset":
                legacy.require(not os.path.lexists(base / ".claude/assets" / resource["id"] / "RESOURCE"),
                               "retired project asset remains: " + resource["id"])
    require_status(direct, workspace, unrelated=True)
    direct.apply(workspace, ["deactivate", "ponytail", "--surface", "claude"])
    if scope == "project":
        for name in ("packy.json", "packy.lock.json", "PACKY-NOTICES.md"):
            legacy.require(not (base / name).exists(), "uninstall retained " + name)
    probe.evidence["outcomes"].append({"scenario": "addy-native", "surface": "claude", "scope": scope,
                                       "composite_skills": checked, "result": "passed"})


def reject_unsupported_layouts(probe):
    for name, capability in (("plain", []), ("incomplete-composite", [{"type": "claude-composite-skill",
                                                                        "claude_composite_skill": {"dependencies": [], "references": []}}])):
        project = probe.root / ("unsupported-" + name)
        shutil.copytree(legacy.ROOT / "packs", project / "packs")
        path = project / "packs/addy/pack.json"
        manifest = json.loads(path.read_text())
        build = next(item for item in manifest["resources"] if item["kind"] == "skill" and item["id"] == "build")
        next(item for item in build["bindings"] if item["surface"] == "claude")["capabilities"] = capability
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        before = legacy.tree(project)
        stdout, stderr = probe.execute([str(probe.executable), "catalog", "validate", "--project", str(project), "--json"], failure=True, timeout=600)
        legacy.require("asset" in (stdout + stderr) and "build" in (stdout + stderr), "unsupported layout failed for an unrelated cause")
        legacy.require(legacy.tree(project) == before, "qualification changed unsupported Catalog input")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--qualification-executable", type=Path,
                        help="also prove unsupported-layout rejection with this explicitly selected engine")
    args = parser.parse_args()
    if not legacy.math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    evidence = {"schema_version": 1, "report": "catalog-content-probes", "provenance": "local-candidate",
                "official_publication": False, "commands": [], "outcomes": [], "result": "failed"}
    root = None
    handler = signal.signal(signal.SIGTERM, legacy.interrupted)
    try:
        with tempfile.TemporaryDirectory(prefix="addy-native-") as directory:
            root = Path(directory).resolve()
            env = legacy.isolated_environment(root)
            probe = legacy.Probe(root / "packy", root / "dist", root, env, evidence, args.timeout)
            commit = legacy.checkout_commit(probe, legacy.ROOT)
            probe.set_context("acquisition")
            probe.execute([sys.executable, "-B", str(legacy.ROOT / "scripts/packy_tool.py"), "--pin",
                           str(legacy.ROOT / "packy-release.json"), "--executable-output", str(probe.executable)], timeout=180)
            identity, _ = probe.execute([str(probe.executable), "version", "--json"])
            evidence["verified_packy_identity"] = json.loads(identity)
            probe.set_context("candidate-construction")
            evidence.update(legacy.build_catalog(probe, legacy.ROOT, commit, probe.snapshot))
            manifest = json.loads((legacy.ROOT / "packs/addy/pack.json").read_text())
            for scope in ("global", "project"):
                lifecycle(probe, manifest, commit, scope)
            if args.qualification_executable is not None:
                executable = args.qualification_executable.resolve(strict=True)
                legacy.require(executable.is_file() and os.access(executable, os.X_OK),
                               "qualification executable must be an executable file")
                qualification = legacy.Probe(executable, probe.snapshot, root, env, evidence, args.timeout)
                qualification.set_context("unsupported-native-qualification", surface="claude")
                identity, _ = qualification.execute([str(executable), "version", "--json"])
                evidence["qualification_packy_identity"] = json.loads(identity)
                reject_unsupported_layouts(qualification)
                evidence["outcomes"].append({"scenario": "unsupported-native-qualification", "result": "passed"})
            legacy.require(legacy.checkout_commit(probe, legacy.ROOT) == commit, "Catalog candidate changed during acceptance")
            evidence["result"] = "passed"
    except (OSError, ValueError, KeyError, RuntimeError, legacy.subprocess.SubprocessError, KeyboardInterrupt) as error:
        evidence["error"] = str(error) or "probe interrupted"
        print("Addy native probe: " + evidence["error"], file=sys.stderr)
    finally:
        signal.signal(signal.SIGTERM, handler)
        evidence["cleanup"] = "removed" if root is None or not root.exists() else "failed"
        if evidence["cleanup"] != "removed":
            evidence["result"] = "failed"
        print(json.dumps(evidence, indent=2))
    return 0 if evidence["result"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
