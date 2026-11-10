"""Offline regression tests; all writes are confined to temporary directories."""
import contextlib
import gzip
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import merge_partial_legacy_proximity as merger
import run_legacy_proximity_union as runner

ROOT = Path(__file__).resolve().parent
ARCHIVE = Path("stansfield_pilot/legacy_union_proximity_run")
QUERY = Path("stansfield_pilot/queries/legacy_union_proximity_wildcards.oql")


class ProximityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.out = self.root / ARCHIVE
        shutil.copytree(ROOT / ARCHIVE, self.out)
        for path in [QUERY, Path("run_legacy_proximity_union.py"),
                     Path("stansfield_pilot/reference_retrieval.csv"),
                     Path("stansfield_pilot/cursor_study_2026-10-04/"
                          "legacy_union_normalized/default/ordered_ids.json")]:
            destination = self.root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)
        for name, value in [("ROOT", self.root), ("INPUT", self.root / QUERY),
                            ("OUT", self.out), ("API_KEY", "offline-test-key"),
                            ("REQUEST_COUNT", 0), ("LOG", []), ("RUN_START", runner.RUN_START)]:
            patch = mock.patch.object(runner, name, value)
            patch.start()
            self.addCleanup(patch.stop)
        network = mock.patch.object(runner, "urlopen", side_effect=AssertionError("Network forbidden"))
        network.start()
        self.addCleanup(network.stop)

    def read(self, name):
        return json.loads((self.out / name).read_text())

    def write(self, name, value):
        (self.out / name).write_text(json.dumps(value))

    def run_with(self, response):
        with mock.patch.object(runner, "call", side_effect=response), contextlib.redirect_stdout(io.StringIO()):
            return runner.main()

    def assert_no_derived_results(self):
        for name in (*merger.PRODUCTS, "merged_work_ids.json.gz", "merged_work_ids.txt",
                     "legacy_comparison.json", "reference_recall.json"):
            self.assertFalse((self.out / name).exists(), name)

    def test_archived_counts_and_reference_recovery_reproduce(self):
        original = self.read("partial_merge_summary.json")
        result = merger.merge(self.root)
        for key in ["all_observed_unique_work_ids", "original_legacy_unique",
                    "observed_overlap_with_original_legacy", "observed_new_only",
                    "original_legacy_not_yet_observed", "branch_counts", "reference_recovery"]:
            self.assertEqual(result[key], original[key], key)
        self.assertEqual(result["all_observed_unique_work_ids"], 10079)
        self.assertEqual(result["status"], "PARTIAL_NOT_COMPLETE")

    def test_zero_result_failures_replace_old_files_and_merge_as_lower_bounds(self):
        self.assertEqual(self.run_with(RuntimeError("simulated credit exhaustion")), 1)
        self.assert_no_derived_results()
        stats = self.read("branches_summary.json")
        self.assertEqual(len(stats), 9)
        for row in stats:
            self.assertEqual(row["status"], "failed")
            self.assertEqual(row["partial_unique"], 0)
            with gzip.open(self.out / f"branch_{row['line']:02d}_partial_ids.json.gz", "rt") as f:
                self.assertEqual(json.load(f), [])
        self.assertFalse(self.read("final_summary.json")["complete"])
        self.assertIsNone(self.read("final_summary.json")["union_unique"])
        result = merger.merge(self.root)
        self.assertEqual(result["all_observed_unique_work_ids"], 0)
        self.assertIn("9 of nine", result["meaning"])
        self.assertEqual(result["status"], "PARTIAL_NOT_COMPLETE")
        self.assertEqual((self.out / "partial_merged_work_ids.txt").read_text(), "")
        self.assertFalse(self.read("run_manifest.json")["no_api_key_used"])
        self.assertNotIn("offline-test-key", (self.out / "run_manifest.json").read_text())

    def test_incomplete_cli_exits_nonzero_and_preserves_audit(self):
        env = dict(os.environ, OPENALEX_API_KEY="offline-test-key", OPENALEX_MAX_REQUESTS="0")
        process = subprocess.run([sys.executable, str(self.root / "run_legacy_proximity_union.py")],
                                 env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(self.read("final_summary.json")["failed_branches"], list(range(1, 10)))
        self.assertEqual(self.read("request_log.json"), [])

    def test_missing_key_preserves_archive_without_requests(self):
        before = {path.name: path.read_bytes() for path in self.out.iterdir()}
        with mock.patch.object(runner, "API_KEY", ""), self.assertRaises(SystemExit):
            runner.main()
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.out.iterdir()})

    def test_interruption_removes_old_results_and_marks_new_run_incomplete(self):
        with self.assertRaises(KeyboardInterrupt):
            self.run_with(KeyboardInterrupt())
        self.assert_no_derived_results()
        self.assertFalse((self.out / "final_summary.json").exists())
        self.assertEqual(self.read("branches_summary.json"), [])
        self.assertFalse(self.read("execution_status.json")["complete"])
        with self.assertRaisesRegex(RuntimeError, "exactly once"):
            merger.merge(self.root)

    def test_complete_pagination_deduplicates_and_exits_successfully(self):
        def reply(endpoint, payload):
            first = payload["cursor"] == "*"
            return {"meta": {"count": 2, "next_cursor": "next" if first else None},
                    "results": [{"id": "https://openalex.org/" + work_id}
                                for work_id in (["W1"] if first else ["W1", "W2"])]}
        self.assertEqual(self.run_with(reply), 0)
        self.assertEqual(self.read("final_summary.json")["union_unique"], 2)
        self.assertTrue(self.read("final_summary.json")["complete"])
        for row in self.read("branches_summary.json"):
            self.assertEqual(row["duplicate_positions"], 1)
            self.assertEqual(row["total_unique"], 2)
        self.assertEqual(list(self.out.glob("*_partial_ids.json.gz")), [])
        for name in merger.PRODUCTS:
            self.assertFalse((self.out / name).exists())
        result = merger.merge(self.root)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertIn("all nine branches completed", result["meaning"])

    def test_repeated_cursor_and_count_mismatch_withhold_union(self):
        for scenario in ["repeated_cursor", "missing_ids", "changed_count"]:
            with self.subTest(scenario=scenario):
                def reply(endpoint, payload):
                    count = 3 if scenario == "changed_count" and payload["cursor"] != "*" else 2
                    cursor = "*" if scenario == "repeated_cursor" else (
                        "next" if scenario == "changed_count" and payload["cursor"] == "*" else None)
                    return {"meta": {"count": count, "next_cursor": cursor}, "results": [{"id": "W1"}]}
                self.assertEqual(self.run_with(reply), 1)
                self.assert_no_derived_results()
                self.assertFalse(self.read("final_summary.json")["complete"])

    def test_merger_rejects_stale_counts_and_invalidates_old_union(self):
        stats = self.read("branches_summary.json")
        stats[0]["partial_unique"] = 0
        self.write("branches_summary.json", stats)
        with self.assertRaisesRegex(RuntimeError, "saved ID count"):
            merger.merge(self.root)
        for name in merger.PRODUCTS:
            self.assertFalse((self.out / name).exists())

    def test_merger_requires_each_branch_once(self):
        stats = self.read("branches_summary.json")
        stats[-1] = stats[0]
        self.write("branches_summary.json", stats)
        with self.assertRaisesRegex(RuntimeError, "exactly once"):
            merger.merge(self.root)

    def test_merger_accepts_reordered_summary(self):
        self.write("branches_summary.json", list(reversed(self.read("branches_summary.json"))))
        self.assertEqual(merger.merge(self.root)["all_observed_unique_work_ids"], 10079)

    def test_merger_checks_query_provenance(self):
        manifest = self.read("run_manifest.json")
        manifest["input_sha256"] = "wrong"
        self.write("run_manifest.json", manifest)
        with self.assertRaisesRegex(RuntimeError, "manifest"):
            merger.merge(self.root)

    def test_merger_checks_branch_provenance(self):
        stats = self.read("branches_summary.json")
        stats[0]["query_sha256"] = "wrong"
        self.write("branches_summary.json", stats)
        with self.assertRaisesRegex(RuntimeError, "query hash"):
            merger.merge(self.root)

    def test_merger_checks_completed_api_count(self):
        stats = self.read("branches_summary.json")
        stats[3]["api_reported_count"] += 1
        self.write("branches_summary.json", stats)
        with self.assertRaisesRegex(RuntimeError, "API count"):
            merger.merge(self.root)


if __name__ == "__main__":
    unittest.main()
