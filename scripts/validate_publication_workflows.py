"""Enforce the executable and credential boundaries of Catalog publication."""
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("install workflow prerequisites: python3 -m pip install -r requirements-tooling.txt")

from packy_tool import read_pin

ROOT = Path(__file__).resolve().parents[1]


class UniqueLoader(yaml.BaseLoader):
    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError("duplicate workflow key: " + str(key))
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate():
    read_pin(ROOT / "packy-release.json")
    validation_text = (ROOT / ".github/workflows/validate.yml").read_text()
    publication_text = (ROOT / ".github/workflows/publish.yml").read_text()
    validation = yaml.load(validation_text, Loader=UniqueLoader)
    publication = yaml.load(publication_text, Loader=UniqueLoader)
    for workflow in (validation, publication):
        require(set(workflow) <= {"name", "on", "permissions", "concurrency", "jobs"}, "unexpected workflow controls")
    for job in (*validation["jobs"].values(), *publication["jobs"].values()):
        require(set(job) <= {"name", "if", "needs", "runs-on", "timeout-minutes", "permissions", "env", "steps"},
                "unexpected job execution controls")
    require(validation["permissions"] == {"contents": "read"}, "candidate validation must be read-only")
    require(set(validation["jobs"]) == {"validate"}, "unexpected validation job")
    require("permissions" not in validation["jobs"]["validate"], "validation job may not override permissions")
    require(not re.search(r"secrets\.|(?:contents|attestations|id-token):\s*write", validation_text),
            "candidate validation must not receive publication authority")
    require('./scripts/validate.sh "${args[@]}" --json' in validation_text,
            "CI must invoke the documented local validation entry point")
    require(publication["permissions"] == {}, "publication must deny default permissions")
    require(publication["on"] == {"workflow_run": {"workflows": ["Catalog validation"], "types": ["completed"]}},
            "publication must follow the validation workflow")
    require(publication["concurrency"] == {"group": "catalog-publication", "cancel-in-progress": "false"},
            "publication retries must be serialized")
    require(set(publication["jobs"]) == {"prepare", "publish"}, "unexpected publication job")
    prepare = publication["jobs"]["prepare"]
    publish = publication["jobs"]["publish"]
    expected_gate = " && ".join([
        "github.repository == 'yersonargotev/packy-catalog'",
        "github.event.workflow_run.event == 'push'",
        "github.event.workflow_run.head_branch == 'main'",
        "github.event.workflow_run.head_repository.full_name == github.repository",
        "github.event.workflow_run.conclusion == 'success'",
    ])
    require(" ".join(prepare["if"].split()) == expected_gate, "preparation must gate the exact successful official main push")
    require(prepare["permissions"] == {"contents": "read"}, "preparation must remain read-only")
    require(publish["needs"] == "prepare" and "if" not in publish, "publication must require successful preparation")
    require(publish["permissions"] == {"actions": "read", "attestations": "write", "contents": "write", "id-token": "write"},
            "unexpected publication authority")
    expected_env = {"CATALOG_COMMIT": "${{ github.event.workflow_run.head_sha }}"}
    require(prepare["env"] == expected_env and publish["env"] == expected_env, "jobs must use the exact validated commit")
    checkout, build, retain = prepare["steps"]
    require(checkout["with"] == {"ref": "${{ env.CATALOG_COMMIT }}", "path": "catalog-project", "persist-credentials": "false"},
            "preparation checkout must use the validated commit without credentials")
    require(build["run"] == '''set -euo pipefail
[[ "$(git rev-parse HEAD)" == "$CATALOG_COMMIT" ]] || { echo "source commit mismatch" >&2; exit 1; }
source_status="$(git status --porcelain)"
[[ -z "$source_status" ]] || { echo "source checkout is dirty" >&2; exit 1; }
./scripts/packy.sh catalog build \\
  --project . \\
  --source-repository "$GITHUB_REPOSITORY" \\
  --source-commit "$CATALOG_COMMIT" \\
  --out-dir "$GITHUB_WORKSPACE/dist" --json
''', "build must bind pinned tooling and clean exact source")
    require(retain["with"] == {"name": "catalog-snapshot-${{ env.CATALOG_COMMIT }}", "path": "dist", "if-no-files-found": "error"},
            "retain only the prepared snapshot")
    download, pin, acquire, attest, release = publish["steps"]
    require(download["with"] == {"name": "catalog-snapshot-${{ env.CATALOG_COMMIT }}", "path": "dist"},
            "download assets only from this preparation run")
    require(pin["run"] == '''set -euo pipefail
[[ "$CATALOG_COMMIT" =~ ^[0-9a-f]{40}$ ]]
gh api --header 'Accept: application/vnd.github.raw+json' \\
  "repos/$GITHUB_REPOSITORY/contents/packy-release.json?ref=$CATALOG_COMMIT" \\
  > "$RUNNER_TEMP/packy-release.json"
''', "credentialed job must fetch only reviewed pin data at the validated commit")
    tool_source = (ROOT / "scripts/packy_tool.py").read_text()
    expected_acquisition = '''set -euo pipefail
python3 -B - --pin "$RUNNER_TEMP/packy-release.json" \\
  --executable-output "$RUNNER_TEMP/verified-packy" <<'PY'
# BEGIN VERIFIED ACQUISITION
''' + tool_source + '''# END VERIFIED ACQUISITION
PY
'''
    require(acquire["run"] == expected_acquisition, "trusted inline acquisition must match the local verification contract")
    require(acquire["env"] == {"PACKY_CACHE_DIR": "${{ runner.temp }}/publisher-cache"}, "publisher must use a fresh job-local cache")
    require(attest["with"] == {"subject-path": "dist/catalog-snapshot.tar.gz"}, "attest only the prepared archive")
    require(release["run"].strip() == '"$RUNNER_TEMP/verified-packy" catalog publish --repository "$GITHUB_REPOSITORY" --commit "$CATALOG_COMMIT" --dist dist --json',
            "publication must invoke only independently verified release tooling")
    for step in (pin, release):
        require(step["env"] == {"GH_TOKEN": "${{ github.token }}"}, "credentials belong only to reviewed pin read and publisher")
    for step, action in ((checkout, "checkout"), (retain, "upload-artifact"),
                         (download, "download-artifact"), (attest, "attest-build-provenance")):
        require(re.fullmatch(r"actions/" + action + r"@[0-9a-f]{40}", step.get("uses", "")),
                "publication step must use pinned actions/" + action)
    for step in prepare["steps"] + publish["steps"]:
        allowed = {"name", "uses", "with"} if "uses" in step else {"name", "run", "shell", "env", "working-directory"}
        require(set(step) <= allowed, "unexpected publication step execution controls")
        if "run" in step:
            require(step.get("shell", "bash") == "bash", "publication must use its reviewed shell")
    require(build.get("working-directory") == "catalog-project" and "env" not in build,
            "preparation must build the reviewed project with the declared environment")
    for step in publish["steps"]:
        require("working-directory" not in step, "publisher steps may not redirect proof")
    require(not re.search(r"go run|setup-go|repository: yersonargotev/packy|PACKY_(BUILDER_COMMIT|VALIDATOR_ROOT)|v[0-9]+\.[0-9]+\.[0-9]+", "\n".join(
        line for line in (validation_text + publication_text).splitlines() if not line.lstrip().startswith("uses:")
    )), "workflows must consume one data pin without source/tool-version declarations")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        sys.exit("publication workflow validation: " + str(error))
    print("validated read-only candidate checks and independently verified publication authority")
