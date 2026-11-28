"""Fail when a Catalog skill lacks reviewed on-demand compatibility.

Every skill resource must declare `on_demand` (common or in a surface variant)
or be listed in docs/on-demand-exceptions.json with a reason. Stale exceptions
fail too, so the list only shrinks as Packs are reviewed.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = "docs/on-demand-exceptions.json"


def declared(resource):
    return "on_demand" in resource or any("on_demand" in variant for variant in resource.get("variants", []))


def check(root):
    skills = {}
    for manifest in sorted((root / "packs").glob("*/pack.json")):
        pack = json.loads(manifest.read_text())
        for resource in pack.get("resources", []):
            if resource.get("kind") == "skill":
                skills[pack["id"] + ":" + resource["id"]] = declared(resource)
    exceptions = json.loads((root / EXCEPTIONS).read_text())["skills"]
    errors = []
    if list(exceptions) != sorted(exceptions):
        errors.append(f"{EXCEPTIONS}: skills must be sorted by qualified identity")
    for skill, reason in exceptions.items():
        if skill not in skills:
            errors.append(f"{skill}: exception names an unknown skill")
        elif skills[skill]:
            errors.append(f"{skill}: declares on_demand; remove its exception")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{skill}: exception needs a nonempty reason")
    for skill, has in sorted(skills.items()):
        if not has and skill not in exceptions:
            errors.append(f"{skill}: declare on_demand or add a reviewed exception to {EXCEPTIONS}")
    return errors, sum(skills.values()), len(skills)


def main():
    errors, covered, total = check(ROOT)
    if errors:
        sys.exit("on-demand coverage failed:\n" + "\n".join(errors))
    print(f"on-demand coverage passed: {covered}/{total} skills declared, {total - covered} excepted")


if __name__ == "__main__":
    main()
