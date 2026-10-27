#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path

CANON_DIRS = (
    "sources", "evidence", "evidence_projections", "nodes", "node_definitions",
    "propositions", "interpretations", "adjudications", "lifecycle",
)

POSITIVE_CURRENT_DECISIONS = {"ACCEPT", "REFINE", "REOPEN", "REINSTATE"}
TERMINAL_EVENT_TYPES = {"SUPERSEDED", "RETRACTED", "RETIRED"}


def load_objects(root: Path):
    objects = {}
    for dirname in CANON_DIRS:
        directory = root / "atlas" / dirname
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            obj = json.loads(path.read_text(encoding="utf-8"))
            if obj["id"] in objects:
                raise ValueError(f"duplicate canonical object id {obj['id']} at {path}")
            objects[obj["id"]] = obj

    # Canonical validation treats vocabulary relation types as first-class
    # reference targets. The direct derived builder must use the same domain.
    vocabulary = root / "vocabulary" / "relation_types_v0.1.json"
    if vocabulary.exists():
        for obj in json.loads(vocabulary.read_text(encoding="utf-8")).get("relation_types", []):
            if obj["id"] in objects:
                raise ValueError(f"duplicate canonical object id {obj['id']} in {vocabulary}")
            objects[obj["id"]] = obj
    return objects


def active_adjudications(objects):
    adjudications = {
        object_id: obj for object_id, obj in objects.items()
        if obj.get("object_type") == "adjudication"
    }
    # An adjudication's supersession chain must stay within its subject.
    # Cross-subject lineage belongs in explicit semantic propositions, not
    # an unrelated decision's authority-revocation chain.
    successors = {object_id: [] for object_id in adjudications}
    pending_predecessors = {}
    for adjudication_id, adjudication in adjudications.items():
        predecessors = adjudication.get("supersedes_adjudication_ids", [])
        if len(predecessors) != len(set(predecessors)):
            raise ValueError(f"duplicate adjudication supersession in {adjudication_id}")
        pending_predecessors[adjudication_id] = len(predecessors)
        for older_id in predecessors:
            older = adjudications.get(older_id)
            if older is None:
                raise ValueError(
                    f"unresolved adjudication supersession {adjudication_id} -> {older_id}"
                )
            if older.get("subject_id") != adjudication.get("subject_id"):
                raise ValueError(
                    f"cross-subject adjudication supersession {adjudication['id']} -> {older_id}"
                )
            successors[older_id].append(adjudication_id)

    # The validator checks these invariants, but this builder is also a direct
    # CLI/public function. Invalid chains must not silently erase or multiply
    # the derived CURRENT_CANON state when callers skip validation.
    ready = deque(sorted(
        object_id for object_id, count in pending_predecessors.items() if count == 0
    ))
    visited_count = 0
    while ready:
        older_id = ready.popleft()
        visited_count += 1
        for successor_id in sorted(successors[older_id]):
            pending_predecessors[successor_id] -= 1
            if pending_predecessors[successor_id] == 0:
                ready.append(successor_id)
    if visited_count != len(adjudications):
        raise ValueError("adjudication supersession cycle")

    superseded_ids = {
        older_id
        for adjudication in adjudications.values()
        for older_id in adjudication.get("supersedes_adjudication_ids", [])
    }
    active_ids = set(adjudications) - superseded_ids
    current_by_subject = {}
    for adjudication_id in sorted(active_ids):
        adjudication = adjudications[adjudication_id]
        if adjudication.get("authority_scope") != "CURRENT_CANON":
            continue
        subject_id = adjudication["subject_id"]
        if subject_id in current_by_subject:
            raise ValueError(
                f"multiple active CURRENT_CANON adjudications for {subject_id}: "
                f"{current_by_subject[subject_id]}, {adjudication_id}"
            )
        current_by_subject[subject_id] = adjudication_id

    # Lifecycle events are immutable history, but only an event whose causing
    # adjudication is still active affects the current projection. If a later
    # REOPEN/REINSTATE/REFINE adjudication supersedes the earlier disposition,
    # the older lifecycle event remains in history without remaining effective.
    active_terminal_subjects = {
        obj["subject_id"]
        for obj in objects.values()
        if obj.get("object_type") == "lifecycle_event"
        and obj.get("event_type") in TERMINAL_EVENT_TYPES
        and obj.get("caused_by_adjudication_id") in active_ids
    }

    return [
        adjudication
        for adjudication_id, adjudication in sorted(adjudications.items())
        if adjudication_id in active_ids
        and adjudication["decision"] in POSITIVE_CURRENT_DECISIONS
        and adjudication["authority_scope"] == "CURRENT_CANON"
        and adjudication["subject_id"] not in active_terminal_subjects
    ]


