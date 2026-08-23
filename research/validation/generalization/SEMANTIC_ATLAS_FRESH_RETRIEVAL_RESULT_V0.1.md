# Semantic Atlas Fresh Retrieval Generalization Result V0.1

Status: `MEASURED_FRESH_GENERALIZATION_RESULT`

This result was frozen immediately after the first retrieval run over the fresh corpus. The corpus was committed before the run and was not edited after seeing retrieval output.

## Corpus

- Branch: `validation/semantic-atlas-generalization-v0.1`
- Corpus commit before first run: `f1776040578f4b2bce191ba040b221696c61b590`
- Corpus: `research/validation/generalization/SEMANTIC_ATLAS_FRESH_RETRIEVAL_CORPUS_V0.1.jsonl`
- Cases: 24
- Content scope: non-sensitive Project-engineering and Star Trek research-governance cases drawn from existing Project-backed material

## Retrieval algorithm

The one-shot test reproduced the deployed V10 ranking algorithm over the frozen fresh corpus without modifying the live runtime tables:

- PostgreSQL `english` text-search configuration
- `websearch_to_tsquery('english', prompt)` strict path
- broad OR fallback from `tsvector_to_array(to_tsvector('english', prompt))`
- candidate search text = concatenated `sources[].content`
- ranking = query coverage descending, `ts_rank_cd` descending, UTF-8 case ID ordering as deterministic final tie-break

This isolates retrieval generalization from provider-currentness/runtime plumbing, which was already separately attacked and recorded H0/M0 for live V10.

## First-run result

- Top-1: 23/24 = 95.8%
- Top-3: 23/24 = 95.8%
- Top-5: 24/24 = 100%
- Top-10: 24/24 = 100%
- No hit: 0/24
- Broad ambiguous: 0/24
- Mean candidate count: 7.33

The single non-Top-1 case was `FRESH-TREK-ASYNC-001`, whose intended document ranked 5th. Its Top-1 result was `FRESH-TREK-LIBRARIAN-BINDING-001`; the query ran through BROAD_CANDIDATES with nine candidates and no top-coverage tie.

## Interpretation

The fresh corpus was not used to select or tune V10. The result therefore provides new evidence that the small `english` FTS change generalizes beyond the exposed synthetic holdout: 95.8% Top-1 and 100% Top-5 on this 24-case fresh set.

This remains a retrieval result, not behavioral qualification. No claim is made that retrieval alone improves answer quality, establishes truth, grants memory class, or authorizes release/promotion.

The fresh corpus is now exposed evaluation material and must not be silently rewritten to improve these numbers.
