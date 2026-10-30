"""Check Matty source fidelity, native lifecycle and retained access without running skills."""
import argparse
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile


spec = importlib.util.spec_from_file_location("content_probe", Path(__file__).with_name("content-probes.py"))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def source_fidelity(upstream, manifest):
    commit = legacy.subprocess.check_output(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True, timeout=30).strip()
    legacy.require(commit == manifest["origins"][0]["commit"], "upstream checkout has the wrong commit")
    state = legacy.subprocess.check_output(
        ["git", "-C", str(upstream), "status", "--porcelain"], text=True, timeout=30)
    legacy.require(not state.strip(), "upstream checkout must be clean")
    checked = 0
    for resource in manifest["resources"]:
        if "origin" not in resource:
            continue
        source = upstream / resource["origin"]["path"]
        target = legacy.ROOT / "packs/matty" / resource["source"]
        files = [source] if source.is_file() else sorted(path for path in source.rglob("*") if path.is_file())
        legacy.require(bool(files), "missing upstream resource: " + str(source))
        for original in files:
            copied = target if source.is_file() else target / original.relative_to(source)
            legacy.require(original.read_bytes() == copied.read_bytes()
                           and bool(original.stat().st_mode & 0o111) == bool(copied.stat().st_mode & 0o111),
                           "source bytes or executable mode differ: " + str(copied))
            checked += 1
    return {"upstream_commit": commit, "original_files_checked": checked}


