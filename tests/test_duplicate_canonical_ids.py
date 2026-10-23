"""The derived current-view builder must not silently resolve conflicting IDs.

Independent source-level invariant: calling build_current_view directly cannot
override an earlier canonical JSON object, even when validate_atlas is skipped.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_current_builder_duplicate_guard", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DuplicateCanonicalObjectTests(unittest.TestCase):
    def test_duplicate_ids_in_same_directory_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            nodes = root / "atlas" / "nodes"
            nodes.mkdir(parents=True)
            duplicate_id = "NODE-11111111-1111-4111-8111-111111111111"
            (nodes / "a.json").write_text(json.dumps({"id": duplicate_id, "object_type": "node", "primary_label": "Original"}))
            (nodes / "b.json").write_text(json.dumps({"id": duplicate_id, "object_type": "node", "primary_label": "Substituted"}))
            with self.assertRaisesRegex(ValueError, "duplicate canonical object id"):
                builder.build(root, root / "derived")

    def test_duplicate_ids_across_directories_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for directory in ("sources", "nodes"):
                (root / "atlas" / directory).mkdir(parents=True)
            duplicate_id = "NODE-22222222-2222-4222-8222-222222222222"
            (root / "atlas" / "sources" / "one.json").write_text(json.dumps({"id": duplicate_id, "object_type": "source_instance"}))
            (root / "atlas" / "nodes" / "two.json").write_text(json.dumps({"id": duplicate_id, "object_type": "node"}))
            with self.assertRaisesRegex(ValueError, "duplicate canonical object id"):
                builder.load_objects(root)

    def test_unique_objects_still_build(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            nodes = root / "atlas" / "nodes"
            nodes.mkdir(parents=True)
            node_id = "NODE-33333333-3333-4333-8333-333333333333"
            (nodes / "one.json").write_text(json.dumps({"id": node_id, "object_type": "node", "primary_label": "Unique"}))
            objects = builder.load_objects(root)
            self.assertEqual(objects[node_id]["primary_label"], "Unique")
            result = builder.build(root, root / "derived")
            self.assertEqual(len(result["current_view_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
