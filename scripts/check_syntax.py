"""Check Catalog-owned tooling syntax without executing probes or Pack content."""
import ast
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def check_shell(source, name):
    result = subprocess.run(["bash", "-n"], input=source, text=True, capture_output=True)
    if result.returncode:
        sys.exit(f"{name}: {result.stderr.strip()}")


def main():
    for script in sorted((ROOT / "scripts").rglob("*.py")):
        name = script.relative_to(ROOT).as_posix()
        try:
            ast.parse(script.read_text(), filename=name)
        except SyntaxError as error:
            sys.exit(f"{name}: {error}")
    for script in sorted((ROOT / "scripts").rglob("*.sh")):
        check_shell(script.read_text(), script.relative_to(ROOT).as_posix())
    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        name = workflow.relative_to(ROOT).as_posix()
        data = yaml.load(workflow.read_text(), Loader=yaml.BaseLoader)
        for job_name, job in data["jobs"].items():
            for number, step in enumerate(job["steps"], 1):
                if "run" in step:
                    check_shell(step["run"], f"{name}: {job_name} step {number}")
    print("Catalog tooling syntax passed")


if __name__ == "__main__":
    main()
