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
import time

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
    result = {}
    for directory, folders, files in os.walk(root, followlinks=True):
        for name in sorted(folders + files):
            path = Path(directory) / name
            result[str(path.relative_to(root))] = (path.lstat().st_mode, path.read_bytes() if path.is_file() else None,
                                                  os.readlink(path) if path.is_symlink() else None)
    return result


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
        self.set_context("candidate-verification")

    def set_context(self, stage, *, scenario=None, surface=None, scope=None):
        self.context = {"stage": stage, "scenario": scenario, "surface": surface, "scope": scope}

    def execute(self, command, *, approval=None, failure=False, timeout=None, context=None):
        receipt = {"command": [str(value) for value in command], "outcome": "failed",
                   "context": {**self.context, **(context or {})}}
        self.evidence["commands"].append(receipt)
        event = {"command_id": len(self.evidence["commands"]), "context": receipt["context"]}
        print("Content probe: " + json.dumps({**event, "event": "started", "command": receipt["command"]}),
              file=sys.stderr, flush=True)
        started = time.monotonic()
        try:
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
        finally:
            receipt["elapsed_seconds"] = time.monotonic() - started
            print("Content probe: " + json.dumps({**event, "event": receipt["outcome"],
                                                  "elapsed_seconds": receipt["elapsed_seconds"]}),
                  file=sys.stderr, flush=True)

    def candidate(self, workspace, args, *, snapshot=None, approval=None, failure=False):
        context = {"surface": args[args.index("--surface") + 1]} if "--surface" in args else None
        stdout, stderr = self.execute([str(self.executable), "catalog", "candidate", "--snapshot",
                                      str(snapshot or self.snapshot), "--workspace", str(workspace), "--", *args],
                                     approval=approval, failure=failure, context=context)
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
        before = tree(workspace)
        preview = self.candidate(workspace, [*args, "--dry-run", "--json"])
        require(tree(workspace) == before, "preview changed workspace")
        if args[0] in ("install", "uninstall") or args[0] == "update" and "--project" in args:
            observation = preview["observation"]
            require(isinstance(observation, str) and observation, "missing exact preview observation")
            operation = {"install": "project installation", "uninstall": "project surface uninstall",
                         "update": "project update"}[args[0]]
            prompts = [f"Approve {operation} for exact preview {observation}? [y/N] "]
            if args[0] == "update" and preview.get("retirements"):
                prompts.append(f"Approve destructive-cleanup phase for exact project update preview {observation}? [y/N] ")
        else:
            require(preview["plan_id"] and preview["disposition"] in ("applicable", "converged"), "global plan cannot apply")
            prompts = [f"Approve {phase['kind']} phase for exact plan {preview['plan_id']}? [y/N] "
                       for phase in preview["phases"] if phase["approval_required"]]
            if preview["disposition"] == "converged":
                require(not preview["phases"], "converged global plan unexpectedly contains action phases")
            else:
                require(bool(prompts), "global lifecycle missing approval phases")
        return self.candidate(workspace, [*args, "--json"], approval=prompts)

    def prepare(self, name, *, pack_ids=None):
        workspace = self.root / name
        listing = self.candidate(workspace, ["list", "--json"])
        actual = {pack["id"] for pack in listing["packs"]}
        require(actual == set(pack_ids or self.evidence["pack_ids"]), "complete catalog consumption lost Packs")
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
        probe.context["surface"] = surface
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
        probe.context["surface"] = surface
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
        probe.context["surface"] = surface
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


def checkout_commit(probe, project):
    state, _ = probe.execute(["git", "-C", str(project), "status", "--porcelain"])
    require(not state.strip(), "content probes require a clean committed Catalog candidate: " + str(project))
    commit, _ = probe.execute(["git", "-C", str(project), "rev-parse", "HEAD"])
    return commit.strip()


def build_catalog(probe, project, commit, output):
    built, _ = probe.execute([str(probe.executable), "catalog", "build", "--project", str(project),
                              "--source-repository", "yersonargotev/packy-catalog", "--source-commit",
                              commit, "--out-dir", str(output), "--json"], timeout=600)
    build = json.loads(built)
    require(build["result"] == "built", "incomplete candidate build")
    return {"candidate_commit": commit, "archive_sha256": build["archive_sha256"],
            "builder": build["index"]["builder"], "pack_ids": [pack["id"] for pack in build["index"]["packs"]]}


def pstack(probe, surfaces):
    baseline = probe.evidence["pstack_baseline"]
    old = Probe(probe.executable, probe.root / "baseline-dist", probe.root, probe.env, probe.evidence, probe.timeout)
    for scope in ("project", "global"):
        for runner in (probe, old):
            runner.set_context("content-acceptance", scenario="pstack",
                               scope="project" if scope == "project" else "disposable-global")
        workspace = old.prepare("pstack-" + scope, pack_ids=baseline["pack_ids"])
        base = workspace / ("project" if scope == "project" else "home")
        apply, remove = ("install", "uninstall") if scope == "project" else ("activate", "deactivate")
        targets = {surface: base / SKILL_DIRECTORIES[surface] for surface in ("codex", "claude")}
        original_project = tree(workspace / "project")
        personal_sentinels = {name: (workspace / name / "personal-sentinel").read_bytes() for name in ("home", "config")}
        inactive = {name: tree(workspace / name) for name in (("home", "config") if scope == "project" else ("project",))}
        for surface in ("codex", "claude"):
            old.apply(workspace, [apply, "pstack", "--surface", surface])
        installed = {name: tree(workspace / name) for name in ("home", "config", "project")}
        transition = probe.candidate(workspace, ["transition", "--expect-archive-sha256", baseline["archive_sha256"], "--json"])
        require(transition["report"] == "catalog-candidate-transition" and transition["result"] == "transitioned"
                and transition["provenance"] == "local-candidate"
                and transition["previous_archive_sha256"] == baseline["archive_sha256"]
                and transition["archive_sha256"] == probe.evidence["archive_sha256"], "wrong snapshot transition report")
        require(installed == {name: tree(workspace / name) for name in installed}, "transition changed installed baseline")
        for surface, other in (("codex", "claude"), ("claude", "codex")):
            untouched = tree(targets[other])
            args = ["update", "pstack", "--surface", surface]
            if scope == "project":
                args.append("--project")
            probe.apply(workspace, args)
            label = "Codex" if surface == "codex" else "Claude Code"
            require("## " + label + " execution" in (targets[surface] / "reflect/SKILL.md").read_text(),
                    "wrong pstack " + surface + " definition")
            require(untouched == tree(targets[other]), "pstack update changed other surface")
        helper = targets["codex"] / "poteto-mode/scripts/bootstrap.ts"
        original_helper = helper.read_bytes()
        original_mode = helper.stat().st_mode
        try:
            helper.write_bytes(original_helper + b"\n// drift probe\n")
            before = tree(workspace)
            out, diagnostic = probe.candidate(workspace, [remove, "pstack", "--surface", "codex", "--dry-run", "--json"], failure=True)
            require("drift" in out + diagnostic or "does not match its indexed identity" in diagnostic,
                    "helper rejection failed for unrelated reason")
            require(tree(workspace) == before, "helper drift rejection changed workspace")
        finally:
            helper.write_bytes(original_helper)
            helper.chmod(original_mode)
        claude_before = tree(targets["claude"])
        probe.apply(workspace, [remove, "pstack", "--surface", "codex"])
        require(claude_before == tree(targets["claude"]), "Codex removal changed Claude tree")
        probe.apply(workspace, [remove, "pstack", "--surface", "claude"])
        probe.apply(workspace, [apply, "pstack", "--surface", "codex", "--resource", "skill:architect"])
        for name in ("principle-exhaust-the-design-space", "principle-fix-root-causes", "principle-prove-it-works",
                     "principle-redesign-from-first-principles"):
            require((targets["codex"] / name / "SKILL.md").is_file(), "missing pstack effective dependency: " + name)
        require(not (targets["codex"] / "reflect").exists(), "architect selection installed unrelated reflect")
        probe.apply(workspace, [remove, "pstack", "--surface", "codex"])
        for surface, target in targets.items():
            require(not target.exists() or not list(target.iterdir()), "pstack retirement retained " + surface + " skills")
        if scope == "project":
            assert_retired(workspace / "project", original_project, "codex")
        require(inactive == {name: tree(workspace / name) for name in inactive}, "pstack lifecycle changed inactive scope")
        for name, contents in personal_sentinels.items():
            require((workspace / name / "personal-sentinel").read_bytes() == contents, "pstack changed unrelated personal file")
        probe.evidence["outcomes"].append({"scenario": "pstack", "scope": scope, "result": "passed",
                                          "checks": ["baseline-transition", "targeted-updates", "other-surface-preservation",
                                                     "helper-drift-rejection",
                                                     "effective-dependencies", "complete-retirement", "unrelated-state-preservation"]})


def pstack_withdrawal(probe, surfaces):
    """Prove support withdrawal and legacy retirement through the public CLI."""
    baseline_root = Path(probe.evidence["pstack_baseline_project"])
    previous = json.loads((baseline_root / "packs/pstack/pack.json").read_text())
    manifest = json.loads((ROOT / "packs/pstack/pack.json").read_text())
    old = Probe(probe.executable, probe.root / "baseline-dist", probe.root, probe.env, probe.evidence, probe.timeout)

    def content(path):
        # Global native directories link to a different retained snapshot after update.
        return {name: (mode & 0o777, data) for name, (mode, data, link) in tree(path).items()
                if data is not None}

    def unsupported(workspace, args):
        before = tree(workspace)
        output, diagnostic = probe.candidate(
            workspace, [*args, "--json"], failure=True,
            approval=[] if args[0] in ("install", "activate") and "--dry-run" not in args else None)
        require("support" in (output + diagnostic).lower() and "surface" in (output + diagnostic).lower(),
                "OpenCode rejection did not identify unsupported surface")
        require(tree(workspace) == before, "unsupported OpenCode request mutated workspace")

    # First observable assertion deliberately fails while the old support contract remains.
    workspace = probe.prepare("pstack-unsupported")
    unsupported(workspace, ["install", "pstack", "--surface", "opencode", "--dry-run"])
    require(previous["surfaces"] == ["claude", "codex", "opencode"], "withdrawal requires the reviewed three-host baseline")
    expected = json.loads(json.dumps(previous))
    expected["version"] = "5.0.0"
    expected["surfaces"].remove("opencode")
    for resource in expected["resources"]:
        for key in ("bindings", "variants", "surface_exclusions"):
            if key in resource:
                resource[key] = [item for item in resource[key] if item["surface"] != "opencode"]
    require(manifest == expected, "withdrawal changed more than version and OpenCode support")
    for args in (["show", "pstack"], ["get", "skill", "pstack:architect"], ["activate", "pstack", "--dry-run"],
                 ["install", "pstack"], ["activate", "pstack"]):
        unsupported(workspace, [*args, "--surface", "opencode"])

    for host in ("codex", "claude"):
        for runner in (probe, old):
            runner.set_context("content-acceptance", scenario="pstack-withdrawal", surface=host, scope="project")
        workspace = probe.prepare("pstack-preserved-access-" + host)
        target = tree(workspace / "project")
        discovery = probe.candidate(workspace, ["show", "pstack", "--surface", host, "--json"])
        old_workspace = old.prepare("pstack-baseline-access-" + host)
        old_discovery = old.candidate(old_workspace, ["show", "pstack", "--surface", host, "--json"])
        # Discovery reports the deliberate version/support change on each entry.
        expected_skills = json.loads(json.dumps(old_discovery["skills"]))
        for item in expected_skills:
            item["pack_version"] = "5.0.0"
            item["supported_surfaces"].remove("opencode")
        require(discovery["skills"] == expected_skills, "withdrawal changed effective discovery metadata")
        for resource in manifest["resources"]:
            effective = {**resource, **next((v for v in resource.get("variants", []) if v["surface"] == host), {})}
            if not effective.get("on_demand"):
                continue
            report = probe.candidate(workspace, ["get", "skill", "pstack:" + resource["id"], "--surface", host, "--json"])
            descriptors = {item["qualified_skill"]: item for item in [report, *report["dependencies"]]}
            require(report["qualified_skill"] == "pstack:" + resource["id"] and all(
                item["surface"] == host and item["pack_version"] == "5.0.0"
                and item["snapshot_id"] == report["snapshot_id"] for item in descriptors.values()),
                "withdrawal changed qualified access identity")
            assert_skill_content(descriptors, manifest, pack="pstack")
        require(tree(workspace / "project") == target, "preserved access changed target project")
        for scope in ("project", "global"):
            for runner in (probe, old):
                runner.set_context("content-acceptance", scenario="pstack-withdrawal", surface=host,
                                   scope="project" if scope == "project" else "disposable-global")
            workspace = old.prepare("pstack-preserved-" + host + "-" + scope)
            apply, remove = ("install", "uninstall") if scope == "project" else ("activate", "deactivate")
            old.apply(workspace, [apply, "pstack", "--surface", host])
            native = workspace / ("project" if scope == "project" else "home") / SKILL_DIRECTORIES[host]
            before = content(native)
            probe.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["pstack_baseline"]["archive_sha256"], "--json"])
            probe.apply(workspace, ["update", "pstack", "--surface", host, *(["--project"] if scope == "project" else [])])
            require(content(native) == before, "withdrawal changed native bytes or modes: " + host)
            probe.apply(workspace, [remove, "pstack", "--surface", host])
            require(not native.exists() or not list(native.iterdir()), "supported host retirement left skills")
        probe.evidence["outcomes"].append({"scenario": "pstack-withdrawal", "surface": host, "result": "passed",
                                           "checks": ["discovery-and-access-preserved", "complete-native-bytes-modes", "both-scopes-update-retirement"]})

    for scope in ("project", "global"):
        for runner in (probe, old):
            runner.set_context("content-acceptance", scenario="pstack-withdrawal", surface="opencode",
                               scope="project" if scope == "project" else "disposable-global")
        workspace = old.prepare("pstack-legacy-opencode-" + scope)
        apply, remove = ("install", "uninstall") if scope == "project" else ("activate", "deactivate")
        original_project = tree(workspace / "project")
        inactive = {name: tree(workspace / name) for name in (("home", "config") if scope == "project" else ("project",))}
        old.apply(workspace, [apply, "pstack", "--surface", "opencode"])
        native = workspace / ("project/.opencode/skills" if scope == "project" else "config/opencode/skills")
        require("## OpenCode execution" in (native / "reflect/SKILL.md").read_text(), "legacy OpenCode installation is missing")
        installed = {name: tree(workspace / name) for name in ("home", "config", "project")}
        probe.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["pstack_baseline"]["archive_sha256"], "--json"])
        require(installed == {name: tree(workspace / name) for name in installed}, "withdrawal transition changed legacy installation")
        args = ["update", "pstack", "--surface", "opencode", *(["--project"] if scope == "project" else [])]
        before = tree(workspace)
        if scope == "project":
            unsupported(workspace, [*args, "--dry-run"])
        else:
            output, diagnostic = probe.candidate(workspace, [*args, "--dry-run", "--json"], failure=True)
            reports = [json.loads(line) for line in output.splitlines() if line.strip()]
            plans = [item for item in reports if item["report"] == "pack-lifecycle-preview"]
            require(len(plans) == 1, "missing personal update preview")
            plan = plans[0]
            require(plan["disposition"] not in ("applicable", "converged")
                    and any(item["report"] == "pack-lifecycle-failure" and item["stage"] == "blocked"
                            for item in reports), "unsupported personal update became actionable")
        output, diagnostic = probe.candidate(workspace, [*args, "--json"], approval=[], failure=True)
        require("interactive terminal" not in diagnostic, "legacy update did not reach the non-actionable plan guard")
        if scope == "global":
            require("plan is not actionable" in output + diagnostic, "personal update failed before the plan guard")
        require(tree(workspace) == before, "failed legacy update changed state")
        for guard in ("drift", "missing-retained-content"):
            path = (native / "reflect/SKILL.md") if guard == "drift" else (native / "reflect/SKILL.md").resolve()
            if guard == "missing-retained-content" and scope == "project":
                # Project uninstall uses installed ownership, not retained content.
                continue
            data, mode = path.read_bytes(), path.stat().st_mode
            try:
                if guard == "drift":
                    path.write_bytes(data + b"\nDrift probe.\n")
                else:
                    path.unlink()
                before = tree(workspace)
                output, diagnostic = probe.candidate(workspace, [remove, "pstack", "--surface", "opencode", "--dry-run", "--json"], failure=True)
                require(any(word in (output + diagnostic).lower() for word in ("drift", "identity", "missing", "no such file", "do not exactly match the index")),
                        "legacy retirement guard failed for unrelated reason")
                require(tree(workspace) == before, "rejected legacy retirement changed state")
            finally:
                path.write_bytes(data)
                path.chmod(mode)
        probe.apply(workspace, [remove, "pstack", "--surface", "opencode"])
        require(not native.exists() or not list(native.iterdir()), "legacy retirement left skills")
        if scope == "project":
            assert_retired(workspace / "project", original_project, "opencode")
        require(inactive == {name: tree(workspace / name) for name in inactive}, "legacy retirement changed inactive scope")
        require(all((workspace / name / "personal-sentinel").read_text() == "Preserve personal state.\n"
                    for name in ("home", "config")), "legacy retirement changed unrelated personal state")
        probe.evidence["outcomes"].append({"scenario": "pstack-withdrawal", "surface": "opencode", "scope": scope, "result": "passed",
                                           "checks": ["unsupported-new-requests", "failed-update-preserves-state", "drift-rejection",
                                                      "explicit-legacy-retirement", "unrelated-state-preserved"],
                                           "missing_retained_guard": scope == "global"})


def bootstrap_state(base):
    """Preserve content/ownership while allowing lifecycle counters and notice spacing."""
    state = tree(base)
    for name in ("PACKY-NOTICES.md", ".packy/packs.json"):
        if name not in state:
            continue
        mode, content, link = state[name]
        if name.endswith(".json"):
            document = json.loads(content)
            document.pop("revision")
            content = json.dumps(document, sort_keys=True).encode()
        else:
            content = content.rstrip(b"\n")
        state[name] = (mode, content, link)
    return state


