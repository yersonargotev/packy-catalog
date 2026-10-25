"""Fictional, offline helper acceptance; run only via --warp-helpers after review."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import urllib.parse
import urllib.request


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def no_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("helper attempted network access: " + event)


# The fixture and every Python child prohibit networking, including accidental APIs.
CHILD = '''import runpy, sys
sys.addaudithook(lambda event, args: (_ for _ in ()).throw(RuntimeError("network prohibited")) if event.startswith("socket.") else None)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def observe(root):
    return {str(p.relative_to(root)): (p.lstat().st_mode, p.read_bytes() if p.is_file() else None)
            for p in root.rglob("*")}


def execute(script, *args, failure=False):
    result = subprocess.run([sys.executable, "-B", "-c", CHILD, str(script), *map(str, args)],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    require((result.returncode != 0) if failure else result.returncode == 0,
            "unexpected helper exit: " + result.stdout + result.stderr)
    return result.stdout + result.stderr


class FictionalResponse(io.BytesIO):
    status = 200
    headers = {}


def fictional_github(request, **kwargs):
    """Replace the external HTTP transport; unknown routes fail closed."""
    url = urllib.parse.urlparse(request.full_url)
    require(url.netloc == "api.github.com", "unexpected API host")
    if url.path == "/graphql":
        payload = {"data": {"repository": {"pullRequest": {
            "closingIssuesReferences": {"nodes": [], "pageInfo": {"hasNextPage": False}},
            "timelineItems": {"nodes": [], "pageInfo": {"hasNextPage": False}},
        }}}}
    else:
        payloads = {
            "/repos/fictional/widgets/pulls/7": {"head": {"ref": "oz-agent/implement-issue-123"}},
            "/repos/fictional/widgets/pulls/7/files": [{"filename": "widget.py"}],
            "/repos/fictional/widgets/issues/123": {"number": 123},
            "/repos/fictional/widgets/pulls": [],
        }
        require(url.path in payloads, "unexpected fictional API route: " + url.path)
        payload = payloads[url.path]
    return FictionalResponse(json.dumps(payload).encode())


def resolver(script, target, *, explicit):
    # Only fictional credentials exist in the runner's isolated environment.
    os.environ["GH_TOKEN"] = "fictional-probe-token"
    if explicit:
        os.environ["OZ_REPO_ROOT"] = str(target)
    else:
        os.environ.pop("OZ_REPO_ROOT", None)
    previous, arguments = urllib.request.urlopen, sys.argv
    urllib.request.urlopen = fictional_github
    sys.argv = [str(script), "--repo", "fictional/widgets", "--pr", "7"]
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(script), run_name="__main__")
    finally:
        urllib.request.urlopen, sys.argv = previous, arguments
    return output.getvalue()


def review_helpers(resources, workspace):
    target, inputs, output = [workspace / name for name in ("target", "inputs", "output")]
    for path in (target, inputs, output):
        path.mkdir()
    spec = target / "specs/GH123/product.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("# Fictional target product\nUse the blue widget.\n")
    script = Path(resources["review-pr"]) / "scripts/resolve_spec_context.py"
    # A separate cache copy supplies a meaningful decoy for the native fallback.
    cache = workspace / "cache/packs/warp/skills/review-pr/scripts"
    cache.mkdir(parents=True)
    cached = cache / script.name
    cached.write_bytes(script.read_bytes())
    cached.chmod(script.stat().st_mode)
    decoy = workspace / "cache/packs/specs/GH123/product.md"
    decoy.parent.mkdir(parents=True)
    decoy.write_text("# Decoy cache product\nUse the WRONG cache widget.\n")
    cache_before = observe(workspace / "cache")
    target_before = observe(target)
    negative = resolver(cached, target, explicit=False)
    require("WRONG cache widget" in negative and "blue widget" not in negative,
            "negative observation failed to expose the script-location fallback")
    positive = resolver(script, target, explicit=True)
    require("Use the blue widget." in positive and "WRONG" not in positive,
            "explicit target did not select the intended specs")
    (output / "spec_context.md").write_text(positive)
    # Removing the intended specs must not silently find a decoy in cache.
    spec.rename(spec.with_suffix(".saved"))
    missing = resolver(script, target, explicit=True)
    require("No approved or repository spec context" in missing and "WRONG" not in missing,
            "missing target spec used a cache fallback")
    spec.with_suffix(".saved").rename(spec)
    diff = inputs / "pr_diff.txt"
    diff.write_text("diff --git a/widget.py b/widget.py\n--- a/widget.py\n+++ b/widget.py\n@@ -1 +1 @@\n[OLD:1] red\n[NEW:1] blue\n")
    (inputs / "pr_description.txt").write_text("Fictional widget color repair.\n")
    inputs_before = observe(inputs)
    review = output / "review.json"
    payload = {"verdict": "APPROVE", "body": "## Overview\nFictional fixture.\n\nFound: 0 critical, 0 important, 1 suggestions\n\nApprove with nits",
               "comments": [{"path": "widget.py", "line": 1, "side": "RIGHT", "body": "💡 [SUGGESTION] Explain the color."}]}
    review.write_text(json.dumps(payload))
    validator = Path(resources["review-pr"]) / "scripts/validate_review_json.py"
    require("validation passed" in execute(validator, "--review-json", review, "--diff", diff), "valid review rejected")
    payload["comments"][0]["line"] = 99
    invalid = output / "invalid-review.json"
    invalid.write_text(json.dumps(payload))
    require("review validation failed" in execute(validator, "--review-json", invalid, "--diff", diff, failure=True),
            "validator accepted an unannotated location")
    require(target_before == observe(target) and inputs_before == observe(inputs)
            and cache_before == observe(workspace / "cache"), "review helper changed target/inputs/cache bytes or modes")
    return ["explicit-target-spec-and-artifact-output", "decoy-cache-negative", "missing-target-no-fallback",
            "exact-diff-review-positive-and-invalid-line-rejection"]


def report_helpers(resources, workspace):
    target, output = workspace / "report-target", workspace / "reports"
    target.mkdir()
    output.mkdir()
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    def git(*args):
        result = subprocess.run(["git", "-C", str(target), *args], capture_output=True, text=True,
                                env=env, stdin=subprocess.DEVNULL, timeout=10)
        require(result.returncode == 0, "fictional Git setup failed: " + result.stderr)
        return result.stdout.strip()
    git("init", "-q")
    git("remote", "add", "origin", "https://github.com/fictional/widgets.git")
    (target / "widget.py").write_text('COLOR = "blue"\n')
    git("add", "widget.py")
    git("-c", "user.name=Fictional Probe", "-c", "user.email=probe@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "Fictional widget")
    commit = git("rev-parse", "HEAD")
    target_before = observe(target)
    source = Path(resources["readout"])
    template = (source / "assets/template.html").read_text()
    pane = (source / "assets/code-pane.html").read_text()
    name = "2026-01-01-fictional-widgets.html"
    existing = output / name
    existing.write_text("Existing report must survive.\n")
    document = output / "2026-01-01-fictional-widgets-2.html"
    title = "Fictional blue widget report"
    html = template.replace("</head>", '<meta name="description" content="Fictional report evidence"></head>')
    html = re.sub(r"<title>.*?</title>", "<title>" + title + "</title>", html, flags=re.S)
    html = html.replace("</body>", f'<a href="https://github.com/fictional/widgets/blob/{commit}/widget.py#L1">widget.py:1</a>\n' + pane + "\n</body>")
    document.write_text(html)
    for kind in ("style", "script"):
        pattern = rf"<{kind} data-readout>.*?</{kind}>"
        expected = re.findall(pattern, template, re.S)
        require(expected and all(block in html for block in expected), "canonical chrome changed")
    execute(source / "scripts/embed_snippets.py", document, "--repo", target)
    embedded = document.read_text()
    blob = re.search(r'<script type="application/json" data-code-snippets>\s*(.*?)</script>', embedded, re.S)
    require(blob is not None, "missing embedded source")
    snippets = json.loads(blob.group(1))
    require(snippets[f"fictional/widgets@{commit}:widget.py"]["text"] == 'COLOR = "blue"\n', "wrong source embedded")
    before_index = document.read_bytes()
    execute(source / "scripts/update_index.py", output)
    index = (output / "index.html").read_text()
    require(title in index and document.name in index and "Fictional report evidence" in index, "incorrect report index")
    require(document.read_bytes() == before_index and existing.read_text() == "Existing report must survive.\n",
            "index or report naming overwrote an input")
    missing_doc = output / "absent.html"
    execute(source / "scripts/embed_snippets.py", missing_doc, "--repo", target, failure=True)
    require(not missing_doc.exists(), "failed helper created input")
    require(target_before == observe(target), "report helper changed source repository bytes or modes")
    return ["explicit-report-directory-and-index", "canonical-chrome-and-source-embedding", "existing-report-preserved",
            "missing-input-rejection"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    sys.addaudithook(no_network)
    resources = json.loads(args.resources.read_text())
    args.workspace.mkdir()
    checks = review_helpers(resources, args.workspace) + report_helpers(resources, args.workspace)
    require(not (Path.home() / ".readouts").exists(), "helper used personal readout output")
    require(not list(args.workspace.rglob("__pycache__")), "helper wrote bytecode into resource/input trees")
    print(json.dumps({"result": "passed", "checks": checks, "network": "prohibited", "browser": "not launched"}))


if __name__ == "__main__":
    main()
