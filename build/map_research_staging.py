#!/usr/bin/env python3
"""Map provisional Semantic Atlas research staging to canonical-shape readiness.

This tool NEVER writes canonical atlas objects. It reports deterministic ID mapping,
shape targets, and promotion blockers so research staging can remain permissive
without weakening canonical validation.
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
}


def canonical_id(record_type: str, staging_id: str) -> str:
    target = TYPE_MAP.get(record_type)
    if not target:
        raise ValueError(f"unsupported staging record_type {record_type!r}")
    if not isinstance(staging_id, str) or "-" not in staging_id:
        raise ValueError(f"invalid staging id {staging_id!r}")
    payload = staging_id.split("-", 1)[1]
    if not UUID_PAYLOAD_RE.fullmatch(payload):
        raise ValueError(f"invalid staging UUID payload {staging_id!r}")
    return f"{target[1]}-{payload}"


def iter_jsonl(staging: Path):
    for path in sorted(staging.glob("candidate_*.jsonl")):
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


def build_report(staging: Path, vocabulary: Path) -> dict:
    vocab = json.loads(vocabulary.read_text(encoding="utf-8"))
    predicate_codes = {item["code"] for item in vocab.get("relation_types", [])}

    entries = []
    blocker_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    seen_canonical_ids = set()

    for path, line_number, record in iter_jsonl(staging):
        record_type = record.get("record_type")
        target = TYPE_MAP.get(record_type)
        if target:
            mapped_id = canonical_id(record_type, record.get("id"))
        else:
            mapped_id = None
        blockers = blocker_list(record, predicate_codes)
        for blocker in blockers:
            blocker_counts[blocker] += 1
        type_counts[record_type or "<missing>"] += 1
        if mapped_id:
            if mapped_id in seen_canonical_ids:
                blockers = sorted(set(blockers + ["CANONICAL_ID_COLLISION"]))
                blocker_counts["CANONICAL_ID_COLLISION"] += 1
            seen_canonical_ids.add(mapped_id)

        entries.append({
            "source_file": path.name,
            "line": line_number,
            "staging_id": record.get("id"),
            "record_type": record_type,
            "canonical_object_type": target[0] if target else None,
            "canonical_id": mapped_id,
            "promotion_ready": not blockers,
            "blockers": blockers,
        })

    return {
        "report_version": "0.1",
        "mode": "NONPROMOTING_STAGING_READINESS",
        "canonical_write_effect": "NONE",
        "staging_record_count": len(entries),
        "record_type_counts": dict(sorted(type_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", type=Path, required=True)
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
        "staging_record_count": report["staging_record_count"],
        "blocker_counts": report["blocker_counts"],
        "canonical_write_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
