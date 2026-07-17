#!/usr/bin/env python3
"""Build source-sensitivity summaries for paper-facing retrieval metrics.

The report is diagnostic: it checks whether the paper-level Recall/HSR/CleanHit
conclusions are dominated by a single core source domain.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUERY_CASES = ROOT / "data" / "query_cases.tsv"
PREDICTIONS = ROOT / "results" / "compact_predictions.tsv"
OUT = ROOT / "reports" / "source_sensitivity_leave_one_core_domain.tsv"


KS = (3, 5, 20)


def _rank(value: str) -> int | None:
    value = (value or "").strip()
    if not value:
        return None
    return int(float(value))


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _metrics(rows: list[dict[str, str]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k in KS:
        recall = []
        hsr = []
        cleanhit = []
        for row in rows:
            helpful_rank = _rank(row["helpful_rank"])
            risky_rank = _rank(row["risky_sibling_rank"])
            helpful_hit = helpful_rank is not None and helpful_rank <= k
            risky_exposed = risky_rank is not None and risky_rank <= k
            recall.append(float(helpful_hit))
            hsr.append(float(risky_exposed))
            cleanhit.append(float(helpful_hit and not risky_exposed))
        out[f"recall_at_{k}"] = _avg(recall)
        out[f"hsr_at_{k}"] = _avg(hsr)
        out[f"cleanhit_at_{k}"] = _avg(cleanhit)
    return out


def _write_row(writer: csv.DictWriter, analysis_id: str, method_id: str, rows: list[dict[str, str]], **extra: object) -> None:
    metrics = _metrics(rows)
    writer.writerow(
        {
            "analysis_id": analysis_id,
            "method_id": method_id,
            "included_cases": len(rows),
            **extra,
            **{key: f"{value:.6f}" for key, value in metrics.items()},
        }
    )


def main() -> None:
    cases: dict[str, dict[str, str]] = {}
    with QUERY_CASES.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            cases[row["query_case_id"]] = row

    predictions_by_method: dict[str, list[dict[str, str]]] = {}
    with PREDICTIONS.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            case = cases[row["query_case_id"]]
            row = {
                **row,
                "domain": case["domain"],
                "case_stratum": case["stratum"],
            }
            predictions_by_method.setdefault(row["method_id"], []).append(row)

    core_domains = sorted(
        {
            case["domain"]
            for case in cases.values()
            if case["stratum"] == "core_marked_sibling"
        }
    )

    fieldnames = [
        "analysis_id",
        "left_out_core_domain",
        "excluded_cases",
        "method_id",
        "included_cases",
        "recall_at_3",
        "hsr_at_3",
        "cleanhit_at_3",
        "recall_at_5",
        "hsr_at_5",
        "cleanhit_at_5",
        "recall_at_20",
        "hsr_at_20",
        "cleanhit_at_20",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()

        for method_id, rows in sorted(predictions_by_method.items()):
            _write_row(
                writer,
                "merged_all",
                method_id,
                rows,
                left_out_core_domain="",
                excluded_cases=0,
            )
            _write_row(
                writer,
                "core_all",
                method_id,
                [r for r in rows if r["case_stratum"] == "core_marked_sibling"],
                left_out_core_domain="",
                excluded_cases=0,
            )
            _write_row(
                writer,
                "hard_all",
                method_id,
                [r for r in rows if r["case_stratum"] == "hard_role_flip"],
                left_out_core_domain="",
                excluded_cases=0,
            )

            for domain in core_domains:
                excluded = [
                    r
                    for r in rows
                    if r["case_stratum"] == "core_marked_sibling" and r["domain"] == domain
                ]
                merged_kept = [
                    r
                    for r in rows
                    if not (r["case_stratum"] == "core_marked_sibling" and r["domain"] == domain)
                ]
                core_kept = [
                    r
                    for r in rows
                    if r["case_stratum"] == "core_marked_sibling" and r["domain"] != domain
                ]
                _write_row(
                    writer,
                    "merged_without_core_domain",
                    method_id,
                    merged_kept,
                    left_out_core_domain=domain,
                    excluded_cases=len(excluded),
                )
                _write_row(
                    writer,
                    "core_without_domain",
                    method_id,
                    core_kept,
                    left_out_core_domain=domain,
                    excluded_cases=len(excluded),
                )

    print(OUT)


if __name__ == "__main__":
    main()
