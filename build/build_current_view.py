#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

CANON_DIRS = (
    "sources", "evidence", "nodes", "node_definitions", "propositions",
    "interpretations", "adjudications", "lifecycle",
)


def load_objects(root: Path):
    objects = {}
    for dirname in CANON_DIRS:
        directory = root / "atlas" / dirname
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            obj = json.loads(path.read_text(encoding="utf-8"))
            objects[obj["id"]] = obj
    return objects


def active_adjudications(objects):
    adjudications = {
        object_id: obj for object_id, obj in objects.items()
        if obj.get("object_type") == "adjudication"
    }
    superseded = {
        older_id
        for adjudication in adjudications.values()
        for older_id in adjudication.get("supersedes_adjudication_ids", [])
    }
    retired_subjects = {
        obj["subject_id"]
        for obj in objects.values()
        if obj.get("object_type") == "lifecycle_event"
        and obj.get("event_type") in {"SUPERSEDED", "RETRACTED", "RETIRED"}
    }
    return [
        adjudication
        for adjudication_id, adjudication in sorted(adjudications.items())
        if adjudication_id not in superseded
        and adjudication["decision"] == "ACCEPT"
        and adjudication["authority_scope"] == "CURRENT_CANON"
        and adjudication["subject_id"] not in retired_subjects
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
    subjects = [objects[item] for item in subject_ids if item in objects]
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
        "authority": "NONE_DERIVED_FROM_EXPLICIT_ADJUDICATION",
        "active_adjudication_ids": sorted(item["id"] for item in active),
        "active_subject_ids": subject_ids,
        "graph_edges": graph_edges,
    }

    outdir.mkdir(parents=True, exist_ok=True)
    current_view = outdir / "current_view.json"
    current_view.write_bytes(canonical_json_bytes(view))

    database = outdir / "semantic_index.sqlite"
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
        ("authority", "NONE_DERIVED_FROM_EXPLICIT_ADJUDICATION"),
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

    return {
        "current_view_sha256": hashlib.sha256(current_view.read_bytes()).hexdigest(),
        "semantic_index_sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
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
