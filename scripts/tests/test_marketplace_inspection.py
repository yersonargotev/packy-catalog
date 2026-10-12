"""Offline acceptance tests through the marketplace inspector's public CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "inspect_marketplace.py"


class MarketplaceInspectionTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name) / "checkout"
        (self.root / ".claude-plugin").mkdir(parents=True)

    def manifest(self, entries, **metadata):
        (self.root / ".claude-plugin/marketplace.json").write_text(
            json.dumps({**metadata, "plugins": entries}), encoding="utf-8")

    def run_cli(self, *args, status=0):
        result = subprocess.run([sys.executable, "-B", str(CLI), str(self.root), *args],
                                capture_output=True)
        self.assertEqual(result.returncode, status, result.stderr or result.stdout)
        self.assertLessEqual(len(result.stdout) + len(result.stderr), 16384)
        self.assertEqual(result.stderr, b"")
        return json.loads(result.stdout)

    def test_large_marketplace_counts_and_bounded_default(self):
        (self.root / "local").mkdir()
        (self.root / "file").write_text("not a directory")
        entries = [
            {"name": "local", "source": "./local"},
            {"name": "missing", "source": "./missing"},
            {"name": "file", "source": "./file"},
            {"name": "unsupported", "source": {"source": "github"}},
            {"name": "malformed", "source": {"source": "url", "url": ""}},
            {"name": "escape", "source": "../outside"},
            {"name": "subdir", "source": {"source": "git-subdir", "url": "https://example.test/r", "path": "plugin"}},
        ]
        entries += [{"name": f"remote-{i}", "source": {"source": "url", "url": "https://example.test/r", "path": "optional"}}
                    for i in range(2277)]
        self.manifest(entries, name="fixture")
        output = self.run_cli()
        self.assertEqual(output["total_entries"], 2284)
        self.assertEqual(output["counts"], {"local_present": 1, "local_absent": 1,
            "external": 2278, "unsupported": 1, "malformed": 2, "unsafe": 1})
        self.assertEqual(output["entries"]["total"], 2284)
        self.assertEqual(len(output["entries"]["items"]), 20)
        self.assertEqual(output["entries"]["omitted"], 2264)

    def test_exact_lookup_preserves_source_and_rejects_ambiguity(self):
        source = {"source": "git-subdir", "url": "https://example.test/r", "path": "sub", "extra": [1, 2]}
        self.manifest([{"name": "chosen", "source": source},
                       {"name": "duplicate", "source": "./one"},
                       {"name": "duplicate", "source": "./two"}])
        output = self.run_cli("--entry", "chosen")
        self.assertEqual(json.loads(output["selected"]["source"]["json"]), source)
        self.assertFalse(output["selected"]["source"]["truncated"])
        self.assertEqual(output["selected"]["location"], "/plugins/0")
        self.assertIn("ambiguous", self.run_cli("--entry", "duplicate", status=1)["error"]["json"])
        self.assertIn("not found", self.run_cli("--entry", "Chosen", status=1)["error"]["json"])

    def test_inventory_is_deterministic_and_never_descends_symlinks(self):
        plugin = self.root / "plugin"
        plugin.mkdir()
        for i in range(140):
            (plugin / f"file-{i:03}.txt").write_text("data")
        outside = Path(self.scratch.name) / "outside"
        outside.mkdir()
        (outside / "secret").write_text("must not be read")
        (plugin / "aaa-link").symlink_to(outside, target_is_directory=True)
        self.manifest([{"name": "plugin", "source": "./plugin"}])
        output = self.run_cli("--entry", "plugin", "--inventory")
        inventory = output["inventory"]
        self.assertEqual(inventory["total"], 141)
        self.assertEqual(inventory["omitted"], 41)
        self.assertEqual(len(inventory["items"]), 100)
        self.assertEqual(inventory["items"][0]["kind"], "symlink")
        self.assertEqual(json.loads(inventory["items"][0]["path"]["json"]), "plugin/aaa-link")
        self.assertEqual(output, self.run_cli("--entry", "plugin", "--inventory"))
        self.assertNotIn("secret", json.dumps(output))

    def test_huge_evidence_and_argument_errors_share_byte_budget(self):
        huge = "🦊\\\"" * 20000
        source = {"source": "url", "url": "https://example.test/" + huge, "extra": huge}
        self.manifest([{"name": huge, "source": source}] * 30, description=huge)
        output = self.run_cli()
        self.assertTrue(output["metadata"]["truncated"])
        self.assertTrue(output["entries"]["items"][0]["name"]["truncated"])
        self.assertEqual(output["entries"]["omitted"], 30 - len(output["entries"]["items"]))
        self.manifest([{"name": "chosen", "source": source}], description=huge)
        selected = self.run_cli("--entry", "chosen")["selected"]
        self.assertTrue(selected["source"]["truncated"])
        self.assertEqual(selected["location"], "/plugins/0")
        self.run_cli("--" + huge, status=2)

    def test_unsafe_sources_and_manifest_links_are_not_followed(self):
        outside = Path(self.scratch.name) / "outside"
        outside.mkdir()
        (outside / "plugin").mkdir()
        (self.root / "escape").symlink_to(outside, target_is_directory=True)
        (self.root / "internal").symlink_to(self.root / ".claude-plugin", target_is_directory=True)
        sources = [str(outside), "../outside", "local/../elsewhere", "C:\\outside", "\\outside", "escape/plugin", "internal", "bad\x00path"]
        self.manifest([{"name": str(i), "source": source} for i, source in enumerate(sources)])
        self.assertEqual(self.run_cli()["counts"]["unsafe"], 8)
        self.run_cli("--entry", "5", "--inventory", status=1)
        manifest = self.root / ".claude-plugin/marketplace.json"
        manifest.unlink()
        manifest.symlink_to(outside / "missing")
        self.assertIn("symlink", self.run_cli(status=1)["error"]["json"])
        manifest.unlink()
        manifest.parent.rmdir()
        manifest.parent.symlink_to(outside, target_is_directory=True)
        self.assertIn("symlink", self.run_cli(status=1)["error"]["json"])

    def test_invalid_top_level_and_nonstandard_json_fail_clearly(self):
        manifest = self.root / ".claude-plugin/marketplace.json"
        for raw in (b"{broken", b"[]", b'{"plugins": {}}', b'{"plugins": [], "bad": NaN}', b"\xff"):
            with self.subTest(raw=raw):
                manifest.write_bytes(raw)
                self.assertIn("error", self.run_cli(status=1))
        manifest.unlink()
        self.run_cli(status=1)

    def test_inventory_long_paths_has_visible_omissions_and_leaves_input_unchanged(self):
        plugin = self.root / "plugin"
        plugin.mkdir()
        for i in range(150):
            (plugin / (f"{i:03}-" + "x" * 200)).write_text("inert data")
        marker = self.root / "executed"
        (plugin / "hook.sh").write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        (plugin / "hook.sh").chmod(0o755)
        self.manifest([{"name": "plugin", "source": "./plugin", "hooks": "hook.sh"}])

        def snapshot():
            return {str(path.relative_to(self.root)): (path.lstat().st_mode,
                    path.read_bytes() if path.is_file() else None)
                    for path in self.root.rglob("*")}

        before = snapshot()
        inventory = self.run_cli("--entry", "plugin", "--inventory")["inventory"]
        self.assertEqual(inventory["total"], 151)
        self.assertGreater(inventory["omitted"], 51)
        self.assertEqual(inventory["omitted"], 151 - len(inventory["items"]))
        self.assertEqual(snapshot(), before)
        self.assertFalse(marker.exists())

    def test_malformed_and_unsupported_entries_remain_visible(self):
        self.manifest([None, [], {}, {"name": ""}, {"name": "no-source"},
                       {"name": "wrong-type", "source": 5},
                       {"name": "unknown", "source": {"source": "other", "extra": True}},
                       {"name": "missing-path", "source": {"source": "git-subdir", "url": "x"}}])
        output = self.run_cli()
        self.assertEqual(output["counts"]["malformed"], 7)
        self.assertEqual(output["counts"]["unsupported"], 1)
        self.assertEqual(output["entries"]["omitted"], 0)


if __name__ == "__main__":
    unittest.main()
