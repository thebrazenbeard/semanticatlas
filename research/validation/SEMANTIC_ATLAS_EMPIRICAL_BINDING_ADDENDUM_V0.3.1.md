# Semantic Atlas Empirical Binding Addendum v0.3.1

Status: `FROZEN_PRE_OUTPUT_MECHANICAL_SUCCESSOR`
Parent protocol: `SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.3`
No holdout output had been generated or scored when this addendum was frozen.

This addendum closes a mechanical gap in the first v0.3 scorer. The v0.3 protocol already requires frozen opaque assignments and blinded left/right presentation, but `validate_empirical_holdout_v0_3.py` did not itself bind incoming generation/pairwise records to those two manifests. A caller could therefore construct different opaque IDs or presentation sides and still satisfy the scorer's other checks.

For qualification, `validate_empirical_holdout_v0_3.py` is superseded by `validate_empirical_holdout_v0_3_1.py`.

The successor must enforce all v0.3 rules plus:

1. Read `SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json` and `SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json`.
2. Require their case sets to exactly equal the frozen 30-case holdout.
3. Recompute every baseline output ID, Atlas output ID, and pair ID from the frozen assignment seed using SHA-256 and require exact equality.
4. Recompute the balanced presentation rule: sort cases by `SHA256(seed|case_id|SIDE)`; the first 15 have Atlas on the left and the remaining 15 have baseline on the left. Require exact equality with the blinded presentation file and exact 15/15 side balance.
5. Require every generation record's opaque output ID to be the condition-specific ID in the assignment manifest.
6. Require every pairwise judgment's pair ID and left/right output IDs to exactly match the blinded presentation manifest.
7. Validate generation context/output/retrieval digests as lowercase 64-character hexadecimal strings where applicable.
8. Require pairwise `basis` to be a non-empty unique subset of the frozen allowed basis vocabulary.
9. Continue to fail closed on unblinded scoring, pilot-case contamination, bogus supporting source IDs, applicability/NA gaming, condition mismatch, V8/snapshot/result-projection/top-5 mismatch, missing holdout coverage, and any preferred answer that introduces a new defect.

The assignment manifest is generator-facing and the presentation manifest is evaluator-facing. Because both are stored in the same private repository, this is procedural blinding, not cryptographic secrecy. A valid run must still ensure the evaluator is only supplied the evaluator packet until scores/judgments are locked.

No numerical threshold changes are made by this addendum.