def packy_bootstrap(probe, surfaces, *, fixtures=True):
    """Exercise the official two-host bootstrap through the released lifecycle."""
    hosts = ("codex", "claude")
    version = json.loads((ROOT / "packs/packy/pack.json").read_text())["version"]
    for scope in ("project", "global"):
        probe.set_context("content-acceptance", scenario="packy-bootstrap",
                          scope="project" if scope == "project" else "disposable-global")
        workspace = probe.prepare("packy-bootstrap-" + scope)
        base = workspace / ("project" if scope == "project" else "home")
        apply, remove = ("install", "uninstall") if scope == "project" else ("activate", "deactivate")
        inactive = {name: tree(workspace / name) for name in (("home", "config") if scope == "project" else ("project",))}
        for host in hosts:
            native = base / SKILL_DIRECTORIES[host] / "unrelated-native"
            native.mkdir(parents=True)
            (native / "SKILL.md").write_text("# Unmanaged native skill\n")
            probe.apply(workspace, [apply, "emil", "--surface", host, "--resource", "skill:write-swift"])
        preserved = bootstrap_state(base)
        for host in hosts:
            other = "claude" if host == "codex" else "codex"
            untouched = tree(base / SKILL_DIRECTORIES[other])
            native_before = tree(base / SKILL_DIRECTORIES[host])
            probe.apply(workspace, [apply, "packy", "--surface", host, "--resource", "skill:packy-cli"])
            installed = base / SKILL_DIRECTORIES[host] / "packy-cli"
            source = ROOT / "packs/packy/skills" / host / "packy-cli"
            require(tree(installed) == tree(source), "bootstrap content/modes differ for " + host)
            require(untouched == tree(base / SKILL_DIRECTORIES[other]), "bootstrap changed other host")
            require((installed / "SKILL.md").is_file(), "bootstrap entry is unusable")
            native_after = {key: value for key, value in tree(base / SKILL_DIRECTORIES[host]).items()
                            if key != "packy-cli" and not key.startswith("packy-cli/")}
            require(native_after == native_before, "bootstrap changed unrelated same-host skills")
            if scope == "project":
                require(f"Pack: packy {version}" in (base / "PACKY-NOTICES.md").read_text()
                        and (ROOT / "packs/packy/notices/MIT").read_text() in (base / "PACKY-NOTICES.md").read_text(),
                        "bootstrap legal notice missing")
                probe.verify(workspace)
        for host in hosts:
            other = "claude" if host == "codex" else "codex"
            untouched = tree(base / SKILL_DIRECTORIES[other])
            probe.apply(workspace, [remove, "packy", "--surface", host])
            require(untouched == tree(base / SKILL_DIRECTORIES[other]), "bootstrap removal changed other host")
        require(bootstrap_state(base) == preserved, "bootstrap lifecycle changed unrelated active Pack/native state")
        require(inactive == {name: tree(workspace / name) for name in inactive}, "bootstrap changed inactive scope")
        for host in hosts:
            probe.apply(workspace, [remove, "emil", "--surface", host])
        probe.evidence["outcomes"].append({"scenario": "packy-bootstrap", "scope": scope, "result": "passed",
                                           "checks": ["two-host-content", "preview-consent", "other-host-preservation",
                                                      "unrelated-pack-and-native-preservation", "inactive-scope-preservation"]})
    if fixtures:
        reviewed_retrieval(probe)


def reviewed_retrieval(probe, *, integrated=False):
    """Complete inert authoring fixtures; never part of official publication inputs."""
    from urllib.parse import quote

    probe.set_context("candidate-construction", scenario="integrated-on-demand" if integrated else "packy-bootstrap")
    project = probe.root / "retrieval-authoring"
    notice_text = (ROOT / "packs/packy/notices/MIT").read_text().replace("Yerson Argote", "Fixture Authors")
    manifests = {}
    for pack_id in ("access-root", "access-support"):
        pack = project / "packs" / pack_id
        (pack / "notices").mkdir(parents=True)
        (pack / "notices/MIT").write_text(notice_text)
        resources = [{"kind": "notice", "id": "mit", "source": "notices/MIT", "description": "Fixture legal notice",
                      "license": "MIT", "attribution": "Copyright (c) 2026 Fixture Authors", "requires": [],
                      "conflicts": [], "bindings": [], "surface_exclusions": []}]
        for skill in (("guide", "local") if pack_id == "access-root" else ("guide",)):
            resource = {"kind": "skill", "id": skill, "source": "skills/" + skill,
                        "description": "Controlled complete access fixture", "requires": [], "conflicts": [],
                        "notices": ["notice:mit"], "bindings": [], "surface_exclusions": [], "variants": []}
            dependencies = ["access-root:local", "access-support:guide"] if pack_id == "access-root" and skill == "guide" else []
            for host in ("codex", "claude"):
                source = "skills/" + skill + ("-claude" if host == "claude" else "")
                directory = pack / source
                (directory / "references").mkdir(parents=True)
                (directory / "assets").mkdir()
                (directory / "references/context.md").write_text("# Reference v1\nUse the fictional widget rules, never submit a workflow.\n")
                (directory / "assets/rules.json").write_text('{"revision":1,"widget_limit":7}\n')
                sentinel = directory / "sentinel.sh"
                sentinel.write_text("#!/bin/sh\nprintf executed > should-never-exist\n")
                sentinel.chmod(0o755)
                (directory / "SKILL.md").write_text(
                    "# " + host + " " + pack_id + ":" + skill + "\n"
                    "[Rules](references/context.md) [Asset](assets/rules.json)\n" +
                    "".join("[" + name + "]({{packy.access:" + name + "}})\n" for name in dependencies))
                declaration = {"protocol": "skill-tree-v1", "reference_files": ["SKILL.md"],
                               "dependencies": [{"type": "skill", "target": name} for name in dependencies],
                               "prerequisites": ["packy-fixture-missing-runtime"]}
                if host == "codex":
                    resource["on_demand"] = declaration
                else:
                    resource["variants"].append({"surface": host, "source": source, "on_demand": declaration})
                resource["bindings"].append({"surface": host, "projection": "skill", "name": skill,
                                             "invocation": skill, "mode": "native", "sharing": "exclusive", "capabilities": []})
            resource["bindings"].sort(key=lambda binding: binding["surface"])
            resources.append(resource)
        manifests[pack_id] = {"schema_version": 3, "id": pack_id, "version": "1.0.0", "description": "Complete inert fixture",
                              "selectable": True, "surfaces": ["claude", "codex"], "readiness_obligations": ["runtime-usability"],
                              "external_requirements": [], "origins": [], "resources": resources}
        (pack / "pack.json").write_text(json.dumps(manifests[pack_id], indent=2) + "\n")
    probe.execute(["git", "init", "-q", str(project)])

    def commit_fixture(message, destination):
        probe.execute(["git", "-C", str(project), "add", "."])
        probe.execute(["git", "-C", str(project), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                       "commit", "-qm", message])
        return build_catalog(probe, project, checkout_commit(probe, project), destination)

    snapshot = probe.root / "retrieval-dist"
    first = commit_fixture("Complete inert access fixtures", snapshot)
    original = tree(project / "packs")
    newer = None
    if integrated:
        for pack_id, manifest in manifests.items():
            manifest["version"] = "1.1.0"
            (project / "packs" / pack_id / "pack.json").write_text(json.dumps(manifest, indent=2) + "\n")
        for path in (project / "packs").rglob("context.md"):
            path.write_text(path.read_text().replace("v1", "v2"))
        for path in (project / "packs").rglob("rules.json"):
            path.write_text('{"revision":2,"widget_limit":11}\n')
        newer = commit_fixture("Advance fixture rules explicitly", probe.root / "retrieval-next-dist")
    authored = tree(project)
    probe.evidence["retrieval_fixtures"] = {"original": first, "next": newer}
    executable = offline_executable(probe) if integrated else probe.executable
    runtime_path = probe.root / "fixture-no-runtimes"
    runtime_path.mkdir()
    (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
    runner = Probe(executable, snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)}, probe.evidence, probe.timeout)

    def verify_content(report, host):
        require(report["schema_version"] == 1 and report["report"] == "skill-access" and report["result"] == "prepared",
                "invalid fixture access envelope")
        descriptors = {item["qualified_skill"]: item for item in [report, *report["dependencies"]]}
        require(set(descriptors) == {"access-root:guide", "access-root:local", "access-support:guide"}
                and len(report["dependencies"]) == 2, "fixture same/cross-Pack closure incomplete")
        for identity, item in descriptors.items():
            require(item["pack_version"] == "1.0.0" and item["surface"] == host
                    and item["snapshot_id"] == report["snapshot_id"]
                    and item["prerequisites"] == ["packy-fixture-missing-runtime"], "fixture identity/prerequisites lost")
            pack_id, skill = identity.split(":")
            prefix = pack_id + "/skills/" + skill + ("-claude" if host == "claude" else "") + "/"
            expected = {name[len(prefix):]: value for name, value in original.items() if name.startswith(prefix)}
            root, entry = Path(item["resource_root"]), Path(item["entry_document"])
            require(root.is_absolute() and entry == root / "SKILL.md" and set(tree(root)) == set(expected),
                    "fixture resource paths/tree unusable")
            for name, (mode, data, link) in expected.items():
                path = root / name
                if data is not None:
                    def render(match):
                        return quote(os.path.relpath(descriptors[match[1]]["entry_document"], path.parent), safe="/")
                    expected_bytes = re.sub(r"\{\{packy.access:([^}]+)\}\}", render, data.decode()).encode()
                    require(path.read_bytes() == expected_bytes, "fixture supporting/asset/reference bytes differ")
                require(path.lstat().st_mode == mode and not link, "fixture supporting modes/links differ")
            require(any(p.read_text() == notice_text for p in root.parents[1].rglob("MIT")), "fixture legal content missing")
        return descriptors

    for host in ("codex", "claude"):
        runner.set_context("content-acceptance", scenario="integrated-on-demand" if integrated else "packy-bootstrap", surface=host)
        workspace = runner.prepare("retrieval-" + host, pack_ids=["access-root", "access-support"])
        # Use the fixture runner for native setup; no official Pack is activated.
        runner.apply(workspace, ["install", "access-support", "--surface", host, "--resource", "skill:guide"])
        native = workspace / "project" / SKILL_DIRECTORIES[host] / "guide/SKILL.md"
        native.write_text("# Modified installed fixture. Never replace this copy.\n")
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True, exist_ok=True)
        protected, snapshots = installation_state(workspace), tree(workspace / "snapshots")
        report = runner.candidate(workspace, ["get", "skill", "access-root:guide", "--surface", host, "--json"])
        descriptors = verify_content(report, host)
        prepared = tree(workspace / "home/.local/share/packy/skill-access")
        if integrated:
            next_runner = Probe(executable, probe.root / "retrieval-next-dist", probe.root, runner.env, probe.evidence, probe.timeout)
            next_runner.set_context("snapshot-transition", scenario="integrated-on-demand", surface=host)
            transition = next_runner.candidate(workspace, ["transition", "--expect-archive-sha256", first["archive_sha256"], "--json"])
            require(transition["result"] == "transitioned" and transition["archive_sha256"] == newer["archive_sha256"],
                    "fixture selection transition failed")
            independent = next_runner.candidate(workspace, ["get", "skill", "access-root:guide", "--surface", host, "--json"])
            require(independent["snapshot_id"] != report["snapshot_id"] and independent["snapshot_id"] == transition["snapshot_id"]
                    and independent["pack_version"] == "1.1.0"
                    and (Path(independent["resource_root"]) / "assets/rules.json").read_text() == '{"revision":2,"widget_limit":11}\n',
                    "independent request ignored changed fixture selection/content")
        else:
            next_runner = runner
        for identity in ("access-root:local", "access-support:guide"):
            nested = next_runner.candidate(workspace, ["get", "skill", identity, "--surface", host,
                                                       "--snapshot", report["snapshot_id"], "--json"])
            require(nested["snapshot_id"] == report["snapshot_id"] and nested["surface"] == host
                    and nested["pack_version"] == "1.0.0" and nested["qualified_skill"] == identity
                    and tree(Path(nested["resource_root"])) == tree(Path(descriptors[identity]["resource_root"])),
                    "nested fixture access lost original host/snapshot/content")
        observed = tree(workspace / "home/.local/share/packy/skill-access")
        require(all(observed.get(name) == value for name, value in prepared.items()), "earlier fixture paths changed")
        observed = tree(workspace / "snapshots")
        require(all(observed.get(name) == value for name, value in snapshots.items()), "original retained fixture changed")
        if integrated:
            retained = workspace / "snapshots" / report["snapshot_id"] / "packs/access-support/skills/guide/SKILL.md"
            retained.unlink()
            output, diagnostic = next_runner.candidate(workspace, ["get", "skill", "access-support:guide", "--surface", host,
                                                                  "--snapshot", report["snapshot_id"], "--json"], failure=True)
            require("snapshot_unavailable" in output or diagnostic.strip() == "Catalog Snapshot extracted files do not exactly match the index",
                    "missing retained fixture substituted latest/native content or failed for unrelated reason")
        require(protected == installation_state(workspace) and authored == tree(project), "fixture access changed native/target/source state")
        require(not list(workspace.rglob("should-never-exist")), "retrieval executed fixture content")
        probe.evidence["outcomes"].append({"scenario": "integrated-fixtures" if integrated else "packy-bootstrap", "surface": host,
                                           "result": "passed", "checks": ["same-and-cross-pack", "complete-effective-trees",
                                           "meaningful-assets-references-notices", "script-modes-nonexecution", "missing-runtimes",
                                           "nested-host-snapshot", "modified-installed-copy-preserved"] +
                                           (["offline", "selection-transition", "old-paths-retained", "independent-new-content", "missing-retained-rejected"] if integrated else [])})


# Reviewed expectations from issue #91, independent of the manifest under test.
MATTY_DESIGN_DEPENDENCIES = {
    "codebase-design": [], "domain-modeling": [], "grilling": [],
    "grill-me": ["grilling"], "grill-with-docs": ["domain-modeling", "grilling"],
    "improve-codebase-architecture": ["codebase-design", "domain-modeling", "grilling"],
    "to-questionnaire": [], "to-spec": [], "to-tickets": [],
    "triage": ["domain-modeling", "grilling"],
    "wayfinder": ["domain-modeling", "grilling", "prototype", "research"],
    "loop-me": ["grilling"], "setup-matt-pocock-skills": [], "wizard": [],
    "writing-for-agents": [], "wait-what": [], "handoff": [], "research": [], "prototype": [],
}


# Reviewed expectations from issue #92; recommendations are not required edges.
MATTY_DELIVERY_DEPENDENCIES = {
    "ask-matt": [], "claude-handoff": [], "code-review": [], "diagnosing-bugs": [],
    "implement": ["code-review", "tdd"], "implement-spec": ["code-review", "tdd"],
    "pr": [], "retro": ["writing-for-agents"],
    "setup-ts-deep-modules": ["codebase-design"], "tdd": ["codebase-design"],
    "teach": [], "writing-beats": [], "writing-fragments": [], "writing-shape": [],
}


def matty_delivery(probe, surfaces):
    matty_design(probe, surfaces, delivery=True)


def skill_descriptors(report, host, version, expected, *, pack="matty"):
    require(report["schema_version"] == 1 and report["report"] == "skill-access"
            and report["result"] == "prepared", "invalid skill-access envelope")
    descriptors = {item["qualified_skill"]: item for item in [report, *report["dependencies"]]}
    require(set(descriptors) == {pack + ":" + name for name in expected}, "wrong skill-access dependency closure")
    require(len(descriptors) == len(report["dependencies"]) + 1, "duplicate skill-access dependency descriptor")
    for descriptor in descriptors.values():
        require(descriptor["pack_version"] == version and descriptor["surface"] == host
                and descriptor["snapshot_id"] == report["snapshot_id"], "wrong skill-access identity/version/host/snapshot")
        entry, root = Path(descriptor["entry_document"]), Path(descriptor["resource_root"])
        require(entry.is_absolute() and root.is_absolute() and entry.parent == root
                and entry.name == "ACCESS.md" and entry.is_file(), "unusable skill-access resource location")
    return descriptors


def assert_skill_content(descriptors, manifest, *, pack="matty"):
    """Compare every authored byte/mode, rendering only explicitly reviewed tokens."""
    from urllib.parse import quote, unquote

    resources = {item["id"]: item for item in manifest["resources"]}
    for identity, descriptor in descriptors.items():
        resource = resources[identity.split(":")[1]]
        resource = {**resource, **next((v for v in resource.get("variants", []) if v["surface"] == descriptor["surface"]), {})}
        source = ROOT / "packs" / pack / resource["source"]
        root = Path(descriptor["resource_root"])
        authored = tree(source)
        require(set(tree(root)) == set(authored), "skill-access supporting tree is incomplete: " + identity)
        for relative, (mode, data, link) in authored.items():
            destination = root / relative
            require(destination.lstat().st_mode == mode and not link, "skill-access resource mode/link changed")
            if data is None:
                continue
            if relative in resource["on_demand"]["reference_files"]:
                def reference(match):
                    target = match[1]
                    if ":" not in target:
                        target = pack + ":" + target
                    require(target in descriptors, "authored skill-access reference lacks declared closure")
                    return quote(os.path.relpath(descriptors[target]["entry_document"], destination.parent), safe="/")
                data = re.sub(r"\{\{packy.access:([^}]+)\}\}", reference, data.decode()).encode()
            require(destination.read_bytes() == data, "skill-access content differs: " + identity + "/" + relative)
        # Check real Markdown links; fenced/inline code contains illustrative target paths.
        documents = root.glob("*.md") if pack == "matty" else sorted({root / "ACCESS.md", *root.glob("references/**/*.md"),
                                                                                         *(root / path for path in resource["on_demand"]["reference_files"])})
        for document in documents:
            prose = re.sub(r"```.*?```", "", document.read_text(), flags=re.S)
            prose = re.sub(r"`[^`\n]*`", "", prose)
            for target in re.findall(r"\]\(([^)]+)\)", prose):
                if "://" in target or target.startswith("#"):
                    continue
                # The retained why synthesis prompt illustrates an output citation.
                if pack == "pstack" and document.name == "synthesizer-prompt.md" and target == "url":
                    continue
                path = (document.parent / unquote(target.split("#")[0])).resolve()
                require(path.is_file() and path.stat().st_size > 0,
                        "broken skill-access relative reference in " + str(document) + ": " + target)
        pack_root = root
        while not (pack_root / "pack.json").is_file():
            require(pack_root.parent != pack_root, "prepared skill-access manifest missing")
            pack_root = pack_root.parent
        require(json.loads((pack_root / "pack.json").read_text()) == manifest, "prepared skill-access provenance changed")
        for notice in (item for item in manifest["resources"] if item["kind"] == "notice"):
            path = notice["source"]
            actual, original = pack_root / path, ROOT / "packs" / pack / path
            require(actual.read_bytes() == original.read_bytes() and actual.stat().st_mode == original.stat().st_mode,
                    pack + " notice bytes/mode changed: " + path)


