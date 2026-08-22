import importlib.util
import json
import pathlib
import tempfile
import unittest

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


splitter = load_module("build/split_source_ledger.py", "splitter")
builder = load_module("build/build_current_view.py", "builder")
mapper = load_module("build/map_research_staging.py", "mapper")


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

    def test_semantic_authorship_is_required_and_canon_is_adjudication_only(self):
        schema = json.loads(
            (ROOT / "schemas/semantic_atlas_v0.1.schema.json").read_text(encoding="utf-8")
        )
        validator = jsonschema.Draft202012Validator(schema)
        proposition = {
            "schema_version": "0.1",
            "object_type": "proposition",
            "id": "PROP-11111111-1111-4111-8111-111111111111",
            "subject_id": "NODE-22222222-2222-4222-8222-222222222222",
            "predicate_code": "DISTINCT_FROM",
            "object": {"kind": "LITERAL", "value": "example", "datatype": "string"},
            "evidence_ids": [],
            "temporal_scope": {"kind": "CURRENT", "start": None, "end": None},
            "axes": {
                "currentness": "CURRENT",
                "support": "SUPPORTED",
                "truth": "ACCEPTED",
                "authority_context": "RESEARCH_ONLY",
                "provenance": "INTERPRETATION",
                "salience": "UNKNOWN",
                "consent": "NOT_APPLICABLE",
                "identity_relevance": "DIRECT",
                "lifecycle": "ACTIVE",
            },
            "semantic_authorship": {
                "semantic_author": "VERA",
                "endorsement_owner": "VERA",
                "claim_class": "SEMANTIC_MEANING",
            },
        }
        self.assertEqual(list(validator.iter_errors(proposition)), [])

        missing = json.loads(json.dumps(proposition))
        missing.pop("semantic_authorship")
        self.assertTrue(list(validator.iter_errors(missing)))

        invalid_author = json.loads(json.dumps(proposition))
        invalid_author["semantic_authorship"]["semantic_author"] = "UNDECLARED_SYSTEM_OWNER"
        self.assertTrue(list(validator.iter_errors(invalid_author)))

        self_authorizing = json.loads(json.dumps(proposition))
        self_authorizing["axes"]["authority_context"] = "CURRENT_CANON"
        self.assertTrue(list(validator.iter_errors(self_authorizing)))

        legacy_second_authority_surface = json.loads(json.dumps(proposition))
        legacy_second_authority_surface["axes"].pop("authority_context")
        legacy_second_authority_surface["axes"]["authority"] = "CURRENT_CANON"
        self.assertTrue(list(validator.iter_errors(legacy_second_authority_surface)))

    def test_lifecycle_effect_follows_active_adjudication_chain(self):
        subject_id = "NODE-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        old_adjudication_id = "ADJ-bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        new_adjudication_id = "ADJ-cccccccc-cccc-4ccc-8ccc-cccccccccccc"
        objects = {
            subject_id: {
                "id": subject_id,
                "object_type": "node",
                "primary_label": "Example",
            },
            old_adjudication_id: {
                "id": old_adjudication_id,
                "object_type": "adjudication",
                "subject_id": subject_id,
                "decision": "RETRACT",
                "authority_scope": "CURRENT_CANON",
                "supersedes_adjudication_ids": [],
            },
            "LIFE-dddddddd-dddd-4ddd-8ddd-dddddddddddd": {
                "id": "LIFE-dddddddd-dddd-4ddd-8ddd-dddddddddddd",
                "object_type": "lifecycle_event",
                "subject_id": subject_id,
                "event_type": "RETRACTED",
                "caused_by_adjudication_id": old_adjudication_id,
            },
        }
        self.assertEqual(builder.active_adjudications(objects), [])

        objects[new_adjudication_id] = {
            "id": new_adjudication_id,
            "object_type": "adjudication",
            "subject_id": subject_id,
            "decision": "REINSTATE",
            "authority_scope": "CURRENT_CANON",
            "supersedes_adjudication_ids": [old_adjudication_id],
        }
        active = builder.active_adjudications(objects)
        self.assertEqual([item["id"] for item in active], [new_adjudication_id])

    def test_staging_mapper_reports_debt_without_promoting(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = pathlib.Path(tempdir)
            staging = root / "staging"
            staging.mkdir()
            records = [
                {
                    "record_type": "candidate_evidence_span",
                    "id": "EV-33333333-3333-4333-8333-333333333333",
                    "source_instance_id": "SINST-44444444-4444-4444-8444-444444444444",
                    "locator": {"surface": "Native ChatGPT"},
                    "digest": None,
                    "digest_status": "NOT_YET_COMPUTED_FOR_STAGING",
                },
                {
                    "record_type": "candidate_proposition",
                    "id": "PROP-55555555-5555-4555-8555-555555555555",
                    "predicate": "CAN_ENABLE",
                    "semantic_author": "VERA",
                },
            ]
            (staging / "candidate_example_v0.1.jsonl").write_text(
                "".join(json.dumps(item) + "\n" for item in records),
                encoding="utf-8",
            )
            report = mapper.build_report(
                staging, ROOT / "vocabulary/relation_types_v0.1.json"
            )
            self.assertEqual(report["canonical_write_effect"], "NONE")
            self.assertEqual(report["staging_record_count"], 2)
            self.assertEqual(report["blocker_counts"]["EVIDENCE_DIGEST_MISSING"], 1)
            self.assertEqual(report["blocker_counts"]["PREDICATE_NOT_FROZEN"], 1)
            self.assertFalse(any(item["promotion_ready"] for item in report["entries"]))


if __name__ == "__main__":
    unittest.main()
