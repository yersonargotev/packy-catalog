#!/usr/bin/env python3
"""Exercise the read-only evidence retention preflight on both adapted resources."""
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile

from content_probe_process import run_child

ROOT = Path(__file__).resolve().parents[2]
HELPERS = [ROOT / f"packs/pstack/skills/{host}/show-me-your-work/scripts/check-retention.py" for host in ("agents", "claude")]
HEADER = "ts\tphase\tdecision\twhy\tevidence\tresult\n"
NAMES = ("probe-v4.log", "probe-v8.log", "artifact-validation.log", "formula.rb", "review.txt", "later-acceptance.log")


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


def main():
    assert all(p.is_file() for p in HELPERS), "missing retention helper"
    assert HELPERS[0].read_bytes() == HELPERS[1].read_bytes(), "adapted helpers differ"
    for helper in HELPERS:
        with tempfile.TemporaryDirectory(prefix="retention-probe-") as tmp:
            root = Path(tmp).resolve()
            env = {"PATH": os.environ.get("PATH", ""), "LANG": "C", "LC_ALL": "C"}
            for key, name in (("HOME", "home"), ("XDG_CONFIG_HOME", "config"), ("TMPDIR", "tmp")):
                (root / name).mkdir()
                env[key] = str(root / name)
            target, retained, unrelated = (root / x for x in ("owned", "retained", "unrelated-worktree"))
            for path in (target, retained, unrelated):
                path.mkdir()
            (unrelated / "sentinel").write_text("operator state")
            trail = retained / "decisions.tsv"
            originals = [target / name for name in NAMES]
            for path in originals:
                path.write_text(path.name)
            trail.write_text(HEADER + "".join(f"now\tproof\tchecked\twhy\t{p}\tok\n" for p in originals))
            shutil.copyfile(originals[-1], retained / NAMES[-1])
            def relocate(source, dest):
                with trail.open("a") as f:
                    f.write(f"now\trelocation\tretained\twhy\t[{source}]({dest})\tok\n")
            relocate(originals[-1], retained / NAMES[-1])
            def check(expect, targets=(target,), handoffs=()):
                args = [sys.executable, "-B", str(helper), "--base", str(root), "--trail", str(trail)]
                args += sum((["--target", str(t)] for t in targets), [])
                args += sum((["--handoff", str(h)] for h in handoffs), []) if handoffs else ["--no-handoff"]
                before = snapshot(root)
                status, out, err = run_child(args, cwd=root, env=env, timeout=30)
                assert (status == 0) == expect, (args, status, out, err)
                assert snapshot(root) == before, "preflight mutated files"
                return out + err
            message = check(False)
            for name in NAMES[:-1]:
                assert name in message, message
            for source in originals[:-1]:
                shutil.copyfile(source, retained / source.name)
                relocate(source, retained / source.name)
            check(True)
            handoff = retained / "handoff.md"
            handoff.write_text(f"[proof]({originals[0]}) and `{originals[1]}`\n")
            check(True, handoffs=(handoff,))
            missing = originals[0]
            missing.rename(root / "saved")
            check(False)
            (root / "saved").rename(missing)
            dest = retained / NAMES[0]
            dest.rename(root / "saved")
            check(False)
            (root / "saved").rename(dest)
            dest.write_text("wrong bytes")
            check(False)
            shutil.copyfile(missing, dest)
            check(False, targets=(target, retained / NAMES[0]))
            check(True, targets=(target, root / "absent"))
            check(False, targets=(root / "absent",), handoffs=(retained / "missing.md",))
            assert (unrelated / "sentinel").read_text() == "operator state"
            print(f"{helper.relative_to(ROOT)}: partial copy blocked; verified copies passed; negatives and read-only state verified")


if __name__ == "__main__":
    main()
