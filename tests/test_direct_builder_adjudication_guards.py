"""Direct materialization must fail closed on invalid adjudication lineages.

Synthetic, isolated fixtures: no semantic authority is conferred by these tests.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "atlas_direct_builder_guard", ROOT / "build" / "build_current_view.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

NODE = "NODE-11111111-1111-4111-8111-111111111111"
FIRST = "ADJ-22222222-2222-4222-8222-222222222222"
SECOND = "ADJ-33333333-3333-4333-8333-333333333333"


def put(root: Path, directory: str, name: str, value: dict):
    target = root / "atlas" / directory
    target.mkdir(parents=True, exist_ok=True)
    (target / name).write_text(json.dumps(value), encoding="utf-8")


def adjudication(identifier: str, supersedes=()):
    return {
        "id": identifier,
        "object_type": "adjudication",
        "subject_id": NODE,
        "decision": "ACCEPT",
        "authority_scope": "CURRENT_CANON",
        "supersedes_adjudication_ids": list(supersedes),
    }


class DirectBuilderAdjudicationGuardTests(unittest.TestCase):
    def test_independent_active_current_decisions_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            put(root, "nodes", "node.json", {"id": NODE, "object_type": "node"})
            put(root, "adjudications", "first.json", adjudication(FIRST))
            put(root, "adjudications", "second.json", adjudication(SECOND))
            with self.assertRaisesRegex(ValueError, "multiple active CURRENT_CANON"):
                builder.build(root, root / "out")

    def test_cycle_rejected_instead_of_emptying_current_canon(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            put(root, "nodes", "node.json", {"id": NODE, "object_type": "node"})
            put(root, "adjudications", "first.json", adjudication(FIRST, [SECOND]))
            put(root, "adjudications", "second.json", adjudication(SECOND, [FIRST]))
            with self.assertRaisesRegex(ValueError, "adjudication supersession cycle"):
                builder.build(root, root / "out")

    def test_unknown_predecessor_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            put(root, "nodes", "node.json", {"id": NODE, "object_type": "node"})
            put(root, "adjudications", "first.json", adjudication(FIRST, [SECOND]))
            with self.assertRaisesRegex(ValueError, "unresolved adjudication supersession"):
                builder.build(root, root / "out")

    def test_legitimate_single_successor_remains_current(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            put(root, "nodes", "node.json", {"id": NODE, "object_type": "node"})
            put(root, "adjudications", "first.json", adjudication(FIRST))
            put(root, "adjudications", "second.json", adjudication(SECOND, [FIRST]))
            result = builder.build(root, root / "out")
            self.assertEqual(len(result["current_view_sha256"]), 64)
            view = json.loads((root / "out" / "current_view.json").read_text())
            self.assertEqual(view["active_adjudication_ids"], [SECOND])


if __name__ == "__main__":
    unittest.main()
