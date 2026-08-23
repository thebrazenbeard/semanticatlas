#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from runtime_manifest_v4 import materialization_digests, sha256_text

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "fixtures" / "SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4_FIXED_VECTORS.json"


def _objects(vector: dict) -> list[dict[str, str]]:
    rows = vector.get("objects") or [vector["object"]]
    result: list[dict[str, str]] = []
    for row in rows:
        payload = row["canonical_payload"]
        expected_payload_sha = row["payload_sha256"]
        observed = sha256_text(payload)
        if observed != expected_payload_sha:
            raise AssertionError(
                f"{vector['vector_id']}: payload hash mismatch for {row['object_id']}: "
                f"expected {expected_payload_sha}, observed {observed}"
            )
        result.append(
            {
                "source_path": row["source_path"],
                "object_id": row["object_id"],
                "object_type": row["object_type"],
                "payload_sha256": expected_payload_sha,
            }
        )
    return result


def compute(vector: dict) -> dict[str, str | int]:
    return materialization_digests(
        authority_scope=vector["authority_scope"],
        git_repository_locator=vector["git_repository_locator"],
        git_commit_sha=vector["git_commit_sha"],
        git_ref=vector["git_ref"],
        source_branch=vector["source_branch"],
        materialization_version=vector["materialization_version"],
        objects=_objects(vector),
    )


def verify(vector: dict) -> dict[str, str | int]:
    digests = compute(vector)
    expected = {
        "pathset_sha256": vector["expected_pathset_sha256"],
        "snapshot_sha256": vector["expected_snapshot_sha256"],
        "manifest_sha256": vector["expected_manifest_sha256"],
    }
    observed = {key: digests[key] for key in expected}
    if observed != expected:
        raise AssertionError(
            f"{vector['vector_id']}: digest mismatch\nexpected={expected}\nobserved={observed}"
        )
    return digests


def main() -> int:
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    if data["contract"] != "SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4":
        raise AssertionError("unexpected manifest contract")

    observed_by_id: dict[str, dict[str, str | int]] = {}
    for vector in data["vectors"]:
        observed_by_id[vector["vector_id"]] = verify(vector)
        print(f"PASS {vector['vector_id']}")

    for vector in data["vectors"]:
        predecessor = vector.get("must_differ_from_manifest_vector_id")
        if predecessor:
            if observed_by_id[vector["vector_id"]]["manifest_sha256"] == observed_by_id[predecessor]["manifest_sha256"]:
                raise AssertionError(
                    f"{vector['vector_id']}: repository locator failed to alter manifest digest vs {predecessor}"
                )
            print(f"PASS repository sensitivity {vector['vector_id']} != {predecessor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
