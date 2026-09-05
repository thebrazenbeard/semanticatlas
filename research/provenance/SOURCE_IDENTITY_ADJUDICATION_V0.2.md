# Semantic Atlas Source Identity Adjudication v0.2

Date: 2026-08-22
Semantic decider: Vera
Status: research architecture decision; not canonical population or merge authority
Issue #1 coordination record: comment `5383168813`

## Decision

Adopt the source lineage model:

`logical_source -> immutable source_instance/capture -> evidence_span`

### logical_source

Stable neutral identity for the underlying artifact, work, or conversation corpus across recoveries. It may record title, creator/origin when known, artifact family, and explicit lineage/equivalence references.

It must not encode currentness, authority, evidentiary weight, salience, consent, semantic disposition, or canon status.

### source_instance

Immutable retrieval/capture/custody identity. It records provider or retrieval surface, locator, capture/retrieval identity, representation metadata, content digest when available, and provider version token when one actually exists.

Repeated recovery of the same underlying artifact may produce multiple source instances when capture context differs. Shared content identity can support equivalence without erasing capture provenance.

### evidence_span

Exact evidence binds the concrete `source_instance`, not merely the logical source.

## source_version rule

Do not create first-class `source_version` objects by default. Add one only when the provider exposes a version identity meaningfully distinct from both the logical artifact and the concrete capture. Repeated recovery alone does not create a version entity.

## Mapping rule

Staging source classifications containing `CURRENT` or `HISTORICAL` are mapping debt. These are temporal/adjudicative dimensions and must not determine neutral source identity.

## CEE boundary

CEE-derived perspective reconstruction, meaning, salience, uncertainty, and competing interpretations belong in interpretation/adjudication records. CEE never mutates neutral source identity and never upgrades retrieval/capture evidence into authority, currentness, consent, or truth.

## Effect boundary

This decision closes the source-identity semantic question for the research/architecture lane. It does not authorize merge, canonical population, Supabase mutation, deployment, or promotion of research content.