def check_surface(probe, manifest, surface):
    skills = {resource["id"]: resource for resource in manifest["resources"] if resource["kind"] == "skill"}
    workspace = probe.prepare("matty-update-" + surface)
    project_before = legacy.tree(workspace / "project")
    probe.apply(workspace, ["install", "matty", "--surface", surface])
    probe.verify(workspace)
    native = workspace / "project" / (".agents/skills" if surface == "agents" else ".claude/skills")
    legacy.require({path.name for path in native.iterdir()} == set(skills), "native Matty inventory differs")
    for name, resource in skills.items():
        legacy.require(legacy.tree(native / name) == legacy.tree(legacy.ROOT / "packs/matty" / resource["source"]),
                       "native bytes or modes differ: " + name)
    notices = (workspace / "project/PACKY-NOTICES.md").read_bytes()
    for resource in manifest["resources"]:
        if resource["kind"] == "notice":
            legacy.require((legacy.ROOT / "packs/matty" / resource["source"]).read_bytes() in notices,
                           "native Matty notice missing: " + resource["id"])
    installed = legacy.installation_state(workspace)
    snapshots = set()
    for name in skills:
        report = probe.candidate(workspace, ["get", "skill", "matty:" + name, "--surface", surface, "--json"])
        descriptors = {item["qualified_skill"]: item for item in [report, *report["dependencies"]]}
        legacy.require(report["qualified_skill"] == "matty:" + name
                       and all(item["surface"] == surface and item["pack_version"] == manifest["version"]
                               and item["snapshot_id"] == report["snapshot_id"] for item in descriptors.values()),
                       "wrong Matty retained resource identity")
        legacy.assert_skill_content(descriptors, manifest)
        snapshots.add(report["snapshot_id"])
        if name == "chief-of-staff":
            retained = probe.candidate(workspace, ["get", "skill", "matty:chief-of-staff", "--surface", surface,
                                                   "--snapshot", report["snapshot_id"], "--json"])
            legacy.require(retained["snapshot_id"] == report["snapshot_id"]
                           and Path(retained["entry_document"]).read_bytes() == Path(report["entry_document"]).read_bytes(),
                           "chief-of-staff explicit retained access differs")
    legacy.require(len(snapshots) == 1 and legacy.installation_state(workspace) == installed,
                   "access changed native installation or mixed snapshots")
    before_export = legacy.tree(workspace)
    output = probe.root / (surface + "-chief-plugin")
    args = ["export", "matty", "--surface", surface, "--skill", "chief-of-staff", "--output", str(output), "--json"]
    if surface == "agents":
        stdout, stderr = probe.candidate(workspace, args, failure=True)
        legacy.require("chief-of-staff" in stdout + stderr and not output.exists(),
                       "unsupported Agent Plugins selection did not fail without output")
    else:
        report = probe.candidate(workspace, args)
        legacy.require(report["result"] == "exported" and report["format"] == "claude-plugin"
                       and report["selected_skills"] == ["chief-of-staff"]
                       and report["snapshot_id"] in snapshots, "wrong chief-of-staff plugin identity")
        legacy.require(legacy.tree(output / "skills/chief-of-staff")
                       == legacy.tree(native / "chief-of-staff"), "chief-of-staff export changed content or invocation policy")
        legacy.require(legacy.tree(output / "notices") == legacy.tree(legacy.ROOT / "packs/matty/notices"),
                       "chief-of-staff export lost legal closure")
    legacy.require(legacy.tree(workspace) == before_export, "plugin export changed installation or client state")
    probe.apply(workspace, ["uninstall", "matty", "--surface", surface])
    for filename in ("AGENTS.md", "CLAUDE.md", "unrelated.txt"):
        legacy.require((workspace / "project" / filename).read_bytes().rstrip(b"\n")
                       == project_before[filename][1].rstrip(b"\n"), "uninstall changed unrelated project content")
    for filename in ("packy.json", "packy.lock.json", "PACKY-NOTICES.md"):
        legacy.require(not (workspace / "project" / filename).exists(), "uninstall retained " + filename)
    legacy.require(not native.exists() or not list(native.iterdir()), "uninstall retained Matty skills")
    return {"surface": surface, "skills_checked": len(skills), "snapshot_id": snapshots.pop(),
            "chief_plugin": "exported" if surface == "claude" else "rejected", "result": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True, help="clean checkout of Matty's pinned upstream commit")
    args = parser.parse_args()
    evidence = {"schema_version": 1, "report": "matty-update-probe", "official_publication": False,
                "commands": [], "outcomes": [], "result": "failed"}
    root = None
    handler = signal.signal(signal.SIGTERM, legacy.interrupted)
    try:
        manifest = json.loads((legacy.ROOT / "packs/matty/pack.json").read_text())
        evidence.update(source_fidelity(args.upstream.resolve(strict=True), manifest))
        authored = legacy.tree(legacy.ROOT / "packs/matty")
        with tempfile.TemporaryDirectory(prefix="matty-update-probe-") as directory:
            root = Path(directory).resolve()
            env = legacy.isolated_environment(root)
            probe = legacy.Probe(root / "packy", root / "dist", root, env, evidence, 30)
            commit = legacy.checkout_commit(probe, legacy.ROOT)
            probe.set_context("acquisition")
            probe.execute([sys.executable, "-B", str(legacy.ROOT / "scripts/packy_tool.py"), "--pin",
                           str(legacy.ROOT / "packy-release.json"), "--executable-output", str(probe.executable)], timeout=180)
            identity, _ = probe.execute([str(probe.executable), "version", "--json"])
            evidence["verified_packy_identity"] = json.loads(identity)
            evidence.update(legacy.build_catalog(probe, legacy.ROOT, commit, probe.snapshot))
            ambient = {key: legacy.tree(Path(env[key])) for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME")}
            for surface in ("agents", "claude"):
                probe.set_context("content-acceptance", scenario="matty-update", surface=surface, scope="project")
                evidence["outcomes"].append(check_surface(probe, manifest, surface))
            legacy.require(ambient == {key: legacy.tree(Path(env[key])) for key in ambient}, "probe changed ambient client state")
            legacy.require(legacy.tree(legacy.ROOT / "packs/matty") == authored, "probe changed authored Matty resources")
            legacy.require(legacy.checkout_commit(probe, legacy.ROOT) == commit, "candidate changed during probe")
            evidence["result"] = "passed"
    except (OSError, ValueError, KeyError, RuntimeError, legacy.subprocess.SubprocessError, KeyboardInterrupt) as error:
        evidence["error"] = str(error) or "probe interrupted"
        print("Matty update probe: " + evidence["error"], file=sys.stderr)
    finally:
        signal.signal(signal.SIGTERM, handler)
        evidence["cleanup"] = "removed" if root is None or not root.exists() else "failed"
        if evidence["cleanup"] != "removed":
            evidence["result"] = "failed"
        print(json.dumps(evidence, indent=2))
    return 0 if evidence["result"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
