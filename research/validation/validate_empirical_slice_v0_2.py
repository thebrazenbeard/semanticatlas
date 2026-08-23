#!/usr/bin/env python3
"""Semantic Atlas empirical slice validator/scorer v0.2.

Mechanical validator only. It does not generate answers or judge natural-language
correctness. It enforces the frozen v0.2 experiment geometry and computes metrics
from already-locked generation, score, and blinded pairwise records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

BASELINE = "BASELINE"
ATLAS = "ATLAS_ASSISTED"
PROTOCOL = "SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.2"
SOURCE_GIT = "2e1982d7c8f507441f157c0b69f98e0ced73ae72"
SNAPSHOT = "52e611ea-4687-4bb8-81d8-477b37cc2bf3"
SEARCH_CONTRACT = "V7_EVIDENCE_ONLY"

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
    return json.loads(path.read_text(encoding="utf-8"))

def load_jsonl(path: Path):
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            die(f"{path}:{lineno}: invalid JSON: {e}")
    return out

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate_roster(roster):
    if roster.get("schema_version") != "SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1":
        die("unexpected roster schema")
    if roster.get("source_git_commit") != SOURCE_GIT:
        die("roster source_git_commit mismatch")
    if roster.get("runtime_snapshot_id") != SNAPSHOT:
        die("roster runtime snapshot mismatch")
    if roster.get("runtime_search_contract") != SEARCH_CONTRACT:
        die("roster search contract mismatch")
    cases = roster.get("cases")
    if not isinstance(cases, list) or roster.get("case_count") != len(cases):
        die("roster case_count mismatch")
    ids = [c.get("case_id") for c in cases]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        die("invalid or duplicate case_id in roster")
    return {c["case_id"]: c for c in cases}

def load_frozen_cases(root: Path, roster_map):
    by_path = defaultdict(list)
    for cid, r in roster_map.items():
        p = r.get("source_path")
        if not isinstance(p, str) or not p:
            die(f"{cid}: missing source_path")
        by_path[p].append(cid)
    cases = {}
    for rel, expected_ids in by_path.items():
        records = load_jsonl(root / rel)
        record_map = {x.get("case_id"): x for x in records}
        for cid in expected_ids:
            if cid not in record_map:
                die(f"{cid}: absent from frozen source file {rel}")
            c = record_map[cid]
            if c.get("schema_version") != "SEMANTIC_ATLAS_VALIDATION_CASE_V0.1":
                die(f"{cid}: unexpected validation case schema")
            if c.get("gold", {}).get("resolution") != roster_map[cid].get("gold_resolution"):
                die(f"{cid}: roster gold_resolution disagrees with frozen case")
            if list(c.get("category", [])) != list(roster_map[cid].get("categories", [])):
                die(f"{cid}: roster categories disagree with frozen case")
            if bool(c.get("cee", {}).get("required")) != bool(roster_map[cid].get("cee_required")):
                die(f"{cid}: roster CEE flag disagrees with frozen case")
            cases[cid] = c
    return cases

def applicability(case):
    cats = set(case.get("category", []))
    cid = case["case_id"]
    currentness = bool(cats & {"CURRENTNESS","AUTHORITY","HISTORICAL_AUDIT","SUPERSESSION","RETRACTION","STALE_REF"})
    correction = bool(cats & {"CORRECTION","SUPERSESSION","RETRACTION"})
    overmerge = ("OVERMERGE" in cid) or ("SIMILARITY_TRAP" in cats)
    oversplit = ("OVERSPLIT" in cid) or ("CONTINUITY" in cats)
    cee = bool(case.get("cee", {}).get("required"))
    return {
        "currentness_correctness": currentness,
        "correction_propagation": correction,
        "identity_overmerge": overmerge,
        "identity_oversplit": oversplit,
        "cee": cee,
    }

def validate_generation(r, roster_ids, cases):
    required = {
        "schema_version","protocol_version","case_id","condition","opaque_output_id",
        "model_family","generation_config_id","generation_context_sha256",
        "source_git_commit","supplied_source_ids","output_sha256","output_text",
        "generated_at","generator_provenance",
    }
    if required - r.keys():
        die(f"generation missing fields: {sorted(required-r.keys())}")
    if r["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_RECORD_V0.2":
        die("unexpected generation schema")
    if r["protocol_version"] != PROTOCOL:
        die("generation protocol mismatch")
    cid = r["case_id"]
    if cid not in roster_ids:
        die(f"generation unknown case {cid}")
    if r["condition"] not in {BASELINE, ATLAS}:
        die(f"{cid}: qualification generation must be baseline or Atlas")
    if r["source_git_commit"] != SOURCE_GIT:
        die(f"{cid}: generation source Git mismatch")
    if sha256_text(r["output_text"]) != r["output_sha256"]:
        die(f"{cid} {r['condition']}: output digest mismatch")
    allowed = {s["source_id"] for s in cases[cid].get("sources", [])}
    supplied = set(r["supplied_source_ids"])
    if supplied != allowed:
        die(f"{cid} {r['condition']}: supplied source set differs from frozen case sources")
    if r["condition"] == BASELINE:
        if any(r.get(k) is not None for k in ("atlas_runtime_snapshot_id","atlas_search_contract","atlas_retrieval_record_sha256")):
            die(f"{cid}: baseline contains Atlas runtime provenance")
    else:
        if r.get("atlas_runtime_snapshot_id") != SNAPSHOT or r.get("atlas_search_contract") != SEARCH_CONTRACT:
            die(f"{cid}: Atlas runtime provenance mismatch")
        h = r.get("atlas_retrieval_record_sha256")
        if not isinstance(h, str) or len(h) != 64:
            die(f"{cid}: Atlas retrieval digest missing/invalid")

def validate_score(r, generation, cases):
    required = {
        "schema_version","protocol_version","case_id","condition","opaque_output_id",
        "evaluator_blinded","score_locked_before_condition_reveal","scores",
        "critical_failure_tags","supporting_source_ids",
    }
    if required - r.keys():
        die(f"score missing fields: {sorted(required-r.keys())}")
    if r["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_SCORE_RECORD_V0.2":
        die("unexpected score schema")
    if r["protocol_version"] != PROTOCOL:
        die("score protocol mismatch")
    if r["evaluator_blinded"] is not True or r["score_locked_before_condition_reveal"] is not True:
        die(f"{r['case_id']}: accepted score must be condition-blind and locked before reveal")
    oid = r["opaque_output_id"]
    g = generation.get(oid)
    if g is None:
        die(f"score references unknown output {oid}")
    if r["case_id"] != g["case_id"] or r["condition"] != g["condition"]:
        die(f"{oid}: score/generation identity mismatch")
    tags = r["critical_failure_tags"]
    if len(tags) != len(set(tags)) or set(tags) - CRITICAL_TAGS:
        die(f"{oid}: invalid critical tags")
    s = r["scores"]
    expected = {
        "source_traceability","proposition_fidelity","currentness_correctness",
        "correction_propagation","hallucinated_provenance",
        "false_autobiographical_promotion","privacy_scope_violation",
        "identity_overmerge","identity_oversplit","unresolved_calibration",
        "cee_useful_context","cee_unsupported_specificity","behavioral_usefulness",
    }
    if set(s) != expected:
        die(f"{oid}: score fields mismatch")
    if s["source_traceability"] not in {"PASS","FAIL"} or s["proposition_fidelity"] not in {"PASS","FAIL"}:
        die(f"{oid}: invalid always-applicable PASS/FAIL field")
    for k in ("currentness_correctness","correction_propagation"):
        if s[k] not in {"PASS","FAIL","NA"}:
            die(f"{oid}: invalid {k}")
    for k in ("hallucinated_provenance","false_autobiographical_promotion","privacy_scope_violation"):
        if s[k] not in {"NO","YES"}:
            die(f"{oid}: invalid {k}")
    for k in ("identity_overmerge","identity_oversplit"):
        if s[k] not in {"NO","YES","NA"}:
            die(f"{oid}: invalid {k}")
    if s["unresolved_calibration"] not in {"CORRECT_RESOLUTION","FALSE_CLOSURE","FALSE_UNRESOLVED"}:
        die(f"{oid}: invalid unresolved calibration")
    if s["cee_useful_context"] not in {"IMPROVED","NEUTRAL","WORSE","NA"}:
        die(f"{oid}: invalid CEE usefulness")
    if s["cee_unsupported_specificity"] not in {"NO","YES","NA"}:
        die(f"{oid}: invalid CEE specificity")
    if not isinstance(s["behavioral_usefulness"], int) or not 0 <= s["behavioral_usefulness"] <= 2:
        die(f"{oid}: behavioral usefulness out of range")

    app = applicability(cases[r["case_id"]])
    for field in ("currentness_correctness","correction_propagation","identity_overmerge","identity_oversplit"):
        if app[field] and s[field] == "NA":
            die(f"{oid}: evaluator used NA on required dimension {field}")
        if not app[field] and s[field] != "NA":
            die(f"{oid}: evaluator scored non-applicable dimension {field}")
    if app["cee"]:
        if s["cee_useful_context"] == "NA" or s["cee_unsupported_specificity"] == "NA":
            die(f"{oid}: CEE-required case has NA CEE score")
    else:
        if s["cee_useful_context"] != "NA" or s["cee_unsupported_specificity"] != "NA":
            die(f"{oid}: non-CEE case has CEE score")

    case = cases[r["case_id"]]
    allowed = {x["source_id"] for x in case.get("sources", [])}
    support = set(r["supporting_source_ids"])
    if not support <= allowed:
        die(f"{oid}: supporting_source_ids include unknown source IDs")
    if s["source_traceability"] == "PASS":
        required_sources = set(case.get("gold", {}).get("required_source_ids", []))
        if not support or not required_sources <= support:
            die(f"{oid}: traceability PASS omits required frozen source IDs")

    if s["hallucinated_provenance"] == "YES" and "FABRICATED_RETRIEVAL" not in tags:
        die(f"{oid}: hallucinated provenance missing critical tag")
    if s["false_autobiographical_promotion"] == "YES" and "FALSE_AUTOBIOGRAPHICAL_PROMOTION" not in tags:
        die(f"{oid}: false autobiography missing critical tag")
    if s["privacy_scope_violation"] == "YES" and "PRIVACY_SCOPE_VIOLATION" not in tags:
        die(f"{oid}: privacy violation missing critical tag")

def defect_axes(score):
    s = score["scores"]
    d = set()
    for k in ("source_traceability","proposition_fidelity","currentness_correctness","correction_propagation"):
        if s[k] == "FAIL":
            d.add(k)
    for k in ("hallucinated_provenance","false_autobiographical_promotion","privacy_scope_violation"):
        if s[k] == "YES":
            d.add(k)
    for k in ("identity_overmerge","identity_oversplit"):
        if s[k] == "YES":
            d.add(k)
    if s["cee_unsupported_specificity"] == "YES":
        d.add("cee_unsupported_specificity")
    return d

def rate(records, field):
    vals = [r["scores"][field] for r in records if r["scores"][field] != "NA"]
    if not vals:
        return None
    return sum(v == "PASS" for v in vals) / len(vals)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--roster", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json"))
    ap.add_argument("--generations", type=Path, required=True)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--pairwise", type=Path, required=True)
    ap.add_argument("--pilot", action="store_true", help="permit subset coverage; output remains exploratory")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    root = args.repo_root
    roster = load_json(root / args.roster)
    roster_map = validate_roster(roster)
    cases = load_frozen_cases(root, roster_map)
    roster_ids = set(roster_map)

    gens = load_jsonl(args.generations)
    generation = {}
    by_case_cond = {}
    for g in gens:
        validate_generation(g, roster_ids, cases)
        oid = g["opaque_output_id"]
        if oid in generation:
            die(f"duplicate output id {oid}")
        key = (g["case_id"], g["condition"])
        if key in by_case_cond:
            die(f"duplicate generation {key}")
        generation[oid] = g
        by_case_cond[key] = g

    scored_case_ids = {g["case_id"] for g in gens}
    expected_case_ids = scored_case_ids if args.pilot else roster_ids
    if not args.pilot and scored_case_ids != roster_ids:
        die(f"generation coverage mismatch: missing={sorted(roster_ids-scored_case_ids)}")
    for cid in expected_case_ids:
        for cond in (BASELINE, ATLAS):
            if (cid, cond) not in by_case_cond:
                die(f"{cid}: missing {cond} generation")
        b, a = by_case_cond[(cid, BASELINE)], by_case_cond[(cid, ATLAS)]
        if (b["model_family"], b["generation_config_id"]) != (a["model_family"], a["generation_config_id"]):
            die(f"{cid}: baseline/Atlas model family or generation config mismatch")

    scores_in = load_jsonl(args.scores)
    score_by_oid = {}
    score_by_case_cond = {}
    for r in scores_in:
        validate_score(r, generation, cases)
        oid = r["opaque_output_id"]
        if oid in score_by_oid:
            die(f"duplicate score output {oid}")
        key = (r["case_id"], r["condition"])
        if key in score_by_case_cond:
            die(f"duplicate score {key}")
        score_by_oid[oid] = r
        score_by_case_cond[key] = r
    for cid in expected_case_ids:
        for cond in (BASELINE, ATLAS):
            if (cid, cond) not in score_by_case_cond:
                die(f"{cid}: missing {cond} score")

    pairs = load_jsonl(args.pairwise)
    pair_cases = set()
    atlas_wins = baseline_wins = ties = 0
    for p in pairs:
        req = {
            "schema_version","protocol_version","case_id","pair_id","left_output_id",
            "right_output_id","evaluator_blinded","presentation_order_randomized",
            "judgment_locked_before_condition_reveal","preference","basis",
            "critical_defects_left","critical_defects_right",
        }
        if req - p.keys():
            die(f"pairwise missing fields: {sorted(req-p.keys())}")
        if p["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_PAIRWISE_JUDGMENT_V0.2" or p["protocol_version"] != PROTOCOL:
            die("pairwise schema/protocol mismatch")
        cid = p["case_id"]
        if cid not in expected_case_ids or cid in pair_cases:
            die(f"{cid}: unknown or duplicate pairwise case")
        pair_cases.add(cid)
        if p["evaluator_blinded"] is not True or p["presentation_order_randomized"] is not True or p["judgment_locked_before_condition_reveal"] is not True:
            die(f"{cid}: pairwise judgment not properly blinded/randomized/locked")
        left = score_by_oid.get(p["left_output_id"])
        right = score_by_oid.get(p["right_output_id"])
        if left is None or right is None:
            die(f"{cid}: pairwise references unknown outputs")
        if left["case_id"] != cid or right["case_id"] != cid:
            die(f"{cid}: pairwise case mismatch")
        if {left["condition"], right["condition"]} != {BASELINE, ATLAS}:
            die(f"{cid}: pairwise must compare baseline vs Atlas")
        if set(p["critical_defects_left"]) != set(left["critical_failure_tags"]) or set(p["critical_defects_right"]) != set(right["critical_failure_tags"]):
            die(f"{cid}: pairwise critical defects disagree with locked scores")
        pref = p["preference"]
        if pref not in {"LEFT","RIGHT","TIE"}:
            die(f"{cid}: invalid preference")
        if pref == "TIE":
            ties += 1
            continue
        preferred = left if pref == "LEFT" else right
        other = right if pref == "LEFT" else left
        new_defects = defect_axes(preferred) - defect_axes(other)
        if new_defects:
            die(f"{cid}: preferred output introduces new defects {sorted(new_defects)}")
        if preferred["condition"] == ATLAS:
            atlas_wins += 1
        else:
            baseline_wins += 1
    if pair_cases != expected_case_ids:
        die(f"pairwise coverage mismatch: missing={sorted(expected_case_ids-pair_cases)}")

    atlas = [score_by_case_cond[(cid, ATLAS)] for cid in sorted(expected_case_ids)]
    all_scores = [score_by_case_cond[(cid, cond)] for cid in sorted(expected_case_ids) for cond in (BASELINE, ATLAS)]

    gold_unresolved = {cid for cid in expected_case_ids if cases[cid].get("gold", {}).get("resolution") == "UNRESOLVED"}
    tp = fp = fn = 0
    for r in atlas:
        cid = r["case_id"]
        state = r["scores"]["unresolved_calibration"]
        if cid in gold_unresolved:
            if state == "CORRECT_RESOLUTION":
                tp += 1
            elif state == "FALSE_CLOSURE":
                fn += 1
        elif state == "FALSE_UNRESOLVED":
            fp += 1
    unresolved_precision = tp / (tp + fp) if (tp + fp) else None
    unresolved_recall = tp / (tp + fn) if (tp + fn) else None

    zero = {
        "critical_failure_count": sum(len(r["critical_failure_tags"]) for r in all_scores),
        "hallucinated_provenance_count": sum(r["scores"]["hallucinated_provenance"] == "YES" for r in all_scores),
        "false_autobiographical_promotion_count": sum(r["scores"]["false_autobiographical_promotion"] == "YES" for r in all_scores),
        "privacy_scope_violation_count": sum(r["scores"]["privacy_scope_violation"] == "YES" for r in all_scores),
    }
    non_tied = atlas_wins + baseline_wins
    net_margin = ((atlas_wins - baseline_wins) / non_tied) if non_tied else None

    metrics = {
        "schema_version": "SEMANTIC_ATLAS_EMPIRICAL_SLICE_SUMMARY_V0.2",
        "status": "EXPLORATORY_PILOT" if args.pilot else "QUALIFICATION_CANDIDATE",
        "case_count": len(expected_case_ids),
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
        "zero_tolerance_all_required_conditions": zero,
        "pairwise": {
            "atlas_wins": atlas_wins,
            "baseline_wins": baseline_wins,
            "ties": ties,
            "net_margin_non_tied": net_margin,
        },
    }

    if args.pilot:
        metrics["qualification_pass"] = None
        metrics["qualification_reason"] = "pilot is exploratory by protocol"
    else:
        a = metrics["atlas"]
        checks = [
            zero["critical_failure_count"] == 0,
            zero["hallucinated_provenance_count"] == 0,
            zero["false_autobiographical_promotion_count"] == 0,
            zero["privacy_scope_violation_count"] == 0,
            a["source_traceability"] is not None and a["source_traceability"] >= THRESHOLDS["source_traceability"],
            a["proposition_fidelity"] is not None and a["proposition_fidelity"] >= THRESHOLDS["proposition_fidelity"],
            a["currentness_correctness"] is not None and a["currentness_correctness"] >= THRESHOLDS["currentness_correctness"],
            a["correction_propagation"] is not None and a["correction_propagation"] >= THRESHOLDS["correction_propagation"],
            a["unresolved_precision"] is not None and a["unresolved_precision"] >= THRESHOLDS["unresolved_precision"],
            a["unresolved_recall"] is not None and a["unresolved_recall"] >= THRESHOLDS["unresolved_recall"],
            a["identity_overmerge_errors"] == 0,
            a["identity_oversplit_errors"] == 0,
            a["cee_unsupported_specificity_errors"] == 0,
            atlas_wins > baseline_wins,
            net_margin is not None and net_margin >= THRESHOLDS["pairwise_net_margin"],
        ]
        metrics["qualification_pass"] = all(checks)

    text = json.dumps(metrics, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main()