def installation_state(workspace):
    # Candidate preparation is provider-owned data, separate from native installs.
    prefix = ".local/share/packy/skill-access"
    home = {name: value for name, value in tree(workspace / "home").items()
            if name != prefix and not name.startswith(prefix + "/")}
    return {"project": tree(workspace / "project"), "home": home, "config": tree(workspace / "config")}


def matty_design(probe, surfaces, *, delivery=False):
    """Check one reviewed slice or the complete Matty inventory through the CLI."""
    scenario = "matty-delivery" if delivery else "matty-design"
    inventory = {**MATTY_DESIGN_DEPENDENCIES, **MATTY_DELIVERY_DEPENDENCIES} if delivery else MATTY_DESIGN_DEPENDENCIES
    changed = MATTY_DELIVERY_DEPENDENCIES if delivery else MATTY_DESIGN_DEPENDENCIES
    wrappers = ("implement", "implement-spec", "retro", "setup-ts-deep-modules", "tdd") if delivery else ("grill-me", "grill-with-docs", "wayfinder")
    transition_root, missing_skill = ("implement", "tdd") if delivery else ("grill-me", "grilling")
    manifest = json.loads((ROOT / "packs/matty/pack.json").read_text())
    resources = {item["id"]: item for item in manifest["resources"]}
    authored = tree(ROOT / "packs/matty")
    baseline_resources = json.loads((Path(probe.evidence["matty_baseline_project"]) / "packs/matty/pack.json").read_text())["resources"]
    require(all(not item.get("on_demand") for item in baseline_resources if item["id"] in changed),
            "Matty baseline must precede the scoped on-demand adaptation")
    require(not delivery or set(inventory) == {item["id"] for item in manifest["resources"] if item["kind"] == "skill"},
            "complete Matty inventory is not accounted for")
    for host in ("codex", "claude"):
        probe.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-" + host)
        # Host tools and content runtimes are unavailable during all retrievals.
        runtime_path = probe.root / (scenario + "-no-runtimes-" + host)
        runtime_path.mkdir()
        (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
        access = Probe(probe.executable, probe.snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)},
                       probe.evidence, probe.timeout)
        access.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        # A modified local native primitive must never substitute for Matty's resource.
        installed = workspace / "project" / SKILL_DIRECTORIES[host] / ("tdd" if delivery else "grilling")
        if delivery:
            probe.apply(workspace, ["install", "matty", "--surface", host, "--resource", "skill:tdd"])
        else:
            installed.mkdir(parents=True)
        (installed / "SKILL.md").write_text("# Locally modified native primitive\nDo not use this copy.\n")
        # Seed provider ancestors so only preparation data is excluded below.
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True)
        protected = installation_state(workspace)
        snapshots = tree(workspace / "snapshots")
        discovery = access.candidate(workspace, ["show", "matty", "--surface", host, "--json"])
        require(discovery["schema_version"] == 1 and discovery["report"] == "skill-discovery", "wrong discovery contract")
        entries = {item["qualified_skill"]: item for item in discovery["skills"]}
        require(not delivery or set(entries) == {"matty:" + skill for skill in inventory}, "Matty discovery inventory changed")
        roots = {}
        for skill, dependencies in inventory.items():
            report = access.candidate(workspace, ["get", "skill", "matty:" + skill, "--surface", host, "--json"])
            item = entries["matty:" + skill]
            resource = resources[skill]
            require(resource["on_demand"]["dependencies"] == [{"type": "skill", "target": "matty:" + name}
                                                            for name in dependencies], "wrong direct Matty dependency declarations")
            require(item["compatible"] and not discovery["prerequisites_verified"],
                    "Matty discovery claims missing compatibility or verified runtimes")
            require(all(item["on_demand"].get(key, []) == value for key, value in resource["on_demand"].items())
                    and item["prerequisites"] == resource["on_demand"]["prerequisites"], "Matty discovery lost reviewed declarations")
            descriptors = skill_descriptors(report, host, manifest["version"], [skill, *dependencies, *sorted({nested for dependency in dependencies
                                                          for nested in inventory[dependency]} - set(dependencies))])
            require(report["qualified_skill"] == "matty:" + skill, "wrong Matty root")
            assert_skill_content(descriptors, manifest)
            for identity, descriptor in descriptors.items():
                require(descriptor["prerequisites"] == resources[identity.split(":")[1]]["on_demand"]["prerequisites"],
                        "Matty access lost known execution prerequisites")
            roots[skill] = report
            probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "skill": skill,
                                               "snapshot_id": report["snapshot_id"], "result": "passed",
                                               "checks": ["reviewed-discovery", "qualified-closure", "full-source-bytes-and-modes",
                                                          "relative-references", "legal-closure", "absent-content-runtimes"]})
        require(protected == installation_state(workspace), "Matty retrieval altered installation/target state")
        require(tree(workspace / "snapshots") == snapshots, "Matty retrieval mutated immutable snapshot")
        prepared = tree(workspace / "home/.local/share/packy/skill-access")
        # Switch only availability through the existing digest-bound candidate transition.
        baseline = probe.evidence["matty_baseline"]
        old = Probe(probe.executable, probe.root / "matty-baseline-dist", probe.root, access.env, probe.evidence, probe.timeout)
        old.set_context("snapshot-transition", scenario=scenario, surface=host, scope="project")
        transition = old.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["archive_sha256"], "--json"])
        require(transition["result"] == "transitioned" and transition["archive_sha256"] == baseline["archive_sha256"],
                "Matty controlled availability transition failed")
        for wrapper in wrappers:
            report = roots[wrapper]
            prior = {item["entry_document"]: Path(item["entry_document"]).read_bytes()
                     for item in [report, *report["dependencies"]]}
            for dependency in inventory[wrapper]:
                from urllib.parse import unquote
                entry = Path(report["entry_document"])
                references = re.findall(r"\[matty:" + dependency + r"\]\(([^)]+)\)", entry.read_text())
                expected = next(item for item in report["dependencies"] if item["qualified_skill"] == "matty:" + dependency)
                require(bool(references) and all((entry.parent / unquote(path)).resolve() == Path(expected["entry_document"])
                                                  for path in references), "nested authored reference points outside qualified closure")
                nested = old.candidate(workspace, ["get", "skill", "matty:" + dependency, "--surface", host,
                                                   "--snapshot", report["snapshot_id"], "--json"])
                require(nested["snapshot_id"] == report["snapshot_id"] and nested["surface"] == host
                        and nested["qualified_skill"] == expected["qualified_skill"]
                        and nested["pack_version"] == expected["pack_version"]
                        and Path(nested["entry_document"]).read_bytes() == prior[expected["entry_document"]],
                        "nested Matty access lost initiating snapshot/content")
            require(all(Path(path).read_bytes() == data for path, data in prior.items()), "prior Matty references stopped working")
        observed = tree(workspace / "home/.local/share/packy/skill-access")
        require(all(observed.get(path) == value for path, value in prepared.items()),
                "nested retrieval changed prior prepared bytes/modes")
        observed_snapshots = tree(workspace / "snapshots")
        require(all(observed_snapshots.get(path) == value for path, value in snapshots.items()),
                "transition/nested access changed prior immutable resources")
        output, _ = old.candidate(workspace, ["get", "skill", "matty:" + transition_root, "--surface", host, "--json"], failure=True)
        require(json.loads(output)["error"]["code"] == "incompatible_resource", "new independent access ignored changed selection")
        retained = workspace / "snapshots" / roots[transition_root]["snapshot_id"] / "packs/matty"
        (retained / resources[missing_skill]["source"] / "ACCESS.md").unlink()
        output, diagnostic = old.candidate(workspace, ["get", "skill", "matty:" + missing_skill, "--surface", host,
                                                      "--snapshot", roots[transition_root]["snapshot_id"], "--json"], failure=True)
        require("snapshot_unavailable" in output
                or diagnostic.strip() == "Catalog Snapshot extracted files do not exactly match the index",
                "missing retained Matty content fell back or failed for unrelated reason")
        require(protected == installation_state(workspace), "nested Matty access changed installation/target state")
        if delivery:
            matty_pstack_tdd(probe, access, host, manifest)
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["qualified-nested-references", "changed-selection", "retained-snapshot",
                                                      "missing-retained-fails", "modified-installed-copy-preserved", "unchanged-target-and-installation"]})
    require(tree(ROOT / "packs/matty") == authored, "Matty acceptance changed authored immutable content")
    matty_native(probe, manifest, inventory, scenario)


def matty_pstack_tdd(probe, access, host, manifest):
    """Use a separate native scope to respect same-name conflict rules."""
    from urllib.parse import unquote

    workspace = probe.prepare("matty-with-pstack-tdd-" + host)
    probe.apply(workspace, ["activate", "pstack", "--surface", host, "--resource", "skill:tdd"])
    native = workspace / "home" / SKILL_DIRECTORIES[host] / "tdd/SKILL.md"
    require(native.is_file() and native.read_bytes() == (ROOT / "packs/pstack/skills" / host / "tdd/SKILL.md").read_bytes(), "pstack TDD was not actually activated")
    (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True)
    protected = installation_state(workspace)
    snapshots = tree(workspace / "snapshots")
    report = access.candidate(workspace, ["get", "skill", "matty:implement-spec", "--surface", host, "--json"])
    descriptors = skill_descriptors(report, host, manifest["version"], ["implement-spec", "code-review", "tdd", "codebase-design"])
    assert_skill_content(descriptors, manifest)
    entry = Path(report["entry_document"])
    text = entry.read_text()
    # Follow the rendered implementation/delegation references, not installed names.
    for dependency in ("tdd", "code-review"):
        references = re.findall(r"\[matty:" + dependency + r"\]\(([^)]+)\)", text)
        require(bool(references), "implementation delegation lost qualified " + dependency)
        expected = descriptors["matty:" + dependency]
        require(all((entry.parent / unquote(path)).resolve() == Path(expected["entry_document"]) for path in references),
                "delegated reference targets a foreign/native resource")
        nested = access.candidate(workspace, ["get", "skill", "matty:" + dependency, "--surface", host,
                                               "--snapshot", report["snapshot_id"], "--json"])
        require(nested["qualified_skill"] == expected["qualified_skill"] and nested["surface"] == host
                and nested["snapshot_id"] == report["snapshot_id"]
                and Path(nested["entry_document"]).read_bytes() == Path(expected["entry_document"]).read_bytes(),
                "pstack-active nested retrieval substituted another workflow")
    require("Refactoring is not part of the loop" in Path(descriptors["matty:tdd"]["entry_document"]).read_text(),
            "Matty TDD semantics lost while pstack was active")
    require(protected == installation_state(workspace) and tree(workspace / "snapshots") == snapshots,
            "qualified Matty retrieval changed active pstack/target/immutable state")
    probe.evidence["outcomes"].append({"scenario": "matty-delivery", "surface": host, "result": "passed",
                                       "checks": ["pstack-tdd-active", "qualified-Matty-TDD", "delegated-rendered-references",
                                                  "nested-host-snapshot", "active-native-state-preserved"]})


def matty_native(probe, manifest, inventory, scenario):
    """Preserve native contracts and every existing source byte on all three hosts."""
    baseline_root = Path(probe.evidence["matty_baseline_project"])
    baseline = json.loads((baseline_root / "packs/matty/pack.json").read_text())
    previous = {item["id"]: item for item in baseline["resources"]}
    resources = {item["id"]: item for item in manifest["resources"]}
    for host in SURFACES:
        probe.set_context("native-regression", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-native-" + host)
        args = ["install", "matty", "--surface", host]
        for skill in inventory:
            args.extend(["--resource", "skill:" + skill])
        probe.apply(workspace, args)
        installed = workspace / "project" / SKILL_DIRECTORIES[host]
        require({path.name for path in installed.iterdir()} == set(inventory), "native Matty selection changed")
        for skill in inventory:
            before, after = previous[skill], resources[skill]
            require({key: value for key, value in after.items() if key not in ("origin", "on_demand")}
                    == {key: value for key, value in before.items() if key not in ("origin", "on_demand")}, "native Matty contract changed")
            original = baseline_root / "packs/matty" / before["source"]
            current = installed / skill
            for relative, observed in tree(original).items():
                require(tree(current).get(relative) == observed, "native Matty upstream bytes/modes changed: " + skill + "/" + relative)
        probe.verify(workspace)
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["native-selection", "unchanged-native-contracts", "all-original-bytes-and-modes", "project-verification"]})



# Reviewed issue #93 expectations, independent of the candidate manifest.
PSTACK_FOUNDATIONAL_DEPENDENCIES = {
    "principle-attack-the-premise": ["principle-build-the-lever", "principle-fix-root-causes", "principle-laziness-protocol"],
    "principle-boundary-discipline": [],
    "principle-build-the-lever": ["principle-laziness-protocol", "principle-prove-it-works"],
    "principle-encode-lessons-in-structure": [], "principle-exhaust-the-design-space": [],
    "principle-experience-first": [], "principle-explain-the-number": ["benchmark-checklist"],
    "principle-fix-root-causes": [], "principle-foundational-thinking": [],
    "principle-guard-the-context-window": [], "principle-laziness-protocol": [],
    "principle-make-operations-idempotent": [], "principle-migrate-callers-then-delete-legacy-apis": [],
    "principle-minimize-reader-load": [], "principle-model-the-domain": [],
    "principle-never-block-on-the-human": [], "principle-outcome-oriented-execution": [],
    "principle-prove-it-works": [], "principle-redesign-from-first-principles": [],
    "principle-separate-before-serializing-shared-state": [], "principle-sequence-verifiable-units": [],
    "principle-subtract-before-you-add": [], "principle-test-behavior-not-implementation": [],
    "principle-type-system-discipline": [],
    "arena": ["principle-laziness-protocol", "principle-prove-it-works", "principle-redesign-from-first-principles",
              "principle-separate-before-serializing-shared-state"],
    "benchmark-checklist": [], "bro": [], "how": [], "in-your-own-words": [], "interrogate": [],
    "ketchup": ["bro"], "reflect": ["principle-encode-lessons-in-structure"],
    "setup-pstack": [], "sharpen": [], "swarm": [], "tdd": [], "unslop": [], "why": [],
}

# The released engine also preserves these pre-existing native requires edges.
# They prepare background resources without invoking the optional comparisons.
PSTACK_NATIVE_BACKGROUND_DEPENDENCIES = {
    "principle-attack-the-premise": ["principle-redesign-from-first-principles"],
    "principle-build-the-lever": ["principle-encode-lessons-in-structure"],
    "principle-minimize-reader-load": ["principle-guard-the-context-window"],
}


