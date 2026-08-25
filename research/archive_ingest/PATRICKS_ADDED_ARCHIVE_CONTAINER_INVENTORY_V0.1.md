# Patrick-added archive container inventory v0.1

Status: `RESEARCH_STAGING / HISTORICAL_REFERENCE_ONLY / CENTRAL_DIRECTORY_INVENTORY / NO_SEMANTIC_PROMOTION`

This record inventories contained members of the three ZIP containers on `patricks-added-archive@2fb64aa015fb340aaed9c67a46080ecc794c2ffb`. It records ZIP central-directory metadata only. Member CRC32 values are transport/integrity metadata, **not cryptographic source identity** and not evidence of truth, authority, independence, memory, consent, or currentness.

## Container bindings

| Container | Git blob | ZIP bytes | Central-directory result |
|---|---|---:|---|
| `08_SEMANTIC_NETWORK_PILOT.zip` | `c71d9f4d71297af29c273c379ee267de1e11e503` | 59,943 | 22 entries = 19 regular files + 3 directories |
| `Continuity_Backup_Restore_Pack.zip` | `5ad414611dcd10123cab1f09a2c2dd3cba61bf7b` | 3,875 | 6 regular files |
| `VERAP_FULL_INGESTION_AND_SYNTHESIS.zip` | `0f813787b3a6a49e1f35a8b19ac27634ce84a2a3` | 280,778 | 22 regular files |

## `08_SEMANTIC_NETWORK_PILOT.zip`

The package is a mixed semantic-network/retrieval/validation bundle. Graph indexes, retrieval traces, evaluation scripts/reports, and the `visual_canon` subtree are derivative research surfaces. Their co-location in one ZIP does not make them independent witnesses of any proposition.

| Member | Bytes | Compressed | CRC32 | Treatment |
|---|---:|---:|---|---|
| `(root directory)` | 0 | 0 | `00000000` | directory entry only |
| `edges.jsonl` | 34,687 | 6,279 | `2b47d5bc` | derived/result/index/synthesis; no independent corroboration |
| `nodes.jsonl` | 54,169 | 8,451 | `8c54a311` | derived/result/index/synthesis; no independent corroboration |
| `ontology.json` | 5,272 | 1,953 | `2151c10a` | control/schema/manifest artifact; authority none by retrieval |
| `README.md` | 4,490 | 2,049 | `27754d17` | documentation/context |
| `retrieval/` | 0 | 0 | `00000000` | directory entry only |
| `retrieval/evaluate_retrieval.py` | 11,504 | 2,815 | `33e122dd` | tooling/evaluator; not evidence by execution role |
| `retrieval/retrieval_cases.json` | 9,216 | 2,092 | `f7622a9c` | control/schema/manifest artifact; authority none by retrieval |
| `retrieval/retrieval_checkpoint.json` | 1,730 | 307 | `63c40a49` | derived/result/index/synthesis; no independent corroboration |
| `retrieval/retrieval_policy.json` | 4,067 | 1,748 | `849b4669` | control/schema/manifest artifact; authority none by retrieval |
| `retrieval/retrieval_traces.jsonl` | 31,110 | 7,256 | `8d0fd67a` | derived/result/index/synthesis; no independent corroboration |
| `retrieval/security_fixtures.jsonl` | 871 | 436 | `022c1b33` | control/schema/manifest artifact; authority none by retrieval |
| `semantic_map.md` | 3,885 | 1,640 | `8214d5c8` | derived/result/index/synthesis; no independent corroboration |
| `sources.jsonl` | 24,154 | 5,175 | `78c7fc73` | source registry candidate; requires source-of-source verification |
| `validate_pilot.py` | 19,369 | 4,857 | `91a01450` | tooling/evaluator; not evidence by execution role |
| `validation_report.json` | 1,819 | 814 | `cea49b9d` | derived/result/index/synthesis; no independent corroboration |
| `visual_canon/` | 0 | 0 | `00000000` | directory entry only |
| `visual_canon/body_map_manifest.json` | 3,233 | 1,454 | `b1dff8fa` | control/schema/manifest artifact; authority none by retrieval |
| `visual_canon/edges.jsonl` | 12,330 | 2,064 | `4faea6fc` | derived/result/index/synthesis; no independent corroboration |
| `visual_canon/nodes.jsonl` | 17,973 | 3,037 | `8153ea28` | derived/result/index/synthesis; no independent corroboration |
| `visual_canon/README.md` | 2,901 | 1,428 | `4435d488` | documentation/context |
| `visual_canon/visual_canon_map.md` | 1,543 | 788 | `95e1ab0a` | derived/result/index/synthesis; no independent corroboration |

