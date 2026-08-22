import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


splitter = load_module("build/split_source_ledger.py", "splitter")
builder = load_module("build/build_current_view.py", "builder")


class ArchitectureTests(unittest.TestCase):
    def test_source_split_is_deterministic_and_nonpromoting(self):
        record = {
            "source_id": "SRC-LEGACY-1",
            "title": "Example",
            "source_class": "TRANSCRIPT_EXPORT",
            "embedded_time_start": "2026-01-01",
            "embedded_time_end": "2026-01-01",
            "retrieval_surface": "File Library",
            "current_authority": "HISTORICAL_REFERENCE_ONLY",
            "key_topics": ["x"],
            "limitations": "old judgment",
        }
        neutral_a, judgment_a = splitter.split_record(record)
        neutral_b, judgment_b = splitter.split_record(record)
        self.assertEqual(neutral_a, neutral_b)
        self.assertEqual(judgment_a, judgment_b)
        self.assertTrue(neutral_a["id"].startswith("SRCI-"))
        self.assertNotIn("current_authority", neutral_a)
        self.assertNotIn("key_topics", neutral_a)
        self.assertTrue(judgment_a["research_only"])

    def test_empty_derived_build_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = pathlib.Path(tempdir)
            (root / "atlas").mkdir()
            out_a = root / "build-a"
            out_b = root / "build-b"
            hashes_a = builder.build(root, out_a)
            hashes_b = builder.build(root, out_b)
            self.assertEqual(hashes_a, hashes_b)
            self.assertEqual(
                (out_a / "current_view.json").read_bytes(),
                (out_b / "current_view.json").read_bytes(),
            )
            self.assertEqual(
                (out_a / "semantic_index.sqlite").read_bytes(),
                (out_b / "semantic_index.sqlite").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
