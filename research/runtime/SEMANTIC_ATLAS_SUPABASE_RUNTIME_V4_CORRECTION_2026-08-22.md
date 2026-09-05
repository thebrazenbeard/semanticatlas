# Semantic Atlas Supabase Runtime V4 Correction — 2026-08-22

Status: `LIVE_SUCCESSOR_UNDER_INDEPENDENT_REVIEW`

Project: Supabase `Vera` (`klmbpaigzeguvnpccqzz`)
Live migration: `20260823003143 semantic_atlas_runtime_sealed_attempt_v4_fix`
Canonical authority: Git remains the canonical Semantic Atlas ledger. Supabase remains a rebuildable runtime/query layer.
Cost constraint: zero-cost only; no paid preview branch, paid agent, or new billable infrastructure used.

## Why this successor exists

The previous live loader contract `20260822225106 semantic_atlas_runtime_manifest_v2_readback_gate` had four independently reproduced material defects:

1. manifest/path ordering depended on database collation rather than frozen UTF-8 byte order;
2. a FAILED snapshot could trap the logical `(authority_scope, git_commit_sha, materialization_version)` identity and prevent a clean successor attempt;
3. Git readback did not seal the materialization, so append remained possible after the readback that was supposed to authorize activation;
4. activation cached freshness time before row-lock acquisition and before expensive verification, allowing the Git readback to become stale by the actual ACTIVE transition.

## Live V4 contract

The migration adds numbered attempt identity and a first-class SEALED state.

Runtime sequence is now:

`LOADING -> SEALED/VERIFIED -> external Git readback -> ACTIVE`

`FAILED` is terminal for an individual attempt but not for the logical operation. An exact logical retry after FAILED creates `attempt_no + 1`. Changed materialization evidence under the same logical operation fails closed and requires a new `materialization_version`.

`seal_runtime_snapshot_v1` performs the expensive deterministic database-side verification before external Git readback. It verifies canonical payload bytes, object count, type counts, pathset digest, materialization digest, and manifest digest, then sets `SEALED/VERIFIED`.

Path and object ordering during seal is explicitly bytewise using `convert_to(...,'UTF8')`, matching off-database UTF-8 byte ordering rather than locale collation.

Runtime objects are machine-immutable after seal. The runtime-object trigger now rejects all UPDATE/DELETE operations and rejects INSERT unless the parent snapshot is `LOADING/UNVERIFIED`, even if the internal runtime-mutation GUC is set.

`confirm_runtime_git_readback_v2` requires an already SEALED/VERIFIED snapshot and requires the external readback timestamp to be later than the DB seal and fresh at confirmation.

`activate_runtime_snapshot_v4` is intentionally lightweight. It locks the snapshot first, takes `clock_timestamp()` after the lock, requires SEALED/VERIFIED state, rechecks the post-seal Git readback freshness immediately before transition, supersedes the prior ACTIVE snapshot for the same scope, and activates the new snapshot. No expensive digest reconstruction occurs after external readback.

Legacy start/confirm/activate wrappers route through the successor behavior so an older caller cannot silently re-enter the unsafe state machine.

Runtime mutation RPC EXECUTE privileges were revoked from PUBLIC/anon/authenticated and granted to service_role. The previously public `mark_runtime_snapshot_failed_v1` surface was included in that hardening.

## Verification already executed

All verification below was rollback-only and left no runtime materialization rows behind.

A byte-order hostile used an expected digest computed outside PostgreSQL for paths whose locale order differs from UTF-8 byte order. The expected byte order was:

`[A, Z, a, z, á, ä]`

The V4 seal accepted the independently computed pathset/materialization/manifest digests.

Additional hostiles passed:

- append after seal rejected;
- direct guarded-GUC object insert after seal rejected by the trigger;
- fresh post-seal Git readback activated successfully;
- FAILED exact retry created a distinct successor `attempt_no=2` instead of returning the unusable FAILED row;
- Git activation readback before seal rejected;
- deliberately stale Git readback rejected at activation with no ACTIVE transition.

Post-test live counts were re-read as:

- `runtime_snapshots = 0`
- `runtime_objects = 0`
- `active_snapshots = 0`

## Real Git-bound rollback pilot

A second rollback-only pilot exercised the complete Git-to-runtime binding path against real repository bytes rather than a purely synthetic manifest.

Exact Git subject:

- commit `33e2c85121814bf90baba85dede920e6f4f17a6b`;
- path `research/validation/SEMANTIC_ATLAS_SYNTHETIC_PILOT_V0.1.jsonl`;
- Git blob `469ff57ff8f5b9433a8e4e3424ad71e9ee6142a7`;
- 12 synthetic validation cases.

The file was freshly fetched from Git at that exact commit. A one-object RESEARCH_STAGING runtime materialization was then constructed from an off-DB canonical payload binding the exact commit, blob, path, and case count. Off-DB pathset, object-stream, payload, and manifest hashes were supplied to the live V4 loader.

The transaction successfully completed:

`start -> append -> seal -> external Git readback confirmation -> activate -> active_runtime_objects readback`

The active derived readback matched the expected exact commit, scope, source path, object ID, and canonical-payload SHA. The transaction was then rolled back, so this proves the real Git-bound state machine without leaving a persistent runtime snapshot or claiming production population.

## Review state

Masa has been assigned an independent live Supabase reliability/security/root-cause review of this exact successor.

Mune has been assigned an independent architecture/integration review against PR #2 and the accepted v0.2 logical-source/source-instance/evidence-span model.

This file records implementation and verification state only. It does not merge PR #2, promote research into canonical Atlas state, populate runtime data, or establish release qualification.
