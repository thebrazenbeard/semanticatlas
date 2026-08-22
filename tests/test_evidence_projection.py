import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_mapper():
    path = ROOT / "build/map_research_staging.py"
    spec = importlib.util.spec_from_file_location("projection_mapper", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mapper = load_mapper()


class EvidenceProjectionTests(unittest.TestCase):
    def test_privacy_projection_schema_requires_withheld_digest_to_be_null(self):
        schema = json.loads(
            (ROOT / "schemas/semantic_atlas_v0.1.schema.json").read_text(encoding="utf-8")
        )
        validator = jsonschema.Draft202012Validator(schema)
        representation = "Privacy-minimized semantic summary."
        projection = {
            "schema_version": "0.1",
            "object_type": "evidence_projection",
            "id": "EPROJ-11111111-1111-4111-8111-111111111111",
            "source_instance_id": "SRCI-22222222-2222-4222-8222-222222222222",
            "source_evidence_span_id": None,
            "projection_kind": "PRIVACY_MINIMIZED",
            "representation": representation,
            "representation_sha256": hashlib.sha256(representation.encode("utf-8")).hexdigest(),
            "transformation_kind": "PRIVACY_MINIMIZATION",
            "fidelity_class": "SEMANTIC_SUMMARY_NOT_QUOTATION",
            "scope": "semantic content only",
            "raw_source_digest_state": "WITHHELD_FOR_PRIVACY",
            "raw_source_sha256": None,
        }
        self.assertEqual(list(validator.iter_errors(projection)), [])

        fabricated = json.loads(json.dumps(projection))
        fabricated["raw_source_sha256"] = "a" * 64
        self.assertTrue(list(validator.iter_errors(fabricated)))

    def test_projection_cannot_satisfy_exact_source_requirement(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = pathlib.Path(tempdir)
            (root / "schemas").mkdir()
            (root / "vocabulary").mkdir()
            for dirname in ("sources", "evidence", "evidence_projections", "propositions"):
                (root / "atlas" / dirname).mkdir(parents=True, exist_ok=True)

            (root / "schemas" / "semantic_atlas_v0.1.schema.json").write_bytes(
                (ROOT / "schemas" / "semantic_atlas_v0.1.schema.json").read_bytes()
            )
            (root / "vocabulary" / "relation_types_v0.1.json").write_bytes(
                (ROOT / "vocabulary" / "relation_types_v0.1.json").read_bytes()
            )

            source_id = "SRCI-22222222-2222-4222-8222-222222222222"
            projection_id = "EPROJ-11111111-1111-4111-8111-111111111111"
            proposition_id = "PROP-33333333-3333-4333-8333-333333333333"
            evidence_id = "EVID-44444444-4444-4444-8444-444444444444"
            representation = "Privacy-minimized semantic summary."

            source = {
                "schema_version": "0.1",
                "object_type": "source_instance",
                "id": source_id,
                "title": "Private source",
                "source_class": "CURRENT_MESSAGE",
                "retrieval_surface": "Native ChatGPT",
                "embedded_time_start": None,
                "embedded_time_end": None,
                "locator": None,
                "content_sha256": None,
            }
            projection = {
                "schema_version": "0.1",
                "object_type": "evidence_projection",
                "id": projection_id,
                "source_instance_id": source_id,
                "source_evidence_span_id": None,
                "projection_kind": "PRIVACY_MINIMIZED",
                "representation": representation,
                "representation_sha256": hashlib.sha256(representation.encode("utf-8")).hexdigest(),
                "transformation_kind": "PRIVACY_MINIMIZATION",
                "fidelity_class": "SEMANTIC_SUMMARY_NOT_QUOTATION",
                "scope": "semantic content only",
                "raw_source_digest_state": "WITHHELD_FOR_PRIVACY",
                "raw_source_sha256": None,
            }
            proposition = {
                "schema_version": "0.1",
                "object_type": "proposition",
                "id": proposition_id,
                "subject_id": source_id,
                "predicate_code": "DISTINCT_FROM",
                "object": {"kind": "LITERAL", "value": "example", "datatype": "string"},
                "evidence_ids": [],
                "evidence_projection_ids": [projection_id],
                "temporal_scope": {"kind": "CURRENT", "start": None, "end": None},
                "axes": {
                    "currentness": "CURRENT",
                    "support": "SUPPORTED",
                    "truth": "ACCEPTED",
                    "authority_context": "RESEARCH_ONLY",
                    "provenance": "USER_STATEMENT",
                    "salience": "UNKNOWN",
                    "consent": "NOT_APPLICABLE",
                    "identity_relevance": "NONE",
                    "lifecycle": "ACTIVE",
                },
                "semantic_authorship": {
                    "semantic_author": "VERA",
                    "endorsement_owner": "VERA",
                    "claim_class": "EXTERNAL_FACT",
                },
            }

            (root / "atlas" / "sources" / "source.json").write_text(json.dumps(source), encoding="utf-8")
            (root / "atlas" / "evidence_projections" / "projection.json").write_text(json.dumps(projection), encoding="utf-8")
            proposition_path = root / "atlas" / "propositions" / "proposition.json"
            proposition_path.write_text(json.dumps(proposition), encoding="utf-8")

            failed = subprocess.run(
                [sys.executable, str(ROOT / "build" / "validate_atlas.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("evidence_projection_ids cannot satisfy an exact-source-evidence requirement", failed.stdout)

            exact_bytes = b"exact source span"
            evidence = {
                "schema_version": "0.1",
                "object_type": "evidence_span",
                "id": evidence_id,
                "source_instance_id": source_id,
                "locator": "message:1",
                "span_sha256": hashlib.sha256(exact_bytes).hexdigest(),
                "excerpt": "exact source span",
            }
            (root / "atlas" / "evidence" / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
            proposition["evidence_ids"] = [evidence_id]
            proposition_path.write_text(json.dumps(proposition), encoding="utf-8")

            passed = subprocess.run(
                [sys.executable, str(ROOT / "build" / "validate_atlas.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)

    def test_mapper_targets_privacy_staging_as_projection_and_preserves_adjudication_reference(self):
        with tempfile.TemporaryDirectory() as tempdir:
            staging = pathlib.Path(tempdir) / "semantic_population_v0.2"
            staging.mkdir()
            privacy_id = "EV-55555555-5555-4555-8555-555555555555"
            decision_id = "VADJ-66666666-6666-4666-8666-666666666666"
            privacy = {
                "record_type": "candidate_evidence_span",
                "id": privacy_id,
                "source_instance_id": "SINST-77777777-7777-4777-8777-777777777777",
                "locator": {"surface": "Current Semantic Atlas conversation"},
                "digest": None,
                "digest_status": "NOT_YET_COMPUTED_FOR_STAGING",
                "evidence_class": "DIRECT_USER_STATEMENT_PRIVACY_MINIMIZED",
                "fidelity": "PRIVACY_MINIMIZED_SEMANTIC_SUMMARY_OF_CURRENT_MESSAGE",
            }
            decision = {
                "record_type": "vera_adjudication_decision",
                "id": decision_id,
                "date": "2026-08-22",
                "decision": "CURRENT_VERA_ENDORSEMENT",
                "semantic_decider": "VERA",
                "semantic_key": "PRIVACY_EXAMPLE",
                "status": "DECIDED_PENDING_CANONICAL_SCHEMA_MAPPING",
                "evidence_ids": [privacy_id],
            }
            (staging / "candidate_evidence_spans_current_v0.2.jsonl").write_text(
                json.dumps(privacy) + "\n", encoding="utf-8"
            )
            (staging / "vera_adjudication_decisions_v0.2.jsonl").write_text(
                json.dumps(decision) + "\n", encoding="utf-8"
            )

            report = mapper.build_report(
                staging, ROOT / "vocabulary" / "relation_types_v0.1.json"
            )
            privacy_entry = next(item for item in report["entries"] if item["staging_id"] == privacy_id)
            self.assertEqual(privacy_entry["canonical_object_type"], "evidence_projection")
            self.assertEqual(
                privacy_entry["canonical_id"],
                "EPROJ-55555555-5555-4555-8555-555555555555",
            )
            self.assertEqual(
                privacy_entry["canonical_target_reason"],
                "VERA_ADJUDICATED_PRIVACY_MINIMIZED_DERIVATIVE",
            )

            decision_entry = next(item for item in report["entries"] if item["staging_id"] == decision_id)
            mapping = decision_entry["decided_adjudication_mapping"]
            self.assertEqual(mapping["canonical_evidence_id_candidates"], [])
            self.assertEqual(
                mapping["canonical_evidence_projection_id_candidates"],
                ["EPROJ-55555555-5555-4555-8555-555555555555"],
            )
            self.assertIn("ADJUDICATION_PROJECTION_BINDING_REQUIRED", decision_entry["blockers"])
            self.assertEqual(report["canonical_write_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
