import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_mapper():
    path = ROOT / "build/map_research_staging.py"
    spec = importlib.util.spec_from_file_location("staging_mapper_identity", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mapper = load_mapper()


class MapperIdentityTests(unittest.TestCase):
    def test_record_type_prefix_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            mapper.canonical_id(
                "candidate_node",
                "EV-11111111-1111-4111-8111-111111111111",
            )

    def test_expected_prefix_preserves_uuid_payload(self):
        self.assertEqual(
            mapper.canonical_id(
                "candidate_node",
                "NODE-11111111-1111-4111-8111-111111111111",
            ),
            "NODE-11111111-1111-4111-8111-111111111111",
        )
        self.assertEqual(
            mapper.canonical_id(
                "vera_adjudication_decision",
                "VADJ-22222222-2222-4222-8222-222222222222",
            ),
            "ADJ-22222222-2222-4222-8222-222222222222",
        )

    def test_structured_source_locator_is_explicit_promotion_debt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            staging = root / "semantic_population_v0.2"
            staging.mkdir()
            records = [
                {
                    "record_type": "candidate_source_instance",
                    "id": "SINST-11111111-1111-4111-8111-111111111111",
                    "locator": {"file_id": "F0TEST", "section": "Historical source"},
                },
                {
                    "record_type": "candidate_source_instance",
                    "id": "SINST-22222222-2222-4222-8222-222222222222",
                    "locator": "file:F0TEST#section=Historical%20source",
                },
            ]
            (staging / "candidate_source_instances.jsonl").write_text(
                "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
                encoding="utf-8",
            )
            vocabulary = root / "relation_types.json"
            vocabulary.write_text(json.dumps({"relation_types": []}) + "\n", encoding="utf-8")

            report = mapper.build_report(staging, vocabulary)
            by_id = {entry["staging_id"]: entry for entry in report["entries"]}

            structured = by_id["SINST-11111111-1111-4111-8111-111111111111"]
            self.assertFalse(structured["promotion_ready"])
            self.assertIn("SOURCE_LOCATOR_MAPPING_REQUIRED", structured["blockers"])

            canonical_string = by_id["SINST-22222222-2222-4222-8222-222222222222"]
            self.assertTrue(canonical_string["promotion_ready"])
            self.assertNotIn("SOURCE_LOCATOR_MAPPING_REQUIRED", canonical_string["blockers"])


if __name__ == "__main__":
    unittest.main()
