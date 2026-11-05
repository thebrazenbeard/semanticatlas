# Chat-history candidate catalog v0.1

Status: **research tooling only / not installed / no memory promotion**.

`build/chat_history_candidates.py` maps an *already authenticated*, normalized
private conversation stream into two classes of in-memory candidate metadata:

- one coverage manifest for every source conversation, including those with no
  text or matches;
- lexical tag candidates for a caller-approved lexicon of `project`, `topic`,
  `person`, or `entity` IDs and aliases.

It does not read ChatGPT ZIP archives, decrypt the Lappy vault, write files,
network-upload material, infer truth, merge source identities, or create
canonical `atlas/` records. The caller is responsible for authenticated source
readback and for encrypting any persisted candidate metadata. Do not commit
private input, private tag configurations, candidate output, transcripts, or
per-conversation identifiers to this public repository.

## Normalized input contract

Provide an iterable of one mapping per conversation:

```python
{
    "source_fingerprint": "a" * 64,  # actual SHA-256 from verified private source
    "conversation_id": "opaque-private-id",
    "source_create_time": 100,
    "source_update_time": 200,
    "messages": [
        {"message_id": "opaque-message-id", "role": "user",
         "source_time": 120, "text": "synthetic topic mention"},
    ],
}
```

The source and message references are caller-supplied provenance, not a proof
that the input was authenticated. Non-text messages still count toward coverage.
Timestamps must be finite numeric scalars or timezone-aware ISO 8601 strings;
arbitrary metadata strings are rejected instead of copied into candidate output.
Text over one million code points is skipped from lexical matching and exposed
as `oversize_text_messages` debt; it is not silently counted as examined text.

## API

```python
from build.chat_history_candidates import catalog_stream

lexicon = [
    {"tag_type": "project", "tag_id": "synthetic_project",
     "aliases": ["Synthetic Project"]},
]
for record in catalog_stream(verified_conversations, lexicon):
    # Keep records in the authenticated private memory/index boundary.
    consume_private_candidate(record)
```

There is deliberately no bundled private-name lexicon or CLI that writes
plaintext candidate artifacts. Aliases match whole words/phrases and ambiguous
duplicate or Unicode case-equivalent aliases fail closed. The output omits source text and match phrases,
but tag IDs and opaque provenance are **still potentially sensitive metadata**.

Every result is explicitly `HISTORICAL_UNTRUSTED`, `UNADJUDICATED_CANDIDATE`,
and `memory_admitted=false`. An explicit user correction cue is an annotation
only, never a machine adjudication of truth, currentness, or contradiction.
Tag association confidence is `UNKNOWN_NOT_ASSESSED`; even a literal alias in
a negation, quoted passage, or assistant message proves only a lexical mention.
No status or tag creates `CURRENT_CANON` or any other Atlas authority.

## Qualification boundary

The synthetic tests establish deterministic lexical behavior, missing-content
coverage accounting, duplicate rejection, candidate-only semantics, and no
output excerpts. They do **not** establish that all numbered export shards were
parsed, that actual transcript nodes were normalized losslessly, that the
private vault is accessible, or that a model retrieves or uses these records.
Those require separately verified private host and inference gates.
