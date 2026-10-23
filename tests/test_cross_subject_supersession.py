"""Reject unrelated adjudication supersession; don't silently erase other canon."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_subject_guard", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

NODE_A = "NODE-11111111-1111-4111-8111-111111111111"
NODE_B = "NODE-22222222-2222-4222-8222-222222222222"
ADJ_A = "ADJ-33333333-3333-4333-8333-333333333333"
ADJ_B = "ADJ-44444444-4444-4444-8444-444444444444"


def make_adjudication(id_, subject, predecessors=()):
    return dict(schema_version="0.1", object_type="adjudication", id=id_,
                subject_id=subject, decision="ACCEPT", authority_scope="CURRENT_CANON",
                decided_by="VERA", rationale="Synthetic test-only decision",
                evidence_ids=[], evidence_projection_ids=[],
                supersedes_adjudication_ids=list(predecessors))


def make_fixture(root, *, same_subject=False):
    for name in ("schemas", "vocabulary", "atlas/nodes", "atlas/adjudications"):
        (root/name).mkdir(parents=True, exist_ok=True)
    for name in ("schemas/semantic_atlas_v0.1.schema.json", "vocabulary/relation_types_v0.1.json"):
        (root/name).write_bytes((ROOT/name).read_bytes())
    nodes = [{"schema_version":"0.1","object_type":"node","id":subject,
              "primary_label":label,"node_kind":"TEST"} for subject,label in
             [(NODE_A,"A"),(NODE_B,"B")]]
    for i,node in enumerate(nodes):
        (root/"atlas"/"nodes"/f"{i}.json").write_text(json.dumps(node),encoding="utf-8")
    first=make_adjudication(ADJ_A,NODE_A)
    second=make_adjudication(ADJ_B,NODE_A if same_subject else NODE_B,(ADJ_A,))
    for i,adj in enumerate((first,second)):
        (root/"atlas"/"adjudications"/f"{i}.json").write_text(json.dumps(adj),encoding="utf-8")
    return first,second


class CrossSubjectAdjudicationTests(unittest.TestCase):
    def test_builder_rejects_cross_subject_supersession(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            make_fixture(root)
            with self.assertRaisesRegex(ValueError, "cross-subject adjudication supersession"):
                builder.build(root,root/"out")

    def test_validator_rejects_cross_subject_supersession(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            make_fixture(root)
            p=subprocess.run([sys.executable,str(ROOT/"build"/"validate_atlas.py"),
                              "--root",str(root)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertIn("cross-subject adjudication supersession",p.stdout)

    def test_same_subject_supersession_remains_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            make_fixture(root,same_subject=True)
            p=subprocess.run([sys.executable,str(ROOT/"build"/"validate_atlas.py"),
                              "--root",str(root)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            active=builder.active_adjudications(builder.load_objects(root))
            self.assertEqual([o["id"] for o in active],[ADJ_B])


if __name__ == "__main__":
    unittest.main()
