# Semantic Atlas Retrieval Holdout V10 Result V0.1

Status: `MEASURED_RETRIEVAL_RESULT`

This record is intentionally narrow. It measures retrieval behavior only. It does not establish Semantic Atlas behavioral superiority, semantic qualification, autobiographical memory, canon, or release readiness.

## Fixed source/runtime cut

- Git repository locator: `github:1342872348`
- Git ref: `refs/heads/research/semantic-provenance-lineage`
- Git commit: `2e1982d7c8f507441f157c0b69f98e0ced73ae72`
- Runtime snapshot: `52e611ea-4687-4bb8-81d8-477b37cc2bf3`
- Frozen holdout manifest: `SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.4`
- Holdout cases: 30
- Pilot/debug cases: 10

The research ref was reread from Git immediately before currentness-gated validation and remained exactly equal to the snapshot commit.

## Candidate selection on pilot only

The existing `simple` PostgreSQL text-search configuration was compared with the built-in `english` text-search configuration on the already excluded 10-case pilot/debug set. No extension, embedding service, external model, paid service, or new corpus annotation was introduced.

Pilot retrieval:

| Configuration | Top-1 | Top-3 | Top-5 | Top-10 | No hit |
|---|---:|---:|---:|---:|---:|
| `simple` | 7/10 | 9/10 | 9/10 | 10/10 | 0 |
| `english` | 9/10 | 10/10 | 10/10 | 10/10 | 0 |

Because `english` improved the excluded pilot without adding evaluator metadata, it was selected as the smallest candidate change for a holdout check.

## Frozen 30-case retrieval comparison

The pre-existing V9 route used `simple` full-text search and the same evidence-only, opaque generator result surface.

V9 holdout retrieval:

- Top-1: 24/30 = 80.0%
- Top-3: 26/30 = 86.7%
- Top-5: 27/30 = 90.0%
- Top-10: 28/30 = 93.3%
- Not in top 10: 2/30

The live V10 successor changes only the PostgreSQL text-search configuration/ranking lexemes from `simple` to `english` while preserving the provider-current read gate, explicit object-type scope, evidence-only indexing, opaque candidate digest, safe projected payload, pre-limit ambiguity statistics, deterministic ordering, and V9 generator projection shape.

Actual deployed V10 holdout retrieval:

- Top-1: 25/30 = 83.3%
- Top-3: 29/30 = 96.7%
- Top-5: 29/30 = 96.7%
- Top-10: 29/30 = 96.7%
- Not in top 10: 1/30

The broad-only predeployment simulation had estimated 27/30 Top-1. That estimate is retired as a hypothesis, not reported as deployed performance, because the live route retains strict-first behavior. The deployed function's measured result is 25/30 Top-1.

## Remaining V10 misses

The intended case is rank 2 for:

- `SYN-IDENTITY-OVERSPLIT-001`
- `SYN-PRIVACY-001`
- `SYN-REPO-IDENTITY-001`
- `SYN-SOURCE-LINEAGE-001`

`SYN-UNRESOLVED-001` remains absent from the first 10 candidates.

These cases are now exposed evaluation material. They must not be silently rewritten, relabeled, or used as a fresh unseen holdout for another tuned successor.

## Runtime successor

Live migration:

`20260823121232 semantic_atlas_runtime_current_search_v10_english_fts`

Service-role ACL was moved from V9 to V10. V8 and V9 are postgres-only. V10 remains `STABLE SECURITY DEFINER` with fixed `search_path`.

A runtime-contract regression query still returned the intended runtime contract as a strict 100%-coverage candidate. The generator-visible validation payload remains `sources[]` only and does not return semantic case IDs, source paths, prompt, gold, category, CEE labels, failure tags, or evaluator metadata.

## Interpretation

This is a real positive retrieval result: a small, standard PostgreSQL configuration change selected on the excluded pilot improved the frozen 30-case holdout at Top-1, Top-3, Top-5, Top-10, and no-hit rate.

It is still only a retrieval result. The behavioral A/B qualification remains a separate experiment and must not borrow these retrieval percentages as answer-quality evidence.
