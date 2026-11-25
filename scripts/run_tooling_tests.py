"""Run the ordinary suite with Pack helper execution sentinels."""
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="catalog-inert-tests-") as scratch:
        project = Path(scratch) / "catalog"
        shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        log = Path(scratch) / "helper-execution.log"
        helpers = sorted((project / "packs/pstack").rglob("worktree-audit.sh"))
        if not helpers:
            sys.exit("no pstack shell helpers found for the inertness check")
        for helper in helpers:
            name = helper.relative_to(project).as_posix()
            # This sentinel records both direct execution and explicit shell dispatch.
            helper.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' {shlex.quote(name)} >> {shlex.quote(str(log))}\n"
                "exit 97\n"
            )
        # Git state belongs to the disposable fixtures, never to the caller.
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("GIT_") and key != "EMAIL"}
        env.update(PACKY_TEST_ARCHIVE=str(Path(os.environ["PACKY_TEST_ARCHIVE"]).resolve()),
                   HOME=str(Path(scratch) / "home"), XDG_CONFIG_HOME=str(Path(scratch) / "config"),
                   PYTHONPATH=os.pathsep.join(filter(None, (str(Path(yaml.__file__).parent.parent),
                                                            os.environ.get("PYTHONPATH")))),
                   PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_SYSTEM=os.devnull,
                   GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="user.useConfigOnly",
                   GIT_CONFIG_VALUE_0="true")
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover",
                                 "-s", str(project / "scripts/tests"), "-v"], cwd=project, env=env)
        if log.exists():
            sys.exit("Pack helper executed during ordinary tests:\n" + log.read_text())
        if result.returncode:
            sys.exit(result.returncode)
        print(f"ordinary suite passed with {len(helpers)} Pack helper execution sentinels")


if __name__ == "__main__":
    main()
