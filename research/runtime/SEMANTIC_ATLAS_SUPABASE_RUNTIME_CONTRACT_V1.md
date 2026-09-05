# Semantic Atlas Supabase Runtime Contract V1

Date: 2026-08-22
Status: research/runtime contract; no canonical semantic promotion

## Authority boundary

Git remains the canonical Semantic Atlas ledger. Supabase is a rebuildable materialized/query runtime only. A Supabase row, ACTIVE snapshot, capture event, or runtime query result cannot independently create semantic truth, currentness, consent, authority, identity, or canonical status.

Research and canonical runtime states are separate authority scopes: `RESEARCH_STAGING` and `CANONICAL_LEDGER`. ACTIVE in one scope does not imply ACTIVE or authoritative in the other.

## Live Supabase location

Existing Supabase project: `Vera`.
Isolated schema: `semantic_atlas`.

The current stable runtime contract is the successor of these live migrations:

- `semantic_atlas_runtime_capture_v1`
- `semantic_atlas_snapshot_scope_v1_fix`
- `semantic_atlas_runtime_capture_hardening_v2_fix`
- `semantic_atlas_runtime_capture_hardening_v3`
- `semantic_atlas_runtime_manifest_v2_readback_gate`

Earlier runtime framing is superseded by `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V2`.

## Salience capture flow

Semantically salient live events may create candidate captures without a user issuing a database command. Capture is a candidate opportunity, not promotion.

Current flow:

1. contextual/CEE-informed salience detection identifies a permitted MEDIUM/HIGH event;
2. `capture_semantic_event_v1` performs atomic insert-or-observe idempotency;
3. exact replay returns the same event; changed payload under the same idempotency key fails closed;
4. Vera adjudicates the candidate;
5. Git write, when warranted, occurs in the correct semantic/research lane;
6. `GIT_WRITE_CONFIRMED` is valid only with exact commit SHA, explicit Git authority scope, exact ref, matching external readback SHA, and non-empty object refs;
7. old outcomes remain immutable. Corrections are append-only successors, never in-place rewrites.

Privacy-minimized capture remains derivative semantic representation and does not become exact evidence merely because it is stored or hashed.

## Runtime materialization flow

Stable loader sequence:

1. Validate and build a deterministic materialization from an exact Git commit and authority scope.
2. Externally read back the Git ref and exact commit.
3. Call `start_runtime_snapshot_v3` with expected manifest/pathset/materialization digests and object count.
4. For each object call `append_runtime_object_v2` with exact canonical UTF-8 JSON text in `canonical_payload`.
5. Supabase parses the payload to JSONB and independently computes SHA-256 from the exact persisted UTF-8 `canonical_payload` bytes.
6. Immediately before activation, externally re-read the Git ref.
7. Call `confirm_runtime_git_readback_v1` with exact ref, matching commit SHA, retrieval timestamp, and retrieval source.
8. Call `activate_runtime_snapshot_v3`.
9. Activation recomputes object count, per-object payload bindings, pathset digest, materialization digest, and manifest digest from stored state.
10. Only after all checks pass does one transaction supersede the prior ACTIVE snapshot in the same authority scope and activate the new snapshot.

If any load, readback, count, digest, representation, or activation check is ambiguous or fails, the previous ACTIVE snapshot remains untouched. Failed/ambiguous loads are inspection-first; never erase state to manufacture apparent atomicity.

## Manifest contract V2

Contract identifier: `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V2`.

All variable textual fields use unambiguous UTF-8 byte-length framing:

`<UTF8_BYTE_LENGTH>:<VALUE>`

The database helper is `semantic_atlas.frame_utf8_v1(text)`.

This framing is used because delimiter-joined tuples are ambiguous when source paths, IDs, types, or other text may contain tabs/newlines.

For each runtime object, the deterministic object record is the concatenation of framed:

1. `source_path`
2. `object_id`
3. `object_type`
4. `payload_sha256`

Object records are sorted by `(source_path, object_id)` and concatenated with no unframed separator.

The pathset stream is the concatenation of framed distinct `source_path` values sorted lexically.

The manifest stream is:

1. literal `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V2`
2. framed `authority_scope`
3. framed `git_commit_sha`
4. framed `git_ref`
5. framed `source_branch`
6. framed `materialization_version`
7. framed decimal object count
8. framed complete object stream

SHA-256 is computed over UTF-8 bytes of each deterministic stream.

## Mutation boundary

`service_role` has read access plus guarded RPC execution, but no raw INSERT/UPDATE/DELETE privilege on runtime snapshots, runtime objects, capture events, or capture outcomes. Runtime state transitions are RPC/guard controlled.

Anonymous/authenticated external roles have no Semantic Atlas schema/table/function route.

## Git replay/rematerialization identity

A runtime operation is keyed by `(authority_scope, git_commit_sha, materialization_version)`.

An exact replay must supply identical ref, branch, expected digests, and expected object count and returns the existing snapshot ID. Changed materialization evidence under the same operation identity fails closed. A genuinely changed materializer must use a new `materialization_version`.

## External Git readback ceiling

Supabase cannot independently query GitHub merely by possessing database state. The loader must perform the external ref readback and provide its result. `confirm_runtime_git_readback_v1` binds that observation and requires it to be fresh (within five minutes) before activation. The loader remains responsible for ensuring the readback came from the intended Git provider and ref.

## Non-goals

This runtime does not replace Git, adjudicate semantics, infer consent, create identity continuity, turn research into canon, or make a stored representation primary evidence. It exists to make already-governed Semantic Atlas state fast to query and deterministic to rebuild.
