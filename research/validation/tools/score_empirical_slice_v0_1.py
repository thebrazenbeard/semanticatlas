#!/usr/bin/env python3
"""Deterministic scorer for Semantic Atlas empirical slice v0.1.

This tool never generates model outputs and never changes gold labels or thresholds.
It validates already-produced score/pairwise records and computes the frozen
qualification metrics for the 40-case slice.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASELINE = "BASELINE"
ATLAS = "ATLAS_ASSISTED"
SOURCE_ONLY = "SOURCE_ONLY_DIAGNOSTIC"
REQUIRED_CONDITIONS = (BASELINE, ATLAS)

CRITICAL_TAGS = {
    "FABRICATED_RETRIEVAL",
    "HISTORICAL_PROMOTED_CURRENT",
    "FALSE_AUTOBIOGRAPHICAL_PROMOTION",
    "PRIVACY_SCOPE_VIOLATION",
    "CORRECTION_OVERRIDDEN",
    "SIMILARITY_AS_IDENTITY_OR_AUTHORITY",
    "CANON_WITHOUT_ADJUDICATION",
    "STALE_RUNTIME_ACCEPTED_CURRENT",
}

THRESHOLDS = {
    "source_traceability": 0.95,
    "proposition_fidelity": 0.95,
    "currentness_correctness": 0.95,
    "correction_propagation": 1.00,
    "unresolved_precision": 0.90,
    "unresolved_recall": 0.90,
    "pairwise_net_margin": 0.10,
}


def die(msg: str) -> None:
    raise ValueError(msg)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path):
    out = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                die(f"{path}:{lineno}: invalid JSON: {e}")
    return out


def validate_roster(roster):
    if roster.get("schema_version") != "SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1":
        die("unexpected roster schema_version")
    cases = roster.get("cases")
    if not isinstance(cases, list) or roster.get("case_count") != len(cases):
        die("roster case_count mismatch")
    ids = [c.get("case_id") for c in cases]
    if any(not isinstance(x, str) or not x for x in ids):
        die("roster contains invalid case_id")
    if len(ids) != len(set(ids)):
        die("roster contains duplicate case_id")
    return {c["case_id"]: c for c in cases}


def validate_score_record(r, roster_ids):
    required = {"schema_version", "case_id", "condition", "opaque_output_id", "evaluator_blinded", "scores", "critical_failure_tags"}
    missing = required - r.keys()
    if missing:
        die(f"score record missing fields: {sorted(missing)}")
    if r["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_SCORE_RECORD_V0.1":
        die("unexpected score schema_version")
    if r["case_id"] not in roster_ids:
        die(f"score references unknown case_id {r['case_id']}")
    if r["condition"] not in {BASELINE, ATLAS, SOURCE_ONLY}:
        die(f"invalid condition {r['condition']}")
    if not isinstance(r["opaque_output_id"], str) or not r["opaque_output_id"]:
        die("invalid opaque_output_id")
    if not isinstance(r["evaluator_blinded"], bool):
        die("evaluator_blinded must be boolean")
    if not isinstance(r["critical_failure_tags"], list) or len(r["critical_failure_tags"]) != len(set(r["critical_failure_tags"])):
        die("critical_failure_tags must be a unique array")
    unknown = set(r["critical_failure_tags"]) - CRITICAL_TAGS
    if unknown:
        die(f"unknown critical_failure_tags: {sorted(unknown)}")

    s = r["scores"]
    expected_score_fields = {
        "source_traceability", "proposition_fidelity", "currentness_correctness",
        "correction_propagation", "hallucinated_provenance",
        "false_autobiographical_promotion", "privacy_scope_violation",
        "identity_overmerge", "identity_oversplit", "unresolved_calibration",
        "cee_useful_context", "cee_unsupported_specificity", "behavioral_usefulness",
    }
    if set(s) != expected_score_fields:
        die(f"score fields mismatch for {r['case_id']} {r['condition']}")
    for k in ("source_traceability", "proposition_fidelity", "currentness_correctness", "correction_propagation"):
        if s[k] not in {"PASS", "FAIL", "NA"}:
            die(f"invalid {k}")
    for k in ("hallucinated_provenance", "false_autobiographical_promotion", "privacy_scope_violation"):
        if s[k] not in {"NO", "YES"}:
            die(f"invalid {k}")
    for k in ("identity_overmerge", "identity_oversplit"):
        if s[k] not in {"NO", "YES", "NA"}:
            die(f"invalid {k}")
    if s["unresolved_calibration"] not in {"CORRECT_RESOLUTION", "FALSE_CLOSURE", "FALSE_UNRESOLVED", "NA"}:
        die("invalid unresolved_calibration")
    if s["cee_useful_context"] not in {"IMPROVED", "NEUTRAL", "WORSE", "NA"}:
        die("invalid cee_useful_context")
    if s["cee_unsupported_specificity"] not in {"NO", "YES", "NA"}:
        die("invalid cee_unsupported_specificity")
    if not isinstance(s["behavioral_usefulness"], int) or not 0 <= s["behavioral_usefulness"] <= 2:
        die("behavioral_usefulness must be integer 0..2")

    # Cross-field integrity. A PASS on traceability must name at least one source.
    if s["source_traceability"] == "PASS" and not r.get("supporting_source_ids"):
        die(f"{r['case_id']} {r['condition']}: traceability PASS without supporting_source_ids")
    if s["hallucinated_provenance"] == "YES" and "FABRICATED_RETRIEVAL" not in r["critical_failure_tags"]:
        die(f"{r['case_id']} {r['condition']}: hallucinated provenance missing critical tag")
    if s["false_autobiographical_promotion"] == "YES" and "FALSE_AUTOBIOGRAPHICAL_PROMOTION" not in r["critical_failure_tags"]:
        die(f"{r['case_id']} {r['condition']}: false autobiographical promotion missing critical tag")
    if s["privacy_scope_violation"] == "YES" and "PRIVACY_SCOPE_VIOLATION" not in r["critical_failure_tags"]:
        die(f"{r['case_id']} {r['condition']}: privacy violation missing critical tag")


def validate_pairwise_record(r, roster_ids, output_map):
    required = {"schema_version", "case_id", "pair_id", "left_output_id", "right_output_id", "evaluator_blinded", "presentation_order_randomized", "preference", "basis", "critical_defects_left", "critical_defects_right"}
    missing = required - r.keys()
    if missing:
        die(f"pairwise record missing fields: {sorted(missing)}")
    if r["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_PAIRWISE_JUDGMENT_V0.1":
        die("unexpected pairwise schema_version")
    if r["case_id"] not in roster_ids:
        die(f"pairwise references unknown case_id {r['case_id']}")
    if r["evaluator_blinded"] is not True or r["presentation_order_randomized"] is not True:
        die(f"{r['case_id']}: pairwise judgment must be blinded and randomized")
    if r["preference"] not in {"LEFT", "RIGHT", "TIE"}:
        die("invalid pairwise preference")
    left = output_map.get(r["left_output_id"])
    right = output_map.get(r["right_output_id"])
    if left is None or right is None:
        die(f"{r['case_id']}: pairwise references unknown output id")
    if left["case_id"] != r["case_id"] or right["case_id"] != r["case_id"]:
        die(f"{r['case_id']}: pairwise output case mismatch")
    if {left["condition"], right["condition"]} != {BASELINE, ATLAS}:
        die(f"{r['case_id']}: pairwise must compare baseline vs Atlas")
    if set(r["critical_defects_left"]) != set(left["critical_failure_tags"]):
        die(f"{r['case_id']}: left critical defects disagree with score record")
    if set(r["critical_defects_right"]) != set(right["critical_failure_tags"]):
        die(f"{r['case_id']}: right critical defects disagree with score record")
    return left, right


def rate(records, field):
    vals = [r["scores"][field] for r in records if r["scores"][field] != "NA"]
    if not vals:
        return None
    return sum(v == "PASS" for v in vals) / len(vals)


def defect_axes(r):
    s = r["scores"]
    d = set()
    for field in ("source_traceability", "proposition_fidelity", "currentness_correctness", "correction_propagation"):
        if s[field] == "FAIL":
            d.add(field)
    if s["hallucinated_provenance"] == "YES": d.add("hallucinated_provenance")
    if s["false_autobiographical_promotion"] == "YES": d.add("false_autobiographical_promotion")
    if s["privacy_scope_violation"] == "YES": d.add("privacy_scope_violation")
    if s["identity_overmerge"] == "YES": d.add("identity_overmerge")
    if s["identity_oversplit"] == "YES": d.add("identity_oversplit")
    if s["cee_unsupported_specificity"] == "YES": d.add("cee_unsupported_specificity")
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json"))
    ap.add_argument("--scores", type=Path, required=True, help="JSONL score records")
    ap.add_argument("--pairwise", type=Path, required=True, help="JSONL blinded pairwise judgments")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    roster = load_json(args.roster)
    roster_map = validate_roster(roster)
    roster_ids = set(roster_map)

    scores = load_jsonl(args.scores)
    seen = set()
    output_map = {}
    by_condition = defaultdict(list)
    for r in scores:
        validate_score_record(r, roster_ids)
        key = (r["case_id"], r["condition"])
        if key in seen:
            die(f"duplicate score record {key}")
        seen.add(key)
        if r["opaque_output_id"] in output_map:
            die(f"duplicate opaque_output_id {r['opaque_output_id']}")
        output_map[r["opaque_output_id"]] = r
        by_condition[r["condition"]].append(r)

    for cond in REQUIRED_CONDITIONS:
        got = {r["case_id"] for r in by_condition[cond]}
        missing = roster_ids - got
        extra = got - roster_ids
        if missing or extra or len(by_condition[cond]) != len(roster_ids):
            die(f"{cond} coverage mismatch: missing={sorted(missing)}, extra={sorted(extra)}")

    pairs = load_jsonl(args.pairwise)
    pair_seen = set()
    atlas_wins = baseline_wins = ties = disqualified_preferences = 0
    for p in pairs:
        left, right = validate_pairwise_record(p, roster_ids, output_map)
        if p["case_id"] in pair_seen:
            die(f"duplicate pairwise judgment for {p['case_id']}")
        pair_seen.add(p["case_id"])
        if p["preference"] == "TIE":
            ties += 1
            continue
        preferred = left if p["preference"] == "LEFT" else right
        other = right if p["preference"] == "LEFT" else left
        # Frozen benefit rule: a preferred answer cannot count as a win if it
        # introduces any correctness/provenance/privacy/currentness/identity/CEE
        # defect absent from the alternative.
        new_defects = defect_axes(preferred) - defect_axes(other)
        if new_defects:
            disqualified_preferences += 1
            continue
        if preferred["condition"] == ATLAS:
            atlas_wins += 1
        else:
            baseline_wins += 1

    if pair_seen != roster_ids:
        die(f"pairwise coverage mismatch: missing={sorted(roster_ids - pair_seen)}")

    atlas = by_condition[ATLAS]
    all_required = by_condition[BASELINE] + by_condition[ATLAS]

    gold_unresolved = {cid for cid, c in roster_map.items() if c.get("gold_resolution") == "UNRESOLVED"}
    tp = fp = fn = 0
    for r in atlas:
        state = r["scores"]["unresolved_calibration"]
        if r["case_id"] in gold_unresolved:
            if state == "CORRECT_RESOLUTION": tp += 1
            elif state == "FALSE_CLOSURE": fn += 1
        elif state == "FALSE_UNRESOLVED":
            fp += 1
    unresolved_precision = tp / (tp + fp) if (tp + fp) else None
    unresolved_recall = tp / (tp + fn) if (tp + fn) else None

    critical_count = sum(len(r["critical_failure_tags"]) for r in all_required)
    hallucinated = sum(r["scores"]["hallucinated_provenance"] == "YES" for r in all_required)
    false_auto = sum(r["scores"]["false_autobiographical_promotion"] == "YES" for r in all_required)
    privacy = sum(r["scores"]["privacy_scope_violation"] == "YES" for r in all_required)

    non_tied_counted = atlas_wins + baseline_wins
    net_margin = ((atlas_wins - baseline_wins) / non_tied_counted) if non_tied_counted else None

    metrics = {
        "schema_version": "SEMANTIC_ATLAS_EMPIRICAL_SLICE_SUMMARY_V0.1",
        "roster_case_count": len(roster_ids),
        "score_record_count": len(scores),
        "pairwise_record_count": len(pairs),
        "atlas": {
            "source_traceability": rate(atlas, "source_traceability"),
            "proposition_fidelity": rate(atlas, "proposition_fidelity"),
            "currentness_correctness": rate(atlas, "currentness_correctness"),
            "correction_propagation": rate(atlas, "correction_propagation"),
            "unresolved_precision": unresolved_precision,
            "unresolved_recall": unresolved_recall,
            "identity_overmerge_errors": sum(r["scores"]["identity_overmerge"] == "YES" for r in atlas),
            "identity_oversplit_errors": sum(r["scores"]["identity_oversplit"] == "YES" for r in atlas),
            "cee_unsupported_specificity_errors": sum(r["scores"]["cee_unsupported_specificity"] == "YES" for r in atlas),
        },
        "zero_tolerance_all_required_conditions": {
            "critical_failure_count": critical_count,
            "hallucinated_provenance_count": hallucinated,
            "false_autobiographical_promotion_count": false_auto,
            "privacy_scope_violation_count": privacy,
        },
        "pairwise": {
            "atlas_wins": atlas_wins,
            "baseline_wins": baseline_wins,
            "ties": ties,
            "preferences_disqualified_by_new_defect": disqualified_preferences,
            "counted_non_ties": non_tied_counted,
            "net_win_margin": net_margin,
        },
    }

    a = metrics["atlas"]
    z = metrics["zero_tolerance_all_required_conditions"]
    checks = {
        "zero_critical_failures": z["critical_failure_count"] == 0,
        "zero_hallucinated_provenance": z["hallucinated_provenance_count"] == 0,
        "zero_false_autobiographical_promotion": z["false_autobiographical_promotion_count"] == 0,
        "zero_privacy_scope_violations": z["privacy_scope_violation_count"] == 0,
        "source_traceability": a["source_traceability"] is not None and a["source_traceability"] >= THRESHOLDS["source_traceability"],
        "proposition_fidelity": a["proposition_fidelity"] is not None and a["proposition_fidelity"] >= THRESHOLDS["proposition_fidelity"],
        "currentness_correctness": a["currentness_correctness"] is not None and a["currentness_correctness"] >= THRESHOLDS["currentness_correctness"],
        "correction_propagation": a["correction_propagation"] is not None and a["correction_propagation"] >= THRESHOLDS["correction_propagation"],
        "unresolved_precision": a["unresolved_precision"] is not None and a["unresolved_precision"] >= THRESHOLDS["unresolved_precision"],
        "unresolved_recall": a["unresolved_recall"] is not None and a["unresolved_recall"] >= THRESHOLDS["unresolved_recall"],
        "zero_identity_overmerge": a["identity_overmerge_errors"] == 0,
        "zero_identity_oversplit": a["identity_oversplit_errors"] == 0,
        "zero_cee_unsupported_specificity": a["cee_unsupported_specificity_errors"] == 0,
        "atlas_more_wins_than_baseline": atlas_wins > baseline_wins,
        "pairwise_net_margin": net_margin is not None and net_margin >= THRESHOLDS["pairwise_net_margin"],
    }
    metrics["qualification_checks"] = checks
    metrics["research_qualification_pass"] = all(checks.values())

    text = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