def pstack_foundational(probe, surfaces):
    """Account for the exact host-effective slice without running its workflows."""
    from urllib.parse import unquote

    inventory = PSTACK_FOUNDATIONAL_DEPENDENCIES
    manifest = json.loads((ROOT / "packs/pstack/pack.json").read_text())
    resources = {item["id"]: item for item in manifest["resources"]}
    baseline_root = Path(probe.evidence["pstack_baseline_project"])
    baseline = json.loads((baseline_root / "packs/pstack/pack.json").read_text())
    authored = tree(ROOT / "packs/pstack")
    require(len(inventory) == 38, "pstack foundational scope changed")
    require(all(not variant.get("on_demand") for item in baseline["resources"] if item["id"] in inventory
                for variant in item["variants"]), "pstack baseline must precede foundational adaptation")

    def closure(skill):
        result = {skill}
        for dependency in set(inventory[skill] + PSTACK_NATIVE_BACKGROUND_DEPENDENCIES.get(skill, [])):
            result.update(closure(dependency))
        return result

    for host in ("codex", "claude"):
        probe.set_context("content-acceptance", scenario="pstack-foundational", surface=host, scope="project")
        workspace = probe.prepare("pstack-foundational-" + host)
        # Exercise qualified access while a real pstack native TDD is active and modified.
        probe.apply(workspace, ["activate", "pstack", "--surface", host, "--resource", "skill:tdd"])
        native = workspace / "home" / SKILL_DIRECTORIES[host] / "tdd/SKILL.md"
        require(native.read_bytes() == (ROOT / "packs/pstack/skills" / host / "tdd/SKILL.md").read_bytes(),
                "native pstack TDD activation did not use the effective host body")
        original_snapshots = tree(workspace / "snapshots")
        # Personal activation links immutable content; customize an owned copy.
        if native.parent.is_symlink():
            original = native.parent.resolve()
            native.parent.unlink()
            shutil.copytree(original, native.parent)
        native.write_text("# Modified installed TDD\nPreserve this native copy.\n")
        require(tree(workspace / "snapshots") == original_snapshots, "native customization changed the immutable snapshot")
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True)
        protected, snapshots = installation_state(workspace), tree(workspace / "snapshots")
        runtime_path = probe.root / ("pstack-no-content-runtimes-" + host)
        runtime_path.mkdir()
        (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
        access = Probe(probe.executable, probe.snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)},
                       probe.evidence, probe.timeout)
        access.set_context("content-acceptance", scenario="pstack-foundational", surface=host, scope="project")
        discovery = access.candidate(workspace, ["show", "pstack", "--surface", host, "--json"])
        require(discovery["schema_version"] == 1 and discovery["report"] == "skill-discovery"
                and not discovery["prerequisites_verified"], "pstack discovery misreports readiness")
        entries = {item["qualified_skill"]: item for item in discovery["skills"]}
        require(set(entries) == {"pstack:" + item["id"] for item in manifest["resources"] if item["kind"] == "skill"},
                "pstack discovery lost logical skills")
        roots = {}
        for skill, dependencies in inventory.items():
            effective = next(variant for variant in resources[skill]["variants"] if variant["surface"] == host)
            declaration = effective["on_demand"]
            require(declaration["dependencies"] == [{"type": "skill", "target": "pstack:" + name} for name in dependencies],
                    "pstack required/optional dependency classification changed: " + skill)
            item = entries["pstack:" + skill]
            require(item["compatible"] and item["prerequisites"] == declaration["prerequisites"]
                    and all(item["on_demand"].get(key, []) == value for key, value in declaration.items()),
                    "pstack discovery lost effective reviewed metadata: " + skill)
            report = access.candidate(workspace, ["get", "skill", "pstack:" + skill, "--surface", host, "--json"])
            descriptors = skill_descriptors(report, host, manifest["version"], closure(skill), pack="pstack")
            require(report["qualified_skill"] == "pstack:" + skill, "wrong pstack root")
            assert_skill_content(descriptors, manifest, pack="pstack")
            for identity, descriptor in descriptors.items():
                expected = next(v for v in resources[identity.split(":")[1]]["variants"] if v["surface"] == host)
                require(descriptor["prerequisites"] == expected["on_demand"]["prerequisites"], "pstack prerequisites lost")
            roots[skill] = report
            probe.evidence["outcomes"].append({"scenario": "pstack-foundational", "surface": host, "skill": skill,
                                               "snapshot_id": report["snapshot_id"], "result": "passed",
                                               "checks": ["effective-discovery", "qualified-required-closure", "full-source-bytes-and-modes",
                                                          "supporting-references", "legal-closure", "absent-content-runtimes"]})
        # Discovery carries metadata, never the large investigation/reference bodies.
        why_root = Path(roots["why"]["resource_root"])
        require("references/epistemics.md" in Path(roots["why"]["entry_document"]).read_text(), "why confidence pointer lost")
        for reference in (why_root / "references").rglob("*.md"):
            require(json.dumps(reference.read_text())[1:-1] not in json.dumps(discovery),
                    "discovery eagerly embeds why supporting bodies")
        for skill in ("arena", "how", "interrogate", "setup-pstack", "swarm", "why"):
            require("~/.pstack/" + host + "-models.md" in Path(roots[skill]["entry_document"]).read_text(),
                    "pstack access substituted a different host's preference contract")
        matty_manifest = json.loads((ROOT / "packs/matty/pack.json").read_text())
        matty = access.candidate(workspace, ["get", "skill", "matty:tdd", "--surface", host,
                                             "--snapshot", roots["tdd"]["snapshot_id"], "--json"])
        assert_skill_content(skill_descriptors(matty, host, matty_manifest["version"], ["tdd", "codebase-design"]), matty_manifest)
        pstack_text = Path(roots["tdd"]["entry_document"]).read_text()
        require("# TDD Bug Fix" in pstack_text and "Do not force a test when it would be impractical" in pstack_text
                and "Refactoring is not part of the loop" in Path(matty["entry_document"]).read_text(),
                "qualified TDD identities lost their distinct policies")
        require(protected == installation_state(workspace) and tree(workspace / "snapshots") == snapshots,
                "pstack retrieval applied setup or modified native/target/immutable state")
        prepared = tree(workspace / "home/.local/share/packy/skill-access")
        old = Probe(probe.executable, probe.root / "baseline-dist", probe.root, access.env, probe.evidence, probe.timeout)
        old.set_context("snapshot-transition", scenario="pstack-foundational", surface=host, scope="project")
        transition = old.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["archive_sha256"], "--json"])
        require(transition["result"] == "transitioned"
                and transition["archive_sha256"] == probe.evidence["pstack_baseline"]["archive_sha256"], "pstack transition failed")
        for wrapper in ("arena", "principle-attack-the-premise", "principle-build-the-lever", "principle-explain-the-number", "ketchup", "reflect"):
            report = roots[wrapper]
            entry = Path(report["entry_document"])
            targets = {item["qualified_skill"]: item for item in report["dependencies"]}
            source = (ROOT / "packs/pstack/skills" / host / wrapper / "ACCESS.md").read_text()
            tokens = re.findall(r"\{\{packy.access:([^}]+)\}\}", source)
            links = re.findall(r"\]\(([^)]+)\)", entry.read_text())
            for dependency in inventory[wrapper]:
                expected = targets["pstack:" + dependency]
                require("pstack:" + dependency in tokens and any((entry.parent / unquote(path)).resolve()
                        == Path(expected["entry_document"]) for path in links), "pstack rendered reference missed declared dependency")
                nested = old.candidate(workspace, ["get", "skill", "pstack:" + dependency, "--surface", host,
                                                   "--snapshot", report["snapshot_id"], "--json"])
                require(nested["snapshot_id"] == report["snapshot_id"] and nested["surface"] == host
                        and nested["qualified_skill"] == expected["qualified_skill"]
                        and Path(nested["entry_document"]).read_bytes() == Path(expected["entry_document"]).read_bytes(),
                        "pstack nested access lost initiating identity/host/snapshot/content")
        observed = tree(workspace / "home/.local/share/packy/skill-access")
        require(all(observed.get(path) == value for path, value in prepared.items()), "nested access changed prior prepared resources")
        retained = tree(workspace / "snapshots")
        require(all(retained.get(path) == value for path, value in snapshots.items()), "transition mutated retained snapshots")
        output, _ = old.candidate(workspace, ["get", "skill", "pstack:arena", "--surface", host, "--json"], failure=True)
        require(json.loads(output)["error"]["code"] == "incompatible_resource", "independent access ignored changed selection")
        missing = workspace / "snapshots" / roots["arena"]["snapshot_id"] / "packs/pstack/skills" / host / "arena/ACCESS.md"
        missing.unlink()
        output, diagnostic = old.candidate(workspace, ["get", "skill", "pstack:arena", "--surface", host,
                                                      "--snapshot", roots["arena"]["snapshot_id"], "--json"], failure=True)
        require("snapshot_unavailable" in output or diagnostic.strip() == "Catalog Snapshot extracted files do not exactly match the index",
                "missing retained pstack content silently fell back")
        require(protected == installation_state(workspace), "nested access changed native/target state")
        probe.evidence["outcomes"].append({"scenario": "pstack-foundational", "surface": host, "result": "passed",
                                           "checks": ["qualified-distinct-TDD", "modified-active-native-preserved", "setup-remains-inert",
                                                      "progressive-why-references", "rendered-nested-references", "retained-snapshot",
                                                      "changed-selection", "missing-retained-fails"]})
    def native_contract(resource):
        result = json.loads(json.dumps(resource))
        result["bindings"] = [b for b in result["bindings"] if b["surface"] in ("codex", "claude")]
        result["variants"] = [v for v in result["variants"] if v["surface"] in ("codex", "claude")]
        for variant in result["variants"]:
            variant.pop("on_demand", None)
        return result

    # Original native contracts/bytes/modes survive on the two supported hosts.
    previous = {item["id"]: item for item in baseline["resources"]}
    for host in ("codex", "claude"):
        probe.set_context("native-regression", scenario="pstack-foundational", surface=host, scope="project")
        workspace = probe.prepare("pstack-foundational-native-" + host)
        args = ["install", "pstack", "--surface", host]
        for skill in inventory:
            args.extend(["--resource", "skill:" + skill])
        probe.apply(workspace, args)
        installed = workspace / "project" / SKILL_DIRECTORIES[host]
        require({path.name for path in installed.iterdir()} == set(inventory), "pstack native selection changed")
        for skill in inventory:
            before, after = previous[skill], resources[skill]
            require(native_contract(before) == native_contract(after), "native pstack contract changed: " + skill)
            effective = next(v for v in before["variants"] if v["surface"] == host)
            original = tree(baseline_root / "packs/pstack" / effective["source"])
            observed = tree(installed / skill)
            require(all(observed.get(path) == value for path, value in original.items()), "native pstack content/mode changed: " + skill)
        probe.verify(workspace)
        probe.evidence["outcomes"].append({"scenario": "pstack-foundational", "surface": host, "result": "passed",
                                           "checks": ["native-selection-and-contracts", "all-original-bytes-and-modes", "project-verification"]})
    require(tree(ROOT / "packs/pstack") == authored, "pstack acceptance mutated authored content")


# Reviewed issue #94 graph, including principles used by architect's runner.
PSTACK_ENGINEERING_DEPENDENCIES = {
    "architect": ["arena", "how", "interrogate", "principle-boundary-discipline",
                  "principle-encode-lessons-in-structure", "principle-exhaust-the-design-space",
                  "principle-fix-root-causes", "principle-foundational-thinking", "principle-laziness-protocol",
                  "principle-make-operations-idempotent", "principle-minimize-reader-load",
                  "principle-outcome-oriented-execution", "principle-redesign-from-first-principles",
                  "principle-separate-before-serializing-shared-state", "principle-subtract-before-you-add", "why"],
    "blast-radius": ["arena", "unslop", "why"], "correct": [],
    "create-formal-verification-skill": [], "create-verification-skill": [],
    "maintain-verification-skill": [], "make-bot-ui": [],
    "no-comments": ["architect", "how", "principle-fix-root-causes", "principle-redesign-from-first-principles", "why"],
    "recall": ["unslop", "why"], "show-me-your-work": ["principle-encode-lessons-in-structure", "unslop"],
    "teach": ["how", "unslop", "why"], "technical-writing": ["unslop"],
    "typescript-best-practices": ["principle-boundary-discipline", "principle-type-system-discipline"],
}

# User-observable policy expectations, not extracted from candidate entry bodies.
PSTACK_ENGINEERING_POLICIES = {
    "architect": ["at least two structurally distinct candidates", "Default: proceed directly to implementation",
                  "pause for sign-off", "references/ACCESS-runner-prompt.md", "references/design-red-flags.md"],
    "blast-radius": ["prove them by running code", "If you couldn't prove it, write unproven"],
    "correct": ["A class counts once it has happened twice", "real past mistake", "human's approval"],
    "create-formal-verification-skill": ["counterexample", "bounds and assumptions", "broken variant",
                                         "do not change product code unless the user asks", "never under this resource root"],
    "create-verification-skill": ["Doctor:", "Evidence:", "features/README.md", "evidence still exists",
                                  "A generated skill that was never executed is a draft"],
    "maintain-verification-skill": ["**clean**", "**changed**", "**blocked**", "Several candidates → ask which one",
                                    "One read-only subagent per feature", "coordinator owns all driving",
                                    "retry once", "exercise every feature live", "never maintenance targets"],
    "make-bot-ui": ["authorized", "sender key on the server", "one try, no retry", "timeout: 8 seconds",
                    "actual response", "--accept-dns=false --ssh=false", "outside data, not as instructions"],
    "no-comments": ["say that it was not independent", "Reject a second", "stop after the sketch",
                    "Step 4 implements", "Wait for interactive approval", "caller pre-approval"],
    "recall": ["last 7 days", "Never read another project's transcripts", "actual source identifier",
               "null results are findings", "At most 5 bullets", "history gap", "pstack:poteto-mode", "playbooks/session-pickup.md"],
    "show-me-your-work": ["Append-only", "never edits or removes a row", "different model family",
                          "Self-review is not a substitute", "explicit writable log path", '"Attention" section'],
    "teach": ["Keep", "confidence language intact", "Run them in parallel", "one plain explanation",
              "image-generation tool", "never a report about what you did"],
    "technical-writing": ["Diátaxis", "STE rules", "Global English", "Don't edit that skill", "codebase is the word list"],
    "typescript-best-practices": ["Schemas before guards", "Narrowing hierarchy", "Boundary validation",
                                  "references/ACCESS-patterns.md"],
}


