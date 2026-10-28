"""Verify representative two-surface behavior against a local Catalog candidate.

This opt-in probe configures files and generates packages; it does not exercise
client loading, authorization, or model-backed use.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import signal
import sys
import tempfile

spec = importlib.util.spec_from_file_location("legacy_probe", Path(__file__).with_name("content-probes.py"))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", default="ponytail")
    parser.add_argument("--skill", default="ponytail")
    parser.add_argument("--access", default="matty:tdd", help="qualified reviewed on-demand skill")
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    if not legacy.math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    evidence = {"schema_version": 1, "report": "catalog-generation-probe", "provenance": "local-candidate",
                "official_publication": False, "commands": [], "outcomes": [], "result": "failed"}
    root = None
    handler = signal.signal(signal.SIGTERM, legacy.interrupted)
    try:
        with tempfile.TemporaryDirectory(prefix="catalog-generation-") as directory:
            root = Path(directory).resolve()
            env = legacy.isolated_environment(root)
            probe = legacy.Probe(root / "packy", root / "dist", root, env, evidence, args.timeout)
            for name in ("git", "curl", "uname"):
                legacy.require(shutil.which(name, path=env["PATH"]) is not None, "missing prerequisite: " + name)
            commit = legacy.checkout_commit(probe, legacy.ROOT)
            probe.set_context("acquisition")
            probe.execute([sys.executable, "-B", str(legacy.ROOT / "scripts/packy_tool.py"), "--pin",
                           str(legacy.ROOT / "packy-release.json"), "--executable-output", str(probe.executable)], timeout=180)
            identity, _ = probe.execute([str(probe.executable), "version", "--json"])
            evidence["verified_packy_identity"] = json.loads(identity)
            probe.set_context("candidate-construction")
            evidence.update(legacy.build_catalog(probe, legacy.ROOT, commit, probe.snapshot))
            ambient = {key: legacy.tree(Path(env[key])) for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME")}
            for surface in ("agents", "claude"):
                probe.set_context("content-acceptance", scenario="generation", surface=surface, scope="project")
                workspace = probe.prepare("generation-" + surface)
                before = legacy.tree(workspace / "project")
                selection = ["--surface", surface, "--resource", "skill:" + args.skill]
                probe.apply(workspace, ["install", args.pack, *selection])
                probe.verify(workspace)
                ponytail = (args.pack, args.skill) == ("ponytail", "ponytail")
                if ponytail:
                    pack_root = legacy.ROOT / "packs/ponytail"
                    native_root = workspace / "project" / (".agents/skills" if surface == "agents" else ".claude/skills") / "ponytail"
                    native = (native_root / "SKILL.md").read_text()
                    legacy.require(legacy.tree(native_root) == legacy.tree(pack_root / "skills/ponytail"),
                                   "native Ponytail tree changed during installation")
                    legacy.require("For native installations" in native
                                   and "`$ponytail lite|full|ultra`" in native
                                   and "`/ponytail lite|full|ultra`" in native
                                   and "OpenCode" not in native and "{{packy.export:" not in native,
                                   "native Ponytail lacks scoped supported invocation guidance")
                content = probe.candidate(workspace, ["get", "skill", args.access, "--surface", surface, "--json"])
                snapshot = content["snapshot_id"]
                entry = Path(content["entry_document"])
                legacy.require(content["surface"] == surface and entry.is_file(), "wrong retained skill identity or entry")
                retained = probe.candidate(workspace, ["get", "skill", args.access, "--surface", surface, "--snapshot", snapshot, "--json"])
                legacy.require(retained["snapshot_id"] == snapshot and Path(retained["entry_document"]).read_bytes() == entry.read_bytes(), "retained access changed")
                state = legacy.tree(workspace)
                outputs = [root / (surface + "-plugin-" + str(i)) for i in (1, 2)]
                reports = []
                for output in outputs:
                    reports.append(probe.candidate(workspace, ["export", args.pack, "--surface", surface, "--skill", args.skill, "--output", str(output), "--json"]))
                expected_format = "agent-plugins" if surface == "agents" else "claude-plugin"
                legacy.require(all(report["result"] == "exported" and report["surface"] == surface and report["format"] == expected_format and report["snapshot_id"] == snapshot for report in reports), "incorrect export report")
                if ponytail:
                    exported = (outputs[0] / "skills/ponytail/SKILL.md").read_text()
                    if surface == "claude":
                        legacy.require("`/ponytail:ponytail lite|full|ultra`" in exported,
                                       "Claude plugin lacks qualified Ponytail invocation")
                    else:
                        legacy.require("consuming client's skill invocation mechanism" in exported,
                                       "Agent Plugins lacks portable Ponytail invocation guidance")
                    legacy.require(all(value not in exported for value in
                                       ("OpenCode", "`/ponytail ", "$ponytail", "{{packy.export:")),
                                   "plugin retains native/retired invocation guidance or unresolved markers")
                    legacy.require(exported.split("## Conversation scope")[0] == native.split("## Conversation scope")[0]
                                   and exported.split("The Packy edition", 1)[1] == native.split("The Packy edition", 1)[1],
                                   "plugin changed Ponytail metadata or behavior beyond invocation guidance")
                    manifest = json.loads((pack_root / "pack.json").read_text())
                    legacy.require(all(report["schema_version"] == 1 and report["report"] == "plugin-export"
                                       and report["pack_id"] == report["plugin_name"] == "ponytail"
                                       and report["pack_version"] == manifest["version"]
                                       and report["selected_skills"] == ["ponytail"]
                                       and report["prerequisites"] == [] for report in reports),
                                   "wrong Ponytail export identity, selection or prerequisites")
                    plugin_manifest = outputs[0] / (".claude-plugin/plugin.json" if surface == "claude" else "plugin.json")
                    package = json.loads(plugin_manifest.read_text())
                    legacy.require(package["name"] == "ponytail" and package["version"] == manifest["version"],
                                   "wrong Ponytail package identity")
                    provenance = json.loads((outputs[0] / "packy-provenance.json").read_text())
                    legacy.require(provenance["snapshot_id"] == snapshot and provenance["pack_id"] == "ponytail"
                                   and provenance["pack_version"] == manifest["version"]
                                   and provenance["origins"] == manifest["origins"]
                                   and provenance["resources"] == reports[0]["resources"],
                                   "Ponytail export lost provenance")
                    resources = {item["resource"]["kind"] + ":" + item["resource"]["id"]: item
                                 for item in provenance["resources"]}
                    legacy.require(set(resources) == {"skill:ponytail", "notice:mit"}
                                   and resources["skill:ponytail"]["origin"] == {
                                       "id": "ponytail", "path": "skills/ponytail", "relationship": "adapted"}
                                   and resources["notice:mit"]["license"] == "MIT"
                                   and resources["notice:mit"]["attribution"] == "Copyright (c) 2026 DietrichGebert"
                                   and legacy.tree(outputs[0] / "notices") == legacy.tree(pack_root / "notices"),
                                   "Ponytail export lost legal closure or adaptation origin")
                legacy.require(legacy.tree(outputs[0]) == legacy.tree(outputs[1]), "exports differ in content or modes")
                legacy.require(legacy.tree(workspace) == state, "export changed installation or client state")
                occupied = root / (surface + "-occupied")
                occupied.mkdir()
                (occupied / "sentinel").write_text("preserve\n")
                occupied_before = legacy.tree(occupied)
                probe.candidate(workspace, ["export", args.pack, "--surface", surface, "--skill", args.skill, "--output", str(occupied), "--json"], failure=True)
                legacy.require(legacy.tree(occupied) == occupied_before and legacy.tree(workspace) == state, "failed export mutated destination or state")
                probe.apply(workspace, ["uninstall", args.pack, "--surface", surface])
                for filename in ("AGENTS.md", "CLAUDE.md", "unrelated.txt"):
                    legacy.require((workspace / "project" / filename).read_bytes().rstrip(b"\n") == before[filename][1].rstrip(b"\n"), "uninstall changed unrelated document")
                for filename in ("packy.json", "packy.lock.json", "PACKY-NOTICES.md"):
                    legacy.require(not (workspace / "project" / filename).exists(), "uninstall retained " + filename)
                skill_root = workspace / "project" / (".agents/skills" if surface == "agents" else ".claude/skills")
                legacy.require(not skill_root.exists() or not list(skill_root.iterdir()), "uninstall retained managed skills")
                evidence["outcomes"].append({"surface": surface, "snapshot_id": snapshot, "pack": args.pack, "skill": args.skill, "format": expected_format, "result": "passed"})
            legacy.require(ambient == {key: legacy.tree(Path(env[key])) for key in ambient}, "candidate changed ambient state")
            probe.set_context("candidate-verification")
            legacy.require(legacy.checkout_commit(probe, legacy.ROOT) == commit, "candidate changed during probe")
            evidence["result"] = "passed"
    except (OSError, ValueError, KeyError, RuntimeError, legacy.subprocess.SubprocessError, KeyboardInterrupt) as error:
        evidence["error"] = str(error) or "probe interrupted"
        print("Generation probe: " + evidence["error"], file=sys.stderr)
    finally:
        signal.signal(signal.SIGTERM, handler)
        evidence["cleanup"] = "removed" if root is None or not root.exists() else "failed"
        if evidence["cleanup"] != "removed":
            evidence["result"] = "failed"
        print(json.dumps(evidence, indent=2))
    return 0 if evidence["result"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
