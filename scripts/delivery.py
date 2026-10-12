"""Verify GitHub closing references before protected Catalog integration."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "yersonargotev/packy-catalog"
PR_FIELDS = """number state headRefOid baseRefName
closingIssuesReferences(first: 100) {
  totalCount pageInfo { hasNextPage }
  nodes { number repository { nameWithOwner } }
}
"""
ISSUE_FIELDS = """number state title body
labels(first: 100) { totalCount pageInfo { hasNextPage } nodes { name } }
comments(first: 100) { totalCount pageInfo { hasNextPage } nodes { id body author { login } } }
"""


def gh(*args):
    result = subprocess.run(["gh", *args], text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError(f"GitHub CLI failed (exit {result.returncode}); tracker operation did not succeed")
    return result.stdout


def query(kind, number, fields):
    owner, name = REPOSITORY.split("/")
    source = ("query($owner: String!, $name: String!, $number: Int!) {"
              " repository(owner: $owner, name: $name) { nameWithOwner "
              f"{kind}(number: $number) {{ {fields} }}" + " } }")
    data = json.loads(gh("api", "graphql", "-f", f"query={source}",
                         "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"number={number}"))
    if data.get("errors"):
        raise ValueError("GitHub returned GraphQL errors; incomplete tracker data")
    repository = data["data"]["repository"]
    if repository["nameWithOwner"].lower() != REPOSITORY.lower():
        raise ValueError("unexpected tracker repository")
    item = repository[kind]
    if type(item["number"]) is not int or item["number"] != number:
        raise ValueError("unexpected tracker number")
    return item


def nodes(connection):
    values = connection["nodes"]
    if (not isinstance(values, list) or type(connection["totalCount"]) is not int
            or connection["totalCount"] != len(values)
            or connection["pageInfo"]["hasNextPage"] is not False):
        raise ValueError("incomplete tracker connection (maximum 100 entries)")
    return values


def preflight(args, report):
    item = query("pullRequest", args.pr, PR_FIELDS)
    report["observed_head"] = item["headRefOid"]
    recognized = []
    for issue in nodes(item["closingIssuesReferences"]):
        number = issue["number"]
        repository = issue["repository"]["nameWithOwner"]
        if type(number) is not int or number < 1 or not isinstance(repository, str):
            raise ValueError("invalid recognized issue identity")
        recognized.append(f"{repository.lower()}#{number}")
    report["recognized_closing_issues"] = sorted(set(recognized))
    if item["state"] != "OPEN" or item["baseRefName"] != "main":
        raise ValueError("pull request must be open and target main")
    if report["observed_head"] != args.head:
        raise ValueError("candidate head changed")
    if report["recognized_closing_issues"] != report["expected_closing_issues"]:
        raise ValueError("closing issue mismatch: compare expected and recognized identities")


def baseline_file(path):
    data = json.loads(Path(path).read_text())
    if (data["schema_version"] != 1 or data["operation"] != "qualify"
            or data["outcome"] != "passed" or data["repository"] != REPOSITORY):
        raise ValueError("qualification exception: baseline must be a successful Catalog qualification")
    return data["qualification"]


def qualify(number, report, baseline=None):
    contract = (ROOT / "docs/agents/triage-labels.md").read_text()
    matches = re.findall(r"^\|\s*`ready-for-agent`\s*\|\s*`([^`]+)`\s*\|", contract, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError("qualification exception: configured readiness mapping is missing or ambiguous")
    item = query("issue", number, ISSUE_FIELDS)
    labels = sorted(label["name"] for label in nodes(item["labels"]))
    comments = nodes(item["comments"])
    if (not isinstance(item["title"], str) or not item["title"].strip()
            or not isinstance(item["body"], str) or not item["body"].strip()):
        raise ValueError("qualification exception: missing issue scope")
    for comment in comments:
        if (not isinstance(comment["id"], str) or not isinstance(comment["body"], str)
                or (comment["author"] is not None and not isinstance(comment["author"]["login"], str))):
            raise ValueError("qualification exception: incomplete conversation")
    snapshot = {"number": number, "state": item["state"], "title": item["title"], "body": item["body"],
                "labels": labels, "comments": comments, "ready_label": matches[0],
                "readiness_contract_sha256": hashlib.sha256(contract.encode()).hexdigest()}
    report["qualification"] = snapshot
    if item["state"] != "OPEN" or matches[0] not in labels or "wontfix" in labels:
        raise ValueError("qualification exception: delivery issue is no longer open and ready")
    if baseline is not None and snapshot != baseline:
        changed = sorted(key for key in snapshot if snapshot[key] != baseline.get(key))
        raise ValueError("qualification exception: changed " + ", ".join(changed))
    return snapshot


def merge(args, report):
    baseline = None
    if args.expect_none:
        if not args.qualification:
            raise ValueError("qualification exception: prerequisite merge requires --qualification")
        baseline = baseline_file(args.qualification)
        qualify(baseline["number"], report, baseline)
    elif args.qualification:
        raise ValueError("--qualification applies only to prerequisite merges with --expect-none")
    report["merge_status"] = "unknown"
    gh("pr", "merge", str(args.pr), "--repo", REPOSITORY,
       "--squash", "--match-head-commit", args.head)
    report["merge_status"] = "requested"
    result = json.loads(gh("pr", "view", str(args.pr), "--repo", REPOSITORY,
                           "--json", "state,headRefOid,mergeCommit"))
    if result["headRefOid"] != args.head:
        raise ValueError("integration exception: returned candidate differs from proven head")
    if result["state"] != "MERGED":
        raise ValueError("integration pending: verify queue/merge state before continuing; do not resume implementation")
    commit = result["mergeCommit"]["oid"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("integration exception: missing integration commit")
    report.update(merge_status="merged", integration_commit=commit)
    if baseline is not None:
        qualify(baseline["number"], report, baseline)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operations = parser.add_subparsers(dest="operation", required=True)
    qualification = operations.add_parser("qualify", help="capture or compare current delivery qualification")
    qualification.add_argument("--issue", type=int, required=True)
    qualification.add_argument("--baseline", help="previous successful qualify JSON")
    for operation in ("preflight", "merge"):
        command = operations.add_parser(operation)
        command.add_argument("--pr", type=int, required=True)
        command.add_argument("--head", required=True)
        expected = command.add_mutually_exclusive_group(required=True)
        expected.add_argument("--expect-none", action="store_true")
        expected.add_argument("--expect", action="append", help="full owner/repository#number; repeat for a set")
        if operation == "merge":
            command.add_argument("--qualification", help="successful qualify JSON, required for prerequisite merges")
    args = parser.parse_args()
    report = {"schema_version": 1, "operation": args.operation, "repository": REPOSITORY, "outcome": "failed"}
    try:
        if args.operation == "qualify":
            if args.issue < 1:
                raise ValueError("positive issue number required")
            baseline = baseline_file(args.baseline) if args.baseline else None
            qualify(args.issue, report, baseline)
            report["outcome"] = "passed"
            print(json.dumps(report, sort_keys=True))
            return 0
        report.update(pull_request=args.pr, candidate_head=args.head, observed_head=None,
                      expected_closing_issues=sorted(set(value.lower() for value in args.expect or [])),
                      recognized_closing_issues=None)
        if args.pr < 1 or not re.fullmatch(r"[0-9a-f]{40}", args.head):
            raise ValueError("positive PR number and full lowercase candidate SHA required")
        for identity in report["expected_closing_issues"]:
            if not re.fullmatch(re.escape(REPOSITORY) + r"#[1-9][0-9]*", identity):
                raise ValueError("expected closing issues must identify this Catalog repository")
        preflight(args, report)
        if args.operation == "merge":
            merge(args, report)
        report["outcome"] = "passed"
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.TimeoutExpired) as error:
        report["error"] = str(error)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["outcome"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
