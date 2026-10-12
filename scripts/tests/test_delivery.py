"""Exercise delivery commands at the GitHub CLI boundary without tracker writes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
REPO = "yersonargotev/packy-catalog"
HEAD = "a" * 40


def connection(nodes):
    return {"nodes": nodes, "totalCount": len(nodes), "pageInfo": {"hasNextPage": False}}


def pull_request(numbers=()):
    return {"data": {"repository": {"nameWithOwner": REPO, "pullRequest": {
        "number": 80, "state": "OPEN", "headRefOid": HEAD, "baseRefName": "main",
        "closingIssuesReferences": connection([
            {"number": number, "repository": {"nameWithOwner": REPO}} for number in numbers])}}}}


def delivery_issue():
    return {"data": {"repository": {"nameWithOwner": REPO, "issue": {
        "number": 71, "state": "OPEN", "title": "Guard closing references", "body": "Approved scope",
        "labels": connection([{"name": "status:approved"}]),
        "comments": connection([{"id": "comment-1", "body": "Approved acceptance", "author": {"login": "owner"}}])}}}}


def merged():
    return {"state": "MERGED", "headRefOid": HEAD, "mergeCommit": {"oid": "b" * 40}}


class DeliveryContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="catalog-delivery-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.project = self.work / "catalog"
        (self.project / "scripts").mkdir(parents=True)
        (self.project / "docs/agents").mkdir(parents=True)
        shutil.copyfile(ROOT / "scripts/delivery.py", self.project / "scripts/delivery.py")
        shutil.copyfile(ROOT / "docs/agents/triage-labels.md", self.project / "docs/agents/triage-labels.md")
        self.responses = self.work / "responses.json"
        self.log = self.work / "calls.jsonl"
        gh = self.work / "gh"
        gh.write_text(f'''#!{sys.executable}
import json, os, pathlib, sys
log = pathlib.Path(os.environ["TEST_GH_LOG"])
calls = log.read_text().splitlines() if log.exists() else []
with log.open("a") as stream:
    stream.write(json.dumps(sys.argv[1:]) + "\\n")
responses = json.loads(pathlib.Path(os.environ["TEST_GH_RESPONSES"]).read_text())
if len(calls) >= len(responses):
    sys.exit("unexpected tracker call")
response = responses[len(calls)]
print(response.get("raw", json.dumps(response.get("json"))))
sys.exit(response.get("exit", 0))
''')
        gh.chmod(0o755)
        self.env = {"PATH": str(self.work), "HOME": str(self.work / "home"),
                    "TEST_GH_LOG": str(self.log), "TEST_GH_RESPONSES": str(self.responses),
                    "PYTHONDONTWRITEBYTECODE": "1"}

    def run_cli(self, *args, responses):
        self.responses.write_text(json.dumps(responses))
        self.log.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, "-B", str(self.project / "scripts/delivery.py"), *args],
                                env=self.env, text=True, capture_output=True, timeout=10)
        return result

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_preflight_proves_an_explicit_empty_prerequisite_set_without_writes(self):
        result = self.run_cli("preflight", "--pr", "80", "--head", HEAD, "--expect-none",
                              responses=[{"json": pull_request()}])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["outcome"], "passed")
        self.assertEqual(report["repository"], REPO)
        self.assertEqual(report["pull_request"], 80)
        self.assertEqual(report["observed_head"], HEAD)
        self.assertEqual(report["expected_closing_issues"], [])
        self.assertEqual(report["recognized_closing_issues"], [])
        self.assertTrue(all(call[:2] == ["api", "graphql"] for call in self.calls()))

    def test_merge_automatically_checks_the_final_singleton_before_exact_head_squash(self):
        result = self.run_cli("merge", "--pr", "80", "--head", HEAD, "--expect", REPO + "#71",
                              responses=[{"json": pull_request([71])}, {"raw": "merged"}, {"json": merged()}])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["recognized_closing_issues"], [REPO + "#71"])
        self.assertEqual(report["merge_status"], "merged")
        self.assertEqual(self.calls()[1], ["pr", "merge", "80", "--repo", REPO,
                                           "--squash", "--match-head-commit", HEAD])

    def test_reference_mismatches_never_attempt_merge(self):
        cases = [((), [71]), ([71], []), ([71], [71, 72]), ([71], [72])]
        for expected, observed in cases:
            with self.subTest(expected=expected, observed=observed):
                flags = ["--expect", REPO + "#71"] if expected else ["--expect-none"]
                response = pull_request(observed)
                # Reproduces the GitHub result of "does not close #71":
                # prose is irrelevant; the server still recognizes the issue.
                response["data"]["repository"]["pullRequest"]["body"] = "This does not close #71"
                result = self.run_cli("merge", "--pr", "80", "--head", HEAD, *flags,
                                      responses=[{"json": response}])
                self.assertNotEqual(result.returncode, 0)
                report = json.loads(result.stdout)
                self.assertIn("closing issue mismatch", report["error"])
                self.assertEqual(report["recognized_closing_issues"], [REPO + f"#{n}" for n in observed])
                self.assertFalse(any(call[:2] == ["pr", "merge"] for call in self.calls()))

    def test_qualification_reloads_scope_conversation_and_configured_readiness(self):
        result = self.run_cli("qualify", "--issue", "71", responses=[{"json": delivery_issue()}])
        self.assertEqual(result.returncode, 0, result.stderr)
        baseline = self.work / "qualified.json"
        baseline.write_text(result.stdout)
        for field, value in [("state", "CLOSED"), ("body", "Different acceptance"),
                             ("title", "Different objective"), ("labels", connection([])),
                             ("comments", connection([]))]:
            with self.subTest(field=field):
                changed = delivery_issue()
                changed["data"]["repository"]["issue"][field] = value
                result = self.run_cli("qualify", "--issue", "71", "--baseline", str(baseline),
                                      responses=[{"json": changed}])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("qualification exception", json.loads(result.stdout)["error"])
                self.assertTrue(all(call[:2] == ["api", "graphql"] for call in self.calls()))
        result = self.run_cli("qualify", "--issue", "71", "--baseline", str(baseline),
                              responses=[{"json": delivery_issue()}])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_prerequisite_merge_requalifies_before_allowing_implementation_to_resume(self):
        qualification = self.run_cli("qualify", "--issue", "71", responses=[{"json": delivery_issue()}])
        self.assertEqual(qualification.returncode, 0, qualification.stderr)
        baseline = self.work / "qualified.json"
        baseline.write_text(qualification.stdout)
        for lost_readiness in (False, True):
            with self.subTest(lost_readiness=lost_readiness):
                after = delivery_issue()
                if lost_readiness:
                    after["data"]["repository"]["issue"]["state"] = "CLOSED"
                result = self.run_cli("merge", "--pr", "80", "--head", HEAD, "--expect-none",
                                      "--qualification", str(baseline), responses=[
                                          {"json": pull_request()}, {"json": delivery_issue()},
                                          {"raw": "merged"}, {"json": merged()}, {"json": after}])
                self.assertEqual(result.returncode, 1 if lost_readiness else 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["merge_status"], "merged")
                self.assertEqual(report["integration_commit"], "b" * 40)
                if lost_readiness:
                    self.assertIn("qualification exception", report["error"])
                else:
                    self.assertEqual(report["outcome"], "passed")
                writes = [call for call in self.calls() if call[:2] != ["api", "graphql"]
                          and call[:2] != ["pr", "view"]]
                self.assertEqual(writes, [["pr", "merge", "80", "--repo", REPO,
                                          "--squash", "--match-head-commit", HEAD]])

    def test_unavailable_incomplete_wrong_repository_and_stale_data_fail_closed(self):
        responses = [{"exit": 1, "raw": "API unavailable"}, {"raw": "not JSON"},
                     {"json": {"errors": [{"message": "partial response"}], "data": None}}]
        for field, value in [("headRefOid", "c" * 40), ("state", "CLOSED"), ("baseRefName", "other"),
                             ("closingIssuesReferences", None),
                             ("closingIssuesReferences", {"nodes": [], "totalCount": 0}),
                             ("closingIssuesReferences", {"nodes": [], "totalCount": 1,
                                                          "pageInfo": {"hasNextPage": False}}),
                             ("closingIssuesReferences", {"nodes": [], "totalCount": 0,
                                                          "pageInfo": {"hasNextPage": True}})]:
            data = pull_request([71])
            data["data"]["repository"]["pullRequest"][field] = value
            responses.append({"json": data})
        wrong_repo = pull_request([71])
        wrong_repo["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["repository"]["nameWithOwner"] = "other/repository"
        responses.append({"json": wrong_repo})
        for response in responses:
            with self.subTest(response=response):
                result = self.run_cli("merge", "--pr", "80", "--head", HEAD, "--expect", REPO + "#71",
                                      responses=[response])
                self.assertNotEqual(result.returncode, 0)
                report = json.loads(result.stdout)
                self.assertEqual(report["outcome"], "failed")
                self.assertEqual(report["expected_closing_issues"], [REPO + "#71"])
                self.assertIn("error", report)
                self.assertTrue(all(call[:2] == ["api", "graphql"] for call in self.calls()))

    def test_prerequisite_cannot_merge_without_unchanged_qualification(self):
        qualification = self.run_cli("qualify", "--issue", "71", responses=[{"json": delivery_issue()}])
        baseline = self.work / "qualified.json"
        baseline.write_text(qualification.stdout)
        changed = delivery_issue()
        changed["data"]["repository"]["issue"]["labels"] = connection([])
        for flags, response in [([], []), (["--qualification", str(baseline)], [{"json": changed}])]:
            with self.subTest(flags=flags):
                result = self.run_cli("merge", "--pr", "80", "--head", HEAD, "--expect-none", *flags,
                                      responses=[{"json": pull_request()}, *response])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("qualification exception", json.loads(result.stdout)["error"])
                self.assertTrue(all(call[:2] == ["api", "graphql"] for call in self.calls()))

    def test_explicit_expectations_and_full_candidate_are_required(self):
        for flags in [[], ["--expect-none", "--expect", REPO + "#71"],
                      ["--expect", "other/repo#71"], ["--expect", "71"]]:
            with self.subTest(flags=flags):
                result = self.run_cli("preflight", "--pr", "80", "--head", HEAD, *flags, responses=[])
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])
        result = self.run_cli("preflight", "--pr", "80", "--head", "aaaaaaa", "--expect-none", responses=[])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_queued_or_failed_merge_never_reports_completed_integration(self):
        for responses in [[{"exit": 1, "raw": "protected merge rejected"}],
                          [{"raw": "queued"}, {"json": {"state": "OPEN", "headRefOid": HEAD, "mergeCommit": None}}],
                          [{"raw": "merged"}, {"json": {**merged(), "headRefOid": "c" * 40}}],
                          [{"raw": "merged"}, {"json": {**merged(), "mergeCommit": None}}]]:
            with self.subTest(responses=responses):
                result = self.run_cli("merge", "--pr", "80", "--head", HEAD, "--expect", REPO + "#71",
                                      responses=[{"json": pull_request([71])}, *responses])
                self.assertNotEqual(result.returncode, 0)
                report = json.loads(result.stdout)
                self.assertNotEqual(report["merge_status"], "merged")
                self.assertNotIn("integration_commit", report)

    def test_qualification_uses_the_consumer_mapping_and_rejects_incomplete_conversations(self):
        contract = self.project / "docs/agents/triage-labels.md"
        contract.write_text(contract.read_text().replace("`status:approved`", "`status:ready`"))
        result = self.run_cli("qualify", "--issue", "71", responses=[{"json": delivery_issue()}])
        self.assertNotEqual(result.returncode, 0)
        ready = delivery_issue()
        ready["data"]["repository"]["issue"]["labels"] = connection([{"name": "status:ready"}])
        result = self.run_cli("qualify", "--issue", "71", responses=[{"json": ready}])
        self.assertEqual(result.returncode, 0, result.stdout)
        baseline = self.work / "qualified.json"
        baseline.write_text(result.stdout)
        contract.write_text(contract.read_text() + "\nChanged readiness policy.\n")
        result = self.run_cli("qualify", "--issue", "71", "--baseline", str(baseline), responses=[{"json": ready}])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("readiness_contract_sha256", json.loads(result.stdout)["error"])
        for comments in [None, {"nodes": [], "totalCount": 1, "pageInfo": {"hasNextPage": True}},
                         connection([{"id": "comment-1"}])]:
            with self.subTest(comments=comments):
                ready["data"]["repository"]["issue"]["comments"] = comments
                result = self.run_cli("qualify", "--issue", "71", responses=[{"json": ready}])
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["outcome"], "failed")
        contract.write_text("No configured mapping\n")
        result = self.run_cli("qualify", "--issue", "71", responses=[])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
