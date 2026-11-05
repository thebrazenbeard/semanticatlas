"""Synthetic-only acceptance tests for untrusted historical catalog candidates."""

import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "chat_history_candidates", ROOT / "build/chat_history_candidates.py"
)
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)

SOURCE = "a" * 64
LEXICON = [
    {"tag_type": "project", "tag_id": "bt2", "aliases": ["Build Team Two", "BT2"]},
    {"tag_type": "topic", "tag_id": "recovery", "aliases": ["recovery"]},
    {"tag_type": "person", "tag_id": "person_a", "aliases": ["Person A"]},
]


def conversation(messages, conversation_id="synthetic-1"):
    return {
        "source_fingerprint": SOURCE,
        "conversation_id": conversation_id,
        "source_create_time": 100,
        "source_update_time": 200,
        "messages": messages,
    }


class HistoryCandidateTests(unittest.TestCase):
    def test_all_conversations_get_coverage_even_without_tags(self):
        records = list(catalog.catalog_stream([
            conversation([{"message_id": "m1", "role": "user", "text": None}]),
            conversation([], conversation_id="synthetic-2"),
        ], []))
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["coverage"]["nontext_messages"], 1)
        self.assertEqual(records[1]["coverage"]["messages"], 0)
        self.assertTrue(all(not item["memory_admitted"] for item in records))

    def test_exact_aliases_are_deterministic_nonpromoting_and_nontextual(self):
        source = conversation([
            {"message_id": "m1", "role": "user", "text": "BT2 recovery and Person A", "source_time": 123},
            {"message_id": "m2", "role": "assistant", "text": "Not aBT2 suffix or recoveryish"},
        ])
        first = list(catalog.catalog_stream([source], LEXICON))
        second = list(catalog.catalog_stream([source], list(reversed(LEXICON))))
        self.assertEqual(first, second)
        tags = first[1:]
        self.assertEqual([(t["tag_type"], t["tag_id"]) for t in tags], [
            ("person", "person_a"), ("project", "bt2"), ("topic", "recovery")
        ])
        self.assertEqual(tags[0]["source_ref"]["source_time"], 123)
        self.assertTrue(all(t["semantic_state"] == "UNADJUDICATED_CANDIDATE" for t in tags))
        self.assertTrue(all(t["association_confidence"] == "UNKNOWN_NOT_ASSESSED" for t in tags))
        self.assertTrue(all(t["requires_review"] and not t["memory_admitted"] for t in tags))
        self.assertNotIn("Person A", repr(tags))
        self.assertNotIn("recovery and", repr(tags))

    def test_correction_cue_is_not_a_currentness_or_conflict_decision(self):
        result = list(catalog.catalog_stream([conversation([
            {"message_id": "m1", "role": "user", "text": "Correction: I meant BT2."},
            {"message_id": "m2", "role": "assistant", "text": "Correction: BT2."},
        ])], LEXICON))
        self.assertEqual(result[0]["coverage"]["correction_cue_messages"], 1)
        self.assertTrue(result[1]["correction_cue_candidate"])
        self.assertFalse(result[2]["correction_cue_candidate"])
        self.assertEqual(result[1]["conflict_state"], "NOT_EVALUATED")
        self.assertEqual(result[1]["currentness"], "UNASSESSED")

    def test_negation_and_assistant_mention_are_only_lexical_candidates(self):
        result = list(catalog.catalog_stream([conversation([
            {"message_id": "m1", "role": "user", "text": "I am not working on BT2."},
            {"message_id": "m2", "role": "assistant", "text": "BT2 might be relevant."},
        ])], LEXICON))
        self.assertEqual(len(result), 3)
        self.assertEqual([item["source_ref"]["role"] for item in result[1:]], ["user", "assistant"])
        self.assertTrue(all(item["association_confidence"] == "UNKNOWN_NOT_ASSESSED"
                            and item["memory_admitted"] is False for item in result[1:]))

    def test_duplicate_and_ambiguous_sources_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate conversation identity"):
            list(catalog.catalog_stream([conversation([]), conversation([])], []))
        with self.assertRaisesRegex(ValueError, "duplicate message_id"):
            list(catalog.catalog_stream([conversation([
                {"message_id": "x", "role": "user", "text": ""},
                {"message_id": "x", "role": "assistant", "text": ""},
            ])], []))
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            catalog.compile_lexicon([
                {"tag_type": "topic", "tag_id": "a", "aliases": ["same"]},
                {"tag_type": "project", "tag_id": "b", "aliases": ["Same"]},
            ])

    def test_oversize_text_is_visible_as_coverage_debt(self):
        result = list(catalog.catalog_stream([conversation([
            {"message_id": "x", "role": "user", "text": "A" * (catalog.MAX_TEXT_LENGTH + 1)}
        ])], LEXICON))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["coverage"]["oversize_text_messages"], 1)

    def test_bad_fingerprint_and_unsupported_role_are_rejected(self):
        bad = conversation([])
        bad["source_fingerprint"] = "unknown"
        with self.assertRaisesRegex(ValueError, "source_fingerprint"):
            list(catalog.catalog_stream([bad], []))
        with self.assertRaisesRegex(ValueError, "unsupported message role"):
            list(catalog.catalog_stream([conversation([
                {"message_id": "x", "role": "owner", "text": "BT2"}
            ])], LEXICON))

    def test_timestamps_are_numeric_or_valid_timezone_aware_iso_strings(self):
        valid = conversation([{"message_id": "x", "role": "user", "text": "BT2",
                               "source_time": "2026-10-29T13:14:15Z"}])
        self.assertEqual(list(catalog.catalog_stream([valid], LEXICON))[1]
                         ["source_ref"]["source_time"], "2026-10-29T13:14:15Z")
        for invalid in ("SECRET_SENTINEL_NOT_A_TIMESTAMP", "2026-10-29T13:14:15",
                        "2026-02-31T13:14:15Z", "2026-10-29T13:14:15+25:00"):
            valid["messages"][0]["source_time"] = invalid
            with self.assertRaisesRegex(ValueError, "source_time"):
                list(catalog.catalog_stream([valid], LEXICON))

    def test_unicode_case_equivalent_aliases_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            catalog.compile_lexicon([
                {"tag_type": "topic", "tag_id": "first", "aliases": ["i"]},
                {"tag_type": "topic", "tag_id": "second", "aliases": ["İ"]},
            ])

    def test_private_metadata_cannot_smuggle_arbitrary_objects_or_control_lines(self):
        bad = conversation([{"message_id": "x", "role": "user", "text": "BT2",
                             "source_time": {"plaintext": "sensitive"}}])
        with self.assertRaisesRegex(ValueError, "source_time"):
            list(catalog.catalog_stream([bad], LEXICON))
        bad = conversation([])
        bad["source_create_time"] = {"body": "sensitive"}
        with self.assertRaisesRegex(ValueError, "source_create_time"):
            list(catalog.catalog_stream([bad], []))
        with self.assertRaisesRegex(ValueError, "conversation_id"):
            list(catalog.catalog_stream([conversation([], "line\nsecret")], []))


if __name__ == "__main__":
    unittest.main()
