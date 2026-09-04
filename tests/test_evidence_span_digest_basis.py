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
    spec = importlib.util.spec_from_file_location("digest_basis_mapper", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mapper = load_mapper()


class EvidenceSpanDigestBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "schemas/semantic_atlas_v0.1.schema.json").read_text(encoding="utf-8")
        )
        cls.validator = jsonschema.Draft202012Validator(cls.schema)

    def exact_utf8_span(self):
        text = "Exact retrieved text\r\nwith original line endings."
        return {
            "schema_version": "0.1",
            "object_type": "evidence_span",
            "id": "EVID-11111111-1111-4111-8111-111111111111",
            "source_instance_id": "SRCI-22222222-2222-4222-8222-222222222222",
            "source_version_ref": "provider-version-17",
            "locator": "native-message:17",
            "digest_basis": "EXACT_UTF8_SPAN",
            "representation_contract": "Exact authoritative retrieval text; encode UTF-8 exactly as retrieved",
            "span_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "byte_start": None,
            "byte_end_exclusive": None,
            "text_encoding": "UTF-8",
            "normalization": "NONE",
            "extractor_identity": None,
            "extractor_version": None,
            "excerpt": text,
        }

    def test_exact_utf8_requires_no_normalization(self):
        span = self.exact_utf8_span()
        self.assertEqual(list(self.validator.iter_errors(span)), [])

        normalized = json.loads(json.dumps(span))
        normalized["normalization"] = None
        self.assertTrue(list(self.validator.iter_errors(normalized)))

    def test_verified_extraction_requires_extractor_identity_and_version(self):
        span = self.exact_utf8_span()
        span.update({
            "digest_basis": "VERIFIED_EXTRACTION_REPRESENTATION",
            "representation_contract": "DOCX paragraph extraction preserving paragraph order and exact extracted text bytes",
            "text_encoding": "UTF-8",
            "normalization": "NONE",
            "extractor_identity": "semantic-atlas-docx-extractor",
            "extractor_version": "1.0.0",
        })
        self.assertEqual(list(self.validator.iter_errors(span)), [])

        missing_extractor = json.loads(json.dumps(span))
        missing_extractor["extractor_version"] = None
        self.assertTrue(list(self.validator.iter_errors(missing_extractor)))

    def test_summary_ocr_and_privacy_are_not_exact_digest_bases(self):
        for bad_basis in ("PRIVACY_PROJECTION", "SEMANTIC_SUMMARY", "OCR_GUESS"):
            with self.subTest(bad_basis=bad_basis):
                span = self.exact_utf8_span()
                span["digest_basis"] = bad_basis
                self.assertTrue(list(self.validator.iter_errors(span)))

    def test_source_bytes_range_must_move_forward(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = pathlib.Path(tempdir)
            (root / "schemas").mkdir()
            (root / "vocabulary").mkdir()
            (root / "atlas" / "sources").mkdir(parents=True)
            (root / "atlas" / "evidence").mkdir(parents=True)
            (root / "schemas" / "semantic_atlas_v0.1.schema.json").write_bytes(
                (ROOT / "schemas" / "semantic_atlas_v0.1.schema.json").read_bytes()
            )
            (root / "vocabulary" / "relation_types_v0.1.json").write_bytes(
                (ROOT / "vocabulary" / "relation_types_v0.1.json").read_bytes()
            )
            source = {
                "schema_version": "0.1",
                "object_type": "source_instance",
                "id": "SRCI-22222222-2222-4222-8222-222222222222",
                "title": "Raw file",
                "source_class": "FILE",
                "retrieval_surface": "Git",
                "embedded_time_start": None,
                "embedded_time_end": None,
                "locator": "blob:abc",
                "content_sha256": "a" * 64,
            }
            span = {
                "schema_version": "0.1",
                "object_type": "evidence_span",
                "id": "EVID-11111111-1111-4111-8111-111111111111",
                "source_instance_id": source["id"],
                "source_version_ref": "blob:abc",
                "locator": "bytes:10-10",
                "digest_basis": "SOURCE_BYTES_RANGE",
                "representation_contract": "Raw source bytes [start,end)",
                "span_sha256": hashlib.sha256(b"").hexdigest(),
                "byte_start": 10,
                "byte_end_exclusive": 10,
                "text_encoding": None,
                "normalization": None,
                "extractor_identity": None,
                "extractor_version": None,
                "excerpt": None,
            }
            (root / "atlas" / "sources" / "source.json").write_text(json.dumps(source), encoding="utf-8")
            (root / "atlas" / "evidence" / "span.json").write_text(json.dumps(span), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "build" / "validate_atlas.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("byte_end_exclusive > byte_start", result.stdout)

    def test_mapper_exposes_new_exact_evidence_promotion_debt(self):
        record = {
            "record_type": "candidate_evidence_span",
            "id": "EV-33333333-3333-4333-8333-333333333333",
            "source_instance_id": "SINST-44444444-4444-4444-8444-444444444444",
            "locator": {"section": "A"},
            "digest": "b" * 64,
        }
        blockers = mapper.blocker_list(record, set())
        self.assertIn("EVIDENCE_DIGEST_BASIS_MAPPING_REQUIRED", blockers)
        self.assertIn("EVIDENCE_SOURCE_VERSION_BINDING_REQUIRED", blockers)
        self.assertIn("EVIDENCE_REPRESENTATION_CONTRACT_MAPPING_REQUIRED", blockers)
        self.assertNotIn("EVIDENCE_DIGEST_MISSING", blockers)


if __name__ == "__main__":
    unittest.main()