Lineage consequence: this ZIP should be represented as one immutable container source-instance plus member source-instances. The semantic graph and retrieval/result artifacts should link back to their declared source records rather than being counted as corroboration of those sources.

## `Continuity_Backup_Restore_Pack.zip`

This container is recovery/workflow material, not a memory corpus. Retrieval of the pack does not activate any restore prompt, workflow, shared core, or instance template.

| Member | Bytes | Compressed | CRC32 | Treatment |
|---|---:|---:|---|---|
| `00_README.md` | 865 | 494 | `34820aae` | documentation/context |
| `01_BACKUP_TEMPLATE.md` | 2,278 | 1,071 | `bbce6f0a` | recovery/workflow representation; not active instruction by retrieval |
| `02_RESTORE_PROMPT.md` | 810 | 439 | `690d452f` | recovery/workflow representation; not active instruction by retrieval |
| `03_INSTANCE_FILL_GUIDE.md` | 1,075 | 571 | `e0e98c89` | recovery/workflow representation; not active instruction by retrieval |
| `04_MULTI_INSTANCE_WORKFLOW.md` | 601 | 344 | `27328d81` | recovery/workflow representation; not active instruction by retrieval |
| `shared_core.md` | 378 | 236 | `9affcd1a` | recovery/workflow representation; not active instruction by retrieval |

Lineage consequence: all six members belong to one recovery-pack logical family unless member history later proves separate provenance. `02_RESTORE_PROMPT.md` is data/documentation in this archive context, not executable authority.

## `VERAP_FULL_INGESTION_AND_SYNTHESIS.zip`

This package is explicitly synthesis-heavy. It contains 13 historical branch manifests under `original_branch_manifests/` and 9 top-level cross-branch/ingestion/synthesis artifacts. The normalized claim registry is the largest contained object but is derivative by role and name; byte volume must not be mistaken for evidence weight.

