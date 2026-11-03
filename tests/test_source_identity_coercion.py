"""Synthetic source IDs must not be coerced into false provenance identity."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "atlas_source_identity", ROOT / "build" / "split_source_ledger.py"
)
splitter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(splitter)


def source(source_id: object) -> dict:
    return {
        "source_id": source_id,
        "title": "synthetic evidence only",
        "source_class": "SYNTHETIC",
        "embedded_time_start": None,
        "embedded_time_end": None,
        "retrieval_surface": "synthetic fixture",
    }


class SourceIdentityTests(unittest.TestCase):
    def test_nonstring_id_cannot_alias_exact_text_identity(self):
        exact, _ = splitter.split_record(source("1"))
        self.assertEqual(exact["legacy_source_id"], "1")
        for coerced in (1, True, {"id": "1"}, ["1"], None):
            with self.subTest(coerced=coerced):
                with self.assertRaisesRegex(ValueError, "source_id"):
                    splitter.split_record(source(coerced))

    def test_blank_or_control_source_id_fails_closed(self):
        for invalid in ("", "   ", "message\nspoof", "source\x00id"):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "source_id"):
                    splitter.split_record(source(invalid))

    def test_canonical_source_api_refuses_untyped_id(self):
        with self.assertRaisesRegex(ValueError, "source_id"):
            splitter.canonical_source_id(1)
        self.assertEqual(
            splitter.canonical_source_id("SRC-1"),
            splitter.canonical_source_id("SRC-1"),
        )


if __name__ == "__main__":
    unittest.main()
