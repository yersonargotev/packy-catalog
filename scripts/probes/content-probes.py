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
            require(preview["plan_id"] and preview["disposition"] == "applicable", "global plan cannot apply")
            prompts = [f"Approve {phase['kind']} phase for exact plan {preview['plan_id']}? [y/N] "
                       for phase in preview["phases"] if phase["approval_required"]]
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
        targets = {surface: base / SKILL_DIRECTORIES[surface] for surface in SURFACES}
        if scope == "global":
            targets["opencode"] = workspace / "config/opencode/skills"
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
        before = tree(workspace)
        out, diagnostic = probe.candidate(workspace, [apply, "pstack", "--surface", "opencode", "--dry-run", "--json"], failure=True)
        require("deterministic coexistence is not verified" in out + diagnostic, "OpenCode coexistence failed for unrelated reason")
        require(tree(workspace) == before, "OpenCode coexistence rejection changed workspace")
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
        probe.apply(workspace, [apply, "pstack", "--surface", "opencode"])
        require("## OpenCode execution" in (targets["opencode"] / "reflect/SKILL.md").read_text(),
                "wrong pstack OpenCode definition")
        probe.apply(workspace, [remove, "pstack", "--surface", "opencode"])
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
                                                     "opencode-coexistence-rejection", "helper-drift-rejection",
                                                     "effective-dependencies", "complete-retirement", "unrelated-state-preservation"]})


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


