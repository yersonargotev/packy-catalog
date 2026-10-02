#!/usr/bin/env python3
"""Check the single reviewed v2 -> v3 catalog cut without converting content."""

import json
from pathlib import Path
import re
import stat
import sys


def inventory(root):
    files = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlink in catalog: {path}")
        if path.is_file():
            files[path.relative_to(root)] = (stat.S_IMODE(path.stat().st_mode), path.read_bytes())
    return files


def validate(candidate, baseline):
    before, after = inventory(baseline / "packs"), inventory(candidate / "packs")
    if before.keys() != after.keys():
        raise ValueError("schema cut must preserve the complete Pack file inventory")
    manifests = sorted(baseline.glob("packs/*/pack.json"))
    if not manifests:
        raise ValueError("baseline has no Packs")
    for path, (mode, data) in before.items():
        new_mode, new_data = after[path]
        if mode != new_mode:
            raise ValueError(f"schema cut changed mode: {path}")
        if len(path.parts) != 2 or path.name != "pack.json":
            if data != new_data:
                raise ValueError(f"schema cut changed resource bytes: {path}")
            continue
        old, new = json.loads(data), json.loads(new_data)
        if old.pop("schema_version") != 2 or new.pop("schema_version") != 3:
            raise ValueError(f"expected complete v2 -> v3 cut: {path}")
        old_version, new_version = old.pop("version"), new.pop("version")
        if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", old_version):
            raise ValueError(f"unexpected baseline version: {old_version}")
        expected = f"{int(old_version.split('.')[0]) + 1}.0.0"
        if new_version != expected:
            raise ValueError(f"{path}: expected major cut version {expected}, got {new_version}")
        if old != new:
            raise ValueError(f"schema cut changed manifest contract: {path}")
    print(f"validated exact schema cut: {len(manifests)} Packs; all resource bytes and modes preserved")


if __name__ == "__main__":
    try:
        validate(Path(sys.argv[1]), Path(sys.argv[2]))
    except (ValueError, KeyError, IndexError, OSError) as error:
        sys.exit(f"schema cut validation: {error}")
