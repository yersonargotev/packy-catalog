"""Run the ordinary suite with Pack helper execution sentinels."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="catalog-inert-tests-") as scratch:
        project = Path(scratch) / "catalog"
        shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        log = Path(scratch) / "helper-execution.log"
        helpers = sorted((project / "packs/pstack").rglob("check-plan.mjs"))
        if not helpers:
            sys.exit("no pstack plan helpers found for the inertness check")
        for helper in helpers:
            name = helper.relative_to(project).as_posix()
            # This sentinel records both direct shell and Node .mjs dispatch.
            helper.write_text(
                "#!/bin/sh\n"
                f"// 2>/dev/null; printf '%s\\n' {shlex.quote(name)} >> {shlex.quote(str(log))}; exit 97\n"
                'import { appendFileSync } from "node:fs";\n'
                f"appendFileSync({json.dumps(str(log))}, {json.dumps(name + chr(10))});\n"
                "process.exit(97);\n"
            )
        env = {**os.environ, "PACKY_TEST_ARCHIVE": str(Path(os.environ["PACKY_TEST_ARCHIVE"]).resolve()),
               "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover",
                                 "-s", str(project / "scripts/tests"), "-v"], cwd=project, env=env)
        if log.exists():
            sys.exit("Pack helper executed during ordinary tests:\n" + log.read_text())
        if result.returncode:
            sys.exit(result.returncode)
        print(f"ordinary suite passed with {len(helpers)} Pack helper execution sentinels")


if __name__ == "__main__":
    main()
