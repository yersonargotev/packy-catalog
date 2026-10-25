#!/usr/bin/env python3
"""Run shipped helpers and assert runtime work leaves installed bytes untouched."""
import hashlib
import os
from pathlib import Path
import shutil
import tempfile

from content_probe_process import run_child

root = Path(__file__).resolve().parents[2] / "packs/pstack/skills"

def inventory(path):
    return {str(p.relative_to(path)): (p.stat().st_mode, hashlib.sha256(p.read_bytes()).hexdigest()) for p in path.rglob("*") if p.is_file()}

def run(command, *, cwd, env):
    status, out, err = run_child(command, cwd=cwd, env=env, timeout=30)
    assert status == 0, (command, status, out, err)
    return out

for host in ("codex", "claude"):
    source = root / host
    original = inventory(source)
    with tempfile.TemporaryDirectory(prefix="pstack-helpers-") as directory:
        workspace = Path(directory).resolve()
        env = {"PATH": os.environ.get("PATH", ""), "LANG": "C", "LC_ALL": "C"}
        for key, name in (("HOME", "home"), ("TMPDIR", "tmp"), ("XDG_CONFIG_HOME", "config"),
                          ("XDG_DATA_HOME", "data"), ("XDG_CACHE_HOME", "cache"),
                          ("BUN_INSTALL_CACHE_DIR", "bun-cache")):
            path = workspace / name
            path.mkdir()
            env[key] = str(path)
        for key in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY", "https_proxy", "http_proxy",
                    "all_proxy", "no_proxy", "SSL_CERT_FILE", "SSL_CERT_DIR", "CURL_CA_BUNDLE"):
            if key in os.environ:
                env[key] = os.environ[key]
        skills = workspace / host
        shutil.copytree(source, skills)
        before = inventory(skills)
        scripts = skills / "poteto-mode/scripts"
        assert "Usage: orch" in run(["bun", str(scripts / "orch/orch.ts"), "--help"], cwd=workspace, env=env)
        assert "usage:" in run(["bun", str(scripts / "watch-pr/watch-pr"), "--help"], cwd=workspace, env=env).lower()
        with tempfile.TemporaryDirectory(prefix="pstack-log-", dir=workspace) as directory:
            log = Path(directory) / "decisions.tsv"
            command = ["bash", str(skills / "show-me-your-work/scripts/log.sh"), str(log)]
            run(command + ["probe", "=unsafe", "reason\nnext", "source\tpath", "pass"], cwd=workspace, env=env)
            run(command + ["probe", "second", "reason", "source", "pass"], cwd=workspace, env=env)
            rows = log.read_text().splitlines()
            assert len(rows) == 3 and all(len(row.split("\t")) == 6 for row in rows)
            assert "'=unsafe" in rows[1]
        assert before == inventory(skills), f"{host} runtime changed installed skill closure"
        print(f"{host}: orch/watch-pr execute; log appends and escapes cells; installed closure unchanged", flush=True)
    assert original == inventory(source), f"{host} authored closure changed"