def canonical_json_bytes(value) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def build(root: Path, outdir: Path):
    objects = load_objects(root)
    active = active_adjudications(objects)
    subject_ids = sorted({item["subject_id"] for item in active})
    missing = sorted(set(subject_ids) - set(objects))
    if missing:
        raise ValueError(f"unresolved active adjudication subject: {missing}")
    subjects = [objects[item] for item in subject_ids]
    propositions = [
        item for item in subjects if item.get("object_type") == "proposition"
    ]

    graph_edges = [
        {
            "proposition_id": proposition["id"],
            "subject_id": proposition["subject_id"],
            "predicate_code": proposition["predicate_code"],
            "object_id": proposition["object"]["id"],
        }
        for proposition in propositions
        if proposition["object"]["kind"] == "OBJECT_REF"
    ]
    graph_edges.sort(
        key=lambda item: (
            item["subject_id"], item["predicate_code"],
            item["object_id"], item["proposition_id"],
        )
    )

    view = {
        "schema_version": "0.1",
        "derived": True,
        "authority": "NONE_DERIVED_FROM_ACTIVE_EXPLICIT_ADJUDICATION_CHAIN",
        "active_adjudication_ids": sorted(item["id"] for item in active),
        "active_subject_ids": subject_ids,
        "graph_edges": graph_edges,
    }

    outdir.mkdir(parents=True, exist_ok=True)
    # Construct off-path: a failed materialization cannot first replace
    # previously published derived artifacts.
    with tempfile.TemporaryDirectory(prefix=".semanticatlas-build-", dir=outdir) as stage_name:
        staging = Path(stage_name)
        current_view = staging / "current_view.json"
        current_view.write_bytes(canonical_json_bytes(view))

        database = staging / "semantic_index.sqlite"
        if database.exists():
            database.unlink()
        connection = sqlite3.connect(database)
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=OFF")
        connection.executescript(
            """
            CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE current_subject(id TEXT PRIMARY KEY, object_type TEXT NOT NULL, json TEXT NOT NULL);
            CREATE TABLE graph_edge(proposition_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, predicate_code TEXT NOT NULL, object_id TEXT NOT NULL);
            """
        )
        connection.execute(
            "INSERT INTO meta VALUES(?, ?)",
            ("schema_version", "0.1"),
        )
        connection.execute(
            "INSERT INTO meta VALUES(?, ?)",
            ("authority", "NONE_DERIVED_FROM_ACTIVE_EXPLICIT_ADJUDICATION_CHAIN"),
        )
        for obj in sorted(subjects, key=lambda item: item["id"]):
            connection.execute(
                "INSERT INTO current_subject VALUES(?, ?, ?)",
                (
                    obj["id"], obj["object_type"],
                    json.dumps(obj, sort_keys=True, separators=(",", ":")),
                ),
            )
        for edge in graph_edges:
            connection.execute(
                "INSERT INTO graph_edge VALUES(?, ?, ?, ?)",
                (
                    edge["proposition_id"], edge["subject_id"],
                    edge["predicate_code"], edge["object_id"],
                ),
            )
        connection.commit()
        connection.execute("VACUUM")
        connection.close()

        view_sha = hashlib.sha256(current_view.read_bytes()).hexdigest()
        index_sha = hashlib.sha256(database.read_bytes()).hexdigest()
        # These two replacements are NOT a fully atomic multi-file commit.
        # Consumers requiring that property need a versioned bundle pointer.
        os.replace(database, outdir / "semantic_index.sqlite")
        os.replace(current_view, outdir / "current_view.json")
    return {
        "current_view_sha256": view_sha,
        "semantic_index_sha256": index_sha,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.root.resolve(), args.out.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
