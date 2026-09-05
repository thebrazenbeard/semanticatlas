#!/usr/bin/env python3
"""Provider-neutral reference implementation of SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4.

Research/reference surface only. Git remains canonical; this helper creates no provider effect.
V4 extends V3 by binding an immutable provider repository locator into the manifest.
"""
from __future__ import annotations

import hashlib
from typing import Iterable, Mapping

CONTRACT = "SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4"


def utf8_bytes(value: str) -> bytes:
    return value.encode("utf-8")


def frame_utf8_v1(value: str) -> str:
    """Frame exact text as decimal UTF-8 byte length + ':' + exact value."""
    return f"{len(utf8_bytes(value))}:{value}"


def sha256_text(value: str) -> str:
    return hashlib.sha256(utf8_bytes(value)).hexdigest()


def _byte_key(value: str) -> bytes:
    return utf8_bytes(value)


def pathset_stream(source_paths: Iterable[str]) -> str:
    unique_paths = sorted(set(source_paths), key=_byte_key)
    return "".join(frame_utf8_v1(path) for path in unique_paths)


def object_stream(objects: Iterable[Mapping[str, str]]) -> str:
    ordered = sorted(
        objects,
        key=lambda obj: (_byte_key(obj["source_path"]), _byte_key(obj["object_id"])),
    )
    return "".join(
        frame_utf8_v1(obj["source_path"])
        + frame_utf8_v1(obj["object_id"])
        + frame_utf8_v1(obj["object_type"])
        + frame_utf8_v1(obj["payload_sha256"])
        for obj in ordered
    )


def manifest_stream_v4(
    *,
    authority_scope: str,
    git_repository_locator: str,
    git_commit_sha: str,
    git_ref: str,
    source_branch: str,
    materialization_version: str,
    object_count: int,
    canonical_object_stream: str,
) -> str:
    if object_count < 0:
        raise ValueError("object_count must be nonnegative")
    if not git_repository_locator:
        raise ValueError("git_repository_locator is required")
    return (
        CONTRACT
        + frame_utf8_v1(authority_scope)
        + frame_utf8_v1(git_repository_locator)
        + frame_utf8_v1(git_commit_sha)
        + frame_utf8_v1(git_ref)
        + frame_utf8_v1(source_branch)
        + frame_utf8_v1(materialization_version)
        + frame_utf8_v1(str(object_count))
        + frame_utf8_v1(canonical_object_stream)
    )


def materialization_digests(
    *,
    authority_scope: str,
    git_repository_locator: str,
    git_commit_sha: str,
    git_ref: str,
    source_branch: str,
    materialization_version: str,
    objects: Iterable[Mapping[str, str]],
) -> dict[str, str | int]:
    object_list = list(objects)
    paths = pathset_stream(obj["source_path"] for obj in object_list)
    objects_text = object_stream(object_list)
    manifest = manifest_stream_v4(
        authority_scope=authority_scope,
        git_repository_locator=git_repository_locator,
        git_commit_sha=git_commit_sha,
        git_ref=git_ref,
        source_branch=source_branch,
        materialization_version=materialization_version,
        object_count=len(object_list),
        canonical_object_stream=objects_text,
    )
    return {
        "contract": CONTRACT,
        "object_count": len(object_list),
        "pathset_sha256": sha256_text(paths),
        "snapshot_sha256": sha256_text(objects_text),
        "manifest_sha256": sha256_text(manifest),
    }
