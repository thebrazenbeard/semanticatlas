# Semantic Atlas Supabase Runtime V6 Repository Binding — 2026-08-22

Status: `LIVE_SUCCESSOR_UNDER_INDEPENDENT_REVIEW`

Supabase project: `Vera` (`klmbpaigzeguvnpccqzz`)
Live migration: `20260823005615 semantic_atlas_runtime_repository_bound_manifest_v4_v6_fix`
Canonical Git repository: GitHub repository ID `1342872348` (`thebrazenbeard/semanticatlas`)
Canonical repository locator: `github:1342872348`
Cost constraint: zero-cost only.

## Why V6 exists

V5 closed the runtime state-machine defects and passed an independent H0/M0 reliability review, but a later architecture integration pass found one remaining medium-severity boundary defect before persistent research staging: runtime snapshots bound a Git commit and repo-local ref/branch without binding the immutable repository identity. The same commit object can exist in more than one repository, so commit + ref alone does not mechanically prove which repository supplied the final readback.

V6 therefore treats repository identity as part of the runtime materialization operation rather than as commentary.

## Manifest V4

V6 introduces `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4` and does not reinterpret the published V3 contract.

V4 keeps the V3 byte contract:

- UTF-8 exact text;
- no Unicode, whitespace, line-ending, or semantic normalization;
- decimal UTF-8 octet-length framing;
- raw UTF-8 byte ordering for source paths and `(source_path, object_id)` object order.

It adds one framed field to the manifest header: `git_repository_locator`, immediately after `authority_scope` and before `git_commit_sha`.

Repository locator syntax is `provider:stable-repository-id`. The current authoritative locator is `github:1342872348`.

## Live database changes

`runtime_snapshots` now has immutable `git_repository_locator` and `activation_git_repository_locator` fields. Active snapshots require the activation-time repository locator to equal the operation repository locator.

The attempt uniqueness and advisory serialization identity now includes repository locator:

`authority_scope + git_repository_locator + git_commit_sha + materialization_version + attempt_no`.

The snapshot transition guard now treats repository locator as immutable operation/evidence identity. New attempts must use Manifest V4.

New successor RPCs are:

- `start_runtime_snapshot_v6`
- `seal_runtime_snapshot_v3`
- `confirm_runtime_git_readback_v4`
- `activate_runtime_snapshot_v6`

Final Git readback confirmation must supply the same repository locator, ref, and commit SHA recorded by the snapshot. Activation rechecks the stored repository-bound readback after taking the row lock.

`active_runtime_objects` preserves its previous columns and now also exposes repository locator, Git ref, materialization version, manifest contract, attempt number, and activation time as additional provenance fields.

Older manifest/start/seal/confirm/activate entrypoints cannot silently activate a V4 snapshot because their contract checks/signatures do not satisfy the V4 table/RPC requirements.

## Rollback-only hostile verification

All tests below ran against the live V6 functions inside explicit rollback transactions and left zero persistent runtime rows.

### Unicode + repository-binding hostile

A six-object Unicode fixture with expected UTF-8 byte order `[A, Z, a, z, á, ä]` sealed with independently computed digests:

- pathset: `532ac7cb6a1d6fd5a881a3810624bce33f6aa5d76973a2b4005dd7b8fbf714e6`
- materialization: `3eeae8407953ac3ea2c303058c6d92efe276739a0fb62a16a5501c294eff086a`
- Manifest V4: `6b94c71cbf9d0a09b7b07489529de5e43a1dd2d60805b66ffabbac69e8aba391`

The same test also verified:

- guarded mutation of `git_repository_locator` is rejected;
- post-seal readback with repository locator `github:9999999999` is rejected;
- correct readback with `github:1342872348` activates successfully;
- the ACTIVE row binds expected and activation-time repository locators to the same value.

### Real Git-bound pilot

The exact Git evidence used was:

- repository: `github:1342872348`
- commit: `b012b1370f334add3032e66992730f5528fb9bda`
- ref: `refs/heads/research/semantic-provenance-lineage`
- path: `research/validation/SEMANTIC_ATLAS_SYNTHETIC_PILOT_V0.1.jsonl`
- Git blob: `469ff57ff8f5b9433a8e4e3424ad71e9ee6142a7`

A one-object runtime materialization completed start -> append -> seal -> wrong-repository rejection -> exact repository/ref/commit readback -> activate -> `active_runtime_objects` verification, then rolled back.

Expected hashes:

- canonical payload: `dc450b9581379fff7401978ab043e44f1d13a3e118d95961086f7b47fcfbacbd`
- pathset: `530909524b2dcf9538dd0064defb47b3ae561731f9b4912af2c1901af15c58a3`
- materialization: `4504dc17acc500fa4604916010f6e975d4d7354ead695b5b357aed726a5637d7`
- Manifest V4: `f73ac5c94174153b0e05478803a8dfbfc5e94d6f3ce2ca786646c9be1f0af01c`

A repository-sensitivity vector using the same commit/ref/object data but locator `github:9999999999` produces a different Manifest V4 digest: `3652a2a49b44b268d27833b4f87cc1be3a413c55b5e6ae0c5def6e674b11c374`.

## Git-side regression oracle

V4 provider-neutral reference surfaces are:

- `research/runtime/reference/runtime_manifest_v4.py`
- `research/runtime/reference/verify_runtime_manifest_v4_vectors.py`
- `research/runtime/fixtures/SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4_FIXED_VECTORS.json`

The V3 reference and fixed vectors remain intact as historical contract regression evidence.

## Current live state

After both rollback tests:

- `runtime_snapshots = 0`
- `runtime_objects = 0`
- `active_snapshots = 0`

The latest Supabase security advisor pass reported no new Semantic Atlas WARN/ERROR attributable to V6. Existing Semantic Atlas `RLS enabled, no policy` notices remain INFO-level and align with the current deny-by-policy-absence exposure model; unrelated Build Team 2 search-path WARNs were not changed in this Semantic Atlas pass.

## Gate

V6 is ready for independent Masa reliability/security attack and Mune architecture/integration review. Persistent `RESEARCH_STAGING` materialization remains held until that repository-bound successor review closes H0/M0 or any new material finding is corrected.

This document does not merge PR #2, promote research into canonical Atlas state, populate `CANONICAL_LEDGER`, or authorize paid services.