def packy_bootstrap(probe, surfaces):
    """Exercise the official two-host bootstrap through the released lifecycle."""
    hosts = ("codex", "claude")
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
                require("Pack: packy 1.0.0" in (base / "PACKY-NOTICES.md").read_text()
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
    reviewed_retrieval(probe)


def reviewed_retrieval(probe):
    """Controlled authoring inputs exercise access without publishing fixture Packs."""
    probe.set_context("candidate-construction")
    project = probe.root / "retrieval-authoring"
    fixture_notice = (ROOT / "packs/packy/notices/MIT").read_text().replace("Yerson Argote", "Fixture Authors")
    for pack_id, host_variant in (("access-root", True), ("access-support", False)):
        pack = project / "packs" / pack_id
        (pack / "skills/guide/references").mkdir(parents=True)
        (pack / "notices").mkdir()
        (pack / "notices/MIT").write_text(fixture_notice)
        (pack / "skills/guide/references/context.md").write_text("# Controlled supporting reference\n")
        sentinel = pack / "skills/guide/sentinel.sh"
        sentinel.write_text("#!/bin/sh\nprintf executed > should-never-exist\n")
        sentinel.chmod(0o755)
        entry = "# Support fixture\n" if not host_variant else "# Codex fixture\n[Dependency]({{packy.access:access-support:guide}})\n"
        (pack / "skills/guide/SKILL.md").write_text(entry)
        resource = {"kind": "skill", "id": "guide", "source": "skills/guide", "description": "Controlled access fixture",
                    "requires": [], "conflicts": [], "notices": ["notice:mit"],
                    "on_demand": {"protocol": "skill-tree-v1", "prerequisites": ["packy-fixture-missing-runtime"]},
                    "bindings": [{"surface": host, "projection": "skill", "name": "guide", "invocation": "guide",
                                  "mode": "native", "sharing": "exclusive", "capabilities": []}
                                 for host in ("claude", "codex")], "surface_exclusions": []}
        if host_variant:
            resource["on_demand"].update(reference_files=["SKILL.md"], dependencies=[{"type": "skill", "target": "access-support:guide"}])
            (pack / "skills/claude-guide").mkdir()
            (pack / "skills/claude-guide/SKILL.md").write_text(entry.replace("Codex", "Claude"))
            shutil.copytree(pack / "skills/guide/references", pack / "skills/claude-guide/references")
            shutil.copy2(sentinel, pack / "skills/claude-guide/sentinel.sh")
            resource["variants"] = [{"surface": "claude", "source": "skills/claude-guide"}]
        notice = {"kind": "notice", "id": "mit", "source": "notices/MIT", "description": "Controlled legal fixture",
                  "license": "MIT", "attribution": "Copyright (c) 2026 Fixture Authors", "requires": [], "conflicts": [],
                  "bindings": [], "surface_exclusions": []}
        manifest = {"schema_version": 3, "id": pack_id, "version": "1.0.0", "description": "Controlled retrieval fixture",
                    "selectable": True, "surfaces": ["claude", "codex"], "readiness_obligations": ["runtime-usability"],
                    "external_requirements": [], "origins": [], "resources": [notice, resource]}
        (pack / "pack.json").write_text(json.dumps(manifest, indent=2) + "\n")
    probe.execute(["git", "init", "-q", str(project)])
    probe.execute(["git", "-C", str(project), "add", "."])
    probe.execute(["git", "-C", str(project), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                   "commit", "-qm", "Controlled retrieval inputs"])
    fixture_commit = checkout_commit(probe, project)
    fixture_snapshot = probe.root / "retrieval-dist"
    build_catalog(probe, project, fixture_commit, fixture_snapshot)
    runner = Probe(probe.executable, fixture_snapshot, probe.root, probe.env, probe.evidence, probe.timeout)
    authored = tree(project)
    for host in ("codex", "claude"):
        runner.set_context("content-acceptance", scenario="packy-bootstrap", surface=host, scope="project")
        workspace = runner.prepare("retrieval-" + host, pack_ids=["access-root", "access-support"])
        target = tree(workspace / "project")
        require(shutil.which("packy-fixture-missing-runtime", path=probe.env["PATH"]) is None, "fixture runtime unexpectedly exists")
        discovery = runner.candidate(workspace, ["show", "access-root", "--surface", host, "--json"])
        require(discovery["schema_version"] == 1 and discovery["report"] == "skill-discovery", "invalid discovery envelope")
        report = runner.candidate(workspace, ["get", "skill", "access-root:guide", "--surface", host, "--json"])
        require(report["schema_version"] == 1 and report["report"] == "skill-access" and report["result"] == "prepared", "invalid access envelope")
        require(len(report["dependencies"]) == 1, "cross-Pack dependency missing")
        for descriptor, identity in ((report, "access-root:guide"), (report["dependencies"][0], "access-support:guide")):
            require(descriptor["qualified_skill"] == identity and descriptor["pack_version"] == "1.0.0"
                    and descriptor["surface"] == host and descriptor["snapshot_id"] == report["snapshot_id"]
                    and isinstance(descriptor["snapshot_id"], str) and bool(descriptor["snapshot_id"]), "wrong access identity")
            require(descriptor["prerequisites"] == ["packy-fixture-missing-runtime"], "known prerequisite lost")
            entry, root = Path(descriptor["entry_document"]), Path(descriptor["resource_root"])
            require(entry.is_absolute() and root.is_absolute() and entry.is_file() and entry.parent == root,
                    "unusable entry/resource paths")
            require((root / "references/context.md").read_text() == "# Controlled supporting reference\n", "reference closure lost")
            require((root / "sentinel.sh").read_bytes() == b"#!/bin/sh\nprintf executed > should-never-exist\n"
                    and (root / "sentinel.sh").stat().st_mode & 0o777 == 0o755, "script bytes/mode lost")
            require(any(p.read_text() == fixture_notice
                        for p in root.parents[1].rglob("MIT")), "legal closure lost")
        entry = Path(report["entry_document"])
        text = entry.read_text()
        require(text.startswith("# " + ("Codex" if host == "codex" else "Claude") + " fixture\n"), "wrong effective entry")
        reference = re.search(r"\[Dependency\]\(([^)]+)\)", text)
        require(reference is not None and (entry.parent / reference[1]).resolve() == Path(report["dependencies"][0]["entry_document"]),
                "reviewed dependency reference is unusable")
        nested = runner.candidate(workspace, ["get", "skill", "access-support:guide", "--surface", host,
                                             "--snapshot", report["snapshot_id"], "--json"])
        require(nested["snapshot_id"] == report["snapshot_id"] and Path(nested["entry_document"]).read_bytes() == Path(report["dependencies"][0]["entry_document"]).read_bytes(),
                "nested retrieval changed snapshot or dependency content")
        require(tree(workspace / "project") == target, "retrieval changed target project")
        require(not list(workspace.rglob("should-never-exist")), "retrieval executed a script")
        require(tree(project) == authored, "retrieval changed authored resources")
        probe.evidence["outcomes"].append({"scenario": "packy-bootstrap", "surface": host, "result": "passed",
                                           "checks": ["reviewed-cross-pack-retrieval", "effective-host", "structured-contract",
                                                      "supporting-legal-closure", "executable-mode", "nested-snapshot",
                                                      "absent-runtime", "inert-scripts", "unchanged-target-and-sources"]})


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
        documents = root.glob("*.md") if pack == "matty" else [root / "ACCESS.md", *root.glob("references/**/*.md")]
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
        for variant in result["variants"]:
            variant.pop("on_demand", None)
        return result

    # Original native contracts/bytes/modes survive on all three supported hosts.
    previous = {item["id"]: item for item in baseline["resources"]}
    for host in SURFACES:
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", choices=("adoption", "ponytail", "claude", "pstack", "packy-bootstrap", "matty-design", "matty-delivery", "pstack-foundational"), required=True)
    parser.add_argument("--pstack-baseline", type=Path, help="clean committed complete Catalog baseline for pstack transitions")
    parser.add_argument("--matty-baseline", type=Path, help="clean complete Catalog baseline before Matty on-demand adaptation")
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
    if {"packy-bootstrap", "matty-design", "matty-delivery", "pstack-foundational"}.intersection(scenarios) and not {"codex", "claude"}.issubset(surfaces):
        parser.error("on-demand scenarios require Codex and Claude surfaces")
    if "pstack" in scenarios and set(surfaces) != set(SURFACES):
        parser.error("pstack requires --pstack-baseline and all three surfaces")
    if bool({"pstack", "pstack-foundational"}.intersection(scenarios)) != (args.pstack_baseline is not None):
        parser.error("pstack scenarios require --pstack-baseline, used only with those scenarios")
    if bool({"matty-design", "matty-delivery"}.intersection(scenarios)) != (args.matty_baseline is not None):
        parser.error("Matty scenarios require --matty-baseline, used only with those scenarios")
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
            commit = checkout_commit(probe, ROOT)
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
                {"adoption": adoption, "ponytail": ponytail, "claude": claude, "pstack": pstack, "packy-bootstrap": packy_bootstrap, "matty-design": matty_design, "matty-delivery": matty_delivery, "pstack-foundational": pstack_foundational}[scenario](probe, surfaces)
            require(ambient == {key: tree(Path(env[key])) for key in ambient}, "candidate changed ambient user state")
            probe.set_context("candidate-verification")
            require(checkout_commit(probe, ROOT) == commit, "Catalog candidate changed during probes")
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
