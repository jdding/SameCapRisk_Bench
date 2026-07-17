#!/usr/bin/env python3
"""Recompute clustered uncertainty for merged SameCapRisk comparisons.

Hard role-flip units contribute two related query cases, so uncertainty is
computed over benchmark units rather than treating all query cases as
independent observations. Point estimates remain query-weighted.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260711
BOOTSTRAP_SAMPLES = 5000
csv.field_size_limit(sys.maxsize)

METHODS = {
    "skillrouter_official": "SkillRouter",
    "skillret_embedding_0_6b": "SkillRet",
    "r3_skill_embedding_reranker": "R3-Skill",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def query_to_unit() -> dict[str, str]:
    rows = read_tsv(ROOT / "data" / "query_cases.tsv")
    mapping = {row["query_case_id"]: row["unit_id"] for row in rows}
    if len(mapping) != 1686 or len(set(mapping.values())) != 1190:
        raise RuntimeError("expected 1,686 query cases grouped into 1,190 units")
    return mapping


def prediction_maps() -> dict[str, dict[str, dict[str, str]]]:
    rows = read_tsv(ROOT / "results" / "compact_predictions.tsv")
    wanted = {"controlled_reference", *METHODS}
    out: dict[str, dict[str, dict[str, str]]] = {method: {} for method in wanted}
    for row in rows:
        method = row["method_id"]
        if method in out:
            out[method][row["query_case_id"]] = row
    for method, method_rows in out.items():
        if len(method_rows) != 1686:
            raise RuntimeError(f"{method}: expected 1,686 rows, found {len(method_rows)}")
    return out


def metric_value(row: dict[str, str], metric: str) -> float:
    if metric == "cleanhit_at_3":
        return float(float(row["recall_at_3"]) > 0.5 and float(row["hsr_at_3"]) < 0.5)
    return float(row[metric])


def direction_diff(reference: float, baseline: float, metric: str) -> float:
    if metric == "hsr_at_3":
        return baseline - reference
    return reference - baseline


def percentile(sorted_values: list[float], probability: float) -> float:
    index = max(0, min(len(sorted_values) - 1, int(probability * len(sorted_values))))
    return sorted_values[index]


def exact_two_sided_sign_p(successes: int, trials: int) -> float:
    if trials == 0:
        return 1.0
    tail = min(successes, trials - successes)
    log_two = math.log(2.0)
    cumulative = 0.0
    for k in range(tail + 1):
        log_p = (
            math.lgamma(trials + 1)
            - math.lgamma(k + 1)
            - math.lgamma(trials - k + 1)
            - trials * log_two
        )
        cumulative += math.exp(log_p)
    return min(1.0, 2.0 * cumulative)


def build_outputs() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    unit_for_query = query_to_unit()
    predictions = prediction_maps()
    query_ids = sorted(unit_for_query)
    unit_ids = sorted(set(unit_for_query.values()))
    rng = random.Random(SEED)
    bootstrap_rows: list[dict[str, object]] = []
    sign_rows: list[dict[str, object]] = []

    for baseline_id, baseline_label in METHODS.items():
        for metric in ("recall_at_3", "ndcg_at_3", "hsr_at_3"):
            diffs_by_unit: dict[str, list[float]] = defaultdict(list)
            for query_id in query_ids:
                reference = metric_value(predictions["controlled_reference"][query_id], metric)
                baseline = metric_value(predictions[baseline_id][query_id], metric)
                diffs_by_unit[unit_for_query[query_id]].append(direction_diff(reference, baseline, metric))
            estimate = sum(sum(values) for values in diffs_by_unit.values()) / len(query_ids)
            samples = []
            for _ in range(BOOTSTRAP_SAMPLES):
                total = 0.0
                query_count = 0
                for _ in unit_ids:
                    values = diffs_by_unit[unit_ids[rng.randrange(len(unit_ids))]]
                    total += sum(values)
                    query_count += len(values)
                samples.append(total / query_count)
            samples.sort()
            bootstrap_rows.append({
                "comparison": f"Reference pipeline vs {baseline_label}",
                "metric": metric,
                "direction": "baseline_minus_reference" if metric == "hsr_at_3" else "reference_minus_baseline",
                "estimate": f"{estimate:.6f}",
                "ci_low": f"{percentile(samples, 0.025):.6f}",
                "ci_high": f"{percentile(samples, 0.975):.6f}",
                "n": len(unit_ids),
                "query_n": len(query_ids),
                "bootstrap_samples": BOOTSTRAP_SAMPLES,
                "seed": SEED,
                "resampling_unit": "benchmark_unit",
            })

        for metric in ("recall_at_3", "hsr_at_3", "cleanhit_at_3"):
            unit_diffs: dict[str, list[float]] = defaultdict(list)
            baseline_success = 0
            reference_success = 0
            query_diffs = []
            for query_id in query_ids:
                reference = metric_value(predictions["controlled_reference"][query_id], metric)
                baseline = metric_value(predictions[baseline_id][query_id], metric)
                reference_success += int(reference > 0.5)
                baseline_success += int(baseline > 0.5)
                diff = direction_diff(reference, baseline, metric)
                query_diffs.append(diff)
                unit_diffs[unit_for_query[query_id]].append(diff)
            unit_means = [sum(values) / len(values) for values in unit_diffs.values()]
            reference_better = sum(value > 0 for value in unit_means)
            baseline_better = sum(value < 0 for value in unit_means)
            discordant = reference_better + baseline_better
            sign_rows.append({
                "comparison": f"Reference pipeline vs {baseline_label}",
                "metric": metric,
                "reported_direction": "Baseline minus reference" if metric == "hsr_at_3" else "Reference minus baseline",
                "n": len(unit_ids),
                "query_n": len(query_ids),
                "baseline_success": baseline_success,
                "reference_success": reference_success,
                "mean_delta": f"{sum(query_diffs) / len(query_diffs):.6f}",
                "discordant_n": discordant,
                "reference_better_n": reference_better,
                "baseline_better_n": baseline_better,
                "two_sided_sign_p": f"{exact_two_sided_sign_p(reference_better, discordant):.6g}",
                "comparison_unit": "benchmark_unit",
            })
    return bootstrap_rows, sign_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare computed rows with released TSVs")
    args = parser.parse_args()
    bootstrap_rows, sign_rows = build_outputs()
    bootstrap_path = ROOT / "results" / "paired_bootstrap_ci.tsv"
    sign_path = ROOT / "reports" / "paired_sign_tests.tsv"
    bootstrap_fields = [
        "comparison", "metric", "direction", "estimate", "ci_low", "ci_high", "n", "query_n",
        "bootstrap_samples", "seed", "resampling_unit",
    ]
    sign_fields = [
        "comparison", "metric", "reported_direction", "n", "query_n", "baseline_success",
        "reference_success", "mean_delta", "discordant_n", "reference_better_n",
        "baseline_better_n", "two_sided_sign_p", "comparison_unit",
    ]
    if args.check:
        expected_bootstrap = read_tsv(bootstrap_path)
        expected_sign = read_tsv(sign_path)
        ok = expected_bootstrap == [{key: str(row[key]) for key in bootstrap_fields} for row in bootstrap_rows]
        ok = ok and expected_sign == [{key: str(row[key]) for key in sign_fields} for row in sign_rows]
        print("status: ok" if ok else "status: mismatch")
        return 0 if ok else 1
    write_tsv(bootstrap_path, bootstrap_rows, bootstrap_fields)
    write_tsv(sign_path, sign_rows, sign_fields)
    print(f"wrote {len(bootstrap_rows)} bootstrap rows and {len(sign_rows)} sign-test rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
