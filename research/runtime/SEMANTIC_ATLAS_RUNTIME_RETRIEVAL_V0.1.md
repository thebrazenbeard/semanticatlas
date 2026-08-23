# Semantic Atlas Runtime Retrieval V0.1

Status: `RESEARCH_RUNTIME_IMPLEMENTED`

## Scope

This contract defines the first zero-cost retrieval surface over the repository-bound Semantic Atlas research runtime. Git remains canonical. Supabase is a derived/query layer.

The runtime must not infer currentness from an `ACTIVE` database row alone. Every currentness-sensitive read is bound to a fresh external provider readback of repository identity, exact ref, and current commit SHA.

## Current-read gate

Live migration:

`20260823010932 semantic_atlas_runtime_current_read_gate_v1`

`read_current_runtime_objects_v1` fails closed unless:

- the requested authority scope has an ACTIVE snapshot;
- repository locator matches that snapshot;
- Git ref matches that snapshot;
- fresh provider SHA matches the snapshot commit;
- provider readback evidence is no more than 60 seconds old at the database check;
- the readback does not predate snapshot activation.

The returned state is current **as of the provider readback cut**. It is not a claim that the remote ref cannot move after that cut.

## Search surface

Live migration:

`semantic_atlas_runtime_current_search_v1`

`search_current_runtime_objects_v1` wraps the current-read gate and performs deterministic PostgreSQL full-text retrieval over the JSON runtime representation. It uses the `simple` text-search configuration, ranks with `ts_rank_cd`, caps requested results at 100, and returns:

- snapshot ID;
- object ID/type;
- source path;
- payload SHA-256;
- JSON payload;
- rank.

This is intentionally a lexical retrieval baseline, not an embedding model and not a claim of semantic equivalence. It is useful because its behavior is deterministic, zero-cost, provider-neutral, and easy to compare against later retrieval systems.

## First materialized validation corpus

The runtime has successfully materialized the 12-case frozen synthetic validation corpus from:

`research/validation/SEMANTIC_ATLAS_SYNTHETIC_PILOT_V0.1.jsonl`

The materialization represents each frozen test case as one `validation_case` object. Each JSON payload includes the case plus repository/commit/blob/source-path provenance. Payloads are deterministically serialized JSON research representations; they are not falsely labeled as raw-source byte spans.

The 12-case materialization used Manifest V4 and successfully passed database-side count, payload, pathset, object-stream, and manifest verification before repository-bound external Git readback and activation.

Currentness-gated retrieval was then exercised against the active case set. Representative lexical searches returned the intended case:

- `current maximum upload size` -> `SYN-CURRENTNESS-001`
- `Alex stopped replying review` -> `SYN-CEE-AMBIGUITY-001`
- `Phoenix same entity identity` -> `SYN-IDENTITY-OVERMERGE-001`

These results establish functional deterministic retrieval only. They do not establish behavioral superiority of Semantic Atlas, which remains a separate empirical A/B validation question.

## Boundaries

Research runtime retrieval must preserve the architecture distinctions already adopted by Semantic Atlas:

- source/provenance is not interpretation;
- historical evidence is not current authority;
- repetition/salience is not consent or authority;
- semantic similarity is not identity;
- retrieval is not autobiographical recollection;
- a database ACTIVE state is not provider currentness;
- a successful deterministic search is not proof that the returned proposition is true.

CEE may be applied to perspective-sensitive material after retrieval, but CEE does not grant fact, intent, consent, authority, or memory class. Clues remain clues rather than conclusions.

No CANONICAL_LEDGER population, research promotion, PR merge, embedding service, paid AI service, or external publication is implied by this runtime retrieval contract.