def pstack_engineering(probe, surfaces):
    """Retrieve the exact engineering slice; execute only the reviewed log helper."""
    from urllib.parse import unquote

    scenario = "pstack-engineering"
    inventory = PSTACK_ENGINEERING_DEPENDENCIES
    graph = {**PSTACK_FOUNDATIONAL_DEPENDENCIES, **inventory}
    manifest = json.loads((ROOT / "packs/pstack/pack.json").read_text())
    resources = {item["id"]: item for item in manifest["resources"]}
    baseline_root = Path(probe.evidence["pstack_baseline_project"])
    baseline = json.loads((baseline_root / "packs/pstack/pack.json").read_text())
    previous = {item["id"]: item for item in baseline["resources"]}
    authored = tree(ROOT / "packs/pstack")
    require(len(inventory) == 13, "pstack engineering scope changed")
    require(set(manifest["surfaces"]) == {"codex", "claude"}
            and all(item["surface"] != "opencode" for resource in manifest["resources"]
                    for key in ("bindings", "variants") for item in resource.get(key, [])),
            "engineering restored withdrawn pstack host support")
    require(all(not variant.get("on_demand") for name in inventory for variant in previous[name]["variants"]),
            "pstack engineering baseline must precede this adaptation")

    def closure(skill):
        result = {skill}
        for dependency in set(graph[skill] + PSTACK_NATIVE_BACKGROUND_DEPENDENCIES.get(skill, [])):
            result.update(closure(dependency))
        return result

    for host in ("codex", "claude"):
        probe.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-" + host)
        probe.apply(workspace, ["activate", "pstack", "--surface", host, "--resource", "skill:architect"])
        native = workspace / "home" / SKILL_DIRECTORIES[host] / "architect"
        if native.is_symlink():
            original = native.resolve()
            native.unlink()
            shutil.copytree(original, native)
        (native / "SKILL.md").write_text("# Modified native architect. Preserve this copy.\n")
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True)
        protected, snapshots = installation_state(workspace), tree(workspace / "snapshots")
        runtime_path = probe.root / (scenario + "-no-runtimes-" + host)
        runtime_path.mkdir()
        (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
        access = Probe(probe.executable, probe.snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)},
                       probe.evidence, probe.timeout)
        access.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        discovery = access.candidate(workspace, ["show", "pstack", "--surface", host, "--json"])
        require(discovery["schema_version"] == 1 and discovery["report"] == "skill-discovery"
                and not discovery["prerequisites_verified"], "engineering discovery misreports readiness")
        entries = {item["qualified_skill"]: item for item in discovery["skills"]}
        roots = {}
        for skill, dependencies in inventory.items():
            # The public retrieval is the primary assertion, including its red baseline.
            report = access.candidate(workspace, ["get", "skill", "pstack:" + skill, "--surface", host, "--json"])
            effective = next(v for v in resources[skill]["variants"] if v["surface"] == host)
            declaration = effective["on_demand"]
            require(declaration["dependencies"] == [{"type": "skill", "target": "pstack:" + dep} for dep in dependencies],
                    "engineering required/optional dependency classification changed: " + skill)
            item = entries["pstack:" + skill]
            require(item["compatible"] and item["prerequisites"] == declaration["prerequisites"]
                    and all(item["on_demand"].get(key, []) == value for key, value in declaration.items()),
                    "engineering discovery lost reviewed declarations")
            descriptors = skill_descriptors(report, host, manifest["version"], closure(skill), pack="pstack")
            require(report["qualified_skill"] == "pstack:" + skill, "wrong engineering root")
            assert_skill_content(descriptors, manifest, pack="pstack")
            for identity, descriptor in descriptors.items():
                expected = next(v for v in resources[identity.split(":")[1]]["variants"] if v["surface"] == host)
                require(descriptor["prerequisites"] == expected["on_demand"]["prerequisites"], "engineering prerequisites lost")
            for reference in (ROOT / "packs/pstack" / effective["source"] / "references").rglob("*.md"):
                require(json.dumps(reference.read_text())[1:-1] not in json.dumps(discovery),
                        "engineering discovery eagerly embeds supporting bodies")
            text = Path(report["entry_document"]).read_text()
            require(all(fragment in text for fragment in PSTACK_ENGINEERING_POLICIES[skill]),
                    "engineering policy lost: " + skill)
            require(".agents/skills" in text if host == "codex" else "disable-model-invocation: true" in text
                    and ".claude/skills" in text and "do not invoke them through the Skill tool" in text,
                    "engineering host invocation contract lost")
            require(skill == "correct" or "~/.pstack/" + host + "-models.md" in text,
                    "engineering model preference host changed")
            roots[skill] = report
            probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "skill": skill,
                                               "snapshot_id": report["snapshot_id"], "result": "passed",
                                               "checks": ["effective-discovery", "qualified-required-closure", "full-source-bytes-and-modes",
                                                          "supporting-and-legal-content", "host-workflow-policy", "absent-content-runtimes"]})
        require(protected == installation_state(workspace) and tree(workspace / "snapshots") == snapshots,
                "engineering retrieval executed a procedure or changed native/target/immutable state")
        prepared_root = workspace / "home/.local/share/packy/skill-access"
        prepared = tree(prepared_root)
        decision_log_helper(probe, roots["show-me-your-work"], host)
        require(tree(prepared_root) == prepared and tree(workspace / "snapshots") == snapshots
                and protected == installation_state(workspace), "log helper changed prepared/native/target resources")
        old = Probe(probe.executable, probe.root / "baseline-dist", probe.root, access.env, probe.evidence, probe.timeout)
        old.set_context("snapshot-transition", scenario=scenario, surface=host, scope="project")
        transition = old.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["archive_sha256"], "--json"])
        require(transition["result"] == "transitioned"
                and transition["archive_sha256"] == probe.evidence["pstack_baseline"]["archive_sha256"], "engineering transition failed")
        for wrapper in ("architect", "no-comments", "recall", "teach", "technical-writing", "typescript-best-practices", "show-me-your-work"):
            report = roots[wrapper]
            targets = {item["qualified_skill"]: item for item in report["dependencies"]}
            effective = next(v for v in resources[wrapper]["variants"] if v["surface"] == host)
            for dependency in inventory[wrapper]:
                expected = targets["pstack:" + dependency]
                references = []
                for relative in effective["on_demand"]["reference_files"]:
                    document = Path(report["resource_root"]) / relative
                    references.extend((document.parent / unquote(path)).resolve()
                                      for path in re.findall(r"\[pstack:" + dependency + r"\]\(([^)]+)\)", document.read_text()))
                require(references and all(path == Path(expected["entry_document"]) for path in references),
                        "engineering prepared reference missed dependency: " + wrapper + " -> " + dependency)
                nested = old.candidate(workspace, ["get", "skill", "pstack:" + dependency, "--surface", host,
                                                   "--snapshot", report["snapshot_id"], "--json"])
                require(nested["snapshot_id"] == report["snapshot_id"] and nested["surface"] == host
                        and nested["qualified_skill"] == expected["qualified_skill"]
                        and nested["pack_version"] == expected["pack_version"]
                        and Path(nested["entry_document"]).read_bytes() == Path(expected["entry_document"]).read_bytes(),
                        "engineering nested retrieval changed initiating identity/snapshot/content")
        observed = tree(prepared_root)
        require(all(observed.get(path) == value for path, value in prepared.items()), "engineering prior prepared paths changed")
        retained = tree(workspace / "snapshots")
        require(all(retained.get(path) == value for path, value in snapshots.items()), "engineering transition mutated snapshots")
        output, _ = old.candidate(workspace, ["get", "skill", "pstack:architect", "--surface", host, "--json"], failure=True)
        require(json.loads(output)["error"]["code"] == "incompatible_resource", "engineering independent call ignored new selection")
        missing = workspace / "snapshots" / roots["architect"]["snapshot_id"] / "packs/pstack/skills" / host / "architect/ACCESS.md"
        missing.unlink()
        output, diagnostic = old.candidate(workspace, ["get", "skill", "pstack:architect", "--surface", host,
                                                      "--snapshot", roots["architect"]["snapshot_id"], "--json"], failure=True)
        require("snapshot_unavailable" in output or diagnostic.strip() == "Catalog Snapshot extracted files do not exactly match the index",
                "engineering missing retained content silently fell back")
        require(protected == installation_state(workspace), "engineering nested retrieval changed target/native state")
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["rendered-nested-and-supporting-references", "retained-snapshot", "changed-selection",
                                                      "missing-retained-fails", "modified-active-native-preserved", "inert-workflows"]})

    def native_closure(skill, host):
        resource = {**previous[skill], **next(v for v in previous[skill]["variants"] if v["surface"] == host)}
        result = {skill}
        for dependency in resource["requires"]:
            if dependency.startswith("skill:"):
                result.update(native_closure(dependency.split(":")[1], host))
        return result

    for host in ("codex", "claude"):
        probe.set_context("native-regression", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-native-" + host)
        probe.apply(workspace, ["install", "emil", "--surface", host, "--resource", "skill:write-swift"])
        unrelated = tree(workspace / "project" / SKILL_DIRECTORIES[host] / "write-swift")
        inactive = {name: tree(workspace / name) for name in ("home", "config")}
        guidance = {name: (workspace / "project" / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md", "unrelated.txt")}
        args = ["install", "pstack", "--surface", host]
        for skill in inventory:
            args.extend(["--resource", "skill:" + skill])
        probe.apply(workspace, args)
        installed = workspace / "project" / SKILL_DIRECTORIES[host]
        expected = set().union(*(native_closure(skill, host) for skill in inventory))
        require({path.name for path in installed.iterdir()} == expected | {"write-swift"}, "engineering native scoped selection changed")
        require(tree(installed / "write-swift") == unrelated and inactive == {name: tree(workspace / name) for name in inactive}
                and all((workspace / "project" / name).read_bytes() == data for name, data in guidance.items()),
                "engineering native regression changed unrelated resources or inactive state")
        for skill in expected:
            def native_contract(resource):
                result = json.loads(json.dumps(resource))
                for variant in result["variants"]:
                    variant.pop("on_demand", None)
                return result
            require(native_contract(previous[skill]) == native_contract(resources[skill]), "engineering native contract changed")
            source = next(v["source"] for v in previous[skill]["variants"] if v["surface"] == host)
            original, actual = tree(baseline_root / "packs/pstack" / source), tree(installed / skill)
            require(all(actual.get(path) == value for path, value in original.items()), "engineering original native bytes/modes changed")
        probe.verify(workspace)
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["native-scoped-selection-and-contracts", "original-bytes-and-modes", "project-verification"]})
    require(tree(ROOT / "packs/pstack") == authored, "engineering acceptance mutated authored sources")


def decision_log_helper(probe, report, host):
    """Execute only the reviewed six-argument helper into explicitly owned output."""
    with tempfile.TemporaryDirectory(prefix="decision-log-", dir=probe.root) as directory:
        output = Path(directory) / "output/decisions.tsv"
        unrelated = Path(directory) / "unrelated.txt"
        unrelated.write_bytes(b"Preserve unrelated target content.\n")
        helper = Path(report["resource_root"]) / "scripts/log.sh"
        before = tree(Path(report["resource_root"]))
        probe.execute([str(helper), str(output), "frame", "chose the public CLI", "real user boundary", "issue #94", "open"])
        first = output.read_bytes()
        probe.execute([str(helper), str(output), "=formula", "+decision\tcell", "-why\nline", "@evidence\rvalue", "done"])
        require(output.read_bytes().startswith(first), "decision log did not preserve append history")
        rows = output.read_text().splitlines()
        require(rows[0] == "ts\tphase\tdecision\twhy\tevidence\tresult" and rows.count(rows[0]) == 1
                and len(rows) == 3 and all(len(row.split("\t")) == 6 for row in rows), "decision log row/header contract changed")
        require(rows[1].split("\t")[1:] == ["frame", "chose the public CLI", "real user boundary", "issue #94", "open"]
                and rows[2].split("\t")[1:] == ["'=formula", "'+decision cell", "'-why line", "'@evidence value", "done"],
                "decision log failed formula/tab/newline escaping")
        require(before == tree(Path(report["resource_root"])) and unrelated.read_bytes() == b"Preserve unrelated target content.\n",
                "decision helper changed resources or unrelated target")
    require(not Path(directory).exists(), "decision helper owned execution state was not removed")
    probe.evidence["outcomes"].append({"scenario": "pstack-engineering", "surface": host, "result": "passed",
                                       "checks": ["explicit-disposable-log-output", "single-header", "append-preservation", "six-columns",
                                                  "formula-tab-newline-escaping", "source-target-preservation", "helper-state-cleanup"]})


# Independently reviewed issue #95 edges. Optional routes are deliberately absent.
PSTACK_ORCHESTRATION_DEPENDENCIES = {
    "automate-me": ["poteto-mode", "unslop"],
    "figure-it-out": ["architect", "arena", "poteto-mode", "principle-encode-lessons-in-structure",
                      "principle-foundational-thinking", "principle-laziness-protocol", "principle-never-block-on-the-human",
                      "principle-prove-it-works", "principle-separate-before-serializing-shared-state",
                      "principle-sequence-verifiable-units", "show-me-your-work"],
    "poteto-help": ["poteto-mode", "setup-pstack"],
    "poteto-mode": ["architect", "arena", "benchmark-checklist", "how", "interrogate", "ketchup", "no-comments",
                    "principle-attack-the-premise", "principle-boundary-discipline", "principle-build-the-lever",
                    "principle-encode-lessons-in-structure", "principle-exhaust-the-design-space", "principle-experience-first",
                    "principle-explain-the-number", "principle-fix-root-causes", "principle-foundational-thinking",
                    "principle-guard-the-context-window", "principle-laziness-protocol", "principle-make-operations-idempotent",
                    "principle-migrate-callers-then-delete-legacy-apis", "principle-minimize-reader-load", "principle-model-the-domain",
                    "principle-never-block-on-the-human", "principle-outcome-oriented-execution", "principle-prove-it-works",
                    "principle-redesign-from-first-principles", "principle-separate-before-serializing-shared-state",
                    "principle-sequence-verifiable-units", "principle-subtract-before-you-add", "principle-test-behavior-not-implementation",
                    "principle-type-system-discipline", "reflect", "setup-pstack", "show-me-your-work", "swarm", "tdd",
                    "technical-writing", "unslop", "why"],
}

PSTACK_ORCHESTRATION_POLICIES = {
    "automate-me": ["unless the user already asked", "since the skill was last edited", "current project",
                    "what's changed or missing", "Don't copy its content", "Show the draft to the user",
                    "explicit writable destination", "does not activate its workflow", "author and validate"],
    "figure-it-out": ["before any code", "falsifiable predicate", "Scope, quantified", "multi-hour run earns one checkpoint",
                      "independently-landable units", "State the hypothesis", "never a self-report",
                      "VERIFIED, NOT VERIFIED, or INCONCLUSIVE", "show-me-your-work", "independent/diverse-review gate"],
    "poteto-help": ["packy show pstack", "selected optional recommendation", "actual returned host entry",
                    "Never substitute Matty TDD", "does not authorize", "Missing preferences alone",
                    "A help question calls for an explanation", "Playbooks are files", "current CLI help and catalog version"],
    "poteto-mode": ["optional host integrations", "follow-up", "always pause", "required independent-review gate remains incomplete",
                    "Same-model reviewers are not a multi-model panel", "PSTACK_HELPER_WORKSPACE", "original target working directory",
                    "scripts/", "separate temporary execution/dependency space"],
}


def pstack_orchestration(probe, surfaces):
    """Complete 55-skill access, pinned nested routes, native contracts and safe helpers."""
    from urllib.parse import unquote

    scenario = "pstack-orchestration"
    graph = {**PSTACK_FOUNDATIONAL_DEPENDENCIES, **PSTACK_ENGINEERING_DEPENDENCIES,
             **PSTACK_ORCHESTRATION_DEPENDENCIES}
    manifest = json.loads((ROOT / "packs/pstack/pack.json").read_text())
    resources = {item["id"]: item for item in manifest["resources"]}
    baseline_root = Path(probe.evidence["pstack_baseline_project"])
    baseline = json.loads((baseline_root / "packs/pstack/pack.json").read_text())
    previous = {item["id"]: item for item in baseline["resources"]}
    authored = tree(ROOT / "packs/pstack")
    require(len(graph) == 55 and {r["id"] for r in manifest["resources"] if r["kind"] == "skill"} == set(graph),
            "pstack complete inventory changed")
    require(manifest["surfaces"] == baseline["surfaces"] and set(manifest["surfaces"]) == {"codex", "claude"},
            "orchestration restored withdrawn host support")
    require(all(not v.get("on_demand") for name in PSTACK_ORCHESTRATION_DEPENDENCIES for v in previous[name]["variants"]),
            "orchestration baseline must precede this adaptation")

    def closure(skill):
        result = {skill}
        for dependency in set(graph[skill] + PSTACK_NATIVE_BACKGROUND_DEPENDENCIES.get(skill, [])):
            result.update(closure(dependency))
        return result

    for host in ("codex", "claude"):
        probe.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-" + host)
        probe.apply(workspace, ["activate", "pstack", "--surface", host, "--resource", "skill:poteto-help"])
        native = workspace / "home" / SKILL_DIRECTORIES[host] / "poteto-help"
        if native.is_symlink():
            original = native.resolve()
            native.unlink()
            shutil.copytree(original, native)
        (native / "SKILL.md").write_text("# Preserve this modified native help.\n")
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True)
        protected, snapshots = installation_state(workspace), tree(workspace / "snapshots")
        runtime_path = probe.root / (scenario + "-no-runtimes-" + host)
        runtime_path.mkdir()
        (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
        access = Probe(probe.executable, probe.snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)},
                       probe.evidence, probe.timeout)
        access.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        discovery = access.candidate(workspace, ["show", "pstack", "--surface", host, "--json"])
        entries = {item["qualified_skill"]: item for item in discovery["skills"]}
        require(discovery["schema_version"] == 1 and discovery["report"] == "skill-discovery"
                and not discovery["prerequisites_verified"] and len(entries) == 55
                and all(item["compatible"] for item in entries.values()), "complete pstack discovery is not compatible")
        roots = {}
        for skill, dependencies in graph.items():
            report = access.candidate(workspace, ["get", "skill", "pstack:" + skill, "--surface", host, "--json"])
            require(report["qualified_skill"] == "pstack:" + skill, "wrong complete-inventory identity")
            effective = next(v for v in resources[skill]["variants"] if v["surface"] == host)
            declaration = effective["on_demand"]
            require(declaration["dependencies"] == [{"type": "skill", "target": "pstack:" + d} for d in dependencies],
                    "pstack required/optional classification changed: " + skill)
            item = entries["pstack:" + skill]
            require(item["prerequisites"] == declaration["prerequisites"]
                    and all(item["on_demand"].get(key, []) == value for key, value in declaration.items()),
                    "complete discovery lost effective declarations")
            descriptors = skill_descriptors(report, host, manifest["version"], closure(skill), pack="pstack")
            assert_skill_content(descriptors, manifest, pack="pstack")
            for identity, descriptor in descriptors.items():
                expected = next(v for v in resources[identity.split(":")[1]]["variants"] if v["surface"] == host)
                require(descriptor["prerequisites"] == expected["on_demand"]["prerequisites"], "pstack prerequisites changed")
            entry = Path(report["entry_document"]).read_text()
            if skill in PSTACK_ORCHESTRATION_POLICIES:
                require(all(fragment.lower() in entry.lower() for fragment in PSTACK_ORCHESTRATION_POLICIES[skill]),
                        "orchestration substantive policy lost: " + skill)
                require(".agents/skills" in entry if host == "codex" else "disable-model-invocation: true" in entry
                        and ".claude/skills" in entry and "do not invoke them through the Skill tool" in entry,
                        "orchestration host invocation contract lost")
                require("~/.pstack/" + host + "-models.md" in entry, "orchestration model preference host changed")
            if skill == "poteto-help":
                require("$skill-name" not in entry and "/skill-name" not in entry
                        and "$principle-<name>" not in entry and "/principle-<name>" not in entry,
                        "help retains unqualified native routing")
            if skill == "poteto-mode":
                supporting = {
                    "autopilot-full": ["initiating Catalog Snapshot", "nothing merges until", "hourly audit"],
                    "autopilot-stack": ["initiating Catalog Snapshot", "never the landing", "Only you rebase or retarget"],
                    "multi-phase-plan": ["Do not implement", "live block is mandatory", "operator's explicit go", "ACCESS-<execution playbook>"],
                    "orchestrate": ["The CLI never spawns", "Every file has exactly one writer", "A new head SHA voids the row"],
                    "babysit": ["Declare a mode", "Babysitting never authorizes merging"],
                    "shipping": ["Only a verdict from an agent that did not write the code counts"],
                    "worktree-cleanup": ["The bucket is advice, not permission", "Verify usage before deleting"],
                    "eval": ["one judge scores both", "never by model name", "mark chain-following evidence unknown", "`candidate`, or `arena` in any directory"],
                    "bug-fix": ["Confirm the surviving", "cheap local test path", "pstack:tdd"],
                }
                for playbook, fragments in supporting.items():
                    body = (Path(report["resource_root"]) / ("playbooks/ACCESS-" + playbook + ".md")).read_text()
                    require(all(fragment in body for fragment in fragments), "supporting policy lost: " + playbook)
                    require("playbook from trunk" not in body and "playbooks from trunk" not in body,
                            "autopilot substitutes latest playbooks for retained content")
            for reference in (Path(report["resource_root"]) / "references").glob("*.md"):
                require(json.dumps(reference.read_text())[1:-1] not in json.dumps(discovery), "discovery embeds supporting bodies")
            roots[skill] = report
            probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "skill": skill,
                                               "snapshot_id": report["snapshot_id"], "result": "passed",
                                               "checks": ["qualified-identity-version-surface-snapshot", "complete-required-closure",
                                                          "full-tree-bytes-modes-notices", "rendered-references", "absent-content-runtimes"]})
        # Exercise the colliding name at the same public boundary.
        matty = access.candidate(workspace, ["get", "skill", "matty:tdd", "--surface", host, "--json"])
        require("# TDD Bug Fix" in Path(roots["tdd"]["entry_document"]).read_text()
                and "Refactoring is not part of the loop" in Path(matty["entry_document"]).read_text(),
                "help can substitute another Pack's TDD")
        require(protected == installation_state(workspace) and snapshots == tree(workspace / "snapshots"),
                "retrieval ran content or changed native/target/snapshot state")
        prepared_root = workspace / "home/.local/share/packy/skill-access"
        prepared = tree(prepared_root)
        orchestration_helpers(probe, roots["poteto-mode"], host)
        decision_log_helper(probe, roots["show-me-your-work"], host)
        require(prepared == tree(prepared_root) and snapshots == tree(workspace / "snapshots"),
                "helpers changed prepared/retained resources")
        old = Probe(probe.executable, probe.root / "baseline-dist", probe.root, access.env, probe.evidence, probe.timeout)
        old.set_context("snapshot-transition", scenario=scenario, surface=host, scope="project")
        transition = old.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["archive_sha256"], "--json"])
        require(transition["result"] == "transitioned"
                and transition["archive_sha256"] == probe.evidence["pstack_baseline"]["archive_sha256"], "orchestration transition failed")
        routes = [("poteto-mode", "tdd", "playbooks/ACCESS-bug-fix.md"),
                  ("figure-it-out", "show-me-your-work", "ACCESS.md"),
                  ("figure-it-out", "principle-sequence-verifiable-units", "ACCESS.md"),
                  ("automate-me", "poteto-mode", "ACCESS.md"), ("automate-me", "unslop", "ACCESS.md")]
        for wrapper, dependency, relative in routes:
            report = roots[wrapper]
            expected = next(item for item in report["dependencies"] if item["qualified_skill"] == "pstack:" + dependency)
            document = Path(report["resource_root"]) / relative
            links = re.findall(r"\[pstack:" + dependency + r"\]\(([^)]+)\)", document.read_text())
            require(links and all((document.parent / unquote(path)).resolve() == Path(expected["entry_document"]) for path in links),
                    "nested playbook/entry reference points outside qualified closure")
            nested = old.candidate(workspace, ["get", "skill", "pstack:" + dependency, "--surface", host,
                                               "--snapshot", report["snapshot_id"], "--json"])
            require(nested["snapshot_id"] == report["snapshot_id"] and nested["surface"] == host
                    and nested["qualified_skill"] == "pstack:" + dependency
                    and Path(nested["entry_document"]).read_bytes() == Path(expected["entry_document"]).read_bytes(),
                    "nested route lost initiating context")
        # Help's TDD and mode's bespoke route remain optional and pinned, including delegated context.
        for wrapper, selected in [("poteto-help", "tdd"), ("poteto-help", "figure-it-out"), ("poteto-mode", "figure-it-out")]:
            report = roots[wrapper]
            require(selected not in PSTACK_ORCHESTRATION_DEPENDENCIES[wrapper], "selected optional route became required")
            text = Path(report["entry_document"]).read_text()
            require("pstack:" + selected in text and "delegat" in text and "scratch/output" in text,
                    "optional/delegated route lacks qualified context")
            nested = old.candidate(workspace, ["get", "skill", "pstack:" + selected, "--surface", host,
                                               "--snapshot", report["snapshot_id"], "--json"])
            require(nested["snapshot_id"] == report["snapshot_id"] and nested["surface"] == host
                    and nested["qualified_skill"] == "pstack:" + selected
                    and nested["pack_version"] == manifest["version"], "optional route followed new selection")
        observed, retained = tree(prepared_root), tree(workspace / "snapshots")
        require(all(observed.get(p) == value for p, value in prepared.items())
                and all(retained.get(p) == value for p, value in snapshots.items()), "transition invalidated prior resource paths")
        independent = old.candidate(workspace, ["get", "skill", "pstack:tdd", "--surface", host, "--json"])
        require(independent["snapshot_id"] == transition["snapshot_id"] and independent["pack_version"] == baseline["version"],
                "independent request ignored newly selected baseline")
        output, _ = old.candidate(workspace, ["get", "skill", "pstack:poteto-help", "--surface", host, "--json"], failure=True)
        require(json.loads(output)["error"]["code"] == "incompatible_resource", "independent orchestration ignored baseline selection")
        require(protected == installation_state(workspace), "nested retrieval changed target/native state")
        missing = workspace / "snapshots" / roots["poteto-mode"]["snapshot_id"] / "packs/pstack/skills" / host / "poteto-mode/playbooks/ACCESS-bug-fix.md"
        missing.unlink()
        # Native links share this retained fixture; observe our deliberate damage before testing rejection.
        unavailable_state = installation_state(workspace)
        output, diagnostic = old.candidate(workspace, ["get", "skill", "pstack:poteto-mode", "--surface", host,
                                                      "--snapshot", roots["poteto-mode"]["snapshot_id"], "--json"], failure=True)
        require("snapshot_unavailable" in output or diagnostic.strip() == "Catalog Snapshot extracted files do not exactly match the index",
                "missing retained supporting content silently fell back")
        require(unavailable_state == installation_state(workspace), "failed retained retrieval changed target/native state")
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["all-55-obtainable", "distinct-qualified-TDD", "retained-required-optional-delegated-context",
                                                      "prior-paths-usable", "new-selection", "missing-supporting-content-fails", "inert-retrieval"]})
        orchestration_native(probe, host, manifest, baseline_root, previous)
    require(authored == tree(ROOT / "packs/pstack"), "acceptance mutated authored pstack sources")


