# Branch and Promotion Policy

Status: ENGINEERING CANDIDATE / REVIEW REQUIRED

## Branch roles

- `main`: validated schema/tooling, neutral source-registry facts, and explicitly adjudicated Atlas state.
- `research/*`: source archaeology, historical reconstruction, unresolved interpretations, candidate propositions, candidate relation semantics, and incomplete provenance.
- `architecture/*` and `feature/*`: schema, validation, migration, and derived-index implementation.

One branch per ontology node is prohibited. Branches represent coherent graph/repository states or implementation work.

## Promotion to main

A pull request may merge canonical Atlas objects only when:

1. deterministic schema and structural validation passes;
2. all referenced IDs resolve;
3. source registration contains no hidden semantic promotion;
4. semantic objects that claim current canon have explicit active adjudication;
5. research-stage weak relations are not presented as stronger typed relations;
6. current views and indexes rebuild deterministically;
7. Vera has adjudicated any new semantic assumption introduced by the change.

Green CI proves shape and integrity. It does not prove semantic truth.

## Historical material

Historical material may be registered as neutral source instances without making its conclusions current.

Historical interpretations, authority-at-time claims, present authority judgments, topic assignments, survival/refinement judgments, and similar semantic assessments belong in separate evidence/proposition/interpretation/adjudication objects.

A later-discovered source is append-only lineage evidence. Its later discovery date does not make it contradictory or current.

## Review discipline

PR descriptions should state:

- exact branch/base;
- object classes changed;
- whether semantic assumptions changed;
- whether any current-canon adjudication changed;
- generated-view hash before/after when applicable;
- known unresolved provenance.

Do not merge a research branch wholesale into `main`.
