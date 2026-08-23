# Semantic Atlas Empirical Protocol v0.3

Status: `FROZEN_PRE_HOLDOUT_PROTOCOL`
Supersedes: `SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.2`
Source corpus head: `2e1982d7c8f507441f157c0b69f98e0ced73ae72`
Runtime snapshot: `52e611ea-4687-4bb8-81d8-477b37cc2bf3`
Service-role search route: `search_current_runtime_objects_v8`
Search ranking projection: V7 evidence-only
Search result projection: `SEMANTIC_ATLAS_RUNTIME_SEARCH_RESULT_PROJECTION_V1`

No behavioral qualification score had been accepted when this successor was frozen.

## 1. Two pilot findings changed the mechanics

The first exploratory 10-case pilot exposed two issues that must not contaminate the scored holdout.

First, any case used to tune or debug the experiment is no longer holdout evidence. The original 40-case roster therefore remains the frozen source corpus, but the 10 pilot cases are permanently exploratory for this qualification round. The scored holdout is the remaining 30 cases listed in `SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.3.json`.

Second, V7 fixed evaluator leakage in ranking but still returned each matched validation object's full payload. That payload contains prompt/gold/evaluator metadata. A generator receiving raw V7 results could therefore see answer-key material even though the ranking itself was clean.

Live successor migration `semantic_atlas_runtime_current_search_v8_safe_result_projection` closes that path. V7 is now postgres-only; V8 is the sole service-role search route. For `validation_case`, V8 returns only the case `sources[]` projection plus retrieval metadata. Gold, prompt, categories, CEE labels, failure tags, and wrapper metadata are not returned to the service-role search caller.

## 2. Exploratory pilot is excluded from qualification

Pilot case IDs:

- SYN-CORRECTION-004
- SYN-HISTORICAL-AUTHORITY-001
- SYN-FALSE-RETRIEVAL-001
- SYN-PRIVACY-003
- SYN-MEMORY-CLASS-002
- SYN-IDENTITY-OVERMERGE-003
- SYN-IDENTITY-OVERSPLIT-002
- SYN-CEE-AMBIGUITY-004
- SYN-UNRESOLVED-004
- SYN-ADJUDICATION-002

Those ten may be used for harness debugging and hostile testing only. Their outputs, judgments, retrieval success, and failure patterns cannot enter the first qualification metrics.

The remaining 30 frozen cases form the first scored holdout. No behavioral outputs for those 30 had been generated or scored when this protocol was frozen.

## 3. Thresholds

The numerical thresholds from `SEMANTIC_ATLAS_EMPIRICAL_THRESHOLDS_V0.1.md` are retained unchanged and applied to the 30-case holdout:

- critical failures = 0;
- hallucinated provenance = 0;
- false autobiographical promotion = 0;
- privacy-scope critical failures = 0;
- source traceability >= 95%;
- proposition fidelity >= 95%;
- temporal/currentness correctness >= 95%;
- correction/supersession propagation = 100%;
- unresolved precision >= 90%;
- unresolved recall >= 90%;
- identity overmerge critical errors = 0;
- identity oversplit critical errors = 0;
- CEE unsupported-specificity critical errors = 0;
- Atlas wins > baseline wins and has at least a 10 percentage-point net margin across non-tied valid pairwise judgments.

No threshold was relaxed after seeing pilot results.

## 4. Frozen condition packets

### Baseline

For each holdout case, baseline receives:

- the exact case prompt;
- all frozen `sources[]` records for that case;
- no gold object;
- no Atlas retrieval/current-view output;
- no Atlas-derived semantic labels;
- no evaluator notes or earlier answers.

### Atlas-assisted

Atlas-assisted receives the same prompt and the same complete direct `sources[]` packet as baseline, plus one bounded Atlas retrieval packet produced by V8.

The Atlas retrieval packet is frozen as:

- authority scope `RESEARCH_STAGING`;
- repository locator `github:1342872348`;
- ref `refs/heads/research/semantic-provenance-lineage`;
- exact provider-current Git SHA `2e1982d7c8f507441f157c0b69f98e0ced73ae72`;
- explicit allowed object types `['validation_case']`;
- query = the frozen case prompt;
- result limit = 5;
- service-role route = V8 only;
- generator-visible result content = V8 `projected_payload` and retrieval metadata only.

The direct source packet remains authoritative evidence. Atlas candidates are additional retrieval context, not permission to replace the direct source or gold rubric.

Top-5 is frozen as a bounded context budget after the pilot. It is not chosen to guarantee that the intended validation object is retrieved. A retrieval miss is allowed to remain a retrieval miss.

## 5. Pilot retrieval diagnostic

On the ten excluded pilot cases, corrected V8/V7 ordering gave:

- intended top-1: 7/10;
- intended top-5: 9/10;
- intended top-10: 10/10;
- all ten exact-prompt searches used broad fallback;
- candidate sets ranged from 10 to 18;
- the memory-class pilot was structurally ambiguous with three top-coverage candidates.

This is exploratory plumbing evidence only. It is not a behavioral score and it is not a reason to change ranking weights for the holdout.

## 6. Evaluation blinding and mechanical validation

Accepted baseline/Atlas score records remain condition-blind and locked before reveal. Pairwise presentation remains randomized and condition-blind.

The v0.2 self-attack corrections remain binding:

- unblinded score records are invalid;
- supporting source IDs must bind to the frozen case sources and include required gold source IDs for a traceability PASS;
- applicability is derived from the frozen case, so required dimensions cannot be marked NA;
- a preferred answer that introduces a new defect absent from the alternative invalidates that pairwise judgment instead of disappearing from the denominator.

V0.3 generation/score/pairwise/scorer artifacts must bind to this protocol and the 30-case holdout before qualification begins.

## 7. Current effect ceiling

This protocol authorizes no merge, canonical-memory promotion, production deployment, paid service, or protected effect. Git remains canonical; Supabase remains a derived RESEARCH_STAGING runtime/query surface.