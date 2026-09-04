#!/usr/bin/env python3
"""Split research source ledger into neutral source facts and research-only judgments.

The output intentionally does not promote semantic judgments. Interpretive/adjudicative
fields are preserved in a separate candidate stream for Vera to adjudicate later.
"""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

MIGRATION_NAMESPACE = uuid.UUID("c3f5b8ba-8f52-5fa8-a6c2-4c8468088e0f")
NEUTRAL_FIELDS = (
    "source_id", "title", "source_class", "embedded_time_start",
    "embedded_time_end", "retrieval_surface",
)
JUDGMENT_FIELDS = (
    "historical_authority_at_time", "current_authority", "evidentiary_value",
    "key_topics", "limitations",
)


def canonical_source_id(legacy_id: str) -> str:
    return f"SRCI-{uuid.uuid5(MIGRATION_NAMESPACE, legacy_id)}"


def split_record(record: dict) -> tuple[dict, dict]:
    missing = [key for key in NEUTRAL_FIELDS if key not in record]
    if missing:
        raise ValueError(f"source record missing neutral fields: {missing}")

    legacy_id = str(record["source_id"])
    neutral = {
        "schema_version": "0.1",
        "object_type": "source_instance",
        "id": canonical_source_id(legacy_id),
        "legacy_source_id": legacy_id,
        "title": record["title"],
        "source_class": record["source_class"],
        "retrieval_surface": record["retrieval_surface"],
        "embedded_time_start": record["embedded_time_start"],
        "embedded_time_end": record["embedded_time_end"],
        "locator": None,
        "content_sha256": None,
    }

    judgment = {
        "legacy_source_id": legacy_id,
        "source_instance_id": neutral["id"],
        "research_only": True,
        "unadjudicated_fields": {
            key: record.get(key) for key in JUDGMENT_FIELDS if key in record
        },
    }
    extras = sorted(set(record) - set(NEUTRAL_FIELDS) - set(JUDGMENT_FIELDS))
    if extras:
        judgment["unclassified_extra_fields"] = {key: record[key] for key in extras}
    return neutral, judgment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("--neutral-out", type=Path, required=True)
    parser.add_argument("--judgments-out", type=Path, required=True)
    args = parser.parse_args()

    neutral_records = []
    judgment_records = []
    seen = set()

    for line_number, line in enumerate(
        args.input_jsonl.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        neutral, judgment = split_record(json.loads(line))
        if neutral["id"] in seen:
            raise ValueError(
                f"duplicate canonical source identity at line {line_number}: {neutral['id']}"
            )
        seen.add(neutral["id"])
        neutral_records.append(neutral)
        judgment_records.append(judgment)

    neutral_records.sort(key=lambda item: item["id"])
    judgment_records.sort(key=lambda item: item["source_instance_id"])
    args.neutral_out.parent.mkdir(parents=True, exist_ok=True)
    args.judgments_out.parent.mkdir(parents=True, exist_ok=True)

    args.neutral_out.write_text(
        "".join(
            json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n"
            for item in neutral_records
        ),
        encoding="utf-8",
    )
    args.judgments_out.write_text(
        "".join(
            json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n"
            for item in judgment_records
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