def orchestration_native(probe, host, manifest, baseline_root, previous):
    resources = {item["id"]: item for item in manifest["resources"]}
    def native_closure(skill):
        resource = {**previous[skill], **next(v for v in previous[skill]["variants"] if v["surface"] == host)}
        result = {skill}
        for dependency in resource["requires"]:
            if dependency.startswith("skill:"):
                result.update(native_closure(dependency.split(":")[1]))
        return result
    probe.set_context("native-regression", scenario="pstack-orchestration", surface=host, scope="project")
    workspace = probe.prepare("pstack-orchestration-native-" + host)
    probe.apply(workspace, ["install", "emil", "--surface", host, "--resource", "skill:write-swift"])
    unrelated = tree(workspace / "project" / SKILL_DIRECTORIES[host] / "write-swift")
    inactive = {name: tree(workspace / name) for name in ("home", "config")}
    guidance = {name: (workspace / "project" / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md", "unrelated.txt")}
    args = ["install", "pstack", "--surface", host]
    for skill in PSTACK_ORCHESTRATION_DEPENDENCIES:
        args.extend(["--resource", "skill:" + skill])
    probe.apply(workspace, args)
    installed = workspace / "project" / SKILL_DIRECTORIES[host]
    expected = set().union(*(native_closure(skill) for skill in PSTACK_ORCHESTRATION_DEPENDENCIES))
    require({p.name for p in installed.iterdir()} == expected | {"write-swift"}, "native scoped selection changed")
    require(unrelated == tree(installed / "write-swift") and inactive == {name: tree(workspace / name) for name in inactive}
            and all((workspace / "project" / name).read_bytes() == data for name, data in guidance.items()),
            "native regression changed unrelated/inactive state")
    for skill in expected:
        def native_contract(resource):
            result = json.loads(json.dumps(resource))
            for variant in result["variants"]:
                variant.pop("on_demand", None)
            return result
        require(native_contract(previous[skill]) == native_contract(resources[skill]), "native contract changed: " + skill)
        source = next(v["source"] for v in previous[skill]["variants"] if v["surface"] == host)
        original, actual = tree(baseline_root / "packs/pstack" / source), tree(installed / skill)
        require(all(actual.get(path) == value for path, value in original.items()), "original native bytes/modes changed: " + skill)
    probe.verify(workspace)
    probe.evidence["outcomes"].append({"scenario": "pstack-orchestration", "surface": host, "result": "passed",
                                       "checks": ["native-scoped-selection", "all-original-contracts-bytes-modes", "unrelated-inactive-preserved"]})


def orchestration_helpers(probe, report, host):
    """Opt-in public helper checks; no live forge, merge, message or deletion fixtures."""
    source = Path(report["resource_root"])
    original = tree(source)
    with tempfile.TemporaryDirectory(prefix="orchestration-helpers-", dir=probe.root) as directory:
        owned = Path(directory)
        env = isolated_environment(owned)
        for name in ("BUN_INSTALL_CACHE_DIR",):
            destination = owned / name.lower()
            destination.mkdir()
            env[name] = str(destination)
        target, output = owned / "target", owned / "output"
        target.mkdir()
        output.mkdir()
        (target / "unrelated.txt").write_bytes(b"Keep target bytes.\n")
        runner = Probe(probe.executable, probe.snapshot, target, env, probe.evidence, probe.timeout)
        runner.set_context("helper-execution", scenario="pstack-orchestration", surface=host, scope="disposable")
        node, bun = (shutil.which(name, path=env["PATH"]) for name in ("node", "bun"))
        require(node is not None and bun is not None, "helper probes require reviewed Node and Bun")
        versions = {}
        for name, executable in (("node", node), ("bun", bun)):
            versions[name] = runner.execute([executable, "--version"])[0].strip()
        fixture = (ROOT / "scripts/probes/fixtures/pstack-plan.md").read_text().replace("@AUDIT@", "hourly audit")
        for name, content, diagnostic in (
                ("valid", fixture, "0 problems"),
                ("obsolete-cadence", fixture.replace("hourly audit", "five-minute audit"), "hourly audit"),
                ("missing-live-lane", re.sub(r"^- \[ \] Lane 10\..*\n", "", fixture, flags=re.M), "expected 1 to 10")):
            plan = output / (name + ".md")
            plan.write_text(content)
            stdout, stderr = runner.execute([node, str(source / "scripts/check-plan.mjs"), str(plan)], failure=name != "valid")
            require(diagnostic in stdout + stderr, "plan fixture did not exercise expected rejection: " + name)
        # A fake forge at the external process boundary prevents real authenticated queries.
        tools_path = owned / "bin"
        tools_path.mkdir()
        forge = tools_path / "gh"
        forge.write_text("#!" + sys.executable + "\nimport json,sys\nfrom pathlib import Path\n"
                         "Path(" + repr(str(output / "forge-calls.jsonl")) + ").open('a').write(json.dumps(sys.argv[1:])+'\\n')\n"
                         "print('fixture forge deliberately unavailable', file=sys.stderr)\nsys.exit(1)\n")
        forge.chmod(0o755)
        env["PATH"] = str(tools_path) + os.pathsep + env["PATH"]
        store = output / "store"
        orch = [bun, str(source / "scripts/orch/orch.ts"), "--store", str(store), "--json"]
        initialized, _ = runner.execute([*orch, "init"], timeout=180)
        require(json.loads(initialized)["store"] == str(store), "orchestration ignored explicit store")
        runner.execute([*orch, "unit", "add", "fixture-unit", "--track", "fixture"])
        observed, _ = runner.execute([*orch, "unit", "get", "fixture-unit"])
        require(json.loads(observed)["id"] == "fixture-unit" and json.loads(observed)["track"] == "fixture",
                "orchestration unit roundtrip failed")
        runner.execute([*orch, "ledger", "record", "1", "a" * 40, "unit-test-verified", "--evidence", str(output / "proof.txt")])
        verdict, _ = runner.execute([*orch, "ledger", "check", "1", "a" * 40])
        require(json.loads(verdict)["verdict"] == "unit-test-verified", "orchestration lost exact-head ledger verdict")
        runner.execute([*orch, "unit", "set", "missing", "--state", "done"], failure=True)
        watcher = [bun, str(source / "scripts/watch-pr/watch-pr")]
        help_text, _ = runner.execute([*watcher, "--help"], timeout=180)
        require("--status-only" in help_text and "--queued-stack" in help_text, "watcher help lost modes")
        runner.execute([*watcher, "--pr", "0"], failure=True)
        rejected, _ = runner.execute([*watcher, "--owner", "fixture", "--repo", "fixture", "--pr", "1", "--status-only", "--max-query-errors", "1", "--timeout", "5"], failure=True)
        verdict = json.loads(rejected.splitlines()[-1])
        require(verdict["kind"] == "BLOCKER" and verdict["blocker"]["kind"] == "status-query" and verdict["terminal"] and (output / "forge-calls.jsonl").is_file(),
                "watcher did not expose the external query failure")
        require(not any("merge" in json.loads(line) or "send" in json.loads(line)
                        for line in (output / "forge-calls.jsonl").read_text().splitlines()), "helper attempted an external mutation")
        require(not list(Path(env["TMPDIR"]).iterdir()), "bootstrap leaked temporary execution/dependency state")
        # The actual exported bootstrap is exercised with a harmless disposable entry.
        scripts = owned / "bootstrap-input"
        shutil.copytree(source / "scripts", scripts)
        entry = scripts / "cwd-probe.ts"
        marker = output / "bootstrap.json"
        entry.write_text('import { ensureDependenciesInstalled } from "./bootstrap.ts";\n'
                         'import { existsSync, writeFileSync } from "node:fs";\n'
                         'ensureDependenciesInstalled();\n'
                         'writeFileSync(process.env.PSTACK_PROBE_OUTPUT!, JSON.stringify({cwd:process.cwd(),'
                         'directory:import.meta.dir, dependency:existsSync(import.meta.dir+"/node_modules/commander/package.json")}));\n'
                         'process.exitCode=Number(process.env.PSTACK_PROBE_EXIT ?? "0");\n')
        copied = tree(scripts)
        runner.env = {**env, "PSTACK_PROBE_OUTPUT": str(marker)}
        runner.execute([bun, str(entry)], timeout=180)
        details = json.loads(marker.read_text())
        require(Path(details["cwd"]).resolve() == target.resolve() and details["dependency"]
                and Path(details["directory"]).is_relative_to(Path(env["TMPDIR"]))
                and not Path(details["directory"]).exists(), "bootstrap lost target cwd, staged dependencies or cleanup")
        runner.env = {**runner.env, "PSTACK_PROBE_EXIT": "7"}
        runner.execute([bun, str(entry)], failure=True, timeout=180)
        require(probe.evidence["commands"][-1]["exit_status"] == 7 and not list(Path(env["TMPDIR"]).iterdir())
                and copied == tree(scripts), "bootstrap failure lost status, cleanup or input preservation")
        # Bound an interrupted entry and remove all its owned state through the outer lifecycle.
        entry.write_text(entry.read_text().replace('process.exitCode=Number(process.env.PSTACK_PROBE_EXIT ?? "0");',
                                                   'await new Promise(() => {setInterval(() => {}, 1000);});'))
        runner.env = {**env, "PSTACK_PROBE_OUTPUT": str(marker)}
        try:
            runner.execute([bun, str(entry)], timeout=10)
        except RuntimeError as error:
            require("deadline" in str(error).lower() or "timed out" in str(error).lower(), "unexpected interruption failure")
        else:
            raise RuntimeError("interruption fixture did not reach its deadline")
        require(tree(target) == {"unrelated.txt": ((target / "unrelated.txt").stat().st_mode, b"Keep target bytes.\n", None)},
                "helper changed target project content")
        require(original == tree(source), "helpers modified immutable prepared resources")
    require(not Path(directory).exists(), "helper success/failure/interruption owned state remains")
    probe.evidence["outcomes"].append({"scenario": "pstack-orchestration", "surface": host, "result": "passed",
                                       "runtime_versions": versions,
                                       "checks": ["plan-positive-and-two-rejections", "owned-store-roundtrip-and-exact-head-ledger",
                                                  "watcher-help-usage-and-controlled-query-failure", "real-bootstrap-dependency-staging",
                                                  "target-cwd-preserved", "success-failure-interruption-cleanup", "sources-unchanged"]})



# Reviewed issue #96 routes. Related lists, attribution, and retired alternatives
# are not required edges; first-round generation is conditional in cross-critique.
WARP_SPECIFICATION_DEPENDENCIES = {
    "check-impl-against-spec": [], "council": [],
    "cross-critique": ["council", "research"], "implement-specs": [],
    "merge-risk": [], "research": [], "saga": [], "scan-new-specs": [],
    "spec-driven-implementation": ["implement-specs", "write-product-spec", "write-tech-spec"],
    "update-skill": [], "validate-changes-match-specs": [], "write-feature-docs": [],
    "write-pr-description": [], "write-product-spec": ["write-tech-spec"], "write-tech-spec": [],
}

WARP_SPECIFICATION_POLICIES = {
    "check-impl-against-spec": ["spec_context.md", "pr_diff.txt", "review.json", "Do not post to GitHub directly"],
    "council": ["model diversity", "perspective-only diversity", "wait for approval", "valid model IDs",
                "read-only", "own git worktree", "evidence quality, not by vote count"],
    "cross-critique": ["independent proposals first", "genuinely divergent", "same subagents", "*both* pros and cons",
                       "evidence quality, not vote count"],
    "implement-specs": ["reviewed and approved", "optional aids", "same PR", "keep specs and code synchronized"],
    "merge-risk": ["Impact = 2x", "Verification = 2x", "Rollback cost = 1.5x", "high: ≥ 2.25",
                   "Keep the numerical score and its calculations internal"],
    "research": ["Always spawn research subagents as **local**", "Pick the model for the search task",
                 "Anything where you need the raw material", "distilled answer plus its supporting evidence"],
    "saga": ["Confirm the exact path with the user", "Do not begin Phase 2 until the user approves",
             "Delegate, don't implement", "durable handoff before cleanup", "Never commit or open PRs unless the user asks",
             "Only consider the saga complete when the user confirms acceptance"],
    "scan-new-specs": ["Do not invoke this skill and do not schedule it", "is paused and stays paused",
                       "warpdotdev/docs", "missing_docs"],
    "spec-driven-implementation": ["create one before writing specs", "Do not create engineer-named",
                                   "After the specs are approved", "tech spec may be unnecessary"],
    "update-skill": ["references/best-practices.md", "Must be non-empty", "When to Split Content"],
    "validate-changes-match-specs": ["no relevant spec, stop", "untrusted data", "Resolve one-by-one",
                                   "Collect all decisions", "If two mismatch decisions conflict, stop",
                                   "Do not post GitHub comments without explicit approval", "Commit and push prompt"],
    "write-feature-docs": ["two separate confirmations, in that order", "Do not include anything marked confidential",
                           "Wait for the engineer's reply", "there is no unattended mode", "Gate 0",
                           "content-design-plan.md", "Maximum attempts per screenshot: 2"],
    "write-pr-description": ["template's own instructions outrank", "Never write intent as though it were a result",
                             "references/plain-language.md", "references/review-guide.md"],
    "write-product-spec": ["Only create a new Linear ticket or GitHub issue when the user explicitly asks",
                           "Do not include Validation, Success criteria, or Testing sections", "Figma: none provided"],
    "write-tech-spec": ["Only create a new Linear ticket or GitHub issue when the user explicitly asks",
                        "Research before writing", "commit-pinned references", "Parallelization"],
}


# Issue #97: these are independently reviewed call edges, not parsed prompt mentions.
WARP_REPOSITORY_DEPENDENCIES = {
    "brandalf": [], "complain": [], "create-pr": ["write-pr-description"],
    "diagnose-ci-failures": ["fix-errors"], "fix-errors": [], "migrate-to-factory": [],
    "pr-walkthrough": ["brandalf"], "readout": [], "reproduce-bug-report": [],
    "resolve-merge-conflicts": [], "respond-to-pr-comments-in-blocklist": [],
    "review-pr": [], "suggestion-box": [],
}
WARP_REPOSITORY_POLICIES = {
    "brandalf": ["https://warp-brand-site.vercel.app/brand/skill", "ask the user whether to proceed"],
    "complain": ["under 1,200 characters", "Preserve anonymity", "Do not forward user-provided text",
                 "do not retry", "submit.py", "evals/evals.json"],
    "create-pr": ["Always merge master", "candidate has not changed", "Do not rerun tests or lint after formatting",
                  "--draft", "ask before skipping integration coverage", "Co-Authored-By", "warp-integration-test"],
    "diagnose-ci-failures": ["plan (not code changes)", "Generate a plan for user review", "GH_PAGER=cat"],
    "fix-errors": ["narrowest useful command", "only when the user, task, or approved spec explicitly requires",
                   "Run `./script/format` once", "Do not rerun tests or Clippy after formatting"],
    "migrate-to-factory": ["factory.yaml", "factory-files", "untrusted migration data", "read-only inputs",
                           "Do not add schedules", "inside the Factory root"],
    "pr-walkthrough": ["system-overview", "data-flow", "code-dependency", "user-action", "d3@7.9.0",
                       "--require-browser", "rendering as unverified", "unless the user explicitly accepts"],
    "readout": ["Snapshot mode", "Research mode", "depth and audience", "ACCESS-doc-guide.md",
                "chrome blocks must be copied verbatim", "suffix -2, -3", "update_index.py", "distilled dump"],
    "reproduce-bug-report": ["Oz cloud", "remote.computer_use_enabled", "screen recording", "at most two",
                             "Do not silently substitute", "blocked", "Do not ask the public reporter for credentials"],
    "resolve-merge-conflicts": ["--repo", "one file at a time", "index stages", "Run targeted tests"],
    "respond-to-pr-comments-in-blocklist": ["Comment filtering", "Collect all decisions", "explanation loop",
                                           "Do not commit changes unless", "final preview is approved",
                                           "[Warp Agent]", "If commit or push fails, stop"],
    "review-pr": ["OZ_REPO_ROOT", "annotated diff", "only source of truth", "review-pr-local",
                  "security-review-pr", "check-impl-against-spec", "Pre-Verdict Audit", "validate_review_json.py",
                  "Do not post comments or reviews to GitHub directly"],
    "suggestion-box": ["under 1,200 characters", "More than three suggestions", "Include useful context safely",
                       "Do not include", "do not retry", "submit.py", "evals/evals.json"],
}


def warp_skill_doctor(probe, surfaces):
    warp_access(probe, surfaces, scenario="warp-skill-doctor", graph={"skill-doctor": []},
                policies={"skill-doctor": ["supported-harnesses.md", "Which conversations should I grade?",
                    "Which skills should I evaluate?", "--harness auto", "failed_conversations",
                    "insufficient_evidence", "--codex-home", "--claude-home", "python3 -B"]},
                routes=[], damaged_skill="skill-doctor", damaged_path="assets/pierre-diffs.js")


def warp_repository(probe, surfaces):
    warp_access(probe, surfaces, scenario="warp-repository", graph=WARP_REPOSITORY_DEPENDENCIES,
                policies=WARP_REPOSITORY_POLICIES,
                routes=[("create-pr", "write-pr-description"), ("pr-walkthrough", "brandalf"),
                        ("diagnose-ci-failures", "fix-errors")],
                damaged_skill="review-pr", damaged_path="scripts/resolve_spec_context.py")


def warp_specification(probe, surfaces):
    warp_access(probe, surfaces, scenario="warp-specification", graph=WARP_SPECIFICATION_DEPENDENCIES,
                policies=WARP_SPECIFICATION_POLICIES,
                routes=[("spec-driven-implementation", "write-product-spec"),
                        ("spec-driven-implementation", "write-tech-spec"),
                        ("spec-driven-implementation", "implement-specs"),
                        ("write-product-spec", "write-tech-spec"), ("cross-critique", "council")],
                damaged_skill="saga", damaged_path="references/validation-strategies.md")


def warp_access(probe, surfaces, *, scenario, graph, policies, routes, damaged_skill, damaged_path):
    """Retrieve one reviewed Warp slice without running its skill procedures."""
    from urllib.parse import unquote

    manifest = json.loads((ROOT / "packs/warp/pack.json").read_text())
    resources = {item["id"]: item for item in manifest["resources"]}
    baseline_root = Path(probe.evidence["warp_baseline_project"])
    baseline = json.loads((baseline_root / "packs/warp/pack.json").read_text())
    previous = {item["id"]: item for item in baseline["resources"]}
    authored = tree(ROOT / "packs/warp")
    require(set(resources) == set(previous) | {"catalog-adaptations"} and manifest["origins"] == baseline["origins"]
            and manifest["surfaces"] == baseline["surfaces"],
            "Warp provenance or native host support changed")
    require(all(resource == previous[name] for name, resource in resources.items() if name not in graph
                and name not in ("mit", "catalog-adaptations")),
            "Warp adaptation changed unrelated resources")
    require({**resources["mit"], "notices": previous["mit"]["notices"]} == previous["mit"]
            and resources["mit"]["notices"] == ["notice:catalog-adaptations"]
            and resources["catalog-adaptations"]["notices"] == [], "Warp legal closure must be complete and acyclic")
    require(all(not previous[name].get("on_demand") and not previous[name].get("variants") for name in graph),
            "Warp baseline must precede the reviewed slice")

    def closure(skill):
        result = {skill}
        dependencies = {**WARP_SPECIFICATION_DEPENDENCIES, **graph}[skill]
        for dependency in dependencies:
            result.update(closure(dependency))
        return result

    for host in ("codex", "claude"):
        probe.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-" + host)
        native_skill = "skill-doctor" if scenario == "warp-skill-doctor" else "write-product-spec"
        probe.apply(workspace, ["activate", "warp", "--surface", host, "--resource", "skill:" + native_skill])
        native = workspace / "home" / SKILL_DIRECTORIES[host] / native_skill
        if native.is_symlink():
            original = native.resolve()
            native.unlink()
            shutil.copytree(original, native)
        (native / "SKILL.md").write_text("# Preserve this locally modified native copy.\n")
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True)
        protected, snapshots = installation_state(workspace), tree(workspace / "snapshots")
        runtime_path = probe.root / (scenario + "-no-runtimes-" + host)
        runtime_path.mkdir()
        (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
        access = Probe(probe.executable, probe.snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)},
                       probe.evidence, probe.timeout)
        access.set_context("content-acceptance", scenario=scenario, surface=host, scope="project")
        discovery = access.candidate(workspace, ["show", "warp", "--surface", host, "--json"])
        entries = {item["qualified_skill"]: item for item in discovery["skills"]}
        require(discovery["schema_version"] == 1 and discovery["report"] == "skill-discovery"
                and not discovery["prerequisites_verified"], "Warp discovery claims runtime readiness")
        roots = {}
        for skill, dependencies in graph.items():
            report = access.candidate(workspace, ["get", "skill", "warp:" + skill, "--surface", host, "--json"])
            require(report["qualified_skill"] == "warp:" + skill, "wrong Warp root identity")
            effective = {**resources[skill], **next(v for v in resources[skill]["variants"] if v["surface"] == host)}
            declaration = effective["on_demand"]
            require(declaration["dependencies"] == [{"type": "skill", "target": "warp:" + name} for name in dependencies],
                    "Warp required/optional classification changed: " + skill)
            item = entries["warp:" + skill]
            require(item["compatible"] and item["prerequisites"] == declaration["prerequisites"]
                    and declaration["prerequisites"] and all(item["on_demand"].get(k, []) == v for k, v in declaration.items()),
                    "Warp discovery lost reviewed declarations")
            descriptors = skill_descriptors(report, host, manifest["version"], closure(skill), pack="warp")
            assert_skill_content(descriptors, manifest, pack="warp")
            entry = Path(report["entry_document"]).read_text()
            require(all(fragment.lower() in entry.lower() for fragment in policies[skill]),
                    "Warp substantive policy lost: " + skill)
            require("initiating" in entry and "snapshot_id" in entry and "scratch/output" in entry
                    and "unverified" in entry and "delegate" in entry, "Warp access context lost: " + skill)
            if skill == "write-feature-docs":
                require(entry.index("## Step 3:") < entry.index("## Step 4:") < entry.index("## Step 5:"),
                        "feature documentation reordered its two human checkpoints")
            if skill == "saga":
                for reference in ("continuing-a-saga", "saga-spec-template", "validation-strategies"):
                    relative = "references/ACCESS-" + reference + ".md"
                    require(relative in entry and (Path(report["resource_root"]) / relative).is_file(),
                            "saga lost an adapted supporting route")
                resume = (Path(report["resource_root"]) / "references/ACCESS-continuing-a-saga.md").read_text()
                require("../ACCESS.md" in resume and "worker_run_id" in resume and "Reconcile" in resume,
                        "saga resume lost context or durable reconciliation")
            for identity, descriptor in descriptors.items():
                resource = resources[identity.split(":")[1]]
                expected = next(v for v in resource["variants"] if v["surface"] == host)
                require(descriptor["prerequisites"] == expected["on_demand"]["prerequisites"], "Warp prerequisites lost")
            roots[skill] = report
            probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "skill": skill, "result": "passed",
                                               "snapshot_id": report["snapshot_id"],
                                               "checks": ["full-tree-bytes-modes-notices", "qualified-required-closure",
                                                          "substantive-policy", "unverified-prerequisites", "absent-content-runtimes"]})
        require(protected == installation_state(workspace) and snapshots == tree(workspace / "snapshots"),
                "Warp retrieval executed content or changed target/native/snapshot state")
        if scenario in ("warp-repository", "warp-skill-doctor") and probe.evidence.get("warp_helpers"):
            prepared_before = tree(workspace / "home/.local/share/packy/skill-access")
            resource_file = probe.root / ("warp-helper-resources-" + host + ".json")
            resource_file.write_text(json.dumps({name: report["resource_root"] for name, report in roots.items()}))
            fixture = "warp-skill-doctor.py" if scenario == "warp-skill-doctor" else "warp-repository.py"
            helper_output, _ = probe.execute([sys.executable, "-B", str(ROOT / "scripts/probes/fixtures" / fixture),
                                              "--resources", str(resource_file), "--workspace",
                                              str(probe.root / ("warp-helper-workspace-" + host))], timeout=60)
            helper_result = json.loads(helper_output)
            require(helper_result["result"] == "passed", "Warp helper acceptance failed")
            require(prepared_before == tree(workspace / "home/.local/share/packy/skill-access")
                    and snapshots == tree(workspace / "snapshots") and protected == installation_state(workspace),
                    "Warp helpers changed immutable resources or target/native state")
            probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "helpers": helper_result})
        prepared_root = workspace / "home/.local/share/packy/skill-access"
        prepared = tree(prepared_root)
        old = Probe(probe.executable, probe.root / "warp-baseline-dist", probe.root, access.env, probe.evidence, probe.timeout)
        old.set_context("snapshot-transition", scenario=scenario, surface=host, scope="project")
        transition = old.candidate(workspace, ["transition", "--expect-archive-sha256", probe.evidence["archive_sha256"], "--json"])
        require(transition["result"] == "transitioned"
                and transition["archive_sha256"] == probe.evidence["warp_baseline"]["archive_sha256"], "Warp transition failed")
        for wrapper, dependency in routes:
            root = roots[wrapper]
            expected = next(d for d in root["dependencies"] if d["qualified_skill"] == "warp:" + dependency)
            document = Path(root["entry_document"])
            links = re.findall(r"\[warp:" + dependency + r"\]\(([^)]+)\)", document.read_text())
            require(links and all((document.parent / unquote(path)).resolve() == Path(expected["entry_document"]) for path in links),
                    "Warp rendered route leaves its qualified closure")
            nested = old.candidate(workspace, ["get", "skill", "warp:" + dependency, "--surface", host,
                                               "--snapshot", root["snapshot_id"], "--json"])
            require(nested["snapshot_id"] == root["snapshot_id"] and nested["surface"] == host
                    and nested["qualified_skill"] == "warp:" + dependency
                    and Path(nested["entry_document"]).read_bytes() == Path(expected["entry_document"]).read_bytes(),
                    "Warp nested/delegated route followed new selection")
        if scenario == "warp-skill-doctor":
            root = roots["skill-doctor"]
            retained_report = old.candidate(workspace, ["get", "skill", "warp:skill-doctor", "--surface", host,
                                                       "--snapshot", root["snapshot_id"], "--json"])
            require(retained_report == root, "skill-doctor re-entry changed initiating identity or paths")
        observed, retained = tree(prepared_root), tree(workspace / "snapshots")
        require(all(observed.get(path) == value for path, value in prepared.items())
                and all(retained.get(path) == value for path, value in snapshots.items()),
                "Warp transition invalidated prior resource paths")
        independent = old.candidate(workspace, ["show", "warp", "--surface", host, "--json"])
        selected = old.candidate(workspace, ["get", "skill", "matty:grilling", "--surface", host, "--json"])
        require(selected["snapshot_id"] == transition["snapshot_id"]
                and all(not item["compatible"] for item in independent["skills"] if item["qualified_skill"].split(":")[1] in graph),
                "Warp independent discovery ignored baseline selection")
        output, _ = old.candidate(workspace, ["get", "skill", "warp:" + damaged_skill, "--surface", host, "--json"], failure=True)
        require(json.loads(output)["error"]["code"] == "incompatible_resource", "Warp independent request ignored new selection")
        require(protected == installation_state(workspace), "Warp transition changed target/native state")
        missing = (workspace / "snapshots" / roots[damaged_skill]["snapshot_id"]
                   / "packs/warp/skills" / damaged_skill / damaged_path)
        missing.unlink()
        damaged = installation_state(workspace)
        output, diagnostic = old.candidate(workspace, ["get", "skill", "warp:" + damaged_skill, "--surface", host,
                                                      "--snapshot", roots[damaged_skill]["snapshot_id"], "--json"], failure=True)
        require("snapshot_unavailable" in output or diagnostic.strip() == "Catalog Snapshot extracted files do not exactly match the index",
                "Warp missing retained content silently fell back")
        require(damaged == installation_state(workspace), "failed Warp retrieval changed target/native state")
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["retained-nested-specification-context", "prior-paths-usable", "new-selection",
                                                      "missing-retained-content-fails", "inert-retrieval"]})
    for host in SURFACES:
        probe.set_context("native-regression", scenario=scenario, surface=host, scope="project")
        workspace = probe.prepare(scenario + "-native-" + host)
        probe.apply(workspace, ["install", "emil", "--surface", host, "--resource", "skill:write-swift"])
        unrelated = tree(workspace / "project" / SKILL_DIRECTORIES[host] / "write-swift")
        personal = {name: tree(workspace / name) for name in ("home", "config")}
        guidance = {name: (workspace / "project" / name).read_bytes() for name in ("AGENTS.md", "CLAUDE.md", "unrelated.txt")}
        args = ["install", "warp", "--surface", host]
        for skill in graph:
            args.extend(["--resource", "skill:" + skill])
        probe.apply(workspace, args)
        installed = workspace / "project" / SKILL_DIRECTORIES[host]
        require({p.name for p in installed.iterdir()} == set(graph) | {"write-swift"}, "Warp native selection changed")
        require(unrelated == tree(installed / "write-swift")
                and personal == {name: tree(workspace / name) for name in personal}
                and all((workspace / "project" / name).read_bytes() == data for name, data in guidance.items()),
                "Warp native installation changed unrelated/personal state")
        for skill in graph:
            before, after = previous[skill], resources[skill]
            require({k: v for k, v in after.items() if k not in ("origin", "variants")}
                    == {k: v for k, v in before.items() if k not in ("origin", "variants")}, "Warp native contract changed")
            original, actual = tree(baseline_root / "packs/warp" / before["source"]), tree(installed / skill)
            require(all(actual.get(path) == value for path, value in original.items()), "Warp original native bytes/modes changed")
        if host == "opencode":
            require(all(not resources[skill].get("on_demand")
                        and {v["surface"] for v in resources[skill]["variants"]} == {"codex", "claude"}
                        for skill in graph), "Warp added OpenCode on-demand declarations")
            before = installation_state(workspace)
            output, diagnostic = probe.candidate(workspace, ["show", "warp", "--surface", host, "--json"], failure=True)
            require('unsupported on-demand discovery surface "opencode"' in output + diagnostic,
                    "OpenCode discovery failed for an unrelated reason")
            require(before == installation_state(workspace), "unsupported discovery changed OpenCode native state")
        probe.verify(workspace)
        probe.evidence["outcomes"].append({"scenario": scenario, "surface": host, "result": "passed",
                                           "checks": ["native-installation", "original-contracts-bytes-modes", "opencode-contract-preserved"]})
    require(authored == tree(ROOT / "packs/warp"), "acceptance changed Warp sources")


