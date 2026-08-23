# Semantic Atlas Runtime V6 Review Addendum — 2026-08-22

Status: `REVIEW_CORRECTION_APPLIED`

This addendum follows `SEMANTIC_ATLAS_SUPABASE_RUNTIME_V6_REPOSITORY_BOUND_2026-08-22.md`.

## Independent review finding

The first post-V6 independent pass reported H0/M1 with two observations:

1. it inspected the still-present historical function `reject_runtime_direct_mutation_v3` and noted that function does not know about `git_repository_locator`;
2. `canonical_runtime_objects` and `research_runtime_objects` still selected the pre-V6 ten-column projection from `active_runtime_objects`, so scoped consumers lost the newly added repository/ref/manifest/attempt/activation provenance.

## Resolution of observation 1

Fresh trigger introspection shows the live `runtime_snapshots` table has exactly one non-internal snapshot guard:

- trigger: `semantic_atlas_runtime_snapshot_guard_v4`
- function: `semantic_atlas.reject_runtime_direct_mutation_v4()`

That active V4 guard explicitly treats `git_repository_locator` as immutable operation/evidence identity. The historical V3 trigger function is not attached to `runtime_snapshots` and no current raw-DML bypass was found. Therefore the V3-function observation is not a live transition-guard defect.

The historical V3 function was not deleted in this pass. It remains inert legacy schema history rather than an active route.

## Resolution of observation 2

This was a real scoped-projection defect and was corrected by live migration:

`semantic_atlas_runtime_scoped_provenance_views_v6_fix`

All three runtime views now expose the repository-bound provenance set while preserving their previous columns:

- `active_runtime_objects`
- `canonical_runtime_objects`
- `research_runtime_objects`

Added provenance includes:

- `git_repository_locator`
- `git_ref`
- `materialization_version`
- `manifest_contract`
- `attempt_no`
- `activated_at`
- `activation_git_repository_locator`
- `activation_git_readback_sha`
- `activation_git_readback_at`
- `activation_git_readback_source`
- `manifest_sha256`
- `pathset_sha256`
- `snapshot_sha256`
- `expected_object_count`
- `validated_at`
- `sealed_at`

## Rollback verification

A fresh one-object real Git-bound `RESEARCH_STAGING` transaction completed:

`start_v6 -> append -> seal_v3 -> confirm_v4 -> activate_v6 -> research_runtime_objects readback`

The scoped research view was required to return all of the following together:

- repository `github:1342872348`
- exact Git ref `refs/heads/research/semantic-provenance-lineage`
- Manifest V4
- attempt 1
- non-null activation time
- activation repository `github:1342872348`
- activation readback SHA `b012b1370f334add3032e66992730f5528fb9bda`
- activation readback timestamp and source

The hostile passed and the transaction rolled back. Persistent state remains:

- `runtime_snapshots = 0`
- `runtime_objects = 0`
- `active_snapshots = 0`

## Current gate

The scoped-provenance M is corrected. Persistent `RESEARCH_STAGING` remains held for the reviewers to re-read this exact successor state and return either a new material defect or terminal H0/M0.

No merge, canonical promotion, paid service, or persistent runtime population occurred in this correction.
