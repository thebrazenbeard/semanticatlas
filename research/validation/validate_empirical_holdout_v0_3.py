#!/usr/bin/env python3
"""Semantic Atlas 30-case empirical holdout validator/scorer v0.3.

This is a mechanical validator. It does not generate answers or decide whether
natural-language answers deserve PASS/FAIL. It verifies experiment geometry and
computes the frozen metrics from already-locked records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

BASELINE = "BASELINE"
ATLAS = "ATLAS_ASSISTED"
PROTOCOL = "SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.3"
HOLDOUT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.3"
SOURCE_GIT = "2e1982d7c8f507441f157c0b69f98e0ced73ae72"
SNAPSHOT = "52e611ea-4687-4bb8-81d8-477b37cc2bf3"
SEARCH_ROUTE = "search_current_runtime_objects_v8"
RESULT_PROJECTION = "SEMANTIC_ATLAS_RUNTIME_SEARCH_RESULT_PROJECTION_V1"
RETRIEVAL_LIMIT = 5

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
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            die(f"{path}:{lineno}: invalid JSON: {e}")
    return rows

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate_roster(roster):
    if roster.get("schema_version") != "SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1":
        die("unexpected base roster schema")
    if roster.get("source_git_commit") != SOURCE_GIT:
        die("base roster source Git mismatch")
    cases = roster.get("cases")
    if not isinstance(cases, list) or roster.get("case_count") != len(cases):
        die("base roster count mismatch")
    ids = [c.get("case_id") for c in cases]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        die("base roster has invalid/duplicate case IDs")
    return {c["case_id"]: c for c in cases}

def validate_holdout(holdout, roster_ids):
    if holdout.get("schema_version") != HOLDOUT_SCHEMA:
        die("unexpected holdout schema")
    if holdout.get("protocol_version") != PROTOCOL:
        die("holdout protocol mismatch")
    if holdout.get("source_git_commit") != SOURCE_GIT:
        die("holdout source Git mismatch")
    if holdout.get("runtime_snapshot_id") != SNAPSHOT:
        die("holdout snapshot mismatch")
    if holdout.get("service_role_search_route") != SEARCH_ROUTE:
        die("holdout search route mismatch")
    if holdout.get("search_result_projection") != RESULT_PROJECTION:
        die("holdout result projection mismatch")
    ids = holdout.get("case_ids")
    excluded = holdout.get("excluded_pilot_case_ids")
    if not isinstance(ids, list) or holdout.get("case_count") != len(ids):
        die("holdout count mismatch")
    if len(ids) != len(set(ids)) or len(excluded) != len(set(excluded)):
        die("holdout/excluded IDs must be unique")
    if set(ids) & set(excluded):
        die("pilot cases overlap holdout")
    if set(ids) | set(excluded) != roster_ids:
        die("holdout + excluded pilot cases must exactly partition frozen 40-case roster")
    if len(ids) != 30 or len(excluded) != 10:
        die("v0.3 requires exactly 30 holdout + 10 pilot cases")
    return set(ids)

def load_frozen_cases(root: Path, roster_map):
    by_path = defaultdict(list)
    for cid, r in roster_map.items():
        p = r.get("source_path")
        if not isinstance(p, str) or not p:
            die(f"{cid}: missing source_path")
        by_path[p].append(cid)
    cases = {}
    for rel, ids in by_path.items():
        rows = load_jsonl(root / rel)
        m = {r.get("case_id"): r for r in rows}
        for cid in ids:
            c = m.get(cid)
            if c is None:
                die(f"{cid}: missing from {rel}")
            if c.get("schema_version") != "SEMANTIC_ATLAS_VALIDATION_CASE_V0.1":
                die(f"{cid}: validation case schema mismatch")
            r = roster_map[cid]
            if c.get("gold", {}).get("resolution") != r.get("gold_resolution"):
                die(f"{cid}: gold resolution mismatch")
            if list(c.get("category", [])) != list(r.get("categories", [])):
                die(f"{cid}: categories mismatch")
            if bool(c.get("cee", {}).get("required")) != bool(r.get("cee_required")):
                die(f"{cid}: CEE flag mismatch")
            cases[cid] = c
    return cases

def applicability(case):
    cats = set(case.get("category", []))
    cid = case["case_id"]
    return {
        "currentness_correctness": bool(cats & {"CURRENTNESS","AUTHORITY","HISTORICAL_AUDIT","SUPERSESSION","RETRACTION","STALE_REF"}),
        "correction_propagation": bool(cats & {"CORRECTION","SUPERSESSION","RETRACTION"}),
        "identity_overmerge": ("OVERMERGE" in cid) or ("SIMILARITY_TRAP" in cats),
        "identity_oversplit": ("OVERSPLIT" in cid) or ("CONTINUITY" in cats),
        "cee": bool(case.get("cee", {}).get("required")),
    }

def validate_generation(g, holdout_ids, cases):
    required = {
        "schema_version","protocol_version","holdout_manifest_version","case_id",
        "condition","opaque_output_id","model_family","generation_config_id",
        "generation_context_sha256","source_git_commit","supplied_source_ids",
        "output_sha256","output_text","generated_at","generator_provenance",
    }
    if required - g.keys():
        die(f"generation missing fields: {sorted(required-g.keys())}")
    if g["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_RECORD_V0.3":
        die("generation schema mismatch")
    if g["protocol_version"] != PROTOCOL or g["holdout_manifest_version"] != HOLDOUT_SCHEMA:
        die("generation protocol/holdout binding mismatch")
    cid = g["case_id"]
    if cid not in holdout_ids:
        die(f"generation uses non-holdout case {cid}")
    if g["condition"] not in {BASELINE, ATLAS}:
        die(f"{cid}: invalid generation condition")
    if g["source_git_commit"] != SOURCE_GIT:
        die(f"{cid}: generation source Git mismatch")
    if sha256_text(g["output_text"]) != g["output_sha256"]:
        die(f"{cid} {g['condition']}: output hash mismatch")
    allowed = {s["source_id"] for s in cases[cid].get("sources", [])}
    if set(g["supplied_source_ids"]) != allowed:
        die(f"{cid} {g['condition']}: direct source packet differs across frozen case")
    if g["condition"] == BASELINE:
        for k in ("atlas_runtime_snapshot_id","atlas_search_route","atlas_search_result_projection","atlas_retrieval_limit","atlas_retrieval_record_sha256"):
            if g.get(k) is not None:
                die(f"{cid}: baseline contains Atlas provenance")
    else:
        if g.get("atlas_runtime_snapshot_id") != SNAPSHOT:
            die(f"{cid}: Atlas snapshot mismatch")
        if g.get("atlas_search_route") != SEARCH_ROUTE:
            die(f"{cid}: Atlas search route mismatch")
        if g.get("atlas_search_result_projection") != RESULT_PROJECTION:
            die(f"{cid}: Atlas result projection mismatch")
        if g.get("atlas_retrieval_limit") != RETRIEVAL_LIMIT:
            die(f"{cid}: Atlas retrieval limit mismatch")
        h = g.get("atlas_retrieval_record_sha256")
        if not isinstance(h, str) or len(h) != 64 or any(ch not in "0123456789abcdef" for ch in h):
            die(f"{cid}: Atlas retrieval record digest invalid")

def validate_score(srec, generations, cases, holdout_ids):
    required = {
        "schema_version","protocol_version","holdout_manifest_version","case_id",
        "condition","opaque_output_id","evaluator_blinded",
        "score_locked_before_condition_reveal","scores","critical_failure_tags",
        "supporting_source_ids",
    }
    if required - srec.keys():
        die(f"score missing fields: {sorted(required-srec.keys())}")
    if srec["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_SCORE_RECORD_V0.3":
        die("score schema mismatch")
    if srec["protocol_version"] != PROTOCOL or srec["holdout_manifest_version"] != HOLDOUT_SCHEMA:
        die("score protocol/holdout binding mismatch")
    if srec["case_id"] not in holdout_ids:
        die(f"score uses non-holdout case {srec['case_id']}")
    if srec["evaluator_blinded"] is not True or srec["score_locked_before_condition_reveal"] is not True:
        die(f"{srec['case_id']}: accepted score must be blinded and locked before reveal")
    g = generations.get(srec["opaque_output_id"])
    if g is None:
        die("score references unknown output")
    if (srec["case_id"], srec["condition"]) != (g["case_id"], g["condition"]):
        die("score/generation identity mismatch")

    tags = srec["critical_failure_tags"]
    if not isinstance(tags, list) or len(tags) != len(set(tags)) or set(tags) - CRITICAL_TAGS:
        die("invalid critical tags")

    s = srec["scores"]
    expected = {
        "source_traceability","proposition_fidelity","currentness_correctness",
        "correction_propagation","hallucinated_provenance",
        "false_autobiographical_promotion","privacy_scope_violation",
        "identity_overmerge","identity_oversplit","unresolved_calibration",
        "cee_useful_context","cee_unsupported_specificity","behavioral_usefulness",
    }
    if set(s) != expected:
        die("score fields mismatch")
    if s["source_traceability"] not in {"PASS","FAIL"} or s["proposition_fidelity"] not in {"PASS","FAIL"}:
        die("always-applicable dimensions require PASS/FAIL")
    for k in ("currentness_correctness","correction_propagation"):
        if s[k] not in {"PASS","FAIL","NA"}:
            die(f"invalid {k}")
    for k in ("hallucinated_provenance","false_autobiographical_promotion","privacy_scope_violation"):
        if s[k] not in {"NO","YES"}:
            die(f"invalid {k}")
    for k in ("identity_overmerge","identity_oversplit"):
        if s[k] not in {"NO","YES","NA"}:
            die(f"invalid {k}")
    if s["unresolved_calibration"] not in {"CORRECT_RESOLUTION","FALSE_CLOSURE","FALSE_UNRESOLVED"}:
        die("invalid unresolved calibration")
    if s["cee_useful_context"] not in {"IMPROVED","NEUTRAL","WORSE","NA"}:
        die("invalid CEE usefulness")
    if s["cee_unsupported_specificity"] not in {"NO","YES","NA"}:
        die("invalid CEE specificity")
    if not isinstance(s["behavioral_usefulness"], int) or not 0 <= s["behavioral_usefulness"] <= 2:
        die("behavioral usefulness must be 0..2")

    app = applicability(cases[srec["case_id"]])
    for field in ("currentness_correctness","correction_propagation","identity_overmerge","identity_oversplit"):
        if app[field] and s[field] == "NA":
            die(f"{srec['case_id']}: required dimension marked NA: {field}")
        if not app[field] and s[field] != "NA":
            die(f"{srec['case_id']}: non-applicable dimension scored: {field}")
    if app["cee"]:
        if s["cee_useful_context"] == "NA" or s["cee_unsupported_specificity"] == "NA":
            die(f"{srec['case_id']}: CEE-required case has NA")
    else:
        if s["cee_useful_context"] != "NA" or s["cee_unsupported_specificity"] != "NA":
            die(f"{srec['case_id']}: non-CEE case has CEE scoring")

    case = cases[srec["case_id"]]
    allowed = {x["source_id"] for x in case.get("sources", [])}
    support = set(srec["supporting_source_ids"])
    if not support <= allowed:
        die(f"{srec['case_id']}: score cites source not in frozen case")
    if s["source_traceability"] == "PASS":
        required_sources = set(case.get("gold", {}).get("required_source_ids", []))
        if not support or not required_sources <= support:
            die(f"{srec['case_id']}: traceability PASS omits required source")

    if s["hallucinated_provenance"] == "YES" and "FABRICATED_RETRIEVAL" not in tags:
        die("hallucinated provenance missing critical tag")
    if s["false_autobiographical_promotion"] == "YES" and "FALSE_AUTOBIOGRAPHICAL_PROMOTION" not in tags:
        die("false autobiographical promotion missing critical tag")
    if s["privacy_scope_violation"] == "YES" and "PRIVACY_SCOPE_VIOLATION" not in tags:
        die("privacy violation missing critical tag")

def defect_axes(rec):
    s = rec["scores"]
    out = set()
    for k in ("source_traceability","proposition_fidelity","currentness_correctness","correction_propagation"):
        if s[k] == "FAIL":
            out.add(k)
    for k in ("hallucinated_provenance","false_autobiographical_promotion","privacy_scope_violation"):
        if s[k] == "YES":
            out.add(k)
    for k in ("identity_overmerge","identity_oversplit"):
        if s[k] == "YES":
            out.add(k)
    if s["cee_unsupported_specificity"] == "YES":
        out.add("cee_unsupported_specificity")
    return out

def rate(records, field):
    vals = [r["scores"][field] for r in records if r["scores"][field] != "NA"]
    if not vals:
        return None
    return sum(v == "PASS" for v in vals) / len(vals)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--roster", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json"))
    ap.add_argument("--holdout", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.3.json"))
    ap.add_argument("--generations", type=Path, required=True)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--pairwise", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    root = args.repo_root
    roster_map = validate_roster(load_json(root / args.roster))
    roster_ids = set(roster_map)
    holdout_ids = validate_holdout(load_json(root / args.holdout), roster_ids)
    cases = load_frozen_cases(root, roster_map)

    gens = load_jsonl(args.generations)
    generations = {}
    by_case_cond = {}
    for g in gens:
        validate_generation(g, holdout_ids, cases)
        oid = g["opaque_output_id"]
        key = (g["case_id"], g["condition"])
        if oid in generations or key in by_case_cond:
            die("duplicate generation record/output")
        generations[oid] = g
        by_case_cond[key] = g

    if {cid for cid, _ in by_case_cond} != holdout_ids:
        die(f"generation coverage mismatch: missing={sorted(holdout_ids-{cid for cid,_ in by_case_cond})}")
    for cid in holdout_ids:
        if (cid, BASELINE) not in by_case_cond or (cid, ATLAS) not in by_case_cond:
            die(f"{cid}: missing baseline or Atlas generation")
        b = by_case_cond[(cid, BASELINE)]
        a = by_case_cond[(cid, ATLAS)]
        if (b["model_family"], b["generation_config_id"]) != (a["model_family"], a["generation_config_id"]):
            die(f"{cid}: model family/config differs across conditions")

    scores = {}
    score_by_case_cond = {}
    for r in load_jsonl(args.scores):
        validate_score(r, generations, cases, holdout_ids)
        oid = r["opaque_output_id"]
        key = (r["case_id"], r["condition"])
        if oid in scores or key in score_by_case_cond:
            die("duplicate score record/output")
        scores[oid] = r
        score_by_case_cond[key] = r

    for cid in holdout_ids:
        if (cid, BASELINE) not in score_by_case_cond or (cid, ATLAS) not in score_by_case_cond:
            die(f"{cid}: missing baseline or Atlas score")

    pair_cases = set()
    atlas_wins = baseline_wins = ties = 0
    for p in load_jsonl(args.pairwise):
        required = {
            "schema_version","protocol_version","holdout_manifest_version","case_id",
            "pair_id","left_output_id","right_output_id","evaluator_blinded",
            "presentation_order_randomized","judgment_locked_before_condition_reveal",
            "preference","basis","critical_defects_left","critical_defects_right",
        }
        if required - p.keys():
            die(f"pairwise missing fields: {sorted(required-p.keys())}")
        if p["schema_version"] != "SEMANTIC_ATLAS_EMPIRICAL_PAIRWISE_JUDGMENT_V0.3":
            die("pairwise schema mismatch")
        if p["protocol_version"] != PROTOCOL or p["holdout_manifest_version"] != HOLDOUT_SCHEMA:
            die("pairwise protocol/holdout binding mismatch")
        cid = p["case_id"]
        if cid not in holdout_ids or cid in pair_cases:
            die(f"{cid}: non-holdout or duplicate pair")
        pair_cases.add(cid)
        if p["evaluator_blinded"] is not True or p["presentation_order_randomized"] is not True or p["judgment_locked_before_condition_reveal"] is not True:
            die(f"{cid}: pairwise judgment not blinded/randomized/locked")
        left = scores.get(p["left_output_id"])
        right = scores.get(p["right_output_id"])
        if left is None or right is None:
            die(f"{cid}: pair references unknown output")
        if left["case_id"] != cid or right["case_id"] != cid:
            die(f"{cid}: pair output case mismatch")
        if {left["condition"], right["condition"]} != {BASELINE, ATLAS}:
            die(f"{cid}: pair must compare baseline and Atlas")
        if set(p["critical_defects_left"]) != set(left["critical_failure_tags"]) or set(p["critical_defects_right"]) != set(right["critical_failure_tags"]):
            die(f"{cid}: pair critical tags disagree with locked scores")
        pref = p["preference"]
        if pref == "TIE":
            ties += 1
            continue
        if pref not in {"LEFT","RIGHT"}:
            die(f"{cid}: invalid preference")
        preferred = left if pref == "LEFT" else right
        other = right if pref == "LEFT" else left
        new_defects = defect_axes(preferred) - defect_axes(other)
        if new_defects:
            die(f"{cid}: preferred output introduces new defects {sorted(new_defects)}")
        if preferred["condition"] == ATLAS:
            atlas_wins += 1
        else:
            baseline_wins += 1

    if pair_cases != holdout_ids:
        die(f"pairwise coverage mismatch: missing={sorted(holdout_ids-pair_cases)}")

    atlas = [score_by_case_cond[(cid, ATLAS)] for cid in sorted(holdout_ids)]
    all_scores = [score_by_case_cond[(cid, c)] for cid in sorted(holdout_ids) for c in (BASELINE, ATLAS)]

    gold_unresolved = {cid for cid in holdout_ids if cases[cid].get("gold", {}).get("resolution") == "UNRESOLVED"}
    tp = fp = fn = 0
    for r in atlas:
        state = r["scores"]["unresolved_calibration"]
        if r["case_id"] in gold_unresolved:
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
    net_margin = (atlas_wins - baseline_wins) / non_tied if non_tied else None

    a = {
        "source_traceability": rate(atlas, "source_traceability"),
        "proposition_fidelity": rate(atlas, "proposition_fidelity"),
        "currentness_correctness": rate(atlas, "currentness_correctness"),
        "correction_propagation": rate(atlas, "correction_propagation"),
        "unresolved_precision": unresolved_precision,
        "unresolved_recall": unresolved_recall,
        "identity_overmerge_errors": sum(r["scores"]["identity_overmerge"] == "YES" for r in atlas),
        "identity_oversplit_errors": sum(r["scores"]["identity_oversplit"] == "YES" for r in atlas),
        "cee_unsupported_specificity_errors": sum(r["scores"]["cee_unsupported_specificity"] == "YES" for r in atlas),
    }
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

    summary = {
        "schema_version": "SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_SUMMARY_V0.3",
        "protocol_version": PROTOCOL,
        "holdout_manifest_version": HOLDOUT_SCHEMA,
        "case_count": len(holdout_ids),
        "atlas": a,
        "zero_tolerance_all_required_conditions": zero,
        "pairwise": {
            "atlas_wins": atlas_wins,
            "baseline_wins": baseline_wins,
            "ties": ties,
            "net_margin_non_tied": net_margin,
        },
        "qualification_pass": all(checks),
    }
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main()
