"""Direct derived builds must reject conflicting or malformed canon authority."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_chain_guard", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

NODE = "NODE-11111111-1111-4111-8111-111111111111"
FIRST = "ADJ-22222222-2222-4222-8222-222222222222"
SECOND = "ADJ-33333333-3333-4333-8333-333333333333"


def adjudication(identifier: str, supersedes=(), decision="ACCEPT"):
    return {
        "id": identifier,
        "object_type": "adjudication",
        "subject_id": NODE,
        "decision": decision,
        "authority_scope": "CURRENT_CANON",
        "supersedes_adjudication_ids": list(supersedes),
    }


def root_with_adjudications(root: Path, *items):
    node_dir = root / "atlas" / "nodes"
    adjudication_dir = root / "atlas" / "adjudications"
    node_dir.mkdir(parents=True)
    adjudication_dir.mkdir(parents=True)
    (node_dir / "node.json").write_text(
        json.dumps({"id": NODE, "object_type": "node", "primary_label": "Test"}),
        encoding="utf-8",
    )
    for number, obj in enumerate(items):
        (adjudication_dir / f"{number}.json").write_text(json.dumps(obj), encoding="utf-8")


class DerivedAdjudicationChainGuardTests(unittest.TestCase):
    def test_parallel_active_current_canon_decisions_fail_closed(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            root_with_adjudications(root, adjudication(FIRST), adjudication(SECOND))
            with self.assertRaisesRegex(ValueError, "multiple active CURRENT_CANON adjudications"):
                builder.build(root, root / "out")
            self.assertFalse((root / "out" / "current_view.json").exists())

    def test_cyclic_supersession_fails_closed(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            root_with_adjudications(
                root, adjudication(FIRST, [SECOND]), adjudication(SECOND, [FIRST])
            )
            with self.assertRaisesRegex(ValueError, "adjudication supersession cycle"):
                builder.build(root, root / "out")
            self.assertFalse((root / "out" / "semantic_index.sqlite").exists())

    def test_dangling_supersession_does_not_silently_revoke(self):
        objects = {FIRST: adjudication(FIRST, [SECOND])}
        with self.assertRaisesRegex(ValueError, "unresolved adjudication supersession"):
            builder.active_adjudications(objects)

    def test_valid_single_successor_keeps_one_active_decision(self):
        objects = {
            FIRST: adjudication(FIRST, decision="RETRACT"),
            SECOND: adjudication(SECOND, [FIRST], decision="REINSTATE"),
        }
        self.assertEqual(
            [obj["id"] for obj in builder.active_adjudications(objects)], [SECOND]
        )


if __name__ == "__main__":
    unittest.main()
