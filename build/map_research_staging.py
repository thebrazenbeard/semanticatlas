#!/usr/bin/env python3
"""Map provisional Semantic Atlas research staging to canonical-shape readiness.

This tool NEVER writes canonical atlas objects. It reports deterministic ID/reference
mapping, shape targets, decided-vs-candidate semantic state, and promotion blockers so
research staging can remain permissive without weakening canonical validation.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

UUID_PAYLOAD_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

TYPE_MAP = {
    "candidate_source_instance": ("source_instance", "SRCI"),
    "candidate_evidence_span": ("evidence_span", "EVID"),
    "candidate_node": ("node", "NODE"),
    "candidate_definition": ("node_definition", "NDEF"),
    "candidate_proposition": ("proposition", "PROP"),
    "candidate_interpretation": ("interpretation", "INTP"),
    "candidate_adjudication_packet": ("adjudication", "ADJ"),
    "vera_adjudication_decision": ("adjudication", "ADJ"),
}

STAGING_PREFIX_MAP = {
    "candidate_source_instance": "SINST",
    "candidate_evidence_span": "EV",
    "candidate_node": "NODE",
    "candidate_definition": "DEF",
    "candidate_proposition": "PROP",
    "candidate_interpretation": "INT",
    "candidate_adjudication_packet": "ADJPKT",
    "vera_adjudication_decision": "VADJ",
}

REFERENCE_PREFIX_MAP = {
    "SINST": "SRCI",
    "EV": "EVID",
    "NODE": "NODE",
    "DEF": "NDEF",
    "PROP": "PROP",
    "INT": "INTP",
    "ADJPKT": "ADJ",
    "VADJ": "ADJ",
}


def _uuid_payload(value: str) -> str:
    if not isinstance(value, str) or "-" not in value:
        raise ValueError(f"invalid staging id {value!r}")
    payload = value.split("-", 1)[1]
    if not UUID_PAYLOAD_RE.fullmatch(payload):
        raise ValueError(f"invalid staging UUID payload {value!r}")
    return payload


def is_privacy_projection(record: dict) -> bool:
    if record.get("record_type") != "candidate_evidence_span":
        return False
    fields = (
        record.get("projection_kind"),
        record.get("evidence_class"),
        record.get("fidelity"),
        record.get("digest_status"),
    )
    return any("PRIVACY_MINIMIZED" in str(value).upper() for value in fields if value is not None)


def target_for_record(record: dict):
    if is_privacy_projection(record):
        return ("evidence_projection", "EPROJ")
    return TYPE_MAP.get(record.get("record_type"))


def canonical_id(record_type: str, staging_id: str, target=None) -> str:
    target = target or TYPE_MAP.get(record_type)
    expected_prefix = STAGING_PREFIX_MAP.get(record_type)
    if not target or not expected_prefix:
        raise ValueError(f"unsupported staging record_type {record_type!r}")
    if not isinstance(staging_id, str) or "-" not in staging_id:
        raise ValueError(f"invalid staging id {staging_id!r}")
    actual_prefix = staging_id.split("-", 1)[0]
    if actual_prefix != expected_prefix:
        raise ValueError(
            f"staging id prefix {actual_prefix!r} does not match "
            f"record_type {record_type!r} expected prefix {expected_prefix!r}"
        )
    return f"{target[1]}-{_uuid_payload(staging_id)}"


def canonical_reference(staging_id: str, staged_id_map: dict[str, str] | None = None) -> str:
    if staged_id_map and staging_id in staged_id_map:
        return staged_id_map[staging_id]
    if not isinstance(staging_id, str) or "-" not in staging_id:
        raise ValueError(f"invalid staging reference {staging_id!r}")
    prefix = staging_id.split("-", 1)[0]
    target_prefix = REFERENCE_PREFIX_MAP.get(prefix)
    if not target_prefix:
        raise ValueError(f"unsupported staging reference prefix {prefix!r}")
    return f"{target_prefix}-{_uuid_payload(staging_id)}"


def iter_jsonl(staging: Path):
    for path in sorted(staging.glob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            yield path, line_number, json.loads(line)


def blocker_list(record: dict, predicate_codes: set[str]) -> list[str]:
    record_type = record.get("record_type")
    blockers: list[str] = []

    if record_type == "candidate_evidence_span" and is_privacy_projection(record):
        blockers.extend([
            "PROJECTION_REPRESENTATION_DIGEST_REQUIRED",
            "PROJECTION_TRANSFORMATION_MAPPING_REQUIRED",
            "PROJECTION_FIDELITY_MAPPING_REQUIRED",
            "PROJECTION_SCOPE_MAPPING_REQUIRED",
            "PROJECTION_RAW_SOURCE_DIGEST_STATE_MAPPING_REQUIRED",
        ])
        if not record.get("source_instance_id"):
            blockers.append("PROJECTION_SOURCE_BINDING_REQUIRED")
        if not record.get("locator"):
            blockers.append("PROJECTION_SOURCE_PROVENANCE_MAPPING_REQUIRED")

    elif record_type == "candidate_evidence_span":
        digest = record.get("digest")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            blockers.append("EVIDENCE_DIGEST_MISSING")
        if not record.get("locator"):
            blockers.append("EVIDENCE_LOCATOR_MISSING")
        if not record.get("digest_basis"):
            blockers.append("EVIDENCE_DIGEST_BASIS_MAPPING_REQUIRED")
        if not record.get("source_version_ref"):
            blockers.append("EVIDENCE_SOURCE_VERSION_BINDING_REQUIRED")
        if not record.get("representation_contract"):
            blockers.append("EVIDENCE_REPRESENTATION_CONTRACT_MAPPING_REQUIRED")

        basis = record.get("digest_basis")
        if basis == "SOURCE_BYTES_RANGE":
            if not isinstance(record.get("byte_start"), int) or not isinstance(record.get("byte_end_exclusive"), int):
                blockers.append("EVIDENCE_BYTE_RANGE_MAPPING_REQUIRED")
        elif basis == "EXACT_UTF8_SPAN":
            if record.get("text_encoding") != "UTF-8" or record.get("normalization") != "NONE":
                blockers.append("EVIDENCE_UTF8_EXACTNESS_MAPPING_REQUIRED")
        elif basis == "VERIFIED_EXTRACTION_REPRESENTATION":
            if not record.get("extractor_identity") or not record.get("extractor_version"):
                blockers.append("EVIDENCE_EXTRACTOR_PROVENANCE_REQUIRED")
        elif basis is not None:
            blockers.append("EVIDENCE_DIGEST_BASIS_INVALID")

    elif record_type == "candidate_definition":
        blockers.extend([
            "DEFINITION_SCOPE_MAPPING_REQUIRED",
            "ACCEPTING_ADJUDICATION_BINDING_REQUIRED",
            "SEMANTIC_OWNERSHIP_MAPPING_REQUIRED",
        ])

    elif record_type == "candidate_proposition":
        predicate = record.get("predicate")
        if predicate not in predicate_codes:
            blockers.append("PREDICATE_NOT_FROZEN")
        blockers.extend([
            "TEMPORAL_SCOPE_MAPPING_REQUIRED",
            "SEMANTIC_AXES_MAPPING_REQUIRED",
            "SEMANTIC_OWNERSHIP_MAPPING_REQUIRED",
            "ADJUDICATION_REQUIRED_FOR_PROMOTION",
        ])

    elif record_type == "candidate_interpretation":
        blockers.extend([
            "METHOD_MAPPING_REQUIRED",
            "KNOWLEDGE_CEILING_MAPPING_REQUIRED",
            "SEMANTIC_OWNERSHIP_MAPPING_REQUIRED",
            "ADJUDICATION_REQUIRED_FOR_PROMOTION",
        ])

    elif record_type == "candidate_adjudication_packet":
        blockers.extend([
            "ADJUDICATION_SUBJECT_MAPPING_REQUIRED",
            "ADJUDICATION_DECISION_MAPPING_REQUIRED",
            "ADJUDICATION_AUTHORITY_SCOPE_MAPPING_REQUIRED",
        ])
        if not record.get("semantic_decider"):
            blockers.append("ADJUDICATION_DECIDER_MISSING")

    elif record_type == "vera_adjudication_decision":
        blockers.extend([
            "ADJUDICATION_SUBJECT_MAPPING_REQUIRED",
            "ADJUDICATION_DECISION_ENUM_MAPPING_REQUIRED",
            "ADJUDICATION_AUTHORITY_SCOPE_MAPPING_REQUIRED",
        ])
        if not record.get("semantic_key"):
            blockers.append("ADJUDICATION_SEMANTIC_KEY_MISSING")
        if record.get("semantic_decider") != "VERA":
            blockers.append("ADJUDICATION_DECIDER_MAPPING_REQUIRED")
        if record.get("evidence_ids"):
            blockers.append("ADJUDICATION_EVIDENCE_BINDING_REQUIRED")
        if record.get("predecessor_decision_id"):
            blockers.append("ADJUDICATION_SUPERSESSION_MAPPING_REQUIRED")

    elif record_type == "candidate_source_instance":
        locator = record.get("locator")
        if locator is not None and not isinstance(locator, str):
            blockers.append("SOURCE_LOCATOR_MAPPING_REQUIRED")

    elif record_type == "candidate_node":
        pass

    else:
        blockers.append("UNSUPPORTED_STAGING_RECORD_TYPE")

    return sorted(set(blockers))


def decided_adjudication_mapping(record: dict, staged_id_map: dict[str, str]) -> dict | None:
    if record.get("record_type") != "vera_adjudication_decision":
        return None

    evidence_candidates = []
    projection_candidates = []
    evidence_mapping_errors = []
    for evidence_id in record.get("evidence_ids", []):
        try:
            mapped = canonical_reference(evidence_id, staged_id_map)
            if mapped.startswith("EPROJ-"):
                projection_candidates.append(mapped)
            else:
                evidence_candidates.append(mapped)
        except ValueError as exc:
            evidence_mapping_errors.append(str(exc))

    predecessor = record.get("predecessor_decision_id")
    predecessor_candidate = None
    predecessor_mapping_error = None
    if predecessor:
        try:
            predecessor_candidate = canonical_reference(predecessor, staged_id_map)
        except ValueError as exc:
            predecessor_mapping_error = str(exc)

    return {
        "semantic_state": "DECIDED",
        "canonical_mapping_state": "DECIDED_SEMANTICS_PENDING_CANONICAL_BINDING",
        "semantic_decider": record.get("semantic_decider"),
        "staging_decision": record.get("decision"),
        "semantic_key": record.get("semantic_key"),
        "decision_date": record.get("date"),
        "staging_status": record.get("status"),
        "canonical_decided_by_candidate": (
            "VERA" if record.get("semantic_decider") == "VERA" else None
        ),
        "canonical_evidence_id_candidates": evidence_candidates,
        "canonical_evidence_projection_id_candidates": projection_candidates,
        "evidence_mapping_errors": evidence_mapping_errors,
        "predecessor_decision_id": predecessor,
        "canonical_predecessor_adjudication_id_candidate": predecessor_candidate,
        "predecessor_mapping_error": predecessor_mapping_error,
    }


def build_report(staging: Path, vocabulary: Path) -> dict:
    vocab = json.loads(vocabulary.read_text(encoding="utf-8"))
    predicate_codes = {item["code"] for item in vocab.get("relation_types", [])}
    records = list(iter_jsonl(staging))

    prepared = []
    staging_id_counts: Counter[str] = Counter()
    mapped_id_counts: Counter[str] = Counter()
    staged_id_map: dict[str, str] = {}

    for path, line_number, record in records:
        record_type = record.get("record_type")
        target = target_for_record(record)
        mapping_error = None
        mapped_id = None
        if target:
            try:
                mapped_id = canonical_id(record_type, record.get("id"), target=target)
            except ValueError as exc:
                mapping_error = str(exc)
        staging_id = record.get("id")
        if isinstance(staging_id, str):
            staging_id_counts[staging_id] += 1
        if mapped_id:
            mapped_id_counts[mapped_id] += 1
            if staging_id_counts[staging_id] == 1:
                staged_id_map[staging_id] = mapped_id
        prepared.append((path, line_number, record, target, mapped_id, mapping_error))

    entries = []
    blocker_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    target_type_counts: Counter[str] = Counter()
    semantic_state_counts: Counter[str] = Counter()

    for path, line_number, record, target, mapped_id, mapping_error in prepared:
        record_type = record.get("record_type")
        blockers = blocker_list(record, predicate_codes)
        if mapping_error:
            blockers = sorted(set(blockers + ["CANONICAL_ID_MAPPING_FAILED"]))
        staging_id = record.get("id")
        if isinstance(staging_id, str) and staging_id_counts[staging_id] > 1:
            blockers = sorted(set(blockers + ["DUPLICATE_STAGING_ID"]))
        if mapped_id and mapped_id_counts[mapped_id] > 1:
            blockers = sorted(set(blockers + ["CANONICAL_ID_COLLISION"]))

        decided_mapping = decided_adjudication_mapping(record, staged_id_map)
        if decided_mapping and decided_mapping["canonical_evidence_projection_id_candidates"]:
            blockers = sorted(set(blockers + ["ADJUDICATION_PROJECTION_BINDING_REQUIRED"]))
        semantic_state = decided_mapping["semantic_state"] if decided_mapping else "CANDIDATE_OR_NEUTRAL"
        semantic_state_counts[semantic_state] += 1
        type_counts[record_type or "<missing>"] += 1
        target_type_counts[target[0] if target else "<unsupported>"] += 1
        for blocker in blockers:
            blocker_counts[blocker] += 1

        target_reason = None
        if is_privacy_projection(record):
            target_reason = "VERA_ADJUDICATED_PRIVACY_MINIMIZED_DERIVATIVE"

        entry = {
            "source_file": path.name,
            "line": line_number,
            "staging_id": staging_id,
            "record_type": record_type,
            "semantic_state": semantic_state,
            "canonical_object_type": target[0] if target else None,
            "canonical_id": mapped_id,
            "canonical_target_reason": target_reason,
            "canonical_id_mapping_error": mapping_error,
            "promotion_ready": not blockers,
            "blockers": blockers,
        }
        if decided_mapping:
            entry["decided_adjudication_mapping"] = decided_mapping
        entries.append(entry)

    return {
        "report_version": "0.3",
        "mode": "NONPROMOTING_STAGING_READINESS",
        "canonical_write_effect": "NONE",
        "selected_staging_directory_name": staging.name,
        "staging_record_count": len(entries),
        "record_type_counts": dict(sorted(type_counts.items())),
        "canonical_object_type_counts": dict(sorted(target_type_counts.items())),
        "semantic_state_counts": dict(sorted(semantic_state_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--staging",
        type=Path,
        required=True,
        help="Any Semantic Atlas staging directory (for example semantic_population_v0.1 or v0.2)",
    )
    parser.add_argument("--vocabulary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    report = build_report(args.staging.resolve(), args.vocabulary.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "report_version": report["report_version"],
        "staging_record_count": report["staging_record_count"],
        "record_type_counts": report["record_type_counts"],
        "canonical_object_type_counts": report["canonical_object_type_counts"],
        "semantic_state_counts": report["semantic_state_counts"],
        "blocker_counts": report["blocker_counts"],
        "canonical_write_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
