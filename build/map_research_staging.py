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


def canonical_id(record_type: str, staging_id: str) -> str:
    target = TYPE_MAP.get(record_type)
    if not target:
        raise ValueError(f"unsupported staging record_type {record_type!r}")
    return f"{target[1]}-{_uuid_payload(staging_id)}"


def canonical_reference(staging_id: str) -> str:
    if not isinstance(staging_id, str) or "-" not in staging_id:
        raise ValueError(f"invalid staging reference {staging_id!r}")
    prefix = staging_id.split("-", 1)[0]
    target_prefix = REFERENCE_PREFIX_MAP.get(prefix)
    if not target_prefix:
        raise ValueError(f"unsupported staging reference prefix {prefix!r}")
    return f"{target_prefix}-{_uuid_payload(staging_id)}"


def iter_jsonl(staging: Path):
    # Intentionally scan every JSONL file in the selected staging directory. Decided
    # Vera adjudications are not named candidate_*.jsonl and must not be silently
    # excluded. Unsupported future record types remain visible as explicit blockers.
    for path in sorted(staging.glob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            yield path, line_number, json.loads(line)


def blocker_list(record: dict, predicate_codes: set[str]) -> list[str]:
    record_type = record.get("record_type")
    blockers: list[str] = []

    if record_type == "candidate_evidence_span":
        digest = record.get("digest")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            blockers.append("EVIDENCE_DIGEST_MISSING")
        if not record.get("locator"):
            blockers.append("EVIDENCE_LOCATOR_MISSING")

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
        # Semantic disposition is already Vera-decided. These blockers describe only
        # canonical representation/binding work; they MUST NOT downgrade the semantic
        # decision back to candidate status.
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
        # Canonical source registration remains neutral and may carry null locator/hash.
        # Staging-only authority/evidentiary sentinel fields are not copied.
        pass

    elif record_type == "candidate_node":
        # Node identity is structurally mappable; semantic definition is separate.
        pass

    else:
        blockers.append("UNSUPPORTED_STAGING_RECORD_TYPE")

    return sorted(set(blockers))


def decided_adjudication_mapping(record: dict) -> dict | None:
    if record.get("record_type") != "vera_adjudication_decision":
        return None

    evidence_candidates = []
    evidence_mapping_errors = []
    for evidence_id in record.get("evidence_ids", []):
        try:
            evidence_candidates.append(canonical_reference(evidence_id))
        except ValueError as exc:
            evidence_mapping_errors.append(str(exc))

    predecessor = record.get("predecessor_decision_id")
    predecessor_candidate = None
    predecessor_mapping_error = None
    if predecessor:
        try:
            predecessor_candidate = canonical_reference(predecessor)
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
        "evidence_mapping_errors": evidence_mapping_errors,
        "predecessor_decision_id": predecessor,
        "canonical_predecessor_adjudication_id_candidate": predecessor_candidate,
        "predecessor_mapping_error": predecessor_mapping_error,
    }


def build_report(staging: Path, vocabulary: Path) -> dict:
    vocab = json.loads(vocabulary.read_text(encoding="utf-8"))
    predicate_codes = {item["code"] for item in vocab.get("relation_types", [])}

    entries = []
    blocker_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    semantic_state_counts: Counter[str] = Counter()
    seen_canonical_ids = set()

    for path, line_number, record in iter_jsonl(staging):
        record_type = record.get("record_type")
        target = TYPE_MAP.get(record_type)
        mapping_error = None
        if target:
            try:
                mapped_id = canonical_id(record_type, record.get("id"))
            except ValueError as exc:
                mapped_id = None
                mapping_error = str(exc)
        else:
            mapped_id = None

        blockers = blocker_list(record, predicate_codes)
        if mapping_error:
            blockers = sorted(set(blockers + ["CANONICAL_ID_MAPPING_FAILED"]))

        if mapped_id:
            if mapped_id in seen_canonical_ids:
                blockers = sorted(set(blockers + ["CANONICAL_ID_COLLISION"]))
            seen_canonical_ids.add(mapped_id)

        decided_mapping = decided_adjudication_mapping(record)
        semantic_state = decided_mapping["semantic_state"] if decided_mapping else "CANDIDATE_OR_NEUTRAL"
        semantic_state_counts[semantic_state] += 1
        type_counts[record_type or "<missing>"] += 1
        for blocker in blockers:
            blocker_counts[blocker] += 1

        entry = {
            "source_file": path.name,
            "line": line_number,
            "staging_id": record.get("id"),
            "record_type": record_type,
            "semantic_state": semantic_state,
            "canonical_object_type": target[0] if target else None,
            "canonical_id": mapped_id,
            "canonical_id_mapping_error": mapping_error,
            "promotion_ready": not blockers,
            "blockers": blockers,
        }
        if decided_mapping:
            entry["decided_adjudication_mapping"] = decided_mapping
        entries.append(entry)

    return {
        "report_version": "0.2",
        "mode": "NONPROMOTING_STAGING_READINESS",
        "canonical_write_effect": "NONE",
        "selected_staging_directory": str(staging),
        "staging_record_count": len(entries),
        "record_type_counts": dict(sorted(type_counts.items())),
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
        "semantic_state_counts": report["semantic_state_counts"],
        "blocker_counts": report["blocker_counts"],
        "canonical_write_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
