#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TYPE_PREFIX = {
    "source_instance": "SRCI",
    "evidence_span": "EVID",
    "evidence_projection": "EPROJ",
    "node": "NODE",
    "node_definition": "NDEF",
    "relation_type": "RTYPE",
    "proposition": "PROP",
    "interpretation": "INTP",
    "adjudication": "ADJ",
    "lifecycle_event": "LIFE",
}
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
CANON_DIRS = (
    "sources", "evidence", "evidence_projections", "nodes", "node_definitions",
    "propositions", "interpretations", "adjudications", "lifecycle",
)


def valid_typed_id(object_type: str, object_id: str) -> bool:
    prefix = TYPE_PREFIX.get(object_type)
    if not prefix or not isinstance(object_id, str):
        return False
    expected = prefix + "-"
    return object_id.startswith(expected) and bool(UUID_RE.fullmatch(object_id[len(expected):]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = []
    count = 0

    for dirname in CANON_DIRS:
        directory = root / "atlas" / dirname
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            obj = json.loads(path.read_text(encoding="utf-8"))
            count += 1
            if not valid_typed_id(obj.get("object_type"), obj.get("id")):
                errors.append(f"{path}: invalid typed UUID id {obj.get('id')!r}")

    vocabulary = json.loads(
        (root / "vocabulary/relation_types_v0.1.json").read_text(encoding="utf-8")
    )
    for relation_type in vocabulary.get("relation_types", []):
        count += 1
        if not valid_typed_id(relation_type.get("object_type"), relation_type.get("id")):
            errors.append(
                f"vocabulary/relation_types_v0.1.json: invalid typed UUID id {relation_type.get('id')!r}"
            )

    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print(f"PASS: {count} canonical/vocabulary typed UUID identities validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
