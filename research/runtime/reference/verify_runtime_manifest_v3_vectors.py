#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from runtime_manifest_v3 import materialization_digests, sha256_text

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "fixtures" / "SEMANTIC_ATLAS_RUNTIME_MANIFEST_V3_FIXED_VECTORS.json"


def _objects(vector: dict) -> list[dict[str, str]]:
    if "objects" in vector:
        rows = vector["objects"]
    else:
        rows = [vector["object"]]
    result = []
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


def verify(vector: dict) -> None:
    objects = _objects(vector)
    digests = materialization_digests(
        authority_scope=vector["authority_scope"],
        git_commit_sha=vector["git_commit_sha"],
        git_ref=vector["git_ref"],
        source_branch=vector["source_branch"],
        materialization_version=vector["materialization_version"],
        objects=objects,
    )
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


def main() -> int:
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    if data["contract"] != "SEMANTIC_ATLAS_RUNTIME_MANIFEST_V3":
        raise AssertionError("unexpected manifest contract")
    for vector in data["vectors"]:
        verify(vector)
        print(f"PASS {vector['vector_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
