"""Nonpromoting, in-memory catalog candidates for normalized chat exports.

This module does not read an account export, create Atlas objects, persist text,
or promote historical assertions. A trusted private adapter must authenticate
the source and provide one normalized conversation at a time.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime


TAG_TYPES = frozenset({"project", "topic", "person", "entity"})
TAG_ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CORRECTION = re.compile(
    r"(?:^|[.!?]\s+)(?:correction\s*:|i meant\b|to correct my earlier\b|i was wrong\b)",
    re.IGNORECASE,
)
MAX_ALIASES = 500
MAX_TEXT_LENGTH = 1_000_000
ISO_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})"
)


def _nonempty(value: object, name: str) -> str:
    if (not isinstance(value, str) or not 1 <= len(value) <= 512
            or value.strip() != value or any(ord(char) < 32 for char in value)):
        raise ValueError(f"{name} must be a bounded, nonempty, unpadded single-line string")
    return value


def _timestamp(value: object, name: str) -> str | int | float | None:
    """Preserve source times as untrusted scalars, never arbitrary source objects."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a scalar timestamp")
    if isinstance(value, (int, float)) and math.isfinite(value):
        return value
    if isinstance(value, str) and ISO_TIMESTAMP.fullmatch(value):
        try:
            if datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None:
                return value
        except ValueError:
            pass
    raise ValueError(f"{name} must be a bounded scalar timestamp")


def _fingerprint(value: object) -> str:
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise ValueError("source_fingerprint must be a lowercase SHA-256 hex digest")
    return value


def _candidate_id(parts: list[str]) -> str:
    canonical = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return "CHTC-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compile_lexicon(entries: Sequence[Mapping[str, object]]) -> tuple[tuple[str, str, re.Pattern[str]], ...]:
    """Compile caller-approved labels; there is deliberately no default PII lexicon.

    An alias may not map to two tag IDs, even if the type differs. This makes
    otherwise ambiguous matching fail closed rather than assigning meanings.
    """
    if not isinstance(entries, (list, tuple)):
        raise ValueError("lexicon must be an ordered list or tuple")
    patterns: list[tuple[str, str, re.Pattern[str]]] = []
    used_ids: set[str] = set()
    used_aliases: set[str] = set()
    alias_patterns: list[tuple[str, re.Pattern[str]]] = []
    for item in entries:
        if not isinstance(item, Mapping):
            raise ValueError("each lexicon entry must be an object")
        tag_type = item.get("tag_type")
        tag_id = item.get("tag_id")
        if tag_type not in TAG_TYPES or not isinstance(tag_id, str) or not TAG_ID.fullmatch(tag_id):
            raise ValueError("invalid tag_type or tag_id")
        if tag_id in used_ids:
            raise ValueError("duplicate tag_id")
        used_ids.add(tag_id)
        aliases = item.get("aliases")
        if not isinstance(aliases, (list, tuple)) or not aliases:
            raise ValueError("aliases must be a nonempty list")
        for alias in aliases:
            if not isinstance(alias, str) or not 1 <= len(alias) <= 128 or alias.strip() != alias:
                raise ValueError("alias must be nonempty, bounded and unpadded")
            folded = alias.casefold()
            if folded in used_aliases:
                raise ValueError("ambiguous or duplicate alias")
            pattern = re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", re.IGNORECASE)
            if any(old_pattern.fullmatch(alias) or pattern.fullmatch(old_alias)
                   for old_alias, old_pattern in alias_patterns):
                raise ValueError("ambiguous Unicode-equivalent alias")
            used_aliases.add(folded)
            if len(used_aliases) > MAX_ALIASES:
                raise ValueError("lexicon exceeds bounded alias count")
            # Match phrases at word boundaries, never a substring of a larger token.
            alias_patterns.append((alias, pattern))
            patterns.append((tag_type, tag_id, pattern))
    return tuple(sorted(patterns, key=lambda part: (part[1], part[2].pattern)))


