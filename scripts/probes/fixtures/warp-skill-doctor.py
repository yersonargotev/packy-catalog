"""Offline fictional skill-doctor CLI acceptance, explicitly opt-in after review."""
import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def observe(root):
    return {str(p.relative_to(root)): (p.lstat().st_mode, p.read_bytes() if p.is_file() else None)
            for p in root.rglob("*")}


# The helpers run with read-only access to prepared resources and fixture inputs.
# Python runtime reads are allowed; all generated state stays in owned output.
CHILD = r'''
import json, os, pathlib, runpy, sys
policy = json.loads(sys.argv[1])
read_roots = [pathlib.Path(p).resolve() for p in policy["read"]]
write_roots = [pathlib.Path(p).resolve() for p in policy["write"]]
def within(path, roots):
    p = pathlib.Path(os.fsdecode(path)).resolve()
    return any(p == root or root in p.parents for root in roots)
def mutation_path(path, dir_fd):
    if dir_fd in (None, -1):
        return path
    descriptor = os.fstat(dir_fd)
    for root in write_roots:
        for directory, _, _ in os.walk(root):
            info = os.stat(directory)
            if (info.st_dev, info.st_ino) == (descriptor.st_dev, descriptor.st_ino):
                return pathlib.Path(directory) / os.fsdecode(path)
    raise RuntimeError("unowned directory descriptor")
def audit(event, args):
    if event.startswith("socket.") or event == "webbrowser.open":
        raise RuntimeError("network/browser prohibited: " + event)
    if event == "open" and not isinstance(args[0], int):
        path, mode, flags = args
        writing = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        if not within(path, write_roots if writing else read_roots):
            raise RuntimeError("unowned file access: " + str(path))
    if event in ("os.listdir", "os.scandir") and not isinstance(args[0], int):
        if not within(args[0] or os.getcwd(), read_roots):
            raise RuntimeError("unowned discovery: " + str(args[0]))
    if event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod"):
        dir_fd = args[2] if event in ("os.mkdir", "os.chmod") else args[1]
        if not within(mutation_path(args[0], dir_fd), write_roots):
            raise RuntimeError("unowned mutation: " + str(args[0]))
    if event in ("os.rename", "os.link", "os.symlink"):
        if not all(within(p, write_roots) for p in args[:2]):
            raise RuntimeError("unowned move/link")
    if event == "subprocess.Popen":
        argv = args[1]
        if not (isinstance(argv, (list, tuple)) and pathlib.Path(argv[0]).name == "git"
                and len(argv) == 5 and argv[1] == "-C" and argv[2] in policy["repos"]
                and argv[3:] == ["rev-parse", "--show-toplevel"]):
            raise RuntimeError("unreviewed subprocess: " + str(argv))
sys.addaudithook(audit)
sys.argv = sys.argv[2:]
sys.path.insert(0, str(pathlib.Path(sys.argv[0]).parent))
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")


def make_histories(inputs, repos):
    now = datetime.now(timezone.utc).isoformat()
    for index, repo in enumerate(repos):
        sid = "fictional-" + str(index)
        text = "Fictional blue widget " + str(index)
        skill = "blue-widget" if index == 0 else "other-widget"
        jsonl(inputs / "codex/sessions" / ("rollout-" + sid + ".jsonl"), [
            {"type": "session_meta", "payload": {"id": sid, "cwd": str(repo), "timestamp": now}},
            {"type": "event_msg", "payload": {"type": "agent_message"}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": text}},
            {"type": "response_item", "payload": {"type": "function_call", "name": "read",
                "arguments": json.dumps({"path": str(repo / ".agents/skills" / skill / "SKILL.md")})}},
        ])
        common = {"sessionId": sid, "cwd": str(repo), "timestamp": now}
        jsonl(inputs / "claude/projects/fictional" / (sid + ".jsonl"), [
            {**common, "type": "user", "message": {"role": "user", "content": text}},
            {**common, "type": "assistant", "message": {"id": "message-" + sid, "role": "assistant", "content": [
                {"type": "text", "text": "Inspect the fictional widget."},
                {"type": "tool_use", "name": "Skill", "input": {"skill": skill}},
            ]}},
        ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    resource = Path(json.loads(args.resources.read_text())["skill-doctor"])
    workspace = args.workspace.resolve()
    workspace.mkdir()
    inputs, output, runtime = [workspace / name for name in ("inputs", "output", "runtime")]
    for path in (inputs, output, runtime):
        path.mkdir()
    env = {"PATH": os.environ["PATH"], "LANG": "C", "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "TMPDIR"):
        path = runtime / key.lower()
        path.mkdir()
        env[key] = str(path)
    repos = [inputs / name for name in ("selected-project", "other-project", "empty-project")]
    for repo in repos:
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], env=env, check=True,
                       stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
    for path in (repos[0] / ".agents/skills/blue-widget/SKILL.md",
                 repos[1] / ".agents/skills/other-widget/SKILL.md",
                 inputs / "codex/skills/global-widget/SKILL.md",
                 inputs / "extra-skills/extra-widget/SKILL.md"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\ndescription: Fictional widget instructions\n---\nCheck the blue widget.\n")
    make_histories(inputs, repos[:2])
    protected = {str(path): observe(path) for path in (resource, inputs)}
    policy = {"read": [str(workspace), str(resource), sys.base_prefix, sys.prefix, "/usr/lib", os.devnull],
              "write": [str(output), str(runtime)], "repos": list(map(str, repos))}

    def execute(name, *arguments, failure=False):
        result = subprocess.run([sys.executable, "-B", "-c", CHILD, json.dumps(policy),
                                 str(resource / "scripts" / name), *map(str, arguments)],
                                cwd=workspace, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=30)
        require((result.returncode != 0) if failure else result.returncode == 0,
                "unexpected helper exit: " + result.stdout + result.stderr)
        return result.stdout + result.stderr

    checks = []
    for test in ("test_collect_sessions.py", "test_render_report.py"):
        result = execute(test)
        require("OK" in result and "Ran " in result, "bundled helper tests did not run")
        checks.append(test + ":" + re.search(r"Ran (\d+) tests", result).group(1))
    for source in ("codex", "claude", "auto"):
        for scope in ("project", "global", "all", "empty", "extra"):
            destination = output / (source + "-" + scope)
            arguments = ["--harness", source, "--codex-home", inputs / "codex",
                         "--claude-home", inputs / "claude", "--out", destination]
            if scope == "all":
                arguments += ["--all-conversations"]
            else:
                arguments += ["--repo", repos[2] if scope == "empty" else repos[0]]
            if scope == "global":
                arguments += ["--include-global-skills"]
            if scope == "extra":
                arguments += ["--skills-dir", inputs / "extra-skills"]
            execute("collect_sessions.py", *arguments)
            inventory = json.loads((destination / "inventory.json").read_text())
            multiplier = 2 if source == "auto" else 1
            expected = 0 if scope == "empty" else multiplier * (2 if scope == "all" else 1)
            require(inventory["stats"]["sessions_sampled"] == expected, "wrong sampled scope")
            require(inventory["stats"]["sessions_in_scope"] == expected, "wrong conversation filtering")
            require(inventory["stats"]["session_records_in_window"] == multiplier * 2, "history fixtures not scanned")
            names = {skill["name"] for skill in inventory["skills"]}
            expected_names = set() if scope == "empty" else {"blue-widget"}
            if scope == "global":
                expected_names.add("global-widget")
            if scope == "extra":
                expected_names.add("extra-widget")
            if scope == "all":
                expected_names.add("other-widget")
            require(names == expected_names, "wrong skill scope: " + str(names))
            require(inventory["harness"] == ("mixed" if source == "auto" else source), "source selection changed")
            require(inventory["conversation_scope"] == ("all" if scope == "all" else "projects"), "scope metadata wrong")
            for session in inventory["sessions"]:
                transcript = Path(session["transcript_path"])
                require(destination in transcript.parents and "Fictional blue widget" in transcript.read_text(),
                        "transcript missing or escaped output")
                if scope not in ("all", "empty"):
                    require(session["skills_used"] == ["blue-widget"], "skill detection missed fictional tool call")
                    require("Fictional blue widget 1" not in transcript.read_text(), "unselected history leaked")
            checks.append(source + ":" + scope)
    # Predetermined scores are renderer data, never inference/quality evidence.
    destination = output / "render"
    proposed = destination / "proposed/blue-widget/SKILL.md"
    proposed.parent.mkdir(parents=True)
    proposed.write_text("# Fictional proposed skill\nCheck the blue widget before editing.\n")
    diff = "--- blue-widget/SKILL.md\n+++ proposed/blue-widget/SKILL.md\n@@ -1 +1 @@\n-Check the widget.\n+Check the blue widget before editing.\n"
    report = {"title": "Fictional isolated doctor report", "generated_at": "2026-01-01T00:00:00Z",
              "harness": "mixed", "handle": "fictional-widget", "stats": {"sessions_analyzed": 2},
              "scores": {"efficiency": .75, "code_quality": .75, "procedure_compliance": .75,
                         "verbosity": .75, "skill_coverage": 1, "overall": .7875},
              "top_findings": ["Fictional repeated check", "Fictional scope issue", "Fictional verbosity issue"],
              "suggestions": [{"skill": "blue-widget", "change": "Check the blue widget first.",
                  "evidence": "Fictional failed session: procedure compliance below 0.5.",
                  "proposed_path": str(proposed), "diff": diff}]}
    report_path = destination / "report.json"
    report_path.write_text(json.dumps(report))
    report_before = observe(destination)
    execute("render_report.py", report_path)
    require(all(observe(destination).get(path) == value for path, value in report_before.items()),
            "renderer changed report input or proposed file")
    require(Path(report["suggestions"][0]["proposed_path"]).read_text().startswith("# Fictional proposed skill"),
            "proposed file is not usable")
    html = (destination / "report.html").read_text()
    require(all(value in html for value in (report["title"], report["top_findings"][0], 'data-filename="SKILL.md"',
                                            "data-pierre-diff", "Check the blue widget first.")), "report lost substantive content")
    require(base64.b64decode(re.search(r'data-diff="([^"]+)"', html).group(1)).decode() == diff,
            "rendered diff differs from fictional input")
    bundle = (resource / "assets/pierre-diffs.js").read_text()
    require(re.sub(r"</script", r"<\\/script", bundle, flags=re.I) in html, "prepared diff UI was not embedded")
    missing = output / "missing/report.json"
    require("not found" in execute("render_report.py", missing, failure=True) and not missing.parent.exists(),
            "missing report input was not rejected without output")
    require(protected == {str(path): observe(path) for path in (resource, inputs)}, "resource/input bytes or modes changed")
    require(not list(workspace.rglob("__pycache__")) and not list(resource.rglob("__pycache__")), "bytecode leaked")
    print(json.dumps({"result": "passed", "checks": checks + ["report-content", "proposed-file-and-diff",
        "prepared-ui-asset", "missing-input-rejection", "complete-input-resource-preservation"],
        "network": "prohibited", "browser": "prohibited", "scoring": "predetermined fictional fixture only"}))


if __name__ == "__main__":
    main()
