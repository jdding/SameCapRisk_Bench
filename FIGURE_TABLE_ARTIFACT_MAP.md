# Figure and Table Artifact Map

This map links paper-facing claims to reviewer-visible files in this release.
Paths are relative to the root of the code/data supplement.

| Paper item | Claim supported | Primary files | Reproduction/check |
|---|---|---|---|
| Table 1: Benchmark composition | Unit, query-case, candidate-row, evidence-layer, and core risk-type accounting | `manifest.json`, `data/units.tsv`, `data/query_cases.tsv`, `data/candidate_pool.tsv`, `reports/benchmark_composition_summary.tsv` | `bash scripts/run_release_checks.sh` |
| Table 2: Query-weighted merged retrieval | Recall/NDCG/HSR/CleanHit for public retrievers, including R3-Skill, and the controlled-family reference pipeline | `results/main_table.tsv`, `results/compact_predictions.tsv`, `results/diagnostics/r3_skill_per_query.tsv` | `python3 scripts/reproduce_results.py` |
| Figure 3: Recall-HSR decomposition | Public retrievers pair high recall with high marked-sibling exposure; same-score selector rows lower exposure with recall cost | `results/main_table.tsv`, `results/diagnostics/selector_on_public_scores_summary.tsv`, `results/diagnostics/r3_skill_per_query.tsv` | `python3 scripts/reproduce_results.py`; selector diagnostic is a fixed summary |
| Table 3: Open listwise reranking diagnostic | Qwen2.5-7B listwise reranking over BGE-M3 top-20 improves recall/CleanHit but leaves HSR high | `results/diagnostics/open_llm_listwise_summary.tsv`, `results/compact_predictions.tsv` | `python3 scripts/reproduce_results.py` recomputes BGE/Qwen metrics from 1,686 per-query ranks |
| Table 4: Family-source sensitivity | Public metadata/title and text-cluster resolvers reduce exposure without released family labels, but do not match the controlled relation | `reports/table3_family_source_reference.tsv`, `results/diagnostics/reference_family_source_per_query.tsv` | `python3 scripts/reproduce_family_source.py` recomputes all three rows from per-query indicators |
| Table 5: Cutoff sensitivity | Recall-HSR tradeoff persists at K=3/10/20 | `results/cutoff_sensitivity.tsv`, `results/extended_k20.tsv` | `python3 scripts/reproduce_results.py` |
| Table 6: Stratum decomposition | Core supplies public-library pressure; hard role-flip supplies query-necessity pressure and residual HSR headroom | `results/stratum_metrics.tsv`, `reports/source_domain_composition.tsv` | `python3 scripts/reproduce_results.py` |
| Table 7: Selector certificate | Same scorer before/after representative selection: residual exposure drops from pre-selection counts to final exposure counts | `results/selector_certificate.tsv`, `results/selector_certificate_cases.tsv` | `python3 scripts/reproduce_results.py` |
| Appendix Table B.1 | Extended stratum results including no-selector row and NDCG | `results/stratum_metrics.tsv` | `python3 scripts/reproduce_results.py` |
| Appendix uncertainty tests | Clustered bootstrap intervals and paired sign tests over benchmark units | `results/paired_bootstrap_ci.tsv`, `reports/paired_sign_tests.tsv` | `python3 scripts/recompute_uncertainty.py --check` |
| Appendix family-source diagnostics | Released selector, public text selector, R3-Skill, BGE diagnostics, Qwen listwise diagnostic, and reference resolver source rows | `results/diagnostics/selector_on_public_scores_summary.tsv`, `results/diagnostics/public_family_source_selector_summary.tsv`, `results/diagnostics/`, `reports/table3_family_source_reference.tsv` | `bash scripts/run_release_checks.sh` checks file presence and schemas |
| Label-validity and HSR scope discussion | Verifier/SkillsBench/hard-gate evidence, family-pressure scope, and natural-candidate occurrence checks | `reports/label_validity/`, `reports/gate_summaries/`, `reports/admission_ledger.tsv`, `results/diagnostics/selector_on_public_scores_unmarked_pressure.tsv` | `bash scripts/run_release_checks.sh` |
| Natural-candidate validation | Bounded occurrence evidence from organic public retrieval candidates; excluded from benchmark scores | `reports/label_validity/natural_validation/` | `bash scripts/run_release_checks.sh` |
| Appendix chooser proxy | Fixed chooser prompt, condition accounting, and paired natural/risk-added effects | `reports/chooser_proxy/` | `bash scripts/run_release_checks.sh` checks the released evidence surface |
| Appendix scorer and compute provenance | Fixed grouped-fold scorer configuration and validated software environments | `reports/reference_scorer_config.json`, `reports/environment_provenance.tsv` | `bash scripts/run_release_checks.sh` |

Boundary: this artifact reproduces table-level checks from fixed candidate
pools and ranked outputs. It does not rerun GPU embedding, reranker, or LLM
inference from raw model checkpoints.