def catalog_conversation(
    conversation: Mapping[str, object],
    lexicon: tuple[tuple[str, str, re.Pattern[str]], ...],
) -> tuple[dict, list[dict]]:
    """Return one coverage manifest and zero or more nonpromoting tag candidates.

    Required normalized input: source_fingerprint, conversation_id, messages.
    Messages contain message_id, role, source_time and optional text; metadata
    timestamps are preserved verbatim instead of interpreted as current truth.
    No source text or matched phrase is placed in the result.
    """
    if not isinstance(conversation, Mapping):
        raise ValueError("conversation must be an object")
    source = _fingerprint(conversation.get("source_fingerprint"))
    conversation_id = _nonempty(conversation.get("conversation_id"), "conversation_id")
    messages = conversation.get("messages")
    if not isinstance(messages, (list, tuple)):
        raise ValueError("messages must be an array")
    seen_messages: set[str] = set()
    candidates: list[dict] = []
    counts = {"messages": 0, "text_messages": 0, "nontext_messages": 0,
              "oversize_text_messages": 0, "correction_cue_messages": 0}
    for message in messages:
        if not isinstance(message, Mapping):
            raise ValueError("message must be an object")
        message_id = _nonempty(message.get("message_id"), "message_id")
        if message_id in seen_messages:
            raise ValueError("duplicate message_id within conversation")
        seen_messages.add(message_id)
        role = _nonempty(message.get("role"), "role")
        if role not in {"user", "assistant", "system", "tool", "unknown"}:
            raise ValueError("unsupported message role")
        counts["messages"] += 1
        text = message.get("text")
        if text is None:
            counts["nontext_messages"] += 1
            continue
        if not isinstance(text, str):
            raise ValueError("text must be a string or null")
        if len(text) > MAX_TEXT_LENGTH:
            counts["oversize_text_messages"] += 1
            continue
        counts["text_messages"] += 1
        correction_cue = role == "user" and CORRECTION.search(text) is not None
        if correction_cue:
            counts["correction_cue_messages"] += 1
        found: set[tuple[str, str]] = set()
        for tag_type, tag_id, pattern in lexicon:
            if pattern.search(text):
                found.add((tag_type, tag_id))
        for tag_type, tag_id in sorted(found):
            candidates.append({
                "record_type": "chat_history_tag_candidate",
                "candidate_id": _candidate_id([source, conversation_id, message_id, tag_type, tag_id]),
                "source_ref": {"source_fingerprint": source, "conversation_id": conversation_id,
                               "message_id": message_id, "role": role,
                               "source_time": _timestamp(message.get("source_time"), "source_time")},
                "tag_type": tag_type,
                "tag_id": tag_id,
                "taxonomy_version": "chat-candidate-v0.1",
                "match_basis": "LEXICAL_ALIAS_ONLY",
                "association_confidence": "UNKNOWN_NOT_ASSESSED",
                "source_trust": "HISTORICAL_UNTRUSTED",
                "currentness": "UNASSESSED",
                "semantic_state": "UNADJUDICATED_CANDIDATE",
                "requires_review": True,
                "correction_cue_candidate": bool(correction_cue),
                "conflict_state": "NOT_EVALUATED",
                "memory_admitted": False,
            })
    manifest = {
        "record_type": "chat_history_conversation_manifest_candidate",
        "source_fingerprint": source,
        "conversation_id": conversation_id,
        "source_create_time": _timestamp(conversation.get("source_create_time"), "source_create_time"),
        "source_update_time": _timestamp(conversation.get("source_update_time"), "source_update_time"),
        "coverage": counts,
        "tag_candidate_count": len(candidates),
        "semantic_state": "UNADJUDICATED_CANDIDATE",
        "source_trust": "HISTORICAL_UNTRUSTED",
        "memory_admitted": False,
    }
    return manifest, candidates


def catalog_stream(
    conversations: Iterable[Mapping[str, object]],
    lexicon_entries: Sequence[Mapping[str, object]],
) -> Iterable[dict]:
    """Stream coverage for *every* conversation and bounded tag metadata only.

    Duplicate conversation IDs for one source fail closed. No output artifact is
    written by this module; callers must protect private candidate metadata.
    """
    lexicon = compile_lexicon(lexicon_entries)
    seen: set[tuple[str, str]] = set()
    for conversation in conversations:
        manifest, candidates = catalog_conversation(conversation, lexicon)
        identity = (manifest["source_fingerprint"], manifest["conversation_id"])
        if identity in seen:
            raise ValueError("duplicate conversation identity")
        seen.add(identity)
        yield manifest
        yield from candidates