def offline_executable(probe):
    """Apply an OS network boundary to the real binary after acquisition."""
    import shlex

    wrapper = probe.root / "offline-packy"
    if wrapper.exists():
        return wrapper
    if sys.platform == "darwin":
        launcher = ["/usr/bin/sandbox-exec", "-p", "(version 1)(allow default)(deny network*)"]
    else:
        unshare = shutil.which("unshare", path=probe.env["PATH"])
        require(sys.platform.startswith("linux") and unshare, "offline acceptance requires sandbox-exec or Linux unshare")
        launcher = [unshare, "--user", "--map-root-user", "--net", "--"]
    # EPERM/EACCES is the required canary result, not mere connection refusal.
    canary = ("import errno,socket; s=socket.socket(); "
              "status=s.connect_ex(('127.0.0.1',9)); "
              "assert status in (errno.EPERM,errno.EACCES,errno.ENETUNREACH),status; print('network-denied')")
    output, _ = probe.execute([*launcher, sys.executable, "-B", "-c", canary])
    require(output.strip() == "network-denied", "offline network boundary not demonstrated")
    wrapper.write_text("#!/bin/sh\nexec " + " ".join(shlex.quote(str(v)) for v in [*launcher, probe.executable]) + ' "$@"\n')
    wrapper.chmod(0o755)
    probe.evidence["offline_boundary"] = launcher
    return wrapper


