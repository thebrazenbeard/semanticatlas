# Semantic Atlas Runtime Currentness Gate V0.1

Status: `RESEARCH_RUNTIME_ACTIVE`

Live migration: `20260823010932 semantic_atlas_runtime_current_read_gate_v1`

## Problem

An `ACTIVE` runtime snapshot means the database successfully accepted and activated an exact Git materialization at a particular provider-readback cut. It does **not** mean the Git ref can never move afterward.

Git remains canonical. Therefore `ACTIVE` must not be silently promoted into an eternal claim of current Git authority.

## Rule

`ACTIVE != CURRENT_PROVIDER_REF_VERIFIED_NOW`.

A currentness-sensitive runtime read requires a fresh external provider readback of:

- repository identity;
- exact Git ref;
- current commit SHA;
- readback time and source.

The caller must distinguish the provider-readback time from database record time and from the snapshot's earlier activation time.

## Live read gate

`semantic_atlas.read_current_runtime_objects_v1(...)` accepts:

- `authority_scope`
- `git_repository_locator`
- `git_ref`
- `git_readback_sha`
- `readback_at`
- `readback_source`

It fails closed unless:

1. an ACTIVE snapshot exists for the requested scope;
2. repository locator equals the ACTIVE snapshot repository;
3. ref equals the ACTIVE snapshot ref;
4. fresh provider SHA equals the ACTIVE snapshot commit SHA;
5. the readback was recorded within 60 seconds of the database check and is not future-skewed by more than one minute;
6. the currentness readback does not predate activation.

Only then does it return that snapshot's active runtime objects.

The 60-second requirement limits the age of the evidence cut. It cannot make a remote Git ref metaphysically immutable after the readback; claims based on the result are current **as of that verified readback cut**, not proof of uninterrupted future equality.

## First persistent canary

The first persistent Semantic Atlas runtime materialization was activated in `RESEARCH_STAGING` using the corrected repository-bound V6/V4 path:

- snapshot: `c5dc0eac-0e43-4416-8377-1f7725f89bd0`
- repository: `github:1342872348`
- Git commit: `fa92d4f682913761ead04da80a48c145bd0dc33d`
- Git ref: `refs/heads/research/semantic-provenance-lineage`
- manifest contract: `SEMANTIC_ATLAS_RUNTIME_MANIFEST_V4`
- manifest SHA-256: `65431b78820a5385b75ec94837fc832aa8d1b35eb8f7f773093eed4b53b41071`
- object: `VALIDATION-PILOT-V0.1`
- object payload SHA-256: `45d1b5e1ba94511e6fcb299e28cef6307307db3ec1e6735024b50548fd9e2a5a`
- source path: `research/validation/SEMANTIC_ATLAS_SYNTHETIC_PILOT_V0.1.jsonl`
- source Git blob: `469ff57ff8f5b9433a8e4e3424ad71e9ee6142a7`
- scope: `RESEARCH_STAGING` only

After activation, a fresh external ref readback still resolved the branch to `fa92d4f...`, and `read_current_runtime_objects_v1` returned the canary object.

## Intended stale-ref hostile

Committing this document advances the research branch beyond the canary's bound commit. The active canary is intentionally left in place so the next verification can prove the distinction:

- diagnostic `ACTIVE` state may remain;
- a fresh provider readback of the moved branch must cause `read_current_runtime_objects_v1` to reject the old active snapshot as stale;
- a successor RESEARCH_STAGING snapshot can then be materialized from the new exact head, superseding the old active snapshot.

This is a currentness regression test, not a failure of append-only runtime history.

No CANONICAL_LEDGER population, semantic promotion, PR merge, paid service, or external publication is authorized or implied by this research runtime gate.
