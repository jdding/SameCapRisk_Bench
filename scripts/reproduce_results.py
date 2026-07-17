#!/usr/bin/env python3
"""Recompute SameCapRisk-Bench result summaries from compact ranks.

This is the table-level reproducer for the reviewer artifact. It checks the
fixed-rank evidence behind the main merged retrieval table, the Recall/HSR
frontier inputs, cutoff sensitivity, and selector-certificate accounting. It
does not rerun neural embedding, reranking, or LLM inference.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
csv.field_size_limit(sys.maxsize)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def mean(rows: list[dict[str, str]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def rank_metrics(rows: list[dict[str, str]], k: int) -> dict[str, str]:
    recall = []
    hsr = []
    ndcg = []
    for row in rows:
        helpful_rank = int(row["helpful_rank"]) if row["helpful_rank"] else 10**9
        risky_rank = int(row["risky_sibling_rank"]) if row["risky_sibling_rank"] else 10**9
        recall.append(1.0 if helpful_rank <= k else 0.0)
        hsr.append(1.0 if risky_rank <= k else 0.0)
        ndcg.append((1.0 / math.log2(helpful_rank + 1)) if helpful_rank <= k else 0.0)
    return {
        f"recall_at_{k}": f"{sum(recall) / len(recall):.6f}",
        f"hsr_at_{k}": f"{sum(hsr) / len(hsr):.6f}",
        f"ndcg_at_{k}": f"{sum(ndcg) / len(ndcg):.6f}",
    }


def aggregate_predictions() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rows = read_tsv(ROOT / "results" / "compact_predictions.tsv")
    method_labels = {
        "hybrid_lexical_rrf": "Hybrid lexical RRF",
        "skillrouter_official": "SkillRouter",
        "skillret_embedding_0_6b": "SkillRet",
        "r3_skill_embedding_reranker": "R3-Skill",
        "controlled_reference": "Reference pipeline",
    }
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["method_id"] in method_labels:
            grouped[row["method_id"]].append(row)
    main = []
    extended = []
    cutoff = []
    for method_id, label in method_labels.items():
        group = grouped[method_id]
        if len(group) != 1686:
            raise RuntimeError(f"{method_id}: expected 1686 rows, found {len(group)}")
        strata = {stratum: sum(1 for row in group if row["stratum"] == stratum) for stratum in {"core_marked_sibling", "hard_role_flip"}}
        main.append({
            "method_id": method_id,
            "paper_label": label,
            "status": "complete",
            "overall_n": 1686,
            "core_n": strata["core_marked_sibling"],
            "hard_n": strata["hard_role_flip"],
            "recall_at_3": f"{mean(group, 'recall_at_3'):.6f}",
            "ndcg_at_3": f"{mean(group, 'ndcg_at_3'):.6f}",
            "recall_at_5": f"{mean(group, 'recall_at_5'):.6f}",
            "ndcg_at_5": f"{mean(group, 'ndcg_at_5'):.6f}",
            "hsr_at_3": f"{mean(group, 'hsr_at_3'):.6f}",
            "hsr_at_5": f"{mean(group, 'hsr_at_5'):.6f}",
        })
        extended.append({
            "method_id": method_id,
            "paper_label": label,
            "status": "complete",
            "overall_n": 1686,
            "core_n": strata["core_marked_sibling"],
            "hard_n": strata["hard_role_flip"],
            "recall_at_20": f"{mean(group, 'recall_at_20'):.6f}",
            "ndcg_at_20": f"{mean(group, 'ndcg_at_20'):.6f}",
            "hsr_at_20": f"{mean(group, 'hsr_at_20'):.6f}",
        })
        cutoff_row = {
            "method_id": method_id,
            "paper_label": label,
            "overall_n": 1686,
        }
        for k in (3, 10, 20):
            cutoff_row.update(rank_metrics(group, k))
        cutoff_row["source"] = (
            "results/diagnostics/r3_skill_per_query.tsv"
            if method_id == "r3_skill_embedding_reranker"
            else "results/compact_predictions.tsv"
        )
        cutoff.append(cutoff_row)
    return main, extended, cutoff


def selector_certificate() -> list[dict[str, object]]:
    cases = read_tsv(ROOT / "results" / "selector_certificate_cases.tsv")
    out = []
    for k in ("3", "5", "20"):
        group = [row for row in cases if row["k"] == k]
        if len(group) != 1686:
            raise RuntimeError(f"K={k}: expected 1686 selector rows, found {len(group)}")
        core = [row for row in group if row["stratum"] == "core_marked_sibling"]
        hard = [row for row in group if row["stratum"] == "hard_role_flip"]
        core_no = sum(int(row["no_selection_risky_exposed"]) for row in core)
        hard_no = sum(int(row["no_selection_risky_exposed"]) for row in hard)
        core_resolved = sum(int(row["resolved_pre_exposure"]) for row in core)
        hard_resolved = sum(int(row["resolved_pre_exposure"]) for row in hard)
        core_final = sum(int(row["final_risky_exposed"]) for row in core)
        hard_final = sum(int(row["final_risky_exposed"]) for row in hard)
        out.append({
            "k": k,
            "core_no_selection_exposed": core_no,
            "hard_no_selection_exposed": hard_no,
            "merged_no_selection_exposed": core_no + hard_no,
            "core_resolved_exposed": core_resolved,
            "hard_resolved_exposed": hard_resolved,
            "merged_resolved_exposed": core_resolved + hard_resolved,
            "core_final_exposed": core_final,
            "hard_final_exposed": hard_final,
            "merged_final_exposed": core_final + hard_final,
            "merged_n": 1686,
        })
    return out


def compare_float(expected: str, observed: str, tolerance: float = 5e-6) -> bool:
    return abs(float(expected) - float(observed)) <= tolerance


def main() -> int:
    main_rows, extended_rows, cutoff_rows = aggregate_predictions()
    cert_rows = selector_certificate()
    observed_main = {row["method_id"]: row for row in main_rows}
    observed_extended = {row["method_id"]: row for row in extended_rows}
    observed_cutoff = {row["method_id"]: row for row in cutoff_rows}
    observed_cert = {str(row["k"]): row for row in cert_rows}
    expected_main = {row["method_id"]: row for row in read_tsv(ROOT / "results" / "main_table.tsv")}
    expected_extended = {row["method_id"]: row for row in read_tsv(ROOT / "results" / "extended_k20.tsv")}
    expected_cutoff = {row["method_id"]: row for row in read_tsv(ROOT / "results" / "cutoff_sensitivity.tsv")}
    expected_cert = {row["k"]: row for row in read_tsv(ROOT / "results" / "selector_certificate.tsv")}
    compact_all = read_tsv(ROOT / "results" / "compact_predictions.tsv")
    open_llm_rows = read_tsv(ROOT / "results" / "diagnostics" / "open_llm_listwise_summary.tsv")
    bge_rows = read_tsv(ROOT / "results" / "diagnostics" / "bge_reranker_two_stage_summary.tsv")
    errors = []
    for method_id, expected in expected_main.items():
        observed = observed_main.get(method_id)
        for key in ["recall_at_3", "ndcg_at_3", "recall_at_5", "ndcg_at_5", "hsr_at_3", "hsr_at_5"]:
            if observed is None or not compare_float(expected[key], observed[key]):
                errors.append(f"main {method_id} {key}: expected {expected[key]}, observed {observed[key] if observed else 'missing'}")
    for method_id, expected in expected_extended.items():
        observed = observed_extended.get(method_id)
        for key in ["recall_at_20", "ndcg_at_20", "hsr_at_20"]:
            if observed is None or not compare_float(expected[key], observed[key]):
                errors.append(f"extended {method_id} {key}: expected {expected[key]}, observed {observed[key] if observed else 'missing'}")
    for method_id, expected in expected_cutoff.items():
        observed = observed_cutoff.get(method_id)
        for key in ["recall_at_3", "hsr_at_3", "recall_at_10", "hsr_at_10", "recall_at_20", "hsr_at_20"]:
            if observed is None or not compare_float(expected[key], observed[key]):
                errors.append(f"cutoff {method_id} {key}: expected {expected[key]}, observed {observed[key] if observed else 'missing'}")
    cert_map = {
        "core_no_selection_exposed": "core_no_selection_exposed",
        "hard_no_selection_exposed": "hard_no_selection_exposed",
        "merged_no_selection_exposed": "merged_no_selection_exposed",
        "core_resolved_exposed": "core_resolved_exposed",
        "hard_resolved_exposed": "hard_resolved_exposed",
        "merged_resolved_exposed": "merged_resolved_exposed",
        "core_final_exposed": "core_final_exposed",
        "hard_final_exposed": "hard_final_exposed",
        "merged_final_exposed": "merged_final_exposed",
    }
    for k, expected in expected_cert.items():
        observed = observed_cert.get(k)
        for expected_key, observed_key in cert_map.items():
            if observed is None or str(expected[expected_key]) != str(observed[observed_key]):
                errors.append(f"certificate K={k} {expected_key}: expected {expected[expected_key]}, observed {observed[observed_key] if observed else 'missing'}")
    open_expected = {
        row["method"]: row for row in open_llm_rows if row["scope"] == "all"
    }
    for method_id, label in {
        "bge_m3_dense": "BGE-M3 dense original order",
        "qwen2_5_7b_listwise_bge_m3_top20": "Qwen2.5-7B listwise over BGE-M3 top20",
    }.items():
        members = [row for row in compact_all if row["method_id"] == method_id]
        if len(members) != 1686:
            errors.append(f"diagnostic {method_id}: expected 1686 rows, found {len(members)}")
            continue
        expected = open_expected[label]
        for key, expected_key in {
            "recall_at_3": "R@3",
            "hsr_at_3": "HSR@3",
            "cleanhit_at_3": "CleanHit@3",
        }.items():
            observed = mean(members, key)
            if abs(observed - float(expected[expected_key])) > 5e-6:
                errors.append(
                    f"diagnostic {method_id} {key}: expected {expected[expected_key]}, observed {observed:.6f}"
                )
    reranker_members = [
        row for row in compact_all if row["method_id"] == "bge_m3_bge_reranker"
    ]
    reranker_expected = next(row for row in bge_rows if row["scope"] == "merged_all")
    if len(reranker_members) != 1686:
        errors.append(
            f"diagnostic bge_m3_bge_reranker: expected 1686 rows, found {len(reranker_members)}"
        )
    else:
        for key in ["recall_at_3", "hsr_at_3", "cleanhit_at_3"]:
            observed = mean(reranker_members, key)
            if abs(observed - float(reranker_expected[key])) > 5e-6:
                errors.append(
                    f"diagnostic bge_m3_bge_reranker {key}: expected {reranker_expected[key]}, observed {observed:.6f}"
                )
    summary = {"status": "ok" if not errors else "fail", "errors": errors}
    (ROOT / "reports" / "reproduction_report.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
