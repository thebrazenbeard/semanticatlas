# Semantic Atlas Behavioral Pilot V0.1

Status: `FROZEN_EXPLORATORY_BEHAVIORAL_PILOT`

Purpose: test practical answer-quality effect after V10 retrieval generalized on a fresh 24-case corpus. This is deliberately smaller and simpler than formal empirical qualification. It may produce useful research evidence but cannot by itself satisfy the separate frozen qualification thresholds.

## Source cut

- Fresh corpus branch: `validation/semantic-atlas-generalization-v0.1`
- Fresh corpus commit before retrieval run: `f1776040578f4b2bce191ba040b221696c61b590`
- Fresh retrieval result commit: `c489afad3b56b8d48117cda938078999c5c70220`
- Retrieval configuration: V10-equivalent PostgreSQL `english` FTS strict-first + broad fallback.
- Independent reproduction: no concrete mismatch; 23/24 Top-1, 24/24 Top-5, 0 no-hit.

## Case selection

Select exactly 12 cases by sorting all 24 fresh case IDs by lowercase hexadecimal SHA-256(case_id UTF-8 bytes) ascending and taking the first 12. No semantic cherry-picking.

Selected order:

1. P01 = `FRESH-RETRIEVAL-TRUTH-001`
2. P02 = `FRESH-SOURCE-MODEL-001`
3. P03 = `FRESH-CEE-BOUNDARY-001`
4. P04 = `FRESH-TREK-MEDIUM-001`
5. P05 = `FRESH-SHARED-PROJECT-MEMORY-001`
6. P06 = `FRESH-BASIC-MEMORY-001`
7. P07 = `FRESH-TREK-ASYNC-001`
8. P08 = `FRESH-FILENAME-COLLISION-001`
9. P09 = `FRESH-ARCHIVE-INSTRUCTION-001`
10. P10 = `FRESH-GIT-CANONICAL-001`
11. P11 = `FRESH-TREK-ZIP-PRESENCE-001`
12. P12 = `FRESH-TREK-LIBRARIAN-BINDING-001`

## Conditions

`BASELINE`: generator receives the user-style prompt only. No Git, Supabase, web, Project-history, corpus, or other lookup for that case. It must answer from its available model/context knowledge and may state uncertainty.

`ATLAS`: generator receives the same prompt plus only the generator-visible evidence returned by the frozen V10-equivalent Top-1 retrieval result. It receives no case ID, category, gold answer, evaluator label, or hidden candidate metadata.

For P01-P06 and P08-P12 the fresh retrieval run placed the intended evidence object at Top-1. P07 is intentionally left as the observed retrieval miss: its Top-1 evidence is the Librarian-binding object, while the intended async object ranked fifth. Do not repair P07 for the behavioral pilot.

## Counterbalance

Two independent worker contexts generate outputs so worker identity is balanced across conditions:

- Mune: BASELINE for P01,P03,P05,P07,P09,P11; ATLAS for P02,P04,P06,P08,P10,P12.
- Masa: ATLAS for P01,P03,P05,P07,P09,P11; BASELINE for P02,P04,P06,P08,P10,P12.

Each worker must generate only the condition packet supplied to it and must not inspect the counterpart condition before output lock.

## Output rule

For each packet, return one concise answer of no more than 120 words. Do not mention the experiment, packet ID, Semantic Atlas, retrieval, or condition unless the prompt itself requires it.

## Judgment

After both generators lock outputs, a third independent context receives randomized A/B pairs with condition labels removed. Judge `A`, `B`, or `TIE` on:

- factual / source fidelity;
- correct uncertainty and unresolved handling;
- provenance/currentness discipline where relevant;
- privacy/authority/identity boundaries where relevant;
- direct usefulness and clarity.

Any invented authority, fabricated closure, false autobiographical recollection, privacy violation, or unsupported identity merge is a critical defect.

## Interpretation ceiling

Report raw wins/losses/ties and critical defects. This is an exploratory behavioral signal only. Do not call it formal qualification, release authorization, canonical promotion, or proof of autobiographical memory.
