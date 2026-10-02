#!/usr/bin/env python3
"""Run shipped helpers and assert runtime work leaves installed bytes untouched."""
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2] / "packs/pstack/skills"

def inventory(path):
    return {str(p.relative_to(path)): (p.stat().st_mode, hashlib.sha256(p.read_bytes()).hexdigest()) for p in path.rglob("*") if p.is_file()}

def run(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = process.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    assert process.returncode == 0, (command, process.returncode, out, err)
    return out

for host in ("codex", "claude", "opencode"):
    skills = root / host
    before = inventory(skills)
    scripts = skills / "poteto-mode/scripts"
    assert "Usage: orch" in run(["bun", str(scripts / "orch/orch.ts"), "--help"])
    assert "usage:" in run(["bun", str(scripts / "watch-pr/watch-pr"), "--help"]).lower()
    with tempfile.TemporaryDirectory(prefix="pstack-log-") as directory:
        log = Path(directory) / "decisions.tsv"
        command = ["bash", str(skills / "show-me-your-work/scripts/log.sh"), str(log)]
        run(command + ["probe", "=unsafe", "reason\nnext", "source\tpath", "pass"])
        run(command + ["probe", "second", "reason", "source", "pass"])
        rows = log.read_text().splitlines()
        assert len(rows) == 3 and all(len(row.split("\t")) == 6 for row in rows)
        assert "'=unsafe" in rows[1]
    assert before == inventory(skills), f"{host} runtime changed installed skill closure"
    print(f"{host}: orch/watch-pr execute; log appends and escapes cells; installed closure unchanged", flush=True)
