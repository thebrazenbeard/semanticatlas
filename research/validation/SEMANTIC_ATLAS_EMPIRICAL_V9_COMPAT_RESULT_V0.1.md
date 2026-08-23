# Semantic Atlas empirical V9 compatibility result v0.1

Status: `PASS_H0_M0_FOR_COMPATIBILITY_ROUTE_ONLY`

This result does **not** qualify Semantic Atlas behavior, merge the validation branch, promote canonical memory, or authorize production effects. It closes only the bounded runtime-compatibility question needed before a successor empirical protocol can freeze retrieval packets.

## Subject

Git candidate branch: `validation/semantic-atlas-empirical-v0.6`

Route source file parent commit: `afd001bf3c0c32dfd4758ed06c86725c6d2da54d`

Route:

`semantic_atlas.search_current_runtime_objects_empirical_v9_compat_v1`

Current active RESEARCH_STAGING snapshot at validation time:

- snapshot: `cd516166-a3a4-4f41-855a-94d0088c1681`
- repository locator: `github:1342872348`
- ref: `refs/heads/research/cee-always-active-v0.2`
- Git commit: `e68803e2631cf0722fec9a4e7fc39f3ad6b43de4`
- snapshot state: `ACTIVE`
- validation state: `VERIFIED`
- expected objects: `62`
- validation cases: `40`

Fresh Git comparison immediately before route validation confirmed `research/cee-always-active-v0.2` remained exactly `e68803e2631cf0722fec9a4e7fc39f3ad6b43de4`.

## Compatibility semantics

The route is intentionally narrow:

- current `read_current_runtime_objects_v1` gate and ACTIVE-snapshot binding;
- `allowed_object_types` must be exactly `['validation_case']`;
- result limit must be exactly `5`;
- PostgreSQL `simple` FTS;
- strict `websearch_to_tsquery` first;
- broad OR fallback only when no strict match exists;
- coverage descending;
- rank descending;
- hidden UTF-8 `object_id` deterministic tie-break;
- validation-case projected payload contains `sources` only;
- opaque `candidate_digest = payload_sha256`;
- no `object_id`, `source_path`, prompt, gold, or category in returned projection;
- projection label `SEMANTIC_ATLAS_EMPIRICAL_V9_COMPAT_PROJECTION_V1`.

## Oracle 1: frozen V9 treatment survives current snapshot

A read-only SQL reimplementation of the frozen V9/V7 validation treatment was run over all 30 frozen holdout prompts against both:

- old empirical snapshot `52e611ea-4687-4bb8-81d8-477b37cc2bf3`;
- current ACTIVE snapshot `cd516166-a3a4-4f41-855a-94d0088c1681`.

The exact ordered Top-5 `payload_sha256` arrays were compared case by case.

Result:

- case count: `30`
- mismatch count: `0`

This establishes that the current snapshot can reproduce the frozen V9 retrieval treatment for the existing 30-case holdout without importing V10/V11 English-FTS treatment.

## Oracle 2: deployed compatibility route equals deployed V9 route

The deployed `search_current_runtime_objects_v9` and deployed `search_current_runtime_objects_empirical_v9_compat_v1` were executed read-only against the same current ACTIVE snapshot for all 30 frozen prompts.

For each case, ordered result packets were compared after removing only the intentionally different `projection_version` field. Compared fields therefore included:

- candidate digest;
- object type;
- projected sources payload;
- rank;
- match mode;
- query coverage;
- retrieval state;
- candidate count;
- top-coverage tie count;
- allowed object types;
- returned order.

Result:

- case count: `30`
- mismatch count: `0`

## Negative-scope checks

Observed fail-closed behavior:

1. `allowed_object_types=['validation_case','runtime_contract']` was rejected with the route-specific exact-scope exception.
2. `limit=10` was rejected with the route-specific exact-limit exception.
3. Function privilege check:
   - `anon`: EXECUTE `false`
   - `authenticated`: EXECUTE `false`
   - `service_role`: EXECUTE `true`

The migration was applied only to the already-authorized existing RESEARCH_STAGING Supabase project. No data rows, runtime snapshot contents, canonical memory, production database, credentials, paid services, or protected effects were mutated.

## Disposition

`PASS_H0_M0_FOR_COMPATIBILITY_ROUTE_ONLY`

The compatibility uncertainty is closed. The next empirical step may freeze the 30 retrieval packets from this route **before** any successor behavioral generation.

Formal behavioral qualification remains on HOLD until the successor protocol also fixes and cryptographically binds its control root, canonical context/retrieval digest construction, unresolved-state cross-product, and pairwise unresolved defect axes.
