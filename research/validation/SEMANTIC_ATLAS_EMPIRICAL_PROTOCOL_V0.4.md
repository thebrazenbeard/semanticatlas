# Semantic Atlas Empirical Protocol v0.4

Status: `FROZEN_PRE_HOLDOUT_PROTOCOL`
Supersedes: `SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.3` plus binding addendum v0.3.1
Source corpus head: `2e1982d7c8f507441f157c0b69f98e0ced73ae72`
Runtime snapshot: `52e611ea-4687-4bb8-81d8-477b37cc2bf3`
Service-role search route: `search_current_runtime_objects_v9`
Ranking projection: V7 evidence-only
Generator result projection: `SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V2`

No scored holdout output had been generated when this successor was frozen.

## Why v0.4 exists

The v0.3 pilot correctly removed gold/prompt/evaluator fields from returned candidate payloads, but a second generator-visible leakage path remained: V8 still returned semantic object IDs such as `SYN-CORRECTION-*`, `SYN-PRIVACY-*`, and `SYN-UNRESOLVED-*`, plus source paths. Those identifiers encode evaluation-category hints even though the searchable text itself is clean.

Live migration `semantic_atlas_runtime_current_search_v9_opaque_generator_projection` closes that path. V8 is now postgres-only and V9 is the sole service-role search route. V9 returns:

- snapshot ID;
- opaque candidate digest derived from the sealed payload SHA-256;
- generic object type;
- evidence-only `projected_payload`;
- rank/match/coverage/ambiguity metadata;
- explicit projection version.

It does not return semantic object ID, source path, prompt, gold, category, CEE labels, failure tags, or wrapper metadata to the service-role generator surface.

## Holdout separation

The same ten pilot/debug cases frozen under v0.3 remain permanently exploratory for this qualification round. The same remaining 30 cases remain the scored holdout. No case was added, removed, or exchanged after seeing holdout behavior because no holdout behavior has been generated.

## Thresholds

All numerical thresholds from `SEMANTIC_ATLAS_EMPIRICAL_THRESHOLDS_V0.1.md` remain unchanged.

## Baseline condition

For each holdout case, baseline receives only:

- the exact frozen case prompt;
- all direct frozen `sources[]` records for that case;
- no gold object;
- no Atlas retrieval/current-view output;
- no Atlas-derived labels;
- no evaluator notes or previous answers.

## Atlas-assisted condition

Atlas-assisted receives the same prompt and same complete direct source packet as baseline, plus one bounded V9 retrieval packet produced with:

- authority scope `RESEARCH_STAGING`;
- repository locator `github:1342872348`;
- ref `refs/heads/research/semantic-provenance-lineage`;
- provider-current Git SHA `2e1982d7c8f507441f157c0b69f98e0ced73ae72`;
- allowed object types exactly `['validation_case']`;
- query exactly the frozen case prompt;
- result limit exactly `5`;
- route exactly `search_current_runtime_objects_v9`;
- generator projection exactly `SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V2`.

Top-5 remains the frozen bounded context budget. Retrieval misses and ambiguity remain visible rather than being repaired by post-hoc tuning.

## Assignment and presentation

`SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json` and `SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json` are retained unchanged. They were frozen before any holdout generation and are independent of the V8→V9 surface correction.

Every accepted run must mechanically bind generation records to the frozen condition-specific opaque output IDs and pairwise records to the frozen balanced left/right presentation. Procedural blinding remains procedural rather than cryptographic because the private repository contains both control files.

## Scoring and anti-gaming

The v0.3.1 binding rules remain mandatory:

- individual scores condition-blind and locked before reveal;
- pairwise judgments condition-blind, balanced/randomized, and locked before reveal;
- supporting source IDs bound to actual frozen case sources;
- required-source IDs mandatory for traceability PASS;
- applicability derived from frozen cases, not evaluator choice;
- pilot IDs rejected from holdout records;
- full 30-case coverage required;
- any preferred output introducing a new defect invalidates the judgment instead of disappearing from the denominator;
- assignment IDs and presentation sides deterministically re-derived from the frozen seed.

## Qualification integrity

A scored qualification run additionally requires an execution route that can generate baseline and Atlas-assisted answers under genuine condition isolation using the same model family/configuration. This current project chat cannot count as that isolated generator because it already has access to Atlas architecture, evaluation design, and portions of the gold corpus. Any answers generated here are exploratory only.

No merge, canonical-memory promotion, production deployment, paid service, or protected effect is authorized by this protocol.