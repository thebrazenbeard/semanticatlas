"""Direct builder must not let unrelated lifecycle evidence revoke canon."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_lifecycle_guard", ROOT / "build" / "build_current_view.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

S = "NODE-11111111-1111-4111-8111-111111111111"
T = "NODE-22222222-2222-4222-8222-222222222222"
A = "ADJ-11111111-1111-4111-8111-111111111111"
B = "ADJ-22222222-2222-4222-8222-222222222222"

def adj(identity, subject, decision="ACCEPT"):
    return {"object_type": "adjudication", "id": identity, "subject_id": subject,
            "decision": decision, "authority_scope": "CURRENT_CANON",
            "supersedes_adjudication_ids": []}

def terminal(subject, caused_by, successor=None):
    return {"object_type": "lifecycle_event", "id": "LIFE-test",
            "subject_id": subject, "event_type": "RETRACTED",
            "caused_by_adjudication_id": caused_by, "successor_id": successor}

class LifecycleCauseGuardTests(unittest.TestCase):
    def test_cross_subject_cause_cannot_revoke_other_subject(self):
        objects = {A: adj(A,S), B: adj(B,T), "LIFE-test": terminal(S,B)}
        with self.assertRaisesRegex(ValueError, "cross-subject lifecycle cause"):
            builder.active_adjudications(objects)

    def test_dangling_cause_rejected(self):
        objects = {A: adj(A,S), "LIFE-test": terminal(S,B)}
        with self.assertRaisesRegex(ValueError, "unresolved lifecycle cause"):
            builder.active_adjudications(objects)

    def test_valid_same_subject_terminal_suppresses_only_its_subject(self):
        objects = {A: adj(A,S), B: adj(B,T), "LIFE-test": terminal(S,A)}
        result = builder.active_adjudications(objects)
        self.assertEqual([a["id"] for a in result],[B])

    def test_missing_successor_rejected(self):
        objects = {A: adj(A,S), "LIFE-test": terminal(S,A, successor=T)}
        with self.assertRaisesRegex(ValueError, "unresolved lifecycle successor"):
            builder.active_adjudications(objects)

if __name__ == "__main__":
    unittest.main()
