#!/usr/bin/env python3
"""Execution-root wrapper for the frozen Semantic Atlas empirical v0.5 scorer.

This file does not change the experiment, cases, retrieval packets, assignment,
scoring thresholds, or pairwise rules. It only fails closed unless the exact
validator/dependency/schema blobs match the execution binding committed beside it.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BINDING = ROOT / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_EXECUTION_BINDING_V0.7.json"
EXPECTED_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_EXECUTION_BINDING_V0.7"
EXPECTED_TARGET = "research/validation/validate_empirical_holdout_v0_5.py"


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def die(message: str) -> None:
    raise SystemExit(f"EXECUTION_BINDING_FAIL: {message}")


def main() -> None:
    try:
        binding = json.loads(BINDING.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"cannot load execution binding: {exc}")

    if binding.get("schema_version") != EXPECTED_SCHEMA:
        die("execution binding schema mismatch")
    if binding.get("execution_target") != EXPECTED_TARGET:
        die("execution target mismatch")

    artifacts = binding.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        die("execution artifact list missing")

    seen: set[str] = set()
    for rec in artifacts:
        if not isinstance(rec, dict):
            die("invalid execution artifact record")
        rel = rec.get("path")
        expected = rec.get("git_blob_sha1")
        if not isinstance(rel, str) or not rel or rel in seen:
            die("invalid/duplicate execution artifact path")
        if not isinstance(expected, str) or len(expected) != 40:
            die(f"invalid expected blob SHA for {rel}")
        seen.add(rel)
        path = ROOT / rel
        if not path.is_file():
            die(f"missing execution artifact: {rel}")
        actual = git_blob_sha1(path.read_bytes())
        if actual != expected:
            die(f"execution artifact drift: {rel}: expected {expected}, observed {actual}")

    required = set(binding.get("required_paths", []))
    if not required or seen != required:
        die("execution artifact set differs from frozen required_paths")

    validator = ROOT / EXPECTED_TARGET
    completed = subprocess.run(
        [sys.executable, str(validator), *sys.argv[1:]],
        cwd=ROOT,
        check=False,
    )
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
