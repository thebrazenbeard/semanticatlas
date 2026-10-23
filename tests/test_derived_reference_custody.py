"""Keep derived materialization consistent with the canonical validator's ref domain."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_ref_guard", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

NODE="NODE-11111111-1111-4111-8111-111111111111"
UNKNOWN="NODE-22222222-2222-4222-8222-222222222222"
RTYPE="RTYPE-33333333-3333-4333-8333-333333333333"
ADJ="ADJ-44444444-4444-4444-8444-444444444444"


def put(root, directory, name, payload):
    path=root/"atlas"/directory/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload),encoding="utf-8")


def adjudication(subject):
    return {"id":ADJ,"object_type":"adjudication","subject_id":subject,
            "decision":"ACCEPT","authority_scope":"CURRENT_CANON",
            "supersedes_adjudication_ids":[]}


class DirectBuilderReferenceCustodyTests(unittest.TestCase):
    def test_missing_active_subject_is_rejected_not_silently_omitted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            put(root,"adjudications","one.json",adjudication(UNKNOWN))
            with self.assertRaisesRegex(ValueError,"unresolved active adjudication subject"):
                builder.build(root,root/"out")

    def test_legitimate_vocabulary_subject_is_indexed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            vocab=root/"vocabulary"/"relation_types_v0.1.json"
            vocab.parent.mkdir(parents=True)
            vocab.write_text(json.dumps({"relation_types":[
                {"schema_version":"0.1","id":RTYPE,"object_type":"relation_type",
                 "code":"REL_TEST","description":"Synthetic test relationship",
                 "family":"LIFECYCLE_LINEAGE","symmetry":"ASYMMETRIC",
                 "transitivity":"UNKNOWN","current_canon_eligible":True}]}))
            put(root,"adjudications","one.json",adjudication(RTYPE))
            builder.build(root,root/"out")
            db=sqlite3.connect(root/"out"/"semantic_index.sqlite")
            try:
                indexed=db.execute("SELECT id,object_type FROM current_subject").fetchall()
            finally:
                db.close()
            self.assertEqual(indexed,[(RTYPE,"relation_type")])

    def test_regular_node_subject_still_builds(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            put(root,"nodes","one.json",{"id":NODE,"object_type":"node","primary_label":"Test"})
            put(root,"adjudications","one.json",adjudication(NODE))
            result=builder.build(root,root/"out")
            self.assertEqual(len(result["current_view_sha256"]),64)
            view=json.loads((root/"out"/"current_view.json").read_text())
            self.assertEqual(view["active_subject_ids"],[NODE])


if __name__ == "__main__":
    unittest.main()
