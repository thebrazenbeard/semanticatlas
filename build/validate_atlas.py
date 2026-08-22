#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

CANON_DIRS = (
    "sources", "evidence", "nodes", "node_definitions", "propositions",
    "interpretations", "adjudications", "lifecycle",
)
POSITIVE_DEFINITION_DECISIONS = {"ACCEPT", "REFINE", "REOPEN", "REINSTATE"}
EVIDENCE_REQUIRED_CLAIM_CLASSES = {"EXTERNAL_FACT", "UNIVERSAL_ONTOLOGY", "MIXED"}


def iter_objects(root: Path):
    for dirname in CANON_DIRS:
        directory = root / "atlas" / dirname
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            yield path, json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()

    schema = json.loads(
        (root / "schemas/semantic_atlas_v0.1.schema.json").read_text(encoding="utf-8")
    )
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    objects = {}
    by_type = defaultdict(list)

    for path, obj in iter_objects(root):
        for err in validator.iter_errors(obj):
            errors.append(f"{path}: schema: {err.message}")
        object_id = obj.get("id")
        if object_id in objects:
            errors.append(f"{path}: duplicate id {object_id}")
        else:
            objects[object_id] = (path, obj)
        by_type[obj.get("object_type")].append(obj)

    vocabulary_path = root / "vocabulary/relation_types_v0.1.json"
    vocabulary = json.loads(vocabulary_path.read_text(encoding="utf-8"))
    predicate_codes = set()
    for relation_type in vocabulary.get("relation_types", []):
        for err in validator.iter_errors(relation_type):
            errors.append(
                f"{vocabulary_path}: relation {relation_type.get('code')}: {err.message}"
            )
        code = relation_type.get("code")
        if code in predicate_codes:
            errors.append(f"{vocabulary_path}: duplicate predicate code {code}")
        predicate_codes.add(code)
        rid = relation_type.get("id")
        if rid in objects:
            errors.append(f"{vocabulary_path}: duplicate object id {rid}")
        else:
            objects[rid] = (vocabulary_path, relation_type)

    def require_ref(owner_id, ref, expected_type=None):
        if ref not in objects:
            errors.append(f"{owner_id}: unresolved reference {ref}")
            return
        if expected_type and objects[ref][1].get("object_type") != expected_type:
            errors.append(f"{owner_id}: {ref} is not {expected_type}")

    for obj in by_type["evidence_span"]:
        require_ref(obj["id"], obj["source_instance_id"], "source_instance")

    for obj in by_type["node_definition"]:
        require_ref(obj["id"], obj["node_id"], "node")
        require_ref(obj["id"], obj["accepted_by_adjudication_id"], "adjudication")
        if obj.get("predecessor_definition_id"):
            require_ref(obj["id"], obj["predecessor_definition_id"], "node_definition")

    for obj in by_type["proposition"]:
        require_ref(obj["id"], obj["subject_id"])
        if obj["object"]["kind"] == "OBJECT_REF":
            require_ref(obj["id"], obj["object"]["id"])
        for evidence_id in obj["evidence_ids"]:
            require_ref(obj["id"], evidence_id, "evidence_span")
        if obj["predicate_code"] not in predicate_codes:
            errors.append(f"{obj['id']}: unknown predicate_code {obj['predicate_code']}")
        claim_class = obj.get("semantic_authorship", {}).get("claim_class")
        if claim_class in EVIDENCE_REQUIRED_CLAIM_CLASSES and not obj.get("evidence_ids"):
            errors.append(
                f"{obj['id']}: claim_class {claim_class} requires evidence_ids"
            )

    for obj in by_type["interpretation"]:
        for evidence_id in obj["evidence_ids"]:
            require_ref(obj["id"], evidence_id, "evidence_span")
        for proposition_id in obj["candidate_proposition_ids"]:
            require_ref(obj["id"], proposition_id, "proposition")

    for obj in by_type["adjudication"]:
        require_ref(obj["id"], obj["subject_id"])
        for evidence_id in obj["evidence_ids"]:
            require_ref(obj["id"], evidence_id, "evidence_span")
        for older_id in obj["supersedes_adjudication_ids"]:
            require_ref(obj["id"], older_id, "adjudication")

    adjudications = {obj["id"]: obj for obj in by_type["adjudication"]}

    for obj in by_type["lifecycle_event"]:
        require_ref(obj["id"], obj["subject_id"])
        require_ref(obj["id"], obj["caused_by_adjudication_id"], "adjudication")
        if obj.get("successor_id"):
            require_ref(obj["id"], obj["successor_id"])
        cause = adjudications.get(obj["caused_by_adjudication_id"])
        if cause and cause.get("subject_id") != obj.get("subject_id"):
            errors.append(
                f"{obj['id']}: lifecycle cause {cause['id']} adjudicates "
                f"{cause.get('subject_id')} not lifecycle subject {obj.get('subject_id')}"
            )

    for definition in by_type["node_definition"]:
        adjudication = adjudications.get(definition["accepted_by_adjudication_id"])
        if adjudication and not (
            adjudication["subject_id"] == definition["id"]
            and adjudication["decision"] in POSITIVE_DEFINITION_DECISIONS
        ):
            errors.append(
                f"{definition['id']}: accepting adjudication does not positively adjudicate this definition"
            )

    graph = {
        adjudication["id"]: adjudication["supersedes_adjudication_ids"]
        for adjudication in by_type["adjudication"]
    }
    visiting, visited = set(), set()

    def visit(node):
        if node in visiting:
            errors.append(f"adjudication supersession cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for predecessor in graph.get(node, []):
            visit(predecessor)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)

    superseded_adjudication_ids = {
        older_id
        for adjudication in by_type["adjudication"]
        for older_id in adjudication.get("supersedes_adjudication_ids", [])
    }
    active_current_by_subject = defaultdict(list)
    for adjudication in by_type["adjudication"]:
        if (
            adjudication["id"] not in superseded_adjudication_ids
            and adjudication.get("authority_scope") == "CURRENT_CANON"
        ):
            active_current_by_subject[adjudication["subject_id"]].append(adjudication["id"])
    for subject_id, ids in sorted(active_current_by_subject.items()):
        if len(ids) > 1:
            errors.append(
                f"{subject_id}: multiple active CURRENT_CANON adjudications {sorted(ids)}"
            )

    forbidden_source_fields = {
        "current_authority", "historical_authority_at_time", "evidentiary_value",
        "key_topics", "limitations",
    }
    for source in by_type["source_instance"]:
        overlap = forbidden_source_fields.intersection(source)
        if overlap:
            errors.append(
                f"{source['id']}: source registry contains adjudicative fields {sorted(overlap)}"
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        f"PASS: {len(objects)} canonical/vocabulary objects validated; "
        f"{len(predicate_codes)} predicate codes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
