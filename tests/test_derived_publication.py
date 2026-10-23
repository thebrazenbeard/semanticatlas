"""Crash/IO-failure controls for the two derived output artifacts.

Only isolated synthetic canon and temporary output directories are used.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_publication_guard", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
A = "NODE-11111111-1111-4111-8111-111111111111"
B = "NODE-22222222-2222-4222-8222-222222222222"

def add_subject(root, subject):
    target = root / "atlas" / "nodes"
    target.mkdir(parents=True, exist_ok=True)
    (target / (subject + ".json")).write_text(json.dumps({
        "id":subject,"object_type":"node","primary_label":subject,
        "schema_version":"0.1","node_kind":"TEST",
    }))
    adjudications = root / "atlas" / "adjudications"
    adjudications.mkdir(parents=True, exist_ok=True)
    (adjudications / (subject + ".json")).write_text(json.dumps({
        "id":"ADJ-" + subject.split("-",1)[1],
        "object_type":"adjudication","subject_id":subject,
        "authority_scope":"CURRENT_CANON","decision":"ACCEPT",
        "supersedes_adjudication_ids":[],
    }))

class DerivedPublicationTests(unittest.TestCase):
    def test_failed_rebuild_preserves_previous_json_and_index(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root/"out"
            add_subject(root,A)
            builder.build(root,out)
            old_json=(out/"current_view.json").read_bytes()
            old_db=(out/"semantic_index.sqlite").read_bytes()
            add_subject(root,B)
            with patch.object(builder.sqlite3,"connect",side_effect=sqlite3.OperationalError("injected-open-error")):
                with self.assertRaisesRegex(sqlite3.OperationalError,"injected-open-error"):
                    builder.build(root,out)
            self.assertEqual((out/"current_view.json").read_bytes(),old_json)
            self.assertEqual((out/"semantic_index.sqlite").read_bytes(),old_db)

    def test_failed_first_build_does_not_publish_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root/"out"
            add_subject(root,A)
            with patch.object(builder.sqlite3,"connect",side_effect=sqlite3.OperationalError("injected-open-error")):
                with self.assertRaises(sqlite3.OperationalError):
                    builder.build(root,out)
            self.assertFalse((out/"current_view.json").exists())
            self.assertFalse((out/"semantic_index.sqlite").exists())

    def test_successful_rebuild_changes_pair_in_step(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root/"out"
            add_subject(root,A)
            old=builder.build(root,out)
            add_subject(root,B)
            new=builder.build(root,out)
            self.assertNotEqual(old["current_view_sha256"],new["current_view_sha256"])
            self.assertNotEqual(old["semantic_index_sha256"],new["semantic_index_sha256"])
            view=json.loads((out/"current_view.json").read_text())
            self.assertEqual(set(view["active_subject_ids"]),{A,B})
            con=sqlite3.connect(out/"semantic_index.sqlite")
            try:
                n=con.execute("SELECT COUNT(*) FROM current_subject").fetchone()[0]
            finally:
                con.close()
            self.assertEqual(n,2)

if __name__ == "__main__":
    unittest.main()
