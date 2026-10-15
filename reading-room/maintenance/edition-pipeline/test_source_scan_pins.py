#!/usr/bin/env python3
"""Portable source-scan pin regressions; synthetic fixtures, stdlib only."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("edition_pipeline", Path(__file__).with_name("edition_pipeline.py"))
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class SourceScanPinTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="source-scan-pins-")
        root = Path(self.tmp.name)
        self.text = root / "tale.txt"
        self.text.write_bytes(b"Once a reader met a fox. The end.\n")
        self.scan = root / "scan.pdf"
        self.scan.write_bytes(b"%PDF-1.4\nSynthetic source scan fixture.\n")
        report = root / "review.json"
        report.write_text(json.dumps({"synthetic_test_fixture": True}), encoding="utf-8")
        text_pin = pipeline.pin(self.text)
        scan_pin = pipeline.pin(self.scan)
        source = "https://example.invalid/synthetic-tale"
        self.imp = {
            "schema_version": 1,
            "catalog": {
                "id": "synthetic-tale", "title": "Synthetic Tale", "author": "Test Author",
                "edition": "Complete synthetic test edition", "rights": "CC0 synthetic test fixture",
                "available": True, "source": source, "path": "books/synthetic-tale.txt", **text_pin,
                "source_scan": {"path": "books/synthetic-tale-scan.pdf", **scan_pin},
            },
            "spec": {
                "builder": "anchored", "sha256": text_pin["sha256"], "primarySectionCount": 1,
                "primaryOpening": "Once a reader", "defaultSectionId": "story",
                "sections": [{"id": "story", "kind": "primary"}],
            },
            "verification": {
                "status": "verified_complete_digital_edition", "rights_scope": "explicit_license",
                "source_catalog": source, "report": str(report),
            },
            "runtime_assets": [
                {"target": "books/synthetic-tale.txt", "source": str(self.text), "url": source + ".txt", **text_pin},
                {"target": "books/synthetic-tale-scan.pdf", "source": str(self.scan), "url": source + ".pdf", **scan_pin},
            ],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def verify_unchanged(self):
        before = copy.deepcopy(self.imp)
        text_bytes, scan_bytes = self.text.read_bytes(), self.scan.read_bytes()
        try:
            return pipeline.verify_import(self.imp)
        finally:
            self.assertEqual(self.imp, before, "Admission modified import metadata")
            self.assertEqual(self.text.read_bytes(), text_bytes, "Admission modified reading source")
            self.assertEqual(self.scan.read_bytes(), scan_bytes, "Admission modified scan source")

    def test_valid_source_scan_pins_are_accepted(self):
        self.assertIs(self.verify_unchanged(), self.imp)

    def test_catalog_scan_sha256_mismatch_is_rejected(self):
        self.imp["catalog"]["source_scan"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(pipeline.GateError, "Preserved source scan hash/byte mismatch"):
            self.verify_unchanged()

    def test_catalog_scan_byte_count_mismatch_is_rejected(self):
        self.imp["catalog"]["source_scan"]["bytes"] += 1
        with self.assertRaisesRegex(pipeline.GateError, "Preserved source scan hash/byte mismatch"):
            self.verify_unchanged()

    def test_mutated_source_scan_bytes_are_rejected(self):
        original = self.scan.read_bytes()
        self.scan.write_bytes(original.replace(b"Synthetic", b"Tampered!"))
        self.assertEqual(len(self.scan.read_bytes()), len(original))
        with self.assertRaisesRegex(pipeline.GateError, "Pinned source books/synthetic-tale-scan.pdf hash/byte mismatch"):
            self.verify_unchanged()

    def test_legacy_import_without_scan_remains_valid(self):
        del self.imp["catalog"]["source_scan"]
        self.imp["runtime_assets"].pop()
        self.assertIs(self.verify_unchanged(), self.imp)

    def test_matching_catalog_and_asset_pins_still_require_actual_scan_bytes(self):
        false_pin = {"bytes": self.scan.stat().st_size, "sha256": hashlib.sha256(b"different bytes").hexdigest()}
        self.imp["catalog"]["source_scan"].update(false_pin)
        self.imp["runtime_assets"][1].update(false_pin)
        with self.assertRaisesRegex(pipeline.GateError, "Pinned source books/synthetic-tale-scan.pdf hash/byte mismatch"):
            self.verify_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
