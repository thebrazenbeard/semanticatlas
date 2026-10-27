"""Atomic view/db publication contracts for manifest-aware consumers."""
from __future__ import annotations
import importlib.util
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_atomic_builder", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

N="NODE-11111111-1111-4111-8111-111111111111"
A="ADJ-22222222-2222-4222-8222-222222222222"

def source(root, label="A"):
    folder = root/"atlas"/"nodes"; folder.mkdir(parents=True,exist_ok=True)
    (folder/"node.json").write_text(json.dumps({"id":N,"object_type":"node","primary_label":label}),encoding="utf8")
    adjudications=root/"atlas"/"adjudications"; adjudications.mkdir(parents=True,exist_ok=True)
    (adjudications/"adjudication.json").write_text(json.dumps({
        "id":A,"object_type":"adjudication","subject_id":N,
        "decision":"ACCEPT","authority_scope":"CURRENT_CANON",
        "supersedes_adjudication_ids":[]
    }),encoding="utf8")

class CommittedBundleTests(unittest.TestCase):
    def test_reader_picks_single_verified_generation(self):
        with TemporaryDirectory() as name:
            root=Path(name);source(root)
            out=root/"out"
            builder.build(root,out)
            first=builder.load_committed_bundle(out)
            self.assertEqual(first["view"]["active_subject_ids"], [N])
            with closing(sqlite3.connect(first["database"])) as db:
                self.assertEqual(json.loads(db.execute("SELECT json FROM current_subject WHERE id=?",(N,)).fetchone()[0])["primary_label"],"A")
            source(root,"B");builder.build(root,out)
            second=builder.load_committed_bundle(out)
            with closing(sqlite3.connect(second["database"])) as db:
                self.assertEqual(json.loads(db.execute("SELECT json FROM current_subject WHERE id=?",(N,)).fetchone()[0])["primary_label"],"B")
            self.assertNotEqual(first["generation"],second["generation"])

    def test_legacy_second_replace_failure_does_not_commit_mixed_generation(self):
        with TemporaryDirectory() as name:
            root=Path(name);source(root)
            out=root/"out";builder.build(root,out)
            old=builder.load_committed_bundle(out)["generation"]
            source(root,"B")
            actual=builder.os.replace
            def injected(src,dst):
                if Path(dst).name=="current_view.json":
                    raise OSError("injected legacy-export failure")
                return actual(src,dst)
            with patch.object(builder.os,"replace",side_effect=injected):
                with self.assertRaisesRegex(OSError,"injected"):
                    builder.build(root,out)
            self.assertEqual(builder.load_committed_bundle(out)["generation"],old)

    def test_rejects_malformed_manifest_and_tampered_generation(self):
        with TemporaryDirectory() as name:
            root=Path(name);source(root)
            out=root/"out";builder.build(root,out)
            manifest=out/"current_bundle.json"
            payload=json.loads(manifest.read_text())
            location=out/".semanticatlas-generations"/payload["generation"]/"current_view.json"
            location.write_text("{}")
            with self.assertRaisesRegex(ValueError,"digest"):
                builder.load_committed_bundle(out)
            payload["generation"]="../escape"
            manifest.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError,"generation"):
                builder.load_committed_bundle(out)

if __name__ == "__main__":
    unittest.main()

