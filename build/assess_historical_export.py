"""Nonpromoting assessment of historical export source-fidelity descriptors.

This accepts *claims* about a source, never source bytes or private locators.
The result cannot authorize publication, training, or canonical Atlas mutation.
"""

from __future__ import annotations

from collections.abc import Mapping


SCHEMA = "SEMANTIC_ATLAS_HISTORICAL_EXPORT_ASSESSMENT_V1"
_ALLOWED_KEYS = frozenset({
    "schema", "source_class", "capture_state", "representation",
    "privacy_review", "rights_review", "fidelity_review",
})
_SOURCE_CLASSES = frozenset({
    "SEMANTIC_RESEARCH", "CONVERSATION", "PROJECT_HANDOFF", "OTHER",
})
_REPRESENTATIONS = frozenset({
    "METADATA_ONLY", "PRIVACY_PROJECTION", "VERIFIED_EXTRACTION_CLAIM",
    "SOURCE_BYTES_CLAIM",
})


def _exact_string(value: object, expected: str) -> bool:
    return type(value) is str and value == expected


def _one_of_strings(value: object, options: frozenset[str]) -> bool:
    return type(value) is str and value in options


def assess_export_source(descriptor: Mapping[str, object]) -> dict[str, object]:
    """Return redacted blockers; never echo input, admit data, or write files.

    Caller-provided `CLEARED`/`VERIFIED` flags remain claims, not independent
    evidence. The assessment always holds for external source verification and
    semantic adjudication by the existing canonical pathways.
    """
    blockers: set[str] = {"INDEPENDENT_SOURCE_AUTHORITY_UNVERIFIED", "CANONICAL_ADJUDICATION_REQUIRED"}
    fidelity = "UNKNOWN"

    if type(descriptor) is not dict:
        blockers.add("INVALID_DESCRIPTOR")
    else:
        if descriptor.keys() - _ALLOWED_KEYS:
            blockers.add("UNRECOGNIZED_OR_PRIVATE_FIELDS")
        if not _exact_string(descriptor.get("schema"), "HISTORICAL_EXPORT_SOURCE_DESCRIPTOR_V1"):
            blockers.add("SCHEMA_UNRECOGNIZED")
        if not _one_of_strings(descriptor.get("source_class"), _SOURCE_CLASSES):
            blockers.add("SOURCE_CLASS_UNRESOLVED")
        if not _exact_string(descriptor.get("capture_state"), "HISTORICAL_NOT_INSTALLED"):
            blockers.add("HISTORICAL_CAPTURE_NOT_BOUND")
        if not _exact_string(descriptor.get("privacy_review"), "PUBLIC_SAFE_REVIEWED"):
            blockers.add("PRIVACY_REVIEW_REQUIRED")
        if not _exact_string(descriptor.get("rights_review"), "RESEARCH_USE_REVIEWED"):
            blockers.add("RIGHTS_REVIEW_REQUIRED")

        representation = descriptor.get("representation")
        if not _one_of_strings(representation, _REPRESENTATIONS):
            blockers.add("REPRESENTATION_UNRESOLVED")
        elif representation == "PRIVACY_PROJECTION":
            fidelity = "PROJECTION_ONLY"
            blockers.add("EXACT_SOURCE_FIDELITY_NOT_PRESENT")
        elif representation == "METADATA_ONLY":
            fidelity = "METADATA_ONLY"
            blockers.add("EXACT_SOURCE_FIDELITY_NOT_PRESENT")
        elif _exact_string(descriptor.get("fidelity_review"), "EXACT_REPRESENTATION_REVIEWED"):
            # No digest or source locator is admitted by this descriptor.
            fidelity = "REVIEWED_CLAIM_NOT_VERIFIED_CUSTODY"
            blockers.add("EXACT_SOURCE_CUSTODY_UNVERIFIED")
        else:
            fidelity = "UNREVIEWED_EXACTNESS_CLAIM"
            blockers.add("FIDELITY_REVIEW_REQUIRED")

    return {
        "schema": SCHEMA,
        "disposition": "HOLD_RESEARCH_ONLY",
        "source_currentness": "HISTORICAL_NOT_INSTALLED",
        "fidelity_class": fidelity,
        "blockers": sorted(blockers),
        "may_publish": False,
        "may_train": False,
        "may_promote_canonical": False,
        "source_material_read": False,
        "source_material_stored": False,
    }