def reviewed_scope():
    """Frozen review expectations must not follow whatever a candidate contains."""
    inventory = json.loads((ROOT / "docs/on-demand-coverage.json").read_text())
    rows = inventory["skills"]
    by_identity = {row["qualified_skill"]: row for row in rows}
    require(inventory["schema_version"] == 1 and inventory["hosts"] == ["codex", "claude"]
            and len(rows) == len(by_identity) == 117, "duplicate/unassigned integrated scope entry")
    require(inventory["counts"] == {"matty": 33, "pstack": 55, "warp": 29}, "integrated scope counts changed")
    for pack, count in inventory["counts"].items():
        expected = {name.split(":")[1] for name in by_identity if name.startswith(pack + ":")}
        manifest = json.loads((ROOT / "packs" / pack / "pack.json").read_text())
        require(len(expected) == count and expected == {r["id"] for r in manifest["resources"] if r["kind"] == "skill"},
                "integrated scope missing/extra skill in " + pack)
        require(set(manifest["surfaces"]) == ({"codex", "claude"} if pack == "pstack" else set(SURFACES)),
                "native host support changed")
        for notice in inventory["legal"][pack]:
            path = ROOT / "packs" / pack / notice["source"]
            require(path.stat().st_mode & 0o777 == notice["mode"]
                    and hashlib.sha256(path.read_bytes()).hexdigest() == notice["sha256"], "reviewed legal closure changed")
    for identity, row in by_identity.items():
        require(set(row["hosts"]) == {"codex", "claude"} and (ROOT / row["review"]).is_file()
                and row["preserved_workflow_and_support"] and row["reference_classification"], "unassigned host/review: " + identity)
        pack, skill = identity.split(":")
        manifest = json.loads((ROOT / "packs" / pack / "pack.json").read_text())
        resource = next(r for r in manifest["resources"] if r["id"] == skill)
        for host, expected in row["hosts"].items():
            effective = {**resource, **next((v for v in resource.get("variants", []) if v["surface"] == host), {})}
            require(effective["source"] == expected["source"] and effective["on_demand"] == expected["on_demand"]
                    and effective["requires"] == expected["native_requires"], "reviewed effective contract changed: " + identity)
            entries = [[str(p.relative_to(ROOT / "packs" / pack / effective["source"])), p.lstat().st_mode & 0o777,
                        hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None]
                       for p in sorted((ROOT / "packs" / pack / effective["source"]).rglob("*"))]
            require(hashlib.sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest() == expected["source_tree_sha256"],
                    "reviewed full resource bytes/modes changed: " + identity + " " + host)
    return inventory, by_identity


def integrated_on_demand(probe, surfaces):
    """One current-content contract; historical transition probes keep their own baselines."""
    inventory, scope = reviewed_scope()
    probe.evidence["coverage_inventory"] = {"path": "docs/on-demand-coverage.json",
        "sha256": hashlib.sha256((ROOT / "docs/on-demand-coverage.json").read_bytes()).hexdigest(),
        "reviewed_catalog_commit": inventory["reviewed_catalog_commit"], "logical_skills": 117, "host_cases": 234,
        "limits": inventory["evidence_limits"]}
    # Reuse sequential setup/retirement; the complete fixture runs separately below.
    packy_bootstrap(probe, surfaces, fixtures=False)
    executable = offline_executable(probe)
    authored = {pack: tree(ROOT / "packs" / pack) for pack in inventory["counts"]}
    manifests = {pack: json.loads((ROOT / "packs" / pack / "pack.json").read_text()) for pack in authored}

    def closure(identity, host):
        expected = scope[identity]["hosts"][host]
        pack = identity.split(":")[0]
        result = {identity}
        dependencies = scope[identity]["direct_access_dependencies"] + [pack + ":" + name.split(":", 1)[1]
                                    for name in expected["native_requires"] if name.startswith("skill:")]
        for dependency in dependencies:
            result.update(closure(dependency, host))
        return result

    for host in ("codex", "claude"):
        probe.set_context("content-acceptance", scenario="integrated-on-demand", surface=host)
        workspace = probe.prepare("integrated-" + host)
        probe.apply(workspace, ["install", "matty", "--surface", host, "--resource", "skill:tdd"])
        native = workspace / "project" / SKILL_DIRECTORIES[host] / "tdd/SKILL.md"
        native.write_text("# Keep modified native TDD. Never substitute this for Catalog resources.\n")
        (workspace / "home/.local/share/packy/skill-access").mkdir(parents=True, exist_ok=True)
        protected, snapshots = installation_state(workspace), tree(workspace / "snapshots")
        runtime_path = probe.root / ("integrated-no-runtimes-" + host)
        runtime_path.mkdir()
        (runtime_path / "git").symlink_to(shutil.which("git", path=probe.env["PATH"]))
        access = Probe(executable, probe.snapshot, probe.root, {**probe.env, "PATH": str(runtime_path)}, probe.evidence, probe.timeout)
        access.set_context("offline-resource-access", scenario="integrated-on-demand", surface=host)
        listing = access.candidate(workspace, ["list", "--json"])
        require({p["id"] for p in listing["packs"]} == set(probe.evidence["pack_ids"]), "offline discovery lost Packs")
        roots, discovery = {}, {}
        for pack in inventory["counts"]:
            report = access.candidate(workspace, ["show", pack, "--surface", host, "--json"])
            items = {item["qualified_skill"]: item for item in report["skills"]}
            require(report["schema_version"] == 1 and report["report"] == "skill-discovery"
                    and not report["prerequisites_verified"] and len(items) == len(report["skills"])
                    and set(items) == {name for name in scope if name.startswith(pack + ":")}, "wrong effective discovery coverage")
            discovery.update(items)
        # Deterministic metadata establishes ambiguity; the bootstrap must ask the user.
        matches = {name for name in discovery if name.split(":")[1] == "tdd"}
        require(matches == {"matty:tdd", "pstack:tdd"}, "duplicate-name discovery lost qualified choices")
        output, _ = access.candidate(workspace, ["get", "skill", "tdd", "--surface", host, "--json"], failure=True)
        require(json.loads(output)["error"]["code"] == "invalid_identity", "unqualified identity silently selected a Pack")
        for identity, row in scope.items():
            pack, skill = identity.split(":")
            expected = row["hosts"][host]
            item = discovery[identity]
            require(item["compatible"] and item["prerequisites"] == expected["on_demand"]["prerequisites"]
                    and all(item["on_demand"].get(k, []) == v for k, v in expected["on_demand"].items()),
                    "discovery lost independently reviewed declarations")
            report = access.candidate(workspace, ["get", "skill", identity, "--surface", host, "--json"])
            require(report["qualified_skill"] == identity, "integrated root identity changed")
            descriptors = skill_descriptors(report, host, manifests[pack]["version"],
                                             [name.split(":")[1] for name in closure(identity, host)], pack=pack)
            assert_skill_content(descriptors, manifests[pack], pack=pack)
            for name, descriptor in descriptors.items():
                require(descriptor["prerequisites"] == scope[name]["hosts"][host]["on_demand"]["prerequisites"],
                        "retrieval lost known prerequisites")
            roots[identity] = report
            probe.evidence["outcomes"].append({"scenario": "integrated-on-demand", "surface": host, "qualified_skill": identity,
                "snapshot_id": report["snapshot_id"], "result": "passed", "checks": ["reviewed-independent-scope",
                "versioned-identity-host-snapshot", "effective-full-bytes-modes-references-assets", "dependency-and-legal-closure",
                "offline", "absent-content-runtimes"]})
        require(len({r["snapshot_id"] for r in roots.values()}) == 1, "integrated retrieval mixed snapshots")
        require("Refactoring is not part of the loop" in Path(roots["matty:tdd"]["entry_document"]).read_text()
                and "# TDD Bug Fix" in Path(roots["pstack:tdd"]["entry_document"]).read_text(), "qualified TDD policies were merged")
        matty_pstack_tdd(probe, access, host, manifests["matty"])
        # Candidate routing must continue to expose the public non-Git retrieval behavior.
        git_directory = workspace / "project/.git"
        git_directory.rename(workspace / "held-git")
        try:
            non_git = access.candidate(workspace, ["get", "skill", "matty:grill-with-docs", "--surface", host, "--json"])
            require(non_git["snapshot_id"] == roots["matty:grill-with-docs"]["snapshot_id"], "non-Git access changed snapshot")
        finally:
            (workspace / "held-git").rename(git_directory)
        require(protected == installation_state(workspace) and snapshots == tree(workspace / "snapshots"),
                "retrieval changed target/native/activation/immutable state")
        prepared = tree(workspace / "home/.local/share/packy/skill-access")
        if probe.evidence["integrated_helpers"]:
            orchestration_helpers(probe, roots["pstack:poteto-mode"], host)
            decision_log_helper(probe, roots["pstack:show-me-your-work"], host)
            for family, names in (("warp-repository", ["review-pr", "readout"]), ("warp-skill-doctor", ["skill-doctor"])):
                resources = probe.root / (family + "-integrated-" + host + ".json")
                resources.write_text(json.dumps({name: roots["warp:" + name]["resource_root"] for name in names}))
                output, _ = probe.execute([sys.executable, "-B", str(ROOT / "scripts/probes/fixtures" / (family + ".py")),
                    "--resources", str(resources), "--workspace", str(probe.root / (family + "-integrated-workspace-" + host))], timeout=90)
                result = json.loads(output)
                require(result["result"] == "passed", "integrated real-content helper failed")
                probe.evidence["outcomes"].append({"scenario": "integrated-on-demand", "surface": host, "helpers": result})
        require(prepared == tree(workspace / "home/.local/share/packy/skill-access")
                and protected == installation_state(workspace) and snapshots == tree(workspace / "snapshots"),
                "helpers changed resources or target/native state")
        probe.evidence["outcomes"].append({"scenario": "integrated-on-demand", "surface": host, "result": "passed",
            "checks": ["ambiguous-metadata-user-choice-required", "qualified-distinct-TDD", "Matty-nested-wrapper",
                       "non-Git", "managed-modified-copy-preserved", "target-installation-snapshot-prepared-preservation"],
            "model_matching": "not exercised", "native_host_loading": "not exercised"})
    # No candidate initialization: the public CLI must explain explicit acquisition.
    absent = probe.root / "absent-catalog"
    absent.mkdir()
    env = isolated_environment(absent)
    missing = Probe(executable, probe.snapshot, absent, env, probe.evidence, probe.timeout)
    missing.set_context("absent-catalog", scenario="integrated-on-demand")
    before = tree(absent)
    output, diagnostic = missing.execute([str(executable), "get", "skill", "matty:tdd", "--surface", "codex", "--json"], failure=True)
    require(json.loads(output)["error"]["code"] == "catalog_unavailable"
            and ("packy init" in output + diagnostic or "catalog refresh" in output + diagnostic),
            "missing catalog lacks explicit acquisition error/guidance")
    require(tree(absent) == before, "absent-catalog retrieval mutated target or user state")
    reviewed_retrieval(probe, integrated=True)
    require(authored == {pack: tree(ROOT / "packs" / pack) for pack in authored}, "integrated acceptance changed authored Packs")
    probe.evidence["outcomes"].append({"scenario": "integrated-on-demand", "result": "passed",
        "checks": ["117-unique-logical-identities", "234-host-root-cases", "explicit-acquisition-error", "no-authored-content-mutation"],
        "helpers": "passed" if probe.evidence["integrated_helpers"] else "not selected; full acceptance requires --integrated-helpers"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", choices=("adoption", "ponytail", "claude", "pstack", "packy-bootstrap", "matty-design", "matty-delivery", "pstack-foundational", "pstack-withdrawal", "pstack-engineering", "pstack-orchestration", "warp-specification", "warp-repository", "warp-skill-doctor", "integrated-on-demand"), required=True)
    parser.add_argument("--integrated-helpers", action="store_true", help="opt-in reviewed pstack/Warp helpers with integrated acceptance")
    parser.add_argument("--warp-helpers", action="store_true", help="opt-in reviewed offline helpers for the selected Warp slice")
    parser.add_argument("--warp-baseline", type=Path, help="clean complete Catalog baseline before Warp on-demand adaptation")
    parser.add_argument("--pstack-baseline", type=Path, help="clean committed complete Catalog baseline for pstack transitions")
    parser.add_argument("--matty-baseline", type=Path, help="clean complete Catalog baseline before Matty on-demand adaptation")
    parser.add_argument("--surface", action="append", choices=SURFACES)
    parser.add_argument("--html-pack", action="store_true", help="optionally execute the installed Claude HTML packer with Node")
    parser.add_argument("--timeout", type=float, default=30, help="lifecycle deadline in seconds (default: 30)")
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    scenarios = list(dict.fromkeys(args.scenario))
    if args.integrated_helpers and "integrated-on-demand" not in scenarios:
        parser.error("--integrated-helpers requires --scenario integrated-on-demand")
    if bool({"warp-specification", "warp-repository", "warp-skill-doctor"}.intersection(scenarios)) != (args.warp_baseline is not None):
        parser.error("Warp scenarios require --warp-baseline, used only with those scenarios")
    if len({"warp-specification", "warp-repository", "warp-skill-doctor"}.intersection(scenarios)) > 1:
        parser.error("select one Warp slice per run: their reviewed baselines differ")
    if args.warp_helpers and not {"warp-repository", "warp-skill-doctor"}.intersection(scenarios):
        parser.error("--warp-helpers requires --scenario warp-repository or warp-skill-doctor")
    if args.html_pack and "claude" not in scenarios:
        parser.error("--html-pack requires --scenario claude")
    integrated = "integrated-on-demand" in scenarios
    if integrated and len(scenarios) != 1:
        parser.error("integrated-on-demand runs independently; historical scenarios retain their own baselines")
    surfaces = list(dict.fromkeys(args.surface or (("codex", "claude") if integrated else SURFACES)))
    if integrated and set(surfaces) != {"codex", "claude"}:
        parser.error("integrated-on-demand exercises exactly Codex and Claude; OpenCode access is outside scope")
    if {"pstack", "pstack-withdrawal", "packy-bootstrap", "matty-design", "matty-delivery", "pstack-foundational", "pstack-engineering", "pstack-orchestration", "warp-specification", "warp-repository", "warp-skill-doctor", "integrated-on-demand"}.intersection(scenarios) and not {"codex", "claude"}.issubset(surfaces):
        parser.error("on-demand scenarios require Codex and Claude surfaces")
    if bool({"pstack", "pstack-foundational", "pstack-withdrawal", "pstack-engineering", "pstack-orchestration"}.intersection(scenarios)) != (args.pstack_baseline is not None):
        parser.error("pstack scenarios require --pstack-baseline, used only with those scenarios")
    if bool({"matty-design", "matty-delivery"}.intersection(scenarios)) != (args.matty_baseline is not None):
        parser.error("Matty scenarios require --matty-baseline, used only with those scenarios")
    evidence = {"schema_version": 1, "report": "catalog-content-probes", "provenance": "local-candidate",
                "official_publication": False, "scenarios": scenarios, "surfaces": surfaces, "html_pack": args.html_pack,
                "warp_helpers": args.warp_helpers, "integrated_helpers": args.integrated_helpers, "commands": [], "outcomes": [], "result": "failed"}
    root = None
    previous_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        with tempfile.TemporaryDirectory(prefix="catalog-content-probes-") as directory:
            root = Path(directory).resolve()
            env = isolated_environment(root)
            probe = Probe(root / "packy", root / "dist", root, env, evidence, args.timeout)
            for name in ("git", "curl", "uname", *(("node",) if args.html_pack else ())):
                require(shutil.which(name, path=env["PATH"]) is not None, "missing prerequisite: " + name)
            commit = checkout_commit(probe, ROOT)
            if args.warp_baseline is not None:
                args.warp_baseline = args.warp_baseline.resolve(strict=True)
                probe.set_context("baseline-verification")
                warp_baseline_commit = checkout_commit(probe, args.warp_baseline)
                evidence["warp_baseline_project"] = str(args.warp_baseline)
            if args.pstack_baseline is not None:
                args.pstack_baseline = args.pstack_baseline.resolve(strict=True)
                probe.set_context("baseline-verification")
                baseline_commit = checkout_commit(probe, args.pstack_baseline)
                evidence["pstack_baseline_project"] = str(args.pstack_baseline)
            if args.matty_baseline is not None:
                args.matty_baseline = args.matty_baseline.resolve(strict=True)
                probe.set_context("baseline-verification")
                matty_baseline_commit = checkout_commit(probe, args.matty_baseline)
                evidence["matty_baseline_project"] = str(args.matty_baseline)
            probe.set_context("acquisition")
            probe.execute([sys.executable, "-B", str(ROOT / "scripts/packy_tool.py"), "--pin",
                           str(ROOT / "packy-release.json"), "--executable-output", str(probe.executable)], timeout=180)
            version, _ = probe.execute([str(probe.executable), "version", "--json"])
            evidence["verified_packy_identity"] = json.loads(version)
            probe.set_context("candidate-construction")
            evidence.update(build_catalog(probe, ROOT, commit, probe.snapshot))
            if args.warp_baseline is not None:
                probe.set_context("baseline-construction")
                evidence["warp_baseline"] = build_catalog(probe, args.warp_baseline, warp_baseline_commit,
                                                         root / "warp-baseline-dist")
            if args.pstack_baseline is not None:
                probe.set_context("baseline-construction")
                evidence["pstack_baseline"] = build_catalog(probe, args.pstack_baseline, baseline_commit, root / "baseline-dist")
            if args.matty_baseline is not None:
                probe.set_context("baseline-construction")
                evidence["matty_baseline"] = build_catalog(probe, args.matty_baseline, matty_baseline_commit,
                                                          root / "matty-baseline-dist")
            ambient = {key: tree(Path(env[key])) for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME")}
            for scenario in scenarios:
                probe.set_context("content-acceptance", scenario=scenario, scope="project")
                print("Running reviewed content scenario: " + scenario, file=sys.stderr, flush=True)
                {"adoption": adoption, "ponytail": ponytail, "claude": claude, "pstack": pstack, "packy-bootstrap": packy_bootstrap, "matty-design": matty_design, "matty-delivery": matty_delivery, "pstack-foundational": pstack_foundational, "pstack-withdrawal": pstack_withdrawal, "pstack-engineering": pstack_engineering, "pstack-orchestration": pstack_orchestration, "warp-specification": warp_specification, "warp-repository": warp_repository, "warp-skill-doctor": warp_skill_doctor, "integrated-on-demand": integrated_on_demand}[scenario](probe, surfaces)
            require(ambient == {key: tree(Path(env[key])) for key in ambient}, "candidate changed ambient user state")
            probe.set_context("candidate-verification")
            require(checkout_commit(probe, ROOT) == commit, "Catalog candidate changed during probes")
            if args.warp_baseline is not None:
                probe.set_context("baseline-verification")
                require(checkout_commit(probe, args.warp_baseline) == warp_baseline_commit, "Warp baseline changed during probes")
            if args.pstack_baseline is not None:
                probe.set_context("baseline-verification")
                require(checkout_commit(probe, args.pstack_baseline) == baseline_commit, "pstack baseline changed during probes")
            if args.matty_baseline is not None:
                probe.set_context("baseline-verification")
                require(checkout_commit(probe, args.matty_baseline) == matty_baseline_commit, "Matty baseline changed during probes")
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
