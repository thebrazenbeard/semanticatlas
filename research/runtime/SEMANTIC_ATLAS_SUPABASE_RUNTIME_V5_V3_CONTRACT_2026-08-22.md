# Semantic Atlas Supabase Runtime V5 / Manifest V3 — 2026-08-22

Status: `LIVE_SUCCESSOR_UNDER_INDEPENDENT_REVIEW`

Supabase project: `Vera` (`klmbpaigzeguvnpccqzz`)
Live high-water migration: `20260823003901 semantic_atlas_runtime_manifest_v3_transition_guard_v5`
Research branch predecessor: `9774360f9025fd03079cf99cb9b159c0b958518b`
Cost posture: zero-cost only.

## Why V5 supersedes V4

V4 closed the four original loader failures, but independent review found one material contract-identity error: the byte-ordering algorithm had changed from provider/default collation to explicit UTF-8 bytewise ordering while the manifest still called itself `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V2`.

That would let two different algorithms exist under one contract identifier. V4 is therefore historical/nonterminal for final loader binding even though its four mechanical corrections remain useful evidence.

V5 makes the changed algorithm explicit as `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V3` and hardens snapshot transitions so the compact `attempt_no` design has machine-enforced semantics rather than depending only on trusted RPC behavior.

## Current V3 manifest contract

Framing remains byte-length-prefixed UTF-8 with no normalization:

`octet_length(UTF8(value)) || ':' || value`

Pathset ordering is the raw UTF-8 byte ordering of `source_path`.

Object ordering is raw UTF-8 byte ordering of `(source_path, object_id)`.

The object stream frames, in order:

`source_path`, `object_id`, `object_type`, `payload_sha256`.

The manifest stream is:

`SEMANTIC_ATLAS_RUNTIME_MANIFEST_V3`

followed by framed:

`authority_scope`, `git_commit_sha`, `git_ref`, `source_branch`, `materialization_version`, decimal object count, and the complete framed object stream.

No Unicode, whitespace, line-ending, JSON, or semantic normalization is permitted by this representation contract.

## Attempt and lifecycle rules

A new attempt starts `LOADING/UNVERIFIED`.

The expensive deterministic verification step seals it as `SEALED/VERIFIED`. At seal time the database verifies canonical payload bytes, payload SHA, object count, type counts, bytewise pathset digest, bytewise object/materialization digest, and V3 manifest digest.

Only a sealed snapshot may accept the external Git readback used for activation.

Final activation locks the snapshot first, takes current wall-clock time after lock acquisition, rechecks that the post-seal Git readback is still fresh, and performs only the lightweight same-scope transition to `ACTIVE`. A previous ACTIVE snapshot in that scope becomes `SUPERSEDED` in the same transaction.

A `FAILED` attempt remains immutable history. An exact retry of the same logical materialization may create a new numbered attempt. Changed materialization evidence under the same `(authority_scope, git_commit_sha, materialization_version)` fails closed and requires a new materialization version.

## Machine-enforced guards

The runtime snapshot trigger now enforces immutable operation/evidence identity within an attempt and legal transition families:

`LOADING -> SEALED`

`LOADING -> FAILED`

`SEALED -> SEALED` only for external Git-readback fields

`SEALED -> ACTIVE`

`SEALED -> FAILED`

`ACTIVE -> SUPERSEDED`

`FAILED` and `SUPERSEDED` are terminal.

Runtime snapshot deletion is forbidden.

Runtime objects are insertable only while their parent is `LOADING/UNVERIFIED`. Runtime-object UPDATE and DELETE are forbidden. This remains enforced even if the internal guarded-mutation GUC is present.

## Compatibility surfaces

Existing start, seal, Git-confirmation, and activation compatibility entrypoints route through the V3-manifest successor. The old function names therefore do not preserve the obsolete V2 hashing algorithm as a hidden bypass.

Runtime mutation RPC EXECUTE is limited to `postgres` and `service_role`; PUBLIC, anon, and authenticated do not have EXECUTE on the guarded runtime mutation entrypoints.

## Verification completed

Rollback-only V5 hostiles passed for:

- V3 UTF-8 bytewise manifest construction;
- direct immutable `git_ref` mutation rejection even with the guarded mutation GUC enabled;
- direct illegal `LOADING -> ACTIVE` transition rejection;
- V3 `LOADING -> SEALED -> external Git readback -> ACTIVE` success;
- rejection of a historical V2 manifest digest under the V3 contract;
- zero persistent runtime rows after rollback.

A second rollback-only test bound the V3 loader to real Git repository bytes:

- Git commit `9774360f9025fd03079cf99cb9b159c0b958518b`;
- path `research/validation/SEMANTIC_ATLAS_SYNTHETIC_PILOT_V0.1.jsonl`;
- blob SHA `469ff57ff8f5b9433a8e4e3424ad71e9ee6142a7`;
- scope `RESEARCH_STAGING`.

One validation-manifest object completed start, append, seal, fresh exact Git readback, activation, and `active_runtime_objects` readback under the V3 contract. Exact commit, scope, path, object ID, and canonical-payload SHA matched. The transaction was rolled back.

Fresh post-test live counts remain:

`runtime_snapshots = 0`

`runtime_objects = 0`

`active_snapshots = 0`

Fresh ACL readback shows the primary V5 mutation RPCs plus append/fail entrypoints are executable only by `postgres` and `service_role`.

## Remaining review boundary

Masa owns independent live database/security/reliability attack of this exact successor. Mune owns architecture/integration review and the Git-side runtime binding contract. Their agreement is cross-checking, not statistically independent empirical proof.

No persistent runtime population, CANONICAL_LEDGER activation, PR #2 merge, semantic research promotion, or release qualification follows from these tests.