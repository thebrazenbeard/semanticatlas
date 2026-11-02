"""Synthetic tests: historical descriptors cannot elevate source authority."""

import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "historical_export_assessment", ROOT / "build/assess_historical_export.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def clean_descriptor():
    return {
        "schema": "HISTORICAL_EXPORT_SOURCE_DESCRIPTOR_V1",
        "source_class": "SEMANTIC_RESEARCH",
        "capture_state": "HISTORICAL_NOT_INSTALLED",
        "representation": "VERIFIED_EXTRACTION_CLAIM",
        "privacy_review": "PUBLIC_SAFE_REVIEWED",
        "rights_review": "RESEARCH_USE_REVIEWED",
        "fidelity_review": "EXACT_REPRESENTATION_REVIEWED",
    }


class HistoricalExportAssessmentTests(unittest.TestCase):
    def test_even_reviewed_caller_claims_cannot_authorize_effects(self):
        result = MODULE.assess_export_source(clean_descriptor())
        self.assertEqual(result["disposition"], "HOLD_RESEARCH_ONLY")
        self.assertFalse(result["may_publish"])
        self.assertFalse(result["may_train"])
        self.assertFalse(result["may_promote_canonical"])
        self.assertIn("INDEPENDENT_SOURCE_AUTHORITY_UNVERIFIED", result["blockers"])

    def test_privacy_projection_does_not_claim_exact_evidence(self):
        descriptor = clean_descriptor()
        descriptor["representation"] = "PRIVACY_PROJECTION"
        result = MODULE.assess_export_source(descriptor)
        self.assertEqual(result["fidelity_class"], "PROJECTION_ONLY")
        self.assertIn("EXACT_SOURCE_FIDELITY_NOT_PRESENT", result["blockers"])

    def test_private_locator_and_secret_never_echo(self):
        descriptor = clean_descriptor()
        descriptor.update({"absolute_path": "C:/PRIVATE/DO-NOT-ECHO", "token": "secret123"})
        rendered = json.dumps(MODULE.assess_export_source(descriptor), sort_keys=True)
        self.assertIn("UNRECOGNIZED_OR_PRIVATE_FIELDS", rendered)
        self.assertNotIn("C:/PRIVATE/DO-NOT-ECHO", rendered)
        self.assertNotIn("secret123", rendered)
        self.assertNotIn("absolute_path", rendered)

    def test_current_installation_claim_rejected(self):
        descriptor = clean_descriptor()
        descriptor["capture_state"] = "CURRENT_INSTALLED"
        result = MODULE.assess_export_source(descriptor)
        self.assertIn("HISTORICAL_CAPTURE_NOT_BOUND", result["blockers"])
        self.assertEqual(result["source_currentness"], "HISTORICAL_NOT_INSTALLED")

    def test_metadata_only_stays_metadata_only(self):
        descriptor = clean_descriptor()
        descriptor["representation"] = "METADATA_ONLY"
        result = MODULE.assess_export_source(descriptor)
        self.assertEqual(result["fidelity_class"], "METADATA_ONLY")

    def test_malformed_descriptor_fails_closed(self):
        result = MODULE.assess_export_source(None)
        self.assertIn("INVALID_DESCRIPTOR", result["blockers"])
        self.assertFalse(result["may_promote_canonical"])

    def test_unhashable_input_values_do_not_crash_or_grant(self):
        descriptor = clean_descriptor()
        descriptor["source_class"] = ["SEMANTIC_RESEARCH"]
        descriptor["representation"] = ["SOURCE_BYTES_CLAIM"]
        result = MODULE.assess_export_source(descriptor)
        self.assertIn("SOURCE_CLASS_UNRESOLVED", result["blockers"])
        self.assertIn("REPRESENTATION_UNRESOLVED", result["blockers"])
        self.assertFalse(result["may_publish"])

    def test_output_deterministic_under_key_order_change(self):
        desc = clean_descriptor()
        left = MODULE.assess_export_source(desc)
        right = MODULE.assess_export_source(dict(reversed(list(desc.items()))))
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
