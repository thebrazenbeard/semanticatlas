import importlib.util
import pathlib
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


if __name__ == "__main__":
    unittest.main()
