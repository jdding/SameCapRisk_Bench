#!/usr/bin/env python3
"""Validate the paper-facing SameCapRisk-Bench release package.

This script checks the schema/count invariants behind the benchmark
composition table, family-source diagnostics, selector certificates, and label
validity reports. It verifies the released review surface; GPU model inference
and private construction transcripts are intentionally outside this package.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
csv.field_size_limit(sys.maxsize)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_columns(rows: list[dict[str, str]], required: list[str], label: str, errors: list[str]) -> None:
    if not rows:
        errors.append(f"{label} is empty")
        return
    observed = set(rows[0].keys())
    missing = [column for column in required if column not in observed]
    require(not missing, f"{label} missing columns: {missing}", errors)


def float_close(observed: str, expected: float, tolerance: float = 5e-6) -> bool:
    return abs(float(observed) - expected) <= tolerance


def main() -> int:
    errors: list[str] = []

    required_files = [
        ROOT / "README.md",
        ROOT / "ARTIFACT_QUICKSTART.md",
        ROOT / "DATA_CARD.md",
        ROOT / "EVALUATION_PROTOCOL.md",
        ROOT / "BOUNDARIES.md",
        ROOT / "manifest.json",
        ROOT / "data" / "units.tsv",
        ROOT / "data" / "query_cases.tsv",
        ROOT / "data" / "candidate_pool.tsv",
        ROOT / "data" / "family_relation.tsv",
        ROOT / "results" / "main_table.tsv",
        ROOT / "results" / "cutoff_sensitivity.tsv",
        ROOT / "results" / "extended_k20.tsv",
        ROOT / "results" / "selector_certificate.tsv",
        ROOT / "results" / "compact_predictions.tsv",
        ROOT / "results" / "selector_certificate_cases.tsv",
        ROOT / "results" / "stratum_metrics.tsv",
        ROOT / "results" / "paired_bootstrap_ci.tsv",
        ROOT / "reports" / "paired_sign_tests.tsv",
        ROOT / "reports" / "benchmark_composition_summary.tsv",
        ROOT / "reports" / "environment_provenance.tsv",
        ROOT / "reports" / "reference_scorer_config.json",
        ROOT / "reports" / "table3_family_source_reference.tsv",
        ROOT / "results" / "diagnostics" / "reference_family_source_per_query.tsv",
        ROOT / "results" / "diagnostics" / "bge_reranker_two_stage_summary.tsv",
        ROOT / "results" / "diagnostics" / "open_llm_listwise_summary.tsv",
        ROOT / "results" / "diagnostics" / "r3_skill_per_query.tsv",
        ROOT / "results" / "diagnostics" / "r3_skill_summary.tsv",
        ROOT / "results" / "diagnostics" / "r3_skill_top20.tsv",
        ROOT / "results" / "diagnostics" / "r3_skill_status.json",
        ROOT / "results" / "diagnostics" / "selector_on_public_scores_summary.tsv",
        ROOT / "results" / "diagnostics" / "selector_on_public_scores_per_query.tsv",
        ROOT / "results" / "diagnostics" / "selector_on_public_scores_unmarked_pressure.tsv",
        ROOT / "results" / "diagnostics" / "selector_on_public_scores_status.json",
        ROOT / "results" / "diagnostics" / "public_family_source_selector_summary.tsv",
        ROOT / "results" / "diagnostics" / "public_family_source_selector_per_query.tsv",
        ROOT / "results" / "diagnostics" / "public_family_source_selector_status.json",
        ROOT / "reports" / "admission_ledger.tsv",
        ROOT / "reports" / "hard_leakage_per_family.tsv",
        ROOT / "reports" / "gate_summaries" / "hard_blind_gate_external_summary.json",
        ROOT / "reports" / "gate_summaries" / "hard_oracle_gate_external_summary.json",
        ROOT / "reports" / "gate_summaries" / "hard_leakage_diversity_summary.json",
        ROOT / "reports" / "gate_summaries" / "README.md",
        ROOT / "reports" / "label_validity" / "natural_validation" / "natural_validation_accounting.tsv",
        ROOT / "reports" / "label_validity" / "natural_validation" / "natural_validation_consensus.tsv",
        ROOT / "reports" / "label_validity" / "natural_validation" / "natural_validation_summary.json",
        ROOT / "reports" / "chooser_proxy" / "README.md",
        ROOT / "reports" / "chooser_proxy" / "chooser_prompt.md",
        ROOT / "reports" / "chooser_proxy" / "r3_condition_summary.tsv",
        ROOT / "reports" / "chooser_proxy" / "r3_paired_effects.tsv",
        ROOT / "reports" / "chooser_proxy" / "bge_condition_summary.tsv",
        ROOT / "reports" / "chooser_proxy" / "bge_paired_effects.tsv",
        ROOT / "schemas" / "units.schema.json",
        ROOT / "schemas" / "query_cases.schema.json",
        ROOT / "schemas" / "candidate_pool.schema.json",
        ROOT / "schemas" / "family_relation.schema.json",
        ROOT / "schemas" / "compact_predictions.schema.json",
        ROOT / "schemas" / "paired_bootstrap_ci.schema.json",
        ROOT / "scripts" / "reproduce_results.py",
        ROOT / "scripts" / "reproduce_family_source.py",
        ROOT / "scripts" / "recompute_uncertainty.py",
        ROOT / "LICENSE",
        ROOT / "SOURCE_AND_LICENSES.md",
    ]
    for path in required_files:
        require(path.exists(), f"missing required file: {path.relative_to(ROOT)}", errors)

    if not errors:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        counts = manifest["counts"]
        units = read_tsv(ROOT / "data" / "units.tsv")
        query_cases = read_tsv(ROOT / "data" / "query_cases.tsv")
        candidates = read_tsv(ROOT / "data" / "candidate_pool.tsv")
        family = read_tsv(ROOT / "data" / "family_relation.tsv")
        main_table = read_tsv(ROOT / "results" / "main_table.tsv")
        cutoff_sensitivity = read_tsv(ROOT / "results" / "cutoff_sensitivity.tsv")
        extended = read_tsv(ROOT / "results" / "extended_k20.tsv")
        certificate = read_tsv(ROOT / "results" / "selector_certificate.tsv")
        compact_predictions = read_tsv(ROOT / "results" / "compact_predictions.tsv")
        selector_cases = read_tsv(ROOT / "results" / "selector_certificate_cases.tsv")
        stratum_metrics = read_tsv(ROOT / "results" / "stratum_metrics.tsv")
        paired_ci = read_tsv(ROOT / "results" / "paired_bootstrap_ci.tsv")
        paired_sign = read_tsv(ROOT / "reports" / "paired_sign_tests.tsv")
        composition_summary = read_tsv(ROOT / "reports" / "benchmark_composition_summary.tsv")
        environment_provenance = read_tsv(ROOT / "reports" / "environment_provenance.tsv")
        scorer_config = json.loads((ROOT / "reports" / "reference_scorer_config.json").read_text(encoding="utf-8"))
        family_source_reference = read_tsv(ROOT / "reports" / "table3_family_source_reference.tsv")
        family_source_per_query = read_tsv(
            ROOT / "results" / "diagnostics" / "reference_family_source_per_query.tsv"
        )
        bge_reranker = read_tsv(ROOT / "results" / "diagnostics" / "bge_reranker_two_stage_summary.tsv")
        open_llm = read_tsv(ROOT / "results" / "diagnostics" / "open_llm_listwise_summary.tsv")
        admission_ledger = read_tsv(ROOT / "reports" / "admission_ledger.tsv")
        selector_public_summary = read_tsv(ROOT / "results" / "diagnostics" / "selector_on_public_scores_summary.tsv")
        selector_public_per_query = read_tsv(ROOT / "results" / "diagnostics" / "selector_on_public_scores_per_query.tsv")
        selector_public_unmarked = read_tsv(ROOT / "results" / "diagnostics" / "selector_on_public_scores_unmarked_pressure.tsv")
        public_family_summary = read_tsv(ROOT / "results" / "diagnostics" / "public_family_source_selector_summary.tsv")
        public_family_per_query = read_tsv(ROOT / "results" / "diagnostics" / "public_family_source_selector_per_query.tsv")
        natural_validation = read_tsv(
            ROOT / "reports" / "label_validity" / "natural_validation" / "natural_validation_consensus.tsv"
        )
        natural_summary = json.loads(
            (ROOT / "reports" / "label_validity" / "natural_validation" / "natural_validation_summary.json").read_text(
                encoding="utf-8"
            )
        )
        chooser_r3_summary = read_tsv(ROOT / "reports" / "chooser_proxy" / "r3_condition_summary.tsv")
        chooser_bge_summary = read_tsv(ROOT / "reports" / "chooser_proxy" / "bge_condition_summary.tsv")
        chooser_r3_pairs = read_tsv(ROOT / "reports" / "chooser_proxy" / "r3_paired_effects.tsv")
        chooser_bge_pairs = read_tsv(ROOT / "reports" / "chooser_proxy" / "bge_paired_effects.tsv")

        require(len(units) == 1190, f"expected 1190 units, found {len(units)}", errors)
        require(len(query_cases) == 1686, f"expected 1686 query cases, found {len(query_cases)}", errors)
        require(len(candidates) == 9040, f"expected 9040 candidates, found {len(candidates)}", errors)
        require(len(family) == 9040, f"expected 9040 family rows, found {len(family)}", errors)

        require(len(units) == counts["units_total"], "unit count does not match manifest", errors)
        require(len(query_cases) == counts["query_cases_total"], "query-case count does not match manifest", errors)
        require(len(candidates) == counts["candidate_pool_total"], "candidate count does not match manifest", errors)
        require(len(family) == counts["family_relation_rows"], "family count does not match manifest", errors)

        composition_counts = {
            (row["axis"], row["category"]): int(row["unit_count"])
            for row in composition_summary
        }
        require(
            composition_counts == {
                ("evidence_layer", "source_and_admission_audited_core"): 630,
                ("evidence_layer", "executable_or_oracle_backed_core"): 64,
                ("evidence_layer", "blind_oracle_leakage_audited_hard"): 496,
                ("core_risk_type", "wrong_resource_pointer"): 390,
                ("core_risk_type", "wrong_precondition"): 232,
                ("core_risk_type", "poisoned_procedure_clause"): 34,
                ("core_risk_type", "deterministic_oracle"): 33,
                ("core_risk_type", "stale_api_reference"): 3,
                ("core_risk_type", "misleading_example"): 2,
            },
            "benchmark composition summary mismatch",
            errors,
        )
        require(len(environment_provenance) == 9, "environment provenance row count mismatch", errors)
        require(
            len(family_source_per_query) == 5058
            and Counter(row["family_source"] for row in family_source_per_query)
            == {
                "controlled_relation": 1686,
                "public_metadata_title": 1686,
                "public_text_cluster": 1686,
            },
            "reference family-source per-query accounting mismatch",
            errors,
        )
        core_config = scorer_config.get("core_scorer", {})
        implementation_provenance = scorer_config.get("implementation_provenance", {})
        require(
            core_config.get("cv_protocol") == "five_grouped_held_out_folds"
            and core_config.get("C") == 1.0
            and core_config.get("solver") == "liblinear"
            and core_config.get("confusable_rank_depth") == 50
            and core_config.get("max_confusable_negatives_per_query") == 5
            and core_config.get("gamma_grid") == [0.0, 0.1, 0.25, 0.5, 1.0]
            and core_config.get("paired_risky_sibling_used_for_training") is False,
            "reference scorer configuration mismatch",
            errors,
        )
        require(
            implementation_provenance.get("training_scripts_included") is False
            and implementation_provenance.get("core_reference_source_sha256")
            == "b19d8135d59e56a5cf8d4cf1660bd9ca29b6ddb1d7dcd34987a06d5d416007c0"
            and implementation_provenance.get("query_repair_refresh_source_sha256")
            == "47f26f689c468b19c03f3a47837d70155b5fc073f929889dc0f092f54c8e8727",
            "reference scorer source provenance mismatch",
            errors,
        )

        for label, rows in (("R3 chooser", chooser_r3_summary), ("BGE chooser", chooser_bge_summary)):
            require(all(
                int(row["parsed"]) == int(row["pass"]) + int(row["fail"])
                + int(row["unknown"]) - int(row["parse_failure"])
                and int(row["n"]) == int(row["parsed"]) + int(row["parse_failure"])
                for row in rows
            ), f"{label} condition accounting does not close", errors)
        require(len(chooser_r3_pairs) == 48, f"expected 48 R3 chooser pairs, found {len(chooser_r3_pairs)}", errors)
        require(len(chooser_bge_pairs) == 48, f"expected 48 BGE chooser pairs, found {len(chooser_bge_pairs)}", errors)
        require(sum(int(row["introduced_marked_risky_choice"]) for row in chooser_r3_pairs) == 8, "R3 chooser paired effect mismatch", errors)
        require(sum(int(row["introduced_marked_risky_choice"]) for row in chooser_bge_pairs) == 10, "BGE chooser paired effect mismatch", errors)

        unit_strata = Counter(row["stratum"] for row in units)
        query_strata = Counter(row["stratum"] for row in query_cases)
        require(unit_strata == {"core_marked_sibling": 694, "hard_role_flip": 496}, f"unexpected unit strata: {dict(unit_strata)}", errors)
        require(query_strata == {"core_marked_sibling": 694, "hard_role_flip": 992}, f"unexpected query strata: {dict(query_strata)}", errors)

        require_columns(units, json.loads((ROOT / "schemas" / "units.schema.json").read_text(encoding="utf-8"))["required_columns"], "units.tsv", errors)
        require_columns(query_cases, json.loads((ROOT / "schemas" / "query_cases.schema.json").read_text(encoding="utf-8"))["required_columns"], "query_cases.tsv", errors)
        require_columns(candidates, json.loads((ROOT / "schemas" / "candidate_pool.schema.json").read_text(encoding="utf-8"))["required_columns"], "candidate_pool.tsv", errors)
        require_columns(family, json.loads((ROOT / "schemas" / "family_relation.schema.json").read_text(encoding="utf-8"))["required_columns"], "family_relation.tsv", errors)
        require_columns(compact_predictions, json.loads((ROOT / "schemas" / "compact_predictions.schema.json").read_text(encoding="utf-8"))["required_columns"], "compact_predictions.tsv", errors)

        unit_ids = {row["unit_id"] for row in units}
        query_ids = {row["query_case_id"] for row in query_cases}
        candidate_ids = {row["candidate_id"] for row in candidates}
        require(len(unit_ids) == len(units), "duplicate unit_id rows", errors)
        require(len(query_ids) == len(query_cases), "duplicate query_case_id rows", errors)
        require(len(candidate_ids) == len(candidates), "duplicate candidate_id rows", errors)
        require(all(row["unit_id"] in unit_ids for row in query_cases), "query_cases contains unknown unit_id", errors)
        require(all(row["helpful_skill_id"] in candidate_ids and row["risky_sibling_id"] in candidate_ids for row in query_cases), "query_cases contains unknown helpful/risky candidate id", errors)
        require(all(row["candidate_id"] in candidate_ids for row in family), "family_relation contains unknown candidate id", errors)

        hard_units = [row for row in units if row["stratum"] == "hard_role_flip"]
        require(all(row["role_flip"] == "yes" for row in hard_units), "hard units must be role_flip=yes", errors)
        require(all(row["oracle_gate_status"] == "pass" for row in hard_units), "hard units must pass oracle gate", errors)
        require(all(row["blind_gate_status"] == "blind_gate_pass" for row in hard_units), "hard units must pass blind gate", errors)
        require(all(row["leakage_flag"] == "none" for row in hard_units), "hard units must have leakage_flag=none", errors)

        hard_query_cases = [row for row in query_cases if row["stratum"] == "hard_role_flip"]
        hard_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in hard_query_cases:
            hard_by_unit[row["unit_id"]].append(row)
        require(all(len(rows) == 2 for rows in hard_by_unit.values()), "each hard unit must have exactly two query cases", errors)
        for unit_id, rows in hard_by_unit.items():
            helpful_ids = {row["helpful_skill_id"] for row in rows}
            risky_ids = {row["risky_sibling_id"] for row in rows}
            require(helpful_ids == risky_ids and len(helpful_ids) == 2, f"hard role-flip ids do not swap for {unit_id}", errors)

        duplicate_query_hashes = [sha for sha, count in Counter(row["query_sha256"] for row in query_cases).items() if count > 1]
        hard_duplicate_hashes = [sha for sha in duplicate_query_hashes if any(row["query_sha256"] == sha and row["stratum"] == "hard_role_flip" for row in query_cases)]
        require(not hard_duplicate_hashes, f"hard stratum has duplicate query hashes: {hard_duplicate_hashes[:5]}", errors)

        expected_methods = {
            "hybrid_lexical_rrf",
            "skillrouter_official",
            "skillret_embedding_0_6b",
            "r3_skill_embedding_reranker",
            "controlled_reference",
        }
        observed_methods = {row["method_id"] for row in main_table}
        require(observed_methods == expected_methods, f"unexpected main-table methods: {sorted(observed_methods)}", errors)
        for row in main_table:
            require(row["status"] == "complete", f"{row['method_id']} is not complete", errors)
            require(row["overall_n"] == "1686", f"{row['method_id']} overall_n is not 1686", errors)
            require(row["core_n"] == "694", f"{row['method_id']} core_n is not 694", errors)
            require(row["hard_n"] == "992", f"{row['method_id']} hard_n is not 992", errors)

        cutoff_methods = {row["method_id"] for row in cutoff_sensitivity}
        require(cutoff_methods == expected_methods, f"unexpected cutoff-sensitivity methods: {sorted(cutoff_methods)}", errors)
        require_columns(
            cutoff_sensitivity,
            [
                "method_id",
                "paper_label",
                "overall_n",
                "recall_at_3",
                "hsr_at_3",
                "recall_at_10",
                "hsr_at_10",
                "recall_at_20",
                "hsr_at_20",
            ],
            "cutoff_sensitivity.tsv",
            errors,
        )
        for row in cutoff_sensitivity:
            require(row["overall_n"] == "1686", f"{row['method_id']} cutoff overall_n is not 1686", errors)

        extended_methods = {row["method_id"] for row in extended}
        require(extended_methods == expected_methods, f"unexpected extended-table methods: {sorted(extended_methods)}", errors)
        for row in extended:
            require(row["status"] == "complete", f"{row['method_id']} extended row is not complete", errors)
            require(row["overall_n"] == "1686", f"{row['method_id']} extended overall_n is not 1686", errors)
            require("recall_at_20" in row and "hsr_at_20" in row, "extended table must contain @20 columns", errors)
        require_columns(
            certificate,
            [
                "k",
                "core_no_selection_exposed",
                "hard_no_selection_exposed",
                "merged_no_selection_exposed",
                "core_resolved_exposed",
                "hard_resolved_exposed",
                "merged_resolved_exposed",
                "core_final_exposed",
                "hard_final_exposed",
                "merged_final_exposed",
                "merged_n",
            ],
            "selector_certificate.tsv",
            errors,
        )
        require({row["k"] for row in certificate} == {"3", "5", "20"}, "selector certificate must contain K=3/5/20", errors)
        final_exposed = {row["k"]: row["merged_final_exposed"] for row in certificate}
        require(final_exposed == {"3": "12", "5": "33", "20": "70"}, f"unexpected final exposure counts: {final_exposed}", errors)
        prediction_counts = Counter(row["method_id"] for row in compact_predictions)
        require(prediction_counts == {
            "hybrid_lexical_rrf": 1686,
            "skillrouter_official": 1686,
            "skillret_embedding_0_6b": 1686,
            "r3_skill_embedding_reranker": 1686,
            "bge_m3_dense": 1686,
            "bge_m3_bge_reranker": 1686,
            "qwen2_5_7b_listwise_bge_m3_top20": 1686,
            "controlled_reference": 1686,
        }, f"unexpected compact prediction counts: {dict(prediction_counts)}", errors)
        require(all(row["query_case_id"] in query_ids for row in compact_predictions), "compact predictions contain unknown query_case_id", errors)
        r3_predictions = read_tsv(ROOT / "results" / "diagnostics" / "r3_skill_per_query.tsv")
        require(len(r3_predictions) == 1686, f"expected 1686 R3-Skill prediction rows, found {len(r3_predictions)}", errors)
        require({row["method_id"] for row in r3_predictions} == {"r3_skill_embedding_reranker"}, "R3-Skill predictions use unexpected method_id", errors)
        require(all(row["query_case_id"] in query_ids for row in r3_predictions), "R3-Skill predictions contain unknown query_case_id", errors)
        selector_methods = {
            "hybrid_lexical_rrf",
            "skillrouter_official",
            "skillret_embedding_0_6b",
            "r3_skill_embedding_reranker",
        }
        require({row["method_id"] for row in selector_public_summary} == selector_methods, "same-score selector summary has unexpected methods", errors)
        require({row["stratum"] for row in selector_public_summary} == {"core", "hard", "merged"}, "same-score selector summary must cover core/hard/merged", errors)
        require(len(selector_public_summary) == 12, f"expected 12 same-score selector summary rows, found {len(selector_public_summary)}", errors)
        require(len(selector_public_per_query) == 6744, f"expected 6744 same-score selector per-query rows, found {len(selector_public_per_query)}", errors)
        require(len(selector_public_unmarked) == 12, f"expected 12 same-score unmarked-pressure rows, found {len(selector_public_unmarked)}", errors)
        require(all(row["query_id"] in query_ids for row in selector_public_per_query), "same-score selector rows contain unknown query_id", errors)
        r3_selector_rows = [row for row in selector_public_summary if row["method_id"] == "r3_skill_embedding_reranker" and row["stratum"] == "merged"]
        require(len(r3_selector_rows) == 1, "missing merged R3-Skill same-score selector row", errors)
        if r3_selector_rows:
            row = r3_selector_rows[0]
            require(float_close(row["recall_at_3_before"], 0.888494) and float_close(row["hsr_at_3_before"], 0.372479), "R3-Skill same-score selector before values mismatch", errors)
            require(float_close(row["recall_at_3_after"], 0.753855) and float_close(row["hsr_at_3_after"], 0.162515), "R3-Skill same-score selector after values mismatch", errors)
        require({row["method_id"] for row in public_family_summary} == selector_methods, "public family-source selector summary has unexpected methods", errors)
        require({row["resolver"] for row in public_family_summary} == {"metadata_title", "text_cluster"}, "public family-source summary has unexpected resolvers", errors)
        require({row["stratum"] for row in public_family_summary} == {"core", "hard", "merged"}, "public family-source summary must cover core/hard/merged", errors)
        require(len(public_family_summary) == 24, f"expected 24 public family-source summary rows, found {len(public_family_summary)}", errors)
        require(len(public_family_per_query) == 13488, f"expected 13488 public family-source per-query rows, found {len(public_family_per_query)}", errors)
        require(all(row["query_id"] in query_ids for row in public_family_per_query), "public family-source selector rows contain unknown query_id", errors)
        require(all(row["helpful_id"] in candidate_ids and row["risk_id"] in candidate_ids for row in public_family_per_query), "public family-source selector rows contain unknown helpful/risk candidate id", errors)
        r3_text_rows = [
            row for row in public_family_summary
            if row["method_id"] == "r3_skill_embedding_reranker"
            and row["stratum"] == "merged"
            and row["resolver"] == "text_cluster"
        ]
        require(len(r3_text_rows) == 1, "missing merged R3-Skill public text-cluster row", errors)
        if r3_text_rows:
            row = r3_text_rows[0]
            require(float_close(row["recall_at_3_after"], 0.749110) and float_close(row["hsr_at_3_after"], 0.180308), "R3-Skill public text-cluster values mismatch", errors)
        require(len(selector_cases) == 5058, f"expected 5058 selector case rows, found {len(selector_cases)}", errors)
        require({row["k"] for row in selector_cases} == {"3", "5", "20"}, "selector case rows must contain K=3/5/20", errors)
        require(len(admission_ledger) == 1190, f"expected 1190 admission ledger rows, found {len(admission_ledger)}", errors)
        require({row["unit_id"] for row in admission_ledger} == unit_ids, "admission ledger unit ids do not match units.tsv", errors)
        require(Counter(row["final_admission_status"] for row in admission_ledger)["admitted_after_blind_oracle_leakage_release_gates"] == 496, "hard admission ledger count mismatch", errors)
        require(len(stratum_metrics) >= 14, "stratum metrics table is unexpectedly small", errors)
        require(len(paired_ci) == 9, f"expected 9 paired CI rows, found {len(paired_ci)}", errors)
        require({row["metric"] for row in paired_ci} == {"recall_at_3", "ndcg_at_3", "hsr_at_3"}, "paired CI must cover R@3/NDCG@3/HSR@3", errors)
        require(all(
            row["n"] == "1190"
            and row["query_n"] == "1686"
            and row["resampling_unit"] == "benchmark_unit"
            for row in paired_ci
        ), "paired CI uses unexpected n or resampling unit", errors)
        require(len(paired_sign) == 9, f"expected 9 paired sign-test rows, found {len(paired_sign)}", errors)
        require(all(
            row["n"] == "1190"
            and row["query_n"] == "1686"
            and row["comparison_unit"] == "benchmark_unit"
            for row in paired_sign
        ), "paired sign tests use unexpected n or comparison unit", errors)
        r3_sign = [
            row for row in paired_sign
            if row["comparison"] == "Reference pipeline vs R3-Skill"
            and row["metric"] == "hsr_at_3"
        ]
        require(len(r3_sign) == 1, "missing R3-Skill HSR paired sign-test row", errors)
        if r3_sign:
            require(r3_sign[0]["n"] == "1190" and r3_sign[0]["discordant_n"] == "627", "R3-Skill HSR paired sign-test n mismatch", errors)
            require(float_close(r3_sign[0]["mean_delta"], 0.365362), "R3-Skill HSR paired sign-test delta mismatch", errors)
        text_ref = [row for row in family_source_reference if row["resolver"] == "Text cluster"]
        require(len(text_ref) == 1, "missing text-cluster reference resolver row", errors)
        if text_ref:
            require(float_close(text_ref[0]["merged_recall_at_3"], 0.809609), "text-cluster reference recall mismatch", errors)
            require(float_close(text_ref[0]["merged_hsr_at_3"], 0.011862), "text-cluster reference HSR mismatch", errors)
        bge_rows = [row for row in bge_reranker if row["method_id"] == "bge_m3_bge_reranker" and row["scope"] == "merged_all"]
        require(len(bge_rows) == 1, "missing merged BGE reranker diagnostic row", errors)
        if bge_rows:
            require(float_close(bge_rows[0]["recall_at_3"], 0.814947), "BGE reranker recall mismatch", errors)
            require(float_close(bge_rows[0]["hsr_at_3"], 0.314947), "BGE reranker HSR mismatch", errors)
        qwen_rows = [row for row in open_llm if row["method"] == "Qwen2.5-7B listwise over BGE-M3 top20" and row["scope"] == "all"]
        require(len(qwen_rows) == 1, "missing merged Qwen listwise diagnostic row", errors)
        if qwen_rows:
            require(float_close(qwen_rows[0]["R@3"], 0.798339), "Qwen listwise recall mismatch", errors)
            require(float_close(qwen_rows[0]["HSR@3"], 0.344009), "Qwen listwise HSR mismatch", errors)

        natural_pass = [row for row in natural_validation if row["final_admission"] == "pass"]
        require(len(natural_validation) == 63, "natural-validation candidate count mismatch", errors)
        require(
            sum(row["blind_consensus"] == "pass" for row in natural_validation) == 48,
            "natural-validation blind-pass count mismatch",
            errors,
        )
        require(len(natural_pass) == 37, "natural-validation strict consensus count mismatch", errors)
        require(
            len({row["strict_family"] for row in natural_pass}) == 22,
            "natural-validation strict-family count mismatch",
            errors,
        )
        require(
            Counter(row["risk_type_guess"] for row in natural_pass)
            == {"wrong_precondition": 20, "wrong_resource_pointer": 17},
            "natural-validation risk-type count mismatch",
            errors,
        )
        require(
            natural_summary.get("status") == "GO_BOUNDED_MODEL_SCREENED_NATURAL_VALIDATION"
            and natural_summary.get("strict_oracle_consensus_pass_rows") == 37
            and natural_summary.get("unique_strict_families") == 22,
            "natural-validation summary mismatch",
            errors,
        )

        blind = json.loads((ROOT / "reports" / "gate_summaries" / "hard_blind_gate_external_summary.json").read_text(encoding="utf-8"))
        oracle = json.loads((ROOT / "reports" / "gate_summaries" / "hard_oracle_gate_external_summary.json").read_text(encoding="utf-8"))
        leakage = json.loads((ROOT / "reports" / "gate_summaries" / "hard_leakage_diversity_summary.json").read_text(encoding="utf-8"))
        for label, summary_doc in [("blind", blind), ("oracle", oracle)]:
            provenance = summary_doc.get("provenance_counts", {})
            require(summary_doc.get("judge_model") == "external_model_a", f"{label} gate judge mismatch", errors)
            require(summary_doc.get("rows") == 449, f"{label} gate final-bulk row count mismatch", errors)
            require(summary_doc.get("external_review_rows") == 449, f"{label} gate external row count mismatch", errors)
            require(summary_doc.get("early_hard_candidates") == 47, f"{label} gate early hard count mismatch", errors)
            require(summary_doc.get("full_naturalized_repair") == 449, f"{label} gate naturalized repair count mismatch", errors)
            require(summary_doc.get("combined_admitted_hard_units") == 496, f"{label} gate combined hard count mismatch", errors)
            require(provenance.get("early_hard_candidates") == 47 and provenance.get("full_naturalized_repair") == 449, f"{label} gate provenance count mismatch", errors)
            require(summary_doc.get("combined_release_gate_status") == "pass", f"{label} gate release status mismatch", errors)
        require(leakage.get("status") == "PASS_CLEAN" and leakage.get("candidate_families") == 496, "leakage/diversity summary mismatch", errors)
        leakage_provenance = leakage.get("provenance_counts", {})
        require(leakage_provenance.get("early_hard_candidates") == 47 and leakage_provenance.get("full_naturalized_repair") == 449, "leakage/diversity provenance count mismatch", errors)

    summary = {
        "status": "ok" if not errors else "fail",
        "errors": errors,
        "root": ".",
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "validation_report.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
