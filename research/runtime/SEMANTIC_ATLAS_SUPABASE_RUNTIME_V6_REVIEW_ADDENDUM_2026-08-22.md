# Semantic Atlas Runtime V6 Review Addendum — 2026-08-22

Status: `REVIEW_CORRECTIONS_APPLIED`

This addendum follows `SEMANTIC_ATLAS_SUPABASE_RUNTIME_V6_REPOSITORY_BOUND_2026-08-22.md`.

## First independent review finding

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

`20260823010022 semantic_atlas_runtime_scoped_provenance_views_v6_fix`

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

A fresh one-object real Git-bound `RESEARCH_STAGING` transaction completed:

`start_v6 -> append -> seal_v3 -> confirm_v4 -> activate_v6 -> research_runtime_objects readback`

The scoped research view was required to return repository `github:1342872348`, exact Git ref, Manifest V4, attempt number, activation time, activation repository, activation readback SHA/time/source, and the materialization hashes. The hostile passed and rolled back.

## Second independent review finding: legacy confirm bypass

A later integration pass found a separate material compatibility-route defect. Although V6 introduced repository-bound `confirm_runtime_git_readback_v4`, `service_role` still had execute privilege on historical `confirm_runtime_git_readback_v1`, `v2`, and `v3`. V1/V2 forwarded to V3. V3 could refresh the activation readback SHA/time/source without supplying a repository locator.

That created a concrete bypass sequence for a V4 snapshot: perform a legitimate repository-bound V4 confirmation once, then later refresh only the timestamp/SHA/source through legacy V3. The previously stored repository locator would remain equal to the expected repository locator, so `activate_runtime_snapshot_v6` could mistake the later repository-unbound refresh for a fresh repository-bound readback.

## Legacy route closure

Closed by live migration:

`20260823010215 semantic_atlas_runtime_disable_legacy_repository_unbound_rpcs_v6_fix`

The migration makes two independent protections explicit.

First, `confirm_runtime_git_readback_v3` now fails closed when invoked on a Manifest V4 snapshot with the error that repository-unbound Git readback is disabled for V4 and `confirm_runtime_git_readback_v4` is required.

Second, `service_role` execute privilege was revoked from obsolete runtime entrypoints:

- `start_runtime_snapshot_v2`, `v3`, `v4`, `v5`
- `seal_runtime_snapshot_v1`, `v2`
- `confirm_runtime_git_readback_v1`, `v2`, `v3`
- `activate_runtime_snapshot_v1`, `v2`, `v3`, `v4`, `v5`

Current service-role runtime mutation path is therefore the repository-bound successor family:

- `start_runtime_snapshot_v6`
- `append_runtime_object_v2`
- `seal_runtime_snapshot_v3`
- `confirm_runtime_git_readback_v4`
- `activate_runtime_snapshot_v6`
- the guarded failure-marking route where applicable

Fresh ACL readback confirmed `confirm_runtime_git_readback_v1/v2/v3` are postgres-only, while `confirm_runtime_git_readback_v4`, `start_runtime_snapshot_v6`, `seal_runtime_snapshot_v3`, and `activate_runtime_snapshot_v6` remain executable by postgres/service_role.

## Exact legacy-confirm hostile verification

A rollback-only Manifest V4 snapshot was built with repository `github:1342872348`, commit `b012b1370f334add3032e66992730f5528fb9bda`, exact research ref, the existing validation-manifest object, and materialization version `legacy-confirm-hostile-v4`.

For that materialization version the independently computed Manifest V4 digest is:

`68dee8f6995d3edb961161faccd5c79e276c639df5abde6f15ce1e35c700cc42`

The hostile then completed:

`start_v6 -> append -> seal_v3 -> legitimate confirm_v4 -> attempted legacy confirm_v3`

The legacy V3 refresh was rejected, and the stored activation readback source was verified not to have changed to the repository-unbound test source. The transaction rolled back.

## Current persistent state

After all V6 correction hostiles:

- `runtime_snapshots = 0`
- `runtime_objects = 0`
- `active_snapshots = 0`

## Current gate

The repository-binding, scoped-provenance, and legacy-confirm compatibility defects are corrected. Persistent `RESEARCH_STAGING` remains held for independent re-review of the exact live successor state and Git Manifest V4 regression surfaces. The next acceptable reviewer result is either a new concrete material defect or terminal H0/M0.

No merge, canonical promotion, paid service, or persistent runtime population occurred in these corrections.
