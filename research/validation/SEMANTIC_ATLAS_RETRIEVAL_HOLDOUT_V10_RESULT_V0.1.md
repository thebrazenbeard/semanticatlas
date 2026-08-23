# Semantic Atlas Retrieval Holdout V10 Result V0.1

Status: `MEASURED_RETRIEVAL_RESULT`

This record is intentionally narrow. It measures retrieval behavior only. It does not establish Semantic Atlas behavioral superiority, semantic qualification, autobiographical memory, canon, or release readiness.

## Correction history

The first commit of this result record undercounted deployed V10 Top-1 as 25/30 because the evaluator-side diagnostic re-sorted equal-score opaque results by `candidate_digest`. The deployed function itself deterministically orders equal-score candidates by hidden UTF-8 `object_id` before projecting them to opaque digests. A fresh provider-current rerun mapped each digest back to its sealed object only for evaluation and reproduced the function's actual ordering. The corrected deployed V10 Top-1 is **27/30**, not 25/30. The earlier 25/30 value is superseded, not an alternate metric.

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
- `BROAD_AMBIGUOUS`: 8/30
- Mean candidate count: 14.03
- Mean top-coverage tie count: 1.93

The live V10 successor changes only the PostgreSQL text-search configuration/ranking lexemes from `simple` to `english` while preserving the provider-current read gate, explicit object-type scope, evidence-only indexing, opaque candidate digest, safe projected payload, pre-limit ambiguity statistics, deterministic ordering, and V9 generator projection shape.

Actual deployed V10 holdout retrieval, using the function's real hidden-object deterministic tie order:

- Top-1: 27/30 = 90.0%
- Top-3: 29/30 = 96.7%
- Top-5: 29/30 = 96.7%
- Top-10: 29/30 = 96.7%
- Not in top 10: 1/30
- `BROAD_AMBIGUOUS`: 4/30
- Mean candidate count: 4.63
- Mean top-coverage tie count: 1.30

Thus V10 improved Top-1 by 10 percentage points, Top-3 by 10 points, Top-5 by 6.7 points, Top-10 by 3.4 points, halved broad-ambiguity incidence, and reduced the mean candidate set substantially on this frozen retrieval holdout.

## Remaining V10 misses

The intended case is rank 2 for:

- `SYN-IDENTITY-OVERSPLIT-001` — broad ambiguous, five candidates tied at top coverage.
- `SYN-SOURCE-LINEAGE-001` — broad ambiguous, four candidates tied at top coverage.

`SYN-UNRESOLVED-001` remains absent from the first 10 candidates. Its two evidence sources contain only competing candidate values (`Use SHA-256.` / `Use BLAKE3.`) while the query asks which checksum algorithm is authoritative for archive verification, so the evidence itself contains essentially none of the query's authority/archive/verification vocabulary. This is an exposed lexical-retrieval limitation, not grounds to alter the frozen case.

These cases are now exposed evaluation material. They must not be silently rewritten, relabeled, or used as a fresh unseen holdout for another tuned successor.

## Runtime successor

Live migration:

`20260823121232 semantic_atlas_runtime_current_search_v10_english_fts`

Service-role ACL was moved from V9 to V10. V8 and V9 are postgres-only. V10 remains `STABLE SECURITY DEFINER` with fixed `search_path`.

A runtime-contract regression query still returned the intended runtime contract as a strict 100%-coverage candidate. The generator-visible validation payload remains `sources[]` only and does not return semantic case IDs, source paths, prompt, gold, category, CEE labels, failure tags, or evaluator metadata.

## Interpretation

This is a real positive retrieval result: a small, standard PostgreSQL configuration change selected on the excluded pilot improved the frozen 30-case holdout while also reducing ambiguity and candidate-set size.

It is still only a retrieval result. The behavioral A/B qualification remains a separate experiment and must not borrow these retrieval percentages as answer-quality evidence.