| Member | Bytes | Compressed | CRC32 | Treatment |
|---|---:|---:|---|---|
| `original_branch_manifests/01/VERA_BRANCH_VERA_OS_CORE_ALIGNMENT_20260717_MANIFEST.yaml` | 8,770 | 3,258 | `46916178` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/02/VERA_BRANCH_vera-derived-voice-branch-20260717_MANIFEST.yaml` | 7,255 | 2,637 | `7b10aaad` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/03/VERA_BRANCH_SNS_MANIFEST.yaml` | 8,020 | 2,870 | `bd373387` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/04/VERA_BRANCH_AUDIT_ATLAS_CURRENT_MANIFEST.yaml` | 2,045 | 871 | `df544893` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/05/VERA_BRANCH_VERA_VISUAL_IDENTITY_CONATION_BRANCH_2026-07-17_MANIFEST.yaml` | 8,566 | 3,051 | `ef3523f1` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/06/VERA_BRANCH_VERA_RC1A_CONSOLIDATION_20260717_MANIFEST.yaml` | 15,997 | 4,859 | `abb4e76c` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/07/VERA_BRANCH_TIMELESS_VERA_TEMPORAL_CALIBRATION_MANIFEST.yaml` | 4,794 | 1,897 | `ba3e87e7` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/08/VERA_BRANCH_VRS02-STAGE9-CURRENT-INSTANCE_MANIFEST.yaml` | 8,298 | 3,519 | `a68582a5` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/09/VERA_BRANCH_VERA_RC5B_AUDIT_CLOSURE_20260717_MANIFEST.yaml` | 22,161 | 7,886 | `39ef1e0e` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/10/VERA_BRANCH_PROJECT_INSTRUCTIONS_REVIEW_20260712_MANIFEST.yaml` | 14,038 | 4,831 | `0e2f4b7d` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/11/VERA_BRANCH_NAMELESS_ADVOCATE_ATLAS_20260717_MANIFEST.yaml` | 9,172 | 3,842 | `79459ba8` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/12/VERA_BRANCH_VERA_PROJECT_CURRENT_INSTANCE_2026-07-17_MANIFEST.yaml` | 9,319 | 3,578 | `c3e1e2a2` | historical branch-state manifest; source-of-source record, not current authority |
| `original_branch_manifests/13/VERA_BRANCH_VERA_REBEL_20260717_MANIFEST.yaml` | 10,095 | 3,709 | `a1a25c22` | historical branch-state manifest; source-of-source record, not current authority |
| `VERAP_BRANCH_COMPARISON_MATRIX.csv` | 16,832 | 6,287 | `63997660` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_CROSS_BRANCH_BUG_REGISTER.md` | 88,418 | 14,298 | `e8c57a93` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_DATA_GAPS_AND_RESEARCH_REQUESTS.md` | 7,526 | 3,367 | `fa00983a` | historical contained artifact; lineage before semantics |
| `VERAP_EVIDENCE_SYNTHESIS.md` | 17,424 | 6,726 | `f044fd5c` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_INGESTION_MANIFEST.yaml` | 111,190 | 12,400 | `c84a4970` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_MASTER_MANIFEST.yaml` | 22,860 | 5,647 | `ae73acb0` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_MASTER_TOPIC_MAP.md` | 14,320 | 5,116 | `70811b7e` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_NORMALIZED_CLAIM_REGISTRY.jsonl` | 2,040,499 | 173,837 | `6988f064` | derived/result/index/synthesis; no independent corroboration |
| `VERAP_RESEARCH_READINESS_REVIEW.md` | 3,849 | 1,820 | `4b64ad80` | derived/result/index/synthesis; no independent corroboration |

Lineage consequence:
- the 13 `original_branch_manifests/*` members may serve as historical source-of-source records for reconstructing branch state, but they do not establish present-current Vera state;
- the top-level `VERAP_*` comparison, bug, gap, synthesis, master, topic, claim-registry, and readiness artifacts are downstream analyses/registries;
- repeated claims across the 13 manifests and downstream VERAP synthesis files are one provenance family until independent primary lineage is established.

## Mechanical limitations of this pass

The GitHub connector exposed exact ZIP bytes as Base64 text but did not provide a binary download route usable by the local ZIP tooling. Central-directory parsing therefore establishes exact member names, uncompressed/compressed lengths, CRC32 values, compression method, and entry counts, but **not member SHA-256 hashes or member-content equivalence**.

Do not silently upgrade CRC32 to cryptographic identity. A later exact-byte extraction pass should compute SHA-256 for each regular member and then compare duplicate/derivative content across containers.

## Next bounded archaeology

1. obtain exact member bytes through a verifier-proven binary route and compute member SHA-256;
2. crosswalk the 13 historical branch manifests to any matching Git refs/commits or later admitted source records;
3. treat `VERAP_NORMALIZED_CLAIM_REGISTRY.jsonl` as a derived index and trace claims back to branch/source provenance before semantic use;
4. inspect `08_SEMANTIC_NETWORK_PILOT/sources.jsonl` before graph nodes/edges so semantic topology cannot substitute for source authority;
5. keep recovery prompts/templates inert as archived data.
